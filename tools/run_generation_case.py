#!/usr/bin/env python3
"""Run one pinned article case in a fresh directory and retain process evidence."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def run_case(executable, model, output, timeout):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    original = ROOT / "configs" / model / "article.conf"
    text = original.read_text(encoding="utf-8")
    input_path = re.search(r"^INPUT_MODEL=(.+)$", text, re.M)[1].strip()
    model_path = (ROOT / input_path).resolve()
    model_hash = hashlib.sha256(model_path.read_bytes()).hexdigest()
    text = re.sub(r"^INPUT_MODEL=.*$", "INPUT_MODEL=" + (ROOT / input_path).as_posix(), text, flags=re.M)
    text = re.sub(r"^OUTPUT_PREFIX=.*$", "OUTPUT_PREFIX=" + (output / model).as_posix(), text, flags=re.M)
    config = output / "article.conf"
    config.write_text(text, encoding="utf-8", newline="\n")
    command = [str(executable.resolve()), "--config", str(config)]
    started = time.perf_counter()
    with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
        try:
            process = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, timeout=timeout)
            code, status = process.returncode, "completed"
        except subprocess.TimeoutExpired:
            code, status = None, "timeout"
    report = {
        "model": model, "status": status, "exit_code": code,
        "wall_seconds": time.perf_counter() - started,
        "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
        "source_config_sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
        "input_model": str(model_path), "input_model_sha256": model_hash,
        "relocated_keys": ["INPUT_MODEL", "OUTPUT_PREFIX"],
        "command": command,
    }
    if hashlib.sha256(model_path.read_bytes()).hexdigest() != model_hash:
        raise ValueError("Input model changed during generation")
    (output / "process.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--model", choices=["eistute", "book", "decor_shelf"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args()
    report = run_case(args.exe, args.model, args.output, args.timeout)
    print(json.dumps(report))
    raise SystemExit(0 if report["exit_code"] == 0 else 1)
