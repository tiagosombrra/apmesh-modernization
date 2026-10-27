#!/usr/bin/env python3
"""Check typed terminal propagation, real CLI classification and failed prefixes."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from verify_generation import verify_run


def validate_types(code, text):
    rows = re.findall(r"^typed_error case=(\d+) status_bytes=(\d+) payload=1 identity=1 allocations=0$", text, re.M)
    if (code != 0 or "Typed domain failure:" in text
            or [tuple(map(int, row)) for row in rows] != list(enumerate([0, 17, 257] * 3))
            or text.count("typed_unwind_hook attempts=1 denied=1") != 1
            or text.count("typed_error_contracts=9 complete=1") != 1):
        raise ValueError("Missing typed payload, lifetime, rethrow or allocation-hook coverage")


def validate_library(code, text, model):
    rows = re.findall(r"^typed_library patches=(\d+) target=(\d+) calls=(\d+) changed_before=(\d+) detached=(\d+) nonnull_after_owner=(\d+) samples=(\d+) allocations=(\d+) unwind_allocations=(\d+) denied=(\d+) payload=(\d+)$", text, re.M)
    expected = {"book": (28, 0, 1, 0, 28, 0, 0, 0, 0, 0, 1),
                "eistute": (4, 1, 2, 1, 4, 0, 0, 0, 0, 0, 1)}[model]
    if (code != 0 or "Typed domain failure:" in text or "Error: domain generation failed" in text
            or "Error: input or configuration failure:" in text
            or [tuple(map(int, row)) for row in rows] != [expected]):
        raise ValueError("Typed library propagation lost payload, attempts or bounded cleanup")


def validate_cli(code, text, patch, calls):
    marker = f"Typed domain control: step=2 patch={patch}"
    diagnostic = f"Error: domain generation failed (step=2, patch={patch}, retry=0, status=generation_failed)"
    if (code != 1 or text.count(marker) != calls or text.count(diagnostic) != 1
            or text.count("Error: domain generation failed") != 1
            or "Error: input or configuration failure:" in text or "Typed domain failure:" in text
            or text.count("Typed CLI unwind allocations=0") != 1):
        raise ValueError("Typed CLI failed status, classification, context, attempt count or unwinding")


def run(executable, workspace):
    workspace.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="run-", dir=workspace))
    cases = []
    matrix = [("types", None, None, None), ("library-book", "book", 0, 1),
              ("library-eistute", "eistute", 1, 2), ("cli-book", "book", 0, 1),
              ("cli-eistute-p0", "eistute", 0, 2), ("cli-eistute-p1", "eistute", 1, 2)]
    for name, model, patch, calls in matrix:
        folder = output / name
        folder.mkdir()
        command = [str(executable.resolve()), "--typed-domain-contracts"]
        record = {"case": name, "status": "passed"}
        if model is not None:
            source = ROOT / "configs" / model / "article.conf"
            text = source.read_text(encoding="utf-8")
            input_name = re.search(r"^INPUT_MODEL=(.+)$", text, re.M)[1].strip()
            text = re.sub(r"^INPUT_MODEL=.*$", "INPUT_MODEL=" + (ROOT / input_name).as_posix(), text, flags=re.M)
            text = re.sub(r"^OUTPUT_PREFIX=.*$", "OUTPUT_PREFIX=" + (folder / model).as_posix(), text, flags=re.M)
            config = folder / "article.conf"
            config.write_text(text, encoding="utf-8", newline="\n")
            command = [str(executable.resolve()), "--typed-domain-library-config" if name.startswith("library") else "--typed-domain-cli-config", str(config), str(patch)]
            record.update(source_config_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                          input_model_sha256=hashlib.sha256((ROOT / input_name).read_bytes()).hexdigest())
        log = folder / "output.log"
        with log.open("wb") as stream:
            process = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, timeout=45)
        record.update(command=command, exit_code=process.returncode,
                      log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
        try:
            observed = log.read_text(encoding="utf-8")
            if name == "types":
                validate_types(process.returncode, observed)
            elif name.startswith("library"):
                validate_library(process.returncode, observed, model)
            else:
                validate_cli(process.returncode, observed, patch, calls)
                (folder / "process.json").write_text(json.dumps({"status": "completed", "exit_code": process.returncode}) + "\n", encoding="utf-8")
                try:
                    verify_run(folder)
                except ValueError as error:
                    if str(error) != "Generation did not complete successfully":
                        raise
                    record["failed_prefix_rejected"] = True
                else:
                    raise ValueError("Failed generation prefix was accepted as successful")
        except ValueError as error:
            record.update(status="failed", reason=str(error))
        cases.append(record)
    report = {"status": "passed" if all(c["status"] == "passed" for c in cases) else "failed",
              "cases": cases, "type_contracts": 9,
              "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
              "scope": "GNU serial typed payload, actual library/CLI false paths and global operator-new denial during unwinding; no rollback, retry or complete-process qualification"}
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
