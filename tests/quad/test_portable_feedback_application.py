"""Run the portable native feedback trial on the two development geometries."""

import argparse
from functools import partial
import json
from math import dist, isclose, isfinite
from pathlib import Path
import sys

from audit_model_catalog import parse_bp
from independent_common_grid import load_physical_obj

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from quad_generation_metrics import geometry_error_at_sites
from quad_portable_feedback_trial import run
from quad_transition_comparison import bernstein, golden


def ribbed_fixture(destination):
    raw = (ROOT / "input_models/ribbed_bracket_nm_decor.bp").read_text(encoding="utf-8")
    points, patches = parse_bp(raw)
    controls = [points[i] for i in patches[12]]
    records = ["v " + " ".join(format(x, ".17g") for x in point) for point in controls]
    records.append("p " + " ".join(map(str, range(16))))
    destination.write_text("\n".join(records) + "\n", encoding="ascii")
    return str(destination)


def verify_birth_trace(feedback, schema):
    trace = json.loads((feedback / "candidate_front/front.json").read_text(encoding="utf-8"))
    _, uv, faces = load_physical_obj(feedback / "smoothing_comparison/before.obj")
    if (trace["schema"] != schema
            or trace["smoothing"] is not None or not trace["commits"]
            or [tuple(site) for site in trace["vertices"]] != uv
            or [tuple(face) for face in trace["seed_faces"]]
            + [tuple(step["polygon"]) for step in trace["commits"]] != faces):
        raise ValueError(f"Guarded birth history differs from its native frame: {feedback}")
    return trace


def verify_screened_pairs(feedback, evaluate, limit):
    trace = verify_birth_trace(feedback, "apmesh.quad.article_front_screened_pairs.v1")
    if trace["additional_pair_error_limit"] != limit:
        raise ValueError("Additional-pair error limit differs from the plan")
    xyz, uv, _ = load_physical_obj(feedback / "smoothing_comparison/before.obj")
    accepted, blocked = 0, 0
    for step in trace["commits"]:
        if step["selected_side"] >= 0:
            if "pair_measurements" in step or "additional_pair" in step:
                raise ValueError("A legacy QUAD decision was screened")
            continue
        passing = []
        for row in step["pair_measurements"]:
            face = row["quad"]
            if face[:2] != step["best"][:2] or not 1 <= row["score"] <= 1.5:
                raise ValueError("Additional pair changed the active base or shape limit")
            chord = dist(xyz[face[0]], xyz[face[1]])
            if not isfinite(chord) or chord <= 0:
                if row["relative_error"] is not None:
                    raise ValueError("Unavailable active edge has a measured relative error")
                blocked += 1
                continue
            sites = []
            for s, t in ((.5, .5), (.25, .25), (.75, .25), (.75, .75), (.25, .75)):
                weights = ((1-s)*(1-t), s*(1-t), s*t, (1-s)*t)
                sites.append(tuple(sum(w*uv[i][axis] for w, i in zip(weights, face))
                                   for axis in range(2)))
            observed = geometry_error_at_sites(xyz, uv, (face,), sites, evaluate)["max_xyz"]/chord
            measured = row["relative_error"]
            if measured is None and not isfinite(observed):
                blocked += 1
                continue
            if measured is None or not isclose(observed, measured, rel_tol=2e-9, abs_tol=1e-11):
                raise ValueError("Additional-pair error differs from independent analytic samples")
            if measured <= limit:
                passing.append(row)
            else:
                blocked += 1
        if passing:
            winner = min(passing, key=lambda row: row["score"])
            if (step["polygon"] != winner["quad"]
                    or step["additional_pair"]["score"] != winner["score"]):
                raise ValueError("Screened front did not retain the best passing pair")
            accepted += 1
        elif step["polygon"] != step["best"] or "additional_pair" in step:
            raise ValueError("Screened front did not retain the original TRI")
    return accepted, blocked


