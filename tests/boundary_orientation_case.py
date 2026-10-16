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


def run_control(executable, workspace, name, reverse, sheets, *, curved=False, slot=3, adaptive=False, force_retry=False):
    folder = workspace / name
    folder.mkdir()
    model = folder / "control.bp"
    fixture = analytic_fixture(sheet_count=sheets, reverse_last=reverse)
    if curved:
        base_curve = [(0, 0, 0), (0, 0, 0.15), (0, 0.2, 0.55), (0, 1, 1)]
        vectors = [(1, 0, 0), (-1, 0.7, 0), (0, -1, 0.3)]
        for index, patch in enumerate(fixture["patches"]):
            curve = base_curve[::-1] if reverse and index == sheets - 1 else base_curve
            patch["control_points"] = [
                [p[k] + u * vectors[index][k] for k in range(3)]
                for p in curve for u in [0.0, 1 / 3, 2 / 3, 1.0]]
    if slot != 3:
        controls = fixture["patches"][-1]["control_points"]
        def old_indices(i, j):
            return [(j, i), (3 - i, j), (3 - j, i), (i, j)][slot]
        fixture["patches"][-1]["control_points"] = [
            controls[old_indices(i, j)[1] * 4 + old_indices(i, j)[0]]
            for j in range(4) for i in range(4)]
    lines = []
    for index, patch in enumerate(fixture["patches"]):
        lines.extend("v " + " ".join(format(x, ".17g") for x in point)
                     for point in patch["control_points"])
        lines.append("p " + " ".join(str(index * 16 + j) for j in range(16)))
    model.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    config = folder / "article.conf"
    config_text = (
        f"INPUT_MODEL={model.as_posix()}\nOUTPUT_PREFIX={(folder / 'control').as_posix()}\n"
        "NUM_PROCESSES=1\nNUM_THREADS=1\nWRITE_MODE=h\nUSE_TEMPLATE=y\n"
        f"ADAPTIVE_MAX_STEPS={3 if adaptive else 1}\n")
    if adaptive:
        config_text += "EPSYLON=0.0000001\nPATCH_QUADTREE_DEPTH_STEP1=3\nPATCH_QUADTREE_DEPTH_STEPN=3\nADAPTIVE_RETRY_COUNT=1\n"
    if force_retry:
        config_text += "ADAPTIVE_TARGET_GROWTH=1.01\nADAPTIVE_QUALITY_PRIORITY=1.0\nADAPTIVE_INTENSITY=1.0\nADAPTIVE_RETRY_SHRINK=0.72\n"
    config.write_text(config_text, encoding="utf-8", newline="\n")
    command = [str(executable), "--config", str(config)]
    with (folder / "stdout.log").open("wb") as stdout, (folder / "stderr.log").open("wb") as stderr:
        process = subprocess.run(command, cwd=ROOT, stdout=stdout, stderr=stderr, timeout=60)
    metadata = {"model": name, "status": "completed", "exit_code": process.returncode,
                "input_model": str(model), "input_model_sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
                "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(), "command": command}
    (folder / "process.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n")
    result = {"case": name, "sheets": sheets, "reversed": reverse, "curved": curved, "slot": slot, "adaptive": adaptive, "force_retry": force_retry, "process": metadata}
    try:
        verified = verify_run(folder, require_boundary=True)
        if adaptive:
            if len(verified["boundary_incidences"]) < 2:
                raise ValueError("Adaptive orientation control did not exercise reconstruction")
            if max(r["boundary_segments"] for r in verified["boundary_incidences"].values()) <= sheets * 4:
                raise ValueError("Adaptive orientation control did not refine boundary partitions")
        # retry_attempt records an accepted retry; rejected trials use budget_retry_count.
        retries = max(max(int(row.get("retry_attempt", "0")), int(row.get("budget_retry_count", "0")))
                      for row in verified["metrics"].values())
        if force_retry and (retries < 1 or not verified["rejected_steps"]):
            raise ValueError("Forced-retry orientation control did not exercise retry and rejection")
        result.update(status="passed", boundary_incidences=verified["boundary_incidences"],
                      accepted_steps=verified["accepted_steps"], rejected_steps=verified["rejected_steps"],
                      max_retry=retries)
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
        for sheets in [2, 3]:
            cases.append(run_control(args.exe.resolve(), workspace, f"curved_aligned_{sheets}",
                                     False, sheets, curved=True, adaptive=True))
            for slot in range(4):
                cases.append(run_control(args.exe.resolve(), workspace, f"curved_reversed_{sheets}_side_{slot}",
                                         True, sheets, curved=True, slot=slot, adaptive=True,
                                         force_retry=(sheets == 3 and slot == 2)))
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
