"""Negative provenance and acceptance-gate tests for original research artifacts.

All negative fixtures are in-memory or temporary copies, not new generator runs.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from tools.mesh_studio.source_epoch_inventory import (
    SourceEpochInventoryError,
    audit_eistute_reference,
    audit_r28_gate,
    build_source_epoch_inventory,
    SOURCE_REPORT_SHA256,
    EXPECTED_ARCHIVED_TRI,
    EISTUTE_SHA256,
    HISTORIC_EISTUTE_MANIFEST_SHA256,
)

ROOT = Path(__file__).resolve().parents[2]


class TestScientificSourceEpochInventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Recompute all five real-source Bernstein/UV/XYZ studies once.
        cls.inventory = build_source_epoch_inventory(ROOT)

    def test_original_artifacts_and_single_experiment_are_pinned(self) -> None:
        report = self.inventory
        self.assertEqual(report["source_experiments"], 1)
        self.assertEqual(report["accepted_adaptive_epochs"], 0)
        self.assertEqual(report["source_provenance"]["generator_report_sha256"],
                         SOURCE_REPORT_SHA256)
        self.assertEqual([item["name"] for item in report["source_objects"]],
                         ["control", "band", "west", "north", "both"])
        self.assertEqual(
            [item["elements"] for item in report["source_objects"]],
            [78, 106, 125, 125, 134],
        )
        self.assertEqual([item["state"] for item in report["source_objects"]],
                         ["CONTROLLED_NONADAPTIVE_OUTPUT"] +
                         ["STAGED_UNACCEPTED"] * 4)
        self.assertTrue(all(item["source_grid_sites"] == 4096
                            for item in report["source_objects"]))
        self.assertTrue(all(item["accepted_adaptive_epoch"] is None
                            for item in report["source_objects"]))

    def test_archived_eistute_is_identified_but_never_accepted(self) -> None:
        archive = self.inventory["legacy_archive"]
        self.assertEqual(archive["file_sha256"], EISTUTE_SHA256)
        self.assertEqual(archive["triangles"], EXPECTED_ARCHIVED_TRI)
        self.assertEqual(archive["vertices"], 3691)
        self.assertEqual(archive["historic_manifest_sha256"],
                         HISTORIC_EISTUTE_MANIFEST_SHA256)
        self.assertFalse(archive["historical_manifest_matches_file"])
        self.assertFalse(archive["adaptive_acceptance_verified"])
        self.assertFalse(archive["per_face_original_generator_id_verified"])
        self.assertEqual(archive["obj_face_index_semantics"],
                         "ORDINAL_IN_OBJ_NOT_GENERATOR_FACE_ID")

    def test_r28_rejected_with_missing_scientific_lineage(self) -> None:
        gate = self.inventory["r28_gate"]
        self.assertFalse(gate["eligible_for_r28_lod"])
        self.assertEqual(len(gate["blocking_evidence"]), 5)
        self.assertIn("NO_NATIVE_EPOCH_TRACE_AND_DECISION_ORACLE",
                      gate["blocking_evidence"])

    def test_no_promotion_of_staged_candidate(self) -> None:
        corrupted = deepcopy(self.inventory)
        corrupted["source_objects"][1]["state"] = "ACCEPTED_ADAPTIVE_EPOCH"
        with self.assertRaisesRegex(SourceEpochInventoryError,
                                    "unverified_candidate_promotion_band"):
            audit_r28_gate(corrupted)

    def test_reject_claim_of_accepted_epochs_or_more_runs(self) -> None:
        for field, new, expected in (
            ("accepted_adaptive_epochs", 1, "unverified_adaptive_epoch_claim"),
            ("source_experiments", 5, "unverified_independent_runs"),
        ):
            fake = deepcopy(self.inventory)
            fake[field] = new
            with self.subTest(field=field):
                with self.assertRaisesRegex(SourceEpochInventoryError, expected):
                    audit_r28_gate(fake)

    def test_reject_unverified_source_face_id_and_missing_oracle(self) -> None:
        fake = deepcopy(self.inventory)
        fake["legacy_archive"]["per_face_original_generator_id_verified"] = True
        with self.assertRaisesRegex(SourceEpochInventoryError,
                                    "unverified_legacy_source_promotion"):
            audit_r28_gate(fake)
        fake = deepcopy(self.inventory)
        fake["scientific_evidence"]["continuous_source_error_bound_verified"] = True
        with self.assertRaisesRegex(SourceEpochInventoryError,
                                    "unsupported_scientific_evidence_assertion"):
            audit_r28_gate(fake)
        fake = deepcopy(self.inventory)
        fake["source_objects"][4]["accepted_adaptive_epoch"] = 2
        with self.assertRaisesRegex(SourceEpochInventoryError,
                                    "candidate_promoted_to_adaptive_epoch_both"):
            audit_r28_gate(fake)

    def test_archived_obj_is_exact_byte_pinned(self) -> None:
        # Mutate only a temporary copy of legacy OBJ, never the source corpus.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "reference"
            archive.mkdir()
            for source_name in ("eistute_stage4.obj",
                                "eistute_stage4.json", "eistute_metrics.csv"):
                shutil.copyfile(ROOT / "reference" / source_name,
                                archive / source_name)
            shutil.copyfile(ROOT / "MANIFEST.sha256",
                            root / "MANIFEST.sha256")
            original = archive / "eistute_stage4.obj"
            data = original.read_bytes()
            self.assertGreater(len(data), 100_000)
            original.write_bytes(data.replace(b"# step 4", b"# step 5", 1))
            with self.assertRaisesRegex(SourceEpochInventoryError,
                                        "eistute_reference_sha256_mismatch"):
                audit_eistute_reference(root)

    def test_read_only_report_determinism(self) -> None:
        # Re-running the final admission policy cannot mutate an inventory.
        before = json.dumps(self.inventory, sort_keys=True)
        first = audit_r28_gate(self.inventory)
        second = audit_r28_gate(self.inventory)
        self.assertEqual(first, second)
        self.assertEqual(before, json.dumps(self.inventory, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
