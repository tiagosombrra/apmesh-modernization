"""Adversarial synthetic-only R2.7.28 original Adapter CSV validation tests."""

from __future__ import annotations

import csv
import io
from pathlib import Path
import tempfile
import unittest

from tools.mesh_studio.native_patch_csv_replay import (
    attest_original_sources, parse_original_patch_csv,
)
from tools.mesh_studio.test_native_acceptance_gate_forensics import row
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError

ROOT = Path(__file__).resolve().parents[2]
FIELDS = [
    "step", "retry", "patch_id", "local_regen_attempt",
    "generation_status", "transition_floor", "transition_underresolved",
    "interior_transition_imbalance", "transition_element_ratio",
    "internal_element_ratio", "generated_faces", "quadtree_leaves",
    "curve_domain_balance",
]


def gates() -> list[dict]:
    """Generate fake gate chronology used only for parser negative tests."""
    return [row(1, True), row(2, False), row(2, False, 1),
            row(3, False), row(3, False, 1), row(4, False),
            row(4, False, 1)]


def fake_rows() -> list[dict]:
    rows = []
    for event in sorted(gates() + [row(1, False, 1)],
                        key=lambda item: (item["step"], item["retry"])):
        for patch in range(4):
            rows.append({
                "step": event["step"],
                "retry": event["retry"],
                "patch_id": patch,
                "local_regen_attempt": 0,
                "generation_status": "curve_transition_needs_retry",
                "transition_floor": 0.10,
                "transition_underresolved": 1,
                "interior_transition_imbalance": 0.105,
                "transition_element_ratio": 0.02,
                "internal_element_ratio": 0.70,
                "generated_faces": 50,
                "quadtree_leaves": 11,
                "curve_domain_balance": 0.8,
            })
    return rows


def fake_events(extra: list[dict] | None = None) -> list[dict]:
    """Construct synthetic local witnesses, including ungated Adapter scope."""
    return [{
        "adaptive_step": int(record["step"]),
        "retry_index": int(record["retry"]),
        "patch_index": int(record["patch_id"]),
        "local_attempt": int(record["local_regen_attempt"]),
    } for record in (fake_rows() + (extra or []))]


def encode(rows: list[dict], columns: list[str] | None = None) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns or FIELDS,
                            lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


