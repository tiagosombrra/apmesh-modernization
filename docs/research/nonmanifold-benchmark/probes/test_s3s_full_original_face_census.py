#!/usr/bin/env python3
"""S3.S source/native full-topology gap-census regression and adversarial tests."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import unittest

import cadquery as cq

from s3s_full_original_face_census import (
    S3R_EXPECTED_PATCHES, _has_bijection, _hex_digest, audit_report,
    classify, full_correspondence, represented_source_faces, source_gate,
)


class OriginalS40SourceNativeGapCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_dir = Path(os.environ.get("APMESH_ORIGINAL_CAD_DIR", ""))
        cls.source = source_dir / "i25o_s40.step"
        cls.bp = Path(os.environ["APMESH_S3R_BASELINE_BP"])
        cls.manifest_path = Path(os.environ["APMESH_S3R_BASELINE_MANIFEST"])
        cls.source_text, cls.source_sha = source_gate(cls.source.read_bytes())
        cls.bp_raw = cls.bp.read_bytes()
        cls.manifest = json.loads(cls.manifest_path.read_text(encoding="utf-8"))
        cls.native = cq.importers.importStep(str(cls.source)).val()
        cls.census = classify(cls.source_text, cls.native, cls.bp_raw, cls.manifest)

    def test_01_frozen_original_hash_and_model_gate(self):
        self.assertEqual(self.source_sha,
            "b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b")
        with self.assertRaisesRegex(ValueError, "only accepts"):
            source_gate(self.source.read_bytes(), model="M5")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            source_gate(self.source.read_bytes() + b"# forged")

    def test_02_native_full_face_edge_vertex_correspondence(self):
        c = self.census
        self.assertEqual((c["original_source_native_bijective_face_count"],
                          c["original_source_native_bijective_edge_count"],
                          c["original_source_native_bijective_vertex_count"]), (43, 117, 77))

    def test_03_known_original_complex_face_indices_are_stable(self):
        m = full_correspondence(self.source_text, self.native)["face_map"]
        self.assertEqual({i: m[i] for i in (218, 1519, 1986, 2457)},
                         {218: 1, 1519: 12, 1986: 17, 2457: 22})

    def test_04_same_endpoint_circles_need_source_incidence(self):
        self.assertEqual(
            self.census["original_same_endpoint_ambiguous_edges_disambiguated_by_incidence"],
            [378, 1991])
        mapping = full_correspondence(self.source_text, self.native)["edge_map"]
        self.assertNotEqual(mapping[378], mapping[1991])
        self.assertEqual((mapping[378], mapping[1991]), (10, 64))

    def test_05_no_original_three_sheet_evidence(self):
        self.assertEqual(self.census["max_original_source_edge_owner_count"], 2)
        self.assertEqual(self.census["original_source_multi_sheet_nonmanifold_3plus"], 0)

    def test_06_baseline_126_patches_17_faces_is_not_modified(self):
        self.assertEqual(self.census["baseline_integrated_patches"], S3R_EXPECTED_PATCHES)
        self.assertEqual(len(self.census["baseline_original_face_ids"]), 17)
        self.assertEqual(len(represented_source_faces(
            self.source_text, self.bp_raw, self.manifest)), 17)
        self.assertEqual(self.census["new_patches_generated"], 0)
        self.assertFalse(self.census["s3r_atlas_mutated"])

    def test_07_exact_26_original_exclusions_and_histogram(self):
        self.assertEqual(self.census["excluded_original_face_count"], 26)
        self.assertEqual(self.census["excluded_support_histogram"], {
            "PLANE": 17, "CYLINDRICAL_SURFACE": 6,
            "B_SPLINE_SURFACE_WITH_KNOTS": 2,
            "COMPLEX_RATIONAL_B_SPLINE_SURFACE": 1})
        self.assertEqual(len(self.census["classified_original_faces"]), 26)

    def test_08_original_graph_distance_matches_direct_adjacency(self):
        self.assertEqual(self.census["excluded_minimum_source_edge_hops_histogram"],
                         {"1": 15, "2": 11})
        self.assertEqual(self.census["excluded_faces_with_direct_indexed_atlas_adjacency"], 15)
        self.assertEqual(self.census["excluded_faces_without_direct_indexed_atlas_adjacency"], 11)

    def test_09_candidate_912_and_3737_are_line_only_non_hole(self):
        faces = {row["source_advanced_face_id"]: row
                 for row in self.census["classified_original_faces"]}
        for sid in (912, 3737):
            face = faces[sid]
            self.assertEqual(face["source_wire_edge_counts"], [8])
            self.assertEqual(face["3d_master_curve_histogram"], {"LINE": 8})
            self.assertEqual(face["inner_wire_count"], 0)
            self.assertEqual(face["incident_represented_edge_count"], 3)
            self.assertEqual(face["candidate_admission_status"], "NOT_GENERATED_AND_NOT_AUDITED")
        self.assertEqual([row["source_advanced_face_id"]
                          for row in self.census["classified_original_faces"][:2]],
                         [912, 3737])

    def test_10_explicit_native_geometric_and_wire_types(self):
        for row in self.census["classified_original_faces"]:
            self.assertTrue(row["native_brep_has_valid_face_shape"])
            self.assertGreaterEqual(row["source_wire_count"], 1)
            self.assertEqual(sum(row["source_wire_edge_counts"]),
                             row["source_boundary_edge_count"])
            self.assertGreaterEqual(row["inner_wire_count"], 0)
            self.assertEqual(row["source_wire_count"] - 1, row["inner_wire_count"])

    def test_11_critical_false_bijection_is_rejected(self):
        self.assertFalse(_has_bijection([1, 2], {10, 11},
                                         {1: [10], 2: [10]}))
        self.assertTrue(_has_bijection([1, 2], {10, 11},
                                        {1: [10, 11], 2: [10, 11]}))
        self.assertFalse(_has_bijection([1, 2], {10, 11, 12},
                                         {1: [10, 11], 2: [10, 11]}))

    def test_12_wrong_baseline_bp_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "BP SHA-256 mismatch"):
            represented_source_faces(self.source_text, self.bp_raw + b"1", self.manifest)

    def test_13_forged_manifest_does_not_admit_missing_hole(self):
        forged = dict(self.manifest)
        forged["source_inner_hole_retained"] = False
        with self.assertRaisesRegex(ValueError, "hole"):
            represented_source_faces(self.source_text, self.bp_raw, forged)

    def test_14_original_report_digest_derived_from_actual_rows(self):
        check = deepcopy(self.census)
        digest = check.pop("report_sha256")
        self.assertEqual(digest, _hex_digest(check))
        self.assertEqual(len({x["source_advanced_face_id"] for x in
                              check["classified_original_faces"]}), 26)

    def test_15_adversarial_forged_priority_receipt_is_rejected(self):
        altered = deepcopy(self.census)
        altered["classified_original_faces"][0]["research_priority_score_heuristic"] += 900
        with self.assertRaisesRegex(ValueError, "checksum"):
            audit_report(self.source_text, self.native, self.bp_raw, self.manifest, altered)
        altered["report_sha256"] = _hex_digest({k: v for k, v in altered.items()
                                                if k != "report_sha256"})
        with self.assertRaisesRegex(ValueError, "differs from"):
            audit_report(self.source_text, self.native, self.bp_raw, self.manifest, altered)

    def test_16_independent_report_recomputation_passes(self):
        result = audit_report(self.source_text, self.native, self.bp_raw,
                              self.manifest, self.census)
        self.assertEqual(result, {"audit_pass": True,
                                  "source_faces_checked": 43,
                                  "source_edges_checked": 117,
                                  "excluded_faces_checked": 26})

    def test_17_no_derived_original_coordinate_payload(self):
        content = self.census
        text = json.dumps(content, sort_keys=True)
        self.assertNotIn("control_vertex_ids", text)
        self.assertNotIn("native_uv_rectangle", text)
        self.assertNotIn("source_step_text", text)
        self.assertNotIn("vertices_xyz", text)
        self.assertEqual(content["apmesh_tri_quad_meshing"], "NOT_RUN")
        self.assertEqual(content["production_cpp_regression"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
