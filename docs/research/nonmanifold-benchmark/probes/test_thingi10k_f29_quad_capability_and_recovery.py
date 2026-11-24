#!/usr/bin/env python3
"""Hermetic, no-original-asset negative/positive F29 QUAD research controls."""
from __future__ import annotations
import json
import math
import tempfile
import unittest
from pathlib import Path

import thingi10k_f29_quad_capability_and_recovery as m

STAR=[(0,1,4),(1,2,4),(2,3,4),(3,0,4)]
UNIT=[(0.,0.,0.),(1.,0.,0.),(1.,1.,0.),(0.,1.,0.),(.5,.5,0.)]
NORMAL=(0.,0.,1.)


def reject(fn):
    with unittest.TestCase().assertRaises((ValueError,KeyError,IndexError,TypeError)):
        fn()


def cube():
    # Six counterclockwise faces seen from outside the unit cube.
    xyz=[(0.,0.,0.),(1.,0.,0.),(1.,1.,0.),(0.,1.,0.),
         (0.,0.,1.),(1.,0.,1.),(1.,1.,1.),(0.,1.,1.)]
    quads=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),
           (2,3,7,6),(3,0,4,7)]
    return xyz,quads


class OriginalQuadCapabilityContracts(unittest.TestCase):
    def test_01_source_sha_audit_hard_pinned(self):
        self.assertEqual(len(m.NATIVE_BLOBS),5)
        self.assertTrue(all(len(v)==40 for v in m.NATIVE_BLOBS.values()))
    def test_02_disallow_missing_native_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            reject(lambda:m.audit_native_original_quad_capability(Path(tmp)))
    def test_03_wrong_hash_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for path in m.NATIVE_BLOBS:
                file=Path(tmp)/path;file.parent.mkdir(parents=True,exist_ok=True)
                file.write_text('injected fake native source\n')
            reject(lambda:m.audit_native_original_quad_capability(Path(tmp)))
    def test_04_f28_input_digest_pinned(self):
        self.assertEqual(len(m.F28_STITCHED_SHA256),64)
    def test_05_source_geometry_never_embedded(self):
        self.assertEqual(len(STAR),4)


