"""Closed-form UV distributions and deliberately incorrect report controls."""

import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from verify_generation import inspect_parametric_quality


class ParametricQualityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.snapshot = Path(self.temp.name) / "snapshot.json"
        # Equal sides 1 and base 0.1 give q=b*(2-b)=0.19. The other two
        # triangles have the closed-form right-isosceles and equilateral q.
        self.uv = [[[0, 0], [0.1, 0], [0.05, math.sqrt(1 - 0.05**2)]],
                   [[0, 0], [1, 0], [0, 1]],
                   [[0, 0], [1, 0], [0.5, math.sqrt(3) / 2]]]
        right = 2 * (math.sqrt(2) - 1)
        self.mean = (0.19 + right + 1) / 3
        self.std = math.sqrt(sum((q - self.mean)**2 for q in (0.19, right, 1)) / 2)
        values = dict(min=0.19, p05=0.19 + 0.1 * (right - 0.19), p50=right,
                      p95=right + 0.9 * (1 - right), max=1, mean=self.mean, std=self.std,
                      poor_ratio_lt_0_30=100 / 3, q_ge_0_60=200 / 3, excellent_ratio_ge_0_80=200 / 3)
        self.row = {"quality_uv_" + field: format(value, ".6g") for field, value in values.items()}

    def tearDown(self):
        self.temp.cleanup()

    def inspect(self, uv=None, row=None):
        physical = [[0, 0, 0], [1, 0, 0], [0, 0, 1]]
        faces = [[index, *[[3 * index + k, *p, *physical[k]] for k, p in enumerate(points)]]
                 for index, points in enumerate(self.uv if uv is None else uv)]
        self.snapshot.write_text(json.dumps({"patches": [{"index": 0, "faces": faces}]}), encoding="utf-8")
        return inspect_parametric_quality(self.snapshot, self.row if row is None else row)

    def test_all_statistics_use_uv_and_report_integer_counts(self):
        report = self.inspect()
        self.assertEqual(report["csv_fields_compared"], 10)
        self.assertEqual(report["counts"], {"poor_triangles_lt_0_30": 1, "good_triangles_ge_0_60": 2,
                                            "excellent_triangles_ge_0_80": 2})
        self.assertAlmostEqual(report["statistics"]["min"], 0.19)
        self.assertAlmostEqual(report["statistics"]["mean"], self.mean)
        self.assertAlmostEqual(report["statistics"]["std"], self.std)
        self.assertEqual(report["patches"][0]["poor_triangles_lt_0_30"], 1)

    def test_each_false_uv_field_fails(self):
        for field in self.row:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                self.inspect(row={**self.row, field: "0"})

    def test_sample_standard_deviation_is_not_population_deviation(self):
        with self.assertRaisesRegex(ValueError, "quality_uv_std"):
            self.inspect(row={**self.row, "quality_uv_std": str(self.std * math.sqrt(2 / 3))})

    def test_percentiles_use_linear_n_minus_one_positions(self):
        with self.assertRaisesRegex(ValueError, "quality_uv_p05"):
            self.inspect(row={**self.row, "quality_uv_p05": "0.19"})

    def test_one_triangle_has_zero_standard_deviation(self):
        row = {"quality_uv_" + key: "1" for key in ("min", "p05", "p50", "p95", "max", "mean")}
        row.update(quality_uv_std="0", quality_uv_poor_ratio_lt_0_30="0",
                   quality_uv_q_ge_0_60="100", quality_uv_excellent_ratio_ge_0_80="100")
        self.assertEqual(self.inspect(uv=[self.uv[2]], row=row)["statistics"]["std"], 0)

    def test_percentages_are_not_fractions(self):
        with self.assertRaisesRegex(ValueError, "quality_uv_q_ge_0_60"):
            self.inspect(row={**self.row, "quality_uv_q_ge_0_60": str(2 / 3)})

    def test_nonfinite_and_out_of_range_fields_fail(self):
        for value in ("nan", "inf", "1e999", "-1", "2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.inspect(row={**self.row, "quality_uv_mean": value})

    def test_missing_uv_column_fails(self):
        row = dict(self.row)
        row.pop("quality_uv_p50")
        with self.assertRaises(KeyError):
            self.inspect(row=row)

    def test_native_zero_guard_domain_is_not_qualified_as_good_quality(self):
        for scale in (0, 1e-9):
            points = [[scale * u, scale * v] for u, v in self.uv[2]]
            with self.subTest(scale=scale), self.assertRaisesRegex(ValueError, "nondegenerate metric domain"):
                self.inspect(uv=[points])

    def test_threshold_ambiguity_is_unqualified(self):
        for threshold in (0.3, 0.6, 0.8):
            base = 1 - math.sqrt(1 - threshold)
            points = [[0, 0], [base, 0], [base / 2, math.sqrt(1 - base**2 / 4)]]
            with self.subTest(threshold=threshold), self.assertRaisesRegex(ValueError, "numerically unresolved"):
                self.inspect(uv=[points])

    def test_adjacent_incorrect_six_digit_mean_fails(self):
        value = format(float(self.row["quality_uv_mean"]) + 1e-6, ".6g")
        with self.assertRaisesRegex(ValueError, "quality_uv_mean"):
            self.inspect(row={**self.row, "quality_uv_mean": value})

    def test_empty_snapshot_is_not_quality_evidence(self):
        self.snapshot.write_text('{"patches":[]}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "contains no triangles"):
            inspect_parametric_quality(self.snapshot, self.row)


if __name__ == "__main__":
    unittest.main()
