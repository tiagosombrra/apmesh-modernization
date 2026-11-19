"""R2.7.27 read-only original C++ transition-coherence gate forensics.

This is a necessary-predicate proof from real source-native stderr, not an
intervention, geometric ancestry certification or a new accepted LOD epoch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from .native_acceptance_gate_forensics import parse_original_gate_stderr
from .native_active_generation_study import (
    TRIALS, attest_predeclared_source, audit as audit_previous,
)
from .native_controlled_sensitivity import git_blob
from .verify_native_lineage import require

SCHEMA = "apmesh.meshstudio.r2727.original_cpp_transition_coherence_forensics.v1"
CPP_SOURCE_BLOB = "844673ea764f3092330e5e9ebb01d8eb339869bc"
GATE_PARSER_BLOB = "f415a2f1410b1c41411aeebbc383d9497753cfd1"
PREREGISTRATION_BLOB = "38b226fb0f08b9f364f4b197298f04d737f1d25c"
PATCH_SEMANTICS_ADDENDUM_BLOB = "7115b00de89848aad1ebb5432e1625109192186f"
NUMERIC_EPS = 1e-12


def attest_cpp_acceptance_source(root: Path) -> dict:
    """Check the byte-exact original generator and original gate parser."""
    sources = {
        "src/generator/generator_adaptive.cpp": CPP_SOURCE_BLOB,
        "tools/mesh_studio/native_acceptance_gate_forensics.py":
            GATE_PARSER_BLOB,
        "docs/mesh-studio/R2_7_27_ORIGINAL_TRANSITION_COHERENCE_FORENSICS_PROTOCOL_20261118.md":
            PREREGISTRATION_BLOB,
        "docs/mesh-studio/R2_7_27A_ORIGINAL_PATCH_COUNT_SEMANTICS_ADDENDUM_20261118.md":
            PATCH_SEMANTICS_ADDENDUM_BLOB,
    }
    receipts = {}
    for name, blob in sources.items():
        raw = (root / name).read_bytes()
        require(git_blob(raw) == blob,
                "r2727_original_cpp_acceptance_or_gate_parser_bytes_changed")
        receipts[name] = {
            "git_blob": blob,
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    text = (root / "src/generator/generator_adaptive.cpp").read_text(
        encoding="utf-8")
    anchors = (
        "0.55 * underresolved_real",
        "0.30 * imbalance_mean_real",
        "0.25 * overshoot_excess",
        "0.10 * curve_aux_penalty",
        "? 1.0",
        "? 0.42 : 0.25",
        "current_underresolved_transition_fraction_real_ <=\n"
        "                     ((this->step_ >= 4) ? 0.25 : 0.10)",
        "current_transition_imbalance_max_real_ <= ((this->step_ >= 4) ? 0.18 : 0.12)",
        "current_transition_coherence_penalty_ <= transition_penalty_cap",
        "current_underresolved_transition_patch_count_real_ == 0U",
        "for (unsigned int i = 0; i < geometry->GetNumberPatches(); ++i)",
        "if (structural->transition_underresolved != 0)",
        "++current_underresolved_transition_patch_count_real_;",
        "static_cast<double>(current_underresolved_transition_patch_count_real_) /",
        "static_cast<double>(geometry->GetNumberPatches());",
    )
    require(all(x in text for x in anchors),
            "r2727_original_cpp_transition_gate_formula_not_attested")
    return receipts


def diagnose_gate(row: dict) -> dict:
    """Rederive only observable necessary gates; never relax the C++ policy."""
    require(
        type(row) is dict and type(row.get("step")) is int
        and type(row.get("retry")) is int
        and type(row.get("stable_mode")) is bool
        and type(row.get("transition_coherence_ok")) is bool
        and type(row.get("stable_transition_ready")) is bool
        and 1 <= row["step"] <= 16 and 0 <= row["retry"] <= 12,
        "r2727_invalid_source_gate_scope_or_flags")
    for key in (
        "transition_coherence_penalty",
        "underresolved_transition_fraction",
        "transition_imbalance_max",
    ):
        require(type(row.get(key)) in (int, float)
                and math.isfinite(row[key]),
                "r2727_nonfinite_source_transition_metric")
    penalty = float(row["transition_coherence_penalty"])
    fraction = float(row["underresolved_transition_fraction"])
    imbalance = float(row["transition_imbalance_max"])
    require(penalty >= 0 and 0 <= fraction <= 1 and imbalance >= 0,
            "r2727_invalid_original_transition_metric_bounds")
    floor = 0.55 * fraction
    require(penalty + NUMERIC_EPS >= floor,
            "r2727_original_cpp_nonnegative_penalty_components_violated")
    step = row["step"]
    stable = row["stable_mode"]
    if not stable or step == 1:
        require(row["transition_coherence_ok"]
                and row["stable_transition_ready"],
                "r2727_original_cpp_bypassed_stable_gate_was_false")
        return {
            "step": step, "retry": row["retry"],
            "stable_mode": stable,
            "source_coherence_gate": True,
            "source_transition_ready": True,
            "coherence_rederived": True,
            "readiness_rederived": True,
            "coherence_cap": None,
            "underresolved_fraction_cap": None,
            "imbalance_max_cap": None,
            "actual_penalty": penalty,
            "nonnegative_underresolved_penalty_lower_bound": floor,
            "underresolved_fraction": fraction,
            "imbalance_max": imbalance,
            "unobserved_step2_patch_count_not_inferred": True,
            "necessary_bottleneck": [],
        }
    ready_fraction_cap = 0.25 if step >= 4 else 0.10
    ready_imbalance_cap = 0.18 if step >= 4 else 0.12
    expected_ready = (
        fraction <= ready_fraction_cap and
        imbalance <= ready_imbalance_cap
    )
    require(row["stable_transition_ready"] is expected_ready,
            "r2727_source_transition_ready_predicate_changed")
    if step == 2:
        # The exact C++ step-2 expression also requires the unreported
        # source patch count to be zero. Never reconstruct an omitted value.
        coherence_cap = 0.20
        if row["transition_coherence_ok"]:
            require(fraction == 0 and imbalance <= 0.12
                    and penalty <= coherence_cap,
                    "r2727_original_step2_necessary_coherence_violation")
        coherence_rederived = None
    else:
        coherence_cap = 0.42 if step >= 4 else 0.25
        coherence_rederived = penalty <= coherence_cap
        require(row["transition_coherence_ok"] is coherence_rederived,
                "r2727_original_cpp_transition_coherence_gate_changed")
    blocking = []
    if fraction > ready_fraction_cap:
        blocking.append("actual_underresolved_fraction_exceeds_readiness_cap")
    if imbalance > ready_imbalance_cap:
        blocking.append("actual_max_imbalance_exceeds_readiness_cap")
    if penalty > coherence_cap:
        blocking.append("actual_transition_penalty_exceeds_coherence_cap")
    if floor > coherence_cap:
        blocking.append("underresolution_term_alone_exceeds_coherence_cap")
    return {
        "step": step, "retry": row["retry"],
        "stable_mode": stable,
        "source_coherence_gate": row["transition_coherence_ok"],
        "source_transition_ready": row["stable_transition_ready"],
        "coherence_rederived": coherence_rederived,
        "readiness_rederived": expected_ready,
        "coherence_cap": coherence_cap,
        "underresolved_fraction_cap": ready_fraction_cap,
        "imbalance_max_cap": ready_imbalance_cap,
        "actual_penalty": penalty,
        "nonnegative_underresolved_penalty_lower_bound": floor,
        "underresolved_fraction": fraction,
        "imbalance_max": imbalance,
        "unobserved_step2_patch_count_not_inferred": step == 2,
        "necessary_bottleneck": blocking,
    }


def _native_gates(original: Path, trials: Path, model: str,
                  trial_id: str) -> tuple[list[dict], list[dict]]:
    """Bind original and independent one-factor stderr to their saved hashes."""
    source_receipt = json.loads(
        (original / f"r2712-{model}-native-lineage-audit.json")
        .read_text(encoding="utf-8"))
    trial_receipt = json.loads(
        (trials / trial_id / "treatment-report.json")
        .read_text(encoding="utf-8"))
    source_data = (
        original / f"r2718-{model}-original-native-generator-stderr.log"
    ).read_bytes()
    variant_data = (
        trials / trial_id / "original-generator-stderr.log"
    ).read_bytes()
    require(
        source_receipt["original_model"] == model
        and source_receipt["r2718_original_stderr_sha256"] ==
        hashlib.sha256(source_data).hexdigest()
        and trial_receipt["source_model"] == model
        and trial_receipt["id"] == trial_id
        and trial_receipt["original_stderr_sha256"] ==
        hashlib.sha256(variant_data).hexdigest()
        and source_receipt["research_executable_sha256"] ==
        trial_receipt["original_compiled_cpp_executable_sha256"]
        and source_receipt["real_model_input_sha256"] ==
        trial_receipt["native_model_input_sha256"],
        "r2727_original_cpp_stderr_or_executable_source_scope_tampered")
    return (parse_original_gate_stderr(source_data),
            parse_original_gate_stderr(variant_data))


def audit(root: Path, executable: Path, original: Path, trials: Path,
          previous_audit: Path) -> dict:
    """Reopen genuine bytes independently and prove the observed gate bottleneck."""
    root = root.resolve()
    source_attestation = attest_cpp_acceptance_source(root)
    attest_predeclared_source(root)
    reread = audit_previous(root, executable, original, trials)
    retained = json.loads(previous_audit.read_text(encoding="utf-8"))
    require(retained == reread,
            "r2727_prior_original_cpp_source_audit_not_reproduced")
    models = {}
    for trial in TRIALS:
        source, variant = _native_gates(
            original, trials, trial.model, trial.id)
        expected_attempts = 7 if trial.model == "eistute" else 3
        original_keys = [(r["step"], r["retry"]) for r in source]
        variant_keys = [(r["step"], r["retry"]) for r in variant]
        require(original_keys == variant_keys
                and len(original_keys) == expected_attempts
                and original_keys[0] == (1, 0)
                and reread["models"][trial.model]["original_article_steps"]
                == [1]
                and reread["models"][trial.model][
                    "variant_genuine_accepted_steps"] == [1],
                "r2727_original_cpp_attempts_or_postcommit_epochs_changed")
        audited_source = [diagnose_gate(row) for row in source]
        audited_variant = [diagnose_gate(row) for row in variant]
        source_receipt = json.loads((
            original / f"r2712-{trial.model}-native-lineage-audit.json"
        ).read_text(encoding="utf-8"))
        variant_receipt = json.loads((
            trials / trial.id / "treatment-report.json"
        ).read_text(encoding="utf-8"))
        patch_count = source_receipt["accepted_snapshots"][0][
            "native_source_patches"]
        require(type(patch_count) is int and 1 <= patch_count <= 128 and
                variant_receipt["accepted_real_native_face_snapshots"][0][
                    "native_source_patches"] == patch_count,
                "r2727_original_cpp_model_patch_count_not_source_bound")
        deduced_step_four_patch_slots = []
        if trial.model == "eistute":
            require(patch_count == 4,
                    "r2727_original_Eistute_four_source_patches_not_attested")
            require(all(r["stable_mode"] and
                        r["acceptance_mode"] == 0
                        for r in source + variant),
                    "r2727_original_eistute_native_stable_mode_changed")
            step_four = [
                [r for r in records if r["step"] == 4]
                for records in (audited_source, audited_variant)
            ]
            require(
                all(len(pair) == 2 and {x["retry"] for x in pair} ==
                    {0, 1} for pair in step_four)
                and all(
                    r["underresolved_fraction"] == 1.0
                    and r["nonnegative_underresolved_penalty_lower_bound"]
                    > r["coherence_cap"]
                    and not r["source_coherence_gate"]
                    and not r["source_transition_ready"]
                    and {
                        "actual_underresolved_fraction_exceeds_readiness_cap",
                        "underresolution_term_alone_exceeds_coherence_cap",
                    }.issubset(r["necessary_bottleneck"])
                    for pair in step_four for r in pair
                ),
                "r2727_original_eistute_step4_blocker_not_reproduced")
            # The original C++ loop can increment at most once per patch,
            # and its denominator is ALL geometry patches. A fraction of
            # exactly 1.0 proves every original Eistute patch was flagged.
            deduced_step_four_patch_slots = list(range(patch_count))
        else:
            require(all(not r["stable_mode"] for r in source + variant),
                    "r2727_original_book_negative_mode_control_changed")
        models[trial.model] = {
            "trial_id": trial.id,
            "genuine_accepted_steps_inside_original_process": [1],
            "genuine_accepted_steps_inside_variant_process": [1],
            "separate_cpp_processes_not_pooled": True,
            "matching_original_attempts": expected_attempts,
            "source_attempts": audited_source,
            "one_factor_attempts": audited_variant,
            "source_native_patch_count": patch_count,
            "inferred_step4_underresolved_patch_slots":
                deduced_step_four_patch_slots,
            "patch_slots_inferred_from_unchanged_cpp_loop_not_per_patch_log":
                trial.model == "eistute",
            "per_patch_quantitative_transition_mechanism_observed": False,
            "original_source_cpp_executable_sha256": (
                json.loads((
                    original / f"r2712-{trial.model}-native-lineage-audit.json"
                ).read_text())["research_executable_sha256"]),
            "actual_source_stderr_sha256": hashlib.sha256((
                original / f"r2718-{trial.model}-original-native-generator-stderr.log"
            ).read_bytes()).hexdigest(),
            "actual_variant_stderr_sha256": hashlib.sha256((
                trials / trial.id / "original-generator-stderr.log"
            ).read_bytes()).hexdigest(),
        }
    return {
        "schema": SCHEMA,
        "exact_original_generator_and_gate_parser_source": source_attestation,
        "original_r2726_audit_recomputed_and_matched": True,
        "original_native_cpp_acceptance_policy_unchanged": True,
        "all_original_postcommit_receipts_reaudited": True,
        "independent_native_source_models": models,
        "observed_step4_necessary_failure_not_counterfactual_success": True,
        "individual_patch_structural_quantities_directly_observed": False,
        "eistute_all_four_patch_slots_proven_underresolved_by_source_loop": True,
        "actual_second_same_run_accepted_epoch": False,
        "cross_epoch_original_face_curve_ancestry_certified": False,
        "continuous_surface_error_bounds_certified": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--original-directory", required=True, type=Path)
    parser.add_argument("--trials-directory", required=True, type=Path)
    parser.add_argument("--r2726-audit", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    opts = parser.parse_args()
    report = audit(opts.root, opts.exe, opts.original_directory,
                   opts.trials_directory, opts.r2726_audit)
    opts.output.parent.mkdir(parents=True, exist_ok=True)
    with opts.output.open("xb") as out:
        out.write((json.dumps(report, sort_keys=True, indent=2,
                              allow_nan=False) + "\n").encode("utf-8"))
    for item in report["independent_native_source_models"]["eistute"][
            "one_factor_attempts"]:
        if item["step"] == 4:
            print("R2727_ORIGINAL_CPP_STEP4_COHERENCE=" + json.dumps({
                "retry": item["retry"],
                "original_gate_coherent": item["source_coherence_gate"],
                "original_transition_ready": item["source_transition_ready"],
                "underresolved_fraction": item["underresolved_fraction"],
                "penalty": item["actual_penalty"],
                "underresolved_lower_bound":
                    item["nonnegative_underresolved_penalty_lower_bound"],
                "observed_accepted_second_epoch": False,
            }, sort_keys=True))


if __name__ == "__main__":
    main()
