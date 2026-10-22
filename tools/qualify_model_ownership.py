#!/usr/bin/env python3
"""Qualify actual Model adoption, transfer, failed growth and retirement."""
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
    modes = ["contracts", "lifetime"] + [f"trace-{i}" for i in range(8)] + [f"move-{i}" for i in range(5)]
    cases = [(name, exe, mode) for name, exe in instruments for mode in modes]
    cases += [("crt", crt, f"failure-{i}") for i in range(8)]
    cases += [("crt", crt, f"noalloc-{i}") for i in range(12)]
    cases += [("asan", asan, "uaf-control"), ("crt", crt, "leak-control"), ("crt", crt, "hook-control")]
    cases += [(name, exe, mode) for name, exe in instruments for mode in ["order-control", "adjacency-control"]]
    results = []
    for instrument, executable, mode in cases:
        process = subprocess.run([str(executable.resolve()), mode], env=environment,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        data = process.stdout
        (output/f"{instrument}-{mode}.log").write_bytes(data)
        text = data.decode("utf-8", errors="replace")
        retained = re.search(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if mode == "uaf-control":
            passed = process.returncode != 0 and "ERROR: AddressSanitizer:" in text and "heap-use-after-free" in text
        elif mode == "leak-control":
            passed = process.returncode == 1 and retained is not None and int(retained[1]) > 0 and int(retained[2]) > 0
        elif mode in ["order-control", "adjacency-control"]:
            diagnostic = "reverse mesh retirement" if mode == "order-control" else "live triangle adjacency"
            passed = process.returncode == 2 and "Model ownership contract failed: " + diagnostic in text
        else:
            passed = process.returncode == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if instrument == "crt":
                passed = passed and retained is not None and int(retained[1]) == int(retained[2]) == 0
            if mode.startswith("failure-"):
                variant = mode.split("-")[1]
                measured = re.search(rf"model_measured={variant},allocations:(\d+)", text)
                summary = re.search(rf"model_sweep={variant},denied:(\d+)/(\d+)", text)
                denials = re.findall(rf"model_denied={variant},ordinal:(\d+),attempts:(\d+),retained:0,bytes:0,prefix:1,reuse:1", text)
                passed = (passed and measured is not None and summary is not None and int(measured[1]) > 0
                          and summary[1] == summary[2] == measured[1] and len(denials) == int(measured[1])
                          and [int(row[0]) for row in denials] == list(range(len(denials)))
                          and all(int(a)+1 == int(b) for a, b in denials))
            elif mode.startswith("noalloc-"):
                passed = passed and f"model_noalloc={mode.split('-')[1]},attempts:0" in text
            elif mode == "hook-control":
                passed = passed and "model_hook=detected" in text
        results.append({"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                        "passed": bool(passed), "log_sha256": hashlib.sha256(data).hexdigest(),
                        "retained_blocks": int(retained[1]) if retained else None,
                        "retained_bytes": int(retained[2]) if retained else None,
                        "observations": [line for line in text.splitlines() if line.startswith("model_")]})
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "scope": "Actual Model and fourteen dependency units; raw/owning, empty/seeded/null append, all calibrated growth allocations, live committed prefixes and subsequent reuse, borrowed Geometry, reverse retirement, supported move/self-move and real instrument/oracle controls. Duplicate/foreign ownership, derived-base deletion, caller preparation, patch rebinding, parallel/full-process/LSan/UBSan remain outside scope.",
              "executables": {name: {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for name, path in instruments},
              "complete_sweeps": sum(case["passed"] and case["mode"].startswith("failure-") for case in results),
              "allocation_denials": sum(line.startswith("model_denied=") for case in results for line in case["observations"]),
              "zero_allocation_operations": sum(case["passed"] and case["mode"].startswith("noalloc-") for case in results),
              "cases": results}
    (output/"report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ["asan", "crt", "runtime", "output"]:
        parser.add_argument("--"+flag, type=Path, required=True)
    args = parser.parse_args()
    report = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({"status": report["status"], "cases": len(report["cases"]),
                      "sweeps": report["complete_sweeps"], "denials": report["allocation_denials"],
                      "noalloc": report["zero_allocation_operations"],
                      "failed": [(c["instrument"], c["mode"]) for c in report["cases"] if not c["passed"]]}))
    raise SystemExit(0 if report["status"] == "passed" else 1)
