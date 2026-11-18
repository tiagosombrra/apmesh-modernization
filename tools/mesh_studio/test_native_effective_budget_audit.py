"""R2.7.25 synthetic hostile contract tests; not accepted C++ geometry evidence."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.mesh_studio.native_effective_budget_audit import (
    BUDGET_SCHEMA, BASE_SCHEMA, FINAL_SCHEMA,
    parse_effective_budgets, summarize_source_trial,
)
from tools.mesh_studio.test_native_acceptance_gate_forensics import row
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def synthetic_cpp_budget_stderr(model: str = "eistute",
                                omit_last_curve: bool = False,
                                swap_final_retry: bool = False) -> bytes:
    """Create a source-shaped zero-evidence input for contract testing."""
    curves = 13 if model == "eistute" else 85
    pieces = [b"UNTRUSTED SYNTHETIC UNIT CONTRACT\n"]
    element = {
        "schema": BUDGET_SCHEMA, "scientific_lod_qualified": False,
        "step": 1, "retry": 0, "stable": model == "eistute",
        "configured_intensity": 0.02,
        "policy_step1_growth": 1.16,
        "step1_element_growth": 1.3,
        "step2_element_growth": 1.4,
        "step3_element_growth": 1.5,
        "budget_driven": 1, "element_target_mode": 1,
        "effective_growth": 1.3, "effective_target_elements": 120.0,
        "previous_elements": 90,
    }
    def log(prefix: bytes, source: dict):
        pieces.append(prefix + json.dumps(source, sort_keys=True).encode() + b"\n")
    log(b"R2725_ELEMENT_BUDGET=", element)
    for index in range(curves - int(omit_last_curve)):
        log(b"R2725_CURVE_BASE=", {
            "schema": BASE_SCHEMA, "scientific_lod_qualified": False,
            "step": 1, "retry": 0, "curve_index": index,
            "previous_points": 4, "budget_active": True,
            "configured_growth_cap": 4.0,
            "growth_target": 7, "priority_target": 9,
            "geometric_floor": 12, "priority_patch": True,
            "sensitive_curve": True, "pre_consistency_target": 12,
        })
    for index in range(curves):
        log(b"R2725_CURVE_FINAL=", {
            "schema": FINAL_SCHEMA, "scientific_lod_qualified": False,
            "step": 1, "retry": int(swap_final_retry and index == 0),
            "curve_index": index, "before_consistency": 12,
            "after_consistency": 11, "final_target": 11,
            "actual_points": 10, "structurally_clamped": True,
        })
    log(b"R2723_NATIVE_ACCEPTANCE_GATE=", row(1, True))
    return b"".join(pieces)


class NativeEffectiveBudgets(unittest.TestCase):
    def test_one_synthetic_attempt_is_not_an_accepted_lod(self):
        data = parse_effective_budgets(synthetic_cpp_budget_stderr(), "eistute")
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]["base"]), 13)
        self.assertEqual(len(data[0]["final"]), 13)
        comparison = summarize_source_trial(data, data, "eistute")
        self.assertEqual(comparison["different_actual_curve_point_counts"], 0)
        self.assertEqual(comparison["original_geometric_floor_strictly_dominant_count"], 13)
        self.assertEqual(comparison["original_structural_clamp_count"], 13)
        self.assertTrue(comparison["no_accepted_native_epoch_inferred_from_raw_curve_budgets"])

    def test_book_has_85_original_curves_not_13(self):
        data = parse_effective_budgets(synthetic_cpp_budget_stderr("book"), "book")
        self.assertEqual(len(data[0]["base"]), 85)
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "r2725_incomplete_original_curves"):
            parse_effective_budgets(synthetic_cpp_budget_stderr(), "book")

    def test_missing_original_curve_witness_refused(self):
        with self.assertRaises(NativeLineageValidationError):
            parse_effective_budgets(
                synthetic_cpp_budget_stderr(omit_last_curve=True), "eistute")

    def test_witness_from_different_native_retry_refused(self):
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "r2725_unscoped_or_cross_retry"):
            parse_effective_budgets(
                synthetic_cpp_budget_stderr(swap_final_retry=True), "eistute")

    def test_missing_native_precommit_gate_refused(self):
        data = synthetic_cpp_budget_stderr()
        data = b"\n".join(line for line in data.splitlines()
                          if not line.startswith(b"R2723_NATIVE_ACCEPTANCE_GATE="))
        with self.assertRaises(NativeLineageValidationError):
            parse_effective_budgets(data, "eistute")

    def test_duplicate_original_cpp_field_refused(self):
        data = synthetic_cpp_budget_stderr().replace(
            b'"step": 1, "step"', b'"step": 1, "step"')
        # Insert an actual duplicate rather than a no-op replacement.
        data = data.replace(b'"step": 1', b'"step": 1, "step": 1', 1)
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "r2725_duplicate_native_cpp_json_key"):
            parse_effective_budgets(data, "eistute")

    def test_forged_accepted_lod_flag_refused(self):
        data = synthetic_cpp_budget_stderr().replace(
            b'"scientific_lod_qualified": false',
            b'"scientific_lod_qualified": true', 1)
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "r2725_original_cpp_trace_schema"):
            parse_effective_budgets(data, "eistute")

    def test_nonfinite_native_real_budget_rejected(self):
        data = synthetic_cpp_budget_stderr().replace(
            b'"effective_growth": 1.3',
            b'"effective_growth": NaN', 1)
        with self.assertRaisesRegex(ValueError,
                                    "r2725_invalid_original_cpp_budget_json"):
            parse_effective_budgets(data, "eistute")

    def test_negative_budget_curve_target_is_not_valid_cpp(self):
        data = synthetic_cpp_budget_stderr().replace(
            b'"growth_target": 7',
            b'"growth_target": -7', 1)
        with self.assertRaises(NativeLineageValidationError):
            parse_effective_budgets(data, "eistute")

    def test_two_different_original_attempt_chronologies_not_combined(self):
        source = parse_effective_budgets(synthetic_cpp_budget_stderr(), "eistute")
        trial = deepcopy(source)
        trial[0]["retry"] = 1
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "r2725_original_and_trial_different"):
            summarize_source_trial(source, trial, "eistute")

    def test_changing_only_configured_cap_does_not_prove_real_geometry_changed(self):
        source = parse_effective_budgets(synthetic_cpp_budget_stderr(), "eistute")
        trial = deepcopy(source)
        for curve in trial[0]["base"]:
            curve["configured_growth_cap"] = 2.0
        summary = summarize_source_trial(source, trial, "eistute")
        self.assertEqual(summary["different_growth_component_targets"], 0)
        self.assertEqual(summary["different_final_curve_targets"], 0)
        self.assertFalse("scientific_lod_qualified" in summary)


if __name__ == "__main__":
    unittest.main()
