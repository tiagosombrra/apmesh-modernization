#!/usr/bin/env python3
"""Bidirectional source-edge coverage tests on original S40 arc descriptors.

The pin records come from original STEP #1307/#1336/#1415/#1444; the
OCP edges are reconstructed primitives, not imported original TopoDS_Edge.
This test must not be counted as a full native original-S40 CAD admission.
"""
from __future__ import annotations

import ast
import math
from pathlib import Path
import unittest

from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.GeomAbs import GeomAbs_Circle
from OCP.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt, gp_Vec
from scipy.optimize import minimize_scalar

SCRIPT = Path(__file__).with_name('s40f1_six_edge_planar_builder.py')
HELPERS = {'cubic_point','distance','curve_distance','check_curve_fit',
           'bezier_segment_distance','native_curve_to_bezier_chain_distance',
           '_unit','circle_piece','fit_circle_source_segments',
           'recover_inherited_source_chain'}
TREE = ast.parse(SCRIPT.read_text())
FUNCTIONS = [n for n in TREE.body if isinstance(n,ast.FunctionDef)
             and n.name in HELPERS]
assert {n.name for n in FUNCTIONS} == HELPERS
NAMESPACE = {'math':math, 'gp_Pnt':gp_Pnt, 'gp_Vec':gp_Vec,
             'GeomAbs_Circle':GeomAbs_Circle,
             'minimize_scalar':minimize_scalar, 'BUDGET_MM':0.001}
exec(compile(ast.Module(body=FUNCTIONS,type_ignores=[]),str(SCRIPT),'exec'),
     NAMESPACE)

# Verified STEP source values, not independent authorization to replace the STEP.
SOURCE_CIRCLE_DESCRIPTORS = {
    1307:((-22.,-67.17767,-33.75), math.pi/2,3*math.pi/4,
          (-22.,-73.17767,-33.75),(-26.2426406871,-71.4203106871,-33.75)),
    1336:((-22.,-67.17767,-33.75),3*math.pi/4,math.pi,
          (-26.2426406871,-71.4203106871,-33.75),(-28.,-67.17767,-33.75)),
    1415:((22.,-67.17767,-33.75),0.,math.pi/4,
          (28.,-67.17767,-33.75),(26.2426406871,-71.4203106871,-33.75)),
    1444:((22.,-67.17767,-33.75),math.pi/4,math.pi/2,
          (26.2426406871,-71.4203106871,-33.75),(22.,-73.17767,-33.75)),
}


def make_arc(edge_id):
    """Reconstruct analytic arc from pinned original STEP circle descriptors."""
    center, lo, hi, first, last = SOURCE_CIRCLE_DESCRIPTORS[edge_id]
    circle=gp_Circ(gp_Ax2(gp_Pnt(*center),gp_Dir(0.,0.,-1.),
                              gp_Dir(1.,0.,0.)),6.)
    adaptor=BRepAdaptor_Curve(BRepBuilderAPI_MakeEdge(circle,lo,hi).Edge())
    return adaptor,first,last


