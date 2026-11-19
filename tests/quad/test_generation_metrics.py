"""Analytic reporting controls and original-reference scope protection."""
import csv
import copy
import hashlib
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/"tools"))
import quad_generation_metrics as metrics
import quad_diagonal_curvature as diagonals


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

    def make_history(self, directory):
        archive = self.make_archive(directory)
        with (archive/'manifest.csv').open() as handle:
            initial = next(csv.DictReader(handle))
        rows = [initial]
        for step, epoch, retry, accepted in ((1, 1, 0, '1'), (2, 2, 0, '0'), (3, 4, 1, '0')):
            row = dict(initial, step=step, epoch=epoch, retry=retry, domain_generation=1,
                       reference_tri_accepted=accepted, reason='accepted' if accepted == '1' else 'global_error_increased')
            if step > 1:
                uv = [(0, 0), (1, 0), (1, 1), (0, 1), (0.5 if step == 2 else 0.4, 0.5)]
                lines = ['v '+' '.join(map(str, metrics.golden(*p)[0])) for p in uv]
                lines += ['vt '+' '.join(map(str, p)) for p in uv]
                lines += ['f 1/1 2/2 5/5', 'f 2/2 3/3 5/5', 'f 3/3 4/4 5/5', 'f 4/4 1/1 5/5']
                name = f'rejected_{step}.obj'
                (archive/name).write_text('\n'.join(lines)+'\n')
                row.update(tri_obj=name, quad_tri_obj=name)
            rows.append(row)
        self.write_manifest(archive, rows)
        native = directory/'fixture_n.process__metrics_rank_-1.csv'
        with native.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, ['step', 'retry_attempt', 'nodes', 'elements', 'error_global_surface_curvature'])
            writer.writeheader()
            for step, retry, nodes, elements, error in ((0, 0, 4, 2, 0.125), (1, 0, 4, 2, 0.1), (2, 0, 5, 4, 0.25), (3, 1, 5, 4, 0.2)):
                writer.writerow(dict(step=step, retry_attempt=retry, nodes=nodes, elements=elements, error_global_surface_curvature=error))
        return archive, rows, native

    def write_manifest(self, archive, rows):
        with (archive/'manifest.csv').open('w', newline='') as handle:
            writer = csv.DictWriter(handle, list(rows[0]))
            writer.writeheader();writer.writerows(rows)

    def test_rejected_attempt_never_becomes_the_comparison_base(self):
        with tempfile.TemporaryDirectory() as temp:
            archive, _, _ = self.make_history(Path(temp))
            report = metrics.collect_archive(archive, 4)
            events = report['history']['events']
            self.assertEqual([e['source_outcome'] for e in events], ['initial', 'accepted', 'rejected', 'rejected'])
            self.assertEqual([e['retained_reference_accepted']['epoch'] for e in events], [0, 1, 1, 1])
            self.assertEqual(events[-1]['identity'], dict(step=3, epoch=4, retry=1, domain_generation=1))
            for event in events[2:]:
                self.assertEqual(event['previous_reference_accepted']['epoch'], 1)
                for observation in event['observations'].values():
                    delta = observation['change_from_previous_reference_accepted']
                    self.assertEqual(delta['nodes_delta'], 1)
                    self.assertEqual(delta['elements_delta'], 2)
                    self.assertEqual(delta['node_ratio'], 1.25)
            self.assertEqual([e['tri_reference_adaptive_error'] for e in events], [0.125, 0.1, 0.25, 0.2])
            self.assertTrue(all(e['mixed_adaptive_error'] is None and e['accepted_mixed_adaptive_epochs'] == 0 for e in events))
            self.assertEqual(report['history']['last_reference_accepted']['epoch'], 1)

    def test_missing_reference_metrics_stays_unavailable(self):
        with tempfile.TemporaryDirectory() as temp:
            archive, _, native = self.make_history(Path(temp))
            native.unlink()
            report = metrics.collect_archive(archive, 4)
            self.assertIsNone(report['reference_metrics_source'])
            self.assertTrue(all(e['tri_reference_adaptive_error'] is None for e in report['history']['events']))

    def test_rejected_reference_counts_and_nonfinite_error_reject(self):
        for column, value in (('nodes', '99'), ('error_global_surface_curvature', 'nan')):
            with tempfile.TemporaryDirectory() as temp:
                archive, _, native = self.make_history(Path(temp))
                with native.open() as handle:
                    rows = list(csv.DictReader(handle))
                rows[2][column] = value
                with native.open('w', newline='') as handle:
                    writer = csv.DictWriter(handle, list(rows[0]))
                    writer.writeheader();writer.writerows(rows)
                with self.assertRaises(ValueError):
                    metrics.collect_archive(archive, 4)

    def test_forged_history_order_outcome_and_duplicate_scope_reject(self):
        for fault in ('missing_initial', 'epoch_order', 'outcome', 'flag', 'retry', 'duplicate_scope'):
            with tempfile.TemporaryDirectory() as temp:
                archive, rows, _ = self.make_history(Path(temp))
                if fault == 'missing_initial':
                    rows.pop(0)
                elif fault == 'epoch_order':
                    rows[3]['epoch'] = 1
                elif fault == 'outcome':
                    rows[2]['reason'] = 'accepted'
                elif fault == 'flag':
                    rows[2]['reference_tri_accepted'] = '2'
                elif fault == 'retry':
                    rows[3]['retry'] = -1
                else:
                    rows.append(dict(rows[2], reference_tri_accepted='1', reason='accepted'))
                self.write_manifest(archive, rows)
                with self.assertRaises(ValueError):
                    metrics.collect_archive(archive, 4)

    def test_foreign_or_missing_observation_rejects_binding(self):
        with tempfile.TemporaryDirectory() as temp:
            archive, _, _ = self.make_history(Path(temp))
            measured = metrics.collect_archive(archive, 4)
            with (archive/'manifest.csv').open() as handle:
                rows = list(csv.DictReader(handle))
            for fault in ('missing', 'identity', 'scheme', 'file'):
                stages = copy.deepcopy(measured['stages'])
                if fault == 'missing':
                    stages.pop()
                elif fault == 'identity':
                    stages[-1]['epoch'] = 99
                elif fault == 'scheme':
                    stages[-1]['scheme'] = 'TRI'
                else:
                    stages[-1]['file'] = 'foreign.obj'
                with self.assertRaises(ValueError):
                    metrics.bind_history(rows, stages)

    def test_history_export_binds_hashes_without_mutating_archived_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            archive, _, _ = self.make_history(directory)
            before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.rglob('*') if p.is_file()}
            report = metrics.collect_archive(archive, 4)
            output = metrics.write_report(report, directory/'report')
            self.assertTrue(all(hashlib.sha256(p.read_bytes()).hexdigest() == digest for p, digest in before.items()))
            with (output/'history.csv').open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 8)
            self.assertEqual(rows[-1]['retained_reference_accepted_epoch'], '1')
            self.assertEqual(rows[-1]['nodes_delta'], '1')
            self.assertEqual(rows[-1]['sha256'], before[archive/rows[-1]['file']])
            self.assertIn('a rejected stage never becomes', (output/'results.md').read_text())


