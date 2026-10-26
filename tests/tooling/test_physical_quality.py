"""Analytic XYZ geometry and corrupted CSV controls for full-precision quality."""

import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from verify_generation import inspect_physical_quality, triangle_quality


class PhysicalQualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.snapshot = Path(self.temp.name) / "snapshot.json"
        # Unit equal sides and base b give 2r/R=b*(2-b)=0.19 at b=0.1.
        thin = [[0, 0, 0], [0.1, 0, 0], [0.05, math.sqrt(1 - 0.05**2), 0]]
        right = [[0, 0, 0], [1, 0, 0], [0, 0, 1]]
        self.document = {"patches": [self.patch(0, thin), self.patch(1, right)]}
        self.right_quality = 2 * (math.sqrt(2) - 1)
        self.row = {"quality_min": "0.19", "quality_mean": format((0.19 + self.right_quality) / 2, ".6g"),
                    "poor_ratio_lt_0_30": "50", "q_ge_0_60": "50", "excellent_ratio_ge_0_80": "50"}

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def patch(index, xyz):
        # UV is equilateral for both faces: it cannot explain physical quality.
        uv = [[0, 0], [1, 0], [0.5, math.sqrt(3) / 2]]
        return {"index": index, "faces": [[0, *[[i, *p, *q] for i, (p, q) in enumerate(zip(uv, xyz))]]]}

    def inspect(self, document=None, row=None):
        self.snapshot.write_text(json.dumps(self.document if document is None else document), encoding="utf-8")
        return inspect_physical_quality(self.snapshot, self.row if row is None else row)

    def test_physical_coordinates_and_per_patch_counts(self):
        report = self.inspect()
        self.assertEqual(report["triangles"], 2)
        self.assertEqual(report["csv_fields_compared"], 5)
        self.assertEqual(report["counts"], {"poor_triangles_lt_0_30": 1, "good_triangles_ge_0_60": 1,
                                            "excellent_triangles_ge_0_80": 1})
        self.assertEqual([p["poor_triangles_lt_0_30"] for p in report["patches"]], [1, 0])
        self.assertAlmostEqual(report["quality_min"], 0.19)

    def test_each_wrong_quality_field_is_detected(self):
        for field in self.row:
            with self.subTest(field=field):
                row = {**self.row, field: "1" if field.startswith("quality_") else "0"}
                with self.assertRaisesRegex(ValueError, field):
                    self.inspect(row=row)

    def test_ratios_are_percentages_not_fractions(self):
        with self.assertRaisesRegex(ValueError, "poor_ratio"):
            self.inspect(row={**self.row, "poor_ratio_lt_0_30": "0.5"})

    def test_nonfinite_and_out_of_range_values_fail(self):
        for value in ("nan", "inf", "1e999", "-1", "101"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.inspect(row={**self.row, "q_ge_0_60": value})

    def test_missing_quality_column_fails(self):
        row = dict(self.row)
        row.pop("poor_ratio_lt_0_30")
        with self.assertRaises(KeyError):
            self.inspect(row=row)

    def test_six_digit_rounding_is_supported_but_adjacent_wrong_value_fails(self):
        self.inspect()
        with self.assertRaisesRegex(ValueError, "quality_mean"):
            self.inspect(row={**self.row, "quality_mean": "0.509215"})

    def test_threshold_ambiguity_does_not_qualify_a_count(self):
        for threshold in (0.3, 0.6, 0.8):
            base = 1 - math.sqrt(1 - threshold)
            xyz = [[0, 0, 0], [base, 0, 0], [base / 2, math.sqrt(1 - base**2 / 4), 0]]
            with self.subTest(threshold=threshold), self.assertRaisesRegex(ValueError, "numerically unresolved"):
                self.inspect(document={"patches": [self.patch(0, xyz)]})

    def test_analytic_quality_under_scale_and_rigid_rotation(self):
        for scale in (1e-100, 1, 1e100):
            right = [[0, 0, 0], [scale / math.sqrt(2), scale / math.sqrt(2), 0], [0, 0, scale]]
            equilateral = [[0, 0, 0], [scale, 0, 0], [scale / 2, 0, math.sqrt(3) * scale / 2]]
            with self.subTest(scale=scale):
                self.assertAlmostEqual(triangle_quality(right), self.right_quality)
                self.assertAlmostEqual(triangle_quality(equilateral), 1)

    def test_empty_and_degenerate_neighborhoods_fail(self):
        for document in ({"patches": []}, {"patches": [{"index": 0, "faces": []}]},
                         {"patches": [self.patch(0, [[0, 0, 0], [1, 0, 0], [2, 0, 0]])]}):
            with self.subTest(document=document), self.assertRaises(ValueError):
                self.inspect(document=document)

    def test_duplicate_snapshot_fields_fail(self):
        self.snapshot.write_text('{"patches":[],"patches":[]}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate snapshot field"):
            inspect_physical_quality(self.snapshot, self.row)


if __name__ == "__main__":
    unittest.main()
