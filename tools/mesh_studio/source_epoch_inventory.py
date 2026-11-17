"""Bounded, fail-closed inventory of original APMesh artifacts and adaptive evidence.

This reads existing verified source files. It does NOT manufacture missing
adaptive epochs, patch identities or scientific error bounds.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from .real_candidate_study import (
    OBJ_HASHES,
    ORDER,
    SOURCE_CI_RUN_ID,
    SOURCE_GENERATOR_SHA,
    SOURCE_LINUX_ARTIFACT_ID,
    SOURCE_REPORT_SHA256,
    SOURCE_WINDOWS_ARTIFACT_ID,
    qualify_real_study,
)

SCHEMA = "apmesh.meshstudio.r2710.source_epoch_inventory.v1"
GATE = "apmesh.meshstudio.r28.scientific_lod_admission.v1"
EISTUTE_SHA256 = "378b62da75400c1bfe6871be29d22d8b14d6d6e054a1fa79de062de35c95f9eb"
EISTUTE_GIT_BLOB_SHA1 = "8f54a95e0192e9af3e76ba5d9f28202cd47dae79"
HISTORIC_EISTUTE_MANIFEST_SHA256 = (
    "c0c55cbdf473233408dd21a9a17b542adee12f969e187abaea8116f103080e18"
)
MAX_OBJ_BYTES = 2_000_000
MAX_CSV_BYTES = 1_000_000
EXPECTED_ARCHIVED_TRI = 7184
EXPECTED_ARCHIVED_VERTICES = 3691
EXPECTED_COUNTS = {
    "control": (69, 42, 36),
    "band": (93, 62, 44),
    "west": (109, 75, 50),
    "north": (107, 71, 54),
    "both": (117, 82, 52),
}
REQUIRED_BLOCKERS = (
    "NO_ACCEPTED_ADAPTIVE_EPOCH",
    "NO_NATIVE_EPOCH_TRACE_AND_DECISION_ORACLE",
    "NO_MULTIPATCH_GENERATOR_FACE_PATCH_CURVE_LINEAGE",
    "NO_QUALIFIED_LARGER_ACCEPTED_SOURCE",
    "NO_CONTINUOUS_GEOMETRIC_ERROR_BOUND",
)


class SourceEpochInventoryError(ValueError):
    """A pinned artifact or required scientific provenance invariant is violated."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise SourceEpochInventoryError(reason)


