"""Regression and tamper controls for source-native shared planar/cylinder BP."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
import unittest

import cadquery as cq

from s3c_step_source_gate import parse_entities, refs
from s3h_source_cylinder_bp import _source_pcurve_const_u, face_geometry
from s3i_joint_source_atlas import construct_joint, independently_check_joint, run


class SourceJointAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.source_path=Path(cls.temp.name)/'two_generator_half_cylinder.step'
        cylinder=cq.Workplane('XY').circle(3).extrude(4)
        clip=cq.Workplane('XY').box(8,4,4,centered=(True,False,False))
        cq.exporters.export(cylinder.intersect(clip).val(),str(cls.source_path))
        cls.raw=cls.source_path.read_text(encoding='utf-8')
        cls.digest=sha256(cls.source_path.read_bytes()).hexdigest()
        cls.native=cq.importers.importStep(str(cls.source_path)).val()
        cls.table=parse_entities(cls.raw)
        cls.cylinder_face=next(k for k,(typ,payload) in cls.table.items()
                               if typ=='ADVANCED_FACE' and
                               cls.table[refs(payload)[-1]][0]=='CYLINDRICAL_SURFACE')
        cls.bp,cls.receipt=construct_joint(cls.raw,cls.native,model='SYNTHETIC',
            source_sha256=cls.digest,cylinder_face_ids=[cls.cylinder_face],sectors=6,
            sampled_budget_mm=.001)
        cls.audit=independently_check_joint(cls.raw,cls.native,cls.bp,cls.receipt,
                                           model='SYNTHETIC',source_sha256=cls.digest)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_degree_one_spline_pcurve_is_admitted_as_linear(self):
        geo=face_geometry(self.raw,face_id=self.cylinder_face,model='SYNTHETIC',
                          source_sha256=self.digest)
        self.assertEqual(len(geo['generators']),2)
        self.assertAlmostEqual(abs(geo['signed_sweep_rad']),3.141592653589793,places=10)
        self.assertIn('B_SPLINE_CURVE_WITH_KNOTS',self.raw)

    def test_two_surface_source_graph_is_fused_by_original_indices(self):
        self.assertEqual(self.receipt['admitted_planar_source_faces'],1)
        self.assertEqual(self.receipt['admitted_cylinder_source_faces'],1)
        self.assertEqual(self.receipt['generated_partial_bp_patch_count'],7)
        self.assertEqual(self.receipt['shared_original_generator_edges'],2)
        self.assertEqual(self.audit['shared_original_generator_control_ids_checked'],8)
        self.assertEqual(self.receipt['unique_control_points'],84)
        self.assertEqual(self.receipt['accepted_apmesh_tri_quad'],'NOT_RUN')

    def test_shared_original_controls_really_reuse_integer_ids(self):
        labels=self.receipt['patches']
        for seam in self.receipt['original_generator_shared_controls']:
            plane=next(x for x in labels if x['kind']=='SOURCE_EXACT_PLANAR_QUAD' and
                       x['source_face_id']==seam['planar_source_face_id'])
            cylinder=[x for x in labels if x['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE'
                      and x['source_face_id']==seam['cylinder_source_face_id']]
            for idx in seam['shared_original_control_vertex_ids']:
                self.assertIn(idx,plane['control_vertex_ids'])
                self.assertTrue(any(idx in p['control_vertex_ids'] for p in cylinder))

    def test_native_trimmed_face_sampled_distance(self):
        self.assertLess(self.audit['independent_native_trimmed_cylinder_distance_max_mm'],.001)
        self.assertGreater(self.audit['native_cylinder_distance_sample_count'],500)
        self.assertLess(self.audit['independent_planar_source_face_distance_max_mm'],1e-8)
        self.assertEqual(self.audit['native_cylinder_uv_trim_oracle'],
                         'NOT_CERTIFIED_BY_SAMPLED_DISTANCE')

    def test_four_sectors_fail_without_widening_tolerance(self):
        with self.assertRaisesRegex(ValueError,'predeclared source sampled budget'):
            construct_joint(self.raw,self.native,model='SYNTHETIC',
                            source_sha256=self.digest,cylinder_face_ids=[self.cylinder_face],
                            sectors=4,sampled_budget_mm=.001)

    def test_wrong_original_source_checksum_rejected(self):
        with self.assertRaisesRegex(ValueError,'digest mismatch'):
            construct_joint(self.raw,self.native,model='SYNTHETIC',
                            source_sha256='f'*64,cylinder_face_ids=[self.cylinder_face])

    def test_synthetic_cannot_be_spoofed_as_original_m5(self):
        with self.assertRaisesRegex(ValueError,'Pinned industrial input SHA-256 mismatch'):
            construct_joint(self.raw,self.native,model='M5',source_sha256=self.digest,
                            cylinder_face_ids=[self.cylinder_face])

    def test_wrong_source_face_rejected(self):
        planar=self.receipt['patches'][0]['source_face_id']
        with self.assertRaisesRegex(ValueError,'not mapped to a native first-ring support'):
            construct_joint(self.raw,self.native,model='SYNTHETIC',
                            source_sha256=self.digest,cylinder_face_ids=[planar],
                            sectors=6)

    def test_invalid_segment_count_and_budget_rejected(self):
        for sectors in (0,-1,65):
            with self.subTest(sectors=sectors),self.assertRaises(ValueError):
                construct_joint(self.raw,self.native,model='SYNTHETIC',
                                source_sha256=self.digest,cylinder_face_ids=[self.cylinder_face],
                                sectors=sectors)
        for budget in (0,-1,float('nan'),float('inf')):
            with self.subTest(budget=budget),self.assertRaises(ValueError):
                construct_joint(self.raw,self.native,model='SYNTHETIC',
                                source_sha256=self.digest,cylinder_face_ids=[self.cylinder_face],
                                sampled_budget_mm=budget)

    def test_bp_digest_tamper_rejected(self):
        with self.assertRaisesRegex(ValueError,'BP SHA-256 mismatch'):
            independently_check_joint(self.raw,self.native,self.bp.replace('v ', 'v 7 ',1),
                self.receipt,model='SYNTHETIC',source_sha256=self.digest)

    def test_rehashed_cylinder_interior_deformation_rejected_by_native_oracle(self):
        local=deepcopy(self.receipt)
        idx=next(j for key,j in local['control_key_to_id'].items()
                 if key.startswith('interior:'))
        lines=self.bp.splitlines()
        vertex_line=next(i for i,line in enumerate(lines) if line.startswith('v '))+idx
        tokens=lines[vertex_line].split()
        tokens[1]=str(float(tokens[1])+.02)
        lines[vertex_line]=' '.join(tokens)
        tampered='\n'.join(lines)+'\n'
        local['bp_sha256']=sha256(tampered.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,'sampled distance exceeds budget'):
            independently_check_joint(self.raw,self.native,tampered,local,
                                      model='SYNTHETIC',source_sha256=self.digest)

    def test_source_generator_ids_cannot_be_forged_even_with_valid_hash(self):
        local=deepcopy(self.receipt)
        local['original_generator_shared_controls'][0]['shared_original_control_vertex_ids'][0]+=1
        with self.assertRaisesRegex(ValueError,'Tampered original source boundary identity'):
            independently_check_joint(self.raw,self.native,self.bp,local,
                                      model='SYNTHETIC',source_sha256=self.digest)

    def test_native_face_mapping_cannot_be_forged(self):
        local=deepcopy(self.receipt)
        source_plane=next(p for p in local['patches'] if p['kind']=='SOURCE_EXACT_PLANAR_QUAD')
        cylinder=next(p for p in local['patches'] if p['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE')
        cylinder['source_native_face_index']=source_plane['source_native_face_index']
        with self.assertRaisesRegex(ValueError,'Forged joint source-to-native face identity'):
            independently_check_joint(self.raw,self.native,self.bp,local,
                                      model='SYNTHETIC',source_sha256=self.digest)

    def test_non_linear_spline_pcurve_is_rejected(self):
        # The native STEP contains an exact 2-pole degree-one line-as-spline.
        if 'B_SPLINE_CURVE_WITH_KNOTS' not in self.raw:
            self.skipTest('OCCT exporter did not produce a linear spline PCURVE')
        import re
        mutated,count=re.subn(r'(B_SPLINE_CURVE_WITH_KNOTS\(\s*\'[^\']*\'\s*,\s*)1\s*,',
                              r'\g<1>2,',self.raw,count=1)
        self.assertEqual(count,1)
        with self.assertRaises(ValueError):
            face_geometry(mutated,face_id=self.cylinder_face,model='SYNTHETIC',
                          source_sha256=sha256(mutated.encode()).hexdigest())

    def test_cli_records_bundle_after_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'joint'
            receipt,audit=run(self.source_path,out,model='SYNTHETIC',
                source_sha256=self.digest,cylinder_face_ids=[self.cylinder_face],
                sectors=6,sampled_budget_mm=.001)
            self.assertEqual(receipt['shared_original_generator_edges'],2)
            self.assertEqual(audit['shared_original_generator_control_ids_checked'],8)
            self.assertTrue((out/'source_joint.partial.bp').is_file())
            self.assertTrue((out/'independent_joint_audit.json').is_file())

    def test_cli_fails_without_writing_rejected_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'rejected'
            with self.assertRaisesRegex(ValueError,'predeclared source sampled budget'):
                run(self.source_path,out,model='SYNTHETIC',source_sha256=self.digest,
                    cylinder_face_ids=[self.cylinder_face],sectors=4,sampled_budget_mm=.001)
            self.assertFalse(out.exists())

    def test_duplicate_original_cylinder_face_rejected(self):
        with self.assertRaisesRegex(ValueError,'nonempty and distinct'):
            construct_joint(self.raw,self.native,model='SYNTHETIC',source_sha256=self.digest,
                cylinder_face_ids=[self.cylinder_face,self.cylinder_face])

    @unittest.skipUnless(
        (Path(os.environ.get('APMESH_MAMBO_SOURCE_DIR', '/external/mambo/sources'))/
         'i05o_m5.step').is_file(), 'Pinned original M5 STEP absent locally')
    def test_original_m5_native_joint_cylinder_gate(self):
        path=Path(os.environ.get('APMESH_MAMBO_SOURCE_DIR', '/external/mambo/sources'))/'i05o_m5.step'
        with tempfile.TemporaryDirectory() as tmp:
            manifest,report=run(path,Path(tmp)/'original_m5',model='M5',
                cylinder_face_ids=[3493,3976],sectors=4,sampled_budget_mm=.001)
            self.assertEqual(manifest['admitted_planar_source_faces'],6)
            self.assertEqual(manifest['admitted_cylinder_source_faces'],2)
            self.assertEqual(manifest['generated_partial_bp_patch_count'],14)
            self.assertEqual(manifest['shared_original_generator_edges'],4)
            self.assertEqual(report['shared_original_generator_control_ids_checked'],16)


if __name__=='__main__':
    unittest.main()
