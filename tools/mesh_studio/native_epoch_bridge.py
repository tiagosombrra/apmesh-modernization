"""R2.7.11 read-only bridge from original native TRI acceptance to Mesh Studio.

This rechecks pinned archived reports and actual source branches. It neither runs
GeneratorAdaptive nor claims an independently replayed adaptive epoch.
"""

from __future__ import annotations

from hashlib import sha1, sha256
import argparse
import json
from pathlib import Path

from .source_epoch_inventory import build_source_epoch_inventory

SCHEMA = "apmesh.meshstudio.r2711.native_epoch_evidence_bridge.v1"
BASE = Path("docs/research/quad/evidence")
R2C13 = BASE / "R2C13_REAL_GENERATOR_ACCEPTED_EPOCHS_20261113.json"
R2C14 = BASE / "R2C14_ORIGINAL_GENERATOR_REJECTION_FORENSICS_20261113.json"
SOURCE = Path("src/generator/generator_adaptive.cpp")
OUTCOME = Path("research/quad/global_outcome.h")
PINNED_BLOBS = {
    str(R2C13): "9572f0b8951138e757f8c83df5b9999c4073831e",
    str(R2C14): "2259281b8b16bbd8a089c7f2805b7676dd252082",
    str(SOURCE): "e0d1edd28968a684edba1e6c11a72b54e07e283a",
    str(OUTCOME): "ddac6497d4e05b23e0da1448ca59ea427ea18b1a",
}
SOURCE_RUN = 43502743922
SOURCE_COMMIT = "082ecd0408d31808dae5d629e711be99fd01d1a7"
FORENSICS_RUN = 43504972443
EXPECTED = {
    "eistute": {
        "patches": 4, "curves": 13,
        "source_sha256": "fdce4714524b88f536ec9f8eddc467e54e638dc6e765784ab68edc9a366a0a3f",
        "source_config": "configs/eistute/article.conf",
        "accepted_commits": 1, "rejected_restored": 3,
        "source_boundary_witnesses": 960,
    },
    "book": {
        "patches": 28, "curves": 85,
        "source_sha256": "3c4255cbd2f46bd2dce5f0e86b8e7ee9ac0c58df949d4563dd821deedcd8412d",
        "source_config": "configs/book/article.conf",
        "accepted_commits": 1, "rejected_restored": 2,
        "source_boundary_witnesses": 1008,
    },
}


class NativeEpochBridgeError(ValueError):
    """Archived source native-evidence contract was changed or overclaimed."""


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise NativeEpochBridgeError(reason)


def verified_bytes(root: Path, path: Path) -> tuple[str, str]:
    """Verify canonical Git blob even if a Windows checkout rewrites EOL bytes."""
    file = root / path
    require(file.is_file() and file.stat().st_size <= 600_000,
            "missing_or_oversized_pinned_file_" + str(path))
    disk = file.read_bytes()
    require(b"\0" not in disk, "unexpected_binary_pinned_file")
    normalized = disk.replace(b"\r\n", b"\n")
    require(b"\r" not in normalized, "unsupported_source_line_ending")
    head = b"blob " + str(len(normalized)).encode("ascii") + b"\0"
    blob = sha1(head + normalized).hexdigest()
    require(blob == PINNED_BLOBS[str(path)],
            "pinned_git_blob_changed_" + str(path))
    return normalized.decode("utf-8"), sha256(normalized).hexdigest()


def pinned_json(root: Path, path: Path) -> tuple[dict, str]:
    text, digest = verified_bytes(root, path)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate_json_field_" + str(path))
            result[key] = value
        return result
    data = json.loads(text, object_pairs_hook=unique)
    require(type(data) is dict, "invalid_archived_json")
    return data, digest


