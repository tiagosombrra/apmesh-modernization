"""Prepare a source-exact, explicitly NOT FOR DISTRIBUTION notice candidate.

The selected candidate is ONLY the V5.11 seven-file browser research UI plus
the 13-package minimal local Python API dependency closure. Original C++ source,
scientific/PDF/VTK Python profiles and unbuilt installers are out of scope.
No license grant, attribution requirement or dual-license choice is inferred.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import tempfile

from .v511_bundle_license_reaudit import (
    HOSTS, EXPECTED_STATIC_SHA, review as source_to_bundle_review,
)
from .v511_license_evidence_reaudit import review as installed_source_review

SOURCE_CI_RUN = 45209742219
SOURCE_CI_COMMIT = "fb665764143da62b9a44516654ed1057858c2639"
SCHEMA = "apmesh.meshstudio.v511.local_reviewer_notice_candidate.v1"
BROWSER_NPM = (
    "@kitware/vtk.js", "d3-array", "d3-color", "d3-format",
    "d3-interpolate", "d3-scale", "fast-deep-equal", "gl-matrix",
    "react", "react-dom", "scheduler", "seedrandom", "spark-md5",
)
BROWSER_COUNT = len(BROWSER_NPM)
PYTHON_COUNT = 13
MAX_READ = 100_000
MAX_FILE_COUNT = 128
SEEDRANDOM_NOTICE_PATH = "README.md"
SEEDRANDOM_SECTION = re.compile(
    r"(?mi)^(?:#{1,3}[ \t]+)?LICENSE[ \t]*\(MIT\)[ \t]*\r?\n"
)
DRAFT_PREFIX = "THIRD_PARTY_NOTICES_CANDIDATE_"


class NoticeCandidateError(ValueError):
    """Proposed attribution text is incomplete, altered or outside its scope."""


def require(ok: bool, code: str) -> None:
    if not ok:
        raise NoticeCandidateError("v511_notice_candidate_" + code)


def sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def read_manifest(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink() and
            path.stat().st_size < 400_000, "missing_bounded_manifest")
    return json.loads(path.read_bytes())


def package_slug(name: str, version: str) -> str:
    require(bool(re.fullmatch(r"[@a-zA-Z0-9._/-]{1,100}", name)) and
            bool(re.fullmatch(r"[A-Za-z0-9._-]{1,40}", version)),
            "unsafe_package_identity")
    return re.sub(r"[^a-zA-Z0-9._-]", "_", name) + "-" + version


def source_bytes(root: Path, item: dict) -> bytes:
    name = item["path"]
    require(isinstance(name, str) and name.startswith("notices/") and
            "\\" not in name and "%" not in name and
            all(part not in (".", "..", "") for part in PurePosixPath(name).parts),
            "source_path_traversal")
    p = root.joinpath(*name.split("/"))
    require(p.is_file() and not p.is_symlink() and
            all(not x.is_symlink() for x in p.parents if x != root.parent),
            "missing_or_symlinked_source_notice")
    require(0 < p.stat().st_size < MAX_READ, "source_notice_oversize")
    raw = p.read_bytes()
    require(len(raw) == item["size"] and sha(raw) == item["sha256"],
            "source_notice_byte_drift")
    return raw


def seedrandom_license_from_readme(raw: bytes, evidence: dict) -> bytes:
    """Extract only the original installed README's verbatim MIT grant."""
    body = raw.decode("utf-8")
    m = SEEDRANDOM_SECTION.search(body)
    require(m is not None, "seedrandom_mit_header_absent")
    grant = body[m.end():].lstrip()
    if grant.startswith("-------------"):
        grant = grant.partition("\n")[2].lstrip()
    result = grant.encode("utf-8")
    require(len(result) == evidence["embedded_license_section_size"] and
            sha(result) == evidence["embedded_license_section_sha256"] and
            b"Copyright 2019 David Bau." in result and
            b"Permission is hereby granted" in result,
            "seedrandom_original_embedded_grant_drift")
    return result


