"""A failed native copy observation must not start the next caller."""

import json
from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
from qualify_curve_copy import qualify


class CurveCopyRunnerTests(unittest.TestCase):
    def test_timeout_preserves_partial_capture_and_stops_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / 'binary'
            executable.write_bytes(b'controller-only fixture, never executed')
            raw = b'partial timeout prefix\r\n'
            with patch('qualify_curve_copy.subprocess.run', side_effect=TimeoutExpired([], 30, output=raw)) as launch:
                report = qualify(executable, executable, root, root / 'result')
            self.assertEqual(launch.call_count, 1)
            self.assertEqual(report['status'], 'failed')
            self.assertEqual(report['completed_cases'], 1)
            self.assertEqual(report['cases'][0]['timeout_seconds'], 30)
            self.assertEqual((root / 'result/asan-copy-0-0.log').read_bytes(), raw)
            self.assertEqual(json.loads((root / 'result/report.json').read_text(encoding='utf-8'))['status'], 'failed')

    def test_first_failure_retains_bytes_and_stops_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / 'binary'
            executable.write_bytes(b'controller-only fixture, never executed')
            raw = b'incomplete native prefix\r\n'
            with patch('qualify_curve_copy.subprocess.run', return_value=CompletedProcess([], 1, raw)) as launch:
                report = qualify(executable, executable, root, root / 'result')
            self.assertEqual(launch.call_count, 1)
            self.assertEqual(report['status'], 'failed')
            self.assertEqual(report['expected_cases'], 30)
            self.assertEqual(report['completed_cases'], 1)
            self.assertEqual((root / 'result/asan-copy-0-0.log').read_bytes(), raw)
            persisted = json.loads((root / 'result/report.json').read_text(encoding='utf-8'))
            self.assertFalse(persisted['cases'][0]['passed'])


if __name__ == '__main__':
    unittest.main()
