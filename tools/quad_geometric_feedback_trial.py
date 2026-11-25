"""Stage a geometric feedback comparison from a recorded CurvaBezier selection."""

import argparse
import csv
import json
from pathlib import Path
import subprocess

from quad_adjacent_group_selector import protected_size_requests
from quad_grouping_trial import (
    BASELINE, BASELINE_FRONT, CANDIDATE, CANDIDATE_FRONT, digest,
    original_curve_witness, run_mesh, selected_payload, write_json,
)
from quad_transition_comparison import compare


def observations(directory, predecessor):
    lines = (directory / "result.txt").read_text(encoding="utf-8").splitlines()
    status = lines[0]
    cap, before, after, edits = map(int, lines[1].split())
    with (directory / "requests.csv").open(encoding="ascii", newline="") as stream:
        rows = list(csv.DictReader(stream))
    capped = [row for row in rows if row["disposition"] == "capped"]
    result = dict(status=status, depth_cap=cap, leaves_before=before, leaves_after=after,
                  direct_leaf_edits=edits, requests=len(rows), capped_requests=len(capped))
    if status == "staged":
        candidate = directory / "candidate.obj"
        if original_curve_witness(candidate) != original_curve_witness(predecessor):
            raise ValueError("Staged successor changed the original curve")
        chart = [(0, 0), (1, 0), (1, 1), (0, 1)]
        for grid in (24, 48):
            report = compare(predecessor, candidate, chart, grid=grid)
            if not report["same_ordered_contour_edges"]:
                raise ValueError("Staged successor changed the directed contour")
            write_json(directory / f"comparison-{grid}.json", report)
        result["candidate_sha256"] = digest(candidate)
    elif status == "rejected":
        result["reason"] = lines[2]
    elif status != "no_action":
        raise ValueError("Unknown native feedback outcome")
    return result


def trial(exe, source, out):
    state = json.loads((source / "result.json").read_text(encoding="utf-8"))
    recovered = selected_payload(source, state)
    if state["status"] != "eligible_candidate_selected":
        raise ValueError("Feedback requires the grouped experimental selection")
    requests = {arm: protected_size_requests(source / mesh)
                for arm, mesh in (("predecessor", BASELINE), ("recovered", CANDIDATE))}
    out.mkdir(parents=True)
    (out / "grouping.plan").write_bytes((source / "grouping.plan").read_bytes())
    with (out / "feedback.plan").open("x", encoding="ascii", newline="\n") as stream:
        stream.write("apmesh_curvabezier_feedback_v1\n")
        for arm, measurements in requests.items():
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
    for name, prior in (("predecessor", steps / BASELINE.name), ("recovered", out / CANDIDATE)):
        outcome[name] = observations(steps / f"feedback_{name}", prior)
    write_json(out / "feedback-result.json", outcome)
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = trial(args.exe.resolve(strict=True), args.source.resolve(strict=True),
                       args.out.resolve())
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Geometric feedback trial failed: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
