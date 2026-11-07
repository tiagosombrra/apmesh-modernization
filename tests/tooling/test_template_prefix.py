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
from template_prefix_case import check, compare, parse_output, require_contract, run_cases
from prepare_template_prefix import prepare, transform

SAMPLES = json.loads((ROOT / 'tests/template_prefix/data/observations.json').read_text())
CURRENT = json.loads((ROOT / 'tests/template_prefix/data/current_contracts.json').read_text(encoding='utf-8'))


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