def prepare(inputs: Path, output: Path) -> dict:
    """Validate both actual host source archives before selecting any notice."""
    bundles = inputs / "bundles"
    installed = inputs / "installed"
    source_to_bundle_review(bundles, installed, SOURCE_CI_COMMIT)
    installed_source_review(installed, SOURCE_CI_COMMIT)

    output.mkdir(parents=True, exist_ok=True)
    source_names = {}
    source_sha = {}
    used_outputs = set()
    per_host = {}
    combined_rows = {}
    for host in HOSTS:
        prefix = "mesh-studio-v511-"
        bundle_dir = bundles / (
            prefix + "bundle-" + host + "-" + SOURCE_CI_COMMIT)
        installed_dir = installed / (
            prefix + "installed-license-" + host + "-" + SOURCE_CI_COMMIT)
        vite_rows = read_manifest(bundle_dir / "vite-bundled-licenses.json")
        npm = read_manifest(installed_dir / "npm-installed-evidence.json")
        py = read_manifest(installed_dir / "python-installed-evidence.json")
        assert isinstance(vite_rows, list)
        require(len(vite_rows) == BROWSER_COUNT and
                len(py["packages"]) == PYTHON_COUNT and
                {row["name"] for row in vite_rows} == set(BROWSER_NPM),
                "browser_or_server_package_scope_drift")
        notice_parts = [
            "THIRD-PARTY NOTICES — RESEARCH REVIEW CANDIDATE ONLY\n",
            "NOT APPROVED FOR DISTRIBUTION OR PUBLIC RELEASE\n",
            f"Target OS: {host}\n",
            "Target scope: seven source-certified static web assets plus ",
            "13-package minimal Python local API dependency closure.\n",
            "The original C++ native generator, heavy scientific/PDF environment, ",
            "installers and binaries are NOT included or licensed by this file.\n",
            "This draft preserves installed license materials. It is not a ",
            "legal compatibility review and does not select optional license paths.\n",
            "Original license source bytes are preserved in source-notices/.\n\n",
        ]
        rows = []
        vite_by_name = {x["name"]: x for x in vite_rows}
        names_and_data = [
            ("npm", name, npm["npm_entries"]["node_modules/" + name],
             vite_by_name[name]) for name in BROWSER_NPM
        ] + [
            ("python", name, py["packages"][name], None)
            for name in sorted(py["packages"])
        ]
        require(len(names_and_data) == BROWSER_COUNT + PYTHON_COUNT,
                "wrong_notice_package_count")
        for ecosystem, name, package, vite in names_and_data:
            version = package["version"]
            slug = package_slug(name, version)
            if ecosystem == "npm":
                require(package["installed"] is True and
                        package["lock_development_only"] is False and
                        package["lock_optional"] is False and
                        vite["version"] == version,
                        "browser_source_package_version_or_kind_invalid")
                declared = vite["identifier"]
                require(declared == package["lock_license_declaration"],
                        "vite_vs_lock_declared_license_drift")
            else:
                declared = package.get("license_expression") or (
                    package.get("legacy_license") or "UNKNOWN")
            expected_files = package["license_files"]
            require(bool(expected_files) and len(expected_files) <= 5,
                    "missing_bounded_package_notice")
            notice_parts.extend([
                "================================================================\n",
                f"[{ecosystem}] {name}@{version}\n",
                f"Declared license metadata: {declared}\n",
            ])
            if name == "spark-md5" and ecosystem == "npm":
                require(declared == "(WTFPL OR MIT)",
                        "spark_md5_source_choice_changed")
                notice_parts.append(
                    "UNRESOLVED: source LICENSE contains WTFPL; metadata gives ",
                )
                notice_parts.append(
                    "(WTFPL OR MIT). No MIT branch selected or approved.\n")
            if name == "seedrandom" and ecosystem == "npm":
                require(vite["text"] is None and declared == "MIT",
                        "seedrandom_missing_vite_notice_evidence_changed")
                notice_parts.append(
                    "Vite's license metadata omits this package's text. ",
                )
                notice_parts.append(
                    "The license below is extracted from the verified ",
                )
                notice_parts.append("installed README.md, not inferred.\n")
            file_rows = []
            for index, item in enumerate(expected_files):
                raw = source_bytes(installed_dir, item)
                source_label = item["source"]
                require(bool(source_label) and len(source_label) < 150,
                        "invalid_source_label")
                # The source name is in the original authenticated evidence,
                # never used as a filesystem traversal path in our output.
                dest = (f"source-notices/{host}/{ecosystem}/{slug}/"
                        f"{index:02d}-{sha(source_label.encode())[:10]}.txt")
                require(dest not in used_outputs, "duplicate_source_output")
                used_outputs.add(dest)
                disk_path = output.joinpath(*dest.split("/"))
                disk_path.parent.mkdir(parents=True, exist_ok=True)
                disk_path.write_bytes(raw)
                file_rows.append({
                    "upstream_source_path": item["path"],
                    "upstream_source_filename": source_label,
                    "original_bytes_sha256": sha(raw),
                    "original_bytes_size": len(raw),
                    "candidate_source_path": dest,
                    "embedded_original_mit_grant": name == "seedrandom",
                })
                if name == "seedrandom":
                    require(item.get("source_kind") ==
                            "verbatim_readme_with_embedded_mit_license" and
                            source_label == SEEDRANDOM_NOTICE_PATH,
                            "seedrandom_original_license_not_readme")
                    notice_text = seedrandom_license_from_readme(raw, item)
                else:
                    notice_text = raw
                # Composite text is a review index; only the separate files
                # are claimed to be bit-identical to the original notices.
                notice_parts.extend([
                    f"Source file: {source_label}\n",
                    f"Original source SHA-256: {sha(raw)}\n",
                    f"Verbatim source text (or README MIT subsection):\n",
                    notice_text.decode("utf-8").replace("\r\n", "\n"),
                    "\n\n",
                ])
            rows.append({
                "ecosystem": ecosystem, "package": name, "version": version,
                "declared_license_metadata": declared,
                "installed_original_license_material": file_rows,
                "licence_choice_resolved_by_automation": False,
                "source_notice_obligations_legally_cleared": False,
            })
        filename = DRAFT_PREFIX + host.upper().replace("-", "_") + ".txt"
        notice_bytes = "".join(notice_parts).encode("utf-8")
        candidate = output / filename
        candidate.write_bytes(notice_bytes)
        source_names[host] = filename
        source_sha[host] = sha(notice_bytes)
        per_host[host] = rows
        combined_rows[host] = {f"{r['ecosystem']}:{r['package']}":
                               [x["original_bytes_sha256"] for x in
                                r["installed_original_license_material"]]
                               for r in rows}

    differences = []
    linux, windows = (combined_rows[h] for h in HOSTS)
    require(set(linux) == set(windows), "host_dependency_difference")
    for name in sorted(linux):
        if linux[name] != windows[name]:
            differences.append(name)
    require("python:pydantic-core" in differences,
            "original_platform_specific_pydantic_core_notice_not_retained")
    ledger = {
        "schema": SCHEMA,
        "classification": "DRAFT_RESEARCH_EVIDENCE_NOT_DISTRIBUTION_APPROVAL",
        "source_github_actions_run": SOURCE_CI_RUN,
        "source_github_actions_code_sha": SOURCE_CI_COMMIT,
        "original_static_browser_inventory_sha256": EXPECTED_STATIC_SHA,
        "compiled_browser_assets_count": 7,
        "rendered_browser_npm_package_count": BROWSER_COUNT,
        "minimal_python_dependency_count": PYTHON_COUNT,
        "proposed_profile": "LOCAL_LOOPBACK_REVIEW_ONLY_WITHOUT_FULL_SCIENTIFIC_ENV",
        "notices_by_host": source_names,
        "notice_document_sha256_by_host": source_sha,
        "rows_by_host": per_host,
        "source_notice_sha_differences_between_hosts": differences,
        "seedrandom_notice_source": "exact installed README.md MIT section",
        "spark_md5_dual_licence_choice": "UNRESOLVED",
        "full_scientific_python_environment_reviewed": False,
        "pymupdf_agpl_commercial_obligations_reviewed": False,
        "other_software_sources_not_reviewed": True,
        "shipped_notice_integration_implemented": False,
        "licence_compatibility_reviewed_by_human": False,
        "legal_distribution_approved": False,
        "original_cpp_recompiled": False,
        "scientific_lod_qualified": False,
    }
    manifest = output / "NOTICE_EVIDENCE_LEDGER.json"
    manifest.write_text(json.dumps(ledger, indent=2, sort_keys=True,
                                   ensure_ascii=False, allow_nan=False) + "\n",
                        encoding="utf-8", newline="\n")
    require(sum(1 for f in output.rglob("*") if f.is_file()) <= MAX_FILE_COUNT,
            "unbounded_output_file_count")
    print("V511_THIRD_PARTY_NOTICES_DRAFT=" + json.dumps({
        "packages_per_os": BROWSER_COUNT + PYTHON_COUNT,
        "browser_packages": BROWSER_COUNT,
        "minimal_python_packages": PYTHON_COUNT,
        "os_source_notice_byte_differences": differences,
        "distributable": False,
        "legal_distribution_approved": False,
    }, sort_keys=True))
    return ledger


