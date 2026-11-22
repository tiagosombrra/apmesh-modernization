"""Fail-closed synthetic and real-lock controls for the V5.6 source SBOM."""

from __future__ import annotations

from base64 import b64encode
from hashlib import sha256
import json
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory
import unittest

from .dependency_lock_audit import DependencyLockError, PROFILES, ROOT
from .source_sbom import (
    build_source_inventory, npm_components, python_components, write_inventory,
)


class SourceSBOMTests(unittest.TestCase):
    def test_actual_lock_closure_and_license_uncertainty(self):
        bom, ledger = build_source_inventory()
        self.assertEqual((bom["bomFormat"], bom["specVersion"]),
                         ("CycloneDX", "1.6"))
        self.assertEqual(len(bom["components"]), 220)
        self.assertEqual(ledger["npm"]["package_count"], 141)
        self.assertEqual(ledger["npm"]["with_lock_license_declaration"], 140)
        self.assertEqual(ledger["npm"]["without_lock_license_declaration"], 1)
        self.assertEqual(ledger["npm"]["unknown_install_paths"],
                         ["node_modules/rechoir"])
        self.assertEqual(ledger["python"]["package_profile_records"], 79)
        self.assertEqual(ledger["python"]["license_records_verified"], 0)
        vtk = next(c for c in bom["components"]
                   if c["bom-ref"] == "npm:node_modules/@kitware/vtk.js@38.0.9")
        self.assertEqual(vtk["purl"], "pkg:npm/%40kitware/vtk.js@38.0.9")
        self.assertEqual(vtk["hashes"][0]["alg"], "SHA-512")
        self.assertEqual(len(vtk["hashes"][0]["content"]), 128)

    def test_python_hash_sets_are_not_misrepresented_as_installed_wheels(self):
        bom, _ = build_source_inventory()
        python = [c for c in bom["components"]
                  if c["bom-ref"].startswith("pypi:")]
        self.assertEqual(len(python), 79)
        self.assertTrue(all("hashes" not in c for c in python))
        for item in python:
            props = {p["name"]: p["value"] for p in item["properties"]}
            self.assertEqual(props["apmesh:license:status"], "unavailable")
            self.assertGreater(int(props[
                "apmesh:lock:allowed-distribution-sha256-count"]), 0)
            self.assertEqual(len(props[
                "apmesh:lock:allowed-distribution-hash-set-sha256"]), 64)

    def test_sbom_and_ledger_are_byte_reproducible(self):
        with TemporaryDirectory(prefix="v56-sbom-a-") as a, TemporaryDirectory(
                prefix="v56-sbom-b-") as b:
            first = write_inventory(Path(a))
            second = write_inventory(Path(b))
            self.assertEqual(first, second)
            for name, record in first.items():
                raw = (Path(a) / name).read_bytes()
                self.assertEqual(raw, (Path(b) / name).read_bytes())
                self.assertEqual(sha256(raw).hexdigest(), record["sha256"])
                self.assertEqual(len(raw), record["bytes"])
                self.assertTrue(isinstance(json.loads(raw), dict))

    def test_invalid_npm_hash_and_unverified_license_are_not_promoted(self):
        fake = {"packages": {"node_modules/fake": {
            "version": "1.0.0", "integrity": "sha512-invalid!"
        }}}
        with self.assertRaises(DependencyLockError):
            npm_components(fake)
        fake["packages"]["node_modules/fake"]["integrity"] = (
            "sha512-" + b64encode(bytes(64)).decode("ascii"))
        result = npm_components(fake)
        self.assertEqual(result[0]["name"], "fake")
        self.assertIn("apmesh:license:status", [
            prop["name"] for prop in result[0]["properties"]])
        self.assertFalse(any(prop["name"] == "apmesh:license:lock-declaration"
                             for prop in result[0]["properties"]))

    def test_missing_python_hash_fails_closed(self):
        with self.assertRaisesRegex(
                DependencyLockError, "missing_or_duplicate_python_distribution_hash"):
            python_components("example==1.0.0\n", "api-linux-py313")

    def test_preflight_rejects_direct_dependency_drift(self):
        with TemporaryDirectory(prefix="v56-sbom-drift-") as temporary:
            root = Path(temporary)
            source = ROOT / "tools/mesh_studio"
            target = root / "tools/mesh_studio"
            (target / "web").mkdir(parents=True)
            (target / "locks").mkdir(parents=True)
            for relative in ["web/package.json", "web/package-lock.json",
                             "requirements-web-ci.txt", "requirements-native-pdf-ci.txt"]:
                copy2(source / relative, target / relative)
            for _, filename, _ in PROFILES:
                copy2(source / "locks" / filename, target / "locks" / filename)
            direct = target / "requirements-web-ci.txt"
            direct.write_text(direct.read_text(encoding="utf-8").replace(
                "fastapi==0.128.2", "fastapi==0.0.1"), encoding="utf-8")
            with self.assertRaises(DependencyLockError):
                build_source_inventory(root)


if __name__ == "__main__":
    unittest.main()
