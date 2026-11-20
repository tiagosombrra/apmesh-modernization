"""R2.7.21 synthetic seam-edge negative tests are not C++ research evidence."""

from __future__ import annotations

from copy import deepcopy
import unittest

from tools.mesh_studio.native_seam_edges import audit_actual_seam_edges
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def synthetic_original_edge_bundle():
    """Create mock original patch-local triangles without welding node IDs."""
    scenes, documents = [], []
    for model, count in (("eistute", 4), ("book", 28)):
        faces = []
        for patch in range(count):
            faces.append([
                patch, 400 + patch, 0, 500 + patch,
                [[1000 + patch, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [2000, 0.0, 1.0, 0.0, 0.0, 1.0],
                 [3000 + patch, 1.0, 0.0, float(patch), 1.0, 0.0]],
            ])
        groups = []
        for ordinal in range(2):
            groups.append({"members": [{
                "patch_slot": patch,
                "native_node_id": 1000 + patch if ordinal == 0 else 2000,
                "original_xyz": [0.0, float(ordinal), 0.0],
            } for patch in range(count)]})
        scenes.append({
            "model": model, "accepted_native_step": 1,
            "source_ndjson_sha256": "a" * 64,
            "native_tri_faces": count,
            "native_faces": faces,
        })
        documents.append({
            "model": model, "accepted_native_step": 1,
            "source_ndjson_sha256": "a" * 64,
            "qualified_shared_source_curves": [{
                "source_curve_slot": 3, "native_curve_id": 7,
                "patch_slots": list(range(count)),
                "sample_count": 2, "sample_groups": groups,
            }],
        })
    return {"identity": {"documents": documents}, "scenes": scenes}


class ActualNativeSeamEdgeContracts(unittest.TestCase):
    def test_all_original_patch_local_native_tri_edges_are_required(self):
        result = audit_actual_seam_edges(synthetic_original_edge_bundle())
        self.assertEqual(result["schema"],
                         "apmesh.meshstudio.r2721.original_native_patch_seam_edges.v1")
        self.assertEqual(result["original_models"]["eistute"][
            "total_qualified_patch_local_edges"], 4)
        self.assertEqual(result["original_models"]["book"][
            "total_qualified_patch_local_edges"], 28)
        self.assertFalse(result["cross_patch_welding_certified"])

    def test_missing_real_triangle_edge_rejected_even_with_two_source_nodes(self):
        source = synthetic_original_edge_bundle()
        face = source["scenes"][0]["native_faces"][0]
        # Both source samples remain in accepted triangles, but the true
        # edge (1000,2000) no longer appears as one native TRI edge.
        face[4][1] = [4000, 0.5, 0.0, 0.0, 0.5, 0.0]
        source["scenes"][0]["native_faces"].append([
            0, 400, 1, 999,
            [[2000, 0, 1, 0, 0, 1],
             [4010, 1, 1, 0, 1, 1],
             [4020, 1, 0.7, 0, 1, 0.7]],
        ])
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2721_source_sample_segment_is_not"):
            audit_actual_seam_edges(source)

    def test_source_and_original_native_face_xyz_mismatch_rejected(self):
        source = synthetic_original_edge_bundle()
        source["identity"]["documents"][1][
            "qualified_shared_source_curves"][0][
                "sample_groups"][0]["members"][0]["original_xyz"] = [3, 0, 0]
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2721_original_source_sample_native_face"):
            audit_actual_seam_edges(source)

    def test_conflicting_native_id_coordinate_inside_patch_is_rejected(self):
        source = synthetic_original_edge_bundle()
        source["scenes"][0]["native_faces"].append([
            0, 400, 1, 888,
            [[1000, 1, 0, 0, 0, 0],
             [5010, 1, 1, 0, 1, 1],
             [5020, 0, 1, 0, 0, 1]],
        ])
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2721_original_patch_native_node_xyz"):
            audit_actual_seam_edges(source)

    def test_incomplete_28_patch_sample_fan_rejected(self):
        source = synthetic_original_edge_bundle()
        source["identity"]["documents"][1][
            "qualified_shared_source_curves"][0][
                "sample_groups"][0]["members"].pop()
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2721_original_source_incidence_incomplete"):
            audit_actual_seam_edges(source)

    def test_forged_original_native_source_digest_rejected(self):
        source = synthetic_original_edge_bundle()
        source["scenes"][1]["source_ndjson_sha256"] = "b" * 64
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2721_source_scene_digest"):
            audit_actual_seam_edges(source)


if __name__ == "__main__":
    unittest.main()
