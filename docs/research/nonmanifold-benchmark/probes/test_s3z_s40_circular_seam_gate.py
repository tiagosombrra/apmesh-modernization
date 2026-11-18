#!/usr/bin/env python3
"""Hermetic directed tests for S3.Z fail-closed circular seam preparation."""
import hashlib
import math
import sys
import types
import unittest
from unittest.mock import patch

import s3z_s40_circular_seam_gate as s3z


class CircularSeamGateUnitTests(unittest.TestCase):
    def test_rejects_unavailable_original_bytes(self):
        with self.assertRaisesRegex(ValueError, 'STEP SHA-256'):
            s3z.check_input_hashes(b'unverified third-party STEP',b'parent')

    def test_rejects_parent_mutation(self):
        with patch.object(s3z,'ORIGINAL_STEP_SHA',hashlib.sha256(b'step').hexdigest()):
            with self.assertRaisesRegex(ValueError, 'parent BP'):
                s3z.check_input_hashes(b'step',b'corrupted')

    def test_valid_exact_pins(self):
        with patch.object(s3z,'ORIGINAL_STEP_SHA',hashlib.sha256(b'step').hexdigest()),\
             patch.object(s3z,'S3W_PARENT_SHA',hashlib.sha256(b'bp').hexdigest()):
            self.assertIsNone(s3z.check_input_hashes(b'step',b'bp'))

    def test_rejects_tolerance_relaxation(self):
        with self.assertRaisesRegex(ValueError, 'budget'):
            s3z.check_input_hashes(b'step',b'bp',budget_mm=.01)

    def test_source_circle_identity_set_is_pinned(self):
        self.assertEqual(s3z.TARGET_FACES,(1827,1907))
        self.assertEqual(set(s3z.TARGET_CIRCLES[1827]),{1523,252,1834,1886})
        self.assertEqual(set(s3z.TARGET_CIRCLES[1907]),{1911,1962,326,1593})

    def test_bernstein_line_midpoint(self):
        pts=[(0.,0.,0.),(1.,0.,0.),(2.,0.,0.),(3.,0.,0.)]
        self.assertEqual(s3z.bernstein_point(pts,(0,1,2,3),.5),(1.5,0.,0.))

    def test_normalization_with_nonfinite_and_zero_fails(self):
        for vec in ((0,0,0),(math.nan,0,0),(math.inf,0,0)):
            with self.subTest(vec=vec),self.assertRaises(ValueError):
                s3z.unit(vec)

    def test_control_movement_uses_native_inward_side(self):
        pts=[(0.,0.,0.),(1.,0.,0.),(2.,0.,0.),(3.,0.,0.)]
        directions=s3z.control_bias_directions(pts,(0,1,2,3),(0.,0.,1.),lambda p:p[1]>0)
        self.assertEqual(directions,((0.,1.,0.),(0.,1.,0.)))

    def test_reverses_direction_when_native_interior_is_negative(self):
        pts=[(0.,0.,0.),(1.,0.,0.),(2.,0.,0.),(3.,0.,0.)]
        directions=s3z.control_bias_directions(pts,(0,1,2,3),(0.,0.,1.),lambda p:p[1]<0)
        self.assertEqual(directions,((0.,-1.,0.),(0.,-1.,0.)))

    def test_ambiguous_inward_direction_fails_closed(self):
        pts=[(0.,0.,0.),(1.,0.,0.),(2.,0.,0.),(3.,0.,0.)]
        with self.assertRaisesRegex(ValueError,'Ambiguous'):
            s3z.control_bias_directions(pts,(0,1,2,3),(0.,0.,1.),lambda p:True)

    def test_coons_net_preserves_all_four_boundaries(self):
        bottom=[(u,0.,0.) for u in (0.,1/3,2/3,1.)]
        right=[(1.,v,0.) for v in (0.,1/3,2/3,1.)]
        top=[(u,1.,0.) for u in (1.,2/3,1/3,0.)]
        left=[(0.,v,0.) for v in (1.,2/3,1/3,0.)]
        net=s3z.coons_interior((bottom,right,top,left))
        self.assertEqual(list(net[0]),bottom)
        self.assertEqual([row[3] for row in net],right)
        self.assertEqual(list(reversed(net[3])),top)
        self.assertEqual([row[0] for row in reversed(net)],left)
        self.assertAlmostEqual(net[2][1][0],1/3)
        self.assertAlmostEqual(net[2][1][1],2/3)

    def test_coons_interior_rejects_shared_control_overlap(self):
        # Use an isolated _side provider for a self-contained synthetic patch.
        stub=types.ModuleType('s3r_s40_conforming_hole_join')
        stub._side=lambda p,l: {'bottom':p[:4], 'top':p[12:],
                                'left':p[::4], 'right':p[3::4]}[l]
        pts=[(float(i%4),float(i//4),0.) for i in range(16)]
        patch=tuple(range(16))
        with patch_dict_modules({'s3r_s40_conforming_hole_join':stub}):
            with self.assertRaisesRegex(ValueError,'overlap'):
                s3z.compose_controls(pts,[patch],{5:(7.,7.,0.)},first_new=0)

    def test_coons_interior_update_keeps_boundary_indices(self):
        stub=types.ModuleType('s3r_s40_conforming_hole_join')
        stub._side=lambda p,l: {'bottom':p[:4], 'top':p[12:],
                                'left':p[::4], 'right':p[3::4]}[l]
        pts=[(float(i%4)/3,float(i//4)/3,0.) for i in range(16)]
        with patch_dict_modules({'s3r_s40_conforming_hole_join':stub}):
            new,interior=s3z.compose_controls(pts,[tuple(range(16))],{1:(1/3,.03,0.)},first_new=0)
        self.assertEqual(interior,{5,6,9,10})
        self.assertEqual(new[1],(1/3,.03,0.))
        self.assertEqual(new[0],pts[0])
        self.assertNotEqual(new[5],pts[5])


class patch_dict_modules:
    """Tiny test-only sys.modules override with guaranteed rollback."""
    def __init__(self,values):self.values=values
    def __enter__(self):
        self.previous={k:sys.modules.get(k) for k in self.values}
        sys.modules.update(self.values)
    def __exit__(self,exc_type,exc,trace):
        for k,v in self.previous.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v


if __name__=='__main__':unittest.main()
