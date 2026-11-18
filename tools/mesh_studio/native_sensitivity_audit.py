"""Independent R2.7.24 original-native sensitivity audit over retained bytes.

Treatments remain exploratory, independently source-scoped C++ executions.
They are never appended to the original article run's accepted-epoch history.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from .native_acceptance_gate_forensics import parse_original_gate_stderr
from .native_controlled_sensitivity import (
    BASELINE_BLOBS, SCHEMA, TREATMENTS, certify_same_run_outcomes,
    git_blob, make_single_factor_config, resolve_isolated_config,
)
from .verify_native_lineage import (
    decode_ndjson, require, sha256_file, validate_lineage_records,
)

AUDIT_SCHEMA = "apmesh.meshstudio.r2724.independent_native_treatment_audit.v1"


def audit_preregistered_treatments(root: Path, original_dir: Path,
                                  artifact_root: Path, exe: Path) -> dict:
    """Rebuild claims from original article inputs, stderr and postcommit bytes."""
    root, exe = root.resolve(), exe.resolve()
    index_path = artifact_root / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    require(index.get("schema") ==
            "apmesh.meshstudio.r2724.separate_cpp_process_treatment_index.v1" and
            index.get("scope") ==
            "EXPLORATORY_CONFIG_ONLY_UNCHANGED_CPP_ACCEPTANCE_POLICY" and
            index.get("treatment_ids") == [v.id for v in TREATMENTS] and
            index.get("source_input_models") == sorted(
                {v.model for v in TREATMENTS}) and
            index.get("cross_epoch_native_descendants_certified") is False and
            index.get("continuous_error_bound_certified") is False and
            index.get("each_treatment_is_a_distinct_cpp_process_not_a_combined_epoch")
            is True and index.get("baseline_native_article_runs_remain_separate_controls")
            is True and index.get("scientific_lod_qualified") is False and
            set(item.name for item in artifact_root.iterdir()) ==
            {"index.json"} | {v.id for v in TREATMENTS},
            "r2724_original_single_factor_inventory_not_preregistered")
    observed = {}
    for variant in TREATMENTS:
        original = root / "configs" / variant.model / "article.conf"
        control = json.loads(
            (original_dir / f"r2712-{variant.model}-native-lineage-audit.json")
            .read_text(encoding="utf-8"))
        article = original.read_bytes()
        selector = re.search(rb"^INPUT_MODEL=(.+)$", article, flags=re.M)
        require(selector is not None, "r2724_original_native_input_selector_missing")
        source_path = (root / selector.group(1).decode("utf-8").strip()).resolve()
        require(source_path.is_relative_to(root) and source_path.is_file() and
                sha256_file(source_path) == control["real_model_input_sha256"],
                "r2724_original_native_model_input_changed")
        expected_intent = make_single_factor_config(article, variant)
        directory = artifact_root / variant.id
        report = json.loads(
            (directory / "treatment-report.json").read_text(encoding="utf-8"))
        retained_config = (directory / "single-factor-intent.conf").read_bytes()
        # Detect a forged preregistered treatment before inspecting any
        # secondary run-time IO transformation of that source config.
        require(retained_config == expected_intent,
                "r2724_treatment_article_input_config_or_executable_forged")
        resolved_config = (directory / "resolved-execution.conf").read_bytes()
        require(b"\r" not in resolved_config and
                resolved_config.endswith(b"\n"),
                "r2724_original_resolved_execution_not_canonical")
        output_selector = re.search(
            rb"^OUTPUT_PREFIX=(.+)$", resolved_config, re.M)
        require(output_selector is not None,
                "r2724_missing_isolated_native_output")
        output_prefix = Path(output_selector.group(1).decode("utf-8").strip())
        require(output_prefix.is_absolute() and
                resolved_config.decode("utf-8") ==
                resolve_isolated_config(
                    retained_config.decode("utf-8"), source_path,
                    output_prefix),
                "r2724_resolved_config_changed_more_than_io")
        require(type(report) is dict and report.get("schema") == SCHEMA and
                report.get("id") == variant.id and
                report.get("source_model") == variant.model and
                report.get("treatment_role") ==
                "EXPLORATORY_CONFIG_SENSITIVITY_NOT_ARTICLE_REPLICATION" and
                report.get("preregistered_exactly_one_parameter") is True and
                report.get("parameter") == variant.parameter and
                report.get("original_value") == variant.original and
                report.get("variant_value") == variant.treatment and
                report.get("rationale") == variant.rationale and
                report.get("original_article_git_blob") ==
                BASELINE_BLOBS[variant.model] and
                git_blob(article) == BASELINE_BLOBS[variant.model] and
                report.get("original_article_sha256") ==
                control["native_config_source_sha256"] ==
                sha256_file(original) and
                retained_config == expected_intent and
                report.get("single_factor_intent_sha256") ==
                hashlib.sha256(retained_config).hexdigest() and
                report.get("resolved_run_config_sha256") ==
                hashlib.sha256(resolved_config).hexdigest() and
                report.get("native_model_input_sha256") ==
                control["real_model_input_sha256"] and
                report.get("original_compiled_cpp_executable_sha256") ==
                control["research_executable_sha256"] == sha256_file(exe) and
                report.get("process_returncode") == 0 and
                report.get("scientific_lod_qualified") is False,
                "r2724_treatment_article_input_config_or_executable_forged")
        stdout = (directory / "original-generator-stdout.log").read_bytes()
        stderr = (directory / "original-generator-stderr.log").read_bytes()
        require(len(stdout) <= 3_000_000 and len(stderr) <= 12_000_000 and
                report.get("original_stdout_sha256") ==
                hashlib.sha256(stdout).hexdigest() and
                report.get("original_stderr_sha256") ==
                hashlib.sha256(stderr).hexdigest() and
                report.get("original_stderr_contains_precommit_native_gates") is True and
                report.get("original_stderr_contains_actual_adapter_boundary_events") is
                (b"R2718_ADAPTER_BOUNDARY_CLOSE=" in stderr) and
                b"R2712_NATIVE_LINEAGE_ERROR=" not in stderr and
                b"R2718_ADAPTER_BOUNDARY_TRACE_ERROR=" not in stderr,
                "r2724_native_controlled_original_process_bytes_invalid")
        marker = re.findall(
            rb"^real_generator_outcomes=1 accepted_tri=(\d+) restored_tri=(\d+)",
            stdout, flags=re.M)
        require(len(marker) == 1,
                "r2724_missing_actual_cpp_outcomes_in_raw_stdout")
        accepted, restored = map(int, marker[0])
        gates = parse_original_gate_stderr(stderr)
        receipts = []
        for file in sorted(directory.glob("*.ndjson")):
            data = file.read_bytes()
            verify = validate_lineage_records(
                decode_ndjson(data), variant.model)
            require(file.name ==
                    f"accepted_step_{verify['accepted_step']}_retry_{verify['retry_index']}.ndjson",
                    "r2724_native_accepted_sidecar_wrong_scope")
            verify["artifact_file"] = file.name
            verify["sha256"] = hashlib.sha256(data).hexdigest()
            receipts.append(verify)
        receipts.sort(key=lambda x: x["accepted_step"])
        certification = certify_same_run_outcomes(
            gates, receipts, accepted, restored)
        require(report.get("accepted_real_native_face_snapshots") == receipts and
                report.get("source_accepted_steps") ==
                certification["source_accepted_steps"] and
                report.get("genuine_source_postcommit_receipts") == accepted and
                report.get("restored_native_steps") == restored and
                report.get("local_precommit_decisions") == len(gates) and
                report.get("two_distinct_commits_within_THIS_single_run") is
                certification["two_distinct_commits_within_THIS_single_run"] and
                report.get("cross_epoch_native_face_descendants_qualified") is False and
                report.get("continuous_geometric_error_bounds_qualified") is False,
                "r2724_treatment_report_does_not_match_original_native_commits")
        predictions = [{
            "step": x["step"], "retry": x["retry"],
            "predicted_not_yet_committed":
                x["predicted_branch_accept_not_committed"],
            "error_improvement_fraction": x["error_improvement_fraction"],
            "transition_coherence_ok": x["transition_coherence_ok"],
            "quality_gate_ok": x["quality_gate_ok"],
            "stable_transition_ready": x["stable_transition_ready"],
            "candidate_quality_min": x["candidate_quality_min"],
            "element_growth_factor": x["element_growth_factor"],
            "native_acceptance_mode": x["acceptance_mode"],
        } for x in gates]
        require(report.get("precommit_original_gate_trace") == predictions,
                "r2724_reported_original_predicates_do_not_match_cpp_stderr")
        require(set(file.name for file in directory.iterdir()) ==
                {"single-factor-intent.conf", "resolved-execution.conf",
                 "treatment-report.json",
                 "original-generator-stdout.log",
                 "original-generator-stderr.log"} |
                {receipt["artifact_file"] for receipt in receipts},
                "r2724_unaccounted_native_treatment_artifacts")
        original_steps = [x["accepted_step"]
                          for x in control["accepted_snapshots"]]
        require(original_steps == [1] and
                control["native_accepted_commits"] == 1 and
                control["second_accepted_epoch_observed"] is False,
                "r2724_original_article_control_not_one_real_epoch")
        observed[variant.id] = {
            "model": variant.model,
            "article_control_accepted_steps": original_steps,
            "original_article_config_sha256":
                control["native_config_source_sha256"],
            "controlled_variant_config_sha256":
                report["single_factor_intent_sha256"],
            "original_compiled_executable_sha256":
                report["original_compiled_cpp_executable_sha256"],
            "unchanged_original_model_input_sha256":
                report["native_model_input_sha256"],
            "parameter": variant.parameter,
            "one_factor_value": variant.treatment,
            "independent_native_run_accepted_steps":
                certification["source_accepted_steps"],
            "native_postcommit_accepted_face_counts": [
                x["native_tri_faces"] for x in receipts],
            "independent_native_run_restored_steps": restored,
            "original_cpp_precommit_attempt_count": len(gates),
            "original_stderr_sha256": hashlib.sha256(stderr).hexdigest(),
            "two_genuine_committed_steps_inside_one_treatment_run":
                accepted >= 2,
            "cross_epoch_face_or_curve_descendants_certified": False,
            "continuous_geometric_error_bound_certified": False,
            "scientific_lod_qualified": False,
        }
    require(index.get("all_treatments_have_genuine_two_accepted_same_run_epochs") is
            all(x["two_genuine_committed_steps_inside_one_treatment_run"]
                for x in observed.values()),
            "r2724_pooled_acceptance_misrepresented_as_within_run_epochs")
    return {
        "schema": AUDIT_SCHEMA,
        "kind": "ACTUAL_ISOLATED_COMPILED_NATIVE_CPP_CONFIG_SENSITIVITY",
        "all_original_article_configs_unchanged": True,
        "all_original_model_input_sha256_unchanged": True,
        "native_generator_acceptance_policy_modified": False,
        "variants_are_exploratory_not_article_replications": True,
        "treatments": observed,
        "two_epoch_lod_acceptance_gate_qualified": False,
        "cross_epoch_native_descendants_qualified": False,
        "continuous_error_bound_qualified": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--original-directory", required=True, type=Path)
    parser.add_argument("--treatments", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    audit = audit_preregistered_treatments(
        args.root, args.original_directory, args.treatments, args.exe)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as sink:
        sink.write((json.dumps(audit, sort_keys=True, indent=2,
                               allow_nan=False) + "\n").encode("utf-8"))
    print("R2724_INDEPENDENT_NATIVE_TREATMENT_AUDIT="+json.dumps({
        name:{
            "original_article_accepted_steps":x["article_control_accepted_steps"],
            "variant_accepted_steps":x["independent_native_run_accepted_steps"],
            "variant_restored":x["independent_native_run_restored_steps"],
            "two_inside_same_run":
                x["two_genuine_committed_steps_inside_one_treatment_run"],
            "original_source_input_sha256":
                x["unchanged_original_model_input_sha256"],
            "variant_config_sha256":
                x["controlled_variant_config_sha256"],
        } for name,x in audit["treatments"].items()}, sort_keys=True))


if __name__ == "__main__":
    main()
