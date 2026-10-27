"""Reject incomplete coverage and incorrect candidate/snapshot outcomes."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from candidate_snapshot_case import expected_rows, validate


def complete():
    return "\n".join(f"snapshot scenario={s} alias={a} calls={c} selected={v} retained=0 denied={d} unwind=0"
                     for s, a, c, v, d in expected_rows()) + "\nsnapshot_contracts=40 complete=1\n"


class CandidateSnapshotTests(unittest.TestCase):
    def test_complete(self):
        validate(0, complete())

    def test_missing_reused_slot_or_sequence(self):
        for index in (8, 9, 24, 28):
            lines = complete().splitlines()
            del lines[index]
            with self.subTest(index=index), self.assertRaises(ValueError):
                validate(0, "\n".join(lines))

    def test_wrong_selected_identity(self):
        with self.assertRaises(ValueError):
            validate(0, complete().replace("selected=1", "selected=0", 1))

    def test_changed_epsilon_or_fallback_outcome(self):
        for scenario in (6, 7, 12, 13, 14, 15):
            old = next(line for line in complete().splitlines() if line.startswith(f"snapshot scenario={scenario} alias=0"))
            changed = old.replace(f"selected={int(scenario % 2 == 0)}", f"selected={int(scenario % 2 != 0)}")
            with self.subTest(scenario=scenario), self.assertRaises(ValueError):
                validate(0, complete().replace(old, changed))

    def test_retention_denial_or_unwind(self):
        for old, new in (("retained=0", "retained=1"), ("denied=1", "denied=0"), ("unwind=0", "unwind=1")):
            with self.subTest(new=new), self.assertRaises(ValueError):
                validate(0, complete().replace(old, new, 1))

    def test_duplicate_or_reordered(self):
        lines = complete().splitlines()
        lines[0], lines[1] = lines[1], lines[0]
        for text in ("\n".join(lines), complete().splitlines()[0] + "\n" + complete()):
            with self.subTest(text=text[:50]), self.assertRaises(ValueError):
                validate(0, text)

    def test_missing_or_duplicate_completion(self):
        for text in (complete().replace("snapshot_contracts=40 complete=1", ""), complete() + "snapshot_contracts=40 complete=1\n"):
            with self.assertRaises(ValueError):
                validate(0, text)

    def test_process_failure_or_diagnostic(self):
        for code, text in ((1, complete()), (0, complete() + "Snapshot contract failure: bad\n")):
            with self.assertRaises(ValueError):
                validate(code, text)
