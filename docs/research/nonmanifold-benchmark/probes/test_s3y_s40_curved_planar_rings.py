#!/usr/bin/env python3
"""Directed source-native tests for original industrial S40 S3.Y admission."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import os
import unittest

import cadquery as cq

from audit_analytic_bp import read_bp
from s3r_s40_conforming_hole_join import _edge_adjacency, _side
from s3y_s40_curved_planar_rings import (
    SOURCE_SHA, BASELINE_SHA, BUDGET_MM, SOURCE_SIDE_LINEAGE,
    audit_candidate, build_candidate, check_inputs, recover_source_sides,
)

class S3YOriginalS40DirectedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_dir=Path(os.environ['APMESH_ORIGINAL_CAD_DIR'])
        private_dir=Path(os.environ['APMESH_S3V_PRIVATE_DIR'])
        cls.source_path=source_dir/'i25o_s40.step'
        cls.source=cls.source_path.read_bytes()
        cls.parent=(private_dir/'s40_spline_shared_repair.partial.bp').read_bytes()
        cls.manifest=json.loads((private_dir/'s40_spline_shared_repair_manifest.json').read_text())
        cls.native=cq.importers.importStep(str(cls.source_path)).val()
        cls.single,cls.receipt=build_candidate(cls.source,cls.native,cls.parent,cls.manifest,
                                                faces=(3044,))
        cls.audit=audit_candidate(cls.source,cls.native,cls.parent,cls.manifest,
                                  cls.single,cls.receipt,interior_grid=17,boundary_grid=31)
        cls.three,cls.three_receipt=build_candidate(cls.source,cls.native,cls.parent,cls.manifest)
        cls.three_audit=audit_candidate(cls.source,cls.native,cls.parent,cls.manifest,
                                        cls.three,cls.three_receipt)

    def test_frozen_step_identity(self):
        self.assertEqual(sha256(self.source).hexdigest(),SOURCE_SHA)

    def test_frozen_parent_identity(self):
        self.assertEqual(sha256(self.parent).hexdigest(),BASELINE_SHA)

    def test_original_native_brep_is_valid(self):
        self.assertTrue(self.native.isValid())
        self.assertEqual(len(self.native.Faces()),43)
        self.assertEqual(len(self.native.Edges()),117)
        self.assertEqual(len(self.native.Vertices()),77)

    def test_three_targets_have_distinct_native_faces(self):
        from s3y_s40_curved_planar_rings import FACE_TO_NATIVE
        self.assertEqual(FACE_TO_NATIVE,{1827:15,1907:16,3044:29})

    def test_six_original_edges_per_target(self):
        for key,mapping in SOURCE_SIDE_LINEAGE.items():
            with self.subTest(original_face=key):
                self.assertEqual(len(mapping),6)

    def test_source_edge_indexed_segment_counts(self):
        self.assertEqual([v['segments'] for v in self.receipt['faces']['3044']['source_edge_checks'].values()],
                         [1,4,4,1,4,4])

    def test_source_native_edge_id_uniqueness(self):
        for _,r in self.three_receipt['faces'].items():
            self.assertEqual(len({x['source_native_edge_index'] for x in r['source_edge_checks'].values()}),6)

    def test_original_owner_incidence_two(self):
        for _,r in self.three_receipt['faces'].items():
            self.assertTrue(all(x['original_incident_face_count']==2
                                for x in r['source_edge_checks'].values()))

    def test_expected_single_face_patch_count(self):
        self.assertEqual(self.receipt['candidate_patch_count'],156)
        self.assertEqual(self.receipt['added_patches'],8)

    def test_expected_global_control_count(self):
        self.assertEqual(self.receipt['candidate_control_count'],1665)

    def test_original_atlas_control_prefix_immutable(self):
        old, oldpatches=read_bp(self.parent.decode())
        new, newpatches=read_bp(self.single)
        self.assertEqual(new[:len(old)],old)
        self.assertEqual(newpatches[:len(oldpatches)],oldpatches)

    def test_single_face_original_seams(self):
        self.assertEqual(self.receipt['candidate_two_sided_indexed_seams'],264)
        self.assertEqual(self.receipt['candidate_open_indexed_sides'],96)
        self.assertEqual(Counter(len(v) for v in _edge_adjacency(read_bp(self.single)[1]).values()),
                         Counter({2:264,1:96}))

    def test_original_six_edges_have_two_indexed_sides(self):
        _,patches=read_bp(self.single)
        adjacency=_edge_adjacency(patches)
        for segments in SOURCE_SIDE_LINEAGE[3044].values():
            for pid,side in segments:
                self.assertEqual(len(adjacency[tuple(sorted(_side(patches[pid],side)))]),2)

    def test_native_interior_classification(self):
        self.assertEqual(self.audit['native_interior_IN'],2312)

    def test_native_boundary_classification(self):
        self.assertEqual(self.audit['native_boundary_IN_or_ON'],992)
        self.assertEqual(self.audit['native_boundary_OUT'],0)
        self.assertEqual(self.audit['status'],'PASS')

    def test_edge_to_native_curve_budget(self):
        self.assertGreater(self.audit['original_native_curve_samples'],0)
        self.assertLess(self.audit['max_boundary_native_curve_distance_mm'],BUDGET_MM)

    def test_original_plane_support(self):
        self.assertLess(self.audit['max_plane_distance_mm'],1e-7)

    def test_positive_outward_jacobian(self):
        value=self.audit['by_face']['3044']['area_and_orientation']
        self.assertGreater(value['min_sampled_oriented_jacobian'],0.)

    def test_planar_coverage_area_tolerance(self):
        value=self.audit['by_face']['3044']['area_and_orientation']
        self.assertLess(value['sampled_relative_area_difference'],1e-4)
        self.assertLess(value['sampled_2d_patch_overlap_area'],1e-5)
        self.assertEqual(value['sampled_2d_union_component_count'],1)
        self.assertLess(value['sampled_numerical_hole_area_mm2'],1e-7)

    def test_existing_original_hole_218_untouched(self):
        _,old=read_bp(self.parent.decode())
        _,new=read_bp(self.single)
        self.assertEqual(old[96:126],new[96:126])

    def test_three_face_candidate_not_admitted(self):
        self.assertEqual(self.three_receipt['candidate_patch_count'],160)
        self.assertEqual(self.three_audit['status'],'BLOCKED_ORIGINAL_NATIVE_TRIM')
        self.assertEqual(self.three_audit['native_boundary_OUT'],36)
        self.assertEqual(self.three_audit['native_boundary_out_by_face'],{'1827':18,'1907':18})

    def test_3044_independent_in_three_face_candidate(self):
        self.assertEqual(self.three_audit['by_face']['3044']['native_boundary_OUT'],0)
        self.assertEqual(self.three_audit['by_face']['3044']['native_interior_IN'],648)

    def test_strict_budget_no_relaxation(self):
        with self.assertRaises(ValueError):
            check_inputs(self.source,self.parent,self.manifest,budget=.002)

    def test_forged_source_bytes_rejected(self):
        with self.assertRaises(ValueError):
            check_inputs(self.source[:-1]+b'x',self.parent,self.manifest,budget=BUDGET_MM)

    def test_forged_parent_bytes_rejected(self):
        with self.assertRaises(ValueError):
            check_inputs(self.source,self.parent+b'\n',self.manifest,budget=BUDGET_MM)

    def test_forged_parent_manifest_rejected(self):
        forged=deepcopy(self.manifest)
        forged['combined_patches']=160
        with self.assertRaises(ValueError):
            check_inputs(self.source,self.parent,forged,budget=BUDGET_MM)

    def test_forged_hole_provenance_rejected(self):
        forged=deepcopy(self.manifest)
        forged['original_step_218_hole_patch_ids_unchanged']=False
        with self.assertRaises(ValueError):
            check_inputs(self.source,self.parent,forged,budget=BUDGET_MM)

    def test_unknown_target_face_rejected(self):
        with self.assertRaises(ValueError):
            build_candidate(self.source,self.native,self.parent,self.manifest,faces=(123456,))

    def test_duplicate_target_face_rejected(self):
        with self.assertRaises(ValueError):
            build_candidate(self.source,self.native,self.parent,self.manifest,faces=(3044,3044))

    def test_candidate_digest_is_pinned_by_receipt(self):
        self.assertEqual(sha256(self.single.encode()).hexdigest(),self.receipt['candidate_bp_sha256'])

    def test_receipt_classification_is_not_automatic(self):
        self.assertEqual(self.receipt['classification'],'CANDIDATE_NOT_NATIVE_ADMITTED')
        self.assertFalse(self.audit['continuous_trim_hausdorff_certified'])
        self.assertEqual(self.audit['apmesh_cpp_tri_quad'],'NOT_RUN')


if __name__=='__main__':
    unittest.main()
