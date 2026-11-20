"""R2.7.25: audit effective native C++ curve and element budgets, read-only.

This audit never labels a rejected adapter candidate as accepted TRI geometry.
The raw C++ stderr, original source SHA and separately certified postcommit
sidecars remain the authoritative scientific source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from .native_acceptance_gate_forensics import parse_original_gate_stderr
from .native_controlled_sensitivity import TREATMENTS
from .verify_native_lineage import NativeLineageValidationError, require

BUDGET_SCHEMA = "apmesh.meshstudio.r2725.actual_effective_budget.v1"
BASE_SCHEMA = "apmesh.meshstudio.r2725.actual_curve_components.v1"
FINAL_SCHEMA = "apmesh.meshstudio.r2725.actual_curve_final.v1"
REPORT_SCHEMA = "apmesh.meshstudio.r2725.source_bound_effective_budget_audit.v1"
MARKERS = (
    (b"R2725_ELEMENT_BUDGET=", "element"),
    (b"R2725_CURVE_BASE=", "curve_base"),
    (b"R2725_CURVE_FINAL=", "curve_final"),
)
SIZES = {"eistute": 13, "book": 85}
MAX_STDERR = 5_000_000
MAX_EVENTS = 1500
INT_ELEMENT = ("step", "retry", "budget_driven", "element_target_mode",
               "previous_elements")
NUM_ELEMENT = ("configured_intensity", "policy_step1_growth",
               "step1_element_growth", "step2_element_growth",
               "step3_element_growth", "effective_growth",
               "effective_target_elements")
INT_CURVE_BASE = ("step", "retry", "curve_index", "previous_points",
                  "growth_target", "priority_target", "geometric_floor",
                  "pre_consistency_target")
INT_CURVE_FINAL = ("step", "retry", "curve_index", "before_consistency",
                   "after_consistency", "final_target", "actual_points")


def _parse_strict(raw: bytes, expected: str) -> dict:
    """Reject missing, duplicate or non-finite source-native JSON fields."""
    require(0 < len(raw) < 1500, "r2725_invalid_or_oversized_cpp_trace_line")
    def unique(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, "r2725_duplicate_native_cpp_json_key")
            value[key] = item
        return value
    try:
        record = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                            parse_constant=lambda value: (_ for _ in ()).throw(
                                ValueError("non-finite original C++ " + value)))
    except NativeLineageValidationError:
        raise
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("r2725_invalid_original_cpp_budget_json") from exc
    require(type(record) is dict and record.get("schema") == expected and
            record.get("scientific_lod_qualified") is False and
            all(type(v) is not float or math.isfinite(v)
                for v in record.values()),
            "r2725_original_cpp_trace_schema_or_number_invalid")
    return record


def _check_fields(record: dict, integers: tuple[str, ...],
                  numbers: tuple[str, ...], booleans: tuple[str, ...]) -> None:
    fields = {"schema", "scientific_lod_qualified"} | set(integers) | \
             set(numbers) | set(booleans)
    require(set(record) == fields and
            all(type(record[k]) is int and 0 <= record[k] <= 100_000_000
                for k in integers) and
            all(type(record[k]) in (float, int) and
                math.isfinite(record[k]) and
                0 <= record[k] <= 1e12 for k in numbers) and
            all(type(record[k]) is bool for k in booleans),
            "r2725_original_cpp_budget_fields_invalid")


def parse_effective_budgets(stderr: bytes, model: str) -> list[dict]:
    """Group exactly one original C++ element and N curve witnesses per retry."""
    require(model in SIZES and 0 < len(stderr) <= MAX_STDERR,
            "r2725_missing_or_unbounded_original_cpp_stderr")
    events = []
    for line in stderr.splitlines():
        for prefix, kind in MARKERS:
            if line.startswith(prefix):
                events.append((kind, line[len(prefix):]))
                break
    count = SIZES[model]
    require(0 < len(events) <= MAX_EVENTS,
            "r2725_missing_or_unbounded_source_budget_events")
    grouped = []
    current = None
    for kind, source in events:
        schema = {"element": BUDGET_SCHEMA, "curve_base": BASE_SCHEMA,
                  "curve_final": FINAL_SCHEMA}[kind]
        row = _parse_strict(source, schema)
        if kind == "element":
            _check_fields(row, INT_ELEMENT, NUM_ELEMENT, ("stable",))
            require(row["step"] <= 16 and row["retry"] <= 12 and
                    row["budget_driven"] in (0, 1) and
                    row["element_target_mode"] in (0, 1) and
                    row["configured_intensity"] <= 1.0,
                    "r2725_bad_native_budget_scope")
            if current is not None:
                _finish(current, count)
                grouped.append(current)
            current = {"step": row["step"], "retry": row["retry"],
                       "element": row, "base": [], "final": []}
        else:
            require(current is not None and
                    (row["step"], row["retry"]) ==
                    (current["step"], current["retry"]),
                    "r2725_unscoped_or_cross_retry_curve_witness")
            if kind == "curve_base":
                _check_fields(row, INT_CURVE_BASE, ("configured_growth_cap",),
                              ("budget_active", "priority_patch",
                               "sensitive_curve"))
                require(not current["final"] and
                        row["curve_index"] == len(current["base"]) and
                        row["curve_index"] < count and
                        2 <= row["previous_points"] and
                        (not row["budget_active"] or
                         current["element"]["budget_driven"] == 1),
                        "r2725_source_curve_component_order_invalid")
                require(row["pre_consistency_target"] ==
                        max(row["growth_target"], row["priority_target"],
                            row["geometric_floor"]) and
                        row["growth_target"] >= 2 and
                        row["priority_target"] >= 2 and
                        row["configured_growth_cap"] <= 1e5,
                        "r2725_cpp_component_target_not_original_max")
                current["base"].append(row)
            else:
                _check_fields(row, INT_CURVE_FINAL, (),
                              ("structurally_clamped",))
                require(len(current["base"]) == count,
                        "r2725_incomplete_original_curves_per_native_attempt")
                require(
                        row["curve_index"] == len(current["final"]) and
                        row["curve_index"] < count and
                        row["before_consistency"] ==
                        current["base"][row["curve_index"]][
                            "pre_consistency_target"] and
                        row["after_consistency"] == row["final_target"] and
                        row["final_target"] >= 2 and
                        row["actual_points"] >= 2,
                        "r2725_original_after_consistency_or_actual_curve_mismatch")
                current["final"].append(row)
    require(current is not None,
            "r2725_original_native_effective_budget_missing")
    _finish(current, count)
    grouped.append(current)
    identities = [(x["step"], x["retry"]) for x in grouped]
    require(len(set(identities)) == len(identities) and
            identities == sorted(identities),
            "r2725_duplicate_or_out_of_order_native_attempt")
    acceptance = parse_original_gate_stderr(stderr)
    require(identities == [(x["step"], x["retry"]) for x in acceptance],
            "r2725_original_cpp_budget_not_same_accepted_restored_attempts")
    return grouped


def _finish(group: dict, expected: int) -> None:
    require(len(group["base"]) == len(group["final"]) == expected,
            "r2725_incomplete_original_curves_per_native_attempt")


def summarize_source_trial(source: list[dict], experimental: list[dict],
                           model: str) -> dict:
    """Attribute observed budget changes without presuming causal acceptance."""
    require(model in SIZES and
            [(x["step"], x["retry"]) for x in source] ==
            [(x["step"], x["retry"]) for x in experimental],
            "r2725_original_and_trial_different_cpp_attempt_chronology")
    base_curve_changes = 0
    output_target_changes = 0
    real_sample_count_changes = 0
    effective_element_target_changes = 0
    geometric_floor_dominant = 0
    priority_floor_dominant = 0
    structural_clamps = 0
    attempts = []
    for baseline, trial in zip(source, experimental):
        if (baseline["element"]["effective_target_elements"] !=
                trial["element"]["effective_target_elements"]):
            effective_element_target_changes += 1
        diffs = {"base": 0, "final_target": 0, "actual": 0}
        for b, t, bf, tf in zip(
                baseline["base"], trial["base"],
                baseline["final"], trial["final"]):
            if b["growth_target"] != t["growth_target"]:
                base_curve_changes += 1
                diffs["base"] += 1
            if bf["final_target"] != tf["final_target"]:
                output_target_changes += 1
                diffs["final_target"] += 1
            if bf["actual_points"] != tf["actual_points"]:
                real_sample_count_changes += 1
                diffs["actual"] += 1
            geometric_floor_dominant += int(
                b["geometric_floor"] > b["growth_target"] and
                b["geometric_floor"] >= b["priority_target"])
            priority_floor_dominant += int(
                b["priority_target"] > b["growth_target"] and
                b["priority_target"] > b["geometric_floor"])
            structural_clamps += int(bf["structurally_clamped"])
        attempts.append({"step": baseline["step"], "retry": baseline["retry"],
                         "different_growth_targets": diffs["base"],
                         "different_postconsistency_targets":
                             diffs["final_target"],
                         "different_actual_point_counts": diffs["actual"],
                         "source_effective_element_target":
                             baseline["element"]["effective_target_elements"],
                         "trial_effective_element_target":
                             trial["element"]["effective_target_elements"]})
    return {
        "model": model,
        "real_original_attempts": len(source),
        "real_original_curves_per_attempt": SIZES[model],
        "original_configured_intensity": source[0]["element"]["configured_intensity"],
        "variant_configured_intensity": experimental[0]["element"]["configured_intensity"],
        "original_policy_nominal_step1_growth": source[0]["element"]["policy_step1_growth"],
        "variant_policy_nominal_step1_growth": experimental[0]["element"]["policy_step1_growth"],
        "original_curve_step_n_growth_cap": source[0]["base"][0]["configured_growth_cap"],
        "variant_curve_step_n_growth_cap": experimental[0]["base"][0]["configured_growth_cap"],
        "different_growth_component_targets": base_curve_changes,
        "different_final_curve_targets": output_target_changes,
        "different_actual_curve_point_counts": real_sample_count_changes,
        "different_effective_element_targets":
            effective_element_target_changes,
        "original_geometric_floor_strictly_dominant_count":
            geometric_floor_dominant,
        "original_priority_floor_strictly_dominant_count":
            priority_floor_dominant,
        "original_structural_clamp_count": structural_clamps,
        "actual_original_per_attempt_comparison": attempts,
        "no_accepted_native_epoch_inferred_from_raw_curve_budgets": True,
    }


def audit(original_dir: Path, trials_dir: Path) -> dict:
    models = {}
    for treatment in TREATMENTS:
        model = treatment.model
        receipt = json.loads(
            (original_dir / f"r2712-{model}-native-lineage-audit.json")
            .read_text(encoding="utf-8"))
        base_path = original_dir / f"r2718-{model}-original-native-generator-stderr.log"
        trial_path = (trials_dir / treatment.id /
                      "original-generator-stderr.log")
        trial_report = json.loads(
            (trials_dir / treatment.id / "treatment-report.json")
            .read_text(encoding="utf-8"))
        base_bytes, trial_bytes = base_path.read_bytes(), trial_path.read_bytes()
        require(receipt["original_model"] == model and
                receipt["r2718_original_stderr_sha256"] ==
                hashlib.sha256(base_bytes).hexdigest() and
                trial_report["source_model"] == model and
                trial_report["id"] == treatment.id and
                trial_report["original_stderr_sha256"] ==
                hashlib.sha256(trial_bytes).hexdigest() and
                trial_report["original_compiled_cpp_executable_sha256"] ==
                receipt["research_executable_sha256"] and
                trial_report["native_model_input_sha256"] ==
                receipt["real_model_input_sha256"],
                "r2725_source_cpp_stderr_or_executable_sha_mismatch")
        baseline = parse_effective_budgets(base_bytes, model)
        trial = parse_effective_budgets(trial_bytes, model)
        observation = summarize_source_trial(baseline, trial, model)
        observation["original_article_native_stderr_sha256"] = (
            hashlib.sha256(base_bytes).hexdigest())
        observation["variant_native_stderr_sha256"] = (
            hashlib.sha256(trial_bytes).hexdigest())
        observation["original_cpp_executable_sha256"] = (
            receipt["research_executable_sha256"])
        observation["original_source_model_input_sha256"] = (
            receipt["real_model_input_sha256"])
        observation["experiment_one_control_only"] = {
            "name": treatment.parameter,
            "source": treatment.original,
            "variant": treatment.treatment,
            "variant_intent_sha256":
                trial_report["single_factor_intent_sha256"],
        }
        observation["original_article_accepted_steps"] = [
            x["accepted_step"] for x in receipt["accepted_snapshots"]]
        observation["variant_accepted_steps"] = (
            trial_report["source_accepted_steps"])
        observation["original_has_two_independent_accepted_steps"] = (
            len(receipt["accepted_snapshots"]) >= 2)
        observation["variant_has_two_independent_accepted_steps"] = (
            len(trial_report["source_accepted_steps"]) >= 2)
        models[model] = observation
    return {
        "schema": REPORT_SCHEMA,
        "original_source": "GENERATOR_ADAPTIVE_SERIAL_CPP_REAL_SOURCE",
        "real_native_models": models,
        "individual_trials_not_pooled_as_an_epoch": True,
        "original_acceptance_policy_changed": False,
        "original_cpp_source_attestation_requires_original_byte_parity": True,
        "cross_epoch_native_descendants_qualified": False,
        "continuous_geometric_error_bound_qualified": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-directory", type=Path, required=True)
    parser.add_argument("--trials-directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.original_directory, args.trials_directory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as sink:
        sink.write((json.dumps(result, sort_keys=True, indent=2,
                               allow_nan=False) + "\n").encode("utf-8"))
    print("R2725_NATIVE_ACTUAL_EFFECTIVE_BUDGETS=" + json.dumps({
        model: {field: data[field] for field in (
            "real_original_attempts", "different_growth_component_targets",
            "different_final_curve_targets",
            "different_actual_curve_point_counts",
            "different_effective_element_targets",
            "original_geometric_floor_strictly_dominant_count",
            "original_priority_floor_strictly_dominant_count",
            "original_structural_clamp_count",
        )} for model, data in result["real_native_models"].items()},
        sort_keys=True))


if __name__ == "__main__":
    main()
