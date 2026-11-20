#!/usr/bin/env python3
"""Hermetic plus private source-data tests for the S40-F6 four-face pilot."""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import unittest

import s40f6_four_face_source_island as f6
import s40f6_independent_bp_audit as independent

F5_SPEC = os.environ.get('S40_F5_SPEC')
F6_SPEC = os.environ.get('S40_F6_SPEC')
F5_BP = os.environ.get('S40_F5_BP')


def invented_pentagon():
    """Independent synthetic plane fixture with no third-party CAD coordinates."""
    return {'vertices': [31,32,33,34,35],
            'coordinates': [[10,0,0],[10,0,-20],[10,50,-20],[10,50,-10],[10,20,0]],
            'edges': [[51,'LINE'],[52,'LINE'],[53,'LINE'],[54,'LINE'],[55,'LINE']],
            'plane_axis':[1,0,0], 'plane_location':[10,0,0],
            'shared_f5_source_edge':52,'prior_s3y_source_edges':[53]}


class PartitionTests(unittest.TestCase):
    def test_source_five_side_partition(self):
        v=f6.select_source_split(invented_pentagon(),excluded_source_edges={52,53})
        self.assertEqual(len(v['quads']),2)
        self.assertEqual(len(v['expanded_points']),6)
        self.assertNotIn(v['split_edge_id'],{52,53})
        self.assertGreater(v['source_original_face_area'],0)

    def test_determinism(self):
        p=invented_pentagon()
        self.assertEqual(f6.select_source_split(p,excluded_source_edges={52,53}),
                         f6.select_source_split(p,excluded_source_edges={52,53}))

    def test_never_split_frozen_source_edge(self):
        v=f6.select_source_split(invented_pentagon(),excluded_source_edges={51,52,54,55})
        self.assertEqual(v['split_edge_id'],53)

    def test_no_candidate_if_all_source_edges_frozen(self):
        with self.assertRaises(ValueError):
            f6.select_source_split(invented_pentagon(),excluded_source_edges={51,52,53,54,55})

    def test_curve_requires_explicit_separate_builder(self):
        x=invented_pentagon();x['edges'][0][1]='CIRCLE'
        with self.assertRaises(ValueError):
            f6.select_source_split(x,excluded_source_edges={52,53})

    def test_degenerate_source_polygon(self):
        x=invented_pentagon()
        x['coordinates']=[[10,j,0] for j in range(5)]
        with self.assertRaises(ValueError):
            f6.select_source_split(x,excluded_source_edges=set())

    def test_duplicate_vertex_pentagon(self):
        x=invented_pentagon();x['coordinates'][3]=x['coordinates'][1]
        with self.assertRaises(ValueError):
            f6.select_source_split(x,excluded_source_edges={52,53})

    def test_collinear_rejected_by_strict_quad_convexity(self):
        self.assertFalse(f6._is_strictly_convex_quad([(0,0),(1,0),(2,0),(0,1)],1))

    def test_convex_reverse_orientation(self):
        q=[(0,0),(1,0),(1,1),(0,1)]
        self.assertTrue(f6._is_strictly_convex_quad(q,1))
        self.assertTrue(f6._is_strictly_convex_quad(q[::-1],-1))

    def test_cubic_line_endpoints(self):
        a=(1.,2.,3.);b=(4.,5.,6.)
        self.assertEqual(f6.cubic_line(a,b)[0],a)
        self.assertEqual(f6.cubic_line(a,b)[-1],b)

    def test_cubic_line_exact_midpoint(self):
        a=(2.,0.,-1.);b=(-4.,6.,9.)
        self.assertEqual(f6.f5._point_cubic(f6.cubic_line(a,b),0.5),(-1.,3.,4.))

    def test_indexed_bp_roundtrip(self):
        points=[(float(j),0.,0.) for j in range(16)]
        body='\n'.join(['// synthetic only',*('v '+' '.join(map(str,x)) for x in points),
                        'p '+' '.join(map(str,range(16)))])+'\n'
        pts,nets=f6.read_indexed_bp(body)
        self.assertEqual(pts,points)
        self.assertEqual(nets,[tuple(range(16))])
        self.assertEqual(independent.read_bp(body),(pts,nets))

    def test_reject_nonfinite_indexed_bp(self):
        with self.assertRaises(ValueError):f6.read_indexed_bp('v nan 0 0\np '+' '.join(['0']*16)+'\n')

    def test_reject_missing_control_reference(self):
        with self.assertRaises(ValueError):f6.read_indexed_bp('v 0 0 0\np '+' '.join(['2']*16)+'\n')

    def test_reject_forward_index(self):
        with self.assertRaises(ValueError):independent.read_bp('p '+' '.join(['0']*16)+'\nv 0 0 0\n')

    def test_correct_indexed_patch_ccw_side_directions(self):
        x=tuple(range(16))
        expected=[(0,1,2,3),(3,7,11,15),(15,14,13,12),(12,8,4,0)]
        self.assertEqual(independent.edges(x),expected)
        self.assertEqual([f6._directed_side(x,k) for k in ('bottom','right','top','left')],expected)

    def test_coons_interior_number_and_boundary_preservation(self):
        p=[]
        def add(x):p.append(x);return len(p)-1
        bottom=[add((j/3.,0.,0.)) for j in range(4)]
        right=[bottom[-1],add((1.,1/3.,0.)),add((1.,2/3.,0.)),add((1.,1.,0.))]
        top=[right[-1],add((2/3.,1.,0.)),add((1/3.,1.,0.)),add((0.,1.,0.))]
        left=[top[-1],add((0.,2/3.,0.)),add((0.,1/3.,0.)),bottom[0]]
        out=f6.coons_indexed(p,[bottom,right,top,left],add)
        self.assertEqual(len(out),16)
        self.assertEqual(len(p),16)
        self.assertEqual(out[:4],tuple(bottom))
        self.assertEqual(out[3::4],tuple(right))
        self.assertEqual(tuple(reversed(out[-4:])),tuple(top))
        self.assertEqual(tuple(reversed(out[::4])),tuple(left))

    def test_independent_curve_middle(self):
        x=[(0.,0.,0.),(1.,0.,0.),(2.,0.,0.),(3.,0.,0.)]
        self.assertAlmostEqual(independent.cubic(x,0.5)[0],1.5)

    def test_source_hash_rejects_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source.json';p.write_text('{"faces":{}}')
            with self.assertRaises(ValueError):f6.load_f6_spec(p)

    def test_independent_auditor_rejects_missing_bp(self):
        with self.assertRaises(FileNotFoundError):
            independent.audit('/definitely/unavailable.bp','/no/sidecar','/no/old.bp','/no/spec')

    def test_pinned_provenance_declared(self):
        self.assertEqual(f6.SOURCE_SHA,independent.SOURCE_SHA)
        self.assertEqual(f6.F6_SPEC_SHA,independent.EXPECTED_F6_SPEC_SHA)
        self.assertEqual(f6.F5_BP_SHA,independent.EXPECTED_F5_BP_SHA)


