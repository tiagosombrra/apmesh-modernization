#!/usr/bin/env python3
"""S3.V strict native-trim adversarial gates for original byte-pinned S40."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface

from audit_analytic_bp import read_bp
from s3c_step_source_gate import entity, oriented_edges
from s3r_s40_conforming_hole_join import _edge_adjacency
from s3s_full_original_face_census import full_correspondence
from s3v_s40_curved_planar_closure import (
    BASELINE_SHA, BUDGET_MM, SOURCE_SHA, TARGETS, EXPECTED_NATIVE,
    SOURCE_SIDE_PATCH_IDS, SOURCE_NEIGHBOR_FACES,
    audit_native, build_extension, quadrangulate_source_boundary,
    source_boundary_sides, verify_source_and_atlas,
)


class OriginalS40CurvedPlanarGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assets = Path(os.environ['APMESH_S3V_PRIVATE_DIR'])
        cls.source_path = Path(os.environ['APMESH_ORIGINAL_CAD_DIR']) / 'i25o_s40.step'
        cls.source=cls.source_path.read_bytes()
        cls.baseline=(assets/'s40_planar_octagons.partial.bp').read_bytes()
        cls.manifest=json.loads((assets/'s40_planar_octagons_manifest.json').read_text())
        cls.native=cq.importers.importStep(str(cls.source_path)).val()
        cls.table,cls.points,cls.patches=verify_source_and_atlas(cls.source,cls.baseline,cls.manifest)
        cls.adj=_edge_adjacency(cls.patches)
        cls.mapping=full_correspondence(cls.source.decode(),cls.native)
        cls.joined,cls.receipt=build_extension(cls.source,cls.baseline,cls.manifest,cls.native)
        cls.audit=audit_native(cls.source,cls.baseline,cls.manifest,cls.native,cls.joined,cls.receipt)

    def test_original_source_hash(self):
        self.assertEqual(sha256(self.source).hexdigest(),SOURCE_SHA)

    def test_original_baseline_hash(self):
        self.assertEqual(sha256(self.baseline).hexdigest(),BASELINE_SHA)

    def test_source_native_mapping_complete(self):
        self.assertEqual((len(self.mapping['face_map']),len(self.mapping['edge_map']),len(self.mapping['vertex_map'])),(43,117,77))

    def test_source_native_face_ids(self):
        for sid,nid in EXPECTED_NATIVE.items():
            with self.subTest(face=sid):
                self.assertEqual(self.mapping['face_map'][sid],nid)
                self.assertEqual(self.native.Faces()[nid].geomType(),'PLANE')

    def test_degree_five_source_curves(self):
        for eid in (85,2096):
            with self.subTest(edge=eid):
                kind,body=entity(self.table,eid,'EDGE_CURVE')
                # The master curve is defined by a degree-five B-spline entity.
                wire=next(e for sid in TARGETS for e in oriented_edges(self.table,sid)[1][0] if e['edge_curve_id']==eid)
                self.assertEqual(wire['master_3d_curve'],'B_SPLINE_CURVE_WITH_KNOTS')

    def test_source_neighbor_incidence(self):
        for fid,edges in SOURCE_NEIGHBOR_FACES.items():
            for eid,owner in edges.items():
                with self.subTest(face=fid,edge=eid):
                    self.assertEqual(self.mapping['owners'][eid],{fid,owner})

    def test_one_outer_wire_and_four_original_edges_each(self):
        for fid in TARGETS:
            with self.subTest(face=fid):
                kind,wires=oriented_edges(self.table,fid)
                self.assertEqual((kind,len(wires),len(wires[0])),('PLANE',1,4))
                self.assertEqual(len(set(e['edge_curve_id'] for e in wires[0])),4)

    def test_boundary_has_eighteen_exact_old_indexed_sides(self):
        for fid in TARGETS:
            sides=source_boundary_sides(fid,self.table,self.points,self.patches,self.adj)
            self.assertEqual(len(sides),18)
            for eid,ids in sides:
                self.assertEqual(len(self.adj[tuple(sorted(ids))]),1)

    def test_each_source_edge_boundary_chain_is_connected(self):
        for fid in TARGETS:
            sides=source_boundary_sides(fid,self.table,self.points,self.patches,self.adj)
            self.assertTrue(all(a[1][-1]==b[1][0] for a,b in zip(sides,sides[1:]+sides[:1])))

    def test_original_split_profiles_preserved(self):
        self.assertEqual(self.receipt['faces']['17']['source_edge_segment_counts'],{'21':9,'57':1,'85':7,'193':1})
        self.assertEqual(self.receipt['faces']['2092']['source_edge_segment_counts'],{'2096':8,'2201':1,'2042':8,'2223':1})

    def test_eight_convex_quads_per_face(self):
        for fid in TARGETS:
            face=self.native.Faces()[EXPECTED_NATIVE[fid]]
            sides=source_boundary_sides(fid,self.table,self.points,self.patches,self.adj)
            cells,summary=quadrangulate_source_boundary(self.points,sides,face)
            self.assertEqual(len(cells),8)
            self.assertAlmostEqual(summary['source_uv_polygon_area'],summary['source_quad_uv_area'],places=7)

    def test_new_candidate_is_148_patches_with_1619_controls(self):
        pts,patches=read_bp(self.joined)
        self.assertEqual((len(pts),len(patches)),(1619,148))

    def test_exact_indexed_seams_and_open_boundaries(self):
        pts,patches=read_bp(self.joined)
        adj=_edge_adjacency(patches)
        self.assertEqual((sum(len(z)==2 for z in adj.values()),sum(len(z)==1 for z in adj.values())),(239,114))
        self.assertFalse(any(len(z)>2 for z in adj.values()))

    def test_existing_atlas_is_exactly_unchanged(self):
        p0,q0=read_bp(self.baseline.decode())
        p1,q1=read_bp(self.joined)
        self.assertEqual((p1[:len(p0)],q1[:len(q0)]),(p0,q0))
        self.assertTrue(self.receipt['original_hole_218_preserved'])

    def test_new_candidate_hash_is_reproducible(self):
        self.assertEqual(sha256(self.joined.encode()).hexdigest(),self.receipt['new_bp_sha256'])

    def test_original_native_interiors_all_in(self):
        self.assertEqual(self.audit['native_interior_IN'],1296)
        self.assertEqual(self.audit['per_face']['17']['native_interior_IN'],648)
        self.assertEqual(self.audit['per_face']['2092']['native_interior_IN'],648)

    def test_original_native_boundary_rejects_specific_spline_curves(self):
        self.assertEqual(self.audit['native_boundary_IN_or_ON']+self.audit['native_boundary_OUT'],704)
        self.assertEqual(self.audit['native_boundary_OUT'],135)
        self.assertEqual(self.audit['native_strict_boundary_OUT_by_original_edge'],{'85':63,'2096':72})
        self.assertEqual(self.audit['native_strict_boundary_OUT_on_derived_diagonal'],0)

    def test_spline_errors_below_experimental_budget_do_not_imply_admission(self):
        self.assertTrue(self.audit['within_original_experimental_1e-3_mm_curve_budget'])
        self.assertLess(self.audit['maximum_original_native_edge_distance_mm'], BUDGET_MM)
        self.assertGreater(self.audit['maximum_original_native_edge_distance_mm'],0)
        self.assertEqual(self.audit['native_original_edge_samples'],396)
        self.assertFalse(self.audit['strict_native_trim_membership_pass'])
        self.assertEqual(self.audit['status'],'BLOCKED_NATIVE_TRIM_BOUNDARY')

    def test_new_planar_support_deviation_below_strict_threshold(self):
        self.assertLess(self.audit['max_native_plane_support_distance_mm'],1e-7)

    def test_no_production_claims_in_receipt(self):
        self.assertEqual(self.receipt['apmesh_cpp_tri_quad'],'NOT_RUN')
        self.assertEqual(self.receipt['production_cpp_regression'],'NOT_RUN')
        self.assertFalse(self.receipt['continuous_trim_Hausdorff_certified'])

    def test_modified_source_rejected(self):
        with self.assertRaisesRegex(ValueError,'SHA mismatch'):
            verify_source_and_atlas(self.source+b' ',self.baseline,self.manifest)

    def test_modified_previous_bp_rejected(self):
        with self.assertRaisesRegex(ValueError,'BP SHA mismatch'):
            verify_source_and_atlas(self.source,self.baseline+b' ',self.manifest)

    def test_changed_experimental_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,'tolerance modification'):
            verify_source_and_atlas(self.source,self.baseline,self.manifest,budget_mm=0.002)

    def test_forged_previous_manifest_rejected(self):
        forged=deepcopy(self.manifest);forged['source_original_faces_represented']=21
        with self.assertRaisesRegex(ValueError,'manifest changed'):
            verify_source_and_atlas(self.source,self.baseline,forged)

    def test_forged_source_face_owner_rejected(self):
        with patch.dict(SOURCE_NEIGHBOR_FACES[17],{21:2092}):
            with self.assertRaisesRegex(ValueError,'EDGE_CURVE owner identity'):
                build_extension(self.source,self.baseline,self.manifest,self.native)

    def test_removed_inherited_boundary_side_rejected(self):
        with patch.dict(SOURCE_SIDE_PATCH_IDS[17],{85:(64,66,68)}):
            with self.assertRaisesRegex(ValueError,'wrong final endpoint|disconnected|profile'):
                source_boundary_sides(17,self.table,self.points,self.patches,self.adj)

    def test_duplicate_inherited_patch_rejected(self):
        with patch.dict(SOURCE_SIDE_PATCH_IDS[2092],{2096:(88,88,90,91,92,93,94,95)}):
            with self.assertRaisesRegex(ValueError,'Duplicate source boundary side'):
                source_boundary_sides(2092,self.table,self.points,self.patches,self.adj)

    def test_forged_recomputed_receipt_rejected(self):
        fake=deepcopy(self.receipt);fake['combined_patches']=149
        with self.assertRaisesRegex(ValueError,'BP/manifest mismatch'):
            audit_native(self.source,self.baseline,self.manifest,self.native,self.joined,fake)

    def test_forged_generated_bp_rejected(self):
        corrupted=self.joined.replace('1619','1620',1)
        with self.assertRaisesRegex(ValueError,'BP/manifest mismatch'):
            audit_native(self.source,self.baseline,self.manifest,self.native,corrupted,self.receipt)

    def test_non_admitted_candidate_not_merged_with_previous_faces(self):
        self.assertEqual(self.receipt['represented_original_faces'],21)
        self.assertEqual(self.audit['status'],'BLOCKED_NATIVE_TRIM_BOUNDARY')
        self.assertEqual(self.manifest['source_original_faces_represented'],19)


if __name__=='__main__':
    unittest.main()
