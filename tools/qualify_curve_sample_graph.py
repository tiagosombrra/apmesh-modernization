#!/usr/bin/env python3
"""Qualify complete serial curve sample graph ownership and rollback."""

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
    variants=[f"{k}-{v}" for k in range(3) for v in range(6)]
    instruments=[("asan",asan),("crt",crt)]
    cases=[(instrument,exe,"normal-"+v,None) for instrument,exe in instruments for v in variants]
    cases += [("crt",crt,"failure-"+v,None) for v in variants]
    cases += [(instrument,exe,"abort-"+stop+"-"+v,None) for instrument,exe in instruments for stop in ["prefix","surface"] for v in variants]
    cases += [(instrument,exe,f"abort-before-{k}-0",None) for instrument,exe in instruments for k in range(3)]
    cases += [("crt",crt,"retention-"+v,None) for v in variants]
    cases += [(instrument,exe,"guards",None) for instrument,exe in instruments]
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
                k,v=mode.split("-")[1:]
                passed=passed and len(re.findall(r"^graph_normal=kind:"+k+" variant:"+v+r" curves:4 ",text,re.M))==2 and len(re.findall(r"^graph_point=",text,re.M))==40
            elif mode.startswith("failure-"):
                k,v=mode.split("-")[1:]
                groups=re.findall(r"graph_failure_sites=kind:(\d) variant:(\d) denied:(\d+)/(\d+) retry:1 prefixes:(\d+) consumed:(\d+)",text)
                passed=passed and len(groups)==1 and all(kind==k and variant==v and int(denied)==int(total)>0 and int(prefixes)>0 and 0<int(consumed)<int(total) for kind,variant,denied,total,prefixes,consumed in groups)
                if groups:passed=passed and re.findall(r"graph_inject=ordinal:(\d+)",text)==[str(i) for i in range(int(groups[0][3]))]
                passed=passed and f"graph_final_edge=kind:{k} variant:{v} prefix:3 " in text and "restored:1" in text
            elif mode.startswith(("abort-","retention-")):
                retention=mode.startswith("retention-")
                k,v=mode.split("-")[-2:]
                stop=1+int(v)%4 if retention or mode.startswith("abort-prefix-") else 20+int(v)%4 if mode.startswith("abort-surface-") else 0
                passed=passed and f"graph_abort=kind:{k} variant:{v} stop:{stop} retention:{int(retention)} orphaned:0 retry:{int(not retention)}" in text
            elif mode=="guards":
                passed=passed and "graph_guards=empty_commit_and_abort:no_positive_graph_coverage" in text
            elif mode=="return-move-control":passed=passed and "return_move_control=detected" in text
            else:passed=passed and "allocation_hook_control=detected" in text
        result = {"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                  "expected_diagnostic": diagnostic, "passed": passed,
                  "retained_blocks": int(retained[1]) if retained else None,
                  "retained_bytes": int(retained[2]) if retained else None,
                  "observations": [line for line in text.splitlines() if line.startswith(
                      ("graph_", "allocation_hook_control=", "return_move_control="))],
                  "log_sha256": hashlib.sha256(data).hexdigest()}
        results.append(result)
        print(json.dumps(result), flush=True)
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "scope": "Actual complete-loop point/parameter graph guard, actual per-curve publication/sample/rebuild operations, Geometry and independent physical SubMesh. Original uses pinned actual units plus a verified verbatim initial-capture/final-retirement interface adapter, not full historical Generator/Adapter TUs or upstream numerical selection. Four curves, shared non-manifold/reversed/closed/distinct/two-endpoint/mixed-type graph layouts, later operations and actual analytic interiors; positive full allocation sweeps, committed prefixes, initial objects retained until commit, exact original graph/list-node restoration and retry, ID prefix consumption and deliberate ASan/CRT controls. Retention-only originals reclaim only current reachable graph samples, preserving orphan leaks without rollback/retry claims. New target consistently disables optional NRVO/Debug iterator metadata with actual heap checks and prior target settings retained. Empty graph is an explicit guard, not positive graph qualification. Evaluator scratch and orchestration metadata/error/history/budget/patch/mesh/acceptance rollback, full-process/parallel/LSan/UBSan remain unqualified.",
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
