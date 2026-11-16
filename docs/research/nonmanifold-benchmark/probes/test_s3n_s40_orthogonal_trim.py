"""Directed original-S40 native tests for the bounded S3.N #1986 partition."""
from __future__ import annotations

import copy
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest

import cadquery as cq

from audit_analytic_bp import read_bp
from s3c_step_source_gate import SOURCES, parse_entities
from s3j_radial_support_enclosure import certify_patch
from s3l_s40_partial_cylinder_atlas import construct_partial
from s3n_s40_orthogonal_trim import (
    FACE, SOURCE_CIRCLES, SOURCE_GENERATORS, _boundary_coverage_and_distance,
    _native_original_edges, _parametric_partition_proof, audit_original,
    angular_grid, build_extension, rectangle_cells, source_partition,
)


class OriginalS40OrthogonalTrimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = Path(os.environ.get('APMESH_ORIGINAL_CAD_DIR', '.'))
        cls.step = folder / SOURCES['S40'][0]
        if not cls.step.is_file():
            raise unittest.SkipTest('Pinned original S40 STEP absent; set APMESH_ORIGINAL_CAD_DIR')
        cls.source = cls.step.read_text('utf-8')
        cls.digest = sha256(cls.step.read_bytes()).hexdigest()
        if cls.digest != SOURCES['S40'][1]:
            raise ValueError('S3.N source archive does not match frozen raw SHA-256')
        cls.native = cq.importers.importStep(str(cls.step)).val()
        cls.original = source_partition(cls.source)
        cls.base_bp, cls.base_manifest = construct_partial(
            cls.source,cls.native,model='S40',source_sha256=cls.digest,
            sectors=4,sampled_budget_mm=.001)
        cls.bp,cls.manifest=build_extension(
            cls.source,cls.base_bp,cls.base_manifest,middle_sectors=8)
        cls.audit=audit_original(cls.source,cls.native,cls.base_bp,cls.base_manifest,
                                 cls.bp,cls.manifest,declared_budget_mm=.001)

    def test_original_source_hash_is_pinned(self):
        self.assertEqual(self.digest,'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b')

    def test_source_curve_census_recovered_without_welding(self):
        self.assertEqual(set(self.original['source_expected_edge_ids']),set(SOURCE_GENERATORS)|set(SOURCE_CIRCLES))
        self.assertEqual(len(self.original['original_vertices']),8)
        self.assertEqual(len(self.original['source_wire_uv']),8)

    def test_source_uv_is_one_stepped_polygon(self):
        u=self.original['u_breaks'];z=self.original['v_breaks']
        self.assertEqual(len(u),4)
        self.assertEqual(len(z),3)
        self.assertTrue(u[0]<u[1]<u[2]<u[3])
        self.assertTrue(z[0]<z[1]<z[2])

    def test_rectangle_partition_exact_area_and_no_overlap(self):
        record=_parametric_partition_proof(self.original,8)
        self.assertAlmostEqual(record['source_polygon_area_parametric'],record['partition_area_parametric'],places=9)
        self.assertEqual(len(rectangle_cells(self.original,8)),18)

    def test_patch_and_control_census(self):
        self.assertEqual(self.manifest['baseline_patch_count'],25)
        self.assertEqual(self.manifest['added_patch_count'],18)
        self.assertEqual(self.manifest['combined_patch_count'],43)
        self.assertEqual(self.manifest['combined_control_count'],511)
        self.assertEqual(len(angular_grid(self.original,8)),11)

    def test_24_internal_seams_are_shared_by_integer_identity(self):
        self.assertEqual(self.manifest['derived_internal_indexed_seam_count'],24)
        self.assertEqual(self.audit['derived_indexed_internal_seams'],24)

    def test_source_to_native_original_eight_edges_are_distinct(self):
        rows=self.audit['original_native_boundary_edges_in_source']
        self.assertEqual(len(rows),8)
        self.assertEqual(len({r['native_topods_edge_index'] for r in rows}),8)
        self.assertTrue(all(len(r['native_incident_face_indices'])==2 for r in rows))

    def test_all_eight_original_boundaries_covered(self):
        coverage=self.audit['original_boundary_curve_coverage']
        self.assertEqual(len(coverage),8)
        byid={r['original_source_edge_curve_id']:r for r in coverage}
        self.assertEqual(byid[1991]['indexed_boundary_subsegments'],10)
        self.assertEqual(byid[2042]['indexed_boundary_subsegments'],8)
        self.assertEqual(byid[1962]['indexed_boundary_subsegments'],1)
        self.assertEqual(byid[1834]['indexed_boundary_subsegments'],1)
        self.assertLess(self.audit['maximum_native_original_boundary_sampled_distance_mm'],.001)

    def test_original_planar_shared_edge_controls_preserved(self):
        witnesses=self.audit['source_planar_native_shared_edges_checked']
        self.assertEqual({r['original_edge_curve_id'] for r in witnesses},{2019,2071})
        for row in witnesses:
            self.assertEqual(len(row['shared_source_control_ids']),4)
            self.assertTrue(all(i<320 for i in row['shared_source_control_ids']))

    def test_native_trim_membership_samples(self):
        self.assertEqual(self.audit['native_trim_interior_samples'],18*81)
        self.assertEqual(self.audit['native_trim_boundary_samples'],18*44)
        self.assertEqual(self.audit['native_trim_sampled_gate'],'PASS')

    def test_radial_support_and_original_edge_distance_both_pass(self):
        self.assertLess(self.audit['max_guarded_bernstein_radial_support_error_mm'],.001)
        self.assertLess(self.audit['max_native_projected_distance_mm'],.001)
        self.assertLess(self.audit['maximum_native_original_boundary_sampled_distance_mm'],.001)

    def test_seven_central_sectors_not_admitted(self):
        candidate,manifest=build_extension(self.source,self.base_bp,self.base_manifest,middle_sectors=7)
        with self.assertRaisesRegex(ValueError,'radial enclosure exceeds budget'):
            audit_original(self.source,self.native,self.base_bp,self.base_manifest,
                           candidate,manifest,declared_budget_mm=.001)

    def test_original_source_text_change_rejected(self):
        with self.assertRaisesRegex(ValueError,'SHA-256'):
            source_partition(self.source.replace('ISO-10303-21;','ISO-10303-22;',1))

    def test_wrong_pilot_budget_rejected(self):
        with self.assertRaises(ValueError):
            build_extension(self.source,self.base_bp,self.base_manifest,
                            middle_sectors=8,declared_budget_mm=.002)
        with self.assertRaises(ValueError):
            audit_original(self.source,self.native,self.base_bp,self.base_manifest,
                           self.bp,self.manifest,declared_budget_mm=.002)

    def test_forged_manifest_even_with_original_bp_rejected(self):
        changed=copy.deepcopy(self.manifest)
        changed['source_wire_original_edge_ids'][0]=666
        with self.assertRaisesRegex(ValueError,'recomputation'):
            audit_original(self.source,self.native,self.base_bp,self.base_manifest,
                           self.bp,changed,declared_budget_mm=.001)

    def test_forged_bp_and_recomputed_digest_rejected(self):
        lines=self.bp.splitlines(keepends=True)
        item=next(i for i,line in enumerate(lines) if line.startswith('v '))
        fields=lines[item].strip().split()
        fields[1]=format(float(fields[1])+.05,'.17g')
        lines[item]=' '.join(fields)+'\n'
        changed=''.join(lines)
        changed_manifest=copy.deepcopy(self.manifest)
        changed_manifest['combined_bp_sha256']=sha256(changed.encode()).hexdigest()
        with self.assertRaises(ValueError):
            audit_original(self.source,self.native,self.base_bp,self.base_manifest,
                           changed,changed_manifest,declared_budget_mm=.001)

    def test_missing_original_boundary_mapping_rejected(self):
        vertices,patches=read_bp(self.bp)
        table=parse_entities(self.source)
        rows=_native_original_edges(table,self.native,self.audit['native_face_index'])
        with self.assertRaisesRegex(ValueError,'boundary patches'):
            _boundary_coverage_and_distance(self.original,
                {**self.manifest,'added_patches':self.manifest['added_patches'][:-1]},
                vertices,patches[:-1],rows,fixed_budget_mm=.001)

    def test_invalid_segment_count_fails_closed(self):
        for count in (0,33,1.5,True):
            with self.subTest(count=count),self.assertRaises(ValueError):
                angular_grid(self.original,count)

    def test_partial_benchmark_not_claimed_as_apmesh_mesh(self):
        self.assertFalse(self.manifest['full_s40_cad_patch_atlas'])
        self.assertEqual(self.audit['apmesh_tri_quad'],'NOT_RUN')
        self.assertEqual(self.audit['unrepresented_original_faces'],29)


if __name__=='__main__':
    unittest.main()
