#!/usr/bin/env python3
"""Safely stage and publish the S40-F9/F10 original-native *candidate* pair.

This module never validates a CAD model by itself. It only prevents an
incomplete or stale pair of BP and JSON evidence from appearing as a fresh run.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path

BP_NAME = "s40f9_source_joined.ORIGINAL_NATIVE_SAMPLED_CANDIDATE.bp"
RECEIPT_NAME = "s40f9_original_native_reconciliation_receipt.json"
EXPECTED_CLASSIFICATION = "ORIGINAL_NATIVE_SAMPLED_RESEARCH_CANDIDATE"
EXPECTED_CERTIFICATE = "CERTIFIED_STRICT_POSITIVE_POSTREBASE_DECIMAL_BP"
EXPECTED_NATIVE_GATE = "PASS_SAMPLED_ORIGINAL_NATIVE_GATES"


def require_fresh_destination(directory: str | Path) -> Path:
    """Reject any existing destination, including dangling symbolic links."""
    path = Path(directory)
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing existing candidate destination: {path}")
    if path.name in ("", ".", ".."):
        raise ValueError("Candidate destination must be a new named directory")
    return path


def _verify_receipt(candidate_bytes: bytes, report: dict) -> None:
    """Bind the two files to the same post-rebase candidate before writing."""
    if not isinstance(report, dict) or report.get("classification") != EXPECTED_CLASSIFICATION:
        raise ValueError("Candidate classification does not attest the sampled native gate")
    post = report.get("postrebase_exact_jacobian_proof")
    if not isinstance(post, dict) or post.get("status") != EXPECTED_CERTIFICATE:
        raise ValueError("Missing exact post-rebase Jacobian certification")
    if post.get("joined_bp_sha256") != sha256(candidate_bytes).hexdigest():
        raise ValueError("Joined BP SHA-256 is inconsistent with its mathematical receipt")
    if (post.get("certified_postrebase_patch_count") != 8
            or post.get("joined_patch_count") != 164
            or post.get("joined_control_count") != 1743
            or post.get("new_source_patch_indices") != list(range(156, 164))):
        raise ValueError("Exact post-rebase certificate scope is incomplete")
    native = report.get("original_native_audit")
    if (not isinstance(native, dict)
            or native.get("status") != EXPECTED_NATIVE_GATE
            or report.get("all_original_native_trim_and_edge_gates_executed") is not True):
        raise ValueError("Original S40 source-native sampled gate was not completed")
    if (report.get("apmesh_cpp_tri_quad_executed") is not False
            or report.get("full_43_face_atlas_complete") is not False
            or report.get("formal_continuous_original_STEP_hausdorff_certified") is not False
            or report.get("new_original_source_faces_admitted") != 0):
        raise ValueError("Experimental candidate would be misrepresented as admitted/complete")


def publish_native_candidate(directory: str | Path, candidate_text: str, report: dict) -> Path:
    """Write both artifacts in a private staging directory, then rename it.

    The destination must not exist. A failed write leaves no destination; a
    failed rename cleans the staging directory. As with every path-based check,
    an untrusted concurrent writer can race on the destination name.
    """
    path = require_fresh_destination(directory)
    if not isinstance(candidate_text, str):
        raise TypeError("Candidate BP must be a UTF-8 string")
    candidate = candidate_text.encode("utf-8")
    _verify_receipt(candidate, report)
    receipt = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=f".{path.name}.stage-", dir=path.parent))
    try:
        (staged / BP_NAME).write_bytes(candidate)
        (staged / RECEIPT_NAME).write_bytes(receipt)
        # Confirm exact bytes in the staged files before publication.
        if (sha256((staged / BP_NAME).read_bytes()).hexdigest()
                != report["postrebase_exact_jacobian_proof"]["joined_bp_sha256"]):
            raise ValueError("Staged BP bytes changed before publication")
        if json.loads((staged / RECEIPT_NAME).read_bytes()) != report:
            raise ValueError("Staged receipt differs from the validated report")
        require_fresh_destination(path)
        os.rename(staged, path)
    except BaseException:
        shutil.rmtree(staged, ignore_errors=True)
        raise
    return path
