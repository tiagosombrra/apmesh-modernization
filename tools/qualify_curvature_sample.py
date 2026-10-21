#!/usr/bin/env python3
"""Qualify actual curvature sample lifetime and zero-allocation boundaries."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def qualify(asan, crt, runtime, output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    environment["PATH"] = str(runtime) + os.pathsep + environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
    cases = []
    for instrument, executable in [("asan", asan), ("crt", crt)]:
        cases.append((instrument, executable, "contracts", None))
        for shape in range(3):
            for count in [4, 9, 17, 25]:
                for repeats in [1, 3]:
                    cases.append((instrument, executable, f"normal-{shape}-{count}-{repeats}", None))
    for shape in range(3):
        for count in [4, 9, 17, 25]:
            cases.append(("crt", crt, f"noalloc-{shape}-{count}-0", None))
            for step in range(1, 2 * count + 1):
                cases.append(("asan", asan, f"throw-{shape}-{count}-{step}", None))
                cases.append(("crt", crt, f"noalloc-{shape}-{count}-{step}", None))
    cases += [("asan", asan, "use-after-free", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks"),
              ("crt", crt, "allocation-hook-control", None)]
    assert len(cases) == 725, "Review the fixed qualification inventory"
    report = {"status": "running", "cases": [], "expected_outcomes": 725,
              "executables": {label: {"path": str(path.resolve()),
                  "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                  for label, path in [("asan", asan), ("crt", crt)]},
              "scope": "Actual sampler, curvature and patch dependencies; 3 valid surfaces and 4 sample levels, repetition, all 330 sampled forward/inverse exception positions and 342 measured zero-allocation operations. Contracts additionally cover threshold gaps and integer extremes. Only caller-level Parameterize/FindUV boundaries are injected; internal solver iterations, arbitrary overriding callbacks, other numerical helpers, full-process/parallel/LSan/UBSan and scientific validity remain separate. ASan leak detection is disabled; Debug CRT supplies independent retention measurement."}
    for instrument, executable, mode, diagnostic in cases:
        log = output / f"{instrument}-{mode}.log"
        timed_out = False
        with log.open("xb") as stream:
            try:
                process = subprocess.run([str(executable.resolve()), mode], cwd=output,
                    env=environment, stdout=stream, stderr=subprocess.STDOUT, timeout=30)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                exit_code, timed_out = None, True
        data = log.read_bytes()
        text = data.decode("utf-8", errors="replace")
        retained = re.findall(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if diagnostic == "heap-use-after-free":
            passed = exit_code not in [None, 0] and "ERROR: AddressSanitizer:" in text and diagnostic in text
        elif diagnostic == "retained-blocks":
            passed = exit_code == 1 and len(retained) == 1 and int(retained[0][0]) > 0
        else:
            passed = exit_code == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if instrument == "crt":
                passed = passed and retained == [("0", "0")]
            if mode.startswith("noalloc-"):
                passed = passed and "sample_noalloc=attempts:0 denied:0 " in text
            if mode.startswith("normal-"):
                repeats = int(mode.rsplit("-", 1)[1])
                count = int(mode.split("-")[2])
                passed = passed and text.count("sample_result=") == repeats
                passed = passed and text.count("sample_event=") == 2 * count * repeats
            if mode.startswith("throw-"):
                step = int(mode.rsplit("-", 1)[1])
                passed = passed and text.count("sample_result=") == 1 and text.count("sample_event=") == step
                passed = passed and "caught:1" in text
            if mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        report["cases"].append({"instrument": instrument, "mode": mode, "passed": bool(passed),
            "exit_code": exit_code, "timed_out": timed_out, "expected_diagnostic": diagnostic,
            "log_sha256": hashlib.sha256(data).hexdigest(), "retained": retained,
            "observations": [line for line in text.splitlines() if line.startswith("sample_")]})
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    report["failed_cases"] = sum(not case["passed"] for case in report["cases"])
    report["status"] = "failed" if report["failed_cases"] else "passed"
    report["zero_allocation_operations"] = sum(case["mode"].startswith("noalloc-") and case["passed"] for case in report["cases"])
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["asan", "crt", "runtime", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({name: report[name] for name in ["status", "expected_outcomes", "failed_cases", "zero_allocation_operations"]}))
    raise SystemExit(report["status"] != "passed")
