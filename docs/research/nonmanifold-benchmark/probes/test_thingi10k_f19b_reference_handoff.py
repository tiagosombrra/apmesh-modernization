"""Hermetic negative/identity tests for the F19B cross-stage evidence handoff."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from thingi10k_f19b_reference_handoff import AUTHOR_ARCHIVE_URL, check

SOURCE = '2c7c322af76b46a307e67af451ebba9e6609e6932a2829f4c596853dbf122d4b'


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.actual = self.root / '58012_output.obj'
        self.actual.write_text('v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\nf 1 2 3 4\n', encoding='utf-8')
        self.digest = hashlib.sha256(self.actual.read_bytes()).hexdigest()
        self.source = self.root / 'sources.csv'
        fields = ['thingi10k_file_id','literature_cohort','raw_stl_audit_executed',
                  'source_stl_sha256','source_zip_git_blob_sha1','conditional_source_surface_genus']
        with self.source.open('w', newline='', encoding='utf-8') as out:
            w = csv.DictWriter(out, fieldnames=fields); w.writeheader()
            for i in range(23):
                w.writerow(dict(thingi10k_file_id=58012 if i == 0 else 100000+i,
                    literature_cohort='QUADWILD_FIG29' if i == 0 else 'BADIA_FIG10_TABLE1',
                    raw_stl_audit_executed='YES' if i == 0 else 'NO',
                    source_stl_sha256=SOURCE if i == 0 else '',
                    source_zip_git_blob_sha1='a'*40 if i == 0 else '',
                    conditional_source_surface_genus='41' if i == 0 else ''))
        self.paper = self.root / 'paper.csv'
        with self.paper.open('w', newline='', encoding='utf-8') as out:
            w = csv.DictWriter(out, fieldnames=['thingi10k_file_id','literature_cohort',
                                               'published_quad_vertices','published_quad_faces']); w.writeheader()
            for i in range(12):
                w.writerow(dict(thingi10k_file_id=58012 if i == 0 else 200000+i,
                    literature_cohort='QUADWILD_FIG29',
                    published_quad_vertices=113799 if i == 0 else 10,
                    published_quad_faces=113879 if i == 0 else 12))
        self.extract = self.root / 'f19.json'
        self.f18 = self.root / 'f18.json'
        self.extdata = dict(schema='apmesh-quadwild-f19-range-index-v1',
            status='ONE_ORIGINAL_OUTPUT_MEMBER_EXTRACTED_NOT_PAIR_VERIFIED',
            original_thin_archive_url=AUTHOR_ARCHIVE_URL, thingi10k_file_id=58012,
            selected_member='quads/58012_output.obj',
            candidate_members=[{'name':'quads/58012_output.obj'}],
            output_local_file=str(self.actual),
            selected_member_original_sha256=self.digest,
            selected_member_original_bytes=self.actual.stat().st_size,
            source_output_pair_verified=False, matched_published_quad_output=False)
        self.f18data = dict(file_id=58012, actual_quad_sha256=self.digest,
            original_stl_sha256=SOURCE, published_vertex_face_counts_match=False,
            reference_pair_accepted_for_fair_comparison=False,
            raw_quad_topology=dict(vertices=4,quad_faces=1,closed_connected_orientable_combinatorial=False,
                                   singular_vertex_links=0,orientation_conflicts=0,face_components=1,
                                   genus_if_valid=None), reference_topology_screen_passed=False)
        self.save()

    def save(self):
        self.extract.write_text(json.dumps(self.extdata), encoding='utf-8')
        self.f18.write_text(json.dumps(self.f18data), encoding='utf-8')

    def runcheck(self):
        self.save()
        return check(58012, self.source, self.paper, self.extract, self.f18, self.actual)

    def test_01_negative_reference_never_admitted(self):
        r = self.runcheck()
        self.assertTrue(r['f18_raw_quad_topology_claim_cross_checked'])
        self.assertFalse(r['published_count_parity'])
        self.assertFalse(r['scientific_reference_pair_admitted'])
        self.assertFalse(r['comparison_with_apmesh_permitted'])

    def test_02_bad_extracted_file_sha_rejected(self):
        self.actual.write_text(self.actual.read_text()+'# changed\n')
        with self.assertRaisesRegex(ValueError, 'SHA-256'): self.runcheck()

    def test_03_wrong_member_id_rejected(self):
        self.extdata['selected_member'] = '580123_output.obj'
        self.extdata['candidate_members'] = [{'name':'580123_output.obj'}]
        with self.assertRaisesRegex(ValueError, 'exact model ID'): self.runcheck()

    def test_04_ambiguous_index_member_rejected(self):
        self.extdata['candidate_members'].append(dict(name=self.extdata['selected_member']))
        with self.assertRaisesRegex(ValueError, 'not unique'): self.runcheck()

    def test_05_wrong_original_source_sha_rejected(self):
        self.f18data['original_stl_sha256'] = 'f'*64
        with self.assertRaisesRegex(ValueError, 'frozen F17'): self.runcheck()

    def test_06_wrong_author_url_rejected(self):
        self.extdata['original_thin_archive_url'] = 'https://attacker.invalid/fake.zip'
        with self.assertRaisesRegex(ValueError, 'authors archive'): self.runcheck()

    def test_07_no_extraction_status_rejected(self):
        self.extdata['status'] = 'REMOTE_ZIP_CENTRAL_DIRECTORY_INSPECTED_ONLY'
        with self.assertRaisesRegex(ValueError, 'does not attest extraction'): self.runcheck()

    def test_08_mismatched_f18_sha_rejected(self):
        self.f18data['actual_quad_sha256'] = 'f'*64
        with self.assertRaisesRegex(ValueError, 'different output file hash'): self.runcheck()

    def test_09_false_paper_count_flag_rejected(self):
        self.f18data['published_vertex_face_counts_match'] = True
        with self.assertRaisesRegex(ValueError, 'parity flag'): self.runcheck()

    def test_10_false_topology_flag_rejected(self):
        self.f18data['reference_topology_screen_passed'] = True
        with self.assertRaisesRegex(ValueError, 'screening flag'): self.runcheck()

    def test_11_wrong_saved_output_path_rejected(self):
        self.extdata['output_local_file'] = str(self.root/'another.obj')
        with self.assertRaisesRegex(ValueError, 'not the F19 extracted file'): self.runcheck()

    def test_12_missing_f18_receipt_rejected(self):
        self.f18.unlink()
        with self.assertRaisesRegex(ValueError, 'Missing/oversized receipt'):
            check(58012,self.source,self.paper,self.extract,self.f18,self.actual)

    def test_13_unreviewed_source_rejected(self):
        self.source.write_text(self.source.read_text().replace('QUADWILD_FIG29,YES,','QUADWILD_FIG29,NO,'))
        with self.assertRaisesRegex(ValueError, 'not been audited'): self.runcheck()

    def test_14_rights_and_independent_pair_never_inferred(self):
        r=self.runcheck()
        self.assertFalse(r['independent_author_input_to_output_pair_provenance_verified'])
        self.assertFalse(r['per_asset_source_and_output_redistribution_rights_cleared'])
        self.assertFalse(r['paper_quality_metrics_independently_recomputed'])
        self.assertFalse(r['apmesh_matched_input_tri_quad_executed'])

    def test_15_wrong_f18_case_rejected(self):
        self.f18data['file_id']=67792
        with self.assertRaisesRegex(ValueError, 'different model ID'):self.runcheck()

    def test_16_traversal_member_rejected(self):
        self.extdata['selected_member'] = '../58012_output.obj'
        self.extdata['candidate_members'] = [{'name':'../58012_output.obj'}]
        with self.assertRaisesRegex(ValueError, 'Unsafe'):self.runcheck()

    def test_17_missing_frozen_paper_row_rejected(self):
        content=self.paper.read_text().splitlines()
        self.paper.write_text('\n'.join([content[0]]+content[2:])+'\n')
        with self.assertRaisesRegex(ValueError, 'twelve'): self.runcheck()

    def test_18_f18_pretend_admission_rejected(self):
        self.f18data['reference_pair_accepted_for_fair_comparison']=True
        with self.assertRaisesRegex(ValueError, 'incorrectly claims pair admission'): self.runcheck()


if __name__ == '__main__':
    unittest.main()
