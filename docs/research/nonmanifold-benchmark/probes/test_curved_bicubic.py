"""Curved four-sheet Bezier topology, representation and rejection controls."""
from __future__ import annotations
import copy
import hashlib
import json
import tempfile
from pathlib import Path
import unittest
import cadquery as cq
from curved_bicubic_pilot import generate, native_surface_complex
from audit_curved_bicubic import audit, sine_nonpolynomial_exact_case


class CurvedBicubicPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bp,cls.sidecar=generate()
        cls.shape,cls.report=native_surface_complex()

    def test_real_curved_nonmanifold_topological_edge(self):
        self.assertEqual(self.report['edge_incidence_histogram'],{1:12,4:1})
        self.assertEqual(self.report['four_incident_edges'],1)
        self.assertEqual(self.report['faces'],4)

    def test_analytic_representation_and_kernel_agreement(self):
        receipt=audit(self.bp,self.sidecar,self.shape)
        self.assertEqual(receipt['evaluated_bp_points'],324)
        self.assertLess(receipt['max_power_basis_difference'],2e-12)
        self.assertLess(receipt['max_native_brep_distance'],1e-8)

    def test_one_reversed_incidence_supported(self):
        self.assertEqual(self.sidecar['patches'][1]['reverse_v'],True)
        self.assertEqual([self.sidecar['patches'][i]['sides'][3]['control_indices']
                          for i in range(4)],[[0,1,2,3],[3,2,1,0],[0,1,2,3],[0,1,2,3]])

    def test_native_brep_roundtrip_retains_shared_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'curved.brep'
            self.shape.exportBrep(str(p))
            restored=cq.Shape.importBrep(str(p))
            receipt=audit(self.bp,self.sidecar,restored)
            self.assertEqual(receipt['native_edge_face_incidence'],{1:12,4:1})

    def test_conventional_sewing_does_not_fake_shared_four(self):
        _,s=native_surface_complex(nonmanifold=False)
        self.assertEqual(s['four_incident_edges'],0)

    def test_displacement_beyond_tolerance_breaks_common_edge(self):
        _,s=native_surface_complex(displaced_patch=1,offset=2e-5)
        self.assertEqual(s['four_incident_edges'],0)

    def test_idempotent_fixture(self):
        bp,meta=generate()
        self.assertEqual(bp,self.bp)
        self.assertEqual(json.dumps(meta,sort_keys=True),json.dumps(self.sidecar,sort_keys=True))

    def test_index_mutation_with_rehashed_bp_rejected(self):
        new=self.bp.replace('p 0 ', 'p 16 ', 1)
        self.assertNotEqual(new,self.bp)
        meta=copy.deepcopy(self.sidecar)
        meta['bp_sha256']=hashlib.sha256(new.encode()).hexdigest()
        meta['patches'][0]['control_indices'][0]=16
        meta['patches'][0]['sides'][0]['control_indices'][0]=16
        meta['patches'][0]['sides'][3]['control_indices'][0]=16
        with self.assertRaisesRegex(ValueError,'Shared edge control mismatch'):
            audit(new,meta)

    def test_off_curve_control_with_rehash_rejected(self):
        bp=self.bp.replace('v 0 0 -2.5','v 0.002 0 -2.5',1)
        meta=copy.deepcopy(self.sidecar)
        meta['bp_sha256']=hashlib.sha256(bp.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,'Curved polynomial mismatch'):
            audit(bp,meta)

    def test_reverse_flag_corruption_rejected(self):
        meta=copy.deepcopy(self.sidecar)
        meta['patches'][1]['reverse_v']=False
        with self.assertRaisesRegex(ValueError,'Wrong sheet direction'):
            audit(self.bp,meta)

    def test_wrong_scientific_claim_rejected(self):
        meta=copy.deepcopy(self.sidecar)
        meta['apmesh_tri_generation']='ACCEPTED'
        with self.assertRaisesRegex(ValueError,'False TRI run claim'):
            audit(self.bp,meta)

    def test_nonpolynomial_curve_explicitly_unsupported(self):
        negative=sine_nonpolynomial_exact_case()
        self.assertEqual(negative['exact_nonrational_cubic_representation'],
                         'IMPOSSIBLE_FOR_THIS_SOURCE')
        self.assertGreater(negative['fourth_derivative_at_v_quarter'],1.)


if __name__=='__main__':
    unittest.main()
