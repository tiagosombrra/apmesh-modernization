"""Run the existing size-feedback pilot on one native Bezier patch."""

import argparse
import json
from math import isfinite
import os
from pathlib import Path
import shutil
import subprocess

from quad_adjacent_group_selector import geometric_size_requests, transition_size_requests
from quad_geometric_feedback_trial import observations
from quad_grouping_trial import digest, write_json
from quad_progressive_admission import SOURCE_FILES, assess_trial, load_profile
from quad_transition_comparison import bernstein, golden, parse_bp

PROFILE = Path(__file__).resolve().parents[1] / "configs/quad/curved_patch_article_front.conf"
PLAN = "APMESH_QUAD_FEEDBACK_PLAN"


def model_evaluator(model, directory):
    if model == "builtin:curva_bezier":
        return model, golden
    source = Path(model).resolve(strict=True)
    raw = source.read_bytes()
    vertices, patches = parse_bp(raw.decode("utf-8"))
    if len(patches) != 1:
        raise ValueError("Single-patch feedback requires one indexed Bezier patch")
    (directory / "source.bp").write_bytes(raw)
    controls = [vertices[i] for i in patches[0]]
    return "source.bp", lambda u, v: bernstein(controls, u, v)


def write_plan(path, step, faces=(), curves=(), reference=None, *, additional_pairs=False,
               additional_pair_error_limit=None, certify_boundary_refinement=False):
    with path.open("x", encoding="ascii", newline="\n") as file:
        file.write(f"apmesh_single_patch_feedback_v1 {step}\n")
        if reference is not None:
            file.write(f'reference "{reference.name}"\n')
        if certify_boundary_refinement:
            file.write("certify_boundary_refinement\n")
        if additional_pairs:
            file.write("additional_pairs\n")
        if additional_pair_error_limit is not None:
            file.write(f"additional_pair_error_limit {additional_pair_error_limit:.17g}\n")
        for row in curves:
            file.write(f"curve {row['interval']}\n")
        for row in faces:
            u, v = row["site"]
            file.write(f"face {row['face']} {u:.17g} {v:.17g} {row['h']:.17g}\n")


def run_native(exe, directory, model, arm, plan):
    overrides = {"INPUT_MODEL": model, "OUTPUT_PREFIX": arm}
    config = []
    for row in PROFILE.read_text(encoding="ascii").splitlines():
        name, _, _ = row.partition("=")
        config.append(f"{name}={overrides[name]}" if name in overrides else row)
    filename = directory / f"{arm}.conf"
    filename.write_text("\n".join(config) + "\n", encoding="ascii")
    environment = os.environ.copy()
    for name in ("APMESH_QUAD_GROUPING_PLAN", PLAN):
        environment.pop(name, None)
    environment[PLAN] = plan.name
    stderr_path = directory / f"{arm}.stderr"
    with (directory / f"{arm}.stdout").open("xb") as stdout, stderr_path.open("xb") as stderr:
        result = subprocess.run([str(exe), "--config", filename.name], cwd=directory,
                                env=environment, stdout=stdout, stderr=stderr, timeout=180)
    return result.returncode, stderr_path


def source_hashes(archive):
    return {name: digest(archive / name) for name in SOURCE_FILES}


