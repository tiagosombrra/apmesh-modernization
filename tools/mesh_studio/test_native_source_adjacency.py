"""R2.7.14 source incidence tests: synthetic graph contracts, not mesh evidence."""

import unittest

from tools.mesh_studio.native_source_adjacency import analyze_source_incidences
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def patch(slot, curves, observers=None, native_id_override=None):
    """Build an explicitly synthetic source patch incidence test record."""
    observers = observers or {}
    native_id_override = native_id_override or {}
    return {
        "type": "patch",
        "patch_slot": slot,
        "source_curves": [
            {
                "edge_slot": edge,
                "source_curve_slot": curve,
                "native_curve_id": native_id_override.get(curve, curve + 100),
                "reversed": bool((slot + edge) % 2),
                "reported_curve_patch_observers": observers.get(curve, 1),
            }
            for edge, curve in enumerate(curves)
        ],
    }


def synthetic(curves, *patches):
    return [{"type": "accepted_commit", "source_curve_count": curves}, *patches]


class TestOriginalSourceAdjacency(unittest.TestCase):
    def test_four_patch_source_graph_is_counted_without_welding_claim(self):
        overlaps = {1: 2, 2: 2, 3: 2}
        records = synthetic(
            13,
            patch(0, [0, 1, 2, 3], overlaps),
            patch(1, [1, 4, 5, 6], overlaps),
            patch(2, [2, 7, 8, 9], overlaps),
            patch(3, [3, 10, 11, 12], overlaps),
        )
        graph = analyze_source_incidences(records)
        self.assertEqual(graph["source_curve_count"], 13)
        self.assertEqual(graph["total_source_curve_incidences"], 16)
        self.assertEqual(graph["source_curve_ownership_classes"], {
            "single_patch": 10, "two_patch": 3, "three_or_more_patches": 0})
        self.assertEqual(len(graph["source_patch_pair_adjacencies"]), 3)
        self.assertEqual(graph["source_curve_observer_count_disagreements"], [])
        self.assertFalse(graph["shared_curve_geometry_or_welded_node_continuity_verified"])
        self.assertFalse(graph["cross_epoch_face_curve_descendants_verified"])

    def test_three_patch_source_curve_is_flagged_not_welded(self):
        records = synthetic(
            6,
            patch(0, [0, 1, 2, 3], {0: 3}),
            patch(1, [0, 4], {0: 3}),
            patch(2, [0, 5], {0: 3}),
        )
        graph = analyze_source_incidences(records)
        self.assertEqual(graph["source_curve_ownership_classes"]["three_or_more_patches"], 1)
        self.assertEqual(len(graph["source_patch_pair_adjacencies"]), 3)
        self.assertFalse(graph["shared_curve_geometry_or_welded_node_continuity_verified"])

    def test_repeated_curve_on_one_patch_stays_explicit(self):
        records = synthetic(
            3,
            patch(0, [0, 0, 1], {0: 1}),
            patch(1, [2]),
        )
        graph = analyze_source_incidences(records)
        self.assertEqual(graph["source_curve_slots_with_repeated_same_patch_incidence"], [0])
        self.assertEqual(graph["source_curve_ownership_classes"]["two_patch"], 0)

    def test_observer_count_disagreement_is_diagnostic_only(self):
        graph = analyze_source_incidences(synthetic(
            3, patch(0, [0, 1], {0: 4}),
            patch(1, [0, 2], {0: 4})))
        self.assertEqual(len(graph["source_curve_observer_count_disagreements"]), 1)
        self.assertEqual(graph["source_curve_observer_count_disagreements"][0][
            "unique_source_patches"], 2)

    def test_native_curve_ids_cannot_disagree_for_same_source_slot(self):
        with self.assertRaises(NativeLineageValidationError):
            analyze_source_incidences(synthetic(
                3, patch(0, [0, 1]),
                patch(1, [0, 2], native_id_override={0: 999})))

    def test_missing_source_curve_is_rejected(self):
        with self.assertRaises(NativeLineageValidationError):
            analyze_source_incidences(synthetic(4, patch(0, [0, 1, 2])))

    def test_patch_record_order_does_not_change_adjacency(self):
        first = patch(0, [0, 1, 2], {0: 2})
        second = patch(1, [0, 3], {0: 2})
        a = analyze_source_incidences(synthetic(4, first, second))
        b = analyze_source_incidences(synthetic(4, second, first))
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
