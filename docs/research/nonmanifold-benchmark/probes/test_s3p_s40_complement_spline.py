"""Adversarial original S40 #2457 half-cylinder seam and native trim tests."""
from __future__ import annotations

import copy
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest

import cadquery as cq

from audit_analytic_bp import read_bp
from s3c_step_source_gate import SOURCES, parse_entities, oriented_edges
from s3p_s40_complement_spline import (
    FACE, EDGES, SPLINE_EDGES, GENERATOR_EDGES, EXISTING_SEAMS,
    _area, _boundary_pieces, _native_boundary_map, audit_original,
    build_extension, cells, grid, source_partition,
)


class OriginalS40ComplementaryCylinderGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ.get('APMESH_ORIGINAL_CAD_DIR','.'))
        cls.step = root / SOURCES['S40'][0]
        if not cls.step.exists():
            raise unittest.SkipTest('Pinned original S40 STEP is not available')
        cls.source = cls.step.read_text('utf-8')
        if sha256(cls.step.read_bytes()).hexdigest()!=SOURCES['S40'][1]:
            raise ValueError('Pinned STEP hash mismatch')
        cls.native = cq.importers.importStep(str(cls.step)).val()
        package=Path(__file__).resolve().parents[1]
        cls.baseline_bp = (package/'private_bp/s40_spline1519.partial.bp').read_text('utf-8')
        cls.baseline_manifest = json.loads((package/'private_bp/s40_spline1519_manifest.json').read_text('utf-8'))
        cls.partition=source_partition(cls.source)
        cls.bp,cls.manifest=build_extension(cls.source,cls.baseline_bp,cls.baseline_manifest,
                                            left_sectors=2,right_sectors=6)
        cls.audit=audit_original(cls.source,cls.native,cls.baseline_bp,cls.baseline_manifest,
                                 cls.bp,cls.manifest)

    def test_pinned_source_and_unique_native_faces(self):
        self.assertEqual(sha256(self.step.read_bytes()).hexdigest(),SOURCES['S40'][1])
        self.assertEqual(len(self.native.Faces()),43)
        self.assertEqual((self.audit['native_face_index'],self.audit['neighbor_native_face_index']),(22,12))
        self.assertEqual(FACE,2457)

    def test_exact_nine_original_edge_curve_ids(self):
        self.assertEqual(tuple(self.partition['source_wire_original_edge_ids']),EDGES)
        self.assertEqual(len(self.partition['original_vertices']),9)
        self.assertEqual(set(self.partition['source_wire_original_edge_ids']),set(EDGES))

    def test_3d_splines_cylinder_pcurves_and_split_top(self):
        e={x['edge_id']:x for x in self.partition['source_edges']}
        self.assertEqual({x for x in e if e[x]['curve_type_3d']=='B_SPLINE_CURVE_WITH_KNOTS'},set(SPLINE_EDGES))
        self.assertEqual([e[i]['pcurve_control_count'] for i in SPLINE_EDGES],[47,25,47])
        self.assertEqual({x for x in e if e[x]['curve_type_3d']=='LINE'},set(GENERATOR_EDGES))
        self.assertEqual(e[1886]['pcurve_type'],'LINE')
        self.assertEqual(e[1911]['pcurve_type'],'BSPLINE_DEGREE_1')

    def test_angular_x_reference_is_opposite_and_physical_faces_disjoint_in_centroid(self):
        self.assertAlmostEqual(self.partition['source_opposite_reference_x_dot'],-1.,places=12)
        self.assertGreater(self.audit['native_centroid_separation_mm'],20.)
        self.assertLess(self.audit['native_centroid_separation_mm'],22.)

    def test_rectangular_uv_partition_and_nine_original_nodes(self):
        self.assertEqual(len(grid(self.partition,2,6)),11)
        self.assertEqual(len(cells(self.partition,2,6)),18)
        self.assertAlmostEqual(self.audit['source_uv_area'],_area(self.partition,2,6),places=10)

    def test_partial_bp_extension_with_exact_global_controls(self):
        points,patches=read_bp(self.bp)
        self.assertEqual(len(patches),77)
        self.assertEqual(len(points),864)
        self.assertEqual(self.manifest['baseline_patch_count'],59)
        self.assertEqual(self.manifest['added_patch_count'],18)
        self.assertEqual(self.manifest['internal_new_seams'],24)
        self.assertEqual(self.audit['new_integer_internal_seams'],24)

    def test_boundary_partition_exactly_explains_nine_source_edges(self):
        by_edge,boundary_count=_boundary_pieces(self.partition,self.manifest['added_patches'])
        self.assertEqual(boundary_count,24)
        self.assertEqual({eid:len(by_edge[eid]) for eid in EDGES},
                         {2309:7,2251:3,1616:1,1911:1,2434:1,2096:8,2407:1,1886:1,1753:1})

    def test_native_topods_edge_bijection_and_twin_generator_identity(self):
        edges=_native_boundary_map(self.partition,parse_entities(self.source),self.native,22)
        self.assertEqual(len({a['native_index'] for a in edges.values()}),9)
        for eid in EXISTING_SEAMS:
            self.assertIn(12,edges[eid]['incident'])
            self.assertIn(22,edges[eid]['incident'])

    def test_both_original_shared_generators_reuse_baseline_integer_ids(self):
        a=self.baseline_manifest['original_global_source_key_to_control_index']
        b=self.manifest['original_global_source_key_to_control_index']
        for eid in EXISTING_SEAMS:
            for n in (1,2):
                self.assertEqual(a[f'edge:{eid}:{n}'],b[f'edge:{eid}:{n}'])
        self.assertEqual(self.audit['shared_original_indexed_control_references'],8)

    def test_all_nine_original_curves_have_native_distance_checks(self):
        rows=self.audit['source_native_boundary_rows']
        self.assertEqual(len(rows),9)
        self.assertEqual(len({r['native_topods_edge_index'] for r in rows}),9)
        self.assertEqual(sum(r['boundary_sample_count'] for r in rows),24*9)
        self.assertTrue(all(r['max_sampled_3d_edge_distance_mm']<.001 for r in rows))
        self.assertEqual({r['original_edge_curve_id'] for r in rows},set(EDGES))

    def test_native_trimmed_uv_membership_and_bernstein_gate(self):
        self.assertEqual(self.audit['native_interior_sample_count'],1458)
        self.assertEqual(self.audit['native_boundary_sample_count'],792)
        self.assertEqual(self.audit['native_trim_histogram']['INTERIOR_IN'],1458)
        self.assertEqual(sum(v for k,v in self.audit['native_trim_histogram'].items() if k.startswith('BOUNDARY_')),792)
        self.assertLess(self.audit['max_guarded_radial_support_error_mm'],.001)
        self.assertLess(self.audit['max_native_cylinder_sampled_projection_error_mm'],.001)

    def test_inadequate_right_partition_fails_the_fixed_budget(self):
        bp,meta=build_extension(self.source,self.baseline_bp,self.baseline_manifest,left_sectors=2,right_sectors=5)
        with self.assertRaisesRegex(ValueError,'Bernstein radial enclosure exceeds'):
            audit_original(self.source,self.native,self.baseline_bp,self.baseline_manifest,bp,meta)

    def test_source_sha_change_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'SHA-256'):
            source_partition(self.source.replace('ISO-10303-21;','ISO-10303-22;',1))

    def test_fixed_budget_may_not_be_raised_after_trial(self):
        with self.assertRaisesRegex(ValueError,'budget'):
            build_extension(self.source,self.baseline_bp,self.baseline_manifest,left_sectors=2,right_sectors=6,declared_budget_mm=.002)
        with self.assertRaisesRegex(ValueError,'budget'):
            audit_original(self.source,self.native,self.baseline_bp,self.baseline_manifest,self.bp,self.manifest,declared_budget_mm=.002)

    def test_modified_bp_content_and_forged_manifest_fail(self):
        with self.assertRaisesRegex(ValueError,'checksum'):
            audit_original(self.source,self.native,self.baseline_bp,self.baseline_manifest,
                           self.bp.replace('BP','Bp',1),self.manifest)
        modified=copy.deepcopy(self.manifest)
        modified['original_wire_edge_curve_ids'][0]=9999
        with self.assertRaisesRegex(ValueError,'Recomputed.*mismatch'):
            audit_original(self.source,self.native,self.baseline_bp,self.baseline_manifest,self.bp,modified)

    def test_baseline_patch_registry_may_not_change(self):
        changed=copy.deepcopy(self.baseline_manifest)
        changed['original_global_source_key_to_control_index']['edge:1616:1']=-1
        with self.assertRaisesRegex(ValueError,'injective'):
            build_extension(self.source,self.baseline_bp,changed,left_sectors=2,right_sectors=6)


if __name__=='__main__':
    unittest.main()
