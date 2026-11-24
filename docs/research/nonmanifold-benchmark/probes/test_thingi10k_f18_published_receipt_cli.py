"""Fail-closed tests for publishing frozen QuadWild source/paper count receipts."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from thingi10k_f18_published_receipt_cli import pinned_git_blob, recalculate, CATALOG_GIT_BLOB
from test_thingi10k_f18_quad_reference_gate import make_roster, catalog


def hash_git(blob: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()


class SourcePreflightTests(unittest.TestCase):
    def test_01_pinned_blob_validates_exact_original_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{}\n')
            self.assertEqual(pinned_git_blob(p, hash_git(p.read_bytes())),p.read_bytes())
    def test_02_corrupt_source_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json';p.write_text('{}\n')
            with self.assertRaises(ValueError):pinned_git_blob(p,'0'*40)
    def test_03_missing_source_fails(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):pinned_git_blob(Path(d)/'missing','0'*40)
    def test_04_catalog_provenance_immutable(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            roster=folder/'roster.csv';make_roster(roster)
            c=folder/'subset.json';c.write_text(json.dumps({'catalog_git_blob_sha1':'0'*40,'source_records':catalog()})+'\n')
            f=folder/'f17.json';f.write_text(json.dumps({'raw_stl_audits':[{}]*7})+'\n')
            with self.assertRaisesRegex(ValueError,'Wrong upstream'):
                recalculate(roster,c,f,expected_roster=hash_git(roster.read_bytes()),expected_catalog=hash_git(c.read_bytes()),expected_f17=hash_git(f.read_bytes()))

    def test_05_end_to_end_synthetic_current_published_contract(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);roster=folder/'roster.csv';make_roster(roster)
            original_catalog=catalog()
            for row in original_catalog:
                if row['id']==61394:
                    row['faces']=6747
                    row['vertices']=3367
            c=folder/'catalog.json';c.write_text(json.dumps({'catalog_git_blob_sha1':CATALOG_GIT_BLOB,
                'frozen_quadwild_model_ids':[44503,128001,58012,61394,67792,69975,81877,94884,230923,364256,423069,498974],
                'source_records':original_catalog})+'\n')
            sample={'thingi10k_file_id':58012,'raw_stl_sha256':'2c7c322af76b46a307e67af451ebba9e6609e6932a2829f4c596853dbf122d4b',
                'topology':dict(source_unique_exact_vertices=9090,source_unique_exact_edges=27510,
                    source_triangles=18340,boundary_edges=0,three_plus_edges=0,
                    vertex_link_singular=0,vertex_connected_components=1,
                    zero_area_triangles=0,raw_duplicate_triangles=0,edge_winding_conflicts=0)}
            dummy=[dict(thingi10k_file_id=x,topology={}) for x in (293137,37881,47076,550964,96457)]
            dummy.append({'thingi10k_file_id':61394,
              'raw_stl_sha256':'7a614a8d71b65cae465868a6c7f3800e44b4c4a79d56aa58e6b501a58bff8c3c',
              'topology':dict(source_unique_exact_vertices=3367,source_unique_exact_edges=10127,
                      source_triangles=6747,boundary_edges=87,three_plus_edges=61,
                      vertex_link_singular=86,vertex_connected_components=4,
                      zero_area_triangles=72,raw_duplicate_triangles=1,edge_winding_conflicts=0)})
            f=folder/'f17.json';f.write_text(json.dumps({'raw_stl_audits':[sample,*dummy]})+'\n')
            x=recalculate(roster,c,f,expected_roster=hash_git(roster.read_bytes()),
                expected_catalog=hash_git(c.read_bytes()),expected_f17=hash_git(f.read_bytes()))
            self.assertEqual(x['source_vs_published_euler_conditional_matches'],4)
            self.assertEqual(x['original_stl_audited_and_source_euler_match_count'],1)
            self.assertFalse(x['source_vs_output_homeomorphism_demonstrated'])

    def test_06_wrong_roster_and_catalog_order_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);roster=folder/'roster.csv';make_roster(roster)
            c=folder/'catalog.json';c.write_text(json.dumps({'catalog_git_blob_sha1':CATALOG_GIT_BLOB,
                'frozen_quadwild_model_ids':list(reversed([44503,128001,58012,61394,67792,69975,81877,94884,230923,364256,423069,498974])),
                'source_records':catalog()})+'\n')
            f=folder/'f17.json';f.write_text(json.dumps({'raw_stl_audits':[{}]*7})+'\n')
            with self.assertRaisesRegex(ValueError,'order'):
                recalculate(roster,c,f,expected_roster=hash_git(roster.read_bytes()),
                    expected_catalog=hash_git(c.read_bytes()),expected_f17=hash_git(f.read_bytes()))


if __name__=='__main__':
    unittest.main()
