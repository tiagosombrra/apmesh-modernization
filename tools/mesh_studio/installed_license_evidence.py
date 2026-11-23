"""Collect bounded license-file evidence from hash-locked installed packages.

The resulting file records actual installed metadata and text digests, not
legal compatibility, distribution completeness, CVE status or archive hashes.
Install each environment with npm ci or pip --require-hashes before scanning.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from importlib import metadata
import json
import os
from pathlib import Path
import re

from .dependency_lock_audit import ROOT, PIN, DependencyLockError, audit_all, require

LICENSE_FILE = re.compile(r"^(licen[sc]e|copying|notice|copyright)(?:[.\-_ ].*)?$", re.I)
NPM_PRIORITY = (
    "node_modules/rechoir",
    "node_modules/argparse",
    "node_modules/caniuse-lite",
    "node_modules/pako",
    "node_modules/spark-md5",
    "node_modules/lightningcss",
)
PY_LOCKS = {
    "api-linux": "requirements-web-ci-linux-py313.lock",
    "api-windows": "requirements-web-ci-windows-py313.lock",
    "native-pdf-linux": "requirements-native-pdf-ci-linux-py313.lock",
}
MAX_LICENSE_BYTES = 1_000_000
MAX_LICENSE_FILES_PER_PACKAGE = 40


def _sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _metadata_field(value: str | None) -> dict:
    """Avoid embedding arbitrary license text or unbounded metadata in receipts."""
    if not value:
        return {"status": "absent"}
    data = value.encode("utf-8")
    return {
        "status": "recorded",
        "sha256": _sha(data),
        "bytes": len(data),
        "short_expression": value if len(value) <= 120 and "\n" not in value else None,
    }


def license_file_receipts(directory: Path, base: Path, depth: int = 3) -> list[dict]:
    """Hash bounded file bytes only; do not follow links or leave package roots."""
    directory = directory.resolve()
    base = base.resolve()
    require(directory.is_relative_to(base), "license_scan_outside_install_base")
    files: list[dict] = []
    if not directory.is_dir():
        return files

    for parent, dirs, names in os.walk(directory, followlinks=False):
        current = Path(parent)
        rel = current.relative_to(directory)
        if len(rel.parts) >= depth:
            dirs[:] = []
        else:
            dirs[:] = sorted(d for d in dirs if d not in
                             ("node_modules", ".git", ".cache") and
                             not (current / d).is_symlink())
        for name in sorted(names):
            if LICENSE_FILE.fullmatch(name) is None:
                continue
            path = current / name
            if path.is_symlink() or not path.is_file():
                continue
            resolved = path.resolve()
            require(resolved.is_relative_to(directory) and
                    resolved.is_relative_to(base), "license_file_outside_install_base")
            size = path.stat().st_size
            if size > MAX_LICENSE_BYTES:
                files.append({"path": path.relative_to(directory).as_posix(),
                              "status": "oversize_unread", "bytes": size})
            else:
                raw = path.read_bytes()
                files.append({"path": path.relative_to(directory).as_posix(),
                              "status": "hash-recorded",
                              "bytes": len(raw), "sha256": _sha(raw)})
            require(len(files) <= MAX_LICENSE_FILES_PER_PACKAGE,
                    "unbounded_license_file_inventory")
    return files


def collect_installed_npm(root: Path = ROOT) -> dict:
    """Map immutable-lock install paths to locally unpacked files."""
    audited = audit_all(root)
    web = root / "tools/mesh_studio/web"
    lock = json.loads((web / "package-lock.json").read_text(encoding="utf-8"))
    items: list[dict] = []
    statuses: Counter[str] = Counter()

    for rel, locked in sorted(lock["packages"].items()):
        if not rel:
            continue
        require(rel.startswith("node_modules/") and
                ".." not in Path(rel).parts and not Path(rel).is_absolute(),
                "untrusted_npm_install_path")
        folder = web / rel
        absent = not folder.is_dir()
        if absent and not locked.get("optional"):
            raise DependencyLockError("missing_nonoptional_installed_npm:" + rel)
        entry = {
            "install_path": rel,
            "name": rel.rsplit("node_modules/", 1)[-1],
            "lock_version": locked["version"],
            "lock_integrity": locked["integrity"],
            "lock_license_declaration": locked.get("license"),
            "development_dependency": bool(locked.get("dev")),
            "optional_dependency": bool(locked.get("optional")),
            "status": "not_installed_optional" if absent else "installed",
            "installed_manifest_license": {"status": "not_installed"},
            "license_files": [],
        }
        if not absent:
            package_json = folder / "package.json"
            require(package_json.is_file() and not package_json.is_symlink(),
                    "missing_installed_npm_package_manifest:" + rel)
            raw = package_json.read_bytes()
            info = json.loads(raw)
            require(info.get("version") == locked["version"] and
                    info.get("name") == entry["name"],
                    "installed_npm_name_or_version_drift:" + rel)
            entry["installed_manifest_sha256"] = _sha(raw)
            declared = info.get("license")
            entry["installed_manifest_license"] = _metadata_field(
                declared if isinstance(declared, str) else None)
            entry["license_files"] = license_file_receipts(folder, web, depth=3)
        statuses[entry["status"]] += 1
        items.append(entry)

    rechoir = next((item for item in items
                    if item["install_path"] == "node_modules/rechoir"), None)
    require(rechoir is not None and rechoir["lock_version"] == "0.6.2",
            "unrecognized_rechoir_original_lock_version")
    return {
        "schema": "apmesh.meshstudio.v561.installed_license_evidence.v1",
        "profile": "npm-linux-node22-npm10",
        "provenance": "npm-ci-ignore-scripts-from-audited-lock",
        "source_lock_sha256": audited["npm"]["npm_lock_sha256"],
        "qualification": "metadata_and_file_bytes_only_not_license_approval",
        "statuses": dict(sorted(statuses.items())),
        "focus_paths": list(NPM_PRIORITY),
        "components": items,
    }


def collect_installed_python(profile: str, root: Path = ROOT) -> dict:
    """Match installed distribution metadata to the exact OS-specific lock."""
    require(profile in PY_LOCKS, "unrecognized_python_lock_profile")
    audits = audit_all(root)
    name = PY_LOCKS[profile]
    path = root / "tools/mesh_studio/locks" / name
    source = path.read_text(encoding="utf-8")
    pins = PIN.findall(source)
    seen: set[str] = set()
    items: list[dict] = []
    for raw_name, version in pins:
        key = _name(raw_name)
        require(key not in seen, "duplicate_python_installed_dependency")
        seen.add(key)
        try:
            dist = metadata.distribution(raw_name)
        except metadata.PackageNotFoundError as error:
            raise DependencyLockError("missing_installed_python_distribution:" + key) from error
        require(dist.version == version, "installed_python_version_drift:" + key)
        dist_name = dist.metadata.get("Name")
        require(dist_name is not None and _name(dist_name) == key,
                "installed_python_distribution_name_drift:" + key)

        files = []
        for rel in sorted(dist.files or [], key=lambda p: str(p)):
            basename = Path(str(rel)).name
            if LICENSE_FILE.fullmatch(basename) is None:
                continue
            local = Path(dist.locate_file(rel))
            if local.is_symlink() or not local.is_file():
                continue
            size = local.stat().st_size
            if size > MAX_LICENSE_BYTES:
                files.append({"path": str(rel).replace("\\", "/"),
                              "status": "oversize_unread", "bytes": size})
            else:
                raw = local.read_bytes()
                files.append({"path": str(rel).replace("\\", "/"),
                              "status": "hash-recorded",
                              "bytes": len(raw), "sha256": _sha(raw)})
            require(len(files) <= MAX_LICENSE_FILES_PER_PACKAGE,
                    "unbounded_python_license_inventory")

        record = dist.read_text("RECORD")
        classifiers = dist.metadata.get_all("Classifier") or []
        items.append({
            "name": key,
            "version": version,
            "installed_metadata_name": dist_name,
            "metadata_license_expression": _metadata_field(
                dist.metadata.get("License-Expression")),
            "metadata_legacy_license": _metadata_field(dist.metadata.get("License")),
            "metadata_license_classifiers": sorted(
                v for v in classifiers if v.startswith("License :: "))[:30],
            "installed_record_sha256": _sha(record.encode("utf-8"))
            if record is not None else None,
            "license_files": files,
        })

    return {
        "schema": "apmesh.meshstudio.v561.installed_license_evidence.v1",
        "profile": profile,
        "provenance": "pip-require-hashes-from-matching-os-lock",
        "source_lock_sha256": audits["python"][name]["lock_sha256"],
        "qualification": "installed_metadata_and_file_bytes_not_wheel_archive_identity",
        "component_count": len(items),
        "components": sorted(items, key=lambda x: x["name"]),
    }


def write_evidence(report: dict, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / ("mesh-studio-v561-" + report["profile"] + ".json")
    raw = (json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n")
    target.write_text(raw, encoding="utf-8", newline="\n")
    return {"name": target.name, "sha256": _sha(raw.encode("utf-8")),
            "bytes": len(raw.encode("utf-8")), "components": len(report["components"])}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("npm", "python"), required=True)
    parser.add_argument("--profile", choices=tuple(PY_LOCKS),
                        default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "npm":
        require(args.profile is None, "npm_python_profile_unexpected")
        receipt = collect_installed_npm()
    else:
        require(args.profile is not None, "missing_python_profile")
        receipt = collect_installed_python(args.profile)
    print("V561_INSTALLED_LICENSE_EVIDENCE=" +
          json.dumps(write_evidence(receipt, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
