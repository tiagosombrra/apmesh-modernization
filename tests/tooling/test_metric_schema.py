"""Controls for independent CSV-header alignment auditing."""

import csv
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from audit_metric_schema import CONTROL_FIELDS, audit


class MetricSchemaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.root = Path(self.temp.name)
        self.values = dict.fromkeys(CONTROL_FIELDS, "0")
        self.values.update(adaptation_relaxation="0.3", generation_control_mode="initial",
                           top_patch_candidate_count="4", budget_driver_mode="factor_driven")
        (self.root / "control_passo_0_qualite_0_rank_-1.log").write_text(
            "".join(f"{k}={v}\n" for k, v in self.values.items()), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def write_csv(self, fields):
        with (self.root / "control_metrics_rank_-1.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["step", *fields])
            writer.writerow(["0", *self.values.values()])

    def test_aligned_schema_passes(self):
        self.write_csv(CONTROL_FIELDS)
        result = audit(self.root)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["compared_fields"], len(CONTROL_FIELDS))

    def test_shifted_header_fails_with_unchanged_row_length(self):
        self.write_csv(CONTROL_FIELDS[1:] + CONTROL_FIELDS[:1])
        result = audit(self.root)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["differences"])

    def test_missing_field_fails(self):
        self.write_csv(CONTROL_FIELDS[:-1])
        with self.assertRaises(ValueError):
            audit(self.root)


if __name__ == "__main__":
    unittest.main()