def main():
    from test_progressive_admission import fixture_profile

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    exe = args.exe.resolve(strict=True)
    directory = args.directory.resolve()
    directory.mkdir(parents=True)
    progressive_profile = directory / "progressive-test-profile.json"
    progressive_profile.write_text(json.dumps(fixture_profile()), encoding="ascii")
    cases = (("curva", "builtin:curva_bezier", 3, False),
             ("ribbed", ribbed_fixture(directory / "ribbed original patch.bp"), 2, True))
    image = None
    original = {}
    for name, model, step, negative in cases:
        result = run(exe, directory / name, model, step, negative)
        original[name] = result
        successor = result["successor"]
        if image is not None and image != result["engine_sha256"]:
            raise ValueError("Development cases used different application images")
        image = result["engine_sha256"]
        if (successor["status"] != "staged" or successor["segments_after"] <= successor["segments_before"]
                or successor["requests"] <= 0 or successor["direct_leaf_edits"] <= 0
                or result["mixed_adaptive_epochs"] != 0
                or "progressive_admission" in result
                or (negative and result.get("foreign_tree_control") != "rejected_before_feedback")):
            raise ValueError(f"Missing portable native feedback evidence for {name}: {successor}")
        verify_birth_trace(directory / name / "successor.steps/feedback",
                           "apmesh.quad.article_front_guarded.v1")
        print(name, result["source_sha256"], successor, flush=True)

    quiet = run(exe, directory / "relative-no-action", cases[1][1], cases[1][2],
                relative_tolerance=1, progressive_profile=progressive_profile)
    if (quiet["successor"]["status"] != "no_action" or quiet["face_requests"]
            or quiet["curve_requests"] or quiet["mixed_adaptive_epochs"] != 0
            or (directory / "relative-no-action/successor.steps").exists()
            or quiet["source_sha256"] != result["source_sha256"]
            or quiet["progressive_admission"]["status"] != "no_action"):
        raise ValueError("Relative threshold control did not retain only the original source")
    print("relative-no-action", quiet["source_sha256"], quiet["successor"], flush=True)

    pairs_dir = directory / "selective-additional-pairs"
    paired = run(exe, pairs_dir, cases[0][1], cases[0][2],
                 relative_tolerance=.034341894205194436, additional_pairs=True)
    if paired["successor"]["status"] != "staged" or paired["mixed_adaptive_epochs"] != 0:
        raise ValueError("The alternate local-pair contract did not stage")
    trace = verify_birth_trace(pairs_dir / "successor.steps/feedback",
                               "apmesh.quad.article_front_guarded_pairs.v1")
    if not any(step.get("additional_pair") for step in trace["commits"]):
        raise ValueError("The alternate local-pair contract did not exercise its fallback")
    print("selective-additional-pairs", paired["source_sha256"], paired["successor"], flush=True)

    limit = .045
    for name, model, step, _ in cases:
        screened = directory / f"screened-{name}"
        result = run(exe, screened, model, step, additional_pairs=True,
                     additional_pair_error_limit=limit, progressive_profile=progressive_profile,
                     relative_tolerance=.034341894205194436 if name == "curva" else None)
        if (result["successor"]["status"] != "staged" or result["mixed_adaptive_epochs"] != 0
                or result["engine_sha256"] != image):
            raise ValueError(f"Screened pair comparison did not stage for {name}")
        assessment = result["progressive_admission"]
        if (assessment["status"] != "eligible" or assessment["mixed_adaptive_epochs"] != 0
                or assessment["predecessor_sha256"] != result["source_sha256"]["source.obj"]
                or assessment["candidate_sha256"] != result["successor"]["candidate_sha256"]
                or assessment["boundary_certificate_sha256"] != result["boundary_refinement_sha256"]):
            raise ValueError(f"Missing opt-in progressive assessment for {name}")
        reference = paired if name == "curva" else original[name]
        for key in ("source_sha256", "face_requests", "curve_requests"):
            if result[key] != reference[key]:
                raise ValueError(f"The screened pair comparison changed {name} {key}")
        certificate = json.loads((screened / "successor.steps/feedback/boundary_refinement.json")
                                 .read_text(encoding="ascii"))
        if (certificate["schema"] != "apmesh.quad.boundary_refinement.v1"
                or certificate["parent_sites"] != result["successor"]["segments_before"]
                or certificate["candidate_sites"] != result["successor"]["segments_after"]
                or [row["parent_interval"] for row in certificate["splits"]]
                != sorted(row["interval"] for row in result["curve_requests"])):
            raise ValueError(f"Native refinement certificate does not match {name} requests")
        evaluate = golden
        if name == "ribbed":
            points, patches = parse_bp(Path(model).read_text(encoding="ascii"))
            evaluate = partial(bernstein, [points[i] for i in patches[0]])
        accepted, blocked = verify_screened_pairs(screened / "successor.steps/feedback", evaluate, limit)
        if not accepted or (name == "ribbed" and not blocked):
            raise ValueError(f"Screened pair controls were not exercised on {name}")
        print(f"screened-{name}", "passing operations", accepted, "blocked pairs", blocked, flush=True)


if __name__ == "__main__":
    main()
