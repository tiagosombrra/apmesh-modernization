#!/usr/bin/env python3
"""Check the actual exporter against explicit candidate and accepted-state oracles."""

import argparse
import csv
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile


def check_archive_controls(exe, root):
    def launch(mode, folder):
        process = subprocess.Popen([str(exe), "--archive-control", mode, str(folder)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = process.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise
        return process, stdout, stderr

    modes = ["closed", "occupied"] + (["held", "external"] if os.name == "nt" else [])
    observations = []
    for mode in modes:
        folder = root / ("archive-" + mode)
        if mode == "external":
            (folder / "live").mkdir(parents=True)
            source = folder / "live" / "output.txt"
            source.write_text("known external file owner\n", encoding="utf-8")
            with source.open(encoding="utf-8"):
                process, stdout, stderr = launch(mode, folder)
            owner = os.getpid()
        else:
            process, stdout, stderr = launch(mode, folder)
            owner = process.pid
        (root / (mode + "-stdout.log")).write_bytes(stdout)
        (root / (mode + "-stderr.log")).write_bytes(stderr)
        assert process.returncode == (0 if mode == "closed" else 1), (mode, stderr)
        if mode == "closed":
            assert b"archive_result status=completed" in stderr
            assert (folder / "first" / "output.txt").read_text() == "native archival ownership control\n"
            assert not (folder / "live").exists()
        else:
            assert b"archive_result status=failed" in stderr
            assert (folder / "live" / "output.txt").is_file()
            if mode == "occupied":
                assert (folder / "first" / "existing.txt").read_text() == "preserve occupied destination\n"
            else:
                assert b"archive_delete_access" in stderr and b"win32_error=32" in stderr
                assert re.search(rb"archive_owner pid=" + str(owner).encode() + rb"\b", stderr), stderr
                assert not (folder / "first").exists()
        observations.append({"mode": mode, "status": "passed"})
    return observations


def check(root):
    with (root / "attempt_n.process__metrics_rank_-1.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 6
    # Independently specified state transitions and expected report values.
    errors = [10, 8, 12, 9, 4, 6]
    counts = [2, 4, 6, 8, 5, 7]
    previous = [2, 2, 4, 4, 4, 5]
    scores = [0, .25, -.5, -.125, .75, -.25]
    gauss, mean = [6, 9, 15, 21, 12, 0], [0, 3, 3, 3, 3, 0]
    retries = [0, 0, 1, 2, 1, 3]
    relaxation, max_delta = [.8, .6, .3, .15, .4, .1], [.2, .15, .075, .0375, .1, .025]
    accepted_error = 10
    checked = 0
    log_fields = {"error": "error_global_current", "error_prev": "error_global_previous",
                  "elements_prev": "elements_previous", "gauss_nodes": "curvature_mode_gauss_nodes",
                  "mean_nodes": "curvature_mode_mean_nodes"}
    for step, row in enumerate(rows):
        delta = max(counts[step] - previous[step], 0)
        drop = accepted_error - errors[step]
        expected = {"step": step, "elements": counts[step], "error": errors[step],
                    "error_prev": accepted_error, "elements_prev": previous[step],
                    "elements_delta": delta, "element_growth_factor": counts[step]/previous[step],
                    "actual_element_growth": counts[step]/previous[step],
                    "actual_growth_step": counts[step]/previous[step],
                    "error_improvement_abs": drop, "error_improvement_pct": 100*drop/accepted_error,
                    "error_improvement_per_element": drop/delta if delta else drop,
                    "error_normalized": errors[step]/10,
                    "error_total_reduction_pct": (10-errors[step])*10,
                    "acceptance_score": scores[step], "gauss_nodes": gauss[step], "mean_nodes": mean[step],
                    "gauss_ratio": gauss[step]/(gauss[step]+mean[step]) if gauss[step] else 0,
                    "mean_ratio": mean[step]/(gauss[step]+mean[step]) if mean[step] else 0,
                    "retry_attempt": retries[step], "adaptation_relaxation": relaxation[step],
                    "adaptation_max_delta": max_delta[step]}
        log = dict(line.split("=", 1) for line in
                   (root / f"attempt_n.process__passo_{step}_qualite_{step}_rank_-1.log").read_text().splitlines()
                   if "=" in line)
        for field, value in expected.items():
            assert math.isclose(float(row[field]), value, rel_tol=5e-6, abs_tol=5e-7), (step, field, row[field], value)
            name = log_fields.get(field, field)
            if name in log and field != "step":
                assert math.isclose(float(log[name]), value, rel_tol=5e-6, abs_tol=5e-7), (step, name)
            checked += 1
        if step in (0, 1, 4):
            accepted_error = errors[step]
    with (root / "zero_n.process__metrics_rank_-1.csv").open(newline="") as stream:
        zero_rows = list(csv.DictReader(stream))
    assert len(zero_rows) == 2
    assert [float(row["error_normalized"]) for row in zero_rows] == [1, 0]
    assert all(float(row["error_total_reduction_pct"]) == 0 for row in zero_rows)
    return {"status": "passed", "attempts": 8, "candidate_field_checks": checked,
            "sequence": "initial/accepted/rejected/rejected/accepted/rejected-before-curvature"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    args.workspace.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="run-", dir=args.workspace)).resolve()
    subprocess.run([str(args.exe.resolve()), str(work / "output")], check=True, timeout=30)
    report = check(work / "output")
    report["archive_controls"] = check_archive_controls(args.exe.resolve(), work)
    (work / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**report, "report": str(work / "report.json")}))
