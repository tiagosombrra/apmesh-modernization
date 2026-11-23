#!/usr/bin/env python3
"""Hermetic F28 seam-identity, winding, nonmanifold and false-weld tests."""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch as override

import thingi10k_f28_topology_aware_stitch as f28
import thingi10k_f27_native_tri_evidence as f27

# Original synthetic oriented tetrahedron, not any third-party source geometry.
VERTICES = ((0., 0., 0.), (1., 0., 0.), (0., 1., 0.), (0., 0., 1.))
SOURCE = tuple(tuple(VERTICES[i] for i in f) for f in
               ((0, 2, 1), (0, 1, 3), (0, 3, 2), (1, 2, 3)))


def bilinear(corners, u, v):
    a, b, c, d = corners
    return tuple((1-u)*(1-v)*a[k] + u*(1-v)*b[k] + u*v*c[k] + (1-u)*v*d[k]
                 for k in range(3))


def cubic(a, b):
    return (a, tuple((2*x+y)/3 for x,y in zip(a,b)),
            tuple((x+2*y)/3 for x,y in zip(a,b)), b)


def net_for_corners(corners, ids):
    net = [bilinear(corners, i/3, j/3) for j in range(4) for i in range(4)]
    for side, idxs in enumerate(((0,1,2,3), (3,7,11,15),
                                 (12,13,14,15), (0,4,8,12))):
        loc = ((0,1), (1,2), (3,2), (0,3))[side]
        ia, ib = ids[loc[0]], ids[loc[1]]
        a, b = corners[loc[0]], corners[loc[1]]
        seq = cubic(a,b) if ia < ib else cubic(b,a)[::-1]
        for index,point in zip(idxs,seq):net[index] = point
    return [list(p) for p in net]


def synthetic_fixture():
    """Generate a 12-patch closed tetra from private-free handcrafted geometry."""
    original_nodes = list(VERTICES)
    vertex_ids = dict(zip(VERTICES, range(4)))
    mids = {}
    for triangle in SOURCE:
        for j in range(3):
            e = f28.edge_key(triangle[j], triangle[(j+1)%3])
            if e not in mids:
                mids[e] = len(original_nodes)
                original_nodes.append(tuple((a+b)/2 for a,b in zip(*e)))
    centers = []
    for tri in SOURCE:
        centers.append(len(original_nodes))
        original_nodes.append(tuple(sum(x)/3 for x in zip(*tri)))
    curves = {}
    patches, vertices, faces = [], [], []
    for ti, tri in enumerate(SOURCE):
        for sector in range(3):
            pi = 3*ti+sector
            qids = (vertex_ids[tri[sector]],
                    mids[f28.edge_key(tri[sector],tri[(sector+1)%3])],
                    centers[ti],
                    mids[f28.edge_key(tri[(sector+2)%3],tri[sector])])
            corner = tuple(original_nodes[i] for i in qids)
            center = bilinear(corner, .5, .5)
            order = (corner[0],corner[1],corner[3],corner[2],center)
            net = net_for_corners(corner,qids)
            ids=[]
            for j in range(4):
                ek=tuple(sorted((qids[j],qids[(j+1)%4])))
                if ek not in curves:curves[ek]=len(curves)
                ids.append(curves[ek])
            nodeids = [5*pi+j+1 for j in range(5)]
            uv = ((0.,0.),(1.,0.),(0.,1.),(1.,1.),(.5,.5))
            patch_faces = []
            for k,f in enumerate(((0,1,4),(1,3,4),(3,2,4),(2,0,4))):
                patch_faces.append([k]+[[nodeids[i],*uv[i],*order[i]] for i in f])
                faces.append(tuple(5*pi+i for i in f))
            patches.append({'index':pi,'control_points':net,'curves':ids,
                            'nodes':[[nodeids[i],*order[i]] for i in range(5)],
                            'faces':patch_faces})
            vertices.extend(tuple(float(format(x,'.6g')) for x in pos) for pos in order)
    return vertices,faces,patches,SOURCE


