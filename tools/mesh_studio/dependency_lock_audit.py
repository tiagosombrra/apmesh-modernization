"""Independently validate bounded Studio npm and platform-specific Python hash locks.

This checks source manifest closure and package hashes without fetching registries.
Actual npm ci / pip --require-hashes installation is a separate mandatory CI gate.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
LOCK_DIR = ROOT / "tools/mesh_studio/locks"
PROFILES = (
    ("requirements-web-ci.txt", "requirements-web-ci-linux-py313.lock", 30),
    ("requirements-web-ci.txt", "requirements-web-ci-windows-py313.lock", 30),
    ("requirements-native-pdf-ci.txt", "requirements-native-pdf-ci-linux-py313.lock", 14),
)
PIN = re.compile(r"(?m)^([A-Za-z][A-Za-z0-9_.-]*)==([^\s\\;]+)")
HASH = re.compile(r"--hash=sha256:([0-9a-f]{64})(?=\s|\\|$)")
INTEGRITY = re.compile(r"^sha(?:512|384|256)-[a-zA-Z0-9+/=]+$")


class DependencyLockError(ValueError):
    """An admitted dependency lock is missing or contradicts its manifest."""


def require(ok: bool, description: str) -> None:
    if not ok:
        raise DependencyLockError(description)


def _object_pairs(pairs: list[tuple[str, object]]) -> dict:
    out: dict = {}
    for key, value in pairs:
        require(key not in out, "duplicate_dependency_lock_json_key")
        out[key] = value
    return out


def audit_npm_lock(manifest_path: Path, lock_path: Path) -> dict:
    require(manifest_path.is_file() and lock_path.is_file() and
            10000 < lock_path.stat().st_size < 500_000,
            "npm_lock_missing_or_unbounded")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"),
                          object_pairs_hook=_object_pairs)
    lock = json.loads(lock_path.read_text(encoding="utf-8"),
                      object_pairs_hook=_object_pairs)
    packages = lock.get("packages")
    require(type(packages) is dict and len(packages) >= 100 and
            lock.get("lockfileVersion") == 3 and
            lock.get("name") == manifest.get("name") and
            lock.get("version") == manifest.get("version"),
            "npm_lock_version_root_or_inventory_invalid")
    root = packages.get("")
    require(type(root) is dict and
            root.get("dependencies") == manifest.get("dependencies") and
            root.get("devDependencies") == manifest.get("devDependencies"),
            "npm_lock_root_direct_dependency_drift")
    count = 0
    for path, package in packages.items():
        if not path:
            continue
        require(type(package) is dict and path.startswith("node_modules/") and
                bool(package.get("version")),
                "npm_lock_invalid_transitive_package")
        resolved = package.get("resolved")
        require(type(resolved) is str and
                resolved.startswith("https://registry.npmjs.org/") and
                type(package.get("integrity")) is str and
                INTEGRITY.fullmatch(package["integrity"]) is not None,
                "npm_lock_missing_integrity_or_untrusted_registry")
        count += 1
    return {
        "status": "npm_lock_validated",
        "packages": count,
        "npm_lock_sha256": sha256(lock_path.read_bytes()).hexdigest(),
        "source_manifest_sha256": sha256(manifest_path.read_bytes()).hexdigest(),
    }


def _pins(text: str) -> dict[str, str]:
    matches = list(PIN.finditer(text))
    require(len(matches) > 0, "empty_or_unpinned_python_dependencies")
    values = {}
    for match in matches:
        key = re.sub(r"[-_.]+", "-", match.group(1).lower())
        require(key not in values, "duplicate_python_dependency_pin")
        values[key] = match.group(2)
    return values


def audit_python_lock(direct_path: Path, lock_path: Path,
                      min_packages: int = 10) -> dict:
    require(direct_path.is_file() and lock_path.is_file() and
            2500 < lock_path.stat().st_size < 250_000,
            "python_hash_lock_missing_or_unbounded")
    direct = direct_path.read_text(encoding="utf-8")
    locked = lock_path.read_text(encoding="utf-8")
    direct_pins = _pins(direct)
    all_pins = _pins(locked)
    require(len(all_pins) >= max(min_packages, len(direct_pins)) and
            all(all_pins.get(key) == version
                for key, version in direct_pins.items()),
            "python_direct_versions_drift_from_hash_lock")
    rows = list(PIN.finditer(locked))
    full_hash_count = 0
    for n, match in enumerate(rows):
        block = locked[match.end():rows[n + 1].start()
                       if n + 1 < len(rows) else len(locked)]
        hashes = HASH.findall(block)
        require(hashes and len(set(hashes)) == len(hashes),
                "python_transitive_pin_without_unique_sha256_hash")
        full_hash_count += len(hashes)
    require("git+" not in locked and "\n-e " not in locked and
            "--extra-index-url" not in locked and
            "--trusted-host" not in locked,
            "python_lock_unqualified_external_dependency")
    return {
        "status": "python_sha256_hash_lock_validated",
        "packages": len(all_pins),
        "sha256_hashes": full_hash_count,
        "direct_pins": len(direct_pins),
        "lock_sha256": sha256(lock_path.read_bytes()).hexdigest(),
        "source_manifest_sha256": sha256(direct_path.read_bytes()).hexdigest(),
    }


def audit_all(root: Path = ROOT) -> dict:
    base = root / "tools/mesh_studio"
    result = {
        "schema": "apmesh.meshstudio.v54.dependency_lock_audit.v1",
        "npm": audit_npm_lock(base / "web/package.json",
                              base / "web/package-lock.json"),
        "python": {},
        "native_cpp_scientific_policy_changed": False,
        "physical_gpu_qualified": False,
        "hash_aware_runtime_installs_still_required": True,
    }
    for source, target, minimum in PROFILES:
        result["python"][target] = audit_python_lock(
            base / source, base / "locks" / target, minimum)
    return result


def main() -> None:
    print("V54_DEPENDENCY_HASH_LOCK_AUDIT=" +
          json.dumps(audit_all(), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
