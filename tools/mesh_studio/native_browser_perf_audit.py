"""R2.7.22 audit hosted Chromium timings against real original native C++.

A browser E2E measurement is affected by driver, load and test-controller
overhead. It must not be called physical GPU present, RSS, VRAM, a rendering
regression threshold, or an accepted multi-epoch scientific geometry result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

from .verify_native_lineage import require

SCHEMA = "apmesh.meshstudio.r2722.real_original_native_chromium_interactions.v1"
AUDIT_SCHEMA = "apmesh.meshstudio.r2722.hosted_native_browser_performance_audit.v1"


def number(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def audit_distribution(raw: object, required_samples: int) -> dict:
    require(type(raw) is dict and raw.get("samples") == required_samples and
            type(raw.get("observed_ms")) is list and
            len(raw["observed_ms"]) == required_samples,
            "r2722_original_browser_sample_count_or_distribution_invalid")
    values = raw["observed_ms"]
    require(all(number(x) and x < 120_000 for x in values),
            "r2722_nonfinite_or_unbounded_original_browser_duration")
    ordered = sorted(values)
    for key, reference in (
        ("minimum_ms", ordered[0]),
        ("median_ms", ordered[math.ceil((len(ordered)-1)*.5)]),
        ("p95_ms", ordered[math.ceil((len(ordered)-1)*.95)]),
        ("maximum_ms", ordered[-1]),
    ):
        require(number(raw.get(key)) and
                abs(raw[key]-reference) <= .01,
                "r2722_reported_percentile_not_from_actual_sample_values")
    return {
        "samples":len(ordered),
        "median_ms":raw["median_ms"],
        "p95_ms":raw["p95_ms"],
        "maximum_ms":raw["maximum_ms"],
    }


def audit_original_browser_measurements(
    report: dict, budget: dict, scene_bytes: bytes,
) -> dict:
    """Refuse mixed sources, fake GPU claims and manipulated sample summaries."""
    require(type(report) is dict and report.get("schema") == SCHEMA and
            report.get("source_kind") ==
            "SAME_RUN_COMPILED_ORIGINAL_ACCEPTED_NATIVE_TRI_SCENE" and
            report.get("physical_windows_gpu_present_rss_vram_qualified") is False and
            report.get("scientific_lod_qualified") is False and
            type(report.get("source_browser_user_agent")) is str and
            "Chrome" in report["source_browser_user_agent"] and
            "ubuntu-24.04 GitHub-hosted Chromium" in
            report.get("hosted_runner_scope",""),
            "r2722_browser_scope_or_false_gpu_qualification")
    require(budget.get("schema") ==
            "apmesh.meshstudio.r2722.native_visual_transfer_budget.v1" and
            budget.get("explicit_arrays_estimates_only") is True and
            budget.get("physical_windows_gpu_rss_vram_gate_qualified") is False and
            budget.get("scientific_lod_qualified") is False,
            "r2722_original_source_transfer_budget_untrusted")
    digest=hashlib.sha256(scene_bytes).hexdigest()
    require(report.get("original_scene_json_sha256") == digest ==
            budget["source_scene_json_sha256"] and
            report.get("original_scene_json_bytes") == len(scene_bytes) ==
            budget["source_scene_json_bytes"] and
            len(scene_bytes)<=9_000_000,
            "r2722_hosted_browser_source_sha_or_byte_length_mismatch")
    expected_sha=os.getenv("GITHUB_SHA")
    if expected_sha:
        require(report.get("workflow_sha") == expected_sha,
                "r2722_browser_workflow_revision_not_same_original_source")
    original=json.loads(scene_bytes)
    require(original.get("schema") ==
            "apmesh.meshstudio.r2720.original_accepted_tri_scene.v1" and
            original.get("no_implicit_node_welding") is True and
            original.get("scientific_lod_qualified") is False,
            "r2722_scene_unqualified_native_source")
    sources={
        s["model"]:s for s in original["scenes"]
    }
    measured=report.get("real_original_sources")
    require(type(measured) is dict and
            set(measured) == set(sources) == set(budget["models"]) ==
            {"eistute","book"},
            "r2722_real_eistute_book_original_measurements_incomplete")
    read=report.get("imported_original_cpu")
    require(type(read) is dict and
            read.get("json_bytes") == len(scene_bytes) and
            all(number(read.get(x)) for x in (
                "file_read_ms","contract_ms","verified_real_seam_edges_ms",
                "pre_react_ms")) and
            number(report.get("original_import_to_two_raf_ready_ms")) and
            report["original_import_to_two_raf_ready_ms"] >= read["pre_react_ms"],
            "r2722_original_import_measurements_missing_or_nonmonotonic")
    models={}
    for model,scene in sources.items():
        observed=measured[model]
        source_budget=budget["models"][model]
        require(type(observed) is dict and
                observed.get("original_native_accepted_step") ==
                scene["accepted_native_step"] ==
                source_budget["actually_accepted_native_step"] == 1 and
                observed.get("original_native_source_sha256") ==
                scene["source_ndjson_sha256"] ==
                source_budget["original_native_source_sha256"] and
                observed.get("real_original_accepted_faces") ==
                scene["native_tri_faces"] ==
                source_budget["accepted_tri_faces"] and
                observed.get("original_source_patches") ==
                scene["native_source_patches"] ==
                source_budget["source_patches"] and
                observed.get("original_accepted_seam_edges") ==
                source_budget["verified_seam_segments"] and
                observed.get("physical_gpu_present_time_measured") is False and
                number(observed.get("model_select_to_two_raf_ready_ms")),
                "r2722_original_browser_model_source_or_gpu_claim_mismatch")
        patches=audit_distribution(observed.get("patches"),10)
        samples=audit_distribution(observed.get("source_samples"),6)
        for viewport, expected_faces in (
            ("final_xyz_vtk_cpu_calls",scene["native_tri_faces"]),
            ("final_local_uv_vtk_cpu_calls",scene["source_patch_face_counts"][1]),
        ):
            receipt=observed.get(viewport)
            require(type(receipt) is dict and
                    receipt.get("typed_cpu_buffer_bytes") == expected_faces*56 and
                    all(number(receipt.get(k)) for k in (
                        "vtk_setup_cpu_ms","vtk_render_call_cpu_ms",
                        "vtk_seam_overlay_cpu_ms")),
                    "r2722_original_native_vtk_explicit_buffer_or_cpu_receipt_invalid")
        models[model]={
            "real_original_accepted_tri_faces":scene["native_tri_faces"],
            "source_original_ndjson_sha256":scene["source_ndjson_sha256"],
            "original_patch_local_accepted_seam_edges":
                source_budget["verified_seam_segments"],
            "hosted_patch_selection":patches,
            "hosted_source_sample_selection":samples,
            "model_to_two_raf_ready_ms":
                observed["model_select_to_two_raf_ready_ms"],
            "xyz_explicit_cpu_typed_buffer_bytes":
                observed["final_xyz_vtk_cpu_calls"]["typed_cpu_buffer_bytes"],
            "physical_gpu_present_qualified":False,
        }
    for name in ("memory_before_original_import","memory_after_original_import",
                 "memory_after_interactions"):
        sample=report.get(name)
        require(type(sample) is dict and
                number(sample.get("js_heap_used_bytes")) and
                sample["js_heap_used_bytes"] > 0 and
                number(sample.get("js_heap_total_bytes")) and
                sample["js_heap_total_bytes"] >= sample["js_heap_used_bytes"],
                "r2722_browser_cdp_js_heap_sample_missing")
    return {
        "schema":AUDIT_SCHEMA,
        "actual_same_run_original_native_scene_sha256":digest,
        "original_json_bytes":len(scene_bytes),
        "hosted_browser_js_heap_before_bytes":
            report["memory_before_original_import"]["js_heap_used_bytes"],
        "hosted_browser_js_heap_after_import_bytes":
            report["memory_after_original_import"]["js_heap_used_bytes"],
        "hosted_browser_js_heap_after_interactions_bytes":
            report["memory_after_interactions"]["js_heap_used_bytes"],
        "real_original_models":models,
        "no_statistical_or_physical_workstation_claim":True,
        "actual_gpu_present_measured":False,
        "actual_windows_physical_process_rss_measured":False,
        "actual_vram_measured":False,
        "scientific_lod_qualified":False,
    }


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report",type=Path,required=True)
    parser.add_argument("--budget",type=Path,required=True)
    parser.add_argument("--scene",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    audit=audit_original_browser_measurements(
        json.loads(args.report.read_text(encoding="utf-8")),
        json.loads(args.budget.read_text(encoding="utf-8")),
        args.scene.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write((json.dumps(audit,indent=2,sort_keys=True,
                                 allow_nan=False)+"\n").encode())
    print("R2722_ORIGINAL_HOSTED_CHROMIUM_PERF_AUDIT="+json.dumps({
        "source_sha256":audit["actual_same_run_original_native_scene_sha256"],
        "models":{m:{
            "faces":row["real_original_accepted_tri_faces"],
            "patch_p95_ms":row["hosted_patch_selection"]["p95_ms"],
            "sample_p95_ms":row["hosted_source_sample_selection"]["p95_ms"],
        } for m,row in audit["real_original_models"].items()},
        "physical_gpu_present_qualified":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
