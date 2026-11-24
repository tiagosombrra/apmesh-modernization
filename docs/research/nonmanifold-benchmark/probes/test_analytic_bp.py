"""R3 bounded representation controls and deliberate malformed BP/sidecar cases."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import unittest


from build_analytic_bp import construct
from audit_analytic_bp import audit, read_bp
from interface_graph_probe import analyze
from nonmanifold_sewing_probe import construct as make_native_surface


class AnalyticBPPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads(json.dumps(analyze()))
        cls.bp, cls.manifest = construct(cls.graph)
        cls.native = make_native_surface(cls.graph)[1]

    def test_native_geometry_and_exact_shared_indices(self):
        report = audit(self.bp, self.manifest, self.native)
        self.assertEqual(report['patches'], 4)
        self.assertEqual(report['unique_control_vertices'], 52)
        self.assertEqual(report['unique_curves'], 13)
        self.assertEqual(report['common_curve_incidence'], 4)
        self.assertLess(report['analytical_sample_max_abs_error'], 1e-12)
        self.assertLess(report['native_brep_sample_max_distance'], 1e-9)

    def test_deterministic_generation(self):
        bp, manifest = construct(self.graph)
        self.assertEqual(bp, self.bp)
        self.assertEqual(json.dumps(manifest, sort_keys=True),
                         json.dumps(self.manifest, sort_keys=True))

    def test_independent_grammar(self):
        vertices, patches = read_bp(self.bp)
        self.assertEqual(len(vertices), 52)
        self.assertEqual(len(patches), 4)
        self.assertEqual([tuple(p[i] for i in (0, 4, 8, 12)) for p in patches],
                         [(0, 1, 2, 3)] * 4)

    def test_corrupted_sha_rejected(self):
        new = copy.deepcopy(self.manifest)
        new['bp_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'digest'):
            audit(self.bp, new)

    def test_nonfinite_record_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            read_bp(self.bp.replace('v 0 0 -2.5', 'v NaN 0 -2.5', 1))

    def test_out_of_range_control_rejected(self):
        bp = self.bp.replace('p 0', 'p 100000', 1)
        with self.assertRaisesRegex(ValueError, 'reference'):
            read_bp(bp)

    def test_incomplete_patch_rejected(self):
        bp = self.bp.replace('\np 0 ', '\np ', 1)
        with self.assertRaisesRegex(ValueError, 'Invalid patch'):
            read_bp(bp)

    def test_shared_curve_index_mutation_rejected(self):
        text = self.bp.replace('\np 0 4 ', '\np 4 0 ', 1)
        manifest = copy.deepcopy(self.manifest)
        manifest['bp_sha256'] = hashlib.sha256(text.encode()).hexdigest()
        manifest['patches'][0]['control_vertex_ids'][0] = 4
        manifest['patches'][0]['control_vertex_ids'][1] = 0
        manifest['patches'][0]['sides'][0]['control_vertex_ids'][0] = 4
        manifest['patches'][0]['sides'][0]['control_vertex_ids'][1] = 0
        manifest['patches'][0]['sides'][3]['control_vertex_ids'][0] = 4
        with self.assertRaisesRegex(ValueError, 'Common edge'):
            audit(text, manifest)

    def test_wrong_geometry_rejected_with_matching_digest(self):
        vertices, _ = read_bp(self.bp)
        old = 'v ' + ' '.join(format(x, '.17g') for x in vertices[5])
        changed = 'v 999 0 0'
        text = self.bp.replace(old, changed, 1)
        self.assertNotEqual(text, self.bp)
        manifest = copy.deepcopy(self.manifest)
        manifest['bp_sha256'] = hashlib.sha256(text.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'Planar BP geometry'):
            audit(text, manifest)

    def test_duplicate_source_face_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        target = manifest['patches'][0]['source_faces'][0]
        manifest['patches'][1]['source_faces'][0] = copy.deepcopy(target)
        with self.assertRaises(ValueError):
            audit(self.bp, manifest)

    def test_false_g2_approval_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['g2_external_admission'] = 'PASS'
        with self.assertRaisesRegex(ValueError, 'overclaim'):
            audit(self.bp, manifest)

    def test_incorrect_side_curve_id_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['patches'][1]['sides'][3]['curve_id'] = 'C_fake'
        with self.assertRaisesRegex(ValueError, 'canonical'):
            audit(self.bp, manifest)

    def test_source_graph_wrong_provenance_rejected(self):
        graph = copy.deepcopy(self.graph)
        graph['g2_admission'] = 'PASS'
        with self.assertRaisesRegex(ValueError, 'Unexpected G2'):
            construct(graph)


if __name__ == '__main__':
    unittest.main()
