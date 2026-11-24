"""Hermetic tests for source/published topology and actual QUAD reference gates."""
import csv
import hashlib
import io
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np
from thingi10k_f18_quad_reference_gate import (
    MAX_BYTES, audit_quad_index_topology, build_published_comparison,
    conditional_euler, inspect_actual_reference, normalize_source_catalog,
    parse_obj_quad, published_rows, read_quad_npz,
)

IDS_V_F = (
    (44503,18937,19130),(128001,56309,56162),(58012,113799,113879),
    (61394,38038,37730),(67792,16615,16735),(69975,22629,22563),
    (81877,35185,35305),(94884,47116,47466),(230923,45410,45398),
    (364256,70060,68905),(423069,60804,60624),(498974,376509,380068),
)

def rows():
    return {x:{"file_id":x,"published_vertices":v,"published_faces":f} for x,v,f in IDS_V_F}


def catalog():
    cat=[]
    for model_id,_,_ in IDS_V_F:
        # Default cases are deliberately missing clean-surface evidence.
        cat.append(dict(id=model_id,vertices=100,faces=200,closed=False,
                        edge_manifold=True,vertex_manifold=True,single_component=True,
                        pwn=True,degenerate_faces=False,duplicated_faces=False))
    expected={58012:(9090,18340),67792:(17280,34800),81877:(123047,246334),94884:(23224,47148)}
    for v in cat:
        if v['id'] in expected:
            v['vertices'],v['faces']=expected[v['id']]
            v['closed']=True
    return cat


def cube():
    v=[(0,0,0),(1,0,0),(1,1,0),(0,1,0),
       (0,0,1),(1,0,1),(1,1,1),(0,1,1)]
    f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return v,f


def torus(n=5,m=4):
    v=[]
    for i in range(n):
        u=2*math.pi*i/n
        for j in range(m):
            z=2*math.pi*j/m
            v.append(((3+math.cos(z))*math.cos(u),(3+math.cos(z))*math.sin(u),math.sin(z)))
    faces=[]
    for i in range(n):
        for j in range(m):
            a=lambda i,j:(i%n)*m+(j%m)
            faces.append((a(i,j),a(i+1,j),a(i+1,j+1),a(i,j+1)))
    return v,faces


def make_roster(path):
    with path.open('w',encoding='utf-8',newline='') as s:
        w=csv.DictWriter(s,fieldnames=['thingi10k_file_id','literature_cohort','published_quad_vertices','published_quad_faces'])
        w.writeheader()
        for x,v,f in IDS_V_F:
            w.writerow(dict(thingi10k_file_id=x,literature_cohort='QUADWILD_FIG29',published_quad_vertices=v,published_quad_faces=f))