def source_sha256(path: Path, *, limit: int = MAX_OBJ_BYTES) -> str:
    require(path.is_file() and path.stat().st_size <= limit, "missing_or_oversized_source")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_eistute_reference(root: Path) -> dict:
    """Confirm historical OBJ identity/metadata without claiming epoch acceptance."""
    mesh = root / "reference" / "eistute_stage4.obj"
    sidecar = root / "reference" / "eistute_stage4.json"
    metrics = root / "reference" / "eistute_metrics.csv"
    manifest = root / "MANIFEST.sha256"

    raw_sha = source_sha256(mesh)
    require(raw_sha == EISTUTE_SHA256, "eistute_reference_sha256_mismatch")
    raw = mesh.read_bytes()
    blob_sha = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw,
        usedforsecurity=False,
    ).hexdigest()
    require(blob_sha == EISTUTE_GIT_BLOB_SHA1, "eistute_git_blob_mismatch")
    require(sidecar.is_file() and sidecar.stat().st_size < 16_384,
            "missing_eistute_sidecar")
    record = json.loads(sidecar.read_text(encoding="utf-8"))
    require(record.get("model") == "Eistute" and record.get("stage") == 4 and
            record.get("triangles") == EXPECTED_ARCHIVED_TRI,
            "eistute_archived_target_mismatch")
    for name, expected in (
        ("normalized_error", 0.036712),
        ("error_reduction_percent", 96.3288),
        ("quality_q_ge_0_60_percent", 58.6303),
        ("mean_shared_curve_compatibility_error", 0.0),
    ):
        require(type(record.get(name)) in (int, float) and
                math.isclose(record[name], expected, abs_tol=1e-9, rel_tol=0),
                "eistute_archived_" + name + "_mismatch")

    vertices = 0
    faces = 0
    max_index = 0
    for line in raw.decode("utf-8").splitlines():
        fields = line.split()
        if not fields or fields[0] == "#":
            continue
        if fields[0] == "v":
            require(len(fields) == 4 and
                    all(math.isfinite(float(x)) for x in fields[1:]),
                    "invalid_eistute_vertex_record")
            vertices += 1
        elif fields[0] == "f":
            require(len(fields) == 4, "eistute_not_all_triangle")
            try:
                ids = [int(word) for word in fields[1:]]
            except ValueError as exc:
                raise SourceEpochInventoryError("invalid_eistute_index_record") from exc
            require(len(set(ids)) == 3 and all(index > 0 for index in ids),
                    "invalid_eistute_triangle_indices")
            max_index = max(max_index, *ids)
            faces += 1
        else:
            raise SourceEpochInventoryError("unsupported_eistute_record")
    require(vertices == EXPECTED_ARCHIVED_VERTICES and
            faces == EXPECTED_ARCHIVED_TRI and max_index <= vertices,
            "eistute_index_or_counts_mismatch")

    require(metrics.is_file() and metrics.stat().st_size <= MAX_CSV_BYTES,
            "missing_eistute_reference_csv")
    with metrics.open(encoding="utf-8", newline="") as reader:
        rows = list(csv.DictReader(reader))
    expected_columns = {
        "error_normalized": "normalized_error",
        "error_total_reduction_pct": "error_reduction_percent",
        "q_ge_0_60": "quality_q_ge_0_60_percent",
    }
    matching = [
        row for row in rows
        if row.get("step") == "4" and row.get("elements") == str(faces) and
        all(math.isclose(float(row[k]), record[v], abs_tol=1e-6, rel_tol=0)
            for k, v in expected_columns.items())
    ]
    require(len(matching) >= 1, "eistute_archived_csv_reference_mismatch")
    # The archived CSV records rejection of the saved candidate.
    # This is source-reported history, not an independently replayed native trace.
    require(all(row.get("budget_final_status") == "rejected" and
                row.get("stop_reason") == "hybrid_criterion_rejected" and
                row.get("step_mode") == "refine" for row in matching),
            "archived_eistute_rejection_status_mismatch")

    require(manifest.is_file() and manifest.stat().st_size < 100_000,
            "missing_historical_manifest")
    declared = [
        line.split(" ", 1)[0] for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.endswith(" *./reference/eistute_stage4.obj")
    ]
    require(declared == [HISTORIC_EISTUTE_MANIFEST_SHA256],
            "historical_eistute_manifest_entry_changed")
    require(declared[0] != raw_sha, "historical_eistute_manifest_discrepancy_missing")
    # Reconstruct the archived Windows-style representation from the pinned
    # LF repository blob. A matching hash is byte-level proof of line endings
    # alone; do not rewrite the historical manifest or silently normalize OBJ.
    require(b"\r" not in raw and b"\n" in raw,
            "eistute_original_lf_bytes_unexpected")
    crlf_sha = hashlib.sha256(raw.replace(b"\n", b"\r\n")).hexdigest()
    require(crlf_sha == declared[0],
            "historical_manifest_not_reproduced_by_crlf_conversion")

    return {
        "artifact": "reference/eistute_stage4.obj",
        "file_sha256": raw_sha,
        "git_blob_sha1": blob_sha,
        "historic_manifest_sha256": declared[0],
        "historical_manifest_matches_file": False,
        "historic_manifest_matches_crlf_equivalent": True,
        "crlf_reconstructed_sha256": crlf_sha,
        "manifest_discrepancy_explanation": "EXACT_LF_TO_CRLF_CONVERSION_NOT_GEOMETRY_CHANGE",
        "header": "Wavefront OBJ generated by ap_mesh / step 4",
        "vertices": vertices,
        "triangles": faces,
        "quads": 0,
        "archived_stage": 4,
        "archived_numeric_targets": {
            "normalized_error": record["normalized_error"],
            "error_reduction_percent": record["error_reduction_percent"],
            "quality_q_ge_0_60_percent": record["quality_q_ge_0_60_percent"],
            "mean_shared_curve_compatibility_error":
                record["mean_shared_curve_compatibility_error"],
        },
        "record_type": "SAVED_HISTORICAL_STAGE4_CANDIDATE",
        "archived_csv_matching_reference_rows": len(matching),
        "archived_csv_budget_final_status": "rejected",
        "archived_csv_stop_reason": "hybrid_criterion_rejected",
        "archived_csv_step_mode": "refine",
        "archived_csv_decision_scope": "SOURCE_REPORTED_REJECTION_NOT_REPLAYED_NATIVE_TRACE",
        "adaptive_acceptance_verified": False,
        "per_face_original_generator_id_verified": False,
        "multi_patch_curve_ownership_verified": False,
        "source_model_oracle_available": False,
        "obj_face_index_semantics": "ORDINAL_IN_OBJ_NOT_GENERATOR_FACE_ID",
        "warnings": [
            "HISTORICAL_MANIFEST_HASH_REPRODUCED_BY_CRLF_LINE_ENDINGS_ONLY",
            "ARCHIVED_CSV_RECORDS_HYBRID_CRITERION_REJECTION_NOT_ADAPTIVE_ACCEPTANCE",
            "ARCHIVED_CSV_IS_NOT_INDEPENDENT_NATIVE_EVENT_TRACE",
            "OBJ_CONTAINS_NEITHER_CANONICAL_FACE_IDS_NOR_PATCH_CURVE_IDENTITIES",
        ],
    }


