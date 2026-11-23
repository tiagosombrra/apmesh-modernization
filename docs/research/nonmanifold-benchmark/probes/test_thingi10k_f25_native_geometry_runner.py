#!/usr/bin/env python3
"""Fail-closed tests of the F25 original-engine C++ execution boundary.

These tests do not pretend to execute the production C++ reader or mesher.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import thingi10k_f25_native_geometry_runner as f25


class F25RunnerContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    @staticmethod
    def sample(**replace):
        data = {'schema': 'apmesh-s40-f25-native-geometry-v1',
                'result': 'PASS', 'patches': 2, 'curves': 7, 'boundary': 6,
                'shared': 1, 'nonmanifold': 0, 'sides': 8,
                'load_ms': 1.2, 'verify_ms': 0.2, 'peak_rss_kib': 7000}
        data.update(replace)
        return json.dumps(data)

    def test_01_single_patch_is_four_boundaries(self):
        self.assertEqual(f25.synthetic(self.root / 'a.bp', 1), (1, 4, 4, 0))

    def test_02_two_patches_have_shared_curve(self):
        self.assertEqual(f25.synthetic(self.root / 'b.bp', 2), (2, 7, 6, 1))

    def test_03_unsupported_synthetic_case_rejected(self):
        with self.assertRaises(ValueError):
            f25.synthetic(self.root / 'c.bp', 3)

    def test_04_synthetic_outputs_exact_records(self):
        path = self.root / 's.bp'
        f25.synthetic(path, 2)
        lines = path.read_text().splitlines()
        self.assertEqual(sum(s.startswith('v ') for s in lines), 32)
        self.assertEqual(sum(s.startswith('p ') for s in lines), 2)

    def test_05_synthetic_shared_side_is_exact(self):
        path = self.root / 's.bp'
        f25.synthetic(path, 2)
        rows = [line for line in path.read_text().splitlines() if line.startswith('v ')]
        self.assertEqual([rows[i] for i in (3, 7, 11, 15)],
                         [rows[i] for i in (16, 20, 24, 28)])

    def test_06_no_full_checkout_no_native_admission(self):
        with self.assertRaisesRegex(ValueError, 'checkout is unavailable'):
            f25.verify_checkout(self.root)

    def test_07_checkout_partial_source_rejected(self):
        for path in f25.ROOT_FILES:
            file = self.root / path
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('// placeholder\n')
        with self.assertRaisesRegex(ValueError, 'source drift'):
            f25.verify_checkout(self.root)

    def test_08_missing_private_file_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Missing or wrong-sized'):
            f25.verify_real_bp(self.root / 'missing.bp')

    def test_09_wrong_size_private_file_rejected(self):
        path = self.root / 'fake.bp'
        path.write_text('v 0 0 0\n')
        with self.assertRaisesRegex(ValueError, 'wrong-sized'):
            f25.verify_real_bp(path)

    def test_10_wrong_sha_with_same_size_rejected(self):
        path = self.root / 'fake.bp'
        path.write_bytes(b'x' * f25.REAL_BP_SIZE)
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            f25.verify_real_bp(path)

    def test_11_sha256_matches_python_hashlib(self):
        path = self.root / 'f'
        path.write_bytes(b'F25-checksum-test')
        self.assertEqual(f25.digest(path), hashlib.sha256(b'F25-checksum-test').hexdigest())

    def test_12_gitblob_empty_file_is_canonical(self):
        path = self.root / 'empty'
        path.write_bytes(b'')
        self.assertEqual(f25.git_blob(path), 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')

    def test_13_good_native_result_parse(self):
        report = f25.parse_observation(self.sample() + '\n', (2, 7, 6, 1))
        self.assertEqual(report['curves'], 7)

    def test_14_unexpected_schema_rejected(self):
        with self.assertRaisesRegex(ValueError, 'native proof schema'):
            f25.parse_observation(self.sample(schema='synthetic') + '\n', (2, 7, 6, 1))

    def test_15_nonpass_rejected(self):
        with self.assertRaisesRegex(ValueError, 'native proof schema'):
            f25.parse_observation(self.sample(result='FAIL'), (2, 7, 6, 1))

    def test_16_bad_json_rejected(self):
        with self.assertRaises(json.JSONDecodeError):
            f25.parse_observation('{bad}', (2, 7, 6, 1))

    def test_17_multiple_stdout_lines_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unexpected output'):
            f25.parse_observation(self.sample() + '\nnot-a-native-gate\n', (2, 7, 6, 1))

    def test_18_missing_rss_rejected(self):
        with self.assertRaisesRegex(ValueError, 'RSS observation'):
            f25.parse_observation(self.sample(peak_rss_kib=None), (2, 7, 6, 1))

    def test_19_nonfinite_time_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Infinity|nonfinite native timing'):
            f25.parse_observation(self.sample(load_ms=float('inf')), (2, 7, 6, 1))

    def test_20_wrong_curve_count_rejected(self):
        with self.assertRaisesRegex(ValueError, 'counts do not match'):
            f25.parse_observation(self.sample(curves=8), (2, 7, 6, 1))

    def test_21_nonmanifold_curve_rejected(self):
        with self.assertRaisesRegex(ValueError, 'counts do not match'):
            f25.parse_observation(self.sample(nonmanifold=1), (2, 7, 6, 1))

    def test_22_incorrect_observer_sides_rejected(self):
        with self.assertRaisesRegex(ValueError, 'counts do not match'):
            f25.parse_observation(self.sample(sides=7), (2, 7, 6, 1))

    def test_23_invalid_count_type_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Invalid native curve counts'):
            f25.parse_observation(self.sample(patches=True), (2, 7, 6, 1))

    def test_24_subprocess_failed_exit_rejected(self):
        with self.assertRaisesRegex(ValueError, 'no native result admitted'):
            f25.run(['python', '-c', 'raise SystemExit(3)'], timeout=4, hide=True)

    def test_25_subprocess_success_is_not_native_admission(self):
        result, sec = f25.run(['python', '-c', 'print("not native")'], timeout=4, hide=True)
        self.assertEqual(result.returncode, 0)
        with self.assertRaisesRegex(ValueError, 'native proof schema|Invalid|Expecting'):
            f25.parse_observation(result.stdout, (2, 7, 6, 1))

    def test_26_real_bp_identity_cannot_be_omitted(self):
        self.assertEqual(len(f25.REAL_BP_SHA256), 64)
        self.assertEqual(f25.MODEL_COUNTS, (876, 1752, 0, 1752))
        self.assertEqual(4 * f25.MODEL_COUNTS[0], 2 * f25.MODEL_COUNTS[3])

    def test_27_report_no_overwrite(self):
        out = self.root / 'receipt.json'
        out.write_text('existing')
        with mock.patch('sys.argv', ['runner', '--root', str(self.root), '--receipt', str(out)]):
            with self.assertRaisesRegex(ValueError, 'refusing overwrite'):
                f25.main()

    def test_28_duplicate_native_evidence_field_rejected(self):
        raw = self.sample().replace('"patches": 2', '"patches": 2, "patches": 2')
        with self.assertRaisesRegex(ValueError, 'Duplicated key'):
            f25.parse_observation(raw, (2, 7, 6, 1))

    def test_29_zero_rss_rejected(self):
        with self.assertRaisesRegex(ValueError, 'RSS observation'):
            f25.parse_observation(self.sample(peak_rss_kib=0), (2, 7, 6, 1))

    def test_30_source_hash_failure_before_build(self):
        with self.assertRaisesRegex(ValueError, 'checkout is unavailable'):
            f25.measure(self.root, self.root / 'nonexistent.cpp', bp=None)


if __name__ == '__main__':
    unittest.main()
