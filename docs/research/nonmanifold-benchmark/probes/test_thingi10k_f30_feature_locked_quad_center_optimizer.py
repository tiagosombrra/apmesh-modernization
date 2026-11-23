#!/usr/bin/env python3
"""Hermetic F30 geometry and negative controls without any Thingi10K model bytes."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import thingi10k_f30_feature_locked_quad_center_optimizer as m

TRI = ((0.,0.,0.),(1.,0.,0.),(0.,1.,0.))
EQUILATERAL = ((0.,0.,0.),(2.,0.,0.),(1.,math.sqrt(3),0.))


def qrecord(lo=45., hi=135., jac=0.71):
    return {'min_angle_deg':lo,'max_angle_deg':hi,'min_scaled_jacobian':jac,
            'area':1.,'max_plane_residual':0.}


def synthetic_writer():
    return (b'# a synthetic QUAD\nv 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\n'
            b'f 1 2 3 4\n')


class OriginalSourceBoundaryTests(unittest.TestCase):
    def test_01_candidate_count(self):
        self.assertEqual(len(m.candidate_weights()),171)

    def test_02_candidate_weights_positive(self):
        self.assertTrue(all(all(0 < w < 1 for w in r) for r in m.candidate_weights()))

    def test_03_candidate_weights_sum_one(self):
        self.assertTrue(all(abs(math.fsum(r)-1)<1e-14 for r in m.candidate_weights()))

    def test_04_candidate_denominator_bound(self):
        self.assertTrue(all(min(r) >= m.MIN_BARYCENTRIC_WEIGHT-1e-14
                            for r in m.candidate_weights()))

    def test_05_candidate_deterministic_order(self):
        self.assertEqual(m.candidate_weights(),m.candidate_weights())

    def test_06_centroid_coordinates(self):
        self.assertEqual(m.barycentric(TRI,(1/3,1/3,1/3)),(1/3,1/3,0.))

    def test_07_barycentric_edge_rejected(self):
        with self.assertRaises(ValueError):m.barycentric(TRI,(0.,.5,.5))

    def test_08_barycentric_negative_rejected(self):
        with self.assertRaises(ValueError):m.barycentric(TRI,(-.1,.5,.6))

    def test_09_barycentric_sum_rejected(self):
        with self.assertRaises(ValueError):m.barycentric(TRI,(.1,.1,.1))

    def test_10_barycentric_nonfinite_rejected(self):
        with self.assertRaises(ValueError):m.barycentric(TRI,(float('nan'),.5,.5))

    def test_11_midpoint_exact(self):
        self.assertEqual(m.midpoint((0.,0.,0.),(2.,4.,6.)),(1.,2.,3.))

    def test_12_triangle_angles_right(self):
        self.assertEqual(tuple(round(x) for x in m.source_triangle_corners(TRI)),(90,45,45))

    def test_13_triangle_angles_equilateral(self):
        self.assertTrue(all(abs(x-60)<1e-9 for x in m.source_triangle_corners(EQUILATERAL)))

    def test_14_triangle_corner_sum_180(self):
        self.assertAlmostEqual(math.fsum(m.source_triangle_corners(TRI)),180,places=8)

    def test_15_degenerate_source_rejected(self):
        with self.assertRaises(ValueError):m.source_triangle_corners(((0.,0.,0.),)*3)

    def test_16_wrong_source_arity_rejected(self):
        with self.assertRaises(ValueError):m.source_triangle_corners(((0.,0.,0.),)*2)

    def test_17_reference_facet_shape_positive(self):
        values=m.candidate_metrics(TRI,(1/3,1/3,0.))
        self.assertEqual(len(values),3)
        self.assertTrue(all(v['min_scaled_jacobian']>0 for v in values))

    def test_18_reference_facet_areas_sum_source(self):
        values=m.candidate_metrics(TRI,(1/3,1/3,0.))
        self.assertAlmostEqual(math.fsum(v['area'] for v in values),0.5)

    def test_19_invalid_candidate_center_rejected(self):
        with self.assertRaises(ValueError):m.candidate_metrics(TRI,(math.inf,0.,0.))

    def test_20_outside_facet_rejected_by_convexity(self):
        with self.assertRaises(ValueError):m.candidate_metrics(TRI,(3.,3.,0.))


class NonRegressionTests(unittest.TestCase):
    def test_21_identical_patch_metrics_nondominated(self):
        self.assertTrue(m.dominates_or_equals([qrecord()]*3,[qrecord()]*3))

    def test_22_shorter_metric_record_rejected(self):
        with self.assertRaises(ValueError):m.dominates_or_equals([qrecord()]*2,[qrecord()]*3)

    def test_23_lower_min_angle_rejected(self):
        v=[qrecord()]*3; u=[qrecord(lo=44.)]*3
        self.assertFalse(m.dominates_or_equals(u,v))

    def test_24_higher_max_angle_rejected(self):
        self.assertFalse(m.dominates_or_equals([qrecord(hi=136.)]*3,[qrecord()]*3))

    def test_25_lower_scaled_jacobian_rejected(self):
        self.assertFalse(m.dominates_or_equals([qrecord(jac=.70)]*3,[qrecord()]*3))

    def test_26_better_all_metrics_accepted(self):
        self.assertTrue(m.dominates_or_equals([qrecord(46.,134.,.72)]*3,[qrecord()]*3))

    def test_27_one_regressive_quad_rejected(self):
        self.assertFalse(m.dominates_or_equals([qrecord(46.),qrecord(lo=44.),qrecord()],
                                              [qrecord()]*3))

    def test_28_equal_metrics_not_a_strict_improvement(self):
        self.assertFalse(m.meaningfully_better([qrecord()]*3,[qrecord()]*3))

    def test_29_min_angle_improvement_counts(self):
        self.assertTrue(m.meaningfully_better([qrecord(lo=46.)]*3,[qrecord()]*3))

    def test_30_max_angle_improvement_counts(self):
        self.assertTrue(m.meaningfully_better([qrecord(hi=134.)]*3,[qrecord()]*3))

    def test_31_scaled_jac_improvement_counts(self):
        self.assertTrue(m.meaningfully_better([qrecord(jac=.73)]*3,[qrecord()]*3))

    def test_32_small_numerical_noise_not_improvement(self):
        self.assertFalse(m.meaningfully_better([qrecord(lo=45.+1e-9,hi=135.-1e-9,
                                                         jac=.71+1e-10)]*3,[qrecord()]*3))

    def test_33_no_tradeoff_even_when_other_quality_improves(self):
        self.assertFalse(m.dominates_or_equals([qrecord(lo=50.,jac=.60)]*3,[qrecord()]*3))


class ConservativeOptimizationTests(unittest.TestCase):
    def test_34_right_triangle_deterministic(self):
        self.assertEqual(m.optimize_facet(TRI),m.optimize_facet(TRI))

    def test_35_triangle_metrics_never_regress(self):
        result=m.optimize_facet(TRI)
        self.assertTrue(m.dominates_or_equals(result['optimized'],result['baseline']))

    def test_36_equilateral_never_regresses(self):
        r=m.optimize_facet(EQUILATERAL)
        self.assertTrue(m.dominates_or_equals(r['optimized'],r['baseline']))

    def test_37_center_is_inside_triangle(self):
        r=m.optimize_facet(TRI)
        self.assertTrue(0<r['optimized_center'][0] and 0<r['optimized_center'][1]
                        and math.fsum(r['optimized_center'][:2])<1)

    def test_38_original_source_area_unchanged(self):
        r=m.optimize_facet(TRI)
        self.assertAlmostEqual(math.fsum(x['area'] for x in r['optimized']),0.5)

    def test_39_original_corner_angle_ceiling_correct(self):
        r=m.optimize_source([TRI])
        self.assertAlmostEqual(r['original_corner_angle_upper_bound_deg'],45.)
        self.assertLessEqual(r['optimized_quality']['min_angle_deg'],45.+1e-7)

    def test_40_source_corner_scaled_jac_ceiling_correct(self):
        r=m.optimize_source([TRI])
        self.assertAlmostEqual(r['original_corner_jacobian_upper_bound'],math.sqrt(.5))

    def test_41_empty_model_rejected(self):
        with self.assertRaises(ValueError):m.optimize_source([])

    def test_42_invalid_source_triangle_rejected(self):
        with self.assertRaises(ValueError):m.optimize_source([TRI[:2]])

    def test_43_degenerate_source_rejected(self):
        with self.assertRaises(ValueError):m.optimize_source([((0.,0.,0.),)*3])

    def test_44_sample_two_facets_produces_six_quads(self):
        r=m.optimize_source([TRI,EQUILATERAL])
        self.assertEqual(r['optimized_quality']['quads'],6)

    def test_45_reference_count_threshold_validity(self):
        r=m.optimize_source([TRI])
        self.assertLessEqual(r['optimized_quality']['count_min_angle_below_30_deg'],
                             r['baseline_quality']['count_min_angle_below_30_deg'])

    def test_46_facet_center_displacement_is_finite(self):
        r=m.optimize_source([TRI])
        self.assertTrue(0 <= r['max_center_displacement_over_source_edge'] < 1)

    def test_47_source_sine_upper_bound_when_obtuse(self):
        skinny=((0.,0.,0.),(1.,0.,0.),(-.95,.01,0.))
        r=m.optimize_source([skinny])
        self.assertLessEqual(r['optimized_quality']['min_scaled_jacobian'],
                             r['original_corner_jacobian_upper_bound']+1e-7)


class GeometryAndEmissionGuards(unittest.TestCase):
    def test_48_missing_centroid_tag_rejected(self):
        with patch.object(m,'EXPECTED_QUAD_VERTICES',5),patch.object(m,'EXPECTED_SOURCE_FACETS',1):
            r=m.optimize_source([TRI])
            vertices=list(TRI)+[(.5,.5,0.),(1/3,1/3,0.)]
            tags=[('vertex',i) for i in range(5)]
            with self.assertRaises(ValueError):m.updated_geometry_from_f29(vertices,tags,[TRI],r)

    def test_49_duplicate_topological_tag_rejected(self):
        with patch.object(m,'EXPECTED_QUAD_VERTICES',5),patch.object(m,'EXPECTED_SOURCE_FACETS',1):
            r=m.optimize_source([TRI])
            vertices=list(TRI)+[(.5,.5,0.),(1/3,1/3,0.)]
            tags=[('vertex',1)]*5
            with self.assertRaises(ValueError):m.updated_geometry_from_f29(vertices,tags,[TRI],r)

    def test_50_private_writer_rejects_bad_F29_digest(self):
        with self.assertRaises(ValueError):m.emit_private_f30_obj(synthetic_writer(),[(0.,0.,0.)]*4,[1])

    def test_51_private_writer_rejects_duplicate_changed_vertex(self):
        data=synthetic_writer()
        with patch.object(m,'F29_QUAD_SHA256',hashlib.sha256(data).hexdigest()),\
             patch.object(m,'F29_QUAD_BYTES',len(data)),\
             patch.object(m,'EXPECTED_QUAD_VERTICES',4),\
             patch.object(m,'EXPECTED_QUADS',1):
            with self.assertRaises(ValueError):m.emit_private_f30_obj(data,[(0.,0.,0.)]*4,[1,1])

    def test_52_private_writer_safely_emits_quad_not_tri(self):
        data=synthetic_writer()
        with patch.object(m,'F29_QUAD_SHA256',hashlib.sha256(data).hexdigest()),\
             patch.object(m,'F29_QUAD_BYTES',len(data)),\
             patch.object(m,'EXPECTED_QUAD_VERTICES',4),\
             patch.object(m,'EXPECTED_QUADS',1):
            output=m.emit_private_f30_obj(data,[(0.,0.,0.),(.8,0.,0.),(1.,1.,0.),(0.,1.,0.)],[1])
            self.assertIn(b'NOT native APMesh QUAD output',output)
            self.assertIn(b'f 1 2 3 4',output)
            self.assertIn(b'v 0.8 0 0',output)

    def test_53_private_writer_rejects_nonfinite(self):
        data=synthetic_writer()
        with patch.object(m,'F29_QUAD_SHA256',hashlib.sha256(data).hexdigest()),\
             patch.object(m,'F29_QUAD_BYTES',len(data)),\
             patch.object(m,'EXPECTED_QUAD_VERTICES',4),\
             patch.object(m,'EXPECTED_QUADS',1):
            with self.assertRaises(ValueError):m.emit_private_f30_obj(data,[(math.nan,0.,0.)]*4,[1])

    def test_54_private_writer_rejects_invalid_vertex_index(self):
        data=synthetic_writer()
        with patch.object(m,'F29_QUAD_SHA256',hashlib.sha256(data).hexdigest()),\
             patch.object(m,'F29_QUAD_BYTES',len(data)),\
             patch.object(m,'EXPECTED_QUAD_VERTICES',4),\
             patch.object(m,'EXPECTED_QUADS',1):
            with self.assertRaises(ValueError):m.emit_private_f30_obj(data,[(0.,0.,0.)]*4,[4])

    def test_55_no_overwrite_private_output(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            (p/'private').mkdir()
            with self.assertRaises(ValueError):m.replay_private(p/'src.zip',p/'x.bp',p/'r1',p/'r2',
                    p/'tri.obj',p/'quad.obj',p/'private',p/'receipt.json')

    def test_56_no_overwrite_existing_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            (p/'receipt.json').write_text('protected')
            with self.assertRaises(ValueError):m.replay_private(p/'src.zip',p/'x.bp',p/'r1',p/'r2',
                    p/'tri.obj',p/'quad.obj',p/'private',p/'receipt.json')

    def test_57_nonexisting_original_F29_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            with self.assertRaises(FileNotFoundError):m.replay_private(p/'src.zip',p/'x.bp',p/'r1',p/'r2',
                    p/'tri.obj',p/'quad.obj',p/'private',p/'receipt.json')

    def test_58_constant_source_hash_digest_is_pinned(self):
        self.assertEqual(m.F29_QUAD_SHA256,
                         'e2687802ec3314178a973282a33ffd86d71ee8aaa87eed3d4976b266000cf548')

    def test_59_source_scripts_remain_distinct_from_native_quad(self):
        self.assertIn('NOT a',m.__doc__)

    def test_60_minimum_barycentric_guard_is_positive(self):
        self.assertEqual(m.MIN_BARYCENTRIC_WEIGHT,.05)


if __name__=='__main__':
    unittest.main()
