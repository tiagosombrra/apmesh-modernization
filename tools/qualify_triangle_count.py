#!/usr/bin/env python3
"""Qualify temporary triangle-count ownership and borrowed graph preservation."""

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
    fixtures = [f"{shape}-{layout}-{degree}" for shape in range(2) for layout in range(7)
                for degree in [1, 2, 4]]
    cases = [(instrument, executable, "normal-" + fixture, None)
             for instrument, executable in instruments for fixture in fixtures]
    cases += [("crt", crt, "failure-" + fixture, None) for fixture in fixtures]
    cases += [(instrument, executable, f"repeat-{shape}-{layout}", None)
              for instrument, executable in instruments for shape in range(2) for layout in range(7)]
    cases += [(instrument, executable, "invalid-degree", None) for instrument, executable in instruments]
    cases += [("asan", asan, "use-after-free", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks"),
              ("crt", crt, "allocation-hook-control", None)]
    results = []
    for instrument, executable, mode, diagnostic in cases:
        process = subprocess.run([str(executable.resolve()), mode], env=environment,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        data = process.stdout
        (output / f"{instrument}-{mode}.log").write_bytes(data)
        text = data.decode("utf-8", errors="replace")
        retained = re.search(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if diagnostic == "heap-use-after-free":
            passed = (process.returncode != 0 and "ERROR: AddressSanitizer:" in text and diagnostic in text)
        elif diagnostic == "retained-blocks":
            passed = process.returncode == 1 and retained is not None and int(retained[1]) > 0
        else:
            passed = process.returncode == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if instrument == "crt":
                passed = passed and retained is not None and int(retained[1]) == int(retained[2]) == 0
            if mode.startswith(("normal-", "repeat-")):
                count = 3 if mode.startswith("repeat-") else 1
                values = re.findall(r"count_result=shape:\d layout:\d degree:(\d) value:(\d+) restored:(\d)", text)
                states = re.findall(r"count_state=patch:1 points:1 parameters:1 borrowed_nodes:1 previous_live:1 borrowed_entries:\d+", text)
                passed = (passed and len(values) == len(states) == count
                          and all(int(value) == 4 * int(degree)**2 and restored == "1"
                                  for degree, value, restored in values))
            elif mode.startswith("failure-"):
                calibration = re.search(r"count_measured=shape:\d layout:\d degree:\d allocations:(\d+) calibration_restored:(\d)", text)
                summary = re.search(r"count_failure_sites=shape:\d layout:\d degree:\d denied:(\d+)/(\d+)", text)
                denials = re.findall(r"count_denied=shape:\d layout:\d degree:\d ordinal:(\d+) live_blocks:(-?\d+) live_bytes:(-?\d+) restored:(\d)", text)
                passed = (passed and calibration is not None and summary is not None
                          and int(calibration[1]) > 0 and calibration[2] == "1"
                          and summary[1] == summary[2] == calibration[1]
                          and len(denials) == int(calibration[1])
                          and [int(row[0]) for row in denials] == list(range(len(denials)))
                          and all(row[1:] == ("0", "0", "1") for row in denials))
            elif mode == "invalid-degree":
                passed = passed and len(re.findall(r"^count_degree_guard=degree:-?\d+ unchanged:1\r?$", text, re.M)) == 3
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        record = {
            "instrument": instrument, "mode": mode, "exit_code": process.returncode,
            "passed": bool(passed), "log_sha256": hashlib.sha256(data).hexdigest(),
            "retained_blocks": int(retained[1]) if retained else None,
            "retained_bytes": int(retained[2]) if retained else None,
            "observations": [line for line in text.splitlines()
                             if line.startswith(("count_", "allocation_hook_control="))],
        }
        results.append(record)
        print(json.dumps({key: value for key, value in record.items() if key != "observations"}), flush=True)
    report = {
        "status": "passed" if all(case["passed"] for case in results) else "failed",
        "scope": "Actual triangle-count helper, construction and dependency units. Original uses a verified extracted CalculateNumbersTriangle body with a minimal class/factory interface adapter, not the full ChargeEstimateProcess TU. Plane/bilinear degree 1/2/4, seven graph layouts, exact borrowed point/parameter/adjacency list-node/scalar identity, a live preceding mesh, repeated calls and 0/-1/INT_MIN guards. Complete candidate actual-wrapper allocation sweeps require nonallocating failure cleanup and zero live/final CRT deltas. Original successful calibration itself leaks its private mesh and fails restoration; its terminal CRT deltas include that calibration retention. Per-denial live deltas independently measure exceptional cleanup; original sweeps stop at their first live mismatch, so later ordinals are unmeasured. Repeated-incidence and deliberately independent parameter-list fixtures qualify lifetime, not geometric consistency. No evaluator scratch rollback, CLI retry, area/error wrapper, arbitrary patch callback, parallel or full-process qualification.",
        "executables": {name: {"path": str(path.resolve()),
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for name, path in instruments},
        "cases": results,
    }
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
