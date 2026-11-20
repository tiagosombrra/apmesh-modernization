"""Directed mathematical and native CAD checks for the bounded S3.B pilot."""
import json
import math
import unittest

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.gp import gp_Cylinder, gp_Ax3, gp_Dir, gp_Pnt

from s3b_curved_source_screen import screen
from s3b_cylindrical_bicubic_pilot import (
    UnsupportedGeometry, approximate_cylindrical_face,
    synthetic_quarter_cylinder,
)
from audit_original_cad_planar_atlas import audit
from original_cad_planar_atlas import build_atlas


class SourceFaceScreenTests(unittest.TestCase):
    def test_all_planar_exact_candidates(self):
        shape=cq.Workplane('XY').box(2,3,4).val()
        r=screen(shape,model_id='SYNTHETIC_BOX',raw_sha256='test-only')
        self.assertEqual(r['face_classification_histogram'],{'EXACT_PLANAR_QUAD_CANDIDATE':6})
        self.assertEqual(r['native_nondegenerate_edge_incidence'],{2:12})
        self.assertEqual(r['source_degenerate_edges'],0)
        self.assertEqual(r['bp_conversion'],'NOT_RUN')
        self.assertEqual(r['original_external_multisheet_admission'],'NOT_GRANTED')

    def test_native_cylinder_support_and_periodic_flag(self):
        r=screen(cq.Workplane('XY').cylinder(4,2).val(),model_id='CYL',raw_sha256='test')
        self.assertEqual(r['face_classification_histogram']['ANALYTIC_CURVE_APPROX_OR_DECOMPOSE'],1)
        cyl=next(x for x in r['face_records'] if x['support_type']=='CYLINDER')
        self.assertTrue(cyl['native_support_is_u_periodic'])
        self.assertEqual(cyl['bp_conversion'],'NOT_RUN')

    def test_rational_bspline_detected_from_native_weights(self):
        f=synthetic_quarter_cylinder().toNURBS()
        r=screen(f,model_id='RATIONAL_LOCAL',raw_sha256='test')
        x=r['face_records'][0]
        self.assertEqual(x['category'],'RATIONAL_BSPLINE_APPROX_OR_DECOMPOSE')
        self.assertTrue(x['spline_details']['rational'])
        self.assertEqual(x['spline_details']['u_degree'],2)
        self.assertEqual(x['spline_details']['v_degree'],1)
        self.assertLess(x['spline_details']['minimum_weight'],1)
        self.assertFalse(x['spline_details']['all_weights_equal'])

    def test_hole_requires_explicit_trim(self):
        f=cq.Workplane('XY').rect(4,4).rect(1,1).extrude(1).val()
        r=screen(f,model_id='HOLE',raw_sha256='test')
        self.assertGreater(r['face_classification_histogram']['PLANAR_PARTITION_REQUIRED'],0)
        self.assertTrue(any(x['has_multiple_wires'] for x in r['face_records']))

    def test_source_face_screen_does_not_claim_external_multisheet(self):
        a=cq.Workplane('XY').box(1,1,1).val()
        b=cq.Workplane('XY').box(1,1,1).translate((1+1e-10,0,0)).val()
        r=screen(cq.Compound.makeCompound([a,b]),model_id='NEAR',raw_sha256='test')
        self.assertEqual(r['native_nondegenerate_edge_incidence'],{2:24})
        self.assertEqual(r['original_external_multisheet_admission'],'NOT_GRANTED')


class BoundedCylinderPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.face=synthetic_quarter_cylinder()
        cls.net,cls.loose=approximate_cylindrical_face(
            cls.face,absolute_budget_mm=.01,relative_budget=.01)

    def test_control_net_and_native_samples(self):
        self.assertEqual(len(self.net),16)
        self.assertTrue(self.loose['budget_pass'])
        self.assertEqual(self.loose['convergence'][-1]['sample_count'],33*33)
        self.assertEqual(self.loose['native_face_distance_samples'],49)
        self.assertGreater(self.loose['maximum_pointwise_sampled_error_mm'],0)
        self.assertLess(self.loose['maximum_pointwise_sampled_error_mm'],.01)
        self.assertEqual(self.loose['continuous_distance_bound'],'NOT_CERTIFIED')
        self.assertEqual(self.loose['apmesh_generation'],'NOT_RUN')

    def test_budget_violation_is_recorded_not_relaxed(self):
        _,strict=approximate_cylindrical_face(
            self.face,absolute_budget_mm=1e-5,relative_budget=.01)
        self.assertFalse(strict['budget_pass'])
        self.assertGreater(strict['maximum_pointwise_sampled_error_mm'],strict['effective_strict_budget_mm'])
        self.assertAlmostEqual(strict['maximum_pointwise_sampled_error_mm'],
                               self.loose['maximum_pointwise_sampled_error_mm'])

    def test_non_cylindrical_or_wrong_trim_rejected(self):
        flat=cq.Workplane('XY').box(1,1,1).val().Faces()[0]
        with self.assertRaisesRegex(UnsupportedGeometry,'Only cylindrical'):
            approximate_cylindrical_face(flat,absolute_budget_mm=.01,relative_budget=.01)
        full=cq.Workplane('XY').cylinder(4,3).val().Faces()[0]
        with self.assertRaisesRegex(UnsupportedGeometry,'four-edge'):
            approximate_cylindrical_face(full,absolute_budget_mm=.01,relative_budget=.01)

    def test_cylinder_larger_than_quarter_rejected(self):
        cyl=gp_Cylinder(gp_Ax3(gp_Pnt(0,0,0),gp_Dir(0,0,1)),3)
        f=cq.Face(BRepBuilderAPI_MakeFace(cyl,0,math.pi,0,4).Face())
        with self.assertRaisesRegex(UnsupportedGeometry,'Angular span'):
            approximate_cylindrical_face(f,absolute_budget_mm=.01,relative_budget=.01)

    def test_invalid_budgets_rejected(self):
        for bad in (0,-1,float('nan'),float('inf')):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    approximate_cylindrical_face(self.face,absolute_budget_mm=bad,relative_budget=.01)

    def test_independent_cad_atlas_gate_remains_separate(self):
        shape=cq.Workplane('XY').box(1,1,1).val()
        bp,sidecar=build_atlas(shape,'SYNTHETIC','test-sha')
        r=audit(shape,bp,sidecar,source_sha256='test-sha')
        self.assertEqual(r['validated_patches'],6)
        self.assertEqual(self.loose['full_original_model_converted'],False)
        self.assertNotEqual(self.loose['schema'],sidecar['schema'])


if __name__=='__main__':
    unittest.main()
