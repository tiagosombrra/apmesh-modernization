#!/usr/bin/env python3
"""Collect reproducible M0 evidence without changing TRI scientific policy."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN_ENTRY = "f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94"
BRANCH = "quad-templates"


def git(*args: str) -> str:
    """Read Git metadata; failure must not be mistaken for a clean checkout."""
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save(report: dict, directory: Path) -> None:
    """Keep a usable report after each step, including partial failures."""
    temp = directory / "report.json.tmp"
    temp.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temp.replace(directory / "report.json")


def execute(
    report: dict, directory: Path, name: str, command: list[str], timeout: int
) -> bool:
    log = directory / f"{name}.log"
    started = time.monotonic()
    record = {
        "command": command,
        "log": log.name,
        "status": "running",
        "timeout_seconds": timeout,
    }
    report["steps"].append(record)
    save(report, directory)
    print(f"RUN {name}: {' '.join(command)}", flush=True)
    try:
        with log.open("wb") as stream:
            result = subprocess.run(
                command, cwd=ROOT, stdout=stream,
                stderr=subprocess.STDOUT, timeout=timeout
            )
        record["exit_code"] = result.returncode
        record["status"] = "passed" if result.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        record["status"] = "timeout"
        record["exit_code"] = None
    except OSError as exc:
        record["status"] = "unavailable"
        record["error"] = str(exc)
        record["exit_code"] = None
    record["elapsed_seconds"] = round(time.monotonic() - started, 3)
    record["log_sha256"] = sha256(log) if log.exists() else None
    save(report, directory)
    print(f"{name}: {record['status']} ({record['elapsed_seconds']}s)", flush=True)
    return record["status"] == "passed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("gcc", "msvc"), default="gcc")
    parser.add_argument(
        "--output", type=Path, help="New results directory (must not exist)"
    )
    parser.add_argument(
        "--science", action="store_true",
        help="Run frozen cases; does not compare independent oracles"
    )
    parser.add_argument("--build-timeout", type=int, default=1800)
    parser.add_argument("--ctest-timeout", type=int, default=1800)
    args = parser.parse_args()
    if args.build_timeout <= 0 or args.ctest_timeout <= 0:
        parser.error("Timeouts must be positive")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    directory = (
        args.output or ROOT / "build" / "quad-m0" / f"{stamp}-{args.mode}"
    ).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    report = {
        "schema": 1,
        "date_utc": stamp,
        "branch_required": BRANCH,
        "frozen_entry": FROZEN_ENTRY,
        "mode": args.mode,
        "source_root": str(ROOT),
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "python": sys.version,
            "machine": platform.machine(),
        },
        "steps": [],
        "status": "incomplete",
        "scientific_oracles_compared": False,
        "note": "Successful execution is not an independent scientific "
                "comparison or complete M0 qualification.",
    }
    save(report, directory)

    try:
        report["git"] = {
            "head": git("rev-parse", "HEAD"),
            "branch": git("branch", "--show-current"),
            "working_tree_status": git("status", "--porcelain"),
        }
        descendant = subprocess.run(
            ["git", "merge-base", "--is-ancestor", FROZEN_ENTRY, "HEAD"],
            cwd=ROOT,
        ).returncode == 0
        report["git"]["frozen_entry_is_ancestor"] = descendant
        if (
            report["git"]["branch"] != BRANCH
            or report["git"]["working_tree_status"]
            or not descendant
        ):
            raise ValueError(
                "Wrong branch, dirty worktree, or frozen baseline not in ancestry"
            )
        if not (ROOT / "CMakePresets.json").is_file():
            raise ValueError("CMakePresets.json is missing")
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        report["status"] = "blocked_preflight"
        report["preflight_error"] = str(exc)
        save(report, directory)
        print(
            f"BLOCKED: {exc}\nEvidence: {directory / 'report.json'}",
            file=sys.stderr,
        )
        return 2
    save(report, directory)

    versions = [
        ("git-version", ["git", "--version"]),
        ("cmake-version", ["cmake", "--version"]),
        ("python-version", [sys.executable, "--version"]),
    ]
    if args.mode == "gcc":
        versions.append(("compiler-version", ["g++", "--version"]))
    for name, command in versions:
        if not execute(report, directory, name, command, 20):
            report["status"] = "blocked_toolchain"
            save(report, directory)
            return 1
    preset = "local-serial" if args.mode == "gcc" else "windows-msvc-serial"
    steps = [
        ("configure", ["cmake", "--preset", preset], args.build_timeout),
        (
            "build",
            ["cmake", "--build", "--preset", preset, "--parallel", "2"],
            args.build_timeout,
        ),
    ]
    if args.mode == "gcc":
        steps.extend([
            ("ctest-inventory", ["ctest", "--preset", preset, "-N"], 120),
            (
                "ctest",
                ["ctest", "--preset", preset, "--output-on-failure"],
                args.ctest_timeout,
            ),
        ])
    for name, command, timeout in steps:
        if not execute(report, directory, name, command, timeout):
            report["status"] = f"blocked_{name}"
            save(report, directory)
            return 1

    if args.science:
        executable = ROOT / (
            "build/local-serial/bin/ap_mesh" if args.mode == "gcc"
            else "build/windows-msvc-serial/bin/Debug/ap_mesh.exe"
        )
        if args.mode == "gcc" and not executable.exists():
            alternative = executable.with_suffix(".exe")
            if alternative.exists():
                executable = alternative
        if not executable.is_file():
            report["status"] = "blocked_science_executable"
            report["missing_executable"] = str(executable)
            save(report, directory)
            return 1
        report["executable_sha256"] = sha256(executable)
        for model in ("eistute", "book"):
            command = [
                sys.executable, "tools/run_generation_case.py",
                "--exe", str(executable), "--model", model,
                "--output", str(directory / f"science-{model}"),
                "--timeout", "300",
            ]
            if not execute(report, directory, f"science-{model}", command, 330):
                report["status"] = f"blocked_science_{model}"
                save(report, directory)
                return 1

    if not execute(
        report, directory, "quality-doctor",
        [sys.executable, "tools/quality.py", "doctor"], 90
    ):
        report["status"] = "blocked_quality_doctor"
        save(report, directory)
        return 1

    report["status"] = "execution_passed_oracles_pending"
    save(report, directory)
    print(
        "Execution completed; independent science and full M0 gates "
        f"remain pending.\nEvidence: {directory / 'report.json'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