class OriginalAdapterPatchCsvContracts(unittest.TestCase):
    def test_source_cpp_and_preregistered_csv_path_attested(self):
        evidence = attest_original_sources(ROOT)
        self.assertIn("src/adapter/adapter.cpp", evidence)
        self.assertIn(
            "docs/mesh-studio/R2_7_28_PREREGISTERED_EXISTING_ADAPTER_PATCH_CSV_20261119.md",
            evidence)

    def test_genuine_shape_synthetic_eistute_candidate_inventory(self):
        result = parse_original_patch_csv(encode(fake_rows()), gates(), fake_events())
        self.assertEqual(result["native_local_patch_attempt_rows"], 32)
        self.assertEqual(len(result["step4_local_candidate_sets_by_patch"]), 8)\n        self.assertEqual(result["real_original_adapter_outer_attempt_scopes"], 8)\n        self.assertEqual(result["original_adapter_only_outer_scopes_not_global_gate"], [[1, 1]])
        self.assertTrue(all(
            v["all_recorded_local_attempts_underresolved"]
            for v in result["step4_local_candidate_sets_by_patch"]))
        self.assertEqual(result["n_rounding_ambiguous_strict_conditions"], 0)
        self.assertTrue(result["local_attempts_not_assumed_selected"])
        self.assertFalse(result["scientific_lod_qualified"])

    def test_local_fallback_is_not_conflated_with_selected_candidate(self):
        rows = fake_rows()
        trial = rows[-1].copy()
        trial.update({
            "local_regen_attempt": 1,
            "transition_floor": 0.10,
            "transition_underresolved": 0,
            "interior_transition_imbalance": 0.0,
            "transition_element_ratio": 0.20,
            "internal_element_ratio": 0.50,
        })
        rows.append(trial)
        result = parse_original_patch_csv(encode(rows), gates(), fake_events([trial]))
        self.assertFalse(
            result["step4_local_candidate_sets_by_patch"][-1][
                "all_recorded_local_attempts_underresolved"])
        self.assertEqual(
            len(result["step4_local_candidate_sets_by_patch"][-1][
                "local_attempts"]), 2)

    def test_duplicate_local_identity_rejected(self):
        rows = fake_rows()
        rows.append(rows[0].copy())
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2728_original_adapter_csv_wrong_outer_or_duplicate"):
            parse_original_patch_csv(encode(rows), gates(), fake_events())

    def test_missing_patch_scope_rejected(self):
        rows = fake_rows()
        rows.pop()
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2728_original_adapter_missing_patch"):
            parse_original_patch_csv(encode(rows), gates(), fake_events())

    def test_missing_attempt_zero_rejected(self):
        rows = fake_rows()
        rows[-1]["local_regen_attempt"] = 1
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2728_original_adapter_missing_patch"):
            parse_original_patch_csv(encode(rows), gates(), fake_events([rows[-1]]))

    def test_noncontiguous_local_indices_rejected(self):
        rows = fake_rows()
        added = rows[-1].copy()
        added["local_regen_attempt"] = 2
        rows.append(added)
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2728_original_adapter_missing_patch"):
            parse_original_patch_csv(encode(rows), gates(), fake_events([added]))

    def test_forged_boolean_transition_flag_rejected(self):
        rows = fake_rows()
        rows[2]["transition_underresolved"] = 0
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2728_original_cpp_transition_underresolved_formula_forged"):
            parse_original_patch_csv(encode(rows), gates(), fake_events())

    def test_forged_interior_imbalance_rejected(self):
        rows = fake_rows()
        rows[3]["interior_transition_imbalance"] = 0.9
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2728_original_cpp_interior_transition_imbalance_forged"):
            parse_original_patch_csv(encode(rows), gates(), fake_events())

    def test_nonfinite_metrics_rejected(self):
        for value in ("nan", "inf", "-inf"):
            with self.subTest(value=value):
                rows = fake_rows()
                rows[0]["transition_floor"] = value
                with self.assertRaisesRegex(
                        NativeLineageValidationError,
                        "r2728_original_adapter_csv_nonfinite"):
                    parse_original_patch_csv(encode(rows), gates(), fake_events())

    def test_missing_required_header_rejected(self):
        columns = [s for s in FIELDS if s != "transition_underresolved"]
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2728_original_adapter_csv_missing_or_duplicate_headers"):
            parse_original_patch_csv(encode(fake_rows(), columns), gates(), fake_events())

    def test_duplicate_header_rejected(self):
        raw = encode(fake_rows())
        corrupted = raw.replace(
            b"internal_element_ratio,generated_faces",
            b"internal_element_ratio,internal_element_ratio,generated_faces")
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2728_original_adapter_csv_missing_or_duplicate_headers"):
            parse_original_patch_csv(corrupted, gates(), fake_events())

    def test_truncated_or_windows_newline_rejected(self):
        raw = encode(fake_rows())
        for corrupted in (raw.rstrip(b"\n"), raw.replace(b"\n", b"\r\n")):
            with self.subTest(kind=corrupted[:20]):
                with self.assertRaisesRegex(
                        NativeLineageValidationError,
                        "r2728_missing_oversized_or_noncanonical_native_patch_csv"):
                    parse_original_patch_csv(corrupted, gates(), fake_events())

    def test_different_actual_native_cpp_gate_chronology_rejected(self):
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2728_not_original_seven_eistute_cpp_gate_attempts"):
            parse_original_patch_csv(encode(fake_rows()), gates()[:-1], fake_events())

    def test_no_source_fake_directory_can_pass_attestation(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                attest_original_sources(Path(tmp))


if __name__ == "__main__":
    unittest.main()
