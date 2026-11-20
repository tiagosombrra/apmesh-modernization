"""Synthetic adversarial R2.7.27 gate contracts, never native experiment data."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from tools.mesh_studio.native_transition_coherence_audit import (
    attest_cpp_acceptance_source, diagnose_gate, infer_every_patch_flagged,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError

ROOT = Path(__file__).resolve().parents[2]


def step_gate(step=4, *, penalty=0.95, fraction=1.0,
              imbalance=0.06, coherent=False, ready=False,
              stable=True, retry=0):
    """Construct deliberately fake unit-test input, not C++ stderr."""
    return {
        "step": step, "retry": retry, "stable_mode": stable,
        "transition_coherence_penalty": penalty,
        "underresolved_transition_fraction": fraction,
        "transition_imbalance_max": imbalance,
        "transition_coherence_ok": coherent,
        "stable_transition_ready": ready,
    }


class OriginalTransitionGateContracts(unittest.TestCase):
    def test_exact_original_cpp_and_prior_protocol_attested(self):
        verified = attest_cpp_acceptance_source(ROOT)
        self.assertIn("src/generator/generator_adaptive.cpp", verified)
        self.assertIn(
            "docs/mesh-studio/R2_7_27_ORIGINAL_TRANSITION_COHERENCE_FORENSICS_PROTOCOL_20261118.md",
            verified)
        self.assertIn(
            "docs/mesh-studio/R2_7_27A_ORIGINAL_PATCH_COUNT_SEMANTICS_ADDENDUM_20261118.md",
            verified)

    def test_registered_step4_source_underresolution_is_decisive(self):
        record = diagnose_gate(step_gate())
        self.assertFalse(record["source_coherence_gate"])
        self.assertFalse(record["source_transition_ready"])
        self.assertEqual(record["coherence_cap"], 0.42)
        self.assertEqual(record["underresolved_fraction_cap"], 0.25)
        self.assertEqual(record["nonnegative_underresolved_penalty_lower_bound"], 0.55)
        self.assertIn("underresolution_term_alone_exceeds_coherence_cap",
                      record["necessary_bottleneck"])
        self.assertIn("actual_underresolved_fraction_exceeds_readiness_cap",
                      record["necessary_bottleneck"])

    def test_step1_coherence_is_bypassed_despite_large_penalty(self):
        record = diagnose_gate(step_gate(
            step=1, penalty=20, fraction=0, coherent=True, ready=True))
        self.assertTrue(record["coherence_rederived"])
        self.assertIsNone(record["coherence_cap"])

    def test_step3_uses_different_scientific_caps(self):
        record = diagnose_gate(step_gate(
            step=3, penalty=0.21, fraction=0,
            imbalance=0.02, coherent=True, ready=True))
        self.assertEqual(record["coherence_cap"], 0.25)
        self.assertEqual(record["underresolved_fraction_cap"], 0.10)
        self.assertEqual(record["imbalance_max_cap"], 0.12)

    def test_step2_unlogged_raw_patch_count_is_not_invented(self):
        record = diagnose_gate(step_gate(
            step=2, penalty=0.14, fraction=0, imbalance=0.08,
            coherent=False, ready=True))
        self.assertIsNone(record["coherence_rederived"])
        self.assertTrue(record["unobserved_step2_patch_count_not_inferred"])

    def test_step2_true_coherence_requires_visible_bounded_metrics(self):
        record = diagnose_gate(step_gate(
            step=2, penalty=0.14, fraction=0, imbalance=0.08,
            coherent=True, ready=True))
        self.assertTrue(record["source_coherence_gate"])
        bad = step_gate(
            step=2, penalty=0.14, fraction=0.10, imbalance=0.08,
            coherent=True, ready=True)
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2727_original_step2_necessary_coherence_violation"):
            diagnose_gate(bad)

    def test_book_nonstable_gate_bypass_not_as_eistute(self):
        record = diagnose_gate(step_gate(
            step=4, penalty=3.0, fraction=1.0, imbalance=0.5,
            coherent=True, ready=True, stable=False))
        self.assertIsNone(record["coherence_cap"])
        self.assertEqual(record["necessary_bottleneck"], [])

    def test_forged_step4_coherence_true_with_too_large_penalty_fails(self):
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2727_original_cpp_transition_coherence_gate_changed"):
            diagnose_gate(step_gate(coherent=True))

    def test_forged_transition_ready_true_with_fraction_one_fails(self):
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2727_source_transition_ready_predicate_changed"):
            diagnose_gate(step_gate(ready=True))

    def test_nonfinite_source_metric_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                        NativeLineageValidationError,
                        "r2727_nonfinite_source_transition_metric"):
                    diagnose_gate(step_gate(penalty=value))

    def test_underresolution_fraction_must_be_bounded(self):
        for fraction in (-0.01, 1.01):
            with self.subTest(value=fraction):
                with self.assertRaisesRegex(
                        NativeLineageValidationError,
                        "r2727_invalid_original_transition_metric_bounds"):
                    diagnose_gate(step_gate(fraction=fraction))

    def test_no_negative_penalty_components_claim_allowed(self):
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2727_original_cpp_nonnegative_penalty_components_violated"):
            diagnose_gate(step_gate(
                penalty=0.42, fraction=1.0, coherent=True, ready=False))

    def test_step4_large_imbalance_blocks_readiness_independently(self):
        record = diagnose_gate(step_gate(
            penalty=0.10, fraction=0, imbalance=0.30,
            coherent=True, ready=False))
        self.assertIn("actual_max_imbalance_exceeds_readiness_cap",
                      record["necessary_bottleneck"])
        self.assertNotIn(
            "underresolution_term_alone_exceeds_coherence_cap",
            record["necessary_bottleneck"])

    def test_invalid_source_field_types_not_tolerated(self):
        for key, invalid in (
            ("step", "4"), ("retry", True), ("stable_mode", 1),
            ("transition_coherence_ok", 1),
            ("stable_transition_ready", 0),
        ):
            with self.subTest(field=key):
                sample = step_gate()
                sample[key] = invalid
                with self.assertRaisesRegex(
                        NativeLineageValidationError,
                        "r2727_invalid_source_gate_scope_or_flags"):
                    diagnose_gate(sample)

    def test_absent_original_cpp_attestation_not_synthetic_success(self):
        with tempfile.TemporaryDirectory(prefix="r2727-fake-source-") as tmp:
            with self.assertRaises(FileNotFoundError):
                attest_cpp_acceptance_source(Path(tmp))


    def test_source_loop_proves_all_four_eistute_patch_flags(self):
        self.assertEqual(
            infer_every_patch_flagged(1.0, 4), [0, 1, 2, 3])

    def test_subunit_fraction_cannot_identify_all_patch_flags(self):
        for fraction in (0.0, 0.25, 0.75, 0.999999):
            with self.subTest(fraction=fraction):
                with self.assertRaisesRegex(
                        NativeLineageValidationError,
                        "r2727_partial_fraction_cannot_prove_all_source_patch_slots"):
                    infer_every_patch_flagged(fraction, 4)

    def test_patch_count_and_fraction_forgery_fail_closed(self):
        for patch_count in (0, -1, True, "4", 200):
            with self.subTest(count=patch_count):
                with self.assertRaisesRegex(
                        NativeLineageValidationError,
                        "r2727_partial_fraction_cannot_prove_all_source_patch_slots"):
                    infer_every_patch_flagged(1.0, patch_count)


if __name__ == "__main__":
    unittest.main()
