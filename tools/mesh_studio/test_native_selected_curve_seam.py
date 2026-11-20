"""Synthetic-only source curve pointer-incidence and TRI seam audit tests.

These are software integrity fixtures, not real Eistute observations.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from tools.mesh_studio.native_selected_curve_seam import (
    attest,
    accepted_canonical_source_incidence,
    observed_original_curve_groups,
    symmetric_seam_pair,
    tri_source_edge_geometry,
)
from tools.mesh_studio.test_native_selected_tri_return import (
    fake_tri_sidecar,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError

ROOT = Path(__file__).resolve().parents[2]


def fake_accepted_incidence() -> bytes:
    """Source geometry with exactly one original four-patch shared curve."""
    faces = [{
        "type": "accepted_commit", "step": 1,
        "source_patch_count": 4, "source_curve_count": 13,
    }]
    for patch in range(4):
        slots = [0, 1, 2, 3] if patch == 0 else [
            4 + 3 * (patch - 1) + j for j in range(3)] + [3]
        faces.append({
            "type": "patch", "patch_slot": patch,
            "source_curves": [
                {"edge_slot": i, "source_curve_slot": s, "reversed": False}
                for i, s in enumerate(slots)],
        })
    return ("\n".join(json.dumps(row) for row in faces) + "\n").encode()


def synthetic_curve_observations():
    """Four repeated observation cohorts; native pointer labels are permuted."""
    accepted = accepted_canonical_source_incidence(fake_accepted_incidence())
    # The original pointer first-encounter order is intentionally noncanonical.
    remap = {i: (i + 5) % 13 for i in range(13)}
    by_patch = {}
    for source_slot, signature in accepted.items():
        for patch, edge, reverse in signature:
            by_patch[patch, edge] = {
                "edge_slot": edge,
                "source_object_group": remap[source_slot],
                "native_curve_id": 0,
                "reversed": reverse,
                "source_curve_points": 20,
                "source_endpoint_xyz": [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
            }
    all_selected = []
    for repeat in range(4):
        for patch in range(4):
            all_selected.append({
                "return": {
                    "return_index": 25 + repeat * 4 + patch,
                    "patch": patch,
                },
                "geometry": {
                    "curves": [by_patch[patch, edge].copy()
                               for edge in range(4)],
                },
            })
    return all_selected


class OriginalNativeCurveAndSeamSyntheticTests(unittest.TestCase):
    def test_preregistered_source_and_separate_elf_probe_attested(self):
        source = attest(ROOT)
        self.assertIn("src/adapter/adapter.cpp", source)

    def test_real_original_step1_synthetic_incidence_is_not_native_id(self):
        slots = accepted_canonical_source_incidence(fake_accepted_incidence())
        self.assertEqual(len(slots), 13)
        self.assertEqual(len(slots[3]), 4)
        self.assertEqual({p for p, _, _ in slots[3]}, set(range(4)))

    def test_source_pointer_ordinal_maps_by_incidence_not_native_id(self):
        observations = synthetic_curve_observations()
        original = accepted_canonical_source_incidence(fake_accepted_incidence())
        result = observed_original_curve_groups(observations, original)
        self.assertEqual(result["original_unique_source_objects_seen"], 13)
        self.assertEqual(result["shared_source_original_curve_slots"], [3])
        self.assertEqual(
            result["source_object_group_to_original_accepted_curve_slot"]["8"], 3)
        self.assertFalse(result["source_original_curve_cpp_pointer_address_serialized"])

    def test_incorrect_original_curve_count_is_rejected(self):
        wrong = fake_accepted_incidence().replace(
            b'"source_curve_count": 13', b'"source_curve_count": 12')
        with self.assertRaises(NativeLineageValidationError):
            accepted_canonical_source_incidence(wrong)

    def test_duplicate_accepted_patch_edge_is_rejected(self):
        wrong = fake_accepted_incidence().replace(
            b'"edge_slot": 1', b'"edge_slot": 0', 1)
        with self.assertRaises(NativeLineageValidationError):
            accepted_canonical_source_incidence(wrong)

    def test_forged_accepted_curve_slot_is_rejected(self):
        wrong = fake_accepted_incidence().replace(
            b'"source_curve_slot": 12', b'"source_curve_slot": 13')
        with self.assertRaises(NativeLineageValidationError):
            accepted_canonical_source_incidence(wrong)

    def test_inconsistent_native_source_object_for_same_edge_rejected(self):
        obs = synthetic_curve_observations()
        obs[5]["geometry"]["curves"][0]["source_object_group"] = 12
        original = accepted_canonical_source_incidence(fake_accepted_incidence())
        with self.assertRaises(NativeLineageValidationError):
            observed_original_curve_groups(obs, original)

    def test_curve_object_not_same_as_accepted_source_incidence_rejected(self):
        obs = synthetic_curve_observations()
        obs[0]["geometry"]["curves"][3]["source_object_group"] = 0
        original = accepted_canonical_source_incidence(fake_accepted_incidence())
        with self.assertRaises(NativeLineageValidationError):
            observed_original_curve_groups(obs, original)

    def test_exact_discrete_xyz_sets_still_not_physical_welding(self):
        points = {(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)}
        result = symmetric_seam_pair(points, points)
        self.assertTrue(result["exact_double_vertex_set_equal"])
        self.assertEqual(result["max_vertex_to_vertex_xyz_distance"], 0)
        self.assertTrue(result["no_continuous_geometric_hausdorff_bound"])
        self.assertTrue(result["no_physical_source_node_welding_asserted"])

    def test_discrete_xyz_partial_mismatch_is_retained(self):
        a = {(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)}
        b = {(0.0, 0.0, 0.0), (1.0, 0.0, 1.0)}
        result = symmetric_seam_pair(a, b)
        self.assertFalse(result["exact_double_vertex_set_equal"])
        self.assertGreater(result["max_vertex_to_vertex_xyz_distance"], 0)
        self.assertLess(result["exact_double_vertex_jaccard"], 1)

    def test_empty_source_boundary_does_not_get_fabricated(self):
        a = {(0.0, 0.0, 0.0)}
        b = {(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)}
        with self.assertRaises(NativeLineageValidationError):
            symmetric_seam_pair(a, b)

    def test_nonfinite_source_curve_endpoint_is_rejected(self):
        returned = {
            "return_index": 1, "step": 4, "retry": 0, "patch": 0,
            "local": 0, "outer_epoch": 6, "outer_retry": 0,
            "faces": 10, "nodes": 11,
        }
        raw = json.loads(fake_tri_sidecar(returned).splitlines()[0])
        for index, source in enumerate(raw["source_curves"]):
            source["source_object_group"] = index
            source["source_endpoint_xyz"] = [[0.0, 0.0, 0.0],
                                             [1.0, 0.0, 0.0]]
        raw["source_curves"][0]["source_endpoint_xyz"][0][0] = float("nan")
        rows = [raw] + [
            json.loads(line) for line in fake_tri_sidecar(returned)
            .splitlines()[1:]]
        data = ("\n".join(json.dumps(row, allow_nan=True) for row in rows) +
                "\n").encode()
        with self.assertRaises(NativeLineageValidationError):
            tri_source_edge_geometry(data, returned)

    def test_original_tri_free_boundary_not_assigned_to_uv_side_without_evidence(self):
        returned = {
            "return_index": 1, "step": 4, "retry": 0, "patch": 0,
            "local": 0, "outer_epoch": 6, "outer_retry": 0,
            "faces": 10, "nodes": 11,
        }
        raw = json.loads(fake_tri_sidecar(returned).splitlines()[0])
        for index, source in enumerate(raw["source_curves"]):
            source["source_object_group"] = index
            source["source_endpoint_xyz"] = [[0.0, 0.0, 0.0],
                                             [1.0, 0.0, 0.0]]
        rows = [raw] + [
            json.loads(line) for line in fake_tri_sidecar(returned)
            .splitlines()[1:]]
        data = ("\n".join(json.dumps(row) for row in rows) + "\n").encode()
        record = tri_source_edge_geometry(data, returned)
        self.assertEqual(record["unclassified_free_edges"], 10)
        self.assertEqual(sum(x["edges"] for x in
                             record["sides"].values()), 0)


if __name__ == "__main__":
    unittest.main()
