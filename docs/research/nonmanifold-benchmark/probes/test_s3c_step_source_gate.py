"""Directed original STEP identity and topology controls for the S3.C source gate."""
from __future__ import annotations

from hashlib import sha256
import re
import tempfile
from pathlib import Path
import unittest

import cadquery as cq

from s3c_step_source_gate import analyze, parse_entities, SOURCES


class S3COriginalSourceGraphTests(unittest.TestCase):
    @staticmethod
    def export(shape):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "model.step"
            cq.exporters.export(shape, str(path))
            raw = path.read_bytes()
            return raw.decode("utf8")

    @classmethod
    def setUpClass(cls):
        cls.cube = cls.export(cq.Workplane().box(2, 3, 4))

    def evaluate(self, source):
        return analyze(source, model="SYNTHETIC", source_sha256=sha256(source.encode()).hexdigest())

    def test_cube_six_planar_and_twelve_shared_edges(self):
        r = self.evaluate(self.cube)
        self.assertEqual(r["original_advanced_faces"], 6)
        self.assertEqual(r["candidate_faces"], 6)
        self.assertEqual(r["candidate_distinct_original_edges"], 12)
        self.assertEqual(r["candidate_edge_neighbors"], {"CANDIDATE_TO_CANDIDATE": 12})
        self.assertEqual(r["apmesh_generation"], "NOT_RUN")

    def test_exact_source_edge_identity_not_coordinate_welding(self):
        a = cq.Workplane().box(1, 1, 1).val()
        b = cq.Workplane().box(1, 1, 1).translate((1 + 1e-8, 0, 0)).val()
        compound = cq.Compound.makeCompound([a, b])
        r = self.evaluate(self.export(compound))
        self.assertEqual(r["candidate_faces"], 12)
        self.assertEqual(r["candidate_edge_neighbors"], {"CANDIDATE_TO_CANDIDATE": 24})
        self.assertEqual(r["candidate_distinct_original_edges"], 24)

    def test_cylinder_requires_nonplanar_and_nonquad_exclusions(self):
        r = self.evaluate(self.export(cq.Workplane().cylinder(4, 2)))
        self.assertEqual(r["candidate_faces"], 0)
        self.assertEqual(r["original_advanced_faces"], 3)
        self.assertGreater(r["other_face_dispositions"].get("NONPLANAR_SUPPORT", 0), 0)
        self.assertGreater(sum(r["other_face_dispositions"].values()), 0)

    def test_prism_preserves_only_true_quadrilaterals(self):
        shape = cq.Workplane().polyline([(0,0), (3,0), (1,2)]).close().extrude(1)
        r = self.evaluate(self.export(shape))
        self.assertEqual(r["original_advanced_faces"], 5)
        self.assertEqual(r["candidate_faces"], 3)
        self.assertEqual(r["other_face_dispositions"]["NOT_FOUR_SIDES"], 2)

    def test_reversed_single_oriented_edge_rejected(self):
        mutated, count = re.subn(r"(ORIENTED_EDGE\([^;]*?),\.T\.\);", r"\1,.F.);", self.cube, count=1)
        self.assertEqual(count, 1)
        r = self.evaluate(mutated)
        self.assertLess(r["candidate_faces"], 6)
        self.assertGreater(r["other_face_dispositions"].get("DISCONNECTED_ORIENTED_LOOP", 0), 0)

    def test_complex_rational_bspline_entity_is_classified_not_lost(self):
        plane = re.search(r"(#\d+)\s*=\s*PLANE\([^;]*;", self.cube)
        self.assertIsNotNone(plane)
        complex_surface = (plane[1] + " = ( BOUNDED_SURFACE() "
                           "B_SPLINE_SURFACE(1,2,()) "
                           "RATIONAL_B_SPLINE_SURFACE(((1.,0.8))) SURFACE() );")
        mutated = self.cube.replace(plane[0], complex_surface)
        report = self.evaluate(mutated)
        self.assertEqual(report["candidate_faces"], 5)
        self.assertEqual(report["source_face_support_histogram"]["COMPLEX_RATIONAL_B_SPLINE_SURFACE"], 1)

    def test_duplicate_entity_is_rejected(self):
        duplicate = re.search(r"#\d+\s*=\s*[^;]+;", self.cube)
        self.assertIsNotNone(duplicate)
        mutated = self.cube.replace("ENDSEC;", duplicate[0] + "\nENDSEC;", 1)
        with self.assertRaisesRegex(ValueError, "Duplicate entity"):
            parse_entities(mutated)

    def test_truncated_step_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "envelope"):
            parse_entities(self.cube.replace("END-ISO-10303-21;", ""))

    def test_face_graph_records_same_original_entity_not_sampled_proximity(self):
        r = self.evaluate(self.cube)
        identifiers = r["candidate_source_entity_graph"]
        self.assertEqual(len(set(x["source_advanced_face_id"] for x in identifiers)), 6)
        self.assertEqual(sum(len(x["source_edge_curve_ids"]) for x in identifiers), 24)
        self.assertEqual(r["scope"], "PINNED_STEP_SOURCE_GRAPH_NO_NATIVE_BREP_CONVERSION")
        self.assertFalse(r["source_original_file_admitted_for_redistribution"])

    def test_known_external_inputs_are_sha256_pinned(self):
        self.assertEqual(len(SOURCES), 4)
        for source in SOURCES.values():
            self.assertEqual(len(source[1]), 64)
            self.assertGreater(source[2], 0)
            self.assertGreater(source[3], 0)

    def test_full_source_execution_is_explicitly_skipped_when_unavailable(self):
        import os
        workspace = os.environ.get("APMESH_REAL_CAD_WORKSPACE")
        if not workspace:
            self.skipTest("Original pinned STEP bytes are not present; this is not a successful original import")
        for model, (filename, digest, face_count, candidate_count) in SOURCES.items():
            with self.subTest(model=model):
                data = (Path(workspace) / "sources" / filename).read_bytes()
                self.assertEqual(sha256(data).hexdigest(), digest)
                result = analyze(data.decode(), model=model, source_sha256=digest)
                self.assertEqual(result["original_advanced_faces"], face_count)
                self.assertEqual(result["candidate_faces"], candidate_count)


if __name__ == "__main__":
    unittest.main()
