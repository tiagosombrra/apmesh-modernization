"""Reject missing owner/sequence coverage and broken failure observers."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from accepted_root_case import validate_contracts, validate_release


def complete():
    rows = [f"accepted_root archived={a} action={action} reverse={r} denied={int(action == 3)} unwind=0 retained=0"
            for a in (0, 1) for action in range(5) for r in (0, 1)]
    return "\n".join(rows + [f"accepted_sequence archived={a} steps=4 retries=8 commits=2 retained=0" for a in (0, 1)] + ["accepted_root_contracts=22 complete=1"])


class AcceptedRootTests(unittest.TestCase):
    def test_complete(self):
        validate_contracts(0, complete())

    def test_missing_owner_failure_or_sequence(self):
        for i in (0, 6, 8, 18, 20, 21):
            rows = complete().splitlines()
            del rows[i]
            with self.subTest(i=i), self.assertRaises(ValueError):
                validate_contracts(0, "\n".join(rows))

    def test_storage_or_unwind_failure(self):
        for old, new in (("retained=0", "retained=1"), ("unwind=0", "unwind=1"), ("denied=1", "denied=0")):
            with self.assertRaises(ValueError):
                validate_contracts(0, complete().replace(old, new, 1))

    def test_reorder_or_duplicate(self):
        rows = complete().splitlines()
        rows[0], rows[1] = rows[1], rows[0]
        for text in ("\n".join(rows), rows[0] + "\n" + complete()):
            with self.assertRaises(ValueError):
                validate_contracts(0, text)

    def test_process_or_hidden_diagnostic(self):
        for code, text in ((1, complete()), (0, complete() + "\nAccepted root contract failure: bad")):
            with self.assertRaises(ValueError):
                validate_contracts(code, text)

    def test_completion_once(self):
        for text in (complete().replace("accepted_root_contracts=22 complete=1", ""), complete() + "\naccepted_root_contracts=22 complete=1"):
            with self.assertRaises(ValueError):
                validate_contracts(0, text)

    def test_real_release_control(self):
        validate_release(1, "accepted_root_release_suppressed=1\nAccepted root contract failure: accepted root retained observed native storage\n")

    def test_release_injection_and_detection_required(self):
        text = "accepted_root_release_suppressed=1\nAccepted root contract failure: accepted root retained observed native storage\n"
        for code, changed in ((0, text), (1, text.replace("suppressed=1", "suppressed=0")), (1, text.replace("native storage", "other"))):
            with self.assertRaises(ValueError):
                validate_release(code, changed)