class SourceIdentityTests(unittest.TestCase):
    def test_01_tetra_source_has_4_facets(self):
        self.assertEqual(len(SOURCE),4)

    def test_02_topological_source_vertex_tag(self):
        tag,point=f28.source_tag(SOURCE[0],0,(0.,0.),0,0)
        self.assertEqual(tag,('vertex',SOURCE[0][0]))
        self.assertEqual(point,SOURCE[0][0])

    def test_03_topological_edge_midpoint_tag(self):
        tag,point=f28.source_tag(SOURCE[0],0,(1.,0.),0,0)
        self.assertEqual(tag,('edge',f28.edge_key(SOURCE[0][0],SOURCE[0][1])))
        self.assertEqual(point,tuple((a+b)/2 for a,b in zip(SOURCE[0][0],SOURCE[0][1])))

    def test_04_second_midpoint_is_incoming_edge(self):
        tag,_=f28.source_tag(SOURCE[0],0,(0.,1.),0,0)
        self.assertEqual(tag,('edge',f28.edge_key(SOURCE[0][0],SOURCE[0][2])))

    def test_05_source_centroid_tag_distinguishes_triangles(self):
        a,_=f28.source_tag(SOURCE[0],0,(1.,1.),0,0)
        b,_=f28.source_tag(SOURCE[1],0,(1.,1.),1,3)
        self.assertNotEqual(a,b)

    def test_06_patch_interiors_are_not_globally_welded(self):
        a,_=f28.source_tag(SOURCE[0],0,(.5,.5),0,0)
        b,_=f28.source_tag(SOURCE[0],1,(.5,.5),0,1)
        self.assertNotEqual(a,b)

    def test_07_unknown_uv_rejected(self):
        with self.assertRaises(ValueError):
            f28.source_tag(SOURCE[0],0,(.2,.5),0,0)

    def test_08_edge_key_unoriented(self):
        self.assertEqual(f28.edge_key(VERTICES[0],VERTICES[1]),
                         f28.edge_key(VERTICES[1],VERTICES[0]))

    def test_09_disjoint_sets_compress(self):
        d=f28.DisjointSets(4)
        d.union(0,1);d.union(2,3);d.union(0,3)
        self.assertEqual(d.merges,3)
        self.assertEqual(len({d.find(i) for i in range(4)}),1)

    def test_10_duplicate_union_does_not_count(self):
        d=f28.DisjointSets(2);d.union(0,1);d.union(1,0)
        self.assertEqual(d.merges,1)

    def test_11_three_component_union(self):
        d=f28.DisjointSets(5)
        d.union(0,1);d.union(2,3)
        self.assertEqual(len({d.find(i) for i in range(5)}),3)


