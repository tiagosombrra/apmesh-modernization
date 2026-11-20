"""R2.7.17 negative controls use synthetic records, not actual C++ evidence."""

from __future__ import annotations

from copy import deepcopy
import unittest

from tools.mesh_studio.native_corner_origin import (
    HEADER_CONTRACT, accepted_uv00_corner, analyze_real_corner_source,
    source_corner_endpoint,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def endpoint(identifier, index, t, xyz=None):
    """Represent a bounded original native curve point-list endpoint."""
    return {
        "stored_index": index, "stored_parameter": t,
        "original_sample_id": identifier,
        "xyz": list(xyz if xyz is not None else [0.0, 0.0, 0.0]),
    }


def incidence(edge, curve_slot, first, last, reversed_incidence=False):
    return {
        "edge_slot": edge, "source_curve_slot": curve_slot,
        "native_curve_id": 100 + curve_slot,
        "reversed": reversed_incidence,
        "reported_curve_patch_observers": 2 if curve_slot == 3 else 1,
        "r2717_original_curve_endpoints": [
            endpoint(first, 0, 0.0), endpoint(last, 4, 1.0)],
    }


def records():
    """Create two synthetic patch corners sharing curve slot 3."""
    rows = [{
        "type": "accepted_commit", "source_patch_count": 2,
        "source_curve_count": 7, "r2717_corner_observer": HEADER_CONTRACT,
    }]
    for patch in range(2):
        curves = [0, 1, 2, 3] if patch == 0 else [4, 5, 6, 3]
        edges = []
        for edge, slot in enumerate(curves):
            first = 99 if slot == 3 else 10 + patch * 10 if edge == 0 else 200 + slot
            last = 300 + slot
            if slot == 3:
                last = 399
            edges.append(incidence(edge, slot, first, last))
        rows.append({
            "type": "patch", "patch_slot": patch,
            "source_curves": edges,
        })
        rows.append({
            "type": "face", "patch_slot": patch,
            "vertices": [
                {"uv": [0.0, 0.0],
                 "native_node_id": 10 + 10 * patch, "xyz": [0.0, 0.0, 0.0]},
                {"uv": [1.0, 0.0],
                 "native_node_id": 400 + patch, "xyz": [1.0, 0.0, 0.0]},
                {"uv": [0.0, 1.0],
                 "native_node_id": 500 + patch, "xyz": [0.0, 1.0, 0.0]},
            ],
        })
    return rows


class TestNativeCornerOrigin(unittest.TestCase):
    def test_closing_corner_matches_edge0_but_not_shared_edge3(self):
        result = analyze_real_corner_source(records())
        self.assertEqual(result["original_source_patch_count"], 2)
        self.assertEqual(result["original_source_curve_count"], 7)
        self.assertEqual(result["accepted_id_matches_source_edge0"], 2)
        self.assertEqual(result["accepted_id_matches_source_edge3"], 0)
        self.assertEqual(result["accepted_xyz_matches_source_edge0"], 2)
        self.assertEqual(result["accepted_xyz_matches_source_edge3"], 2)
        self.assertFalse(result["actual_native_shared_cpp_node_pointers_certified"])
        self.assertFalse(result["scientific_lod_qualified"])

    def test_reversed_source_incidence_uses_last_stored_sample(self):
        edge = incidence(3, 3, 77, 88, reversed_incidence=True)
        self.assertEqual(source_corner_endpoint(edge)["original_sample_id"], 88)

    def test_natively_matching_edge3_corner_is_measured_not_assumed(self):
        rows = records()
        rows[2]["vertices"][0]["native_node_id"] = 99
        result = analyze_real_corner_source(rows)
        self.assertEqual(result["accepted_id_matches_source_edge0"], 1)
        self.assertEqual(result["accepted_id_matches_source_edge3"], 1)

    def test_missing_cpp_postcommit_instrumentation_is_rejected(self):
        rows = records()
        del rows[0]["r2717_corner_observer"]
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2717_missing_original_cpp"):
            analyze_real_corner_source(rows)

    def test_missing_source_sample_observation_is_rejected(self):
        rows = records()
        del rows[1]["source_curves"][0]["r2717_original_curve_endpoints"]
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2717_source_curve_endpoints_missing"):
            analyze_real_corner_source(rows)

    def test_shared_canonical_curve_must_have_same_source_samples(self):
        rows = records()
        rows[3]["source_curves"][3]["r2717_original_curve_endpoints"][0][
            "original_sample_id"] = 888
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2717_shared_original_curve"):
            analyze_real_corner_source(rows)

    def test_ambiguous_uv00_accepted_corner_is_rejected(self):
        rows = records()
        forged = deepcopy(rows[2]["vertices"][0])
        forged["native_node_id"] = 901
        rows[2]["vertices"].append(forged)
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2717_missing_or_ambiguous"):
            analyze_real_corner_source(rows)

    def test_source_parameters_must_be_finite_and_bounded(self):
        curve = incidence(0, 0, 1, 2)
        curve["r2717_original_curve_endpoints"][0]["stored_parameter"] = float("nan")
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2717_invalid_original"):
            source_corner_endpoint(curve)

    def test_same_original_corner_id_cannot_have_different_xyz(self):
        faces = [
            {"patch_slot": 0, "vertices": [
                {"uv": [0, 0], "native_node_id": 1, "xyz": [0, 0, 0]}]},
            {"patch_slot": 0, "vertices": [
                {"uv": [0, 0], "native_node_id": 1, "xyz": [0, 0, 0.2]}]},
        ]
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2717_native_corner_id_xyz"):
            accepted_uv00_corner(faces, 0)


if __name__ == "__main__":
    unittest.main()
