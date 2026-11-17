"""Directed research tests for original S40 STEP #912/#3737 and 132-patch BP."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest

import cadquery as cq

from audit_analytic_bp import read_bp
from s3c_step_source_gate import coordinates, entity, oriented_edges, parse_entities, refs
from s3r_s40_conforming_hole_join import _edge_adjacency, _side
from s3t_s40_planar_octagons import (
    BUDGET_MM, FACE_IDS, PINNED_BP_SHA, SOURCE_EDGES_SHARED,
    STRICT_PLANAR_TOL_MM, _recover_partition, _check_pins,
    audit_original, build_extension,
)


class OriginalS40PlanarOctagonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        basedir = Path(os.environ.get('APMESH_ORIGINAL_CAD_DIR', ''))
        original = basedir / 'i25o_s40.step'
        if not original.is_file():
            raise unittest.SkipTest('Authorized pinned original S40 STEP not present locally')
        bp_file = Path(os.environ['APMESH_S3R_BASELINE_BP'])
        manifest_file = Path(os.environ['APMESH_S3R_BASELINE_MANIFEST'])
        registry_file = Path(os.environ['APMESH_S3P_SOURCE_REGISTRY'])
        cls.raw=original.read_bytes()
        cls.base_bp=bp_file.read_bytes()
        cls.base_manifest=json.loads(manifest_file.read_text('utf-8'))
        cls.registry=json.loads(registry_file.read_text('utf-8'))
        cls.source=_check_pins(cls.raw,cls.base_bp,cls.base_manifest,cls.registry,BUDGET_MM)
        cls.table=parse_entities(cls.source)
        cls.native=cq.importers.importStep(str(original)).val()
        cls.new_bp,cls.receipt=build_extension(cls.raw,cls.base_bp,cls.base_manifest,cls.registry)
        cls.audit=audit_original(cls.raw,cls.native,cls.base_bp,cls.base_manifest,
                                 cls.registry,cls.new_bp,cls.receipt)
        cls.base_points,cls.base_patches=read_bp(cls.base_bp.decode('utf-8'))
        cls.points,cls.patches=read_bp(cls.new_bp)
        cls.adjacency=_edge_adjacency(cls.patches)

    def test_01_original_sha256(self):
        self.assertEqual(sha256(self.raw).hexdigest(),
                         'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b')

    def test_02_frozen_parent_sha(self):
        self.assertEqual(sha256(self.base_bp).hexdigest(),PINNED_BP_SHA)

    def test_03_two_original_faces(self):
        self.assertEqual(FACE_IDS,(912,3737))
        self.assertEqual(self.receipt['original_face_ids'],[912,3737])

    def test_04_native_original_faces(self):
        self.assertEqual(self.audit['native_face_bijection_count'],43)
        self.assertEqual(self.audit['native_edge_bijection_count'],117)
        self.assertEqual(self.audit['native_vertex_bijection_count'],77)

    def test_05_source_octagons_are_all_lines(self):
        for face in FACE_IDS:
            support,wires=oriented_edges(self.table,face)
            self.assertEqual(support,'PLANE')
            self.assertEqual(len(wires),1)
            self.assertEqual(len(wires[0]),8)
            self.assertTrue(all(row['master_3d_curve']=='LINE' for row in wires[0]))

    def test_06_exhaustive_unique_convex_partition(self):
        for face in FACE_IDS:
            q=_recover_partition(self.table,face)
            self.assertEqual(len(q['quad_vertices']),3)
            self.assertEqual(len(q['diagonals']),2)
            self.assertTrue(all(len(p)==4 and len(set(p))==4 for p in q['quad_vertices']))

    def test_07_source_polygon_areas_recomputed(self):
        self.assertAlmostEqual(_recover_partition(self.table,912)['planar_area_mm2'],
                               242.89192333128233,places=7)
        self.assertAlmostEqual(_recover_partition(self.table,3737)['planar_area_mm2'],
                               932.8414433368824,places=7)

    def test_08_six_new_patches(self):
        self.assertEqual(len(self.patches),132)
        self.assertEqual(len(self.patches)-len(self.base_patches),6)

    def test_09_old_126_patches_preserved(self):
        self.assertEqual(self.patches[:126],self.base_patches)
        self.assertEqual(self.points[:1467],self.base_points)

    def test_10_existing_source_controls_reused(self):
        registry=self.registry['original_global_source_key_to_control_index']
        for face in FACE_IDS:
            newpart=self.patches[126:129] if face==912 else self.patches[129:132]
            sides={tuple(_side(p,name)) for p in newpart for name in ('left','right','top','bottom')}
            for edge in SOURCE_EDGES_SHARED[face]:
                ab=refs(entity(self.table,edge,'EDGE_CURVE')[1])[:2]
                keyed=(registry[f'vertex:{ab[0]}'],registry[f'edge:{edge}:1'],
                       registry[f'edge:{edge}:2'],registry[f'vertex:{ab[1]}'])
                self.assertTrue(keyed in sides or keyed[::-1] in sides)

    def test_11_six_new_original_native_two_sided_joins(self):
        registry=self.registry['original_global_source_key_to_control_index']
        for face in FACE_IDS:
            for e in SOURCE_EDGES_SHARED[face]:
                a,b=refs(entity(self.table,e,'EDGE_CURVE')[1])[:2]
                ids=(registry[f'vertex:{a}'],registry[f'edge:{e}:1'],
                     registry[f'edge:{e}:2'],registry[f'vertex:{b}'])
                self.assertEqual(len(self.adjacency[tuple(sorted(ids))]),2)

    def test_12_global_seam_census(self):
        self.assertEqual(sum(len(rows)==2 for rows in self.adjacency.values()),189)
        self.assertEqual(sum(len(rows)==1 for rows in self.adjacency.values()),150)
        self.assertTrue(all(len(rows)<=2 for rows in self.adjacency.values()))

    def test_13_no_previous_t_junction(self):
        self.assertEqual(len(_edge_adjacency(self.base_patches)),179+146)
        self.assertEqual(len(self.adjacency),189+150)

    def test_14_global_controls_count(self):
        self.assertEqual(len(self.points),1527)
        self.assertEqual(len({i for p in self.patches for i in p}),1409)

    def test_15_native_trimmed_interior_samples(self):
        self.assertEqual(self.audit['native_interior_samples'],486)

    def test_16_native_trimmed_boundary_samples(self):
        self.assertEqual(self.audit['native_boundary_samples'],264)

    def test_17_independent_native_original_edge_samples(self):
        self.assertEqual(self.audit['source_boundary_curve_samples'],176)
        self.assertEqual(self.audit['unique_source_native_edges'],16)

    def test_18_stricter_planar_error_than_experimental_budget(self):
        self.assertLess(self.audit['max_planar_surface_distance_mm'],STRICT_PLANAR_TOL_MM)
        self.assertLess(self.audit['max_native_source_edge_distance_mm'],STRICT_PLANAR_TOL_MM)
        self.assertLess(STRICT_PLANAR_TOL_MM,BUDGET_MM)

    def test_19_hole_not_removed(self):
        self.assertTrue(self.receipt['source_inner_hole_retained'])
        self.assertEqual(self.patches[96:126],self.base_patches[96:126])

    def test_20_not_apmesh_meshing(self):
        self.assertEqual(self.receipt['apmesh_tri_quad_generation'],'NOT_RUN')
        self.assertEqual(self.receipt['production_cpp_regression'],'NOT_RUN')
        self.assertFalse(self.receipt['continuous_trim_hausdorff_certified'])

    def test_21_source_hash_mutation_rejected(self):
        original=bytearray(self.raw)
        original[30]^=1
        with self.assertRaises(ValueError):
            build_extension(bytes(original),self.base_bp,self.base_manifest,self.registry)

    def test_22_baseline_bp_mutation_rejected(self):
        original=bytearray(self.base_bp)
        original[25]^=1
        with self.assertRaises(ValueError):
            build_extension(self.raw,bytes(original),self.base_manifest,self.registry)

    def test_23_budget_relaxation_and_tightening_rejected(self):
        for bad in (.01,.002,.0001):
            with self.subTest(budget=bad),self.assertRaises(ValueError):
                build_extension(self.raw,self.base_bp,self.base_manifest,self.registry,budget_mm=bad)

    def test_24_registry_control_tamper_rejected(self):
        forged=deepcopy(self.registry)
        forged['original_global_source_key_to_control_index']['edge:916:1']=999
        with self.assertRaises(ValueError):
            build_extension(self.raw,self.base_bp,self.base_manifest,forged)

    def test_25_missing_hole_provenance_rejected(self):
        forged=deepcopy(self.base_manifest)
        forged['source_inner_hole_retained']=False
        with self.assertRaises(ValueError):
            build_extension(self.raw,self.base_bp,forged,self.registry)

    def test_26_receipt_tamper_rejected(self):
        forged=deepcopy(self.receipt)
        forged['source_original_faces_represented']=43
        with self.assertRaises(ValueError):
            audit_original(self.raw,self.native,self.base_bp,self.base_manifest,
                           self.registry,self.new_bp,forged)

    def test_27_bp_control_tamper_rejected(self):
        forged=self.new_bp.replace('v ', 'v 999 ',1)
        with self.assertRaises(ValueError):
            audit_original(self.raw,self.native,self.base_bp,self.base_manifest,
                           self.registry,forged,self.receipt)

    def test_28_wrong_native_brep_rejected(self):
        forged=cq.Workplane().box(10,10,10).val()
        with self.assertRaises(ValueError):
            audit_original(self.raw,forged,self.base_bp,self.base_manifest,
                           self.registry,self.new_bp,self.receipt)


if __name__=='__main__':
    unittest.main()
