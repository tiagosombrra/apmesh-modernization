#!/usr/bin/env python3
"""Qualify curve cloning, publication and per-curve graph failure recovery."""

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
    graph = [f"{k}-{v}" for k in range(4) for v in range(4)]
    helpers = [f"{k}-{v}" for k in range(4) for v in range(2)]
    cases = [(instrument, executable, prefix + variant, None)
             for instrument, executable in [("asan", asan), ("crt", crt)]
             for prefix, variants in [("normal-", graph), ("helper-", helpers)] for variant in variants]
    cases += [(instrument, executable, "guards", None)
              for instrument, executable in [("asan", asan), ("crt", crt)]]
    cases += [("crt", crt, "failure-" + variant, None) for variant in graph]
    cases += [("crt", crt, f"helper-failure-{k}-0", None) for k in range(4)]
    cases += [("crt", crt, "allocation-hook-control", None),
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
            if mode.startswith("normal-"):
                k, v = mode.removeprefix("normal-").split("-")
                clones = "0" if v == "3" else "2" if v == "0" else "4"
                passed = passed and f"sync_graph=kind:{k} variant:{v} committed:2 clones:{clones} orientation:1 values:1" in text
            elif mode.startswith("helper-failure-") or mode.startswith("failure-"):
                direct = mode.startswith("helper-failure-")
                k, v = mode.removeprefix("helper-failure-" if direct else "failure-").split("-")
                groups = re.findall(r"sync_failure_sites=kind:(\d) variant:(\d) direct:(\d) denied:(\d+)/(\d+) prefix:(\d+) retry:1", text)
                passed = passed and len(groups) == 1 and all(
                    kind == k and variant == v and d == str(int(direct)) and int(denied) == int(total) > 0 and (direct or int(prefix) > 0)
                    for kind, variant, d, denied, total, prefix in groups)
                if groups:
                    injected = re.findall(r"sync_inject=ordinal:(\d+)", text)
                    passed = passed and injected == [str(i) for i in range(int(groups[0][4]))]
            elif mode.startswith("helper-"):
                k, v = mode.removeprefix("helper-").split("-")
                passed = passed and f"sync_helper=kind:{k} null:{v} values:1 lifetime:1" in text
            elif mode == "guards":
                passed = passed and "sync_guards=null-source:1 null-geometry:1 filtered-singleton:1" in text
            else:
                passed = passed and "allocation_hook_control=detected" in text
        result = {"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                  "expected_diagnostic": diagnostic, "passed": passed,
                  "retained_blocks": int(retained[1]) if retained else None,
                  "retained_bytes": int(retained[2]) if retained else None,
                  "observations": [line for line in text.splitlines() if line.startswith(
                      ("sync_", "allocation_hook_control="))],
                  "log_sha256": hashlib.sha256(data).hexdigest()}
        results.append(result)
        print(json.dumps(result), flush=True)
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "scope": "Candidate: thirteen actual Geometry/curve/patch/numerical/synchronization production units. Original: twelve pinned actual units and a mechanically extracted, hash-verified adapter of the original generator functions, not the full historical generator translation unit. Actual PatchBezier orientation/control-net and repeated-edge incidences, per-original-curve publication, committed prefixes and whole-operation retry. Not adaptive rollback, full CLI synchronization-disabled campaign, full application, parallel, LSan or UBSan.",
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
