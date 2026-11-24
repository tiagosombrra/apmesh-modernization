"""Independent expected-shape and provenance tests for original MAMBO CAD files.

The four original STEP assets must be acquired separately, not committed here.
In a source-free checkout these tests report explicit SKIP, never fake PASS.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import unittest

from native_source_audit import CASES, ROOT, SOURCE_DIR, RESULT_DIR, incident_faces
import cadquery as cq

EXPECTED = {
    'M5': {'sha256': '895f67c0669096b287077ac1bb56dad0e117cd96f78334d3129d783fd78b96cb',
           'faces': 41, 'edges': 108, 'degenerate': 6, 'incidence': {'1':29, '2':79}, 'quad': 6},
    'S40': {'sha256': 'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b',
            'faces': 43, 'edges': 117, 'degenerate': 0, 'incidence': {'2':117}, 'quad': 9},
    'S27': {'sha256': 'b4a60c43cabd3c72bf61d54a23f36e6e539ad985015d2a7c377885b5d170f8c5',
            'faces': 52, 'edges': 144, 'degenerate': 0, 'incidence': {'2':144}, 'quad': 20},
    'M3': {'sha256': 'c42862fa6bc1e94a9bb70e43a7dc9901aa5281d7b58de6ee4699494088286008',
           'faces': 60, 'edges': 169, 'degenerate': 0, 'incidence': {'1':10, '2':159}, 'quad': 10},
}


class OriginalCADSourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        missing = [f for f, _ in CASES.values() if not (SOURCE_DIR / f).exists()]
        if missing:
            if os.environ.get('APMESH_REAL_CAD_WORKSPACE'):
                raise AssertionError('Explicit CAD test workspace has missing originals: ' + ','.join(missing))
            raise unittest.SkipTest('Original CAD not acquired (no implicit remote download): ' + ','.join(missing))
        cls.receipts = {
            name: json.loads((RESULT_DIR / f'{name.lower()}_native_receipt.json').read_text())
            for name in CASES
        }

    def test_exact_source_hashes(self):
        for name, (filename, _) in CASES.items():
            with self.subTest(name=name):
                data = (SOURCE_DIR / filename).read_bytes()
                self.assertEqual(sha256(data).hexdigest(), EXPECTED[name]['sha256'])

    def test_source_identity_and_kernel_validity(self):
        for name, (_, blob) in CASES.items():
            with self.subTest(name=name):
                receipt = self.receipts[name]
                self.assertEqual(receipt['source_blob_sha1'], blob)
                self.assertEqual(receipt['rendered_from_actual_source_sha256'], EXPECTED[name]['sha256'])
                self.assertTrue(receipt['valid_native_cad'])
                self.assertEqual(receipt['shape_type'], 'Solid')
                self.assertEqual(receipt['solids'], 1)
                self.assertEqual(receipt['shells'], 1)
                self.assertIn('millimetre', receipt['source_length_unit'])

    def test_native_topology_prevents_false_multisheet(self):
        for name in CASES:
            with self.subTest(name=name):
                receipt = self.receipts[name]
                reference = EXPECTED[name]
                self.assertEqual(receipt['faces'], reference['faces'])
                self.assertEqual(receipt['edges'], reference['edges'])
                self.assertEqual(receipt['native_degenerate_edges'], reference['degenerate'])
                self.assertEqual(receipt['face_to_exact_topods_edge_incidence_histogram'], reference['incidence'])
                self.assertEqual(receipt['explicit_native_edge_three_plus_distinct_faces'], 0)
                self.assertEqual(receipt['independent_multisheet_admission'], 'NOT_GRANTED')

    def test_face_decomposition_screen_not_an_accepted_fit(self):
        for name in CASES:
            with self.subTest(name=name):
                r = self.receipts[name]
                self.assertEqual(r['planar_four_straight_edge_candidate_face_count'], EXPECTED[name]['quad'])
                self.assertEqual(r['bicubic_fit'], 'NOT_RUN')
                self.assertEqual(r['apmesh_tri_quad_generation'], 'NOT_RUN')
                self.assertEqual(len(r['source_face_records']), r['faces'])

    def test_rendered_images_are_from_exact_sources(self):
        for name in CASES:
            with self.subTest(name=name):
                self.assertTrue((RESULT_DIR / f'{name.lower()}_shaded.png').stat().st_size > 4000)
                self.assertTrue((RESULT_DIR / f'{name.lower()}_support_types.png').stat().st_size > 4000)
                self.assertTrue((RESULT_DIR / f'{name.lower()}_source_cad.png').stat().st_size > 5000)

    def test_negative_corrupt_original_bytes_detected(self):
        # A changed byte cannot inherit the pinned original's SHA-256 receipt.
        filename = SOURCE_DIR / CASES['M5'][0]
        data = filename.read_bytes()
        mutated = data.replace(b'ISO-10303-21;', b'ISO-10303-20;', 1)
        self.assertNotEqual(sha256(mutated).hexdigest(), EXPECTED['M5']['sha256'])

    def test_artifact_json_has_independent_actual_evidence(self):
        for name in CASES:
            with self.subTest(name=name):
                receipt = self.receipts[name]
                self.assertTrue(receipt['surface_geom_types'])
                self.assertTrue(receipt['face_to_exact_topods_edge_incidence_histogram'])
                self.assertGreater(receipt['bounding_box_native_units']['diagonal'], 0)
                self.assertGreater(receipt['surface_area_native_units_squared'], 0)
                self.assertGreater(receipt['volume_native_units_cubed'], 0)


if __name__ == '__main__':
    unittest.main()
