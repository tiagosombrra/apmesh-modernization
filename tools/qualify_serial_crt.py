#!/usr/bin/env python3
"""Qualify checked-CRT controls, then observe the existing complete-entry SP-02 once."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from boundary_orientation_case import run_control


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_observer(stdout, stderr):
    """Require a complete checkpoint and newer-live-block dump, including balanced leaks."""
    rows = re.findall(r"^SERIAL_CRT (.+)$", stdout, re.MULTILINE)
    if len(rows) != 1:
        raise ValueError("Exactly one complete CRT checkpoint is required")
    fields = dict(re.findall(r"([a-z_]+)=(-?\d+)", rows[0]))
    expected = {
        "app_exit", "heap_valid", "iterator_level", "allocations", "denied", "caught",
        "normal_blocks_delta", "normal_bytes_delta", "client_blocks_delta", "client_bytes_delta",
    }
    if set(fields) != expected:
        raise ValueError("Incomplete or unexpected CRT checkpoint fields")
    data = {key: int(value) for key, value in fields.items()}
    if data["heap_valid"] != 1 or data["iterator_level"] != 2 or data["allocations"] < 1:
        raise ValueError("Heap, checked iterator or actual allocation control is unqualified")
    if stderr.count("SERIAL_CRT_DUMP_BEGIN\n") != 1 or stderr.count("SERIAL_CRT_DUMP_END\n") != 1:
        raise ValueError("Missing or duplicate newer-live-block dump")
    begin = stderr.index("SERIAL_CRT_DUMP_BEGIN\n") + len("SERIAL_CRT_DUMP_BEGIN\n")
    end = stderr.index("SERIAL_CRT_DUMP_END\n")
    if end < begin:
        raise ValueError("Reversed CRT dump delimiters")
    dump = stderr[begin:end]
    blocks = re.findall(r"\{(\d+)\} (normal|client) block at .*?, (\d+) bytes long\.", dump)
    data["newer_live_blocks"] = len(blocks)
    data["newer_live_bytes"] = sum(int(block[2]) for block in blocks)
    # Unknown dump output cannot silently become a clean observation.
    empty_dump = dump.replace("Dumping objects ->", "").replace("Object dump complete.", "").strip()
    if empty_dump and not blocks:
        raise ValueError("Unrecognized nonempty CRT dump")
    if re.search(r"HEAP CORRUPTION|Debug Assertion Failed|DAMAGE:|Runtime Check Failure", stderr):
        raise ValueError("Unexpected native heap or checked-runtime diagnostic")
    deltas = [data[key] for key in expected if key.endswith("_delta")]
    data["clean"] = not any(deltas) and not blocks
    return data


def qualify_control(mode, code, data):
    if data["app_exit"] != 0:
        raise ValueError("Instrument control did not complete")
    if mode == "hook-control":
        if code or not data["clean"] or (data["allocations"], data["denied"], data["caught"]) != (1, 1, 1):
            raise ValueError("Actual allocation denial/unwind control failed")
    elif data["denied"] or data["caught"]:
        raise ValueError("Unexpected allocation denial")
    elif mode == "release-control":
        if code or not data["clean"]:
            raise ValueError("Actual release control failed")
    elif mode in ("leak-control", "replacement-control"):
        expected_delta = 0 if mode == "replacement-control" else 1
        expected_code = 0 if mode == "replacement-control" else 2
        if (code != expected_code or data["clean"] or data["normal_blocks_delta"] != expected_delta
                or data["normal_bytes_delta"] != 64 * expected_delta
                or data["client_blocks_delta"] or data["client_bytes_delta"]
                or data["newer_live_blocks"] != 1 or data["newer_live_bytes"] != 64):
            raise ValueError("Deliberate retained-storage control was not detected exactly")
    else:
        raise ValueError("Unknown instrument control")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    executable = args.exe.resolve(strict=True)
    report = {
        "schema": 1, "status": "incomplete", "classification": "engineering-only instrument observation",
        "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "executable": str(executable), "executable_sha256": digest(executable),
        "controls": [], "production_cases": [], "stop_after_first_unexpected_failure": True,
        "stage_closure": False,
    }
    report["source_hashes"] = {
        path.relative_to(ROOT).as_posix(): digest(path)
        for folder in ("src", "include") for path in sorted((ROOT / folder).rglob("*")) if path.is_file()
    }
    for name in ("tests/serial_crt/probe.cpp", "tests/serial_crt/CMakeLists.txt",
                 "tools/qualify_serial_crt.py", "tests/boundary_orientation_case.py"):
        report["source_hashes"][name] = digest(ROOT / name)
    start = time.monotonic()
    try:
        for mode in ("release-control", "leak-control", "replacement-control", "hook-control"):
            command = [str(executable), mode]
            item = {"mode": mode, "command": command, "timeout_seconds": 10, "status": "started"}
            report["controls"].append(item)
            stdout_path, stderr_path = output / f"{mode}.stdout.log", output / f"{mode}.stderr.log"
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                process = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, timeout=10)
            item["exit_code"] = process.returncode
            item["observer"] = inspect_observer(stdout_path.read_text(), stderr_path.read_text())
            qualify_control(mode, process.returncode, item["observer"])
            item["status"] = "passed"
        report["instrument_controls"] = "passed"
        # Reuse the fixed input generator, invocation, timeout and independent checker unchanged.
        pending_case = {"case": "aligned", "ledger_id": "SP-02", "status": "started",
                        "timeout_seconds": 60}
        report["production_cases"].append(pending_case)
        case = run_control(executable, output, "aligned", False, 2)
        pending_case.update(case)
        case = pending_case
        folder = output / "aligned"
        case["observer"] = inspect_observer((folder / "stdout.log").read_text(),
                                            (folder / "stderr.log").read_text())
        if not case["observer"]["clean"] or case["observer"]["app_exit"] != 0:
            case["status"] = "failed"
            raise ValueError("SP-02 complete-entry CRT accounting retains storage or failed")
        if case["status"] != "passed":
            raise ValueError("SP-02 independent physical/UV/boundary checks failed")
        report["status"] = "passed_bounded_sp02"
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report.update(status="failed", error=str(error))
        for item in report["controls"] + report["production_cases"]:
            if item["status"] == "started":
                item.update(status="timeout" if isinstance(error, subprocess.TimeoutExpired) else "failed",
                            error=str(error))
    finally:
        report["elapsed_seconds"] = time.monotonic() - start
        report["artifacts"] = {path.relative_to(output).as_posix(): digest(path)
                               for path in sorted(output.rglob("*")) if path.is_file()}
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(output / "report.json"),
                      "error": report.get("error")}))
    return 0 if report["status"] == "passed_bounded_sp02" else 1


if __name__ == "__main__":
    raise SystemExit(main())
