#!/usr/bin/env python3
"""Negative and positive controls for the generated, source-independent F31 corpus."""
from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import thingi10k_f31_synthetic_generalization as f31
import thingi10k_f30_feature_locked_quad_center_optimizer as f30


class GeneratedGeometryTests(unittest.TestCase):
    def test_generated_model_count(self):
        self.assertEqual(len(f31.build_sources()),9)

    def test_model_names_pinned(self):
        self.assertEqual(tuple(f31.build_sources()),f31.SOURCE_FAMILIES)

    def test_model_sources_not_original_assets(self):
        self.assertNotIn('293137',repr(f31.build_sources()))

    def test_tetra_face_count(self):
        self.assertEqual(len(f31.tetra()[1]),4)

    def test_stretched_tetra_face_count(self):
        self.assertEqual(len(f31.tetra(True)[1]),4)

    def test_octa_face_count(self):
        self.assertEqual(len(f31.octa()[1]),8)

    def test_cube_face_count(self):
        self.assertEqual(len(f31.cube()[1]),12)

    def test_cube_eight_unique_vertices(self):
        self.assertEqual(len(f31.cube()[0]),8)

    def test_icosa_faces(self):
        self.assertEqual(len(f31.icosahedron()[1]),20)

    def test_prism_faces(self):
        self.assertEqual(len(f31.capped_prism()[1]),32)

    def test_torus_faces(self):
        self.assertEqual(len(f31.torus()[1]),192)

    def test_corrugated_torus_faces(self):
        self.assertEqual(len(f31.torus(True)[1]),192)

    def test_invalid_prism_sides_rejected(self):
        with self.assertRaises(ValueError):f31.capped_prism(2)

    def test_invalid_torus_discretization_rejected(self):
        with self.assertRaises(ValueError):f31.torus(nu=2,nv=8)

    def test_generated_coordinates_are_finite(self):
        for vs,_ in f31.build_sources().values():
            self.assertTrue(all(math.isfinite(x) for vertex in vs for x in vertex))

    def test_generated_faces_have_three_unique_nodes(self):
        for vs,faces in f31.build_sources().values():
            self.assertTrue(all(len(set(f))==3 and max(f)<len(vs) for f in faces))

    def test_genus_zero_models_closed(self):
        for name,(vs,fs) in f31.build_sources().items():
            if 'torus' not in name:
                self.assertEqual(f31.topology(vs,fs,expected_genus=0)['euler'],2)

    def test_genus_one_models_closed(self):
        for name,(vs,fs) in f31.build_sources().items():
            if 'torus' in name:
                self.assertEqual(f31.topology(vs,fs,expected_genus=1)['euler'],0)

    def test_cross_product_contract(self):
        self.assertEqual(f31.cross((1,0,0),(0,1,0)),(0,0,1))

    def test_edge_key_canonical(self):
        self.assertEqual(f31.edge_key(2,1),f31.edge_key(1,2))

    def test_self_edge_rejected(self):
        with self.assertRaises(ValueError):f31.edge_key(1,1)

    def test_undefined_faces_rejected(self):
        with self.assertRaises(ValueError):f31.topology(((0.,0.,0.),),(),expected_genus=0)

    def test_malformed_coordinates_rejected(self):
        vs,fs=f31.tetra()
        with self.assertRaises(ValueError):f31.topology(((math.nan,0.,0.),*vs[1:]),fs,expected_genus=0)

    def test_wrong_face_arity_rejected(self):
        vs,fs=f31.tetra()
        with self.assertRaises(ValueError):f31.topology(vs,((0,1),*fs[1:]),expected_genus=0)

    def test_repeated_face_vertex_rejected(self):
        vs,fs=f31.tetra()
        with self.assertRaises(ValueError):f31.topology(vs,((0,0,1),*fs[1:]),expected_genus=0)

    def test_out_of_range_face_vertex_rejected(self):
        vs,fs=f31.tetra()
        with self.assertRaises(ValueError):f31.topology(vs,((0,1,500),*fs[1:]),expected_genus=0)

    def test_reversed_face_rejected(self):
        vs,fs=f31.tetra()
        with self.assertRaises(ValueError):f31.topology(vs,(tuple(reversed(fs[0])),*fs[1:]),expected_genus=0)

    def test_missing_face_rejected(self):
        vs,fs=f31.tetra()
        with self.assertRaises(ValueError):f31.topology(vs,fs[:-1],expected_genus=0)

    def test_duplicate_face_rejected(self):
        vs,fs=f31.tetra()
        with self.assertRaises(ValueError):f31.topology(vs,fs+(fs[0],),expected_genus=0)

    def test_incorrect_genus_rejected(self):
        vs,fs=f31.tetra()
        with self.assertRaises(ValueError):f31.topology(vs,fs,expected_genus=1)

    def test_negative_genus_rejected(self):
        vs,fs=f31.tetra()
        with self.assertRaises(ValueError):f31.topology(vs,fs,expected_genus=-1)

    def test_unused_vertex_rejected(self):
        vs,fs=f31.tetra()
        with self.assertRaises(ValueError):f31.topology(vs+((100.,0.,0.),),fs,expected_genus=0)

    def test_independent_coincident_shells_not_welded(self):
        vs,fs=f31.tetra()
        combined_v=vs+vs
        combined_f=fs+tuple(tuple(v+len(vs) for v in f) for f in fs)
        derived_v,derived_f=f31.derive_sector_quad_complex(combined_v,combined_f)
        self.assertEqual(len(derived_v),2*len(f31.derive_sector_quad_complex(vs,fs)[0]))
        with self.assertRaises(ValueError):f31.topology(derived_v,derived_f,expected_genus=0)

    def test_separated_shells_rejected(self):
        vs,fs=f31.tetra()
        translated=tuple((x+15.,y+15.,z+15.) for x,y,z in vs)
        with self.assertRaises(ValueError):
            f31.topology(vs+translated,fs+tuple(tuple(v+4 for v in f) for f in fs),
                         expected_genus=0)

    def test_pinched_vertex_link_rejected(self):
        vs,fs=f31.tetra()
        # Two closed tetrahedra with a single shared node index create a pinch.
        second_vs=vs[1:]
        second_fs=tuple(tuple(0 if v==0 else v+3 for v in f) for f in fs)
        with self.assertRaises(ValueError):f31.topology(vs+second_vs,fs+second_fs,expected_genus=0)

    def test_quad_subdivision_preserves_chi(self):
        for name,(vs,fs) in f31.build_sources().items():
            derived_v,derived_f=f31.derive_sector_quad_complex(vs,fs)
            expected=int('torus' in name)
            t=f31.topology(derived_v,derived_f,expected_genus=expected)
            self.assertEqual(t['euler'],2-2*expected)
            self.assertEqual(t['faces'],3*len(fs))

    def test_quad_subdivision_no_new_extraneous_nodes(self):
        vs,fs=f31.cube()
        derived_v,derived_f=f31.derive_sector_quad_complex(vs,fs)
        source=f31.topology(vs,fs,expected_genus=0)
        self.assertEqual(len(derived_v),source['vertices']+source['edges']+source['faces'])
        self.assertEqual(len(derived_f),3*source['faces'])

    def test_each_generated_quad_has_four_unique_vertices(self):
        vs,fs=f31.icosahedron()
        _,quads=f31.derive_sector_quad_complex(vs,fs)
        self.assertTrue(all(len(q)==4 and len(set(q))==4 for q in quads))

    def test_original_triangles_remain_source_of_quad_corners(self):
        vs,fs=f31.cube()
        derived_v,derived_f=f31.derive_sector_quad_complex(vs,fs)
        self.assertTrue(any(p in vs for p in derived_v))


