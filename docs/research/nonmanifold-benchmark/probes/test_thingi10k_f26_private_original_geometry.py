#!/usr/bin/env python3
"""Hermetic negative and positive tests of the private-original native-replay gate."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import thingi10k_f26_private_original_geometry as f26


def positive():
    return dict(schema=f26.OBSERVATION_SCHEMA, result='PASS', patches=876,
                curves=1752, boundary=0, shared=1752, nonmanifold=0,
                sides=3504, matched_control_sides=3504,
                reversed_control_sides=1580, parse_ms=3.3,
                load_ms=760.0, verify_ms=5.6, peak_rss_kib=54232)


class F26PrivateNativeGate(unittest.TestCase):
    def test_01_positive_receipt(self):
        self.assertEqual(f26.verify_native_observation(json.dumps(positive()))['curves'], 1752)

    def test_02_real_binary_must_exist(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'Missing original-engine'):
                f26.private_run(Path(d) / 'none', Path(d) / 'no.bp', '0' * 64)

    def test_03_duplicate_json_field_rejected(self):
        raw=json.dumps(positive())[:-1]+',"patches":876}'
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            f26.verify_native_observation(raw)

    def test_04_nan_json_rejected(self):
        row=positive();row['load_ms']=float('nan')
        with self.assertRaises(ValueError):
            f26.verify_native_observation(json.dumps(row))

    def test_05_wrong_schema_rejected(self):
        row=positive();row['schema']='incorrect'
        with self.assertRaisesRegex(ValueError, 'not PASS'):
            f26.verify_native_observation(json.dumps(row))

    def test_06_failure_status_rejected(self):
        row=positive();row['result']='FAIL'
        with self.assertRaisesRegex(ValueError, 'not PASS'):
            f26.verify_native_observation(json.dumps(row))

    def test_07_not_1752_curves_rejected(self):
        row=positive();row['curves']=1751
        with self.assertRaisesRegex(ValueError, 'curves'):
            f26.verify_native_observation(json.dumps(row))

    def test_08_not_3504_matched_control_sides_rejected(self):
        row=positive();row['matched_control_sides']=3503
        with self.assertRaisesRegex(ValueError, 'matched_control_sides'):
            f26.verify_native_observation(json.dumps(row))

    def test_09_boundary_curves_rejected(self):
        row=positive();row['boundary']=4
        with self.assertRaisesRegex(ValueError, 'boundary'):
            f26.verify_native_observation(json.dumps(row))

    def test_10_nonmanifold_rejected(self):
        row=positive();row['nonmanifold']=1
        with self.assertRaisesRegex(ValueError, 'nonmanifold'):
            f26.verify_native_observation(json.dumps(row))

    def test_11_negative_reversal_rejected(self):
        row=positive();row['reversed_control_sides']=-1
        with self.assertRaisesRegex(ValueError, 'orientation'):
            f26.verify_native_observation(json.dumps(row))

    def test_12_excess_reversal_rejected(self):
        row=positive();row['reversed_control_sides']=3505
        with self.assertRaisesRegex(ValueError, 'orientation'):
            f26.verify_native_observation(json.dumps(row))

    def test_13_nonfinite_run_time_rejected(self):
        row=positive();row['verify_ms']=-1
        with self.assertRaisesRegex(ValueError, 'measurement'):
            f26.verify_native_observation(json.dumps(row))

    def test_14_rss_zero_rejected(self):
        row=positive();row['peak_rss_kib']=0
        with self.assertRaisesRegex(ValueError, 'RSS'):
            f26.verify_native_observation(json.dumps(row))

    def test_15_unexpected_multiline_rejected(self):
        with self.assertRaisesRegex(ValueError, 'one bounded'):
            f26.verify_native_observation(json.dumps(positive())+'\n{}')

    def test_16_boolean_count_rejected(self):
        row=positive();row['patches']=True
        with self.assertRaisesRegex(ValueError, 'patches'):
            f26.verify_native_observation(json.dumps(row))

    def test_17_missing_private_input_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, 'Missing or resized'):
                f26.verify_private_bp(Path(d)/'none.bp')

    def test_18_wrong_sha_private_input_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'wrong.bp';path.write_bytes(b'x'*f26.ORIGINAL_BP_BYTES)
            with self.assertRaisesRegex(ValueError, 'digest differs'):
                f26.verify_private_bp(path)

    def test_19_hash_is_known(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'input';path.write_bytes(b'hello')
            self.assertEqual(f26.sha256(path),hashlib.sha256(b'hello').hexdigest())

    def test_20_missing_field_rejected(self):
        row=positive();del row['sides']
        with self.assertRaisesRegex(ValueError, 'sides'):
            f26.verify_native_observation(json.dumps(row))


if __name__ == '__main__':
    unittest.main()
