#!/usr/bin/env python3
"""Exact-rational unit tests and explicitly private-pinned S40-F6 regression."""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import os
import unittest

import s40f8_exact_planar_jacobian as s


def bilinear_patch(*, reverse=False):
    """Create a 4x4 control grid for a regular linear map with optional flip."""
    points=[]
    for j in range(4):
        for i in range(4):
            u,v=Fraction(i,3), Fraction(j,3)
            points.append((1-u if reverse else u,v,Fraction(0)))
    return points,tuple(range(16))


def bernstein_evaluate(net, u, v):
    """Evaluate the exact bi-degree-5 polynomial for test oracles."""
    from math import comb
    return sum(net[i][j]*comb(5,i)*u**i*(1-u)**(5-i)*
               comb(5,j)*v**j*(1-v)**(5-j) for i in range(6) for j in range(6))


class ExactMathTests(unittest.TestCase):
    def test_linear_patch_strictly_positive_everywhere(self):
        pts,ids=bilinear_patch()
        net=s.jacobian_net(pts,ids,(0,0,1))
        self.assertEqual({v for row in net for v in row},{Fraction(1)})
        self.assertEqual(s.certify_strict_sign(net)['status'],'CERTIFIED_POSITIVE')

    def test_reversed_linear_patch_rejected(self):
        pts,ids=bilinear_patch(reverse=True)
        net=s.jacobian_net(pts,ids,(0,0,1))
        self.assertEqual({v for row in net for v in row},{Fraction(-1)})
        self.assertEqual(s.certify_strict_sign(net)['status'],'NONPOSITIVE_CERTIFIED')

    def test_zero_jacobian_rejected(self):
        pts,ids=bilinear_patch()
        pts=[(x,Fraction(0),Fraction(0)) for x,y,z in pts]
        net=s.jacobian_net(pts,ids,(0,0,1))
        self.assertEqual(s.certify_strict_sign(net)['status'],'NONPOSITIVE_CERTIFIED')

    def test_exact_bernstein_product_on_bivariate_functions(self):
        a=[[Fraction(i+3*j+1) for j in range(4)] for i in range(3)]
        b=[[Fraction(2*i-j+4) for j in range(3)] for i in range(4)]
        c=s.bernstein_product(a,(2,3),b,(3,2))
        self.assertEqual((len(c),len(c[0])),(6,6))
        for u,v in [(Fraction(0),Fraction(0)), (Fraction(1),Fraction(1)),
                    (Fraction(1,3),Fraction(2,7)),(Fraction(4,5),Fraction(7,9))]:
            from math import comb
            evala=sum(a[i][j]*comb(2,i)*u**i*(1-u)**(2-i)*comb(3,j)*v**j*(1-v)**(3-j) for i in range(3) for j in range(4))
            evalb=sum(b[i][j]*comb(3,i)*u**i*(1-u)**(3-i)*comb(2,j)*v**j*(1-v)**(2-j) for i in range(4) for j in range(3))
            self.assertEqual(bernstein_evaluate(c,u,v),evala*evalb)

    def test_split_preserves_exact_polynomial(self):
        pts,ids=bilinear_patch()
        grid=s.jacobian_net(pts,ids,(0,0,1))
        # Nonconstant polynomial to test both parameter axes.
        grid=[[v+Fraction(i*i+2*j,5) for j,v in enumerate(row)] for i,row in enumerate(grid)]
        for axis in [0,1]:
            left,right=s.split_net(grid,axis)
            for u,v in [(Fraction(1,7),Fraction(2,3)),(Fraction(3,7),Fraction(1,4))]:
                p=(u/2,v) if axis==0 else (u,v/2)
                q=((u+1)/2,v) if axis==0 else (u,(v+1)/2)
                self.assertEqual(bernstein_evaluate(left,u,v),bernstein_evaluate(grid,*p))
                self.assertEqual(bernstein_evaluate(right,u,v),bernstein_evaluate(grid,*q))

    def test_false_root_near_corner_is_not_silently_accepted(self):
        pts,ids=bilinear_patch()
        grid=s.jacobian_net(pts,ids,(0,0,1))
        grid[-1][-1]=-Fraction(1,10**11)
        self.assertNotEqual(s.certify_strict_sign(grid,max_depth=3)['status'],'CERTIFIED_POSITIVE')
        self.assertLess(bernstein_evaluate(grid,Fraction(1),Fraction(1)),0)

    def test_invalid_bp_fails_strict_parser(self):
        with self.assertRaises(ValueError):
            s.parse_decimal_bp(b'v 0 0 0\np 0 1 2\n')

    def test_tampered_private_bp_rejected_before_certificate(self):
        with self.assertRaises(ValueError):
            s.audit_f6(b'// wrong input\n')

    def test_pinned_sha_is_known(self):
        self.assertEqual(s.F6_SHA256,'72b8756c948a7a7da19c9f2a9a7099673e81a30573f19e4820abf27ba720f0a7')


class PrivateOriginalF6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=os.environ.get('APMESH_S40F8_PRIVATE_F6_BP')
        if not path:
            raise unittest.SkipTest('The original S40-F6 private BP was not supplied')
        cls.raw=Path(path).read_bytes()

    def test_exact_private_pin_and_cardinality(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),s.F6_SHA256)
        points,patches=s.parse_decimal_bp(self.raw)
        self.assertEqual((len(points),len(patches)),(104,8))

    def test_eight_jacobians_have_exact_enclosure(self):
        r=s.audit_f6(self.raw,max_depth=12)
        self.assertTrue(r['all_jacobians_bounded_below_minus_5e_minus_11_mm2'])
        self.assertFalse(r['all_jacobians_strictly_positive'])
        self.assertEqual(sum(c['classification']=='CERTIFIED_STRICT_POSITIVE' for c in r['certificates']),5)

    def test_boundary_roundoff_and_exact_zero_are_disclosed(self):
        cert=s.audit_f6(self.raw)['certificates']
        self.assertEqual([x['patch_index'] for x in cert if x['corners_have_exact_negative']],[0,3])
        self.assertEqual([x['patch_index'] for x in cert if x['corners_have_exact_zero']],[1])
        self.assertTrue(all(x['minimum_corner_jacobian_mm2']> -5e-11 for x in cert))

    def test_exact_corner_matches_direct_cross_derivative(self):
        points,patches=s.parse_decimal_bp(self.raw)
        for pid in [0,1,3]:
            net=s.jacobian_net(points,patches[pid],s.NORMALS[s.FACE_IDS[pid]])
            for u,v in [(0,0),(3,0),(0,3),(3,3)]:
                patch=patches[pid]
                p=lambda i,j:points[patch[j*4+i]]
                du=tuple(3*(p(u+1,v)[k]-p(u,v)[k]) if u==0 else 3*(p(u,v)[k]-p(u-1,v)[k]) for k in range(3))
                dv=tuple(3*(p(u,v+1)[k]-p(u,v)[k]) if v==0 else 3*(p(u,v)[k]-p(u,v-1)[k]) for k in range(3))
                n=s.NORMALS[s.FACE_IDS[pid]]
                cross=(du[1]*dv[2]-du[2]*dv[1],du[2]*dv[0]-du[0]*dv[2],du[0]*dv[1]-du[1]*dv[0])
                self.assertEqual(sum(n[k]*cross[k] for k in range(3)),net[5 if u else 0][5 if v else 0])


if __name__=='__main__':
    unittest.main()
