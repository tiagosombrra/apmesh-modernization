"""Independently compare Vite's source-linked browser bundle licenses to npm.

Vite 8's licence metadata and Rolldown's chunk.modules come from a separate
diagnostic build that must recreate the exact seven certified browser files.
The report is bounded technical evidence, not a legal distribution approval.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

from .v511_license_evidence_reaudit import EXPECTED_STATIC_SHA, HOSTS, read_json
from .v511_runtime_license_evidence import SCHEMA as INSTALLED_SCHEMA

BUNDLE_PREFIX = "mesh-studio-v511-bundle-"
INSTALLED_PREFIX = "mesh-studio-v511-installed-license-"
GRAPH_SCHEMA = "apmesh.meshstudio.v511.rolldown_rendered_source_graph.v1"
PARITY_SCHEMA = "apmesh.meshstudio.v511.diagnostic_bundle_parity.v1"
MAX_LICENSE_BYTES = 2_500_000
MAX_GRAPH_BYTES = 4_000_000
MAX_LICENSE_ROWS = 256
MAX_MODULES = 12_000


class BundleAttributionError(ValueError):
    """Browser bundle or third-party notice lacks source-bound evidence."""


def require(value: bool, description: str) -> None:
    if not value:
        raise BundleAttributionError("v511_bundle_licence_" + description)


def sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def stable_json(path: Path, max_size: int) -> dict | list:
    require(path.is_file() and not path.is_symlink() and
            path.stat().st_size <= max_size, "missing_or_unbounded_report")
    def pairs(items):
        record = {}
        for key, value in items:
            require(key not in record, "duplicate_json_key")
            record[key] = value
        return record
    return json.loads(path.read_bytes(), object_pairs_hook=pairs)


def untrusted_path(name: str) -> bool:
    if not isinstance(name, str):
        return True
    p = PurePosixPath(name)
    return ("\\" in name or "%" in name or name.startswith("/") or
            not p.parts or any(x in (".", "..", "") for x in p.parts))


def validate_host(host: str, commit: str, bundles: Path, installed: Path,
                  packages: dict, npm_lock_sha: str) -> dict:
    bpath = bundles / (BUNDLE_PREFIX + host + "-" + commit)
    ipath = installed / (INSTALLED_PREFIX + host + "-" + commit)
    require(bpath.is_dir() and ipath.is_dir() and
            not bpath.is_symlink() and not ipath.is_symlink(),
            "source_artifact_missing:" + host)
    actual = {p.relative_to(bpath).as_posix() for p in bpath.rglob("*")
              if p.is_file()}
    require(actual == {
        "diagnostic-parity.json", "rolldown-source-graph.json",
        "vite-bundled-licenses.json",
    } and not any(p.is_symlink() for p in bpath.rglob("*")),
        "diagnostic_artifact_unlisted_files:" + host)
    parity = stable_json(bpath / "diagnostic-parity.json", MAX_LICENSE_BYTES)
    graph = stable_json(bpath / "rolldown-source-graph.json", MAX_GRAPH_BYTES)
    licences_file = bpath / "vite-bundled-licenses.json"
    licences = stable_json(licences_file, MAX_LICENSE_BYTES)
    source = read_json(ipath / "npm-installed-evidence.json")
    require(isinstance(parity, dict) and isinstance(graph, dict) and
            isinstance(licences, list) and len(licences) <= MAX_LICENSE_ROWS and
            source["schema"] == INSTALLED_SCHEMA and
            source["npm_source_lock_sha256"] == npm_lock_sha and
            graph["schema"] == GRAPH_SCHEMA and
            parity["schema"] == PARITY_SCHEMA and
            graph["original_static_inventory_sha256"] ==
            parity["original_static_inventory_sha256"] ==
            source["static_build_inventory_sha256"] == EXPECTED_STATIC_SHA and
            graph["npm_source_lock_sha256"] ==
            parity["npm_source_lock_sha256"] == npm_lock_sha and
            graph["vite_license_sha256"] ==
            parity["vite_license_sha256"] == sha(licences_file.read_bytes()) and
            parity["vite_license_rows"] == len(licences) and
            parity["compiled_assets_byte_identical"] is True and
            parity["diagnostic_license_generated_outside_served_static_tree"] is True and
            parity["legal_distribution_approved"] is False and
            graph["css_transitive_license_closure_qualified"] is False,
            "source_manifest_or_vite_license_proof_drift:" + host)
    assets = parity["exact_static_files"]
    require(len(assets) == 7 and
            set(assets) == set(source.get("static_assets", assets)),
            "missing_one_of_seven_certified_assets")
    for file, row in assets.items():
        require(not untrusted_path(file) and
                isinstance(row["sha256"], str) and len(row["sha256"]) == 64 and
                isinstance(row["size"], int) and row["size"] > 0,
                "unsafe_or_empty_certified_asset")
    chunks = graph["chunks"]
    require(isinstance(chunks, list) and chunks and
            len(chunks) <= 24, "missing_bounded_rolldown_chunks")
    names = []
    graph_packages = set()
    unknown_modules = set()
    total_modules = 0
    positive_length = 0
    per_package = {}
    for chunk in chunks:
        file = chunk["file"]
        require(file in assets and file.endswith(".js") and
                not untrusted_path(file) and file not in names,
                "unknown_or_duplicate_js_chunk")
        names.append(file)
        modules = chunk["modules"]
        require(isinstance(modules, list), "missing_chunk_module_details")
        total_modules += len(modules)
        for row in modules:
            kind = row["kind"]
            source_package = row["source_package"]
            require(kind in ("npm_source", "virtual_or_generated",
                             "application_source", "unmatched_npm_source",
                             "unclassified_module") and
                    isinstance(row["module"], str), "invalid_module_class")
            length = row["rendered_length"]
            require(length is None or
                    (isinstance(length, int) and length >= 0),
                    "invalid_rendered_module_length")
            if length is not None and length > 0:
                positive_length += 1
            if kind == "npm_source":
                require(source_package in packages and
                        source["npm_entries"][source_package]["installed"],
                        "npm_module_not_present_in_installed_source_lock")
                graph_packages.add(source_package)
                per_package.setdefault(source_package, set()).add(file)
            elif kind in ("unmatched_npm_source", "unclassified_module"):
                unknown_modules.add(row["module"])
            elif source_package is not None:
                require(source_package in packages, "virtual_module_wrong_package")
        require(len(chunk["css_assets"]) <= 16 and all(
            css in assets and css.endswith(".css") and not untrusted_path(css)
            for css in chunk["css_assets"]), "unmapped_css_asset")
    require(total_modules <= MAX_MODULES and positive_length > 0 and
            set(names) == set(parity["chunk_js_files"]),
            "missing_rendered_module_or_js_chunk")
    require(set(graph["detected_npm_source_paths"]) ==
            {row["source_package"] for chunk in chunks
             for row in chunk["modules"] if row["source_package"] is not None},
            "source_package_evidence_mismatch")

    # Vite's build.license is bundler-generated attribution, not an independent
    # legal opinion. Link its entries back to versions in npm's immutable lock.
    by_identity = {}
    for path, package in packages.items():
        if path:
            leaf = path.rsplit("node_modules/", 1)[1]
            identity = (package.get("name", leaf), package["version"])
            by_identity.setdefault(identity, []).append(path)

    statements = []
    observed_licenses = set()
    unmatched_licenses = []
    for row in licences:
        require(type(row) is dict and
                isinstance(row.get("name"), str) and
                isinstance(row.get("version"), str) and
                isinstance(row.get("identifier"), str) and
                isinstance(row.get("text"), str), "vite_license_row_invalid")
        identity = (row["name"], row["version"])
        require(identity not in observed_licenses,
                "duplicate_vite_bundled_license_identity")
        observed_licenses.add(identity)
        source_paths = by_identity.get(identity, [])
        actual_source_paths = sorted(x for x in source_paths if x in graph_packages)
        if not source_paths:
            unmatched_licenses.append(row["name"] + "@" + row["version"])
        exact_installed_source_text = False
        for source_path in source_paths:
            entry = source["npm_entries"].get(source_path)
            if not entry or not entry["installed"]:
                continue
            for file in entry["license_files"]:
                note = ipath.joinpath(*file["path"].split("/"))
                require(note.is_file() and not note.is_symlink(),
                        "installed_source_license_missing")
                original = note.read_bytes()
                require(len(original) == file["size"] and
                        sha(original) == file["sha256"],
                        "installed_source_license_bytes_changed")
                if original == row["text"].encode("utf-8"):
                    exact_installed_source_text = True
        statements.append({
            "name": row["name"],
            "version": row["version"],
            "declared_identifier_by_vite": row["identifier"],
            "license_text_sha256": sha(row["text"].encode("utf-8")),
            "license_text_size_bytes": len(row["text"].encode("utf-8")),
            "locked_package_paths": source_paths,
            "module_graph_package_paths": actual_source_paths,
            "exact_installed_license_text_byte_match": exact_installed_source_text,
        })
    require(set(source["npm_entries"]) == {x for x in packages if x},
            "npm_source_scope_changed:" + host)
    matched_packages = set(p for row in statements
                           for p in row["module_graph_package_paths"])
    unlisted = sorted(graph_packages - matched_packages)
    # Missing package attribution is an explicit admission blocker, not a
    # synthetic self-attestation that all shipped license obligations are met.
    return {
        "host": host,
        "vite_license_entries": len(statements),
        "license_entries": statements,
        "source_package_paths_seen_in_rendered_js_graph": sorted(graph_packages),
        "module_graph_package_chunks": {k: sorted(v) for k, v in sorted(per_package.items())},
        "rendered_source_module_count": total_modules,
        "positive_rendered_length_modules": positive_length,
        "unclassified_module_ids": sorted(unknown_modules),
        "bundle_source_packages_missing_vite_license_entry": unlisted,
        "vite_license_entries_missing_lock_identity": sorted(unmatched_licenses),
        "vite_license_text_not_exact_installed_file": sorted(
            row["name"] + "@" + row["version"]
            for row in statements if not row["exact_installed_license_text_byte_match"]),
        "source_graph_sha256": sha((bpath / "rolldown-source-graph.json").read_bytes()),
        "vite_license_json_sha256": sha(licences_file.read_bytes()),
        "static_bundle_asset_sha256s": {k: v["sha256"] for k,v in sorted(assets.items())},
        "legal_distribution_approved": False,
    }


def review(bundles: Path, installed: Path, commit: str) -> dict:
    require(len(commit) == 40 and all(c in "0123456789abcdef" for c in commit),
            "invalid_commit")
    from . import local_launcher
    packages = json.loads((local_launcher.WEB / "package-lock.json").read_bytes())["packages"]
    npm_lock_sha = sha((local_launcher.WEB / "package-lock.json").read_bytes())
    expected_bundle = {BUNDLE_PREFIX + h + "-" + commit for h in HOSTS}
    expected_installed = {INSTALLED_PREFIX + h + "-" + commit for h in HOSTS}
    require({x.name for x in bundles.iterdir()} == expected_bundle and
            {x.name for x in installed.iterdir()} == expected_installed,
            "missing_or_extra_windows_linux_artifact")
    os_report = {h: validate_host(h, commit, bundles, installed,
                                  packages, npm_lock_sha) for h in HOSTS}
    linux = os_report[HOSTS[0]]
    windows = os_report[HOSTS[1]]
    # A byte-identical browser deliverable should have same identified source
    # package set across OSs. Do not assert individual native build-tool trees
    # are the same, since npm optional binaries are platform-specific.
    require(linux["static_bundle_asset_sha256s"] ==
            windows["static_bundle_asset_sha256s"] and
            linux["source_package_paths_seen_in_rendered_js_graph"] ==
            windows["source_package_paths_seen_in_rendered_js_graph"],
            "bundle_bytes_or_browser_dependency_graph_differ_across_os")
    return {
        "schema": "apmesh.meshstudio.v511.two_host_rolldown_source_notice_audit.v1",
        "tested_code_sha": commit,
        "original_certified_browser_inventory_sha256": EXPECTED_STATIC_SHA,
        "npm_source_lock_sha256": npm_lock_sha,
        "linux_windows_same_browser_source_packages": True,
        "independently_checked_bytes_of_bundler_notice_and_installed_source": True,
        "os_results": os_report,
        "unresolved_attribution_or_notice_review_remains": True,
        "physical_workstation_approval": False,
        "original_cpp_native_recompiled": False,
        "scientific_lod_qualified": False,
        "license_obligations_human_review_required": True,
        "binary_distribution_approved": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-artifacts", type=Path, required=True)
    parser.add_argument("--installed-artifacts", type=Path, required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = review(args.bundle_artifacts, args.installed_artifacts, args.head_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True,
                                      indent=2, ensure_ascii=False,
                                      allow_nan=False) + "\n",
                           encoding="utf-8", newline="\n")
    print("V511_INDEPENDENT_SOURCE_TO_BROWSER_BUNDLE_NOTICE=" + json.dumps({
        "os_bundled_license_counts": {
            host: result["os_results"][host]["vite_license_entries"]
            for host in HOSTS
        },
        "os_npm_module_package_counts": {
            host: len(result["os_results"][host][
                "source_package_paths_seen_in_rendered_js_graph"])
            for host in HOSTS
        },
        "same_browser_assets_and_package_set": True,
        "unresolved": True,
        "distribution_approved": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
