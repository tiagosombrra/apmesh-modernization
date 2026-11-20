"""Synthetic retained-artifact audit controls; these are not real native runs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.mesh_studio.audit_retained_native_lineage import (
    NativeLineageValidationError, audit_retained_directory,
)
from tools.mesh_studio.test_verify_native_lineage import synthetic_receipt
from tools.mesh_studio.verify_native_lineage import (
    REPORT_SCHEMA, validate_lineage_records,
)


def write_fake_archive(directory: Path) -> None:
    for model in ("eistute", "book"):
        records = synthetic_receipt(model)
        data = ("\n".join(json.dumps(record, separators=(",", ":")) for record in records)
                + "\n").encode("utf-8")
        name = "r2712-" + model + "-test-only.ndjson"
        (directory / name).write_bytes(data)
        observed = validate_lineage_records(records, model)
        observed["source_file_sha256"] = hashlib.sha256(data).hexdigest()
        observed["raw_native_ndjson_artifact_name"] = name
        summary = {
            "schema": REPORT_SCHEMA,
            "classification": "REAL_NATIVE_SERIAL_SOURCE_COMMIT_NOT_SCIENTIFIC_LOD",
            "original_model": model,
            "scientific_lod_qualified": False,
            "cross_epoch_original_face_id_lineage_qualified": False,
            "source_shared_curve_incidence_not_welded_nodes": True,
            "native_accepted_commits": 1, "native_rejected_restored": 1,
            "accepted_snapshots": [observed],
        }
        for key in ("native_config_source_sha256", "real_model_input_sha256",
                    "research_executable_sha256", "resolved_research_config_sha256",
                    "native_stdout_sha256", "native_stderr_sha256"):
            summary[key] = "0" * 64
        (directory / ("r2712-" + model + "-native-lineage-audit.json")).write_text(
            json.dumps(summary), encoding="utf-8")


class RetainedNativeLineageContractTests(unittest.TestCase):
    def test_synthetic_archived_bytes_are_independently_reparsed(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            write_fake_archive(root)
            summary = audit_retained_directory(root)
            self.assertTrue(summary["all_native_raw_sidecar_sha256_verified"])
            self.assertFalse(summary["cross_epoch_face_lineage_qualified"])

    def test_missing_native_face_records_cannot_be_replaced_by_hash_only(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            write_fake_archive(root)
            (root / "r2712-eistute-test-only.ndjson").unlink()
            with self.assertRaisesRegex(NativeLineageValidationError,
                                        "original_native_face_records_not_retained_eistute"):
                audit_retained_directory(root)

    def test_corrupt_original_face_bytes_fail_even_if_summary_still_present(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            write_fake_archive(root)
            file = root / "r2712-book-test-only.ndjson"
            file.write_bytes(file.read_bytes().replace(b"0.2", b"0.3", 1))
            with self.assertRaisesRegex(NativeLineageValidationError,
                                        "retained_native_raw_face_sha256_mismatch_book"):
                audit_retained_directory(root)

    def test_fake_summary_face_count_and_unindexed_extra_sidecar_rejected(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            write_fake_archive(root)
            file = root / "r2712-book-native-lineage-audit.json"
            report = json.loads(file.read_text(encoding="utf-8"))
            report["accepted_snapshots"][0]["native_tri_faces"] += 1
            file.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(NativeLineageValidationError,
                                        "native_summary_differs_from_raw_book_native_tri_faces"):
                audit_retained_directory(root)
            write_fake_archive(root)
            (root / "unindexed-fake.ndjson").write_bytes(b"\n")
            with self.assertRaisesRegex(NativeLineageValidationError,
                                        "unqualified_or_unindexed_native_raw_sidecar"):
                audit_retained_directory(root)


if __name__ == "__main__":
    unittest.main()