class DiagonalCurvatureTests(unittest.TestCase):
    def graph_controls(self, a, b, c):
        return tuple(tuple((i/3, j/3, a*i*(i-1)/6+b*j*(j-1)/6+c*i*j/9) for j in range(4)) for i in range(4))

    def grid(self, curved=False):
        xyz = [(x, y, 0.2*(x*x+x*y+2*y*y) if curved else 0) for y in (0, 0.6, 1) for x in (0, 0.3, 1)]
        faces = [(0, 1, 4, 3), (1, 2, 5, 4), (3, 4, 7, 6), (4, 5, 8, 7)]
        return xyz, faces

    def test_analytical_gaussian_plane_paraboloid_and_saddle(self):
        for a, b, c in ((0, 0, 0), (0.5, 0.5, 0), (0.5, -0.5, 0), (0, 0, 1)):
            for u, v in ((0, 0), (0.2, 0.7), (1, 1)):
                expected = (4*a*b-c*c)/(1+(2*a*u+c*v)**2+(2*b*v+c*u)**2)**2
                self.assertAlmostEqual(diagonals.source_gaussian(u, v, self.graph_controls(a, b, c)), expected, places=12)

    def test_analytical_sphere_and_singular_surface(self):
        for radius in (1, 3):
            u, v = 0.4, 0.6
            su, cu, sv, cv = math.sin(u), math.cos(u), math.sin(v), math.cos(v)
            du = (-radius*su*cv, radius*cu*cv, 0)
            dv = (-radius*cu*sv, -radius*su*sv, radius*cv)
            duu = (-radius*cu*cv, -radius*su*cv, 0)
            duv = (radius*su*sv, -radius*cu*sv, 0)
            dvv = (-radius*cu*cv, -radius*su*cv, -radius*sv)
            self.assertAlmostEqual(diagonals.gaussian_from_derivatives(du, dv, duu, duv, dvv), 1/radius**2, places=13)
        with self.assertRaises(ValueError):
            diagonals.gaussian_from_derivatives((0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))

    def test_planar_interior_and_boundary_are_distinct(self):
        xyz, faces = self.grid()
        for diagonal in ('02', '13'):
            result = diagonals.independent_metric(xyz, faces, diagonal)
            self.assertFalse(result[4]['boundary'])
            self.assertAlmostEqual(result[4]['density'], 0, places=12)
            self.assertEqual(sum(n['boundary'] for n in result), 8)
            self.assertAlmostEqual(sum(n['defect'] for n in result), 2*math.pi, places=12)
            self.assertGreater(result[0]['density'], 0)

    def test_quad_rotation_selects_the_other_diagonal(self):
        xyz, faces = self.grid(curved=True)
        rotated = [f[1:]+f[:1] for f in faces]
        expected = diagonals.independent_metric(xyz, faces, '13')
        self.assertEqual(diagonals.independent_metric(xyz, rotated, '02'), expected)
        first = diagonals.independent_metric(xyz, faces, '02')
        self.assertGreater(abs(first[4]['density']-expected[4]['density']), 1e-6)

    def test_pure_tri_is_insensitive_and_density_scales_as_inverse_area(self):
        xyz, quads = self.grid(curved=True)
        faces = [t for a, b, c, d in quads for t in ((a, b, c), (a, c, d))]
        first = diagonals.independent_metric(xyz, faces, '02')
        self.assertEqual(first, diagonals.independent_metric(xyz, faces, '13'))
        scaled = diagonals.independent_metric([tuple(7*x for x in p) for p in xyz], faces, '02')
        for a, b in zip(first, scaled):
            self.assertAlmostEqual(a['density']/49, b['density'], places=12)

    def test_malformed_diagonal_geometry_rejects(self):
        xyz, faces = self.grid()
        for broken, diagonal in (([(0, 1, 1)], '02'), ([(0, 1, 2)], '02'), (faces, 'other'),
                                 (faces+[(0, 1, 4)], '02'), ([(0, 1, 99)], '13')):
            with self.assertRaises(ValueError):
                diagonals.independent_metric(xyz, broken, diagonal)


if __name__ == '__main__':
    unittest.main()
