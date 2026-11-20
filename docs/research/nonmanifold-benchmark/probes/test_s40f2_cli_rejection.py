#!/usr/bin/env python3
"""Exercise S40-F2 CLI status and artifact behavior without original third-party CAD."""
from __future__ import annotations

import argparse
import contextlib
import io
import ast
import json
import math
from pathlib import Path
import sys
import tempfile
from unittest import TestCase, main
from unittest.mock import patch

SOURCE=Path(__file__).with_name('s40f1_six_edge_planar_builder.py')
TREE=ast.parse(SOURCE.read_text(encoding='utf-8'))
FUNCTIONS={x.name:x for x in TREE.body if isinstance(x,ast.FunctionDef)}
NAMES=('require_native_pilot_pass','main')
assert all(x in FUNCTIONS for x in NAMES)
ns={'argparse':argparse,'json':json,'math':math,'Path':Path}
exec(compile(ast.Module(body=[FUNCTIONS[x] for x in NAMES],type_ignores=[]),str(SOURCE),'exec'),ns)


def good_report():
    one={'interior_IN':1,'boundary_IN_or_ON':4,'boundary_OUT':0,
         'candidate_patches':1,'sampled_native_coverage':{
             'native_area_mm2':3.,'approximate_integrated_bp_area_mm2':3.,
             'min_sampled_oriented_jacobian':.1,
             'sampled_relative_area_difference':0.,
             'sampled_2d_patch_overlap_area':0.,
             'sampled_numerical_hole_area_mm2':0.,
             'continuous_coverage_certified':False}}
    return {'status':'PASS_BOUNDED_SAMPLED_NATIVE_TRIM',
            'inside_IN':2,'boundary_IN_or_ON':8,'boundary_OUT':0,
            'by_face':{'1279':dict(one),'1386':dict(one)},
            'continuous_hausdorff_certified':False,
            'apmesh_TRI_QUAD_executed':False}


class NativeCLIControlFlowTest(TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='s40f2-cli-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.args=['s40f1_six_edge_planar_builder.py','--original-step',str(self.root/'original.step'),
                   '--selected-s3y-bp',str(self.root/'parent.bp'),
                   '--selected-s3y-manifest',str(self.root/'parent.json'),
                   '--output',str(self.root/'results')]
        (self.root/'original.step').write_bytes(b'fake STEP for control-flow unit test')
        (self.root/'parent.bp').write_bytes(b'fake parent for control-flow unit test')
        (self.root/'parent.json').write_text('{}')
        # Use a lightweight import stub; do not call a CAD kernel with synthetic bytes.
        import types
        ns['cq']=types.SimpleNamespace(importers=types.SimpleNamespace(
            importStep=lambda _:__import__("types").SimpleNamespace(val=lambda:object())))
        ns['validate_frozen']=lambda *args:True
        ns['build_source_candidate']=lambda *args:('synthetic-net',{'synthetic':True})
        ns['audit_native']=lambda *args:good_report()

    def run_cli(self):
        with patch.object(sys,'argv',self.args), contextlib.redirect_stdout(io.StringIO()):
            ns['main']()

    def test_missing_original_input_fails_closed_with_receipt(self):
        (self.root/'original.step').unlink()
        with self.assertRaises(SystemExit) as x:self.run_cli()
        self.assertEqual(x.exception.code,3)
        receipt=json.loads((self.root/'results/s40f1_rejection.json').read_text())
        self.assertEqual(receipt['error_type'],'FileNotFoundError')
        self.assertEqual(receipt['original_faces_represented_unchanged'],22)
        self.assertEqual(list((self.root/'results').glob('*.bp')),[])

    def test_native_trim_rejection_returns_code_three_without_candidate(self):
        status=good_report();status['status']='BLOCKED_NATIVE_TRIM';status['boundary_OUT']=2
        ns['audit_native']=lambda *args:status
        with self.assertRaises(SystemExit) as x:self.run_cli()
        self.assertEqual(x.exception.code,3)
        receipt=json.loads((self.root/'results/s40f1_rejection.json').read_text())
        self.assertEqual(receipt['state'],'BLOCKED_NO_NEW_FACE_ADMISSION')
        self.assertIn('native trim was not admitted',receipt['reason'])
        self.assertEqual(list((self.root/'results').glob('*.bp')),[])

    def test_runtime_native_import_exception_produces_failure_receipt(self):
        def fail(_):raise RuntimeError('OCP native importer rejected source')
        ns['cq'].importers.importStep=fail
        with self.assertRaises(SystemExit) as x:self.run_cli()
        self.assertEqual(x.exception.code,3)
        receipt=json.loads((self.root/'results/s40f1_rejection.json').read_text())
        self.assertEqual(receipt['error_type'],'RuntimeError')
        self.assertEqual(list((self.root/'results').glob('*.bp')),[])

    def test_indexed_candidate_build_exception_produces_failure_receipt(self):
        def fail(*_):raise IndexError('invalid control ID')
        ns['build_source_candidate']=fail
        with self.assertRaises(SystemExit) as x:self.run_cli()
        self.assertEqual(x.exception.code,3)
        receipt=json.loads((self.root/'results/s40f1_rejection.json').read_text())
        self.assertEqual(receipt['error_type'],'IndexError')
        self.assertEqual(list((self.root/'results').glob('*.bp')),[])

    def test_only_bounded_pilot_gate_emits_candidate(self):
        self.run_cli()
        files=list((self.root/'results').glob('*.bp'))
        self.assertEqual([x.name for x in files],['s40f1.BOUNDED_RESEARCH_CANDIDATE.bp'])
        self.assertEqual(files[0].read_text(),'synthetic-net')
        self.assertFalse((self.root/'results/s40f1_rejection.json').exists())
        self.assertEqual(json.loads((self.root/'results/s40f1_native_audit.json').read_text())['status'],
                         'PASS_BOUNDED_SAMPLED_NATIVE_TRIM')


if __name__=='__main__':main()
