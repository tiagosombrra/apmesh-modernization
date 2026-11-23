"""Adversarial controls for bounded installed dependency and license evidence."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock
import json
import os

from .dependency_lock_audit import DependencyLockError
from . import installed_license_evidence as evidence


class InstalledLicenseEvidenceTests(TestCase):
    def test_actual_original_rechoir_source_lock_is_old_version(self):
        lock = json.loads((evidence.ROOT / "tools/mesh_studio/web/package-lock.json")
                          .read_text(encoding="utf-8"))
        self.assertEqual(lock["packages"]["node_modules/rechoir"]["version"], "0.6.2")
        self.assertIsNone(lock["packages"]["node_modules/rechoir"].get("license"))

    def test_license_file_hash_and_nested_receipt(self):
        with TemporaryDirectory(prefix="v561-files-") as tmp:
            base = Path(tmp)
            package = base / "node_modules/demo"
            (package / "nested").mkdir(parents=True)
            (package / "LICENSE").write_text("MIT sample fixture", encoding="utf-8")
            (package / "nested/NOTICE.txt").write_text("Notice fixture", encoding="utf-8")
            (package / "README.md").write_text("Not license evidence", encoding="utf-8")
            files = evidence.license_file_receipts(package, base)
            self.assertEqual([p["path"] for p in files],
                             ["LICENSE", "nested/NOTICE.txt"])
            self.assertTrue(all(p["status"] == "hash-recorded" for p in files))
            self.assertTrue(all(len(p["sha256"]) == 64 for p in files))

    def test_symlinks_cannot_read_unrelated_license_bytes(self):
        with TemporaryDirectory(prefix="v561-link-") as tmp:
            base = Path(tmp) / "installed"
            pkg = base / "node_modules/demo"
            pkg.mkdir(parents=True)
            external = Path(tmp) / "external-LICENSE"
            external.write_text("unrelated fixture", encoding="utf-8")
            try:
                (pkg / "LICENSE").symlink_to(external)
            except (OSError, NotImplementedError):
                self.skipTest("platform does not permit file symlinks")
            self.assertEqual(evidence.license_file_receipts(pkg, base), [])

    def test_scanning_outside_install_tree_fails_closed(self):
        with TemporaryDirectory(prefix="v561-tree-") as tmp:
            base = Path(tmp) / "base"
            base.mkdir()
            outside = Path(tmp) / "other"
            outside.mkdir()
            with self.assertRaisesRegex(
                    DependencyLockError, "license_scan_outside_install_base"):
                evidence.license_file_receipts(outside, base)

    def test_huge_license_text_is_not_copied_into_report(self):
        self.assertEqual(evidence._metadata_field(None), {"status": "absent"})
        large = "Sensitive placeholder fixture\n" * 500
        record = evidence._metadata_field(large)
        self.assertEqual(record["status"], "recorded")
        self.assertIsNone(record["short_expression"])
        self.assertEqual(len(record["sha256"]), 64)

    def _synthetic_tree(self, base: Path) -> Path:
        web = base / "tools/mesh_studio/web"
        (web / "node_modules/rechoir").mkdir(parents=True)
        (web / "node_modules/sample").mkdir(parents=True)
        (web / "node_modules/rechoir/package.json").write_text(
            '{"name":"rechoir","version":"0.6.2","license":"MIT","licenses":[{"type":"MIT"}]}',
            encoding="utf-8")
        (web / "node_modules/rechoir/LICENSE").write_text(
            "Synthetic MIT notice", encoding="utf-8")
        (web / "node_modules/sample/package.json").write_text(
            '{"name":"sample","version":"1.0.0","license":"Apache-2.0"}',
            encoding="utf-8")
        (web / "package-lock.json").write_text(json.dumps({
            "packages": {
                "": {},
                "node_modules/rechoir": {
                    "version": "0.6.2", "integrity": "sha512-fixture",
                },
                "node_modules/sample": {
                    "version": "1.0.0", "integrity": "sha512-fixture",
                },
                "node_modules/optional-win32": {
                    "version": "1.0.0", "integrity": "sha512-fixture",
                    "optional": True,
                },
            }}), encoding="utf-8")
        return web

    def test_installed_manifest_and_optional_absence_are_distinguished(self):
        with TemporaryDirectory(prefix="v561-npm-") as tmp:
            root = Path(tmp)
            self._synthetic_tree(root)
            with mock.patch.object(evidence, "audit_all",
                                   return_value={"npm": {"npm_lock_sha256": "fixture"}}):
                report = evidence.collect_installed_npm(root)
            self.assertEqual(report["statuses"],
                             {"installed": 2, "not_installed_optional": 1})
            by_path = {p["install_path"]: p for p in report["components"]}
            self.assertEqual(
                by_path["node_modules/rechoir"]["installed_manifest_license"]
                ["short_expression"], "MIT")
            self.assertIsNone(
                by_path["node_modules/rechoir"]["lock_license_declaration"])
            self.assertEqual(len(by_path["node_modules/rechoir"]["license_files"]), 1)
            self.assertEqual(
                by_path["node_modules/rechoir"]["installed_manifest_legacy_licenses"],
                [{"type": "MIT", "url": None}])

    def test_missing_nonoptional_package_is_not_silently_ignored(self):
        with TemporaryDirectory(prefix="v561-npm-loss-") as tmp:
            root = Path(tmp)
            self._synthetic_tree(root)
            (root / "tools/mesh_studio/web/node_modules/sample/package.json").unlink()
            (root / "tools/mesh_studio/web/node_modules/sample").rmdir()
            with mock.patch.object(evidence, "audit_all",
                                   return_value={"npm": {"npm_lock_sha256": "fixture"}}):
                with self.assertRaisesRegex(DependencyLockError,
                                            "missing_nonoptional_installed_npm"):
                    evidence.collect_installed_npm(root)

    def test_installed_npm_version_mismatch_rejected(self):
        with TemporaryDirectory(prefix="v561-npm-version-") as tmp:
            root = Path(tmp)
            web = self._synthetic_tree(root)
            (web / "node_modules/rechoir/package.json").write_text(
                '{"name":"rechoir","version":"0.8.0"}', encoding="utf-8")
            with mock.patch.object(evidence, "audit_all",
                                   return_value={"npm": {"npm_lock_sha256": "fixture"}}):
                with self.assertRaisesRegex(DependencyLockError,
                                            "installed_npm_name_or_version_drift"):
                    evidence.collect_installed_npm(root)

    def test_lock_declared_npm_alias_is_version_checked_and_allowed(self):
        with TemporaryDirectory(prefix="v561-npm-alias-") as tmp:
            root = Path(tmp)
            web = self._synthetic_tree(root)
            alias = web / "node_modules/@typescript/old"
            alias.mkdir(parents=True)
            (alias / "package.json").write_text(
                '{"name":"typescript","version":"6.0.3","license":"Apache-2.0"}',
                encoding="utf-8")
            lock_path = web / "package-lock.json"
            inventory = json.loads(lock_path.read_text(encoding="utf-8"))
            inventory["packages"]["node_modules/@typescript/old"] = {
                "name": "typescript",
                "version": "6.0.3",
                "integrity": "sha512-synthetic",
            }
            lock_path.write_text(json.dumps(inventory), encoding="utf-8")
            with mock.patch.object(evidence, "audit_all",
                                   return_value={"npm": {"npm_lock_sha256": "fixture"}}):
                report = evidence.collect_installed_npm(root)
                alias_record = next(
                    item for item in report["components"]
                    if item["install_path"] == "node_modules/@typescript/old")
                self.assertEqual(alias_record["resolved_package_name"], "typescript")
                self.assertEqual(alias_record["lock_version"], "6.0.3")
                del inventory["packages"]["node_modules/@typescript/old"]["name"]
                lock_path.write_text(json.dumps(inventory), encoding="utf-8")
                with self.assertRaisesRegex(
                        DependencyLockError, "installed_npm_name_or_version_drift"):
                    evidence.collect_installed_npm(root)

    def test_report_bytes_are_deterministic(self):
        report = {"profile": "api-linux", "components": [],
                  "classification": "synthetic-only"}
        with TemporaryDirectory(prefix="v561-out-a-") as a, TemporaryDirectory(
                prefix="v561-out-b-") as b:
            ra = evidence.write_evidence(report, Path(a))
            rb = evidence.write_evidence(report, Path(b))
            self.assertEqual(ra, rb)
            self.assertEqual((Path(a) / ra["name"]).read_bytes(),
                             (Path(b) / rb["name"]).read_bytes())


if __name__ == "__main__":
    import unittest
    unittest.main()
