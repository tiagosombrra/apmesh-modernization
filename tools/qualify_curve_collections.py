#!/usr/bin/env python3
"""Qualify actual curve collection replacement and copy construction boundaries."""

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
    cases = [("asan", asan, "contracts", None), ("crt", crt, "contracts", None)]
    cases += [("crt", crt, f"{kind}-failure-{variant}", None)
              for kind in ["points", "parameters"] for variant in range(6)]
    cases += [("crt", crt, "base-copy-failure", None),
              ("crt", crt, "parametric-copy-failure", None),
              ("crt", crt, "allocation-hook-control", None),
              ("asan", asan, "use-after-free", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks")]
    results = []
    for instrument, executable, mode, diagnostic in cases:
        process = subprocess.run([str(executable.resolve()), mode], env=environment,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
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
            if mode == "contracts":
                normal = re.findall(r"collection_success=kind:(points|parameters) variant:(\d) values:", text)
                copies = re.findall(r"collection_copy=kind:([01]) borrowed:1", text)
                passed = passed and len(normal) == 14 and set(normal) == {
                    (kind, str(variant)) for kind in ["points", "parameters"] for variant in range(7)}
                passed = passed and sorted(copies) == ["0", "1"]
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
            else:
                groups = re.findall(
                    r"collection_failure_sites=kind:([\w-]+) variant:(\d) denied:(\d+)/(\d+) unchanged=1 retry=1", text)
                expected_kind = mode.rsplit("-failure", 1)[0]
                expected_variant = mode.rsplit("-", 1)[-1] if mode[-1].isdigit() else "0"
                passed = passed and len(groups) == 1 and all(
                    kind == expected_kind and variant == expected_variant and int(denied) == int(total) > 0
                    for kind, variant, denied, total in groups)
                if groups:
                    total = int(groups[0][3])
                    injected = re.findall(r"collection_inject=kind:[\w-]+ variant:\d ordinal:(\d+)", text)
                    passed = passed and injected == [str(index) for index in range(total)]
        result = {"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                  "expected_diagnostic": diagnostic, "passed": passed,
                  "retained_blocks": int(retained[1]) if retained else None,
                  "retained_bytes": int(retained[2]) if retained else None,
                  "observations": [line for line in text.splitlines() if line.startswith(
                      ("collection_success=", "collection_copy=", "collection_measured=",
                       "collection_inject=", "collection_failure_sites=", "allocation_hook_control="))],
                  "log_sha256": hashlib.sha256(data).hexdigest()}
        results.append(result)
        print(json.dumps({key: value for key, value in result.items() if key != "log_sha256"}), flush=True)
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "scope": "Seven actual curve/point/patch/numerical production units; observer collection replacement and two pointer-taking copy constructors. ASan invalid-access and Debug CRT scoped retention/allocation denial; not full application, derived curves, LSan, UBSan or arbitrary exception safety.",
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
