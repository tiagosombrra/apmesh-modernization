"""R2.7.18 evidence-bound actual Adapter closure and C++ owner audit.

The executed Adapter close witness belongs to provisional local attempts.
The direct accepted SubMesh pointer witness belongs to the real committed mesh.
They are compared by native logical ID without conflating lifetimes or epochs.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from .audit_retained_native_lineage import audit_retained_directory
from .native_corner_origin import accepted_uv00_corner, analyze_real_corner_source
from .verify_native_lineage import (
    SOURCE_MODELS, decode_ndjson, finite_number, integer, require, sha256_file,
    unique_fields, validate_lineage_records,
)

SCHEMA = "apmesh.meshstudio.r2718.original_native_adapter_close_and_cpp_node_owner.v1"
CLOSE_PREFIX = "R2718_ADAPTER_BOUNDARY_CLOSE="
OWNER_HEADER = "native_postcommit_submesh_cpp_node_owner_v1"


def read_actual_adapter_events(original_stderr: bytes, model: str) -> list[dict]:
    """Parse only actual native process stderr, not fabricated accepted records."""
    require(model in SOURCE_MODELS and len(original_stderr) <= 12_000_000,
            "r2718_original_adapter_stderr_invalid")
    require(b"\x00" not in original_stderr and b"\r" not in original_stderr,
            "r2718_adapter_stderr_contains_nul")
    lines = original_stderr.decode("utf-8").splitlines()
    events = []
    for line in lines:
        if not line.startswith(CLOSE_PREFIX):
            continue
        event = json.loads(line[len(CLOSE_PREFIX):], object_pairs_hook=unique_fields)
        require(type(event) is dict, "r2718_actual_adapter_event_not_object")
        patches = SOURCE_MODELS[model][0]
        require(integer(event.get("adaptive_step")) and
                event["adaptive_step"] > 0 and
                integer(event.get("retry_index")) and
                integer(event.get("local_attempt")) and
                integer(event.get("patch_index")) and
                event["patch_index"] < patches and
                integer(event.get("boundary_vertex_count")) and
                event["boundary_vertex_count"] >= 4 and
                all(integer(event.get(key)) for key in (
                    "first_mapped_native_node_id",
                    "edge0_original_source_local_t0_id",
                    "edge3_original_source_local_t0_id")) and
                all(type(event.get(key)) is bool for key in (
                    "actual_boundary_close_returned",
                    "first_vertex_maps_to_edge0_source_id",
                    "first_vertex_maps_to_edge3_source_id",
                    "first_vertex_was_reused_by_boundary_close",
                    "is_globally_accepted_commit")),
                "r2718_invalid_original_adapter_closure_fields")
        for field in ("first_uv", "last_uv"):
            pair = event.get(field)
            require(type(pair) is list and len(pair) == 2 and
                    all(finite_number(v) and -1e-9 <= v <= 1.0 + 1e-9 for v in pair),
                    "r2718_invalid_adapter_original_local_uv")
        require(abs(event["first_uv"][0]) <= 1e-9 and
                abs(event["first_uv"][1]) <= 1e-9 and
                event["actual_boundary_close_returned"] is True and
                event["first_vertex_was_reused_by_boundary_close"] is True and
                event["is_globally_accepted_commit"] is False and
                event["first_vertex_maps_to_edge0_source_id"] ==
                (event["first_mapped_native_node_id"] ==
                 event["edge0_original_source_local_t0_id"]) and
                event["first_vertex_maps_to_edge3_source_id"] ==
                (event["first_mapped_native_node_id"] ==
                 event["edge3_original_source_local_t0_id"]),
                "r2718_adapter_close_scope_or_native_id_relation_forged")
        events.append(event)
    require(bool(events), "r2718_no_real_original_adapter_boundary_closure")
    return events


def analyze_accepted_cpp_owners(records: list[dict]) -> dict:
    """Classify live postcommit C++ object comparisons, never raw addresses."""
    require(records[0].get("r2718_owner_observer") == OWNER_HEADER,
            "r2718_missing_cpp_pointer_observation")
    corners = analyze_real_corner_source(records)
    corner_by_patch = {r["patch_slot"]: r for r in corners["corner_observations"]}
    rows = []
    for patch in (r for r in records if r.get("type") == "patch"):
        slot = patch["patch_slot"]
        original = corner_by_patch[slot]
        observed = patch.get("r2718_accepted_cpp_node_owner")
        require(type(observed) is dict and
                integer(observed.get("native_node_id")) and
                observed["native_node_id"] == original["accepted_native_uv00_node_id"] and
                integer(observed.get("submesh_node_slot")) and
                observed["submesh_node_slot"] < patch["node_count"] and
                type(observed.get("triangle_has_actual_owner_adjacency")) is bool and
                all(type(observed.get(flag)) is bool for flag in (
                    "cpp_owner_reused_between_previous_patch_submeshes",
                    "cpp_owner_same_as_edge0_source_point",
                    "cpp_owner_same_as_edge3_source_point",
                    "original_edge0_and_edge3_source_points_are_same_cpp_object")),
                "r2718_native_accepted_cpp_owner_receipt_invalid")
        require(observed["triangle_has_actual_owner_adjacency"] is True,
                "r2718_original_accepted_triangle_not_borrowing_its_actual_owner")
        rows.append({
            "patch_slot": slot,
            "original_native_node_id": observed["native_node_id"],
            "submesh_node_slot": observed["submesh_node_slot"],
            "has_actual_accepted_triangle_adjacency":
                observed["triangle_has_actual_owner_adjacency"],
            "same_cpp_owner_pointer_as_earlier_patch":
                observed["cpp_owner_reused_between_previous_patch_submeshes"],
            "same_cpp_pointer_as_original_edge0_source_endpoint":
                observed["cpp_owner_same_as_edge0_source_point"],
            "same_cpp_pointer_as_original_edge3_source_endpoint":
                observed["cpp_owner_same_as_edge3_source_point"],
            "original_source_edge0_edge3_pointer_equal":
                observed["original_edge0_and_edge3_source_points_are_same_cpp_object"],
        })
    require(len(rows) == records[0]["source_patch_count"],
            "r2718_cpp_owner_patches_incomplete")
    return {
        "original_native_patches": len(rows),
        "actual_accepted_owner_rows": rows,
        "triangle_submesh_owner_adjacencies_observed": sum(
            item["has_actual_accepted_triangle_adjacency"] for item in rows),
        "same_cpp_owner_pointer_as_earlier_patch_count": sum(
            item["same_cpp_owner_pointer_as_earlier_patch"] for item in rows),
        "same_cpp_owner_as_source_edge0_count": sum(
            item["same_cpp_pointer_as_original_edge0_source_endpoint"] for item in rows),
        "same_cpp_owner_as_source_edge3_count": sum(
            item["same_cpp_pointer_as_original_edge3_source_endpoint"] for item in rows),
        "native_node_ids_are_not_cpp_addresses": True,
        "cross_epoch_cpp_pointer_persistence_proven": False,
    }


def match_provisional_closure(
    accepted: dict, original_events: list[dict], accepted_step: int,
) -> dict:
    """Associate same-step same-patch same-ID attempts; never infer selection."""
    rows = []
    for item in accepted["actual_accepted_owner_rows"]:
        slot = item["patch_slot"]
        scope = [
            ev for ev in original_events
            if ev["adaptive_step"] == accepted_step and ev["patch_index"] == slot
        ]
        same_id = [
            ev for ev in scope
            if ev["first_mapped_native_node_id"] == item["original_native_node_id"]
        ]
        rows.append({
            "patch_slot": slot,
            "accepted_native_logical_node_id": item["original_native_node_id"],
            "same_step_patch_provisional_boundary_closures": len(scope),
            "same_id_provisional_boundary_closures": len(same_id),
            "all_close_events_are_globally_accepted": False,
            "which_local_attempt_was_eventually_accepted_proven": False,
        })
    return {
        "original_accepted_step": accepted_step,
        "all_original_provisional_closure_events": len(original_events),
        "unique_attempt_scopes": len({
            (event["adaptive_step"], event["retry_index"],
             event["patch_index"], event["local_attempt"])
            for event in original_events
        }),
        "accepted_patch_correlations": rows,
        "patches_with_matching_provisional_closure": sum(
            r["same_id_provisional_boundary_closures"] > 0 for r in rows),
        "provisional_attempt_is_not_a_global_commit": True,
        "actual_accepted_attempt_pointers_stable_since_closure_proven": False,
    }


def audit_original_boundary_ownership(directory: Path) -> dict:
    """Authenticate all three independent real native observation layers."""
    retained = audit_retained_directory(directory)
    models = {}
    for model in SOURCE_MODELS:
        summary = json.loads(
            (directory / f"r2712-{model}-native-lineage-audit.json")
            .read_text(encoding="utf-8"))
        stderr_name = f"r2718-{model}-original-native-generator-stderr.log"
        require(summary.get("r2718_original_stderr_artifact_name") == stderr_name,
                "r2718_original_process_stderr_receipt_missing")
        original_stderr = directory.joinpath(stderr_name).read_bytes()
        stderr_hash = sha256_file(directory / stderr_name)
        require(stderr_hash == summary["native_stderr_sha256"] ==
                summary.get("r2718_original_stderr_sha256"),
                "r2718_original_process_stderr_sha256_mismatch")
        events = read_actual_adapter_events(original_stderr, model)
        snapshots = []
        for snapshot in summary["accepted_snapshots"]:
            path = directory / snapshot["raw_native_ndjson_artifact_name"]
            original_source_hash = sha256_file(path)
            require(original_source_hash == snapshot["source_file_sha256"],
                    "r2718_original_accepted_native_ndjson_sha256_mismatch")
            records = decode_ndjson(path.read_bytes())
            verified = validate_lineage_records(records, model)
            require(verified["accepted_step"] == snapshot["accepted_step"],
                    "r2718_actual_accepted_native_step_changed")
            owner = analyze_accepted_cpp_owners(records)
            closures = match_provisional_closure(owner, events, verified["accepted_step"])
            snapshots.append({
                "original_accepted_step": verified["accepted_step"],
                "original_native_source_sha256": original_source_hash,
                "direct_accepted_cpp_ownership": owner,
                "original_provisional_adapter_closure_correlations": closures,
            })
        require([snap["original_accepted_step"] for snap in snapshots] ==
                retained["original_native_models"][model]["accepted_native_steps"],
                "r2718_native_accepted_epoch_ledger_mismatch")
        models[model] = {
            "original_runtime_stderr_sha256": stderr_hash,
            "complete_original_provisional_adapter_close_events": events,
            "original_native_accepted_snapshots": snapshots,
        }
    return {
        "schema": SCHEMA,
        "original_models": models,
        "actual_cpp_node_pointer_comparison_witnessed": True,
        "raw_cpp_pointer_addresses_retained": False,
        "provisional_adapter_events_are_not_globally_accepted_commits": True,
        "selected_adapter_attempt_pointer_survival_certified": False,
        "nonmanifold_global_welding_certified": False,
        "scientific_lod_qualified": False,
        "physical_gpu_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    options = parser.parse_args()
    result = audit_original_boundary_ownership(options.directory)
    options.output.parent.mkdir(parents=True, exist_ok=True)
    with options.output.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(result, output, sort_keys=True, indent=2, allow_nan=False)
        output.write("\n")
    brief = {
        model: [{
            "step": item["original_accepted_step"],
            "patches": item["direct_accepted_cpp_ownership"]["original_native_patches"],
            "owner_adjacencies": item["direct_accepted_cpp_ownership"][
                "triangle_submesh_owner_adjacencies_observed"],
            "cross_patch_cpp_pointer_reuse": item["direct_accepted_cpp_ownership"][
                "same_cpp_owner_pointer_as_earlier_patch_count"],
            "accepted_ids_correlated_to_provisional_closures": item[
                "original_provisional_adapter_closure_correlations"][
                    "patches_with_matching_provisional_closure"],
            "candidate_closure_events": item[
                "original_provisional_adapter_closure_correlations"][
                    "all_original_provisional_closure_events"],
        } for item in details["original_native_accepted_snapshots"]]
        for model, details in result["original_models"].items()
    }
    print("R2718_ORIGINAL_BOUNDARY_CPP_OWNERSHIP=" +
          json.dumps(brief, sort_keys=True))


if __name__ == "__main__":
    main()
