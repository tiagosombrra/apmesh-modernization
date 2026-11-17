#!/usr/bin/env python3
"""S3.W original industrial S40 source, geometry and negative controls."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

from audit_analytic_bp import read_bp
from s3c_step_source_gate import entity, oriented_edges
from s3r_s40_conforming_hole_join import _edge_adjacency
from s3v_s40_curved_planar_closure import (
    BASELINE_SHA, SOURCE_SHA, _source_edge_closest, audit_native as audit_s3v,
    build_extension, source_boundary_sides, verify_source_and_atlas,
)
from s3w_s40_shared_spline_repair import (
    BUDGET_MM, CONTROL_BIAS_MM, EXPECTED_AFFECTED_OLD_PATCHES,
    EXPECTED_GLOBAL_SEAMS, ORIGINAL_S3V_CANDIDATE_SHA,
    _bias_shared_controls, audit_repaired_original,
    bound_bicubic_cylinder_radial_mm, radial_squared_tensor_net,
)


class OriginalS40TwoSidedSplineRepairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_dir=Path(os.environ['APMESH_ORIGINAL_CAD_DIR'])
        private_dir=Path(os.environ['APMESH_S3V_PRIVATE_DIR'])
        cls.source_path=source_dir/'i25o_s40.step'
        cls.source=cls.source_path.read_bytes()
        cls.parent=(private_dir/'s40_planar_octagons.partial.bp').read_bytes()
        cls.parent_manifest=json.loads((private_dir/'s40_planar_octagons_manifest.json').read_text())
        cls.native=cq.importers.importStep(str(cls.source_path)).val()
        cls.original_candidate,cls.original_receipt=build_extension(cls.source,cls.parent,cls.parent_manifest,cls.native)
        cls.original_audit=audit_s3v(cls.source,cls.parent,cls.parent_manifest,
                                       cls.native,cls.original_candidate,cls.original_receipt)
        cls.repaired,cls.receipt=_bias_shared_controls(cls.source,cls.parent,cls.parent_manifest,cls.native)
        cls.audit=audit_repaired_original(cls.source,cls.parent,cls.parent_manifest,
                                         cls.native,cls.repaired,cls.receipt)
        cls.old_points,cls.old_patches=read_bp(cls.parent.decode())
        cls.old_candidate_points,cls.old_candidate_patches=read_bp(cls.original_candidate)
        cls.points,cls.patches=read_bp(cls.repaired)
        cls.table,*_=verify_source_and_atlas(cls.source,cls.parent,cls.parent_manifest)

    def test_pinned_original_step_hash(self):
        self.assertEqual(sha256(self.source).hexdigest(),SOURCE_SHA)

    def test_pinned_admitted_baseline_hash(self):
        self.assertEqual(sha256(self.parent).hexdigest(),BASELINE_SHA)

    def test_predecessor_s3v_candidate_hash(self):
        self.assertEqual(sha256(self.original_candidate.encode()).hexdigest(),ORIGINAL_S3V_CANDIDATE_SHA)

    def test_old_candidate_actually_blocked(self):
        self.assertEqual(self.original_audit['native_boundary_OUT'],135)
        self.assertEqual(self.original_audit['status'],'BLOCKED_NATIVE_TRIM_BOUNDARY')

    def test_repaired_bp_hash_reproducible(self):
        self.assertEqual(sha256(self.repaired.encode()).hexdigest(),self.receipt['repaired_bp_sha256'])

    def test_original_source_native_census(self):
        self.assertEqual((self.audit['original_native_face_count'],self.audit['original_native_edge_count'],
                          self.audit['original_native_vertex_count']),(43,117,77))

    def test_new_original_face_source_ids(self):
        self.assertEqual(self.receipt['new_original_face_ids'],[17,2092])

    def test_pinned_spline_curve_types(self):
        for fid,eid in ((17,85),(2092,2096)):
            edges=oriented_edges(self.table,fid)[1][0]
            self.assertEqual(next(e for e in edges if e['edge_curve_id']==eid)['master_3d_curve'],
                             'B_SPLINE_CURVE_WITH_KNOTS')

    def test_original_source_indexed_patch_count(self):
        self.assertEqual((len(self.points),len(self.patches)),(1619,148))

    def test_two_sided_seams_count(self):
        adjacency=_edge_adjacency(self.patches)
        self.assertEqual(sum(len(x)==2 for x in adjacency.values()),EXPECTED_GLOBAL_SEAMS)
        self.assertEqual(sum(len(x)==1 for x in adjacency.values()),114)
        self.assertFalse(any(len(x)>2 for x in adjacency.values()))

    def test_prior_patch_indices_unchanged(self):
        self.assertEqual(self.patches[:132],self.old_patches)

    def test_unrelated_old_patch_nets_unchanged(self):
        affected=set(EXPECTED_AFFECTED_OLD_PATCHES)
        for index in range(132):
            if index not in affected:
                self.assertEqual(tuple(self.points[z] for z in self.patches[index]),
                                 tuple(self.old_points[z] for z in self.old_patches[index]))

    def test_only_thirty_original_controls_changed(self):
        changed={i for i,(a,b) in enumerate(zip(self.points,self.old_candidate_points)) if a!=b}
        self.assertEqual(len(changed),30)
        self.assertTrue(all(i<1527 for i in changed))
        self.assertEqual(self.receipt['modified_shared_original_control_count'],30)

    def test_original_step_218_hole_nets_exact(self):
        for index in range(96,126):
            self.assertEqual(tuple(self.points[z] for z in self.patches[index]),
                             tuple(self.old_points[z] for z in self.old_patches[index]))

    def test_original_step_218_hole_native_exclusion(self):
        self.assertEqual(self.audit['original_source_hole_OUT_samples'],49)

    def test_planar_interior_native_in(self):
        self.assertEqual(self.audit['planar_original_interior_IN'],1296)

    def test_planar_boundary_all_in_or_on(self):
        self.assertEqual((self.audit['planar_original_boundary_IN_or_ON'],
                          self.audit['planar_original_boundary_OUT']),(704,0))

    def test_dense_original_spline_plane_membership(self):
        self.assertEqual((self.audit['dense_planar_spline_boundary_IN_or_ON'],
                          self.audit['dense_planar_spline_boundary_OUT']),(1515,0))

    def test_dense_original_spline_cylinder_membership(self):
        self.assertEqual((self.audit['dense_cylinder_spline_boundary_IN_or_ON'],
                          self.audit['dense_cylinder_spline_boundary_OUT']),(1515,0))

    def test_changed_cylinders_trim_membership(self):
        self.assertEqual((self.audit['modified_cylinder_native_IN_or_ON_samples'],
                          self.audit['modified_cylinder_native_OUT_samples']),(1815,0))

    def test_original_splines_below_native_curve_budget(self):
        self.assertLess(self.audit['maximum_original_spline_dense_curve_distance_mm'],BUDGET_MM)
        self.assertLess(self.audit['maximum_original_curve_distance_mm'],BUDGET_MM)
        self.assertEqual(set(self.audit['spline_original_edge_results']),{'85','2096'})

    def test_planar_support_tight(self):
        self.assertLess(self.audit['maximum_planar_support_mm'],1e-7)

    def test_full_bivariate_bernstein_radial_bounds(self):
        self.assertLess(self.audit['maximum_guarded_bivariate_bernstein_radial_mm'],BUDGET_MM)
        self.assertGreater(self.audit['maximum_guarded_bivariate_bernstein_radial_mm'],0)

    def test_guarded_bernstein_rejects_corrupted_controls(self):
        face=self.native.Faces()[12]
        cylinder=BRepAdaptor_Surface(face.wrapped).Cylinder()
        net=[self.points[i] for i in self.patches[64]]
        bad=list(net)
        p=list(bad[1]);p[0]+=0.1;bad[1]=tuple(p)
        candidate=bound_bicubic_cylinder_radial_mm(bad,cylinder)
        self.assertFalse(candidate['pass'])

    def test_unchanged_fixed_geometry_budget(self):
        self.assertEqual((self.receipt['unchanged_original_geometric_budget_mm'],
                          self.audit['pilot_budget_mm']),(0.001,0.001))

    def test_original_cylinder_native_radial_samples_below_budget(self):
        self.assertLess(self.audit['maximum_native_cylinder_sampled_radial_mm'],0.001)

    def test_repaired_plane_area_matches_native_at_sampled_scale(self):
        results=self.audit['planar_area_results_mm2']
        self.assertEqual(set(results),{'17','2092'})
        for row in results.values():
            self.assertGreater(row['minimum_sampled_positive_jacobian_mm2'],0)
            self.assertLess(row['sampled_absolute_area_difference_mm2'],.1)
            self.assertLess(row['sampled_absolute_area_difference_mm2']/row['original_native_face_area_mm2'],.0002)

    def test_pilot_admitted_but_not_complete_cad_or_apmesh(self):
        self.assertEqual(self.audit['classification'],'PASS_BOUNDED_NATIVE_GEOMETRY_AND_INDEXED_SEAMS')
        self.assertEqual((self.audit['admitted_research_patch_count'],
                          self.audit['represented_original_source_faces']),(148,21))
        self.assertEqual(self.audit['apmesh_cpp_tri_quad'],'NOT_RUN')
        self.assertFalse(self.audit['continuous_trimmed_hausdorff_certified'])
        self.assertFalse(self.audit['formal_directed_rounding_interval_proof'])

    def test_tampered_original_step_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'SHA mismatch'):
            _bias_shared_controls(self.source+b' ',self.parent,self.parent_manifest,self.native)

    def test_tampered_parent_bp_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'BP SHA mismatch'):
            _bias_shared_controls(self.source,self.parent+b' ',self.parent_manifest,self.native)

    def test_forged_old_manifest_fails_closed(self):
        m=deepcopy(self.parent_manifest);m['joined_patches']=133
        with self.assertRaisesRegex(ValueError,'manifest changed'):
            _bias_shared_controls(self.source,self.parent,m,self.native)

    def test_relaxed_geometry_budget_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'budget was modified'):
            _bias_shared_controls(self.source,self.parent,self.parent_manifest,self.native,budget_mm=.002)

    def test_tampered_displacement_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'displacement'):
            _bias_shared_controls(self.source,self.parent,self.parent_manifest,self.native,bias_mm=.002)

    def test_tampered_repaired_bp_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'Altered repaired BP'):
            audit_repaired_original(self.source,self.parent,self.parent_manifest,self.native,
                                  self.repaired+' ',self.receipt)

    def test_rehashed_forged_receipt_fails_closed(self):
        forged=deepcopy(self.receipt)
        forged['combined_patches']=149
        with self.assertRaisesRegex(ValueError,'forged original-source repair receipt'):
            audit_repaired_original(self.source,self.parent,self.parent_manifest,self.native,
                                  self.repaired,forged)

    def test_native_wrong_original_body_rejected(self):
        other=cq.Workplane('XY').box(1,1,1).val()
        with self.assertRaises(Exception):
            audit_repaired_original(self.source,self.parent,self.parent_manifest,other,
                                  self.repaired,self.receipt)


if __name__=='__main__':
    unittest.main()
