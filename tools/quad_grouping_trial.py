"""Run one portable CurvaBezier grouping trial with an experimental selected OBJ."""

import argparse
import json
import os
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile
from hashlib import sha256

from quad_grouping_admission import evaluate
from quad_transition_comparison import compare
from quad_adjacent_group_selector import select_adjacent_group


STEM = "step_3_retry_0_accepted"
BASELINE = Path("baseline.steps") / f"{STEM}_quad_tri.obj"
BASELINE_FRONT = BASELINE.parent / f"{STEM}_article_front/front.json"
CANDIDATE = Path("staging.steps/adjacent_trial/candidate.obj")
CANDIDATE_FRONT = CANDIDATE.parent / "candidate_front/front.json"
SCHEMA = "apmesh.curvabezier_grouping_selection.v1"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write_bytes(path, content):
    with NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
        pending = Path(stream.name)
        try:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        except OSError:
            stream.close()
            pending.unlink(missing_ok=True)
            raise
    try:
        os.replace(pending, path)
    finally:
        pending.unlink(missing_ok=True)


def write_json(path, content):
    write_bytes(path, (json.dumps(content, indent=2, allow_nan=False)+"\n").encode("utf-8"))


def curve_rows(payload):
    return [line for line in payload.splitlines()
            if line.startswith((b"# source_site ", b"# original_curve "))]


def original_curve_witness(path):
    return curve_rows(path.read_bytes())


def selected_payload(out, record):
    if record.get("schema") != SCHEMA:
        raise ValueError("Unsupported grouping selection record")
    status = record["status"]
    if status not in ("baseline_ready", "failed", "no_action", "reject", "inconclusive",
                      "rejected_control", "eligible_candidate_selected"):
        raise ValueError("Unknown grouping selection status")
    accepted = status == "eligible_candidate_selected"
    mesh, front = (CANDIDATE, CANDIDATE_FRONT) if accepted else (BASELINE, BASELINE_FRONT)
    if record["selected_source"] != mesh.as_posix() or record["selected_front"] != front.as_posix():
        raise ValueError("Grouping selection record contains an invalid source")
    if accepted and (record["decision"]["verdict"] != "eligible" or
                     record["selected_sha256"] != record["candidate_sha256"]):
        raise ValueError("Grouping selection record has no eligible decision")
    prior = (out/BASELINE).read_bytes()
    if sha256(prior).hexdigest() != record["baseline_sha256"]:
        raise ValueError("Grouping predecessor does not match its recorded hash")
    if digest(out/BASELINE_FRONT) != record["baseline_front_sha256"]:
        raise ValueError("Grouping predecessor front does not match its recorded hash")
    payload = (out/mesh).read_bytes() if accepted else prior
    if sha256(payload).hexdigest() != record["selected_sha256"]:
        raise ValueError("Grouping selected mesh does not match its recorded hash")
    if digest(out/front) != record["selected_front_sha256"]:
        raise ValueError("Grouping selected front does not match its recorded hash")
    if not curve_rows(prior) or curve_rows(prior) != curve_rows(payload):
        raise ValueError("Grouping selection does not preserve its original curve witness")
    return payload


def recover(out):
    record = json.loads((out/"result.json").read_text(encoding="utf-8"))
    write_bytes(out/"selected.obj", selected_payload(out, record))
    return record


def run_mesh(exe, out, arm, grouped=False, feedback=False):
    config = (Path(__file__).resolve().parents[1]/"configs/quad/curved_patch_article_front.conf")
    lines = [f"OUTPUT_PREFIX={arm}" if line.startswith("OUTPUT_PREFIX=") else line
             for line in config.read_text(encoding="ascii").splitlines()]
    environment = os.environ.copy()
    environment.pop("APMESH_QUAD_GROUPING_PLAN", None)
    environment.pop("APMESH_QUAD_FEEDBACK_PLAN", None)
    if grouped:
        environment["APMESH_QUAD_GROUPING_PLAN"] = "grouping.plan"
    if feedback:
        environment["APMESH_QUAD_FEEDBACK_PLAN"] = "feedback.plan"
    conf = out/f"{arm}.conf"
    conf.write_text("\n".join(lines)+"\n", encoding="ascii")
    with (out/f"{arm}.stdout").open("xb") as stdout, (out/f"{arm}.stderr").open("xb") as stderr:
        subprocess.run([str(exe), "--config", conf.name], cwd=out, check=True, timeout=180,
                       stdout=stdout, stderr=stderr, env=environment)


