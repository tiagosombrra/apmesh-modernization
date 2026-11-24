#!/usr/bin/env python3
"""Hermetic negative tests for the F24 source-inspected curve-identity preflight."""
from __future__ import annotations

from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import thingi10k_f24_curve_identity_preflight as gate


def patch_plane(origin_x):
    return [(origin_x + i / 3, j / 3, 0.0) for j in range(4) for i in range(4)]


def sample_two_patches(offset=0.0):
    controls = patch_plane(0) + patch_plane(1 + offset)
    return controls, [tuple(range(16)), tuple(range(16, 32))]


class F24CurvePreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='apmesh-f24-fixture-')
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'fixture.bp'

    def write(self, points=None, faces=None):
        if points is None or faces is None:
            points, faces = sample_two_patches()
        content = ''.join('v ' + ' '.join(map(str, p)) + '\n' for p in points)
        content += ''.join('p ' + ' '.join(map(str, f)) + '\n' for f in faces)
        self.path.write_text(content, encoding='utf-8')
        return self.path

    def test_01_reads_indexed_bicubic_fixture(self):
        controls, faces = gate.read_bp(self.write())
        self.assertEqual((len(controls), len(faces)), (32, 2))

    def test_02_finds_exact_shared_geometry(self):
        p, f = sample_two_patches()
        groups = gate.curve_groups(p, f)
        self.assertEqual(len(groups), 7)
        self.assertEqual(sorted(map(len, groups.values())), [1] * 6 + [2])

    def test_03_boundary_shared_orientation_is_opposite(self):
        p, f = sample_two_patches()
        groups = gate.curve_groups(p, f)
        self.assertTrue(all(g[0][2] == g[1][2][::-1] for g in groups.values() if len(g) == 2))

    def test_04_no_ambiguous_curves_at_default_epsilon(self):
        p, f = sample_two_patches()
        self.assertEqual(gate.near_distinct_curves(list(gate.curve_groups(p, f)), 1e-7), 0)

    def test_05_shifted_sheet_is_near_at_tenth(self):
        p, f = sample_two_patches(.05)
        self.assertGreater(gate.near_distinct_curves(list(gate.curve_groups(p, f)), .1), 0)

    def test_06_shifted_sheet_is_not_near_at_hundredth(self):
        p, f = sample_two_patches(.05)
        self.assertEqual(gate.near_distinct_curves(list(gate.curve_groups(p, f)), .01), 0)

    def test_07_near_points_at_tenth(self):
        self.assertEqual(gate.near_distinct_points([(0, 0, 0), (.05, 0, 0)], .1), 1)

    def test_08_points_distant_at_hundredth(self):
        self.assertEqual(gate.near_distinct_points([(0, 0, 0), (.05, 0, 0)], .01), 0)

    def test_09_point_boundary_epsilon_is_inclusive(self):
        self.assertTrue(gate.within((1, 0, 0), (1.1, 0, 0), .1000000000001))

    def test_10_reversed_curve_is_equivalent(self):
        a = tuple((i, 0, 0) for i in range(4))
        self.assertTrue(gate.curves_approximately_equal(a, a[::-1], 1e-7))

    def test_11_nonmatching_curve_is_not_equivalent(self):
        a = tuple((i, 0, 0) for i in range(4))
        b = tuple((i, .05, 0) for i in range(4))
        self.assertFalse(gate.curves_approximately_equal(a, b, .01))

    def test_12_invalid_zero_epsilon_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Invalid tolerance'):
            gate.near_distinct_points([(0, 0, 0)], 0)

    def test_13_negative_epsilon_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Invalid tolerance'):
            gate.near_distinct_curves([], -1)

    def test_14_invalid_file_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Missing, empty or oversized'):
            gate.read_bp(self.path)

    def test_15_nonfinite_vertex_is_rejected(self):
        f = self.write()
        f.write_text(f.read_text().replace('v 0.0 0.0 0.0', 'v nan 0 0', 1))
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            gate.read_bp(f)

    def test_16_missing_control_index_is_rejected(self):
        f = self.write()
        s = f.read_text().replace('p 0 1 2', 'p 999 1 2', 1)
        f.write_text(s)
        with self.assertRaisesRegex(ValueError, 'missing or future control'):
            gate.read_bp(f)

    def test_17_unknown_record_is_rejected(self):
        self.write()
        with self.path.open('a') as stream:
            stream.write('f 0 1 2\n')
        with self.assertRaisesRegex(ValueError, 'unsupported BP line'):
            gate.read_bp(self.path)

    def test_18_truncated_patch_is_rejected(self):
        self.write()
        self.path.write_text(self.path.read_text().replace('p 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15', 'p 0 1', 1))
        with self.assertRaisesRegex(ValueError, 'patch arity'):
            gate.read_bp(self.path)

    def test_19_identity_gate_rejects_synthetic(self):
        with self.assertRaisesRegex(ValueError, 'do not match F22'):
            gate.read_bp(self.write(), private_identity=True)

    def test_20_closed_model_gate_refuses_open_fixture(self):
        p, f = sample_two_patches()
        with self.assertRaisesRegex(ValueError, 'unpaired'):
            gate.analyze(p[:16], f[:1], require_closed=True)

    def test_21_mathematical_curve_scan_exact_on_fixture(self):
        p, f = sample_two_patches()
        q = gate.linear_curve_lookup_count(p, f)
        self.assertEqual(q['lookup_calls'], 8)
        self.assertEqual(q['curves_assuming_no_false_epsilon_matches'], 7)

    def test_22_find_control_id_comparisons_exact_on_fixture(self):
        p, f = sample_two_patches()
        q = gate.analyze(p, f)
        self.assertEqual(q['indexed_bp_successful_id_comparisons_under_original_find_control'],
                         sum(i + 1 for patch in f for i in patch))

    def test_23_curve_id_is_reuse_invariant_to_reversal(self):
        curve = tuple((x, 0, 0) for x in range(4))
        self.assertEqual(gate.canonical(curve), gate.canonical(curve[::-1]))

    def test_24_missing_full_geometry_execution_stays_explicit(self):
        self.assertFalse('apmesh C++ Geometry' in gate.__doc__ or 'original source-native Geometry' in gate.__doc__)


if __name__ == '__main__':
    unittest.main()