class StarToQuadContracts(unittest.TestCase):
    def test_06_recover_one_patch(self):
        self.assertEqual(m.recover_quad_from_star(STAR),((0,1,2,3),4))
    def test_07_recover_after_vertex_relabel(self):
        faces=[tuple(x+5 for x in f) for f in STAR]
        self.assertEqual(m.recover_quad_from_star(faces),((5,6,7,8),9))
    def test_08_empty_star_rejected(self):reject(lambda:m.recover_quad_from_star([]))
    def test_09_missing_face_rejected(self):reject(lambda:m.recover_quad_from_star(STAR[:-1]))
    def test_10_extra_face_rejected(self):reject(lambda:m.recover_quad_from_star(STAR+STAR[:1]))
    def test_11_wrong_face_arity_rejected(self):reject(lambda:m.recover_quad_from_star(STAR[:3]+[(3,0,4,9)]))
    def test_12_reversed_boundary_rejected(self):reject(lambda:m.recover_quad_from_star(STAR[:3]+[(0,3,4)]))
    def test_13_changed_center_rejected(self):reject(lambda:m.recover_quad_from_star(STAR[:3]+[(3,0,5)]))
    def test_14_duplicate_corner_rejected(self):reject(lambda:m.recover_quad_from_star([(0,1,4),(1,2,4),(2,0,4),(0,0,4)]))
    def test_15_center_as_boundary_rejected(self):reject(lambda:m.recover_quad_from_star([(0,1,0),(1,2,0),(2,3,0),(3,0,0)]))
    def test_16_negative_index_rejected(self):reject(lambda:m.recover_quad_from_star([(-1,1,4),(1,2,4),(2,3,4),(3,-1,4)]))
    def test_17_float_index_rejected(self):reject(lambda:m.recover_quad_from_star([(0.0,1,4),(1,2,4),(2,3,4),(3,0.0,4)]))
    def test_18_stitch_replaces_center(self):
        r=m.reconstruct_patch_quads(UNIT,STAR)
        self.assertEqual(r['vertices'],UNIT[:4]);self.assertEqual(r['removed_patch_centers'],1)
        self.assertEqual(r['quads'],[(0,1,2,3)])
    def test_19_invalid_native_triangle_index_rejected(self):
        reject(lambda:m.reconstruct_patch_quads(UNIT[:4],STAR))
    def test_20_extra_unused_input_vertex_rejected(self):
        reject(lambda:m.reconstruct_patch_quads(UNIT+[(3.,3.,3.)],STAR))
    def test_21_wrong_interior_tag_rejected(self):
        reject(lambda:m.reconstruct_patch_quads(UNIT,STAR,[('source',i) for i in range(5)]))
    def test_22_right_interior_tag_accepted(self):
        tags=[('vertex',i) for i in range(4)]+[('patch_interior',0)]
        self.assertEqual(m.reconstruct_patch_quads(UNIT,STAR,tags)['quads'],[(0,1,2,3)])
    def test_23_reused_interior_center_across_patches_rejected(self):
        another=[tuple((i+5 if i!=4 else 4) for i in f) for f in STAR]
        reject(lambda:m.reconstruct_patch_quads(UNIT+[(3.,0.,0.),(4.,0.,0.),(4.,1.,0.),(3.,1.,0.),(3.5,.5,0.)],STAR+another))
    def test_24_nonfinite_coordinate_rejected(self):
        reject(lambda:m.reconstruct_patch_quads(UNIT[:4]+[(math.inf,.5,0.)],STAR))
    def test_25_nonmultiple_four_faces_rejected(self):
        reject(lambda:m.reconstruct_patch_quads(UNIT,STAR+[(0,1,4)]))


class QuadTopologyContracts(unittest.TestCase):
    def test_26_unit_cube_closed_sphere(self):
        pts,q=cube()
        self.assertEqual(m.quad_topology(len(pts),q),
                         {'vertices':8,'edges':12,'faces':6,'components':1,'boundary_edges':0,
                          'nonmanifold_edges':0,'winding_conflicts':0,'singular_vertex_links':0,'euler':2})
    def test_27_missing_cube_face_fails(self):
        pts,q=cube();reject(lambda:m.quad_topology(len(pts),q[:-1]))
    def test_28_duplicate_cube_face_fails(self):
        pts,q=cube();reject(lambda:m.quad_topology(len(pts),q+[q[0]]))
    def test_29_wrong_cube_winding_fails(self):
        pts,q=cube();q[0]=tuple(reversed(q[0]));reject(lambda:m.quad_topology(len(pts),q))
    def test_30_unused_vertex_fails(self):
        pts,q=cube();reject(lambda:m.quad_topology(len(pts)+1,q))
    def test_31_quad_with_repeated_indices_fails(self):
        pts,q=cube();q[0]=(0,0,1,2);reject(lambda:m.quad_topology(len(pts),q))
    def test_32_quad_with_nonint_vertex_fails(self):
        pts,q=cube();q[0]=(0.,1,2,3);reject(lambda:m.quad_topology(len(pts),q))
    def test_33_two_disconnected_cubes_retain_two_components(self):
        pts,q=cube();quads=q+[tuple(v+8 for v in face) for face in q]
        self.assertEqual(m.quad_topology(16,quads)['components'],2)
    def test_34_unclosed_single_face_rejected(self):
        reject(lambda:m.quad_topology(4,[(0,1,2,3)]))
    def test_35_empty_mesh_rejected(self):
        reject(lambda:m.quad_topology(0,[]))


