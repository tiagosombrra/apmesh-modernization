#!/usr/bin/env python3
"""Qualify the executable-owned CRT interval before entering the fixed serial inventory."""

import argparse
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


def inspect_lifetime(stdout, stderr, exit_code):
    # Normalize only the parsed view; immutable raw capture bytes retain their native endings.
    stdout, stderr = stdout.replace("\r\n", "\n"), stderr.replace("\r\n", "\n")
    main = re.findall(r"^LIFETIME_MAIN app_exit=(-?\d+) iterator_level=(\d+) attempts=(\d+) "
                      r"denied=(\d+) caught=(\d+)$", stdout, re.MULTILINE)
    final = re.findall(r"^LIFETIME_FINAL active=(\d+) heap_valid=(\d+) normal_blocks_delta=(-?\d+) "
                       r"normal_bytes_delta=(-?\d+) client_blocks_delta=(-?\d+) "
                       r"client_bytes_delta=(-?\d+)$", stderr, re.MULTILINE)
    owner = re.findall(r"^LIFETIME_OWNER destroyed=1 late_mode=(\d+)$", stderr, re.MULTILINE)
    if len(main) != 1 or len(final) != 1 or len(owner) != 1:
        raise ValueError("Missing, incomplete or duplicate entry/owner/final CRT checkpoint")
    app_exit, iterator_level, attempts, denied, caught = map(int, main[0])
    active, heap_valid, normal_blocks, normal_bytes, client_blocks, client_bytes = map(int, final[0])
    # Windows exposes the native int return value through an unsigned 32-bit process code.
    if (not -(1 << 31) <= app_exit < (1 << 31) or
            (app_exit & 0xffffffff) != (exit_code & 0xffffffff) or
            iterator_level != 2 or active != 1 or heap_valid != 1):
        raise ValueError("Native status, checked ABI or final heap integrity differs")
    if stderr.count("LIFETIME_DUMP_BEGIN\n") != 1 or stderr.count("LIFETIME_DUMP_END\n") != 1:
        raise ValueError("Missing or duplicate independent final heap dump")
    begin, end = stderr.index("LIFETIME_DUMP_BEGIN\n"), stderr.index("LIFETIME_DUMP_END\n")
    if not stderr.index("LIFETIME_OWNER destroyed=1") < begin < end < stderr.index("LIFETIME_FINAL "):
        raise ValueError("Final accounting does not follow the owning static destructor")
    dump = stderr[begin + len("LIFETIME_DUMP_BEGIN\n"):end]
    blocks = re.findall(r"\{(\d+)\} (normal|client) block at .*?, (\d+) bytes long\.", dump)
    residual = dump.replace("Dumping objects ->", "").replace("Object dump complete.", "").strip()
    if residual and not blocks:
        raise ValueError("Unrecognized nonempty CRT object dump")
    if re.search(r"HEAP CORRUPTION|Debug Assertion Failed|DAMAGE:|Runtime Check Failure", stderr):
        raise ValueError("Unexpected native heap diagnostic")
    allocations = re.findall(r"^LIFETIME_ALLOCATION phase=(main|shutdown) observed=(\d+) "
                             r"request=(\d+) bytes=(\d+)$", stderr, re.MULTILINE)
    observed = []
    for phase, valid, request, size in allocations:
        if valid != "1" or int(request) <= 0 or int(size) != 64:
            raise ValueError("Allocation calibration has no actual 64-byte debug heap block")
        observed.append({"phase": phase, "request": int(request), "bytes": int(size)})
    return {"app_exit": app_exit, "attempts": attempts, "denied": denied, "caught": caught,
            "late_mode": int(owner[0]), "normal_blocks_delta": normal_blocks,
            "normal_bytes_delta": normal_bytes, "client_blocks_delta": client_blocks,
            "client_bytes_delta": client_bytes, "newer_live_blocks": len(blocks),
            "newer_live_bytes": sum(int(row[2]) for row in blocks),
            "live_requests": [int(row[0]) for row in blocks], "observed_allocations": observed,
            "clean": not any((normal_blocks, normal_bytes, client_blocks, client_bytes)) and not blocks}


