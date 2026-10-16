#!/usr/bin/env python3
"""Qualify the narrow MSVC ASan and Debug CRT node boundary with broken controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def qualify(asan: Path, crt: Path, runtime: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    environment = dict(os.environ)
    environment["PATH"] = str(runtime.resolve()) + os.pathsep + environment.get("PATH", "")
    # Windows ASan is used for invalid accesses; Debug CRT measures retained blocks.
    environment["ASAN_OPTIONS"] = "halt_on_error=1:abort_on_error=0:detect_leaks=0"
    cases = [
        ("asan", asan, "contracts", None),
        ("asan", asan, "expired-copy", None),
        ("asan", asan, "use-after-free", "heap-use-after-free"),
        ("asan", asan, "double-free", "attempting double-free"),
        ("crt", crt, "contracts", None),
        ("crt", crt, "expired-copy", None),
        ("crt", crt, "leak", "retained-blocks"),
    ]
    results = []
    for kind, executable, mode, expected in cases:
        process = subprocess.run([str(executable.resolve()), mode], env=environment,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        data = process.stdout
        (output / f"{kind}-{mode}.log").write_bytes(data)
        text = data.decode("utf-8", errors="replace")
        if expected == "retained-blocks":
            match = re.search(r"CRT retained_blocks=(\d+) retained_bytes=(\d+)", text)
            passed = process.returncode == 1 and match is not None and int(match[1]) > 0
        elif expected is not None:
            passed = process.returncode != 0 and "ERROR: AddressSanitizer:" in text and expected in text
        else:
            passed = process.returncode == 0 and "PASS" in text and "ERROR: AddressSanitizer:" not in text
            if kind == "crt":
                passed = passed and "CRT retained_blocks=0 retained_bytes=0" in text
        results.append({"instrument": kind, "mode": mode, "exit_code": process.returncode,
                        "expected_diagnostic": expected, "passed": passed,
                        "log_sha256": hashlib.sha256(data).hexdigest()})
    report = {"status": "passed" if all(case["passed"] for case in results) else "failed",
              "scope": "Isolated actual physical node/submesh/triangle production sources; no whole-application or UBSan/LSan qualification.",
              "executables": {kind: {"path": str(path.resolve()),
                                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                              for kind, path in [("asan", asan), ("crt", crt)]},
              "cases": results}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asan", type=Path, required=True)
    parser.add_argument("--crt", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = qualify(args.asan, args.crt, args.runtime, args.output)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["status"] == "passed" else 1)
