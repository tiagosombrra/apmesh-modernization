#!/usr/bin/env python3
"""Exercise actual serial terminal failure under an explicit GNU linker fault."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MARKER = "Domain failure control: step=2 patch=0"
DIAGNOSTIC = "Error: domain generation failed (step=2, patch=0, retry=0, status=generation_failed)"


def validate_failure(code, stderr, expected_calls):
    if code != 1:
        raise ValueError("Terminal generation must exit with status 1, not success or a crash")
    if stderr.count(MARKER) != expected_calls or DIAGNOSTIC not in stderr:
        raise ValueError("Missing controlled call count or terminal failure context")


def run(executable, workspace):
    workspace.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="run-", dir=workspace))
    records = []
    for model, calls in (("book", 1), ("eistute", 2)):
        folder = output / model
        folder.mkdir()
        source = ROOT / "configs" / model / "article.conf"
        text = source.read_text(encoding="utf-8")
        input_name = re.search(r"^INPUT_MODEL=(.+)$", text, re.M)[1].strip()
        text = re.sub(r"^INPUT_MODEL=.*$", "INPUT_MODEL=" + (ROOT / input_name).as_posix(), text, flags=re.M)
        text = re.sub(r"^OUTPUT_PREFIX=.*$", "OUTPUT_PREFIX=" + (folder / model).as_posix(), text, flags=re.M)
        config = folder / "article.conf"
        config.write_text(text, encoding="utf-8", newline="\n")
        command = [str(executable.resolve()), "--domain-failure-config", str(config)]
        with (folder / "stdout.log").open("wb") as stdout, (folder / "stderr.log").open("wb") as stderr:
            process = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, timeout=30)
        diagnostic = (folder / "stderr.log").read_text(encoding="utf-8")
        record = {"model": model, "exit_code": process.returncode, "expected_calls": calls,
                  "command": command, "source_config_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                  "status": "passed"}
        try:
            validate_failure(process.returncode, diagnostic, calls)
        except ValueError as error:
            record.update(status="failed", reason=str(error))
        records.append(record)
    report = {"status": "passed" if all(r["status"] == "passed" for r in records) else "failed",
              "scope": "GNU serial controlled AFT false outcome; not a natural numerical failure or memory qualification",
              "cases": records}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.exe, args.workspace)
    print(json.dumps(report))
    raise SystemExit(0 if report["status"] == "passed" else 1)
