#!/usr/bin/env python3
"""Audit native Adapter per-patch regeneration against original rejected TRI epochs.

The original domain CSV is a chronological record of local candidate attempts;
it does not automatically identify the selected final candidate or authorize
acceptance. This verifier preserves that distinction and the original source.
"""

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import re


ORIGINAL_PATCHES = {"eistute": 4, "book": 28}
REQUIRED_FIELDS = (
    "step", "retry", "patch_id", "local_regen_attempt",
    "generation_status", "generated_faces", "quality_post_aft_min",
    "poor_ratio_post_aft", "degenerate_post_aft_count",
    "degenerate_post_smoothing_count", "template_low_score_count",
    "template_score_min", "transition_floor", "transition_underresolved",
    "transition_element_ratio", "internal_element_ratio",
    "interior_transition_imbalance", "curve_domain_balance",
    "degeneracy_score",
)
SOURCE_ANCHORS = (
    '"degenerate_needs_retry"',
    '"curve_transition_needs_retry"',
    "bool PatchNeedsFallback(",
    "aft_stats.quality_post_aft_min < StablePatchQualityMin(policy_config)",
    "aft_stats.poor_ratio_post_aft > StablePatchPoorRatioMax(policy_config)",
    "IsTransitionUnderresolved(aft_stats, transition_floor)",
    "aft_stats.quadtree_low_score_count > 0",
)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric(row, name):
    require(name in row and row[name] is not None,
            f"Native domain Adapter record missing {name}")
    value = float(row[name])
    require(math.isfinite(value), f"Nonfinite native Adapter {name}")
    return value


def load_csv(path):
    require(path.is_file(), f"Missing original Adapter CSV: {path.name}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames is not None and
                set(REQUIRED_FIELDS).issubset(reader.fieldnames),
                "Original Adapter domain CSV lacks documented source fields")
        return list(reader)


def read_config_mode(root, model, profile_case):
    article = root / "configs" / model / "article.conf"
    text = article.read_text(encoding="utf-8")
    def original_setting(key):
        found = re.findall(rf"^{re.escape(key)}=([^\n]+)$",
                           text, flags=re.MULTILINE)
        require(len(found) == 1, f"Original model must define unique {key}")
        return found[0].strip()
    overrides = profile_case["overrides"]
    mode = overrides.get("ADAPTIVE_MODE", original_setting("ADAPTIVE_MODE"))
    intensity = float(overrides.get(
        "ADAPTIVE_INTENSITY", original_setting("ADAPTIVE_INTENSITY")))
    priority = float(overrides.get(
        "ADAPTIVE_QUALITY_PRIORITY",
        original_setting("ADAPTIVE_QUALITY_PRIORITY")))
    require(mode in ("adaptive_stable", "research_debug") and
            math.isfinite(intensity) and math.isfinite(priority) and
            0.0 <= intensity <= 1.0 and 0.0 <= priority <= 1.0,
            "Unrecognized original research policy parameters")
    return mode, intensity, priority


def clipped(number, minimum, maximum):
    return max(minimum, min(maximum, number))


def inspect_trial(row, priority, intensity):
    aft_quality = numeric(row, "quality_post_aft_min")
    poor = numeric(row, "poor_ratio_post_aft")
    low_templates = int(numeric(row, "template_low_score_count"))
    score_min = numeric(row, "template_score_min")
    internal = numeric(row, "internal_element_ratio")
    transition_ratio = numeric(row, "transition_element_ratio")
    floor = numeric(row, "transition_floor")
    count = int(numeric(row, "generated_faces"))
    quality_threshold = clipped(0.16 + 0.12 * priority, 0.16, 0.30)
    poor_threshold = clipped(0.45 - 0.25 * priority, 0.15, 0.45)
    template_threshold = 0.50 - 0.10 * intensity
    min_elements = max(8, math.floor(6.0 + 8.0 * priority + 0.5))
    measured = {
        "generated_faces_below_original_min":
            count < min_elements,
        "aft_min_quality_below_original_threshold":
            aft_quality < quality_threshold,
        "aft_poor_ratio_above_original_threshold":
            poor > poor_threshold,
        "quadtree_low_score_template_original_threshold":
            low_templates > 0 and score_min < template_threshold,
        "native_transition_underresolved":
            internal > 0.66 and transition_ratio + 1e-9 < floor,
        "post_aft_degenerate_faces_observed":
            numeric(row, "degenerate_post_aft_count") > 0,
        "post_smoothing_degenerate_faces_observed":
            numeric(row, "degenerate_post_smoothing_count") > 0,
    }
    require(int(numeric(row, "transition_underresolved")) in (0, 1),
            "Original transition indicator was not Boolean")
    # These booleans measure selected original fallback predicates. The
    # patch-area/target-h and curve-balance predicates need additional inputs.
    return measured


