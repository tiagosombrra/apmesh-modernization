#!/usr/bin/env python3
"""Independent structural and bounded native-surrogate tests for S40-F5."""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import s40f5_original_source_analytic_pilot as pilot

ROOT=Path(__file__).parent
PRIVATE_SPEC=ROOT/'s40f5_source_spec.PRIVATE.json'


def parse_bp_bytes(data):
    """Independently reject malformed indexed BP input records."""
    vertices=[];patches=[]
    for line in data.decode().splitlines():
        line=line.split('//',1)[0].strip()
        if not line:continue
        fields=line.split()
        if fields[0]=='v':
            if len(fields)!=4:raise ValueError('Malformed control point')
            p=tuple(map(float,fields[1:]))
            if not all(math.isfinite(x) for x in p):raise ValueError('Nonfinite control')
            vertices.append(p)
        elif fields[0]=='p':
            if len(fields)!=17:raise ValueError('Malformed patch')
            ids=tuple(map(int,fields[1:]))
            if not all(0<=x<len(vertices) for x in ids):raise ValueError('Forward or out-of-range index')
            patches.append(ids)
        else:raise ValueError('Unsupported indexed record')
    return vertices,patches


def perimeter(net):
    return [tuple(net[:4]),tuple(net[3::4]),
            tuple(reversed(net[12:16])),tuple(reversed(net[::4]))]