def audit_native_source(original: str, outcome: str) -> dict:
    """Locate actual existing branch hooks; do not infer runtime execution from text."""
    commit = original.find("accepted_mesh = accepted_scope.Commit();")
    accepted = original.find("GlobalOutcomeKind::AcceptedStepCommitted")
    # Multiple restorations can occur earlier during candidate retries. Only
    # inspect the rejection arm *after* the current accepted-commit branch.
    rejected_arm = original.find("if (!accepted_step) {", accepted)
    restore_domain = original.find(
        "restore_geometry_submeshes(geometry, accepted_mesh);", rejected_arm
    )
    restore_curve = original.find(
        "restore_curve_snapshots(geometry, accepted_curve_snapshots);", restore_domain
    )
    rejected = original.find(
        "GlobalOutcomeKind::RejectedStepRestored", restore_curve
    )
    acceptance_branch = original.rfind(
        "if (score_ok || small_mesh_progress_override)", 0, commit
    )
    require(all(i >= 0 for i in (commit, accepted, restore_domain, restore_curve,
                                  rejected, acceptance_branch, rejected_arm)),
            "missing_native_acceptance_or_restore_anchor")
    require(acceptance_branch < commit < accepted < rejected_arm <
            restore_domain < restore_curve < rejected,
            "native_commit_restore_event_sequence_changed")
    require(accepted - commit < 800 and rejected - restore_curve < 800,
            "native_event_no_longer_near_lifecycle_boundary")
    require(original.count("accepted_mesh = accepted_scope.Commit();") == 1 and
            original.count("GlobalOutcomeKind::AcceptedStepCommitted") == 1 and
            original.count("GlobalOutcomeKind::RejectedStepRestored") == 1,
            "nonunique_native_commit_or_restore_event")
    require("void Record(GlobalOutcomeEvent event) noexcept" in outcome and
            "truncated_ = true;" in outcome and
            "using GlobalOutcomeLog = BoundedGlobalOutcomeLog<128>;" in outcome,
            "native_bounded_log_truncation_contract_changed")
    return {
        "scope": "PINNED_NATIVE_SOURCE_STATIC_HOOK_AUDIT_NOT_NEW_RUNTIME_EXECUTION",
        "acceptance_uses_native_accepted_mesh_scope_commit": True,
        "accepted_outcome_recorded_after_commit": True,
        "rejected_outcome_recorded_after_domain_and_curve_restoration": True,
        "event_log_capacity": 128,
        "event_log_truncation_observable": True,
        "original_cpp_file": str(SOURCE),
    }


def audit_native_obj_identity_gap(source: str) -> dict:
    """Establish why original OBJ ordinal is not a canonical generator face ID."""
    first = source.find("void GeneratorAdaptive::WriteMesh(MeshAdaptive* malha, int step_) {")
    next_writer = source.find(
        "void GeneratorAdaptive::WriteMesh(MeshAdaptive* malha, int step_,",
        first + 1,
    )
    require(first >= 0 and next_writer > first,
            "original_obj_writer_overload_missing")
    writer = source[first:next_writer]
    require("node_index[n->GetId()] = next_index++;" in writer and
            'obj << "v "' in writer and 'obj << "f "' in writer and
            "TriangleAdaptive* t = (TriangleAdaptive*)sub->GetElement(j);" in writer,
            "original_obj_writer_structure_changed")
    require("t->GetId()" not in writer and
            "sub->GetPatch()" not in writer and
            'obj << "g "' not in writer,
            "original_obj_writer_provenance_revised_reaudit_required")
    # Native C++ interfaces own IDs, but they are not written to OBJ face records.
    return {
        "scope": "FIRST_LEGACY_TRI_OBJ_WRITER_SOURCE_AUDIT",
        "generator_node_id_used_for_output_vertex_deduplication": True,
        "generator_element_face_id_serialized": False,
        "per_face_source_patch_id_serialized": False,
        "per_face_source_curve_identity_serialized": False,
        "obj_face_position_equals_native_source_element_id": False,
        "new_opt_in_native_identity_sidecar_required": True,
    }


