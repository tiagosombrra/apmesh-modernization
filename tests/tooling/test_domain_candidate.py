"""Reject missing caller branches and broken release instrumentation."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from domain_candidate_case import expected_rows, validate_contracts, validate_release_control


def complete():
    return "\n".join(f"candidate branch={b} select={s} mode={m} alias={a} calls=2 retained=0 denied={d}"
                     for b, s, m, a, d in expected_rows()) + "\ncandidate_contracts=32 complete=1\n"


class DomainCandidateOracleTests(unittest.TestCase):
    def test_complete_contract_inventory(self):
        validate_contracts(0, complete())

    def test_missing_branch_or_alias_case(self):
        for index in (0, 15, 31):
            lines = complete().splitlines()
            del lines[index]
            with self.subTest(index=index), self.assertRaises(ValueError):
                validate_contracts(0, "\n".join(lines))

    def test_retention_or_wrong_denial(self):
        for old, new in (("retained=0", "retained=1"), ("denied=1", "denied=0")):
            with self.subTest(new=new), self.assertRaises(ValueError):
                validate_contracts(0, complete().replace(old, new, 1))

    def test_duplicate_or_reordered_case(self):
        lines = complete().splitlines()
        lines[0], lines[1] = lines[1], lines[0]
        for text in ("\n".join(lines), complete().splitlines()[0] + "\n" + complete()):
            with self.subTest(text=text[:60]), self.assertRaises(ValueError):
                validate_contracts(0, text)

    def test_completion_required_once(self):
        for text in (complete().replace("candidate_contracts=32 complete=1", ""),
                     complete() + "candidate_contracts=32 complete=1\n"):
            with self.subTest(text=text[-50:]), self.assertRaises(ValueError):
                validate_contracts(0, text)

    def test_process_failure_or_hidden_diagnostic(self):
        for code, text in ((1, complete()), (0, complete() + "Candidate contract failure: bad\n")):
            with self.subTest(code=code), self.assertRaises(ValueError):
                validate_contracts(code, text)

    def test_actual_release_control(self):
        validate_release_control(1, "candidate_release_control_suppressed=1\nCandidate contract failure: candidate release observer detected retained storage\n")

    def test_release_control_requires_injection_and_detection(self):
        text = "candidate_release_control_suppressed=1\nCandidate contract failure: candidate release observer detected retained storage\n"
        for code, changed in ((0, text), (1, text.replace("suppressed=1", "suppressed=0")),
                              (1, text.replace("retained storage", "unrelated failure"))):
            with self.subTest(code=code), self.assertRaises(ValueError):
                validate_release_control(code, changed)


if __name__ == "__main__":
    unittest.main()
