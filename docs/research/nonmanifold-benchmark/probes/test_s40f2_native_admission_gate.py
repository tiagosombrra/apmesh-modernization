#!/usr/bin/env python3
"""Tests for native admission receipt and fail-closed CLI control flow."""
from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path
import unittest

FILE = Path(__file__).with_name('s40f1_six_edge_planar_builder.py')
TREE = ast.parse(FILE.read_text(encoding='utf-8'))
NAMES = {'require_native_pilot_pass', 'validate_native_sample_grids'}
HELPERS = [x for x in TREE.body if isinstance(x, ast.FunctionDef) and x.name in NAMES]
assert {x.name for x in HELPERS} == NAMES
import math
ns = {'math': math}
exec(compile(ast.Module(body=HELPERS,type_ignores=[]),str(FILE),'exec'),ns)


def native_report():
    part=lambda: dict(boundary_OUT=0,interior_IN=50,boundary_IN_or_ON=80,
                      candidate_patches=2,sampled_native_coverage={
                          'continuous_coverage_certified':False,
                          'sampled_relative_area_difference':0.000005,
                          'native_area_mm2': 100.,
                          'approximate_integrated_bp_area_mm2': 100.0005,
                          'min_sampled_oriented_jacobian': .5,
                          'sampled_2d_patch_overlap_area': 0.,
                          'sampled_numerical_hole_area_mm2': 0.})
    return {'status':'PASS_BOUNDED_SAMPLED_NATIVE_TRIM',
            'inside_IN':100,'boundary_IN_or_ON':160,'boundary_OUT':0,
            'by_face':{'1279':part(),'1386':part()},
            'continuous_hausdorff_certified':False,
            'apmesh_TRI_QUAD_executed':False}


