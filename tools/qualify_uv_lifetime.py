#!/usr/bin/env python3
"""Qualify real UV lifecycle scenarios with MSVC ASan and separate Debug CRT controls."""

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
    valid = ["normal", "partial", "failure", "exception", "topology-failure", "pending-tree",
             "transfer-contract", "transfer-order", "midpoint-alias", "contracts",
             "primitive-contracts", "face-alias-cache", "registration-contracts",
             "unowned-edge-query", "unowned-face-query"]
    cases = [(kind, executable, mode, None) for kind, executable in [("asan", asan), ("crt", crt)]
             for mode in valid]
    cases += [("crt", crt, "teardown-allocation", None),
              ("crt", crt, "allocation-hook-control", None),
              ("crt", crt, "transfer-allocation-failure", None),
              ("crt", crt, "edge-construction-failure", None),
              ("crt", crt, "face-construction-failure", None),
              ("crt", crt, "front-construction-failure", None),
              ("crt", crt, "edge-cache-failure", None),
              ("crt", crt, "face-cache-failure", None),
              *[("crt", crt, mode, None) for mode in (
                  "boundary-first-failure", "boundary-append-failure", "boundary-close-failure",
                  "face-quality-failure", "outer-vertex-failure", "outer-edge-failure",
                  "template-one-failure", "template-four-failure")],
              ("asan", asan, "use-after-free", "heap-use-after-free"),
              ("asan", asan, "shared-delete", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks")]
    results = []
    for kind, executable, mode, diagnostic in cases:
        timeout = 180 if mode in {"outer-vertex-failure", "outer-edge-failure",
                                  "template-one-failure", "template-four-failure"} else 30
        process = subprocess.run([str(executable.resolve()), mode], env=environment,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        data = process.stdout
        (output / f"{kind}-{mode}.log").write_bytes(data)
        text = data.decode("utf-8", errors="replace")
        retained = re.search(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if diagnostic == "retained-blocks":
            passed = process.returncode == 1 and retained is not None and int(retained[1]) > 0
        elif diagnostic is not None:
            passed = process.returncode != 0 and "ERROR: AddressSanitizer:" in text and diagnostic in text
        else:
            passed = process.returncode == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if kind == "crt":
                passed = passed and retained is not None and int(retained[1]) == int(retained[2]) == 0
            if mode == "teardown-allocation":
                passed = passed and "teardown_allocation_attempts=0" in text
            if mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
            if mode == "transfer-allocation-failure":
                passed = passed and "transfer_allocation_failures=3" in text
            if mode in {"edge-construction-failure", "face-construction-failure",
                        "front-construction-failure", "edge-cache-failure", "face-cache-failure"}:
                sites = re.findall(r"allocation_failure_sites=[\w-]+:(\d+)/(\d+)", text)
                expected_groups = 2 if mode == "face-construction-failure" else 1
                passed = passed and len(sites) == expected_groups and all(
                    int(injected) == int(total) > 0 for injected, total in sites)
                if "cache" in mode:
                    passed = passed and "unchanged=1" in text
            if mode in {"boundary-first-failure", "boundary-append-failure", "boundary-close-failure",
                        "face-quality-failure", "outer-vertex-failure", "outer-edge-failure",
                        "template-one-failure", "template-four-failure"}:
                sites = re.findall(r"registration_failure_sites=[\w-]+:(\d+)/(\d+)", text)
                passed = passed and len(sites) == 1 and all(
                    int(injected) == int(total) > 0 for injected, total in sites)
                if mode.startswith("boundary-"):
                    passed = passed and "unchanged=1" in text
        result = {"instrument": kind, "mode": mode, "exit_code": process.returncode,
                  "expected_diagnostic": diagnostic, "passed": passed,
                  "retained_blocks": int(retained[1]) if retained else None,
                  "retained_bytes": int(retained[2]) if retained else None,
                  "observations": sorted({line for line in text.splitlines() if line.startswith(
                      ("generated_faces=", "template_type_counts=", "templates_before_failure=",
                       "transfer_allocation_failures=", "allocation_hook_control=", "teardown_allocation_attempts=",
                       "allocation_failure_sites=", "registration_failure_sites=", "registration_measured="))}),
                  "log_sha256": hashlib.sha256(data).hexdigest()}
        results.append(result)
        print(json.dumps({key: value for key, value in result.items() if key != "log_sha256"}), flush=True)
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "scope": "14 actual UV/curve/numerical production units; isolated ASan invalid-access and Debug CRT retained-block/allocation-hook coverage. Not full application, LSan, UBSan or arbitrary exception safety.",
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
