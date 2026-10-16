#!/usr/bin/env python3
"""Compare two runs using exactly the same executable, configuration and output path."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

from run_generation_case import ROOT, run_case
from verify_generation import RegressionMismatch, compare_runs, verify_run


def repeat(executable: Path, model: str, output: Path, timeout: float) -> dict:
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    working = output / "working"
    metadata = run_case(executable, model, working, timeout)
    config = working / "article.conf"
    config_hash = hashlib.sha256(config.read_bytes()).hexdigest()
    reports = []
    for repetition in [1, 2]:
        if repetition == 2:
            started = time.perf_counter()
            with (working / "stdout.log").open("wb") as stdout, (working / "stderr.log").open("wb") as stderr:
                process = subprocess.run(metadata["command"], cwd=ROOT, stdout=stdout,
                                         stderr=stderr, timeout=timeout)
            metadata = {**metadata, "exit_code": process.returncode,
                        "wall_seconds": time.perf_counter() - started}
            (working / "process.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n")
        if hashlib.sha256(config.read_bytes()).hexdigest() != config_hash:
            raise ValueError("Configuration changed during the repeatability experiment")
        if hashlib.sha256(executable.read_bytes()).hexdigest() != metadata["executable_sha256"]:
            raise ValueError("Executable changed during the repeatability experiment")
        reports.append(verify_run(working))
        archive = output / f"repetition-{repetition}"
        archive.mkdir()
        for path in working.iterdir():
            if path.is_file():
                shutil.copy2(path, archive / path.name)
        if repetition == 1:
            # Remove only backed-up generated files in this newly owned working directory.
            for path in working.iterdir():
                if path.is_file() and path.name != "article.conf":
                    if not path.resolve().is_relative_to(working.resolve()):
                        raise ValueError("Unexpected generated output path")
                    path.unlink()
    try:
        report = {"status": "passed", **compare_runs(*reports)}
    except RegressionMismatch as error:
        report = error.report
    return {**report, "same_executable_same_configuration_same_command": True,
            "executable_sha256": metadata["executable_sha256"],
            "configuration_sha256": config_hash}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--model", choices=["eistute", "book", "decor_shelf"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = repeat(args.exe, args.model, args.output, args.timeout)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({key: value for key, value in report.items() if key != "differences"}))
        raise SystemExit(0 if report["status"] == "passed" else 1)
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"Repeatability experiment failed: {error}\n")