def write_obj(path,v,f):
    lines=[f'v {x} {y} {z}' for x,y,z in v]
    lines += ['f '+' '.join(str(i+1) for i in face) for face in f]
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PublishedTopologyTests(unittest.TestCase):
    def test_01_exact_twelve_roster(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'roster.csv';make_roster(path)
            self.assertEqual(set(published_rows(path)),set(rows()))
    def test_02_source_vs_paper_four_conditional_matches(self):
        x=build_published_comparison(rows(),catalog())
        self.assertEqual(x['source_vs_published_euler_conditional_matches'],4)
        self.assertEqual(x['actual_quad_outputs_read'],0)
        self.assertEqual([y['file_id'] for y in x['cases'] if y['published_output_euler_compatible_with_source']],[58012,67792,81877,94884])
    def test_03_independently_audited_canopy_euler(self):
        raw={'raw_stl_audits':[{'thingi10k_file_id':58012,'raw_stl_sha256':'2c7c322af76b46a307e67af451ebba9e6609e6932a2829f4c596853dbf122d4b','topology':dict(source_unique_exact_vertices=9090,source_unique_exact_edges=27510,source_triangles=18340,boundary_edges=0,three_plus_edges=0,vertex_link_singular=0,vertex_connected_components=1,zero_area_triangles=0,raw_duplicate_triangles=0,edge_winding_conflicts=0)}]}
        x=build_published_comparison(rows(),catalog(),raw)
        canopy=next(y for y in x['cases'] if y['file_id']==58012)
        self.assertEqual(canopy['source_euler'],-80)
        self.assertEqual(canopy['hypothetical_closed_connected_orientable_genus'],41)
        self.assertEqual(canopy['source_euler_evidence'],'AUDITED_EXACT_COORDINATE_STL')
        self.assertEqual(x['original_stl_audited_and_source_euler_match_count'],1)
    def test_04_no_false_genus_from_positive_euler_147(self):
        x=conditional_euler(56309,56162)
        self.assertIsNone(x['hypothetical_closed_connected_orientable_genus'])
        self.assertFalse(x['closed_connected_orientable_possible_by_counts'])
    def test_05_no_half_integer_genus(self):
        x=conditional_euler(18937,19130)
        self.assertIsNone(x['hypothetical_closed_connected_orientable_genus'])
    def test_06_catalog_flags_do_not_verify_actual_topology(self):
        row=next(x for x in catalog() if x['id']==58012)
        x=normalize_source_catalog(row)
        self.assertEqual(x['conditional_source_euler'],-80)
        self.assertFalse(x['source_topology_independently_verified'])
    def test_07_nonmanifold_catalog_does_not_infer_genus(self):
        row=catalog()[3];row['vertex_manifold']=False
        self.assertIsNone(normalize_source_catalog(row)['conditional_source_genus'])
    def test_08_catalog_missing_rights_fails_no_silent_pass(self):
        with self.assertRaises(ValueError):normalize_source_catalog({'id':58012,'faces':1,'vertices':1})
    def test_09_duplicate_catalog_model_fails(self):
        cs=catalog();cs[1]['id']=cs[0]['id']
        with self.assertRaises(ValueError):build_published_comparison(rows(),cs)
    def test_10_missing_catalog_model_fails(self):
        with self.assertRaises(ValueError):build_published_comparison(rows(),catalog()[:-1])
    def test_11_missing_published_row_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'f.csv';make_roster(p)
            s=p.read_text();p.write_text('\n'.join(s.splitlines()[:-1])+'\n')
            with self.assertRaises(ValueError):published_rows(p)
    def test_12_duplicate_published_row_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'f.csv';make_roster(p)
            s=p.read_text().splitlines();p.write_text('\n'.join(s+[s[-1]])+'\n')
            with self.assertRaises(ValueError):published_rows(p)

    def test_33_bad_real_source_cannot_fallback_to_clean_catalog(self):
        raw={'raw_stl_audits':[{'thingi10k_file_id':58012,
            'raw_stl_sha256':'2c7c322af76b46a307e67af451ebba9e6609e6932a2829f4c596853dbf122d4b',
            'topology':dict(source_unique_exact_vertices=9090,source_unique_exact_edges=27510,source_triangles=18340,
                            boundary_edges=12,three_plus_edges=0,vertex_link_singular=0,
                            vertex_connected_components=1,zero_area_triangles=0,raw_duplicate_triangles=0,edge_winding_conflicts=0)}]}
        x=build_published_comparison(rows(),catalog(),raw)
        canopy=next(y for y in x['cases'] if y['file_id']==58012)
        self.assertIsNone(canopy['source_euler'])
        self.assertEqual(canopy['source_euler_evidence'],'AUDITED_SOURCE_CONTRADICTS_MANIFOLD_CONTRACT')
    def test_34_catalog_source_face_count_conflict_fails(self):
        raw={'raw_stl_audits':[{'thingi10k_file_id':58012,
           'raw_stl_sha256':'f'*64,
           'topology':dict(source_unique_exact_vertices=9,source_unique_exact_edges=9,source_triangles=200)}]}
        with self.assertRaises(ValueError):build_published_comparison(rows(),catalog(),raw)


class RealQuadGateTests(unittest.TestCase):
    def test_13_cube_genus_0_and_six_quads(self):
        v,f=cube();x=audit_quad_index_topology(v,f)
        self.assertEqual((x['vertices'],x['edges'],x['quad_faces'],x['euler'],x['genus_if_valid']),(8,12,6,2,0))
        self.assertTrue(x['closed_connected_orientable_combinatorial'])
        self.assertEqual(x['singular_vertex_links'],0)
    def test_14_torus_genus_1(self):
        v,f=torus();x=audit_quad_index_topology(v,f)
        self.assertEqual((x['vertices'],x['edges'],x['quad_faces'],x['genus_if_valid']),(20,40,20,1))
        self.assertEqual(x['valence_4_irregular_vertex_count'],0)
        self.assertTrue(x['closed_quad_gauss_bonnet_parity_pass'])
    def test_15_open_quad_not_closed(self):
        v,f=cube();x=audit_quad_index_topology(v,f[:-1])
        self.assertFalse(x['closed_connected_orientable_combinatorial'])
        self.assertIsNone(x['genus_if_valid'])
        self.assertGreater(x['edge_incidence_counts'][1],0)
    def test_16_nonmanifold_three_face_edge_detected(self):
        v,f=cube();f.append((0,1,5,6))
        x=audit_quad_index_topology(v,f)
        self.assertFalse(x['closed_connected_orientable_combinatorial'])
        self.assertGreater(x['edge_incidence_counts'].get(3,0),0)
    def test_17_two_cubes_glued_at_one_vertex_has_singular_link(self):
        v,f=cube()
        w,g=cube()
        # Reuse one indexed vertex but keep both shells otherwise separate.
        offset=len(v)-1
        v2=v+[(x+2,y+2,z+2) for x,y,z in w[1:]]
        g2=[tuple(0 if i==0 else i+offset for i in q) for q in g]
        x=audit_quad_index_topology(v2,f+g2)
        self.assertEqual(x['face_components'],2)
        self.assertGreater(x['singular_vertex_links'],0)
    def test_18_duplicate_face_fails_closed(self):
        v,f=cube()
        with self.assertRaises(ValueError):audit_quad_index_topology(v,f+[f[0]])
    def test_19_repeated_index_fails(self):
        v,f=cube();f[1]=(4,4,6,7)
        with self.assertRaises(ValueError):audit_quad_index_topology(v,f)
    def test_20_out_of_bounds_index_fails(self):
        v,f=cube();f[0]=(0,3,2,100)
        with self.assertRaises(ValueError):audit_quad_index_topology(v,f)
    def test_21_unused_vertex_fails(self):
        v,f=cube();v.append((99,99,99))
        with self.assertRaises(ValueError):audit_quad_index_topology(v,f)
    def test_22_winding_conflict_detected(self):
        v,f=cube();f[0]=tuple(reversed(f[0]))
        x=audit_quad_index_topology(v,f)
        self.assertGreater(x['orientation_conflicts'],0)
        self.assertFalse(x['closed_connected_orientable_combinatorial'])
    def test_23_obj_negative_indices_valid(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'58012.obj'
            p.write_text('v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\nf -4 -3 -2 -1\n')
            _,f=parse_obj_quad(p)
            self.assertEqual(f[0],(0,1,2,3))
    def test_24_obj_triangle_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'58012.obj'
            p.write_text('v 0 0 0\nv 1 0 0\nv 1 1 0\nf 1 2 3\n')
            with self.assertRaises(ValueError):parse_obj_quad(p)
    def test_25_obj_nan_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'58012.obj'
            p.write_text('v nan 0 0\n')
            with self.assertRaises(ValueError):parse_obj_quad(p)
    def test_26_actual_file_sha_must_match(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'58012_quadrangulation_smooth.obj'
            v,f=cube();write_obj(p,v,f)
            with self.assertRaises(ValueError):inspect_actual_reference(p,58012,'0'*64,rows()[58012],'1'*64)
    def test_27_wrong_file_id_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'580123_quadrangulation_smooth.obj'
            v,f=cube();digest=write_obj(p,v,f)
            with self.assertRaises(ValueError):inspect_actual_reference(p,58012,digest,rows()[58012],'1'*64)
    def test_28_real_obj_with_wrong_paper_count_cannot_claim_comparison(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'58012_quadrangulation_smooth.obj'
            v,f=cube();digest=write_obj(p,v,f)
            x=inspect_actual_reference(p,58012,digest,rows()[58012],'1'*64)
            self.assertFalse(x['published_vertex_face_counts_match'])
            self.assertFalse(x['reference_pair_accepted_for_fair_comparison'])
            self.assertEqual(x['raw_quad_topology']['genus_if_valid'],0)
    def test_29_npz_pure_quad_arrays(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'58012.npz';v,f=cube()
            np.savez(p,vertices=np.array(v,float),faces=np.array(f,int))
            vv,ff=read_quad_npz(p)
            self.assertEqual(len(vv),8)
            self.assertEqual(audit_quad_index_topology(vv,ff)['genus_if_valid'],0)
    def test_30_npz_triangles_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'58012.npz';v,f=cube()
            np.savez(p,vertices=np.array(v),faces=np.array([q[:3] for q in f]))
            with self.assertRaises(ValueError):read_quad_npz(p)
    def test_31_npz_pickle_data_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'58012.npz';v,f=cube()
            np.savez(p,vertices=np.array([{'x':1}],dtype=object),faces=np.array(f))
            with self.assertRaises(ValueError):read_quad_npz(p)
    def test_32_source_sha_is_required(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'58012.obj';v,f=cube();digest=write_obj(p,v,f)
            with self.assertRaises(ValueError):inspect_actual_reference(p,58012,digest,rows()[58012],'invalid')


if __name__ == '__main__':
    unittest.main()
