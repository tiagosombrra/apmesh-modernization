"""Directed controls for the read-only research quality guards."""

from pathlib import Path
import sys
import tempfile
import unittest

from test_relative_feedback_requests import fixture, surface

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from quad_regional_quality_guards import GROUPS, assess_archives, assess_guards


def profile(growth=.10, angle=10, score=.2):
    return dict(max_face_growth=growth,
                regional_floors={group: dict(min_angle_deg=angle, min_shape=score)
                                 for group in GROUPS})


class RegionalQualityGuardsTests(unittest.TestCase):
    def test_above_floor_can_change_within_the_growth_budget(self):
        old = {"interior_QUAD": [(50, .8)] * 10}
        new = {"interior_QUAD": [(40, .7)] * 11}
        result = assess_guards(old, new, profile())
        self.assertEqual(result["status"], "passes_configured_guards")
        self.assertEqual(result["growth"]["fraction"], .10)
        self.assertEqual(assess_guards(old, new, profile(growth=.09))["blocking_guards"],
                         ["face_growth"])

    def test_each_minimum_below_the_floor_requires_strict_improvement(self):
        name = "contour_vertex_TRI"
        old = {name: [(5, .1)] * 2}
        new = {name: [(6, .1)] * 2}
        result = assess_guards(old, new, profile())
        self.assertEqual(result["blocking_guards"], [name + ".min_shape"])
        self.assertEqual(result["regions"][name]["min_angle_deg"]["status"], "improved_below_floor")
        new[name] = [(6, .15), (7, .14)]
        result = assess_guards(old, new, profile())
        self.assertEqual(result["status"], "passes_configured_guards")
        self.assertEqual(result["regions"][name]["min_shape"]["candidate_below_floor"], 2)

    def test_crossing_below_an_existing_floor_is_blocked(self):
        old = {"contour_edge_QUAD": [(10, .5)]}
        new = {"contour_edge_QUAD": [(9, .6)]}
        result = assess_guards(old, new, profile())
        self.assertEqual(result["blocking_guards"], ["contour_edge_QUAD.min_angle_deg"])

    def test_new_region_must_meet_its_floor(self):
        old = {"contour_edge_QUAD": [(30, .7)]}
        new = {"interior_TRI": [(9, .5)]}
        result = assess_guards(old, new, profile())
        self.assertEqual(result["blocking_guards"], ["interior_TRI.min_angle_deg"])
        self.assertEqual(result["regions"]["contour_edge_QUAD"]["min_angle_deg"]["status"], "removed")
        self.assertIsNone(result["regions"]["interior_TRI"]["min_angle_deg"]["predecessor_min"])
        self.assertEqual(result["regions"]["interior_QUAD"]["min_shape"]["status"], "absent")

    def test_every_floor_and_finite_growth_are_required(self):
        settings = profile()
        del settings["regional_floors"]["interior_TRI"]
        pair = {"interior_QUAD": [(30, .7)]}
        with self.assertRaisesRegex(ValueError, "each regional"):
            assess_guards(pair, pair, settings)
        with self.assertRaisesRegex(ValueError, "finite and nonnegative"):
            assess_guards(pair, pair, profile(growth=float("nan")))

    def test_archive_measurement_stays_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plane.obj"
            fixture(path, 1)
            content = path.read_bytes()
            evaluate = surface(1, False)
            report = assess_archives(path, path, profile(), evaluate)
            self.assertEqual(report["mixed_adaptive_epochs"], 0)
            self.assertEqual(report["guards"]["growth"]["candidate_faces"], 3)
            self.assertEqual(report["guards"]["regions"]["contour_edge_TRI"]["candidate_count"], 2)
            self.assertEqual(report["guards"]["regions"]["contour_edge_QUAD"]["candidate_count"], 1)
            self.assertEqual(report["geometric_comparison"]["48"]["candidate"]["global_error"]["sample_count"], 2304)
            self.assertEqual(path.read_bytes(), content)
            tampered = Path(directory) / "wrong_surface.obj"
            tampered.write_bytes(content.replace(b"v 0 0 0", b"v 0 0 0.01", 1))
            with self.assertRaisesRegex(ValueError, "differs from the analytic Bezier source"):
                assess_archives(path, tampered, profile(), evaluate)


if __name__ == "__main__":
    unittest.main()
