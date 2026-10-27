"""Challenge accepted-error trace provenance and actual guard outcomes."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stopping_error_case import validate


def trace():
    state = dict(step=0, accepted_step=0, cached_global=0.5, current_local_max=0.6,
                 accepted_global=0.5, accepted_local_max=0.6, history_global=0.5,
                 epsilon=0.1, tolerance=0.1, reason='max_steps_reached')
    rows = [dict(state, event='accepted'), dict(state, event='guard_entry'),
            dict(state, event='attempt_evaluated', step=1),
            dict(state, event='rejected_restored', step=1, cached_global=0.0),
            dict(state, event='rejected_ready', step=1, cached_global=0.0),
            dict(state, event='guard_entry', step=1, cached_global=0.0),
            dict(state, event='attempt_evaluated', step=2),
            dict(state, event='function_end', step=2)]
    return rows


class StoppingErrorTests(unittest.TestCase):
    def test_rejected_scalar_is_not_convergence(self):
        self.assertEqual(validate(trace())['stops'], 0)

    def test_original_attempted_guard_rejected(self):
        rows = trace()
        rows[6:] = [dict(rows[5], event='global_stop'), dict(rows[5], event='function_end', reason='target_error_reached')]
        with self.assertRaises(ValueError):
            validate(rows)

    def test_provenance_controls(self):
        for field, value in (('accepted_global', 0), ('accepted_step', 2), ('history_global', 0), ('accepted_local_max', 0)):
            rows = trace()
            rows[5][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(rows)

    def test_restoration_required(self):
        rows = trace()
        rows[3]['current_local_max'] = 0
        with self.assertRaises(ValueError):
            validate(rows)

    def test_thresholds_and_finite_errors(self):
        for field, value in (('epsilon', 1), ('accepted_global', float('nan'))):
            rows = trace()
            rows[5][field] = value
            with self.assertRaises(ValueError):
                validate(rows)

    def test_accepted_equal_global_has_priority(self):
        rows = trace()[:2]
        for row in rows:
            row.update(cached_global=0.1, accepted_global=0.1, history_global=0.1,
                       current_local_max=0.1, accepted_local_max=0.1)
        rows += [dict(rows[-1], event='global_stop'), dict(rows[-1], event='function_end', reason='target_error_reached')]
        self.assertEqual(validate(rows)['stops'], 1)
        bad = copy.deepcopy(rows)
        bad[2]['event'] = 'local_stop'
        bad[-1]['reason'] = 'local_error_threshold_reached'
        with self.assertRaises(ValueError):
            validate(bad)

    def test_local_equality_and_stop_label(self):
        rows = trace()[:2]
        for row in rows:
            row.update(current_local_max=0.1, accepted_local_max=0.1)
        rows += [dict(rows[-1], event='local_stop'), dict(rows[-1], event='function_end', reason='local_error_threshold_reached')]
        self.assertEqual(validate(rows)['stops'], 1)
        rows[-1]['reason'] = 'max_steps_reached'
        with self.assertRaises(ValueError):
            validate(rows)

    def test_empty_truncated_and_duplicate_completion(self):
        for rows in ([], trace()[:-1], trace() + [trace()[-1]]):
            with self.assertRaises(ValueError):
                validate(rows)