@unittest.skipUnless(F5_SPEC and F6_SPEC and F5_BP, 'Private source-derived pilot input not supplied')
class PrivateOriginalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bp,cls.receipt=f6.build_four_face_island(F5_SPEC,F6_SPEC)
        cls.points,cls.patches=independent.read_bp(cls.bp)
        cls.f6_spec=f6.load_f6_spec(F6_SPEC)

    def test_four_faces_eight_patches(self):
        self.assertEqual(len(self.patches),8)
        self.assertEqual(tuple(self.receipt['face_ids_per_patch']),independent.FACES)

    def test_104_controls_and_exacts(self):
        self.assertEqual(len(self.points),104)
        self.assertEqual(self.receipt['indexed_audit']['declared_global_controls'],104)

    def test_six_global_oriented_seams(self):
        self.assertEqual(self.receipt['indexed_audit']['two_sided_seams'],6)
        self.assertTrue(self.receipt['indexed_audit']['all_internal_seams_ccw_reversed'])

    def test_twenty_registered_open_source_sides(self):
        self.assertEqual(len(self.receipt['source_segment_ids']),20)

    def test_source_split_only_on_future_pending_edges(self):
        self.assertEqual(self.receipt['new_reconstructed_faces']['3269']['split_source_edge_id'],3299)
        self.assertEqual(self.receipt['new_reconstructed_faces']['3485']['split_source_edge_id'],3489)

    def test_source_cross_interfaces_not_virtual_proximity(self):
        self.assertEqual(self.receipt['new_reconstructed_faces']['3269']['shared_prior_f5_source_edge_id'],1392)
        self.assertEqual(self.receipt['new_reconstructed_faces']['3485']['shared_prior_f5_source_edge_id'],1365)

    def test_vertical_native_face_audits(self):
        for raw in self.receipt['new_reconstructed_faces'].values():
            stats=raw['native_surrogate_audit']
            self.assertEqual(stats['interior_IN'],450)
            self.assertEqual(stats['boundary_IN_ON'],408)
            self.assertEqual(stats['boundary_OUT'],0)
            self.assertLess(stats['absolute_area_difference'],1e-6)

    def test_source_vertical_normals_orthogonal_to_horizontal(self):
        for face in self.f6_spec.values():
            normal=face['plane_axis'];self.assertAlmostEqual(normal[2],0)
        self.assertAlmostEqual(sum(self.f6_spec[3269]['plane_axis'][i]*self.f6_spec[3485]['plane_axis'][i] for i in range(3)),-1)

    def test_first_five_face_indices_preserved(self):
        old=Path(F5_BP).read_text();orig_points,orig_patches=independent.read_bp(old)
        self.assertEqual(self.points[:len(orig_points)],orig_points)
        self.assertEqual(self.patches[:len(orig_patches)],orig_patches)

    def test_standalone_private_bp_consistent_with_f5_digest(self):
        self.assertEqual(hashlib.sha256(Path(F5_BP).read_bytes()).hexdigest(),f6.F5_BP_SHA)

    def test_independent_audit(self):
        with tempfile.TemporaryDirectory() as folder:
            bp=Path(folder)/'out.bp';bp.write_text(self.bp)
            receipt=Path(folder)/'sidecar.json';receipt.write_text(json.dumps(self.receipt))
            result=independent.audit(bp,receipt,F5_BP,F6_SPEC)
            self.assertEqual(result['new_patch_oriented_jacobian_samples'],36)
            self.assertEqual(len(result['original_source_face_cross_interfaces']),2)

    def test_reject_tampered_bp(self):
        with tempfile.TemporaryDirectory() as folder:
            bp=Path(folder)/'out.bp';bp.write_text(self.bp+'\n')
            receipt=Path(folder)/'sidecar.json';receipt.write_text(json.dumps(self.receipt))
            with self.assertRaises(ValueError):independent.audit(bp,receipt,F5_BP,F6_SPEC)

    def test_reject_unregistered_source_edge(self):
        with tempfile.TemporaryDirectory() as folder:
            bp=Path(folder)/'out.bp';bp.write_text(self.bp)
            altered=copy.deepcopy(self.receipt);altered['source_segment_ids'].pop('new:3299:1')
            receipt=Path(folder)/'sidecar.json';receipt.write_text(json.dumps(altered))
            with self.assertRaises(ValueError):independent.audit(bp,receipt,F5_BP,F6_SPEC)

    def test_not_claim_production_acceptance(self):
        self.assertFalse(self.receipt['original_step_native_import'])
        self.assertFalse(self.receipt['parent_S3Y_joined'])
        self.assertEqual(self.receipt['newly_admitted_original_source_faces'],0)

    def test_exact_serialized_candidate_sha(self):
        self.assertEqual(hashlib.sha256(self.bp.encode()).hexdigest(),self.receipt['bp_sha256'])

    def test_pass_on_local_saved_private_candidate(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'f6.bp';p.write_text(self.bp)
            self.assertEqual(independent.read_bp(p.read_text())[1],self.patches)


if __name__=='__main__': unittest.main()
