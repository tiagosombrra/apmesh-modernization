#!/usr/bin/env python3
"""Qualify scoped release of serial curve samples, including terminal failures."""

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
    instruments = [("asan", asan), ("crt", crt)]
    fixtures = [f"{kind}-{variant}" for kind in range(3) for variant in range(2)]
    cases = [(instrument, executable, f"{mode}-{fixture}", None)
             for instrument, executable in instruments
             for mode in ["normal", "abort", "inner"] for fixture in fixtures]
    cases += [("crt", crt, f"{mode}-{fixture}", None)
              for mode in ["release", "fault"] for fixture in fixtures]
    cases += [(instrument, executable, "guards", None) for instrument, executable in instruments]
    cases += [("asan", asan, "use-after-free", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks"),
              ("crt", crt, "allocation-hook-control", None)]
    results = []
    for instrument, executable, mode, diagnostic in cases:
        process = subprocess.run([str(executable.resolve()), mode], env=environment,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        data = process.stdout
        (output / f"{instrument}-{mode}.log").write_bytes(data)
        text = data.decode("utf-8", errors="replace")
        retained = re.search(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if diagnostic == "heap-use-after-free":
            passed = (process.returncode != 0 and "ERROR: AddressSanitizer:" in text
                      and diagnostic in text)
        elif diagnostic == "retained-blocks":
            passed = process.returncode == 1 and retained is not None and int(retained[1]) > 0
        else:
            passed = (process.returncode == 0 and "PASS" in text
                      and "ERROR: AddressSanitizer:" not in text)
            if instrument == "crt":
                passed = passed and retained is not None and int(retained[1]) == int(retained[2]) == 0
            if mode.startswith(("normal-", "abort-", "inner-", "release-", "fault-")):
                label, kind, variant = mode.split("-")
                observation = re.search(
                    rf"lifetime_result=mode:{label} kind:{kind} variant:{variant} "
                    r"created:(\d+) destroyed:(\d+) empty:1 aliases_cleared:1 caught:(\d+)", text)
                passed = (passed and observation is not None
                          and int(observation[1]) > 0 and observation[1] == observation[2]
                          and int(observation[3]) == int(label in ["abort", "inner", "fault"]))
                if label == "normal":
                    passed = passed and len(re.findall(r"^lifetime_point=", text, re.M)) == 15
                if label in ["release", "fault"]:
                    expected = "attempts:0 denied:0 caught:0" if label == "release" else "attempts:1 denied:1 caught:1"
                    passed = passed and f"lifetime_allocations=mode:{label} {expected}" in text
            elif mode == "guards":
                passed = passed and "lifetime_guard=empty_and_repeat:no_positive_coverage" in text
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        results.append({
            "instrument": instrument, "mode": mode, "exit_code": process.returncode,
            "passed": bool(passed), "log_sha256": hashlib.sha256(data).hexdigest(),
            "retained_blocks": int(retained[1]) if retained else None,
            "retained_bytes": int(retained[2]) if retained else None,
            "observations": [line for line in text.splitlines()
                             if line.startswith(("lifetime_", "allocation_hook_control="))],
        })
        print(json.dumps({key: value for key, value in results[-1].items()
                          if key != "observations"}), flush=True)
    report = {
        "status": "passed" if all(case["passed"] for case in results) else "failed",
        "scope": "Actual scoped sample owner and existing graph/publication/sample/rebuild units; "
                 "three initialized actual curve types with shared non-manifold or distinct endpoints, "
                 "controlled terminal exceptions, inner graph unwinding after committed prefixes, "
                 "actual heap denial before teardown and allocation-denied explicit teardown. "
                 "Physical mesh copies remain independent. Pinned original uses the verbatim "
                 "Generator final cleanup block in an interface adapter, not the full Generator TU. "
                 "No metadata recovery, full CLI failure injection, arbitrary constructor failure, "
                 "unpublished allocations, parallel, full-process, LSan or UBSan qualification.",
        "executables": {name: {"path": str(path.resolve()),
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for name, path in instruments},
        "cases": results,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ["asan", "crt", "runtime", "output"]:
        parser.add_argument("--" + flag, type=Path, required=True)
    args = parser.parse_args()
    report = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({"status": report["status"], "cases": len(report["cases"])}))
    raise SystemExit(0 if report["status"] == "passed" else 1)