def inspect_model(directory, root, model, spec, source_cases):
    original_profiles = {case["profile"]: case for case in source_cases}
    profile_reports = []
    for case in spec:
        profile = case["profile"]
        require(profile in original_profiles,
                "Original Adapter profile not tied to genuine generator request")
        mode, intensity, priority = read_config_mode(
            root, model, original_profiles[profile])
        root_path = directory / f"{model}_{profile}"
        original_prefix = f"{model}_{profile}"
        path = root_path / (original_prefix + "_domain_adaptation.csv")
        rows = load_csv(path)
        require(len(rows) > 0, "Original Adapter produced no local source attempts")
        for item in rows:
            require(int(numeric(item, "step")) >= 0 and
                    0 <= int(numeric(item, "patch_id")) <
                    ORIGINAL_PATCHES[model] and
                    int(numeric(item, "local_regen_attempt")) >= 0 and
                    int(numeric(item, "retry")) >= 0,
                    "Invalid native Adapter source attempt identity")
        summaries = []
        for rejected in case["rejected_original_candidates"]:
            step = rejected["step"]
            patch_path = root_path / (
                f"{original_prefix}_passo_{step}_patch_adaptation_rejected.csv")
            patches = load_csv_header_only(patch_path)
            require(len(patches) == ORIGINAL_PATCHES[model],
                    "Native selected patch CSV lost original model patches")
            recorded = [r for r in rows if int(r["step"]) == step]
            require(recorded, "Rejected TRI step was never observed by original Adapter")
            by_patch = {}
            for patch in patches:
                patch_id = int(patch["patch_id"])
                selected_status = patch["generation_status_structural"]
                candidates = [r for r in recorded
                              if int(r["patch_id"]) == patch_id]
                require(candidates,
                        "Original rejected patch has no local native source attempt")
                matching = [r for r in candidates
                            if r["generation_status"] == selected_status]
                require(matching, "Rejected patch's chosen structural status was never generated by native Adapter")
                evidence = [
                    inspect_trial(r, priority, intensity) for r in matching
                ]
                indicators = sorted({
                    field for row in evidence
                    for field, active in row.items() if active
                })
                by_patch[patch_id] = {
                    "chosen_generation_status": selected_status,
                    "observed_local_attempts": len(candidates),
                    "matching_original_status_attempts": len(matching),
                    "distinct_original_retry_indices":
                        sorted(set(int(r["retry"]) for r in candidates)),
                    "distinct_local_regen_attempt_indices":
                        sorted(set(int(r["local_regen_attempt"])
                                   for r in candidates)),
                    "observable_fallback_predicates_in_matching_status_trials":
                        indicators,
                    "matching_trials_with_post_smoothing_degenerate_faces":
                        sum(row["post_smoothing_degenerate_faces_observed"]
                            for row in evidence),
                    "unobservable_patch_area_target_h_or_curve_balance_predicate":
                        True,
                }
            selected_statuses = Counter(
                item["chosen_generation_status"] for item in by_patch.values())
            original_observed_statuses = Counter(
                item["generation_status"] for item in recorded)
            summaries.append({
                "step": step,
                "candidate_committed": False,
                "selected_original_patch_statuses":
                    dict(sorted(selected_statuses.items())),
                "all_original_adapter_local_attempt_statuses":
                    dict(sorted(original_observed_statuses.items())),
                "original_source_local_attempt_count": len(recorded),
                "patch_count": len(by_patch),
                "patch_results": {
                    str(k): v for k, v in sorted(by_patch.items())
                },
            })
        profile_reports.append({
            "profile": profile,
            "original_policy_mode": mode,
            "original_policy_intensity": intensity,
            "original_policy_quality_priority": priority,
            "original_native_domain_source_csv_sha256": sha(path),
            "original_adapter_local_trial_count": len(rows),
            "rejected_steps": summaries,
        })
    return profile_reports


def load_csv_header_only(path):
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def run(directory, root, adapter_source):
    raw = adapter_source.read_text(encoding="utf-8")
    require(all(marker in raw for marker in SOURCE_ANCHORS),
            "Original Adapter fallback predicates changed; audit source first")
    report14_path = directory / "r2c14_generator_rejection_forensics.json"
    report13_path = directory / "r2c13_accepted_generator_epochs.json"
    original = json.loads(report14_path.read_text(encoding="utf-8"))
    parent = json.loads(report13_path.read_text(encoding="utf-8"))
    require(original["schema"] ==
            "apmesh.quad.r2c14.original_generator_rejection_forensics.v1"
            and original["parent_r2c13_report_sha256"] == sha(report13_path)
            and parent["all_models_two_accepted_epochs"] is False,
            "Cannot join unqualified original source generator reports")
    result = {
        "schema": "apmesh.quad.r2c17.original_adapter_source_local_fallback.v1",
        "original_adapter_cpp_sha256": sha(adapter_source),
        "source_r2c14_report_sha256": sha(report14_path),
        "source_r2c13_report_sha256": sha(report13_path),
        "original_TRI_acceptance_unchanged": True,
        "complete_original_generator_two_accepted_epochs": False,
        "global_physical_QUAD_AFT_mesh_approved": False,
        "models": {
            model: inspect_model(
                directory, root, model, cases,
                parent["models"][model]["cases"])
            for model, cases in original["models"].items()
        },
    }
    for model, expected in ORIGINAL_PATCHES.items():
        pinned = next(
            item for item in result["models"][model]
            if item["profile"] == "pinned_article")
        require(pinned["rejected_steps"] and all(
            step["patch_count"] == expected
            for step in pinned["rejected_steps"]),
            "Original model pinned Adapter per-patch fallback forensics incomplete")
    result_path = directory / "r2c17_original_adapter_fallback_forensics.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print("R2C17_NATIVE_ADAPTER_DOMAIN_FALLBACK",
          json.dumps({
              model: [{
                  "profile": row["profile"],
                  "rejected": [{
                      "step": step["step"],
                      "statuses": step["selected_original_patch_statuses"],
                      "local_attempts": step["original_source_local_attempt_count"],
                  } for step in row["rejected_steps"]]
              } for row in data]
              for model, data in result["models"].items()
          }, sort_keys=True),
          "scientific_acceptance_unchanged=1",
          "global_physical_welding=0")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--adapter-source", type=Path, required=True)
    args = parser.parse_args()
    run(args.directory.resolve(), args.root.resolve(),
        args.adapter_source.resolve())


if __name__ == "__main__":
    main()
