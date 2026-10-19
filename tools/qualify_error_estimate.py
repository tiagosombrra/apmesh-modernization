#!/usr/bin/env python3
"""Qualify ownership of the temporary error evaluator without changing its policy."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def qualify(asan, crt, runtime, output):
    output.mkdir(parents=True, exist_ok=False)
    environment = dict(os.environ)
    environment["PATH"] = str(runtime.resolve()) + os.pathsep + environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=0:detect_leaks=0"
    instruments = [("asan", asan), ("crt", crt)]
    fixtures = [f"{shape}-{degree}" for shape in range(5) for degree in [1, 2, 4]]
    cases = [(name, executable, "normal-" + fixture, None)
             for name, executable in instruments for fixture in fixtures]
    cases += [("crt", crt, "failure-" + fixture, None) for fixture in fixtures]
    cases += [("asan", asan, "use-after-free", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks"),
              ("crt", crt, "allocation-hook-control", None)]
    results = []
    for instrument, executable, mode, diagnostic in cases:
        invocations = []
        chunks = []
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
            interval = re.search(r"error_failure_range=shape:\d degree:\d first:(\d+) end:(\d+) total:(\d+)", current)
            if interval is None or int(interval[1]) != cursor:
                break
            if total is not None and total != int(interval[3]):
                break
            total = int(interval[3])
            cursor = int(interval[2])
            if cursor >= total:
                break
        data = b"".join(chunks)
        (output / f"{instrument}-{mode}.log").write_bytes(data)
        text = data.decode("utf-8", errors="replace")
        retained = re.search(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if diagnostic == "heap-use-after-free":
            passed = (exit_code is not None and exit_code != 0 and "ERROR: AddressSanitizer:" in text and diagnostic in text)
        elif diagnostic == "retained-blocks":
            passed = exit_code == 1 and retained is not None and int(retained[1]) > 0
        else:
            passed = exit_code == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if instrument == "crt":
                checkpoints = re.findall(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
                passed = passed and len(checkpoints) == len(invocations) and all(row == ("0", "0") for row in checkpoints)
            if mode.startswith("normal-"):
                reference = re.findall(r"error_reference=shape:(\d) degree:(\d) bits:([0-9a-f]{16}) nodes:(\d+)", text)
                policies = re.findall(r"error_policy=shape:\d degree:\d case:(\d) continue:[01] selected:\d+ graph:1 curvature:1", text)
                curvatures = re.findall(r"error_curvature=index:(\d+) bits:[0-9a-f]{16}", text)
                passed = (passed and len(reference) == 1 and policies == [str(i) for i in range(9)]
                          and len(curvatures) == 4 * int(reference[0][3])
                          and [int(i) for i in curvatures] == list(range(len(curvatures))))
            elif mode.startswith("failure-"):
                calibration = re.search(r"error_measured=shape:\d degree:\d allocations:(\d+)", text)
                ranges = re.findall(r"error_failure_range=shape:\d degree:\d first:(\d+) end:(\d+) total:(\d+)", text)
                denials = re.findall(r"error_denied=shape:\d degree:\d ordinal:(\d+) live_blocks:(-?\d+) live_bytes:(-?\d+) graph:(\d)", text)
                passed = (passed and calibration is not None and total is not None and cursor == total
                          and int(calibration[1]) == total and total > 0
                          and len(ranges) == len(invocations)
                          and [int(row[0]) for row in ranges] == list(range(0, total, 32))
                          and all(int(row[1]) == min(int(row[0]) + 32, total) and int(row[2]) == total for row in ranges)
                          and len(denials) == int(calibration[1])
                          and [int(row[0]) for row in denials] == list(range(len(denials)))
                          and all(row[1:] == ("0", "0", "1") for row in denials))
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        record = {"instrument": instrument, "mode": mode, "exit_code": exit_code,
                  "invocations": invocations,
                  "passed": bool(passed), "log_sha256": hashlib.sha256(data).hexdigest(),
                  "retained_blocks": int(retained[1]) if retained else None,
                  "retained_bytes": int(retained[2]) if retained else None,
                  "observations": [line for line in text.splitlines()
                                   if line.startswith(("error_", "allocation_hook_control="))]}
        results.append(record)
        print(json.dumps({key: value for key, value in record.items()
                          if key not in {"observations", "invocations"}}), flush=True)
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "scope": "Actual caller unit, actual class layout and dependency units with exact extracted generator constructor/serial ErrorGlobal and estimator construction/destruction. Original caller body is extracted verbatim from its verified Git snapshot. Full historical generator/estimator TUs contain MSVC-unsupported VLAs and are not instrumented as complete units. Plane, saddle, parabolic cylinder, empty and two-submesh layouts at degrees 1/2/4; nine repeated policy cases include strict/inclusive equality, adjacent floating values, NaN and infinities. Exact per-node curvature bits are compared to the direct unchanged evaluator and paired original traces. Allocation sweeps require zero live and final CRT deltas and preserved borrowed graph/selection state on exceptions; timer and partial node curvature writes are not rolled back. Original calibration itself leaks; original sweeps stop at their first live retention mismatch. ASan leak detection is disabled and original ASan normal success does not establish leak freedom. No area caller, arbitrary callback, CLI retry, full-process, parallel or scientific selection-policy qualification.",
              "executables": {name: {"path": str(path.resolve()),
                                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                              for name, path in instruments}, "cases": results}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ["asan", "crt", "runtime", "output"]:
        parser.add_argument("--" + flag, type=Path, required=True)
    args = parser.parse_args()
    result = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({"status": result["status"], "cases": len(result["cases"])}))
    raise SystemExit(0 if result["status"] == "passed" else 1)
