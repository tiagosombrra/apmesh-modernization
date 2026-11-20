"""Directed S3.H tests for original-key-preserving cylindrical source BP pilots."""
from __future__ import annotations

import copy
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import tempfile
import unittest

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.gp import gp_Ax3, gp_Cylinder, gp_Dir, gp_Pnt

from s3c_step_source_gate import parse_entities
from s3h_source_cylinder_bp import construct, face_geometry, independent_audit, run


def make_source(path, *, angle=2.102093169774461, radius=2.0):
    surface=gp_Cylinder(gp_Ax3(gp_Pnt(10,0,-2.5), gp_Dir(0,1,0),
                                gp_Dir(0,0,1)), radius)
    face=cq.Face(BRepBuilderAPI_MakeFace(surface,math.pi,math.pi+angle,
                                          -7.5,7.5).Face())
    cq.exporters.export(face,str(path))
    raw=path.read_text(encoding='utf-8')
    digest=sha256(raw.encode('utf-8')).hexdigest()
    table=parse_entities(raw)
    ids=[i for i,(kind,_) in table.items() if kind=='ADVANCED_FACE']
    assert len(ids)==1
    return raw,digest,ids[0]


class SourceCylinderBoundedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.path=Path(cls.temp.name)/'synthetic_source_cylinder.step'
        cls.source,cls.digest,cls.face=make_source(cls.path)
        cls.geometry=face_geometry(cls.source,face_id=cls.face,
                                   model='SYNTHETIC',source_sha256=cls.digest)
        cls.results={}
        for n in (2,4,6):
            bp,manifest=construct(cls.geometry,sectors=n,absolute_budget_mm=.001)
            report=independent_audit(cls.source,bp,manifest,
                                     model='SYNTHETIC',source_sha256=cls.digest)
            cls.results[n]=(bp,manifest,report)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_source_curves_are_oriented_not_minor_arc_guessed(self):
        arcs=self.geometry['original_circle_records']
        self.assertEqual(len(arcs),2)
        self.assertAlmostEqual(arcs[0]['sweep_rad_signed'],
                               -arcs[1]['sweep_rad_signed'],places=11)
        self.assertAlmostEqual(abs(arcs[0]['sweep_rad_signed']),2.102093169774461,places=10)
        self.assertGreater(abs(arcs[0]['sweep_rad_signed']), math.pi/2)

    def test_source_controls_match_original_generator_curve_keys(self):
        _,manifest,_=self.results[4]
        original_keys=[k for k in manifest['control_keys'] if k.startswith('edge:') or k.startswith('vertex:')]
        self.assertEqual(len(original_keys),8)
        self.assertEqual(len(set(original_keys)),8)
        self.assertEqual(manifest['source_start_generator_edge'],self.geometry['start_generator_edge'])
        self.assertEqual(manifest['source_end_generator_edge'],self.geometry['end_generator_edge'])

    def test_patch_counts_and_exact_derived_shared_indices(self):
        for count,(bp,manifest,audit) in self.results.items():
            with self.subTest(sectors=count):
                self.assertEqual(manifest['sectors'],count)
                self.assertEqual(manifest['control_count'],12*count+4)
                self.assertEqual(audit['derived_seams_verified'],count-1)
                self.assertEqual(audit['original_generator_edges_checked'],2)
                self.assertEqual(audit['independent_samples'],count*35*35)

    def test_error_refinement_and_prespecified_gate(self):
        errors=[self.results[n][2]['maximum_sampled_distance_mm'] for n in (2,4,6)]
        self.assertEqual(errors,sorted(errors,reverse=True))
        self.assertGreater(errors[0],.001)
        self.assertLess(errors[1],.001)
        self.assertLess(errors[2],.0001)
        self.assertFalse(self.results[2][2]['sampled_budget_pass'])
        self.assertTrue(self.results[4][2]['sampled_budget_pass'])
        self.assertTrue(self.results[6][2]['sampled_budget_pass'])

    def test_no_claim_of_continuous_bound_or_native_mesh(self):
        _,manifest,audit=self.results[4]
        self.assertFalse(manifest['source_native_trim_verified'])
        self.assertFalse(manifest['complete_source_atlas'])
        self.assertEqual(manifest['apmesh_generation'],'NOT_RUN')
        self.assertEqual(audit['continuous_error_bound'],'NOT_CERTIFIED')

    def test_fail_closed_for_insufficient_sector_count(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'rejected'
            with self.assertRaisesRegex(ValueError,'exceeds prespecified'):
                run(self.path,output,model='SYNTHETIC',face_ids=[self.face],
                    sectors=2,absolute_budget_mm=.001,expected_sha256=self.digest)
            self.assertFalse(output.exists())

    def test_positive_cli_writes_research_bp_and_sidecar(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'admitted'
            r=run(self.path,output,model='SYNTHETIC',face_ids=[self.face],
                  sectors=4,absolute_budget_mm=.001,expected_sha256=self.digest)
            self.assertTrue(r[0]['sampled_budget_pass'])
            bpfile=output/f'face_{self.face}_segments_4.bp'
            sidecar=json.loads((output/f'face_{self.face}_segments_4.json').read_text())
            self.assertTrue(bpfile.exists())
            self.assertEqual(sidecar['manifest']['source_model'],'SYNTHETIC')
            self.assertTrue(sidecar['audit']['sampled_budget_pass'])

    def test_bad_source_digest_rejected(self):
        with self.assertRaisesRegex(ValueError,'SHA-256 mismatch'):
            face_geometry(self.source,face_id=self.face,model='SYNTHETIC',
                          source_sha256='0'*64)
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError,'SHA-256 mismatch'):
                run(self.path,Path(folder)/'out',model='SYNTHETIC',face_ids=[self.face],
                    sectors=4,absolute_budget_mm=.001,expected_sha256='0'*64)

    def test_mambo_model_cannot_be_spoofed_by_synthetic_source(self):
        with self.assertRaisesRegex(ValueError,'Pinned STEP source SHA-256 mismatch'):
            face_geometry(self.source,face_id=self.face,model='M5',
                          source_sha256=self.digest)

    def test_invalid_segment_count_and_budget(self):
        for n in (0,-1,65):
            with self.subTest(n=n),self.assertRaises(ValueError):
                construct(self.geometry,sectors=n,absolute_budget_mm=.001)
        for budget in (0,-1,math.nan,math.inf):
            with self.subTest(budget=budget),self.assertRaises(ValueError):
                construct(self.geometry,sectors=4,absolute_budget_mm=budget)

    def test_no_arbitrary_non_cylinder_face_admission(self):
        with self.assertRaises(ValueError):
            face_geometry(self.source,face_id=0,model='SYNTHETIC',
                          source_sha256=self.digest)

    def test_bp_byte_mutation_detected(self):
        bp,manifest,_=self.results[4]
        with self.assertRaisesRegex(ValueError,'hash mismatch'):
            independent_audit(self.source,bp.replace('v 10 ', 'v 20 ',1),manifest,
                              model='SYNTHETIC',source_sha256=self.digest)

    def test_forged_manifest_sector_count_detected(self):
        bp,manifest,_=self.results[4]
        forged=copy.deepcopy(manifest)
        forged['sectors']=8
        with self.assertRaisesRegex(ValueError,'inventory mismatch'):
            independent_audit(self.source,bp,forged,
                              model='SYNTHETIC',source_sha256=self.digest)

    def test_forged_original_source_control_identity_detected(self):
        bp,manifest,_=self.results[4]
        fake=copy.deepcopy(manifest)
        fake['control_keys'][0]='vertex:999999'
        with self.assertRaisesRegex(ValueError,'control was not retained'):
            independent_audit(self.source,bp,fake,
                              model='SYNTHETIC',source_sha256=self.digest)

    def test_forged_interior_control_fails_independent_oracle(self):
        bp,manifest,_=self.results[4]
        lines=bp.splitlines()
        target=next(i for i,line in enumerate(lines) if line.startswith('v '))
        vals=lines[target].split()
        vals[1]=str(float(vals[1])+0.05)
        lines[target]=' '.join(vals)
        fakebp='\n'.join(lines)+'\n'
        fake=copy.deepcopy(manifest)
        fake['bp_sha256']=sha256(fakebp.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,'canonical control'):
            independent_audit(self.source,fakebp,fake,
                              model='SYNTHETIC',source_sha256=self.digest)

    def test_original_arc_identity_tampering_rejected(self):
        bp,manifest,_=self.results[4]
        fake=copy.deepcopy(manifest)
        fake['source_original_circle_ids'][0]=100000
        with self.assertRaisesRegex(ValueError,'Source circular edge identity'):
            independent_audit(self.source,bp,fake,model='SYNTHETIC',source_sha256=self.digest)

    def test_duplicate_source_face_selection_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError,'Face IDs must be'):
                run(self.path,Path(folder)/'out',model='SYNTHETIC',
                    face_ids=[self.face,self.face],sectors=4,
                    absolute_budget_mm=.001,expected_sha256=self.digest)

    def test_signed_major_arc_not_automatically_folded_to_minor(self):
        with tempfile.TemporaryDirectory() as folder:
            raw,dig,face=make_source(Path(folder)/'major.step',angle=4.0)
            g=face_geometry(raw,face_id=face,model='SYNTHETIC',source_sha256=dig)
            self.assertAlmostEqual(abs(g['signed_sweep_rad']),4.0,places=10)
            self.assertGreater(abs(g['signed_sweep_rad']),math.pi)

    @unittest.skipUnless(
        (Path(os.environ.get('APMESH_MAMBO_SOURCE_DIR', '/external/mambo/sources'))/'i05o_m5.step').is_file(),
        'Original M5 immutable STEP bytes are not mounted in this runtime')
    def test_original_m5_3493_and_3976(self):
        source_dir=Path(os.environ.get('APMESH_MAMBO_SOURCE_DIR', '/external/mambo/sources'))
        with tempfile.TemporaryDirectory() as folder:
            audits=run(source_dir/'i05o_m5.step',Path(folder)/'m5',model='M5',
                       face_ids=[3493,3976],sectors=4,absolute_budget_mm=.001)
            self.assertEqual(len(audits),2)
            self.assertTrue(all(x['sampled_budget_pass'] for x in audits))


if __name__=='__main__':
    unittest.main()
