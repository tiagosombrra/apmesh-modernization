#!/usr/bin/env python3
"""Hermetic negative/positive tests for the source-native S3.Z.4 orchestrator."""
from __future__ import annotations

from contextlib import contextmanager
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import s3zd_original_s40_runner as runner


def sample_trial_receipt(statuses=None):
    """Make a synthetic native-style receipt without original CAD geometry."""
    states = statuses or ["BLOCKED"] * 8
    return {
        "source_sha256": runner.ORIGINAL_STEP_SHA,
        "parent_156_patch_sha256": runner.S3Y_SELECTED_SHA,
        "original_step_faces_blocked": list(runner.TARGET_FACES),
        "admitted_patch_count": 156,
        "admitted_source_faces": 22,
        "strict_native_admission_completed": False,
        "apmesh_tri_quad_executed": False,
        "candidate_trials": [
            {"shared_control_bias_mm": bias, "status": state,
             "candidate_sha256": f"{i:064x}"}
            for i, (bias, state) in enumerate(zip(runner.TRIAL_BIASES_MM, states))
        ],
    }


class Stream:
    """Minimal context-managed HTTP fixture."""
    def __init__(self, data):
        self.fp = io.BytesIO(data)
    def __enter__(self):return self
    def __exit__(self, *_):return False
    def read(self, length):return self.fp.read(length)


