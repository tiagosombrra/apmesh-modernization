"""Negative and positive controls for local quality infrastructure."""

import importlib.util
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


quality = load("quality")
compatibility = load("check_compatibility")
sys.path.insert(0, str(ROOT / "tools"))
staged = load("check_staged")


class QualityTests(unittest.TestCase):
    def doctor_case(self, missing=(), failure=None):
        output, errors = io.StringIO(), io.StringIO()
        resolve = lambda name: None if name in missing else f"C:/tools with spaces/{name}.exe"
        with patch.object(quality.shutil, "which", side_effect=resolve), \
                patch.object(quality, "run", side_effect=failure) as run, \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = quality.doctor()
        return code, output.getvalue(), errors.getvalue(), run

    def test_doctor_all_tools_present(self):
        code, output, errors, run = self.doctor_case()
        self.assertEqual(code, 0)
        self.assertEqual(len(output.splitlines()), 7)
        self.assertEqual(errors, "")
        self.assertEqual(run.call_count, 7)
        self.assertEqual(run.call_args_list[0].args[0], ["C:/tools with spaces/git.exe", "--version"])
        self.assertEqual(run.call_args_list[0].kwargs, {"timeout": 10})

    def test_doctor_one_missing_fails_and_checks_remaining_tools(self):
        code, output, _, run = self.doctor_case(missing={"git"})
        self.assertEqual(code, 1)
        self.assertIn("git: UNAVAILABLE (not found on PATH)", output)
        self.assertIn("doxygen:", output)
        self.assertEqual(run.call_count, 6)

    def test_doctor_all_missing_is_not_success(self):
        with patch.object(quality.shutil, "which", return_value=None), \
                patch.object(quality, "run") as run, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(quality.doctor(), 1)
        run.assert_not_called()

    def test_doctor_version_failure_does_not_stop_inventory(self):
        failure = subprocess.CalledProcessError(7, ["git", "--version"])
        code, output, errors, run = self.doctor_case(failure=[failure] + [None] * 6)
        self.assertEqual(code, 1)
        self.assertEqual(run.call_count, 7)
        self.assertIn("git: BROKEN", errors)
        self.assertIn("doxygen:", output)

    def test_doctor_unlaunchable_tool_is_broken(self):
        for failure in (FileNotFoundError("disappeared"), PermissionError("denied"),
                        subprocess.TimeoutExpired(["git", "--version"], 10)):
            with self.subTest(failure=type(failure).__name__):
                code, _, errors, run = self.doctor_case(failure=[failure] + [None] * 6)
                self.assertEqual(code, 1)
                self.assertEqual(run.call_count, 7)
                self.assertIn("BROKEN", errors)

    def test_doctor_main_propagates_failure(self):
        with patch.object(sys, "argv", ["quality.py", "doctor"]), \
                patch.object(quality, "doctor", return_value=1):
            self.assertEqual(quality.main(), 1)

    def test_check_never_changes_bytes(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path = Path(folder) / "sample.cpp"
            path.write_bytes(b"int x;  \r\n")
            self.assertEqual(quality.whitespace([path], False), 1)
            self.assertEqual(path.read_bytes(), b"int x;  \r\n")

    def test_fix_is_explicit_and_idempotent(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path = Path(folder) / "sample.cpp"
            path.write_bytes(b"int x;  \r\n")
            self.assertEqual(quality.whitespace([path], True), 0)
            self.assertEqual(path.read_bytes(), b"int x;\n")
            self.assertEqual(quality.whitespace([path], False), 0)

    def test_markdown_hard_break_is_preserved(self):
        self.assertEqual(quality.normalized(b"text  \r\nnext\r\n", markdown=True), b"text  \nnext\n")

    def test_binary_content_is_rejected(self):
        with self.assertRaises(ValueError):
            quality.normalized(b"data\0")

    def test_empty_file_selection_is_failure(self):
        with self.assertRaises(ValueError):
            quality.select(["image.png"], None, cpp=True)

    def test_outside_path_is_rejected(self):
        with self.assertRaises(ValueError):
            quality.select(["../outside.cpp"], None)

    def test_vendor_input_is_rejected(self):
        with self.assertRaises(ValueError):
            quality.select(["libs/eigen3/Eigen/Core"], None)

    def test_missing_tool_is_failure(self):
        with patch.object(quality.shutil, "which", return_value=None):
            with self.assertRaises(ValueError):
                quality.tool("clang-tidy")

    def test_empty_compilation_database_is_failure(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path = Path(folder)
            (path / "compile_commands.json").write_text(json.dumps([]))
            with self.assertRaises(ValueError):
                quality.compilation_sources(path)

    def test_staged_bytes_are_checked_despite_clean_working_copy(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = Path(folder).resolve()
            subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
            path = root / "file with spaces.py"
            path.write_bytes(b"value = 1  \n")
            subprocess.run(["git", "-C", str(root), "add", "--", path.name], check=True)
            path.write_bytes(b"value = 1\n")
            with patch.object(quality, "ROOT", root):
                with self.assertRaises(ValueError):
                    staged.main()

    def test_clean_index_is_not_confused_with_unstaged_debt(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            root = Path(folder).resolve()
            subprocess.run(["git", "init", str(root)], check=True, capture_output=True)
            path = root / "file with spaces.py"
            path.write_bytes(b"value = 1\n")
            subprocess.run(["git", "-C", str(root), "add", "--", path.name], check=True)
            path.write_bytes(b"value = 1  \n")
            with patch.object(quality, "ROOT", root):
                self.assertEqual(staged.main(), 0)


class CompatibilityTests(unittest.TestCase):
    def check(self, row, succeeds=False):
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            path = Path(folder) / "compatibility.csv"
            path.write_text("compared_groups,desynchronized_groups,compat_error_mean,compat_error_max\n" + row)
            if succeeds:
                self.assertEqual(compatibility.validate(path), 1)
            else:
                with self.assertRaises(ValueError):
                    compatibility.validate(path)

    def test_positive_measured_control(self):
        self.check("2,0,0,0\n", succeeds=True)

    def test_zero_coverage_fails(self):
        self.check("0,0,0,0\n")

    def test_empty_report_fails(self):
        self.check("")

    def test_nan_fails(self):
        self.check("2,0,nan,nan\n")

    def test_desynchronization_fails(self):
        self.check("2,1,0,0\n")

    def test_excessive_error_fails(self):
        self.check("2,0,0.1,0.2\n")

    def test_inconsistent_errors_fail(self):
        self.check("2,0,0.2,0.1\n")


if __name__ == "__main__":
    unittest.main()