class OriginalS40ArcDescriptorTests(unittest.TestCase):
    def test_four_original_source_circle_descriptors_fit_one_cubic_each(self):
        for edge_id in SOURCE_CIRCLE_DESCRIPTORS:
            with self.subTest(edge=edge_id):
                curve,first,last=make_arc(edge_id)
                self.assertEqual(curve.GetType(),GeomAbs_Circle)
                self.assertLess(NAMESPACE['distance'](curve.Value(curve.FirstParameter()).Coord(), first),1e-9)
                self.assertLess(NAMESPACE['distance'](curve.Value(curve.LastParameter()).Coord(), last),1e-9)
                nets,forward=NAMESPACE['fit_circle_source_segments'](curve)
                self.assertEqual(len(nets),1)
                inverse=NAMESPACE['native_curve_to_bezier_chain_distance'](curve,nets)
                self.assertLess(forward,0.000035)
                self.assertLess(inverse,0.000035)
                self.assertLess(max(forward,inverse),0.001)

    def test_missing_half_arc_is_rejected_by_reverse_projection(self):
        arc,_,_=make_arc(1307)
        a,b=arc.FirstParameter(),arc.LastParameter()
        half=NAMESPACE['circle_piece'](arc,a,(a+b)/2)
        forward=max(NAMESPACE['curve_distance'](arc,NAMESPACE['cubic_point'](half,k/32))
                    for k in range(33))
        backward=NAMESPACE['native_curve_to_bezier_chain_distance'](arc,[half])
        self.assertLess(forward,0.001)
        self.assertGreater(backward,1.)

    def test_complete_two_half_arcs_restore_source_coverage(self):
        arc,_,_=make_arc(1415)
        a,b=arc.FirstParameter(),arc.LastParameter()
        left=NAMESPACE['circle_piece'](arc,a,(a+b)/2)
        right=NAMESPACE['circle_piece'](arc,(a+b)/2,b)
        self.assertEqual(left[-1],right[0])
        error=NAMESPACE['native_curve_to_bezier_chain_distance'](arc,[left,right])
        self.assertLess(error,0.00002)

    def test_entire_arc_not_accidentally_accepted_from_wrong_source_center(self):
        arc,_,_=make_arc(1307)
        other,_,_=make_arc(1415)
        net=NAMESPACE['circle_piece'](other,other.FirstParameter(),other.LastParameter())
        self.assertGreater(NAMESPACE['native_curve_to_bezier_chain_distance'](arc,[net]),40.)

    def test_endpoints_and_interior_sample_are_measured(self):
        arc,_,_=make_arc(1307)
        net=NAMESPACE['circle_piece'](arc,arc.FirstParameter(),arc.LastParameter())
        shifted=tuple(tuple(x+0.002 if j==0 else x for j,x in enumerate(p)) for p in net)
        err=NAMESPACE['native_curve_to_bezier_chain_distance'](arc,[shifted],samples=17)
        self.assertGreater(err,0.001)

    def test_near_endpoint_native_distance_uses_bounded_cubic(self):
        arc,first,_=make_arc(1307)
        net=NAMESPACE['circle_piece'](arc,arc.FirstParameter(),arc.LastParameter())
        self.assertLess(NAMESPACE['bezier_segment_distance'](net,first),1e-12)

    def test_bidirectional_exact_segment_endpoint_join(self):
        arc,_,_=make_arc(1336)
        a,b=arc.FirstParameter(),arc.LastParameter()
        halves=[NAMESPACE['circle_piece'](arc,a,(a+b)/2),
                NAMESPACE['circle_piece'](arc,(a+b)/2,b)]
        self.assertEqual(halves[0][-1],halves[1][0])
        self.assertLess(NAMESPACE['native_curve_to_bezier_chain_distance'](arc,halves),0.001)

    def test_coverage_density_rejects_zero(self):
        arc,_,_=make_arc(1307)
        net=NAMESPACE['circle_piece'](arc,arc.FirstParameter(),arc.LastParameter())
        with self.assertRaises(ValueError):
            NAMESPACE['native_curve_to_bezier_chain_distance'](arc,[net],samples=0)

    def test_coverage_density_rejects_boolean(self):
        arc,_,_=make_arc(1307)
        net=NAMESPACE['circle_piece'](arc,arc.FirstParameter(),arc.LastParameter())
        with self.assertRaises(ValueError):
            NAMESPACE['native_curve_to_bezier_chain_distance'](arc,[net],samples=True)

    def test_empty_chain_is_rejected(self):
        arc,_,_=make_arc(1307)
        with self.assertRaises(ValueError):
            NAMESPACE['native_curve_to_bezier_chain_distance'](arc,[])

    def test_invalid_degenerate_net_is_rejected(self):
        net=((0.,0.,0.),)*3
        with self.assertRaises(ValueError):
            NAMESPACE['bezier_segment_distance'](net,(0.,0.,0.))

    def test_nan_native_query_is_rejected(self):
        arc,_,_=make_arc(1307)
        net=NAMESPACE['circle_piece'](arc,arc.FirstParameter(),arc.LastParameter())
        with self.assertRaises(ValueError):
            NAMESPACE['bezier_segment_distance'](net,(math.nan,0.,0.))

    def test_invalid_projection_divisions_rejected(self):
        arc,_,_=make_arc(1307)
        net=NAMESPACE['circle_piece'](arc,arc.FirstParameter(),arc.LastParameter())
        with self.assertRaises(ValueError):
            NAMESPACE['bezier_segment_distance'](net,net[0],divisions=0)

    def test_source_reverse_works_with_reversed_control_order(self):
        arc,_,_=make_arc(1444)
        net=NAMESPACE['circle_piece'](arc,arc.FirstParameter(),arc.LastParameter())
        self.assertLess(NAMESPACE['native_curve_to_bezier_chain_distance'](arc,[net[::-1]]),0.001)

    def test_clipped_source_curve_far_from_candidate_is_rejected(self):
        arc,_,_=make_arc(1307)
        other,_,_=make_arc(1336)
        net=NAMESPACE['circle_piece'](other,other.FirstParameter(),other.LastParameter())
        self.assertGreater(NAMESPACE['native_curve_to_bezier_chain_distance'](arc,[net]),0.1)


if __name__=='__main__':
    unittest.main()
