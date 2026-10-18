#!/usr/bin/env python3
"""Qualify ordered curve sample capture and transactional point-graph restoration."""

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
    variants = [f"{k}-{v}" for k in range(4) for v in range(5)]
    capture = [f"{k}-{v}" for k in range(4) for v in range(2)]
    cases = [(instrument, executable, prefix + variant, None)
             for instrument, executable in [("asan", asan), ("crt", crt)]
             for prefix, values in [("normal-", variants), ("capture-", capture)] for variant in values]
    cases += [(instrument, executable, "guards", None) for instrument, executable in [("asan", asan), ("crt", crt)]]
    cases += [("crt", crt, "failure-" + variant, None) for variant in variants]
    cases += [("crt", crt, "capture-failure-" + variant, None) for variant in capture]
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
                unique="3" if v=="1" else "0" if v=="2" else "1" if v=="4" else "4"
                destroyed="4" if int(v)<3 else "0"
                passed=passed and f"snapshot_restore=kind:{k} variant:{v} unique:{unique} old-destroyed:{destroyed} mesh:1 parameters:unchanged" in text
                expected_points=0 if v=="2" else 1 if v=="4" else 9
                passed=passed and len(re.findall(r"^snapshot_point=",text,re.M))==expected_points
            elif mode.startswith("capture-failure-") or mode.startswith("failure-"):
                capture_only=mode.startswith("capture-failure-")
                k,v=mode.removeprefix("capture-failure-" if capture_only else "failure-").split("-")
                groups=re.findall(r"snapshot_failure_sites=kind:(\d) variant:(\d) capture:(\d) denied:(\d+)/(\d+) unchanged:1 retry:1",text)
                passed=passed and len(groups)==1 and all(kind==k and variant==v and capture==str(int(capture_only)) and int(denied)==int(total)>0 for kind,variant,capture,denied,total in groups)
                if groups: passed=passed and re.findall(r"snapshot_inject=ordinal:(\d+)",text)==[str(i) for i in range(int(groups[0][4]))]
            elif mode.startswith("capture-"):
                k,v=mode.removeprefix("capture-").split("-")
                passed=passed and f"snapshot_capture=kind:{k} variant:{v} curves:3 references:9 unchanged:1" in text
            elif mode=="guards": passed=passed and "snapshot_guards=null:1 empty:1 count-mismatch:1" in text
            else: passed=passed and "allocation_hook_control=detected" in text
        result = {"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                  "expected_diagnostic": diagnostic, "passed": passed,
                  "retained_blocks": int(retained[1]) if retained else None,
                  "retained_bytes": int(retained[2]) if retained else None,
                  "observations": [line for line in text.splitlines() if line.startswith(
                      ("snapshot_", "allocation_hook_control="))],
                  "log_sha256": hashlib.sha256(data).hexdigest()}
        results.append(result)
        print(json.dumps(result), flush=True)
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "scope": "Candidate: fifteen actual curve/Geometry/node/mesh/triangle/numerical/snapshot production units. Original: fourteen pinned actual units plus hash-verified original lambda bodies in an adapter, not the full historical generator translation unit. Collectively owned sample graph capture/ID-first restoration, shared/repeated references, duplicate-ID policy controls, empty guards, failure preservation/retry and independent accepted mesh copies. Parameters and full mesh/acceptance rollback are unchanged and unqualified. Debug CRT uses non-debug iterator metadata with actual heap checks; not full application, parallel, LSan or UBSan.",
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
