#!/usr/bin/env python3
"""Directed native S3.X tests: original face census and marginal spline envelope."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import os
import unittest

import cadquery as cq

from s3x_s40_post_repair_risk_audit import (
    BUDGET_MM, ORIGINAL_SHA, PARENT_SHA, REPAIRED_SHA,
    check_pinned_inputs, audit_s3x, public_summary,
    stress_shared_spline_seams,
)


class OriginalS40PostRepairAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_dir = Path(os.environ['APMESH_ORIGINAL_CAD_DIR'])
        root = Path(os.environ['APMESH_S3V_PRIVATE_DIR'])
        cls.source_file = source_dir / 'i25o_s40.step'
        cls.source = cls.source_file.read_bytes()
        cls.parent = (root / 's40_planar_octagons.partial.bp').read_bytes()
        cls.repaired = (root / 's40_spline_shared_repair.partial.bp').read_bytes()
        cls.s3r = (root / 's40_218_conforming.partial.bp').read_bytes()
        cls.parent_manifest = json.loads((root / 's40_planar_octagons_manifest.json').read_text())
        cls.repaired_manifest = json.loads((root / 's40_spline_shared_repair_manifest.json').read_text())
        cls.s3r_manifest = json.loads((root / 's40_218_conforming_manifest.json').read_text())
        cls.native = cq.importers.importStep(str(cls.source_file)).val()
        cls.audit = audit_s3x(cls.source, cls.native, cls.parent, cls.parent_manifest,
                             cls.repaired, cls.repaired_manifest, cls.s3r, cls.s3r_manifest,
                             segment_grid=33, interior_grid=7)

    def verify(self, **overrides):
        data = dict(original=self.source, parent=self.parent, repaired=self.repaired,
                    parent_manifest=self.parent_manifest,
                    repaired_manifest=self.repaired_manifest,
                    s3r=self.s3r, s3r_manifest=self.s3r_manifest)
        data.update(overrides)
        return check_pinned_inputs(**data)

    def test_source_frozen_hash(self):
        self.assertEqual(sha256(self.source).hexdigest(), ORIGINAL_SHA)

    def test_repaired_bps_frozen(self):
        self.assertEqual((sha256(self.parent).hexdigest(), sha256(self.repaired).hexdigest()),
                         (PARENT_SHA, REPAIRED_SHA))

    def test_real_native_faces_edges_vertices(self):
        gap = self.audit['gap']
        self.assertEqual((gap['corresponded_original_faces'],gap['corresponded_original_edges'],
                          gap['corresponded_original_vertices']), (43,117,77))

    def test_original_source_admitted_vs_gap(self):
        gap = self.audit['gap']
        self.assertEqual((gap['represented_original_faces'],gap['remaining_original_faces']), (21,22))
        self.assertFalse(set(gap['represented_original_face_ids']) & {
            f['source_advanced_face_id'] for f in gap['pending_original_faces']})

    def test_updated_gap_support_counts(self):
        g = self.audit['gap']['pending_original_support_histogram']
        self.assertEqual((g['PLANE'],g['CYLINDRICAL_SURFACE'],g['B_SPLINE_SURFACE_WITH_KNOTS'],
                          g['COMPLEX_RATIONAL_B_SPLINE_SURFACE']), (13,6,2,1))

    def test_gap_direct_adjacent_and_hops(self):
        gap = self.audit['gap']
        self.assertEqual(gap['remaining_direct_adjacency_count'], 16)
        self.assertEqual(gap['remaining_edge_hop_histogram'], {'1':16,'2':6})

    def test_priority_original_six_sided_faces(self):
        self.assertEqual(self.audit['gap']['topology_front_candidates'], [1827,1907,3044])
        for row in self.audit['gap']['pending_original_faces']:
            if row['source_advanced_face_id'] in (1827,1907,3044):
                self.assertEqual((row['original_boundary_edge_count'],
                                  row['already_indexed_incident_original_edges']), (6,6))
                self.assertEqual(row['original_master_curve_histogram'], {'CIRCLE':4,'LINE':2})

    def test_original_is_manifold_control_not_false_positive(self):
        self.assertEqual(self.audit['gap']['source_original_three_plus_incidence_edges'], 0)

    def test_spline_seams_native_sidedness(self):
        x = self.audit['stress']
        self.assertEqual((x['corrected_spline_planar_trim_in_or_on'],
                          x['corrected_spline_cylinder_trim_in_or_on']), (495,495))
        self.assertEqual(x['corrected_spline_out_samples'],0)
        self.assertEqual(x['source_spline_seams']['85']['source_indexed_cubic_segments'], 7)
        self.assertEqual(x['source_spline_seams']['2096']['source_indexed_cubic_segments'],8)

    def test_all_modified_original_cylinder_patches_retested(self):
        x = self.audit['stress']
        self.assertEqual(x['modified_prior_cylinder_patch_count'],15)
        self.assertEqual(x['modified_prior_cylinder_interior_samples'], 15*7*7)
        self.assertEqual(x['modified_prior_cylinder_out_samples'],0)

    def test_radial_guard_slack_is_positive_but_small(self):
        x = self.audit['stress']
        self.assertGreater(x['float_guarded_remaining_margin_mm'],0)
        self.assertLess(x['float_guarded_remaining_margin_mm'],2e-5)
        self.assertLess(x['max_float_guarded_bernstein_radial_mm'],BUDGET_MM)
        self.assertFalse(x['formal_interval_bound'])
        self.assertFalse(x['continuous_trimmed_surface_equivalence'])

    def test_no_new_bp_or_meshing_claim(self):
        self.assertEqual(self.audit['classification'],
                         'PASS_BOUNDED_SAMPLED_AUDIT_NO_NEW_BP_ADMISSION')
        self.assertEqual(self.audit['research_patch_count'],148)
        self.assertFalse(self.audit['apmesh_tri_quad_executed'])
        self.assertFalse(self.audit['production_cpp_regression_executed'])

    def test_public_receipt_excludes_source_edge_identifiers_per_record(self):
        public=public_summary(self.audit)
        self.assertNotIn('pending_original_faces',public['gap'])
        self.assertNotIn('already_indexed_incident_source_edge_ids',
                         public['pending_face_summary'][0])
        self.assertEqual(len(public['pending_face_summary']),22)

    def test_reject_forged_original_step(self):
        with self.assertRaisesRegex(ValueError,'STEP SHA-256'):
            self.verify(original=self.source + b'altered')

    def test_reject_forged_prior_atlas(self):
        with self.assertRaisesRegex(ValueError,'S3.T BP SHA-256'):
            self.verify(parent=self.parent + b'altered')

    def test_reject_forged_repaired_atlas(self):
        with self.assertRaisesRegex(ValueError,'S3.W BP SHA-256'):
            self.verify(repaired=self.repaired + b'altered')

    def test_reject_forged_s3r_lineage(self):
        with self.assertRaisesRegex(ValueError,'S3.R BP SHA-256'):
            self.verify(s3r=self.s3r + b'altered')

    def test_reject_modified_immutable_budget(self):
        with self.assertRaisesRegex(ValueError,'immutable'):
            self.verify(budget_mm=.002)

    def test_reject_modified_parent_manifest(self):
        forged=deepcopy(self.parent_manifest)
        forged['new_bp_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'manifest'):
            self.verify(parent_manifest=forged)

    def test_reject_modified_repair_manifest(self):
        forged=deepcopy(self.repaired_manifest)
        forged['source_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'manifest'):
            self.verify(repaired_manifest=forged)

    def test_reject_modified_s3r_manifest(self):
        forged=deepcopy(self.s3r_manifest)
        forged['joined_bp_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'manifest'):
            self.verify(s3r_manifest=forged)

    def test_reject_invalid_stress_sampling_grids(self):
        with self.assertRaisesRegex(ValueError,'sampling'):
            stress_shared_spline_seams(self.source,self.native,self.parent,self.repaired,
                                       segment_grid=1,interior_grid=7)
        with self.assertRaisesRegex(ValueError,'sampling'):
            stress_shared_spline_seams(self.source,self.native,self.parent,self.repaired,
                                       segment_grid=33,interior_grid=1)

    def test_reject_forged_brep_shape(self):
        wrong=cq.Workplane('XY').box(1,1,1).val()
        with self.assertRaises((ValueError, IndexError, RuntimeError)):
            audit_s3x(self.source,wrong,self.parent,self.parent_manifest,
                      self.repaired,self.repaired_manifest,self.s3r,self.s3r_manifest,
                      segment_grid=3,interior_grid=3)


if __name__ == '__main__':
    unittest.main()
