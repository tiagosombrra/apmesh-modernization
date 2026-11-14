#!/usr/bin/env python3
"""Exercise original-model AFT postprocess controls without changing TRI admission.

Each profile changes exactly one existing runtime AFT control. The native
GeneratorAdaptive retains the original quality thresholds and rollback logic.
"""

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path

from test_r2c13_m7_accepted_epochs import MODELS, require, scenario


PROFILES = {
    "eistute": (
        ("aft_postprocess_blend_0p78", {
            "AFT_LOCAL_POSTPROCESS_BLEND": "0.78",
        }),
        ("aft_postprocess_quality_0p80", {
            "AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD": "0.80",
        }),
    ),
    "book": (
        ("aft_postprocess_passes_4", {
            "AFT_LOCAL_POSTPROCESS_PASSES": "4",
        }),
        ("aft_postprocess_passes_8", {
            "AFT_LOCAL_POSTPROCESS_PASSES": "8",
        }),
    ),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_local_attempts(directory, model, name):
    path = directory / f"{model}_{name}" / (
        f"{model}_{name}_domain_adaptation.csv"
    )
    if not path.is_file():
        return {"file_present": False, "local_source_attempts": 0}
    with path.open(newline="", encoding="utf-8") as handle:
        data = list(csv.DictReader(handle))
    if not data:
        return {"file_present": True, "local_source_attempts": 0,
                "domain_csv_sha256": digest(path)}
    for key in (
        "step", "patch_id", "generation_status", "local_regen_attempt",
        "quality_post_aft_min", "transition_underresolved",
        "degenerate_post_aft_count", "degenerate_post_smoothing_count",
        "curve_domain_balance", "template_low_score_count",
    ):
        require(key in data[0], f"Original Adapter log lost {key}")
    by_step = {}
    for item in data:
        step = int(item["step"])
        patch = int(item["patch_id"])
        require(0 <= patch < MODELS[model]["patches"],
                "Original Adapter reported a foreign model patch")
        entry = by_step.setdefault(step, [])
        entry.append(item)

    source_metrics = []
    for step, rows in sorted(by_step.items()):
        quality = [float(r["quality_post_aft_min"]) for r in rows]
        balance = [float(r["curve_domain_balance"]) for r in rows]
        require(all(math.isfinite(q) for q in quality + balance),
                "Non-finite native original quality/balance metric")
        source_metrics.append({
            "step": step,
            "local_attempts": len(rows),
            "status_attempts": dict(sorted(Counter(
                r["generation_status"] for r in rows).items())),
            "min_post_aft_quality_in_attempts": min(quality),
            "max_post_aft_quality_in_attempts": max(quality),
            "native_underresolved_transition_attempts": sum(
                int(r["transition_underresolved"]) for r in rows),
            "native_post_aft_degenerate_face_observations": sum(
                int(r["degenerate_post_aft_count"]) for r in rows),
            "native_post_smoothing_degenerate_face_observations": sum(
                int(r["degenerate_post_smoothing_count"]) for r in rows),
            "local_regeneration_retry_attempts": sum(
                int(r["local_regen_attempt"]) > 0 for r in rows),
            "minimum_curve_interior_balance": min(balance),
        })
    return {
        "file_present": True,
        "domain_csv_sha256": digest(path),
        "local_source_attempts": len(data),
        "observed_per_step": source_metrics,
        "local_candidates_are_not_accepted_generator_epochs": True,
    }


def execute(exe, root, directory):
    result = {
        "schema": "apmesh.quad.r2c18.original_tri_aft_postprocess_sensitivity.v1",
        "source_change_scope": "one_existing_AFT_postprocess_control_per_case",
        "scientific_TRI_acceptance_thresholds_changed": False,
        "original_GeneratorAdaptive_source_changed": False,
        "input_original_models_sha256_verified": True,
        "global_nonmanifold_QUAD_accepted": False,
        "models": {},
    }
    for model, original in MODELS.items():
        cases = []
        for name, overrides in PROFILES[model]:
            require(len(overrides) == 1,
                    "An AFT postprocess sensitivity has multiple knobs")
            diagnosis = scenario(exe, root, directory, model, original,
                                 name, overrides)
            diagnosis["native_adapter_local_attempts"] = (
                native_local_attempts(directory, model, name))
            diagnosis["research_profile"] = True
            diagnosis["scientific_TRI_acceptance_thresholds_changed"] = False
            cases.append(diagnosis)
        result["models"][model] = {
            "scenarios": cases,
            "has_two_accepted_original_generator_epochs": any(
                c["accepted_two_original_generator_epochs"] for c in cases),
        }
    result["both_models_have_two_original_accepted_epochs"] = all(
        x["has_two_accepted_original_generator_epochs"]
        for x in result["models"].values())
    outfile = directory / "r2c18_original_aft_postprocess_profiles.json"
    outfile.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8")
    print("R2C18_ORIGINAL_AFT_POSTPROCESS_PROFILES",
          json.dumps({
              model: [{
                  "profile": case["profile"],
                  "native_status": case["status"],
                  "accepted": case.get("accepted_committed_steps", 0),
                  "restored": case.get("rejected_restored_steps", 0),
                  "two_accepted": case["accepted_two_original_generator_epochs"],
                  "native_local_attempts": case[
                      "native_adapter_local_attempts"]["local_source_attempts"],
              } for case in content["scenarios"]]
              for model, content in result["models"].items()
          }, sort_keys=True),
          "both_original_models_two_accepted_epochs=" +
          str(int(result["both_models_have_two_original_accepted_epochs"])),
          "original_TRI_admission_thresholds_changed=0")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    args.directory.resolve().mkdir(parents=True, exist_ok=True)
    execute(args.exe.resolve(), args.root.resolve(),
            args.directory.resolve())


if __name__ == "__main__":
    main()
