"""Synthetic controls for automatic post-smoothing seed-layer planning."""

from collections import Counter
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from quad_auto_seed_layer import directed_ring, find_layout, find_layouts, patches, quad_rank, select


FLOORS = {
    "TRI": {"min_angle_deg": 15, "min_shape": 0.125},
    "QUAD": {"min_angle_deg": 22.5, "min_shape": 0.25},
}
UV = [(0, 0), (1, 0), (1, 1), (0, 1), (0.01, 0.01)]
RING = (0, 1, 2, 3)


def flat_normal(_point):
    return 0, 0, 1


def xyz(uv):
    return [(u, v, 0) for u, v in uv]


class AutoSeedLayerTests(unittest.TestCase):
    def layout(self, inner=(), claims=(), cap=1):
        return find_layout(RING, inner, UV, xyz(UV), flat_normal, FLOORS,
                           claims, cap, Counter())

    def test_constructs_one_quad_at_fixed_sites(self):
        self.assertEqual(self.layout(), (RING,))

    def test_rank_prefers_quad_retention_then_face_count_then_quality(self):
        tris = ((0, 1, 2), (0, 2, 3))
        layouts = tuple(find_layouts(RING, (), UV, xyz(UV), flat_normal, FLOORS, [], 2, Counter()))
        self.assertEqual(layouts[0], tris)
        self.assertEqual(min(layouts, key=lambda trial: quad_rank((RING,), trial, 1.0)), (RING,))
        self.assertLess(quad_rank((RING,), tris, 1.0),
                        quad_rank((RING,), tris + ((1, 2, 3),), 2.0))
        self.assertLess(quad_rank((RING,), tris, 2.0), quad_rank((RING,), tris, 1.0))

    def test_rejects_unattainable_physical_request(self):
        self.assertIsNone(self.layout(claims=[((0.5, 0.5), 0.5)], cap=3))

    def test_does_not_drop_a_required_inner_site(self):
        self.assertIsNone(self.layout(inner=(4,), cap=4))

    def test_rejects_face_budget_below_minimum(self):
        self.assertIsNone(self.layout(cap=0))

    def test_rejects_disconnected_directed_boundary(self):
        self.assertFalse(directed_ring([(0, 1, 2), (3, 4, 5)]))

    def test_expands_front_and_uses_only_edge_adjacent_seed_faces(self):
        adjacency = [{1, 3}, {0, 4}, {3}, {0, 2, 4}, {1, 3}]
        self.assertEqual(list(patches(3, adjacency, 3)),
                         [(0, 3), (2, 3), (0, 2, 3), (0, 3, 4), (1, 3, 4),
                          (2, 3, 4), (0, 1, 3, 4), (0, 2, 3, 4), (1, 2, 3, 4),
                          (0, 1, 2, 3, 4)])

    def test_first_shape_violation_is_selected_with_same_rule(self):
        uv = [(0, 0), (0.45, 0), (0.45, 1), (0, 1), (1, 0), (1, 1), (0.46, 0.5)]
        faces = [(0, 1, 2, 3), (1, 4, 6), (4, 5, 6), (5, 2, 6), (2, 1, 6)]
        result, counts = select(faces, 1, uv, uv, xyz(uv), flat_normal, FLOORS, [], {6}, 5)
        self.assertEqual((result["target"], result["rank"], result["retired"]), (4, 1, ()))
        self.assertEqual(set(result["replaced"]), {0, 1, 2, 4})
        self.assertTrue(any(6 in face for face in result["replacement"]))
        self.assertGreater(counts["retention_trials"], 1)
        locked, counts = select(faces, 1, uv, uv, xyz(uv), flat_normal, FLOORS, [], {6}, 1)
        self.assertIsNone(locked)
        self.assertFalse(counts["bound"])

    def test_passing_mesh_does_not_trigger_replacement(self):
        result, counts = select([RING], 1, UV, UV, xyz(UV), flat_normal, FLOORS, [], set(), 1)
        self.assertIsNone(result)
        self.assertEqual(counts["ranked_faces"], 0)

    def test_ranked_search_keeps_the_first_target_and_protected_site(self):
        uv = [(0, 0), (0.45, 0), (0.45, 1), (0, 1), (1, 0), (1, 1), (0.46, 0.5)]
        faces = [(0, 1, 2, 3), (1, 4, 6), (4, 5, 6), (5, 2, 6), (2, 1, 6)]
        data = (faces, 1, uv, uv, xyz(uv), flat_normal, FLOORS, [], {6}, 5)
        first, _ = select(*data)
        selected, counts = select(*data, retain_quads_from=first)
        self.assertEqual(selected["target"], first["target"])
        self.assertNotIn(6, selected["retired"])
        self.assertLessEqual(counts["chosen_rank"], counts["first_rank"])
        self.assertGreater(counts["feasible_witnesses"], 0)
        with patch("quad_auto_seed_layer.MAX_STATES", 0):
            fallback, counts = select(*data, retain_quads_from=first)
        self.assertEqual(fallback, first)
        self.assertTrue(counts["bound"])


if __name__ == "__main__":
    unittest.main()
