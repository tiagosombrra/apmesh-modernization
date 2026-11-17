"""R2.7.17 verify accepted native UV(0,0) against live source curve endpoints.

This is a post-commit read-only C++ observation: native logical IDs, original
curve point-list ends and accepted TRI face corners. No pointer-welding proof.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path

from .audit_retained_native_lineage import audit_retained_directory
from .native_seam_samples import UV_TOL, close_xyz
from .verify_native_lineage import (
    SOURCE_MODELS, decode_ndjson, finite_number, integer, require, sha256_file,
    validate_lineage_records,
)

SCHEMA = "apmesh.meshstudio.r2717.accepted_native_uv00_corner_source_observer.v1"
HEADER_CONTRACT = "native_postcommit_source_curve_endpoints_v1"


def source_corner_endpoint(curve: dict) -> dict:
    """Resolve the local t=0 endpoint from original ordered curve samples."""
    endpoints = curve.get("r2717_original_curve_endpoints")
    require(type(endpoints) is list and len(endpoints) == 2 and
            type(curve.get("reversed")) is bool,
            "r2717_missing_native_source_endpoint_observation")
    for index, point in enumerate(endpoints):
        require(type(point) is dict and integer(point.get("stored_index")) and
                (point["stored_index"] == 0 if index == 0 else point["stored_index"] >= 1)
                and finite_number(point.get("stored_parameter")) and
                -UV_TOL <= point["stored_parameter"] <= 1.0 + UV_TOL and
                integer(point.get("original_sample_id")) and
                type(point.get("xyz")) is list and len(point["xyz"]) == 3 and
                all(finite_number(x) for x in point["xyz"]),
                "r2717_invalid_original_curve_endpoint_record")
    require(endpoints[0]["stored_parameter"] <=
            endpoints[1]["stored_parameter"] + UV_TOL,
            "r2717_original_sample_parameter_order_not_monotonic")
    return endpoints[1 if curve["reversed"] else 0]


def accepted_uv00_corner(faces: list[dict], patch_slot: int) -> dict:
    """Extract actual committed triangle corner, never an OBJ ordinal."""
    seen = {}
    for face in faces:
        require(face.get("patch_slot") == patch_slot,
                "r2717_native_face_patch_mismatch")
        for vertex in face["vertices"]:
            if all(abs(v) <= UV_TOL for v in vertex["uv"]):
                node_id = vertex["native_node_id"]
                previous = seen.setdefault(node_id, vertex)
                require(close_xyz(previous["xyz"], vertex["xyz"]),
                        "r2717_native_corner_id_xyz_disagreement")
    require(len(seen) == 1, "r2717_missing_or_ambiguous_accepted_uv00_corner")
    return next(iter(seen.values()))


def analyze_real_corner_source(records: list[dict]) -> dict:
    """Retain original endpoint IDs and compare independently to live TRI."""
    require(records[0].get("r2717_corner_observer") == HEADER_CONTRACT,
            "r2717_missing_original_cpp_postcommit_instrumentation")
    patches = [record for record in records if record.get("type") == "patch"]
    faces_by_patch: dict[int, list[dict]] = {}
    for face in records:
        if face.get("type") == "face":
            faces_by_patch.setdefault(face["patch_slot"], []).append(face)
    unique_original_curve_endpoints: dict[int, list[dict]] = {}
    results = []
    for patch in patches:
        slot = patch["patch_slot"]
        require(len(patch["source_curves"]) == 4 and
                slot in faces_by_patch, "r2717_missing_original_source_patch_faces")
        sides = patch["source_curves"]
        for side in sides:
            endpoints = side.get("r2717_original_curve_endpoints")
            require(type(endpoints) is list and len(endpoints) == 2,
                    "r2717_source_curve_endpoints_missing")
            # One canonical source curve slot must expose the same live
            # first/last source sample identity for each incident patch.
            curve_slot = side["source_curve_slot"]
            if curve_slot in unique_original_curve_endpoints:
                require(endpoints == unique_original_curve_endpoints[curve_slot],
                        "r2717_shared_original_curve_source_samples_disagree")
            else:
                unique_original_curve_endpoints[curve_slot] = endpoints
        uv00 = accepted_uv00_corner(faces_by_patch[slot], slot)
        edge0 = source_corner_endpoint(sides[0])
        edge3 = source_corner_endpoint(sides[3])
        row = {
            "patch_slot": slot,
            "accepted_native_uv00_node_id": uv00["native_node_id"],
            "accepted_native_uv00_xyz": uv00["xyz"],
            "edge0_source_curve_slot": sides[0]["source_curve_slot"],
            "edge3_source_curve_slot": sides[3]["source_curve_slot"],
            "edge0_original_local_t0_sample_id": edge0["original_sample_id"],
            "edge3_original_local_t0_sample_id": edge3["original_sample_id"],
            "accepted_corner_id_equals_edge0_source_sample": (
                uv00["native_node_id"] == edge0["original_sample_id"]),
            "accepted_corner_id_equals_edge3_source_sample": (
                uv00["native_node_id"] == edge3["original_sample_id"]),
            "accepted_corner_xyz_equals_edge0_sample_with_tolerance": close_xyz(
                uv00["xyz"], edge0["xyz"]),
            "accepted_corner_xyz_equals_edge3_sample_with_tolerance": close_xyz(
                uv00["xyz"], edge3["xyz"]),
            "edge0_and_edge3_source_endpoint_ids_equal": (
                edge0["original_sample_id"] == edge3["original_sample_id"]),
            "cpp_node_pointer_identity_proven": False,
            "historical_boundary_closure_execution_proven": False,
        }
        results.append(row)
    require(len(results) == records[0]["source_patch_count"],
            "r2717_original_patches_incomplete")
    require(len(unique_original_curve_endpoints) ==
            records[0]["source_curve_count"], "r2717_original_curves_incomplete")
    result = {
        "original_source_patch_count": len(results),
        "original_source_curve_count": len(unique_original_curve_endpoints),
        "native_postcommit_corner_observer_present": True,
        "corner_observations": results,
        "accepted_id_matches_source_edge0": sum(
            x["accepted_corner_id_equals_edge0_source_sample"] for x in results),
        "accepted_id_matches_source_edge3": sum(
            x["accepted_corner_id_equals_edge3_source_sample"] for x in results),
        "accepted_xyz_matches_source_edge0": sum(
            x["accepted_corner_xyz_equals_edge0_sample_with_tolerance"] for x in results),
        "accepted_xyz_matches_source_edge3": sum(
            x["accepted_corner_xyz_equals_edge3_sample_with_tolerance"] for x in results),
        "original_endpoints_equal_id": sum(
            x["edge0_and_edge3_source_endpoint_ids_equal"] for x in results),
        "actual_native_shared_cpp_node_pointers_certified": False,
        "scientific_lod_qualified": False,
    }
    return result


def audit_native_corner_observer(directory: Path) -> dict:
    """Revalidate original native post-commit face and C++ source evidence."""
    retained = audit_retained_directory(directory)
    results = {}
    for model in SOURCE_MODELS:
        report = json.loads(
            (directory / f"r2712-{model}-native-lineage-audit.json")
            .read_text(encoding="utf-8"))
        epochs = []
        for snapshot in report["accepted_snapshots"]:
            path = directory / snapshot["raw_native_ndjson_artifact_name"]
            raw = path.read_bytes()
            require(sha256_file(path) == snapshot["source_file_sha256"],
                    "r2717_original_native_ndjson_sha_changed")
            records = decode_ndjson(raw)
            qualified = validate_lineage_records(records, model)
            require(qualified["accepted_step"] == snapshot["accepted_step"],
                    "r2717_original_native_step_changed")
            epochs.append({
                "original_accepted_step": qualified["accepted_step"],
                "original_native_ndjson_sha256": snapshot["source_file_sha256"],
                "original_live_corner_evidence": analyze_real_corner_source(records),
            })
        require([e["original_accepted_step"] for e in epochs] ==
                retained["original_native_models"][model]["accepted_native_steps"],
                "r2717_native_epoch_provenance_mismatch")
        results[model] = epochs
    return {
        "schema": SCHEMA,
        "scope": "POSTCOMMIT_ORIGINAL_CPLUSPLUS_SOURCE_AND_ACCEPTED_TRI_READ_ONLY",
        "original_models": results,
        "native_cpp_pointer_ownership_verified": False,
        "cross_epoch_descendants_verified": False,
        "continuous_geometric_bound_verified": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = audit_native_corner_observer(args.directory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(result, file, indent=2, sort_keys=True, allow_nan=False)
        file.write("\n")
    brief = {
        model: [{
            "step": item["original_accepted_step"],
            "patches": item["original_live_corner_evidence"]["original_source_patch_count"],
            "edge0_id_matches": item["original_live_corner_evidence"][
                "accepted_id_matches_source_edge0"],
            "edge3_id_matches": item["original_live_corner_evidence"][
                "accepted_id_matches_source_edge3"],
            "edge0_xyz_matches": item["original_live_corner_evidence"][
                "accepted_xyz_matches_source_edge0"],
            "edge3_xyz_matches": item["original_live_corner_evidence"][
                "accepted_xyz_matches_source_edge3"],
        } for item in epochs]
        for model, epochs in result["original_models"].items()
    }
    print("R2717_ORIGINAL_NATIVE_CORNER_SOURCE=" +
          json.dumps(brief, sort_keys=True))


if __name__ == "__main__":
    main()
