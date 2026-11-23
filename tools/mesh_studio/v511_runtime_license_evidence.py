"""Collect installed, source-lock-bound license NOTICE evidence for local V5.11.

This is an evidence inventory, NOT legal approval, binary-content attribution,
a software release, or a substitute for reviewing all derivative notices.
All copied license texts come from installed package files, never guessed SPDX.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from importlib import metadata
import json
from pathlib import Path
import re
import shutil

from . import local_launcher, local_static_site
from .dependency_lock_audit import audit_npm_lock

SCHEMA = "apmesh.meshstudio.v511.installed_license_source_evidence.v1"
NOTICE = re.compile(r"(?i)^(?:licen[sc]e|copying|copyright|notice|authors)(?:[._ -].*)?$")
MAX_NOTICE = 700_000
MAX_PACKAGE_NOTICES = 32
MAX_ITEMS = 256
BROWSER_DIRECT = frozenset({"@kitware/vtk.js", "react", "react-dom"})


class EvidenceError(RuntimeError):
    """An installed package/version, source lock or notice hash is invalid."""


def require(value: bool, message: str) -> None:
    if not value:
        raise EvidenceError("v511_installed_license_" + message)


def sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.lower())


def _write_notice(dest: Path, data: bytes) -> dict:
    require(0 < len(data) < MAX_NOTICE, "unsafe_license_size")
    dest.parent.mkdir(parents=True, exist_ok=True)
    require(not dest.is_symlink(), "refusing_notice_symlink")
    dest.write_bytes(data)
    return {
        "path": dest.as_posix(),
        "size": len(data),
        "sha256": sha(data),
    }


def _python_expected() -> tuple[dict, str]:
    _, report = local_launcher.source_preflight()
    expected = report["minimal_python_packages"]
    require(set(expected) == local_launcher.MINIMAL and len(expected) == 13,
            "minimal_python_closure_drift")
    return expected, report["source_lock_sha256"]


def _python_package_license_files(dist: metadata.Distribution) -> list[tuple[str, bytes]]:
    found = []
    files = dist.files or []
    for entry in files:
        name = Path(str(entry).replace("\\", "/")).name
        if not NOTICE.fullmatch(name):
            continue
        # Distribution metadata paths are ground truth, not arbitrary file search.
        path = Path(dist.locate_file(entry))
        require(path.is_file() and not path.is_symlink(),
                "missing_python_license_path:" + name)
        data = path.read_bytes()
        require(0 < len(data) < MAX_NOTICE, "unbounded_python_license")
        found.append((str(entry).replace("\\", "/"), data))
    require(len(found) <= MAX_PACKAGE_NOTICES, "excess_python_license_files")
    return sorted(found)


def python_receipt(out: Path) -> dict:
    expected, source_lock = _python_expected()
    installed = {}
    for dist in metadata.distributions():
        name = canonical(dist.metadata.get("Name", ""))
        if name not in expected:
            continue
        require(name not in installed, "duplicate_python_install:" + name)
        require(dist.version == expected[name], "python_package_version_drift:" + name)
        files = []
        for index, (source, data) in enumerate(_python_package_license_files(dist)):
            output = _write_notice(
                out / "notices" / "python" / name /
                (f"{index:02d}-{sha(source.encode())[:8]}-{Path(source).name}"),
                data,
            )
            files.append({"source": source, **output})
        # PEP 639 License-Expression is kept separate from legacy License fields.
        declared = dist.metadata.get("License-Expression")
        legacy = dist.metadata.get("License")
        classifiers = sorted(
            x for x in dist.metadata.get_all("Classifier", [])
            if x.startswith("License ::")
        )
        installed[name] = {
            "name": name,
            "version": dist.version,
            "license_expression": declared or None,
            "legacy_license": legacy if legacy and len(legacy) < 250 else None,
            "license_classifiers": classifiers,
            "license_files": files,
            "evidence_class": (
                "installed_license_text_recovered" if files
                else "installed_metadata_only_license_text_unresolved"
            ),
        }
    require(set(installed) == set(expected),
            "minimal_python_package_not_installed:" +
            ",".join(sorted(set(expected)-set(installed))))
    return {
        "schema": SCHEMA,
        "scope": "isolated_13_package_python_runtime",
        "original_python_source_lock_sha256": source_lock,
        "package_count": len(installed),
        "packages": dict(sorted(installed.items())),
        "packages_without_installed_license_text": sorted(
            name for name, value in installed.items()
            if not value["license_files"]
        ),
        "pymupdf_present_in_minimal_server": False,
        "complete_research_python_environment_audited": False,
        "scientific_lod_qualified": False,
        "legal_distribution_approved": False,
    }


def _npm_package_name(path: str) -> str:
    require(path.startswith("node_modules/"), "invalid_npm_package_path")
    tail = path.rsplit("node_modules/", 1)[1]
    require(tail and "/" not in tail if not tail.startswith("@")
            else tail.count("/") == 1, "unsupported_npm_package_path")
    return tail


def _npm_license_files(directory: Path) -> list[tuple[str, bytes]]:
    require(directory.is_dir() and not directory.is_symlink(),
            "installed_npm_package_missing_or_symlink")
    found = []
    for file in sorted(directory.iterdir()):
        if not file.is_file() or file.is_symlink() or not NOTICE.fullmatch(file.name):
            continue
        data = file.read_bytes()
        require(0 < len(data) < MAX_NOTICE, "unbounded_npm_license")
        found.append((file.name, data))
    require(len(found) <= MAX_PACKAGE_NOTICES, "excess_npm_license_files")
    return found


def npm_receipt(out: Path) -> dict:
    web = local_launcher.WEB
    runtime = local_static_site.verify_inventory()
    audit = audit_npm_lock(web / "package.json", web / "package-lock.json")
    lock = json.loads((web / "package-lock.json").read_text(encoding="utf-8"))
    packages = lock["packages"]
    records = {}
    for path, item in sorted(packages.items()):
        if not path:
            continue
        require(len(records) < MAX_ITEMS, "too_many_npm_packages")
        name = _npm_package_name(path)
        package_root = web.joinpath(*path.split("/"))
        installed = package_root.is_dir()
        if not installed:
            require(item.get("optional") is True or
                    bool(item.get("os")) or bool(item.get("cpu")),
                    "missing_nonoptional_npm_package:" + path)
            license_files = []
            installed_declared = None
        else:
            manifest = package_root / "package.json"
            require(manifest.is_file() and not manifest.is_symlink(),
                    "installed_npm_metadata_missing:" + path)
            metadata_json = json.loads(manifest.read_text(encoding="utf-8"))
            require(metadata_json.get("version") == item["version"] and
                    metadata_json.get("name") == name,
                    "installed_npm_package_identity_drift:" + path)
            installed_declared = metadata_json.get("license")
            license_files = []
            for index, (source, data) in enumerate(_npm_license_files(package_root)):
                output = _write_notice(
                    out / "notices" / "npm" / sha(path.encode())[:16] /
                    f"{index:02d}-{source}", data)
                license_files.append({"source": source, **output})
        records[path] = {
            "package": name,
            "version": item["version"],
            "installed": installed,
            "lock_development_only": item.get("dev") is True,
            "lock_optional": item.get("optional") is True,
            "lock_license_declaration": item.get("license"),
            "installed_license_declaration": installed_declared,
            "registry_integrity": item["integrity"],
            "registry_resolved": item["resolved"],
            "license_files": license_files,
            "evidence_class": ("not_installed_optional_platform_dependency"
                               if not installed else
                               "installed_license_text_recovered" if license_files
                               else "installed_metadata_only_license_text_unresolved"),
            "in_bundled_browser_js_certified": False,
        }
    direct = lock["packages"][""]["dependencies"]
    require(set(direct) == BROWSER_DIRECT,
            "browser_direct_dependency_scope_drift")
    require(all(records["node_modules/" + x]["installed"] for x in BROWSER_DIRECT),
            "direct_browser_runtime_package_missing")
    return {
        "schema": SCHEMA,
        "scope": "npm_installed_lock_packages_and_static_browser_build",
        "npm_source_lock_sha256": audit["npm_lock_sha256"],
        "static_build_inventory_sha256": sha(
            (local_static_site.DIST / local_static_site.MANIFEST_NAME).read_bytes()),
        "static_build_asset_count": runtime["static_asset_count"],
        "npm_lock_package_count": audit["packages"],
        "npm_entries": records,
        "direct_browser_dependencies": dict(sorted(direct.items())),
        "source_lock_entries_missing_license_declaration": sorted(
            p for p, v in records.items() if v["lock_license_declaration"] is None),
        "installed_packages_without_license_text": sorted(
            p for p, v in records.items()
            if v["installed"] and not v["license_files"]
        ),
        "installed_package_texts_not_proof_of_actual_js_bundle_contributions": True,
        "dev_and_optional_packages_not_assumed_to_be_shipped": True,
        "bundled_js_legal_notice_assembly_verified": False,
        "scientific_lod_qualified": False,
        "legal_distribution_approved": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("npm", "python"), required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    # Prevent output inside the installed dependency tree from influencing audit.
    out = args.out_dir.resolve()
    require(not str(out).startswith(str(local_launcher.WEB / "node_modules")),
            "report_inside_install_tree")
    out.mkdir(parents=True, exist_ok=True)
    report = python_receipt(out) if args.scope == "python" else npm_receipt(out)
    path = out / (args.scope + "-installed-evidence.json")
    path.write_text(json.dumps(report, sort_keys=True, indent=2,
                               ensure_ascii=False, allow_nan=False) + "\n",
                    encoding="utf-8", newline="\n")
    if args.scope == "python":
        missing = len(report["packages_without_installed_license_text"])
        total = report["package_count"]
    else:
        missing = len(report["installed_packages_without_license_text"])
        total = report["npm_lock_package_count"]
    print("V511_INSTALLED_LICENSE_SOURCE_EVIDENCE=" + json.dumps({
        "scope": args.scope, "package_count": total,
        "installed_packages_without_license_text": missing,
        "notices_copied_from_actual_installed_packages": True,
        "bundled_js_license_review_complete": False,
        "legal_distribution_approved": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
