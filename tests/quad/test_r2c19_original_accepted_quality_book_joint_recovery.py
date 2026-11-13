#!/usr/bin/env python3
"""Audit genuine accepted TRI face quality and bounded Book AFT recovery.

Original GeneratorAdaptive and TRI admission thresholds are unchanged.
Eistute's actual postprocess success is rechecked for every accepted
source step; Book's two-control tests are labeled non-univariate.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from test_r2c13_m7_accepted_epochs import MODELS, require, scenario
from test_r2c18_original_aft_postprocess_profiles import native_local_attempts


BOOK_JOINT_CASES = (
    ("aft_passes4_quality_0p80", {
        "AFT_LOCAL_POSTPROCESS_PASSES": "4",
        "AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD": "0.80",
    }),
    ("aft_passes8_quality_0p80", {
        "AFT_LOCAL_POSTPROCESS_PASSES": "8",
        "AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD": "0.80",
    }),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_kv(path):
    require(path.is_file(), f"Missing actual accepted TRI source {path.name}")
    result = {}
    for row in path.read_text(encoding="utf-8").splitlines():
        if "=" not in row:
            continue
        key, value = row.split("=", 1)
        require(key not in result, "Native original acceptance log duplicated a field")
        result[key] = value
    return result


def number(value, description):
    v = float(value)
    require(math.isfinite(v), f"Non-finite TRI {description}")
    return v


def validate_original_accepted_step_quality(directory, model, profile, steps):
    prefix = directory / f"{model}_{profile}" / f"{model}_{profile}"
    snapshots = []
    for step in steps:
        path = Path(f"{prefix}_passo_{step}_acceptance_accepted.log")
        fields = read_kv(path)
        require(fields.get("step") == str(step) and
                fields.get("accepted") == "1" and
                fields.get("error_global_definition") ==
                "surface_curvature_3d_relative",
                "Original committed TRI log has invalid accepted/error provenance")
        source_3d = number(fields["quality_min_3d"], "accepted min 3D quality")
        source_uv = number(fields["quality_min_uv"], "accepted min UV quality")
        source_global = number(fields["quality_min"], "accepted min global quality")
        # Positive minimum quality is necessary, not a complete independent
        # per-face zero-volume or 1993 surface-accuracy certification.
        require(source_3d > 0.0 and source_uv > 0.0 and source_global > 0.0,
                "A committed original source TRI epoch reports degenerate quality")
        patch_path = Path(f"{prefix}_passo_{step}_patch_adaptation_accepted.csv")
        require(patch_path.is_file(), "Missing native accepted TRI patch evidence")
        with patch_path.open(newline="", encoding="utf-8") as f:
            patches = list(csv.DictReader(f))
        require(len(patches) == MODELS[model]["patches"] and
                sorted(int(p["patch_id"]) for p in patches) ==
                list(range(MODELS[model]["patches"])),
                "Original accepted patch coverage is not complete")
        min_patch_3d = min(
            number(p["quality_min_3d"], "accepted patch min 3D quality")
            for p in patches)
        min_patch_uv = min(
            number(p["quality_min_uv"], "accepted patch min UV quality")
            for p in patches)
        require(min_patch_3d > 0.0 and min_patch_uv > 0.0,
                "An accepted original TRI patch reports nonpositive 3D/UV quality")
        snapshots.append({
            "original_accepted_step": step,
            "source_min_quality_3d": source_3d,
            "source_min_quality_uv": source_uv,
            "source_min_quality_global": source_global,
            "minimum_accepted_patch_quality_3d": min_patch_3d,
            "minimum_accepted_patch_quality_uv": min_patch_uv,
            "accepted_global_error_improvement_fraction": number(
                fields["error_improvement"], "accepted global error improvement"),
            "accepted_original_growth_factor": number(
                fields["element_growth_factor"], "original accepted growth"),
            "accepted_original_TRI_source_log_sha256": digest(path),
            "accepted_original_TRI_patch_log_sha256": digest(patch_path),
            "independent_full_face_area_scan_completed": False,
        })
    return snapshots


def run(exe, root, directory, prior):
    r18_path = prior / "r2c18_original_aft_postprocess_profiles.json"
    r18 = json.loads(r18_path.read_text(encoding="utf-8"))
    require(r18["schema"] ==
            "apmesh.quad.r2c18.original_tri_aft_postprocess_sensitivity.v1"
            and r18["models"]["eistute"][
                "has_two_accepted_original_generator_epochs"] is True
            and r18["both_models_have_two_original_accepted_epochs"] is False,
            "Missing the actually verified R2c18 native Eistute/Book baseline")
    eistute = next(
        c for c in r18["models"]["eistute"]["scenarios"]
        if c["profile"] == "aft_postprocess_quality_0p80")
    require(eistute["status"] == "qualified_two_accepted_epochs" and
            eistute["accepted_step_ids"] == [1, 2, 4] and
            eistute["accepted_outer_epoch_ids"] == [1, 2, 5] and
            len(eistute["per_accepted_step_receipts"]) == 3,
            "Eistute R2c18 real accepted source epoch identity drifted")
    accepted = validate_original_accepted_step_quality(
        prior, "eistute", eistute["profile"], eistute["accepted_step_ids"])

    directory.mkdir(parents=True, exist_ok=True)
    book_cases = []
    for profile, overrides in BOOK_JOINT_CASES:
        require(len(overrides) == 2,
                "Two-knob Book postprocess recovery lost source transparency")
        case = scenario(exe, root, directory,
                        "book", MODELS["book"], profile, overrides)
        case["sensitivity_design"] = "joint_two_knob_noncausal"
        case["native_adapter_local_attempts"] = native_local_attempts(
            directory, "book", profile)
        if case["accepted_committed_steps"] if "accepted_committed_steps" in case else False:
            case["actual_accepted_TRI_quality"] = (
                validate_original_accepted_step_quality(
                    directory, "book", profile, case["accepted_step_ids"]))
        book_cases.append(case)

    report = {
        "schema": "apmesh.quad.r2c19.original_accepted_tri_quality_and_book_joint_recovery.v1",
        "previous_r2c18_report_sha256": digest(r18_path),
        "original_eistute_sha256": MODELS["eistute"]["sha256"],
        "original_book_sha256": MODELS["book"]["sha256"],
        "eistute_r2c18_three_true_source_commits": True,
        "eistute_quality_audit": {
            "accepted_step_ids": eistute["accepted_step_ids"],
            "accepted_outer_epoch_ids": eistute["accepted_outer_epoch_ids"],
            "accepted_TRI_quality": accepted,
            "global_error_monotonically_decreased_in_all_commits":
                all(x["accepted_global_error_improvement_fraction"] > 0.0
                    for x in accepted),
            "full_independent_3d_face_area_scan_completed": False,
        },
        "book_joint_recovery": {
            "scenarios": book_cases,
            "any_two_original_accepted_source_epochs": any(
                c["accepted_two_original_generator_epochs"]
                for c in book_cases),
            "two_knob_profiles_do_not_prove_one_knob_causality": True,
        },
        "original_generator_and_adapter_source_modified": False,
        "original_TRI_admission_thresholds_modified": False,
        "scientific_1993_rule_approved": False,
        "global_nonmanifold_QUAD_AFT_weld_approved": False,
    }
    target = directory / "r2c19_original_accepted_tri_quality_book_joint_recovery.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("R2C19_ACCEPTED_TRI_FACE_QUALITY_AND_BOOK_JOINT_RECOVERY",
          json.dumps({
              "eistute_accepted_steps": [x["original_accepted_step"]
                                         for x in accepted],
              "eistute_all_accepted_positive_3d_uv_quality": True,
              "eistute_accepted_global_error_monotone":
                  report["eistute_quality_audit"][
                      "global_error_monotonically_decreased_in_all_commits"],
              "book": [{
                  "profile": c["profile"],
                  "status": c["status"],
                  "accepted": c.get("accepted_committed_steps", 0),
                  "two_accepted": c["accepted_two_original_generator_epochs"]
              } for c in book_cases],
          }, sort_keys=True),
          "TRI_acceptance_unchanged=1",
          "global_QUAD_AFT_welding_approved=0")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--r2c18-directory", type=Path, required=True)
    a = parser.parse_args()
    run(a.exe.resolve(), a.root.resolve(), a.directory.resolve(),
        a.r2c18_directory.resolve())


if __name__ == "__main__":
    main()
