"""Directed pinned-original S40 de Casteljau conformity and hole controls."""
from __future__ import annotations

from collections import Counter
import copy
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import tempfile
import unittest

import cadquery as cq

from audit_analytic_bp import read_bp
from s3c_step_source_gate import SOURCES
from s3q_s40_hole_preserving_island import PREEXISTING_GENERATORS, source_partition
from s3r_s40_conforming_hole_join import (
    BUDGET_MM, ISLAND_PATCHES, ORIGINAL_PATCHES, ORIGINAL_CONTROLS,
    PINNED_S3P_BP_SHA256, PINNED_S3P_MANIFEST_SHA256,
    TARGET_SPLIT_PATCHES, _edge_adjacency, _nets_split, _point_split,
    _side, audit_join, build_join, propagation,
)


class OriginalS40ConformingHoleJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder=os.environ.get('APMESH_ORIGINAL_CAD_DIR') or os.environ.get('APMESH_MAMBO_SOURCE_DIR')
        if not folder:
            raise unittest.SkipTest('Pinned original S40 STEP is required')
        cls.path=Path(folder)/SOURCES['S40'][0]
        if not cls.path.is_file():
            raise unittest.SkipTest('Pinned original S40 STEP was not supplied')
        raw=cls.path.read_bytes()
        if sha256(raw).hexdigest()!=SOURCES['S40'][1]:
            raise ValueError('Wrong original S40 byte-level SHA-256')
        cls.source=raw.decode('utf-8')
        package=Path(os.environ.get('APMESH_S3R_PRIVATE_DIR',Path(__file__).resolve().parents[1]/'private_bp'))
        cls.old_bp=(package/'s40_previous_77_patches.partial.bp').read_text('utf-8')
        cls.old_manifest=json.loads((package/'s40_previous_77_patches_manifest.json').read_text('utf-8'))
        cls.island_bp=(package/'s40_face218_hole.isolated.bp').read_text('utf-8')
        cls.island_manifest=json.loads((package/'s40_face218_hole_manifest.json').read_text('utf-8'))
        cls.bp,cls.manifest=build_join(cls.source,cls.old_bp,cls.old_manifest,cls.island_bp,cls.island_manifest)
        cls.native=cq.importers.importStep(str(cls.path)).val()
        cls.audit=audit_join(cls.source,cls.native,cls.bp,cls.manifest,
                             cls.old_bp,cls.old_manifest,cls.island_bp,cls.island_manifest)
        cls.points,cls.patches=read_bp(cls.bp)
        cls.old_points,cls.old_patches=read_bp(cls.old_bp)

    def test_01_original_s40_sha256(self):
        self.assertEqual(sha256(self.source.encode()).hexdigest(),SOURCES['S40'][1])

    def test_02_original_prior_bp_sha256(self):
        self.assertEqual(sha256(self.old_bp.encode()).hexdigest(),PINNED_S3P_BP_SHA256)

    def test_03_original_prior_manifest_sha256(self):
        encoded=(json.dumps(self.old_manifest,sort_keys=True,indent=2)+'\n').encode()
        self.assertEqual(sha256(encoded).hexdigest(),PINNED_S3P_MANIFEST_SHA256)

    def test_04_original_island_rebuilt_from_source(self):
        self.assertEqual(self.manifest['original_island_bp_sha256'],sha256(self.island_bp.encode()).hexdigest())

    def test_05_exact_19_parent_propagation(self):
        self.assertEqual(self.manifest['propagated_parent_patch_count'],TARGET_SPLIT_PATCHES)
        self.assertEqual(len(self.manifest['propagated_split_records']),19)

    def test_06_four_original_source_id_seeds(self):
        self.assertEqual({x['edge_curve_id'] for x in self.manifest['source_seed_edges']},set(PREEXISTING_GENERATORS))
        self.assertEqual(len(self.manifest['joined_original_generator_controls']),4)

    def test_07_propagation_reaches_original_cylinder_and_planar_neighbors(self):
        prior_ids={s['parent_patch_id'] for s in self.manifest['propagated_split_records']}
        self.assertTrue({3,4,25,34,52,58}.issubset(prior_ids))

    def test_08_old_patch_retopology_is_77_plus_19(self):
        self.assertEqual(self.manifest['retopologized_old_patch_count'],96)
        self.assertEqual(self.manifest['island_first_patch_id'],96)

    def test_09_new_hole_candidate_adds_30(self):
        self.assertEqual(self.manifest['island_patches_added'],ISLAND_PATCHES)
        self.assertEqual(self.manifest['joined_patch_count'],ORIGINAL_PATCHES+19+30)
        self.assertEqual(len(self.patches),126)

    def test_10_original_face_coverage_is_partial(self):
        self.assertEqual(self.manifest['source_original_face_coverage'],17)
        self.assertEqual(self.manifest['source_face_count'],43)

    def test_11_all_original_global_indices_are_stable(self):
        self.assertEqual(self.points[:ORIGINAL_CONTROLS],self.old_points)
        self.assertEqual(self.manifest['prior_controls'],864)
        self.assertEqual(len(self.points),self.manifest['joined_control_count'])

    def test_12_original_source_seams_are_two_sided(self):
        edge_map=_edge_adjacency(self.patches)
        for edge in self.manifest['joined_original_generator_controls'].values():
            for child in edge['previous_children']:
                self.assertTrue(any(child in [r[0] for r in side] and len(side)==2
                                    for side in edge_map.values()))

    def test_13_all_four_source_edges_have_two_island_pieces(self):
        for original_edge in self.manifest['joined_original_generator_controls'].values():
            self.assertEqual(len(original_edge['previous_children']),2)
            self.assertEqual(len(original_edge['island_patches']),2)

    def test_14_all_computed_index_seams_are_at_most_two_sided(self):
        edge_map=_edge_adjacency(self.patches)
        self.assertEqual(sum(len(side)==2 for side in edge_map.values()),179)
        self.assertEqual(sum(len(side)==1 for side in edge_map.values()),146)

    def test_15_no_source_coordinates_welded_by_proximity(self):
        self.assertIn('ORIGINAL_EDGE_CURVE',self.manifest['source_seam_identity_method'])
        self.assertEqual(self.manifest['joined_control_comparison_tolerance_mm'],1e-8)

    def test_16_patch_cube_de_casteljau_endpoints(self):
        control=[(float(i),0.,0.) for i in range(4)]
        left,right=_point_split(control,0.4)
        self.assertEqual(left[0],control[0])
        self.assertEqual(right[-1],control[-1])
        self.assertEqual(left[-1],right[0])

    def test_17_patch_surface_invariance(self):
        self.assertLess(self.audit['max_original_surface_reparameterization_sample_difference_mm'],1e-10)

    def test_18_original_12_outer_inner_native_boundary_edges(self):
        self.assertEqual(self.audit['original_source_native_boundary_count'],12)
        self.assertEqual(self.audit['original_inner_hole_native_edge_count'],4)

    def test_19_source_hole_is_retained(self):
        self.assertTrue(self.manifest['source_inner_hole_retained'])
        self.assertEqual(self.audit['native_hole_OUT_samples'],49)

    def test_20_all_new_patch_uv_samples_are_in_or_on(self):
        states=self.audit['native_island_trim_classification_histogram']
        self.assertEqual(states.get('INTERIOR_IN'),2430)
        self.assertEqual(sum(n for key,n in states.items() if key.startswith('BOUNDARY_')),1320)
        self.assertFalse(any(key.endswith('OUT') and n>0 for key,n in states.items()))

    def test_21_native_split_cylinder_children_audited(self):
        self.assertEqual(self.audit['retopologized_original_native_cylinder_children'],34)
        self.assertEqual(self.audit['retopologized_original_native_sample_histogram']['INTERIOR_IN'],1666)

    def test_22_fixed_budget_on_original_native_curves(self):
        self.assertLess(self.audit['max_native_source_edge_distance_mm'],BUDGET_MM)
        self.assertLess(self.audit['max_guarded_radial_support_bound_mm'],BUDGET_MM)
        self.assertLess(self.audit['retopologized_original_native_max_projection_distance_mm'],BUDGET_MM)

    def test_23_no_false_full_cad_or_meshing_claim(self):
        self.assertEqual(self.manifest['apmesh_tri_quad_mesh'],'NOT_RUN')
        self.assertEqual(self.manifest['source_nonmanifold_3plus'],'NOT_ESTABLISHED')
        self.assertEqual(self.audit['continuous_trim_or_hole_topology_certificate'],'NOT_ESTABLISHED')

    def test_24_wrong_original_step_rejected(self):
        with self.assertRaises(ValueError):
            build_join(self.source.replace('ISO-10303-21;','ISO-10303-20;',1),
                       self.old_bp,self.old_manifest,self.island_bp,self.island_manifest)

    def test_25_wrong_original_baseline_bp_rejected(self):
        with self.assertRaises(ValueError):
            build_join(self.source,self.old_bp+' ',self.old_manifest,self.island_bp,self.island_manifest)

    def test_26_rehashed_forged_baseline_manifest_rejected(self):
        bad=copy.deepcopy(self.old_manifest)
        bad['original_global_source_key_to_control_index']['edge:222:1']+=1
        with self.assertRaises(ValueError):
            build_join(self.source,self.old_bp,bad,self.island_bp,self.island_manifest)

    def test_27_wrong_island_bp_rejected(self):
        with self.assertRaises(ValueError):
            build_join(self.source,self.old_bp,self.old_manifest,self.island_bp+' ',self.island_manifest)

    def test_28_wrong_island_manifest_rejected(self):
        bad=copy.deepcopy(self.island_manifest)
        bad['original_hole_preserved']=False
        with self.assertRaises(ValueError):
            build_join(self.source,self.old_bp,self.old_manifest,self.island_bp,bad)

    def test_29_relaxed_budget_rejected(self):
        with self.assertRaises(ValueError):
            build_join(self.source,self.old_bp,self.old_manifest,self.island_bp,self.island_manifest,budget_mm=.01)

    def test_30_modified_joined_bp_rejected(self):
        with self.assertRaises(ValueError):
            audit_join(self.source,self.native,self.bp+' ',self.manifest,
                       self.old_bp,self.old_manifest,self.island_bp,self.island_manifest)

    def test_31_forged_joined_manifest_rejected(self):
        bad=copy.deepcopy(self.manifest)
        bad['native_hole_OUT_samples']=0
        with self.assertRaises(ValueError):
            audit_join(self.source,self.native,self.bp,bad,
                       self.old_bp,self.old_manifest,self.island_bp,self.island_manifest)

    def test_32_nonconforming_forged_adjacency_rejected(self):
        wrong=self.patches + [self.patches[0]]*2
        with self.assertRaises(ValueError):_edge_adjacency(wrong)

    def test_33_surface_split_rejects_endpoint_t(self):
        with self.assertRaises(ValueError):_point_split([(float(i),)*3 for i in range(4)],0.)
        with self.assertRaises(ValueError):_point_split([(float(i),)*3 for i in range(4)],1.)

    def test_34_private_derived_bp_integrity(self):
        self.assertEqual(self.manifest['joined_bp_sha256'],sha256(self.bp.encode()).hexdigest())


if __name__=='__main__':unittest.main()
