"""Independent attempt-oracle controls, including mutually wrong CSV/log exports."""

import csv
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from audit_attempt_metrics import audit


class AttemptMetricTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.rows = []
        last_count, last_error = 1, 10
        for step, (count, error, accepted) in enumerate(((1, 10, 1), (2, 8, 1), (3, 12, 0), (4, 9, 0), (3, 4, 1))):
            growth = count/last_count
            self.rows.append({"step": step, "elements": count, "error": error, "error_prev": last_error,
                              "elements_prev": last_count, "elements_delta": count-last_count,
                              "element_growth_factor": growth, "actual_element_growth": growth,
                              "actual_growth_step": growth, "acceptance_score": step/10})
            (self.root / f"case_passo_{step}_acceptance_{'accepted' if accepted else 'rejected'}.log").write_text(
                f"step={step}\naccepted={accepted}\nacceptance_score={step/10}\nelement_growth_factor={growth}\n")
            vertices, faces = [], []
            for triangle in range(count):
                vertices.extend((f"v {2*triangle} 0 0", f"v {2*triangle+1} 0 0", f"v {2*triangle} 1 0"))
                faces.append(f"f {3*triangle+1} {3*triangle+2} {3*triangle+3}")
            (self.root / f"case_passo_{step}_malha_{step}.obj").write_text("\n".join(vertices+faces)+"\n")
            if accepted:
                last_count, last_error = count, error
        self.write_exports()

    def tearDown(self):
        self.temp.cleanup()

    def write_exports(self):
        with (self.root / "case_metrics_rank_-1.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(self.rows[0]))
            writer.writeheader()
            writer.writerows(self.rows)
        for row in self.rows:
            values = {"elements_previous": row["elements_prev"], "elements_delta": row["elements_delta"],
                      "element_growth_factor": row["element_growth_factor"], "actual_element_growth": row["actual_element_growth"],
                      "actual_growth_step": row["actual_growth_step"], "acceptance_score": row["acceptance_score"],
                      "error_global_previous": row["error_prev"]}
            (self.root / f"case_passo_{row['step']}_qualite_{row['step']}_rank_-1.log").write_text(
                "".join(f"{key}={value}\n" for key, value in values.items()))

    def test_rejections_do_not_advance_reference(self):
        result = audit(self.root)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["accepted_steps"], [0, 1, 4])
        self.assertEqual(result["rejected_steps"], [2, 3])
        self.assertEqual(result["compared_values"], 80)

    def test_mutually_wrong_growth_is_detected(self):
        self.rows[2]["element_growth_factor"] = 1
        self.rows[2]["actual_element_growth"] = 1
        self.rows[2]["actual_growth_step"] = 1
        self.write_exports()
        self.assertEqual(audit(self.root)["status"], "failed")

    def test_rejected_candidate_as_previous_is_detected(self):
        self.rows[3]["elements_prev"] = 3
        self.rows[3]["error_prev"] = 12
        self.write_exports()
        fields = {diff["field"] for diff in audit(self.root)["differences"]}
        self.assertTrue({"elements_prev", "error_prev"} <= fields)

    def test_wrong_score_is_detected(self):
        self.rows[2]["acceptance_score"] = 0
        self.write_exports()
        self.assertEqual(audit(self.root)["status"], "failed")

    def test_nonfinite_value_is_rejected(self):
        self.rows[2]["element_growth_factor"] = "nan"
        self.write_exports()
        with self.assertRaisesRegex(ValueError, "Non-finite"):
            audit(self.root)

    def test_missing_or_duplicate_attempt_is_rejected(self):
        self.rows[3]["step"] = 2
        self.write_exports()
        with self.assertRaises(ValueError):
            audit(self.root)

    def test_duplicate_named_analysis_field_is_rejected(self):
        with (self.root / "case_passo_2_qualite_2_rank_-1.log").open("a") as stream:
            stream.write("element_growth_factor=1\n")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            audit(self.root)


if __name__ == "__main__":
    unittest.main()