def audit_r28_gate(report: dict) -> dict:
    """Require independent native source evidence; candidate quality never bypasses it."""
    require(report.get("schema") == SCHEMA, "wrong_inventory_schema")
    require(report.get("source_experiments") == 1, "unverified_independent_runs")
    require(report.get("accepted_adaptive_epochs") == 0,
            "unverified_adaptive_epoch_claim")
    items = report.get("source_objects")
    require(type(items) is list and len(items) == len(ORDER),
            "invalid_source_epoch_inventory")
    for i, name in enumerate(ORDER):
        item = items[i]
        require(item.get("name") == name and item.get("sha256") == OBJ_HASHES[name],
                "tampered_real_source_identity_" + name)
        require(item.get("state") ==
                ("CONTROLLED_NONADAPTIVE_OUTPUT" if name == "control"
                 else "STAGED_UNACCEPTED"), "unverified_candidate_promotion_" + name)
        require(item.get("nodes") == EXPECTED_COUNTS[name][0] and
                item.get("quads") == EXPECTED_COUNTS[name][1] and
                item.get("triangles") == EXPECTED_COUNTS[name][2],
                "tampered_real_source_counts_" + name)
        require(item.get("accepted_adaptive_epoch") is None,
                "candidate_promoted_to_adaptive_epoch_" + name)
    legacy = report.get("legacy_archive")
    require(type(legacy) is dict and legacy.get("file_sha256") == EISTUTE_SHA256 and
            legacy.get("historical_manifest_matches_file") is False and
            legacy.get("historic_manifest_matches_crlf_equivalent") is True and
            legacy.get("crlf_reconstructed_sha256") == HISTORIC_EISTUTE_MANIFEST_SHA256 and
            legacy.get("adaptive_acceptance_verified") is False and
            legacy.get("per_face_original_generator_id_verified") is False and
            legacy.get("archived_csv_budget_final_status") == "rejected" and
            legacy.get("archived_csv_stop_reason") == "hybrid_criterion_rejected",
            "unverified_legacy_source_promotion")
    flags = report.get("scientific_evidence")
    require(type(flags) is dict and
            all(flags.get(key) is False for key in (
                "native_acceptance_trace_verified",
                "multi_patch_curve_and_face_lineage_verified",
                "continuous_source_error_bound_verified",
                "larger_accepted_source_mesh_verified",
                "two_independent_accepted_adaptive_epochs_verified",
            )), "unsupported_scientific_evidence_assertion")
    return {
        "schema": GATE,
        "eligible_for_r28_lod": False,
        "status": "BLOCKED_BY_UNAVAILABLE_INDEPENDENT_SCIENTIFIC_EVIDENCE",
        "blocking_evidence": list(REQUIRED_BLOCKERS),
        "tests_of_artifact_integrity_are_not_scientific_acceptance": True,
        "synthetic_lod_speedups_cannot_override_native_acceptance": True,
    }