class NativeAdmissionChecks(unittest.TestCase):
    def accept(self, report):
        return ns['require_native_pilot_pass'](report)

    def test_full_sampled_native_evidence_admits_bounded_pilot(self):
        self.assertTrue(self.accept(native_report()))

    def test_forged_global_success_status_without_actual_face_checks(self):
        report=native_report();report['by_face']={}
        with self.assertRaisesRegex(ValueError,'incomplete'):
            self.accept(report)

    def test_missing_receipt_rejected(self):
        with self.assertRaisesRegex(ValueError,'Missing original'):
            self.accept(None)

    def test_blocked_native_trim_rejected_despite_nonzero_interior(self):
        report=native_report();report['status']='BLOCKED_NATIVE_TRIM'
        with self.assertRaisesRegex(ValueError,'not admitted'):
            self.accept(report)

    def test_candidate_generated_but_native_not_run_rejected(self):
        report=native_report();report['status']='NOT_RUN'
        with self.assertRaisesRegex(ValueError,'not admitted'):
            self.accept(report)

    def test_nonzero_global_out_samples_rejected(self):
        report=native_report();report['boundary_OUT']=1
        with self.assertRaisesRegex(ValueError,'counts failed'):
            self.accept(report)

    def test_zero_global_interior_samples_rejected(self):
        report=native_report();report['inside_IN']=0
        with self.assertRaisesRegex(ValueError,'counts failed'):
            self.accept(report)

    def test_zero_boundary_samples_rejected(self):
        report=native_report();report['boundary_IN_or_ON']=0
        with self.assertRaisesRegex(ValueError,'were not executed'):
            self.accept(report)

    def test_malformed_per_face_info_rejected(self):
        report=native_report();report['by_face']['1279']=None
        with self.assertRaisesRegex(ValueError,'face #1279'):
            self.accept(report)

    def test_missing_one_source_face_rejected(self):
        report=native_report();del report['by_face']['1386']
        with self.assertRaisesRegex(ValueError,'incomplete'):
            self.accept(report)

    def test_nonzero_per_face_out_rejected(self):
        report=native_report();report['by_face']['1386']['boundary_OUT']=1
        with self.assertRaisesRegex(ValueError,'face #1386'):
            self.accept(report)

    def test_zero_per_face_patch_count_rejected(self):
        report=native_report();report['by_face']['1279']['candidate_patches']=0
        with self.assertRaisesRegex(ValueError,'face #1279'):
            self.accept(report)

    def test_missing_independent_coverage_audit_rejected(self):
        report=native_report();report['by_face']['1386'].pop('sampled_native_coverage')
        with self.assertRaisesRegex(ValueError,'face #1386'):
            self.accept(report)

    def test_continuous_coverage_claim_rejected(self):
        report=native_report();report['by_face']['1279']['sampled_native_coverage']['continuous_coverage_certified']=True
        with self.assertRaisesRegex(ValueError,'Unsupported continuous CAD'):
            self.accept(report)

    def test_continuous_hausdorff_claim_rejected(self):
        report=native_report();report['continuous_hausdorff_certified']=True
        with self.assertRaisesRegex(ValueError,'Unsupported continuous or production'):
            self.accept(report)

    def test_cpp_meshing_claim_rejected(self):
        report=native_report();report['apmesh_TRI_QUAD_executed']=True
        with self.assertRaisesRegex(ValueError,'Unsupported continuous or production'):
            self.accept(report)

    def test_default_sample_density_accepted(self):
        self.assertTrue(ns['validate_native_sample_grids'](13,31))

    def test_zero_native_interior_density_rejected(self):
        with self.assertRaisesRegex(ValueError,'Invalid original'):
            ns['validate_native_sample_grids'](0,31)

    def test_nan_area_difference_rejected(self):
        report=native_report();report['by_face']['1279']['sampled_native_coverage']['sampled_relative_area_difference']=float('nan')
        with self.assertRaisesRegex(ValueError,'missing finite'):
            self.accept(report)

    def test_forged_overlapping_patch_regions_rejected(self):
        report=native_report();report['by_face']['1386']['sampled_native_coverage']['sampled_2d_patch_overlap_area']=0.1
        with self.assertRaisesRegex(ValueError,'coverage metrics failed'):
            self.accept(report)

    def test_excessive_area_error_rejected(self):
        report=native_report();report['by_face']['1279']['sampled_native_coverage']['sampled_relative_area_difference']=.005
        with self.assertRaisesRegex(ValueError,'coverage metrics failed'):
            self.accept(report)

    def test_negative_jacobian_rejected(self):
        report=native_report();report['by_face']['1279']['sampled_native_coverage']['min_sampled_oriented_jacobian']=-.5
        with self.assertRaisesRegex(ValueError,'coverage metrics failed'):
            self.accept(report)

    def test_sample_count_mismatch_rejected(self):
        report=native_report();report['inside_IN']=101
        with self.assertRaisesRegex(ValueError,'sample counts differ'):
            self.accept(report)

    def test_sample_count_boundary_mismatch_rejected(self):
        report=native_report();report['boundary_IN_or_ON']=161
        with self.assertRaisesRegex(ValueError,'sample counts differ'):
            self.accept(report)

    def test_zero_native_boundary_density_rejected(self):
        with self.assertRaisesRegex(ValueError,'Invalid original'):
            ns['validate_native_sample_grids'](13,0)

    def test_unbounded_native_density_rejected(self):
        with self.assertRaisesRegex(ValueError,'Invalid original'):
            ns['validate_native_sample_grids'](10000,10000)

    def test_boolean_density_rejected(self):
        with self.assertRaisesRegex(ValueError,'integer densities'):
            ns['validate_native_sample_grids'](True,31)

    def test_non_integer_density_rejected(self):
        with self.assertRaisesRegex(ValueError,'integer densities'):
            ns['validate_native_sample_grids'](13.0,31)

    def test_cli_native_gate_before_output_file_write(self):
        builder=next(x for x in TREE.body if isinstance(x,ast.FunctionDef) and x.name=='main')
        calls=[(x.func.id,x.lineno) for x in ast.walk(builder)
               if isinstance(x,ast.Call) and isinstance(x.func,ast.Name)
               and x.func.id in ('audit_native','require_native_pilot_pass')]
        order=dict(calls)
        self.assertLess(order['audit_native'],order['require_native_pilot_pass'])

    def test_native_pilot_input_grid_validated_before_sampling(self):
        builder=next(x for x in TREE.body if isinstance(x,ast.FunctionDef) and x.name=='audit_native')
        methods=[(x.func.id,x.lineno) for x in ast.walk(builder)
                 if isinstance(x,ast.Call) and isinstance(x.func,ast.Name)
                 and x.func.id in ('validate_native_sample_grids','build_source_candidate')]
        order=dict(methods)
        self.assertLess(order['validate_native_sample_grids'],order['build_source_candidate'])


if __name__ == '__main__':
    unittest.main()
