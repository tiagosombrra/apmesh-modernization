#!/usr/bin/env python3
"""Hermetic geometry and source-indexed curve-chaining tests for S40-F1.

These are synthetic/native-primitive unit tests, not full original-S40 BP tests.
"""
from __future__ import annotations

import ast
import hashlib
import math
from pathlib import Path
import unittest

from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.GeomAbs import GeomAbs_Circle
from OCP.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt, gp_Vec
from scipy.optimize import minimize_scalar

TARGET = Path(__file__).with_name('s40f1_six_edge_planar_builder.py')
HELPERS = {'cubic_point','distance','curve_distance','check_curve_fit','_unit',
           'circle_piece','fit_circle_source_segments','recover_inherited_source_chain'}
tree = ast.parse(TARGET.read_text(encoding='utf-8'))
functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in HELPERS]
source_module=ast.Module(body=functions,type_ignores=[])
# Read the exact function definitions under test; do not fork the implementation.
ns={'math':math,'gp_Pnt':gp_Pnt,'gp_Vec':gp_Vec,
    'GeomAbs_Circle':GeomAbs_Circle,'minimize_scalar':minimize_scalar,'BUDGET_MM':0.001}
exec(compile(source_module,str(TARGET),'exec'),ns)


def circle(radius=25,angle=1.8):
    """Use a real Open CASCADE analytic circular EDGE_CURVE primitive."""
    c=gp_Circ(gp_Ax2(gp_Pnt(0,0,0),gp_Dir(0,0,1)),radius)
    return BRepAdaptor_Curve(BRepBuilderAPI_MakeEdge(c,0.,angle).Edge())


def straight():
    return BRepAdaptor_Curve(BRepBuilderAPI_MakeEdge(gp_Pnt(0,0,0),gp_Pnt(3,0,0)).Edge())


class NativePrimitiveCurveTests(unittest.TestCase):
    def test_cubic_endpoints(self):
        net=((0.,0.,0.),(1.,0.,0.),(2.,0.,0.),(3.,0.,0.))
        self.assertEqual(ns['cubic_point'](net,0),net[0])
        self.assertEqual(ns['cubic_point'](net,1),net[3])

    def test_cubic_midpoint(self):
        net=((0.,0.,0.),(0.,2.,0.),(2.,2.,0.),(2.,0.,0.))
        self.assertAlmostEqual(ns['cubic_point'](net,.5)[1],1.5)

    def test_circle_one_piece_start_end_match(self):
        c=circle(25,.2);a,b=c.FirstParameter(),c.LastParameter()
        net=ns['circle_piece'](c,a,b)
        self.assertLess(ns['distance'](net[0],c.Value(a).Coord()),1e-12)
        self.assertLess(ns['distance'](net[-1],c.Value(b).Coord()),1e-12)

    def test_circle_divides_large_arc(self):
        pieces,err=ns['fit_circle_source_segments'](circle(25,1.8))
        self.assertGreaterEqual(len(pieces),2)
        self.assertLess(err,0.00075)

    def test_circle_uses_native_radius(self):
        p1,_=ns['fit_circle_source_segments'](circle(1.,1.))
        p2,_=ns['fit_circle_source_segments'](circle(80.,1.))
        self.assertGreater(len(p2),len(p1))

    def test_arc_segments_share_exact_endpoints(self):
        pieces,_=ns['fit_circle_source_segments'](circle(25,3.1))
        for a,b in zip(pieces,pieces[1:]):self.assertEqual(a[-1],b[0])

    def test_native_curve_projection_within_budget(self):
        c=circle(25,1.4);pieces,err=ns['fit_circle_source_segments'](c)
        for net in pieces:
            for j in range(13):
                p=ns['cubic_point'](net,j/12)
                self.assertLess(ns['curve_distance'](c,p),0.001)

    def test_invalid_arc_rejects_reverse_interval(self):
        with self.assertRaises(ValueError):ns['circle_piece'](circle(),1.,0.)

    def test_invalid_arc_rejects_large_single_interval(self):
        with self.assertRaises(ValueError):ns['circle_piece'](circle(angle=4.),0.,4.)

    def test_tangent_helper_rejects_zero(self):
        with self.assertRaises(ValueError):ns['_unit']((0.,0.,0.))

    def test_non_circle_rejects_circular_builder(self):
        with self.assertRaises(ValueError):ns['fit_circle_source_segments'](straight())

    def test_non_circle_rejects_arc_piece(self):
        with self.assertRaises(ValueError):ns['circle_piece'](straight(),0.,1.)

    def test_budget_fails_closed_on_zero(self):
        with self.assertRaises(ValueError):ns['fit_circle_source_segments'](circle(25,1.8),limit=0)

    def test_curve_projection_line(self):
        self.assertLess(ns['curve_distance'](straight(),(1.,0.,0.)),1e-10)
        self.assertAlmostEqual(ns['curve_distance'](straight(),(1.,.2,0.)),.2,places=8)

    def test_source_chain_two_exact_indexed_segments(self):
        c=straight()
        points=[(0.,0.,0.),(.5,0.,0.),(1.,0.,0.),(1.5,0.,0.),
                (2.,0.,0.),(2.5,0.,0.),(3.,0.,0.)]
        ns['coordinates']=lambda table,vid:table[vid]
        table={12:(0.,0.,0.),13:(3.,0.,0.)}
        first=(2,'bottom',(0,1,2,3));second=(3,'right',(3,4,5,6))
        entry={'start_vertex_id':12,'end_vertex_id':13}
        chain=ns['recover_inherited_source_chain'](table,entry,c,points,[second,first])
        self.assertEqual(chain,[first,second])

    def test_source_chain_reverse_input(self):
        c=straight()
        points=[(0.,0.,0.),(1.,0.,0.),(2.,0.,0.),(3.,0.,0.)]
        ns['coordinates']=lambda table,vid:table[vid]
        entry={'start_vertex_id':12,'end_vertex_id':13}
        chain=ns['recover_inherited_source_chain']({12:points[0],13:points[3]},entry,c,points,[(1,'top',(3,2,1,0))])
        self.assertEqual(chain[0][2],(0,1,2,3))

    def test_source_chain_rejects_duplicate_start(self):
        c=straight();pts=[(0.,0.,0.),(1.,0.,0.),(2.,0.,0.),(3.,0.,0.)]
        ns['coordinates']=lambda table,vid:table[vid]
        entry={'start_vertex_id':12,'end_vertex_id':13}
        with self.assertRaisesRegex(ValueError,'unique indexed start'):
            ns['recover_inherited_source_chain']({12:pts[0],13:pts[3]},entry,c,pts,
                [(1,'bottom',(0,1,2,3)),(2,'bottom',(0,1,2,3))])

    def test_source_chain_rejects_unmatched_endpoint(self):
        c=straight();pts=[(0.,0.,0.),(.5,0.,0.),(1.,0.,0.),(1.5,0.,0.)]
        ns['coordinates']=lambda table,vid:table[vid]
        entry={'start_vertex_id':12,'end_vertex_id':13}
        with self.assertRaisesRegex(ValueError,'missing/ambiguous'):
            ns['recover_inherited_source_chain']({12:(0.,0.,0.),13:(3.,0.,0.)},entry,c,pts,
                [(1,'bottom',(0,1,2,3))])


if __name__=='__main__':unittest.main()
