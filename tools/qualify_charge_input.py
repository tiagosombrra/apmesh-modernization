#!/usr/bin/env python3
"""Qualify bounded charge-input ownership with actual reader/caller units."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def fixtures(output):
    directory = output / "fixtures"
    directory.mkdir()
    paths = []
    for shape in range(4):
        rows = []
        count = 1 if shape < 2 else 3
        for patch in range(count):
            for v in range(4):
                for u in range(4):
                    x, y = patch + u / 3, v / 3
                    z = 0 if shape == 0 else (x * x + y * y) / 8
                    rows.append(f"v {x:.17g} {y:.17g} {z:.17g}")
        for patch in range(count):
            base = 0 if shape == 3 and patch == 2 else patch * 16
            rows.append("p " + " ".join(str(base + i) for i in range(16)))
        path = directory / f"{shape}.bp"
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        paths.append(path)
    empty = directory / "empty.bp"
    empty.write_bytes(b"")
    return paths, empty


def qualify(asan, crt, runtime, output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    paths, empty = fixtures(output)
    environment = dict(os.environ)
    environment["PATH"] = str(runtime.resolve()) + os.pathsep + environment.get("PATH", "")
    environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=0:detect_leaks=0"
    instruments = [("asan", asan.resolve()), ("crt", crt.resolve())]
    cases = []
    for instrument, executable in instruments:
        for shape, path in enumerate(paths):
            for seed in range(2):
                for mode in ["normal", "repeat", "writer"]:
                    cases.append((instrument, executable, f"{mode}-{shape}-{seed}", path, None))
                for step in range(1, (3 if shape < 2 else 9) + 1):
                    cases.append((instrument, executable, f"throw-{shape}-{seed}-{step}", path, None))
            cases.append((instrument, executable, f"read-{shape}", path, None))
            cases.append((instrument, executable, f"reuse-{shape}", path, None))
        for label, path in [("empty", empty), ("missing", output / "missing.bp"), ("no-name", None)]:
            cases.append((instrument, executable, f"read-{label}", path, None))
    for shape, path in enumerate(paths):
        for seed in range(2):
            for writer in [0, 2]:
                cases.append(("crt", crt.resolve(), f"failure-{shape}-{seed}-{writer}", path, None))
        cases.append(("crt", crt.resolve(), f"failure-{shape}-0-1", path, None))
    cases += [("asan", asan.resolve(), "use-after-free", paths[0], "heap-use-after-free"),
              ("crt", crt.resolve(), "leak", paths[0], "retained-blocks"),
              ("crt", crt.resolve(), "allocation-hook-control", paths[0], None)]
    assert len(cases) == 189, "Review the fixed qualification inventory"
    results = []
    for instrument, executable, mode, path, diagnostic in cases:
        directory = output / f"{instrument}-{mode}"
        directory.mkdir()
        cursor, total = 0, None
        invocations, chunks = [], []
        while True:
            child_mode = "read" if mode.startswith("read-") else mode
            if mode.startswith("reuse-"):
                child_mode = "reuse"
            if mode.startswith("failure-"):
                child_mode += f"-{cursor}"
            log = directory / f"{cursor}.log"
            timed_out = False
            with log.open("xb") as stream:
                try:
                    process = subprocess.run([str(executable), child_mode, str(path) if path else ""],
                                             cwd=directory, env=environment, stdout=stream,
                                             stderr=subprocess.STDOUT, timeout=30)
                    exit_code = process.returncode
                except subprocess.TimeoutExpired:
                    exit_code, timed_out = None, True
            chunk = log.read_bytes()
            chunks.append(chunk)
            invocations.append({"mode": child_mode, "exit_code": exit_code, "timed_out": timed_out,
                                "log": str(log.relative_to(output)),
                                "log_sha256": hashlib.sha256(chunk).hexdigest()})
            if not mode.startswith("failure-") or exit_code != 0:
                break
            interval = re.search(rb"charge_failure_range=first:(\d+) end:(\d+) total:(\d+)", chunk)
            if interval is None or int(interval[1]) != cursor:
                break
            if total is not None and total != int(interval[3]):
                break
            total, cursor = int(interval[3]), int(interval[2])
            if cursor >= total:
                break
        data = b"".join(chunks)
        log = output / f"{instrument}-{mode}.log"
        log.write_bytes(data)
        text = data.decode("utf-8", errors="replace")
        retained = re.findall(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
        if diagnostic == "heap-use-after-free":
            passed = (exit_code is not None and exit_code != 0 and "ERROR: AddressSanitizer:" in text
                      and diagnostic in text)
        elif diagnostic == "retained-blocks":
            passed = exit_code == 1 and retained and int(retained[-1][0]) > 0
        else:
            passed = exit_code == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if instrument == "crt":
                passed = passed and len(retained) == len(invocations) and all(row == ("0", "0") for row in retained)
            if mode.startswith(("normal-", "repeat-", "writer-", "throw-")):
                values = re.findall(r"charge_result=repeat:(\d+) caught:(\d) patches:(\d+) curves:(\d+) results:(\d+) curvatures:(\d+) live:(\d)", text)
                expected = 3 if mode.startswith("repeat-") else 1
                passed = passed and len(values) == expected and all(row[-1] == "1" for row in values)
                if not mode.startswith("throw-"):
                    shape = int(mode.split("-")[1])
                    expected_count = 1 if shape < 2 else 3
                    passed = passed and all(int(row[4]) == expected_count for row in values)
                    passed = passed and text.count("charge_control=") == 16 * expected_count * expected
                    steps = re.findall(r"charge_step=index:\d+ stage:(\d) argument:(\d+)", text)
                    passed = passed and steps == [("1", "4"), ("2", "25"), ("3", "0")] * expected_count * expected
                else:
                    passed = passed and values[0][1] == "1"
            elif mode.startswith("read-"):
                count = int(mode.rsplit("-", 1)[1]) if mode.rsplit("-", 1)[1].isdigit() else -1
                expected = (1 if count < 2 else 3) if count >= 0 else 0
                passed = passed and text.count("charge_read=") == expected
            elif mode.startswith("reuse-"):
                shape = int(mode.rsplit("-", 1)[1])
                count = 1 if shape < 2 else 3
                passed = passed and f"charge_reuse=first:{count} second:{count} independent:1" in text
            elif mode.startswith("failure-"):
                denials = re.findall(r"charge_denied=ordinal:(\d+) caught:(\d) attempts:(\d+) blocks:(-?\d+) bytes:(-?\d+) live:(\d)", text)
                ranges = re.findall(r"charge_failure_range=first:(\d+) end:(\d+) total:(\d+)", text)
                measured = {int(row) for row in re.findall(r"charge_measured=allocations:(\d+)", text)}
                passed = (passed and total is not None and total > 0 and cursor == total and measured == {total}
                          and len(ranges) == len(invocations)
                          and [int(row[0]) for row in ranges] == list(range(0, total, 32))
                          and all(int(row[1]) == min(int(row[0]) + 32, total) and int(row[2]) == total for row in ranges)
                          and [int(row[0]) for row in denials] == list(range(total))
                          and all(row[3:] == ("0", "0", "1") for row in denials))
            elif mode == "allocation-hook-control":
                passed = passed and "allocation_hook_control=detected" in text
        record = {"instrument": instrument, "mode": mode, "exit_code": exit_code,
                  "passed": bool(passed), "log": log.name, "log_sha256": hashlib.sha256(data).hexdigest(),
                  "invocations": invocations, "retained": retained,
                  "observations": [line for line in text.splitlines() if line.startswith(("charge_", "allocation_hook_control="))],
                  "artifacts": {str(file.relative_to(output)): hashlib.sha256(file.read_bytes()).hexdigest()
                                for file in directory.glob("*_analise_curvature_patches.log")}}
        results.append(record)
        print(json.dumps({key: record[key] for key in ["instrument", "mode", "exit_code", "passed"]}), flush=True)
    report = {"status": "passed" if all(row["passed"] for row in results) else "failed",
              "scope": "Actual reader/caller/dependency units, exact unchanged estimator lifetime, controlled existing numerical members in the memory executable only. Positive single/three-patch, adjacent/repeated shared-curve, pre-existing null/repeated observers, stable ties, repeated calls, writer, evaluation exceptions and complete allocation-denial intervals. Geometry may retain committed curves/patches after failure. Reader badbit resource failures propagate; ordinary EOF/failbit behavior and timer/global/curvature writes are preserved, not rolled back. Writer streams may internally absorb a denial and produce partial output; the failure gate measures memory and live observers, not successful export or caller error reporting. No full numerical-helper, arbitrary callback publication, malformed parser-input, full-process/parallel/LSan/UBSan qualification. ASan leak detection disabled; the explicitly qualified static Debug CRT measures retention without DLL Debug STL aborts. Original stopped intervals leave later ordinals unmeasured.",
              "executables": {name: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                              for name, path in instruments},
              "fixtures": {str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in paths + [empty]}, "cases": results}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ["asan", "crt", "runtime", "output"]:
        parser.add_argument("--" + flag, type=Path, required=True)
    args = parser.parse_args()
    result = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps({"status": result["status"], "cases": len(result["cases"])}))
    raise SystemExit(0 if result["status"] == "passed" else 1)
