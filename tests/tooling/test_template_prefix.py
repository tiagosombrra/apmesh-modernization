"""Reject missing topology, unsafe coverage claims and ambiguous source preparation."""
from pathlib import Path
import copy
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
sys.path.insert(0, str(ROOT / 'tools'))
from template_prefix_case import (check, compare, parse_output, require_contract, run_cases,
                                  check_complete, parse_complete_output, run_complete_cases,
                                  COMPLETE_PROGRESS)
from prepare_template_prefix import prepare, transform

SAMPLES = json.loads((ROOT / 'tests/template_prefix/data/observations.json').read_text())
CURRENT = json.loads((ROOT / 'tests/template_prefix/data/current_contracts.json').read_text(encoding='utf-8'))
COMPLETED = json.loads((ROOT / 'tests/template_prefix/data/completed_observations.json').read_text(encoding='utf-8'))


class CompleteCallerTests(unittest.TestCase):
    def sample(self):
        return copy.deepcopy(COMPLETED['samples'][0])

    def reject(self, change):
        row = self.sample()
        change(row['result'])
        with self.assertRaises((AssertionError, KeyError)):
            check_complete(row['prefix'], row['result'], row['context'])

    def test_captured_coarse_and_fine_meshes(self):
        for row in COMPLETED['samples']:
            self.assertIn('ownership transfer', check_complete(row['prefix'], row['result'], row['context']))

    def test_failed_native_return(self):
        self.reject(lambda r: r.update(success=0))

    def test_unretired_source_owner(self):
        self.reject(lambda r: r.update(tree_owners=[1, 0, 0]))

    def test_missing_transfer(self):
        self.reject(lambda r: r['transferred'].__setitem__(0, r['transferred'][0] - 1))

    def test_duplicate_vertex_identity_number(self):
        self.reject(lambda r: r['vertices'].append(r['vertices'][0][:]))

    def test_foreign_face_endpoint(self):
        self.reject(lambda r: r['faces'][0].__setitem__(1, -100))

    def test_missing_final_face(self):
        self.reject(lambda r: r['faces'].pop())

    def test_inverted_final_face(self):
        def invert(r):
            face = r['faces'][0]
            face[1], face[2] = face[2], face[1]
        self.reject(invert)

    def test_foreign_edge_endpoint(self):
        self.reject(lambda r: r['edges'][0].__setitem__(1, -100))

    def test_inconsistent_smoothed_quality(self):
        self.reject(lambda r: r['quality'].__setitem__(3, 0.25))

    def test_remaining_front(self):
        self.reject(lambda r: r.update(queues=[1, 0]))

    def output(self, row):
        return ('\n'.join(COMPLETE_PROGRESS) + '\n' + json.dumps({'complete_result': row['result']})
                + '\n' + json.dumps(row['prefix']) + '\n')

    def test_exact_complete_progress(self):
        row = self.sample()
        self.assertEqual(parse_complete_output(self.output(row)), (row['prefix'], row['result']))

    def test_unknown_diagnostic(self):
        with self.assertRaises(ValueError):
            parse_complete_output('unknown diagnostic\n' + self.output(self.sample()))

    def test_missing_or_duplicate_completion(self):
        row = self.sample()
        output = self.output(row)
        record = json.dumps({'complete_result': row['result']}) + '\n'
        for text in (output.replace(record, ''), record + output):
            with self.assertRaises(ValueError):
                parse_complete_output(text)

    def test_stop_before_unobserved_after_failed_completion(self):
        from unittest.mock import patch
        from subprocess import CompletedProcess
        row = self.sample()
        row['result']['success'] = 0
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            binary = folder / 'binary'
            binary.write_bytes(b'controller-only fixture, never executed')
            output = folder / 'captures'
            result = CompletedProcess([], 0, self.output(row).encode('utf-8'), b'')
            with patch('template_prefix_case.subprocess.run', return_value=result) as launch:
                with self.assertRaises(AssertionError):
                    run_complete_cases(binary, binary, output)
            self.assertEqual(launch.call_count, 1)
            report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'], 'failed')
            self.assertEqual(len(report['cases']), 1)
            case = report['cases'][0]
            self.assertEqual((output / case['stdout']['path']).read_bytes(), result.stdout)
            self.assertEqual((output / case['stderr']['path']).read_bytes(), b'')

    def test_timeout_preserves_partial_streams_and_stops(self):
        from unittest.mock import patch
        from subprocess import TimeoutExpired
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            binary = folder / 'binary'
            binary.write_bytes(b'controller-only fixture, never executed')
            output = folder / 'captures'
            failure = TimeoutExpired([], 30, output=b'partial\r\n', stderr=b'native stderr\n')
            with patch('template_prefix_case.subprocess.run', side_effect=failure) as launch:
                with self.assertRaises(TimeoutExpired):
                    run_complete_cases(binary, binary, output)
            self.assertEqual(launch.call_count, 1)
            report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'], 'failed')
            case = report['cases'][0]
            self.assertEqual(case['timeout_seconds'], 30)
            self.assertEqual((output / case['stdout']['path']).read_bytes(), failure.stdout)
            self.assertEqual((output / case['stderr']['path']).read_bytes(), failure.stderr)


