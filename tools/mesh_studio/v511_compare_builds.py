"""Independently compare Windows/Linux compiled research UI and original C++ receipts.

Consume only the two artifacts uploaded by the SAME workflow/commit, reopen
every original emitted asset byte and original-source browser receipt, and
fail closed on content drift. These artifacts are NOT signed releases.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from .local_static_site import verify_inventory

PREFIX = "mesh-studio-v511-built-original-cpp-reviewer-"
MACHINES = ("ubuntu-24.04", "windows-2022")
EXPECTED_CXX_RUN = 45147268663
EXPECTED_SCENE_SHA = "eb72cb058fef2a7632e09f5a3572f39e32f4d9038780cce05337d1afd86f2816"
EXPECTED_P1_SHA = "c4b759169bc68d147c70f8ae5a2127783e33299fe7ed3d35dca51610709d6bfe"


class CrossPlatformMismatch(RuntimeError):
    """An original-source or static-byte review proof did not match."""


def ensure(ok: bool, reason: str) -> None:
    if not ok:
        raise CrossPlatformMismatch("v511_cross_os_" + reason)


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    ensure(path.is_file() and not path.is_symlink() and
           path.stat().st_size < 300_000,
           "report_missing_or_too_large:" + path.name)

    def no_duplicates(pairs):
        seen = {}
        for key, value in pairs:
            ensure(key not in seen, "duplicate_json_key:" + key)
            seen[key] = value
        return seen

    return json.loads(path.read_bytes(), object_pairs_hook=no_duplicates)


def compare(directory: Path, head_sha: str) -> dict:
    ensure(len(head_sha) == 40 and all(c in "0123456789abcdef"
                                      for c in head_sha),
           "invalid_source_commit")
    expected_dirs = {
        os_name: directory / (PREFIX + os_name + "-" + head_sha)
        for os_name in MACHINES
    }
    ensure(directory.is_dir() and not directory.is_symlink() and
           {x.name for x in directory.iterdir()} ==
           {path.name for path in expected_dirs.values()},
           "same_commit_two_os_artifacts_required")
    inventories = {}
    receipts = {}
    for os_name, base in expected_dirs.items():
        root = base / "tools/mesh_studio/web/dist"
        inventory = verify_inventory(root)
        source = read_json(base / "build/v59-source-audit.json")
        browser = read_json(
            base / "tools/mesh_studio/web/test-results/v59-original-reviewer.json")
        local = read_json(base / "build/v511-original-reviewer.json")
        built = read_json(base / "build/v511-static-build.json")
        ensure(
            source.get("original_native_ci_run") == EXPECTED_CXX_RUN and
            source.get("source_cpp_raw_postcommit_reopened") is True and
            source.get("source_exact_files_rehashed", {})
            .get("r2720-native-accepted-scene.json", {})
            .get("sha256") == EXPECTED_SCENE_SHA and
            source.get("scientific_lod_qualified") is False and
            browser.get("original_scene_sha256") == EXPECTED_SCENE_SHA and
            browser.get("native_cpp_source_run") == EXPECTED_CXX_RUN and
            browser.get("p1_source_svg_sha256") == EXPECTED_P1_SHA and
            browser.get("external_requests") == 0 and
            [m.get("original_tri_faces") for m in browser.get("native_models", [])]
            == [1168, 4256] and
            browser.get("scientific_lod_qualified") is False and
            local.get("actual_cpp_original_reviewer_browser") == "PASS" and
            local.get("native_cpp_recompiled") is False and
            local.get("guarded_live_http_negative_probes") == 11 and
            local.get("vite_hmr_running") is False and
            built.get("built_asset_sha256") == inventory["static_assets"] and
            built.get("built_asset_count") == inventory["static_asset_count"],
            "source_browser_or_static_build_receipt_invalid:" + os_name,
        )
        inventories[os_name] = inventory
        receipts[os_name] = {
            "inventory_sha256": digest(
                (root / ".apmesh-local-review-inventory.json").read_bytes()
            ),
            "static_asset_count": inventory["static_asset_count"],
            "original_cpp_source_raw_reopened": True,
            "original_scene_sha256": EXPECTED_SCENE_SHA,
            "p1_svg_sha256": EXPECTED_P1_SHA,
        }
    a, b = (inventories[name] for name in MACHINES)
    ensure(a == b, "compiled_asset_names_lengths_or_hashes_differ")
    for name, record in a["static_assets"].items():
        sources = [expected_dirs[m] / "tools/mesh_studio/web/dist" /
                   Path(*name.split("/")) for m in MACHINES]
        raw = [x.read_bytes() for x in sources]
        ensure(raw[0] == raw[1] and digest(raw[0]) == record["sha256"] and
               len(raw[0]) == record["size"],
               "not_byte_identical:" + name)
    ensure(receipts[MACHINES[0]]["inventory_sha256"] ==
           receipts[MACHINES[1]]["inventory_sha256"],
           "manifest_bytes_differ_after_equal_asset_inventory")
    return {
        "schema": "apmesh.meshstudio.v511.cross_host_static_build_reaudit.v1",
        "classification": "TWO_HOSTS_SAME_COMMIT_BUILT_RESEARCH_UI_NOT_RELEASE",
        "tested_code_sha": head_sha,
        "hosts": receipts,
        "all_built_ui_assets_byte_identical": True,
        "build_asset_count": len(a["static_assets"]),
        "individual_asset_sha256": a["static_assets"],
        "original_cpp_native_source_run": EXPECTED_CXX_RUN,
        "original_cpp_original_scene_sha256": EXPECTED_SCENE_SHA,
        "original_cpp_postcommit_source_reopened_on_both_hosts": True,
        "native_cpp_recompiled_in_this_ui_workflow": False,
        "real_physical_gpu_certified": False,
        "scientific_lod_qualified": False,
        "independent_physical_human_review_completed": False,
        "installer_or_distribution_signed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.directory, args.head_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n")
    print("V511_CROSS_HOST_EXACT_STATIC_ASSET_BYTES=" +
          json.dumps({
              "code_sha": result["tested_code_sha"],
              "asset_count": result["build_asset_count"],
              "identical": result["all_built_ui_assets_byte_identical"],
              "manifest_sha": result["hosts"][MACHINES[0]]["inventory_sha256"],
              "original_cpp_run": result["original_cpp_native_source_run"],
              "lod_qualified": False,
          }, sort_keys=True))


if __name__ == "__main__":
    main()
