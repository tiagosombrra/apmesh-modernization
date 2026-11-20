"""Directed fail-closed source/native admission tests for original S40 #1519."""
from __future__ import annotations

import copy
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest

import cadquery as cq

from audit_analytic_bp import read_bp
from s3c_step_source_gate import SOURCES, parse_entities, entity
from s3o_s40_spline_trim import (
    FACE, ORIGINAL_BSPLINE_EDGES, PREEXISTING_SEAMS, EXPECTED_SOURCE_EDGES,
    _cells, _pcurve, _area_check, source_partition, build_extension,
    audit_original, _native_edge_correspondence,
)


class OriginalS40SplineTrimGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        src = Path(os.environ.get('APMESH_ORIGINAL_CAD_DIR', '.'))
        cls.path = src / SOURCES['S40'][0]
        if not cls.path.exists():
            raise unittest.SkipTest('Pinned original S40 STEP not available')
        cls.source = cls.path.read_text('utf-8')
        cls.sha = sha256(cls.path.read_bytes()).hexdigest()
        if cls.sha != SOURCES['S40'][1]:
            raise ValueError('Original S40 source failed frozen byte hash')
        cls.native = cq.importers.importStep(str(cls.path)).val()
        pkg = Path(__file__).resolve().parents[1]
        cls.baseline_bp = (pkg / 'private_bp/s40_step1986.partial.bp').read_text('utf-8')
        cls.baseline_manifest = json.loads((pkg / 'private_bp/s40_step1986_manifest.json').read_text('utf-8'))
        cls.part = source_partition(cls.source)
        cls.bp,cls.manifest = build_extension(cls.source,cls.baseline_bp,cls.baseline_manifest,middle_sectors=7)
        cls.audit = audit_original(cls.source,cls.native,cls.baseline_bp,cls.baseline_manifest,cls.bp,cls.manifest)

    def test_hash_and_original_cad_census(self):
        self.assertEqual(self.sha, 'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b')
        self.assertEqual(len(self.native.Faces()),43)
        self.assertEqual(FACE,1519)

    def test_source_splines_and_pcurves_are_independently_identified(self):
        self.assertEqual(tuple(self.part['source_wire_original_edge_ids']), EXPECTED_SOURCE_EDGES)
        records={x['edge_id']:x for x in self.part['source_edges']}
        self.assertEqual({e for e,r in records.items() if r['curve_type_3d']=='B_SPLINE_CURVE_WITH_KNOTS'},set(ORIGINAL_BSPLINE_EDGES))
        self.assertEqual(records[85]['pcurve_control_count'],47)
        self.assertEqual(records[1644]['pcurve_control_count'],47)
        self.assertEqual(records[85]['pcurve_type'],'BSPLINE_DEGREE_3')
        self.assertEqual(records[1523]['pcurve_type'],'BSPLINE_DEGREE_1')

    def test_original_source_uv_rectangle_union(self):
        self.assertEqual(len(self.part['original_vertices']),8)
        self.assertEqual(len(_cells(self.part,7)),16)
        self.assertGreater(_area_check(self.part,7),0)
        self.assertEqual(self.part['frame']['radius'],16.)

    def test_partial_original_bp_extension(self):
        self.assertEqual(self.manifest['baseline_patch_count'],43)
        self.assertEqual(self.manifest['added_patch_count'],16)
        self.assertEqual(self.manifest['combined_patch_count'],59)
        self.assertEqual(self.manifest['combined_control_count'],681)
        self.assertEqual(len(read_bp(self.bp)[1]),59)

    def test_all_internal_seams_use_same_integer_controls(self):
        self.assertEqual(self.manifest['internal_new_seams'],21)
        self.assertEqual(self.audit['derived_seams_verified'],21)

    def test_original_planar_feature_identity_is_reused(self):
        self.assertEqual(set(self.audit['preexisting_planar_shared_edges_verified']),set(PREEXISTING_SEAMS))
        for eid in PREEXISTING_SEAMS:
            for index in (1,2):
                key=f'edge:{eid}:{index}'
                self.assertEqual(self.manifest['original_global_source_key_to_control_index'][key],
                                 self.baseline_manifest['original_global_source_key_to_control_index'][key])

    def test_unique_source_to_native_boundary_identity(self):
        native_indices=self.audit['native_original_boundary_edges']
        self.assertEqual(len(native_indices),8)
        self.assertEqual(len({entry['native_topods_edge_index'] for entry in native_indices}),8)
        self.assertTrue(all(len(e['original_step_owner_face_ids'])==2 and FACE in e['original_step_owner_face_ids']
                            and len(e['native_incident_face_indices'])==2 for e in native_indices))

    def test_every_original_curve_boundary_piece_is_covered(self):
        source={e['original_edge_curve_id']:e for e in self.audit['native_original_boundary_edges']}
        self.assertEqual(source[85]['boundary_sample_count'],63)
        self.assertEqual(source[1644]['boundary_sample_count'],81)
        self.assertEqual(sum(e['boundary_sample_count'] for e in source.values()),198)
        self.assertLess(source[85]['max_native_edge_distance_mm'],.001)
        self.assertLess(source[1644]['max_native_edge_distance_mm'],.001)

    def test_actual_native_trim_uv_classification(self):
        self.assertEqual(self.audit['native_interior_sample_count'],16*81)
        self.assertEqual(self.audit['native_boundary_sample_count'],16*44)
        self.assertEqual(self.audit['native_trim_classification_histogram']['INTERIOR_IN'],1296)
        self.assertEqual(sum(v for k,v in self.audit['native_trim_classification_histogram'].items()
                             if k.startswith('BOUNDARY_')),704)

    def test_radial_bernstein_and_native_spline_budget_pass(self):
        self.assertLess(self.audit['max_guarded_radial_support_error_mm'],.001)
        self.assertLess(self.audit['max_native_original_edge_sampled_distance_mm'],.001)
        self.assertLess(self.audit['max_native_cylinder_sampled_projection_error_mm'],.001)

    def test_six_sectors_fail_before_admission(self):
        bp,meta=build_extension(self.source,self.baseline_bp,self.baseline_manifest,middle_sectors=6)
        with self.assertRaisesRegex(ValueError,'Bernstein radial enclosure exceeds'):
            audit_original(self.source,self.native,self.baseline_bp,self.baseline_manifest,bp,meta)

    def test_original_source_hash_rejects_modified_bytes(self):
        with self.assertRaisesRegex(ValueError,'SHA-256'):
            source_partition(self.source.replace('ISO-10303-21;','ISO-10303-22;',1))

    def test_pilot_budget_cannot_be_relaxed(self):
        with self.assertRaisesRegex(ValueError,'pilot budget'):
            build_extension(self.source,self.baseline_bp,self.baseline_manifest,middle_sectors=7,declared_budget_mm=.002)
        with self.assertRaisesRegex(ValueError,'Pilot budget'):
            audit_original(self.source,self.native,self.baseline_bp,self.baseline_manifest,self.bp,self.manifest,declared_budget_mm=.002)

    def test_forged_manifest_rejected_even_with_hash(self):
        damaged=copy.deepcopy(self.manifest)
        damaged['original_3d_spline_edge_ids']=[85,1616]
        with self.assertRaisesRegex(ValueError,'recomputation mismatch'):
            audit_original(self.source,self.native,self.baseline_bp,self.baseline_manifest,self.bp,damaged)

    def test_forged_bp_payload_rejected_even_if_new_hash_supplied(self):
        lines=self.bp.splitlines(keepends=True)
        i=next(i for i,line in enumerate(lines) if line.startswith('v '))
        lines[i]=lines[i].replace('v ','v 999 ',1)
        modified=''.join(lines)
        damaged=copy.deepcopy(self.manifest)
        damaged['combined_bp_sha256']=sha256(modified.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,'recomputation mismatch'):
            audit_original(self.source,self.native,self.baseline_bp,self.baseline_manifest,modified,damaged)

    def test_missing_or_ambiguous_native_edges_rejected(self):
        fake=cq.Workplane('XY').box(1,1,1).val()
        with self.assertRaises(ValueError):
            _native_edge_correspondence(self.part,parse_entities(self.source),fake,0)

    def test_spline_nonmonotone_controls_fail_closed(self):
        table=parse_entities(self.source)
        t,c=table[143]
        bad=c.replace('#144,#145,#146', '#144,#146,#145',1)
        table[143]=(t,bad)
        with self.assertRaisesRegex(ValueError,'Nonmonotone'):
            _pcurve(table,85,self.part['frame']['id'])


if __name__=='__main__':
    unittest.main()
