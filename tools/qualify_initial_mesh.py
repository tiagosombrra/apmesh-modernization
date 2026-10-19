#!/usr/bin/env python3
"""Qualify serial coarse-mesh construction and unpublished resource ownership."""

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
    fixtures = [f"{shape}-{layout}" for shape in range(2) for layout in range(4)]
    cases = [(instrument, executable, "normal-" + fixture, None)
             for instrument, executable in instruments for fixture in fixtures]
    cases += [("crt", crt, "failure-" + fixture, None) for fixture in fixtures]
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
            if mode.startswith("normal-"):
                passed = (passed and len(re.findall(r"^initial_node=", text, re.M)) == 5
                          and len(re.findall(r"^initial_triangle=", text, re.M)) == 4
                          and len(re.findall(r"^initial_sample=", text, re.M)) == 8)
            elif mode.startswith("failure-"):
                shape, layout = mode.split("-")[1:]
                calibration = re.search(rf"initial_measured=shape:{shape} layout:{layout} allocations:(\d+)", text)
                summary = re.search(rf"initial_failure_sites=shape:{shape} layout:{layout} denied:(\d+)/(\d+)", text)
                denials = re.findall(r"initial_denied=shape:\d layout:\d ordinal:(\d+) consumed:(\d+) elements:(\d+) retained:(\d+)", text)
                passed = (passed and calibration is not None and summary is not None
                          and int(calibration[1]) > 0 and summary[1] == summary[2] == calibration[1]
                          and len(denials) == int(calibration[1])
                          and [int(row[0]) for row in denials] == list(range(len(denials)))
                          and all(row[3] == "0" for row in denials))
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        results.append({
            "instrument": instrument, "mode": mode, "exit_code": process.returncode,
            "passed": bool(passed), "log_sha256": hashlib.sha256(data).hexdigest(),
            "retained_blocks": int(retained[1]) if retained else None,
            "retained_bytes": int(retained[2]) if retained else None,
            "observations": [line for line in text.splitlines()
                             if line.startswith(("initial_", "allocation_hook_control="))],
        })
        print(json.dumps({key: value for key, value in results[-1].items()
                          if key != "observations"}), flush=True)
    report = {
        "status": "passed" if all(case["passed"] for case in results) else "failed",
        "scope": "Actual extracted serial InitialMesh implementation, real Bezier patch/curves, "
                 "nodes/triangles/SubMesh and published-sample lifetime. Original uses the verbatim "
                 "function body in a minimal class/result interface adapter, not the full Generator TU. "
                 "Planar/bilinear surfaces, fresh/partially initialized/initialized reversed curves, "
                 "independent analytic coordinates, ordered node/triangle/UV traces, complete observed "
                 "allocation sweeps and actual ASan UAF/CRT leak/hook controls. "
                 "Terminal failure cleans resources without metadata/curve/ID rollback. "
                 "Fixture setup, general mesh adoption, parallel and full-process memory remain outside scope.",
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