def run(exe, out, model, step, verify_rejection=False, *, relative_tolerance=None,
        additional_pairs=False, additional_pair_error_limit=None, certify_boundary_refinement=False,
        progressive_profile=None, transition_size_feedback=False):
    if step < 1:
        raise ValueError("Select a positive accepted TRI source step")
    if relative_tolerance is not None and (not isfinite(relative_tolerance) or relative_tolerance < 0):
        raise ValueError("Relative residual tolerance must be finite and nonnegative")
    if additional_pair_error_limit is not None and (
            not additional_pairs or not isfinite(additional_pair_error_limit) or additional_pair_error_limit < 0):
        raise ValueError("A finite nonnegative additional-pair error limit requires --additional-pairs")
    admission_profile = load_profile(progressive_profile) if progressive_profile is not None else None
    certify_boundary_refinement = (certify_boundary_refinement or admission_profile is not None
                                   or transition_size_feedback)
    out.mkdir(parents=True)
    native_model, evaluate = model_evaluator(model, out)
    model_fingerprint = digest(out / native_model) if native_model == "source.bp" else native_model
    prep = out / "source.plan"
    write_plan(prep, step)
    code, log = run_native(exe, out, native_model, "source", prep)
    if code != 0:
        raise ValueError(f"Native source capture failed with exit {code}. See {log.name}")
    archive = out / "source.steps"
    hashes = source_hashes(archive)
    source = archive / "source.obj"
    if transition_size_feedback:
        faces, curves, transition = transition_size_requests(
            source, evaluate, relative_tolerance=relative_tolerance)
    else:
        faces, curves = geometric_size_requests(source, evaluate, relative_tolerance=relative_tolerance)
    result = dict(model=native_model, model_fingerprint=model_fingerprint,
                  engine_sha256=digest(exe), step=step, source_sha256=hashes,
                  relative_residual_tolerance=relative_tolerance, face_requests=faces,
                  curve_requests=curves, mixed_adaptive_epochs=0)
    if transition_size_feedback:
        result["transition_size_seed"] = transition

    def save_progressive_assessment():
        if admission_profile is not None:
            result["progressive_admission"] = assess_trial(out, result, admission_profile)
            write_json(out / "result.json", result)

    if additional_pairs:
        result["additional_pair_search"] = True
    if additional_pair_error_limit is not None:
        result["additional_pair_error_limit"] = additional_pair_error_limit
    if not faces and not curves:
        if relative_tolerance is None or verify_rejection:
            raise ValueError("The requested comparison needs active feedback")
        result["successor"] = dict(status="no_action", reason="no_relative_residual_exceeds_tolerance")
        write_json(out / "result.json", result)
        save_progressive_assessment()
        return result
    request = out / "successor.plan"
    write_plan(request, step, faces, curves, archive, additional_pairs=additional_pairs,
               additional_pair_error_limit=additional_pair_error_limit,
               certify_boundary_refinement=certify_boundary_refinement)
    code, log = run_native(exe, out, native_model, "successor", request)
    if code != 0:
        raise ValueError(f"Native successor invocation failed with exit {code}. See {log.name}")
    successor = out / "successor.steps"
    if source_hashes(successor) != hashes or source_hashes(archive) != hashes:
        raise ValueError("Native source replay changed the original TRI, mixed mesh or tree")
    result["successor"] = observations(successor / "feedback", source, len(curves), evaluate)
    if certify_boundary_refinement:
        certificate = successor / "feedback/boundary_refinement.json"
        result["boundary_refinement_sha256"] = digest(certificate)
    write_json(out / "result.json", result)
    if verify_rejection:
        forged = out / "forged_source"
        forged.mkdir()
        for name in SOURCE_FILES:
            shutil.copyfile(archive / name, forged / name)
        binding = forged / "source_tree.txt"
        with binding.open("ab") as file:
            file.write(b"corrupted provenance\n")
        forged_plan = out / "foreign.plan"
        write_plan(forged_plan, step, faces, curves, forged, additional_pairs=additional_pairs,
                   additional_pair_error_limit=additional_pair_error_limit,
                   certify_boundary_refinement=certify_boundary_refinement)
        code, log = run_native(exe, out, native_model, "foreign", forged_plan)
        reason = b"Single-patch feedback did not reproduce its original source binding"
        if (code == 0 or reason not in log.read_bytes() or (out / "foreign.steps").exists()
                or (out / "foreign.steps.pending/feedback").exists()
                or source_hashes(archive) != hashes or source_hashes(successor) != hashes):
            raise ValueError("The foreign-tree control did not reject before the candidate")
        result["foreign_tree_control"] = "rejected_before_feedback"
        write_json(out / "result.json", result)
    save_progressive_assessment()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--model", required=True, help="Built-in CurvaBezier or one indexed Bezier .bp patch")
    parser.add_argument("--step", type=int, required=True, help="Accepted step of the original TRI generator")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--verify-rejection", action="store_true")
    parser.add_argument("--additional-pairs", action="store_true",
                        help="Try remaining local pairs when the original choice is a TRI")
    parser.add_argument("--additional-pair-error-limit", type=float,
                        help="Maximum sampled XYZ deviation divided by the physical active edge length")
    parser.add_argument("--certify-boundary-refinement", action="store_true",
                        help="Verify ordered native curve splits against the bound predecessor")
    parser.add_argument("--relative-tolerance", type=float,
                        help="Experimental dimensionless trigger with no default tolerance")
    parser.add_argument("--transition-size-feedback", action="store_true",
                        help="Grade one supplemental contour size seed during active geometric feedback")
    parser.add_argument("--progressive-profile", type=Path,
                        help="Certify the native curve and assess the candidate with an explicit progressive profile")
    args = parser.parse_args()
    try:
        result = run(args.exe.resolve(strict=True), args.out.resolve(), args.model, args.step,
                     args.verify_rejection, relative_tolerance=args.relative_tolerance,
                     additional_pairs=args.additional_pairs,
                     additional_pair_error_limit=args.additional_pair_error_limit,
                     certify_boundary_refinement=args.certify_boundary_refinement,
                     progressive_profile=args.progressive_profile,
                     transition_size_feedback=args.transition_size_feedback)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Single-patch feedback failed: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
