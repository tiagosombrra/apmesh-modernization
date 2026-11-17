"""Directed original-CAD tests for a deliberately isolated holed surface."""
from __future__ import annotations

import copy
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import unittest

import cadquery as cq
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.TopAbs import TopAbs_OUT
from OCP.gp import gp_Pnt2d

from audit_analytic_bp import read_bp
from s3c_step_source_gate import SOURCES
from s3q_s40_hole_preserving_island import (
    EXTERIOR,INTERIOR,PREEXISTING_GENERATORS,SEGMENTS,
    _boundary_sides, _pcurve, _native_edges, audit_nonconforming_join,
    audit_original,build_island,cells,grid,pilot_angular_bound,
    source_partition,source_spline_endpoint_deviation,verify_uv_partition,
)
from s3c_step_source_gate import parse_entities


class OriginalS40HolePreservingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder=os.environ.get('APMESH_ORIGINAL_CAD_DIR') or os.environ.get('APMESH_MAMBO_SOURCE_DIR')
        if not folder:
            raise unittest.SkipTest('Pinned original MAMBO S40 requires APMESH_ORIGINAL_CAD_DIR')
        cls.path=Path(folder)/SOURCES['S40'][0]
        if not cls.path.is_file():
            raise unittest.SkipTest('Original S40 STEP file not provided')
        raw=cls.path.read_bytes()
        if sha256(raw).hexdigest()!=SOURCES['S40'][1]:
            raise ValueError('The provided original S40 bytes fail the pinned SHA-256')
        cls.source=raw.decode('utf-8')
        cls.part=source_partition(cls.source)
        cls.bp,cls.manifest=build_island(cls.source)
        cls.native=cq.importers.importStep(str(cls.path)).val()
        cls.audit=audit_original(cls.source,cls.native,cls.bp,cls.manifest)
        cls.basebp=None
        source_bp=os.environ.get('APMESH_S3Q_BASELINE_BP')
        source_manifest=os.environ.get('APMESH_S3Q_BASELINE_MANIFEST')
        if source_bp and source_manifest:
            cls.basebp=Path(source_bp).read_text('utf-8')
            cls.base_manifest=json.loads(Path(source_manifest).read_text('utf-8'))
            cls.join=audit_nonconforming_join(cls.source,cls.manifest,cls.basebp,cls.base_manifest)

    def test_01_source_pinned_bytes(self):
        self.assertEqual(self.part['source_sha256'],SOURCES['S40'][1])

    def test_02_two_original_wires(self):
        self.assertEqual([x['wire'] for x in self.part['source_edges']].count('EXTERIOR'),8)
        self.assertEqual([x['wire'] for x in self.part['source_edges']].count('HOLE'),4)

    def test_03_twelve_distinct_source_vertices(self):
        self.assertEqual(len(self.part['original_vertices']),12)

    def test_04_outer_inner_source_edge_ids(self):
        self.assertEqual(tuple(self.manifest['original_outer_edge_ids']),EXTERIOR)
        self.assertEqual(tuple(self.manifest['original_inner_edge_ids']),INTERIOR)

    def test_05_original_quadratic_hole_curves(self):
        splines=[x for x in self.part['source_edges'] if x['edge_id'] in (411,500)]
        self.assertEqual({x['degree'] for x in splines},{2})
        self.assertEqual({x['fixed_axis'] for x in splines},{'U','V'})

    def test_06_original_3d_spline_endpoint_is_not_exact_cylinder(self):
        observed=source_spline_endpoint_deviation(self.part)
        self.assertGreater(max(x['source_support_radial_endpoint_residual_mm'] for x in observed),1e-7)
        self.assertLess(max(x['source_support_radial_endpoint_residual_mm'] for x in observed),1e-5)

    def test_07_hole_uv_area_is_subtracted(self):
        area=verify_uv_partition(self.part)
        self.assertGreater(area['original_inner_hole_parametric_area'],0)
        self.assertAlmostEqual(area['partition_parametric_area'],area['expected_source_parametric_area'],places=7)

    def test_08_explicit_hole_not_filled_by_patches(self):
        self.assertTrue(self.manifest['source_uv_area_audit']['hole_not_filled'])
        self.assertEqual(len(cells(self.part)),30)

    def test_09_computed_hole_infill_is_rejected(self):
        corrupted=cells(self.part)
        u=self.part['breakpoints_u'];v=self.part['breakpoints_v']
        corrupted.append((999,999,u[2],u[3],v[2],v[3]))
        with self.assertRaises(ValueError):verify_uv_partition(self.part,corrupted)

    def test_10_missing_hole_loop_is_rejected(self):
        bad=copy.deepcopy(self.part)
        bad['source_wires_uv'][1]=[]
        with self.assertRaises(ValueError):verify_uv_partition(bad)

    def test_11_grid_and_original_hole_breakpoints(self):
        self.assertEqual(len(grid(self.part)),12)
        self.assertEqual(SEGMENTS,(1,2,5,2,1))

    def test_12_four_middle_sectors_fail_original_budget(self):
        self.assertGreater(pilot_angular_bound(self.part,4),.001)

    def test_13_five_middle_sectors_meet_original_budget(self):
        self.assertLess(pilot_angular_bound(self.part,5),.001)

    def test_14_exact_indexed_bicubic_island_inventory(self):
        vertices,patches=read_bp(self.bp)
        self.assertEqual(len(patches),30)
        self.assertEqual(len(vertices),336)
        self.assertEqual(self.manifest['island_internal_indexed_seam_count'],38)
        self.assertEqual(len(self.manifest['source_indexed_control_keys']),len(vertices))

    def test_15_all_original_source_edges_have_boundary_cover(self):
        boundaries,frontier=_boundary_sides(self.part,self.manifest['added_patches'])
        self.assertEqual(set(boundaries),set(EXTERIOR)|set(INTERIOR))
        self.assertEqual(len(frontier),sum(len(x) for x in boundaries.values()))

    def test_16_original_source_native_face_and_edges(self):
        self.assertEqual(self.audit['native_face_index'],1)
        self.assertEqual(len(self.audit['original_source_native_edge_mappings']),12)
        self.assertEqual(len({x['native_edge_index'] for x in self.audit['original_source_native_edge_mappings']}),12)

    def test_17_native_hole_out_with_49_samples(self):
        self.assertEqual(self.audit['native_hole_OUT_samples'],49)
        u=self.part['breakpoints_u'];v=self.part['breakpoints_v']
        center=gp_Pnt2d((u[2]+u[3])/2,(v[1]+v[3])/2)
        state=BRepClass_FaceClassifier(self.native.Faces()[1].wrapped,center,1e-7).State()
        self.assertEqual(state,TopAbs_OUT)

    def test_18_native_patch_trim_samples_in(self):
        self.assertEqual(self.audit['native_patch_classification_histogram']['INTERIOR_IN'],2430)
        self.assertEqual(sum(x for key,x in self.audit['native_patch_classification_histogram'].items() if key.startswith('BOUNDARY_')),1320)

    def test_19_native_boundary_distance_budget(self):
        self.assertLess(self.audit['maximum_sampled_native_trimmed_edge_distance_mm'],.001)
        self.assertEqual({x['wire'] for x in self.audit['original_source_native_edge_mappings']},{'HOLE','EXTERIOR'})

    def test_20_native_radial_support_guard(self):
        self.assertLess(self.audit['maximum_guarded_bernstein_radial_bound_mm'],.001)
        self.assertLess(self.audit['maximum_sampled_native_cylinder_projection_distance_mm'],.001)

    def test_21_reject_mutated_original_step(self):
        with self.assertRaises(ValueError): source_partition(self.source.replace('ISO-10303-21;','ISO-10303-99;',1))

    def test_22_reject_changed_bp(self):
        changed=self.bp.replace('0.', '1.',1)
        self.assertNotEqual(changed,self.bp)
        with self.assertRaises(ValueError): audit_original(self.source,self.native,changed,self.manifest)

    def test_23_reject_rehashed_misleading_manifest(self):
        bad=copy.deepcopy(self.manifest)
        bad['original_hole_preserved']=False
        with self.assertRaises(ValueError): audit_original(self.source,self.native,self.bp,bad)

    def test_24_reject_relaxed_budget(self):
        with self.assertRaises(ValueError):build_island(self.source,declared_budget_mm=.01)
        with self.assertRaises(ValueError):audit_original(self.source,self.native,self.bp,self.manifest,budget_mm=.01)

    def test_25_reject_nonpredeclared_sector_counts(self):
        with self.assertRaises(ValueError):build_island(self.source,sectors=(1,2,4,2,1))

    def test_26_reject_wrong_native_shape(self):
        wrong=cq.Workplane('XY').box(10,10,10).val()
        with self.assertRaises(ValueError):audit_original(self.source,wrong,self.bp,self.manifest)

    def test_27_island_not_a_conforming_join(self):
        self.assertFalse(self.manifest['original_hole_preserved'] is False)
        self.assertEqual(self.manifest['joint_77_patch_atlas'],'BLOCKED_BY_PREEXISTING_EDGE_SUBDIVISION')
        self.assertEqual(tuple(self.manifest['preexisting_generator_edges_requiring_conforming_split']),PREEXISTING_GENERATORS)

    def test_28_prior_original_atlas_is_not_silently_changed(self):
        if self.basebp is None:self.skipTest('Optional previous original 77-patch baseline unavailable')
        self.assertEqual(self.join['prior_accepted_patch_count'],77)
        self.assertFalse(self.join['combined_atlas_is_conforming'])
        self.assertEqual(len(self.join['blocked_original_interfaces']),4)
        self.assertTrue(all(x['new_island_boundary_piece_count']==2 for x in self.join['blocked_original_interfaces']))

    def test_29_reject_changed_baseline_hash(self):
        if self.basebp is None:self.skipTest('Optional previous original baseline unavailable')
        with self.assertRaises(ValueError):
            audit_nonconforming_join(self.source,self.manifest,self.basebp+' ',self.base_manifest)

    def test_30_no_mesh_or_full_shell_claim(self):
        self.assertEqual(self.audit['apmesh_tri_quad_mesh'],'NOT_RUN')
        self.assertFalse(self.audit['combined_original_atlas'])
        self.assertEqual(self.manifest['original_s40_face_coverage_prior'],16)


if __name__=='__main__':unittest.main()
