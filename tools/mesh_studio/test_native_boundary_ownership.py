"""Synthetic R2.7.18 source and pointer observer contracts, not mesh evidence."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.mesh_studio.native_boundary_ownership import (
    CLOSE_PREFIX, OWNER_HEADER, analyze_accepted_cpp_owners,
    match_provisional_closure, read_actual_adapter_events,
)
from tools.mesh_studio.test_native_corner_origin import records
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def synthetic_native():
    """Attach invented C++ pointer comparison results to synthetic R2.7.17."""
    rows = records()
    rows[0]["r2718_owner_observer"] = OWNER_HEADER
    for patch in (row for row in rows if row["type"] == "patch"):
        patch["node_count"] = 3
        patch["r2718_accepted_cpp_node_owner"] = {
            "native_node_id": 10 + patch["patch_slot"] * 10,
            "submesh_node_slot": 0,
            "triangle_has_actual_owner_adjacency": True,
            "cpp_owner_reused_between_previous_patch_submeshes": False,
            "cpp_owner_same_as_edge0_source_point": False,
            "cpp_owner_same_as_edge3_source_point": False,
            "original_edge0_and_edge3_source_points_are_same_cpp_object": False,
        }
    return rows


def synthetic_event(patch, node_id, attempt=0):
    """Invent a provisional closure event with explicit nonacceptance."""
    edge3_id = 99
    return {
        "adaptive_step": 1, "retry_index": 0, "local_attempt": attempt,
        "patch_index": patch, "actual_boundary_close_returned": True,
        "boundary_vertex_count": 12, "first_uv": [0.0, 0.0],
        "last_uv": [0.0, 0.1], "first_mapped_native_node_id": node_id,
        "edge0_original_source_local_t0_id": node_id,
        "edge3_original_source_local_t0_id": edge3_id,
        "first_vertex_maps_to_edge0_source_id": True,
        "first_vertex_maps_to_edge3_source_id": node_id == edge3_id,
        "first_vertex_was_reused_by_boundary_close": True,
        "is_globally_accepted_commit": False,
    }


def native_stderr(*events):
    """Simulate original stderr bytes without claiming actual native execution."""
    return (
        "Native preamble\n" +
        "".join(CLOSE_PREFIX + json.dumps(ev) + "\n" for ev in events)
    ).encode("utf-8")


class TestNativeBoundaryOwner(unittest.TestCase):
    def test_accepted_node_is_actual_submesh_owner_and_not_welded(self):
        owner = analyze_accepted_cpp_owners(synthetic_native())
        self.assertEqual(owner["triangle_submesh_owner_adjacencies_observed"], 2)
        self.assertEqual(owner["same_cpp_owner_pointer_as_earlier_patch_count"], 0)
        self.assertEqual(owner["same_cpp_owner_as_source_edge0_count"], 0)
        self.assertEqual(owner["same_cpp_owner_as_source_edge3_count"], 0)
        self.assertFalse(owner["cross_epoch_cpp_pointer_persistence_proven"])

    def test_provisional_original_close_observations_are_not_commits(self):
        events = read_actual_adapter_events(
            native_stderr(synthetic_event(0, 10), synthetic_event(1, 20)),
            "eistute")
        owner = analyze_accepted_cpp_owners(synthetic_native())
        joined = match_provisional_closure(owner, events, 1)
        self.assertEqual(joined["patches_with_matching_provisional_closure"], 2)
        self.assertEqual(joined["all_original_provisional_closure_events"], 2)
        self.assertFalse(joined["actual_accepted_attempt_pointers_stable_since_closure_proven"])
        self.assertFalse(joined["accepted_patch_correlations"][0][
            "which_local_attempt_was_eventually_accepted_proven"])

    def test_different_local_attempts_are_never_counted_as_accepted(self):
        events = read_actual_adapter_events(
            native_stderr(synthetic_event(0, 10, 0),
                          synthetic_event(0, 10, 1),
                          synthetic_event(1, 999, 2)), "eistute")
        joined = match_provisional_closure(analyze_accepted_cpp_owners(
            synthetic_native()), events, 1)
        self.assertEqual(joined["patches_with_matching_provisional_closure"], 1)
        self.assertEqual(joined["accepted_patch_correlations"][0][
            "same_id_provisional_boundary_closures"], 2)
        self.assertEqual(joined["accepted_patch_correlations"][1][
            "same_id_provisional_boundary_closures"], 0)

    def test_fake_globally_accepted_close_is_rejected(self):
        ev = synthetic_event(0, 10)
        ev["is_globally_accepted_commit"] = True
        with self.assertRaises(NativeLineageValidationError):
            read_actual_adapter_events(native_stderr(ev), "eistute")

    def test_fake_cpp_owner_adjacency_is_rejected(self):
        rows = synthetic_native()
        rows[1]["r2718_accepted_cpp_node_owner"][
            "triangle_has_actual_owner_adjacency"] = False
        with self.assertRaises(NativeLineageValidationError):
            analyze_accepted_cpp_owners(rows)

    def test_mismatching_owner_native_logical_id_is_rejected(self):
        rows = synthetic_native()
        rows[1]["r2718_accepted_cpp_node_owner"]["native_node_id"] = 888
        with self.assertRaises(NativeLineageValidationError):
            analyze_accepted_cpp_owners(rows)

    def test_out_of_bounds_submesh_node_slot_is_rejected(self):
        rows = synthetic_native()
        rows[1]["r2718_accepted_cpp_node_owner"]["submesh_node_slot"] = 9
        with self.assertRaises(NativeLineageValidationError):
            analyze_accepted_cpp_owners(rows)

    def test_unobserved_cpp_owner_is_rejected(self):
        rows = synthetic_native()
        del rows[0]["r2718_owner_observer"]
        with self.assertRaises(NativeLineageValidationError):
            analyze_accepted_cpp_owners(rows)

    def test_adapter_event_id_boolean_mismatch_is_rejected(self):
        ev = synthetic_event(1, 20)
        ev["first_vertex_maps_to_edge3_source_id"] = True
        with self.assertRaises(NativeLineageValidationError):
            read_actual_adapter_events(native_stderr(ev), "eistute")

    def test_injected_duplicate_json_event_field_is_rejected(self):
        text = json.dumps(synthetic_event(0, 10))[:-1] + ', "patch_index": 1}'
        with self.assertRaisesRegex(
                NativeLineageValidationError, "duplicate_json_key_patch_index"):
            read_actual_adapter_events((CLOSE_PREFIX + text + "\n").encode(), "eistute")

    def test_missing_real_adapter_event_is_rejected(self):
        with self.assertRaises(NativeLineageValidationError):
            read_actual_adapter_events(b"only unrelated diagnostics\n", "eistute")

    def test_false_cpp_pointer_reuse_is_diagnostic_not_topology_certification(self):
        rows = synthetic_native()
        rows[3]["r2718_accepted_cpp_node_owner"][
            "cpp_owner_reused_between_previous_patch_submeshes"] = True
        owner = analyze_accepted_cpp_owners(rows)
        self.assertEqual(owner["same_cpp_owner_pointer_as_earlier_patch_count"], 1)
        self.assertTrue(owner["native_node_ids_are_not_cpp_addresses"])


if __name__ == "__main__":
    unittest.main()
