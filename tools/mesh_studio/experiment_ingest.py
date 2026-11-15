"""Versioned, fail-closed experiment provenance for real and synthetic meshes.

A manifest is a *claim* until this module verifies its referenced bytes and
independently evaluates an explicitly supported source oracle. In particular,
P1 fixed sampling does not qualify an adaptive algorithm or a factorial study.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
from pathlib import Path, PurePosixPath
import re
from typing import Any

from .import_obj import MeshImportError, import_obj
from .p1_source_oracle import (
    SOURCE_ACTIONS_RUN, SOURCE_ARTIFACT_LINUX, SOURCE_CANDIDATE,
    SOURCE_COMMIT, SOURCE_OBJ_SHA256, qualify_p1,
)
from .quality_analysis import analyze_mesh

SCHEMA = "apmesh.meshstudio.experiment_run.v1"
MAX_MANIFEST_BYTES = 256 * 1024
MAX_ARTIFACT_BYTES = 20 * 1024 * 1024
P1_REPORT_SHA256 = "1ec6d5e698b6502f117b01d9fce9f2ce9e26048b82b97484da219b747ad908d2"
SHA = re.compile(r"[0-9a-f]{64}\Z")
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
GIT_SHA = re.compile(r"[0-9a-f]{40}\Z")
TOPOLOGIES = ("tri", "quad_tri", "all_quad")
SIZING = ("isotropic", "anisotropic", "controlled_fixed16_vertex_mean_v1")
EVIDENCE = ("source_generated_ci", "source_unverified", "synthetic")
DECISIONS = ("CONTROLLED_NONADAPTIVE_OUTPUT", "SYNTHETIC_BASELINE",
             "CANDIDATE_STAGED_UNACCEPTED", "CANDIDATE_REJECTED",
             "ACCEPTED_ADAPTIVE_EPOCH")
P1_METRIC_CONTRACTS = {
    "p1_min_sampled_facet_normal_alignment_v1":
        ("dimensionless", "xyz", "120_discrete_facets_centroids"),
    "p1_max_source_xyz_component_error_v1":
        ("original_xyz_coordinate_units_unspecified", "xyz", "69_mesh_vertices"),
    "triangle_mean_ratio_3d_v1":
        ("dimensionless", "xyz", "36_native_aft_triangles"),
}


class ExperimentIngestError(ValueError):
    """A bounded provenance or numerical-scientific acceptance gate failed."""


def _require(predicate: bool, reason: str) -> None:
    if not predicate:
        raise ExperimentIngestError(reason)


def _only_fields(data: Any, fields: set[str], path: str) -> dict:
    _require(type(data) is dict, f"invalid_{path}_object")
    _require(set(data) == fields, f"invalid_{path}_fields")
    return data


def _id(value: Any, field: str) -> str:
    _require(type(value) is str and IDENTIFIER.fullmatch(value) is not None,
             f"invalid_{field}")
    return value


def _sha(value: Any, field: str, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    _require(type(value) is str and SHA.fullmatch(value) is not None,
             f"invalid_{field}")
    return value


def _finite(value: Any, field: str) -> float:
    _require(type(value) in (int, float) and math.isfinite(value), f"invalid_{field}")
    return float(value)


def _positive_int(value: Any, field: str) -> int:
    _require(type(value) is int and value > 0, f"invalid_{field}")
    return value


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    mapping = {}
    for key, value in pairs:
        _require(key not in mapping, "duplicate_json_property")
        mapping[key] = value
    return mapping


def _read_manifest(path: Path) -> tuple[dict, str]:
    _require(path.is_file() and path.stat().st_size <= MAX_MANIFEST_BYTES,
             "missing_or_oversized_experiment_manifest")
    raw = path.read_bytes()
    try:
        record = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs_no_duplicates,
                            parse_constant=lambda _: (_ for _ in ()).throw(
                                ExperimentIngestError("nonfinite_json_constant")))
    except (UnicodeError, json.JSONDecodeError, RecursionError, OverflowError) as exc:
        raise ExperimentIngestError("invalid_experiment_json") from exc
    _require(type(record) is dict, "invalid_experiment_manifest")
    return record, sha256(raw).hexdigest()


def _artifact(root: Path, claim: Any, role: str) -> Path:
    item = _only_fields(claim, {"path", "sha256"}, role)
    value = item["path"]
    _require(type(value) is str and 0 < len(value) <= 512 and "\\" not in value,
             f"invalid_{role}_path")
    _require(all(part in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_./-"
                 for part in value), f"invalid_{role}_path")
    parts = PurePosixPath(value)
    _require(not parts.is_absolute() and value == parts.as_posix() and
             all(component not in ("", ".", "..") for component in parts.parts),
             f"unsafe_{role}_path")
    # Only read files below the declared root. Never follow a symlink outside it.
    resolved = (root / value).resolve()
    _require(resolved.is_relative_to(root.resolve()), f"unsafe_{role}_path")
    _require(resolved.is_file() and resolved.stat().st_size <= MAX_ARTIFACT_BYTES,
             f"missing_or_oversized_{role}")
    actual = sha256(resolved.read_bytes()).hexdigest()
    _require(actual == _sha(item["sha256"], role + "_sha256"), f"{role}_hash_mismatch")
    return resolved


@dataclass(frozen=True)
class VerifiedRun:
    """Only obtained from a validated bundle, never from an untrusted JSON claim."""

    run_id: str
    evidence_grade: str
    method_topology: str
    sizing_policy: str
    source_model_sha256: str | None
    model_id: str
    mesh_sha256: str
    metric_rows: tuple[dict, ...]
    adaptive_accepted_epochs: int
    candidate_rejections: int
    manifest_sha256: str
    figure_comparison_eligible: bool
    warnings: tuple[str, ...]

    def as_receipt(self) -> dict:
        return {
            "schema": "apmesh.meshstudio.experiment_qualification.v1",
            "run_id": self.run_id,
            "manifest_sha256": self.manifest_sha256,
            "mesh_sha256": self.mesh_sha256,
            "evidence_grade": self.evidence_grade,
            "source_model": self.model_id,
            "source_model_sha256": self.source_model_sha256,
            "topology": self.method_topology,
            "sizing_policy": self.sizing_policy,
            "metrics": list(self.metric_rows),
            "accepted_adaptive_epochs": self.adaptive_accepted_epochs,
            "rejected_candidates": self.candidate_rejections,
            "figure_comparison_eligible": self.figure_comparison_eligible,
            "warnings": list(self.warnings),
        }


def _validate_metrics(rows: Any) -> tuple[dict, ...]:
    _require(type(rows) is list and len(rows) <= 64, "invalid_measurement_inventory")
    seen: set[str] = set()
    result = []
    for i, item in enumerate(rows):
        metric = _only_fields(item, {"id", "value", "units", "frame", "sampling",
                                     "definition_sha256", "origin"}, f"measurement_{i}")
        name = _id(metric["id"], "metric_id")
        _require(name not in seen, "duplicate_metric")
        seen.add(name)
        _finite(metric["value"], "metric_value")
        for field in ("units", "frame", "sampling", "origin"):
            _id(metric[field], field)
        _sha(metric["definition_sha256"], "metric_definition")
        _require(metric["origin"] in ("studio_derived_independent", "source_reported_unverified"),
                 "unrecognized_metric_origin")
        result.append(dict(metric))
    return tuple(sorted(result, key=lambda item: item["id"]))


def _validate_events(rows: Any, mesh_sha: str) -> tuple[int, int]:
    _require(type(rows) is list and 1 <= len(rows) <= 256, "invalid_history_inventory")
    accepted, rejected = 0, 0
    for i, row in enumerate(rows):
        event = _only_fields(row, {"event_index", "decision", "mesh_sha256",
                                   "adaptive_epoch", "trace_sha256"}, f"event_{i}")
        _require(type(event["event_index"]) is int and event["event_index"] == i,
                 "nonconsecutive_event_indices")
        _require(event["decision"] in DECISIONS, "unknown_history_decision")
        _require(event["mesh_sha256"] in (None, mesh_sha), "history_mesh_not_linked")
        _sha(event["trace_sha256"], "trace_sha256", optional=True)
        if event["decision"] == "ACCEPTED_ADAPTIVE_EPOCH":
            # A bare manifest is not a native event trace or acceptance oracle.
            raise ExperimentIngestError("adaptive_acceptance_requires_native_trace_oracle")
        _require(event["adaptive_epoch"] is None, "unverified_adaptive_epoch")
        if event["decision"] == "CANDIDATE_REJECTED":
            rejected += 1
        if event["decision"] in ("CONTROLLED_NONADAPTIVE_OUTPUT", "SYNTHETIC_BASELINE"):
            _require(i == 0, "nonbaseline_controlled_output")
        if i == 0:
            _require(event["mesh_sha256"] == mesh_sha, "baseline_mesh_not_bound")
            _require(event["decision"] in ("CONTROLLED_NONADAPTIVE_OUTPUT", "SYNTHETIC_BASELINE"),
                     "missing_nonadaptive_baseline")
    return accepted, rejected


def qualify_experiment(manifest: Path | str, *, repository_root: Path | str) -> VerifiedRun:
    """Verify source bytes, semantic inventory and supported independent oracle.

    An unknown source can be recorded as provisional, never published as a
    scientifically verified run by self-attestation in its own manifest.
    """
    root = Path(repository_root).resolve()
    record, manifest_sha = _read_manifest(Path(manifest))
    _only_fields(record, {"schema", "run_id", "method", "source_model", "execution",
                          "artifacts", "measurements", "events", "evidence"}, "run")
    _require(record["schema"] == SCHEMA, "unsupported_run_schema")
    run_id = _id(record["run_id"], "run_id")
    method = _only_fields(record["method"], {"topology", "sizing_policy"}, "method")
    topology, sizing = method["topology"], method["sizing_policy"]
    _require(topology in TOPOLOGIES and sizing in SIZING, "unsupported_method_policy")
    model = _only_fields(record["source_model"], {"id", "sha256", "identity_basis"}, "model")
    model_id = _id(model["id"], "source_model_id")
    model_sha = _sha(model["sha256"], "source_model_sha256", optional=True)
    _require(model["identity_basis"] in ("independent_control_net_oracle", "source_file_sha256",
                                         "unverified_model_identity"), "invalid_model_identity_basis")
    if model_sha is None:
        _require(model["identity_basis"] != "source_file_sha256", "missing_model_source_hash")
    execution = _only_fields(record["execution"], {"repository", "commit", "candidate_commit",
                                                   "workflow_run", "artifact_id", "platform",
                                                   "wall_seconds", "hardware"}, "execution")
    _require(execution["repository"] == "tiagosombrra/apmesh-modernization", "unknown_repository")
    _require(type(execution["commit"]) is str and GIT_SHA.fullmatch(execution["commit"]),
             "invalid_commit")
    _require(execution["candidate_commit"] is None or
             (type(execution["candidate_commit"]) is str and
              GIT_SHA.fullmatch(execution["candidate_commit"])), "invalid_candidate_commit")
    _positive_int(execution["workflow_run"], "workflow_run")
    _positive_int(execution["artifact_id"], "artifact_id")
    _id(execution["platform"], "platform")
    _id(execution["hardware"], "hardware")
    if execution["wall_seconds"] is not None:
        _require(_finite(execution["wall_seconds"], "wall_seconds") > 0,
                 "invalid_wall_seconds")
    evidence = _only_fields(record["evidence"], {"kind", "independent_oracle", "synthetic"},
                            "evidence")
    _require(evidence["kind"] in EVIDENCE and type(evidence["synthetic"]) is bool,
             "invalid_evidence_kind")
    _require(type(evidence["independent_oracle"]) is str or
             evidence["independent_oracle"] is None, "invalid_oracle_identity")
    _require(evidence["synthetic"] == (evidence["kind"] == "synthetic"),
             "synthetic_origin_contradiction")
    artifacts = _only_fields(record["artifacts"], {"mesh", "generator_report"}, "artifacts")
    mesh_file = _artifact(root, artifacts["mesh"], "mesh")
    generator_file = _artifact(root, artifacts["generator_report"], "generator_report")
    _require(mesh_file != generator_file, "same_file_as_mesh_and_report")
    try:
        document = import_obj(mesh_file)
    except (MeshImportError, UnicodeError) as exc:
        raise ExperimentIngestError("invalid_bound_mesh") from exc
    _require(document.synthetic == evidence["synthetic"], "mesh_evidence_origin_mismatch")
    _require((document.triangles > 0, document.quads > 0) ==
             {"tri": (True, False), "quad_tri": (True, True),
              "all_quad": (False, True)}[topology], "topology_inventory_mismatch")
    try:
        report = json.loads(generator_file.read_text(encoding="utf-8"),
                            object_pairs_hook=_pairs_no_duplicates)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ExperimentIngestError("invalid_generator_report") from exc
    metrics = _validate_metrics(record["measurements"])
    accepted, rejected = _validate_events(record["events"], document.source_sha256)
    if sizing == "anisotropic":
        # Future revisions must bind full source tensor data and a genuine
        # metric-field-aware algorithm oracle before calling this an experiment.
        raise ExperimentIngestError("anisotropic_field_contract_not_implemented")
    warnings = ["NO_GENERATOR_ADAPTIVE_HISTORY_QUALIFICATION",
                "NO_GLOBAL_SOURCE_SHEET_WELDING_OR_CONTINUOUS_JACOBIAN_CERTIFICATION"]
    grade = "SOURCE_PROVISIONAL_NOT_SCIENTIFICALLY_QUALIFIED"
    if evidence["kind"] == "source_generated_ci":
        _require(evidence["independent_oracle"] == "P1_BEZIER_ORACLE_PR217_V1",
                 "unsupported_claimed_independent_oracle")
        _require(execution["commit"] == SOURCE_COMMIT and
                 execution["candidate_commit"] == SOURCE_CANDIDATE and
                 execution["workflow_run"] == SOURCE_ACTIONS_RUN and
                 execution["artifact_id"] == SOURCE_ARTIFACT_LINUX and
                 execution["platform"] == "ubuntu-24.04", "p1_execution_not_bound")
        _require(model_id == "Models3d::ModelCurvaBezier" and
                 model_sha is None and
                 model["identity_basis"] == "independent_control_net_oracle" and
                 topology == "quad_tri" and sizing == "controlled_fixed16_vertex_mean_v1",
                 "p1_source_or_method_mismatch")
        _require(artifacts["generator_report"]["sha256"] == P1_REPORT_SHA256,
                 "p1_generator_report_not_original")
        _require(execution["wall_seconds"] is None and
                 execution["hardware"] == "not_recorded",
                 "p1_runtime_not_measured")
        _require(document.source_sha256 == SOURCE_OBJ_SHA256 and
                 record["events"] == [{"event_index": 0,
                                       "decision": "CONTROLLED_NONADAPTIVE_OUTPUT",
                                       "mesh_sha256": SOURCE_OBJ_SHA256,
                                       "adaptive_epoch": None, "trace_sha256": None}],
                 "p1_event_or_geometry_mismatch")
        surface = qualify_p1(document, report)["source"]
        scores = analyze_mesh(document)["measures"]["triangle_mean_ratio_3d_v1"]
        observed = {
            "p1_min_sampled_facet_normal_alignment_v1": surface["minimum_facet_normal_alignment"],
            "p1_max_source_xyz_component_error_v1": surface["max_source_xyz_component_error"],
            "triangle_mean_ratio_3d_v1": scores["mean"],
        }
        _require({m["id"] for m in metrics} == set(observed),
                 "p1_measurement_inventory_mismatch")
        for item in metrics:
            _require((item["units"], item["frame"], item["sampling"],
                      item["definition_sha256"]) ==
                     (P1_METRIC_CONTRACTS[item["id"]][0],
                      P1_METRIC_CONTRACTS[item["id"]][1],
                      P1_METRIC_CONTRACTS[item["id"]][2],
                      _definition_sha(item["id"])),
                     "p1_metric_definition_mismatch")
            _require(item["origin"] == "studio_derived_independent" and
                     math.isclose(item["value"], observed[item["id"]],
                                  rel_tol=1e-12, abs_tol=1e-14),
                     "p1_metric_not_independently_reproducible")
        grade = "REAL_P1_GEOMETRY_AND_SPECIFIED_METRICS_VERIFIED"
        warnings += ["P1_FIXED16_IS_NOT_ISOTROPIC_OR_ANISOTROPIC_ADAPTATION",
                     "BUILTIN_MODEL_HAS_NO_INDEPENDENT_FILE_SHA"]
    elif evidence["kind"] == "synthetic":
        _require(evidence["independent_oracle"] is None,
                 "synthetic_cannot_claim_real_independent_oracle")
        grade = "SYNTHETIC_ONLY_NOT_MEASURED"
        warnings.append("SYNTHETIC_FIGURES_NOT_A_SCIENTIFIC_COMPARISON")
    else:
        _require(evidence["independent_oracle"] is None,
                 "unsupported_independent_source_oracle")
        warnings.append("UNVERIFIED_SOURCE_CANNOT_POPULATE_PUBLICATION_METRICS")

    # No verified adaptive experiment is presently available from the source.
    return VerifiedRun(run_id, grade, topology, sizing, model_sha, model_id,
                       document.source_sha256, metrics, accepted, rejected,
                       manifest_sha, False, tuple(warnings))


def _definition_sha(metric_id: str) -> str:
    """Hash a fixed, public, versioned equation identity; not a runtime result."""
    definitions = {
        "p1_min_sampled_facet_normal_alignment_v1": "cos(n_facet,n_source)_at_two_quad_tri_centroids_v1",
        "p1_max_source_xyz_component_error_v1": "max_abs_XYZ_minus_original_Bezier_at_69_source_nodes_v1",
        "triangle_mean_ratio_3d_v1": "4_sqrt3_area_over_sum_squared_3d_edges_for_36_tri_v1",
    }
    return sha256(definitions[metric_id].encode("ascii")).hexdigest()


def scientific_matrix_from_qualified(runs: tuple[VerifiedRun, ...]) -> dict:
    """Expose six missing factorial cells without promoting P1 or mocks."""
    _require(len(runs) <= 256 and len({r.run_id for r in runs}) == len(runs),
             "invalid_qualified_run_set")
    grid = [{"topology": t, "sizing": s, "status": "NOT_AVAILABLE", "run_ids": []}
            for t in TOPOLOGIES for s in ("isotropic", "anisotropic")]
    excluded = []
    for run in runs:
        if run.figure_comparison_eligible:
            # A future source-oracle implementation must separately qualify
            # both source measurement and common comparison protocol.
            raise ExperimentIngestError("comparison_protocol_not_yet_certified")
        excluded.append({"run_id": run.run_id,
                         "evidence_grade": run.evidence_grade,
                         "reason": ("FIXED_SAMPLING_NOT_FACTORIAL" if
                                    run.sizing_policy == "controlled_fixed16_vertex_mean_v1"
                                    else "MISSING_QUALIFIED_COMMON_PROTOCOL")})
    return {"schema": "apmesh.meshstudio.real_experiment_matrix.v1",
            "cells": grid, "excluded_runs": excluded,
            "source_results_not_fabricated": True,
            "comparison_protocol_qualified": False}


def write_receipt(path: Path | str, result: VerifiedRun) -> None:
    """Write deterministic output only after all validations have completed."""
    Path(path).write_text(json.dumps(result.as_receipt(), indent=2, sort_keys=True,
                                     allow_nan=False, ensure_ascii=True) + "\n",
                          encoding="utf-8", newline="\n")
