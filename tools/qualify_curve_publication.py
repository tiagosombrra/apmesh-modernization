#!/usr/bin/env python3
"""Qualify per-curve Generator sample publication and collective rollback ownership."""

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
    cases += [(instrument,exe,"abort-"+variant,None) for instrument,exe in [("asan",asan),("crt",crt)] for variant in variants]
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
                passed=passed and f"publication_normal=kind:{k} variant:{v} " in text and len(re.findall(r"^publication_point=",text,re.M))>=2 and "publication_cache=" in text
            elif mode.startswith("failure-"):
                k,v=mode.split("-")[1:]
                groups=re.findall(r"publication_failure_sites=kind:(\d) variant:(\d) denied:(\d+)/(\d+) retry:1 consumed:(\d+) surface:(\d+)",text)
                passed=passed and len(groups)==1 and all(kind==k and variant==v and int(denied)==int(total)>0 and 0<int(consumed)<int(total) and int(surface)>0 for kind,variant,denied,total,consumed,surface in groups)
                if groups:passed=passed and re.findall(r"publication_inject=ordinal:(\d+)",text)==[str(i) for i in range(int(groups[0][3]))]
                passed=passed and f"publication_final_edge=kind:{k} variant:{v} " in text and "restored:1" in text
            elif mode.startswith("abort-"):
                k,v=mode.split("-")[1:]
                passed=passed and f"publication_abort=kind:{k} variant:{v} restored:1 retry:1" in text
            elif mode=="return-move-control":passed=passed and "return_move_control=detected" in text
            else:passed=passed and "allocation_hook_control=detected" in text
        result = {"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                  "expected_diagnostic": diagnostic, "passed": passed,
                  "retained_blocks": int(retained[1]) if retained else None,
                  "retained_bytes": int(retained[2]) if retained else None,
                  "observations": [line for line in text.splitlines() if line.startswith(
                      ("publication_", "allocation_hook_control=", "return_move_control="))],
                  "log_sha256": hashlib.sha256(data).hexdigest()}
        results.append(result)
        print(json.dumps(result), flush=True)
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "scope": "Actual per-curve publication template and RAII guard with actual sample/rebuild/curve/node units. Original uses pinned production units plus a verified publication-block adapter. Controlled callbacks use actual sample tails and a pre-sort capture/list-reversal mutation; upstream numerical selection and full historical Generator/Adapter TUs are not instrumented. Source/cache samples borrowed, exact list/cache rollback, collective new-sample cleanup, ID prefix consumption, retry and post-rebuild handoff. Optional NRVO disabled and Debug iterator metadata disabled only for the new target; actual CRT heap and negative controls retained. Earlier-curve/initial graph lifetime, evaluator scratch and full AdaptCurve/mesh/history/budget rollback remain unqualified.",
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
