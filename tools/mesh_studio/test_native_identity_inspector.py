"""R2.7.19 synthetic manifest contracts are NOT native scientific evidence."""

from __future__ import annotations

from copy import deepcopy
import unittest

from tools.mesh_studio.native_identity_inspector import (
    SCHEMA, build_native_inspector_bundle,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def synthetic_inputs():
    """Create source-sized mock read-only curve and accepted corner receipts."""
    correlations = {"original_models": {}}
    native = {"original_models": {}}
    summaries = {}
    for model, count, source_curves in (
        ("eistute", 4, 13), ("book", 28, 85),
    ):
        rows = []
        for ordinal in range(2):
            members = [{
                "patch_slot": patch,
                "edge_slot": 3,
                "original_native_node_id": (1000 + patch if ordinal == 0 else 2000),
                "original_canonical_t": float(ordinal),
                "original_xyz": [float(ordinal), 0.0, 0.0],
            } for patch in range(count)]
            rows.append({
                "source_scoped_sample_reference": {
                    "accepted_step": 1, "source_curve_slot": 3,
                    "sample_ordinal_within_this_step": ordinal,
                    "namespace": "read_only_original_source_sample_not_native_id",
                },
                "reference_canonical_t": float(ordinal),
                "logical_node_id_relation": (
                    "different_native_logical_id_in_every_source_patch"
                    if ordinal == 0 else
                    "same_native_logical_id_in_all_source_patches"),
                "original_native_members": members,
            })
        correlations["original_models"][model] = [{
            "original_native_accepted_step": 1,
            "original_source_ndjson_sha256": "a" * 64,
            "source_scoped_curve_correspondences": [{
                "pairwise_geometry_qualified": True,
                "original_source_curve_slot": 3,
                "original_native_curve_id": 50,
                "source_owner_patch_slots": list(range(count)),
                "read_only_seam_sample_groups": rows,
            }],
        }]
        native["original_models"][model] = {
            "original_runtime_stderr_sha256": "d" * 64,
            "original_native_accepted_snapshots": [{
                "original_accepted_step": 1,
                "original_native_source_sha256": "a" * 64,
                "direct_accepted_cpp_ownership": {
                    "actual_accepted_owner_rows": [{
                        "patch_slot": patch,
                        "original_native_node_id": 1000 + patch,
                        "has_actual_accepted_triangle_adjacency": True,
                        "same_cpp_owner_pointer_as_earlier_patch": False,
                    } for patch in range(count)],
                    "triangle_submesh_owner_adjacencies_observed": count,
                    "same_cpp_owner_pointer_as_earlier_patch_count": 0,
                },
                "original_provisional_adapter_closure_correlations": {
                    "all_original_provisional_closure_events": count,
                },
            }],
        }
        summaries[model] = {
            "real_model_input_sha256": "b" * 64,
            "native_config_source_sha256": "c" * 64,
        }
    return correlations, native, summaries


class TestNativeIdentityInspectorBundle(unittest.TestCase):
    def test_preserves_source_ids_without_global_welding(self):
        output = build_native_inspector_bundle(*synthetic_inputs())
        self.assertEqual(output["schema"], SCHEMA)
        self.assertFalse(output["scientific_lod_qualified"])
        self.assertFalse(output["new_globally_welded_node_ids_created"])
        for doc in output["documents"]:
            count = doc["source_patch_count"]
            curve = doc["qualified_shared_source_curves"][0]
            self.assertEqual(len(curve["patch_slots"]), count)
            self.assertEqual(len(curve["sample_groups"]), 2)
            first = curve["sample_groups"][0]
            self.assertEqual(len(first["members"]), count)
            self.assertEqual(len({
                row["native_node_id"] for row in first["members"]}), count)
            self.assertTrue(all(
                row["accepted_corner_cpp_owner_observed"] is True and
                row["accepted_corner_shared_cpp_pointer_with_earlier_patch"] is False
                for row in first["members"]))
            self.assertTrue(all(
                row["accepted_corner_cpp_owner_observed"] is None and
                row["accepted_corner_shared_cpp_pointer_with_earlier_patch"] is None
                for row in curve["sample_groups"][1]["members"]))

    def test_original_source_hash_mismatch_rejected(self):
        candidate = synthetic_inputs()
        candidate[1]["original_models"]["book"][
            "original_native_accepted_snapshots"][0][
                "original_native_source_sha256"] = "z" * 64
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2719_original_native_source_sha_join"):
            build_native_inspector_bundle(*candidate)

    def test_foreign_member_patch_is_rejected(self):
        candidate = synthetic_inputs()
        curve = candidate[0]["original_models"]["eistute"][0][
            "source_scoped_curve_correspondences"][0]
        curve["read_only_seam_sample_groups"][1][
            "original_native_members"][0]["patch_slot"] = 88
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2719_member_has_foreign_patch"):
            build_native_inspector_bundle(*candidate)

    def test_missing_member_refuses_nonwelded_source_manifest(self):
        candidate = synthetic_inputs()
        curve = candidate[0]["original_models"]["book"][0][
            "source_scoped_curve_correspondences"][0]
        curve["read_only_seam_sample_groups"][0]["original_native_members"].pop()
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2719_incomplete_original_source_sample"):
            build_native_inspector_bundle(*candidate)

    def test_forged_native_accepted_corner_id_rejected(self):
        candidate = synthetic_inputs()
        candidate[1]["original_models"]["eistute"][
            "original_native_accepted_snapshots"][0][
                "direct_accepted_cpp_ownership"][
                    "actual_accepted_owner_rows"][0]["original_native_node_id"] = 9
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2719_corner_sample_id_not_real"):
            build_native_inspector_bundle(*candidate)

    def test_unqualified_curve_never_creates_source_sample_groups(self):
        candidate = synthetic_inputs()
        candidate[0]["original_models"]["book"][0][
            "source_scoped_curve_correspondences"][0][
                "pairwise_geometry_qualified"] = False
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2719_missing_qualified"):
            build_native_inspector_bundle(*candidate)


if __name__ == "__main__":
    unittest.main()
