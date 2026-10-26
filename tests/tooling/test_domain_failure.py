"""Reject false success, crashes and unrelated diagnostics in the fault contract."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from domain_failure_case import DIAGNOSTIC, MARKER, validate_failure


class DomainFailureTests(unittest.TestCase):
    def test_expected_failure_and_fallback_counts_pass(self):
        for calls in (1, 2):
            validate_failure(1, (MARKER + "\n") * calls + DIAGNOSTIC, calls)

    def test_zero_status_is_not_failure_evidence(self):
        with self.assertRaises(ValueError):
            validate_failure(0, MARKER + DIAGNOSTIC, 1)

    def test_crash_is_not_expected_failure(self):
        for code in (-11, 3221225477):
            with self.assertRaises(ValueError):
                validate_failure(code, MARKER + DIAGNOSTIC, 1)

    def test_missing_hook_wrong_context_or_call_count_fails(self):
        for text in (DIAGNOSTIC, MARKER + DIAGNOSTIC.replace("patch=0", "patch=1"), MARKER * 2 + DIAGNOSTIC):
            with self.assertRaises(ValueError):
                validate_failure(1, text, 1)


if __name__ == "__main__":
    unittest.main()
