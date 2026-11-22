"""Produce a deterministic, source-lock-scoped CycloneDX component inventory.

This is an inventory of permitted locked dependencies, not a claim about
installed artifacts, independently verified licenses, CVEs, or native C++.
"""

from __future__ import annotations

import argparse
from base64 import b64decode
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import quote

from .dependency_lock_audit import (
    HASH, PIN, PROFILES, ROOT, DependencyLockError, audit_all, require,
)

NPM_INTEGRITY = re.compile(r"^sha(256|384|512)-([A-Za-z0-9+/=]+)$")
PROFILE_NAMES = {
    "requirements-web-ci-linux-py313.lock": "api-linux-py313",
    "requirements-web-ci-windows-py313.lock": "api-windows-py313",
    "requirements-native-pdf-ci-linux-py313.lock": "native-pdf-linux-py313",
}


def property_value(name: str, value: object) -> dict[str, str]:
    return {"name": "apmesh:" + name, "value": str(value)}


def npm_components(lock: dict) -> list[dict]:
    """Read each recorded install path, including distinct nested copies."""
    result: list[dict] = []
    for path, package in sorted(lock["packages"].items()):
        if not path:
            continue
        require(isinstance(package, dict) and "node_modules/" in path,
                "invalid_npm_package_path")
        name = path.rsplit("node_modules/", 1)[1]
        require(bool(name) and name != "." and isinstance(package.get("version"), str),
                "invalid_npm_component_name_or_version")
        integrity = package.get("integrity")
        match = NPM_INTEGRITY.fullmatch(integrity) if isinstance(integrity, str) else None
        require(match is not None, "unrecognized_npm_integrity")
        algorithm, encoded = match.groups()
        try:
            raw = b64decode(encoded, validate=True)
        except ValueError as error:
            raise DependencyLockError("invalid_npm_integrity_base64") from error
        require(len(raw) == int(algorithm) // 8, "wrong_npm_integrity_digest_length")
        declared_license = package.get("license")
        require(declared_license is None or
                (isinstance(declared_license, str) and bool(declared_license.strip())),
                "invalid_npm_license_declaration")
        npm_name = "/".join(quote(part, safe="") for part in name.split("/"))
        properties = [
            property_value("lock:ecosystem", "npm"),
            property_value("lock:install-path", path),
            property_value("lock:dev", str(bool(package.get("dev"))).lower()),
            property_value("lock:optional", str(bool(package.get("optional"))).lower()),
            property_value("license:status", "declared-unverified"
                           if declared_license is not None else "unavailable"),
        ]
        if declared_license is not None:
            properties.append(property_value("license:lock-declaration", declared_license))
        result.append({
            "type": "library",
            "bom-ref": "npm:" + path + "@" + package["version"],
            "name": name,
            "version": package["version"],
            "purl": "pkg:npm/" + npm_name + "@" + quote(package["version"], safe=""),
            "hashes": [{"alg": "SHA-" + algorithm, "content": raw.hex()}],
            "properties": properties,
        })
    return result


def python_components(lock_text: str, profile: str) -> list[dict]:
    """Record allowed wheel-hash sets without calling them installed files."""
    matches = list(PIN.finditer(lock_text))
    result: list[dict] = []
    names: set[str] = set()
    for index, match in enumerate(matches):
        name = re.sub(r"[-_.]+", "-", match.group(1).lower())
        version = match.group(2)
        require(name not in names, "duplicate_python_sbom_name")
        names.add(name)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(lock_text)
        hashes = HASH.findall(lock_text[match.end():end])
        require(bool(hashes) and len(set(hashes)) == len(hashes),
                "missing_or_duplicate_python_distribution_hash")
        digest = sha256(("\n".join(sorted(hashes)) + "\n").encode("ascii")).hexdigest()
        result.append({
            "type": "library",
            "bom-ref": "pypi:" + profile + ":" + name + "@" + version,
            "name": name,
            "version": version,
            "purl": "pkg:pypi/" + quote(name, safe="") + "@" + quote(version, safe=""),
            "properties": [
                property_value("lock:ecosystem", "pypi"),
                property_value("lock:profile", profile),
                property_value("lock:allowed-distribution-sha256-count", len(hashes)),
                property_value("lock:allowed-distribution-hash-set-sha256", digest),
                property_value("license:status", "unavailable"),
            ],
        })
    return sorted(result, key=lambda item: item["bom-ref"])


def build_source_inventory(root: Path = ROOT) -> tuple[dict, dict]:
    """Revalidate manifests and locks before admitting any SBOM data."""
    audited = audit_all(root)
    base = root / "tools/mesh_studio"
    npm_lock = json.loads((base / "web/package-lock.json").read_text(encoding="utf-8"))
    npm = npm_components(npm_lock)
    python: list[dict] = []
    for _, filename, _ in PROFILES:
        profile = PROFILE_NAMES[filename]
        source = (base / "locks" / filename).read_text(encoding="utf-8")
        python.extend(python_components(source, profile))

    declarations = Counter()
    missing_npm = []
    for package in npm_lock["packages"]:
        if not package:
            continue
        license_text = npm_lock["packages"][package].get("license")
        if license_text is None:
            missing_npm.append(package)
        else:
            declarations[license_text] += 1

    npm_meta = audited["npm"]
    properties = [
        property_value("inventory:scope", "source-locked-permitted-components-not-installed-runtime"),
        property_value("inventory:npm-lock-sha256", npm_meta["npm_lock_sha256"]),
        property_value("inventory:npm-manifest-sha256", npm_meta["source_manifest_sha256"]),
        property_value("inventory:license-evidence", "lock-declaration-only-no-legal-verification"),
        property_value("inventory:original-cpp-acceptance", "not-executed"),
    ]
    for lock_name, record in sorted(audited["python"].items()):
        properties.extend([
            property_value("inventory:" + lock_name + ":sha256", record["lock_sha256"]),
            property_value("inventory:" + lock_name + ":source-sha256",
                           record["source_manifest_sha256"]),
        ])

    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": "apmesh-mesh-studio-source-lock-inventory",
                "version": "v5.6-experimental",
            },
            "properties": properties,
        },
        "components": npm + python,
    }
    ledger = {
        "schema": "apmesh.meshstudio.v56.license_evidence.v1",
        "scope": "lock-declarations-only; not package-source-license validation",
        "npm": {
            "package_count": len(npm),
            "with_lock_license_declaration": sum(declarations.values()),
            "without_lock_license_declaration": len(missing_npm),
            "declared_license_expressions": dict(sorted(declarations.items())),
            "unknown_install_paths": sorted(missing_npm),
        },
        "python": {
            "package_profile_records": len(python),
            "profile_counts": dict(sorted(Counter(
                next(p["value"] for p in c["properties"]
                     if p["name"] == "apmesh:lock:profile") for c in python
            ).items())),
            "license_status": "unavailable-in-pip-compile-locks",
            "license_records_verified": 0,
        },
        "unqualified": [
            "actual_platform_installed_wheel_selection",
            "independent_license_text_and_notice_audit",
            "dependency_vulnerability_and_suspicious_package_triage",
            "native_cpp_third_party_and_os_packages",
            "complete_runtime_and_build_graph",
            "signed_offline_distribution",
        ],
    }
    return bom, ledger


def write_inventory(directory: Path, root: Path = ROOT) -> dict:
    bom, ledger = build_source_inventory(root)
    directory.mkdir(parents=True, exist_ok=True)
    output = {}
    for name, data in (
        ("mesh-studio-v56-source-lock.cdx.json", bom),
        ("mesh-studio-v56-license-evidence.json", ledger),
    ):
        raw = (json.dumps(data, sort_keys=True, indent=2, ensure_ascii=True) + "\n")
        (directory / name).write_text(raw, encoding="utf-8", newline="\n")
        output[name] = {"sha256": sha256(raw.encode("utf-8")).hexdigest(),
                        "bytes": len(raw.encode("utf-8"))}
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print("V56_LOCK_SOURCE_SBOM=" +
          json.dumps(write_inventory(args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
