#!/usr/bin/env python3
"""S3.Z.4: fail-closed original S40 acquisition, provenance and trial runner.

This runner MAY fetch a fixed-revision external public STEP into a private path;
it NEVER commits that source or CAD-derived BP. Geometry requires authorized
local S3.W data. A preliminary S3.Z trial is never an admitted surface atlas.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import urllib.error
import urllib.request

from s3z_s40_circular_seam_gate import (
    ORIGINAL_STEP_SHA,
    S3W_PARENT_SHA,
    S3Y_SELECTED_SHA,
    TARGET_FACES,
    TRIAL_BIASES_MM,
    FIXED_BUDGET_MM,
)

UPSTREAM_STEP_URL = (
    "https://raw.githubusercontent.com/cgg-bern/hex-me-if-you-can/"
    "8f00f02579037cc893042f2ee2c910b20e3fb1b0/original/i25o_s40.step"
)
MAX_STEP_BYTES = 10 * 1024 * 1024
PUBLIC_RECEIPT_NAME = "s3zd_nongeometric_trial_receipt.json"


class InputBlocked(RuntimeError):
    """Input materials are unavailable or not byte-identical."""


def verify_original_bytes(data: bytes) -> None:
    """Never interpret or admit any nonmatching industrial STEP bytes."""
    if sha256(data).hexdigest() != ORIGINAL_STEP_SHA:
        raise InputBlocked("Original S40 STEP source hash mismatch")


def fetch_pinned_original(destination: Path, *, opener=None) -> dict:
    """Fetch a pinned original only when explicitly requested.

    A temporary file is used to avoid leaving partial or unverified source
    data behind after a failed request. No arbitrary remote URL is accepted.
    """
    destination = Path(destination)
    if destination.is_file():
        verify_original_bytes(destination.read_bytes())
        return {"source": "EXISTING_VERIFIED_FILE", "sha256": ORIGINAL_STEP_SHA}
    if destination.exists():
        raise InputBlocked("Original STEP destination already exists and is not a file")
    destination.parent.mkdir(parents=True, exist_ok=True)
    opener = opener or urllib.request.urlopen
    temp_name = None
    try:
        response = opener(UPSTREAM_STEP_URL, timeout=30)
        with response:
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=".s3z4-step-", suffix=".partial",
                dir=destination.parent, delete=False,
            ) as temporary:
                temp_name = temporary.name
                total = 0
                hasher = __import__("hashlib").sha256()
                while True:
                    chunk = response.read(65536)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_STEP_BYTES:
                        raise InputBlocked("Pinned STEP download exceeds declared size limit")
                    temporary.write(chunk)
                    hasher.update(chunk)
                if hasher.hexdigest() != ORIGINAL_STEP_SHA:
                    raise InputBlocked("Downloaded original STEP failed pinned SHA-256")
        # Do not overwrite another process's original in the private directory.
        if destination.exists():
            raise InputBlocked("Original destination appeared concurrently")
        os.replace(temp_name, destination)
        temp_name = None
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        raise InputBlocked(f"Could not fetch original pinned STEP: {type(exc).__name__}") from exc
    finally:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)
    return {"source": "FETCHED_FIXED_GIT_REVISION", "sha256": ORIGINAL_STEP_SHA}


def _receipt_base() -> dict:
    return {
        "schema": "apmesh-s3zd-s40-original-native-trial-orchestration-v1",
        "original_step_sha256_required": ORIGINAL_STEP_SHA,
        "s3w_bp_sha256_required": S3W_PARENT_SHA,
        "s3y_selected_child_sha256_required": S3Y_SELECTED_SHA,
        "selected_patch_count_before_native_trials": 156,
        "selected_source_faces_before_native_trials": 22,
        "candidate_target_original_source_faces": list(TARGET_FACES),
        "trial_control_displacements_mm": list(TRIAL_BIASES_MM),
        "fixed_original_geometry_budget_mm": FIXED_BUDGET_MM,
        "original_source_coordinates_in_receipt": False,
        "new_original_source_faces_admitted": 0,
        "apmesh_tri_quad_executed": False,
        "production_cpp_regression_executed": False,
        "continuous_cad_equivalence_certified": False,
    }


def assess_trial_result(result: dict) -> dict:
    """Reject truncated or malformed trial logs; never auto-admit a candidate."""
    if result.get("source_sha256") != ORIGINAL_STEP_SHA:
        raise ValueError("Trial receipt source hash mismatch")
    if result.get("parent_156_patch_sha256") != S3Y_SELECTED_SHA:
        raise ValueError("Trial receipt parent hash mismatch")
    if result.get("original_step_faces_blocked") != list(TARGET_FACES):
        raise ValueError("Trial target original source face ids changed")
    if result.get("admitted_patch_count") != 156 or result.get("admitted_source_faces") != 22:
        raise ValueError("Trial incorrectly claims new original source admission")
    if result.get("strict_native_admission_completed") is not False or result.get("apmesh_tri_quad_executed") is not False:
        raise ValueError("Trial receipt invents native admission or production meshing")
    trials = result.get("candidate_trials")
    if not isinstance(trials, list) or len(trials) != len(TRIAL_BIASES_MM):
        raise ValueError("Required eight original circular-seam trials not completed")
    expected_biases = list(TRIAL_BIASES_MM)
    if [r.get("shared_control_bias_mm") for r in trials] != expected_biases:
        raise ValueError("Original circular-seam trial order or budget changed")
    allowed = {"BLOCKED", "PRELIMINARY_TWO_SIDED_TRIM_PASS_NOT_ADMITTED"}
    if any(r.get("status") not in allowed for r in trials):
        raise ValueError("Unexpected native trial disposition")
    if any(not isinstance(r.get("candidate_sha256"), str) or len(r["candidate_sha256"]) != 64
           for r in trials):
        raise ValueError("A native trial lacks its candidate geometry digest")
    passed = sum(r["status"] == "PRELIMINARY_TWO_SIDED_TRIM_PASS_NOT_ADMITTED" for r in trials)
    blocked = len(trials) - passed
    return {
        "status": "TRIALS_EXECUTED_NO_NEW_FACE_ADMISSION",
        "actual_native_candidate_trials": len(trials),
        "preliminary_candidates_needing_independent_audit": passed,
        "rejected_native_candidates": blocked,
        "trial_receipt_sha256": sha256(
            (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode()
        ).hexdigest(),
        "individual_candidate_digests": [r["candidate_sha256"] for r in trials],
        "new_original_source_faces_admitted": 0,
        "formal_final_acceptance": False,
    }


def run_s3z4(
    original: Path, bp: Path, manifest: Path, builder: Path, private_output: Path,
    *, fetch_original: bool = False, importer=None, private_executor=None,
) -> tuple[dict, int]:
    """Coordinate byte-pinned native tests and emit nongeometric evidence.

    Tests may inject a fake importer/runner after a synthetic readiness fixture.
    The production path always rechecks the true pinned original and S3.W BP.
    """
    from s3zb_check_private_readiness import check_readiness

    original, bp, manifest, builder = map(Path, (original, bp, manifest, builder))
    private_output = Path(private_output)
    receipt = _receipt_base()
    receipt["source_fetch_requested"] = bool(fetch_original)
    if fetch_original:
        try:
            receipt["source_acquisition"] = fetch_pinned_original(original)
        except InputBlocked as e:
            receipt["status"] = "BLOCKED_ORIGINAL_SOURCE_UNAVAILABLE"
            receipt["blocker"] = str(e)
            return receipt, 3
    readiness = check_readiness(original, bp, manifest, builder)
    receipt["requirements"] = {
        key: {k: row[k] for k in ("found", "hash_ok", "manifest_hash_ok") if k in row}
        for key, row in readiness["checks"].items()
    }
    receipt["python_dependencies"] = readiness["python_dependencies"]
    if readiness["status"] != "READY_FOR_ORIGINAL_NATIVE_TRIAL":
        receipt["status"] = "BLOCKED_MISSING_OR_MISMATCHED_PRIVATE_DATA"
        return receipt, 3
    # Securely verified by the readiness helper; no changes are made to inputs.
    original_bytes = original.read_bytes()
    bp_bytes = bp.read_bytes()
    verify_original_bytes(original_bytes)
    if sha256(bp_bytes).hexdigest() != S3W_PARENT_SHA:
        raise InputBlocked("S3.W BP changed after initial readiness check")
    parent_manifest = json.loads(manifest.read_text(encoding="utf-8"))
    if builder.name != "s3y_s40_curved_planar_rings.py":
        raise InputBlocked("An unexpected S3.Y source-backed builder was supplied")
    sys.path.insert(0, str(builder.resolve().parent))
    try:
        if importer is None:
            import cadquery as cq
            importer = lambda path: cq.importers.importStep(str(path)).val()
        if private_executor is None:
            private_executor = importlib.import_module("s3z_s40_circular_seam_gate").run_private_trials
        native = importer(original)
        result, _ = private_executor(original_bytes, bp_bytes, parent_manifest, native)
        decision = assess_trial_result(result)
        receipt.update(decision)
        # Native diagnostic records contain only IDs, counts, tolerances and digests.
        # Store them solely in the requested private directory pending rights review.
        private_output.mkdir(parents=True, exist_ok=True)
        private_file = private_output / "s3zd_original_native_trials_private.json"
        _atomic_json(private_file, result)
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
        receipt["status"] = "BLOCKED_NATIVE_OR_TOPOLOGY_GATE"
        receipt["blocker"] = f"{type(exc).__name__}: {exc}"
        return receipt, 4
    finally:
        if sys.path and sys.path[0] == str(builder.resolve().parent):
            sys.path.pop(0)
    return receipt, 0


def _atomic_json(destination: Path, data: dict) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destination.parent,
            prefix=".s3zd-", suffix=".partial", delete=False,
        ) as f:
            temporary = Path(f.name)
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-step", required=True, type=Path)
    parser.add_argument("--s3w-bp", required=True, type=Path)
    parser.add_argument("--s3w-manifest", required=True, type=Path)
    parser.add_argument("--s3y-builder", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--fetch-original", action="store_true",
                        help="Fetch pinned public original into a PRIVATE path when absent")
    args = parser.parse_args()
    report, code = run_s3z4(
        args.original_step, args.s3w_bp, args.s3w_manifest,
        args.s3y_builder, args.output_dir, fetch_original=args.fetch_original,
    )
    _atomic_json(args.output_dir / PUBLIC_RECEIPT_NAME, report)
    print(json.dumps({k: report[k] for k in (
        "status", "new_original_source_faces_admitted", "selected_patch_count_before_native_trials"
    )}, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
