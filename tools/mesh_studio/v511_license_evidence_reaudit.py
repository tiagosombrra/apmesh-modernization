"""Independently reopen both OS installed license file samples and source locks.

This verifies only the recorded exact bytes, versions and installation
provenance; it never claims license compatibility, all bundle contributions,
CVE freedom or permission to distribute a public binary.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

from . import local_launcher
from .dependency_lock_audit import audit_all
from .v511_runtime_license_evidence import BROWSER_DIRECT, SCHEMA

PACKAGE_PREFIX = "mesh-studio-v511-installed-license-"
HOSTS = ("ubuntu-24.04", "windows-2022")
EXPECTED_STATIC_SHA = "ad6c4627090a335c0ed7e3bf1bae0c0d062ed1e48249f120b10f3ba8ff8a85f5"
MAX_REPORT_BYTES = 400_000


class LicenseProofError(ValueError):
    """Independent evidence receipt was modified, incomplete or forged."""


def require(ok: bool, code: str) -> None:
    if not ok:
        raise LicenseProofError("v511_license_proof_" + code)


def read_json(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink() and
            path.stat().st_size <= MAX_REPORT_BYTES, "missing_bounded_report")
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate_json_key")
            result[key] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=unique_pairs)


def verify_notices(root: Path, receipts: tuple[dict, dict]) -> dict:
    """Reject absent/extra notice files, path traversal, symlinks and hash drift."""
    expected = set()
    verified = 0
    for report in receipts:
        records = report["packages"] if report["scope"].startswith("isolated_") \
            else report["npm_entries"]
        for package in records.values():
            for item in package["license_files"]:
                text = item["path"]
                require(isinstance(text, str) and text.startswith("notices/") and
                        "\\" not in text and "%" not in text and
                        all(part not in (".", "..", "") for part in PurePosixPath(text).parts),
                        "unsafe_notice_path")
                require(text not in expected, "duplicate_notice_path")
                expected.add(text)
                target = root.joinpath(*text.split("/"))
                require(target.is_file() and not target.is_symlink() and
                        all(not parent.is_symlink() for parent in
                            target.parents if parent != root.parent),
                        "missing_or_symlinked_notice")
                data = target.read_bytes()
                require(len(data) == item["size"] and
                        sha256(data).hexdigest() == item["sha256"],
                        "installed_license_text_changed")
                verified += 1
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    require(not any(x.is_symlink() for x in root.rglob("*")),
            "symlink_in_evidence_archive")
    require(actual == expected | {"python-installed-evidence.json",
                                  "npm-installed-evidence.json"},
            "missing_or_added_license_evidence_file")
    return {"notice_files_reopened": verified, "license_bytes_rehashed": True}


def review(directory: Path, commit: str) -> dict:
    require(len(commit) == 40 and all(ch in "0123456789abcdef" for ch in commit),
            "invalid_commit")
    require(directory.is_dir() and not directory.is_symlink(),
            "missing_source_artifact_root")
    expected_folders = {PACKAGE_PREFIX + host + "-" + commit for host in HOSTS}
    require({p.name for p in directory.iterdir()} == expected_folders,
            "require_exact_two_host_artifacts")
    original = audit_all()
    lock = original["npm"]["npm_lock_sha256"]
    source = json.loads((local_launcher.WEB / "package-lock.json").read_bytes())
    root_packages = {p for p in source["packages"] if p}
    results = {}
    for host in HOSTS:
        folder = directory / (PACKAGE_PREFIX + host + "-" + commit)
        root = folder / "build/v511-license-evidence"
        python = read_json(root / "python-installed-evidence.json")
        npm = read_json(root / "npm-installed-evidence.json")
        require(python["schema"] == npm["schema"] == SCHEMA and
                python["scope"] == "isolated_13_package_python_runtime" and
                npm["scope"] == "npm_installed_lock_packages_and_static_browser_build" and
                python["package_count"] == len(local_launcher.MINIMAL) == 13 and
                set(python["packages"]) == set(local_launcher.MINIMAL) and
                python["original_python_source_lock_sha256"] ==
                original["python"]["requirements-web-ci-" + (
                    "linux" if host == "ubuntu-24.04" else "windows") +
                    "-py313.lock"]["lock_sha256"] and
                npm["npm_source_lock_sha256"] == lock and
                npm["npm_lock_package_count"] == len(root_packages) and
                set(npm["npm_entries"]) == root_packages and
                npm["static_build_inventory_sha256"] == EXPECTED_STATIC_SHA and
                npm["static_build_asset_count"] == 7 and
                python["pymupdf_present_in_minimal_server"] is False and
                python["legal_distribution_approved"] is False and
                npm["legal_distribution_approved"] is False and
                npm["bundled_js_legal_notice_assembly_verified"] is False,
                "installed_runtime_scope_or_lock_invalid")
        for name, version in local_launcher._project_hash_lock(
            (local_launcher.ROOT / "tools/mesh_studio/locks" /
             ("requirements-web-ci-linux-py313.lock" if host=="ubuntu-24.04"
              else "requirements-web-ci-windows-py313.lock")
            ).read_text(encoding="utf-8"), "source-only")[1].items():
            require(python["packages"][name]["version"] == version,
                    "python_distribution_version_drift")
        for path, source_pkg in source["packages"].items():
            if not path:
                continue
            item = npm["npm_entries"][path]
            require(item["version"] == source_pkg["version"] and
                    item["registry_integrity"] == source_pkg["integrity"] and
                    item["registry_resolved"] == source_pkg["resolved"] and
                    item["lock_license_declaration"] == source_pkg.get("license"),
                    "installed_npm_source_claim_drift")
        for name in BROWSER_DIRECT:
            require(npm["npm_entries"]["node_modules/" + name]["installed"],
                    "missing_direct_browser_package")
        proof = verify_notices(root, (python, npm))
        missing_python = python["packages_without_installed_license_text"]
        missing_npm = npm["installed_packages_without_license_text"]
        rechoir = npm["npm_entries"].get("node_modules/rechoir")
        require(rechoir is not None and
                rechoir["lock_license_declaration"] is None,
                "rechoir_missing_declaration_issue_not_reproduced")
        results[host] = {
            "minimal_python_runtime_package_count": 13,
            "npm_source_package_count": len(root_packages),
            "installed_npm_count": sum(v["installed"] for v in npm["npm_entries"].values()),
            "installed_notice_files_rehashed": proof["notice_files_reopened"],
            "python_missing_license_text": missing_python,
            "npm_missing_license_text": missing_npm,
            "rechoir_installed": rechoir["installed"],
            "rechoir_actual_license_text_files": rechoir["license_files"],
            "browser_runtime_direct": sorted(BROWSER_DIRECT),
            "full_python_research_environment_audited": False,
            "bundle_dependency_license_closure_verified": False,
        }
    return {
        "schema": "apmesh.meshstudio.v511.two_os_installed_license_evidence_v1",
        "code_sha": commit,
        "source_npm_lock_sha256": lock,
        "static_build_inventory_sha256": EXPECTED_STATIC_SHA,
        "os_results": results,
        "cross_host_source_lock_bound": True,
        "individual_license_text_bytes_read_again_and_verified": True,
        "browser_bundle_distribution_notices_complete": False,
        "complete_scientific_python_environment_license_reviewed": False,
        "legal_license_distribution_approved": False,
        "original_cpp_source_changed": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = review(args.directory, args.head_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True,
                                      indent=2, allow_nan=False) + "\n",
                           encoding="utf-8", newline="\n")
    print("V511_LICENSE_TWO_OS_REOPEN=" + json.dumps({
        "linux_notices": receipt["os_results"][HOSTS[0]]["installed_notice_files_rehashed"],
        "windows_notices": receipt["os_results"][HOSTS[1]]["installed_notice_files_rehashed"],
        "same_npm_source_sha": receipt["source_npm_lock_sha256"],
        "distribution_authorized": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
