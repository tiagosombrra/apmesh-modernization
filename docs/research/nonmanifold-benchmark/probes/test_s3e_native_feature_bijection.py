"""Native OCCT source-entity correspondence tests with stringent negative gates."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import cadquery as cq

from s3c_step_source_gate import SOURCES, analyze, coordinates, parse_entities, refs
from s3e_native_feature_bijection import (
    correlate, run_one, verify_certificate,
)


def half_cylinder():
    """A real four-faced BRep with two straight planar-cylinder interfaces."""
    solid = cq.Workplane("XY").circle(3).extrude(4)
    clipping = cq.Workplane("XY").box(8, 4, 4, centered=(True, False, False))
    return solid.intersect(clipping).val()


class S3ENativeCorrespondenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.source = cls.root / "half_cylinder.step"
        cq.exporters.export(half_cylinder(), str(cls.source))
        cls.raw = cls.source.read_bytes()
        cls.digest = sha256(cls.raw).hexdigest()
        cls.step = cls.raw.decode("utf-8")
        cls.native = cq.importers.importStep(str(cls.source)).val()
        cls.cert = correlate(cls.step, cls.native, model="HALF", source_sha256=cls.digest)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_exactly_two_planar_cylinder_and_two_planar_planar_interfaces(self):
        report = self.cert
        self.assertEqual(report["source_advanced_face_total"], 4)
        self.assertEqual(report["uniquely_mapped_source_candidate_faces"], 1)
        self.assertEqual(report["source_to_excluded_native_interfaces"], 4)
        self.assertEqual(report["source_to_excluded_native_cylinder_interfaces"], 2)
        self.assertEqual(report["native_neighbor_support_histogram"], {
            "CYLINDER": 2, "PLANE": 2,
        })
        self.assertEqual(len({r["native_edge_index"] for r in report["boundary_interfaces"]}), 4)
        self.assertEqual(report["full_original_source_native_face_bijection"], "NOT_ESTABLISHED")
        self.assertEqual(report["apmesh_generation"], "NOT_RUN")

    def test_nontrivial_source_id_to_native_id_certificate(self):
        report = verify_certificate(self.step, self.native, self.cert,
                                    model="HALF", source_sha256=self.digest)
        self.assertTrue(report["certificate_valid"])
        self.assertEqual(report["candidate_face_bindings_checked"], 1)
        self.assertEqual(report["original_boundary_interfaces_checked"], 4)
        self.assertFalse(report["complete_original_model_meshed"])

    def test_bp_partial_has_identical_native_source_edges(self):
        output = self.root / "s3e_output"
        report = run_one(self.source, output, model="HALF", expected_sha256=self.digest)
        self.assertEqual(report["status"], "LOCAL_PLANAR_AND_INTERFACE_CORRESPONDENCE_AUDITED")
        self.assertEqual(report["matched_cylinder_interfaces"], 2)
        self.assertFalse(report["source_neighbor_advanced_face_ids_verified"])
        self.assertTrue((output / "planar.partial.bp").exists())
        curve_audit = json.loads((output / "independent_source_curve_audit.json").read_text())
        self.assertEqual(curve_audit["source_edges_checked"], 4)
        self.assertEqual(curve_audit["source_topological_vertex_identity"], "CHECKED")
        result = json.loads((output / "independent_partial_bp_audit.json").read_text())
        self.assertEqual(result["validated_patches"], 1)
        self.assertEqual(result["excluded_source_faces"], 3)
        self.assertEqual(result["apmesh_accepted_mesh"], "NOT_RUN")

    def test_six_flat_box_faces_match_without_excluded_interfaces(self):
        box_path = self.root / "simple_box.step"
        cq.exporters.export(cq.Workplane("XY").box(2, 3, 4), str(box_path))
        raw = box_path.read_bytes()
        native = cq.importers.importStep(str(box_path)).val()
        matched = correlate(raw.decode(), native, model="BOX", source_sha256=sha256(raw).hexdigest())
        self.assertEqual(matched["uniquely_mapped_source_candidate_faces"], 6)
        self.assertEqual(matched["source_to_excluded_native_interfaces"], 0)
        self.assertEqual(matched["uniquely_mapped_source_side_edges"], 12)

    def test_reject_native_transform_that_breaks_source_geometry(self):
        moved = self.native.translate((0, 0, .01))
        with self.assertRaisesRegex(ValueError, "Ambiguous/missing source-to-native"):
            correlate(self.step, moved, model="HALF", source_sha256=self.digest)

    def test_reject_ambiguous_coincident_distinct_source_faces(self):
        # Two unrelated solids share geometry but not native identity.
        shape = cq.Workplane("XY").box(2, 3, 4).val()
        compound = cq.Compound.makeCompound([shape, shape.copy()])
        original = self.root / "coincident.step"
        cq.exporters.export(compound, str(original))
        raw = original.read_bytes()
        imported = cq.importers.importStep(str(original)).val()
        with self.assertRaisesRegex(ValueError, "Ambiguous/missing source-to-native"):
            correlate(raw.decode(), imported, model="COINCIDENT",
                      source_sha256=sha256(raw).hexdigest())

    def test_source_vertex_mutation_rejected_against_original_native(self):
        source_report = analyze(self.step, model="HALF", source_sha256=self.digest)
        vid = source_report["candidate_source_entity_graph"][0]["source_oriented_vertex_ids"][0]
        table = parse_entities(self.step)
        coord_id = refs(table[vid][1])[0]
        old = coordinates(table, vid)
        pattern = re.compile(rf"(#{coord_id}\s*=\s*CARTESIAN_POINT\('',\()([-+\deE.]+)")
        changed, hits = pattern.subn(lambda m: m[1] + repr(old[0]+.1), self.step, count=1)
        self.assertEqual(hits, 1)
        with self.assertRaisesRegex(ValueError, "Ambiguous/missing source-to-native"):
            correlate(changed, self.native, model="HALF",
                      source_sha256=sha256(changed.encode()).hexdigest())

    def test_support_type_mismatch_rejected(self):
        with patch.dict("s3e_native_feature_bijection.SUPPORT_MAP",
                        {"CYLINDRICAL_SURFACE": "CONE"}):
            with self.assertRaisesRegex(ValueError, "neighbor support disagrees"):
                correlate(self.step, self.native, model="HALF", source_sha256=self.digest)

    def test_forged_certificate_rejected_even_after_checksum_recomputation(self):
        forged = json.loads(json.dumps(self.cert))
        forged["boundary_interfaces"][0]["native_edge_index"] += 1
        forged.pop("certificate_sha256")
        payload = json.dumps(forged, sort_keys=True, separators=(",", ":"))
        forged["certificate_sha256"] = sha256(payload.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, "Certificate fields differ"):
            verify_certificate(self.step, self.native, forged,
                               model="HALF", source_sha256=self.digest)

    def test_wrong_sha256_fails_without_output(self):
        output = self.root / "hash_failure"
        with self.assertRaisesRegex(ValueError, "Requested source SHA-256 mismatch"):
            run_one(self.source, output, model="HALF", expected_sha256="0"*64)
        self.assertFalse(output.exists())

    def test_real_models_cannot_be_substituted_by_synthetic_fixture(self):
        output = self.root / "real_source_failure"
        with self.assertRaisesRegex(ValueError, "Pinned original STEP SHA-256 mismatch"):
            run_one(self.source, output, model="M5")
        self.assertFalse(output.exists())
        self.assertEqual(SOURCES["M5"][2:], (41, 6))

    def test_original_assets_if_mounted_are_natively_correlated(self):
        import os
        source_dir = Path(os.getenv('APMESH_MAMBO_SOURCE_DIR', '/external/mambo/sources'))
        if all((self.root / item[0]).exists() for item in SOURCES.values()):
            self.fail('Unexpected original STEP in synthetic fixture directory')
        if not all((source_dir / SOURCES[model][0]).is_file() for model in ('M5','S40')):
            self.skipTest('Original pinned M5/S40 STEP files not mounted')
        for model, interfaces in (('M5',20),('S40',32)):
            with self.subTest(model=model):
                name,expected_hash,faces,candidates=SOURCES[model]
                source=source_dir/name
                self.assertEqual(sha256(source.read_bytes()).hexdigest(),expected_hash)
                report=run_one(source,self.root/('original_'+model),model=model)
                self.assertEqual(report['source_file'],name)
                self.assertEqual(report['source_sha256'],expected_hash)
                self.assertEqual(report['candidate_faces'],candidates)
                self.assertEqual(report['matched_interfaces'],interfaces)


if __name__ == "__main__":
    unittest.main()
