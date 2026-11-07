"""Challenge the actual shared reader without weakening its historical oracle."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from audit_control_reader import FILES, audit, expand_shared_reader, originals, verify


class SharedControlReaderTests(unittest.TestCase):
    def test_actual_bodies_expand_to_entry_with_eight_rejected_mutations(self):
        result = audit(ROOT)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["rejected_mutations"], 8)

    def test_duplicate_helper_and_unrelated_lookup_drift_are_rejected(self):
        baseline = originals(ROOT)
        candidate = {name: (ROOT / name).read_text(encoding="utf-8") for name in FILES}
        for name, before, after in (
                (FILES[2], "PointAdaptive PatchReader::GetPointVectorControlPoints",
                 "PointAdaptive PatchReader::ChangedLookup"),
                (FILES[0], "protected:", "public:")):
            changed = dict(candidate)
            self.assertIn(before, changed[name])
            changed[name] = changed[name].replace(before, after, 1)
            with self.subTest(name=name), self.assertRaises(ValueError):
                verify(baseline, changed)
        changed = dict(candidate)
        changed[FILES[2]] += candidate[FILES[2]]
        with self.assertRaises(ValueError):
            expand_shared_reader(changed)

    def test_historical_source_without_helper_is_preserved(self):
        source = originals(ROOT)
        self.assertEqual(expand_shared_reader(source), source)


if __name__ == "__main__":
    unittest.main()
