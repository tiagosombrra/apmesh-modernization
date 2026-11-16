"""Directed negative and native-positive S3.L original S40 admission controls."""
from __future__ import annotations

import copy
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
import unittest

import cadquery as cq

from s3c_step_source_gate import SOURCES
from s3h_source_cylinder_bp import face_geometry
from s3l_s40_partial_cylinder_atlas import (
    S40_CYLINDER_FACES, SOURCE_3D_2D_ANGLE_CLOSURE_TOLERANCE_RAD,
    _pcurve_constrained_geometry, audit_native, construct_partial, run,
)


class PinnedS40NativeAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = os.environ.get('APMESH_MAMBO_SOURCE_DIR')
        if not folder:
            raise unittest.SkipTest('Original S40 asset not configured: APMESH_MAMBO_SOURCE_DIR')
        cls.path = Path(folder) / SOURCES['S40'][0]
        if not cls.path.is_file():
            raise unittest.SkipTest('Original pinned S40 asset missing')
        raw = cls.path.read_bytes()
        cls.digest = sha256(raw).hexdigest()
        if cls.digest != SOURCES['S40'][1]:
            raise ValueError('Original pinned S40 asset SHA-256 mismatch')
        cls.text = raw.decode('utf8')
        cls.native = cq.importers.importStep(str(cls.path)).val()
        cls.bp, cls.manifest = construct_partial(
            cls.text, cls.native, model='S40', source_sha256=cls.digest,
            sectors=4, sampled_budget_mm=.001)
        cls.audit = audit_native(
            cls.text, cls.native, cls.bp, cls.manifest, model='S40',
            source_sha256=cls.digest, declared_budget_mm=.001)

    def check(self, bp=None, manifest=None, *, budget=.001, source=None):
        return audit_native(self.text if source is None else source, self.native,
                            self.bp if bp is None else bp,
                            self.manifest if manifest is None else manifest,
                            model='S40', source_sha256=self.digest,
                            declared_budget_mm=budget, interior_grid=3,
                            boundary_grid=3)

    def test_source_faces_and_partial_bp_inventory(self):
        self.assertEqual(self.manifest['original_faces'], 43)
        self.assertEqual(self.manifest['admitted_planar_faces'], 9)
        self.assertEqual(self.manifest['admitted_cylinder_faces'], 4)
        self.assertEqual(self.manifest['excluded_unrepresented_faces'], 30)
        self.assertEqual(self.manifest['cylinder_face_ids'], list(S40_CYLINDER_FACES))
        self.assertEqual(self.manifest['patch_count'], 25)
        self.assertEqual(self.manifest['control_count'], 320)
        self.assertEqual(self.audit['partial_bp_patch_count'], 25)
        self.assertEqual(self.audit['global_control_count'], 320)

    def test_source_native_shared_curves_include_cylinder_to_cylinder(self):
        by_id = {e['source_edge_curve_id']: e for e in self.manifest['shared_original_edges']}
        self.assertEqual(len(by_id), 8)
        self.assertEqual(set(by_id), {1161, 1210, 2810, 2861, 3104, 3022, 2916, 2970})
        self.assertEqual(by_id[2916]['source_face_ids'], [2882, 3127])
        self.assertEqual(by_id[2970]['source_face_ids'], [2936, 2990])
        self.assertEqual(self.audit['globally_reused_original_source_control_ids'], 32)
        self.assertEqual(self.audit['shared_original_source_edges_native_IsSame'], 8)

    def test_original_native_uv_trim_and_radial_support(self):
        self.assertEqual(self.audit['original_cylinders_independent_native_uv_interior_samples'], 1296)
        self.assertEqual(self.audit['original_cylinders_independent_native_uv_boundary_samples'], 704)
        self.assertLess(self.audit['max_sampled_cylinder_native_projection_distance_mm'], .001)
        self.assertLess(self.audit['max_guarded_bernstein_radial_support_mm'], .001)
        self.assertLess(self.audit['max_sampled_planar_native_face_distance_mm'], 1e-7)
        self.assertTrue(self.audit['audit_pass'])
        self.assertFalse(self.audit['continuous_trimmed_surface_equivalence_certified'])
        self.assertEqual(self.audit['apmesh_tri_quad'], 'NOT_RUN')

    def test_circular_and_pcurve_angular_closure_is_explicit(self):
        checks = self.manifest['source_3d_circle_2d_pcurve_alignment']
        self.assertEqual(len(checks), 4)
        self.assertLessEqual(max(x['absolute_original_3d_2d_angular_closure_residual_rad']
                                 for x in checks), SOURCE_3D_2D_ANGLE_CLOSURE_TOLERANCE_RAD)
        face = next(x for x in checks if x['source_face_id'] == 3127)
        self.assertGreater(face['absolute_original_3d_2d_angular_closure_residual_rad'], 6e-10)
        self.assertEqual(face['alignment'], 'SOURCE_GENERATOR_PCURVE_ANGULAR_ENDPOINTS_WITH_3D_CIRCLE_WINDING')

    def test_unmodified_strict_wedge_rejects_last_3127_control(self):
        from s3h_source_cylinder_bp import construct as raw_construct
        from s3j_radial_support_enclosure import certify_patch
        from audit_analytic_bp import read_bp
        original = face_geometry(self.text, face_id=3127, model='S40',
                                 source_sha256=self.digest, require_anchored=False)
        raw_bp, _ = raw_construct(original, sectors=4, absolute_budget_mm=.001)
        vertices, patches = read_bp(raw_bp)
        with self.assertRaisesRegex(ValueError, 'angular wedge'):
            certify_patch(vertices, patches[3], original, 3, 4)
        constrained, _ = _pcurve_constrained_geometry(original)
        fixed_bp, _ = raw_construct(constrained, sectors=4, absolute_budget_mm=.001)
        vertices, patches = read_bp(fixed_bp)
        self.assertLess(certify_patch(vertices, patches[3], constrained, 3, 4)
                        ['radial_support_error_upper_mm'], .001)

    def test_original_face_rejected_when_3d_2d_closure_exceeds_limit(self):
        geom = face_geometry(self.text, face_id=3127, model='S40',
                             source_sha256=self.digest, require_anchored=False)
        corrupted = copy.deepcopy(geom)
        corrupted['signed_sweep_rad'] += 1e-5
        with self.assertRaisesRegex(ValueError, 'angular closure mismatch'):
            _pcurve_constrained_geometry(corrupted)

    def test_source_sha_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            self.check(source=self.text.replace('HEADER;', 'HEADER; ', 1))

    def test_tampered_bp_with_unchanged_manifest_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'BP digest mismatch'):
            self.check(bp=self.bp.replace('v ', 'v 9 ', 1))

    def test_tampered_bp_with_recomputed_hash_is_still_rejected(self):
        bp = self.bp.replace('v ', 'v 9 ', 1)
        tampered = copy.deepcopy(self.manifest)
        tampered['bp_sha256'] = sha256(bp.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'source recomputation'):
            self.check(bp=bp, manifest=tampered)

    def test_tampered_original_shared_control_ids_are_rejected(self):
        m = copy.deepcopy(self.manifest)
        m['shared_original_edges'][0]['shared_global_control_ids'][0] += 1
        with self.assertRaisesRegex(ValueError, 'source recomputation'):
            self.check(manifest=m)

    def test_external_widened_budget_cannot_override_manifest(self):
        with self.assertRaisesRegex(ValueError, 'Post-hoc widening'):
            self.check(budget=.002)

    def test_undersegmented_cylinders_fail_predeclared_budget(self):
        bp, report = construct_partial(self.text, self.native, model='S40',
                                       source_sha256=self.digest, sectors=2,
                                       sampled_budget_mm=.001)
        with self.assertRaisesRegex(ValueError, 'Bernstein support exceeds'):
            audit_native(self.text, self.native, bp, report, model='S40',
                         source_sha256=self.digest, declared_budget_mm=.001,
                         interior_grid=3, boundary_grid=3)

    def test_fail_closed_cli_rejects_budget_and_leaves_no_output(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / 'not-created'
            with self.assertRaises(ValueError):
                run(self.path, target, sectors=2, budget_mm=.001)
            self.assertFalse(target.exists())

    def test_unsupported_input_is_not_admitted(self):
        with self.assertRaisesRegex(ValueError, 'only admits'):
            construct_partial(self.text, self.native, model='M5',
                              source_sha256=self.digest)

    def test_sectors_and_budgets_validation(self):
        for segments in (0, -1, 65):
            with self.subTest(segments=segments), self.assertRaisesRegex(ValueError, 'Sector count'):
                construct_partial(self.text, self.native, model='S40',
                                  source_sha256=self.digest, sectors=segments)
        for budget in (0, -1, float('nan'), float('inf')):
            with self.subTest(budget=budget), self.assertRaisesRegex(ValueError, 'Budget'):
                construct_partial(self.text, self.native, model='S40',
                                  source_sha256=self.digest, sampled_budget_mm=budget)


if __name__ == '__main__':
    unittest.main()
