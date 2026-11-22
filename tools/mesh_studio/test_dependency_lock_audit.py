"""Adversarial policy tests for public pinned npm and Python hash locks."""

from __future__ import annotations

from pathlib import Path
import json
from tempfile import TemporaryDirectory
import unittest

from .dependency_lock_audit import (
    DependencyLockError, PROFILES, ROOT, audit_all, audit_npm_lock,
    audit_python_lock,
)

BASE = ROOT / "tools/mesh_studio"


class TransitiveDependencyLockTests(unittest.TestCase):
    def test_real_npm_and_three_platform_hash_locks_are_admitted(self):
        result = audit_all()
        self.assertEqual(result["schema"],
                         "apmesh.meshstudio.v54.dependency_lock_audit.v1")
        self.assertGreaterEqual(result["npm"]["packages"], 100)
        self.assertEqual(set(result["python"]),
                         {name for _, name, _ in PROFILES})
        self.assertFalse(result["native_cpp_scientific_policy_changed"])
        for document in result["python"].values():
            self.assertGreaterEqual(document["sha256_hashes"],
                                    document["packages"])
            self.assertEqual(len(document["lock_sha256"]), 64)

    def test_inconsistent_direct_npm_dependency_is_refused(self):
        source = BASE / "web/package.json"
        lock = BASE / "web/package-lock.json"
        with TemporaryDirectory(prefix="apmesh-v54-npm-") as temporary:
            changed = Path(temporary) / "package.json"
            contents = json.loads(source.read_text(encoding="utf-8"))
            contents["dependencies"]["react"] = "0.0.0"
            changed.write_text(json.dumps(contents), encoding="utf-8")
            with self.assertRaisesRegex(
                    DependencyLockError, "npm_lock_root_direct_dependency_drift"):
                audit_npm_lock(changed, lock)

    def test_untrusted_node_package_registry_is_refused(self):
        source = BASE / "web/package.json"
        with TemporaryDirectory(prefix="apmesh-v54-npm-") as temporary:
            altered = Path(temporary) / "package-lock.json"
            contents = json.loads(
                (BASE / "web/package-lock.json").read_text(encoding="utf-8"))
            key = next(key for key in contents["packages"] if key)
            contents["packages"][key]["resolved"] = (
                "https://untrusted.example.org/pkg.tgz")
            altered.write_text(json.dumps(contents), encoding="utf-8")
            with self.assertRaisesRegex(
                    DependencyLockError, "npm_lock_missing_integrity_or_untrusted"):
                audit_npm_lock(source, altered)

    def test_unhashed_transitive_wheel_is_refused(self):
        source = BASE / "requirements-web-ci.txt"
        lock = BASE / "locks/requirements-web-ci-linux-py313.lock"
        with TemporaryDirectory(prefix="apmesh-v54-python-") as temporary:
            altered = Path(temporary) / "source.lock"
            contents = lock.read_text(encoding="utf-8")
            # Make every SHA256 spec invalid, even though all exact pins remain.
            altered.write_text(contents.replace("--hash=sha256:", "--hash=sha257:"),
                               encoding="utf-8")
            with self.assertRaisesRegex(
                    DependencyLockError,
                    "python_transitive_pin_without_unique_sha256_hash"):
                audit_python_lock(source, altered)

    def test_python_direct_version_drift_is_refused(self):
        lock = BASE / "locks/requirements-native-pdf-ci-linux-py313.lock"
        with TemporaryDirectory(prefix="apmesh-v54-python-") as temporary:
            altered = Path(temporary) / "requirements.txt"
            altered.write_text("matplotlib==0.0.0\n", encoding="utf-8")
            with self.assertRaisesRegex(
                    DependencyLockError,
                    "python_direct_versions_drift_from_hash_lock"):
                audit_python_lock(altered, lock)

    def test_npm_and_python_source_hash_files_have_cross_platform_lf(self):
        # Windows CRLF checkout must not change the SHA256 file inventory.
        files = [
            BASE / "web/package.json",
            BASE / "web/package-lock.json",
            BASE / "requirements-web-ci.txt",
            BASE / "requirements-native-pdf-ci.txt",
        ] + [BASE / "locks" / name for _, name, _ in PROFILES]
        for source in files:
            with self.subTest(source=source.name):
                raw = source.read_bytes()
                self.assertGreater(len(raw), 100)
                self.assertIn(bytes([10]), raw)
                self.assertNotIn(bytes([13, 10]), raw)

    def test_each_lock_must_exist_and_be_bounded(self):
        with TemporaryDirectory(prefix="apmesh-v54-absence-") as temporary:
            missing = Path(temporary) / "missing.lock"
            with self.assertRaises(DependencyLockError):
                audit_npm_lock(BASE / "web/package.json", missing)
            with self.assertRaises(DependencyLockError):
                audit_python_lock(BASE / "requirements-web-ci.txt", missing)


if __name__ == "__main__":
    unittest.main()
