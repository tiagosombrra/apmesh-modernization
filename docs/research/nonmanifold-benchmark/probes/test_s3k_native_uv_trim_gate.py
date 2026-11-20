"""Native OCCT-trim positive, adversarial and conditional original-M5 controls."""
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
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.gp import gp_Ax1, gp_Pnt, gp_Trsf

from audit_analytic_bp import read_bp
from s3c_step_source_gate import SOURCES
from s3i_joint_source_atlas import construct_joint
from s3k_native_uv_trim_gate import (
    NativeTrimRejection, audit_native_joint, classify_patch, main,
)


class NativeUvTrimGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.tmp.name)
        cls.source_file = cls.directory / 'synthetic_half_cylinder.step'
        half = (cq.Workplane('XY').circle(3).extrude(4).intersect(
            cq.Workplane('XY').box(8,4,4,centered=(True,False,False)))).val()
        cq.exporters.export(half,str(cls.source_file))
        cls.text=cls.source_file.read_text('utf-8')
        cls.digest=sha256(cls.source_file.read_bytes()).hexdigest()
        cls.shape=cq.importers.importStep(str(cls.source_file)).val()
        from s3c_step_source_gate import parse_entities, refs
        table=parse_entities(cls.text)
        faceid=next(fid for fid,(kind,payload) in table.items()
                    if kind=='ADVANCED_FACE' and table[refs(payload)[-1]][0]=='CYLINDRICAL_SURFACE')
        cls.bp,cls.manifest=construct_joint(cls.text,cls.shape,model='SYNTHETIC',
                                            source_sha256=cls.digest,
                                            cylinder_face_ids=[faceid],sectors=6,
                                            sampled_budget_mm=.001)
        cls.vertices,cls.patches=read_bp(cls.bp)
        cls.cyl_metadata=next(m for m in cls.manifest['patches']
                           if m['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE')
        cls.cylinder=cls.shape.Faces()[cls.cyl_metadata['source_native_face_index']]
        cls.result=audit_native_joint(cls.text,cls.shape,cls.bp,cls.manifest,
                            model='SYNTHETIC',source_sha256=cls.digest,
                            declared_budget_mm=.001)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_native_trim_has_inside_and_boundary_membership(self):
        self.assertEqual(self.result['cylindrical_bp_patch_count'],6)
        self.assertEqual(self.result['native_interior_uv_samples'],486)
        self.assertEqual(self.result['native_boundary_uv_samples'],264)
        self.assertTrue(all(p['classification_histogram'].get('INTERIOR_IN')==81
                            for p in self.result['patch_results']))
        self.assertTrue(self.result['native_face_coverage_envelopes'][0]['no_sampled_U_interval_gaps'])
        self.assertLess(self.result['maximum_native_projection_distance_mm'],.001)
        self.assertFalse(self.result['full_original_CAD_atlas'])

    def test_radial_certificate_and_native_trim_have_distinct_scopes(self):
        self.assertLess(self.result['guarded_radial_support_bound_mm'],.001)
        self.assertEqual(self.result['native_uv_claim'],
                         'DISCRETE_TRIM_MEMBERSHIP_ONLY_NOT_CONTINUOUS_CERTIFICATE')
        self.assertEqual(self.result['apmesh_tri_quad_generation'],'NOT_RUN')

    def test_wrong_native_surface_type_fails_closed(self):
        plane=next(f for f in self.shape.Faces() if f.geomType()=='PLANE')
        with self.assertRaisesRegex(NativeTrimRejection,'cylindrical'):
            classify_patch(plane,self.vertices,self.cyl_metadata['control_vertex_ids'])

    def test_native_cylinder_rotated_patch_rejected_despite_same_radial_distance(self):
        adaptor=BRepAdaptor_Surface(self.cylinder.wrapped,True)
        axis=adaptor.Cylinder().Axis()
        trsf=gp_Trsf();trsf.SetRotation(axis,math.pi)
        rotated=[]
        for xyz in self.vertices:
            p=gp_Pnt(*xyz);p.Transform(trsf)
            rotated.append((p.X(),p.Y(),p.Z()))
        with self.assertRaisesRegex(NativeTrimRejection,'OUTSIDE native trimmed face'):
            classify_patch(self.cylinder,rotated,self.cyl_metadata['control_vertex_ids'])

    def test_native_cylinder_axially_translated_patch_rejected(self):
        a=BRepAdaptor_Surface(self.cylinder.wrapped,True).Cylinder().Axis().Direction()
        d=(a.X(),a.Y(),a.Z())
        translated=[tuple(x+20*t for x,t in zip(p,d)) for p in self.vertices]
        with self.assertRaisesRegex(NativeTrimRejection,'OUTSIDE native trimmed face'):
            classify_patch(self.cylinder,translated,self.cyl_metadata['control_vertex_ids'])

    def test_native_geometry_deformation_exceeds_budget(self):
        controls=deepcopy(self.vertices)
        target=self.cyl_metadata['control_vertex_ids'][5]
        p=controls[target]
        controls[target]=(p[0]+.2,p[1],p[2])
        with self.assertRaises(NativeTrimRejection):
            classify_patch(self.cylinder,controls,self.cyl_metadata['control_vertex_ids'])

    def test_invalid_grid_and_tolerance_rejected(self):
        for bad in (2,0,100,3.4):
            with self.subTest(grid=bad),self.assertRaises(ValueError):
                classify_patch(self.cylinder,self.vertices,
                               self.cyl_metadata['control_vertex_ids'],interior_grid=bad)
        for bad in (0,1,-1,math.inf,math.nan):
            with self.subTest(tolerance=bad),self.assertRaises(ValueError):
                classify_patch(self.cylinder,self.vertices,
                               self.cyl_metadata['control_vertex_ids'],native_tolerance=bad)

    def test_invalid_indexed_patch_rejected(self):
        with self.assertRaisesRegex(ValueError,'Malformed indexed'):
            classify_patch(self.cylinder,self.vertices,[99]*16)

    def test_wrong_original_step_digest_fails(self):
        with self.assertRaisesRegex(ValueError,'source SHA-256'):
            audit_native_joint(self.text,self.shape,self.bp,self.manifest,
                               model='SYNTHETIC',source_sha256='a'*64,
                               declared_budget_mm=.001)

    def test_forged_bp_digest_fails_without_native_admission(self):
        bad_manifest=deepcopy(self.manifest)
        bad_manifest['bp_sha256']='f'*64
        with self.assertRaisesRegex(ValueError,'indexed BP checksum'):
            audit_native_joint(self.text,self.shape,self.bp,bad_manifest,
                               model='SYNTHETIC',source_sha256=self.digest,
                               declared_budget_mm=.001)

    def test_externally_changed_budget_cannot_be_accepted(self):
        with self.assertRaisesRegex(ValueError,'Manifest budget'):
            audit_native_joint(self.text,self.shape,self.bp,self.manifest,
                               model='SYNTHETIC',source_sha256=self.digest,
                               declared_budget_mm=.1)

    def test_fail_closed_cli_does_not_write_on_wrong_source_hash(self):
        from s3k_native_uv_trim_gate import main
        import sys
        bp=self.directory/'joint.partial.bp';bp.write_text(self.bp)
        manifest=self.directory/'joint.json';manifest.write_text(json.dumps(self.manifest))
        output=self.directory/'rejected_uv.json'
        old=sys.argv
        try:
            sys.argv=['s3k_native_uv_trim_gate','--step',str(self.source_file),
                '--bp',str(bp),'--manifest',str(manifest),'--model','SYNTHETIC',
                '--expected-sha256','1'*64,'--budget-mm','.001','--output',str(output)]
            with self.assertRaisesRegex(ValueError,'expected-sha256'):
                main()
        finally:
            sys.argv=old
        self.assertFalse(output.exists())

    def test_original_m5_native_uv_if_available(self):
        original=Path(os.getenv('APMESH_MAMBO_SOURCE_DIR','/external/mambo/sources'))/'i05o_m5.step'
        if not original.is_file():
            self.skipTest('Pinned original M5 STEP not available for native trim audit')
        original_data=original.read_bytes()
        self.assertEqual(sha256(original_data).hexdigest(),SOURCES['M5'][1])
        native=cq.importers.importStep(str(original)).val()
        text=original_data.decode('utf-8')
        bp,manifest=construct_joint(text,native,model='M5',
                        source_sha256=SOURCES['M5'][1],
                        cylinder_face_ids=[3493,3976],
                        sectors=4,sampled_budget_mm=.001)
        receipt=audit_native_joint(text,native,bp,manifest,model='M5',
                        source_sha256=SOURCES['M5'][1],declared_budget_mm=.001)
        self.assertEqual(receipt['original_face_ids'],[3493,3976])
        self.assertEqual(receipt['cylindrical_bp_patch_count'],8)
        self.assertEqual(receipt['native_interior_uv_samples'],648)
        self.assertEqual(receipt['native_boundary_uv_samples'],352)
        self.assertEqual(receipt['joint_original_controls_checked'],16)
        self.assertLess(receipt['maximum_native_projection_distance_mm'],.001)


if __name__=='__main__':
    unittest.main()