def audit(inputs: Path, output: Path) -> dict:
    """Recompute every candidate byte from certified source and reject extras."""
    require(output.is_dir() and not output.is_symlink(),
            "missing_candidate_archive")
    with tempfile.TemporaryDirectory(prefix="apmesh-v511-notice-") as temp:
        expected_dir = Path(temp)
        original = prepare(inputs, expected_dir)
        actual = read_manifest(output / "NOTICE_EVIDENCE_LEDGER.json")
        require(actual == original, "notice_ledger_not_reproducible")
        expected_files = {p.relative_to(expected_dir).as_posix():
                          sha(p.read_bytes()) for p in expected_dir.rglob("*")
                          if p.is_file()}
        actual_files = {p.relative_to(output).as_posix():
                        sha(p.read_bytes()) for p in output.rglob("*")
                        if p.is_file()}
        require(not any(p.is_symlink() for p in output.rglob("*")),
                "symlink_in_candidate_archive")
        require(actual_files == expected_files,
                "candidate_notice_text_or_source_file_mismatch")
    return {
        "source_github_actions_run": SOURCE_CI_RUN,
        "source_github_actions_commit": SOURCE_CI_COMMIT,
        "all_candidate_notice_bytes_reproduced_from_original_source": True,
        "all_original_host_specific_notice_bytes_preserved": True,
        "spark_md5_choice_still_unresolved": True,
        "notices_shipped_with_an_installer": False,
        "license_compatibility_or_distribution_approved": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("prepare", "audit"), required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = (prepare(args.input, args.output) if args.mode == "prepare"
              else audit(args.input, args.output))
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(
            json.dumps(result, indent=2, sort_keys=True,
                       ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
