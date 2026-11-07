"""Keep borrowing separate from the public compatibility contract."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from audit_control_lookup import audit
from audit_control_reader import FILES, expand_borrowed_lookup


class BorrowedControlLookupTests(unittest.TestCase):
    def test_actual_lookup_and_nine_mutations(self):
        result = audit(ROOT)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["rejected_mutations"], 9)

    def test_legacy_source_without_borrowed_helper_is_preserved(self):
        source = {FILES[2]: "PointAdaptive legacy;"}
        self.assertEqual(expand_borrowed_lookup(source), source)

    def test_duplicate_borrowed_definition_is_rejected(self):
        source = {name: (ROOT / name).read_text(encoding="utf-8") for name in FILES}
        source[FILES[2]] += source[FILES[2]]
        with self.assertRaises(ValueError):
            expand_borrowed_lookup(source)


if __name__ == "__main__":
    unittest.main()
