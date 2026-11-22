"""R2.7.20 real accepted native TRI scene, never an OBJ ordinal conversion.

All displayed triangles are reprojected directly from original accepted C++
per-face native NDJSON, with exact patch, element and per-corner identity.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit_retained_native_lineage import audit_retained_directory
from .native_identity_inspector import generate_original_inspector_bundle
from .verify_native_lineage import (
    SOURCE_MODELS, decode_ndjson, integer, require, sha256_file,
    validate_lineage_records,
)

SCHEMA = "apmesh.meshstudio.r2720.original_accepted_tri_scene.v1"
MAX_TRI_PER_MODEL = 12_000
MAX_SCENE_BYTES = 9_000_000
MAX_SAFE_BROWSER_ID = 2**53 - 1


def project_accepted_faces(
    records: list[dict], model: str, expected_sha: str,
) -> dict:
    """Retain native per-face identity and original double-precision corners."""
    verified = validate_lineage_records(records, model)
    patches_expected, curves_expected = SOURCE_MODELS[model]
    require(type(expected_sha) is str and len(expected_sha) == 64,
            "r2720_missing_original_native_source_digest")
    patches = {
        row["patch_slot"]: row
        for row in records if row["type"] == "patch"
    }
    source_faces = [row for row in records if row["type"] == "face"]
    require(len(source_faces) == verified["native_tri_faces"] and
            len(source_faces) <= MAX_TRI_PER_MODEL,
            "r2720_original_native_tri_count_out_of_bounds")
    original_faces = []
    slots = set()
    counts = [0] * patches_expected
    for face in source_faces:
        patch_slot = face["patch_slot"]
        native_patch_id = face["native_patch_id"]
        element_slot = face["element_slot"]
        native_element_id = face["native_element_id"]
        require(all(integer(v) and v <= MAX_SAFE_BROWSER_ID for v in (
            patch_slot, native_patch_id, element_slot, native_element_id)),
            "r2720_original_native_face_id_not_browser_safe")
        require(native_patch_id == patches[patch_slot]["native_patch_id"] and
                (patch_slot, element_slot) not in slots,
                "r2720_original_native_face_owner_ambiguous")
        slots.add((patch_slot, element_slot))
        vertices = []
        for node in face["vertices"]:
            require(integer(node["native_node_id"]) and
                    node["native_node_id"] <= MAX_SAFE_BROWSER_ID,
                    "r2720_original_native_node_id_not_browser_safe")
            # Preserve original C++ double values as JSON numbers. VTK uses
            # Float32 solely for display, never as the source identity oracle.
            vertices.append([
                node["native_node_id"],
                *node["xyz"],
                *node["uv"],
            ])
        original_faces.append([
            patch_slot, native_patch_id, element_slot, native_element_id,
            vertices,
        ])
        counts[patch_slot] += 1
    require(all(counts[p] == patches[p]["face_count"] for p in patches) and
            sum(counts) == verified["native_tri_faces"],
            "r2720_original_native_patch_face_inventory_mismatch")
    return {
        "model": model,
        "accepted_native_step": verified["accepted_step"],
        "source_ndjson_sha256": expected_sha,
        "native_source_patches": patches_expected,
        "native_source_curves": curves_expected,
        "native_tri_faces": verified["native_tri_faces"],
        "source_patch_face_counts": counts,
        "native_faces": original_faces,
        "face_identity": "accepted_step_patch_slot_element_slot_and_native_element_id",
        "corner_identity": "original_patch_local_native_node_id_xyz_uv",
        "visual_transport_float32_only": True,
        "independent_original_ndjson_sha_verified_before_export": True,
        "original_node_ids_unchanged": True,
        "patch_local_points_not_globally_welded": True,
        "cross_epoch_lineage_certified": False,
        "scientific_lod_qualified": False,
    }


def generate_original_scene_bundle(directory: Path) -> dict:
    """Only fully retained original postcommit C++ records may enter the scene."""
    retained = audit_retained_directory(directory)
    identity = generate_original_inspector_bundle(directory)
    existing = {
        (row["model"], row["accepted_native_step"]):
        row for row in identity["documents"]
    }
    scenes = []
    for model in SOURCE_MODELS:
        report = json.loads(
            (directory / f"r2712-{model}-native-lineage-audit.json")
            .read_text(encoding="utf-8"))
        for epoch in report["accepted_snapshots"]:
            path = directory / epoch["raw_native_ndjson_artifact_name"]
            sha = sha256_file(path)
            require(sha == epoch["source_file_sha256"],
                    "r2720_original_accepted_native_bytes_changed")
            records = decode_ndjson(path.read_bytes())
            scene = project_accepted_faces(records, model, sha)
            key = (model, scene["accepted_native_step"])
            require(key in existing and
                    existing[key]["source_ndjson_sha256"] == sha and
                    existing[key]["source_patch_count"] == scene["native_source_patches"] and
                    scene["accepted_native_step"] == epoch["accepted_step"],
                    "r2720_scene_identity_accepted_epoch_or_digest_mismatch")
            scenes.append(scene)
        require([row["accepted_native_step"] for row in scenes
                 if row["model"] == model] ==
                retained["original_native_models"][model]["accepted_native_steps"],
                "r2720_original_native_epoch_inventory_mismatch")
    require(len(scenes) == len(existing), "r2720_scene_did_not_cover_identity_receipts")
    return {
        "schema": SCHEMA,
        "scope": "ORIGINAL_NATIVE_ACCEPTED_TRI_SEPARATE_VISUAL_RESEARCH",
        "identity": identity,
        "scenes": scenes,
        "native_triangles_only": True,
        "visual_float32_not_source_precision": True,
        "source_face_ids_not_obj_ordinals": True,
        "no_implicit_node_welding": True,
        "no_cross_epoch_face_ancestry": True,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = generate_original_scene_bundle(args.directory)
    body = (json.dumps(output, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode("utf-8")
    require(len(body) <= MAX_SCENE_BYTES, "r2720_native_visual_export_oversized")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as file:
        file.write(body)
    print("R2720_ORIGINAL_ACCEPTED_NATIVE_TRI_SCENES=" +
          json.dumps({
              item["model"]: {
                  "source_sha256": item["source_ndjson_sha256"],
                  "accepted_native_step": item["accepted_native_step"],
                  "native_tri_faces": item["native_tri_faces"],
                  "source_patches": item["native_source_patches"],
                  "native_face_key": "patch+element_slot+native_element_id",
                  "physical_welding_certified": False,
              } for item in output["scenes"]
          }, sort_keys=True))


if __name__ == "__main__":
    main()
