#!/usr/bin/env python3
"""Qualify temporary area-mesh lifetime and unchanged bounded orchestration."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def qualify(asan, crt, runtime, output, kind):
    output.mkdir(parents=True, exist_ok=False)
    environment = dict(os.environ)
    environment["PATH"] = str(runtime.resolve()) + os.pathsep + environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=0:detect_leaks=0"
    instruments = [("asan", asan), ("crt", crt)]
    fixtures = [f"{shape}-{layout}" for shape in range(2) for layout in range(7)]
    paths = range(7) if kind == "controlled" else [0]
    cases = [(name, executable, f"normal-{fixture}-{path}", None)
             for name, executable in instruments for fixture in fixtures for path in paths]
    if kind == "controlled":
        cases += [("crt", crt, f"failure-{fixture}-{path}", None)
                  for fixture in fixtures for path in range(4)]
        cases += [(name, executable, f"{mode}-{fixture}", None)
                  for mode in ["guard", "repeat"] for name, executable in instruments
                  for fixture in fixtures]
    cases += [("asan", asan, "use-after-free", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks"),
              ("crt", crt, "allocation-hook-control", None)]
    results = []
    for instrument, executable, mode, diagnostic in cases:
        invocations, chunks = [], []
        cursor, total = 0, None
        while True:
            child_mode = f"{mode}-{cursor}" if mode.startswith("failure-") else mode
            log = output / f"{instrument}-{child_mode}.raw.log"
            timed_out = False
            with log.open("xb") as stream:
                try:
                    process = subprocess.run([str(executable.resolve()), child_mode], env=environment,
                                             stdout=stream, stderr=subprocess.STDOUT, timeout=30)
                    exit_code = process.returncode
                except subprocess.TimeoutExpired:
                    timed_out, exit_code = True, None
            chunk = log.read_bytes()
            chunks.append(chunk)
            invocations.append({"mode": child_mode, "exit_code": exit_code, "timed_out": timed_out,
                                "log": log.name, "log_sha256": hashlib.sha256(chunk).hexdigest()})
            if not mode.startswith("failure-") or exit_code != 0:
                break
            current = chunk.decode("utf-8", errors="replace")
            interval = re.search(r"area_failure_range=shape:\d layout:\d path:\d first:(\d+) end:(\d+) total:(\d+)", current)
            if interval is None or int(interval[1]) != cursor:
                break
            if total is not None and total != int(interval[3]):
                break
            total, cursor = int(interval[3]), int(interval[2])
            if cursor >= total:
                break
        data = b"".join(chunks)
        (output / f"{instrument}-{mode}.log").write_bytes(data)
        text = data.decode("utf-8", errors="replace")
        retained = re.search(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if diagnostic == "heap-use-after-free":
            passed = (exit_code is not None and exit_code != 0
                      and "ERROR: AddressSanitizer:" in text and diagnostic in text)
        elif diagnostic == "retained-blocks":
            passed = exit_code == 1 and retained is not None and int(retained[1]) > 0
        else:
            passed = exit_code == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if instrument == "crt":
                checkpoints = re.findall(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
                passed = (passed and len(checkpoints) == len(invocations)
                          and all(row == ("0", "0") for row in checkpoints))
            if mode.startswith(("normal-", "repeat-")):
                values = re.findall(r"area_result=shape:\d layout:\d path:(\d) selected:(\d+) exception:(\d) bits:([0-9a-f]{16}) restored:(\d)", text)
                expected = [int(mode.rsplit("-", 1)[1])] if mode.startswith("normal-") else [0, 1, 2]
                if kind == "real":
                    expected = [0, 0, 0]
                passed = passed and [int(row[0]) for row in values] == expected
                passed = passed and all(row[4] == "1" for row in values)
                states = re.findall(r"area_state=patch:1 points:1 parameters:1 borrowed_nodes:1 previous_live:1 borrowed_entries:\d+", text)
                passed = passed and len(states) == len(expected)
                steps = re.findall(r"area_step=index:(\d) degree:(\d+) nodes:(\d+) elements:(\d+) bits:([0-9a-f]{16})", text)
                expected_steps = []
                if kind == "controlled":
                    for path in expected:
                        degree = 4 if path == 3 else 1
                        count = 2 if path in [1, 2, 3, 6] else 1
                        expected_steps += [(str(index), str(degree + index)) for index in range(count)]
                passed = passed and [(row[0], row[1]) for row in steps] == expected_steps
            elif mode.startswith("guard-"):
                guards = re.findall(r"area_guard=degree:(-?\d+) restored:(\d)", text)
                passed = passed and guards == [("0", "1"), ("-1", "1"), ("-2147483648", "1")]
            elif mode.startswith("failure-"):
                calibrations = {int(row) for row in re.findall(r"area_measured=shape:\d layout:\d path:\d allocations:(\d+)", text)}
                ranges = re.findall(r"area_failure_range=shape:\d layout:\d path:\d first:(\d+) end:(\d+) total:(\d+)", text)
                denials = re.findall(r"area_denied=shape:\d layout:\d path:\d ordinal:(\d+) live_blocks:(-?\d+) live_bytes:(-?\d+) restored:(\d)", text)
                passed = (passed and total is not None and total > 0 and cursor == total
                          and calibrations == {total} and len(ranges) == len(invocations)
                          and [int(row[0]) for row in ranges] == list(range(0, total, 32))
                          and all(int(row[1]) == min(int(row[0]) + 32, total)
                                  and int(row[2]) == total for row in ranges)
                          and [int(row[0]) for row in denials] == list(range(total))
                          and all(row[1:] == ("0", "0", "1") for row in denials))
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        record = {"instrument": instrument, "mode": mode, "exit_code": exit_code,
                  "invocations": invocations, "passed": bool(passed),
                  "log_sha256": hashlib.sha256(data).hexdigest(),
                  "retained_blocks": int(retained[1]) if retained else None,
                  "retained_bytes": int(retained[2]) if retained else None,
                  "observations": [line for line in text.splitlines()
                                   if line.startswith(("area_", "allocation_hook_control="))]}
        results.append(record)
        print(json.dumps({key: value for key, value in record.items()
                          if key not in {"observations", "invocations"}}), flush=True)
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "kind": kind,
              "scope": "Actual area caller and factory/dependency units. Controlled target defines the existing error member only in its test executable to force stop, increment, earlier selected degree, evaluate-before-cap at 5, selected-zero rejection and exceptions before/after replacement. No callback seam is added to production. Real target separately uses the actual error caller plus exact extracted generator constructor/serial ErrorGlobal and actual class/dependency units for three repeated degree-1 calls. Full historical generator/estimator TUs contain MSVC-unsupported VLAs and are not instrumented as complete units. Plane/bilinear analytic areas and original/repaired exact traces at selected dyadic degrees, seven lifetime layouts, fixed topology/factory publication. Physical mesh and fresh samples are reclaimed; previous patch observer and borrowed sample/parameter/adjacency list nodes survive. Existing minor_error behavior, selected-zero rejection and timer/partial curvature writes are preserved, not rolled back. Complete degree-5/extreme mesh geometry, arbitrary callbacks/foreign publications, cache recovery, CLI retry, full-process/parallel/LSan/UBSan and scientific policy are unqualified. Original successful calibration itself leaks; stopped original sweeps leave later ordinals unmeasured. Removing the raw outer Mesh allocation deliberately changes calibration counts. ASan leak detection is disabled.",
              "executables": {name: {"path": str(path.resolve()),
                                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                              for name, path in instruments}, "cases": results}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ["asan", "crt", "runtime", "output"]:
        parser.add_argument("--" + flag, type=Path, required=True)
    parser.add_argument("--kind", choices=["controlled", "real"], default="controlled")
    args = parser.parse_args()
    result = qualify(args.asan, args.crt, args.runtime, args.output, args.kind)
    print(json.dumps({"status": result["status"], "cases": len(result["cases"])}))
    raise SystemExit(0 if result["status"] == "passed" else 1)
