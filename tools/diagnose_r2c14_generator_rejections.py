#!/usr/bin/env python3
"""Explain original GeneratorAdaptive rejected candidates from actual runtime logs.

This is a read-only failure-forensics report. It neither changes the original
TRI acceptance criteria nor promotes rejected candidate epochs to commits.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re


EXPECTED = {
    "eistute": {"patches": 4, "curves": 13},
    "book": {"patches": 28, "curves": 85},
}
REQUIRED = (
    "step", "accepted", "acceptance_score", "error_improvement",
    "element_growth_factor", "quality_min", "quality_mean", "poor_ratio",
    "budget_exceeded", "budget_final_status", "overshoot_ratio",
    "transition_coherence_penalty", "underresolved_transition_fraction_real",
    "transition_imbalance_max_real", "local_progress_coverage",
    "actual_elements_step", "target_elements_step",
)


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def finite_number(value, description):
    try:
        number = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid numeric {description}") from exc
    require(math.isfinite(number), f"Nonfinite {description}")
    return number


def key_file(path):
    raw = path.read_bytes()
    lines = raw.decode("utf-8").splitlines()
    data = {}
    for line in lines:
        if "=" not in line:
            continue
        name, value = line.split("=", 1)
        require(name not in data, f"Duplicated original acceptance attribute: {name}")
        data[name] = value
    return data, sha(raw)


def csv_rows(path, expected_rows):
    require(path.is_file(), f"Missing original source runtime CSV {path.name}")
    raw = path.read_bytes()
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    require(len(rows) == expected_rows,
            f"Original candidate source CSV cardinality changed: {path.name}")
    return rows, sha(raw)


def accepted_ancestor(prefix, accepted_steps, before_step, patch_count):
    older = [step for step in accepted_steps if step < before_step]
    if not older:
        return None
    step = max(older)
    path = prefix.parent / f"{prefix.name}_passo_{step}_patch_adaptation_accepted.csv"
    rows, digest = csv_rows(path, patch_count)
    return step, {int(r["patch_id"]): finite_number(
        r["last_submesh_error"], "accepted local patch error") for r in rows}, digest


def rejected_profile(directory, model, spec, case):
    profile = case["profile"]
    folder = directory / f"{model}_{profile}"
    prefix = folder / f"{model}_{profile}"
    stdout_path = folder / "generator_stdout.log"
    require(stdout_path.is_file(), "Missing original candidate GeneratorAdaptive native log")
    raw_stdout = stdout_path.read_bytes()
    stops = [line.strip() for line in
             raw_stdout.decode("utf-8", errors="replace").splitlines()
             if line.startswith("Motivo da parada:")]
    rejected_logs = list(folder.glob(f"{prefix.name}_passo_*_acceptance_rejected.log"))
    seen_steps = set()
    examples = []
    for path in rejected_logs:
        parsed = re.fullmatch(
            re.escape(prefix.name) + r"_passo_(\d+)_acceptance_rejected\.log",
            path.name)
        require(parsed is not None, "Unexpected original rejected acceptance log path")
        step = int(parsed.group(1))
        require(step >= 1 and step not in seen_steps,
                "Duplicated original rejected adaptive step")
        seen_steps.add(step)
        attributes, attribute_sha = key_file(path)
        require(all(key in attributes for key in REQUIRED) and
                attributes["step"] == str(step) and attributes["accepted"] == "0",
                "Rejected original candidate was not explicitly marked rejected")
        rejected_patch_path = folder / (
            f"{prefix.name}_passo_{step}_patch_adaptation_rejected.csv")
        rejected_curve_path = folder / (
            f"{prefix.name}_passo_{step}_curve_adaptation_rejected.csv")
        patches, patch_sha = csv_rows(rejected_patch_path, spec["patches"])
        curves, curve_sha = csv_rows(rejected_curve_path, spec["curves"])
        patch_ids = sorted(int(item["patch_id"]) for item in patches)
        require(patch_ids == list(range(spec["patches"])),
                "The rejected original patch adaptation omitted a model patch")
        accepted_steps = case.get("accepted_step_ids", [])
        parent = accepted_ancestor(prefix, accepted_steps, step, spec["patches"])
        regressed = []
        if parent is not None:
            _, previously_accepted, _ = parent
            for patch in patches:
                index = int(patch["patch_id"])
                prior = previously_accepted[index]
                current = finite_number(
                    patch["last_submesh_error"], "rejected local patch error")
                if current > prior:
                    regressed.append({
                        "patch_id": index,
                        "accepted_patch_error": prior,
                        "rejected_patch_error": current,
                        "error_increase": current - prior,
                    })
        regressed.sort(key=lambda item: item["error_increase"], reverse=True)
        under_target = 0
        max_curve_growth = 0.0
        max_curve_target = 0
        for curve_index, row in enumerate(curves):
            actual = int(row["actual_curve_points"])
            target = int(row["target_curve_points"])
            growth = finite_number(row["curve_point_growth_factor"],
                                   "original curve growth factor")
            require(actual >= 2 and target >= 2,
                    f"Original source curve {curve_index} lost its subdivisions")
            under_target += int(actual < target)
            max_curve_growth = max(max_curve_growth, growth)
            max_curve_target = max(max_curve_target, target)

        score = finite_number(attributes["acceptance_score"], "acceptance score")
        improvement = finite_number(attributes["error_improvement"],
                                    "global error improvement")
        growth_factor = finite_number(attributes["element_growth_factor"],
                                      "element growth factor")
        candidate = {
            "step": step, "candidate_status": "REJECTED_NOT_COMMITTED",
            "error_improvement_fraction": improvement,
            "global_error_improved": improvement > 0.0,
            "global_error_increased": improvement < 0.0,
            "acceptance_score": score,
            "original_element_growth_factor": growth_factor,
            "accepted_ancestor_step": parent[0] if parent else None,
            "local_patches_worsened_vs_accepted_ancestor": len(regressed),
            "top_three_patch_error_increases": regressed[:3],
            "under_target_source_curves": under_target,
            "max_original_source_curve_growth_factor": max_curve_growth,
            "max_original_source_curve_target_points": max_curve_target,
            "quality_min": finite_number(attributes["quality_min"], "quality min"),
            "quality_mean": finite_number(attributes["quality_mean"], "quality mean"),
            "poor_ratio": finite_number(attributes["poor_ratio"], "poor ratio"),
            "transition_coherence_penalty": finite_number(
                attributes["transition_coherence_penalty"], "transition penalty"),
            "underresolved_transition_fraction": finite_number(
                attributes["underresolved_transition_fraction_real"],
                "underresolved transition fraction"),
            "transition_imbalance_max": finite_number(
                attributes["transition_imbalance_max_real"], "transition imbalance"),
            "local_progress_coverage": finite_number(
                attributes["local_progress_coverage"], "local progress"),
            "target_elements_step": finite_number(
                attributes["target_elements_step"], "target element count"),
            "actual_elements_step": finite_number(
                attributes["actual_elements_step"], "actual element count"),
            "overshoot_ratio": finite_number(
                attributes["overshoot_ratio"], "original overshoot ratio"),
            "budget_exceeded": int(attributes["budget_exceeded"]),
            "budget_final_status": attributes["budget_final_status"],
            "rejected_acceptance_log_sha256": attribute_sha,
            "rejected_patch_adaptation_sha256": patch_sha,
            "rejected_curve_adaptation_sha256": curve_sha,
            "precise_boolean_acceptance_subgate_proved": False,
        }
        examples.append(candidate)
    examples.sort(key=lambda c: c["step"])
    if case["status"] in ("qualified_two_accepted_epochs",
                          "observed_but_fewer_than_two_accepted_epochs"):
        require(len(examples) == case["rejected_restored_steps"],
                "Rejected candidate log count differs from real restored TRI steps")
        require(set(x["step"] for x in examples).isdisjoint(
            set(case["accepted_step_ids"])),
            "One original step was both committed and rejected")
    return {
        "model": model, "profile": profile,
        "native_status": case["status"],
        "stopping_reasons": stops,
        "accepted_actual_steps": case.get("accepted_step_ids", []),
        "rejected_original_candidates": examples,
        "retained_original_stdout_sha256": sha(raw_stdout),
        "rejected_candidates_never_count_as_accepted": True,
        "no_change_to_production_admission": True,
        "notes": ("Acceptance logs expose computed metrics but not the complete "
                  "per-boolean gate decisions. These numbers support diagnosis, "
                  "not permission to override scientific quality constraints."),
    }


def run(directory):
    source = directory / "r2c13_accepted_generator_epochs.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    require(data["schema"] ==
            "apmesh.quad.r2c13.actual_production_generator_epochs.v1"
            and data["global_quad_aft_model_approved"] is False,
            "Missing authenticated original M7 diagnostic")
    report = {
        "schema": "apmesh.quad.r2c14.original_generator_rejection_forensics.v1",
        "parent_r2c13_report_sha256": sha(source.read_bytes()),
        "source_type": "original_GeneratorAdaptive_runtime_debug",
        "models": {},
        "original_accepted_epoch_gate_unchanged": True,
        "no_physical_quad_welding_or_admission": True,
    }
    for model, spec in EXPECTED.items():
        cases = data["models"][model]["cases"]
        report["models"][model] = [
            rejected_profile(directory, model, spec, case)
            for case in cases
        ]
        require(any(x["profile"] == "pinned_article" and
                    len(x["rejected_original_candidates"]) > 0
                    for x in report["models"][model]),
                f"The original {model} pinned rejection evidence was not archived")
    target = directory / "r2c14_generator_rejection_forensics.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    summary = {
        model: [{
            "profile": case["profile"],
            "rejected_steps": [x["step"] for x in
                               case["rejected_original_candidates"]],
            "increased_global_error_steps": [
                x["step"] for x in case["rejected_original_candidates"]
                if x["global_error_increased"]],
            "improved_but_rejected_steps": [
                x["step"] for x in case["rejected_original_candidates"]
                if x["global_error_improved"]],
        } for case in cases]
        for model, cases in report["models"].items()
    }
    print("R2C14_ORIGINAL_GENERATOR_REJECTION_FORENSICS",
          json.dumps(summary, sort_keys=True),
          "production_acceptance_unchanged=1 exact_boolean_gate_unapproved=1")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, type=Path)
    args = parser.parse_args()
    run(args.directory.resolve())


if __name__ == "__main__":
    main()
