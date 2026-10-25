#!/usr/bin/env python3
"""Require complete constructor rollback, retry and actual model failure sweeps."""
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
    environment["PATH"] = str(runtime.resolve()) + os.pathsep + environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1"
    modes = [["contracts"], ["model-sweep"], ["hook"], ["oracle"]]
    modes += [[mode, str(layout), str(seed)] for mode in ["live", "sweep", "adoption"]
              for layout in range(3) for seed in [0, 3, 4, 7]]
    cases = [(instrument, executable, mode, None)
             for instrument, executable in [("asan", asan), ("crt", crt)] for mode in modes]
    cases += [("asan", asan, ["uaf"], "heap-use-after-free"),
              ("crt", crt, ["leak"], "retention")]
    assert len(cases) == 82
    results = []
    for instrument, executable, mode, diagnostic in cases:
        log = output / (instrument + "-" + "-".join(mode) + ".log")
        command = [str(executable.resolve()), *mode]
        timed_out = False
        with log.open("xb") as stream:
            try:
                process = subprocess.run(command, cwd=output, env=environment,
                                         stdout=stream, stderr=subprocess.STDOUT, timeout=30)
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                exit_code, timed_out = None, True
        data = log.read_bytes()
        text = data.decode("utf-8", errors="replace")
        retained = re.findall(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        sweeps = re.findall(r"sweep flags=(\d+) allocations=(\d+) denials=(\d+) stale_cases=(\d+) complete=1", text)
        models = re.findall(r"model_sweep allocations=(\d+) denials=(\d+) stale_cases=0 complete=1", text)
        if diagnostic == "heap-use-after-free":
            passed = exit_code not in [None, 0] and "ERROR: AddressSanitizer: heap-use-after-free" in text
        elif diagnostic == "retention":
            passed = exit_code == 1 and len(retained) == 1 and int(retained[0][0]) > 0 and int(retained[0][1]) > 0
        else:
            passed = exit_code == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if instrument == "crt":
                passed = passed and retained == [("0", "0")]
            if mode[0] in ["contracts", "sweep"]:
                expected = 192 if mode[0] == "contracts" else 16
                passed = (passed and len(sweeps) == expected
                          and all(int(a) > 0 and a == b and stale == "0" for _, a, b, stale in sweeps)
                          and [int(row[0]) for row in sweeps] == list(range(16)) * (expected // 16))
            if mode[0] in ["contracts", "model-sweep"]:
                passed = passed and len(models) == 1 and int(models[0][0]) > 0 and models[0][0] == models[0][1]
                model_rows = re.findall(r"model ordinal=(-?\d+) attempts=\d+ denied=(\d+) caught=(\d+) curves=\d+ patches=\d+ stale=(\d+)", text)
                expected_total = int(models[0][0]) if models else 0
                passed = (passed and len(model_rows) == expected_total + 1
                          and [int(row[0]) for row in model_rows] == [-1, *range(expected_total)]
                          and all(row[1:] == ("1", "1", "0") for row in model_rows[1:]))
            if mode[0] in ["contracts", "live"]:
                expected = 192 if mode[0] == "contracts" else 16
                passed = passed and text.count("live_points=25 completed_publications=4 retirement_restored=1") == expected
            if mode[0] == "adoption":
                passed = passed and text.count("adoption_denied=1 geometry_prefix_preserved=1 stale=0") == 1
            if mode[0] == "hook":
                passed = passed and "denial_control=detected" in text
            if mode[0] == "oracle":
                passed = passed and "oracle_corruptions=2 detected=2" in text
        results.append({"instrument": instrument, "mode": mode, "command": command,
                        "exit_code": exit_code, "timed_out": timed_out, "passed": bool(passed),
                        "expected_diagnostic": diagnostic, "log_sha256": hashlib.sha256(data).hexdigest(),
                        "constructor_sweeps": len(sweeps),
                        "constructor_denials": sum(int(row[2]) for row in sweeps),
                        "model_denials": sum(int(row[1]) for row in models), "retained": retained})
    report = {"status": "passed" if all(row["passed"] for row in results) else "failed",
              "expected_outcomes": len(cases), "cases": results,
              "executables": {label: {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                              for label, path in [("asan", asan), ("crt", crt)]},
              "scope": "Live nonnull borrowed Hermite curves; exclusive append-only constructor publication. "
                       "Three incidence layouts, four foreign/null prefixes and all sixteen flags. "
                       "Each actual denial must propagate without additional allocation, restore the exact prefix "
                       "and allow successful construction and retirement on retry. ModelBaseQuadrada is swept "
                       "independently. No complete loader/adaptive/parallel/LSan/UBSan qualification follows."}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["asan", "crt", "runtime", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({"status": report["status"], "expected_outcomes": report["expected_outcomes"],
                      "failures": [row["command"] for row in report["cases"] if not row["passed"]]}))
    raise SystemExit(report["status"] != "passed")
