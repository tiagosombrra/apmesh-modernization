"""R2.7.24 preregistered single-factor original C++ source sensitivity experiments.

Never change GeneratorAdaptive acceptance predicates or reclassify a rejected
candidate. Each treatment is a separate source-bound generator process.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

from .native_acceptance_gate_forensics import parse_original_gate_stderr
from .verify_native_lineage import (
    SOURCE_MODELS, decode_ndjson, require, sha256_file,
    validate_lineage_records,
)

SCHEMA = "apmesh.meshstudio.r2724.controlled_single_factor_native_sensitivity.v1"
BASELINE_BLOBS = {
    "eistute": "bd368dbad5b61515106b5d74d28cbde159780cd6",
    "book": "d88116054728311df74a6ece1d38d0cd23a64466",
}


@dataclass(frozen=True)
class Treatment:
    id: str
    model: str
    parameter: str
    original: str
    treatment: str
    rationale: str
    insert_after: str | None = None


# Preregistered, source-controlled treatments. One generation input at a time.
# The source model, native acceptance policy and binary are NEVER changed.
TREATMENTS = (
    Treatment(
        "eistute_curve_growth_stepn_half", "eistute",
        "CURVE_POINT_GROWTH_STEPN", "4.0", "2.0",
        "Test whether a lower subsequent-step source curve point budget "
        "reduces step-four transition imbalance and weak TRI quality.",
    ),
    Treatment(
        "book_adaptive_intensity_half", "book",
        "ADAPTIVE_INTENSITY", "0.02", "0.01",
        "Test whether lower original adaptive sampling intensity avoids "
        "the step-two increase in the actual nonstable mode-zero error.",
    ),
)
MAX_STDERR = 12_000_000
MAX_STDOUT = 3_000_000
MAX_NATIVE_SIDECAR_BYTES = 30_000_000
MAX_STEPS = 4


def git_blob(raw: bytes) -> str:
    head = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    return hashlib.sha1(head + raw).hexdigest()


def make_single_factor_config(original_bytes: bytes, treatment: Treatment) -> bytes:
    """Require an exact, one-line source input change from the article config."""
    require(treatment.model in SOURCE_MODELS and
            git_blob(original_bytes) == BASELINE_BLOBS[treatment.model],
            "r2724_original_article_config_blob_modified")
    require(b"\r" not in original_bytes and original_bytes.endswith(b"\n"),
            "r2724_original_article_config_not_canonical")
    original = original_bytes.decode("utf-8")
    before = treatment.parameter + "=" + treatment.original
    after = treatment.parameter + "=" + treatment.treatment
    require(treatment.original != treatment.treatment,
            "r2724_requested_parameter_not_one_legitimate_source_control")
    if treatment.insert_after is None:
        require(len(re.findall("^" + re.escape(treatment.parameter) + "=",
                               original, flags=re.M)) == 1 and
                original.splitlines().count(before) == 1,
                "r2724_requested_parameter_not_one_legitimate_source_control")
        changed = original.replace(before + "\n", after + "\n")
        require(len(changed.splitlines()) == len(original.splitlines()) and
                sum(a != b for a, b in zip(original.splitlines(),
                                          changed.splitlines())) == 1 and
                changed.replace(after + "\n", before + "\n") == original,
                "r2724_treatment_modified_more_than_one_original_parameter")
    else:
        # Only the independently preregistered Book default-off AFT switch
        # may insert one absent key. Other additions still fail closed.
        require(treatment.model == "book" and
                treatment.parameter == "AFT_LOCAL_POSTPROCESS_PASSES" and
                treatment.original == "0" and treatment.treatment == "1" and
                treatment.insert_after == "ADAPTIVE_TARGET_GROWTH=1.05" and
                original.splitlines().count(treatment.insert_after) == 1 and
                len(re.findall("^" + re.escape(treatment.parameter) + "=",
                               original, flags=re.M)) == 0,
                "r2726_unqualified_omitted_default_parameter")
        marker = treatment.insert_after + "\n"
        changed = original.replace(marker, marker + after + "\n")
        require(changed.replace(after + "\n", "", 1) == original and
                len(changed.splitlines()) == len(original.splitlines()) + 1 and
                changed.splitlines().count(after) == 1,
                "r2726_variant_not_exactly_one_added_default_override")
    # For article configs, original output and input selectors are retained
    # in the immutable intention config. Only the ephemeral run copy changes
    # absolute INPUT_MODEL and OUTPUT_PREFIX to isolate side effects.
    return changed.encode("utf-8")


def resolve_isolated_config(config: str, native_input: Path,
                            output_prefix: Path) -> str:
    """Move only IO into the unique, disposable per-treatment workspace."""
    require(len(re.findall("^INPUT_MODEL=", config, re.M)) == 1 and
            len(re.findall("^OUTPUT_PREFIX=", config, re.M)) == 1,
            "r2724_original_config_io_keys_missing")
    changed = re.sub("^INPUT_MODEL=.+$",
                     lambda _: "INPUT_MODEL=" + native_input.as_posix(),
                     config, flags=re.M)
    changed = re.sub("^OUTPUT_PREFIX=.+$",
                     lambda _: "OUTPUT_PREFIX=" + output_prefix.as_posix(),
                     changed, flags=re.M)
    require(len(re.findall("^INPUT_MODEL=", changed, re.M)) == 1 and
            len(re.findall("^OUTPUT_PREFIX=", changed, re.M)) == 1,
            "r2724_duplicate_isolated_io_fields")
    return changed


def certify_same_run_outcomes(gates: list[dict], receipts: list[dict],
                              accepted_count: int,
                              restored_count: int) -> dict:
    """A precommit yes is not a genuine adaptive epoch without a sidecar."""
    require(0 <= accepted_count <= MAX_STEPS and
            0 <= restored_count <= MAX_STEPS and
            0 < accepted_count + restored_count <= MAX_STEPS and
            len(gates) > 0,
            "r2724_invalid_original_native_step_outcome_count")
    found = {(row["accepted_step"], row["retry_index"])
             for row in receipts}
    require(len(found) == len(receipts) == accepted_count,
            "r2724_duplicate_or_missing_native_accepted_receipt")
    good = {(row["step"], row["retry"]) for row in gates
            if row["predicted_branch_accept_not_committed"]}
    require(good == found and len(good) == accepted_count,
            "r2724_predicted_accept_not_backed_by_real_cpp_commit")
    steps = {row["step"] for row in gates}
    committed_steps = {x[0] for x in found}
    require(all(step in steps for step in committed_steps) and
            len(steps) == accepted_count + restored_count and
            sum(step not in committed_steps for step in steps) == restored_count,
            "r2724_cpp_restored_outcome_not_in_original_gate_events")
    require([row["accepted_step"] for row in receipts] ==
            sorted(committed_steps),
            "r2724_postcommit_source_steps_not_monotonic")
    return {
        "source_accepted_steps": sorted(committed_steps),
        "genuine_source_postcommit_receipts": accepted_count,
        "restored_native_steps": restored_count,
        "local_precommit_decisions": len(gates),
        "two_distinct_commits_within_THIS_single_run": accepted_count >= 2,
        "rejected_intermediates_are_not_adaptive_epochs": True,
        "cross_epoch_native_face_descendants_qualified": False,
        "continuous_geometric_error_bounds_qualified": False,
        "scientific_lod_qualified": False,
    }


def run_treatment(exe: Path, root: Path, original_dir: Path,
                  artifact_root: Path, treatment: Treatment,
                  timeout: int = 300) -> dict:
    """Run genuine compiled serial C++ while retaining all native attempts."""
    require(10 <= timeout <= 600, "r2724_native_timeout_out_of_bounds")
    require(exe.is_file(), "r2724_missing_original_compiled_executable")
    baseline = json.loads(
        (original_dir / f"r2712-{treatment.model}-native-lineage-audit.json")
        .read_text(encoding="utf-8"))
    original_path = root / "configs" / treatment.model / "article.conf"
    original_bytes = original_path.read_bytes()
    require(sha256_file(original_path) ==
            baseline["native_config_source_sha256"] and
            sha256_file(exe) == baseline["research_executable_sha256"] and
            baseline["original_model"] == treatment.model and
            baseline["native_accepted_commits"] == 1,
            "r2724_original_article_control_or_compiled_binary_changed")
    original_text = original_bytes.decode("utf-8")
    selector = re.search(r"^INPUT_MODEL=(.+)$", original_text, flags=re.M)
    require(selector is not None, "r2724_original_source_model_missing")
    model_path = (root / selector.group(1).strip()).resolve()
    require(model_path.is_relative_to(root) and model_path.is_file() and
            sha256_file(model_path) == baseline["real_model_input_sha256"],
            "r2724_original_model_input_changed")
    variant_bytes = make_single_factor_config(original_bytes, treatment)
    destination = artifact_root / treatment.id
    destination.mkdir(parents=True, exist_ok=False)
    # Preserve the exact predeclared intention configuration independently
    # of the disposable resolved temp input/output paths.
    intent_path = destination / "single-factor-intent.conf"
    intent_path.write_bytes(variant_bytes)
    with TemporaryDirectory(prefix=f"r2724-{treatment.model}-") as temp:
        work = Path(temp)
        lineage = work / "accepted-source"
        lineage.mkdir()
        execution_config = resolve_isolated_config(
            variant_bytes.decode("utf-8"), model_path,
            work / (treatment.model + "-treatment"))
        config = work / "isolated-research.conf"
        config.write_text(execution_config, encoding="utf-8", newline="\n")
        (destination / "resolved-execution.conf").write_bytes(
            config.read_bytes())
        env = dict(os.environ,
                   APMESH_RESEARCH_LINEAGE_DIR=str(lineage),
                   APMESH_RESEARCH_ACCEPTANCE_GATES="1",
                   APMESH_RESEARCH_EFFECTIVE_BUDGETS="1")
        process = subprocess.run(
            [str(exe), str(config)], cwd=root, env=env,
            capture_output=True, timeout=timeout, check=False)
        stdout, stderr = process.stdout, process.stderr
        require(len(stdout) <= MAX_STDOUT and len(stderr) <= MAX_STDERR,
                "r2724_native_treatment_logs_exceed_safe_bound")
        (destination / "original-generator-stdout.log").write_bytes(stdout)
        (destination / "original-generator-stderr.log").write_bytes(stderr)
        require(process.returncode == 0 and
                b"R2712_NATIVE_LINEAGE_ERROR=" not in stderr and
                b"R2718_ADAPTER_BOUNDARY_TRACE_ERROR=" not in stderr,
                "r2724_true_original_native_generator_failed")
        marker = re.findall(
            rb"^real_generator_outcomes=1 accepted_tri=(\d+) restored_tri=(\d+)",
            stdout, flags=re.M)
        require(len(marker) == 1,
                "r2724_missing_or_multiple_real_cpp_outcome_markers")
        accepted_count, restored_count = map(int, marker[0])
        gates = parse_original_gate_stderr(stderr)
        sidecars = list(lineage.glob("*.ndjson"))
        require(len(sidecars) == accepted_count and
                not list(lineage.glob("*.pending")),
                "r2724_native_commit_count_vs_original_sidecars_mismatch")
        summaries = []
        for file in sidecars:
            data = file.read_bytes()
            require(0 < len(data) <= MAX_NATIVE_SIDECAR_BYTES,
                    "r2724_unbounded_native_accepted_face_record")
            summary = validate_lineage_records(
                decode_ndjson(data), treatment.model)
            safe_name = (
                "accepted_step_" + str(summary["accepted_step"]) +
                "_retry_" + str(summary["retry_index"]) + ".ndjson"
            )
            require(not (destination / safe_name).exists(),
                    "r2724_duplicate_original_native_accepted_step")
            (destination / safe_name).write_bytes(data)
            summary["artifact_file"] = safe_name
            summary["sha256"] = hashlib.sha256(data).hexdigest()
            summaries.append(summary)
        summaries.sort(key=lambda x: x["accepted_step"])
        verdict = certify_same_run_outcomes(
            gates, summaries, accepted_count, restored_count)
        require(all(row["accepted_step"] <= MAX_STEPS for row in summaries) and
                all(row["step"] <= MAX_STEPS for row in gates),
                "r2724_article_experiment_exceeded_max_steps")
        report = {
            "schema": SCHEMA,
            "id": treatment.id,
            "source_model": treatment.model,
            "treatment_role": "EXPLORATORY_CONFIG_SENSITIVITY_NOT_ARTICLE_REPLICATION",
            "preregistered_exactly_one_parameter": True,
            "parameter": treatment.parameter,
            "original_value": treatment.original,
            "variant_value": treatment.treatment,
            "rationale": treatment.rationale,
            "original_article_git_blob": BASELINE_BLOBS[treatment.model],
            "original_article_sha256": hashlib.sha256(original_bytes).hexdigest(),
            "single_factor_intent_sha256": hashlib.sha256(variant_bytes).hexdigest(),
            "resolved_run_config_sha256": sha256_file(config),
            "native_model_input_sha256": sha256_file(model_path),
            "original_compiled_cpp_executable_sha256": sha256_file(exe),
            "original_stdout_sha256": hashlib.sha256(stdout).hexdigest(),
            "original_stderr_sha256": hashlib.sha256(stderr).hexdigest(),
            "original_stderr_contains_precommit_native_gates": True,
            "original_stderr_contains_actual_adapter_boundary_events":
                b"R2718_ADAPTER_BOUNDARY_CLOSE=" in stderr,
            "process_returncode": process.returncode,
            "accepted_real_native_face_snapshots": summaries,
            "precommit_original_gate_trace": [
                {
                    "step": x["step"],
                    "retry": x["retry"],
                    "predicted_not_yet_committed":
                        x["predicted_branch_accept_not_committed"],
                    "error_improvement_fraction": x["error_improvement_fraction"],
                    "transition_coherence_ok": x["transition_coherence_ok"],
                    "quality_gate_ok": x["quality_gate_ok"],
                    "stable_transition_ready": x["stable_transition_ready"],
                    "candidate_quality_min": x["candidate_quality_min"],
                    "element_growth_factor": x["element_growth_factor"],
                    "native_acceptance_mode": x["acceptance_mode"],
                } for x in gates
            ],
            **verdict,
        }
        (destination / "treatment-report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8", newline="\n")
        return report


def run_preregistered(exe: Path, root: Path, original_dir: Path,
                      output: Path, timeout: int = 300) -> dict:
    exe, root = exe.resolve(), root.resolve()
    require(output != original_dir and
            not output.exists() and len(TREATMENTS) == 2 and
            {x.model for x in TREATMENTS} == set(SOURCE_MODELS),
            "r2724_invalid_preregistered_scope_or_output")
    output.mkdir(parents=True)
    reports = [
        run_treatment(exe, root, original_dir, output, variant, timeout)
        for variant in TREATMENTS
    ]
    conclusion = {
        "schema": "apmesh.meshstudio.r2724.separate_cpp_process_treatment_index.v1",
        "scope": "EXPLORATORY_CONFIG_ONLY_UNCHANGED_CPP_ACCEPTANCE_POLICY",
        "source_input_models": sorted(SOURCE_MODELS),
        "treatment_ids": [r["id"] for r in reports],
        "each_treatment_is_a_distinct_cpp_process_not_a_combined_epoch": True,
        "baseline_native_article_runs_remain_separate_controls": True,
        "all_treatments_have_genuine_two_accepted_same_run_epochs":
            all(r["two_distinct_commits_within_THIS_single_run"]
                for r in reports),
        "cross_epoch_native_descendants_certified": False,
        "continuous_error_bound_certified": False,
        "scientific_lod_qualified": False,
    }
    (output / "index.json").write_text(
        json.dumps(conclusion, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print("R2724_NATIVE_CONTROLLED_SOURCE_SENSITIVITY=" +
          json.dumps({r["id"]: {
              "accepted_steps": r["source_accepted_steps"],
              "restored": r["restored_native_steps"],
              "local_attempts": r["local_precommit_decisions"],
              "two_committed_same_run": r[
                  "two_distinct_commits_within_THIS_single_run"],
              "changed_parameter": r["parameter"],
              "variant_value": r["variant_value"],
          } for r in reports}, sort_keys=True))
    return conclusion


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--original-directory", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=300)
    arguments = parser.parse_args()
    run_preregistered(arguments.exe, arguments.root,
                      arguments.original_directory,
                      arguments.out_dir, arguments.timeout)


if __name__ == "__main__":
    main()
