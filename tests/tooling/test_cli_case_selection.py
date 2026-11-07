import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cli_failures import verify_failures


class InvalidCaseSelectionTests(unittest.TestCase):
    def test_empty_selection_cannot_succeed_without_observations(self):
        with tempfile.TemporaryDirectory() as folder, patch("cli_failures.subprocess.run") as run:
            with self.assertRaisesRegex(ValueError, "nonempty unique subset"):
                verify_failures(Path("unused.exe"), Path(folder), case_names=[])
            run.assert_not_called()

    def test_duplicate_selection_is_rejected_before_native_execution(self):
        with tempfile.TemporaryDirectory() as folder, patch("cli_failures.subprocess.run") as run:
            with self.assertRaisesRegex(ValueError, "nonempty unique subset"):
                verify_failures(Path("unused.exe"), Path(folder), case_names=["empty_model", "empty_model"])
            run.assert_not_called()

    def test_unknown_selection_cannot_silently_drop_required_cases(self):
        with tempfile.TemporaryDirectory() as folder, patch("cli_failures.subprocess.run") as run:
            with self.assertRaisesRegex(ValueError, "nonempty unique subset"):
                verify_failures(Path("unused.exe"), Path(folder), case_names=["not_a_case"])
            run.assert_not_called()