def audit_archived_r2c13(original: dict) -> dict:
    require(original.get("schema") ==
            "apmesh.quad.r2c13.m7.genuine_generator_accepted_epochs.v1",
            "archived_acceptance_schema_changed")
    require(original.get("pr_head") == SOURCE_COMMIT and
            original.get("workflow_run_id") == SOURCE_RUN and
            original.get("actual_two_accepted_epochs_qualified") is False,
            "archived_source_run_identity_or_gate_changed")
    run = original.get("native_execution_this_turn", {})
    require(run.get("commit") == SOURCE_COMMIT and
            run.get("run_id") == SOURCE_RUN and
            run.get("conclusion") == "success" and
            run.get("jobs") == "4/4" and
            run.get("artifact_id") == 14074978033 and
            run.get("root_linux_ctest") == "89/89" and
            run.get("python_tooling") == "527/527",
            "native_r2c13_run_claim_changed")
    source_models = original.get("original_scenarios")
    require(type(source_models) is list and len(source_models) == 2,
            "missing_original_model_pair")
    measured = original.get("measured_models")
    require(type(measured) is list and len(measured) == 2,
            "missing_native_generator_model_measurements")
    inventory = {}
    for scenario, row in zip(source_models, measured):
        name = scenario.get("model")
        require(name in EXPECTED and row.get("name") == name and
                name not in inventory, "native_model_pair_order_or_identity_changed")
        expected = EXPECTED[name]
        require(scenario.get("source") == expected["source_config"] and
                scenario.get("expected_sha256") == expected["source_sha256"] and
                scenario.get("original_patches") == expected["patches"] and
                scenario.get("curves") == expected["curves"],
                "original_model_source_or_patch_curve_claim_changed_" + name)
        actual = row.get("pinned_article", {})
        require(actual.get("accepted_commits") == 1 and
                actual.get("rejected_restored") == expected["rejected_restored"] and
                actual.get("distinct_accepted_epochs") == [1] and
                actual.get("accepted_original_curves") == expected["curves"] and
                actual.get("source_boundary_witnesses") ==
                expected["source_boundary_witnesses"] and
                row.get("two_accepted_epochs") is False,
                "native_accepted_epoch_overclaim_" + name)
        inventory[name] = {
            "original_source_config": expected["source_config"],
            "original_model_sha256": expected["source_sha256"],
            "original_source_patches": expected["patches"],
            "original_source_curves": expected["curves"],
            "original_patch_boundary_witnesses":
                expected["source_boundary_witnesses"],
            "archived_committed_steps": [1],
            "archived_committed_count": actual["accepted_commits"],
            "archived_rejected_restored_count": actual["rejected_restored"],
            "source": "ARCHIVED_ORIGINAL_NATIVE_CI_R2C13_NOT_REPLAYED_THIS_RUN",
            "two_accepted_epochs_per_model_qualified": False,
        }
    require(set(inventory) == set(EXPECTED),
            "incomplete_native_model_pair")
    return inventory


def audit_archived_r2c14(forensics: dict) -> dict:
    require(forensics.get("schema") ==
            "apmesh.quad.r2c14.actual_original_generator_rejection_forensics.v1" and
            forensics.get("accepted_two_original_generator_epochs") is False,
            "forensics_adaptive_gate_claim_changed")
    ci = forensics.get("exact_ci", {})
    parent = forensics.get("qualified_predecessor", {})
    require(ci.get("run_id") == FORENSICS_RUN and
            ci.get("conclusion") == "success" and
            parent.get("commit") == SOURCE_COMMIT and
            parent.get("run_id") == SOURCE_RUN and
            parent.get("actual_two_accepted_source_epochs") is False,
            "forensics_run_lineage_changed")
    original = forensics.get("measured_rejections", {})
    require(original.get("eistute", {}).get("pinned", {}).get("step4", {}).get("growth")
            == 6.17808 and
            original.get("book", {}).get("pinned", {}).get("step2", {}).get("growth")
            == 4.64615,
            "forensics_rejected_candidate_metrics_changed")
    return {
        "native_forensics_ci_run": FORENSICS_RUN,
        "reason_scope": "ARCHIVED_SOURCE_REJECTION_FORENSICS_NOT_ORIGINAL_GATE_BOOLEAN_REPLAY",
        "eistute_step4_rejected_growth": 6.17808,
        "book_step2_rejected_growth": 4.64615,
        "accepted_second_epochs_qualified": False,
    }


