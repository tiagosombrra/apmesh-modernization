"""R2.7.21 certify shared original source samples as actual accepted TRI edges.

A source curve correspondence is NOT a welded physical node. Every segment
must be an existing edge in a real accepted native triangle in its OWN patch.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .native_accepted_scene import generate_original_scene_bundle
from .verify_native_lineage import require

SCHEMA = "apmesh.meshstudio.r2721.original_native_patch_seam_edges.v1"


def audit_actual_seam_edges(bundle: dict) -> dict:
    """Check each source-sample segment against real accepted native face edges."""
    identity = {(d["model"], d["accepted_native_step"]): d
                for d in bundle["identity"]["documents"]}
    models = {}
    for scene in bundle["scenes"]:
        key = (scene["model"], scene["accepted_native_step"])
        doc = identity.get(key)
        require(doc is not None and
                doc["source_ndjson_sha256"] == scene["source_ndjson_sha256"],
                "r2721_source_scene_digest_or_epoch_mismatch")
        edges = {}
        vertices = {}
        for face in scene["native_faces"]:
            patch = face[0]
            native_patch = face[1]
            nodes = face[4]
            for node in nodes:
                index = (patch, node[0])
                reference = (node[1], node[2], node[3])
                require(index not in vertices or vertices[index] == reference,
                        "r2721_original_patch_native_node_xyz_conflict")
                vertices[index] = reference
            for i in range(3):
                a, b = nodes[i], nodes[(i + 1) % 3]
                require(a[0] != b[0],
                        "r2721_degenerate_original_native_triangle_edge")
                edge_key = (patch, min(a[0], b[0]), max(a[0], b[0]))
                edges.setdefault(edge_key, []).append(
                    (native_patch, face[2], face[3]))
        observed = []
        for curve in doc["qualified_shared_source_curves"]:
            members_by_sample = [{
                member["patch_slot"]: member for member in group["members"]
            } for group in curve["sample_groups"]]
            patches = curve["patch_slots"]
            require(all(set(members) == set(patches)
                        for members in members_by_sample),
                    "r2721_original_source_incidence_incomplete")
            per_patch = []
            for patch in patches:
                hits = []
                for ordinal in range(len(members_by_sample) - 1):
                    first = members_by_sample[ordinal][patch]
                    second = members_by_sample[ordinal + 1][patch]
                    left, right = first["native_node_id"], second["native_node_id"]
                    require(left != right, "r2721_zero_length_original_native_edge_id")
                    for node in (first, second):
                        key_node = (patch, node["native_node_id"])
                        require(key_node in vertices and
                                all(abs(a-b) <= 1e-9 for a,b in zip(
                                    vertices[key_node],node["original_xyz"])),
                                "r2721_original_source_sample_native_face_xyz_mismatch")
                    edge_key = (patch, min(left, right), max(left, right))
                    require(edge_key in edges,
                            "r2721_source_sample_segment_is_not_accepted_tri_edge")
                    hits.append({
                        "source_sample_ordinal_start": ordinal,
                        "native_node_id_start": left,
                        "native_node_id_end": right,
                        "real_incident_face_count": len(edges[edge_key]),
                        "original_incident_element_slots": sorted({
                            row[1] for row in edges[edge_key]}),
                    })
                per_patch.append({
                    "original_source_patch_slot": patch,
                    "real_accepted_native_edge_segments": len(hits),
                    "exact_original_sample_edge_witnesses": hits,
                })
            observed.append({
                "original_source_curve_slot": curve["source_curve_slot"],
                "original_native_curve_id": curve["native_curve_id"],
                "distinct_patch_incidence": len(patches),
                "source_sample_groups": curve["sample_count"],
                "all_patch_sample_segments_are_actual_accepted_native_tri_edges": True,
                "patch_local_edge_witnesses": per_patch,
                "total_patch_local_accepted_edge_segments": sum(
                    row["real_accepted_native_edge_segments"] for row in per_patch),
                "source_geom_xyz_match_is_not_cpp_pointer_welding": True,
            })
        require(bool(observed), "r2721_no_qualified_actual_shared_source_curve")
        models[scene["model"]] = {
            "real_native_accepted_step": scene["accepted_native_step"],
            "original_native_face_ndjson_sha256": scene["source_ndjson_sha256"],
            "real_accepted_tri_faces": scene["native_tri_faces"],
            "qualified_shared_source_edges": observed,
            "total_qualified_patch_local_edges": sum(
                r["total_patch_local_accepted_edge_segments"] for r in observed),
        }
    return {
        "schema": SCHEMA,
        "scope": "ORIGINAL_NATIVE_ACCEPTED_TRI_EDGE_MEMBERSHIP_NOT_WELDED",
        "original_models": models,
        "raw_pointer_addresses_serialized": False,
        "cross_patch_welding_certified": False,
        "cross_epoch_descendant_faces_certified": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = audit_actual_seam_edges(generate_original_scene_bundle(args.directory))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as file:
        file.write((json.dumps(evidence,sort_keys=True,indent=2,
                               allow_nan=False)+"\n").encode("utf-8"))
    print("R2721_ORIGINAL_ACTUAL_NATIVE_TRI_SEAM_EDGES=" +
          json.dumps({name:{
              "source_sha256":report["original_native_face_ndjson_sha256"],
              "accepted_native_step":report["real_native_accepted_step"],
              "patch_local_real_tri_edges":report["total_qualified_patch_local_edges"],
              "shared_source_curves":len(report["qualified_shared_source_edges"]),
              "all_native_edges_present":True,
              "welded_cpp_nodes_certified":False,
          } for name,report in evidence["original_models"].items()},sort_keys=True))


if __name__ == "__main__":
    main()
