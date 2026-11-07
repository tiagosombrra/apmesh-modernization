#!/usr/bin/env python3
"""Observe the five fixed terminal contexts through the checked-CRT executable window."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from qualify_serial_crt_lifetime import inspect_lifetime, qualify_control

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from typed_domain_failure_case import validate_cli, validate_library, validate_types
from verify_generation import verify_run


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixed_contexts(ledger):
    contexts = [case for case in ledger["cases"] if case["id"] in ("SP-09", "SP-10")]
    actual = [(case["id"], context["model"], context["step"], context["patch"], context["calls"])
              for case in contexts for context in case["contexts"]]
    expected = [("SP-09", "book", 2, 0, 1), ("SP-09", "eistute", 2, 0, 2),
                ("SP-09", "eistute", 2, 1, 2), ("SP-10", "book", 2, 0, 1),
                ("SP-10", "eistute", 2, 1, 2)]
    if actual != expected or len(contexts) != 2 or any(
            case["timeout_seconds_each"] != 300 for case in contexts):
        raise ValueError("Fixed five-context terminal inventory or cap changed")
    return contexts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    executable, output = args.exe.resolve(strict=True), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    ledger = json.loads((ROOT / "docs/evidence/stage3/serial_execution/ledger.json").read_text())
    report = {"schema": 1, "status": "qualifying", "controls": [], "cases": [], "stage_closure": False,
              "executable": str(executable), "executable_sha256": digest(executable),
              "scope": "controlled full-caller executable-owned normal/client CRT interval"}

    def launch(name, arguments, cap, control=False):
        if digest(executable) != report["executable_sha256"]:
            raise ValueError("Qualified terminal executable changed")
        folder = output / name
        folder.mkdir(exist_ok=False)
        row = {"name": name, "command": [str(executable), *map(str, arguments)],
               "timeout_seconds": cap, "status": "started"}
        (report["controls"] if control else report["cases"]).append(row)
        print(json.dumps({"event": "launch", "name": name, "timeout_seconds": cap}), flush=True)
        with (folder / "stdout.log").open("wb") as stdout, (folder / "stderr.log").open("wb") as stderr:
            process = subprocess.run(row["command"], cwd=ROOT, stdout=stdout, stderr=stderr, timeout=cap)
        row["exit_code"] = process.returncode
        stdout = (folder / "stdout.log").read_text(encoding="utf-8", errors="replace")
        stderr = (folder / "stderr.log").read_text(encoding="utf-8", errors="replace")
        row["observer"] = inspect_lifetime(stdout, stderr, process.returncode)
        return folder, row, stdout + stderr

    try:
        contexts = fixed_contexts(ledger)
        for mode in ("release", "global-release", "late-release", "retention", "late-retention", "denial"):
            folder, row, text = launch("lifetime-" + mode, ["--lifetime-control", mode], 10, True)
            qualify_control(mode, row["observer"])
            row["status"] = "passed_expected_retention" if mode.endswith("retention") else "passed"
        for name, flag in (("terminal-release", "--instrument-release"),
                           ("observer-contracts", "--observer-contracts"),
                           ("typed-contracts", "--typed-domain-contracts")):
            folder, row, text = launch(name, [flag], 10, True)
            if row["exit_code"] or not row["observer"]["clean"]:
                raise ValueError("Terminal fixture prerequisite retains storage or failed")
            if name == "terminal-release":
                if "terminal_instrument release=1" not in text:
                    raise ValueError("Actual terminal release marker absent")
            elif name == "observer-contracts":
                if ("terminal_observer selected=1 excluded=2 disabled=1 live_aft=1 hook_denied=1" not in text
                        or "terminal_native_submesh allocation=1 release=1 uncaught=0" not in text):
                    raise ValueError("Live AFT, exclusion or actual allocation qualification absent")
            else:
                validate_types(row["exit_code"], text)
                found = re.search(r"^terminal_unwind_allocation calls=(\d+) uncaught=(\d+) attempts=(\d+) denied=(\d+)$", text, re.M)
                if not found or tuple(map(int, found.groups())) != (1, 1, 1, 1):
                    raise ValueError("Real SubMesh allocation during unwind was not denied exactly")
            row["status"] = "passed"
            print(json.dumps({"event": "control_passed", "name": name}), flush=True)
        report["instrument_and_fixture_controls"] = "passed"
        for spec in contexts:
            for context in spec["contexts"]:
                model, patch = context["model"], context["patch"]
                name = f"{spec['id']}-{model}-p{patch}"
                folder = output / name
                config_folder = output / "configurations"
                config_folder.mkdir(exist_ok=True)
                source = ROOT / "configs" / model / "article.conf"
                text = source.read_text(encoding="utf-8")
                input_model = (ROOT / re.search(r"^INPUT_MODEL=(.*)$", text, re.M)[1].strip()).resolve()
                text = re.sub(r"^INPUT_MODEL=.*$", "INPUT_MODEL=" + input_model.as_posix(), text, flags=re.M)
                text = re.sub(r"^OUTPUT_PREFIX=.*$", "OUTPUT_PREFIX=" + (folder / model).as_posix(), text, flags=re.M)
                config = config_folder / (name + ".conf")
                config.write_text(text, encoding="utf-8", newline="\n")
                mode = "--typed-domain-cli-config" if spec["id"] == "SP-09" else "--typed-domain-library-config"
                folder, row, text = launch(name, [mode, config, patch], spec["timeout_seconds_each"])
                row.update(group=spec["id"], context=context, source_config_sha256=digest(source),
                           input_model_sha256=digest(input_model), config_sha256=digest(config))
                if not row["observer"]["clean"]:
                    raise ValueError("Terminal context retains executable-owned CRT storage")
                if spec["id"] == "SP-09":
                    validate_cli(row["exit_code"], text, patch, context["calls"])
                    (folder / "process.json").write_text(json.dumps({"status": "completed", "exit_code": row["exit_code"]}) + "\n", encoding="utf-8", newline="\n")
                    try:
                        verify_run(folder)
                    except ValueError as error:
                        if str(error) != "Generation did not complete successfully":
                            raise
                        row["failed_prefix_rejected"] = True
                    else:
                        raise ValueError("Failed terminal prefix was accepted as successful generation")
                else:
                    validate_library(row["exit_code"], text, model)
                row["status"] = "passed"
                print(json.dumps({"event": "context_passed", "name": name}), flush=True)
        report["status"] = "fixed_terminal_crt_contexts_passed"
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        report.update(status="stopped_at_first_unexpected_failure", error=str(error))
        for row in report["controls"] + report["cases"]:
            if row["status"] == "started":
                row.update(status="failed", error=str(error))
    finally:
        report["artifacts"] = {p.relative_to(output).as_posix(): digest(p)
                               for p in sorted(output.rglob("*")) if p.is_file()}
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "controls": len(report["controls"]),
                      "cases": len(report["cases"]), "error": report.get("error"),
                      "report": str(output / "report.json")}))
    return int(report["status"] != "fixed_terminal_crt_contexts_passed")


if __name__ == "__main__":
    raise SystemExit(main())
