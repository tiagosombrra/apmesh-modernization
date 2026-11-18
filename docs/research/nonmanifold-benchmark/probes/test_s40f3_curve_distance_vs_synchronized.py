#!/usr/bin/env python3
"""Independent OCP arc tests for geometric rather than synchronized parameter error."""
from __future__ import annotations

import ast
import math
from pathlib import Path
import unittest

from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt
from OCP.GeomAbs import GeomAbs_Circle
from scipy.optimize import minimize_scalar
from OCP.gp import gp_Vec

FILE=Path(__file__).with_name('s40f1_six_edge_planar_builder.py')
HELPERS={'cubic_point','distance','curve_distance','check_curve_fit','_unit',
         'circle_piece','fit_circle_source_segments',
         'bezier_segment_distance','native_curve_to_bezier_chain_distance'}
tree=ast.parse(FILE.read_text())
funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in HELPERS]
assert {n.name for n in funcs}==HELPERS
ns={'math':math,'gp_Pnt':gp_Pnt,'gp_Vec':gp_Vec,'GeomAbs_Circle':GeomAbs_Circle,
    'minimize_scalar':minimize_scalar,'BUDGET_MM':0.001}
exec(compile(ast.Module(body=funcs,type_ignores=[]),str(FILE),'exec'),ns)


def original_circle(*,radius=6.,start=0.,angle=math.pi/4):
    """Construct a bounded native OCP arc, not an infinite-support circle."""
    circ=gp_Circ(gp_Ax2(gp_Pnt(0.,0.,-33.75),gp_Dir(0.,0.,1.)),radius)
    return BRepAdaptor_Curve(BRepBuilderAPI_MakeEdge(circ,start,start+angle).Edge())


def point_to_point_max(curve,controls,density=129):
    a,b=curve.FirstParameter(),curve.LastParameter()
    return max(ns['distance'](ns['cubic_point'](controls,i/(density-1)),
                curve.Value(a+(b-a)*i/(density-1)).Coord()) for i in range(density))


def radial_max(curve,controls,density=129):
    c=curve.Circle()
    center=c.Location().Coord()
    return max(abs(ns['distance'](ns['cubic_point'](controls,i/(density-1)),center)-c.Radius())
               for i in range(density))


class SourceArcMetricTests(unittest.TestCase):
    def setUp(self):
        self.arc=original_circle()
        self.net=ns['circle_piece'](self.arc,self.arc.FirstParameter(),self.arc.LastParameter())

    def test_source_geometry_45_degrees_6_mm_is_one_piece(self):
        pieces,err=ns['fit_circle_source_segments'](self.arc)
        self.assertEqual(len(pieces),1)
        self.assertLess(err,0.001)
        self.assertEqual(pieces[0],self.net)

    def test_naive_synchronized_error_is_false_fail(self):
        self.assertGreater(point_to_point_max(self.arc,self.net),0.005)
        self.assertLess(radial_max(self.arc,self.net),0.00003)

    def test_original_trimmed_edge_distance_under_budget(self):
        sampled=max(ns['curve_distance'](self.arc,ns['cubic_point'](self.net,i/64),divisions=64)
                    for i in range(65))
        self.assertLess(sampled,0.00003)
        self.assertGreater(sampled,0.)

    def test_curve_distance_checks_bounded_trim_not_support_circle(self):
        wrong_arc=original_circle(start=math.pi/2)
        sample=ns['cubic_point'](self.net,.5)
        self.assertGreater(ns['curve_distance'](wrong_arc,sample,divisions=64),1.)

    def test_native_curve_not_bypassable_by_out_of_plane_controls(self):
        raised=list(self.net)
        raised[1]=(raised[1][0],raised[1][1],raised[1][2]+.1)
        deviation,ok=ns['check_curve_fit'](raised,range(4),self.arc)
        self.assertFalse(ok)
        self.assertGreater(deviation,.001)

    def test_reversed_original_parameter_interval_is_rejected(self):
        with self.assertRaises(ValueError):
            ns['circle_piece'](self.arc,self.arc.LastParameter(),self.arc.FirstParameter())

    def test_gap_between_consecutive_piece_endpoints_remains_zero(self):
        curve=original_circle(radius=25.,angle=2.1)
        pieces,err=ns['fit_circle_source_segments'](curve)
        self.assertGreaterEqual(len(pieces),2)
        self.assertTrue(all(a[-1]==b[0] for a,b in zip(pieces,pieces[1:])))
        self.assertLess(err,.00075)

    def test_sufficiently_strict_budget_fails_closed(self):
        with self.assertRaises(ValueError):
            ns['fit_circle_source_segments'](self.arc,limit=0)

    def test_numerical_translated_circle(self):
        c=gp_Circ(gp_Ax2(gp_Pnt(125.,-78.,-33.75),gp_Dir(0,0,1)),6.)
        arc=BRepAdaptor_Curve(BRepBuilderAPI_MakeEdge(c,math.pi/3,math.pi/3+math.pi/4).Edge())
        patches,err=ns['fit_circle_source_segments'](arc)
        self.assertEqual(len(patches),1)
        self.assertLess(err,.001)

    def test_no_incorrect_claim_of_continuous_hausdorff(self):
        # The geometric verification is sampled against native trimmed arcs.
        self.assertGreater(point_to_point_max(self.arc,self.net),radial_max(self.arc,self.net))

if __name__=='__main__':unittest.main()
