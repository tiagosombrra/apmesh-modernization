"""Targeted controls for the explicitly parameterized relative feedback trigger."""

from collections import defaultdict
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from quad_adjacent_group_selector import (
    _transition_seed, edge_set, geometric_size_requests, transition_size_requests,
)
from quad_generation_metrics import load_physical_obj


def surface(scale, curved):
    def evaluate(u, v):
        width = (u - .5) * (1 - u) if curved and u > .5 else 0
        derivative = 1.5 - 2 * u
        return ((scale * u, scale * v, scale * width**2 * v),
                (scale, 0, scale * 2 * width * derivative * v),
                (0, scale, scale * width**2))
    return evaluate


def fixture(path, scale, *, transition_ring=False):
    if transition_ring:
        uv = ((0, 0), (1, 0), (1, 1), (0, 1),
              (.375, .375), (.625, .375), (.625, .625), (.375, .625))
        faces = ((4, 5, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
                 (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7))
        sides = (0, 1, 2, 3)
    else:
        uv = ((0, 0), (.5, 0), (1, 0), (1, 1), (.5, 1), (0, 1))
        faces = ((0, 1, 4, 5), (1, 2, 3), (1, 3, 4))
        sides = (0, 0, 1, 2, 2, 3)
    rows = []
    for i, ((u, v), side) in enumerate(zip(uv, sides)):
        x, y = uv[(i + 1) % len(sides)]
        uv_mid = ((u + x) / 2, (v + y) / 2)
        t = u if side % 2 == 0 else v
        arc = abs(x - u) + abs(y - v)
        rows.append("# source_site " + " ".join(map(str, (side, t, u, v, i + 1, scale * u,
                                                          scale * v, 0, *uv_mid, arc, -1))))
    rows.extend(f"v {scale * u} {scale * v} 0" for u, v in uv)
    rows.extend(f"vt {u} {v}" for u, v in uv)
    rows.extend("f " + " ".join(f"{i + 1}/{i + 1}" for i in face) for face in faces)
    path.write_text("\n".join(rows) + "\n", encoding="ascii")


class RelativeFeedbackTests(unittest.TestCase):
    def test_exact_plane_stays_fixed_in_relative_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "flat.obj"
            fixture(path, 1)
            evaluate = surface(1, False)
            legacy_faces, legacy_curves = geometric_size_requests(path, evaluate)
            self.assertEqual((len(legacy_faces), len(legacy_curves)), (3, 2))
            self.assertEqual(geometric_size_requests(path, evaluate, relative_tolerance=0), ([], []))

    def test_curved_face_requests_propagate_to_flat_neighbor_and_rescale(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "curved.obj"
            fixture(path, 1)
            face_requests, curve_requests = geometric_size_requests(path, surface(1, True),
                                                                     relative_tolerance=0)
            self.assertIn(0, [row["face"] for row in face_requests])
            self.assertTrue(curve_requests)
            self.assertEqual(geometric_size_requests(path, surface(1, True),
                                                     relative_tolerance=1), ([], []))
            fixture(path, 8)
            scaled_faces, scaled_curves = geometric_size_requests(path, surface(8, True),
                                                                   relative_tolerance=0)
            self.assertEqual([dict(row, h=row["h"] * 8) for row in face_requests], scaled_faces)
            self.assertEqual([dict(row, h=row["h"] * 8, previous_size=row["previous_size"] * 8)
                              for row in curve_requests], scaled_curves)

    def test_invalid_tolerance_fails_before_the_input_is_read(self):
        for value in (-1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "finite and nonnegative"):
                geometric_size_requests(Path("not-read.obj"), relative_tolerance=value)

    def test_transition_seed_has_no_action_on_an_inactive_plane(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "flat.obj"
            fixture(path, 1, transition_ring=True)
            self.assertEqual(transition_size_requests(path, surface(1, False),
                                                     relative_tolerance=0), ([], [], None))

    def test_transition_seed_does_not_repeat_a_geometric_curve_request(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mixed.obj"
            fixture(path, 1, transition_ring=True)
            evaluate = surface(1, True)
            kwargs = dict(relative_tolerance=0)
            before_faces, before_curves = geometric_size_requests(path, evaluate, **kwargs)
            faces, curves, seed = transition_size_requests(path, evaluate, **kwargs)
            self.assertEqual(len(before_curves), 4)
            self.assertEqual((faces, curves, seed), (before_faces, before_curves, None))

    def test_transition_seed_uses_physical_sizes_and_respects_reserved_intervals(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mixed.obj"

            def select(scale, reserved):
                fixture(path, scale, transition_ring=True)
                xyz, _, faces = load_physical_obj(path)
                owners = defaultdict(list)
                for index, face in enumerate(faces):
                    for edge in edge_set(face):
                        owners[edge].append(index)
                return _transition_seed(xyz, faces, owners, (0, 1, 2, 3),
                                        [scale] * 4, reserved)

            seed = select(1, {0})
            self.assertGreater(seed["ratio"], 1.35)
            self.assertEqual(seed["interval"], 1)
            self.assertEqual(seed["h"], .5)
            self.assertIsNone(select(1, {0, 1, 2, 3}))
            scaled = select(8, {0})
            self.assertEqual(scaled["interval"], seed["interval"])
            self.assertEqual(scaled["face"], seed["face"])
            self.assertAlmostEqual(scaled["h"], 8 * seed["h"])


if __name__ == "__main__":
    unittest.main()
