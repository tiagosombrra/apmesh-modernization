"""Synthetic negative contracts for R2.7.29; never original C++ mesh evidence."""

from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path
import tempfile
import unittest

from tools.mesh_studio.native_transition_classifier_semantics import (
    REQUIRED, SOURCE_PINS, analyze_pair, inspect_csv, source_attestation,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


ROOT = Path(__file__).resolve().parents[2]
COLUMNS = sorted(REQUIRED)


def synthetic_record() -> dict:
    """Build a fake single local observation for testing a numeric contract."""
    return {
        "step": 4, "retry": 1, "patch_id": 0,
        "local_regen_attempt": 1,
        "generated_faces": 10, "boundary_elements": 2,
        "transition_elements": 5, "interior_elements": 3,
        "boundary_element_ratio": 0.2,
        "transition_element_ratio": 0.1,
        "internal_element_ratio": 0.7,
        "transition_floor": 0.2,
        "transition_underresolved": 1,
        "generation_status": "curve_transition_needs_retry",
    }


def encode(rows: list[dict], columns: list[str] | None = None) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns or COLUMNS,
                            lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


class OriginalNativeTwoTransitionSemanticsContracts(unittest.TestCase):
    def test_exact_source_classification_and_preregistration_are_pinned(self):
        receipts = source_attestation(ROOT)
        self.assertEqual(
            receipts["src/crab_mesh/aft/advancing_front.cpp"]["git_blob"],
            SOURCE_PINS["src/crab_mesh/aft/advancing_front.cpp"])
        self.assertEqual(
            receipts["docs/mesh-studio/R2_7_29_PREREGISTERED_ORIGINAL_AFT_TRANSITION_SEMANTICS_20261119.md"]["git_blob"],
            SOURCE_PINS["docs/mesh-studio/R2_7_29_PREREGISTERED_ORIGINAL_AFT_TRANSITION_SEMANTICS_20261119.md"])

    def test_valid_two_different_classifiers_are_not_forced_equal(self):
        raw = encode([synthetic_record()])
        receipt = inspect_csv(raw)
        self.assertEqual(receipt["raw_source_adapter_csv_sha256"],
                         hashlib.sha256(raw).hexdigest())
        item = receipt["records"][0]
        self.assertAlmostEqual(
            item["aft_stage1_shape_elongation_fraction"], 0.1)
        self.assertAlmostEqual(
            item["regional_spatial_or_shape_transition_fraction"], 0.5)
        self.assertAlmostEqual(
            item["regional_minus_stage1_aft_transition_fraction"], 0.4)
        self.assertTrue(item["original_cpp_underresolved"])
        self.assertTrue(
            item["regional_spatial_or_shape_fraction_reaches_original_floor"])
        self.assertFalse(item["aft_shape_fraction_reaches_original_floor"])

    def test_equal_numeric_fractions_are_permitted_but_not_same_semantics(self):
        sample = synthetic_record()
        sample["transition_elements"] = 1
        sample["interior_elements"] = 7
        receipt = inspect_csv(encode([sample]))
        self.assertAlmostEqual(
            receipt["records"][0]["regional_minus_stage1_aft_transition_fraction"],
            0.0)

    def test_invalid_aft_shape_fraction_partition_rejected(self):
        row = synthetic_record()
        row["internal_element_ratio"] = 0.9
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2729_original_aft_shape_ratio_partition_invalid"):
            inspect_csv(encode([row]))

    def test_regional_face_partition_must_match_generated_geometry(self):
        for amount in (4, -1):
            with self.subTest(value=amount):
                row = synthetic_record()
                row["transition_elements"] = amount
                with self.assertRaisesRegex(
                        NativeLineageValidationError,
                        "r2729_regional_post_smoothing_face_partition_inconsistent"):
                    inspect_csv(encode([row]))

    def test_original_underresolved_flag_uses_aft_not_regional_ratio(self):
        row = synthetic_record()
        row["transition_underresolved"] = 0
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2729_source_underresolved_flag_uses_wrong_classifier"):
            inspect_csv(encode([row]))
        other = synthetic_record()
        other["transition_element_ratio"] = 0.5
        other["internal_element_ratio"] = 0.3
        other["transition_underresolved"] = 1
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2729_source_underresolved_flag_uses_wrong_classifier"):
            inspect_csv(encode([other]))

    def test_nonfinite_aft_or_floor_rejected(self):
        for field in ("internal_element_ratio", "transition_floor"):
            for invalid in ("nan", "inf", "-inf"):
                with self.subTest(field=field, invalid=invalid):
                    row = synthetic_record()
                    row[field] = invalid
                    with self.assertRaisesRegex(
                            NativeLineageValidationError,
                            "r2729_original_aft_shape_ratio_partition_invalid"):
                        inspect_csv(encode([row]))

    def test_unknown_header_or_duplicate_column_rejected(self):
        columns = [x for x in COLUMNS if x != "transition_elements"]
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2729_original_adapter_csv_header_drifted"):
            inspect_csv(encode([synthetic_record()], columns))
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2729_original_adapter_csv_header_drifted"):
            inspect_csv(encode([synthetic_record()], COLUMNS + ["transition_elements"]))

    def test_truncated_windows_newline_and_nul_rejected(self):
        data = encode([synthetic_record()])
        for variant in (data[:-1], data.replace(b"\n", b"\r\n"),
                        data.replace(b"10", b"\x00", 1)):
            with self.subTest(bytes=variant[:15]):
                with self.assertRaisesRegex(
                        NativeLineageValidationError,
                        "r2729_missing_or_noncanonical_raw_original_cpp_csv"):
                    inspect_csv(variant)

    def test_article_and_variant_are_not_pooled_as_two_accepted_epochs(self):
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2729_authentic_r2728_original_cpp_local_count_changed"):
            analyze_pair(encode([synthetic_record()]),
                         encode([synthetic_record()]))

    def test_absent_original_cpp_cannot_be_attested_from_fixture(self):
        with tempfile.TemporaryDirectory(prefix="r2729-synthetic-") as tmp:
            with self.assertRaises(FileNotFoundError):
                source_attestation(Path(tmp))


if __name__ == "__main__":
    unittest.main()
