"""R2.7.16 source-scoped non-welded seam correspondence from accepted TRI.

A canonical sample group is only a read-only association within one actual
accepted native step. It is never a newly allocated native node, a welded
topological vertex or a certified descendant across adaptive epochs.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path

from .native_seam_samples import audit_original_sampled_seams

SCHEMA = "apmesh.meshstudio.r2716.native_nonwelded_sample_correspondence.v1"


def build_curve_correspondence(curve: dict, step: int) -> dict:
    """Group original patch-local IDs only after full sampled geometry parity."""
    sides = curve["native_patch_sides"]
    comparisons = curve["pairwise_sample_comparisons"]
    qualified = (
        len(sides) >= 2 and bool(comparisons)
        and all(side["sampled_uv_edge_chain_complete"] for side in sides)
        and all(
            pair["source_boundary_chains_complete"]
            and pair["same_sample_count"]
            and pair["canonical_t_aligned_with_tolerance"]
            and pair["xyz_aligned_with_explicit_tolerance"]
            for pair in comparisons
        )
    )
    result = {
        "original_source_curve_slot": curve["source_curve_slot"],
        "original_native_curve_id": curve["native_curve_id"],
        "native_accepted_step": step,
        "source_owner_patch_slots": curve["distinct_owner_patch_slots"],
        "pairwise_geometry_qualified": qualified,
        "read_only_seam_sample_groups": [],
        "original_node_ids_preserved": True,
        "new_global_native_node_id_allocated": False,
        "cpp_node_objects_welded": False,
        "cross_epoch_descendant_identity_certified": False,
    }
    if not qualified:
        result["nonqualification_reason"] = (
            "incomplete_or_mismatched_real_native_sampled_boundary")
        return result

    size = sides[0]["unique_boundary_node_count"]
    reference = sides[0]["native_boundary_nodes"]
    histogram: Counter[str] = Counter()
    max_delta = 0.0
    max_t_delta = 0.0
    for sample_index in range(size):
        vertices = [side["native_boundary_nodes"][sample_index] for side in sides]
        distinct_ids = {vertex["native_node_id"] for vertex in vertices}
        if len(distinct_ids) == 1:
            id_class = "same_native_logical_id_in_all_source_patches"
        elif len(distinct_ids) == len(vertices):
            id_class = "different_native_logical_id_in_every_source_patch"
        else:
            id_class = "mixed_reused_native_logical_ids"
        histogram[id_class] += 1
        for i, left in enumerate(vertices):
            for right in vertices[i + 1:]:
                max_delta = max(max_delta, math.dist(left["xyz"], right["xyz"]))
                max_t_delta = max(max_t_delta, abs(left["t"] - right["t"]))
        result["read_only_seam_sample_groups"].append({
            "source_scoped_sample_reference": {
                "accepted_step": step,
                "source_curve_slot": curve["source_curve_slot"],
                "sample_ordinal_within_this_step": sample_index,
                "namespace": "read_only_original_source_sample_not_native_id",
            },
            "reference_canonical_t": reference[sample_index]["t"],
            "original_native_members": [{
                "patch_slot": side["patch_slot"],
                "edge_slot": side["edge_slot"],
                "original_native_node_id": side["native_boundary_nodes"][
                    sample_index]["native_node_id"],
                "original_canonical_t": side["native_boundary_nodes"][sample_index]["t"],
                "original_xyz": side["native_boundary_nodes"][sample_index]["xyz"],
            } for side in sides],
            "logical_node_id_relation": id_class,
            "shared_native_cpp_node_pointer_proven": False,
        })
    result["seam_sample_groups"] = size
    result["logical_node_id_relation_counts"] = dict(sorted(histogram.items()))
    result["maximum_observed_xyz_pair_distance"] = max_delta
    result["maximum_observed_canonical_t_pair_distance"] = max_t_delta
    return result


def build_original_correspondence(original: dict) -> dict:
    """Create per-epoch renderable source associations without mutating meshes."""
    models = {}
    for model, snapshots in original["original_native_models"].items():
        outputs = []
        for snapshot in snapshots:
            step = snapshot["original_native_accepted_step"]
            sampled = snapshot["sampled_boundary"]
            curves = [build_curve_correspondence(curve, step)
                      for curve in sampled["shared_original_source_seams"]]
            outputs.append({
                "original_native_accepted_step": step,
                "original_source_ndjson_sha256": snapshot["original_native_source_sha256"],
                "shared_source_curve_count": len(curves),
                "qualified_nonwelded_source_curves": sum(
                    row["pairwise_geometry_qualified"] for row in curves),
                "sample_correspondence_groups": sum(
                    len(row["read_only_seam_sample_groups"]) for row in curves),
                "source_scoped_curve_correspondences": curves,
                "physical_mesh_node_welding_certified": False,
                "cross_epoch_face_curve_ancestry_certified": False,
            })
        models[model] = outputs
    return {
        "schema": SCHEMA,
        "derived_only_from_native_accepted_source_sha_pins": True,
        "original_models": models,
        "synthetic_global_node_id_was_created": False,
        "original_native_node_ids_overwritten": False,
        "geometric_analytic_continuity_certified": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    original = audit_original_sampled_seams(args.directory)
    result = build_original_correspondence(original)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    brief = {
        model: [{
            "step": snapshot["original_native_accepted_step"],
            "source_curves": snapshot["shared_source_curve_count"],
            "geometric_sampled_curve_groups": snapshot["qualified_nonwelded_source_curves"],
            "read_only_sample_references": snapshot["sample_correspondence_groups"],
            "logical_id_histograms": [
                curve.get("logical_node_id_relation_counts", {})
                for curve in snapshot["source_scoped_curve_correspondences"]
            ],
        } for snapshot in values]
        for model, values in result["original_models"].items()
    }
    print("R2716_ORIGINAL_NONWELDED_CORRESPONDENCE=" +
          json.dumps(brief, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