def finish(out, result, selected):
    front = CANDIDATE_FRONT if selected == CANDIDATE else BASELINE_FRONT
    result["selected_source"] = selected.as_posix()
    result["selected_sha256"] = digest(out/selected)
    result["selected_front"] = front.as_posix()
    result["selected_front_sha256"] = digest(out/front)
    # The record is authoritative. An interruption during materialization can replay it.
    payload = selected_payload(out, result)
    write_json(out/"result.json", result)
    write_bytes(out/"selected.obj", payload)
    return result


def prepare_candidate(exe, out, control, state):
    basis = out/BASELINE
    front_path = out/BASELINE_FRONT
    front_dir = front_path.parent
    baseline_steps = basis.parent
    selection = select_adjacent_group(front_dir, json.loads(front_path.read_text()), basis,
                                      control == "protect-neighbor")
    write_json(out/"selection.json", selection)
    state["projection"] = selection["selection"]["disposition"]
    if state["projection"] != "eligible":
        state["status"] = "no_action"
        return BASELINE
    rows = ["apmesh_adjacent_group_v1"]
    rows += [" ".join(map(str, box)) for box in selection["selection"]["blocks"]]
    if control == "force-reject":
        rows.append("verify_native_rejection")
    (out/"grouping.plan").write_text("\n".join(rows)+"\n", encoding="ascii")
    run_mesh(exe, out, "staging", grouped=True)
    if control == "force-reject":
        native_log = (out/"staging.stdout").read_bytes()
        witness = (b"QUAD_GROUPING_REJECTION previous_owner_preserved=1 "
                   b"previous_obj_preserved=1 candidate_unpublished=1")
        if native_log.splitlines().count(witness) != 1:
            raise ValueError("Grouping did not verify one native rejection")
        state["native_rejection_verified"] = True
    staged_steps = out/"staging.steps"
    peers = sorted(p.name for p in baseline_steps.glob("step_*.obj"))
    if not peers or any(digest(baseline_steps/p) != digest(staged_steps/p) for p in peers):
        raise ValueError("Staging did not reproduce the predecessor histories")
    if digest(staged_steps/front_dir.name/front_path.name) != selection["predecessor_front"]:
        raise ValueError("Staging did not reproduce the selected front")
    candidate = out/CANDIDATE
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
        return CANDIDATE
    else:
        state["status"] = decision["verdict"]
    return BASELINE


def run_trial(exe, out, control):
    out.mkdir(parents=True)
    run_mesh(exe, out, "baseline")
    state = {"schema": SCHEMA, "baseline_sha256": digest(out/BASELINE),
             "baseline_front_sha256": digest(out/BASELINE_FRONT),
             "image_sha256": digest(exe), "control": control, "mixed_adaptive_epochs": 0,
             "status": "baseline_ready"}
    finish(out, state, BASELINE)
    try:
        selected = prepare_candidate(exe, out, control, state)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        state.update(status="failed", error=str(error))
        finish(out, state, BASELINE)
        raise
    return finish(out, state, selected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, help="QUAD-enabled ap_mesh executable")
    parser.add_argument("--out", type=Path, help="New directory for this trial")
    parser.add_argument("--control", choices=("force-reject","protect-neighbor"))
    parser.add_argument("--recover", type=Path, help="Restore selected.obj from an existing result")
    args = parser.parse_args()
    if args.recover is not None:
        if args.exe is not None or args.out is not None or args.control is not None:
            parser.error("--recover must be used alone")
    elif args.exe is None or args.out is None:
        parser.error("--exe and --out are required for a new trial")
    try:
        if args.recover is not None:
            result = recover(args.recover.resolve(strict=True))
        else:
            result = run_trial(args.exe.resolve(strict=True), args.out.resolve(), args.control)
    except (ValueError, KeyError, TypeError, AttributeError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Grouping trial failed: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
