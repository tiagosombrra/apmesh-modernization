#!/usr/bin/env python3
"""Check accepted-owner lifetime and the independent native release control."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


def validate_contracts(code, text):
    rows = re.findall(r"^accepted_root archived=(\d+) action=(\d+) reverse=(\d+) denied=(\d+) unwind=0 retained=0$", text, re.M)
    expected = [(a, action, reverse, int(action == 3)) for a in (0, 1) for action in range(5) for reverse in (0, 1)]
    sequences = re.findall(r"^accepted_sequence archived=(\d+) steps=4 retries=8 commits=2 retained=0$", text, re.M)
    if (code != 0 or "Accepted root contract failure:" in text
            or [tuple(map(int, row)) for row in rows] != expected or sequences != ["0", "1"]
            or text.count("accepted_root_contracts=22 complete=1") != 1):
        raise ValueError("Missing accepted-root lifetime, selection, retry, release or unwinding coverage")


def validate_release(code, text):
    if (code != 1 or text.count("accepted_root_release_suppressed=1") != 1
            or text.count("Accepted root contract failure: accepted root retained observed native storage") != 1):
        raise ValueError("Native release control did not detect its suppressed deallocation")


def run(executable, workspace):
    workspace.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="run-", dir=workspace))
    cases = []
    for name, flag, check in (("contracts", "--accepted-root-contracts", validate_contracts),
                              ("release-control", "--accepted-root-release-control", validate_release)):
        command = [str(executable.resolve()), flag]
        with (folder / (name + ".log")).open("wb") as log:
            p = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=45)
        path = folder / (name + ".log")
        case = {"name": name, "command": command, "exit_code": p.returncode,
                "log_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "status": "passed"}
        try:
            check(p.returncode, path.read_text(encoding="utf-8"))
        except ValueError as error:
            case.update(status="failed", reason=str(error))
        cases.append(case)
    r = {"status": "passed" if all(c["status"] == "passed" for c in cases) else "failed",
         "contracts": 22, "cases": cases, "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
         "scope": "GNU serial native accepted-owner scope, observed SubMesh/node/triangle release, no-allocation cleanup and null/foreign observers; complete caller/quality coverage is separate"}
    (folder / "report.json").write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
    return r


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.exe, args.workspace)
    print(json.dumps(result))
    raise SystemExit(result["status"] != "passed")