def qualify_control(mode, data):
    if data["app_exit"] or len(data["observed_allocations"]) != 1:
        raise ValueError("Control needs one actual allocation and successful native completion")
    observed = data["observed_allocations"][0]
    late = mode.startswith("late-")
    if observed["phase"] != ("shutdown" if late else "main"):
        raise ValueError("Control allocation occurred outside its required lifetime phase")
    expected_late_mode = 1 if mode == "late-release" else 2 if mode == "late-retention" else 0
    if data["late_mode"] != expected_late_mode:
        raise ValueError("Late owner control did not execute its prescribed branch")
    if mode in ("retention", "late-retention"):
        if (data["normal_blocks_delta"], data["normal_bytes_delta"], data["client_blocks_delta"],
                data["client_bytes_delta"], data["newer_live_blocks"], data["newer_live_bytes"]) != (1, 64, 0, 0, 1, 64):
            raise ValueError("Deliberate retained storage is not detected exactly")
        if data["live_requests"] != [observed["request"]]:
            raise ValueError("Retained block differs from the independently observed allocation")
    elif mode in ("release", "global-release", "late-release", "denial"):
        if not data["clean"]:
            raise ValueError("Owned control retains executable-window storage")
    else:
        raise ValueError("Unknown lifetime control")
    expected_denial = (2, 1, 1) if mode == "denial" else (0, 0, 0)
    if (data["attempts"], data["denied"], data["caught"]) != expected_denial:
        raise ValueError("Allocation denial or real owner unwind calibration differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    executable, output = args.exe.resolve(strict=True), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    report = {"schema": 1, "status": "started", "controls": [], "cases": [],
              "executable": str(executable), "executable_sha256": digest(executable),
              "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "scope": "executable-owned normal/client CRT interval; runtime/DLL baseline excluded",
              "stage_closure": False}
    try:
        for mode in ("release", "global-release", "late-release", "retention", "late-retention", "denial"):
            row = {"mode": mode, "status": "started", "timeout_seconds": 10,
                   "command": [str(executable), "--lifetime-control", mode]}
            report["controls"].append(row)
            out_path, err_path = output / f"{mode}.stdout.log", output / f"{mode}.stderr.log"
            with out_path.open("wb") as stdout, err_path.open("wb") as stderr:
                process = subprocess.run(row["command"], cwd=ROOT, stdout=stdout, stderr=stderr, timeout=10)
            row["exit_code"] = process.returncode
            row["observer"] = inspect_lifetime(out_path.read_text(), err_path.read_text(), process.returncode)
            qualify_control(mode, row["observer"])
            row["status"] = "passed_expected_retention" if mode.endswith("retention") else "passed"
        report["instrument_controls"] = "passed"
        pending = {"case": "aligned", "ledger_id": "SP-02", "status": "started", "timeout_seconds": 60}
        report["cases"].append(pending)
        pending.update(run_control(executable, output, "aligned", False, 2))
        folder = output / "aligned"
        pending["observer"] = inspect_lifetime((folder / "stdout.log").read_text(),
                                               (folder / "stderr.log").read_text(),
                                               pending["process"]["exit_code"])
        if pending["status"] != "passed" or not pending["observer"]["clean"]:
            raise ValueError("SP-02 failed final CRT or independent physical/UV/boundary verification")
        report["status"] = "passed_bounded_executable_lifetime_sp02"
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        report.update(status="failed", error=str(error))
        for row in report["controls"] + report["cases"]:
            if row["status"] == "started":
                row.update(status="failed", error=str(error))
    finally:
        report["artifacts"] = {p.relative_to(output).as_posix(): digest(p)
                               for p in sorted(output.rglob("*")) if p.is_file()}
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "report": str(output / "report.json"),
                      "error": report.get("error")}))
    return int(report["status"] != "passed_bounded_executable_lifetime_sp02")


if __name__ == "__main__":
    raise SystemExit(main())
