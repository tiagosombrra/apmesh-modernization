"""Offline boundary, byte-identity, topology, and bicubic F21 candidate tests."""
import hashlib
import io
import json
import math
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

from thingi10k_f21_piecewise_linear_bezier import (
    PIN, Pin, build_patch_domain, collision_counts, controls_for_quad, cross,
    execute, git_blob_sha, jacobian_ratios, length, linear_net, parse_source,
    read_pinned_binary_stl_zip, serialize_bp, source_edges, vec_sub,
    eval_bicubic, bilinear, main, write_private_result,
)


def tetra():
    return [(0,0,0),(1,0,0),(0,1,0),(0,0,1)], [
        (0,2,1), (0,1,3), (1,2,3), (2,0,3)]


def cube():
    v=[(0,0,0),(1,0,0),(1,1,0),(0,1,0),
       (0,0,1),(1,0,1),(1,1,1),(0,1,1)]
    quads=[(0,3,2,1),(4,5,6,7),(0,1,5,4),
           (1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return v, [t for q in quads for t in ((q[0],q[1],q[2]),(q[0],q[2],q[3]))]


def torus(n=6,m=5):
    v=[]
    for i in range(n):
        u=2*math.pi*i/n
        for j in range(m):
            t=2*math.pi*j/m
            v.append(((3+math.cos(t))*math.cos(u),(3+math.cos(t))*math.sin(u),math.sin(t)))
    def idx(i,j):return (i%n)*m+(j%m)
    f=[]
    for i in range(n):
        for j in range(m):
            q=(idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1))
            f.extend(((q[0],q[1],q[2]),(q[0],q[2],q[3])))
    return v,f


def stl_bytes(v,f):
    buf=bytearray(b'unit synthetic geometry'.ljust(80,b'\x00'))
    buf+=struct.pack('<I',len(f))
    for face in f:
        buf+=struct.pack('<12fH',*(0.0,0.0,1.0),*(float(x) for i in face for x in v[i]),0)
    return bytes(buf)


def zip_case(stl,model_id=293137,name=None):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(name or f'{model_id}.stl',stl)
    data=b.getvalue()
    pin=Pin(model_id,git_blob_sha(data),hashlib.sha256(stl).hexdigest(),
            struct.unpack_from('<I',stl,80)[0],len(data))
    return data,pin


class F21Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.v,self.f=tetra()
        self.stl=stl_bytes(self.v,self.f)
        self.zip,self.pin=zip_case(self.stl)
        self.path=self.root/'original.zip'
        self.path.write_bytes(self.zip)

    def test_01_pinned_original_zip_rejects_wrong_git_object(self):
        wrong=Pin(self.pin.model_id,PIN.git_zip_sha1,self.pin.raw_stl_sha256,
                  self.pin.triangles,self.pin.zip_size)
        with self.assertRaisesRegex(ValueError,'Git blob'):
            read_pinned_binary_stl_zip(self.path,wrong)

    def test_02_original_bytes_pass_pinned_synthetic(self):
        self.assertEqual(read_pinned_binary_stl_zip(self.path,self.pin),self.stl)

    def test_03_zip_contents_tampering_fails_sha(self):
        altered=bytearray(self.stl);altered[110]^=1
        a,_=zip_case(bytes(altered));self.path.write_bytes(a)
        newpin=Pin(self.pin.model_id,git_blob_sha(a),self.pin.raw_stl_sha256,
                   self.pin.triangles,len(a))
        with self.assertRaisesRegex(ValueError,'SHA-256'):
            read_pinned_binary_stl_zip(self.path,newpin)

    def test_04_traversal_name_rejected(self):
        data,pin=zip_case(self.stl,name='../293137.stl')
        self.path.write_bytes(data)
        with self.assertRaisesRegex(ValueError,'member identity'):
            read_pinned_binary_stl_zip(self.path,pin)

    def test_05_archive_multiple_entries_rejected(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            z.writestr('293137.stl',self.stl);z.writestr('README','bad')
        raw=b.getvalue();self.path.write_bytes(raw)
        pin=Pin(293137,git_blob_sha(raw),hashlib.sha256(self.stl).hexdigest(),4,len(raw))
        with self.assertRaisesRegex(ValueError,'member identity'):
            read_pinned_binary_stl_zip(self.path,pin)

    def test_06_stl_reconstructed_tetrahedron(self):
        v,f=parse_source(self.stl,4)
        self.assertEqual((len(v),len(f)),(4,4))
        edges,topo=source_edges(v,f)
        self.assertEqual((len(edges),topo['source_euler'],topo['source_genus']),(6,2,0))

    def test_07_tetrahedral_3f_bicubic_source_preserved(self):
        v,f=parse_source(self.stl,4);edges,_=source_edges(v,f)
        status,pts,patches=build_patch_domain(v,f,edges)
        self.assertEqual((status['patch_vertices'],status['patch_edges'],status['bicubic_patches']),
                         (14,24,12))
        self.assertEqual(status['euler'],2)
        self.assertEqual(status['unpaired_or_multiple_seams'],0)
        self.assertEqual(len(patches),12)
        self.assertEqual(len(pts),status['unique_bp_control_vertices'])

    def test_08_cubic_linear_curve_canonical_reverse(self):
        a=(0.3,2.3,-0.3);b=(1.7,-1.3,5)
        u=linear_net(a,b)
        self.assertEqual(tuple(reversed(u)),tuple(reversed(linear_net(a,b))))
        self.assertEqual(u[0],a);self.assertEqual(u[3],b)

    def test_09_exact_bicubic_reproduces_bilinear(self):
        corners=[(0,0,0),(2,0,0),(2,2,0),(0,1,0)]
        net=controls_for_quad(corners,(0,1,2,3))
        for u,v in ((0,0),(1,1),(.2,.4),(.5,.5),(.83,.17)):
            distance=length(vec_sub(eval_bicubic(net,u,v),bilinear(corners,u,v)))
            self.assertLess(distance,1e-14)

    def test_10_jacobian_positive_with_analytic_bounds(self):
        a,b,c=(0,0,0),(1,0,0),(0,1,0)
        midab=(.5,0,0);midca=(0,.5,0);centroid=(1/3,1/3,0)
        ratios=jacobian_ratios((a,midab,centroid,midca),(a,b,c))
        self.assertAlmostEqual(min(ratios),1/12,places=12)
        self.assertAlmostEqual(max(ratios),1/4,places=12)

    def test_11_triangle_inverted_stl_source_orientation_fails(self):
        faces=list(self.f);faces[-1]=tuple(reversed(faces[-1]))
        stl=stl_bytes(self.v,faces);vertices,ids=parse_source(stl,4)
        with self.assertRaisesRegex(ValueError,'consistently oriented'):
            source_edges(vertices,ids)

    def test_12_open_triangle_source_fails(self):
        stl=stl_bytes(self.v,self.f[:-1]);v,f=parse_source(stl,3)
        with self.assertRaisesRegex(ValueError,'closed'):
            source_edges(v,f)

    def test_13_duplicate_triangle_source_fails(self):
        faces=list(self.f)+[self.f[0]]
        stl=stl_bytes(self.v,faces);v,f=parse_source(stl,len(faces))
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            source_edges(v,f)

    def test_14_nonfinite_STL_coordinate_rejected(self):
        stl=bytearray(self.stl);struct.pack_into('<f',stl,96,float('nan'))
        with self.assertRaisesRegex(ValueError,'Nonfinite'):
            parse_source(bytes(stl),4)

    def test_15_degenerate_triangle_rejected(self):
        faces=list(self.f);faces[0]=(0,1,1)
        stl=stl_bytes(self.v,faces)
        with self.assertRaisesRegex(ValueError,'Repeated'):
            parse_source(stl,4)

    def test_16_source_genus_one_torus(self):
        v,f=torus();s=stl_bytes(v,f);vv,ff=parse_source(s,len(f))
        edges,topo=source_edges(vv,ff)
        self.assertEqual((topo['source_euler'],topo['source_genus']),(0,1))
        status,_,_=build_patch_domain(vv,ff,edges)
        self.assertEqual(status['euler'],0)

    def test_17_triangulated_cube_preserves_euler(self):
        v,f=cube();vv,ff=parse_source(stl_bytes(v,f),len(f));edges,topo=source_edges(vv,ff)
        self.assertEqual(topo['source_euler'],2)
        result,_,_=build_patch_domain(vv,ff,edges)
        self.assertEqual(result['bicubic_patches'],36)

    def test_18_bp_serialization_zero_based_indexed_contract(self):
        receipt, model=execute(self.path,self.pin)
        records=model.decode().splitlines()
        verts=[r for r in records if r.startswith('v ')]
        quads=[r for r in records if r.startswith('p ')]
        self.assertEqual(len(quads),12)
        self.assertEqual(len(verts),receipt['patch_domain']['unique_bp_control_vertices'])
        for r in quads:
            words=r.split()
            self.assertEqual(len(words),17)
            self.assertTrue(all(0<=int(k)<len(verts) for k in words[1:]))
        self.assertEqual(hashlib.sha256(model).hexdigest(),receipt['patch_bp_sha256'])
        self.assertFalse(receipt['scientific_model_admission'])

    def test_19_distinct_controls_under_loader_tolerance_risk(self):
        self.assertGreater(collision_counts([(0.,0.,0.),(0.5e-7,0.,0.)]),0)

    def test_20_repeated_identical_controls_are_not_distinct_risk(self):
        self.assertEqual(collision_counts([(0.,0.,0.),(0.,0.,0.)]),0)

    def test_21_source_zip_bad_declared_length_rejected(self):
        pin=Pin(293137,self.pin.git_zip_sha1,self.pin.raw_stl_sha256,5,self.pin.zip_size)
        with self.assertRaisesRegex(ValueError,'bounded binary STL'):
            read_pinned_binary_stl_zip(self.path,pin)

    def test_22_zip_wrong_id_rejected(self):
        with self.assertRaisesRegex(ValueError,'member identity'):
            pin=Pin(123,self.pin.git_zip_sha1,self.pin.raw_stl_sha256,4,self.pin.zip_size)
            read_pinned_binary_stl_zip(self.path,pin)

    def test_23_no_native_or_license_inference(self):
        receipt,_=execute(self.path,self.pin)
        self.assertFalse(receipt['native_apmesh_tri_or_quad_meshing_executed'])
        self.assertFalse(receipt['third_party_license_cleared'])
        self.assertFalse(receipt['upstream_original_author_equivalence_proved'])

    def test_24_fail_closed_existing_output_and_no_geometry(self):
        outfile=self.root/'receipt.json';outfile.write_text('sentinel')
        with self.assertRaisesRegex(ValueError,'existing'):
            main(['--source-zip',str(self.path),'--private-receipt',str(outfile)])
        self.assertEqual(outfile.read_text(),'sentinel')

    def test_25_feature_count_is_finite(self):
        v,f=parse_source(self.stl,4);_,topo=source_edges(v,f)
        self.assertTrue(isinstance(topo['feature_edges_at_30deg_proxy'],int))
        self.assertGreaterEqual(topo['feature_edges_at_30deg_proxy'],0)

    def test_26_full_snapshot_is_repeatable(self):
        a,ab=execute(self.path,self.pin)
        b,bb=execute(self.path,self.pin)
        self.assertEqual(a,b)
        self.assertEqual(ab,bb)

    def test_27_private_bp_and_receipt_created_in_sync(self):
        report,bp=execute(self.path,self.pin)
        out=self.root/'candidate.bp';receipt=self.root/'receipt.json'
        write_private_result(report,bp,receipt,out)
        self.assertEqual(out.read_bytes(),bp)
        got=json.loads(receipt.read_text())
        self.assertTrue(got['private_bp_candidate_written'])
        self.assertFalse(got['scientific_model_admission'])
        self.assertFalse(got['third_party_geometry_published'])

    def test_28_writer_rejects_substituted_bp_payload(self):
        report,bp=execute(self.path,self.pin)
        with self.assertRaisesRegex(ValueError,'changed after'):
            write_private_result(report,bp+b'corrupt',self.root/'receipt.json',self.root/'test.bp')
        self.assertFalse((self.root/'test.bp').exists())

    def test_29_writer_blocks_near_control_merges(self):
        report,bp=execute(self.path,self.pin)
        report['patch_domain']['legacy_reader_near_distinct_control_pairs']=1
        with self.assertRaisesRegex(ValueError,'may merge'):
            write_private_result(report,bp,self.root/'receipt.json',self.root/'test.bp')
        self.assertFalse((self.root/'test.bp').exists())

    def test_30_writer_blocks_existing_bp_and_preserves_receipt(self):
        report,bp=execute(self.path,self.pin)
        output=self.root/'candidate.bp';output.write_text('sentinel')
        with self.assertRaisesRegex(ValueError,'existing'):
            write_private_result(report,bp,self.root/'receipt.json',output)
        self.assertEqual(output.read_text(),'sentinel')
        self.assertFalse((self.root/'receipt.json').exists())



if __name__=='__main__':
    unittest.main()
