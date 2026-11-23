"""Renew only exact historical C++ source evidence, never scientific acceptance.

The ten files must be exact bytes from the independently certified original
C++ generator run; a new archive upload must not be described as a new
compiler run, native accepted epoch, GPU proof, or distribution certificate.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from .v59_reviewer import (
    ORIGINAL_CI_HEAD_SHA, ORIGINAL_CI_RUN, SOURCE_FILES, preflight,
)

SCHEMA = "apmesh.meshstudio.v511.original_cpp_evidence_mirror.v1"
CLASSIFICATION = "EXACT_ORIGINAL_CPP_SOURCE_RETAINED_NOT_RECOMPILED"
ARTIFACT_NAME = ("mesh-studio-v511-original-cpp-source-10files-" +
                 ORIGINAL_CI_HEAD_SHA)


class SourceContinuityError(ValueError):
    """Original-native corpus was modified or its provenance was substituted."""


def require(value: bool, code: str) -> None:
    if not value:
        raise SourceContinuityError("source_mirror_" + code)


def mirror_receipt(source: Path, *, upstream_run_id: int,
                   upstream_kind: str, mirror_commit: str) -> dict:
    """Independently reopen exactly the historic original C++ postcommit bytes."""
    require(upstream_kind in ("historic", "mirror"), "invalid_upstream_kind")
    require(upstream_run_id >= 1, "invalid_upstream_run")
    require(upstream_kind != "historic" or upstream_run_id == ORIGINAL_CI_RUN,
            "historic_origin_run_mismatch")
    require(upstream_kind != "mirror" or upstream_run_id != ORIGINAL_CI_RUN,
            "mirror_must_not_impersonate_historic_run")
    require(len(mirror_commit) == 40 and
            all(ch in "0123456789abcdef" for ch in mirror_commit),
            "invalid_branch_commit")
    proof = preflight(source)
    require(
        proof["original_native_ci_run"] == ORIGINAL_CI_RUN and
        proof["original_native_ci_head_sha"] == ORIGINAL_CI_HEAD_SHA and
        proof["source_cpp_raw_postcommit_reopened"] is True and
        proof["accepted_cpp_global_steps"] ==
        {"eistute": [1], "book": [1]} and
        proof["scientific_lod_qualified"] is False and
        proof["native_cpp_recompiled_in_this_review"] is False and
        proof["physical_node_welding_certified"] is False and
        proof["source_exact_files_rehashed"] ==
        {key: {"size": entry[0], "sha256": entry[1]}
         for key, entry in SOURCE_FILES.items()},
        "original_source_reaudit_or_claim_invalid",
    )
    return {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "evidence_class": "ORIGINAL_CPP_ACCEPTED_STEP_1_RETAINED",
        "original_compiled_source_run_id": ORIGINAL_CI_RUN,
        "original_compiled_source_commit": ORIGINAL_CI_HEAD_SHA,
        "original_cpp_source_independently_reopened": True,
        "source_file_count": len(SOURCE_FILES),
        "source_file_digests": dict(sorted(
            proof["source_exact_files_rehashed"].items())),
        "upstream_evidence_run_id": upstream_run_id,
        "upstream_evidence_kind": upstream_kind,
        "mirror_workflow_commit": mirror_commit,
        "mirror_artifact_name": ARTIFACT_NAME,
        "native_cpp_recompiled_by_mirror": False,
        "new_original_native_accepted_epoch": False,
        "scientific_lod_qualified": False,
        "physical_workstation_reviewer_approved": False,
        "signed_distributed_software": False,
        "renewed_artifact_retention_is_not_permanent_archival": True,
        "private_doctoral_drive_copy_remains_independent": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--upstream-run-id", type=int, required=True)
    parser.add_argument("--upstream-kind", choices=("historic", "mirror"),
                        required=True)
    parser.add_argument("--mirror-commit", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    result = mirror_receipt(
        args.source_dir, upstream_run_id=args.upstream_run_id,
        upstream_kind=args.upstream_kind, mirror_commit=args.mirror_commit)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) +
           "\n").encode("utf-8")
    args.receipt.write_bytes(raw)
    print("STUDIO_ORIGINAL_CPP_SOURCE_RETAINED=" + json.dumps({
        "original_compiled_source_run_id": ORIGINAL_CI_RUN,
        "source_file_count": result["source_file_count"],
        "receipt_sha256": sha256(raw).hexdigest(),
        "mirror_artifact_name": ARTIFACT_NAME,
        "native_cpp_recompiled": False,
        "scientific_lod_qualified": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
