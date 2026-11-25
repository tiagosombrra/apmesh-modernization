"""Check selected output against the native files in each grouping trial outcome."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
ENTRY = ROOT / "tools/quad_grouping_trial.py"
STEM = "step_3_retry_0_accepted_quad_tri.obj"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(exe, out, control=None):
    command = [sys.executable, str(ENTRY), "--exe", str(exe), "--out", str(out)]
    if control:
        command += ["--control", control]
    # An inherited plan must never leak into the independent reference process.
    environment = os.environ.copy()
    environment["APMESH_QUAD_GROUPING_PLAN"] = "nonexistent-inherited.plan"
    subprocess.run(command, cwd=out.parent, check=True, timeout=365, env=environment)
    result = json.loads((out/"result.json").read_text(encoding="utf-8"))
    base = out/"baseline.steps"/STEM
    staged = out/"staging.steps/adjacent_trial/candidate.obj"
    expected_status = {None: "eligible_candidate_selected",
                       "force-reject": "rejected_control", "protect-neighbor": "no_action"}[control]
    if result["status"] != expected_status or result["mixed_adaptive_epochs"] != 0:
        raise ValueError(f"Unexpected trial disposition: {result}")
    if digest(base) != result["baseline_sha256"]:
        raise ValueError("Trial altered its baseline")
    if control == "protect-neighbor":
        if staged.exists() or result["projection"] != "active_smaller_size_request":
            raise ValueError("Fine-size veto did not prevent native staging")
    else:
        if result["decision"]["verdict"] != "eligible" or digest(staged) == digest(base):
            raise ValueError("Expected a distinct, eligible native candidate")
        if len(result["reference_history_files"]) != 8:
            raise ValueError("Expected eight compared native histories")
    selected = staged if control is None else base
    if digest(out/"selected.obj") != digest(selected) or result["selected_sha256"] != digest(selected):
        raise ValueError("Selected file differs from the recorded outcome")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    # Use a fresh location and a path with spaces for the subprocess contract.
    with TemporaryDirectory(dir=args.directory.resolve(), prefix="grouping trials ") as name:
        directory = Path(name)
        for control in (None, "force-reject", "protect-neighbor"):
            check(args.exe.resolve(), directory/(control or "eligible"), control)


if __name__ == "__main__":
    main()
