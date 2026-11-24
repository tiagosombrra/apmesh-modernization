#!/usr/bin/env python3
"""Directed S40-F9 tests: pinned private source, exact J, adverse failure modes."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

import s40f8_exact_planar_jacobian as exact
import s40f9_independent_certificate as independently
import s40f9_regularized_source_island as new
import s40f9_native_join_gate as join
import s40f7_parent_lineage_rebase as f7


class PublicMathAndGateTests(unittest.TestCase):
    def test_budget_is_not_relaxed(self):
        self.assertEqual(new.BUDGET_MM,0.001)
        self.assertEqual(new.INWARD_HANDLE_BIAS_MM,0.0001)

    def test_source_registration_cardinality(self):
        self.assertEqual(len(new.PARENT_INTERFACE_SOURCE_KEYS),8)
        self.assertEqual(set(new.CIRCULAR_SOURCE_EDGES),{1307,1336,1415,1444})
        self.assertEqual(len(new.FACES),8)

    def test_original_pilot_stays_byte_pinned(self):
        self.assertEqual(new.F6_SHA,exact.F6_SHA256)
        self.assertEqual(new.F6_SHA,independently.FROZEN_F6_SHA)
        self.assertEqual(join.f7.S3Y_SHA,'af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177')

    def test_f9_digest_and_structural_schema_are_explicit(self):
        self.assertEqual(independently.F9_SHA,'328ff1ca784b4a82d2bd566309c21d7263cc5134ae37e7b1f4554acd7fd26e38')
        self.assertNotEqual(independently.F9_SHA,new.F6_SHA)

    def test_tampered_f6_is_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'SHA-256 mismatch'):
            exact.audit_f6(b'v 1 1 1\n')

    def test_no_parent_native_gate_accepts_without_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                join.private_f9_native_trial(original_step_path=Path(tmp)/'absent.step',
                    s3y_bp_path=Path(tmp)/'absent_s3y.bp',
                    original_f6_bp_path=Path(tmp)/'f6.bp',
                    original_f6_manifest_path=Path(tmp)/'f6.json',
                    f9_bp_path=Path(tmp)/'f9.bp',
                    f9_manifest_path=Path(tmp)/'f9.json',
                    original_f5_spec_path=Path(tmp)/'f5.json',
                    original_f6_spec_path=Path(tmp)/'f6spec.json')

    def test_no_source_fails_preflight_without_creating_bp(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=subprocess.run([sys.executable,join.__file__,
                '--original-step',str(Path(tmp)/'unavailable.step'),
                '--s3y-bp',str(Path(tmp)/'missing.bp'),
                '--original-f6-bp',str(Path(tmp)/'missing_f6.bp'),
                '--original-f6-manifest',str(Path(tmp)/'missing_f6.json'),
                '--f9-bp',str(Path(tmp)/'missing_f9.bp'),
                '--f9-manifest',str(Path(tmp)/'missing_f9.json'),
                '--original-f5-spec',str(Path(tmp)/'missing_f5.json'),
                '--original-f6-spec',str(Path(tmp)/'missing_f6spec.json'),
                '--output-dir',str(Path(tmp)/'output')],capture_output=True,text=True)
            self.assertEqual(result.returncode,3)
            self.assertIn('BLOCKED_NO_NATIVE_ADMISSION',result.stderr)
            self.assertFalse((Path(tmp)/'output').exists())

    def test_no_source_fails_f9_builder_without_creating_bp(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=subprocess.run([sys.executable,new.__file__,
                '--f6-bp',str(Path(tmp)/'missing.bp'),
                '--f6-manifest',str(Path(tmp)/'missing.json'),
                '--f5-source-spec',str(Path(tmp)/'f5.json'),
                '--f6-source-spec',str(Path(tmp)/'f6.json'),
                '--output-dir',str(Path(tmp)/'output')],capture_output=True,text=True)
            self.assertEqual(result.returncode,3)
            self.assertIn('candidate_emitted": false',result.stderr)
            self.assertFalse((Path(tmp)/'output').exists())

    def test_independent_rejects_altered_candidate_without_geometry(self):
        with self.assertRaisesRegex(ValueError,'Wrong original immutable'):
            independently.audit_candidate_independent(b'invalid',b'invalid',{}, {})


class PrivatePinnedF9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names=['APMESH_S40F9_F6_BP','APMESH_S40F9_F6_RECEIPT',
               'APMESH_S40F9_F5_SPEC','APMESH_S40F9_F6_SPEC']
        if any(not os.environ.get(name) for name in names):
            raise unittest.SkipTest('Four private S40-F9 source prerequisites are not available')
        cls.original=Path(os.environ[names[0]]).read_bytes()
        cls.receipt=json.loads(Path(os.environ[names[1]]).read_bytes())
        cls.f5_source=Path(os.environ[names[2]]).read_bytes()
        cls.f6_source=Path(os.environ[names[3]]).read_bytes()
        cls.candidate,cls.manifest=new.regularize_frozen_f6(cls.original,cls.receipt,
                                                             cls.f5_source,cls.f6_source)
        cls.candidate_bytes=cls.candidate.encode()
        cls.old_points,cls.old_patches=exact.parse_decimal_bp(cls.original)
        cls.new_points,cls.new_patches=exact.parse_decimal_bp(cls.candidate_bytes)

    def test_original_f6_still_fails_three_exact_jacobians(self):
        proof=exact.audit_f6(self.original)
        self.assertEqual([r['patch_index'] for r in proof['certificates']
                          if r['classification']!='CERTIFIED_STRICT_POSITIVE'],[0,1,3])

    def test_f9_new_candidate_sha_is_frozen(self):
        self.assertEqual(sha256(self.candidate_bytes).hexdigest(),independently.F9_SHA)

    def test_unchanged_eight_indexed_patch_nets_and_control_count(self):
        self.assertEqual((len(self.new_points),len(self.new_patches)),(104,8))
        self.assertEqual(self.new_patches,self.old_patches)

    def test_four_circular_source_owners_are_present(self):
        self.assertTrue(all('old:'+str(k) in self.receipt['source_segment_ids']
                            for k in (1307,1336,1415,1444)))

    def test_eight_inherited_parent_interfaces_unchanged(self):
        for key in new.PARENT_INTERFACE_SOURCE_KEYS:
            for i in self.receipt['source_segment_ids'][key]:
                self.assertEqual(self.old_points[i],self.new_points[i])

    def test_unrelated_control_indices_and_source_vertices_preserved(self):
        edited=set(self.manifest['edited_circular_handle_control_ids']+
                   self.manifest['recomputed_coons_interior_control_ids'])
        self.assertEqual(len(edited),24)
        self.assertTrue(all(self.old_points[i]==self.new_points[i]
                            for i in range(104) if i not in edited))

    def test_only_four_circle_curves_receive_new_tangent_controls(self):
        edited=set(self.manifest['edited_circular_handle_control_ids'])
        self.assertEqual(len(edited),8)
        for eid in (1307,1336,1415,1444):
            ids=self.receipt['source_segment_ids']['old:'+str(eid)]
            self.assertTrue(set(ids[1:3]).issubset(edited))
            self.assertTrue(all(self.new_points[i]==self.old_points[i] for i in (ids[0],ids[-1])))

    def test_all_eight_strict_bernstein_certificates(self):
        for pid,patch in enumerate(self.new_patches):
            J=exact.jacobian_net(self.new_points,patch,
                                 exact.NORMALS[exact.FACE_IDS[pid]])
            certificate=exact.certify_strict_sign(J)
            self.assertEqual(certificate['status'],'CERTIFIED_POSITIVE',str(pid))
            self.assertGreater(certificate['strict_lower_bound_mm2'],0)

    def test_every_source_side_and_seam_index_preserved(self):
        points=[tuple(map(float,p)) for p in self.new_points]
        stats=new._indexed_side_audit(points,self.new_patches,
                                       self.receipt['source_segment_ids'])
        self.assertEqual((stats['two_sided_indexed_seams'],
                          stats['open_registered_source_sides']),(6,20))

    def test_deterministic_rebuild_bytes_identical(self):
        again,_=new.regularize_frozen_f6(self.original,self.receipt,
                                         self.f5_source,self.f6_source)
        self.assertEqual(again,self.candidate)

    def test_independent_verifier_accepts_regularized_BP(self):
        proof=independently.audit_candidate_independent(
            self.original,self.candidate_bytes,self.receipt,self.manifest)
        self.assertEqual(proof['strict_positive_full_domain_count'],8)
        self.assertTrue(proof['eight_previous_parent_source_interfaces_numerically_unchanged'])

    def test_independent_verifier_rejects_modified_manifest(self):
        bad=deepcopy(self.manifest)
        bad['source_segment_ids']['old:1307'][1]=73
        with self.assertRaises(ValueError):
            independently.audit_candidate_independent(
                self.original,self.candidate_bytes,self.receipt,bad)

    def test_independent_verifier_rejects_altered_BP(self):
        changed=self.candidate_bytes.replace(b'v ',b'v  ',1)
        self.assertNotEqual(changed,self.candidate_bytes)
        with self.assertRaisesRegex(ValueError,'Wrong F9 candidate BP digest'):
            independently.audit_candidate_independent(
                self.original,changed,self.receipt,self.manifest)

    def test_fail_closed_on_manipulated_source_geometry(self):
        changed=self.f5_source+b'\n'
        with self.assertRaisesRegex(ValueError,'Pinned F5 source geometry'):
            new.regularize_frozen_f6(self.original,self.receipt,changed,self.f6_source)

    def test_fail_closed_on_modified_vertical_geometry(self):
        with self.assertRaisesRegex(ValueError,'Pinned F6 source geometry'):
            new.regularize_frozen_f6(self.original,self.receipt,self.f5_source,
                                     self.f6_source+b'\n')

    def test_fail_closed_on_changed_step_identity(self):
        modified=deepcopy(self.receipt)
        modified['step_original_sha256_reference']='different'
        with self.assertRaisesRegex(ValueError,'Frozen source island manifest'):
            new.regularize_frozen_f6(self.original,modified,self.f5_source,self.f6_source)

    def test_fail_closed_on_changed_experimental_bias(self):
        with self.assertRaisesRegex(ValueError,'Experimental F9 inward bias'):
            new.regularize_frozen_f6(self.original,self.receipt,self.f5_source,
                                     self.f6_source,bias_mm=.0002)

    def test_fail_closed_on_tampered_frozen_f6(self):
        with self.assertRaisesRegex(ValueError,'F6 frozen BP source digest'):
            new.regularize_frozen_f6(self.original+b'\n',self.receipt,self.f5_source,self.f6_source)

    def test_four_source_native_surrogates_and_arc_distance(self):
        with tempfile.TemporaryDirectory() as d:
            f5=Path(d)/'f5.json';f5.write_bytes(self.f5_source)
            f6=Path(d)/'f6.json';f6.write_bytes(self.f6_source)
            result=new.audit_candidate(self.candidate_bytes,self.original,self.receipt,f5,f6)
        self.assertEqual(result['strictly_positive_entire_domain_patch_count'],8)
        self.assertEqual(sum(x['interior_IN'] for x in result['native_surrogate_by_face'].values()),1800)
        self.assertEqual(sum(x['boundary_IN_or_ON'] for x in result['native_surrogate_by_face'].values()),1632)
        self.assertEqual(sum(x['boundary_OUT'] for x in result['native_surrogate_by_face'].values()),0)
        self.assertLess(max(x['relative_area_difference'] for x in result['native_surrogate_by_face'].values()),1e-4)
        self.assertLess(max(max(v['max_sampled_bp_to_original_analytic_edge_mm'],
                                v['max_sampled_original_analytic_edge_to_bp_mm'])
                            for v in result['four_source_arc_radial_certificates']),.001)
        self.assertEqual(result['new_source_faces_native_admitted'],0)

    def test_regularized_candidate_rejected_if_bytes_do_not_match_producer(self):
        with tempfile.TemporaryDirectory() as d:
            f5=Path(d)/'f5.json';f5.write_bytes(self.f5_source)
            f6=Path(d)/'f6.json';f6.write_bytes(self.f6_source)
            changed=self.candidate_bytes+b'\n'
            with self.assertRaisesRegex(ValueError,'Candidate BP differs'):
                new.audit_candidate(changed,self.original,self.receipt,f5,f6)

    def test_unavailable_parent_is_still_blocked_before_native_import(self):
        with tempfile.TemporaryDirectory() as d:
            orig=Path(d)/'step.step';orig.write_bytes(b'not original')
            for name in ('parent.bp','original.bp','parent.json','f9.bp','f9.json','f5.json','f6.json'):
                (Path(d)/name).write_bytes(b'not original')
            with self.assertRaisesRegex(ValueError,'Original source STEP digest'):
                join.private_f9_native_trial(original_step_path=orig,
                    s3y_bp_path=Path(d)/'parent.bp',
                    original_f6_bp_path=Path(d)/'original.bp',
                    original_f6_manifest_path=Path(d)/'parent.json',
                    f9_bp_path=Path(d)/'f9.bp',
                    f9_manifest_path=Path(d)/'f9.json',
                    original_f5_spec_path=Path(d)/'f5.json',
                    original_f6_spec_path=Path(d)/'f6.json')


if __name__=='__main__':
    unittest.main()
