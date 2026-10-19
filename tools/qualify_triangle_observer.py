#!/usr/bin/env python3
"""Qualify stable triangle identity and allocation-free first-vertex observer replacement."""

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
    cases += [("crt", crt, f"noalloc-{variant}", None) for variant in range(8)]
    cases += [(name, executable, mode, None) for name, executable in instruments for mode in ["identity", "guards"]]
    cases += [
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
                passed = (passed and len(re.findall(r"^observer_replacement=variant:\d preserved:1 rejected:[01]\r?$", text, re.M)) == 1)
                if mode.startswith("noalloc-"):
                    passed = passed and "observer_allocation=attempts:0 denied:0" in text
            elif mode == "identity":
                passed = passed and "observer_identity=copy:0 assign:0 move:0 move_assign:0 unregistered_copy:0" in text
            elif mode == "guards":
                passed = passed and "observer_guards=preserved:1" in text
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        results.append({"instrument": instrument, "mode": mode, "exit_code": process.returncode,
                        "passed": bool(passed), "log_sha256": hashlib.sha256(data).hexdigest(),
                        "retained_blocks": int(retained[1]) if retained else None,
                        "retained_bytes": int(retained[2]) if retained else None,
                        "observations": [line for line in text.splitlines()
                                         if line.startswith(("observer_", "allocation_hook_control="))]})
        print(json.dumps({key: value for key, value in results[-1].items()
                          if key != "observations"}), flush=True)
    report = {
        "status": "passed" if all(case["passed"] for case in results) else "failed",
        "scope": "Five actual Node/Point/Element/Triangle/Vector units and the same probe against "
                 "Git-pinned original and candidate. Stable noncopyable/nonmovable identity; first "
                 "matching vertex replacement transfers one physical observer list node without "
                 "allocating. Distinct/repeated/merged vertices, null parent markers, list-node/order "
                 "identity, all cached fields and UV/ID/scalar state, no-op/missing/null/default guards, "
                 "chained replacement and eight zero-allocation paths. Deliberate UAF/leak/hook "
                 "controls required. Ordinary triangle destruction remains empty. Cached geometry "
                 "is not recomputed; no geometric-validity claim after coordinate-changing replacement. "
                 "Public API tightening does not constitute whole-process/parallel/LSan/UBSan safety.",
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
