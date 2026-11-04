#!/usr/bin/env python3
"""Qualify SubMesh destruction and move lifetime ordering with actual elements and nodes."""

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
             for name, executable in instruments for variant in range(8)]
    cases += [("crt", crt, f"noalloc-{variant}", None) for variant in range(8)]
    cases += [("asan", asan, "observer-read", None),
              ("asan", asan, "use-after-free", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks"),
              ("crt", crt, "allocation-hook-control", None)]
    cases += [("asan", asan, "patch-observers", None),
              ("crt", crt, "patch-observers", None),
              ("crt", crt, "patch-noalloc", None)]
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
            if mode.startswith(("normal-", "noalloc-")) or mode == "observer-read":
                passed = (passed and len(re.findall(r"^submesh_observed=variant:\d identity:1 ordered:1 complete:1 nodes:\d+ elements:\d+\r?$", text, re.M)) == 1)
                if mode.startswith("noalloc-"):
                    passed = passed and "submesh_allocation=attempts:0 denied:0" in text
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
            elif mode in ("patch-observers", "patch-noalloc"):
                passed = passed and ("patch_observers mesh_first:1 patch_first:1 history:1 "
                                     "rebind:1 foreign:1 moves:1 patch_moves:1") in text
                if mode == "patch-noalloc":
                    passed = passed and "patch_allocation=attempts:0 denied:0" in text
        results.append({"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                        "passed": bool(passed), "log_sha256": hashlib.sha256(data).hexdigest(),
                        "retained_blocks": int(retained[1]) if retained else None,
                        "retained_bytes": int(retained[2]) if retained else None,
                        "observations": [line for line in text.splitlines()
                                         if line.startswith(("submesh_", "patch_", "allocation_hook_control="))]})
        print(json.dumps({key: value for key, value in results[-1].items()
                          if key != "observations"}), flush=True)
        if not passed:
            break
    report = {
        "status": "passed" if all(case["passed"] for case in results) else "failed",
        "scope": "Seven actual patch/mesh/node/element/triangle/point/vector units; "
                 "Eight lifetime layouts cover ordinary destruction, "
                 "move construction, empty/populated destination assignment, populated self-move, empty "
                 "and node-only source, repeated vertices and null slots. Exact identity, adjacency, "
                 "coordinates, curvature, UV, IDs, area and live patch observer identities are checked. "
                 "Eight CRT operations reject every allocation request and require zero attempts, "
                 "including teardown. Actual derived-element destruction consumes borrowed nodes in "
                 "a separate ASan experiment. Real UAF/leak/allocation-hook controls are required. "
                 "Graphs must own their nodes or borrow independently live nodes, with nonthrowing "
                 "destructors. Registered patch observers retire in both teardown orders, including "
                 "history/list removal, rebind, move/source identity and foreign-forward preservation; "
                 "a CRT check denies every allocation during those operations. No arbitrary foreign "
                 "forward repair, cache refresh, full-process/parallel/LSan/UBSan qualification or numerical change.",
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
