#!/usr/bin/env python3
"""Qualify serial adapter sample ownership, cache publication and return failure recovery."""

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
    variants=[f"{k}-{v}" for k in range(3) for v in range(9)]
    cases=[(instrument,executable,"normal-"+variant,None) for instrument,executable in [("asan",asan),("crt",crt)] for variant in variants]
    cases += [("crt",crt,"failure-"+variant,None) for variant in variants]
    cases += [("crt",crt,f"retention-{k}-0",None) for k in range(3)]
    cases += [("crt",crt,"return-move-control",None),("crt",crt,"allocation-hook-control",None),("asan",asan,"use-after-free","heap-use-after-free"),("crt",crt,"leak","retained-blocks")]
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
                passed=passed and f"sample_normal=kind:{k} variant:{v} " in text and len(re.findall(r"^sample_point=",text,re.M))>=2 and "sample_cache=" in text
            elif mode.startswith(("failure-","retention-")):
                retention=mode.startswith("retention-");k,v=mode.split("-")[1:]
                groups=re.findall(r"sample_failure_sites=kind:(\d) variant:(\d) retention:(\d) denied:(\d+)/(\d+) retry:(\d) consumed:(\d+)",text)
                passed=passed and len(groups)==1 and all(kind==k and variant==v and r==str(int(retention)) and int(denied)==int(total)>0 and retry==str(int(not retention)) for kind,variant,r,denied,total,retry,_ in groups)
                if groups:passed=passed and re.findall(r"sample_inject=ordinal:(\d+)",text)==[str(i) for i in range(int(groups[0][4]))]
                if not retention:passed=passed and f"sample_return_edge=kind:{k} variant:{v} " in text and "preserved:1" in text
            elif mode=="return-move-control":passed=passed and "return_move_control=detected" in text
            else:passed=passed and "allocation_hook_control=detected" in text
        result = {"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                  "expected_diagnostic": diagnostic, "passed": passed,
                  "retained_blocks": int(retained[1]) if retained else None,
                  "retained_bytes": int(retained[2]) if retained else None,
                  "observations": [line for line in text.splitlines() if line.startswith(
                      ("sample_", "allocation_hook_control=", "return_move_control="))],
                  "log_sha256": hashlib.sha256(data).hexdigest()}
        results.append(result)
        print(json.dumps(result), flush=True)
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "scope": "Candidate: fifteen actual curve/node/triangle/numerical/ID-manager/sample production units. Original: fourteen pinned units plus one of two verified identical serial Adapter tails, not full old Adapter/Generator instrumentation. Selected parameters, captured endpoints, borrowed cache/source nodes, preserved endpoint scalar/adjacency copy policy, staged cache publication, stable cache entry nodes, consumed IDs and retry. Optional NRVO disabled consistently for the new target to exercise allocating return moves. Debug CRT uses non-debug iterator metadata and actual heap checks. Retention-only experiments reclaim reachable partial original state without claiming rollback/retry; strict cases require preservation. Upstream sorting/parameter selection, evaluator scratch, later Generator point publication and full-process/parallel/LSan/UBSan remain unqualified.",
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
