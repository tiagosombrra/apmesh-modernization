"""Independent geometric and adversarial checks for the S3.J research gate."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import tempfile
import unittest

import cadquery as cq

from audit_analytic_bp import read_bp, surface
from s3h_source_cylinder_bp import construct as cylinder_construct, face_geometry
from s3j_radial_support_enclosure import (
    _radial_enclosure, _slice_coefficients, _squared_enclosure,
    audit_joint, certify_patch, run,
)
from s3i_joint_source_atlas import construct_joint


class OriginalSupportEnclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.source = Path(cls.temp.name) / 'author_half_cylinder.step'
        cylinder = cq.Workplane('XY').circle(3).extrude(4)
        clip = cq.Workplane('XY').box(8, 4, 4, centered=(True,False,False))
        cq.exporters.export(cylinder.intersect(clip).val(), str(cls.source))
        cls.raw = cls.source.read_text('utf8')
        cls.hash = sha256(cls.source.read_bytes()).hexdigest()
        cls.native = cq.importers.importStep(str(cls.source)).val()
        from s3c_step_source_gate import parse_entities,refs
        table = parse_entities(cls.raw)
        cls.cyl_id = next(i for i, (type_, payload) in table.items()
                          if type_ == 'ADVANCED_FACE' and
                          table[refs(payload)[-1]][0] == 'CYLINDRICAL_SURFACE')
        cls.bp, cls.manifest = construct_joint(
            cls.raw,cls.native,model='SYNTHETIC',source_sha256=cls.hash,
            cylinder_face_ids=[cls.cyl_id],sectors=6,sampled_budget_mm=.001)
        cls.vertices,cls.patches = read_bp(cls.bp)
        cls.geom = face_geometry(cls.raw,face_id=cls.cyl_id,model='SYNTHETIC',
                                 source_sha256=cls.hash)
        cls.report = audit_joint(cls.raw,cls.bp,cls.manifest,
                                 model='SYNTHETIC',source_sha256=cls.hash,declared_budget_mm=.001)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_joint_radial_enclosure_accepts_control(self):
        self.assertEqual(self.report['cylinder_patch_count'],6)
        self.assertTrue(self.report['same_numeric_budget_guarded_radial_support_pass'])
        self.assertLess(self.report['maximum_guarded_radial_support_error_upper_mm'],.001)
        self.assertGreater(self.report['maximum_guarded_radial_support_error_upper_mm'],
                           self.manifest['cylinder_fit_receipts'][0]['source_fit_audit']
                           ['maximum_sampled_distance_mm'])
        self.assertEqual(self.report['original_native_face_trim'],'NOT_CERTIFIED')

    def test_dense_analytic_radial_error_never_exceeds_enclosure(self):
        labels=[(patch,meta) for patch,meta in zip(self.patches,self.manifest['patches'])
                if meta['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE']
        for (patch,meta),control in zip(labels,self.report['patches']):
            net=[self.vertices[i] for i in patch]
            for v in (0.,.17,.5,.83,1.):
                for i in range(121):
                    p=surface(net,i/120,v)
                    xyz=tuple(p[k]-self.geom['frame']['origin'][k] for k in range(3))
                    axis=self.geom['frame']['axis']
                    z=sum(a*b for a,b in zip(xyz,axis))
                    radial=tuple(xyz[k]-z*axis[k] for k in range(3))
                    discrepancy=abs(math.sqrt(sum(x*x for x in radial))-self.geom['frame']['radius'])
                    self.assertLessEqual(discrepancy,control['radial_support_error_upper_mm'])

    def test_two_sector_original_m5_angle_fails_pilot_budget(self):
        theta=2.102093169774461
        for sectors,expected in ((2,False),(4,True),(6,True)):
            angle=theta/sectors
            radius=2.
            A=(radius,0.)
            B=(radius*math.cos(angle),radius*math.sin(angle))
            controls=[A,(radius,radius*angle/3),
                      (B[0]+radius*math.sin(angle)*angle/3,
                       B[1]-radius*math.cos(angle)*angle/3),B]
            q=_slice_coefficients(controls,radius)
            lo,hi=_squared_enclosure(q,8)
            bound=_radial_enclosure(lo,hi,radius)+1e-9
            with self.subTest(sectors=sectors):
                self.assertEqual(bound<=.001,expected)
                self.assertLess(bound,.007)

    def test_bernstein_refinement_tightens_enclosure(self):
        theta=2.102093169774461/4
        r=2
        c=[(r,0),(r,r*theta/3),
           (r*math.cos(theta)+r*math.sin(theta)*theta/3,
            r*math.sin(theta)-r*math.cos(theta)*theta/3),
           (r*math.cos(theta),r*math.sin(theta))]
        polynomial=_slice_coefficients(c,r)
        coarse=_squared_enclosure(polynomial,0)
        fine=_squared_enclosure(polynomial,8)
        self.assertGreaterEqual(coarse[1],fine[1])
        self.assertLessEqual(coarse[0],fine[0])
        self.assertLess(_radial_enclosure(*fine,r),_radial_enclosure(*coarse,r))

    def test_axial_control_deformation_rejected(self):
        curved=next((p,m) for p,m in zip(self.patches,self.manifest['patches'])
                    if m['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE')
        vertices=list(self.vertices)
        index=curved[0][5]
        vertices[index]=tuple(x+(0.02 if i==2 else 0) for i,x in enumerate(vertices[index]))
        with self.assertRaisesRegex(ValueError,'axially linear|radial controls vary'):
            certify_patch(vertices,curved[0],self.geom,0,6)

    def test_radial_row_deformation_rejected(self):
        curved=next((p,m) for p,m in zip(self.patches,self.manifest['patches'])
                    if m['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE')
        vertices=list(self.vertices)
        index=curved[0][6]
        vertices[index]=tuple(x+(0.01 if i==0 else 0) for i,x in enumerate(vertices[index]))
        with self.assertRaisesRegex(ValueError,'radial controls vary'):
            certify_patch(vertices,curved[0],self.geom,0,6)

    def test_angular_wedge_deformation_rejected(self):
        curved=next((p,m) for p,m in zip(self.patches,self.manifest['patches'])
                    if m['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE')
        vertices=list(self.vertices)
        for index in [curved[0][4*row+1] for row in range(4)]:
            p=vertices[index]
            vertices[index]=(p[0]+20,p[1]+20,p[2])
        with self.assertRaisesRegex(ValueError,'angular wedge'):
            certify_patch(vertices,curved[0],self.geom,0,6)

    def test_tampered_bp_digest_rejected(self):
        with self.assertRaisesRegex(ValueError,'digest mismatch'):
            audit_joint(self.raw,self.bp.replace('v ', 'v 10 ',1),self.manifest,
                        model='SYNTHETIC',source_sha256=self.hash,declared_budget_mm=.001)

    def test_rehashed_bp_interior_deformation_breaches_bound(self):
        receipt=deepcopy(self.manifest)
        lines=self.bp.splitlines()
        for k in [key for key in receipt['control_key_to_id'] if key.startswith('interior:')]:
            idx=receipt['control_key_to_id'][k]
            tokens=lines[2+idx].split()
            tokens[1]=str(float(tokens[1])+0.05)
            lines[2+idx]=' '.join(tokens)
        corrupt='\n'.join(lines)+'\n'
        receipt['bp_sha256']=sha256(corrupt.encode()).hexdigest()
        try:
            report = audit_joint(self.raw,corrupt,receipt,model='SYNTHETIC',source_sha256=self.hash,declared_budget_mm=.001)
        except ValueError as exc:
            self.assertRegex(str(exc), 'vary across axial rows|radial controls vary|angular wedge')
        else:
            self.assertFalse(report['same_numeric_budget_guarded_radial_support_pass'])

    def test_forged_patch_identity_rejected(self):
        bad=deepcopy(self.manifest)
        meta=next(x for x in bad['patches'] if x['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE')
        meta['control_vertex_ids'][3] = 999
        with self.assertRaisesRegex(ValueError,'patch control ids disagree'):
            audit_joint(self.raw,self.bp,bad,model='SYNTHETIC',source_sha256=self.hash,declared_budget_mm=.001)

    def test_duplicate_source_cylinder_receipt_rejected(self):
        bad=deepcopy(self.manifest)
        bad['cylinder_fit_receipts'].append(deepcopy(bad['cylinder_fit_receipts'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate cylindrical face receipts'):
            audit_joint(self.raw,self.bp,bad,model='SYNTHETIC',source_sha256=self.hash,declared_budget_mm=.001)

    def test_rehashed_manifest_cannot_widen_predeclared_budget(self):
        forged=deepcopy(self.manifest)
        forged['cylinder_fit_receipts'][0]['source_fit_audit']['prespecified_budget_mm']=0.1
        with self.assertRaisesRegex(ValueError,'externally declared budget'):
            audit_joint(self.raw,self.bp,forged,model='SYNTHETIC',
                        source_sha256=self.hash,declared_budget_mm=.001)

    def test_wrong_source_digest_rejected(self):
        with self.assertRaisesRegex(ValueError,'source digest mismatch'):
            audit_joint(self.raw,self.bp,self.manifest,model='SYNTHETIC',source_sha256='0'*64,declared_budget_mm=.001)

    def test_invalid_angular_sector_input_rejected(self):
        curved=next((p,m) for p,m in zip(self.patches,self.manifest['patches'])
                    if m['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE')
        with self.assertRaisesRegex(ValueError,'<=90 degree'):
            certify_patch(self.vertices,curved[0],self.geom,0,1)

    def test_formal_interval_proof_remains_unclaimed(self):
        self.assertFalse(self.report['patches'][0]['formal_directed_rounding_interval_proof'])
        self.assertEqual(self.report['continuous_support_scope'],
                         'NUMERICAL_BERNSTEIN_ENCLOSURE_NOT_FORMAL_INTERVAL_PROOF')

    def test_fail_closed_runner_does_not_write_on_wrong_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            bp=root/'a.bp';manifest=root/'a.json';bp.write_text(self.bp)
            manifest.write_text(json.dumps(self.manifest))
            output=root/'receipt.json'
            with self.assertRaisesRegex(ValueError,'SHA-256'):
                run(self.source,bp,manifest,output,model='SYNTHETIC',expected_sha256='0'*64,declared_budget_mm=.001)
            self.assertFalse(output.exists())

    def test_runner_writes_recomputed_receipt_only_on_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            bp=root/'a.bp';manifest=root/'a.json';bp.write_text(self.bp)
            manifest.write_text(json.dumps(self.manifest))
            output=root/'receipt.json'
            result=run(self.source,bp,manifest,output,model='SYNTHETIC',expected_sha256=self.hash,declared_budget_mm=.001)
            self.assertTrue(output.exists())
            self.assertTrue(result['same_numeric_budget_guarded_radial_support_pass'])

    @unittest.skipUnless(Path(os.getenv('APMESH_MAMBO_SOURCE_DIR','/external/mambo/sources'),
                              'i05o_m5.step').is_file(), 'Pinned original M5 STEP unavailable')
    def test_original_m5_original_bp_analytic_support_enclosure(self):
        path=Path(os.getenv('APMESH_MAMBO_SOURCE_DIR','/external/mambo/sources'))/'i05o_m5.step'
        with tempfile.TemporaryDirectory() as temp:
            from s3i_joint_source_atlas import run as source_joint_run
            source_joint_run(path,Path(temp)/'joint',model='M5',
                             cylinder_face_ids=[3493,3976],sectors=4,sampled_budget_mm=.001)
            output=Path(temp)/'joint'
            report=run(path,output/'source_joint.partial.bp',
                       output/'source_joint_manifest.json',output/'s3j.json',model='M5',declared_budget_mm=.001)
            self.assertEqual(report['cylinder_patch_count'],8)
            self.assertTrue(report['same_numeric_budget_guarded_radial_support_pass'])


if __name__ == '__main__':
    unittest.main()
