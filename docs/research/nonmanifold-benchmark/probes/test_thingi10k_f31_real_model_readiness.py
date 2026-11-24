#!/usr/bin/env python3
"""Evidence-only and regression-denial tests for F31 real-source readiness ledger."""
from __future__ import annotations
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

import thingi10k_f31_real_model_readiness as m


def fixture():
    header=('thingi10k_file_id,literature_cohort,raw_stl_audit_executed,'
            'original_source_rights_independently_verified,'
            'quadwild_reference_mesh_pair_verified,apmesh_mesh_generated')
    cases=[]
    for i,mid in enumerate(m.EXPECTED_IDS):
        group='QUADWILD_FIG29' if mid in {44503,128001,58012,61394,67792,69975,
                                         81877,94884,230923,364256,423069,498974} else 'BADIA_FIG10_TABLE1'
        cases.append(f'{mid},{group},{"YES" if mid in m.AUDITED else "NO"},NO,NO,NO')
    return ('\n'.join((header,*cases))+'\n').encode('utf-8')


def f27():
    return {'schema':'apmesh-s40-f27-original-tri-stage0-audit-v1',
            'source_model_id':293137,'native_stage0_accepted_by_engine':True,
            'asset_license_independently_cleared':False,
            'scientific_benchmark_admitted':False,'native_triangles':3504}


def f30():
    return {'schema':'apmesh-s40-f30-feature-locked-pareto-center-v1',
            'source_facets':292,'quad_faces':876,'copyright_license_cleared':False,
            'native_quad_generator_executed':False,
            'independent_matched_quad_literature_reference':False,
            'scientific_benchmark_admitted':False}


class ReadinessContractTests(unittest.TestCase):
    def test_01_exact_23_cases(self):self.assertEqual(len(m.EXPECTED_IDS),23)
    def test_02_unique_cases(self):self.assertEqual(len(set(m.EXPECTED_IDS)),23)
    def test_03_expected_seven_source_audits(self):self.assertEqual(len(m.AUDITED),7)
    def test_04_expected_three_pilots(self):self.assertEqual(len(m.PILOTS),3)
    def test_05_frozen_control_priority(self):self.assertEqual(m.role_of(61394),'SOURCE_TOPOLOGY_NEGATIVE_CONTROL')
    def test_06_g41_reference_first(self):self.assertEqual(m.role_of(58012),'EXACT_AUTHOR_REFERENCE_ACQUISITION_FIRST')
    def test_07_higher_genus_stress(self):self.assertEqual(m.role_of(550964),'HIGH_GENUS_SOURCE_CONVERSION_STRESS')
    def test_08_other_case_unqualified(self):self.assertEqual(m.role_of(44503),'SOURCE_GEOMETRY_AUDIT_REQUIRED')
    def test_09_cohort_count(self):self.assertEqual(m.EXPECTED_COHORT,{'QUADWILD_FIG29':12,'BADIA_FIG10_TABLE1':11})
    def test_10_minimal_fixture_matches(self):self.assertEqual(m.reconcile(fixture(),f27(),f30())['case_count'],23)
    def test_11_one_real_native_tri(self):
        r=m.reconcile(fixture(),f27(),f30())
        self.assertEqual([c['model_id'] for c in r['cases'] if c['native_apmesh_tri_model_executed']],[293137])
    def test_12_one_external_quad(self):
        r=m.reconcile(fixture(),f27(),f30())
        self.assertEqual([c['model_id'] for c in r['cases'] if c['external_derived_quad_experiment_executed']],[293137])
    def test_13_no_native_quad(self):self.assertFalse(any(c['native_apmesh_quad_executed'] for c in m.reconcile(fixture(),f27(),f30())['cases']))
    def test_14_no_scientific_benchmark_admission(self):self.assertEqual(m.reconcile(fixture(),f27(),f30())['fair_literature_comparisons_admitted'],0)
    def test_15_source_rights_remain_uncleared(self):self.assertTrue(all(not c['asset_rights_independently_cleared'] for c in m.reconcile(fixture(),f27(),f30())['cases']))
    def test_16_missing_case_rejected(self):
        b=fixture().decode().splitlines()
        with self.assertRaises(ValueError):m.reconcile(('\n'.join(b[:-1])+'\n').encode(),f27(),f30())
    def test_17_duplicate_case_rejected(self):
        b=fixture().decode().splitlines()
        b[-1]=b[-2]
        with self.assertRaises(ValueError):m.reconcile(('\n'.join(b)+'\n').encode(),f27(),f30())
    def test_18_permission_false_promotion_rejected(self):
        b=fixture().replace(b',NO,NO,NO\n',b',YES,NO,NO\n',1)
        with self.assertRaises(ValueError):m.reconcile(b,f27(),f30())
    def test_19_native_tri_false_promotion_in_f17_rejected(self):
        b=fixture().replace(b',NO,NO,NO\n',b',NO,NO,YES\n',1)
        with self.assertRaises(ValueError):m.reconcile(b,f27(),f30())
    def test_20_fake_author_quad_pair_rejected(self):
        b=fixture().replace(b',NO,NO,NO\n',b',NO,YES,NO\n',1)
        with self.assertRaises(ValueError):m.reconcile(b,f27(),f30())
    def test_21_bad_native_tri_count_rejected(self):
        p=f27();p['native_triangles']=0
        with self.assertRaises(ValueError):m.reconcile(fixture(),p,f30())
    def test_22_bad_model_id_rejected(self):
        p=f27();p['source_model_id']=123
        with self.assertRaises(ValueError):m.reconcile(fixture(),p,f30())
    def test_23_unverified_rights_in_f27_cannot_be_promoted(self):
        p=f27();p['asset_license_independently_cleared']=True
        with self.assertRaises(ValueError):m.reconcile(fixture(),p,f30())
    def test_24_native_quad_false_promotion_rejected(self):
        p=f30();p['native_quad_generator_executed']=True
        with self.assertRaises(ValueError):m.reconcile(fixture(),f27(),p)
    def test_25_fake_literature_reference_pair_rejected(self):
        p=f30();p['independent_matched_quad_literature_reference']=True
        with self.assertRaises(ValueError):m.reconcile(fixture(),f27(),p)
    def test_26_changed_f30_schema_rejected(self):
        p=f30();p['schema']='unknown'
        with self.assertRaises(ValueError):m.reconcile(fixture(),f27(),p)
    def test_27_changed_f27_schema_rejected(self):
        p=f27();p['schema']='unknown'
        with self.assertRaises(ValueError):m.reconcile(fixture(),p,f30())
    def test_28_no_geometry_paths_in_output(self):
        txt=json.dumps(m.reconcile(fixture(),f27(),f30()))
        for suffix in ('.stl','.bp','.obj','v 0.','f 1 '):self.assertNotIn(suffix,txt)
    def test_29_output_sorted(self):
        rows=m.reconcile(fixture(),f27(),f30())['cases']
        self.assertEqual([c['model_id'] for c in rows],sorted(m.EXPECTED_IDS))
    def test_30_missing_source_fails_precondition(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):m.produce(Path(d))
    def test_31_mutated_source_hash_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/m.SOURCE_CSV_PATH;p.parent.mkdir(parents=True)
            p.write_bytes(fixture())
            with self.assertRaises(ValueError):m.pinned_file(Path(d),m.SOURCE_CSV_PATH,m.SOURCE_CSV_GIT_BLOB)


if __name__=='__main__':unittest.main()
