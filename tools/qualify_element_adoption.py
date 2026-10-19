#!/usr/bin/env python3
"""Qualify element adoption and strict failure cleanup by the actual SubMesh units."""

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
             for name, executable in instruments for variant in range(8)]
    cases += [("crt", crt, f"failure-{variant}", None) for variant in range(8)]
    cases += [("crt", crt, f"noalloc-{variant}", None) for variant in [1, 3, 5, 7]]
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
            if mode.startswith("normal-"):
                passed = (passed and len(re.findall(r"^element_observed=", text, re.M)) == 1
                          and len(re.findall(r"^element_node=", text, re.M)) == 3
                          and len(re.findall(r"^element_triangle=", text, re.M)) == int(mode[-1]) % 2 + (int(mode[-1]) % 4 < 2))
            elif mode.startswith("failure-"):
                variant = mode.split("-")[1]
                measured = re.search(rf"element_measured=variant:{variant} prefix:\d+ allocations:(\d+)", text)
                summary = re.search(rf"element_failure_sites=variant:{variant} denied:(\d+)/(\d+)", text)
                denials = re.findall(r"element_denied=variant:\d ordinal:(\d+) attempts:(\d+) "
                                     r"complete:(\d+) retained:(\d+) bytes:(\d+)", text)
                passed = (passed and measured is not None and summary is not None
                          and int(measured[1]) > 0 and summary[1] == summary[2] == measured[1]
                          and len(denials) == int(measured[1])
                          and [int(row[0]) for row in denials] == list(range(len(denials)))
                          and all(int(row[1]) == int(row[0]) + 1 and row[2:] == ("1", "0", "0")
                                  for row in denials))
            elif mode.startswith("noalloc-"):
                passed = passed and re.search(rf"element_noalloc=variant:{mode.split('-')[1]} prefix:[1-9]\d* attempts:0", text) is not None
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        results.append({"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                        "passed": bool(passed), "log_sha256": hashlib.sha256(data).hexdigest(),
                        "retained_blocks": int(retained[1]) if retained else None,
                        "retained_bytes": int(retained[2]) if retained else None,
                        "observations": [line for line in text.splitlines()
                                         if line.startswith(("element_", "allocation_hook_control="))]})
        print(json.dumps({key: value for key, value in results[-1].items()
                          if key != "observations"}), flush=True)
    report = {
        "status": "passed" if all(case["passed"] for case in results) else "failed",
        "scope": "Six actual SubMesh/node/triangle production units and the current probe. "
                 "Slice 24 strengthens the failure oracle to require an exact live observer prefix; "
                 "historical slice-20 original reports retain their own probe/source scope and hashes. "
                 "Raw SetElement and owning AddElement, "
                 "empty/populated/null/spare-storage insertion; analytic coordinates/area, IDs/UV, "
                 "ordered slot and successful adjacency identity, move construction, exact single "
                 "destruction and element-before-node terminal teardown. Every measured growth "
                 "ordinal denied once; full fixture owner unwinds before caller handles failure. "
                 "Existing owned prefix and exact observer cleanup are required before rethrow; "
                 "the failed argument is consumed, not reusable. This terminal driver does not "
                 "perform fresh adoption; the paired slice-24 actual-unit probe separately does. "
                 "Constructor-before-entry failures, "
                 "arbitrary subclasses, full-process/parallel memory and estimator root owners remain "
                 "unqualified. Actual ASan UAF/CRT leak/hook controls are required.",
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
