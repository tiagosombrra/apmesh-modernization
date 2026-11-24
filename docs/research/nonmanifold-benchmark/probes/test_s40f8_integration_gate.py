#!/usr/bin/env python3
"""Regression for fail-closed use of exact F8 certificates in F7 joining."""
import hashlib
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import s40f7_parent_lineage_rebase as join


class GateTests(unittest.TestCase):
    def test_invalid_bytes_rejected_before_join(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            join.require_strict_orientation_certificate(b'invalid')

    def test_all_certificates_positive_allows_join_gate(self):
        fake={'certificates':[{'patch_index':i,'classification':'CERTIFIED_STRICT_POSITIVE'} for i in range(8)]}
        with patch('s40f8_exact_planar_jacobian.audit_f6',return_value=fake):
            self.assertIs(join.require_strict_orientation_certificate(b'mock'),fake)

    def test_one_nonpositive_patch_rejected(self):
        fake={'certificates':[{'patch_index':i,'classification':'EXACT_ZERO_CORNER_STRICT_GATE_FAIL' if i==3 else 'CERTIFIED_STRICT_POSITIVE'} for i in range(8)]}
        with patch('s40f8_exact_planar_jacobian.audit_f6',return_value=fake):
            with self.assertRaisesRegex(ValueError,'patches 3'):
                join.require_strict_orientation_certificate(b'mock')


class PrivateF6JoinBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name=os.environ.get('APMESH_S40F8_PRIVATE_F6_BP')
        if not name:
            raise unittest.SkipTest('Original private F6 BP not mounted')
        cls.raw=Path(name).read_bytes()

    def test_frozen_four_face_island_must_fail_strict_gate(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),join.F6_SHA)
        with self.assertRaisesRegex(ValueError,'patches 0,1,3'):
            join.require_strict_orientation_certificate(self.raw)


if __name__=='__main__':
    unittest.main()
