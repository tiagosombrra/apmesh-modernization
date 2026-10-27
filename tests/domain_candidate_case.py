#!/usr/bin/env python3
"""Check actual GNU serial caller ownership and its deliberate release control."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


def expected_rows():
    return [(b, s, m, 0, int(m in (2, 4))) for b in range(3) for s in (0, 1) for m in range(5)] + [
        (2, 0, 0, 1, 0), (2, 1, 0, 1, 0)]


def validate_contracts(code, text):
    if code != 0 or "Candidate contract failure:" in text:
        raise ValueError("Actual candidate ownership contracts failed")
    matches = re.findall(r"^candidate branch=(\d+) select=(\d+) mode=(\d+) alias=(\d+) calls=2 retained=0 denied=(\d+)$", text, re.M)
    if [tuple(map(int, row)) for row in matches] != expected_rows():
        raise ValueError("Incomplete, unordered or corrupted candidate branch coverage")
    if text.count("candidate_contracts=32 complete=1") != 1:
        raise ValueError("Missing or ambiguous candidate contract completion")


def validate_release_control(code, text):
    marker = "Candidate contract failure: candidate release observer detected retained storage"
    if code != 1 or text.count(marker) != 1 or text.count("candidate_release_control_suppressed=1") != 1:
        raise ValueError("Deliberate native release control did not expose retained storage")


def run(executable, workspace):
    workspace.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="run-", dir=workspace))
    cases = []
    for name, flag, check in (("contracts", "--domain-candidate-contracts", validate_contracts),
                              ("release-control", "--domain-candidate-release-control", validate_release_control)):
        command = [str(executable.resolve()), flag]
        log = output / (name + ".log")
        with log.open("wb") as stream:
            process = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=30)
        case = {"name": name, "command": command, "exit_code": process.returncode,
                "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(), "status": "passed"}
        try:
            check(process.returncode, log.read_text(encoding="utf-8"))
        except ValueError as error:
            case.update(status="failed", reason=str(error))
        cases.append(case)
    report = {"status": "passed" if all(c["status"] == "passed" for c in cases) else "failed",
              "contracts": 32, "cases": cases,
              "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
              "scope": "GNU serial actual caller with explicit fixture state, native SubMesh/node/triangle ownership and exact-address release observation; no whole-process/ASan/CRT/parallel qualification"}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.exe, args.workspace)
    print(json.dumps(report))
    raise SystemExit(report["status"] != "passed")