class S40F5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not PRIVATE_SPEC.is_file():
            raise unittest.SkipTest("Original-derived private STEP geometry not installed")
        pilot.load_private_source_spec(PRIVATE_SPEC)
        cls.bp,cls.sidecar=pilot.build_indexed_surrogate()
        cls.vertices,cls.patches=parse_bp_bytes(cls.bp.encode())
        cls.measurements=[pilot.audit_face(fid) for fid in sorted(pilot.SOURCE_DATA)]

    def test_expected_face_ids(self):
        self.assertEqual(set(pilot.SOURCE_DATA),{1279,1386})

    def test_native_surrogate_faces_valid(self):
        for fid in sorted(pilot.SOURCE_DATA):
            face,edges,curves=pilot.reconstruct_face(fid)
            self.assertTrue(face.isValid())
            self.assertEqual(len(edges),6)
            self.assertAlmostEqual(face.normalAt().z,-1.,places=10)

    def test_exact_number_of_indexed_patches(self):
        self.assertEqual(len(self.patches),4)
        self.assertEqual(self.sidecar['patches'],4)

    def test_global_control_count(self):
        self.assertEqual(len(self.vertices),56)
        self.assertEqual(self.sidecar['global_control_points'],56)

    def test_independent_parser_does_not_assume_builder(self):
        self.assertTrue(all(len(p)==16 for p in self.patches))
        self.assertEqual(hashlib.sha256(self.bp.encode()).hexdigest(),self.sidecar['bp_sha256'])

    def test_real_source_edge_lineage(self):
        self.assertEqual(len(self.sidecar['source_edge_control_id_chains']),12)
        for fid in pilot.SOURCE_DATA:
            for eid,kind in pilot.SOURCE_DATA[fid]['edges']:
                ids=self.sidecar['source_edge_control_id_chains'][str(eid)]
                self.assertEqual(len(ids),4)
                self.assertEqual(len(set(ids)),4)

    def test_side_adjacency_both_orientations(self):
        all_sides={}
        for pid,net in enumerate(self.patches):
            for edge in perimeter(net):
                key=tuple(sorted(edge))
                all_sides.setdefault(key,[]).append((pid,edge))
        double=[u for u in all_sides.values() if len(u)==2]
        single=[u for u in all_sides.values() if len(u)==1]
        self.assertEqual(len(double),2)
        self.assertEqual(len(single),12)
        for u in double:
            self.assertEqual(u[0][1],u[1][1][::-1])
            self.assertNotEqual(u[0][0],u[1][0])

    def test_face_areas_near_native_surrogate(self):
        for m in self.measurements:
            self.assertLess(m['relative_area_difference'],1e-5)
            self.assertGreater(m['native_surrogate_area_mm2'],830.)

    def test_no_surrogate_trim_out_samples(self):
        for m in self.measurements:
            self.assertEqual(m['native_surrogate_interior_IN_samples'],450)
            self.assertEqual(m['native_surrogate_boundary_OUT_samples'],0)
            self.assertEqual(m['native_surrogate_boundary_IN_ON_samples'],408)

    def test_signed_normal_orientation(self):
        for m in self.measurements:
            self.assertTrue(all(mx<0 and mn<0 for mn,mx in m['sampled_patch_jacobian_range']))

    def test_two_way_arc_error_within_budget(self):
        for m in self.measurements:
            for edge in m['sampled_arc_errors']:
                self.assertLess(edge['max_sampled_bp_to_curve_mm'],pilot.FIXED_BUDGET_MM)
                self.assertLess(edge['max_sampled_curve_to_bp_mm'],pilot.FIXED_BUDGET_MM)
                self.assertGreater(edge['max_sampled_curve_to_bp_mm'],0.)

    def test_four_source_arcs_only(self):
        self.assertEqual({e['edge'] for m in self.measurements for e in m['sampled_arc_errors']},{1307,1336,1415,1444})

    def test_not_parent_joined(self):
        self.assertEqual(self.sidecar['explicit_indexed_parent_S3Y_joins'],0)
        self.assertEqual(self.sidecar['source_faces_counted_as_admitted'],0)

    def test_source_spec_wrong_hash_rejected(self):
        obj=json.loads(PRIVATE_SPEC.read_text())
        obj['origin_sha256']='0'*64
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'tampered.json'
            p.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):pilot.load_private_source_spec(p)
        pilot.load_private_source_spec(PRIVATE_SPEC)

    def test_source_spec_unknown_face_rejected(self):
        obj=json.loads(PRIVATE_SPEC.read_text())
        obj['faces']['9999']=obj['faces']['1279']
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'tampered.json'
            p.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):pilot.load_private_source_spec(p)
        pilot.load_private_source_spec(PRIVATE_SPEC)

    def test_radius_is_6_mm(self):
        for fid in pilot.SOURCE_DATA:
            f=pilot.SOURCE_DATA[fid]
            for eid,c in f['circle_centers'].items():
                idx=[e[0] for e in f['edges']].index(eid)
                self.assertAlmostEqual(math.dist(f['coordinates'][idx],c),6.,places=8)

    def test_each_original_source_vertex_used_as_control(self):
        face_ids={v for face in pilot.SOURCE_DATA.values() for v in face['vertices']}
        self.assertEqual(len(face_ids),12)

    def test_inward_curve_is_inside_circle(self):
        for fid in pilot.SOURCE_DATA:
            face,edges,curves=pilot.reconstruct_face(fid)
            for eid,c in pilot.SOURCE_DATA[fid]['circle_centers'].items():
                for j in range(1,65):
                    p=pilot._point_cubic(curves[eid],j/65)
                    self.assertLessEqual(math.hypot(p[0]-c[0],p[1]-c[1]),6.+1e-9)

    def test_modified_original_vertex_rejected_by_source_curve(self):
        fid=1279
        f=pilot.SOURCE_DATA[fid]
        old=copy.deepcopy(f['coordinates'][2])
        try:
            f['coordinates'][2]=[22., -73.17767, -33.75]
            with self.assertRaises(ValueError):pilot.reconstruct_face(fid)
        finally:
            f['coordinates'][2]=old

    def test_falsified_private_spec_rejected_even_with_correct_claimed_source_hash(self):
        obj=json.loads(PRIVATE_SPEC.read_text())
        obj['faces']['1279']['coordinates'][2][0]=22.
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'tampered.json'
            p.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):pilot.load_private_source_spec(p)
        pilot.load_private_source_spec(PRIVATE_SPEC)



if __name__=='__main__':unittest.main()
