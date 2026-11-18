#!/usr/bin/env python3
"""Independent synthetic tests for exact-rational radial Bernstein geometry."""
from __future__ import annotations

from fractions import Fraction
import math
import unittest

from s3zc_exact_bernstein_radial_gate import (
    PILOT_BUDGET, _fraction, _split_half,
    certify_cylinder_radial, cylinder_squared_radius_net,
    require_exact_native_cylinder_envelope,
)


def patch_plane(x=25.0, y0=-0.02, y1=0.02, z0=0., z1=1.):
    """An axially oriented planar net close to the exact radius-25 cylinder."""
    return [(x, y0+(y1-y0)*i/3, z0+(z1-z0)*j/3)
            for j in range(4) for i in range(4)]


class ExactBernsteinS3Z3Tests(unittest.TestCase):
    def check(self, points=None, **kw):
        return certify_cylinder_radial(points if points is not None else patch_plane(),
                                        (0.,0.,0.),(0.,0.,1.),25.,**kw)

    def test_exact_float_to_fraction(self):
        self.assertEqual(_fraction(.125),Fraction(1,8))

    def test_original_budget_is_exact_fraction(self):
        self.assertEqual(PILOT_BUDGET,Fraction(1,1000))

    def test_exact_rational_net_shape(self):
        net,r=cylinder_squared_radius_net(patch_plane(),(0.,0.,0.),(0.,0.,1.),25.)
        self.assertEqual((len(net),len(net[0])),(7,7))
        self.assertTrue(all(isinstance(v,Fraction) for row in net for v in row))
        self.assertEqual(r,25)

    def test_synthetic_near_cylinder_certified(self):
        result=self.check()
        self.assertTrue(result['passed'])
        self.assertEqual(result['status'],'CERTIFIED_WITHIN_FLOAT_DEFINED_CYLINDER')

    def test_synthetic_large_radial_offset_rejected(self):
        self.assertFalse(self.check(patch_plane(x=25.02))['passed'])

    def test_wrong_radius_rejected(self):
        self.assertFalse(certify_cylinder_radial(patch_plane(),(0,0,0),(0,0,1),20)['passed'])

    def test_axis_direction_length_invariant(self):
        a=self.check()
        b=certify_cylinder_radial(patch_plane(),(0,0,0),(0,0,2.5),25)
        self.assertEqual(a['passed'],b['passed'])

    def test_offset_source_origin_invariant(self):
        original=patch_plane()
        moved=[(x+101.,y-13.,z+7.) for x,y,z in original]
        a=self.check()
        b=certify_cylinder_radial(moved,(101.,-13.,7.),(0,0,1),25)
        self.assertEqual(a['passed'],b['passed'])

    def test_symbolic_half_split_exact(self):
        grid=tuple(tuple(Fraction(i+j,12) for j in range(7)) for i in range(7))
        left,right=_split_half(grid,0)
        self.assertEqual(left[0],grid[0])
        self.assertEqual(right[-1],grid[-1])
        self.assertEqual(left[-1],right[0])

    def test_second_axis_split_exact(self):
        grid=tuple(tuple(Fraction(i+j,12) for j in range(7)) for i in range(7))
        a,b=_split_half(grid,1)
        self.assertEqual(tuple(row[-1] for row in a),tuple(row[0] for row in b))

    def test_inconclusive_shallow_depth_blocks(self):
        # A poorly bounded, highly curved polynomial must not be called pass.
        pts=patch_plane(y0=-1.0,y1=1.0)
        state=self.check(pts,max_depth=0)['status']
        self.assertNotEqual(state,'CERTIFIED_WITHIN_FLOAT_DEFINED_CYLINDER')

    def test_modified_budget_rejected(self):
        with self.assertRaisesRegex(ValueError,'budget'):
            self.check(budget=.002)

    def test_modified_depth_rejected(self):
        with self.assertRaisesRegex(ValueError,'depth'):
            self.check(max_depth=23)

    def test_nonfinite_control_rejected(self):
        p=patch_plane();p[5]=(math.inf,0.,0.)
        with self.assertRaisesRegex(ValueError,'finite'):
            self.check(p)

    def test_nonfinite_axis_rejected(self):
        with self.assertRaisesRegex(ValueError,'finite'):
            certify_cylinder_radial(patch_plane(),(0,0,0),(0,math.nan,1),25)

    def test_zero_axis_rejected(self):
        with self.assertRaisesRegex(ValueError,'Degenerate'):
            certify_cylinder_radial(patch_plane(),(0,0,0),(0,0,0),25)

    def test_negative_radius_rejected(self):
        with self.assertRaisesRegex(ValueError,'positive'):
            certify_cylinder_radial(patch_plane(),(0,0,0),(0,0,1),-25)

    def test_invalid_control_count_rejected(self):
        with self.assertRaisesRegex(ValueError,'sixteen'):
            self.check(patch_plane()[:-1])

    def test_bool_coordinate_rejected(self):
        pts=patch_plane();pts[0]=(True,0.,0.)
        with self.assertRaisesRegex(ValueError,'Boolean'):
            self.check(pts)

    def test_native_occt_cylinder_compiles_and_certifies(self):
        from OCP.gp import gp_Cylinder, gp_Ax3, gp_Pnt, gp_Dir
        cylinder=gp_Cylinder(gp_Ax3(gp_Pnt(0,0,0),gp_Dir(0,0,1)),25.)
        result=require_exact_native_cylinder_envelope(patch_plane(),cylinder)
        self.assertTrue(result['passed'])

    def test_native_occt_cylinder_rejects_out_of_budget(self):
        from OCP.gp import gp_Cylinder, gp_Ax3, gp_Pnt, gp_Dir
        cylinder=gp_Cylinder(gp_Ax3(gp_Pnt(0,0,0),gp_Dir(0,0,1)),25.)
        with self.assertRaisesRegex(ValueError,'Exact rational radial gate'):
            require_exact_native_cylinder_envelope(patch_plane(x=25.04),cylinder)

    def test_narrow_float_radial_margin_can_be_proven_exactly(self):
        points=[(25.00095,.04*i/3,j/3) for j in range(4) for i in range(4)]
        result=self.check(points)
        self.assertTrue(result['passed'])
        self.assertTrue(result['exact_rational_arithmetic_over_input_floats'])

    def test_exact_bernstein_net_split_preserves_polynomial(self):
        from math import comb
        def evaluate(net,u,v):
            b=lambda k,t: Fraction(comb(6,k))*t**k*(1-t)**(6-k)
            return sum(net[i][j]*b(i,u)*b(j,v) for i in range(7) for j in range(7))
        grid=tuple(tuple(Fraction(i+j,12) for j in range(7)) for i in range(7))
        l,r=_split_half(grid,0)
        t=Fraction(2,5);z=Fraction(7,11)
        self.assertEqual(evaluate(grid,t/2,z),evaluate(l,t,z))
        self.assertEqual(evaluate(grid,(t+1)/2,z),evaluate(r,t,z))

    def test_resource_limit_fails_closed(self):
        pts=patch_plane(y0=-1.0,y1=1.0)
        result=self.check(pts,max_nodes=1)
        self.assertFalse(result['passed'])
        self.assertEqual(result['status'],'INCONCLUSIVE_EXACT_BERNSTEIN_RESOURCE_LIMIT')

    def test_invalid_node_resource_limit_rejected(self):
        with self.assertRaisesRegex(ValueError,'resource budget'):
            self.check(max_nodes=0)

    def test_exact_radial_polynomial_matches_bicubic_evaluation(self):
        from math import comb
        netpoints=patch_plane(x=25.1,y0=-0.11,y1=0.07,z0=1.,z1=2.)
        polynomial,_=cylinder_squared_radius_net(netpoints,(0,0,0),(0,0,1),25)
        u=Fraction(2,5);v=Fraction(1,3)
        basis=lambda degree,k,t: Fraction(comb(degree,k))*t**k*(1-t)**(degree-k)
        poly=sum(polynomial[i][j]*basis(6,i,v)*basis(6,j,u)
                 for i in range(7) for j in range(7))
        x=sum(_fraction(netpoints[i*4+j][0])*basis(3,i,v)*basis(3,j,u)
              for i in range(4) for j in range(4))
        y=sum(_fraction(netpoints[i*4+j][1])*basis(3,i,v)*basis(3,j,u)
              for i in range(4) for j in range(4))
        self.assertEqual(poly,x*x+y*y)

    def test_exact_radial_projection_works_with_nonunit_vector(self):
        netpoints=patch_plane(x=25.1,y0=0.,y1=.04)
        unit,_=cylinder_squared_radius_net(netpoints,(0,0,0),(0,0,1),25)
        scaled,_=cylinder_squared_radius_net(netpoints,(0,0,0),(0,0,2.5),25)
        self.assertEqual(unit,scaled)

    def test_scope_is_not_formal_cad_certificate(self):
        r=self.check()
        self.assertFalse(r['native_cad_input_uncertainty_certified'])
        self.assertFalse(r['continuous_original_trimmed_face_certified'])


if __name__ == '__main__':
    unittest.main()