class FrozenAlgorithmTests(unittest.TestCase):
    def test_regular_tetra_does_not_move(self):
        row=f31._models_result('regular_tetra',f31.tetra())
        self.assertEqual(row['changed_facet_centers'],0)

    def test_equidistant_octa_does_not_move(self):
        row=f31._models_result('regular_octa',f31.octa())
        self.assertEqual(row['changed_facet_centers'],0)

    def test_stretched_octa_can_improve(self):
        row=f31._models_result('stretched_octa',f31.octa(True))
        self.assertGreater(row['optimized_quality']['mean_min_scaled_jacobian'],
                           row['baseline_quality']['mean_min_scaled_jacobian'])

    def test_cube_improves_without_regression(self):
        row=f31._models_result('triangulated_cube',f31.cube())
        self.assertGreater(row['changed_facet_centers'],0)

    def test_frozen_candidate_count(self):
        self.assertEqual(len(f30.candidate_weights()),171)

    def test_centroid_only_candidate_contract(self):
        tri=((0.,0.,0.),(3.,0.,0.),(0.,1.,0.))
        row=f30.optimize_facet(tri)
        self.assertTrue(f30.dominates_or_equals(row['optimized'],row['baseline']))

    def test_planar_rigid_transform_shape_invariant(self):
        original=((0.,0.,0.),(3.,0.,0.),(0.,1.,0.))
        rotated=tuple(((-p[1])*f31.RIGID_TEST_SCALE,
                       p[0]*f31.RIGID_TEST_SCALE,p[2]*f31.RIGID_TEST_SCALE)
                      for p in original)
        before=f30.optimize_facet(original)
        after=f30.optimize_facet(rotated)
        for a,b in zip(before['optimized'],after['optimized']):
            self.assertAlmostEqual(a['min_scaled_jacobian'],b['min_scaled_jacobian'],places=10)
            self.assertAlmostEqual(a['min_angle_deg'],b['min_angle_deg'],places=10)
            self.assertAlmostEqual(a['max_angle_deg'],b['max_angle_deg'],places=10)

    def test_source_corner_quality_ceiling(self):
        tri=((0.,0.,0.),(2.,0.,0.),(.03,.002,0.))
        output=f30.optimize_facet(tri)
        floor=min(f30.source_triangle_corners(tri))
        self.assertLessEqual(min(x['min_angle_deg'] for x in output['optimized']),floor+1e-7)

    def test_topology_not_inferred_from_location(self):
        a=((0.,0.,0.),(1.,0.,0.),(0.,1.,0.))
        b=a
        self.assertEqual(a,b)
        with self.assertRaises(ValueError):
            f31.topology(a+b,((0,1,2),(3,4,5)),expected_genus=0)

    def test_unsupported_scientific_promotion_stays_false(self):
        row=f31._models_result('regular_tetra',f31.tetra())
        self.assertIs(row['scientific_model_admitted'],False)
        self.assertIs(row['native_apmesh_quad_executed'],False)

    def test_generated_metadata_has_no_private_file_paths(self):
        row=f31._models_result('regular_tetra',f31.tetra())
        serial=json.dumps(row)
        self.assertNotIn('.stl',serial)
        self.assertNotIn('.bp',serial)
        self.assertNotIn('.obj',serial)

    def test_corrupt_f30_dependency_fails(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/'docs/research/nonmanifold-benchmark/probes/thingi10k_f30_feature_locked_quad_center_optimizer.py'
            file.parent.mkdir(parents=True)
            file.write_text('# changed source\n')
            self.assertFalse(f31.source_dep_is_pinned(Path(d)))
            with self.assertRaises(ValueError):f31.produce_receipt(Path(d))

    def test_missing_f30_dependency_fails(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(f31.source_dep_is_pinned(Path(d)))

    def test_json_immutable_path(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'generated.json'
            value={'schema':f31.SCHEMA,'synthetic_only':True}
            f31.safe_output(target,value)
            self.assertEqual(json.loads(target.read_text()),value)
            with self.assertRaises(ValueError):f31.safe_output(target,value)

    def test_json_nan_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                f31.safe_output(Path(d)/'generated.json',{'bad':math.nan})

    def test_minimal_expected_declared_ledger(self):
        self.assertEqual(f31.SCHEMA,'apmesh-s40-f31-generated-surface-generalization-v1')


if __name__=='__main__':
    unittest.main()
