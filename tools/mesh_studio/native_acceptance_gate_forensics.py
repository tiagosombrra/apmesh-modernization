"""R2.7.23 genuine C++ acceptance-predicate audit, not an LOD admission.

The C++ gate vector is emitted before branch entry and must never substitute
for an independently observed *post-commit* native lineage sidecar.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from .verify_native_lineage import require, SOURCE_MODELS, sha256_file

SCHEMA = "apmesh.meshstudio.r2723.original_precommit_gate.v1"
REPORT_SCHEMA = "apmesh.meshstudio.r2723.original_native_acceptance_gate_audit.v1"
MARKER = b"R2723_NATIVE_ACCEPTANCE_GATE="
MAX_LINE = 4096
MAX_EVENTS = 96

BOOL_FIELDS = (
    "stable_mode", "score_ok", "small_mesh_progress_override",
    "predicted_branch_accept_not_committed", "stable_mid_explore_accept",
    "stable_late_explore_accept", "transition_coherence_ok", "local_progress_ok",
    "consistency_ok", "stable_transition_ready", "quality_gate_ok",
    "hybrid_shape_gate_ok", "error_within_tolerance", "small_step_drop_ok",
    "efficiency_ok", "target_growth_ok", "step2_quality_stable",
    "stable_step2_error_ok", "step2_overshoot_ok",
    "stable_progressive_overshoot_ok", "step1_override",
    "budget_driven_step1_ok",
)
NUMBER_FIELDS = (
    "error_improvement_fraction", "previous_error", "candidate_error",
    "element_growth_factor", "acceptance_score", "error_drop_abs",
    "error_drop_per_element", "candidate_quality_min",
    "candidate_quality_good_ratio_ge_0_60", "candidate_quality_poor_ratio",
    "transition_coherence_penalty", "underresolved_transition_fraction",
    "transition_imbalance_max", "local_progress_coverage",
    "patch_budget_dispersion",
)
TRACKED_FLAGS = (
    "transition_coherence_ok", "local_progress_ok", "consistency_ok",
    "stable_transition_ready", "quality_gate_ok", "hybrid_shape_gate_ok",
    "error_within_tolerance", "small_step_drop_ok", "efficiency_ok",
    "target_growth_ok", "step2_quality_stable", "stable_step2_error_ok",
    "step2_overshoot_ok", "stable_progressive_overshoot_ok",
)
FLAG_SET = set(BOOL_FIELDS) | set(NUMBER_FIELDS) | {
    "schema","step","retry","acceptance_mode","scientific_lod_admitted",
}


def no_duplicates(pairs):
    obj={}
    for key,value in pairs:
        require(key not in obj, "r2723_duplicate_original_gate_json_field")
        obj[key]=value
    return obj


def parse_original_gate_stderr(data: bytes) -> list[dict]:
    """Only parse exact original C++ marker lines from source-pinned stderr."""
    require(0 < len(data) < 3_000_000,
            "r2723_missing_or_oversized_original_generator_stderr")
    markers=[line.split(MARKER,1)[1]
             for line in data.splitlines() if line.startswith(MARKER)]
    require(1 <= len(markers) <= MAX_EVENTS,
            "r2723_missing_or_oversized_precommit_gate_events")
    rows=[]
    seen=set()
    for raw in markers:
        require(0 < len(raw) <= MAX_LINE,
                "r2723_original_gate_line_unbounded")
        try:
            row=json.loads(raw.decode("utf-8"),
                           object_pairs_hook=no_duplicates,
                           parse_constant=lambda bad: (_ for _ in ()).throw(
                               ValueError("nonfinite gate " + bad)))
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValueError("r2723_invalid_cpp_gate_json") from exc
        require(type(row) is dict and set(row)==FLAG_SET and
                row.get("schema")==SCHEMA and
                row.get("scientific_lod_admitted") is False and
                type(row.get("step")) is int and 1 <= row["step"] <= 16 and
                type(row.get("retry")) is int and 0 <= row["retry"] <= 12 and
                type(row.get("acceptance_mode")) is int and
                row["acceptance_mode"] in (0,1) and
                all(type(row[k]) is bool for k in BOOL_FIELDS) and
                all(type(row[k]) in (float,int) and math.isfinite(row[k])
                    for k in NUMBER_FIELDS),
                "r2723_original_acceptance_gate_schema_or_nonfinite")
        key=(row["step"],row["retry"])
        require(key not in seen,"r2723_duplicate_original_local_gate_attempt")
        seen.add(key)
        require(row["predicted_branch_accept_not_committed"] is
                (row["score_ok"] or row["small_mesh_progress_override"]),
                "r2723_original_cpp_acceptance_branch_changed")
        if row["acceptance_mode"] == 0:
            mode0=(
                (row["error_improvement_fraction"] >= 0 or
                 row["stable_mid_explore_accept"] or
                 row["stable_late_explore_accept"]) and
                all(row[k] for k in (
                    "transition_coherence_ok", "local_progress_ok",
                    "consistency_ok","stable_transition_ready",
                    "quality_gate_ok"))
            )
            require(row["score_ok"] is bool(mode0),
                    "r2723_original_cpp_stable_score_gate_changed")
        elif row["score_ok"] and not (
            row["step1_override"] or row["budget_driven_step1_ok"]):
            require(all(row[k] for k in (
                "error_within_tolerance","small_step_drop_ok",
                "efficiency_ok","target_growth_ok","local_progress_ok",
                "step2_quality_stable","consistency_ok",
                "stable_step2_error_ok","step2_overshoot_ok",
                "stable_progressive_overshoot_ok",
                "transition_coherence_ok","quality_gate_ok")),
                "r2723_original_hybrid_score_conjunction_changed")
        rows.append(row)
    require([r["step"] for r in rows]==sorted(r["step"] for r in rows),
            "r2723_original_gate_steps_not_monotonic")
    return rows


def audit_original_gate_model(
    model:str,stderr:bytes,source_report:dict,
) -> dict:
    require(model in SOURCE_MODELS and
            source_report.get("original_model")==model and
            source_report.get("native_stderr_sha256")==
            hashlib.sha256(stderr).hexdigest() and
            source_report.get("r2718_original_stderr_sha256")==
            hashlib.sha256(stderr).hexdigest(),
            "r2723_original_cpp_stderr_sha_or_source_model_changed")
    rows=parse_original_gate_stderr(stderr)
    accepted={
        (x["accepted_step"],x["retry_index"]):x
        for x in source_report["accepted_snapshots"]
    }
    require(len(accepted)==source_report["native_accepted_commits"] and
            source_report.get("second_accepted_epoch_observed") is
            (len(accepted)>=2),
            "r2723_original_accepted_epoch_sidecar_inventory_invalid")
    true_decisions=[r for r in rows if r["predicted_branch_accept_not_committed"]]
    require(len(true_decisions)==len(accepted) and
            {(r["step"],r["retry"]) for r in true_decisions}==set(accepted),
            "r2723_original_precommit_decision_not_matched_to_real_commit")
    per_step={}
    for row in rows:
        per_step.setdefault(row["step"],[]).append(row)
    require(sum(not any(r["predicted_branch_accept_not_committed"]
                        for r in attempts)
                for attempts in per_step.values())==
            source_report["native_rejected_restored"],
            "r2723_original_failed_steps_not_equal_restored_outcomes")
    # Preserve every retry and reason; the source result has one accepted
    # epoch per article config, and rejected intermediate attempts are not LOD.
    attempts=[]
    for row in rows:
        accepted_receipt=accepted.get((row["step"],row["retry"]))
        failures=[flag for flag in TRACKED_FLAGS if row[flag] is False]
        attempts.append({
            "original_step":row["step"],
            "local_retry":row["retry"],
            "native_acceptance_mode":row["acceptance_mode"],
            "stable_mode":row["stable_mode"],
            "precommit_score_passed":row["score_ok"],
            "precommit_candidate_branch_taken":
                row["predicted_branch_accept_not_committed"],
            "native_postcommit_independently_observed":
                accepted_receipt is not None,
            "source_accepted_sidecar_sha256":
                accepted_receipt["source_file_sha256"]
                if accepted_receipt else None,
            "candidate_error":row["candidate_error"],
            "previous_accepted_error":row["previous_error"],
            "error_improvement_fraction":row["error_improvement_fraction"],
            "candidate_quality_min":row["candidate_quality_min"],
            "candidate_good_ratio":row["candidate_quality_good_ratio_ge_0_60"],
            "candidate_poor_ratio":row["candidate_quality_poor_ratio"],
            "element_growth_factor":row["element_growth_factor"],
            "transition_imbalance_max":row["transition_imbalance_max"],
            "transition_coherence_penalty":row["transition_coherence_penalty"],
            "failed_predicates_not_sufficient_explanation":failures,
            "all_original_native_predicates":
                {key:row[key] for key in BOOL_FIELDS},
            "scientific_lod_qualified":False,
        })
    accepted_steps=sorted(key[0] for key in accepted)
    return {
        "model":model,
        "real_model_input_sha256":source_report["real_model_input_sha256"],
        "original_article_config_sha256":
            source_report["native_config_source_sha256"],
        "actual_original_cpp_executable_sha256":
            source_report["research_executable_sha256"],
        "actual_original_process_stderr_sha256":
            hashlib.sha256(stderr).hexdigest(),
        "original_native_accepted_steps":accepted_steps,
        "original_accepted_count":len(accepted),
        "original_rejected_restored_steps":
            source_report["native_rejected_restored"],
        "original_gate_local_attempt_count":len(rows),
        "actual_original_precommit_attempts":attempts,
        "two_independently_accepted_source_epochs":len(accepted)>=2,
        "failed_predicates_are_descriptive_not_complete_causality":True,
        "raw_pointer_addresses_serialized":False,
        "scientific_lod_qualified":False,
    }


def audit_retained_original_gates(directory:Path)->dict:
    models={}
    for model in SOURCE_MODELS:
        report=json.loads((directory/f"r2712-{model}-native-lineage-audit.json")
                          .read_text(encoding="utf-8"))
        name=report["r2718_original_stderr_artifact_name"]
        require(name==f"r2718-{model}-original-native-generator-stderr.log",
                "r2723_unexpected_original_native_stderr_name")
        stderr=(directory/name).read_bytes()
        models[model]=audit_original_gate_model(model,stderr,report)
    return {
        "schema":REPORT_SCHEMA,
        "scope":"ORIGINAL_COMPILED_CPP_PRECOMMIT_GATE_VECTORS_POSTCOMMIT_MATCH",
        "original_models":models,
        "original_native_acceptance_policy_changed":False,
        "all_original_numerical_outputs_unchanged_requires_off_on_ci":True,
        "two_accepted_epochs_each_source_model":
            all(x["two_independently_accepted_source_epochs"]
                for x in models.values()),
        "cross_epoch_descendants_qualified":False,
        "continuous_error_bound_qualified":False,
        "scientific_lod_qualified":False,
    }


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    report=audit_retained_original_gates(args.directory)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write((json.dumps(report,indent=2,sort_keys=True,
                                 allow_nan=False)+"\n").encode("utf-8"))
    print("R2723_ACTUAL_NATIVE_GATE_FORENSICS="+json.dumps({
        model:{
            "accepted":r["original_accepted_count"],
            "restored":r["original_rejected_restored_steps"],
            "precommit_local_attempts":r["original_gate_local_attempt_count"],
            "first_accepted_steps":r["original_native_accepted_steps"],
            "second_original_accepted_epoch_observed":
                r["two_independently_accepted_source_epochs"],
        } for model,r in report["original_models"].items()},sort_keys=True))


if __name__=="__main__":
    main()
