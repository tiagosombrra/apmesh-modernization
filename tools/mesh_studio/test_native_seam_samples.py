"""R2.7.15 seam-matching unit tests use synthetic faces, never accepted models."""

import copy
import unittest

from tools.mesh_studio.native_seam_samples import (
    analyze_sampled_seams, close_xyz, compare_two_sides, extract_native_side,
    side_parameter,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def side_uv(slot, t):
    """Mirror the four original Adapter UV side equations."""
    return [[t, 0.0], [1.0, t], [t, 1.0], [0.0, t]][slot]


def face(patch, slot, left_t, right_t, left_id, right_id, center_id,
         reversed_incidence=False, drift=0.0):
    """Make a synthetic original-triangle-like face with one boundary edge."""
    c0 = 1.0 - left_t if reversed_incidence else left_t
    c1 = 1.0 - right_t if reversed_incidence else right_t
    return {
        "type": "face",
        "patch_slot": patch,
        "vertices": [
            {"native_node_id": left_id, "uv": side_uv(slot, c0),
             "xyz": [left_t, drift, 0.0]},
            {"native_node_id": right_id, "uv": side_uv(slot, c1),
             "xyz": [right_t, drift, 0.0]},
            {"native_node_id": center_id, "uv": [0.5, 0.5],
             "xyz": [0.5, drift, 0.5]},
        ],
    }


def patch(patch_slot, shared_edge, reversed_incidence):
    curves = [0, 1, 2, 3] if patch_slot == 0 else [4, 5, 0, 6]
    curves[shared_edge] = 0
    return {
        "type": "patch",
        "patch_slot": patch_slot,
        "source_curves": [
            {"edge_slot": i, "source_curve_slot": slot,
             "native_curve_id": 100 if slot == 0 else 100 + slot,
             "reversed": reversed_incidence if slot == 0 else False,
             "reported_curve_patch_observers": 2 if slot == 0 else 1}
            for i, slot in enumerate(curves)
        ],
    }


def source(reversed_incidence=True, drift=0.0, right_second_id=2):
    """Create 2 original source owners and two complete shared boundary chains."""
    records = [
        {"type": "accepted_commit", "source_curve_count": 7},
        patch(0, 0, False), patch(1, 2, reversed_incidence),
    ]
    for t0, t1, l_id, r_id, c in (
        (0.0, 0.5, 1, 2, 40),
        (0.5, 1.0, 2, 3, 41),
    ):
        records.append(face(0, 0, t0, t1, l_id, r_id, c))
        patch1_lid = right_second_id if l_id == 2 else l_id
        patch1_rid = right_second_id if r_id == 2 else r_id
        records.append(face(1, 2, t0, t1, patch1_lid, patch1_rid,
                            c + 100, reversed_incidence, drift))
    return records


class TestNativeSeamSampling(unittest.TestCase):
    def test_side_equations_are_exact_original_adapter_contract(self):
        for slot in range(4):
            self.assertTrue(side_parameter(side_uv(slot, 0.27), slot)[0])
        self.assertFalse(side_parameter([0.2, 0.3], 0)[0])
        self.assertFalse(side_parameter([0.2, 0.3], 1)[0])
        with self.assertRaises(NativeLineageValidationError):
            side_parameter([0.2, 0.3], 4)

    def test_shared_reversed_source_curve_sampled_concordance(self):
        result = analyze_sampled_seams(source(reversed_incidence=True))
        self.assertEqual(result["shared_source_curve_count"], 1)
        self.assertEqual(result["pairwise_owner_edge_comparisons"], 1)
        self.assertEqual(result["pairwise_sampled_concordance_observed"], 1)
        side = result["shared_original_source_seams"][0]["native_patch_sides"][1]
        self.assertEqual([v["t"] for v in side["native_boundary_nodes"]],
                         [0.0, 0.5, 1.0])
        self.assertFalse(result["physical_node_welding_certified"])
        pair = result["shared_original_source_seams"][0][
            "pairwise_sample_comparisons"][0]
        self.assertFalse(pair["shared_physical_cpp_node_ownership_certified"])
        self.assertFalse(pair["analytic_continuous_curve_coincidence_certified"])

    def test_nonreversed_same_boundary_is_supported(self):
        result = analyze_sampled_seams(source(reversed_incidence=False))
        self.assertEqual(result["pairwise_sampled_concordance_observed"], 1)

    def test_xyz_drift_is_measured_without_mislabeling_welding(self):
        result = analyze_sampled_seams(source(drift=0.01))
        self.assertEqual(result["pairwise_sampled_concordance_observed"], 0)
        pair = result["shared_original_source_seams"][0][
            "pairwise_sample_comparisons"][0]
        self.assertTrue(pair["canonical_t_aligned_with_tolerance"])
        self.assertFalse(pair["xyz_aligned_with_explicit_tolerance"])
        self.assertAlmostEqual(pair["max_paired_xyz_delta"], 0.01)

    def test_node_id_drift_is_not_hidden_by_matching_xyz(self):
        result = analyze_sampled_seams(source(right_second_id=222))
        pair = result["shared_original_source_seams"][0][
            "pairwise_sample_comparisons"][0]
        self.assertTrue(pair["xyz_aligned_with_explicit_tolerance"])
        self.assertFalse(pair["native_logical_node_ids_equal"])
        self.assertFalse(pair["sampled_uv_xyz_logical_id_concordance_observed"])

    def test_missing_edge_is_incomplete_even_when_endpoints_appear(self):
        records = source()
        records.pop()  # Remove the second patch's last boundary segment.
        result = analyze_sampled_seams(records)
        side = result["shared_original_source_seams"][0]["native_patch_sides"][1]
        self.assertFalse(side["sampled_uv_edge_chain_complete"])
        self.assertEqual(result["pairwise_sampled_concordance_observed"], 0)

    def test_duplicate_triangle_boundary_edge_is_not_accepted(self):
        records = source()
        records.append(copy.deepcopy(records[3]))
        result = analyze_sampled_seams(records)
        side = result["shared_original_source_seams"][0]["native_patch_sides"][0]
        self.assertIn("boundary_edge_not_unique", side["edge_diagnostics"])
        self.assertEqual(result["pairwise_sampled_concordance_observed"], 0)

    def test_inconsistent_native_id_geometry_is_rejected(self):
        records = source()
        bad = copy.deepcopy(records[3])
        bad["vertices"][0]["xyz"][0] = 9.0
        records.append(bad)
        with self.assertRaises(NativeLineageValidationError):
            analyze_sampled_seams(records)

    def test_xyz_comparison_has_explicit_absolute_and_relative_tolerance(self):
        self.assertTrue(close_xyz([0.0, 0.0, 0.0], [1e-10, 0.0, 0.0]))
        self.assertFalse(close_xyz([0.0, 0.0, 0.0], [1e-4, 0.0, 0.0]))

    def test_xyz_comparison_is_translation_invariant(self):
        self.assertFalse(close_xyz(
            [1.0e12, 0.0, 0.0], [1.0e12 + 0.001, 0.0, 0.0]))
        self.assertTrue(close_xyz(
            [1.0e12, 0.0, 0.0], [1.0e12, 0.0, 0.0]))
        self.assertFalse(close_xyz(
            [0.0, 0.0, 0.0], [0.001, 0.0, 0.0]))
        self.assertTrue(close_xyz(
            [0.0, 0.0, 0.0], [1.5e-9, 0.0, 0.0],
            characteristic_length=1.0))

    def test_same_accepted_face_input_yields_deterministic_result(self):
        a = analyze_sampled_seams(source())
        b = analyze_sampled_seams(source())
        self.assertEqual(a, b)

    def test_compare_does_not_claim_welding_for_identical_sides(self):
        records = source()
        a = extract_native_side([r for r in records if r.get("type") == "face"
                                 and r["patch_slot"] == 0], 0, 0, False)
        b = copy.deepcopy(a)
        b["patch_slot"] = 1
        comparison = compare_two_sides(a, b)
        self.assertTrue(comparison["sampled_uv_xyz_logical_id_concordance_observed"])
        self.assertFalse(comparison["shared_physical_cpp_node_ownership_certified"])


if __name__ == "__main__":
    unittest.main()
