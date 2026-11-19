"""R2.7.32 synthetic-only provenance and UV negative contracts (NOT Eistute)."""

from __future__ import annotations

from pathlib import Path
import unittest

from tools.mesh_studio.native_selected_uv_geometry import (
    attest_source,
    correlate_original_selected_pre_aft_uv,
    parse_original_native_uv_captures,
)
from tools.mesh_studio.test_native_local_selection_provenance import (
    fake_complete_cpp_and_csv,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError

ROOT = Path(__file__).resolve().parents[2]


def fake_cpp_uv_with_selections(role="original", unsupported=()):
    """Generate artificial one-to-one UV and Adapter local records."""
    selection, csv = fake_complete_cpp_and_csv(role)
    captures = []
    for line in selection.decode().splitlines():
        tokens = {}
        for bit in line.split("=", 1)[1].split(","):
            key, val = bit.split("=", 1)
            tokens[key] = val
        ordinal = int(tokens["ordinal"])
        fields = (
            f"ordinal={ordinal},outer_epoch={tokens['outer_epoch']},"
            f"outer_retry={tokens['outer_retry']},step={tokens['step']},"
            f"retry={tokens['retry']},patch={tokens['patch']},"
            f"local={tokens['local']}"
        )
        if ordinal in unsupported:
            fields += (
                ",status=unsupported,leaves=5,excluded=0,vertices=0,"
                "polygons=0,area=0,u_min=0,v_min=0,u_max=0,v_max=0,"
                "pattern=0,pattern=0,pattern=0,pattern=0,pattern=0,pattern=0"
            )
        else:
            fields += (
                ",status=qualified,leaves=5,excluded=1,vertices=6,"
                "polygons=2,area=0.45,u_min=0.1,v_min=0.2,"
                "u_max=0.9,v_max=0.8,"
                "pattern=1,pattern=1,pattern=0,pattern=0,pattern=0,pattern=0"
            )
        captures.append("R2732_UV_CAPTURE=" + fields)
    return ("\n".join(captures) + "\n" + selection.decode()).encode(), csv


class PreAftSourceUvNegativeTests(unittest.TestCase):
    def test_original_cpp_and_pre_registered_observer_are_immutable(self):
        receipt = attest_source(ROOT)
        self.assertIn("research/quad/adapter_capture.h", receipt)

    def test_positive_synthetic_all_eistute_original_selected_uv(self):
        stdout, csv = fake_cpp_uv_with_selections()
        audit = correlate_original_selected_pre_aft_uv(
            stdout, csv, "original")
        self.assertEqual(audit["original_cpp_all_local_attempts"], 104)
        self.assertEqual(audit["selected_local_pre_aft_uv_step4"], 16)
        self.assertEqual(audit["pre_aft_uv_qualified_selected_step4"], 16)
        self.assertFalse(audit["selected_source_tri_face_geometry_observed"])
        self.assertFalse(audit["scientific_lod_qualified"])

    def test_positive_synthetic_variant_keeps_separate_process(self):
        stdout, csv = fake_cpp_uv_with_selections("variant")
        audit = correlate_original_selected_pre_aft_uv(
            stdout, csv, "variant")
        self.assertEqual(audit["original_cpp_all_local_attempts"], 112)
        self.assertEqual(audit["selected_local_pre_aft_uv_step4"], 16)

    def test_rejected_source_tree_is_labeled_unsupported_not_tri(self):
        stdout, csv = fake_cpp_uv_with_selections(unsupported={1, 2, 3})
        audit = correlate_original_selected_pre_aft_uv(stdout, csv, "original")
        self.assertEqual(audit["pre_aft_uv_unsupported_all_attempts"], 3)
        self.assertFalse(audit["selected_source_tri_face_geometry_observed"])

    def test_dropped_uv_capture_is_rejected(self):
        stdout, csv = fake_cpp_uv_with_selections()
        lines = stdout.splitlines()
        lines.pop(0)
        with self.assertRaises(NativeLineageValidationError):
            correlate_original_selected_pre_aft_uv(
                b"\n".join(lines) + b"\n", csv, "original")

    def test_wrong_source_local_patch_join_is_rejected(self):
        stdout, csv = fake_cpp_uv_with_selections()
        corrupted = stdout.replace(
            b"step=1,retry=0,patch=0,local=0,status=qualified",
            b"step=1,retry=0,patch=1,local=0,status=qualified", 1)
        with self.assertRaises(NativeLineageValidationError):
            correlate_original_selected_pre_aft_uv(
                corrupted, csv, "original")

    def test_extra_original_uv_capture_is_rejected(self):
        stdout, _ = fake_cpp_uv_with_selections()
        capture = next(l for l in stdout.splitlines()
                       if l.startswith(b"R2732_UV_CAPTURE="))
        with self.assertRaises(NativeLineageValidationError):
            parse_original_native_uv_captures(
                stdout + capture + b"\n")

    def test_nonfinite_source_uv_bbox_is_rejected(self):
        stdout, _ = fake_cpp_uv_with_selections()
        with self.assertRaises(NativeLineageValidationError):
            parse_original_native_uv_captures(
                stdout.replace(b"u_min=0.1", b"u_min=nan", 1))

    def test_bad_pattern_partition_is_rejected(self):
        stdout, _ = fake_cpp_uv_with_selections()
        with self.assertRaises(NativeLineageValidationError):
            parse_original_native_uv_captures(
                stdout.replace(b"pattern=1,pattern=1,pattern=0",
                               b"pattern=1,pattern=0,pattern=0", 1))

    def test_nonzero_fake_geometry_on_unsupported_tree_rejected(self):
        stdout, _ = fake_cpp_uv_with_selections(unsupported={1})
        with self.assertRaises(NativeLineageValidationError):
            parse_original_native_uv_captures(
                stdout.replace(b"status=unsupported,leaves=5,excluded=0",
                               b"status=unsupported,leaves=5,excluded=1", 1))

    def test_ambiguous_uv_capture_ordinal_rejected(self):
        stdout, _ = fake_cpp_uv_with_selections()
        with self.assertRaises(NativeLineageValidationError):
            parse_original_native_uv_captures(
                stdout.replace(b"R2732_UV_CAPTURE=ordinal=2,",
                               b"R2732_UV_CAPTURE=ordinal=1,", 1))

    def test_false_triangle_evidence_label_is_rejected(self):
        stdout, _ = fake_cpp_uv_with_selections()
        with self.assertRaises(NativeLineageValidationError):
            parse_original_native_uv_captures(
                stdout.replace(b"status=qualified", b"status=selected_tri", 1))


if __name__ == "__main__":
    unittest.main()
