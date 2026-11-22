"""R2.7.22 independently bound original accepted TRI visual transfer buffers.

These byte counts are deterministic CPU-side typed-array allocations predicted
from source faces, NOT measurements of live browser heap, process RSS, GPU
VRAM, render-to-present latency, or sustained physical workstation performance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .native_accepted_scene import generate_original_scene_bundle
from .verify_native_lineage import require

SCHEMA = "apmesh.meshstudio.r2722.native_visual_transfer_budget.v1"
MAX_ORIGINAL_JSON_BYTES = 9_000_000
XYZ_BYTES_PER_TRI = 9 * 4 + 4 * 4 + 4
UV_BYTES_PER_TRI = XYZ_BYTES_PER_TRI
VTK_LINE_BYTES_PER_SEGMENT = 6 * 4 + 3 * 4


def calculate_native_transfer_budget(original: dict, original_bytes: bytes) -> dict:
    """Account only for explicit JS Float32/Uint32/Uint8 transport arrays."""
    require(len(original_bytes) <= MAX_ORIGINAL_JSON_BYTES and
            original.get("schema") ==
            "apmesh.meshstudio.r2720.original_accepted_tri_scene.v1" and
            original.get("no_implicit_node_welding") is True and
            original.get("scientific_lod_qualified") is False,
            "r2722_unqualified_native_scene_or_unbounded_json")
    identity = {
        (d["model"], d["accepted_native_step"]): d
        for d in original["identity"]["documents"]
    }
    models = {}
    for scene in original["scenes"]:
        name = scene["model"]
        require(name in ("eistute", "book") and name not in models and
                scene["scientific_lod_qualified"] is False and
                scene["patch_local_points_not_globally_welded"] is True,
                "r2722_unqualified_original_model")
        counts = scene["source_patch_face_counts"]
        total = scene["native_tri_faces"]
        expected = 1168 if name == "eistute" else 4256
        patches = 4 if name == "eistute" else 28
        require(total == expected and len(counts) == patches and
                sum(counts) == total and
                len(scene["native_faces"]) == total,
                "r2722_original_native_source_tri_inventory_changed")
        doc = identity.get((name,scene["accepted_native_step"]))
        require(doc is not None and
                doc["source_ndjson_sha256"] == scene["source_ndjson_sha256"],
                "r2722_original_source_digest_mismatch")
        segments = sum(
            len(curve["patch_slots"]) * (curve["sample_count"] - 1)
            for curve in doc["qualified_shared_source_curves"])
        require(segments == (40 if name == "eistute" else 336),
                "r2722_source_seam_edge_inventory_changed")
        max_patch = max(counts)
        models[name] = {
            "original_native_source_sha256":scene["source_ndjson_sha256"],
            "actually_accepted_native_step":scene["accepted_native_step"],
            "accepted_tri_faces":total,
            "source_patches":patches,
            "max_tri_faces_in_one_patch_local_uv":max_patch,
            "verified_seam_segments":segments,
            "xyz_display_typed_arrays_bytes":total*XYZ_BYTES_PER_TRI,
            "max_one_patch_uv_typed_arrays_bytes":max_patch*UV_BYTES_PER_TRI,
            "all_source_seam_line_arrays_bytes":segments*VTK_LINE_BYTES_PER_SEGMENT,
            "estimated_concurrent_explicit_cpu_typed_arrays_upper_envelope_bytes":
                (total+max_patch)*XYZ_BYTES_PER_TRI +
                segments*VTK_LINE_BYTES_PER_SEGMENT,
            "actual_browser_heap_bytes_measured":False,
            "actual_gpu_vram_bytes_measured":False,
            "actual_render_to_present_measured":False,
        }
    require(len(models)==2,"r2722_original_native_models_missing")
    return {
        "schema":SCHEMA,
        "source_scene_json_sha256":hashlib.sha256(original_bytes).hexdigest(),
        "source_scene_json_bytes":len(original_bytes),
        "source_original_ndjson_sha_verified_independently":True,
        "models":models,
        "explicit_arrays_estimates_only":True,
        "hosted_browser_heap_requires_separate_evidence":True,
        "physical_windows_gpu_rss_vram_gate_qualified":False,
        "scientific_lod_qualified":False,
    }


def audit_native_transfer_budget(scene_file:Path,original_directory:Path)->dict:
    """Refuse a fake scene: reconstruct independently from original native C++."""
    original_bytes=scene_file.read_bytes()
    require(len(original_bytes)<=MAX_ORIGINAL_JSON_BYTES,
            "r2722_original_scene_json_exceeds_bound")
    parsed=json.loads(original_bytes)
    qualified=generate_original_scene_bundle(original_directory)
    require(parsed==qualified,
            "r2722_original_scene_json_does_not_match_cpp_source")
    return calculate_native_transfer_budget(qualified,original_bytes)


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-directory",type=Path,required=True)
    parser.add_argument("--scene",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=audit_native_transfer_budget(args.scene,args.original_directory)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write((json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n").encode())
    print("R2722_ORIGINAL_NATIVE_VISUAL_TRANSFER_BUDGET="+
          json.dumps({
              "source_scene_json_bytes":result["source_scene_json_bytes"],
              "models":{name:{
                  "tri_faces":row["accepted_tri_faces"],
                  "patches":row["source_patches"],
                  "explicit_cpu_typed_array_envelope_bytes":row[
                      "estimated_concurrent_explicit_cpu_typed_arrays_upper_envelope_bytes"],
              } for name,row in result["models"].items()},
              "gpu_vram_qualified":False,
          },sort_keys=True))


if __name__=="__main__":
    main()
