"""Synthetic R2.7.22 transport-budget controls, never actual GPU evidence."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.mesh_studio.native_scene_perf_budget import (
    SCHEMA, calculate_native_transfer_budget,
    XYZ_BYTES_PER_TRI, VTK_LINE_BYTES_PER_SEGMENT,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def synthetic_budget_source():
    """Use source-shaped counters, not fabricated physical native geometry."""
    docs=[]
    scenes=[]
    for model,tri,patches,samples in (
        ("eistute",1168,4,11),("book",4256,28,13)
    ):
        counts=[tri//patches]*patches
        docs.append({
            "model":model,"accepted_native_step":1,
            "source_ndjson_sha256":"a"*64,
            "qualified_shared_source_curves":[{
                "patch_slots":list(range(patches)),
                "sample_count":samples,
            }],
        })
        scenes.append({
            "model":model,"accepted_native_step":1,
            "source_ndjson_sha256":"a"*64,
            "scientific_lod_qualified":False,
            "patch_local_points_not_globally_welded":True,
            "native_tri_faces":tri,
            "source_patch_face_counts":counts,
            "native_faces":[None]*tri,
        })
    return {
        "schema":"apmesh.meshstudio.r2720.original_accepted_tri_scene.v1",
        "no_implicit_node_welding":True,
        "scientific_lod_qualified":False,
        "identity":{"documents":docs},"scenes":scenes,
    }


class NativeVisualBudgetContracts(unittest.TestCase):
    def test_original_count_contract_predicts_only_explicit_array_bytes(self):
        source=synthetic_budget_source()
        result=calculate_native_transfer_budget(source,b"synthetic native counts only")
        self.assertEqual(result["schema"],SCHEMA)
        self.assertEqual(result["models"]["eistute"][
            "xyz_display_typed_arrays_bytes"],1168*XYZ_BYTES_PER_TRI)
        self.assertEqual(result["models"]["book"][
            "xyz_display_typed_arrays_bytes"],4256*XYZ_BYTES_PER_TRI)
        self.assertEqual(result["models"]["book"][
            "all_source_seam_line_arrays_bytes"],336*VTK_LINE_BYTES_PER_SEGMENT)
        self.assertFalse(result["physical_windows_gpu_rss_vram_gate_qualified"])
        self.assertFalse(result["models"]["book"]["actual_render_to_present_measured"])

    def test_missing_original_accepted_patch_counts_refused(self):
        source=synthetic_budget_source()
        source["scenes"][1]["source_patch_face_counts"].pop()
        with self.assertRaises(NativeLineageValidationError):
            calculate_native_transfer_budget(source,b"synthetic")

    def test_misreported_original_face_total_refused(self):
        source=synthetic_budget_source()
        source["scenes"][0]["native_tri_faces"]+=1
        with self.assertRaises(NativeLineageValidationError):
            calculate_native_transfer_budget(source,b"synthetic")

    def test_forged_source_curve_samples_refused(self):
        source=synthetic_budget_source()
        source["identity"]["documents"][1][
            "qualified_shared_source_curves"][0]["sample_count"]=12
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2722_source_seam_edge_inventory_changed"):
            calculate_native_transfer_budget(source,b"synthetic")

    def test_cross_source_sha_join_refused(self):
        source=synthetic_budget_source()
        source["scenes"][0]["source_ndjson_sha256"]="b"*64
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2722_original_source_digest_mismatch"):
            calculate_native_transfer_budget(source,b"synthetic")

    def test_source_welding_claim_refused(self):
        source=synthetic_budget_source()
        source["no_implicit_node_welding"]=False
        with self.assertRaises(NativeLineageValidationError):
            calculate_native_transfer_budget(source,b"synthetic")

    def test_json_size_above_original_source_bound_refused(self):
        source=synthetic_budget_source()
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2722_unqualified_native_scene_or_unbounded_json"):
            calculate_native_transfer_budget(source,b"x"*9_000_001)


if __name__=="__main__":
    unittest.main()
