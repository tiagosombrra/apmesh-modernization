#!/usr/bin/env python3
"""Qualify bounded UV cache ownership with actual ASan and CRT controls."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess


def analyze_case(text, code, instrument, mode):
    text = text.replace("\r\n", "\n")
    if text.count("warmup_complete\n") != 1:
        raise ValueError("Missing or ambiguous initialized measurement window")
    text = text.split("warmup_complete\n", 1)[1]
    retained = re.findall(r"^CRT retained_blocks=(\d+) retained_bytes=(\d+)$", text, re.M)
    result = {"retained": retained, "sweeps": 0, "denials": 0, "nonalloc_faces": 0}
    if instrument == "asan" and mode == "uaf":
        if code in (None, 0) or "ERROR: AddressSanitizer: heap-use-after-free" not in text:
            raise ValueError("Actual ASan use-after-free control did not detect invalid access")
        return result
    if mode in ("leak", "original-throw", "original-partial"):
        marker = {"leak": "", "original-throw": "original_cached_throw=observed",
                  "original-partial": "original_partial_denial=observed"}[mode]
        if (instrument != "crt" or code != 1 or len(retained) != 1
                or any(int(value) <= 0 for value in retained[0]) or marker not in text):
            raise ValueError("Actual CRT retention/original failure control was not observed")
        return result
    if code != 0 or not re.search(r"^PASS$", text, re.M) or "ERROR: AddressSanitizer:" in text:
        raise ValueError("Positive native cache case failed")
    if instrument == "crt" and retained != [("0", "0")]:
        raise ValueError("CRT cache case retained storage or lacks a measured checkpoint")
    if instrument == "asan" and retained:
        raise ValueError("ASan executable unexpectedly reports the CRT profile")
    if mode == "contracts":
        sweeps = re.findall(r"^sweep shape=(\d+) count=(\d+) throw=(\d+) allocations=(\d+) denials=(\d+) complete=1$", text, re.M)
        expected = [(s, n, t) for s in range(3) for n in (1, 3, 8) for t in (0, 1)]
        if ([tuple(map(int, row[:3])) for row in sweeps] != expected
                or any(int(a) <= 0 or a != b for *_, a, b in sweeps)):
            raise ValueError("Incomplete or nonpositive allocation-denial sweep matrix")
        nonalloc = re.findall(r"^nonalloc shape=(\d+) faces=(\d+) attempts=0$", text, re.M)
        if [tuple(map(int, row)) for row in nonalloc] != [(s, n) for s in range(3) for n in (1, 3, 8)]:
            raise ValueError("Missing nonempty allocation-free cleanup coverage")
        append = re.findall(r"^append_denied shape=(\d+) prefix=2 unchanged=1$", text, re.M)
        consumers = re.findall(r"^consumer mode=(\d+) cached_faces=2 alive_after_front=1$", text, re.M)
        if append != ["0", "1", "2"] or consumers != ["0", "1", "2"]:
            raise ValueError("Missing prefix preservation or actual AFT lifetime cases")
        result.update(sweeps=len(sweeps), denials=sum(int(row[4]) for row in sweeps),
                      nonalloc_faces=sum(int(row[1]) for row in nonalloc))
    elif mode in ("live", "original-live"):
        lines = [line for line in text.splitlines() if line.startswith("live ")]
        actual = [tuple(map(int, match)) for match in re.findall(r"^live shape=(\d+) face=(\d+) id=(\d+)", text, re.M)]
        expected = [(s, i, 100 + i) for s in range(3) for n in (1, 3, 8) for i in range(n)]
        if len(lines) != 36 or actual != expected:
            raise ValueError("Incomplete ordered original/candidate live trace")
        for line in lines:
            if " uv=" not in line:
                raise ValueError("Missing live UV observations")
            values = line.split(" uv=", 1)[1].replace(";", ",").replace(" mid=", ",").replace(" h=", ",").replace(" q=", ",")
            if len(values.split(",")) != 10 or not all(math.isfinite(float(value)) for value in values.split(",")):
                raise ValueError("Incomplete or nonfinite live cache observation")
        result["live_lines"] = lines
    elif mode == "hook":
        if text.count("allocation_hook_control=detected") != 1:
            raise ValueError("Independent allocation hook control missing")
    else:
        raise ValueError("Unknown positive qualification mode")
    return result


def qualify(asan, crt, runtime, output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    environment["PATH"] = str(runtime.resolve()) + os.pathsep + environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1"
    cases = [(instrument, exe, mode) for instrument, exe in (("asan", asan), ("crt", crt))
             for mode in ("contracts", "live", "original-live", "hook")]
    cases += [("asan", asan, "uaf"), *[("crt", crt, mode) for mode in ("leak", "original-throw", "original-partial")]]
    results = []
    for instrument, exe, mode in cases:
        log = output / (instrument + "-" + mode + ".log")
        argv = [str(exe.resolve()), mode]
        with log.open("xb") as stream:
            try:
                process = subprocess.run(argv, cwd=output, env=environment,
                                         stdout=stream, stderr=subprocess.STDOUT, timeout=60)
                code = process.returncode
            except subprocess.TimeoutExpired:
                code = None
        record = {"instrument": instrument, "mode": mode, "command": argv, "exit_code": code,
                  "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}
        try:
            record.update(analyze_case(log.read_text(encoding="utf-8", errors="replace"), code, instrument, mode), passed=True)
        except ValueError as error:
            record.update(passed=False, reason=str(error))
        results.append(record)
    for instrument in ("asan", "crt"):
        live = next(r for r in results if r["instrument"] == instrument and r["mode"] == "live")
        old = next(r for r in results if r["instrument"] == instrument and r["mode"] == "original-live")
        if not live.get("live_lines") or live.get("live_lines") != old.get("live_lines"):
            live.update(passed=False, reason="Original/candidate live observations differ")
    report = {"status": "passed" if all(r["passed"] for r in results) else "failed",
              "expected_outcomes": len(cases), "cases": results,
              "executables": {label: {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                              for label, path in (("asan", asan), ("crt", crt))},
              "scope": "Exclusive fresh serial UV cache faces/endpoints, partial construction, list adoption, throwing borrowers and actual AFT teardown. No whole-process/LSan/UBSan, OpenMP or orchestration rollback qualification."}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("asan", "crt", "runtime", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({"status": report["status"], "expected_outcomes": report["expected_outcomes"],
                      "failures": [{k: r.get(k) for k in ("instrument", "mode", "exit_code", "reason")}
                                   for r in report["cases"] if not r["passed"]]}))
    raise SystemExit(report["status"] != "passed")
