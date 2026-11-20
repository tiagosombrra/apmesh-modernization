"""Synthetic negative controls for the native receipt parser, not mesh results."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from tools.mesh_studio.verify_native_lineage import (
    SCHEMA,
    NativeLineageValidationError,
    decode_ndjson,
    validate_lineage_records,
)


def synthetic_receipt(model: str = "eistute") -> list[dict]:
    patches, curves = (4, 13) if model == "eistute" else (28, 85)
    result = [{
        "schema": SCHEMA, "type": "accepted_commit", "step": 1, "retry": 0,
        "session": 6306001, "outer_epoch": 1, "global_retry": 0,
        "has_typed_outer_scope": True, "source_patch_count": patches,
        "source_curve_count": curves,
        "native_id_semantics": "snapshot_local_not_cross_epoch",
        "face_record_semantics":
            "native_element_id_plus_patch_slot_not_obj_ordinal",
        "scientific_lod_admitted": False,
    }]
    for patch_slot in range(patches):
        edges = []
        for edge in range(4):
            slot = (patch_slot * 4 + edge) % curves
            edges.append({
                "edge_slot": edge, "source_curve_slot": slot,
                "native_curve_id": 1000 + slot,
                "reversed": bool(edge % 2),
                "reported_curve_patch_observers": 2,
            })
        result.append({
            "type": "patch", "patch_slot": patch_slot, "native_patch_id": 0,
            "node_count": 3, "face_count": 1, "source_curves": edges,
        })
        result.append({
            "type": "face", "patch_slot": patch_slot, "native_patch_id": 0,
            "element_slot": 0, "native_element_id": patch_slot + 11,
            "vertices": [{
                "native_node_id": patch_slot * 3 + k + 1,
                "xyz": [float(patch_slot), float(k), 0.0],
                "uv": [0.2 * k, 0.1 * k],
            } for k in range(3)],
        })
    result.append({
        "type": "complete", "patch_records": patches,
        "face_records": patches, "node_records_counted_per_patch": 3 * patches,
        "fully_accepted_source_face_lineage_across_epochs": False,
    })
    return result


class NativeLineageParserContractTests(unittest.TestCase):
    def test_synthetic_parser_contract_on_both_original_source_sizes(self) -> None:
        for model in ("eistute", "book"):
            with self.subTest(model=model):
                report = validate_lineage_records(synthetic_receipt(model), model)
                self.assertEqual(report["native_source_patches"],
                                 4 if model == "eistute" else 28)
                self.assertEqual(report["native_source_curves"],
                                 13 if model == "eistute" else 85)
                self.assertFalse(report["native_ids_persistent_across_accepted_epochs_verified"])
                self.assertFalse(report["scientific_lod_qualified"])

    def test_synthetic_round_trip_ndjson_is_canonical(self) -> None:
        rows = synthetic_receipt()
        raw = ("\n".join(json.dumps(x, separators=(",", ":")) for x in rows) +
               "\n").encode("utf-8")
        self.assertEqual(decode_ndjson(raw), rows)
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "truncated_or_oversized_lineage"):
            decode_ndjson(raw[:-1])

    def test_forged_admitted_lod_is_rejected(self) -> None:
        forged = synthetic_receipt()
        forged[0]["scientific_lod_admitted"] = True
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "invalid_or_forged_native_commit_header"):
            validate_lineage_records(forged, "eistute")

    def test_face_owner_disagreement_is_rejected_even_if_ids_repeat(self) -> None:
        forged = synthetic_receipt()
        forged[2]["native_patch_id"] = 5
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "invalid_native_face_or_patch_owner"):
            validate_lineage_records(forged, "eistute")

    def test_missing_or_duplicate_face_slot_is_rejected(self) -> None:
        forged = synthetic_receipt()
        del forged[2]
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "missing_or_noncontiguous_native_element_slots"):
            validate_lineage_records(forged, "eistute")
        forged = synthetic_receipt()
        forged.insert(3, deepcopy(forged[2]))
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "invalid_native_face_or_patch_owner"):
            validate_lineage_records(forged, "eistute")

    def test_cross_patch_source_curve_spoof_is_rejected(self) -> None:
        forged = synthetic_receipt()
        shared = next(row for row in forged
                      if row.get("type") == "patch" and row["patch_slot"] == 3)
        shared["source_curves"][1]["source_curve_slot"] = 0
        shared["source_curves"][1]["native_curve_id"] = 999999
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "cross_patch_source_curve_id_disagreement"):
            validate_lineage_records(forged, "eistute")

    def test_nonfinite_original_geometry_is_rejected(self) -> None:
        forged = synthetic_receipt()
        forged[2]["vertices"][0]["xyz"][0] = float("nan")
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "invalid_native_vertex_or_source_uv"):
            validate_lineage_records(forged, "eistute")

    def test_incomplete_or_fake_typed_scope_is_rejected(self) -> None:
        forged = synthetic_receipt()
        forged[0]["outer_epoch"] = 0
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "invalid_partial_native_outer_scope"):
            validate_lineage_records(forged, "eistute")

    def test_corrupt_completion_or_trailing_event_is_rejected(self) -> None:
        forged = synthetic_receipt()
        forged[-1]["face_records"] += 1
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "lineage_face_or_node_counts_inconsistent"):
            validate_lineage_records(forged, "eistute")
        forged = synthetic_receipt()
        forged.append({"type": "face"})
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "invalid_or_forged_lineage_completion"):
            validate_lineage_records(forged, "eistute")

    def test_duplicate_json_fields_are_rejected(self) -> None:
        rows = synthetic_receipt()
        head = json.dumps(rows[0])[:-1] + ', "type": "rejected"}'
        payload = (head + "\n" + "\n".join(json.dumps(x) for x in rows[1:]) +
                   "\n").encode("utf-8")
        with self.assertRaisesRegex(NativeLineageValidationError,
                                    "duplicate_json_key_type"):
            decode_ndjson(payload)


if __name__ == "__main__":
    unittest.main()
