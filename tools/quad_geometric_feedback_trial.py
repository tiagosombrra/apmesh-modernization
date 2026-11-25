"""Stage a geometric feedback comparison from a recorded CurvaBezier selection."""

import argparse
import csv
import json
from pathlib import Path
import subprocess

from quad_adjacent_group_selector import geometric_size_requests
from quad_grouping_trial import (
    BASELINE, BASELINE_FRONT, CANDIDATE, CANDIDATE_FRONT, digest,
    original_curve_witness, run_mesh, selected_payload, write_json,
)
from quad_transition_comparison import compare, golden


def observations(directory, predecessor, curve_splits=0, evaluate=golden):
    lines = (directory / "result.txt").read_text(encoding="utf-8").splitlines()
    status = lines[0]
    cap, before, after, edits = map(int, lines[1].split())
    old_segments, new_segments = map(int, lines[3].split())
    if new_segments != old_segments + curve_splits:
        raise ValueError("Unexpected native curve feedback partition")
    with (directory / "requests.csv").open(encoding="ascii", newline="") as stream:
        rows = list(csv.DictReader(stream))
    capped = [row for row in rows if row["disposition"] == "capped"]
    result = dict(status=status, depth_cap=cap, leaves_before=before, leaves_after=after,
                  direct_leaf_edits=edits, requests=len(rows), capped_requests=len(capped),
                  segments_before=old_segments, segments_after=new_segments)
    if status == "staged":
        candidate = directory / "candidate.obj"
        original = original_curve_witness(predecessor)
        selected = original_curve_witness(candidate)
        def stable_fields(rows):
            return {tuple(row.split()[:10]) for row in rows}
        if curve_splits:
            if not stable_fields(original) <= stable_fields(selected):
                raise ValueError("Curve feedback replaced an original sample")
        elif selected != original:
            raise ValueError("Staged successor changed the original curve")
        chart = [(0, 0), (1, 0), (1, 1), (0, 1)]
        for grid in (24, 48):
            report = compare(predecessor, candidate, chart, evaluate, grid)
            if not curve_splits and not report["same_ordered_contour_edges"]:
                raise ValueError("Staged successor changed the directed contour")
            write_json(directory / f"comparison-{grid}.json", report)
        result["candidate_sha256"] = digest(candidate)
    elif status == "rejected":
        result["reason"] = lines[2]
    elif status != "no_action":
        raise ValueError("Unknown native feedback outcome")
    return result


def trial(exe, source, out, mode="tree"):
    state = json.loads((source / "result.json").read_text(encoding="utf-8"))
    recovered = selected_payload(source, state)
    if state["status"] != "eligible_candidate_selected":
        raise ValueError("Feedback requires the grouped experimental selection")
    requests = {arm: geometric_size_requests(source / mesh)
                for arm, mesh in (("predecessor", BASELINE), ("recovered", CANDIDATE))}
    curves = requests["recovered"][1] if mode in ("curve-and-tree", "guarded-curve-and-tree") else []
    out.mkdir(parents=True)
    (out / "grouping.plan").write_bytes((source / "grouping.plan").read_bytes())
    with (out / "feedback.plan").open("x", encoding="ascii", newline="\n") as stream:
        stream.write("apmesh_curvabezier_feedback_v1\n")
        if mode == "previous-search":
            stream.write("previous_search\n")
        if mode == "guarded-curve-and-tree":
            stream.write("guarded_smoothing\n")
        for item in curves:
            stream.write(f"curve {item['interval']}\n")
        for arm, (measurements, _) in requests.items():
            for item in measurements:
                u, v = item["site"]
                stream.write(f"{arm} {item['face']} {u:.17g} {v:.17g} {item['h']:.17g}\n")
    run_mesh(exe, out, "staging", grouped=True, feedback=True)
    steps = out / "staging.steps"
    for src, generated in ((BASELINE, steps / BASELINE.name),
                           (BASELINE_FRONT, steps / BASELINE_FRONT.relative_to(BASELINE.parent)),
                           (CANDIDATE, out / CANDIDATE), (CANDIDATE_FRONT, out / CANDIDATE_FRONT)):
        if digest(source / src) != digest(generated):
            raise ValueError("Native feedback did not reproduce the recorded predecessor")
    if (source / CANDIDATE).read_bytes() != recovered:
        raise ValueError("Recorded recovered mesh changed during feedback")
    outcome = dict(recovered_sha256=state["selected_sha256"],
                   selection_record_sha256=digest(source / "result.json"),
                   engine_sha256=digest(exe), mixed_adaptive_epochs=0)
    outcome["mode"] = mode
    if mode == "tree":
        outcome["predecessor"] = observations(steps / "feedback_predecessor", steps / BASELINE.name)
    outcome["recovered"] = observations(steps / "feedback_recovered", out / CANDIDATE, len(curves))
    if curves:
        outcome["curve_requests"] = curves
    write_json(out / "feedback-result.json", outcome)
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--mode", choices=("tree", "previous-search", "curve-and-tree", "guarded-curve-and-tree"), default="tree")
    args = parser.parse_args()
    try:
        result = trial(args.exe.resolve(strict=True), args.source.resolve(strict=True),
                       args.out.resolve(), args.mode)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Geometric feedback trial failed: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
