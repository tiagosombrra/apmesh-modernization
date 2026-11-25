"""Run one portable CurvaBezier grouping trial with an experimental selected OBJ."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from hashlib import sha256

from quad_grouping_admission import evaluate
from quad_transition_comparison import compare
from quad_adjacent_group_selector import select_adjacent_group


STEM = "step_3_retry_0_accepted"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write_json(path, content):
    pending = path.with_suffix(".pending")
    pending.write_text(json.dumps(content, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    os.replace(pending, path)


def publish_mesh(out, source):
    pending = out/"selected.obj.pending"
    pending.write_bytes(source.read_bytes())
    os.replace(pending, out/"selected.obj")


def original_curve_witness(path):
    return [line for line in path.read_bytes().splitlines()
            if line.startswith((b"# source_site ", b"# original_curve "))]


def run_mesh(exe, out, arm, grouped=False):
    config = (Path(__file__).resolve().parents[1]/"configs/quad/curved_patch_article_front.conf")
    lines = [f"OUTPUT_PREFIX={arm}" if line.startswith("OUTPUT_PREFIX=") else line
             for line in config.read_text(encoding="ascii").splitlines()]
    environment = os.environ.copy()
    environment.pop("APMESH_QUAD_GROUPING_PLAN", None)
    if grouped:
        environment["APMESH_QUAD_GROUPING_PLAN"] = "grouping.plan"
    conf = out/f"{arm}.conf"
    conf.write_text("\n".join(lines)+"\n", encoding="ascii")
    with (out/f"{arm}.stdout").open("xb") as stdout, (out/f"{arm}.stderr").open("xb") as stderr:
        subprocess.run([str(exe), "--config", conf.name], cwd=out, check=True, timeout=180,
                       stdout=stdout, stderr=stderr, env=environment)


def finish(out, result, source):
    result["selected_sha256"] = digest(out/"selected.obj")
    if result["selected_sha256"] != digest(source):
        raise ValueError("Selected OBJ differs from its recorded source")
    result["selected_source"] = source.relative_to(out).as_posix()
    write_json(out/"result.json", result)
    return result


def run_trial(exe, out, control):
    out.mkdir(parents=True)
    run_mesh(exe, out, "baseline")
    baseline_steps = out/"baseline.steps"
    basis = baseline_steps/f"{STEM}_quad_tri.obj"
    front_dir = baseline_steps/f"{STEM}_article_front"
    front_path = front_dir/"front.json"
    basis_hash = digest(basis)
    publish_mesh(out, basis)
    state = {"baseline_sha256": basis_hash, "image_sha256": digest(exe), "control": control,
             "mixed_adaptive_epochs": 0}
    try:
        selection = select_adjacent_group(front_dir, json.loads(front_path.read_text()), basis,
                                          control == "protect-neighbor")
        write_json(out/"selection.json", selection)
        state["projection"] = selection["selection"]["disposition"]
        if state["projection"] != "eligible":
            state["status"] = "no_action"
            return finish(out, state, basis)
        rows = ["apmesh_adjacent_group_v1"]
        rows += [" ".join(map(str, box)) for box in selection["selection"]["blocks"]]
        (out/"grouping.plan").write_text("\n".join(rows)+"\n", encoding="ascii")
        run_mesh(exe, out, "staging", grouped=True)
        staged_steps = out/"staging.steps"
        peers = sorted(p.name for p in baseline_steps.glob("step_*.obj"))
        if not peers or any(digest(baseline_steps/p) != digest(staged_steps/p) for p in peers):
            raise ValueError("Staging did not reproduce the predecessor histories")
        if digest(staged_steps/front_dir.name/front_path.name) != selection["predecessor_front"]:
            raise ValueError("Staging did not reproduce the selected front")
        candidate = staged_steps/"adjacent_trial/candidate.obj"
        original = original_curve_witness(basis)
        if not original or original != original_curve_witness(candidate):
            raise ValueError("Candidate did not preserve the original curve witness")
        reports = {}
        for n in (24,48):
            reports[n] = compare(basis, candidate, selection["region"], grid=n)
            write_json(out/f"comparison-{n}.json", reports[n])
        decision = evaluate(reports[24], reports[48])
        state["decision"] = decision
        state["candidate_sha256"] = digest(candidate)
        state["reference_history_files"] = peers
        if control == "force-reject":
            state["status"] = "rejected_control"
        elif decision["verdict"] == "eligible":
            state["status"] = "eligible_candidate_selected"
            publish_mesh(out, candidate)
            return finish(out, state, candidate)
        else:
            state["status"] = decision["verdict"]
        return finish(out, state, basis)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        if digest(out/"selected.obj") != basis_hash:
            publish_mesh(out, basis)
        state.update(status="failed", error=str(error))
        finish(out, state, basis)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True, help="QUAD-enabled ap_mesh executable")
    parser.add_argument("--out", type=Path, required=True, help="New directory for this trial")
    parser.add_argument("--control", choices=("force-reject","protect-neighbor"))
    args = parser.parse_args()
    try:
        result = run_trial(args.exe.resolve(strict=True), args.out.resolve(), args.control)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Grouping trial failed: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