class S3Z4OrchestrationTests(unittest.TestCase):
    def test_original_pin_is_declared(self):
        self.assertEqual(len(runner.ORIGINAL_STEP_SHA), 64)
        self.assertEqual(runner.FIXED_BUDGET_MM, .001)
        self.assertEqual(len(runner.TRIAL_BIASES_MM), 8)

    def test_no_automatic_original_face_admission(self):
        got = runner.assess_trial_result(sample_trial_receipt())
        self.assertEqual(got['new_original_source_faces_admitted'], 0)
        self.assertFalse(got['formal_final_acceptance'])

    def test_eight_blocked_trials_report_zero_preliminary(self):
        got = runner.assess_trial_result(sample_trial_receipt())
        self.assertEqual(got['rejected_native_candidates'], 8)
        self.assertEqual(got['preliminary_candidates_needing_independent_audit'], 0)

    def test_preliminary_candidates_require_independent_audit(self):
        states = ['BLOCKED'] * 8
        states[4] = "PRELIMINARY_TWO_SIDED_TRIM_PASS_NOT_ADMITTED"
        got = runner.assess_trial_result(sample_trial_receipt(states))
        self.assertEqual(got['preliminary_candidates_needing_independent_audit'], 1)
        self.assertEqual(got['rejected_native_candidates'], 7)
        self.assertEqual(got['new_original_source_faces_admitted'], 0)

    def test_reject_incomplete_trial_list(self):
        x = sample_trial_receipt()
        x['candidate_trials'].pop()
        with self.assertRaisesRegex(ValueError, 'eight'):
            runner.assess_trial_result(x)

    def test_reject_changed_bias_order(self):
        x=sample_trial_receipt()
        x['candidate_trials'][0]['shared_control_bias_mm']=.5
        with self.assertRaisesRegex(ValueError, 'order or budget'):
            runner.assess_trial_result(x)

    def test_reject_fake_admitted_faces(self):
        x=sample_trial_receipt()
        x['admitted_source_faces']=24
        with self.assertRaisesRegex(ValueError, 'claims'):
            runner.assess_trial_result(x)

    def test_reject_fake_cpp_meshing(self):
        x=sample_trial_receipt()
        x['apmesh_tri_quad_executed']=True
        with self.assertRaisesRegex(ValueError, 'invents'):
            runner.assess_trial_result(x)

    def test_reject_missing_geometry_digest(self):
        x=sample_trial_receipt()
        x['candidate_trials'][3].pop('candidate_sha256')
        with self.assertRaisesRegex(ValueError, 'digest'):
            runner.assess_trial_result(x)

    def test_reject_unknown_trial_status(self):
        x=sample_trial_receipt()
        x['candidate_trials'][0]['status']='APPROVED_CAD_FULL'
        with self.assertRaisesRegex(ValueError, 'disposition'):
            runner.assess_trial_result(x)

    def test_reject_different_original_step(self):
        with self.assertRaisesRegex(runner.InputBlocked, 'hash'):
            runner.verify_original_bytes(b'not-original')

    def test_fetched_bytes_are_sha_pinned(self):
        with tempfile.TemporaryDirectory() as d:
            original=Path(d)/'private'/'i25o_s40.step'
            import hashlib
            with patch.object(runner,'ORIGINAL_STEP_SHA',hashlib.sha256(b'pinned-fixture').hexdigest()):
                metadata=runner.fetch_pinned_original(original,opener=lambda url,timeout: Stream(b'pinned-fixture'))
            self.assertEqual(original.read_bytes(),b'pinned-fixture')
            self.assertEqual(metadata['source'],'FETCHED_FIXED_GIT_REVISION')
            self.assertFalse(any('.partial' in z.name for z in original.parent.iterdir()))

    def test_download_hash_mismatch_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as d:
            original=Path(d)/'private'/'i25o_s40.step'
            with self.assertRaisesRegex(runner.InputBlocked, 'SHA-256'):
                runner.fetch_pinned_original(original,opener=lambda *_args,**_kw: Stream(b'fake-step'))
            self.assertFalse(original.exists())
            self.assertEqual(list(original.parent.iterdir()),[])

    def test_download_does_not_overwrite_valid_existing_source(self):
        with tempfile.TemporaryDirectory() as d:
            original=Path(d)/'i25o_s40.step'
            original.write_bytes(b'fixture')
            import hashlib
            with patch.object(runner,'ORIGINAL_STEP_SHA',hashlib.sha256(b'fixture').hexdigest()):
                r=runner.fetch_pinned_original(original,opener=lambda *_args,**_kw: self.fail('Network called'))
            self.assertEqual(r['source'],'EXISTING_VERIFIED_FILE')

    def test_oversized_download_removed(self):
        with tempfile.TemporaryDirectory() as d:
            original=Path(d)/'i25o_s40.step'
            with patch.object(runner,'MAX_STEP_BYTES',4):
                with self.assertRaisesRegex(runner.InputBlocked,'size limit'):
                    runner.fetch_pinned_original(original,opener=lambda *_args,**_kw: Stream(b'12345'))
            self.assertFalse(original.exists())

    def test_missing_private_inputs_produce_blocked_nonclaim(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            report,code=runner.run_s3z4(root/'i25o_s40.step',root/'s3w.bp',root/'s3w.json',
                                         root/'s3y_s40_curved_planar_rings.py',root/'output')
            self.assertEqual(code,3)
            self.assertEqual(report['new_original_source_faces_admitted'],0)
            self.assertEqual(report['status'],'BLOCKED_MISSING_OR_MISMATCHED_PRIVATE_DATA')

    def test_ready_synthetic_trial_writes_private_and_never_admits(self):
        from s3zb_check_private_readiness import check_readiness
        import hashlib
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            original=root/'i25o_s40.step';parent=root/'s3w.bp'
            manifest=root/'s3w.json';builder=root/'s3y_s40_curved_planar_rings.py'
            original.write_bytes(b'step-fixture');parent.write_bytes(b'bp-fixture')
            manifest.write_text('{}');builder.write_text('')
            fake_ready={
                'status':'READY_FOR_ORIGINAL_NATIVE_TRIAL',
                'checks':{k:{'found':True,'hash_ok':True} for k in
                          ('original_step','s3w_parent_bp','s3w_manifest','s3y_builder_py')},
                'python_dependencies':{'cadquery':True,'OCP':True,'numpy':True,'scipy':True,'shapely':True},
            }
            fake=sample_trial_receipt()
            fake['source_sha256']=hashlib.sha256(b'step-fixture').hexdigest()
            with patch('s3zb_check_private_readiness.check_readiness',return_value=fake_ready), \
                 patch.object(runner,'ORIGINAL_STEP_SHA',hashlib.sha256(b'step-fixture').hexdigest()), \
                 patch.object(runner,'S3W_PARENT_SHA',hashlib.sha256(b'bp-fixture').hexdigest()), \
                 patch.object(runner,'S3Y_SELECTED_SHA',fake['parent_156_patch_sha256']):
                report,code=runner.run_s3z4(original,parent,manifest,builder,root/'private-evidence',
                    importer=lambda _path:object(),private_executor=lambda *_:(fake,None))
            self.assertEqual(code,0)
            self.assertEqual(report['status'],'TRIALS_EXECUTED_NO_NEW_FACE_ADMISSION')
            self.assertEqual(report['new_original_source_faces_admitted'],0)
            candidate=root/'private-evidence/s3zd_original_native_trials_private.json'
            self.assertTrue(candidate.is_file())
            self.assertEqual(len(json.loads(candidate.read_text())['candidate_trials']),8)

    def test_native_failure_preserves_156_patch_baseline(self):
        import hashlib
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            original=root/'i25o_s40.step';parent=root/'s3w.bp'
            manifest=root/'s3w.json';builder=root/'s3y_s40_curved_planar_rings.py'
            original.write_bytes(b'step-fixture');parent.write_bytes(b'bp-fixture')
            manifest.write_text('{}');builder.write_text('')
            fake_ready={'status':'READY_FOR_ORIGINAL_NATIVE_TRIAL',
                        'checks':{k:{'found':True} for k in ('original_step','s3w_parent_bp','s3w_manifest','s3y_builder_py')},
                        'python_dependencies':{}}
            def fail(*_):raise ValueError('native original curve failed')
            with patch('s3zb_check_private_readiness.check_readiness',return_value=fake_ready), \
                 patch.object(runner,'ORIGINAL_STEP_SHA',hashlib.sha256(b'step-fixture').hexdigest()), \
                 patch.object(runner,'S3W_PARENT_SHA',hashlib.sha256(b'bp-fixture').hexdigest()):
                report,code=runner.run_s3z4(original,parent,manifest,builder,root/'output',
                                              importer=lambda _path:object(),private_executor=fail)
            self.assertEqual(code,4)
            self.assertEqual(report['status'],'BLOCKED_NATIVE_OR_TOPOLOGY_GATE')
            self.assertEqual(report['selected_patch_count_before_native_trials'],156)
            self.assertEqual(report['new_original_source_faces_admitted'],0)

    def test_receipt_writer_is_atomic(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'report.json'
            runner._atomic_json(p,{'status':'BLOCKED'})
            self.assertEqual(json.loads(p.read_text())['status'],'BLOCKED')
            self.assertEqual([x.name for x in p.parent.iterdir()],['report.json'])


if __name__=='__main__':
    unittest.main()
