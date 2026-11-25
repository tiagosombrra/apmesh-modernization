"""Controls for progressive admission of staged research candidates."""

from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from quad_progressive_admission import GRIDS, load_profile, measure_progress, regional_metric
from quad_regional_quality_guards import GROUPS


def fixture_profile():
    # Small limits exercise the live positive path without choosing a scientific profile.
    floor = dict(min_angle_deg=.01, min_shape=.0001)
    return dict(safety_floors=dict(TRI=dict(floor), QUAD=dict(floor)),
                regional_targets={group: dict(floor) for group in GROUPS},
                min_relative_rms_gain=.01, max_face_growth=1, max_total_faces=2000,
                error_targets=dict(rms_source_area=.0001, max_xyz=.0001))


def common_reports(new_rms=.8, new_max=2.0, previous_rms=1.0):
    def observation(n, rms, maximum):
        return dict(global_error=dict(sample_count=n*n, rms_source_area=rms, max_xyz=maximum))
    return {n: dict(baseline=observation(n, previous_rms, 2.0),
                    candidate=observation(n, new_rms, new_max)) for n in GRIDS}


class ProgressiveAdmissionTests(unittest.TestCase):
    def test_inherited_shortfall_can_remain_if_shape_does_not_regress(self):
        group = "contour_vertex_TRI"
        settings = fixture_profile()
        settings["regional_targets"][group]["min_angle_deg"] = 5
        old = {group: [(2, .2), (9, .8), (10, .9)]}
        new = {group: [(3, .3), (9, .8), (10, .9)]}
        result = measure_progress(old, new, common_reports(), settings)
        self.assertEqual(result["status"], "eligible")
        self.assertFalse(result["quality_targets_met"])
        self.assertFalse(result["stop_targets_met"])

    def test_safety_floor_always_applies_even_with_improvement(self):
        self.assertEqual(regional_metric([1, 9], [2, 9], 3, 5)["status"], "below_safety_floor")

    def test_count_fraction_and_minimum_are_independent_vetoes(self):
        cases = ([3, 4, 7, 9], [3, 7], [1, 7, 9])
        for new in cases:
            self.assertEqual(regional_metric([2, 7, 9], new, 1, 5)["status"], "regional_regression")

    def test_absent_removed_and_new_groups_have_distinct_outcomes(self):
        cases = (([], [], "absent"), ([1], [], "removed"),
                 ([], [3, 9], "regional_regression"), ([], [5, 9], "meets_target"))
        for old, new, expected in cases:
            self.assertEqual(regional_metric(old, new, 1, 5)["status"], expected)

    def test_growth_and_total_face_budgets_are_independent(self):
        settings = fixture_profile()
        settings.update(max_face_growth=.5, max_total_faces=1)
        old = {"interior_QUAD": [(45, .8)]}
        new = {"interior_QUAD": [(48, .9)]*2}
        report = measure_progress(old, new, common_reports(), settings)
        self.assertEqual(report["blockers"], ["face_growth", "total_face_budget"])

    def test_geometry_requires_gain_and_maximum_non_regression_on_both_grids(self):
        reports = common_reports()
        reports[24] = common_reports(new_rms=.99, new_max=2.1)[24]
        groups = {"interior_QUAD": [(45, .8)]}
        settings = fixture_profile()
        settings["min_relative_rms_gain"] = .05
        result = measure_progress(groups, groups, reports, settings)
        self.assertEqual(result["blockers"], ["relative_rms_gain_24", "maximum_deviation_24"])

    def test_zero_rms_has_no_relative_gain(self):
        groups = {"interior_QUAD": [(45, .8)]}
        result = measure_progress(groups, groups, common_reports(new_rms=0, previous_rms=0),
                                  fixture_profile())
        self.assertEqual(result["blockers"], ["relative_rms_gain_24", "relative_rms_gain_48"])

    def test_qualification_needs_both_error_targets(self):
        groups = {"interior_QUAD": [(45, .8)]}
        settings = fixture_profile()
        settings["error_targets"] = dict(rms_source_area=.9, max_xyz=1.95)
        report = measure_progress(groups, groups, common_reports(), settings)
        self.assertTrue(report["quality_targets_met"])
        self.assertFalse(report["stop_targets_met"])
        report = measure_progress(groups, groups, common_reports(new_max=1.9), settings)
        self.assertTrue(report["stop_targets_met"])

    def test_incomplete_grid_is_refused(self):
        groups = {"interior_QUAD": [(45, .8)]}
        with self.assertRaisesRegex(ValueError, "Both common geometry grids"):
            measure_progress(groups, groups, {24: common_reports()[24]}, fixture_profile())
        reports = common_reports()
        reports[48]["candidate"]["global_error"]["sample_count"] -= 1
        with self.assertRaisesRegex(ValueError, "Incomplete common geometry"):
            measure_progress(groups, groups, reports, fixture_profile())

    def test_no_implicit_numerical_profile(self):
        with tempfile.TemporaryDirectory() as out:
            path = Path(out) / "profile.json"
            settings = fixture_profile()
            path.write_text(json.dumps(settings), encoding="ascii")
            self.assertEqual(load_profile(path)[0], settings)
            for key, invalid in (("max_total_faces", True), ("min_relative_rms_gain", 0),
                                 ("safety_floors", {}), ("regional_targets", {})):
                path.write_text(json.dumps(dict(settings, **{key: invalid})), encoding="ascii")
                with self.assertRaises(ValueError):
                    load_profile(path)


if __name__ == "__main__":
    unittest.main()
