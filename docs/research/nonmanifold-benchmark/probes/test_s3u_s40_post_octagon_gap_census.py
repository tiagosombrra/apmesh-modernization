#!/usr/bin/env python3
"""Regression and negative controls for the frozen original S40 S3.U census."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest

import cadquery as cq

from s3s_full_original_face_census import _hex_digest
from s3u_s40_post_octagon_gap_census import (
    EXPECTED_CONTROLS, EXPECTED_FACES, EXPECTED_OPEN_SIDES, EXPECTED_PATCHES,
    EXPECTED_PENDING, EXPECTED_REPRESENTED, EXPECTED_SEAMS,
    NEXT_CIRCLE_PLANAR_IDS, NEXT_CURVED_PLANAR_IDS, ODD_LINE_ONLY_IDS,
    S3R_BP_SHA256, S3T_BP_SHA256,
    _admitted_faces, _partition_preflight, _verify_pinned_inputs,
    audit_post_octagon, classify_post_octagon,
)
from s3s_full_original_face_census import full_correspondence, source_gate


class S3UOriginalS40PostOctagonCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_dir = Path(os.environ["APMESH_ORIGINAL_CAD_DIR"])
        cls.bp_dir = Path(os.environ["APMESH_S3T_PRIVATE_DIR"])
        cls.source = cls.source_dir / "i25o_s40.step"
        cls.source_bytes = cls.source.read_bytes()
        cls.bp_bytes = (cls.bp_dir / "s40_planar_octagons.partial.bp").read_bytes()
        cls.manifest = json.loads((cls.bp_dir / "s40_planar_octagons_manifest.json").read_text())
        cls.s3r_bytes = (cls.bp_dir / "s40_218_conforming.partial.bp").read_bytes()
        cls.s3r_manifest = json.loads((cls.bp_dir / "s40_218_conforming_manifest.json").read_text())
        cls.native = cq.importers.importStep(str(cls.source)).val()
        cls.report = classify_post_octagon(cls.source_bytes, cls.native, cls.bp_bytes,
                                           cls.manifest, cls.s3r_bytes, cls.s3r_manifest)
        cls.by_id = {r["source_advanced_face_id"]:r for r in cls.report["pending_faces"]}

    def build(self, *, source=None, bp=None, manifest=None, s3r=None, s3r_manifest=None, native=None):
        return classify_post_octagon(
            source if source is not None else self.source_bytes,
            native if native is not None else self.native,
            bp if bp is not None else self.bp_bytes,
            manifest if manifest is not None else self.manifest,
            s3r if s3r is not None else self.s3r_bytes,
            s3r_manifest if s3r_manifest is not None else self.s3r_manifest)

    def test_01_original_source_sha_and_s3t_frozen_bp(self):
        self.assertEqual(sha256(self.source_bytes).hexdigest(),
                         "b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b")
        self.assertEqual(sha256(self.bp_bytes).hexdigest(), S3T_BP_SHA256)
        self.assertEqual(sha256(self.s3r_bytes).hexdigest(), S3R_BP_SHA256)

    def test_02_exact_source_native_correspondence(self):
        self.assertEqual((self.report["native_correlated_face_count"],
                          self.report["native_correlated_edge_count"],
                          self.report["native_correlated_vertex_count"]), (43,117,77))

    def test_03_previous_132_patch_prefix_and_seams_are_frozen(self):
        r = self.report
        self.assertEqual((r["prior_integrated_patch_count"],
                          r["prior_integrated_declared_control_count"],
                          r["prior_integrated_original_face_count"]),
                         (EXPECTED_PATCHES, EXPECTED_CONTROLS, EXPECTED_REPRESENTED))
        self.assertEqual((self.manifest["global_two_sided_indexed_seams"],
                          self.manifest["global_open_indexed_sides"]),
                         (EXPECTED_SEAMS, EXPECTED_OPEN_SIDES))
        self.assertTrue(r["original_hole_face_218_preserved_by_frozen_s3t_prefix"])

    def test_04_coverage_is_disjoint_and_exhaustive(self):
        covered = set(self.report["covered_source_face_ids"])
        missing = set(self.by_id)
        self.assertEqual((len(covered),len(missing),len(covered|missing)), (19,24,43))
        self.assertFalse(covered & missing)
        self.assertTrue({912,3737,218,1519,1986,2457} <= covered)

    def test_05_24_pending_support_classes(self):
        self.assertEqual(self.report["pending_source_support_histogram"], {
            "PLANE":15, "CYLINDRICAL_SURFACE":6,
            "B_SPLINE_SURFACE_WITH_KNOTS":2,
            "COMPLEX_RATIONAL_B_SPLINE_SURFACE":1})

    def test_06_new_source_incidence_reaches_18_pending_faces(self):
        self.assertEqual(self.report["pending_with_direct_source_edge_to_existing_atlas"],18)
        self.assertEqual(self.report["pending_without_direct_source_edge_to_existing_atlas"],6)
        self.assertEqual(self.report["pending_original_minimum_hops_histogram"],{"1":18,"2":6})

    def test_07_first_four_priorities_are_stable_source_ids(self):
        ids = [r["source_advanced_face_id"] for r in self.report["pending_faces"][:4]]
        self.assertEqual(ids,[17,2092,1279,1386])
        self.assertEqual(self.report["prioritized_next_candidate_source_faces"], [17,2092])
        self.assertEqual(self.report["analytic_arc_alternative_source_faces"], [1279,1386])

    def test_08_four_sided_original_spline_faces_have_no_holes(self):
        expected = {17:85,2092:2096}
        for sid,eid in expected.items():
            row = self.by_id[sid]
            self.assertEqual(row["original_boundary_edge_count"],4)
            self.assertEqual(row["inner_wire_count"],0)
            self.assertEqual(row["original_spline_edge_curve_id"],eid)
            self.assertEqual(row["3d_bspline_edge_count"],1)
            self.assertEqual(row["incident_represented_edge_count"],4)
            self.assertEqual(row["admission_status"],"NOT_GENERATED_OR_ACCEPTED")

    def test_09_sampled_original_3d_bspline_on_native_plane(self):
        for sid in NEXT_CURVED_PLANAR_IDS:
            row = self.by_id[sid]
            self.assertEqual(row["native_original_spline_samples"],33)
            self.assertLess(row["native_original_spline_support_max_sampled_mm"],1e-8)
            self.assertGreater(row["native_original_spline_support_max_sampled_mm"],0.0)
            self.assertEqual(row["original_master_3d_bspline_degree"], 5)

    def test_10_original_circle_neighbors_are_not_silently_treated_as_lines(self):
        for sid in NEXT_CIRCLE_PLANAR_IDS:
            row=self.by_id[sid]
            self.assertEqual(row["3d_circle_edge_count"],2)
            self.assertEqual(row["original_boundary_edge_count"],6)
            self.assertEqual(row["incident_represented_edge_count"],3)
            self.assertEqual(row["partition_preflight"],
                             "CIRCULAR_BOUNDARY_APPROXIMATION_AND_QUAD_PARTITION_REQUIRED")

    def test_11_odd_line_boundaries_cannot_close_as_quads_without_refinement(self):
        for sid in ODD_LINE_ONLY_IDS:
            row=self.by_id[sid]
            self.assertEqual(row["original_boundary_edge_count"],5)
            self.assertEqual(row["3d_master_curve_histogram"],{"LINE":5})
            self.assertEqual(row["partition_preflight"],
                             "ODD_BOUNDARY_REQUIRES_SPLIT_OR_STEINER_VERTEX")
        for edges in (3,5,7,9):
            x={"inner_wire_count":0, "support_type":"PLANE", "source_wire_count":1,
               "3d_bspline_edge_count":0,"source_boundary_edge_count":edges,
               "3d_circle_edge_count":0}
            self.assertEqual(_partition_preflight(x),"ODD_BOUNDARY_REQUIRES_SPLIT_OR_STEINER_VERTEX")

    def test_12_native_original_has_no_3plus_edge_nonmanifold_positive(self):
        self.assertEqual(self.report["source_edge_max_distinct_face_owners"],2)
        self.assertEqual(self.report["source_original_3plus_incident_edges"],0)

    def test_13_source_forgeries_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"SHA-256 mismatch"):
            self.build(source=self.source_bytes+b"\n#injected")
        with self.assertRaisesRegex(ValueError,"SHA-256 mismatch"):
            self.build(source=self.source_bytes.replace(b"HEADER;",b"HEADER ",1))

    def test_14_bp_mutation_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"S3.T BP SHA-256 mismatch"):
            self.build(bp=self.bp_bytes+b"\n")

    def test_15_s3r_parent_mutation_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"S3.R BP SHA-256 mismatch"):
            self.build(s3r=self.s3r_bytes+b"\n")

    def test_16_manifest_forged_coverage_rejected(self):
        fake=deepcopy(self.manifest)
        fake["source_original_faces_represented"]=20
        with self.assertRaisesRegex(ValueError,"manifest mismatches"):
            self.build(manifest=fake)

    def test_17_manifest_missing_hole_flag_rejected(self):
        fake=deepcopy(self.manifest)
        fake["source_inner_hole_retained"]=False
        with self.assertRaisesRegex(ValueError,"manifest mismatches"):
            self.build(manifest=fake)

    def test_18_manifest_forged_original_edge_list_rejected(self):
        fake=deepcopy(self.manifest)
        fake["source_to_original_face_ids"]["912"][0]=-1
        with self.assertRaisesRegex(ValueError,"lost original STEP boundaries"):
            self.build(manifest=fake)

    def test_19_manifest_relaxed_budget_rejected(self):
        fake=deepcopy(self.manifest)
        fake["numerical_budget_mm"]=0.1
        with self.assertRaisesRegex(ValueError,"manifest mismatches"):
            self.build(manifest=fake)

    def test_20_native_wrong_model_rejected(self):
        # A different native shape cannot impersonate original S40 topology.
        other=cq.Workplane("XY").box(3,3,3).val()
        with self.assertRaises(ValueError):
            self.build(native=other)

    def test_21_receipt_hash_is_canonical(self):
        cleaned=deepcopy(self.report)
        checksum=cleaned.pop("receipt_sha256")
        self.assertEqual(checksum,_hex_digest(cleaned))
        self.assertEqual(len(self.report["pending_faces"]),EXPECTED_PENDING)

    def test_22_forged_receipt_without_hash_fails(self):
        fake=deepcopy(self.report)
        fake["pending_faces"][0]["admission_status"]="ACCEPTED"
        with self.assertRaisesRegex(ValueError,"content hash mismatch"):
            audit_post_octagon(self.source_bytes,self.native,self.bp_bytes,self.manifest,
                               self.s3r_bytes,self.s3r_manifest,fake)

    def test_23_forged_receipt_with_recalculated_hash_fails(self):
        fake=deepcopy(self.report)
        fake["pending_faces"][0]["incident_represented_edge_count"]+=1
        cleaned=deepcopy(fake)
        cleaned.pop("receipt_sha256")
        fake["receipt_sha256"]=_hex_digest(cleaned)
        with self.assertRaisesRegex(ValueError,"differs from original native"):
            audit_post_octagon(self.source_bytes,self.native,self.bp_bytes,self.manifest,
                               self.s3r_bytes,self.s3r_manifest,fake)

    def test_24_independent_recomputation_passes(self):
        result=audit_post_octagon(self.source_bytes,self.native,self.bp_bytes,
                                  self.manifest,self.s3r_bytes,self.s3r_manifest,self.report)
        self.assertEqual(result["status"],"PASS")
        self.assertEqual((result["source_faces_checked"],result["source_edges_checked"],
                          result["source_vertices_checked"],result["pending_faces_checked"]),
                         (43,117,77,24))

    def test_25_research_only_no_new_geometry_or_original_data_leak(self):
        self.assertEqual(self.report["new_bp_patches_generated"],0)
        self.assertEqual(self.report["new_source_faces_admitted"],0)
        self.assertEqual(self.report["apmesh_tri_quad_mesh_generation"],"NOT_RUN")
        self.assertEqual(self.report["production_cpp_regression"],"NOT_RUN")
        out=json.dumps(self.report,sort_keys=True)
        for forbidden in ("vertices_xyz","source_step_text","bp_control_positions",
                          "native_uv_coordinate_grid"):
            self.assertNotIn(forbidden,out)


if __name__ == "__main__":
    unittest.main()
