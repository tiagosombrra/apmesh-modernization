from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from quad_transition_comparison import compare

SQUARE = ((0, 0), (1, 0), (1, 1), (0, 1))
REGION = ((0.25, 0.25), (0.5, 0.25), (0.5, 0.5), (0.25, 0.5))


def plane(u, v):
    return (u, v, 0), (1, 0, 0), (0, 1, 0)


def write_mesh(path, faces, positions=SQUARE):
    lines = [f"v {u} {v} 0" for u, v in positions] + [f"vt {u} {v}" for u, v in positions]
    lines.extend("f " + " ".join(f"{i}/{i}" for i in f) for f in faces)
    path.write_text("\n".join(lines)+"\n", encoding="ascii")


class TransitionComparisonTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.a = Path(directory.name) / "baseline.obj"
        self.b = Path(directory.name) / "candidate.obj"
        write_mesh(self.a, ((1, 2, 3), (1, 3, 4)))
        write_mesh(self.b, ((1, 2, 3, 4),))

    def test_shared_sites_and_shape_when_tri_region_becomes_quad(self):
        result = compare(self.a, self.b, REGION, plane)
        self.assertTrue(result["same_ordered_contour_edges"])
        a, b = result["baseline"], result["candidate"]
        self.assertEqual(a["regional_error"]["sample_count"], 576)
        self.assertEqual(b["regional_error"]["sample_count"], 576)
        self.assertEqual(a["regional_error"]["tri_sites"], 576)
        self.assertEqual(b["regional_error"]["quad_sites"], 576)
        self.assertLess(a["regional_error"]["max_xyz"], 1e-14)
        self.assertLess(b["regional_error"]["max_xyz"], 1e-14)
        self.assertEqual(a["regional_shape"]["by_kind"]["TRI"]["uv_area_fraction"], 1)
        self.assertEqual(b["regional_shape"]["by_kind"]["QUAD"]["uv_area_fraction"], 1)
        self.assertEqual(b["regional_shape"]["minimum_angle"], 90)

    def test_reports_a_changed_curve_partition_with_equal_shape(self):
        positions = ((0, 0), (.5, 0), (1, 0), (1, 1), (.5, 1), (0, 1))
        write_mesh(self.b, ((1, 2, 5, 6), (2, 3, 4, 5)), positions)
        result = compare(self.a, self.b, REGION, plane)
        self.assertFalse(result["same_ordered_contour_edges"])

    def test_rejects_reversed_face_and_foreign_lift(self):
        write_mesh(self.b, ((1, 4, 3, 2),))
        with self.assertRaises(ValueError):
            compare(self.a, self.b, REGION, plane)
        write_mesh(self.b, ((1, 2, 3, 4),))
        self.b.write_text(self.b.read_text().replace("v 1 1 0", "v 1 1 1"), encoding="ascii")
        with self.assertRaisesRegex(ValueError, "analytic Bezier"):
            compare(self.a, self.b, REGION, plane)

    def test_rejects_nonconvex_and_uncovered_regions(self):
        with self.assertRaisesRegex(ValueError, "convex"):
            compare(self.a, self.b, REGION[::-1], plane)
        write_mesh(self.b, ((1, 2, 3),), SQUARE[:3])
        with self.assertRaisesRegex(ValueError, "coverage"):
            compare(self.a, self.b, REGION, plane)


if __name__ == "__main__":
    unittest.main()
