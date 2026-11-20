#!/usr/bin/env python3
"""Fail-closed private S3.Y replay tests with synthetic fixture bytes only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import s40f4_private_s3y_replay as replay


class PrivateReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='s40f4_test_')
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.step=b'FAKE-STEP-NO-CAD-EXECUTION\n'
        self.bp=b'FAKE-S3W-BP-NO-CAD-EXECUTION\n'
        self.child=b'FAKE-SELECTED-S3Y-BP\n'
        self.step_path=self.base/'original.step'
        self.zip_path=self.base/'s3w.zip'
        self.builder=self.base/'builder.py'
        self.step_path.write_bytes(self.step)
        self.s3w_metadata={
            'repaired_bp_sha256':hashlib.sha256(self.bp).hexdigest(),
            'combined_patches':148,
            'global_declared_control_points':1619,
            'original_step_218_hole_patch_ids_unchanged':True
        }
        self.expected_step_sha=hashlib.sha256(self.step).hexdigest()
        self.expected_child_sha=hashlib.sha256(self.child).hexdigest()
        self.pins=patch.multiple(replay, SOURCE_SHA=self.expected_step_sha,
                                S3W_SHA=hashlib.sha256(self.bp).hexdigest(),
                                S3Y_SHA=self.expected_child_sha)
        self.pins.start()
        self.addCleanup(self.pins.stop)
        self._write_zip()
        self._write_stub_builder()

    def _write_zip(self, bp=None, metadata=None, extras=None):
        if bp is None:bp=self.bp
        if metadata is None:metadata=self.s3w_metadata
        with zipfile.ZipFile(self.zip_path,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('Original-S40-S3W/private_bp/'+replay.S3W_BP,bp)
            z.writestr('Original-S40-S3W/private_bp/'+replay.S3W_MANIFEST,json.dumps(metadata))
            for name,data in (extras or []):
                z.writestr(name,data)

    def _write_stub_builder(self, *, corrupt_child=False, fail=False, native_fail=False):
        child=b'WRONG-CHILD' if corrupt_child else self.child
        self.builder.write_text('''from pathlib import Path
import argparse,json,hashlib,sys
p=argparse.ArgumentParser()
for arg in ('source-step','baseline-bp','baseline-manifest','output-dir'):
    p.add_argument('--'+arg,required=True)
p.add_argument('--faces',nargs='+')
p.add_argument('--interior-grid')
p.add_argument('--boundary-grid')
a=p.parse_args()
if {fail}:
    sys.exit(3)
out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
child={child!r}
(out/'s40_three_curved_planar.CANDIDATE.bp').write_bytes(child)
(out/'candidate_manifest.json').write_text(json.dumps({{'candidate_bp_sha256':hashlib.sha256(child).hexdigest(),
    'candidate_patch_count':156,'candidate_control_count':1665}}))
(out/'native_audit.json').write_text(json.dumps({{'status':{status!r},'native_boundary_OUT':{out}}}))
'''.format(fail=fail,child=child,status='BLOCKED' if native_fail else 'PASS',out=1 if native_fail else 0))

    def _run(self):
        return replay.replay_selected_s3y(self.step_path,self.zip_path,
                                           self.builder,self.base/'output')

    def test_frozen_parent_identification_in_zip_suffix(self):
        bp,m=replay.read_verified_s3w_bundle(self.zip_path)
        self.assertEqual(bp,self.bp)
        self.assertEqual(json.loads(m),self.s3w_metadata)

    def test_replay_preserves_pinned_child_and_writes_only_privately(self):
        receipt=self._run()
        self.assertEqual(receipt['selected_child_sha256'],self.expected_child_sha)
        self.assertTrue(receipt['original_native_replay_executed'])
        self.assertEqual((self.base/'output'/'s40_selected_s3y.partial.bp').read_bytes(),self.child)
        metadata=json.loads((self.base/'output'/'s40_selected_s3y_manifest.json').read_text())
        self.assertEqual(metadata['selected_bp_sha256'],self.expected_child_sha)
        self.assertFalse(receipt['apmesh_cpp_tri_quad_executed'])

    def test_wrong_original_step_fails_before_running_builder(self):
        self.step_path.write_bytes(b'WRONG-ORIGINAL')
        with self.assertRaisesRegex(ValueError,'Original industrial STEP'):
            self._run()
        self.assertFalse((self.base/'output').exists())

    def test_wrong_parent_bp_hash_blocks(self):
        self._write_zip(bp=b'DIFFERENT-BP')
        with self.assertRaisesRegex(ValueError,'S3.W BP SHA-256'):
            self._run()

    def test_parent_manifest_forgery_blocks(self):
        d=dict(self.s3w_metadata,combined_patches=149)
        self._write_zip(metadata=d)
        with self.assertRaisesRegex(ValueError,'S3.W private manifest'):
            self._run()

    def test_duplicate_private_bp_entries_block(self):
        self._write_zip(extras=[('other/'+replay.S3W_BP,b'FRAUD')])
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            self._run()

    def test_unsafe_zip_member_rejected(self):
        self._write_zip(extras=[('../'+replay.S3W_BP,b'FRAUD')])
        with self.assertRaises(ValueError):
            self._run()

    def test_missing_parent_manifest_blocks(self):
        with zipfile.ZipFile(self.zip_path,'w') as z:
            z.writestr(replay.S3W_BP,self.bp)
        with self.assertRaisesRegex(ValueError,'Missing or ambiguous'):
            self._run()

    def test_invalid_builder_exit_blocks(self):
        self._write_stub_builder(fail=True)
        with self.assertRaisesRegex(ValueError,'S3.Y replay script rejected'):
            self._run()

    def test_unexpected_selected_child_hash_blocks(self):
        self._write_stub_builder(corrupt_child=True)
        with self.assertRaisesRegex(ValueError,'Replayed selected child SHA'):
            self._run()

    def test_native_trim_blocked_replay_rejected(self):
        self._write_stub_builder(native_fail=True)
        with self.assertRaisesRegex(ValueError,'native original S3.Y trim gate'):
            self._run()

    def test_existing_nonempty_destination_blocks(self):
        target=self.base/'output';target.mkdir();(target/'existing').write_text('x')
        with self.assertRaisesRegex(ValueError,'empty directory'):
            self._run()

    def test_cli_missing_zip_reports_exit_three(self):
        status=replay.main(['--original-step',str(self.step_path),
                           '--s3w-private-zip',str(self.base/'absent.zip'),
                           '--s3y-builder',str(self.builder),
                           '--private-output-dir',str(self.base/'private')])
        self.assertEqual(status,3)

    def test_source_and_child_sha_are_different_frozen_contracts(self):
        self.assertNotEqual(replay.SOURCE_SHA,replay.S3W_SHA)
        self.assertNotEqual(replay.S3W_SHA,replay.S3Y_SHA)


if __name__=='__main__':
    unittest.main()
