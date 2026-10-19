#!/usr/bin/env python3
"""Qualify completed-triangle observer cleanup and live-graph failed adoption."""

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
    cases = [(name, executable, f"normal-{variant}", None)
             for name, executable in instruments for variant in range(10)]
    cases += [("crt", crt, f"noalloc-{variant}", None) for variant in [0, 1, 2, 3, 4, 5, 8, 9]]
    cases += [("crt", crt, f"adoption-{variant}", None) for variant in range(4)]
    cases += [("asan", asan, "consume-after-delete", None),
              ("asan", asan, "use-after-free", "heap-use-after-free"),
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
            if mode.startswith(("normal-", "noalloc-")):
                passed = (passed and len(re.findall(r"^lifetime_destroy=variant:\d restored:1\r?$", text, re.M)) == 1)
                if mode.startswith("noalloc-"):
                    passed = passed and "lifetime_allocation=attempts:0 denied:0" in text
            elif mode.startswith("adoption-"):
                variant = mode[-1]
                measured = re.search(rf"lifetime_adoption_measured=variant:{variant} allocations:(\d+)", text)
                summary = re.search(rf"lifetime_adoption_sites=variant:{variant} denied:(\d+)/(\d+) restored:1", text)
                denials = re.findall(r"lifetime_adoption_denied=variant:\d ordinal:(\d+) attempts:(\d+) restored:(\d+) released:(\d+) fresh:(\d+)", text)
                passed = (passed and measured is not None and summary is not None
                          and int(measured[1]) > 0 and summary[1] == summary[2] == measured[1]
                          and len(denials) == int(measured[1])
                          and [int(row[0]) for row in denials] == list(range(len(denials)))
                          and all(int(row[1]) == int(row[0]) + 1 and row[2:] == ("1", "1", "1") for row in denials))
            elif mode == "consume-after-delete":
                passed = passed and "lifetime_consumed=area:3.0 restored:1" in text
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        results.append({"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                        "passed": bool(passed), "log_sha256": hashlib.sha256(data).hexdigest(),
                        "retained_blocks": int(retained[1]) if retained else None,
                        "retained_bytes": int(retained[2]) if retained else None,
                        "observations": [line for line in text.splitlines()
                                         if line.startswith(("lifetime_", "allocation_hook_control="))]})
        print(json.dumps({key: value for key, value in results[-1].items()
                          if key != "observations"}), flush=True)
    report = {
        "status": "passed" if all(case["passed"] for case in results) else "failed",
        "scope": "Six actual SubMesh/Node/Point/Element/Triangle/Vector units, same probe on "
                 "Git-pinned original and candidate. Distinct/reversed/repeated vertices, default "
                 "empty object, completed base destruction after derived failure, virtual deletion, "
                 "equivalent-node and merged replacement. Exact live parent/null/list-node/scalar "
                 "restoration before safe traversal and fresh component construction; eight actual "
                 "zero-allocation destruction paths and four positive raw/owning empty/populated "
                 "vector-growth failure sweeps with consumed argument deletion, exact prior graph "
                 "and fresh adoption. Separate ASan post-delete traversal reproduces original UAF. "
                 "Real UAF/leak/hook controls required. Nodes must outlive their triangles; arbitrary "
                 "protected mutation, foreign copied observer lists, full CLI retry, whole-process/"
                 "parallel/LSan/UBSan and geometry-cache refresh remain unqualified.",
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
