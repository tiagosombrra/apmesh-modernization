#!/usr/bin/env python3
"""Require nonallocating observer detachment and unchanged exception identity."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def expected_helpers():
    return [(layout, reverse, rethrow, 2 * (layout + 1), 4 * (layout + 1))
            for layout in range(3) for reverse in (0, 1) for rethrow in (0, 1)]


def validate_helpers(code, text):
    if code != 0 or "Domain observer failure:" in text:
        raise ValueError("Actual observer helper contracts failed")
    rows = re.findall(r"^domain_observers layout=(\d+) reverse=(\d+) rethrow=(\d+) owners=(\d+) owned_links=(\d+) foreign_links=2 null_links=2 null_patches=1 attempts=0 identity=1$", text, re.M)
    if [tuple(map(int, row)) for row in rows] != expected_helpers():
        raise ValueError("Missing or corrupted nonempty owner/prefix/rethrow coverage")
    if (text.count("domain_observer_hook attempts=1 denied=1") != 1
            or text.count("domain_observer_contracts=12 complete=1") != 1):
        raise ValueError("Missing or ambiguous actual allocation hook/completion")


def validate_failure(code, text, model):
    if code != 0 or "Domain observer failure:" in text:
        raise ValueError("Actual domain exception cleanup failed")
    rows = re.findall(r"^domain_failure patches=(\d+) target=(\d+) live_before=(\d+) changed_before=(\d+) null_after=(\d+) nonnull_after_owner=(\d+) samples_after=(\d+) attempts=(\d+) denied=(\d+) identity=(\d+)$", text, re.M)
    expected = {"book": (28, 0, 28, 0, 28, 0, 0, 0, 0, 1),
                "eistute": (4, 1, 4, 1, 4, 0, 0, 0, 0, 1)}[model]
    if [tuple(map(int, row)) for row in rows] != [expected] or text.count("domain_failure ") != 1:
        raise ValueError("Missing or corrupted real domain cleanup/identity observations")


def run(executable, workspace):
    workspace.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="run-", dir=workspace))
    cases = []
    for name in ("helpers", "book", "eistute"):
        folder = output / name
        folder.mkdir()
        command = [str(executable.resolve()), "--domain-observer-contracts"]
        record = {"case": name, "status": "passed"}
        if name != "helpers":
            source = ROOT / "configs" / name / "article.conf"
            text = source.read_text(encoding="utf-8")
            input_name = re.search(r"^INPUT_MODEL=(.+)$", text, re.M)[1].strip()
            text = re.sub(r"^INPUT_MODEL=.*$", "INPUT_MODEL=" + (ROOT / input_name).as_posix(), text, flags=re.M)
            text = re.sub(r"^OUTPUT_PREFIX=.*$", "OUTPUT_PREFIX=" + (folder / name).as_posix(), text, flags=re.M)
            config = folder / "article.conf"
            config.write_text(text, encoding="utf-8", newline="\n")
            command = [str(executable.resolve()), "--domain-observer-config", str(config), "0" if name == "book" else "1"]
            record.update(source_config_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                          input_model_sha256=hashlib.sha256((ROOT / input_name).read_bytes()).hexdigest())
        log = folder / "output.log"
        with log.open("wb") as stream:
            process = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=45)
        record.update(command=command, exit_code=process.returncode,
                      log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
        try:
            observed = log.read_text(encoding="utf-8")
            if name == "helpers":
                validate_helpers(process.returncode, observed)
            else:
                validate_failure(process.returncode, observed, name)
        except ValueError as error:
            record.update(status="failed", reason=str(error))
        cases.append(record)
    report = {"status": "passed" if all(c["status"] == "passed" for c in cases) else "failed",
              "cases": cases, "helper_contracts": 12,
              "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
              "scope": "GNU serial helper and actual Generator failure boundary, under global operator-new denial; no terminal-exit change, rollback or full-process qualification"}
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
