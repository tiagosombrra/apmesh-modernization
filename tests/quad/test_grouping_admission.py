from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from quad_grouping_admission import evaluate


class GroupingAdmissionTests(unittest.TestCase):
    def setUp(self):
        receipt = json.loads((ROOT / "docs/research/quad/evidence/"
                              "REVERSIBLE_TRANSITION_TRIAL_20261124.json").read_text(encoding="utf-8"))
        self.coarse = receipt["after_smoothing"]
        self.fine = receipt["after_smoothing_grid48"]

    def test_native_pair_is_eligible(self):
        self.assertEqual(evaluate(self.coarse, self.fine)["verdict"], "eligible")

    def test_regression_is_rejected(self):
        for report in (self.coarse, self.fine):
            report["baseline"], report["candidate"] = report["candidate"], report["baseline"]
        result = evaluate(self.coarse, self.fine)
        self.assertEqual(result["verdict"], "reject")
        self.assertIn("regional_minimum_angle_did_not_improve", result["vetoes"])
        self.assertIn("nodes_increased", result["vetoes"])

    def test_opposite_sampled_error_directions_are_inconclusive(self):
        self.fine["candidate"]["global_error"]["rms_source_area"] = 1.0
        result = evaluate(self.coarse, self.fine)
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertEqual(result["sampling_disagreements"], ["global_error_rms_source_area"])

    def test_contour_change_rejects_even_with_sampling_disagreement(self):
        self.fine["candidate"]["global_error"]["rms_source_area"] = 1.0
        self.coarse["same_ordered_contour_edges"] = False
        result = evaluate(self.coarse, self.fine)
        self.assertEqual(result["verdict"], "reject")
        self.assertIn("ordered_contour_changed", result["vetoes"])

    def test_invalid_inputs_do_not_produce_decisions(self):
        broken = deepcopy(self.fine)
        broken["candidate"]["sha256"] = "different"
        with self.assertRaises(ValueError):
            evaluate(self.coarse, broken)
        self.fine["candidate"]["global_error"]["rms_source_area"] = float("nan")
        with self.assertRaises(ValueError):
            evaluate(self.coarse, self.fine)


if __name__ == "__main__":
    unittest.main()
