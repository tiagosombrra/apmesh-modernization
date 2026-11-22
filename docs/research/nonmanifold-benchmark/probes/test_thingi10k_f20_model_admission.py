"""Hermetic tests for frozen 23-case scientific-admission triage semantics."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from thingi10k_f20_model_admission import audit

Q = [44503, 128001, 58012, 61394, 67792, 69975, 81877, 94884,
     230923, 364256, 423069, 498974]
B = [252119, 293137, 35269, 37266, 37881, 441708, 47076, 550964,
     551021, 65904, 96457]
CLEAN = {58012: (41, -80), 293137: (0, 2), 37881: (1, 0),
         47076: (0, 2), 550964: (4, -6), 96457: (3, -4)}
AUDITED = set(CLEAN) | {61394}
MATCH = {58012, 67792, 81877, 94884}
V_F = {58012: (113799, 113879), 67792: (16615, 16735),
       81877: (35185, 35305), 94884: (47116, 47466)}
SRC_SHA = 'a' * 64


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sources = self.root / 'sources.csv'
        self.literature = self.root / 'literature.csv'
        self.topology = self.root / 'topology.json'
        self.euler = self.root / 'paper.csv'
        self.source_rows = []
        self.literature_rows = []
        self.euler_rows = []
        for mid in Q + B:
            cohort = 'QUADWILD_FIG29' if mid in Q else 'BADIA_FIG10_TABLE1'
            genus, chi = CLEAN.get(mid, (None, -13 if mid == 61394 else None))
            self.source_rows.append(dict(thingi10k_file_id=mid,literature_cohort=cohort,
                raw_stl_audit_executed='YES' if mid in AUDITED else 'NO',
                source_stl_sha256=SRC_SHA if mid in AUDITED else '',
                source_zip_git_blob_sha1='a'*40,source_zip_bytes='1000',
                raw_euler_characteristic=chi if chi is not None else '',
                conditional_source_surface_genus=genus if genus is not None else '',
                original_source_rights_independently_verified='NO',
                quadwild_reference_mesh_pair_verified='NO',apmesh_mesh_generated='NO'))
            pv,pf=V_F.get(mid,(1000,1002))
            self.literature_rows.append(dict(thingi10k_file_id=mid,literature_cohort=cohort,
                published_quad_vertices=pv if mid in Q else '',
                published_quad_faces=pf if mid in Q else '',
                individual_license_status='PER_ASSET_NOT_REVIEWED',
                quad_result_pair_status='ARCHIVE_EXISTS_ID_PAIR_NOT_VERIFIED',
                apmesh_pipeline_status='NOT_RUN'))
            if mid in Q:
                screen = 'DIRECT_RAW_STL_TOPOLOGY_AUDITED' if mid == 58012 else (
                    'CONDITIONAL_PINNED_CATALOG_ONLY' if mid in MATCH else 'CATALOG_NOT_CLEAN')
                self.euler_rows.append(dict(thingi10k_file_id=mid,source_euler_evidence=screen,
                    published_quad_euler_if_closed_quad=pv-pf,
                    published_output_euler_matches_source='true' if mid in MATCH else 'false',
                    actual_quad_mesh_bytes_checked='false',matched_pair_verified='false',
                    apmesh_quad_mesh_generated='false'))
        self.invariants = dict(audited_original_stl_files=7,manifest_entries=23,
            topology_invariants={str(mid):dict(
                source_mesh_euler_characteristic_raw=(CLEAN[mid][1] if mid in CLEAN else -13),
                applicable_genus=(CLEAN[mid][0] if mid in CLEAN else None),
                closed_connected_orientable_surface_screen=('COMBINATORIAL_PASS' if mid in CLEAN else 'NOT_PROVED'),
                failed_conditions=[] if mid in CLEAN else ['edge_manifold'])
                for mid in AUDITED})
        self.save()

    def write_csv(self,path,rows):
        with path.open('w',newline='',encoding='utf-8') as stream:
            w=csv.DictWriter(stream,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)

    def save(self):
        self.write_csv(self.sources,self.source_rows)
        self.write_csv(self.literature,self.literature_rows)
        self.write_csv(self.euler,self.euler_rows)
        self.topology.write_text(json.dumps(self.invariants),encoding='utf-8')

    def runaudit(self):
        self.save()
        return audit(self.sources,self.literature,self.topology,self.euler)

    def test_01_baseline_roster_roles(self):
        data=self.runaudit()
        self.assertEqual(data['source_case_count'],23)
        self.assertEqual(data['independently_audited_raw_stl_cases'],7)
        self.assertEqual(data['audited_closed_surface_sources'],6)
        self.assertEqual(data['audited_adversarial_sources'],1)
        self.assertEqual(data['quadwild_raw_audited_euler_matches'],1)
        self.assertEqual(data['quadwild_catalog_only_euler_matches'],3)
        self.assertEqual(data['priority_roles'],dict(
            REFERENCE_PAIR_ACQUISITION_FIRST=1,ADVERSARIAL_TOPOLOGY_CONTROL=1,
            SMALL_SOURCE_CONVERSION_PILOT=3,HIGHER_GENUS_CONVERSION_STRESS=2,
            SOURCE_GEOMETRY_AUDIT_REQUIRED=16))

    def test_02_no_case_claims_real_meshing_or_rights(self):
        for row in self.runaudit()['cases']:
            self.assertFalse(row['fair_apmesh_vs_paper_comparison_admitted'])
            self.assertFalse(row['source_and_output_permissions_cleared'])
            self.assertFalse(row['four_sided_bezier_patch_domain_constructed'])

    def test_03_canopy_genus_41_reference_pilot(self):
        row=next(c for c in self.runaudit()['cases'] if c['model_id']==58012)
        self.assertEqual(row['source_genus_if_certified'],41)
        self.assertEqual(row['published_output_euler_screen'],'NECESSARY_EULER_MATCH_RAW_SOURCE')
        self.assertEqual(row['research_role'],'REFERENCE_PAIR_ACQUISITION_FIRST')

    def test_04_nonmanifold_stl_not_true_cad_edge(self):
        row=next(c for c in self.runaudit()['cases'] if c['model_id']==61394)
        self.assertEqual(row['research_role'],'ADVERSARIAL_TOPOLOGY_CONTROL')
        self.assertFalse(row['original_cad_curve_junction_proven'])
        self.assertIsNone(row['source_genus_if_certified'])

    def test_05_missing_literature_case_fails(self):
        self.literature_rows.pop()
        with self.assertRaisesRegex(ValueError,'23-case'):self.runaudit()

    def test_06_duplicate_model_fails(self):
        self.source_rows[1]['thingi10k_file_id']=44503
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.runaudit()

    def test_07_unmatching_invariant_ids_fails(self):
        self.invariants['topology_invariants'].pop('58012')
        self.invariants['topology_invariants']['58013']=dict(
            source_mesh_euler_characteristic_raw=-80,applicable_genus=41,
            closed_connected_orientable_surface_screen='COMBINATORIAL_PASS',failed_conditions=[])
        with self.assertRaisesRegex(ValueError,'raw audits disagree'):self.runaudit()

    def test_08_false_raw_euler_fails(self):
        self.source_rows[2]['raw_euler_characteristic']='-70'
        with self.assertRaisesRegex(ValueError,'Euler mismatch'):self.runaudit()

    def test_09_false_raw_genus_fails(self):
        self.source_rows[2]['conditional_source_surface_genus']='40'
        with self.assertRaisesRegex(ValueError,'genus and Euler'):self.runaudit()

    def test_10_invalid_source_hash_fails(self):
        self.source_rows[2]['source_stl_sha256']='0'*16
        with self.assertRaisesRegex(ValueError,'SHA-256'):self.runaudit()

    def test_11_bad_archive_git_blob_fails(self):
        self.source_rows[4]['source_zip_git_blob_sha1']='INVALID'
        with self.assertRaisesRegex(ValueError,'archive provenance'):self.runaudit()

    def test_12_paper_euler_computation_fails(self):
        self.euler_rows[2]['published_quad_euler_if_closed_quad']=0
        with self.assertRaisesRegex(ValueError,'Euler precheck'):self.runaudit()

    def test_13_unproven_paper_euler_match_fails(self):
        self.euler_rows[0]['published_output_euler_matches_source']='true'
        with self.assertRaisesRegex(ValueError,'no source basis'):self.runaudit()

    def test_14_false_paper_euler_source_fails(self):
        self.euler_rows[2]['published_quad_euler_if_closed_quad']=100
        with self.assertRaisesRegex(ValueError,'precheck contradictory'):self.runaudit()

    def test_15_spurious_real_quad_claim_fails(self):
        self.euler_rows[2]['actual_quad_mesh_bytes_checked']='true'
        with self.assertRaisesRegex(ValueError,'availability changed'):self.runaudit()

    def test_16_source_pipeline_claim_requires_new_protocol(self):
        self.source_rows[2]['apmesh_mesh_generated']='YES'
        with self.assertRaisesRegex(ValueError,'new audit protocol'):self.runaudit()

    def test_17_false_original_license_approval_fails(self):
        self.source_rows[2]['original_source_rights_independently_verified']='YES'
        with self.assertRaisesRegex(ValueError,'new audit protocol'):self.runaudit()

    def test_18_fake_genus_for_adversarial_source_fails(self):
        self.source_rows[3]['conditional_source_surface_genus']='0'
        with self.assertRaisesRegex(ValueError,'improperly assigned a genus'):self.runaudit()

    def test_19_unverified_stl_claims_hash_fails(self):
        self.source_rows[0]['source_stl_sha256']='f'*64
        with self.assertRaisesRegex(ValueError,'invented geometry invariants'):self.runaudit()

    def test_20_wrong_cohort_count_fails(self):
        self.source_rows[0]['literature_cohort']='BADIA_FIG10_TABLE1'
        self.literature_rows[0]['literature_cohort']='BADIA_FIG10_TABLE1'
        with self.assertRaisesRegex(ValueError,'cohort changed'):self.runaudit()

    def test_21_bad_invariant_denominator_fails(self):
        self.invariants['audited_original_stl_files']=8
        with self.assertRaisesRegex(ValueError,'denominator'):self.runaudit()

    def test_22_unpaired_f18_ids_fails(self):
        self.euler_rows[-1]['thingi10k_file_id']=293137
        with self.assertRaisesRegex(ValueError,'paper rows'):self.runaudit()


if __name__=='__main__':
    unittest.main()