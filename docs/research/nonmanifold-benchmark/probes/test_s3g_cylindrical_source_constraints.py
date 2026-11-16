"""Directed S3.G source-cylinder and recomputed native support gates."""
from __future__ import annotations

from hashlib import sha256
import copy
import json
from pathlib import Path
import tempfile
import unittest

import cadquery as cq

from s3c_step_source_gate import SOURCES
from s3g_cylindrical_source_constraints import (
    native_support_crosscheck, recompute_audit, run_step, screen,
)


def _sha(value):
    return sha256(value.encode("utf-8")).hexdigest()


class OriginalCylinderSourceConstraintsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.tmp.name)
        cls.step = cls.folder / "half_cylinder.step"
        cylinder = cq.Workplane("XY").circle(3).extrude(4)
        box = cq.Workplane("XY").box(8, 4, 4, centered=(True, False, False))
        cq.exporters.export(cylinder.intersect(box).val(), str(cls.step))
        cls.raw = cls.step.read_text("utf-8")
        cls.sha = _sha(cls.raw)
        cls.native = cq.importers.importStep(str(cls.step)).val()
        cls.report = screen(cls.raw, model="SYNTHETIC", source_sha256=cls.sha)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_author_generated_source_rectangular_generator(self):
        p = self.report
        self.assertEqual(p["original_step_advanced_faces"], 4)
        self.assertEqual(p["source_planar_candidate_faces"], 1)
        self.assertEqual(p["source_planar_to_cylinder_generator_edges"], 2)
        self.assertEqual(p["source_adjacent_cylinder_faces"], 1)
        self.assertEqual(p["candidate_histogram"],
                         {"SOURCE_TWO_GENERATOR_RECTANGLE_CANDIDATE": 1})
        self.assertFalse(p["raw_step_source_distributed"])
        self.assertEqual(p["apmesh_tri_quad"], "NOT_RUN")

    def test_nonrational_generator_matches_cylinder_geometry(self):
        r = self.report["original_cylindrical_face_screens"][0]
        self.assertEqual(r["source_wire_edge_counts"], [4])
        self.assertEqual(r["source_master_curve_histogram"],
                         {"CIRCLE": 2, "LINE": 2})
        self.assertEqual(r["original_anchor_count"], 2)
        self.assertAlmostEqual(r["radius_mm"], 3)
        self.assertAlmostEqual(r["minimum_angular_separation_rad"], 3.141592653589793)
        self.assertEqual(r["minor_arc_lower_bound_on_quarter_turn_segments"], 2)
        self.assertEqual(r["anchored_axis_extent_difference_mm"], 0)
        for g in r["generator_checks"]:
            self.assertLess(g["maximum_endpoint_radial_residual_mm"], 1e-9)
            self.assertLess(g["axis_parallel_lateral_displacement_mm"], 1e-9)

    def test_two_original_anchor_edges_have_distinct_ids(self):
        r = self.report["original_cylindrical_face_screens"][0]
        self.assertEqual(len(set(r["anchored_original_edge_curve_ids"])), 2)
        self.assertEqual(set(r["anchored_original_edge_curve_ids"]),
                         {x["source_edge_curve_id"] for x in r["generator_checks"]})

    def test_source_geometry_report_recomputes(self):
        r = recompute_audit(self.raw, self.report, model="SYNTHETIC",
                            source_sha256=self.sha)
        self.assertTrue(r["audit_pass"])
        self.assertEqual(r["source_generator_edges_verified"], 2)
        self.assertEqual(r["native_source_brep_fit"], "NOT_RUN")

    def test_invalid_report_checksum_rejected(self):
        wrong = copy.deepcopy(self.report)
        wrong["candidate_histogram"]["SOURCE_TWO_GENERATOR_RECTANGLE_CANDIDATE"] = 999
        with self.assertRaisesRegex(ValueError, "checksum"):
            recompute_audit(self.raw, wrong, model="SYNTHETIC", source_sha256=self.sha)

    def test_forged_report_with_recomputed_checksum_rejected(self):
        from s3g_cylindrical_source_constraints import _checksum
        wrong = copy.deepcopy(self.report)
        wrong["original_cylindrical_face_screens"][0]["radius_mm"] = 400
        wrong.pop("report_sha256")
        wrong["report_sha256"] = _checksum(wrong)
        with self.assertRaisesRegex(ValueError, "disagrees with source recomputation"):
            recompute_audit(self.raw, wrong, model="SYNTHETIC", source_sha256=self.sha)

    def test_modified_source_with_stale_sha_rejected(self):
        changed = self.raw.replace("ISO-10303-21;", "ISO-10303-21;\n/* modified */", 1)
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            screen(changed, model="SYNTHETIC", source_sha256=self.sha)

    def test_radius_mutation_cannot_be_labeled_as_source_eligible(self):
        from s3c_step_source_gate import parse_entities, oriented_edges, refs
        t = parse_entities(self.raw)
        f = self.report["original_cylindrical_face_screens"][0]
        sid = f["source_cylindrical_support_entity_id"]
        line = next(line for line in self.raw.splitlines() if line.startswith(f"#{sid} = CYLINDRICAL_SURFACE("))
        changed = self.raw.replace(line, line.replace(",3.", ",3.5"), 1)
        self.assertNotEqual(changed, self.raw)
        report = screen(changed, model="SYNTHETIC", source_sha256=_sha(changed))
        excluded = report["original_cylindrical_face_screens"][0]
        self.assertIn("SOURCE_GENERATOR_AXIS_OR_RADIUS_INCONSISTENCY", excluded["exclusion_reasons"])
        self.assertEqual(excluded["classification"], "SOURCE_ONLY_TRIM_RECONSTRUCTION_REQUIRED")

    def test_six_face_box_has_no_cylinder(self):
        path = self.folder / "box.step"
        cq.exporters.export(cq.Workplane("XY").box(2, 3, 4).val(), str(path))
        source = path.read_text()
        report = screen(source, model="SYNTHETIC", source_sha256=_sha(source))
        self.assertEqual(report["source_planar_to_cylinder_generator_edges"], 0)
        self.assertEqual(report["source_adjacent_cylinder_faces"], 0)
        self.assertEqual(report["candidate_histogram"], {})

    def test_native_cylindrical_support_on_author_control(self):
        result = native_support_crosscheck(self.raw, self.native, model="SYNTHETIC",
                                           source_sha256=self.sha)
        self.assertTrue(result["s3f_first_ring_audit_pass"])
        self.assertEqual(result["native_cylindrical_source_face_ids_checked"], 1)
        cyl = result["original_cylindrical_faces"][0]
        self.assertEqual(cyl["original_edge_anchor_count"], 2)
        self.assertEqual(cyl["radius_residual_mm"], 0)
        self.assertEqual(cyl["axis_line_separation_mm"], 0)
        self.assertFalse(cyl["native_trim_parameter_interval_certified"])

    def test_original_source_support_mutation_is_rejected_by_native_oracle(self):
        record = self.report["original_cylindrical_face_screens"][0]
        sid = record["source_cylindrical_support_entity_id"]
        line = next(line for line in self.raw.splitlines() if line.startswith(f"#{sid} = CYLINDRICAL_SURFACE("))
        changed = self.raw.replace(line, line.replace(",3.", ",3.5"), 1)
        with self.assertRaisesRegex(ValueError, "cylindrical support mismatch"):
            native_support_crosscheck(changed, self.native, model="SYNTHETIC",
                                      source_sha256=_sha(changed))

    def test_cli_native_gate_and_source_only_are_explicit(self):
        dest = self.folder / "native_s3g.json"
        output = run_step(self.step, dest, model="SYNTHETIC",
                          expected_sha256=self.sha, native=True)
        self.assertTrue(dest.exists())
        self.assertIn("native_support_crosscheck", output)
        self.assertEqual(output["native_support_crosscheck"]["native_cylindrical_source_face_ids_checked"], 1)
        self.assertNotIn("original_cylinder_bp", output)
        source_only = run_step(self.step, self.folder / "source_s3g.json", model="SYNTHETIC",
                               expected_sha256=self.sha, native=False)
        self.assertNotIn("native_support_crosscheck", source_only)

    def test_wrong_expected_sha_yields_no_output(self):
        dest = self.folder / "must_not_exist.json"
        with self.assertRaisesRegex(ValueError, "Expected raw STEP SHA-256 mismatch"):
            run_step(self.step, dest, model="SYNTHETIC",
                     expected_sha256="0"*64, native=True)
        self.assertFalse(dest.exists())

    def test_original_model_rejects_synthetic_before_output(self):
        dest = self.folder / "invalid_m5.json"
        with self.assertRaisesRegex(ValueError, "Pinned original STEP SHA-256 mismatch"):
            run_step(self.step, dest, model="M5", native=True)
        self.assertFalse(dest.exists())

    def test_synthetic_source_without_expected_sha_rejected(self):
        with self.assertRaisesRegex(ValueError, "explicit expected SHA-256"):
            run_step(self.step, self.folder / "no_sha.json", model="SYNTHETIC", native=False)

    def test_m5_s40_originals_absent_and_cannot_fake_admission(self):
        for model in ("M5", "S40"):
            with self.subTest(model=model):
                with self.assertRaisesRegex(ValueError, "Pinned original STEP SHA-256 mismatch"):
                    screen(self.raw, model=model, source_sha256=self.sha)
        self.skipTest("Actual pinned M5/S40 original STEP bytes are not mounted locally")


if __name__ == "__main__":
    unittest.main()
