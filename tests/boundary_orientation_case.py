#!/usr/bin/env python3
"""Require actual generation to preserve aligned and reversed analytic boundaries."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests/tooling"))
from check_boundary_incidence import inspect_snapshot
from test_boundary_incidence import analytic_fixture
from verify_generation import verify_run


def run_control(executable, workspace, name, reverse, sheets):
    folder = workspace / name
    folder.mkdir()
    model = folder / "control.bp"
    fixture = analytic_fixture(sheet_count=sheets, reverse_last=reverse)
    lines = []
    for index, patch in enumerate(fixture["patches"]):
        lines.extend("v " + " ".join(format(x, ".17g") for x in point)
                     for point in patch["control_points"])
        lines.append("p " + " ".join(str(index * 16 + j) for j in range(16)))
    model.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    config = folder / "article.conf"
    config.write_text(
        f"INPUT_MODEL={model.as_posix()}\nOUTPUT_PREFIX={(folder / 'control').as_posix()}\n"
        "NUM_PROCESSES=1\nNUM_THREADS=1\nWRITE_MODE=h\nUSE_TEMPLATE=y\nADAPTIVE_MAX_STEPS=1\n",
        encoding="utf-8", newline="\n")
    command = [str(executable), "--config", str(config)]
    with (folder / "stdout.log").open("wb") as stdout, (folder / "stderr.log").open("wb") as stderr:
        process = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, timeout=60)
    metadata = {"model": name, "status": "completed", "exit_code": process.returncode,
                "input_model": str(model), "input_model_sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
                "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(), "command": command}
    (folder / "process.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n")
    result = {"case": name, "sheets": sheets, "reversed": reverse, "process": metadata}
    try:
        verified = verify_run(folder, require_boundary=True)
        result.update(status="passed", boundary_incidences=verified["boundary_incidences"])
    except (ValueError, OSError) as error:
        result.update(status="failed", error=str(error))
        snapshot = folder / "control_passo_0_incidences.json"
        if snapshot.exists():
            # Preserve boundary evidence even when independent mesh validity fails first.
            try:
                result["boundary_diagnostic"] = inspect_snapshot(
                    snapshot, model, folder / "control_passo_0_malha_0.obj", 0)
            except (ValueError, OSError) as diagnostic_error:
                result["boundary_diagnostic_error"] = str(diagnostic_error)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    args.workspace.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="run-", dir=args.workspace)).resolve()
    try:
        cases = [run_control(args.exe.resolve(), workspace, name, reverse, sheets)
                 for name, reverse, sheets in [("aligned_manifold", False, 2),
                                              ("reversed_manifold", True, 2),
                                              ("aligned_nonmanifold", False, 3),
                                              ("reversed_nonmanifold", True, 3)]]
        report = {"status": "passed" if all(c["status"] == "passed" for c in cases) else "failed",
                  "workspace": str(workspace), "cases": cases}
        report_path = args.report or workspace / "orientation_report.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({"status": report["status"], "report": str(report_path),
                          "cases": [{"case": c["case"], "status": c["status"], "error": c.get("error")}
                                    for c in cases]}))
        raise SystemExit(0 if report["status"] == "passed" else 1)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"Orientation generation control failed: {error}\n")