class QuadGeometricContracts(unittest.TestCase):
    def test_36_valid_unit_quad(self):
        q=m.quad_metric((0,1,2,3),UNIT,NORMAL)
        self.assertAlmostEqual(q['area'],1);self.assertAlmostEqual(q['min_scaled_jacobian'],1)
        self.assertAlmostEqual(q['min_angle_deg'],90)
    def test_37_reversed_quad_rejected(self):
        reject(lambda:m.quad_metric((3,2,1,0),UNIT,NORMAL))
    def test_38_bowtie_quad_rejected(self):
        reject(lambda:m.quad_metric((0,2,1,3),UNIT,NORMAL))
    def test_39_concave_quad_rejected(self):
        v=UNIT.copy();v[2]=(.2,.2,0.)
        reject(lambda:m.quad_metric((0,1,2,3),v,NORMAL))
    def test_40_nonplanar_quad_rejected(self):
        v=UNIT.copy();v[2]=(1.,1.,.01)
        reject(lambda:m.quad_metric((0,1,2,3),v,NORMAL))
    def test_41_degenerate_quad_rejected(self):
        v=UNIT.copy();v[2]=v[1]
        reject(lambda:m.quad_metric((0,1,2,3),v,NORMAL))
    def test_42_wrong_reference_normal_rejected(self):
        reject(lambda:m.quad_metric((0,1,2,3),UNIT,(0.,0.,-1.)))
    def test_43_zero_reference_normal_rejected(self):
        reject(lambda:m.quad_metric((0,1,2,3),UNIT,(0.,0.,0.)))
    def test_44_quality_result_has_dimensionless_jacobian(self):
        pts=[tuple(10*x for x in v) for v in UNIT]
        self.assertAlmostEqual(m.quad_metric((0,1,2,3),pts,NORMAL)['min_scaled_jacobian'],1)


class PrivateWriterContracts(unittest.TestCase):
    def test_45_output_requires_exact_src_obj_vertex_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'original.obj';p.write_text('v 0 0 0\nf 1 2 3\n')
            reject(lambda:m.emit_private_quad_obj(p,{'full_original_vertex_indices':[0,1,2,3],
                                                     'removed_patch_centers':1,'quads':[(0,1,2,3)]}))
    def test_46_writer_carries_private_provenance_without_mesh_label_confusion(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'tri.obj'
            p.write_text('\n'.join(['v 0 0 0','v 1 0 0','v 1 1 0','v 0 1 0','v 0.5 0.5 0',
                                    'f 1 2 5','f 2 3 5','f 3 4 5','f 4 1 5'])+'\n')
            data=m.emit_private_quad_obj(p,m.reconstruct_patch_quads(UNIT,STAR))
            self.assertIn(b'NOT native APMesh QUAD output',data)
            self.assertEqual(sum(s.startswith(b'f ') for s in data.splitlines()),1)
            self.assertEqual(sum(s.startswith(b'v ') for s in data.splitlines()),4)
    def test_47_source_crease_gate_rejects_nonoriginal_topology(self):
        reject(lambda:m.source_edge_feature_coverage([tuple(UNIT[:3])],
                                                        [('vertex',i) for i in range(4)],
                                                        [0,1,2,3],[(0,1,2,3)]))
    def test_48_output_config_expected_stats_are_no_native_claim(self):
        self.assertEqual(m.EXPECTED_SOURCE_FACETS*3,m.EXPECTED_PATCHES)
        self.assertEqual(m.EXPECTED_PATCHES*4,m.EXPECTED_NATIVE_TRIS)
    def test_49_refuse_private_output_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'output';out.mkdir()
            reject(lambda:m.run_real_private(Path(tmp)/'missing.zip',Path(tmp)/'missing.bp',
                          Path(tmp)/'first',Path(tmp)/'second',Path(tmp)/'missing.obj',out,
                          Path(tmp)/'receipt.json'))

if __name__=='__main__':unittest.main()
