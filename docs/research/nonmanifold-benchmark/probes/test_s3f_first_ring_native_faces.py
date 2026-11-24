"""Directed positive/negative controls for source-to-native first-ring face IDs."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

import cadquery as cq

from s3c_step_source_gate import SOURCES
from s3e_native_feature_bijection import correlate
from s3f_first_ring_native_faces import first_ring, recompute_audit, run_original


def half_cylinder():
    """Create an authored manifold solid with straight plane-cylinder seams."""
    cylinder = cq.Workplane("XY").circle(3).extrude(4)
    box = cq.Workplane("XY").box(8, 4, 4, centered=(True, False, False))
    return cylinder.intersect(box).val()


class FirstRingBijectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.step_path = cls.root / "half_cylinder.step"
        cq.exporters.export(half_cylinder(), str(cls.step_path))
        cls.step = cls.step_path.read_text(encoding="utf-8")
        cls.digest = sha256(cls.step_path.read_bytes()).hexdigest()
        cls.native = cq.importers.importStep(str(cls.step_path)).val()
        cls.certificate = correlate(cls.step, cls.native, model="SYNTHETIC",
                                    source_sha256=cls.digest)
        cls.report = first_ring(cls.step, cls.native, cls.certificate,
                                model="SYNTHETIC", source_sha256=cls.digest)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_four_original_faces_accounted_for_without_mesh_claim(self):
        r = self.report
        self.assertEqual(r["source_faces"], 4)
        self.assertEqual(r["candidate_faces_verified"], 1)
        self.assertEqual(r["excluded_source_faces_mapped_by_edge_identity"], 3)
        self.assertEqual(r["distinct_original_first_ring_edge_anchors"], 4)
        self.assertEqual(r["mapped_first_ring_source_face_ids"], 4)
        self.assertEqual(r["remaining_unmapped_source_faces"], 0)
        self.assertEqual(r["complete_original_face_geometry_correspondence"], "NOT_ESTABLISHED")
        self.assertEqual(r["accepted_apmesh_tri_or_quad"], "NOT_RUN")

    def test_cylinder_references_the_same_two_original_edges(self):
        cylindrical = [x for x in self.report["excluded_face_mapping"]
                       if x["native_support_type"] == "CYLINDER"]
        self.assertEqual(len(cylindrical), 1)
        self.assertEqual(cylindrical[0]["original_edge_anchor_count"], 2)
        self.assertEqual(len({a["native_neighbor_face_index"] for a in
                              cylindrical[0]["original_edge_anchors"]}), 1)
        self.assertEqual(self.report["neighbor_support_histogram"],
                         {"CYLINDER": 1, "PLANE": 2})
        self.assertFalse(cylindrical[0]["all_neighbor_edges_mapped"])
        self.assertFalse(cylindrical[0]["curved_surface_geometry_audited"])

    def test_first_ring_injectivity_and_multiple_source_anchors(self):
        r = self.report
        source_ids = [x["source_advanced_face_id"] for x in r["excluded_face_mapping"]]
        native_ids = [x["native_face_index"] for x in r["excluded_face_mapping"]]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertEqual(len(native_ids), len(set(native_ids)))
        self.assertEqual(sum(x["original_edge_anchor_count"]
                             for x in r["excluded_face_mapping"]), 4)

    def test_recomputed_original_native_audit(self):
        audit = recompute_audit(self.step, self.native, self.report,
                                model="SYNTHETIC", source_sha256=self.digest)
        self.assertTrue(audit["audit_pass"])
        self.assertEqual(audit["original_first_ring_edges_checked"], 4)
        self.assertEqual(audit["excluded_source_face_id_bindings_checked"], 3)

    def test_run_original_writes_only_after_gate(self):
        out = self.root / "s3f_valid"
        result = run_original(self.step_path, out, model="SYNTHETIC",
                              expected_sha256=self.digest)
        self.assertEqual(result["excluded_source_faces_mapped_by_edge_identity"], 3)
        self.assertEqual(sorted(x.name for x in out.iterdir()), [
            "s3e_native_certificate.json", "s3e_recomputed_audit.json",
            "s3f_first_ring_faces.json", "s3f_recomputed_audit.json"])

    def test_six_face_box_has_zero_excluded_neighbor_faces(self):
        path = self.root / "box.step"
        cq.exporters.export(cq.Workplane("XY").box(2, 3, 4), str(path))
        digest = sha256(path.read_bytes()).hexdigest()
        raw = path.read_text()
        native = cq.importers.importStep(str(path)).val()
        cert = correlate(raw, native, model="BOX", source_sha256=digest)
        report = first_ring(raw, native, cert, model="BOX", source_sha256=digest)
        self.assertEqual(report["candidate_faces_verified"], 6)
        self.assertEqual(report["excluded_source_faces_mapped_by_edge_identity"], 0)
        self.assertEqual(report["remaining_unmapped_source_faces"], 0)
        self.assertTrue(recompute_audit(raw, native, report, model="BOX",
                                        source_sha256=digest)["audit_pass"])

    def test_changed_source_step_text_does_not_preserve_bijection(self):
        modified = self.step.replace("ISO-10303-21;", "ISO-10303-21;\n/* mutation */", 1)
        with self.assertRaisesRegex(ValueError, "STEP source raw SHA-256 mismatch"):
            first_ring(modified, self.native, self.certificate,
                       model="SYNTHETIC", source_sha256=self.digest)

    def test_forged_anchor_even_with_forged_checksum_rejected(self):
        forged = json.loads(json.dumps(self.report))
        forged["excluded_face_mapping"][0]["original_edge_anchors"][0]["native_edge_index"] += 1
        forged.pop("report_sha256")
        from s3f_first_ring_native_faces import _checksum
        forged["report_sha256"] = _checksum(forged)
        with self.assertRaisesRegex(ValueError, "records differ"):
            recompute_audit(self.step, self.native, forged,
                            model="SYNTHETIC", source_sha256=self.digest)

    def test_corrupted_report_checksum_rejected(self):
        wrong = json.loads(json.dumps(self.report))
        wrong["neighbor_support_histogram"]["CYLINDER"] = 2
        with self.assertRaisesRegex(ValueError, "report checksum"):
            recompute_audit(self.step, self.native, wrong,
                            model="SYNTHETIC", source_sha256=self.digest)

    def test_native_transform_rejected_even_with_authentic_step(self):
        moved = self.native.translate((.1, 0, 0))
        with self.assertRaises(ValueError):
            first_ring(self.step, moved, self.certificate,
                       model="SYNTHETIC", source_sha256=self.digest)

    def test_m5_mismatch_fails_without_emitting_pretend_evidence(self):
        dest = self.root / "m5_invalid"
        with self.assertRaisesRegex(ValueError, "Pinned original STEP raw SHA-256 mismatch"):
            run_original(self.step_path, dest, model="M5")
        self.assertFalse(dest.exists())

    def test_s40_mismatch_fails_without_emitting_pretend_evidence(self):
        dest = self.root / "s40_invalid"
        with self.assertRaisesRegex(ValueError, "Pinned original STEP raw SHA-256 mismatch"):
            run_original(self.step_path, dest, model="S40")
        self.assertFalse(dest.exists())

    def test_original_step_bytes_required_for_original_native_evidence(self):
        import os
        source = self.root / SOURCES['M5'][0]
        if source.exists():
            self.fail('Synthetic fixture path unexpectedly contains M5 original')
        folder=Path(os.getenv('APMESH_MAMBO_SOURCE_DIR','/external/mambo/sources'))
        if not all((folder/SOURCES[m][0]).is_file() for m in ('M5','S40')):
            self.skipTest('Original industrial M5/S40 STEP files absent')
        for model,neighbors in (('M5',7),('S40',18)):
            with self.subTest(model=model):
                name,digest,_,_=SOURCES[model]
                self.assertEqual(sha256((folder/name).read_bytes()).hexdigest(),digest)
                result=run_original(folder/name,self.root/('real_'+model),model=model)
                self.assertEqual(result['excluded_source_faces_mapped_by_edge_identity'],neighbors)


if __name__ == "__main__":
    unittest.main()
