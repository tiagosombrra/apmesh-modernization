"""R2.7.20 parser negative controls are synthetic, not original native results."""

from __future__ import annotations

from copy import deepcopy
import unittest

from tools.mesh_studio.native_accepted_scene import project_accepted_faces
from tools.mesh_studio.test_verify_native_lineage import synthetic_receipt
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


class TestAcceptedNativeSceneProjection(unittest.TestCase):
    def test_original_per_patch_face_identity_survives_projection(self):
        for model, patches in (("eistute", 4), ("book", 28)):
            with self.subTest(model=model):
                scene = project_accepted_faces(
                    synthetic_receipt(model), model, "a" * 64)
                self.assertEqual(scene["native_tri_faces"], patches)
                self.assertEqual(scene["source_patch_face_counts"], [1] * patches)
                self.assertEqual(len(scene["native_faces"]), patches)
                for slot, face in enumerate(scene["native_faces"]):
                    self.assertEqual(face[:4], [slot, 0, 0, slot + 11])
                    self.assertEqual(len(face[4]), 3)
                    self.assertEqual(face[4][0][0], slot * 3 + 1)
                    self.assertEqual(face[4][0][1:4], [float(slot), 0.0, 0.0])
                    self.assertEqual(face[4][0][4:], [0.0, 0.0])
                self.assertTrue(scene["patch_local_points_not_globally_welded"])
                self.assertFalse(scene["scientific_lod_qualified"])
                self.assertFalse(scene["cross_epoch_lineage_certified"])

    def test_native_node_id_over_javascript_safe_integer_is_rejected(self):
        sample = synthetic_receipt()
        sample[2]["vertices"][0]["native_node_id"] = 2**53 + 10
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2720_original_native_node_id"):
            project_accepted_faces(sample, "eistute", "a" * 64)

    def test_native_element_id_over_javascript_safe_integer_is_rejected(self):
        sample = synthetic_receipt()
        sample[2]["native_element_id"] = 2**53 + 10
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2720_original_native_face_id"):
            project_accepted_faces(sample, "eistute", "a" * 64)

    def test_original_face_owner_mismatch_is_rejected(self):
        sample = synthetic_receipt()
        sample[2]["native_patch_id"] = 888
        with self.assertRaises(NativeLineageValidationError):
            project_accepted_faces(sample, "eistute", "a" * 64)

    def test_duplicate_original_element_slot_is_rejected(self):
        sample = synthetic_receipt()
        sample.insert(3, deepcopy(sample[2]))
        with self.assertRaises(NativeLineageValidationError):
            project_accepted_faces(sample, "eistute", "a" * 64)

    def test_forged_accepted_source_scope_is_rejected(self):
        sample = synthetic_receipt()
        sample[0]["scientific_lod_admitted"] = True
        with self.assertRaises(NativeLineageValidationError):
            project_accepted_faces(sample, "eistute", "a" * 64)

    def test_missing_original_source_patch_rejected(self):
        sample = synthetic_receipt()
        sample.pop(-3)
        with self.assertRaises(NativeLineageValidationError):
            project_accepted_faces(sample, "eistute", "a" * 64)

    def test_invalid_original_xyz_does_not_enter_render_bundle(self):
        sample = synthetic_receipt()
        sample[2]["vertices"][0]["xyz"][1] = float("nan")
        with self.assertRaises(NativeLineageValidationError):
            project_accepted_faces(sample, "eistute", "a" * 64)


if __name__ == "__main__":
    unittest.main()
