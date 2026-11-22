"""Audit retained original native post-commit face evidence without rerunning C++.

The original per-face NDJSON must accompany the trusted source-bound summary.
A digest alone is not enough to independently inspect patch/curve identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from .verify_native_lineage import (
    REPORT_SCHEMA, SOURCE_MODELS, NativeLineageValidationError,
    decode_ndjson, require, validate_lineage_records,
)

HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAX_REPORT_SIZE = 512_000


def audit_retained_directory(directory: Path) -> dict:
    require(directory.is_dir(), "missing_native_evidence_directory")
    seen_files = set()
    outcome = {}
    for model in SOURCE_MODELS:
        report_name = "r2712-" + model + "-native-lineage-audit.json"
        report_path = directory / report_name
        require(report_path.is_file() and report_path.stat().st_size <= MAX_REPORT_SIZE,
                "missing_or_oversized_native_summary_" + model)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        require(report.get("schema") == REPORT_SCHEMA and
                report.get("classification") ==
                "REAL_NATIVE_SERIAL_SOURCE_COMMIT_NOT_SCIENTIFIC_LOD" and
                report.get("original_model") == model and
                report.get("scientific_lod_qualified") is False and
                report.get("cross_epoch_original_face_id_lineage_qualified") is False and
                report.get("source_shared_curve_incidence_not_welded_nodes") is True,
                "native_summary_research_scope_claim_changed_" + model)
        for key in ("native_config_source_sha256", "real_model_input_sha256",
                    "research_executable_sha256", "resolved_research_config_sha256",
                    "native_stdout_sha256", "native_stderr_sha256"):
            require(type(report.get(key)) is str and
                    HEX_SHA256.fullmatch(report[key]) is not None,
                    "missing_native_reproduction_sha_" + key)
        observations = report.get("accepted_snapshots")
        require(type(observations) is list and len(observations) ==
                report.get("native_accepted_commits") and
                len(observations) >= 1 and
                type(report.get("native_rejected_restored")) is int and
                report["native_rejected_restored"] >= 1,
                "missing_original_native_acceptance_or_restoration_" + model)
        accepted = []
        for record in observations:
            filename = record.get("raw_native_ndjson_artifact_name")
            require(type(filename) is str and filename.startswith("r2712-" + model + "-")
                    and filename.endswith(".ndjson") and
                    Path(filename).name == filename and filename not in seen_files,
                    "invalid_native_raw_artifact_name_" + model)
            filepath = directory / filename
            require(filepath.is_file(), "original_native_face_records_not_retained_" + model)
            body = filepath.read_bytes()
            actual_digest = hashlib.sha256(body).hexdigest()
            require(actual_digest == record.get("source_file_sha256") and
                    HEX_SHA256.fullmatch(actual_digest) is not None,
                    "retained_native_raw_face_sha256_mismatch_" + model)
            direct = validate_lineage_records(decode_ndjson(body), model)
            for key, value in direct.items():
                require(record.get(key) == value,
                        "native_summary_differs_from_raw_" + model + "_" + key)
            require(direct["has_typed_outer_scope"],
                    "raw_native_accepted_commit_has_no_typed_outer_event")
            accepted.append(direct["accepted_step"])
            seen_files.add(filename)
        require(accepted == sorted(set(accepted)),
                "duplicate_or_unsorted_native_accepted_steps_" + model)
        outcome[model] = {
            "accepted_native_steps": accepted,
            "source_face_counts": [x["native_tri_faces"] for x in observations],
            "source_patch_count": SOURCE_MODELS[model][0],
            "source_curve_count": SOURCE_MODELS[model][1],
            "raw_native_face_record_artifacts_retained": True,
            "scientific_lod_qualified": False,
        }
    actual_files = {p.name for p in directory.glob("*.ndjson")}
    require(actual_files == seen_files, "unqualified_or_unindexed_native_raw_sidecar")
    return {
        "schema": "apmesh.meshstudio.r2712.retained_native_original_evidence_audit.v1",
        "scope": "REVALIDATED_ORIGINAL_NATIVE_FACE_BYTES_NOT_EXTERNAL_SOURCE_RUN_AUTHENTICATION",
        "original_native_models": outcome,
        "all_native_raw_sidecar_sha256_verified": True,
        "all_original_face_patch_curve_records_reparsed": True,
        "cross_epoch_face_lineage_qualified": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    args = parser.parse_args()
    result = audit_retained_directory(args.directory)
    print("R2712_RETAINED_NATIVE_EVIDENCE_AUDIT=" +
          json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
