"""Hermetic negative controls for non-manifold model admission statuses."""

import csv
import tempfile
import unittest
from pathlib import Path

from nonmanifold_v3_roster_gate import COLUMNS, validate_roster


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "MODEL_ROSTER_NONMANIFOLD_V3.csv"


class ModelRoleGateTests(unittest.TestCase):
    def setUp(self):
        with ROSTER.open(encoding="utf-8", newline="") as stream:
            self.rows = list(csv.DictReader(stream))

    def modified(self, model, **changes):
        rows = [dict(row) for row in self.rows]
        for row in rows:
            if row["model_id"] == model:
                row.update(changes)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "roster.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=COLUMNS)
                writer.writeheader()
                writer.writerows(rows)
            return validate_roster(path)

    def assert_rejected(self, model, **changes):
        with self.assertRaises(ValueError):
            self.modified(model, **changes)

    def test_01_published_snapshot_passes(self):
        report = validate_roster(ROSTER)
        self.assertEqual(report["top_priority"], "FOUR_SHEET_CURVED")
        self.assertFalse(report["manifold_s40_admitted_as_positive"])

    def test_02_s40_cannot_claim_original_nonmanifold(self):
        self.assert_rejected("S40", original_source_edge_incidence_ge3="yes")

    def test_03_s40_cannot_gain_three_source_sheets(self):
        self.assert_rejected("S40", verified_multisheet_incidence="3")

    def test_04_s40_cannot_lose_partial_atlas_status(self):
        self.assert_rejected("S40", bezier_atlas_state="COMPLETE")

    def test_05_stl_control_cannot_claim_multisheet(self):
        self.assert_rejected("THINGI10K_293137", verified_multisheet_incidence="4")

    def test_06_tsh249_cannot_claim_original_external_nonmanifold(self):
        self.assert_rejected("TSH249_POST_SEWING", original_source_edge_incidence_ge3="yes")

    def test_07_tsh249_cannot_claim_complete_atlas(self):
        self.assert_rejected("TSH249_POST_SEWING", bezier_atlas_state="COMPLETE")

    def test_08_curved_cannot_claim_native_tri_without_evidence(self):
        self.assert_rejected("FOUR_SHEET_CURVED", native_apmesh_tri_state="ACCEPTED")

    def test_09_curved_must_retain_four_incident_sheets(self):
        self.assert_rejected("FOUR_SHEET_CURVED", verified_multisheet_incidence="2")

    def test_10_original_external_cannot_claim_positive_source(self):
        self.assert_rejected("ORIGINAL_EXTERNAL_MULTISHEET", original_source_edge_incidence_ge3="yes")

    def test_11_original_external_cannot_claim_native_tri(self):
        self.assert_rejected("ORIGINAL_EXTERNAL_MULTISHEET", native_apmesh_tri_state="ACCEPTED")

    def test_12_historical_model_cannot_be_promoted(self):
        self.assert_rejected("BOOK", priority="P0-1")

    def test_13_original_native_thingi_tri_count_locked(self):
        self.assert_rejected("THINGI10K_293137", native_apmesh_tri_state="ACCEPTED_TRI_5000")

    def test_14_empty_model_id_rejected(self):
        self.assert_rejected("S40", model_id="")

    def test_15_duplicate_id_rejected(self):
        self.assert_rejected("M5", model_id="S40")

    def test_16_negative_incidence_rejected(self):
        self.assert_rejected("TSH249_POST_SEWING", verified_multisheet_incidence="-1")

    def test_17_false_positive_role_on_manifold_rejected(self):
        self.assert_rejected("M5", role="PRIMARY_NONMANIFOLD_CONTROL")

    def test_18_readme_and_plan_text_linked(self):
        plan = (ROOT / "PLAN_NONMANIFOLD_FIRST_V3.md").read_text(encoding="utf-8")
        self.assertIn("## 4. Plano de entregas", plan)
        self.assertIn("## 5. Critérios de aceite", plan)
        self.assertIn("`NATIVE_TRI_ACCEPTED`", plan)
        self.assertIn("**Ainda nenhum caso N3 qualificado.**", plan)


    def test_19_s40_coordinated_reclassification_is_rejected(self):
        self.assert_rejected("S40", origin_class="N1_AUTHORED", priority="P0-1",
                             role="PRIMARY_NONMANIFOLD_CONTROL", original_source_edge_incidence_ge3="authored",
                             verified_multisheet_incidence="4")

    def test_20_unknown_origin_rejected(self):
        self.assert_rejected("M5", origin_class="UNREVIEWED")

    def test_21_secondary_native_acceptance_needs_evidence(self):
        self.assert_rejected("FOUR_SHEET_PLANAR", native_apmesh_tri_state="ACCEPTED")

    def test_22_tsh249_native_acceptance_needs_evidence(self):
        self.assert_rejected("TSH249_POST_SEWING", native_apmesh_tri_state="ACCEPTED")

    def test_23_tsh249_cannot_promote_source_state(self):
        self.assert_rejected("TSH249_POST_SEWING", source_geometry_state="ORIGINAL_MULTISHEET_VERIFIED")

    def test_24_secondary_atlas_claim_requires_evidence(self):
        self.assert_rejected("CROSS_JUNCTION", bezier_atlas_state="COMPLETE")

    def test_25_unknown_model_rejected(self):
        self.assert_rejected("CROSS_JUNCTION", model_id="NEW_UNVERIFIED")

    def test_26_historical_role_cannot_be_promoted(self):
        self.assert_rejected("BOOK", role="PRIMARY_NONMANIFOLD_CONTROL")

    def test_27_m5_atlas_status_is_frozen(self):
        self.assert_rejected("M5", bezier_atlas_state="COMPLETE")

    def test_28_curved_source_status_is_frozen(self):
        self.assert_rejected("FOUR_SHEET_CURVED", source_geometry_state="SOURCE_EXTERNAL")

    def test_29_n3_cannot_claim_discovered_source(self):
        self.assert_rejected("ORIGINAL_EXTERNAL_MULTISHEET", source_geometry_state="SOURCE_AUTHENTICATED")

    def test_30_duplicate_primary_priority_rejected(self):
        self.assert_rejected("FOUR_SHEET_PLANAR", priority="P0-1")

    def test_31_overlong_csv_record_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "roster.csv"
            lines = ROSTER.read_text(encoding="utf-8").splitlines()
            lines[1] += ",unexpected"
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_roster(path)

    def test_32_missing_secondary_model_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "roster.csv"
            lines = ROSTER.read_text(encoding="utf-8").splitlines()
            path.write_text("\n".join(line for line in lines if not line.startswith("T_JUNCTION,")) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_roster(path)

if __name__ == "__main__":
    unittest.main()
