"""Bounded batch gate controls: never infer source admission from file absence."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

import cadquery as cq

from s3c_original_batch import run_batch, run_one


class OriginalBatchTests(unittest.TestCase):
    def test_original_source_absence_is_blocked_and_nonzero(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            result=run_batch(["M5", "S40"],root/"missing",root/"reports")
            self.assertFalse(result["all_requested_source_checks_completed"])
            self.assertEqual(result["models"]["M5"]["status"],"BLOCKED_MISSING_ORIGINAL_BYTES")
            self.assertEqual(result["models"]["S40"]["status"],"BLOCKED_MISSING_ORIGINAL_BYTES")
            self.assertEqual(result["complete_original_models_converted"],0)
            self.assertEqual(result["apmesh_tri_quad_generation"],"NOT_RUN")
            self.assertTrue((root/"reports"/"s3c_batch_summary.json").exists())

    def test_unpinned_synthetic_box_runs_all_three_distinct_oracles(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            step=root/"box.step"
            cq.exporters.export(cq.Workplane().box(2,3,4),str(step))
            digest=sha256(step.read_bytes()).hexdigest()
            report=run_one("SYNTHETIC_BOX",step,root/"output",expected_digest=digest,
                           expected_faces=6,expected_candidates=6,
                           provenance="LOCAL_TEST_CONTROL_NOT_EXTERNAL")
            self.assertEqual(report["status"],"PARTIAL_PLANAR_ATLAS_AUDITED")
            self.assertEqual(report["step_candidate_faces"],6)
            self.assertEqual(report["converted_faces"],6)
            self.assertEqual(report["candidate_edge_neighbors"]["CANDIDATE_TO_CANDIDATE"],12)
            self.assertEqual(report["independent_audit"]["validated_patches"],6)
            self.assertFalse(report["complete_original_model_converted"])
            self.assertEqual(report["native_to_source_face_id_bijection"],"NOT_ESTABLISHED")
            self.assertTrue((root/"output"/"synthetic_box"/"planar.partial.bp").exists())

    def test_mismatched_hash_aborts_before_any_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            step=root/"box.step"
            cq.exporters.export(cq.Workplane().box(1,2,3),str(step))
            with self.assertRaisesRegex(ValueError,"SHA-256 mismatch"):
                run_one("SYNTHETIC",step,root/"output",expected_digest="0"*64)
            self.assertFalse((root/"output").exists())

    def test_bad_source_inventory_rejects_success_status(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            step=root/"box.step"
            cq.exporters.export(cq.Workplane().box(1,2,3),str(step))
            digest=sha256(step.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError,"face inventory"):
                run_one("SYNTHETIC",step,root/"output",expected_digest=digest,
                        expected_faces=41,expected_candidates=6)

    def test_no_unearned_meshing_claim(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            r=run_batch(["M3"],root/"missing",root/"output")
            self.assertEqual(json.loads((root/"output"/"s3c_batch_summary.json").read_text())['models']['M3']['status'],"BLOCKED_MISSING_ORIGINAL_BYTES")
            self.assertEqual(r["apmesh_tri_quad_generation"],"NOT_RUN")


if __name__ == "__main__":
    unittest.main()
