#!/usr/bin/env python3
"""Qualify initialized pointer-taking parametric, Bezier and Hermite copies."""

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
    cases = [(instrument, executable, f"copy-{kind}-{variant}", None)
             for instrument, executable in [("asan", asan), ("crt", crt)]
             for kind in range(3) for variant in range(3)]
    cases += [("crt", crt, f"failure-{kind}-{variant}", None)
              for kind in range(3) for variant in range(3)]
    cases += [("crt", crt, "allocation-hook-control", None),
              ("asan", asan, "use-after-free", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks")]
    results = []
    for instrument, executable, mode, diagnostic in cases:
        try:
            process = subprocess.run([str(executable.resolve()), mode], env=environment,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        except subprocess.TimeoutExpired as error:
            data = error.stdout or b""
            (output / f"{instrument}-{mode}.log").write_bytes(data)
            results.append({"instrument": instrument, "mode": mode, "exit_code": None,
                            "expected_diagnostic": diagnostic, "passed": False,
                            "timeout_seconds": 30, "log_sha256": hashlib.sha256(data).hexdigest()})
            break
        data = process.stdout
        (output / f"{instrument}-{mode}.log").write_bytes(data)
        text = data.decode("utf-8", errors="replace")
        retained = re.search(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if diagnostic == "heap-use-after-free":
            passed = process.returncode != 0 and "ERROR: AddressSanitizer:" in text and diagnostic in text
        elif diagnostic == "retained-blocks":
            passed = process.returncode == 1 and retained is not None and int(retained[1]) > 0
        else:
            passed = process.returncode == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if instrument == "crt":
                passed = passed and retained is not None and int(retained[1]) == int(retained[2]) == 0
            if mode.startswith("copy-"):
                _, kind, variant = mode.split("-")
                expected_size = "0" if variant == "0" else "5"
                values = re.findall(r"copy_values=kind:(\d) variant:(\d) parameters:(\d+) pairs:(\d+) independent:1", text)
                passed = passed and values == [(kind, variant, expected_size, expected_size)]
                geometry = re.findall(r"copy_geometry=kind:(\d) variant:(\d) sample:(\d) x:\S+ gradient:\S+", text)
                passed = passed and geometry == [(kind, variant, str(i)) for i in range(5)]
                arcs = re.findall(r"copy_arc=kind:(\d) variant:(\d) value:\S+ reverse:\S+", text)
                passed = passed and arcs == [(kind, variant)]
                lifetimes = re.findall(r"copy_lifetimes=kind:(\d) variant:(\d) copy-first:1 source-first:1", text)
                passed = passed and lifetimes == [(kind, variant)]
            elif mode.startswith("failure-"):
                _, kind, variant = mode.split("-")
                groups = re.findall(r"copy_failure_sites=kind:(\d) variant:(\d) denied:(\d+)/(\d+) unchanged=1 retry=1", text)
                passed = passed and len(groups) == 1 and all(
                    k == kind and v == variant and int(denied) == int(total) > 0
                    for k, v, denied, total in groups)
                if groups:
                    injected = re.findall(r"copy_inject=kind:\d variant:\d ordinal:(\d+)", text)
                    passed = passed and injected == [str(i) for i in range(int(groups[0][3]))]
            else:
                passed = passed and "allocation_hook_control=detected" in text
        result = {"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                  "expected_diagnostic": diagnostic, "passed": passed,
                  "retained_blocks": int(retained[1]) if retained else None,
                  "retained_bytes": int(retained[2]) if retained else None,
                  "observations": [line for line in text.splitlines() if line.startswith(
                      ("copy_geometry=", "copy_arc=", "copy_values=", "copy_lifetimes=", "copy_measured=",
                       "copy_inject=", "copy_failure_sites=", "allocation_hook_control="))],
                  "log_sha256": hashlib.sha256(data).hexdigest()}
        results.append(result)
        print(json.dumps({key: value for key, value in result.items() if key != "log_sha256"}), flush=True)
        if not passed:
            break
    report = {"status": "passed" if len(results) == len(cases) and all(case["passed"] for case in results) else "failed",
              "expected_cases": len(cases), "completed_cases": len(results),
              "scope": "Nine actual curve/point/patch/numerical production units. Initialized non-null pointer-taking copies, independent containers and borrowed-object lifetimes; ASan invalid-access and Debug CRT scoped retention/allocation denial. Not implicit copy/assignment, clone publication, full application, parallel, LSan or UBSan.",
              "executables": {kind: {"path": str(path.resolve()),
                                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                              for kind, path in [("asan", asan), ("crt", crt)]},
              "cases": results}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asan", type=Path, required=True)
    parser.add_argument("--crt", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({"status": report["status"], "cases": len(report["cases"])}))
    raise SystemExit(0 if report["status"] == "passed" else 1)
