#!/usr/bin/env python3
"""Hermetic S40-F5 regression tests that do not contain private CAD coordinates."""
from __future__ import annotations

import math
import unittest

from s40f5_original_source_analytic_pilot import (
    _line_cubic, _point_cubic, exact_radial_bernstein_certificate,
    _circle_cubic_inward, FIXED_BUDGET_MM,
)


class AnalyticMathTests(unittest.TestCase):
    def setUp(self):
        self.c=(0.,0.,0.)
        self.p=(6.,0.,0.)
        self.q=(6*math.cos(-math.pi/4),6*math.sin(-math.pi/4),0.)

    def test_line_endpoints(self):
        net=_line_cubic((0.,0.,0.),(3.,6.,9.))
        self.assertEqual(_point_cubic(net,0.),(0.,0.,0.))
        self.assertEqual(_point_cubic(net,1.),(3.,6.,9.))

    def test_line_midpoint(self):
        net=_line_cubic((0.,0.,0.),(3.,6.,9.))
        self.assertEqual(_point_cubic(net,.5),(1.5,3.,4.5))

    def test_correct_inward_circle_tolerance(self):
        net,_=_circle_cubic_inward(self.p,self.q,self.c)
        evidence=exact_radial_bernstein_certificate(net,self.c)
        self.assertEqual(evidence['status'],'RATIONAL_FLOAT_INPUT_SUPPORT_PASS')
        self.assertLessEqual(evidence['upper_radial_bound_mm'],6.0000001)
        self.assertGreaterEqual(evidence['lower_radial_bound_mm'],6.-FIXED_BUDGET_MM)

    def test_unbiased_circle_fails_one_sided_trim_support(self):
        net,_=_circle_cubic_inward(self.p,self.q,self.c,inset=0.)
        with self.assertRaises(ValueError):
            exact_radial_bernstein_certificate(net,self.c)

    def test_marginal_inward_circle_fails_trim_support(self):
        net,_=_circle_cubic_inward(self.p,self.q,self.c,inset=.0002)
        with self.assertRaises(ValueError):
            exact_radial_bernstein_certificate(net,self.c)

    def test_wrong_radius_control_fails(self):
        net,_=_circle_cubic_inward(self.p,self.q,self.c)
        bad=list(net)
        bad[1]=(7.5,bad[1][1],0.)
        with self.assertRaises(ValueError):
            exact_radial_bernstein_certificate(bad,self.c)

    def test_outward_overshoot_is_detected_in_samples(self):
        net,_=_circle_cubic_inward(self.p,self.q,self.c,inset=0.)
        err=max(math.hypot(*_point_cubic(net,t)[:2])-6. for t in [i/1000 for i in range(1,1000)])
        self.assertGreater(err,1e-5)

    def test_error_budget_fixed(self):
        self.assertEqual(FIXED_BUDGET_MM,.001)

    def test_reverse_endpoints_rejected_by_direction(self):
        with self.assertRaises(ValueError):
            _circle_cubic_inward(self.q,self.p,self.c)

    def test_non_circle_endpoint_rejected(self):
        with self.assertRaises(ValueError):
            _circle_cubic_inward((9.,0.,0.),self.q,self.c)

    def test_zero_radial_curve_is_outside(self):
        net=[(0.,0.,0.)]*4
        with self.assertRaises(ValueError):
            exact_radial_bernstein_certificate(net,self.c)

    def test_certificate_not_misnamed_full_step(self):
        net,_=_circle_cubic_inward(self.p,self.q,self.c)
        result=exact_radial_bernstein_certificate(net,self.c)
        self.assertFalse(result['original_step_face_coverage_certified'])
        self.assertTrue(result['continuous_float_defined_radial_support_only'])

    def test_inconclusive_resource_guard(self):
        net,_=_circle_cubic_inward(self.p,self.q,self.c)
        with self.assertRaises(ValueError):
            exact_radial_bernstein_certificate(net,self.c,max_nodes=0)


if __name__=='__main__':unittest.main()
