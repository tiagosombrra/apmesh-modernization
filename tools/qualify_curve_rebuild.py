#!/usr/bin/env python3
"""Qualify paired target-count sample rebuild preparation and allocation recovery."""

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
    variants = [f"{k}-{v}" for k in range(3) for v in range(13)]
    sweeps = [f"{k}-{v}" for k in range(3) for v in range(13) if v!=11]
    cases = [(instrument, executable, "normal-"+variant, None)
             for instrument, executable in [("asan", asan), ("crt", crt)] for variant in variants]
    cases += [("crt", crt, "failure-"+variant, None) for variant in sweeps]
    cases += [("crt", crt, "allocation-hook-control", None), ("asan", asan, "use-after-free", "heap-use-after-free"), ("crt", crt, "leak", "retained-blocks")]
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
            if mode.startswith("normal-"):
                k,v=mode.removeprefix("normal-").split("-")
                passed=passed and f"rebuild_normal=kind:{k} variant:{v} " in text
                if int(v) not in {4,5,6,11}:passed=passed and len(re.findall(r"^rebuild_point=",text,re.M))>=2
            elif mode.startswith("failure-"):
                k,v=mode.removeprefix("failure-").split("-")
                groups=re.findall(r"rebuild_failure_sites=kind:(\d) variant:(\d+) denied:(\d+)/(\d+) unchanged:1 retry:1 ids:consumed",text)
                passed=passed and len(groups)==1 and all(kind==k and variant==v and int(denied)==int(total)>0 for kind,variant,denied,total in groups)
                if groups:passed=passed and re.findall(r"rebuild_inject=ordinal:(\d+)",text)==[str(i) for i in range(int(groups[0][3]))]
            else:passed=passed and "allocation_hook_control=detected" in text
        result = {"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                  "expected_diagnostic": diagnostic, "passed": passed,
                  "retained_blocks": int(retained[1]) if retained else None,
                  "retained_bytes": int(retained[2]) if retained else None,
                  "observations": [line for line in text.splitlines() if line.startswith(
                      ("rebuild_", "allocation_hook_control="))],
                  "log_sha256": hashlib.sha256(data).hexdigest()}
        results.append(result)
        print(json.dumps(result), flush=True)
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "scope": "Candidate: thirteen actual curve/node/numerical/ID-manager/rebuild production units. Original: twelve Git-pinned units plus the verified original lambda with explicit nullable-ID-manager context substitution, not full historical Generator-TU instrumentation. Paired supplied-point/curve-parameter lists, initialized parametric/Bezier/Hermite curves, distinct deletable interiors and borrowed shared endpoints, allocation preservation/retry and consumed-ID behavior. Curve observer publication and full AdaptCurve/mesh rollback remain unqualified. Debug CRT has non-debug iterator metadata and actual heap checks; not full application, parallel, LSan or UBSan.",
              "executables": {kind: {"path": str(path.resolve()),
                                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                              for kind, path in [("asan", asan), ("crt", crt)]},
              "cases": results}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ["asan", "crt", "runtime", "output"]:
        parser.add_argument("--" + flag, type=Path, required=True)
    args = parser.parse_args()
    report = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({"status": report["status"], "cases": len(report["cases"])}))
    raise SystemExit(0 if report["status"] == "passed" else 1)