def build_native_epoch_bridge(root: Path) -> dict:
    root = root.resolve()
    source, source_digest = verified_bytes(root, SOURCE)
    outcome, outcome_digest = verified_bytes(root, OUTCOME)
    r2c13, r2c13_digest = pinned_json(root, R2C13)
    r2c14, r2c14_digest = pinned_json(root, R2C14)
    source_hooks = audit_native_source(source, outcome)
    native_models = audit_archived_r2c13(r2c13)
    forensics = audit_archived_r2c14(r2c14)
    be = build_source_epoch_inventory(root)
    require(be["accepted_adaptive_epochs"] == 0 and
            be["source_experiments"] == 1 and
            be["r28_gate"]["eligible_for_r28_lod"] is False,
            "p1_candidate_adaptation_was_promoted")
    return {
        "schema": SCHEMA,
        "scope": "PINNED_ORIGINAL_NATIVE_CI_ARCHIVE_BRIDGE_NO_REEXECUTION",
        "original_native_source_ci": {
            "run": SOURCE_RUN,
            "original_generator_commit": SOURCE_COMMIT,
            "archived_artifact_id": 14074978033,
            "archived_status": "success",
            "verified_against_new_remote_ci_in_this_run": False,
        },
        "pinned_source_byte_hashes": {
            "generator_cpp_git_blob_sha1": PINNED_BLOBS[str(SOURCE)],
            "generator_cpp_normalized_sha256": source_digest,
            "outcome_header_git_blob_sha1": PINNED_BLOBS[str(OUTCOME)],
            "outcome_header_normalized_sha256": outcome_digest,
            "native_r2c13_evidence_sha256": r2c13_digest,
            "native_r2c14_evidence_sha256": r2c14_digest,
        },
        "source_code_lifecycle": source_hooks,
        "legacy_native_obj_identity_gap": audit_native_obj_identity_gap(source),
        "original_models": native_models,
        "original_generator_rejections": forensics,
        "other_experiment_not_conflated": {
            "bezier_p2d1c3_source_experiments": be["source_experiments"],
            "bezier_p2d1c3_accepted_adaptive_epochs": be["accepted_adaptive_epochs"],
            "eistute_stage4_reference": "SAVED_HISTORICAL_REJECTED_CANDIDATE",
            "archived_eistute_step4_stop_reason":
                be["legacy_archive"]["archived_csv_stop_reason"],
        },
        "qualification": {
            "original_tri_single_accepted_epoch_in_archived_report": True,
            "original_tri_two_accepted_epochs_per_model": False,
            "new_native_execution_in_this_run": False,
            "canonical_cross_epoch_generator_face_ids": False,
            "verified_shared_curve_multipatch_node_welding": False,
            "continuous_error_bounds": False,
            "scientific_r28_geometry_lod_admitted": False,
        },
        "next_native_evidence_required": [
            "REEXECUTE_ORIGINAL_NATIVE_SERIAL_ADAPTATION_WITH_TYPED_ACCEPT_RESTORE_EVENTS",
            "MATCH_ACTUAL_ACCEPTED_STEP_MESH_SHA_TO_SOURCE_FACE_AND_PATCH_IDS",
            "OBTAIN_AT_LEAST_TWO_DISTINCT_NATIVE_COMMITTED_EPOCHS_PER_MODEL",
            "RECORD_SOURCE_CURVE_ORIENTATION_AND_PATCH_OWNERSHIP_FOR_SHARED_SHEETS",
            "VERIFY_CONTINUOUS_GEOMETRIC_ERROR_BOUND_NOT_ONLY_SAMPLED_METRIC",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit pinned original TRI native CI against Mesh Studio source")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    report = build_native_epoch_bridge(options.root)
    if options.output is not None:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R2711_NATIVE_EPOCH_BRIDGE=" + json.dumps({
        "models": list(report["original_models"]),
        "archived_committed_steps": {k: v["archived_committed_steps"]
                                     for k, v in report["original_models"].items()},
        "original_models_two_commits": False,
        "native_run_replayed_this_ci": False,
        "bezier_p2d1c3_accepted_epochs": 0,
        "r28_admitted": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
