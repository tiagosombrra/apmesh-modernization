#!/usr/bin/env python3
"""Qualify exclusive SubMesh adoption by the actual MeshAdaptive source unit."""

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
    cases = [(name, executable, f"normal-{variant}", None)
             for name, executable in instruments for variant in range(11)]
    cases += [("crt", crt, f"failure-{variant}", None) for variant in [0, 1, 2, 3, 8, 9]]
    cases += [("crt", crt, f"noalloc-{variant}", None) for variant in [4, 5, 6, 7, 10]]
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
            passed = (process.returncode != 0 and "ERROR: AddressSanitizer:" in text
                      and diagnostic in text)
        elif diagnostic == "retained-blocks":
            passed = process.returncode == 1 and retained is not None and int(retained[1]) > 0
        else:
            passed = (process.returncode == 0 and "PASS" in text
                      and "ERROR: AddressSanitizer:" not in text)
            if instrument == "crt":
                passed = passed and retained is not None and int(retained[1]) == int(retained[2]) == 0
            if mode.startswith("normal-") and mode not in ["normal-6", "normal-7"]:
                passed = passed and len(re.findall(r"^mesh_observed=", text, re.M)) == 1
            elif mode.startswith("failure-"):
                variant = mode.split("-")[1]
                measured = re.search(rf"mesh_measured=variant:{variant} allocations:(\d+)", text)
                summary = re.search(rf"mesh_failure_sites=variant:{variant} denied:(\d+)/(\d+)", text)
                denials = re.findall(r"mesh_denied=variant:\d ordinal:(\d+) attempts:(\d+) "
                                     r"released:(\d+) retained:(\d+) bytes:(\d+)", text)
                passed = (passed and measured is not None and summary is not None
                          and int(measured[1]) > 0 and summary[1] == summary[2] == measured[1]
                          and len(denials) == int(measured[1])
                          and [int(row[0]) for row in denials] == list(range(len(denials)))
                          and all(int(row[1]) == int(row[0]) + 1 and row[2:] == ("1", "0", "0")
                                  for row in denials))
            elif mode.startswith("noalloc-"):
                passed = passed and f"mesh_noalloc=variant:{mode.split('-')[1]} attempts:0 released:1" in text
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        results.append({"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                        "passed": bool(passed), "log_sha256": hashlib.sha256(data).hexdigest(),
                        "retained_blocks": int(retained[1]) if retained else None,
                        "retained_bytes": int(retained[2]) if retained else None,
                        "observations": [line for line in text.splitlines()
                                         if line.startswith(("mesh_", "allocation_hook_control="))]})
        print(json.dumps({key: value for key, value in results[-1].items()
                          if key != "observations"}), flush=True)
    report = {
        "status": "passed" if all(case["passed"] for case in results) else "failed",
        "scope": "Actual MeshAdaptive/SubMesh/node/triangle units; unique raw adoption into "
                 "empty/full/sparse/presized/replacement slots, negative positions, null slots, "
                 "move/removal and independent area/adjacency/destruction-order checks. "
                 "All observed growth allocations denied once, nonallocating paths and actual "
                 "ASan UAF/CRT leak/allocation-hook controls. Original uses Git-pinned actual units "
                 "without an implementation adapter. Invalid duplicate/base-subclass deletion, "
                 "foreign observer rebinding, SubMesh raw element adoption, other constructors, "
                 "parallel/full-process memory and numerical rejection remain outside scope.",
        "executables": {name: {"path": str(path.resolve()),
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for name, path in instruments},
        "cases": results,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ["asan", "crt", "runtime", "output"]:
        parser.add_argument("--" + flag, type=Path, required=True)
    args = parser.parse_args()
    report = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({"status": report["status"], "cases": len(report["cases"])}))
    raise SystemExit(0 if report["status"] == "passed" else 1)
