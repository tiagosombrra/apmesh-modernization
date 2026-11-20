"""R2.7.19 read-only native seam inspector bundle, from authentic accepted TRI.

An exported source-sample association is not a welded node, selected local
Adapter attempt, immutable C++ pointer or valid geometric LOD.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .native_boundary_ownership import audit_original_boundary_ownership
from .native_seam_correspondence import build_original_correspondence
from .native_seam_samples import audit_original_sampled_seams
from .verify_native_lineage import SOURCE_MODELS, require

SCHEMA = "apmesh.meshstudio.r2719.native_nonwelded_inspector.v1"
MAX_BUNDLE_BYTES = 800_000


def build_native_inspector_bundle(correspondences: dict, owners: dict,
                                  summaries: dict[str, dict]) -> dict:
    """Join distinct verified original reports only by model, epoch and SHA."""
    documents = []
    for model, expected_counts in SOURCE_MODELS.items():
        owner_models = owners["original_models"][model]
        owner_epochs = {
            row["original_accepted_step"]: row
            for row in owner_models["original_native_accepted_snapshots"]
        }
        snapshots = correspondences["original_models"][model]
        require(len(snapshots) == len(owner_epochs) and len(snapshots) >= 1,
                "r2719_original_native_epoch_inventory_changed")
        for item in snapshots:
            step = item["original_native_accepted_step"]
            require(step in owner_epochs, "r2719_unverified_original_native_step")
            ownership = owner_epochs[step]
            require(item["original_source_ndjson_sha256"] ==
                    ownership["original_native_source_sha256"],
                    "r2719_original_native_source_sha_join_mismatch")
            original_owner = ownership["direct_accepted_cpp_ownership"]
            patches = {
                row["patch_slot"]: row
                for row in original_owner["actual_accepted_owner_rows"]
            }
            require(len(patches) == expected_counts[0] and
                    len(item["source_scoped_curve_correspondences"]) <=
                    expected_counts[1], "r2719_original_native_owner_inventory_incomplete")
            curves = []
            for curve in item["source_scoped_curve_correspondences"]:
                if not curve["pairwise_geometry_qualified"]:
                    continue
                patch_slots = curve["source_owner_patch_slots"]
                require(len(patch_slots) >= 2 and len(set(patch_slots)) ==
                        len(patch_slots) and all(p in patches for p in patch_slots),
                        "r2719_original_curve_owner_patches_mismatch")
                samples = []
                for ordinal, group in enumerate(curve["read_only_seam_sample_groups"]):
                    ref = group["source_scoped_sample_reference"]
                    require(ref["accepted_step"] == step and
                            ref["source_curve_slot"] ==
                            curve["original_source_curve_slot"] and
                            ref["sample_ordinal_within_this_step"] == ordinal and
                            ref["namespace"] ==
                            "read_only_original_source_sample_not_native_id",
                            "r2719_original_sample_reference_not_source_scoped")
                    members = []
                    for raw in group["original_native_members"]:
                        patch = raw["patch_slot"]
                        require(patch in patches, "r2719_member_has_foreign_patch")
                        corner = (
                            patches[patch] if ordinal == 0 and
                            raw["edge_slot"] == 3 else None
                        )
                        if corner is not None:
                            # Only accepted UV(0,0) owns this direct C++ pointer
                            # witness. Other samples have unknown pointer identity.
                            require(raw["original_native_node_id"] ==
                                    corner["original_native_node_id"],
                                    "r2719_corner_sample_id_not_real_accepted_owner")
                        members.append({
                            "patch_slot": patch,
                            "edge_slot": raw["edge_slot"],
                            "native_node_id": raw["original_native_node_id"],
                            "original_xyz": raw["original_xyz"],
                            "canonical_t": raw["original_canonical_t"],
                            "accepted_corner_cpp_owner_observed": (
                                corner["has_actual_accepted_triangle_adjacency"]
                                if corner is not None else None),
                            "accepted_corner_shared_cpp_pointer_with_earlier_patch": (
                                corner["same_cpp_owner_pointer_as_earlier_patch"]
                                if corner is not None else None),
                        })
                    require(sorted(x["patch_slot"] for x in members) ==
                            sorted(patch_slots),
                            "r2719_incomplete_original_source_sample_members")
                    samples.append({
                        "ordinal": ordinal,
                        "canonical_t": group["reference_canonical_t"],
                        "logical_id_relation": group["logical_node_id_relation"],
                        "members": sorted(members, key=lambda m: m["patch_slot"]),
                    })
                require(len(samples) >= 2,
                        "r2719_empty_qualified_original_curve_samples")
                curves.append({
                    "source_curve_slot": curve["original_source_curve_slot"],
                    "native_curve_id": curve["original_native_curve_id"],
                    "patch_slots": sorted(patch_slots),
                    "sample_count": len(samples),
                    "sample_groups": samples,
                    "pairwise_source_geometry_qualified": True,
                    "physical_node_welding_certified": False,
                })
            require(curves and len(curves) <= 64,
                    "r2719_missing_qualified_original_shared_curve")
            base = summaries[model]
            documents.append({
                "model": model,
                "accepted_native_step": step,
                "source_ndjson_sha256": item["original_source_ndjson_sha256"],
                "original_model_input_sha256": base["real_model_input_sha256"],
                "original_config_sha256": base["native_config_source_sha256"],
                "original_stderr_sha256": owner_models["original_runtime_stderr_sha256"],
                "source_patch_count": expected_counts[0],
                "source_curve_count": expected_counts[1],
                "original_adapter_provisional_close_events": ownership[
                    "original_provisional_adapter_closure_correlations"][
                        "all_original_provisional_closure_events"],
                "accepted_corner_cpp_adjacency_count": original_owner[
                    "triangle_submesh_owner_adjacencies_observed"],
                "accepted_corner_cpp_pointer_reuse_count": original_owner[
                    "same_cpp_owner_pointer_as_earlier_patch_count"],
                "qualified_shared_source_curves": curves,
                "source_geometry_is_separate_from_current_studio_viewports": True,
                "original_native_node_ids_preserved": True,
                "physical_node_welding_certified": False,
                "cross_epoch_lineage_certified": False,
                "continuous_geometric_error_bound_certified": False,
                "scientific_lod_qualified": False,
            })
    require(len(documents) <= 8, "r2719_unbounded_original_native_snapshots")
    return {
        "schema": SCHEMA,
        "scope": "ORIGINAL_COMPILED_ACCEPTED_TRI_SOURCE_SCOPED_READ_ONLY",
        "documents": documents,
        "built_from_source_sha_pinned_native_audits": True,
        "imported_browser_bundle_is_not_cryptographically_authenticated": True,
        "original_native_node_ids_rewritten": False,
        "new_globally_welded_node_ids_created": False,
        "selected_local_attempt_lifetime_certified": False,
        "scientific_lod_qualified": False,
    }


def generate_original_inspector_bundle(directory: Path) -> dict:
    """Revalidate authentic original generator outputs, not OBJ ordinal data."""
    sampled = audit_original_sampled_seams(directory)
    correspondence = build_original_correspondence(sampled)
    ownership = audit_original_boundary_ownership(directory)
    summaries = {
        model: json.loads(
            (directory / f"r2712-{model}-native-lineage-audit.json")
            .read_text(encoding="utf-8"))
        for model in SOURCE_MODELS
    }
    return build_native_inspector_bundle(correspondence, ownership, summaries)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = generate_original_inspector_bundle(args.directory)
    body = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) +
            "\n").encode("utf-8")
    require(len(body) <= MAX_BUNDLE_BYTES,
            "r2719_native_inspector_bundle_exceeds_bounded_capacity")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as output:
        output.write(body)
    print("R2719_ORIGINAL_NONWELDED_INSPECTOR=" + json.dumps({
        doc["model"]: {
            "accepted_step": doc["accepted_native_step"],
            "original_source_sha256": doc["source_ndjson_sha256"],
            "source_patches": doc["source_patch_count"],
            "qualified_shared_curves": len(doc["qualified_shared_source_curves"]),
            "samples_per_curve": [
                curve["sample_count"] for curve in doc["qualified_shared_source_curves"]],
            "source_cpp_pointer_reuse": doc["accepted_corner_cpp_pointer_reuse_count"],
        } for doc in result["documents"]
    }, sort_keys=True))


if __name__ == "__main__":
    main()
