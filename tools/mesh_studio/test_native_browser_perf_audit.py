"""Adversarial synthetic R2.7.22 report tests, NOT actual host measurements."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
import unittest

from tools.mesh_studio.native_browser_perf_audit import (
    SCHEMA, audit_original_browser_measurements,
)
from tools.mesh_studio.native_scene_perf_budget import calculate_native_transfer_budget
from tools.mesh_studio.test_native_scene_perf_budget import synthetic_budget_source
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def mocked_hosted_receipt():
    source=synthetic_budget_source()
    payload=json.dumps(source,sort_keys=True).encode()
    budget=calculate_native_transfer_budget(source,payload)
    modeled={}
    for scene in source["scenes"]:
        name=scene["model"]
        modeled[name]={
            "original_native_accepted_step":1,
            "original_native_source_sha256":scene["source_ndjson_sha256"],
            "real_original_accepted_faces":scene["native_tri_faces"],
            "original_source_patches":len(scene["source_patch_face_counts"]),
            "original_accepted_seam_edges":budget["models"][name][
                "verified_seam_segments"],
            "model_select_to_two_raf_ready_ms":28.0,
            "patches":{
                "samples":10,"minimum_ms":8.0,"median_ms":8.0,
                "p95_ms":8.0,"maximum_ms":8.0,"observed_ms":[8.0]*10,
            },
            "source_samples":{
                "samples":6,"minimum_ms":5.0,"median_ms":5.0,
                "p95_ms":5.0,"maximum_ms":5.0,"observed_ms":[5.0]*6,
            },
            "final_xyz_vtk_cpu_calls":{
                "vtk_setup_cpu_ms":12.0,"vtk_render_call_cpu_ms":3.0,
                "vtk_seam_overlay_cpu_ms":2.0,
                "typed_cpu_buffer_bytes":scene["native_tri_faces"]*56,
            },
            "final_local_uv_vtk_cpu_calls":{
                "vtk_setup_cpu_ms":2.0,"vtk_render_call_cpu_ms":1.0,
                "vtk_seam_overlay_cpu_ms":1.0,
                "typed_cpu_buffer_bytes":scene["source_patch_face_counts"][1]*56,
            },
            "physical_gpu_present_time_measured":False,
        }
    memory={
        "js_heap_used_bytes":1234567,"js_heap_total_bytes":3456789,
        "dom_nodes":456,"dom_documents":1,"layout_count":8,
    }
    report={
        "schema":SCHEMA,
        "source_kind":"SAME_RUN_COMPILED_ORIGINAL_ACCEPTED_NATIVE_TRI_SCENE",
        "workflow_sha":os.getenv("GITHUB_SHA"),
        "hosted_runner_scope":"ubuntu-24.04 GitHub-hosted Chromium; hardware not qualified",
        "source_browser_user_agent":"HeadlessChrome synthetic CONTRACT ONLY",
        "physical_windows_gpu_present_rss_vram_qualified":False,
        "scientific_lod_qualified":False,
        "original_scene_json_sha256":hashlib.sha256(payload).hexdigest(),
        "original_scene_json_bytes":len(payload),
        "original_import_to_two_raf_ready_ms":30.0,
        "imported_original_cpu":{
            "json_bytes":len(payload),"file_read_ms":2.0,
            "contract_ms":8.0,"verified_real_seam_edges_ms":2.0,
            "pre_react_ms":12.0,
        },
        "memory_before_original_import":memory,
        "memory_after_original_import":memory,
        "memory_after_interactions":memory,
        "real_original_sources":modeled,
    }
    return report,budget,payload


class OriginalBrowserPerformanceAuditContract(unittest.TestCase):
    def test_original_source_shaped_hosted_report_requires_explicit_gpu_exclusions(self):
        result=audit_original_browser_measurements(*mocked_hosted_receipt())
        self.assertEqual(set(result["real_original_models"]),{"eistute","book"})
        self.assertFalse(result["actual_gpu_present_measured"])
        self.assertFalse(result["actual_vram_measured"])
        self.assertEqual(result["real_original_models"]["book"][
            "hosted_patch_selection"]["samples"],10)

    def test_altered_exact_source_byte_digest_rejected(self):
        args=list(mocked_hosted_receipt())
        args[0]["original_scene_json_sha256"]="b"*64
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2722_hosted_browser_source_sha"):
            audit_original_browser_measurements(*args)

    def test_fake_physical_gpu_qualification_rejected(self):
        args=list(mocked_hosted_receipt())
        args[0]["physical_windows_gpu_present_rss_vram_qualified"]=True
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2722_browser_scope"):
            audit_original_browser_measurements(*args)

    def test_missing_book_real_source_rejected(self):
        args=list(mocked_hosted_receipt())
        del args[0]["real_original_sources"]["book"]
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2722_real_eistute_book"):
            audit_original_browser_measurements(*args)

    def test_forged_percentile_must_not_pass(self):
        args=list(mocked_hosted_receipt())
        args[0]["real_original_sources"]["eistute"]["patches"]["p95_ms"]=1.0
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2722_reported_percentile"):
            audit_original_browser_measurements(*args)

    def test_browser_original_node_buffer_count_must_match_real_faces(self):
        args=list(mocked_hosted_receipt())
        args[0]["real_original_sources"]["book"][
            "final_xyz_vtk_cpu_calls"]["typed_cpu_buffer_bytes"]=0
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2722_original_native_vtk"):
            audit_original_browser_measurements(*args)

    def test_null_heap_is_not_measured_memory(self):
        args=list(mocked_hosted_receipt())
        args[0]["memory_after_interactions"]["js_heap_used_bytes"]=None
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2722_browser_cdp_js_heap"):
            audit_original_browser_measurements(*args)

    def test_forged_lod_admission_rejected(self):
        args=list(mocked_hosted_receipt())
        args[0]["scientific_lod_qualified"]=True
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2722_browser_scope"):
            audit_original_browser_measurements(*args)

    def test_source_native_epoch_swap_rejected(self):
        args=list(mocked_hosted_receipt())
        args[0]["real_original_sources"]["book"]["original_native_accepted_step"]=2
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2722_original_browser_model_source"):
            audit_original_browser_measurements(*args)


if __name__=="__main__":
    unittest.main()
