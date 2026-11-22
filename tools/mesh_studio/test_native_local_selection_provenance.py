"""Adversarial synthetic-only tests for source-authenticated local selection events."""

from __future__ import annotations

import csv
import io
from pathlib import Path
import tempfile
import unittest

from tools.mesh_studio.native_local_selection_provenance import (
    attest_original_selection_source,
    join_selected_local_to_native_csv,
    parse_native_local_selection,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError

ROOT = Path(__file__).resolve().parents[2]

FIELDS = (
    "step,retry,patch_id,local_regen_attempt,generated_faces,"
    "boundary_elements,transition_elements,interior_elements,"
    "boundary_element_ratio,transition_element_ratio,internal_element_ratio,"
    "transition_floor,transition_underresolved,generation_status"
).split(",")


def fake_complete_cpp_and_csv(role: str = "original"):
    """Mimic verified original 40-invocation shape; not native article data."""
    assert role in ("original", "variant")
    csv_data = io.StringIO(newline="")
    writer = csv.DictWriter(csv_data, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    events = []
    group_number = 0
    epoch = 0
    def emit(step: int, retry: int, patch: int, local_count: int) -> None:
        nonlocal epoch, group_number
        group_number += 1
        epoch += 1
        for local in range(local_count):
            writer.writerow({
                "step": step, "retry": retry, "patch_id": patch,
                "local_regen_attempt": local,
                "generated_faces": 10, "boundary_elements": 2,
                "transition_elements": 5, "interior_elements": 3,
                "boundary_element_ratio": 0.2,
                "transition_element_ratio": 0.1,
                "internal_element_ratio": 0.7,
                "transition_floor": 0.2,
                "transition_underresolved": 1,
                "generation_status": "curve_transition_needs_retry",
            })
            kind = "selected" if local == local_count - 1 else "superseded"
            events.append(
                f"R2730_LOCAL_SELECTION=ordinal={len(events)+1},session=6306001,"
                f"outer_epoch={epoch},outer_retry=0,step={step},retry={retry},"
                f"patch={patch},local={local},kind={kind},"
                f"status=curve_transition_needs_retry\n")
    for patch in range(4):
        for retry in (0, 1):
            emit(1, retry, patch, 3)
    for step in (2, 3):
        for retry in (0, 1):
            for patch in range(4):
                emit(step, retry, patch,
                     2 if step == 3 and role == "variant" else 1)
    for patch in range(4):
        emit(4, 0, patch, 4)
    for patch in range(4):
        for _ in range(3):
            emit(4, 1, patch, 4)
    return "".join(events).encode(), csv_data.getvalue().encode()


class OriginalCxxLocalSelectionContracts(unittest.TestCase):
    def test_original_generator_and_research_observer_source_are_pinned(self):
        receipts = attest_original_selection_source(ROOT)
        self.assertIn("research/quad/adapter_capture.h", receipts)
        self.assertIn(
            "docs/mesh-studio/R2_7_30A_ADAPTER_INVOCATION_EPOCH_SCOPE_CLARIFICATION_20261119.md",
            receipts)

    def test_source_native_shape_original_selected_csv_match(self):
        stdout, raw = fake_complete_cpp_and_csv()
        result = join_selected_local_to_native_csv(stdout, raw, "original")
        self.assertEqual(result["original_cpp_selected_adapter_returns"], 40)
        self.assertEqual(result["original_cpp_selected_adapter_returns_at_step4"], 16)
        self.assertEqual(result["original_cpp_all_local_event_rows"], 104)
        self.assertTrue(all(
            x["transition_underresolved"]
            for x in result["selected_local_returns"] if x["step"] == 4))
        self.assertFalse(result["scientific_lod_qualified"])

    def test_variant_has_independent_112_candidates_but_one_source_epoch(self):
        stdout, raw = fake_complete_cpp_and_csv("variant")
        result = join_selected_local_to_native_csv(stdout, raw, "variant")
        self.assertEqual(result["original_cpp_all_local_event_rows"], 112)
        self.assertEqual(result["original_cpp_selected_adapter_returns"], 40)
        self.assertEqual(result["genuine_source_cpp_accepted_steps"], [1])

    def test_outer_global_retry_not_forced_equal_to_local_retry(self):
        stdout, raw = fake_complete_cpp_and_csv()
        self.assertIn(b"outer_retry=0,step=1,retry=1", stdout)
        self.assertEqual(
            join_selected_local_to_native_csv(stdout, raw, "original")[
                "original_cpp_selected_adapter_returns"], 40)

    def test_repeated_outer_epoch_patch_is_not_unique_selected_identity(self):
        stdout, raw = fake_complete_cpp_and_csv()
        events = stdout.decode().splitlines()
        # Same patch can have a repeated Adapter invocation in one global epoch.
        events[3:6] = [x.replace("outer_epoch=2", "outer_epoch=1")
                       for x in events[3:6]]
        result = join_selected_local_to_native_csv(
            ("\n".join(events) + "\n").encode(), raw, "original")
        self.assertEqual(result["original_cpp_selected_adapter_returns"], 40)

    def test_unwitnessed_extra_or_missing_cpp_event_rejected(self):
        stdout, raw = fake_complete_cpp_and_csv()
        lines = stdout.splitlines()
        for corrupted in (
            b"\n".join(lines[:-1]) + b"\n",
            b"\n".join(lines + [lines[-1]]) + b"\n",
        ):
            with self.subTest(length=len(corrupted)):
                with self.assertRaises(NativeLineageValidationError):
                    join_selected_local_to_native_csv(
                        corrupted, raw, "original")

    def test_no_selected_attempt_for_return_is_rejected(self):
        stdout, raw = fake_complete_cpp_and_csv()
        changed = stdout.replace(
            b"local=2,kind=selected",
            b"local=2,kind=superseded", 1)
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2730_original_cpp_local_return_identity_not_single_selected"):
            join_selected_local_to_native_csv(changed, raw, "original")

    def test_two_selected_locals_for_same_return_rejected(self):
        stdout, raw = fake_complete_cpp_and_csv()
        changed = stdout.replace(
            b"local=0,kind=superseded",
            b"local=0,kind=selected", 1)
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2730_original_cpp_local_return_identity_not_single_selected"):
            join_selected_local_to_native_csv(changed, raw, "original")

    def test_mismatched_original_generation_status_rejected(self):
        stdout, raw = fake_complete_cpp_and_csv()
        changed = stdout.replace(
            b"status=curve_transition_needs_retry",
            b"status=degenerate_needs_retry", 1)
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2730_native_cpp_local_selection_and_raw_csv_differ"):
            join_selected_local_to_native_csv(changed, raw, "original")

    def test_bogus_original_native_outer_epoch_rejected(self):
        stdout, _raw = fake_complete_cpp_and_csv()
        changed = stdout.replace(b"outer_epoch=2", b"outer_epoch=0", 1)
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2730_original_cpp_local_selection_chronology_or_scope_invalid"):
            parse_native_local_selection(changed)

    def test_nonmonotone_native_outer_epoch_rejected(self):
        stdout, _raw = fake_complete_cpp_and_csv()
        changed = stdout.replace(b"outer_epoch=2", b"outer_epoch=1", 1)
        # The remaining chronology remains valid when epochs are repeated.
        self.assertEqual(len(parse_native_local_selection(changed)), 104)
        changed = stdout.replace(b"outer_epoch=3", b"outer_epoch=1", 1)
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2730_original_cpp_global_epoch_not_monotone"):
            parse_native_local_selection(changed)

    def test_invalid_original_patch_and_unknown_selected_kind_rejected(self):
        stdout, _raw = fake_complete_cpp_and_csv()
        for old, new in (
            (b"patch=0", b"patch=4"),
            (b"kind=selected", b"kind=committed"),
        ):
            with self.subTest(old=old):
                with self.assertRaises(NativeLineageValidationError):
                    parse_native_local_selection(
                        stdout.replace(old, new, 1))

    def test_no_matching_raw_csv_group_rejected(self):
        stdout, raw = fake_complete_cpp_and_csv()
        bad = raw.replace(b"curve_transition_needs_retry",
                          b"degenerate_needs_retry", 1)
        with self.assertRaises(NativeLineageValidationError):
            join_selected_local_to_native_csv(stdout, bad, "original")

    def test_absent_cpp_original_file_never_accepts_fake_attestation(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                attest_original_selection_source(Path(temp))


if __name__ == "__main__":
    unittest.main()
