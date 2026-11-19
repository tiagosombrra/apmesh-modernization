"""Read-only R2.7.31 source-bound decomposition of selected original AFT gates.

This script never runs or modifies a generator. Original and min13 are
separate scientific processes, never two accepted epochs in one process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

from .native_controlled_sensitivity import git_blob
from .native_local_selection_provenance import (
    SCHEMA as PRIOR_SCHEMA,
    attest_original_selection_source,
    join_selected_local_to_native_csv,
)
from .verify_native_lineage import require

SCHEMA = "apmesh.meshstudio.r2731.selected_original_aft_gate_decomposition.v1"
PREREG = "docs/mesh-studio/R2_7_31_PREREGISTERED_SELECTED_GATE_DECOMPOSITION_20261119.md"
PREREG_GIT_BLOB = "e222a8f17c21451f84ae96a027c6753430415715"
ROLES = ("original", "variant")
MAX_REPORT = 3_000_000
MAX_OBSERVATION = 3_000_000
MAX_STDOUT = 3_000_000
MAX_CSV = 2_000_000
MAX_SIDECAR = 30_000_000


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read(path: Path, limit: int) -> bytes:
    """Load only explicitly bounded source-native research evidence."""
    require(path.is_file() and 0 < path.stat().st_size <= limit,
            "r2731_missing_or_oversized_genuine_source_evidence")
    return path.read_bytes()


def _metric(values: list[float]) -> dict:
    require(bool(values) and all(math.isfinite(v) for v in values),
            "r2731_missing_or_nonfinite_selected_local_metric")
    return {
        "minimum": min(values),
        "arithmetic_mean": statistics.fmean(values),
        "maximum": max(values),
        "observations": len(values),
    }


def summarize_selected_step4(selected: list[dict]) -> dict:
    """Describe actually selected local returns; no inferential statistics."""
    require(len(selected) == 40 and
            [row.get("adapter_return_index") for row in selected] ==
            list(range(40)),
            "r2731_original_cpp_adapter_return_chronology_drifted")
    step4 = [row for row in selected if row.get("step") == 4]
    require(len(step4) == 16,
            "r2731_selected_original_step4_return_count_changed")
    result = []
    for row in step4:
        t = row["aft_stage1_transition_ratio"]
        f = row["original_transition_floor"]
        i = row["internal_element_ratio"]
        r = row["regional_spatial_or_shape_ratio"]
        require(all(isinstance(v, (int, float)) and
                    not isinstance(v, bool) and math.isfinite(v)
                    for v in (t, f, i, r)) and
                0 <= t <= 1 and 0.08 <= f <= 0.24 and
                0 <= i <= 1 and 0 <= r <= 1,
                "r2731_original_cpp_local_selected_ratio_invalid")
        require(row["patch"] in range(4) and
                row["retry"] in (0, 1) and
                row["original_selected_local_attempt"] in range(4) and
                row["local_status"] == "curve_transition_needs_retry" and
                row["transition_underresolved"] is True and
                i > 0.66 and t + 1e-9 < f and
                row["local_selected_is_not_global_accepted_tri"] is True,
                "r2731_source_selected_original_underresolution_invariant_failed")
        result.append({
            "adapter_return_index": row["adapter_return_index"],
            "outer_epoch": row["outer_epoch"],
            "retry": row["retry"],
            "patch": row["patch"],
            "selected_local_attempt": row["original_selected_local_attempt"],
            "aft_shape_elongated_nonboundary_fraction": t,
            "original_aft_shape_transition_floor": f,
            "aft_shape_floor_shortfall": f - t,
            "aft_internal_fraction": i,
            "interior_dominance_margin_over_0_66": i - 0.66,
            "independent_regional_spatial_or_shape_fraction": r,
            "regional_minus_aft_shape_fraction": r - t,
            "regional_minus_original_aft_floor": r - f,
            "regional_fraction_at_least_original_floor_descriptive_only": r >= f,
        })
    require([row["patch"] for row in result].count(0) == 4 and
            [row["patch"] for row in result].count(1) == 4 and
            [row["patch"] for row in result].count(2) == 4 and
            [row["patch"] for row in result].count(3) == 4,
            "r2731_selected_original_all_patches_not_exhaustive")
    metrics = (
        "aft_shape_elongated_nonboundary_fraction",
        "original_aft_shape_transition_floor",
        "aft_shape_floor_shortfall",
        "aft_internal_fraction",
        "interior_dominance_margin_over_0_66",
        "independent_regional_spatial_or_shape_fraction",
        "regional_minus_aft_shape_fraction",
        "regional_minus_original_aft_floor",
    )
    def describe(rows: list[dict]) -> dict:
        return {name: _metric([row[name] for row in rows])
                for name in metrics}
    return {
        "selected_original_cpp_local_returns_all_steps": 40,
        "selected_original_cpp_local_returns_step4": 16,
        "selected_source_cpp_step4_underresolved": 16,
        "all_four_source_patch_slots_observed": True,
        "selected_local_metrics": describe(result),
        "source_patch_slots": {
            str(p): {
                "selected_return_count": 4,
                "original_source_local_metrics": describe(
                    [row for row in result if row["patch"] == p]),
                "selected_adapter_return_indices": [
                    row["adapter_return_index"] for row in result
                    if row["patch"] == p],
            } for p in range(4)
        },
        "source_selected_step4_returns": result,
        "regional_at_or_above_original_floor_descriptive_count": sum(
            row["regional_fraction_at_least_original_floor_descriptive_only"]
            for row in result),
        "separately_defined_regional_fraction_not_substituted_for_aft": True,
        "original_aft_underresolution_predicate_used": (
            "internal_element_ratio>0.66 && "
            "aft_transition_element_ratio+1e-9<transition_floor"),
        "local_return_does_not_imply_global_commit": True,
        "not_independent_statistical_samples": True,
        "scientific_lod_qualified": False,
    }


def audit(root: Path, original_selected_dir: Path, prior_report: Path) -> dict:
    """Reopen native bytes and reproduce the prior observer join independently."""
    root = root.resolve()
    attest_original_selection_source(root)
    prereg = _read(root / PREREG, 30_000)
    require(git_blob(prereg) == PREREG_GIT_BLOB,
            "r2731_preregistered_source_document_changed")
    prior_bytes = _read(prior_report, MAX_REPORT)
    prior = json.loads(prior_bytes)
    require(prior.get("schema") == PRIOR_SCHEMA and
            prior.get("global_original_cpp_acceptance_policy_unchanged") is True
            and prior.get("second_same_run_accepted_tri_epoch") is False and
            prior.get("scientific_lod_qualified") is False and
            set(prior["two_processes"]) == set(ROLES),
            "r2731_prior_independently_audited_cpp_evidence_invalid")
    profiles = {}
    for role in ROLES:
        folder = original_selected_dir / role
        stdout = _read(folder / "original-selection-stdout.log", MAX_STDOUT)
        csv = _read(folder / "original-adapter-domain-adaptation.csv", MAX_CSV)
        faces = _read(folder / "accepted_step_1_retry_0.ndjson", MAX_SIDECAR)
        observation_raw = _read(folder / "observation-report.json", MAX_OBSERVATION)
        observation = json.loads(observation_raw)
        previous = prior["two_processes"][role]
        current = join_selected_local_to_native_csv(stdout, csv, role)
        require(observation.get("schema") == PRIOR_SCHEMA and
                observation.get("role") == role and
                observation.get("stdout_sha256") == _sha(stdout) and
                observation.get("source_adapter_csv_sha256") == _sha(csv) and
                observation.get("genuine_source_accepted_face_sha256") ==
                _sha(faces) and
                observation.get("true_original_cpp_accepted_step") == [1] and
                observation.get("original_cpp_restored_steps") == 3 and
                observation.get("scientific_lod_qualified") is False and
                observation.get("selected_observer_result") == current,
                "r2731_original_cpp_source_local_observation_not_reproduced")
        require(previous["native_source_cpp_selected_csv_sha256"] == _sha(csv) and
                previous["genuine_original_cpp_postcommit_sha256"] ==
                _sha(faces) and
                previous["actual_original_cpp_accepted_steps"] == [1] and
                previous["real_global_rejected_restored_steps"] == 3 and
                previous["not_two_same_cpp_process_accepted_epochs"] is True and
                previous["selected_source_native_adapter_returns"] == 40 and
                previous["selected_step4_source_native_adapter_returns"] == 16,
                "r2731_source_original_native_acceptance_evidence_drifted")
        selected = [r for r in current["selected_local_returns"]
                    if r["step"] == 4]
        require([r["original_selected_local_attempt"] for r in selected] ==
                previous["selected_step4_local_attempt_indices"] and
                all(selected == [
                    p for group in range(4)
                    for p in previous["selected_step4_by_patch"][str(group)]
                    if p["step"] == 4
                ] for _ in (0,)),
                "r2731_selected_adapter_returns_differ_from_prior_cpp_audit")
        profiles[role] = {
            "original_cpp_selection_stdout_sha256": _sha(stdout),
            "original_cpp_adapter_csv_sha256": _sha(csv),
            "accepted_original_cpp_tri_face_sha256": _sha(faces),
            "native_cpp_observation_report_sha256": _sha(observation_raw),
            "genuine_original_cpp_accepted_steps": [1],
            "genuine_original_cpp_restored_steps": 3,
            "selected_original_gate_decomposition":
                summarize_selected_step4(current["selected_local_returns"]),
        }
    return {
        "schema": SCHEMA,
        "registered_protocol_git_blob": PREREG_GIT_BLOB,
        "prior_independently_audited_r2730_json_sha256": _sha(prior_bytes),
        "original_cpp_local_selection_source_attested": True,
        "raw_original_cpp_observer_and_csv_reparsed": True,
        "original_and_single_factor_variant_are_distinct_cpp_processes": True,
        "roles": profiles,
        "selected_source_candidates_not_global_acceptance_epochs": True,
        "scientific_spatial_transition_quality_not_proven": True,
        "cross_epoch_original_face_ancestry_not_proven": True,
        "physical_gpu_present_rss_vram_not_measured": True,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--selected-directory", type=Path, required=True)
    parser.add_argument("--prior-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(),
            "r2731_output_receipt_must_be_new_and_immutable")
    result = audit(args.root, args.selected_directory, args.prior_report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8")
    print("R2731_ORIGINAL_SELECTED_AFT_GATE_DECOMPOSITION=" +
          json.dumps({
              role: {
                  "selected_step4": result["roles"][role][
                      "selected_original_gate_decomposition"][
                          "selected_original_cpp_local_returns_step4"],
                  "mean_shape_floor_shortfall":
                      result["roles"][role]["selected_original_gate_decomposition"][
                          "selected_local_metrics"]["aft_shape_floor_shortfall"][
                              "arithmetic_mean"],
                  "real_accepted_epochs": [1],
                  "lod_qualified": False,
              } for role in ROLES
          }, sort_keys=True))


if __name__ == "__main__":
    main()
