"""Negative and positive controls for local quality infrastructure."""

import importlib.util
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
