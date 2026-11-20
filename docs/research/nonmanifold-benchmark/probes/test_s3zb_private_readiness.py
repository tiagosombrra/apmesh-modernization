#!/usr/bin/env python3
"""Readiness receipts are deterministic and cannot substitute for CAD evidence."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import s3zb_check_private_readiness as ready


class PrivateNativePrerequisiteTests(unittest.TestCase):
    def test_missing_source_and_bp_block_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            report=ready.check_readiness(p/'no.step',p/'no.bp',p/'no.json',p/'no.py')
        self.assertEqual(report['status'],'BLOCKED_MISSING_OR_MISMATCHED_INPUT')
        self.assertFalse(report['native_trial_executed'])
        self.assertEqual(report['accepted_new_original_faces'],0)
        self.assertFalse(report['checks']['original_step']['found'])

    def test_wrong_original_and_bp_hash_block_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            for name,contents in [('source.step',b'x'),('parent.bp',b'y')]:
                (p/name).write_bytes(contents)
            result=ready.check_readiness(p/'source.step',p/'parent.bp',p/'missing.json',p/'missing.py')
        self.assertFalse(result['checks']['original_step']['hash_ok'])
        self.assertFalse(result['checks']['s3w_parent_bp']['hash_ok'])

    def test_synthetic_complete_fixture_is_ready_but_not_a_native_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'original.step').write_bytes(b'standalone')
            (root/'parent.bp').write_bytes(b'indexed 3d controls')
            (root/'manifest.json').write_text(json.dumps({
                'source_sha256':sha256(b'standalone').hexdigest(),
                'repaired_bp_sha256':sha256(b'indexed 3d controls').hexdigest(),
                'combined_patches':148,
            }))
            (root/'s3y.py').write_text('# Synthetic test-only placeholder\n')
            with patch.object(ready,'ORIGINAL_STEP_SHA',sha256(b'standalone').hexdigest()), \
                 patch.object(ready,'S3W_PARENT_SHA',sha256(b'indexed 3d controls').hexdigest()):
                out=ready.check_readiness(root/'original.step',root/'parent.bp',
                                          root/'manifest.json',root/'s3y.py')
        self.assertEqual(out['status'],'READY_FOR_ORIGINAL_NATIVE_TRIAL')
        self.assertFalse(out['native_trial_executed'])

    def test_forged_manifest_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'parent.bp').write_bytes(b'correct')
            (root/'source.step').write_bytes(b'correct')
            (root/'manifest.json').write_text(json.dumps({
                'source_sha256':sha256(b'correct').hexdigest(),
                'repaired_bp_sha256':'0'*64,'combined_patches':148}))
            (root/'s3y.py').write_text('# fixture\n')
            with patch.object(ready,'ORIGINAL_STEP_SHA',sha256(b'correct').hexdigest()), \
                 patch.object(ready,'S3W_PARENT_SHA',sha256(b'correct').hexdigest()):
                out=ready.check_readiness(root/'source.step',root/'parent.bp',
                                          root/'manifest.json',root/'s3y.py')
        self.assertEqual(out['status'],'BLOCKED_MISSING_OR_MISMATCHED_INPUT')
        self.assertFalse(out['checks']['s3w_manifest']['manifest_hash_ok'])

    def test_extra_missing_python_module_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            report=ready.check_readiness(p/'missing',p/'missing',p/'missing',p/'missing',
                                         extra_requirements=('module_that_is_not_installed_1b47aa',))
        self.assertFalse(report['python_dependencies']['module_that_is_not_installed_1b47aa'])


if __name__=='__main__':
    unittest.main()