class PrefixObservationTests(unittest.TestCase):
    def test_current_coarse_seeded_contracts_are_nonempty(self):
        for sample in CURRENT['coarse_seeded'].values():
            self.assertEqual(require_contract(sample, sample['context']), 'completed nonempty native prefix')
            self.assertEqual(sample['templates'], [7, 10, 4, 0.125])

    def test_historical_refusal_is_readable_but_not_current_qualification(self):
        sample = SAMPLES['refusal']
        self.assertIn('not qualified', check(sample, sample['context']))
        with self.assertRaisesRegex(ValueError, 'Required native prefix contract not satisfied'):
            require_contract(sample, sample['context'])

    def test_required_guard_and_invalid_input_keep_distinct_contracts(self):
        guard = SAMPLES['guard_only']
        self.assertEqual(require_contract(guard, guard['context']), 'completed guard-only prefix; no template coverage')
        invalid = SAMPLES['input_control']
        self.assertEqual(require_contract(invalid, invalid['context']), 'actual input preflight refusal')

    def test_runner_stops_before_unobserved_call_after_required_refusal(self):
        from unittest.mock import patch
        from subprocess import CompletedProcess
        samples = [CURRENT['guard_pair']['observed'], CURRENT['guard_pair']['unobserved'], SAMPLES['refusal']]
        def native_result(arguments, **kwargs):
            sample = samples.pop(0)
            prefix = 'gerou a quadtree\nrefinou a quadtree\n'
            if sample['status'] == 'prefix_completed':
                prefix += 'gerou malha por templates\n'
            return CompletedProcess(arguments, 0, (prefix + json.dumps(sample)).encode(), b'')
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            executable = folder / 'binary'
            executable.write_bytes(b'controller-only fixture, never executed')
            output = folder / 'captures'
            with patch('template_prefix_case.subprocess.run', side_effect=native_result) as launch:
                with self.assertRaisesRegex(ValueError, 'Required native prefix contract not satisfied'):
                    run_cases(executable, executable, output)
            self.assertEqual(launch.call_count, 3)
            report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'], 'failed')
            self.assertEqual(len(report['cases']), 3)
            self.assertEqual(report['cases'][-1]['context'], [2, 0, 1, 0])
            self.assertEqual(report['cases'][-1]['label'], 'observed')
            self.assertTrue((output / report['cases'][-1]['log']).is_file())

    def reject(self, name, field, value):
        j = copy.deepcopy(SAMPLES[name])
        context = tuple(j['context'])
        j[field] = value
        with self.assertRaises((AssertionError, KeyError)):
            check(j, context)

    def test_nonempty_prefix(self):
        j = SAMPLES['positive']
        self.assertEqual(check(j, j['context']), 'completed nonempty native prefix')

    def test_guard_only_is_not_template_coverage(self):
        j = SAMPLES['guard_only']
        self.assertIn('no template coverage', check(j, j['context']))

    def test_refusal_is_not_qualified(self):
        j = SAMPLES['refusal']
        self.assertIn('not qualified', check(j, j['context']))

    def test_actual_input_control(self):
        j = SAMPLES['input_control']
        self.assertEqual(check(j, j['context']), 'actual input preflight refusal')

    def test_missing_reciprocal_neighbor(self):
        j = copy.deepcopy(SAMPLES['positive'])
        row = next(r for r in j['leaves'] if r['neighbors'][0])
        row['neighbors'][0].pop()
        with self.assertRaises(AssertionError):
            check(j, j['context'])

    def test_foreign_neighbor(self):
        j = copy.deepcopy(SAMPLES['positive'])
        next(r for r in j['leaves'] if r['neighbors'][0])['neighbors'][0][0] = -1
        with self.assertRaises((AssertionError, KeyError)):
            check(j, j['context'])

    def test_missing_partition_cell(self):
        j = copy.deepcopy(SAMPLES['positive'])
        j['leaves'].pop()
        with self.assertRaises((AssertionError, KeyError)):
            check(j, j['context'])

    def test_overlapping_partition(self):
        j = copy.deepcopy(SAMPLES['positive'])
        j['leaves'][1]['box'] = j['leaves'][0]['box'][:]
        with self.assertRaises(AssertionError):
            check(j, j['context'])

    def test_zero_template_claim(self):
        self.reject('positive', 'templates', [0, 0, 0, 0])

    def test_wrong_template_area(self):
        j = SAMPLES['positive']
        self.reject('positive', 'templates', j['templates'][:3] + [0.5])

    def test_id_gap(self):
        self.reject('positive', 'ids', [999, 999, 999])

    def test_missing_teardown(self):
        self.reject('positive', 'teardown', 0)

    def test_expired_curve_report(self):
        self.reject('positive', 'curves_live', 0)

    def test_unchecked_crt(self):
        j = copy.deepcopy(SAMPLES['positive'])
        j['iterator_level'] = 0
        with self.assertRaises(AssertionError):
            check(j, j['context'], profile='crt')

    def test_configuration_drift(self):
        self.reject('positive', 'configuration', [0.85, 1e-8, 4, 1])

    def test_input_refusal_cannot_enter_geometry(self):
        self.reject('input_control', 'geometry_entries', 1)

    def test_unknown_native_diagnostic(self):
        with self.assertRaises(ValueError):
            parse_output('unexpected diagnostic\n' + json.dumps(SAMPLES['positive']))

    def test_exact_legacy_progress(self):
        prefix = 'gerou a quadtree\r\nrefinou a quadtree\r\ngerou malha por templates\r\n'
        self.assertEqual(parse_output(prefix + json.dumps(SAMPLES['positive'])), SAMPLES['positive'])

    def test_differential_drift(self):
        j = copy.deepcopy(SAMPLES['positive'])
        j['views'][0] += 1
        with self.assertRaises(AssertionError):
            compare(SAMPLES['positive'], j)


class PrefixPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = (ROOT / 'src/crab_mesh/aft/quadtree.cpp').read_text()
        cls.cell = (ROOT / 'src/crab_mesh/aft/quadtree_cell.cpp').read_text()

    def test_reversal_and_native_read_inventory(self):
        with tempfile.TemporaryDirectory() as folder:
            metadata = prepare(ROOT, Path(folder))
            self.assertTrue(any(r['chained'] for r in metadata['neighbor_expressions']))
            for name in ('quadtree.cpp', 'quadtree_cell.cpp'):
                restored = (Path(folder) / name).read_text()
                for old, new in reversed(metadata['files'][name]['edits']):
                    self.assertEqual(restored.count(new), 1)
                    restored = restored.replace(new, old)
                self.assertEqual(restored, (ROOT / 'src/crab_mesh/aft' / name).read_text())

    def test_missing_tree_cut(self):
        with self.assertRaises(ValueError):
            transform(self.tree.replace('  root->sortNeighbors();', ''), self.cell)

    def test_duplicate_tree_cut(self):
        with self.assertRaises(ValueError):
            transform(self.tree.replace('  root->sortNeighbors();', '  root->sortNeighbors();\n' * 2), self.cell)

    def test_missing_cell_include(self):
        with self.assertRaises(ValueError):
            transform(self.tree, self.cell.replace('#include <stdexcept>', ''))

    def test_missing_neighbor_inventory(self):
        with self.assertRaises(ValueError):
            transform(self.tree, self.cell.replace('neighbors[', 'other_observers['))


if __name__ == '__main__':
    unittest.main()
