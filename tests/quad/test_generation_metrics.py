"""Analytic reporting controls and original-reference scope protection."""
import csv
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/"tools"))
import quad_generation_metrics as metrics


class GenerationMetricsTests(unittest.TestCase):
    def test_ideal_elements_have_separate_unit_scores(self):
        normal = lambda uv: (0, 0, 1)
        xyz = [(0, 0, 0), (1, 0, 0), (0.5, math.sqrt(3)/2, 0)]
        tri = metrics.element_quality(xyz, [x[:2] for x in xyz], (0, 1, 2), normal)
        self.assertAlmostEqual(tri['tri_q'], 1)
        self.assertAlmostEqual(tri['min_angle_xyz'], 60)
        self.assertIsNone(tri['quad_corner_jacobian'])
        xyz = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
        quad = metrics.element_quality(xyz, [x[:2] for x in xyz], (0, 1, 2, 3), normal)
        self.assertAlmostEqual(quad['quad_corner_jacobian'], 1)
        self.assertAlmostEqual(quad['S_uv'], 1)
        self.assertAlmostEqual(quad['edge_ratio_xyz'], 1)
        self.assertIsNone(quad['tri_q'])

    def test_rectangle_jacobian_does_not_hide_aspect_ratio(self):
        xyz = [(0, 0, 0), (10, 0, 0), (10, 1, 0), (0, 1, 0)]
        result = metrics.element_quality(xyz, [x[:2] for x in xyz], (0, 1, 2, 3), lambda uv: (0, 0, 1))
        self.assertAlmostEqual(result['quad_corner_jacobian'], 1)
        self.assertAlmostEqual(result['edge_ratio_xyz'], 10)

    def test_reversed_and_collapsed_elements_reject(self):
        xyz = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        for face in ((0, 2, 1), (0, 1, 1)):
            with self.assertRaises(ValueError):
                metrics.element_quality(xyz, [x[:2] for x in xyz], face, lambda uv: (0, 0, 1))

    def make_archive(self, directory, foreign=False, wrong_count=False):
        archive = directory/'fixture.steps'
        archive.mkdir()
        uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
        lines = ['v '+' '.join(map(str, metrics.golden(*p)[0])) for p in uv]
        lines += ['vt '+' '.join(map(str, p)) for p in uv]
        lines += ['f 1/1 2/2 3/3', 'f 1/1 3/3 4/4']
        (archive/'mesh.obj').write_text('\n'.join(lines)+'\n')
        fields = ['step', 'epoch', 'retry', 'domain_generation', 'reference_tri_accepted', 'reason', 'tri_obj', 'quad_tri_obj']
        with (archive/'manifest.csv').open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fields);writer.writeheader()
            writer.writerow(dict(step=0, epoch=0, retry=-1, domain_generation=0, reference_tri_accepted=1, reason='initial', tri_obj='../outside.obj' if foreign else 'mesh.obj', quad_tri_obj='mesh.obj'))
        with (directory/'fixture_n.process__metrics_rank_-1.csv').open('w', newline='') as handle:
            writer = csv.DictWriter(handle, ['step', 'retry_attempt', 'nodes', 'elements', 'error_global_surface_curvature'])
            writer.writeheader();writer.writerow(dict(step=0, retry_attempt=0, nodes=99 if wrong_count else 4, elements=2, error_global_surface_curvature=0.125))
        return archive

    def test_initial_reference_and_absent_quad_are_explicit(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = self.make_archive(Path(temp))
            report = metrics.collect_archive(archive, grid=4)
            self.assertEqual(len(report['stages']), 2)
            for stage in report['stages']:
                self.assertEqual(stage['tri_reference_adaptive_error'], 0.125)
                self.assertIsNone(stage['mixed_adaptive_error'])
                self.assertEqual(stage['quality']['quad_corner_jacobian']['count'], 0)
                self.assertIsNone(stage['quality']['quad_corner_jacobian']['minimum'])
                self.assertEqual(stage['geometry_error']['sample_count'], 16)

    def test_foreign_archive_and_reference_count_reject(self):
        for fault in ('foreign', 'wrong_count'):
            with tempfile.TemporaryDirectory() as temp:
                archive = self.make_archive(Path(temp), **{fault: True})
                with self.assertRaises(ValueError):
                    metrics.collect_archive(archive, grid=4)


if __name__ == '__main__':
    unittest.main()
