"""Hermetic controls plus optional original-byte-pinned OCCT STEP integration."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

import tsh249_native_occt_sewing_gate as gate


class SourceAndNativeControls(unittest.TestCase):
    def test_corrupt_source_bytes_are_rejected_before_import(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            gate.verify_pinned_step(b"ISO-10303-21;\nEND-ISO-10303-21;\n")

    def test_source_face_centroids_have_unique_identity(self):
        for index, point in enumerate(gate.EXPECTED_CENTERS):
            self.assertEqual(gate.classify_centroid(point), index)
        with self.assertRaisesRegex(ValueError, "uniquely mapped"):
            gate.classify_centroid((999, 999, 999))

    def test_axis_section_is_orientation_independent(self):
        v1, v2 = ((4., 0., 0.), (6., 0., 0.))
        self.assertEqual(gate.edge_interval_on_source_axis((v1, v2)), (4., 6.))
        self.assertEqual(gate.edge_interval_on_source_axis((v2, v1)), (4., 6.))

    def test_claimed_shared_noncollinear_edge_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "X axis"):
            gate.edge_interval_on_source_axis(((4., 0., 0.), (6., 1., 0.)))

    def test_degenerate_source_edge_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Zero-length"):
            gate.edge_interval_on_source_axis(((4., 0., 0.), (4., 0., 0.)))

    def test_triangle_edge_membership_does_not_accept_interior_or_far_point(self):
        a, b = gate.EXPECTED_TRIANGLE_CORNERS[0][:2]
        self.assertTrue(gate.point_on_closed_segment((4., 0., 0.), a, b))
        self.assertFalse(gate.point_on_closed_segment((4., 0.5, 0.), a, b))
        self.assertFalse(gate.point_on_closed_segment((7., 0., 0.), a, b))

    def test_expected_three_way_native_section_and_source_lineage(self):
        three = [{"x_interval": [a, b],
                  "source_face_ids": [gate.SOURCE_FACE_IDS[i] for i in owners],
                  "distinct_native_face_incidence": len(owners)}
                 for (a,b),owners in gate.EXPECTED_SHARED.items()]
        gate.require_shared_sections(three, gate.EXPECTED_SHARED)

    def test_wrong_source_face_owner_in_triple_edge_is_rejected(self):
        three = [{"x_interval": [a,b],
                  "source_face_ids": [gate.SOURCE_FACE_IDS[i] for i in owners],
                  "distinct_native_face_incidence": len(owners)}
                 for (a,b),owners in gate.EXPECTED_SHARED.items()]
        three[1]["source_face_ids"] = [27, 55]
        with self.assertRaisesRegex(ValueError, "unexpected source face owners"):
            gate.require_shared_sections(three, gate.EXPECTED_SHARED)

    def test_two_face_sections_cannot_substitute_for_triple(self):
        conventional = [{"x_interval": [a,b],
                         "source_face_ids": [27,55] if a <= 4 else [55,83],
                         "distinct_native_face_incidence": 2}
                        for (a,b) in gate.EXPECTED_SHARED]
        with self.assertRaisesRegex(ValueError, "unexpected source face owners"):
            gate.require_shared_sections(conventional, gate.EXPECTED_SHARED)

    def test_missing_step_cli_returns_blocked_without_receipt(self):
        with TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, str(Path(gate.__file__)),
                "--original-step", str(Path(tmp)/"missing.stp"),
                "--receipt", str(Path(tmp)/"result.json")],
                capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 3)
            self.assertFalse((Path(tmp)/"result.json").exists())
            self.assertEqual(json.loads(result.stderr)["classification"],
                             "BLOCKED_NO_NATIVE_RECONSTRUCTION_CLAIM")

    def test_existing_receipt_cli_is_not_overwritten(self):
        with TemporaryDirectory() as tmp:
            target=Path(tmp)/"result.json"
            target.write_text("immutable old trial\n")
            result = subprocess.run([sys.executable, str(Path(gate.__file__)),
                "--original-step", str(Path(tmp)/"missing.stp"),
                "--receipt", str(target)],
                capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 3)
            self.assertEqual(target.read_text(), "immutable old trial\n")

    @unittest.skipUnless(os.environ.get("APMESH_TSH249_ORIGINAL_STEP"),
                         "Set APMESH_TSH249_ORIGINAL_STEP for original pinned integration")
    def test_authentic_pinned_original_step_and_occt_sewing(self):
        path = Path(os.environ["APMESH_TSH249_ORIGINAL_STEP"])
        receipt = gate.run_original_native_reconstruction(path)
        self.assertEqual(receipt["source"]["git_blob_sha1"], gate.SOURCE_GIT_BLOB_SHA1)
        self.assertEqual(receipt["before_native_sewing"]["edge_face_incidence_histogram"], {"1": 9})
        self.assertEqual(receipt["after_conventional_sewing"]["edge_face_incidence_histogram"],
                         {"1": 9, "2": 3})
        self.assertEqual(receipt["after_nonmanifold_sewing"]["edge_face_incidence_histogram"],
                         {"1": 8, "2": 2, "3": 1})
        self.assertEqual(receipt["after_nonmanifold_sewing"]["occt_multiple_edge_counter"], 1)
        self.assertFalse(receipt["apmesh_cpp_tri_quad_executed"])

    @unittest.skipUnless(os.environ.get("APMESH_TSH249_ORIGINAL_STEP"),
                         "Set APMESH_TSH249_ORIGINAL_STEP for original pinned integration")
    def test_authentic_original_step_tampering_blocked(self):
        content = bytearray(Path(os.environ["APMESH_TSH249_ORIGINAL_STEP"]).read_bytes())
        content[0] ^= 1
        with TemporaryDirectory() as tmp:
            target = Path(tmp)/"mutated.stp"
            target.write_bytes(content)
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                gate.run_original_native_reconstruction(target)


if __name__ == "__main__":
    unittest.main()