class OriginalNativeSeamTests(unittest.TestCase):
    def setUp(self):
        self.vertices,self.faces,self.patches,self.source=synthetic_fixture()

    def get_result(self):
        return f28.reconcile_curves(self.vertices,self.faces,self.patches,self.source)

    def test_12_tetra_fixture_counts(self):
        self.assertEqual((len(self.vertices),len(self.faces),len(self.patches)),(60,48,12))

    def test_13_native_topological_stitch_real_semantics(self):
        r=self.get_result()
        self.assertEqual((len(r['vertices']),r['curve_count'],r['merges']),(26,24,34))

    def test_14_stitched_tetra_is_closed(self):
        r=self.get_result()
        topo=f27.topology(len(r['vertices']),r['faces'])
        self.assertEqual((topo['components'],topo['euler'],topo['boundary_edges']),
                         (1,2,0))

    def test_15_no_native_face_or_vertex_coordinate_reordered(self):
        r=self.get_result()
        for original_face,new_face in zip(self.faces,r['faces']):
            self.assertEqual(tuple(self.vertices[i] for i in original_face),
                             tuple(r['vertices'][i] for i in new_face))

    def test_16_every_native_curve_opposite_oriented(self):
        r=self.get_result()
        self.assertEqual(r['native_boundary_orientations'],{'opposite':24})

    def test_17_no_exported_precision_false_aliases(self):
        self.assertEqual(self.get_result()['coord_only_false_alias_groups'],0)

    def test_18_first_patch_has_exact_F27_uv_layout(self):
        by_uv=f28.identify_patch_nodes(self.patches[0],self.source[0],self.vertices[:5],0)
        self.assertEqual(set(by_uv),set(f28.UVS))

    def test_19_incomplete_patch_rejected(self):
        self.patches[0]['faces'].pop()
        with self.assertRaises(ValueError):self.get_result()

    def test_20_node_position_drift_rejected(self):
        self.patches[0]['nodes'][0][1] += .01
        with self.assertRaises(ValueError):self.get_result()

    def test_21_corner_bezier_control_mutation_rejected(self):
        self.patches[0]['control_points'][0][1] += .01
        with self.assertRaises(ValueError):self.get_result()

    def test_22_native_curve_broken_one_patch_identity_rejected(self):
        self.patches[0]['curves'][0] = 100000
        with self.assertRaises(ValueError):self.get_result()

    def test_23_native_curve_three_incidences_rejected(self):
        self.patches[0]['curves'][1] = self.patches[0]['curves'][0]
        with self.assertRaises(ValueError):self.get_result()

    def test_24_shared_curve_control_nearby_but_unauthorized_rejected(self):
        self.patches[0]['control_points'][1][0] += 1e-6
        with self.assertRaises(ValueError):self.get_result()

    def test_25_invalid_native_face_winding_rejected(self):
        self.faces[0] = self.faces[0][::-1]
        with self.assertRaises(ValueError):self.get_result()

    def test_26_unexpected_obj_vertex_number_rejected(self):
        self.vertices.pop()
        with self.assertRaises(ValueError):self.get_result()

    def test_27_unexpected_native_face_count_rejected(self):
        self.faces.pop()
        with self.assertRaises(ValueError):self.get_result()

    def test_28_disjoint_original_corner_identity_rejected(self):
        # Give a shared curve a foreign source identity while keeping its XYZ.
        self.patches[0]['index'] = 2
        with self.assertRaises(ValueError):self.get_result()

    def test_29_missing_patch_node_rejected(self):
        self.patches[0]['nodes'].pop()
        with self.assertRaises(ValueError):self.get_result()

    def test_30_duplicate_native_node_id_rejected(self):
        self.patches[0]['nodes'][1][0] = self.patches[0]['nodes'][0][0]
        with self.assertRaises(ValueError):self.get_result()

    def test_31_uv_mismatch_rejected(self):
        self.patches[0]['faces'][0][1][1] = .2
        with self.assertRaises(ValueError):self.get_result()

    def test_32_shared_curve_orientation_reversal_rejected(self):
        self.patches[0]['control_points'][2][1] += 1e-7
        with self.assertRaises(ValueError):self.get_result()

    def test_33_new_vertices_equal_global_exact_weld_tetra(self):
        r=self.get_result()
        t,duplicates=f27.welded_by_exact_exported_xyz(self.vertices,self.faces)
        self.assertEqual(duplicates, r['merges'])
        self.assertEqual(t,f27.topology(len(r['vertices']),r['faces']))

    def test_34_feature_edges_synthetic_all_confirmed(self):
        r=self.get_result()
        with override.object(f28,'ORIGINAL_STL_EDGES',6),\
             override.object(f28,'EXPECTED_SHARP30',6):
            report=f28.validate_original_feature_edges(self.source,r,{'patches':self.patches})
        self.assertEqual(report['original_crease_edge_segments_confirmed'],12)
        self.assertFalse(report['smoothing_applied'])

    def test_35_crease_missing_face_rejected(self):
        r=self.get_result();r['faces'][0]=(r['faces'][0][0],)*3
        with override.object(f28,'ORIGINAL_STL_EDGES',6),\
             override.object(f28,'EXPECTED_SHARP30',6):
            with self.assertRaises(ValueError):
                f28.validate_original_feature_edges(self.source,r,{'patches':self.patches})

    def test_36_wrong_original_crease_parent_rejected(self):
        r=self.get_result();r['native_face_source_triangles']=[0]*len(r['faces'])
        with override.object(f28,'ORIGINAL_STL_EDGES',6),\
             override.object(f28,'EXPECTED_SHARP30',6):
            with self.assertRaises(ValueError):
                f28.validate_original_feature_edges(self.source,r,{'patches':self.patches})

    def test_37_derived_obj_writer_retains_original_geometry_lines(self):
        r=self.get_result()
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'native.obj'
            path.write_text('# original\n'+'\n'.join('v '+' '.join(map(str,p)) for p in self.vertices)+
                            '\n'+'\n'.join('f '+' '.join(str(i+1) for i in f) for f in self.faces)+'\n')
            output=f28.derived_obj_bytes(path,r)
            self.assertIn(b'NOT original APMesh output',output)
            newpath=Path(temp)/'derived.obj';newpath.write_bytes(output)
            v,faces=f27.parse_obj(newpath)
            self.assertEqual((len(v),len(faces)),(26,48))

    def test_38_private_writer_refuses_wrong_source_coverage(self):
        r=self.get_result();r['original_to_new'].pop()
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'native.obj';path.write_text('# normal\n'+'\n'.join('v 0 0 0' for _ in self.vertices)+'\n')
            with self.assertRaises(ValueError):f28.derived_obj_bytes(path,r)

    def test_39_local_no_overwrite_gate_rejects_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'used';p.mkdir()
            with self.assertRaises(ValueError):
                f28.run_private(Path(temp)/'missing.zip',Path(temp)/'missing.bp',
                                p,p,Path(temp)/'derived',Path(temp)/'receipt.json')

    def test_41_deliberate_disconnected_coincident_source_components_rejected(self):
        # A global-XYZ weld would incorrectly connect these disjoint spheres.
        original_patch_count=len(self.patches)
        original_vertex_count=len(self.vertices)
        original_curves=max(c for p in self.patches for c in p['curves'])+1
        copied=copy.deepcopy(self.patches)
        for item in copied:
            item['index'] += original_patch_count
            item['curves']=[c+original_curves for c in item['curves']]
            for node in item['nodes']:
                node[0]+=original_vertex_count
            for face in item['faces']:
                for row in face[1:]:
                    row[0]+=original_vertex_count
        more_faces=[tuple(i+original_vertex_count for i in f) for f in self.faces]
        with self.assertRaisesRegex(ValueError,'source vertex|source entities|Shared topological'):
            f28.reconcile_curves(self.vertices+self.vertices,
                                 self.faces+more_faces,
                                 self.patches+copied,
                                 self.source+self.source)

    def test_42_unrelated_native_centers_with_same_exported_xyz_rejected(self):
        # Unlike blind XYZ welding, independent local centers never become shared.
        p0,p1=self.patches[0],self.patches[1]
        copied=list(p0['nodes'][4][1:4])
        p1['nodes'][4][1:4]=copied
        self.vertices[9]=tuple(float(format(x,'.6g')) for x in copied)
        for face in p1['faces']:
            for corner in face[1:]:
                if corner[0]==p1['nodes'][4][0]:
                    corner[3:6]=copied
        with self.assertRaisesRegex(ValueError,'Rounded OBJ XYZ|Different source entities'):
            self.get_result()

    def test_43_native_seam_numeric_jitter_within_bound_still_uses_source_identity(self):
        # A permitted small numerical evaluation discrepancy does not authorize new joins.
        self.patches[0]['control_points'][1][1]+=1e-13
        self.assertEqual(self.get_result()['merges'],34)

    def test_44_native_seam_numeric_jitter_above_bound_is_rejected(self):
        self.patches[0]['control_points'][1][1]+=2e-11
        with self.assertRaises(ValueError):self.get_result()

    def test_45_stitch_repeated_in_memory_is_identical(self):
        a=self.get_result()
        b=self.get_result()
        self.assertEqual(a,b)

    def test_46_native_obj_preserves_source_SHA_in_derived_header(self):
        r=self.get_result()
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'native.obj'
            path.write_text('\n'.join('v '+' '.join(map(str,p)) for p in self.vertices)+
                            '\n'+'\n'.join('f '+' '.join(str(i+1) for i in f) for f in self.faces)+'\n')
            b=f28.derived_obj_bytes(path,r)
            self.assertIn(f27.sha256(path).encode('ascii'),b)
            derived=Path(temp)/'derived.obj';derived.write_bytes(b)
            self.assertEqual(len(f27.parse_obj(derived)[1]),48)

    def test_47_full_precision_original_seam_positions_remain_bounded(self):
        r=self.get_result()
        self.assertLessEqual(r['max_source_corner_deviation'],f28.MAX_NATIVE_CORNER_EVAL_ABS)
        self.assertLessEqual(r['max_native_seam_endpoint_disagreement'],f28.MAX_NATIVE_SEAM_EVAL_ABS)
        self.assertLessEqual(r['max_native_shared_control_disagreement'],f28.MAX_NATIVE_SEAM_EVAL_ABS)

    def test_40_mean_quality_invariant(self):
        r=self.get_result()
        q0=[f27.triangle_quality([self.vertices[i] for i in face]) for face in self.faces]
        q1=[f27.triangle_quality([r['vertices'][i] for i in face]) for face in r['faces']]
        self.assertEqual(q0,q1)


if __name__=='__main__':
    unittest.main()
