"""R2.7.11 mutation checks for pinned original TRI native outcome bridge."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import unittest

from tools.mesh_studio.native_epoch_bridge import (
    NativeEpochBridgeError,
    R2C13,
    R2C14,
    OUTCOME,
    SOURCE,
    audit_archived_r2c13,
    audit_archived_r2c14,
    audit_native_source,
    build_native_epoch_bridge,
)

ROOT = Path(__file__).resolve().parents[2]


class NativeEpochBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bridge = build_native_epoch_bridge(ROOT)
        cls.r2c13 = json.loads((ROOT / R2C13).read_text(encoding="utf-8"))
        cls.r2c14 = json.loads((ROOT / R2C14).read_text(encoding="utf-8"))
        cls.source = (ROOT / SOURCE).read_text(encoding="utf-8")
        cls.outcome = (ROOT / OUTCOME).read_text(encoding="utf-8")

    def test_true_one_accepted_epoch_per_original_tri_model(self) -> None:
        report = self.bridge
        self.assertEqual(report["schema"],
                         "apmesh.meshstudio.r2711.native_epoch_evidence_bridge.v1")
        self.assertEqual(set(report["original_models"]), {"eistute", "book"})
        e = report["original_models"]["eistute"]
        b = report["original_models"]["book"]
        self.assertEqual(e["archived_committed_steps"], [1])
        self.assertEqual(b["archived_committed_steps"], [1])
        self.assertEqual((e["original_source_patches"], b["original_source_patches"]),
                         (4, 28))
        self.assertEqual((e["original_source_curves"], b["original_source_curves"]),
                         (13, 85))
        self.assertEqual((e["archived_rejected_restored_count"],
                          b["archived_rejected_restored_count"]), (3, 2))
        self.assertFalse(report["qualification"]["original_tri_two_accepted_epochs_per_model"])
        self.assertFalse(report["qualification"]["new_native_execution_in_this_run"])
        self.assertFalse(report["qualification"]["scientific_r28_geometry_lod_admitted"])

    def test_bezier_source_candidates_are_not_original_tri_accepted_epochs(self) -> None:
        sources = self.bridge["other_experiment_not_conflated"]
        self.assertEqual(sources["bezier_p2d1c3_source_experiments"], 1)
        self.assertEqual(sources["bezier_p2d1c3_accepted_adaptive_epochs"], 0)
        self.assertEqual(sources["eistute_stage4_reference"],
                         "SAVED_HISTORICAL_REJECTED_CANDIDATE")

    def test_original_native_commit_and_restore_hooks_pinned(self) -> None:
        code = self.bridge["source_code_lifecycle"]
        self.assertTrue(code["accepted_outcome_recorded_after_commit"])
        self.assertTrue(code["rejected_outcome_recorded_after_domain_and_curve_restoration"])
        self.assertEqual(code["event_log_capacity"], 128)

    def test_fake_second_commit_is_rejected(self) -> None:
        original = deepcopy(self.r2c13)
        original["measured_models"][0]["pinned_article"]["accepted_commits"] = 2
        with self.assertRaisesRegex(NativeEpochBridgeError,
                                    "native_accepted_epoch_overclaim_eistute"):
            audit_archived_r2c13(original)

    def test_unverified_source_revision_or_artifact_is_rejected(self) -> None:
        original = deepcopy(self.r2c13)
        original["pr_head"] = "0" * 40
        with self.assertRaisesRegex(NativeEpochBridgeError,
                                    "archived_source_run_identity_or_gate_changed"):
            audit_archived_r2c13(original)
        original = deepcopy(self.r2c13)
        original["native_execution_this_turn"]["artifact_id"] = 1
        with self.assertRaisesRegex(NativeEpochBridgeError,
                                    "native_r2c13_run_claim_changed"):
            audit_archived_r2c13(original)

    def test_missing_patch_curve_or_rejection_witness_is_rejected(self) -> None:
        original = deepcopy(self.r2c13)
        original["original_scenarios"][1]["curves"] = 84
        with self.assertRaisesRegex(NativeEpochBridgeError,
                                    "original_model_source_or_patch_curve_claim_changed_book"):
            audit_archived_r2c13(original)
        original = deepcopy(self.r2c13)
        original["measured_models"][0]["pinned_article"]["rejected_restored"] = 0
        with self.assertRaisesRegex(NativeEpochBridgeError,
                                    "native_accepted_epoch_overclaim_eistute"):
            audit_archived_r2c13(original)

    def test_forged_original_rejection_forensics_is_rejected(self) -> None:
        result = deepcopy(self.r2c14)
        result["measured_rejections"]["eistute"]["pinned"]["step4"]["growth"] = 1.0
        with self.assertRaisesRegex(NativeEpochBridgeError,
                                    "forensics_rejected_candidate_metrics_changed"):
            audit_archived_r2c14(result)
        result = deepcopy(self.r2c14)
        result["qualified_predecessor"]["actual_two_accepted_source_epochs"] = True
        with self.assertRaisesRegex(NativeEpochBridgeError,
                                    "forensics_run_lineage_changed"):
            audit_archived_r2c14(result)

    def test_changed_native_hook_sequence_is_rejected(self) -> None:
        broken = self.source.replace(
            "accepted_mesh = accepted_scope.Commit();",
            "accepted_mesh = nullptr;", 1)
        with self.assertRaisesRegex(NativeEpochBridgeError,
                                    "missing_native_acceptance_or_restore_anchor"):
            audit_native_source(broken, self.outcome)
        broken = self.source.replace(
            "GlobalOutcomeKind::RejectedStepRestored",
            "GlobalOutcomeKind::AcceptedStepCommitted", 1)
        with self.assertRaises(NativeEpochBridgeError):
            audit_native_source(broken, self.outcome)

    def test_changed_bounded_log_contract_is_rejected(self) -> None:
        broken = self.outcome.replace(
            "BoundedGlobalOutcomeLog<128>", "BoundedGlobalOutcomeLog<0>", 1)
        with self.assertRaisesRegex(NativeEpochBridgeError,
                                    "native_bounded_log_truncation_contract_changed"):
            audit_native_source(self.source, broken)

    def test_deterministic_json_receipt_with_no_new_native_scientific_claim(self) -> None:
        initial = json.dumps(self.bridge, sort_keys=True)
        self.assertEqual(initial, json.dumps(build_native_epoch_bridge(ROOT),
                                             sort_keys=True))
        self.assertFalse(self.bridge["qualification"]["continuous_error_bounds"])
        self.assertFalse(self.bridge["qualification"]
                         ["verified_shared_curve_multipatch_node_welding"])


if __name__ == "__main__":
    unittest.main()
