#!/usr/bin/env python3
"""Require selected-mesh statistics, independent comparisons and copy-failure cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


def expected_rows():
    rows = []
    for alias in (0, 1):
        for scenario in range(20):
            calls = 4 if scenario in (8, 9) else 1 if scenario == 10 else 2
            selected = 3 if scenario == 8 else 2 if scenario == 9 else -1 if scenario in (10, 11) else int(scenario % 2 == 0)
            rows.append((scenario, alias, calls, selected, int(scenario in (10, 11))))
    return rows


def validate(code, text):
    rows = re.findall(r"^snapshot scenario=(\d+) alias=(\d+) calls=(\d+) selected=(-?\d+) retained=0 denied=(\d+) unwind=0$", text, re.M)
    if (code != 0 or "Snapshot contract failure:" in text
            or [tuple(map(int, r)) for r in rows] != expected_rows()
            or text.count("snapshot_contracts=40 complete=1") != 1):
        raise ValueError("Missing or failed selected snapshot, comparison, sequence or copy-failure contracts")


def run(executable, workspace):
    workspace.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="run-", dir=workspace))
    command = [str(executable.resolve()), "--candidate-snapshot-contracts"]
    with (output / "output.log").open("wb") as log:
        process = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=45)
    report = {"status": "passed", "contracts": 40, "command": command, "exit_code": process.returncode,
              "log_sha256": hashlib.sha256((output / "output.log").read_bytes()).hexdigest(),
              "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
              "scope": "GNU serial actual caller; selected scalar/region exports, independent/reused slots, sequential replacement, epsilon/fallback, null snapshots and native owner cleanup on string-copy failure"}
    try:
        validate(process.returncode, (output / "output.log").read_text(encoding="utf-8"))
    except ValueError as error:
        report.update(status="failed", reason=str(error))
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.exe, args.workspace)
    print(json.dumps(result))
    raise SystemExit(result["status"] != "passed")
