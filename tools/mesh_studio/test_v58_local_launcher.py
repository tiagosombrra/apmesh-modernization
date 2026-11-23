"""Offline/adversarial unit gates for the V5.8 local read-only launcher."""

from __future__ import annotations

from pathlib import Path
import re
from shutil import copy2
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

from .dependency_lock_audit import ROOT, PIN, DependencyLockError
from . import local_launcher as launcher


class LocalLoopbackLauncherTests(unittest.TestCase):
    def _source_lock(self) -> str:
        return (ROOT / "tools/mesh_studio/locks/"
                "requirements-web-ci-linux-py313.lock").read_text(encoding="utf-8")

    def test_real_local_api_import_closure_has_only_fastapi(self):
        report = launcher._source_imports()
        self.assertEqual(report["external_imports"], ["fastapi"])
        self.assertIn("web_api", report["source_modules"])
        self.assertIn("quality_analysis", report["source_modules"])
        self.assertIn("svg_figure", report["source_modules"])

    def test_derived_lock_exact_hashes_and_no_scientific_deps(self):
        text = self._source_lock()
        result, pins = launcher._project_hash_lock(text, "f" * 64)
        self.assertEqual(set(pins), launcher.MINIMAL)
        self.assertEqual(len(pins), 13)
        self.assertEqual(set(launcher.EXCLUDED) & set(pins), set())
        rows = list(PIN.finditer(result))
        self.assertEqual(len(rows), 13)
        self.assertIn("# Original source lock SHA256: " + "f" * 64, result)
        self.assertTrue(all("--hash=sha256:" in
                            result[x.end():rows[i + 1].start()
                                   if i + 1 < len(rows) else len(result)]
                            for i, x in enumerate(rows)))

    def test_missing_hash_fails_closed_even_if_name_and_version_match(self):
        text = self._source_lock()
        rows = list(PIN.finditer(text))
        fast = next(i for i, m in enumerate(rows) if m.group(1) == "fastapi")
        start = rows[fast].start()
        end = rows[fast + 1].start()
        block = text[start:end]
        replacement = re.sub(r"--hash=sha256:[a-f0-9]{64}", "", block)
        self.assertNotEqual(block, replacement)
        with self.assertRaisesRegex(DependencyLockError,
                                    "missing_minimal_dependency_hash"):
            launcher._project_hash_lock(text[:start] + replacement + text[end:],
                                        "f" * 64)

    def test_new_banned_import_in_api_is_not_silently_allowlisted(self):
        report = launcher._source_imports()
        with TemporaryDirectory(prefix="v58-import-tree-") as temp:
            root = Path(temp)
            for module in report["source_modules"]:
                destination = root / (module.replace(".", "/") + ".py")
                destination.parent.mkdir(parents=True, exist_ok=True)
                copy2(launcher.SOURCE_PYTHON /
                      (module.replace(".", "/") + ".py"), destination)
            api = root / "web_api.py"
            api.write_text(api.read_text(encoding="utf-8") + "\nimport fitz\n",
                           encoding="utf-8")
            with self.assertRaisesRegex(DependencyLockError,
                                        "runtime_web_api_vendor_import_drift"):
                launcher._source_imports(root)

    def test_dynamic_dependency_import_requires_review(self):
        report = launcher._source_imports()
        with TemporaryDirectory(prefix="v58-dynamic-tree-") as temp:
            root = Path(temp)
            for module in report["source_modules"]:
                destination = root / (module.replace(".", "/") + ".py")
                destination.parent.mkdir(parents=True, exist_ok=True)
                copy2(launcher.SOURCE_PYTHON /
                      (module.replace(".", "/") + ".py"), destination)
            api = root / "web_api.py"
            api.write_text(api.read_text(encoding="utf-8") +
                           "\n__import__('pymupdf')\n", encoding="utf-8")
            with self.assertRaisesRegex(launcher.LocalStudioError,
                                        "dynamic_import_requires_review"):
                launcher._source_imports(root)

    def test_missing_minimal_package_block_fails_closed(self):
        text = self._source_lock()
        rows = list(PIN.finditer(text))
        fast = next(i for i, match in enumerate(rows)
                    if match.group(1) == "fastapi")
        start = rows[fast].start()
        end = rows[fast + 1].start()
        with self.assertRaisesRegex(DependencyLockError,
                                    "minimal_dependency_closure_missing"):
            launcher._project_hash_lock(text[:start] + text[end:], "f" * 64)

    def test_exact_source_preflight_does_not_launch_or_write(self):
        if launcher.sys.version_info[:2] != (3, 13):
            self.skipTest("real source lock platform check requires Python 3.13")
        lock, report = launcher.source_preflight()
        self.assertEqual(report["minimal_python_count"], 13)
        self.assertEqual(report["native_cpp_replayed"], False)
        self.assertFalse(report["original_cpp_r2_8_lod_qualified"])
        self.assertIn("PyMuPDF/VTK are excluded", lock)

    def test_loopback_busy_port_is_not_accepted(self):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("127.0.0.1", 0))
            port = server.getsockname()[1]
            server.listen(1)
            self.assertFalse(launcher._available(port))

    def test_unsafe_mixed_python_profile_is_explicitly_rejected(self):
        with mock.patch.object(launcher.sys, "platform", "darwin"):
            with self.assertRaisesRegex(launcher.LocalStudioError,
                                        "unsupported_platform_without_python_hash_lock"):
                launcher._platform_profile()


if __name__ == "__main__":
    unittest.main()
