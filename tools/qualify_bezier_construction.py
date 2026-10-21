#!/usr/bin/env python3
"""Qualify actual Bezier constructor ownership and observer restoration."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def qualify(asan, crt, runtime, output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    environment["PATH"] = str(runtime) + os.pathsep + environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
    cases = []
    for instrument, executable in [("asan", asan), ("crt", crt)]:
        cases.extend((instrument, executable, mode, None)
                     for mode in ["contracts", "prefix-negative-control"])
        cases.extend((instrument, executable, f"normal-{kind}-{shape}-{seed}", None)
                     for kind in range(4) for shape in range(2) for seed in range(2))
    cases.extend(("crt", crt, f"failure-{kind}-{shape}-{mask}-{seed}", None)
                 for kind in range(4) for shape in range(2) for mask in [0, 15] for seed in range(2))
    cases += [("asan", asan, "use-after-free", "heap-use-after-free"),
              ("crt", crt, "leak", "retained-blocks"),
              ("crt", crt, "allocation-hook-control", None)]
    assert len(cases) == 71, "Review the fixed qualification inventory"
    results = []
    for instrument, executable, mode, diagnostic in cases:
        log = output / f"{instrument}-{mode}.log"
        timed_out = False
        with log.open("xb") as stream:
            try:
                process = subprocess.run([str(executable.resolve()), mode], cwd=output,
                    env=environment, stdout=stream, stderr=subprocess.STDOUT, timeout=30)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                exit_code, timed_out = None, True
        data = log.read_bytes()
        text = data.decode("utf-8", errors="replace")
        retained = re.findall(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if diagnostic == "heap-use-after-free":
            passed = exit_code not in [None, 0] and "ERROR: AddressSanitizer:" in text and diagnostic in text
        elif diagnostic == "retained-blocks":
            passed = exit_code == 1 and len(retained) == 1 and int(retained[0][0]) > 0
        else:
            passed = exit_code == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if instrument == "crt":
                passed = passed and retained == [("0", "0")]
            if mode.startswith("normal-"):
                passed = passed and text.count("bezier_patch=") == 32 and text.count("live:1") == 32
                passed = passed and text.count("bezier_control=") == 512 and text.count("bezier_scalar=") == 864
            elif mode.startswith("failure-"):
                measured = re.search(r"bezier_measured=allocations:(\d+)", text)
                summary = re.search(r"bezier_sweep=denied:(\d+)/(\d+)", text)
                denials = re.findall(r"bezier_denied=ordinal:(\d+) attempts:(\d+) caught:(\d) "
                                    r"restored:(\d) blocks:(-?\d+) bytes:(-?\d+)", text)
                passed = (passed and measured is not None and summary is not None
                    and int(measured[1]) > 0 and summary[1] == summary[2] == measured[1]
                    and len(denials) == int(measured[1])
                    and [int(row[0]) for row in denials] == list(range(len(denials)))
                    and all(int(row[1]) == int(row[0]) + 1 and row[2:] == ("1", "1", "0", "0") for row in denials))
            elif mode == "prefix-negative-control":
                passed = passed and "bezier_prefix_control=rejected" in text
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        results.append({"instrument": instrument, "mode": mode, "exit_code": exit_code,
            "timed_out": timed_out, "passed": bool(passed), "expected_diagnostic": diagnostic,
            "log_sha256": hashlib.sha256(data).hexdigest(), "retained": retained,
            "observations": [line for line in text.splitlines() if line.startswith("bezier_")]})
        print(json.dumps({key: value for key, value in results[-1].items() if key != "observations"}), flush=True)
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
        "cases": results, "expected_outcomes": 71,
        "complete_sweeps": sum(case["passed"] and case["mode"].startswith("failure-") for case in results),
        "allocation_denials": sum(line.startswith("bezier_denied=") for case in results for line in case["observations"]),
        "executables": {label: {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                        for label, path in [("asan", asan), ("crt", crt)]},
        "scope": "Actual constructors/dependencies; fresh and borrowed curves, distinct/paired/all-slot aliases, plane/curved controls, empty/populated borrowed prefixes, all 16 direction masks and repeated successful calls. Thirty-two complete constructor allocation sweeps require actual denial, immediate propagation without allocation during unwinding, restored pointer-value prefixes and zero terminal retention after fixture destruction. Observer vector capacity is not rolled back. Aliases are lifecycle guards, not geometric validity. Successful constructor ownership is unchanged; the harness owns fresh curves and retires successful registrations while patches are alive. Ordinary destruction/deregistration, caller adoption failures, arbitrary/foreign publications, custom allocators, full-process/parallel/LSan/UBSan remain separate. ASan leaks are disabled; independent Debug CRT supplies retention and actual leak/hook controls."}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["asan", "crt", "runtime", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    r = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({name: r[name] for name in ["status", "expected_outcomes", "complete_sweeps", "allocation_denials"]}))
    raise SystemExit(r["status"] != "passed")
