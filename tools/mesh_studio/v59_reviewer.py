"""Verify the certified original C++ source archive and run a full local reviewer flow.

The corpus is from historical original-native GitHub CI, not a newly compiled
C++ scientific epoch. Never trust a self-declared manifest without exact pinned
bytes and independently reopening retained original postcommit NDJSON.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

from .dependency_lock_audit import ROOT
from . import local_launcher

SCHEMA = "apmesh.meshstudio.v59.local_original_native_reviewer.v1"
ORIGINAL_CI_RUN = 45147268663
ORIGINAL_CI_HEAD_SHA = "7d41ab8ec55b34bf879f9efc2a547168e50143de"
ARTIFACT_EXPIRY_UTC = "2026-12-07T09:30:00Z"
CORPUS = ROOT / "build/v59-native-reviewer"
SOURCE_FILES = {
    "r2720-native-accepted-scene.json": (
        1716994, "eb72cb058fef2a7632e09f5a3572f39e32f4d9038780cce05337d1afd86f2816"),
    "v52-native-accepted-uv-publication/manifest.json": (
        3778, "85e2df4d178bb277c15989d6893903be0e69e1fe37b162ca1dc675e0afe59aee"),
    "v52-native-accepted-uv-publication/eistute-accepted-step1-uv.svg": (
        536961, "c3757577ddc6cc147a029303be4bbe60fa0a87e4063829257ef7f7d91764bd66"),
    "v52-native-accepted-uv-publication/book-accepted-step1-uv.svg": (
        1980092, "8d639313d8ade37fd4a8b0347fe5787d5d2db15296f0d3e6c6844e6abb39b248"),
    "r2712-book-book_accepted_step_1_outer_1.ndjson": (
        2155188, "e5be7af26f0064a01929e33f7db9129a50a17959d20d743f09c224551358524a"),
    "r2712-eistute-eistute_accepted_step_1_outer_1.ndjson": (
        599332, "57eaa949e382aee4537325e7214694fc250d1cf20eeec96beeb6f923f6b518e6"),
    "r2712-book-native-lineage-audit.json": (
        2205, "887143ca82c5b605d826eaeecf28a8b95f5a3b03e05b2bb921df8912abf5646a"),
    "r2712-eistute-native-lineage-audit.json": (
        2219, "a42927bf4d3fe682cb75e43a224fc75e9af27859e2aaa978b8ed457bc9ec07c0"),
    "r2718-book-original-native-generator-stderr.log": (
        205931, "3ebd1f2522d02ef51f20cd9f1d5a9bf4da98ab4b661d816881d076be14d5fcef"),
    "r2718-eistute-original-native-generator-stderr.log": (
        120270, "0d55891c3dd75145c64f4dac6cbad3a233e84b0a51761b0e26ace1463aeb9ad3"),
}


class ReviewerSourceError(ValueError):
    """Pinned reviewer source or scientific admission proof is not available."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ReviewerSourceError("v59_" + code)


def _sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def _verify_exact_source_bytes(directory: Path) -> dict:
    """Require exactly ten files in one original native CI source corpus."""
    require(directory.is_dir() and not directory.is_symlink(),
            "original_cpp_corpus_missing")
    actual = set()
    for entry in directory.rglob("*"):
        require(not entry.is_symlink(), "symlink_in_original_source_bundle")
        if entry.is_file():
            actual.add(entry.relative_to(directory).as_posix())
    require(actual == set(SOURCE_FILES),
            "missing_or_unexpected_original_cpp_source_file")
    verified = {}
    for name, (expected_size, expected_sha) in SOURCE_FILES.items():
        file = directory / name
        data = file.read_bytes()
        require(len(data) == expected_size and _sha(data) == expected_sha,
                "original_cpp_file_sha_or_size_drift:" + name)
        verified[name] = {"size": len(data), "sha256": expected_sha}
    return verified


