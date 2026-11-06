#!/usr/bin/env python3
"""Attribute retained CRT requests and observe their natural static teardown."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from boundary_orientation_case import run_control


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_captured_artifact(folder, artifacts, path):
    try:
        name = path.resolve().relative_to(folder.resolve()).as_posix()
    except ValueError as error:
        raise ValueError("Symbol records must belong to the captured artifact directory") from error
    if name not in artifacts or digest(path) != artifacts[name]:
        raise ValueError("Symbol records are not the registered captured artifact")


def inspect_trace(stdout, stderr, code):
    summary = re.findall(r"^STATIC_CRT app_exit=(\d+) heap_valid=(\d+) iterator_level=(\d+) "
                         r"denied=(\d+) errors=(\d+)$", stdout, re.MULTILINE)
    if len(summary) != 1:
        raise ValueError("Exactly one complete static-observer checkpoint is required")
    app_exit, heap_valid, iterator_level, denied, errors = map(int, summary[0])
    if code != app_exit or heap_valid != 1 or iterator_level != 2 or errors:
        raise ValueError("Invalid native result, heap, iterator ABI or observer errors")
    if re.search(r"HEAP CORRUPTION|Debug Assertion Failed|DAMAGE:|Runtime Check Failure|CRT_ERROR", stderr):
        raise ValueError("Unexpected native diagnostic")
    watches = re.findall(r"^CRT_WATCH request=(\d+) bytes=(\d+)$", stderr, re.MULTILINE)
    watched = {int(request): int(size) for request, size in watches}
    if len(watched) != len(watches):
        raise ValueError("Duplicate retained request")
    begins, ends = stderr.count("STATIC_CRT_DUMP_BEGIN\n"), stderr.count("STATIC_CRT_DUMP_END\n")
    if begins != 1 or ends != 1:
        raise ValueError("Missing or duplicate independent CRT dump")
    begin = stderr.index("STATIC_CRT_DUMP_BEGIN\n") + len("STATIC_CRT_DUMP_BEGIN\n")
    end = stderr.index("STATIC_CRT_DUMP_END\n")
    if end < begin:
        raise ValueError("Reversed independent CRT dump")
    dump = stderr[begin:end]
    blocks = re.findall(r"\{(\d+)\} (?:normal|client) block at .*?, (\d+) bytes long\.", dump)
    independent = {int(request): int(size) for request, size in blocks}
    residue = dump.replace("Dumping objects ->", "").replace("Object dump complete.", "").strip()
    if len(independent) != len(blocks) or independent != watched or (residue and not blocks):
        raise ValueError("Trace and independent newer-live-block dump disagree")
    frees = re.findall(r"^CRT_FREE request=(\d+) phase=(\d+) bytes=(\d+)$", stderr, re.MULTILINE)
    released = {}
    for request, phase, size in frees:
        request, phase, size = int(request), int(phase), int(size)
        if request in released or request not in watched or size != watched[request] or phase not in (2, 3, 4):
            raise ValueError("Unknown, duplicate or inconsistent retained-request release")
        released[request] = phase
    states = re.findall(r"^CRT_STATE name=([a-z_]+) phase=(\d+) blocks=(\d+) bytes=(\d+) "
                        r"errors=(\d+) reallocations=(\d+)$", stderr, re.MULTILINE)
    if [(s[0], int(s[1])) for s in states] != [
            ("entry_return", 1), ("after_lazy_statics", 3), ("after_executable_statics", 4)]:
        raise ValueError("Incomplete or misordered natural teardown boundaries")
    parsed_states = []
    for name, phase, count, size, errors, reallocations in states:
        phase, count, size, errors, reallocations = map(int, (phase, count, size, errors, reallocations))
        remaining = {r: b for r, b in watched.items() if r not in released or released[r] >= phase}
        if errors or reallocations or (count, size) != (len(remaining), sum(remaining.values())):
            raise ValueError("Teardown state disagrees with requests, or observer is incomplete")
        parsed_states.append({"name": name, "phase": phase, "blocks": count, "bytes": size})
    frame_rows = re.findall(r"^CRT_FRAME kind=(allocation|release) request=(\d+) "
                           r"rva=(0x[0-9a-f]+) module=(.+)$", stderr, re.MULTILINE)
    frames = {"allocation": defaultdict(list), "release": defaultdict(list)}
    for kind, request, rva, module in frame_rows:
        request = int(request)
        if request not in watched or (kind == "release" and request not in released):
            raise ValueError("Stack belongs to an unknown request or release")
        frames[kind][request].append({"module": module, "rva": rva})
    if set(frames["allocation"]) != set(watched) or set(frames["release"]) != set(released):
        raise ValueError("Missing retained-allocation or release stack")
    owners = re.findall(r"^CRT_OWNER name=([A-Z_]+) request=(\d+) bytes=(\d+)$", stderr, re.MULTILINE)
    owner_rows = []
    for name, request, size in owners:
        request, size = int(request), int(size)
        if request not in watched or watched[request] != size:
            raise ValueError("Named path owner is not a retained request")
        owner_rows.append({"name": name, "request": request, "bytes": size})
    remaining = {r: b for r, b in watched.items() if r not in released}
    return {"app_exit": app_exit, "denied": denied, "watched": watched,
            "released": released, "states": parsed_states, "owners": owner_rows,
            "frames": {kind: dict(rows) for kind, rows in frames.items()},
            "remaining_after_process_exit": remaining,
            "released_all_observed_requests": not remaining}


def qualify_control(mode, trace):
    entry, lazy, final = trace["states"]
    shape = [(state["blocks"], state["bytes"]) for state in (entry, lazy, final)]
    expected = {
        "release-control": [(0, 0)] * 3,
        "static-release-control": [(1, 64), (1, 64), (0, 0)],
        "static-leak-control": [(1, 64)] * 3,
        "hook-control": [(0, 0)] * 3,
        "keys-control": [(147, 7192), (0, 0), (0, 0)],
    }
    if mode not in expected or shape != expected[mode] or trace["app_exit"]:
        raise ValueError("Native control does not satisfy its exact owner/teardown oracle")
    if trace["denied"] != int(mode == "hook-control"):
        raise ValueError("Native allocation-denial calibration differs")
    if mode == "static-leak-control":
        if trace["released"] or len(trace["remaining_after_process_exit"]) != 1:
            raise ValueError("Deliberate unowned retention was hidden")
    elif not trace["released_all_observed_requests"]:
        raise ValueError("Owned control did not release every observed request")
    if mode == "static-release-control" and set(trace["released"].values()) != {3}:
        raise ValueError("Global owner did not retire between the calibrated boundaries")
    if mode == "keys-control" and set(trace["released"].values()) != {2}:
        raise ValueError("Lazy-static key owners did not retire before their calibrated boundary")


def symbolize(traces, symbolizer, folder):
    addresses = defaultdict(set)
    for trace in traces:
        for requests in trace["frames"].values():
            for frames in requests.values():
                for frame in frames:
                    # Owner attribution requires the executable's private PDB. Keep external
                    # module addresses without claiming unavailable Windows private symbols.
                    if Path(frame["module"]).suffix.lower() == ".exe":
                        addresses[frame["module"]].add(frame["rva"])
    symbols = {}
    for index, (module, offsets) in enumerate(sorted(addresses.items())):
        command = [str(symbolizer), "--relative-address", "--output-style=JSON", "--obj=" + module,
                   *sorted(offsets, key=lambda value: int(value, 16))]
        process = subprocess.run(command, capture_output=True, timeout=30)
        (folder / f"symbols-{index}.stdout.log").write_bytes(process.stdout)
        (folder / f"symbols-{index}.stderr.log").write_bytes(process.stderr)
        if process.returncode:
            raise ValueError("Local stack symbolization failed")
        rows = json.loads(process.stdout)
        if len(rows) != len(offsets):
            raise ValueError("Incomplete local stack symbolization")
        symbols[module] = {hex(int(row["Address"], 16)): row["Symbol"] for row in rows}
    (folder / "symbols.json").write_text(json.dumps(symbols, indent=2) + "\n", encoding="utf-8", newline="\n")
    return symbols


def attribute(trace, symbols):
    groups = defaultdict(list)
    named = {row["request"]: row["name"] for row in trace["owners"]}
    requests = []
    for request, size in trace["watched"].items():
        stacks = {}
        for kind in ("allocation", "release"):
            frames = []
            for frame in trace["frames"][kind].get(request, []):
                resolved = symbols.get(frame["module"], {}).get(hex(int(frame["rva"], 16)), [])
                frames.extend({**frame, **symbol} for symbol in resolved)
                if not resolved:
                    frames.append({**frame, "symbol_status": "unresolved_external_frame"})
            stacks[kind] = frames
        frames = stacks["allocation"]
        names = [frame.get("FunctionName", "") for frame in frames]
        releases = [frame.get("FunctionName", "") for frame in stacks["release"]]
        if request in named:
            owner = named[request]
        elif any("ValidateConfigValue" in name for name in names):
            owner = "configuration_key_sets"
        elif (size == 8 and any("CurveAdaptiveParametric" in name and "vector" in name for name in names)
              and any("atexit destructor" in name and "ptr_aux" in name for name in releases)):
            owner = "ptr_aux_storage"
        else:
            owner = "unattributed"
        groups[owner].append({"request": request, "bytes": size})
        requests.append({"request": request, "bytes": size, "owner": owner,
                         "release_phase": trace["released"].get(request), "allocation_stack": frames,
                         "release_stack": stacks["release"]})
    return {"groups": {name: {"blocks": len(rows), "bytes": sum(r["bytes"] for r in rows)}
                       for name, rows in groups.items()}, "requests": requests}


def analyze_existing(report_path, symbols_path, output):
    """Finish attribution from immutable captured logs; never launch a native process."""
    prior = json.loads(report_path.read_text())
    folder = report_path.parent
    require_captured_artifact(folder, prior["artifacts"], symbols_path)
    for name, value in prior["artifacts"].items():
        if digest(folder / name) != value:
            raise ValueError("Captured diagnostic artifact changed before attribution")
    case = prior["production_cases"][0]
    executable = Path(case["process"]["command"][0])
    if digest(executable) != prior["executable_sha256"] or case["status"] != "passed":
        raise ValueError("Diagnostic executable or independent generation status differs")
    trace = inspect_trace((folder / "aligned/stdout.log").read_text(),
                          (folder / "aligned/stderr.log").read_text(), case["process"]["exit_code"])
    rows = json.loads(symbols_path.read_bytes())
    if not isinstance(rows, list) or not rows:
        raise ValueError("Complete executable symbol records are required")
    if any(Path(row["ModuleName"]).resolve() != executable.resolve() for row in rows):
        raise ValueError("Symbol records belong to a different executable")
    symbols = {str(executable): {hex(int(row["Address"], 16)): row["Symbol"] for row in rows}}
    attribution = attribute(trace, symbols)
    expected = {"configuration_key_sets": {"blocks": 147, "bytes": 7192},
                "INPUT_MODEL": {"blocks": 1, "bytes": 128},
                "NAME_MODEL": {"blocks": 1, "bytes": 128},
                "ptr_aux_storage": {"blocks": 1, "bytes": 8}}
    if attribution["groups"] != expected or not trace["released_all_observed_requests"]:
        raise ValueError("Not every retained request has its demonstrated owner and release")
    result = {"schema": 1, "status": "observed_requests_attributed_and_released",
              "native_executions_added_by_analysis": 0, "trace_report_sha256": digest(report_path),
              "executable_symbols_sha256": digest(symbols_path), "trace": trace,
              "attribution": attribution, "stage_closure": False,
              "external_symbols": "Windows private PDBs unavailable; raw module/RVA frames retained",
              "original_failed_symbolization": prior.get("error")}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path)
    parser.add_argument("--symbolizer", type=Path)
    parser.add_argument("--original", type=Path)
    parser.add_argument("--analyze-existing", type=Path)
    parser.add_argument("--executable-symbols", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.analyze_existing:
        if not args.executable_symbols or args.exe or args.symbolizer or args.original:
            parser.error("Existing-log analysis requires only --executable-symbols and --output")
        result = analyze_existing(args.analyze_existing.resolve(), args.executable_symbols.resolve(),
                                  args.output.resolve())
        print(json.dumps({"status": result["status"], "report": str(args.output),
                          "groups": result["attribution"]["groups"], "native_executions_added": 0}))
        return 0
    if not all((args.exe, args.symbolizer, args.original)):
        parser.error("Native observation requires --exe, --symbolizer and --original")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    executable, symbolizer_path = args.exe.resolve(strict=True), args.symbolizer.resolve(strict=True)
    original = json.loads(args.original.read_text())
    report = {"schema": 1, "status": "started", "controls": [], "production_cases": [],
              "executable_sha256": digest(executable), "symbolizer_sha256": digest(symbolizer_path),
              "original_report_sha256": digest(args.original), "stage_closure": False}
    try:
        for mode in ("release-control", "static-release-control", "static-leak-control", "hook-control", "keys-control"):
            row = {"mode": mode, "status": "started", "command": [str(executable), mode], "timeout_seconds": 10}
            report["controls"].append(row)
            out_path, err_path = output / f"{mode}.stdout.log", output / f"{mode}.stderr.log"
            with out_path.open("wb") as stdout, err_path.open("wb") as stderr:
                process = subprocess.run(row["command"], cwd=ROOT, stdout=stdout, stderr=stderr, timeout=10)
            row["exit_code"] = process.returncode
            row["trace"] = inspect_trace(out_path.read_text(), err_path.read_text(), process.returncode)
            qualify_control(mode, row["trace"])
            row["status"] = "passed_expected_retention" if mode == "static-leak-control" else "passed"
        report["instrument_controls"] = "passed"
        # The same-input diagnostic has a distinct process and output identity.
        pending = {"case": "aligned", "ledger_id": "SP-02", "status": "started", "timeout_seconds": 60}
        report["production_cases"].append(pending)
        case = run_control(executable, output, "aligned", False, 2)
        pending.update(case)
        case = pending
        folder = output / "aligned"
        case["trace"] = inspect_trace((folder / "stdout.log").read_text(), (folder / "stderr.log").read_text(),
                                      case["process"]["exit_code"])
        before = original["production_cases"][0]
        original_dump = (args.original.parent / "aligned/stderr.log").read_text()
        original_shape = Counter(int(size) for size in re.findall(
            r"normal block at .*?, (\d+) bytes long\.", original_dump))
        if case["process"]["input_model_sha256"] != before["process"]["input_model_sha256"]:
            raise ValueError("The diagnostic input differs from the retained original")
        trace = case["trace"]
        if (len(trace["watched"]), sum(trace["watched"].values())) != (150, 7456):
            raise ValueError("The diagnostic does not reproduce the retained entry-return shape")
        if Counter(trace["watched"].values()) != original_shape:
            raise ValueError("The diagnostic retained-size distribution differs from the original")
        if case["status"] != "passed":
            raise ValueError("The diagnostic failed independent physical/UV/boundary verification")
        symbols = symbolize([r["trace"] for r in report["controls"]] + [trace], symbolizer_path, output)
        case["attribution"] = attribute(trace, symbols)
        if not trace["released_all_observed_requests"]:
            raise ValueError("Observed entry-return requests remain unfreed after process exit")
        report["status"] = "observed_retained_requests_released"
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report.update(status="failed", error=str(error))
        for row in report["controls"] + report["production_cases"]:
            if row["status"] == "started":
                row.update(status="failed", error=str(error))
    finally:
        report["artifacts"] = {p.relative_to(output).as_posix(): digest(p)
                               for p in sorted(output.rglob("*")) if p.is_file()}
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "report": str(output / "report.json"), "error": report.get("error")}))
    return int(report["status"] != "observed_retained_requests_released")


if __name__ == "__main__":
    raise SystemExit(main())
