"""Run the existing size-feedback pilot on one native Bezier patch."""

import argparse
import json
from math import isfinite
import os
from pathlib import Path
import shutil
import subprocess

from quad_adjacent_group_selector import geometric_size_requests
from quad_geometric_feedback_trial import observations
from quad_grouping_trial import digest, write_json
from quad_transition_comparison import bernstein, golden, parse_bp

PROFILE = Path(__file__).resolve().parents[1] / "configs/quad/curved_patch_article_front.conf"
PLAN = "APMESH_QUAD_FEEDBACK_PLAN"
SOURCE_FILES = ("tri.obj", "source.obj", "source_tree.txt")


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


def write_plan(path, step, faces=(), curves=(), reference=None):
    with path.open("x", encoding="ascii", newline="\n") as file:
        file.write(f"apmesh_single_patch_feedback_v1 {step}\n")
        if reference is not None:
            file.write(f'reference "{reference.name}"\n')
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


def run(exe, out, model, step, verify_rejection=False, *, relative_tolerance=None):
    if step < 1:
        raise ValueError("Select a positive accepted TRI source step")
    if relative_tolerance is not None and (not isfinite(relative_tolerance) or relative_tolerance < 0):
        raise ValueError("Relative residual tolerance must be finite and nonnegative")
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
    faces, curves = geometric_size_requests(source, evaluate, relative_tolerance=relative_tolerance)
    result = dict(model=native_model, model_fingerprint=model_fingerprint,
                  engine_sha256=digest(exe), step=step, source_sha256=hashes,
                  relative_residual_tolerance=relative_tolerance, face_requests=faces,
                  curve_requests=curves, mixed_adaptive_epochs=0)
    if not faces and not curves:
        if relative_tolerance is None or verify_rejection:
            raise ValueError("The requested comparison needs active feedback")
        result["successor"] = dict(status="no_action", reason="no_relative_residual_exceeds_tolerance")
        write_json(out / "result.json", result)
        return result
    request = out / "successor.plan"
    write_plan(request, step, faces, curves, archive)
    code, log = run_native(exe, out, native_model, "successor", request)
    if code != 0:
        raise ValueError(f"Native successor invocation failed with exit {code}. See {log.name}")
    successor = out / "successor.steps"
    if source_hashes(successor) != hashes or source_hashes(archive) != hashes:
        raise ValueError("Native source replay changed the original TRI, mixed mesh or tree")
    result["successor"] = observations(successor / "feedback", source, len(curves), evaluate)
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
        write_plan(forged_plan, step, faces, curves, forged)
        code, log = run_native(exe, out, native_model, "foreign", forged_plan)
        reason = b"Single-patch feedback did not reproduce its original source binding"
        if (code == 0 or reason not in log.read_bytes() or (out / "foreign.steps").exists()
                or (out / "foreign.steps.pending/feedback").exists()
                or source_hashes(archive) != hashes or source_hashes(successor) != hashes):
            raise ValueError("The foreign-tree control did not reject before the candidate")
        result["foreign_tree_control"] = "rejected_before_feedback"
        write_json(out / "result.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--model", required=True, help="Built-in CurvaBezier or one indexed Bezier .bp patch")
    parser.add_argument("--step", type=int, required=True, help="Accepted step of the original TRI generator")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--verify-rejection", action="store_true")
    parser.add_argument("--relative-tolerance", type=float,
                        help="Experimental dimensionless trigger with no default tolerance")
    args = parser.parse_args()
    try:
        result = run(args.exe.resolve(strict=True), args.out.resolve(), args.model, args.step,
                     args.verify_rejection, relative_tolerance=args.relative_tolerance)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Single-patch feedback failed: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
