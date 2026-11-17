"""R2.7.16 synthetic contracts; no invented mesh or native epoch evidence."""

import copy
import unittest

from tools.mesh_studio.native_seam_correspondence import (
    build_curve_correspondence, build_original_correspondence,
)
from tools.mesh_studio.native_seam_samples import analyze_sampled_seams
from tools.mesh_studio.test_native_seam_samples import source


def single_curve(reversed_incidence=True, drift=0.0, middle_node=2):
    """Use the explicitly synthetic TRI/UV side fixture from R2.7.15."""
    observed = analyze_sampled_seams(source(
        reversed_incidence=reversed_incidence,
        drift=drift,
        right_second_id=middle_node))
    return observed["shared_original_source_seams"][0]


class TestNonweldedCorrespondence(unittest.TestCase):
    def test_canonical_sample_group_preserves_native_ids(self):
        curve = build_curve_correspondence(single_curve(), step=1)
        self.assertTrue(curve["pairwise_geometry_qualified"])
        self.assertEqual(curve["seam_sample_groups"], 3)
        self.assertEqual(curve["logical_node_id_relation_counts"], {
            "same_native_logical_id_in_all_source_patches": 3})
        self.assertEqual(
            [m["original_native_node_id"] for m in
             curve["read_only_seam_sample_groups"][1]["original_native_members"]],
            [2, 2])
        self.assertFalse(curve["cpp_node_objects_welded"])
        self.assertFalse(curve["new_global_native_node_id_allocated"])
        self.assertFalse(curve["cross_epoch_descendant_identity_certified"])

    def test_matching_xyz_can_legitimately_have_different_native_ids(self):
        curve = build_curve_correspondence(
            single_curve(middle_node=222), step=1)
        self.assertTrue(curve["pairwise_geometry_qualified"])
        self.assertEqual(curve["logical_node_id_relation_counts"], {
            "different_native_logical_id_in_every_source_patch": 1,
            "same_native_logical_id_in_all_source_patches": 2,
        })
        members = curve["read_only_seam_sample_groups"][1]["original_native_members"]
        self.assertEqual([m["original_native_node_id"] for m in members],
                         [2, 222])
        self.assertEqual(members[0]["original_xyz"], members[1]["original_xyz"])

    def test_xyz_drift_refuses_to_invent_sample_correspondence(self):
        curve = build_curve_correspondence(
            single_curve(drift=0.01), step=1)
        self.assertFalse(curve["pairwise_geometry_qualified"])
        self.assertEqual(curve["read_only_seam_sample_groups"], [])
        self.assertIn("nonqualification_reason", curve)

    def test_broken_source_edge_chain_refuses_correspondence(self):
        records = source()
        records.pop()
        observed = analyze_sampled_seams(records)
        curve = build_curve_correspondence(
            observed["shared_original_source_seams"][0], step=1)
        self.assertFalse(curve["pairwise_geometry_qualified"])
        self.assertEqual(curve["read_only_seam_sample_groups"], [])

    def test_epoch_reference_is_snapshot_local_not_native_identity(self):
        curve = build_curve_correspondence(single_curve(), step=7)
        ref = curve["read_only_seam_sample_groups"][0][
            "source_scoped_sample_reference"]
        self.assertEqual(ref["accepted_step"], 7)
        self.assertEqual(ref["source_curve_slot"], 0)
        self.assertEqual(ref["sample_ordinal_within_this_step"], 0)
        self.assertEqual(ref["namespace"],
                         "read_only_original_source_sample_not_native_id")

    def test_derived_report_preserves_source_shas_and_no_weld_flags(self):
        observed = analyze_sampled_seams(source(middle_node=222))
        original = {
            "original_native_models": {
                "synthetic": [{
                    "original_native_accepted_step": 1,
                    "original_native_source_sha256": "a" * 64,
                    "sampled_boundary": observed,
                }]
            }
        }
        out = build_original_correspondence(original)
        snapshot = out["original_models"]["synthetic"][0]
        self.assertEqual(snapshot["original_source_ndjson_sha256"], "a" * 64)
        self.assertEqual(snapshot["qualified_nonwelded_source_curves"], 1)
        self.assertEqual(snapshot["sample_correspondence_groups"], 3)
        self.assertFalse(snapshot["physical_mesh_node_welding_certified"])
        self.assertFalse(out["scientific_lod_qualified"])
        self.assertFalse(out["synthetic_global_node_id_was_created"])

    def test_order_is_deterministic_for_identical_native_records(self):
        self.assertEqual(
            build_curve_correspondence(single_curve(), 1),
            build_curve_correspondence(single_curve(), 1))


if __name__ == "__main__":
    unittest.main()
