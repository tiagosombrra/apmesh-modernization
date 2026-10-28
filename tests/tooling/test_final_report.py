"""Challenge actual-step identity and scalar preservation in final reports."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from final_report_case import FIELDS, history_rows, validate


def report(steps):
    fields = ', '.join(key + '=1' for key in sorted(FIELDS - {'error'}))
    return ''.join(f'Erro no step_ {step} = 1, {fields}\r\n' for step in steps).encode()


class FinalReportTests(unittest.TestCase):
    def test_acceptance_gap(self):
        self.assertEqual(validate(report([0, 1, 4]), [0, 1, 4])['rows'], 3)

    def test_initial_and_consecutive(self):
        for steps in ([0], [0, 1], [0, 2, 4, 7]):
            self.assertEqual(validate(report(steps), steps)['accepted_steps'], steps)

    def test_original_ordinal_labels_rejected(self):
        with self.assertRaises(ValueError):
            validate(report([0, 1, 2]), [0, 1, 4])

    def test_missing_duplicate_or_extra_row(self):
        for steps in ([], [0, 1], [0, 1, 1], [0, 1, 4, 5]):
            with self.assertRaises(ValueError):
                validate(report(steps), [0, 1, 4])

    def test_missing_duplicate_or_unordered_ledger(self):
        for steps in ([], [1, 4], [0, 1, 1], [0, 4, 1]):
            with self.assertRaises(ValueError):
                validate(report([0, 1, 4]), steps)

    def test_malformed_or_missing_scalar(self):
        for raw in (report([0]).replace(b'quality_min', b'unknown'), b'Erro no step_ invalid\n',
                    report([0]).replace(b' = 1, ', b' = 1, malformed, ')):
            with self.assertRaises(ValueError):
                validate(raw, [0])

    def test_duplicate_scalar(self):
        with self.assertRaises(ValueError):
            validate(report([0]).replace(b'\r\n', b', retry=1\r\n'), [0])

    def test_nonfinite_scalar(self):
        for value in (b'nan', b'inf', b'-inf'):
            with self.assertRaises(ValueError):
                validate(report([0]).replace(b'retry=1', b'retry=' + value), [0])

    def test_only_labels_may_change(self):
        self.assertEqual(validate(report([0, 1, 4]), [0, 1, 4], report([0, 1, 2]))['scalar_fields'], 48)
        with self.assertRaises(ValueError):
            validate(report([0, 1, 4]).replace(b'retry=1', b'retry=2'), [0, 1, 4], report([0, 1, 2]))

    def test_crlf_lf_and_unrelated_output(self):
        raw = b'Other output\r\n' + report([0, 1, 4])
        self.assertEqual(history_rows(raw), history_rows(raw.replace(b'\r\n', b'\n')))
        self.assertEqual(validate(raw, [0, 1, 4])['rows'], 3)
