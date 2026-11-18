"""R2.7.26: source-bound genuine native single-factor generation treatments.

The preregistration is immutable and precedes both this implementation and
every R2.7.26 real C++ process. Rejected source candidates are not LOD epochs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .native_acceptance_gate_forensics import parse_original_gate_stderr
from .native_controlled_sensitivity import (
    Treatment, git_blob, make_single_factor_config, run_treatment,
)
from .native_effective_budget_audit import parse_effective_budgets
from .native_sensitivity_audit import audit_preregistered_treatments
from .verify_native_lineage import SOURCE_MODELS, require

PREREGISTRATION_PATH = "docs/mesh-studio/R2_7_26_PREREGISTERED_ACTIVE_GENERATION_CONTROLS_20261118.md"
PREREGISTRATION_BLOB = "a2837c5c424d7e88a7383d82f73ca2702532a946"
RUNTIME_CONFIG_BLOB = "f29dc337a64870f14f584849c87943435eb4a04a"
AFT_IMPLEMENTATION_BLOB = "1bd430d1bd1079e6f55f3bc7488ff9313e4bb82b"

SCHEMA = "apmesh.meshstudio.r2726.original_active_generation_source_audit.v1"
INDEX_SCHEMA = "apmesh.meshstudio.r2724.separate_cpp_process_treatment_index.v1"
SCOPE = "EXPLORATORY_CONFIG_ONLY_UNCHANGED_CPP_ACCEPTANCE_POLICY"

# Exactly two predeclared independent processes; no tuning after trial results.
TRIALS = (
    Treatment(
        "eistute_curve_min_13", "eistute",
        "CURVE_POINT_MIN", "11", "13",
        "Test whether the original active minimum curve budget changes "
        "sampling and native postcommit/source-local quality, without "
        "assuming a second accepted epoch.",
    ),
    Treatment(
        "book_aft_one_local_pass", "book",
        "AFT_LOCAL_POSTPROCESS_PASSES", "0", "1",
        "Test whether enabling one original AFT poor-region local smoothing "
        "pass changes real native precommit quality/geometry while retaining "
        "unchanged acceptance predicates.",
        insert_after="ADAPTIVE_TARGET_GROWTH=1.05",
    ),
)


def attest_predeclared_source(root: Path) -> dict:
    """Fail closed if original config semantics or prior protocol drifted."""
    root = root.resolve()
    sources = (
        (PREREGISTRATION_PATH, PREREGISTRATION_BLOB),
        ("src/application/runtime_config.cpp", RUNTIME_CONFIG_BLOB),
        ("src/crab_mesh/aft/advancing_front.cpp", AFT_IMPLEMENTATION_BLOB),
    )
    verified = {}
    for path, expected in sources:
        raw = (root / path).read_bytes()
        require(git_blob(raw) == expected,
                "r2726_original_cpp_parser_aft_or_preregistration_changed")
        verified[path] = {"git_blob": expected,
                          "sha256": hashlib.sha256(raw).hexdigest()}
    parser = (root / "src/application/runtime_config.cpp").read_text(
        encoding="utf-8")
    aft = (root / "src/crab_mesh/aft/advancing_front.cpp").read_text(
        encoding="utf-8")
    require(
        'GetConfigValue(values, "AFT_LOCAL_POSTPROCESS_PASSES", "0")' in parser
        and "for (int pass = 0; pass < PostprocessPasses(); ++pass)" in aft
        and "poorRegionShapeSmoothing(passChanged, faceAdjacency)" in aft,
        "r2726_original_aft_default_or_executable_branch_unproven")
    require(len(TRIALS) == 2 and {v.model for v in TRIALS} == set(SOURCE_MODELS),
            "r2726_wrong_preregistered_source_models")
    for variant in TRIALS:
        article = (root / "configs" / variant.model / "article.conf").read_bytes()
        intention = make_single_factor_config(article, variant)
        require(intention != article and
                intention.count((variant.parameter + "=").encode()) == 1,
                "r2726_inactive_or_duplicate_single_factor_intent")
    return verified


def run(exe: Path, root: Path, original: Path, output: Path,
        timeout: int) -> dict:
    """Execute only real separately isolated predeclared native C++ trials."""
    root, exe = root.resolve(), exe.resolve()
    evidence = attest_predeclared_source(root)
    require(not output.exists() and output.resolve() != original.resolve() and
            10 <= timeout <= 600, "r2726_unsafe_trial_root_or_timeout")
    output.mkdir(parents=True)
    reports = [
        run_treatment(exe, root, original, output, treatment, timeout)
        for treatment in TRIALS
    ]
    # Preserve the existing complete independent R2.7.24 raw audit schema.
    index = {
        "schema": INDEX_SCHEMA,
        "scope": SCOPE,
        "source_input_models": sorted(SOURCE_MODELS),
        "treatment_ids": [x.id for x in TRIALS],
        "each_treatment_is_a_distinct_cpp_process_not_a_combined_epoch": True,
        "baseline_native_article_runs_remain_separate_controls": True,
        "all_treatments_have_genuine_two_accepted_same_run_epochs":
            all(x["two_distinct_commits_within_THIS_single_run"] for x in reports),
        "cross_epoch_native_descendants_certified": False,
        "continuous_error_bound_certified": False,
        "scientific_lod_qualified": False,
        "r2726_preregistration_git_blob": PREREGISTRATION_BLOB,
        "r2726_source_guards": evidence,
    }
    (output / "index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n")
    print("R2726_REAL_NATIVE_TRIALS=" + json.dumps({
        x["id"]: {
            "accepted_steps": x["source_accepted_steps"],
            "restored_steps": x["restored_native_steps"],
            "postcommit_tri_sha256": [
                a["sha256"] for a in x["accepted_real_native_face_snapshots"]],
            "two_in_one_run": x["two_distinct_commits_within_THIS_single_run"],
        } for x in reports
    }, sort_keys=True))
    return index


def audit(root: Path, exe: Path, original: Path, trials: Path) -> dict:
    """Independently reopen real native bytes and compare only shared attempts."""
    root, exe = root.resolve(), exe.resolve()
    source = attest_predeclared_source(root)
    index = json.loads((trials / "index.json").read_text(encoding="utf-8"))
    require(index.get("r2726_preregistration_git_blob") == PREREGISTRATION_BLOB
            and index.get("r2726_source_guards") == source,
            "r2726_original_source_or_preregistration_index_forged")
    legacy_audit = audit_preregistered_treatments(
        root, original, trials, exe, treatments=TRIALS)
    result = {}
    for variant in TRIALS:
        model = variant.model
        base_log = (original /
                    f"r2718-{model}-original-native-generator-stderr.log").read_bytes()
        trial_dir = trials / variant.id
        treated_log = (trial_dir / "original-generator-stderr.log").read_bytes()
        base_receipt = json.loads(
            (original / f"r2712-{model}-native-lineage-audit.json").read_text())
        treated_receipt = json.loads(
            (trial_dir / "treatment-report.json").read_text())
        require(
            base_receipt["r2718_original_stderr_sha256"] ==
            hashlib.sha256(base_log).hexdigest()
            and treated_receipt["original_stderr_sha256"] ==
            hashlib.sha256(treated_log).hexdigest()
            and treated_receipt["original_compiled_cpp_executable_sha256"] ==
            base_receipt["research_executable_sha256"]
            and base_receipt["real_model_input_sha256"] ==
            treated_receipt["native_model_input_sha256"],
            "r2726_original_native_stderr_executable_or_model_not_bound")
        baseline = parse_effective_budgets(base_log, model)
        experiment = parse_effective_budgets(treated_log, model)
        def keyed(data: list[dict]) -> dict:
            return {(x["step"], x["retry"]): x for x in data}
        baseline_by_key, trial_by_key = keyed(baseline), keyed(experiment)
        matched = sorted(baseline_by_key.keys() & trial_by_key.keys())
        require(bool(matched) and matched[0] == (1, 0),
                "r2726_no_common_original_native_attempt_to_compare")
        all_curve_changes = []
        attempts = []
        for key in matched:
            previous = baseline_by_key[key]
            changed = trial_by_key[key]
            count = len(previous["final"])
            require(len(changed["final"]) == count,
                    "r2726_source_curve_record_cardinality_changed")
            actual_changed = sum(
                a["actual_points"] != b["actual_points"]
                for a, b in zip(previous["final"], changed["final"]))
            final_target_changed = sum(
                a["final_target"] != b["final_target"]
                for a, b in zip(previous["final"], changed["final"]))
            pre_target_changed = sum(
                a["pre_consistency_target"] != b["pre_consistency_target"]
                for a, b in zip(previous["base"], changed["base"]))
            all_curve_changes.append(actual_changed)
            attempts.append({
                "step": key[0], "retry": key[1],
                "source_curve_count": count,
                "pre_consistency_target_changes": pre_target_changed,
                "final_target_changes": final_target_changed,
                "actual_curve_sample_changes": actual_changed,
                "native_base_element_target":
                    previous["element"]["effective_target_elements"],
                "native_variant_element_target":
                    changed["element"]["effective_target_elements"],
            })
        g1 = {(x["step"], x["retry"]): x for x in
              parse_original_gate_stderr(base_log)}
        g2 = {(x["step"], x["retry"]): x for x in
              parse_original_gate_stderr(treated_log)}
        quality = [{
            "step": key[0], "retry": key[1],
            "source_quality_min": g1[key]["candidate_quality_min"],
            "variant_quality_min": g2[key]["candidate_quality_min"],
            "source_error": g1[key]["candidate_error"],
            "variant_error": g2[key]["candidate_error"],
            "source_predicted_accept":
                g1[key]["predicted_branch_accept_not_committed"],
            "variant_predicted_accept":
                g2[key]["predicted_branch_accept_not_committed"],
        } for key in matched]
        # Native article evidence uses source_file_sha256; the isolated
        # treatment writer adds sha256. Neither accepted source may be omitted.
        original_sha = [x["source_file_sha256"]
                        for x in base_receipt["accepted_snapshots"]]
        variant_sha = [x["sha256"] for x in
                       treated_receipt["accepted_real_native_face_snapshots"]]
        require(len(original_sha) == base_receipt["native_accepted_commits"]
                and len(variant_sha) ==
                treated_receipt["genuine_source_postcommit_receipts"]
                and all(len(value) == 64 for value in original_sha + variant_sha),
                "r2726_missing_original_or_variant_accepted_source_sha256")
        result[model] = {
            "trial": variant.id,
            "one_factor": {"name": variant.parameter,
                           "source": variant.original,
                           "variant": variant.treatment,
                           "inserted_omitted_default":
                               variant.insert_after is not None},
            "original_article_steps":
                legacy_audit["treatments"][variant.id][
                    "article_control_accepted_steps"],
            "variant_genuine_accepted_steps":
                legacy_audit["treatments"][variant.id][
                    "independent_native_run_accepted_steps"],
            "variant_rejected_restored":
                legacy_audit["treatments"][variant.id][
                    "independent_native_run_restored_steps"],
            "original_native_stdout_stderr_sha256":
                base_receipt["r2718_original_stderr_sha256"],
            "trial_stderr_sha256": treated_receipt["original_stderr_sha256"],
            "original_accepted_face_sha256": original_sha,
            "variant_accepted_face_sha256": variant_sha,
            "matched_original_attempts_only": attempts,
            "matched_quality_and_error_not_normalized": quality,
            "matched_actual_sample_changes": sum(all_curve_changes),
            "unmatched_source_attempts":
                sorted([list(x) for x in baseline_by_key.keys() - trial_by_key.keys()]),
            "unmatched_trial_attempts":
                sorted([list(x) for x in trial_by_key.keys() - baseline_by_key.keys()]),
            "two_accepted_epochs_within_trial":
                len(treated_receipt["source_accepted_steps"]) >= 2,
            "rejected_candidates_never_counted_as_epochs": True,
            "cross_epoch_ancestry_certified": False,
            "continuous_surface_error_certified": False,
            "scientific_lod_qualified": False,
        }
    return {
        "schema": SCHEMA,
        "preregistration_original_git_blob": PREREGISTRATION_BLOB,
        "source_attestation": source,
        "original_native_compiled_cpp_and_per_face_lineage_reaudited": True,
        "r2724_independent_source_auditor_reused": True,
        "original_article_settings_unchanged": True,
        "acceptance_policy_modified": False,
        "separate_cpp_processes_never_pooled_into_epochs": True,
        "models": result,
        "cross_epoch_face_curve_descendants_certified": False,
        "continuous_surface_error_certified": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("run", "audit"), required=True)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--original-directory", type=Path, required=True)
    parser.add_argument("--trials-directory", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.mode == "run":
        run(args.exe, args.root, args.original_directory,
            args.trials_directory, args.timeout)
        return
    require(args.output is not None, "r2726_missing_independent_audit_output")
    verdict = audit(args.root, args.exe, args.original_directory,
                    args.trials_directory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as sink:
        sink.write((json.dumps(verdict, indent=2, sort_keys=True,
                               allow_nan=False) + "\n").encode("utf-8"))
    print("R2726_ORIGINAL_NATIVE_GENERATION_AUDIT=" + json.dumps({
        model: {
            "accepted_steps": record["variant_genuine_accepted_steps"],
            "restored": record["variant_rejected_restored"],
            "sample_changes_shared_attempts":
                record["matched_actual_sample_changes"],
            "two_genuine_same_run_commits":
                record["two_accepted_epochs_within_trial"],
            "lod_certified": False,
        } for model, record in verdict["models"].items()
    }, sort_keys=True))


if __name__ == "__main__":
    main()
