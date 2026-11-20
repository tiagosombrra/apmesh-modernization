"""R2.7.29: read-only audit of two DIFFERENT original C++ transition metrics.

The AFT stage-1 ratio counts nonboundary elongated triangles. The Adapter
regional count includes near-boundary OR elongated faces on later geometry.
Neither is a new committed native TRI epoch or a welded surface transition.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import statistics

from .native_controlled_sensitivity import git_blob
from .native_patch_csv_replay import (
    audit as audit_r2728, attest_original_sources,
)
from .verify_native_lineage import require

SCHEMA = "apmesh.meshstudio.r2729.original_aft_adapter_transition_classifiers.v1"
SOURCE_PINS = {
    "docs/mesh-studio/R2_7_29_PREREGISTERED_ORIGINAL_AFT_TRANSITION_SEMANTICS_20261119.md":
        "7b0da51d3e17578b7b3fc808e554d58e8d241679",
    "src/crab_mesh/aft/advancing_front.cpp":
        "1bd430d1bd1079e6f55f3bc7488ff9313e4bb82b",
    "src/adapter/adapter.cpp":
        "78f821411f33a8ca7594c8e357bbe4a79e5d33f9",
    "src/generator/generator_adaptive.cpp":
        "844673ea764f3092330e5e9ebb01d8eb339869bc",
}
REQUIRED = {
    "step", "retry", "patch_id", "local_regen_attempt",
    "generated_faces", "boundary_elements", "transition_elements",
    "interior_elements", "boundary_element_ratio",
    "transition_element_ratio", "internal_element_ratio",
    "transition_floor", "transition_underresolved", "generation_status",
}
MAX_RAW_CSV = 2_000_000
RATIO_ROUNDING_TOLERANCE = 5.0e-6


def source_attestation(root: Path) -> dict:
    """Require byte-identical original algorithms and preregistered semantics."""
    receipts = attest_original_sources(root)
    for path, expected in SOURCE_PINS.items():
        raw = (root / path).read_bytes()
        require(git_blob(raw) == expected,
                "r2729_original_cpp_semantics_or_prior_registration_drifted")
        receipts[path] = {
            "git_blob": expected, "sha256": hashlib.sha256(raw).hexdigest(),
        }
    aft = (root / "src/crab_mesh/aft/advancing_front.cpp").read_text(
        encoding="utf-8")
    adapter = (root / "src/adapter/adapter.cpp").read_text(
        encoding="utf-8")
    require(all(s in aft for s in (
        "if (boundary_edges > 0U) {",
        "hmax / hmin > 1.8",
        "stats.transition_ratio = static_cast<double>(transition_faces) / total;",
        "} else if (stage == 1) {",
        "run_stats.transition_element_ratio = stats.transition_ratio;",
        "run_stats.internal_element_ratio = stats.internal_ratio;",
    )) and all(s in adapter for s in (
        "const bool transition_band_face = boundary_distance <= transition_band_width || aspect > 1.8;",
        "std::max(0.08, std::min(0.32, (target_patch_h > 0.0) ? target_patch_h * 1.75 : 0.14))",
        "result.regional_stats = ComputeRegionalPatchStats(new_mesh, local_target_h);",
        "result.aft_stats = avanco.GetRunStats();",
        "const bool interior_dominant = aft_stats.internal_element_ratio > 0.66;",
        "aft_stats.transition_element_ratio + 1.0e-9 < transition_floor",
    )), "r2729_original_two_classifier_implementations_not_attested")
    return receipts


def inspect_csv(raw: bytes) -> dict:
    """Independently reopen raw numeric columns; never trust derived JSON only."""
    require(0 < len(raw) <= MAX_RAW_CSV and
            raw.endswith(b"\n") and b"\x00" not in raw and b"\r" not in raw,
            "r2729_missing_or_noncanonical_raw_original_cpp_csv")
    try:
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
        header = reader.fieldnames
        require(header is not None and len(header) == len(set(header)) and
                REQUIRED.issubset(header) and len(header) <= 96,
                "r2729_original_adapter_csv_header_drifted")
        rows = list(reader)
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError("r2729_original_cpp_csv_invalid_encoding") from exc
    require(1 <= len(rows) <= 256,
            "r2729_original_cpp_csv_rows_missing_or_unbounded")
    records = []
    for row in rows:
        require(None not in row and all(
            isinstance(v, str) and v for v in row.values()),
            "r2729_original_cpp_csv_truncated_or_extra_cells")
        try:
            step = int(row["step"])
            retry = int(row["retry"])
            patch = int(row["patch_id"])
            local_attempt = int(row["local_regen_attempt"])
            generated = int(row["generated_faces"])
            counts = {k: int(row[k]) for k in
                      ("boundary_elements", "transition_elements", "interior_elements")}
            ratios = {k: float(row[k]) for k in
                      ("boundary_element_ratio", "transition_element_ratio",
                       "internal_element_ratio")}
            floor = float(row["transition_floor"])
            flagged = int(row["transition_underresolved"])
        except (TypeError, ValueError) as exc:
            raise ValueError("r2729_original_cpp_csv_invalid_numeric_column") from exc
        require(1 <= step <= 4 and 0 <= retry <= 2 and
                0 <= patch < 4 and 0 <= local_attempt <= 3 and
                generated > 0 and all(v >= 0 for v in counts.values()) and
                sum(counts.values()) == generated,
                "r2729_regional_post_smoothing_face_partition_inconsistent")
        require(all(math.isfinite(v) and 0 <= v <= 1 for v in ratios.values())
                and abs(sum(ratios.values()) - 1.0) <=
                RATIO_ROUNDING_TOLERANCE and
                math.isfinite(floor) and 0.08 <= floor <= 0.24
                and flagged in (0, 1),
                "r2729_original_aft_shape_ratio_partition_invalid")
        shape_transition = ratios["transition_element_ratio"]
        internal = ratios["internal_element_ratio"]
        # The original Adapter predicate uses STAGE-1 AFT shape statistics.
        # The independent spatial-or-shape region count is NOT substituted.
        ambiguous = (
            abs(internal - 0.66) <= RATIO_ROUNDING_TOLERANCE or
            abs(shape_transition - floor) <= RATIO_ROUNDING_TOLERANCE)
        if not ambiguous:
            require(flagged == int(internal > 0.66 and
                                   shape_transition + 1e-9 < floor),
                    "r2729_source_underresolved_flag_uses_wrong_classifier")
        regional = counts["transition_elements"] / generated
        records.append({
            "step": step, "retry": retry, "patch_slot": patch,
            "local_attempt": local_attempt,
            "aft_stage1_shape_elongation_fraction": shape_transition,
            "aft_stage1_internal_fraction": internal,
            "aft_stage1_boundary_fraction":
                ratios["boundary_element_ratio"],
            "regional_spatial_or_shape_transition_fraction": regional,
            "regional_transition_faces": counts["transition_elements"],
            "regional_generated_faces": generated,
            "regional_minus_stage1_aft_transition_fraction":
                regional - shape_transition,
            # Descriptive only: this is NOT a proposal to replace the gate.
            "regional_spatial_or_shape_fraction_reaches_original_floor":
                regional >= floor,
            "aft_shape_fraction_reaches_original_floor":
                shape_transition >= floor,
            "transition_floor_original": floor,
            "original_cpp_underresolved": bool(flagged),
            "original_csv_generation_status": row["generation_status"],
            "flag_math_ambiguous_at_original_csv_precision": ambiguous,
        })
    return {
        "raw_source_adapter_csv_sha256": hashlib.sha256(raw).hexdigest(),
        "records": records,
        "original_source_ostream_rounding_respected": True,
        "two_classifier_semantics_not_interchangeable": True,
    }


def _describe(records: list[dict]) -> dict:
    """Report actual source observations, not inferential independent samples."""
    require(records, "r2729_missing_cpp_local_records")
    aft = [r["aft_stage1_shape_elongation_fraction"] for r in records]
    regional = [
        r["regional_spatial_or_shape_transition_fraction"] for r in records]
    differences = [
        r["regional_minus_stage1_aft_transition_fraction"] for r in records]
    return {
        "rows": len(records),
        "aft_shape_transition_mean": statistics.fmean(aft),
        "regional_spatial_or_shape_transition_mean": statistics.fmean(regional),
        "mean_fraction_difference": statistics.fmean(differences),
        "min_fraction_difference": min(differences),
        "max_fraction_difference": max(differences),
        "count_regional_fraction_above_aft_shape_ratio":
            sum(x > 0 for x in differences),
        "underresolved_local_candidate_rows":
            sum(r["original_cpp_underresolved"] for r in records),
        "local_rows_with_regional_fraction_above_original_aft_floor":
            sum(r["regional_spatial_or_shape_fraction_reaches_original_floor"]
                for r in records),
        "local_rows_with_aft_shape_fraction_above_its_own_floor":
            sum(r["aft_shape_fraction_reaches_original_floor"]
                for r in records),
        "original_flagged_even_when_distinct_regional_fraction_above_floor":
            sum(r["original_cpp_underresolved"] and
                r["regional_spatial_or_shape_fraction_reaches_original_floor"]
                for r in records),
        "uncertain_strict_predicate_from_rounded_cpp_ostream":
            sum(r["flag_math_ambiguous_at_original_csv_precision"]
                for r in records),
    }


def analyze_pair(source_raw: bytes, variant_raw: bytes) -> dict:
    """Independent per-process source/variant summary; never pool as epochs."""
    data = {}
    for role, raw, expected_rows in (
        ("original", source_raw, 104),
        ("variant", variant_raw, 112),
    ):
        parsed = inspect_csv(raw)
        allrows = parsed["records"]
        require(len(allrows) == expected_rows,
                "r2729_authentic_r2728_original_cpp_local_count_changed")
        step_sets = {str(i): [r for r in allrows if r["step"] == i]
                     for i in range(1, 5)}
        step4 = step_sets["4"]
        require(len(step4) == 64 and
                all(r["original_cpp_underresolved"] and
                    r["original_csv_generation_status"] ==
                    "curve_transition_needs_retry" for r in step4) and
                all(r["regional_minus_stage1_aft_transition_fraction"] > 0
                    for r in step4),
                "r2729_real_original_cpp_step4_semantics_not_reproduced")
        step4_by_patch = {}
        for patch in range(4):
            group = [r for r in step4 if r["patch_slot"] == patch]
            require(len(group) == 16,
                    "r2729_original_eistute_patch_slots_not_exhaustive")
            step4_by_patch[str(patch)] = _describe(group)
        report = {
            "original_native_cpp_csv_sha256":
                parsed["raw_source_adapter_csv_sha256"],
            "source_native_cpp_local_csv_rows": len(allrows),
            "step_profiles": {
                key: _describe(rows) for key, rows in step_sets.items()},
            "step4_per_patch_slot": step4_by_patch,
            "step4_unresolved_local_candidate_count":
                sum(r["original_cpp_underresolved"] for r in step4),
            "step4_original_adapter_local_statuses":
                sorted({r["original_csv_generation_status"]
                        for r in step4}),
            "transition_ratio_used_by_gate":
                "aft_stage1_nonboundary_edge_aspect_gt_1_8_per_total_faces",
            "region_ratio_not_the_original_eligibility_gate":
                "post_generation_boundary_distance_or_edge_aspect",
            "recorded_local_candidates_are_not_selected_fallbacks": True,
            "genuine_same_process_source_accepted_steps": [1],
            "scientific_lod_qualified": False,
        }
        data[role] = report
    for role, expected_aft, expected_regional in (
        ("original", 0.040383, 0.295003),
        ("variant", 0.056619, 0.345028),
    ):
        group = data[role]["step_profiles"]["4"]
        require(abs(group["aft_shape_transition_mean"] - expected_aft) <
                0.00001 and
                abs(group["regional_spatial_or_shape_transition_mean"] -
                    expected_regional) < 0.00001,
                "r2729_preregistered_native_source_classifier_numbers_changed")
    return data


def audit(root: Path, executable: Path, original: Path,
          old_trials: Path, r2728_directory: Path,
          r2728_report: Path) -> dict:
    """Independently rerun old source verifier and new source semantic audit."""
    root = root.resolve()
    sources = source_attestation(root)
    previous = audit_r2728(
        root, executable, original, old_trials, r2728_directory)
    old_result = json.loads(r2728_report.read_text(encoding="utf-8"))
    require(old_result == previous,
            "r2729_existing_r2728_cpp_source_audit_not_reproduced")
    files = {
        role: (r2728_directory / role /
               "original-adapter-domain-adaptation.csv").read_bytes()
        for role in ("original", "variant")
    }
    results = analyze_pair(files["original"], files["variant"])
    for role, item in results.items():
        expected = previous["observations"][role]
        require(item["original_native_cpp_csv_sha256"] ==
                expected["native_adapter_csv_sha256"] and
                item["source_native_cpp_local_csv_rows"] ==
                expected["local_patch_attempts"] and
                expected["real_native_accepted_steps"] == [1] and
                expected["real_native_restored_steps"] == 3,
                "r2729_new_classifier_not_bound_to_original_cpp_source")
    return {
        "schema": SCHEMA,
        "original_cpp_source_attestation": sources,
        "real_r2728_original_and_variant_cpp_audit_recomputed": True,
        "original_article_and_min13_separate_unmodified_cpp_processes": True,
        "original_cpp_acceptance_policy_changed": False,
        "original_aft_transition_ratio_is_elongation_not_spatial_band": True,
        "original_adapter_regional_count_has_spatial_or_elongation": True,
        "adapter_shape_gate_and_regional_counts_are_distinct": True,
        "classification": "READ_ONLY_ORIGINAL_CPP_METRIC_SEMANTICS",
        "source_model": "eistute",
        "per_cpp_process": results,
        "source_accepted_epoch_in_each_independent_process": [1],
        "local_observation_is_not_an_accepted_epoch": True,
        "real_second_accepted_step_in_same_cpp_process": False,
        "continuous_source_surface_error_bound_proven": False,
        "physical_patch_welding_proven": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--original-directory", type=Path, required=True)
    parser.add_argument("--r2726-trials", type=Path, required=True)
    parser.add_argument("--r2728-directory", type=Path, required=True)
    parser.add_argument("--r2728-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.root, args.exe, args.original_directory,
                   args.r2726_trials, args.r2728_directory,
                   args.r2728_report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as out:
        out.write((json.dumps(result, sort_keys=True, indent=2,
                              allow_nan=False) + "\n").encode("utf-8"))
    print("R2729_REAL_ORIGINAL_CPP_CLASSIFIERS=" + json.dumps({
        role: {
            "native_local_rows": rec["source_native_cpp_local_csv_rows"],
            "stage1_aft_shape_transition":
                rec["step_profiles"]["4"]["aft_shape_transition_mean"],
            "regional_spatial_or_shape_transition":
                rec["step_profiles"]["4"][
                    "regional_spatial_or_shape_transition_mean"],
            "genuine_native_accepted_steps":
                rec["genuine_same_process_source_accepted_steps"],
            "scientific_lod_qualified": False,
        } for role, rec in result["per_cpp_process"].items()
    }, sort_keys=True))


if __name__ == "__main__":
    main()