def build_source_epoch_inventory(root: Path) -> dict:
    """Reuse the existing independent real-candidate study, then classify epoch evidence."""
    root = root.resolve()
    group = root / "tools" / "mesh_studio" / "fixtures" / "real_p2d1c3"
    qualified = qualify_real_study(group)
    require(qualified["schema"] == "apmesh.meshstudio.real_candidate_study.v1",
            "study_oracle_schema_mismatch")
    source = qualified["provenance"]
    require(qualified["scientific_status"]["accepted_adaptive_epochs"] == 0,
            "source_report_claims_adaptation")
    require(source["source_candidate_revision"] == SOURCE_GENERATOR_SHA and
            source["original_actions_run"] == SOURCE_CI_RUN_ID and
            source["linux_artifact_id"] == SOURCE_LINUX_ARTIFACT_ID and
            source["windows_artifact_id"] == SOURCE_WINDOWS_ARTIFACT_ID and
            source["original_source_report_sha256"] == SOURCE_REPORT_SHA256,
            "provenance_root_mismatch")
    objects = []
    for name in ORDER:
        source_object = qualified["physical_candidates"][name]
        geometry = source_object["geometry"]
        count = EXPECTED_COUNTS[name]
        require((geometry["nodes"], geometry["quads"], geometry["triangles"]) == count,
                "unexpected_source_topology_" + name)
        objects.append({
            "name": name,
            "source_path": f"tools/mesh_studio/fixtures/real_p2d1c3/{name}.obj",
            "sha256": source_object["source_mesh_sha256"],
            "state": ("CONTROLLED_NONADAPTIVE_OUTPUT" if name == "control"
                      else "STAGED_UNACCEPTED"),
            "accepted_adaptive_epoch": None,
            "nodes": geometry["nodes"],
            "quads": geometry["quads"],
            "triangles": geometry["triangles"],
            "elements": geometry["elements"],
            "source_grid_sites": qualified["source_sampling"]["sites"],
            "source_oracle": "PINNED_SINGLE_4X4_BEZIER_BERNSTEIN",
            "source_error_kind": "DISCRETE_SAME_4096_UV_MIDPOINTS",
            "max_xyz_discrete": source_object["same_site_error"]["max_xyz"],
            "rms_source_area_discrete":
                source_object["same_site_error"]["rms_source_area"],
            "generator_face_id_correspondence_across_candidates":
                "UNQUALIFIED_DIFFERENT_OBJ_RECORD_ORDERS",
        })
    legacy = audit_eistute_reference(root)
    result = {
        "schema": SCHEMA,
        "scope": "READ_ONLY_SCIENTIFIC_SOURCE_INVENTORY_NOT_NEW_GENERATOR_EXECUTION",
        "source_experiments": 1,
        "accepted_adaptive_epochs": 0,
        "source_provenance": {
            "run_id": SOURCE_CI_RUN_ID,
            "candidate_revision": SOURCE_GENERATOR_SHA,
            "linux_artifact_id": SOURCE_LINUX_ARTIFACT_ID,
            "windows_artifact_id": SOURCE_WINDOWS_ARTIFACT_ID,
            "generator_report_sha256": SOURCE_REPORT_SHA256,
            "linux_windows_equality_recorded_at_fixture_intake_not_rechecked_here": True,
        },
        "source_objects": objects,
        "legacy_archive": legacy,
        "scientific_evidence": {
            "native_acceptance_trace_verified": False,
            "multi_patch_curve_and_face_lineage_verified": False,
            "continuous_source_error_bound_verified": False,
            "larger_accepted_source_mesh_verified": False,
            "two_independent_accepted_adaptive_epochs_verified": False,
        },
    }
    result["r28_gate"] = audit_r28_gate(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only scientific source/epoch ledger")
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None,
                        help="Optional JSON receipt path, never changes any source OBJ")
    options = parser.parse_args()
    result = build_source_epoch_inventory(options.root)
    output = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if options.output:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(output, encoding="utf-8")
    print("R2710_SOURCE_EPOCH_LEDGER=" + json.dumps({
        "source_objects": len(result["source_objects"]),
        "source_experiments": result["source_experiments"],
        "source_accepted_adaptive_epochs": result["accepted_adaptive_epochs"],
        "archived_eistute_faces": result["legacy_archive"]["triangles"],
        "eistute_historical_manifest_disagrees": True,
        "eistute_historical_manifest_explained_by_crlf": True,
        "r28_lod_eligible": result["r28_gate"]["eligible_for_r28_lod"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