def preflight(directory: Path = CORPUS, *, audit_cpp_raw: bool = True) -> dict:
    """Re-audit the actual retained C++ source, not an uploaded visual claim."""
    source = _verify_exact_source_bytes(directory)
    root = directory / "v52-native-accepted-uv-publication"
    scene_file = directory / "r2720-native-accepted-scene.json"
    scene = json.loads(scene_file.read_bytes())
    manifest = json.loads((root / "manifest.json").read_bytes())
    require(scene.get("schema") ==
            "apmesh.meshstudio.r2720.original_accepted_tri_scene.v1" and
            scene.get("scientific_lod_qualified") is False and
            scene.get("no_implicit_node_welding") is True and
            [(m.get("model"), m.get("accepted_native_step"), m.get("native_tri_faces"))
             for m in scene["scenes"]] ==
            [("eistute", 1, 1168), ("book", 1, 4256)] and
            manifest.get("source_scene_bundle_sha256") ==
            SOURCE_FILES["r2720-native-accepted-scene.json"][1] and
            manifest.get("source_cpp_raw_ndjson_reaudited") is True and
            manifest.get("scientific_lod_qualified") is False and
            manifest.get("original_physical_node_welding_certified") is False,
            "original_cpp_accepted_or_manifest_identity_invalid")

    if audit_cpp_raw:
        from .native_accepted_vector_publication import audit_accepted_native_publication
        audited = audit_accepted_native_publication(directory, scene_file, root)
        require(audited.get("original_source_cpp_ndjson_reopened") is True and
                audited.get("all_original_source_face_keys_independently_matched") is True and
                audited.get("scientific_lod_qualified") is False and
                audited.get("original_tri_faces") == {"eistute": 1168, "book": 4256},
                "original_postcommit_raw_cpp_audit_failed")
        reopened = True
    else:
        reopened = False
    return {
        "schema": SCHEMA,
        "source_classification": "HISTORICAL_ACTUAL_COMPILED_ACCEPTED_TRI_SOURCE_REOPENED",
        "original_native_ci_run": ORIGINAL_CI_RUN,
        "original_native_ci_head_sha": ORIGINAL_CI_HEAD_SHA,
        "artifact_expiry_utc": ARTIFACT_EXPIRY_UTC,
        "source_exact_files_rehashed": source,
        "accepted_cpp_global_steps": {"eistute": [1], "book": [1]},
        "source_cpp_raw_postcommit_reopened": reopened,
        "source_attestation_requires_exact_historical_github_ci": True,
        "user_uploaded_json_alone_not_source_proof": True,
        "native_cpp_recompiled_in_this_review": False,
        "physical_node_welding_certified": False,
        "scientific_lod_qualified": False,
        "physical_gpu_qualified": False,
    }


def _browser_review(directory: Path) -> None:
    """Run one real Playwright journey against the V5.8 *already live* servers."""
    node = local_launcher._check_node()
    script = local_launcher.WEB / "node_modules/@playwright/test/cli.js"
    require(script.is_file(), "locked_playwright_runner_missing")
    env = os.environ.copy()
    env["APMESH_V59_EXTERNAL_SERVERS"] = "1"
    env["APMESH_V59_REQUIRED"] = "1"
    env["APMESH_V59_CORPUS_DIR"] = str(directory)
    # Avoid running unrelated original-science browser tests on historical inputs.
    subprocess.run([node["node_executable"], str(script), "test",
                    "tests/viewport-v59-original-reviewer.spec.ts",
                    "--workers=1", "--reporter=line"],
                   check=True, cwd=local_launcher.WEB, env=env, timeout=360)


def smoke(directory: Path = CORPUS) -> dict:
    original = preflight(directory)
    # Browser binaries must be installed separately by the caller/CI.
    result = local_launcher.launch("smoke", on_ready=lambda: _browser_review(directory))
    require(result.get("external_reviewer_gate") == "PASS" and
            result.get("local_health") == "PASS" and
            result.get("vite_proxy") == "PASS",
            "full_reviewer_browser_gate_not_executed")
    return {
        **original,
        "actual_loopback_linux_or_windows_browser_review": "PASS",
        "local_runtime_python_dependencies": result["minimal_python_packages"],
        "local_runtime_python_count": result["minimal_python_count"],
        "local_catalog_count": result["source_catalog_count"],
        "local_p1_svg_sha256": result["source_svg_sha256"],
        "servers_stopped_after_review": True,
        "experimental_original_native_browser_only": True,
        "original_tri_and_quad_generator_not_reexecuted": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preflight", "smoke"))
    parser.add_argument("--corpus", type=Path, default=CORPUS)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = preflight(args.corpus) if args.mode == "preflight" else smoke(args.corpus)
    raw = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(raw, encoding="utf-8", newline="\n")
    print("V59_ORIGINAL_CPP_REVIEWER=" +
          json.dumps({k: v for k, v in result.items()
                      if k != "source_exact_files_rehashed"}, sort_keys=True))


if __name__ == "__main__":
    main()
