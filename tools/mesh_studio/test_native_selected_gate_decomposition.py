"""Synthetic-only negative tests; these are NOT native Eistute measurements."""

from __future__ import annotations

from copy import deepcopy
import math
import unittest

from tools.mesh_studio.native_local_selection_provenance import (
    join_selected_local_to_native_csv,
)
from tools.mesh_studio.native_selected_gate_decomposition import (
    summarize_selected_step4,
)
from tools.mesh_studio.test_native_local_selection_provenance import (
    fake_complete_cpp_and_csv,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def fake_selected():
    """Use a deliberately artificial 40-Adapter-return synthetic fixture."""
    stdout, csv = fake_complete_cpp_and_csv("original")
    return join_selected_local_to_native_csv(
        stdout, csv, "original")["selected_local_returns"]


class SelectedSourceGateSyntheticTests(unittest.TestCase):
    def test_synthetic_fixture_is_never_a_native_acceptance_claim(self):
        result = summarize_selected_step4(fake_selected())
        self.assertEqual(result["selected_original_cpp_local_returns_step4"], 16)
        self.assertEqual(result["selected_source_cpp_step4_underresolved"], 16)
        self.assertFalse(result["scientific_lod_qualified"])
        self.assertTrue(result["not_independent_statistical_samples"])

    def test_selected_source_gate_deficits_are_in_unit_fractions(self):
        result = summarize_selected_step4(fake_selected())
        metrics = result["selected_local_metrics"]
        self.assertAlmostEqual(
            metrics["aft_shape_floor_shortfall"]["arithmetic_mean"], 0.1)
        self.assertAlmostEqual(
            metrics["interior_dominance_margin_over_0_66"][
                "arithmetic_mean"], 0.04)
        self.assertAlmostEqual(
            metrics["regional_minus_aft_shape_fraction"][
                "arithmetic_mean"], 0.4)
        self.assertEqual(
            result["regional_at_or_above_original_floor_descriptive_count"], 16)

    def test_all_four_patch_slots_are_required(self):
        selected = fake_selected()
        for row in selected:
            if row["step"] == 4 and row["patch"] == 3:
                row["patch"] = 2
        with self.assertRaises(NativeLineageValidationError):
            summarize_selected_step4(selected)

    def test_refuse_one_missing_selected_native_return(self):
        with self.assertRaises(NativeLineageValidationError):
            summarize_selected_step4(fake_selected()[:-1])

    def test_refuse_duplicate_adapter_return_chronology(self):
        selected = fake_selected()
        selected[-1]["adapter_return_index"] = 1
        with self.assertRaises(NativeLineageValidationError):
            summarize_selected_step4(selected)

    def test_refuse_false_selected_underresolution_flag(self):
        selected = fake_selected()
        next(x for x in selected if x["step"] == 4)[
            "transition_underresolved"] = False
        with self.assertRaises(NativeLineageValidationError):
            summarize_selected_step4(selected)

    def test_refuse_changed_selected_generation_status(self):
        selected = fake_selected()
        next(x for x in selected if x["step"] == 4)[
            "local_status"] = "success"
        with self.assertRaises(NativeLineageValidationError):
            summarize_selected_step4(selected)

    def test_refuse_changed_original_aft_gate_floor(self):
        selected = fake_selected()
        next(x for x in selected if x["step"] == 4)[
            "original_transition_floor"] = 0.05
        with self.assertRaises(NativeLineageValidationError):
            summarize_selected_step4(selected)

    def test_refuse_non_dominant_original_interior_fraction(self):
        selected = fake_selected()
        next(x for x in selected if x["step"] == 4)[
            "internal_element_ratio"] = 0.65
        with self.assertRaises(NativeLineageValidationError):
            summarize_selected_step4(selected)

    def test_refuse_nonfinite_and_nonunit_shape_metrics(self):
        for invalid in (math.nan, math.inf, -0.1, 1.01):
            selected = fake_selected()
            next(x for x in selected if x["step"] == 4)[
                "aft_stage1_transition_ratio"] = invalid
            with self.subTest(invalid=invalid):
                with self.assertRaises(NativeLineageValidationError):
                    summarize_selected_step4(selected)

    def test_independent_regional_metric_below_floor_is_allowed(self):
        selected = deepcopy(fake_selected())
        for row in selected:
            if row["step"] == 4:
                row["regional_spatial_or_shape_ratio"] = 0.05
        result = summarize_selected_step4(selected)
        self.assertEqual(
            result["regional_at_or_above_original_floor_descriptive_count"], 0)
        self.assertTrue(
            result["separately_defined_regional_fraction_not_substituted_for_aft"])

    def test_selected_local_must_not_be_promoted_to_native_commit(self):
        selected = fake_selected()
        next(x for x in selected if x["step"] == 4)[
            "local_selected_is_not_global_accepted_tri"] = False
        with self.assertRaises(NativeLineageValidationError):
            summarize_selected_step4(selected)


if __name__ == "__main__":
    unittest.main()
