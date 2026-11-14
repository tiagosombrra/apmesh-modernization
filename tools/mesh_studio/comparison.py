"""Scientific experiment status matrix that refuses unsupported comparisons.

The six factorial cells describe intended experiments, not completed methods.
A controlled fixed-sampling source demonstration is deliberately out of grid.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

TOPOLOGIES = ("tri", "quad_tri", "all_quad")
SIZINGS = ("isotropic", "anisotropic")
VALID_EVIDENCE = ("synthetic", "source_measured")
VALID_STATUS = ("accepted", "rejected")


@dataclass(frozen=True)
class ExperimentRun:
    run_id: str
    topology: str
    sizing: str
    evidence: str
    status: str
    source_model_id: str
    source_model_sha256: str | None
    source_mesh_sha256: str
    metric_id: str | None
    metric_value: float | None
    metric_units: str | None
    element_count: int

    def __post_init__(self) -> None:
        if not self.run_id or not self.source_model_id or self.topology not in TOPOLOGIES:
            raise ValueError("invalid_experiment_identity")
        if self.sizing not in SIZINGS or self.evidence not in VALID_EVIDENCE or self.status not in VALID_STATUS:
            raise ValueError("invalid_experiment_classification")
        hashes = (self.source_mesh_sha256,) + ((self.source_model_sha256,) if self.source_model_sha256 else ())
        if any(len(s) != 64 or any(c not in '0123456789abcdef' for c in s) for s in hashes):
            raise ValueError("invalid_experiment_sha")
        if type(self.element_count) is not int or self.element_count < 1:
            raise ValueError("invalid_element_count")
        if self.metric_value is not None and (not isinstance(self.metric_value, (float, int)) or
                                              not math.isfinite(self.metric_value)):
            raise ValueError("invalid_metric_value")
        if (self.metric_value is None) != (self.metric_id is None):
            raise ValueError("metric_id_value_mismatch")
        if self.metric_value is not None and not self.metric_units:
            raise ValueError("metric_units_required")
        if self.evidence == "source_measured" and not self.source_model_sha256:
            raise ValueError("unverified_model_source_hash")


def compare_runs(runs: tuple[ExperimentRun, ...]) -> dict:
    """Return a grid with explicit missing cells and compatible measurement groups.

    A rejected candidate is retained, but never reported as an accepted result.
    Cross-model, cross-unit, cross-definition and synthetic-vs-real differences
    are rejected before creating a numerical 'winner' or aggregate score.
    """
    if len({run.run_id for run in runs}) != len(runs):
        raise ValueError("duplicate_run_id")
    if len(runs) > 256:
        raise ValueError("experiment_limit")
    cells = []
    for topology in TOPOLOGIES:
        for sizing in SIZINGS:
            rows = [r for r in runs if r.topology == topology and r.sizing == sizing]
            accepted = [r for r in rows if r.status == "accepted"]
            cells.append({"topology": topology, "sizing": sizing,
                          "status": ("SYNTHETIC_ONLY" if accepted and
                                     all(r.evidence == "synthetic" for r in accepted)
                                     else "SOURCE_DATA_PRESENT_NOT_YET_COMPARABLE" if accepted
                                     else "REJECTED_ONLY" if rows else "NOT_AVAILABLE"),
                          "accepted_runs": [r.run_id for r in accepted],
                          "rejected_runs": [r.run_id for r in rows if r.status == "rejected"]})
    comparable = []
    for i, a in enumerate(runs):
        for b in runs[i+1:]:
            if a.status != "accepted" or b.status != "accepted":
                continue
            # A numeric contrast is allowed only for the exact same metric and
            # source input, not different TRI and QUAD shape-quality formulas.
            reasons = []
            if not a.source_model_sha256 or not b.source_model_sha256 or a.source_model_sha256 != b.source_model_sha256:
                reasons.append("source_model_unmatched")
            if a.evidence != b.evidence:
                reasons.append("synthetic_vs_real")
            if a.metric_id is None or a.metric_id != b.metric_id or a.metric_units != b.metric_units:
                reasons.append("metric_unmatched")
            if not reasons:
                comparable.append({"run_ids": [a.run_id, b.run_id],
                                   "metric_id": a.metric_id,
                                   "values": [a.metric_value, b.metric_value],
                                   "units": a.metric_units,
                                   "evidence": a.evidence})
    return {"schema": "apmesh.meshstudio.experiment_matrix.v1",
            "topology": list(TOPOLOGIES), "sizing": list(SIZINGS),
            "cells": cells, "comparable_pairs": comparable,
            "limits": ["Matching measured definitions and model hashes are mandatory.",
                       "No source run from P1 has a qualified isotropic/aniso sizing policy.",
                       "A missing result is NOT_AVAILABLE, never score zero."]}


def controlled_p1_registry(source_sha256: str) -> dict:
    """Keep real fixed16 P1 outside the six adaptive-comparison cells."""
    if len(source_sha256) != 64:
        raise ValueError("invalid_p1_hash")
    result = compare_runs(())
    result["outside_factorial_studies"] = [{
        "run_id": "P1-CONTROLLED-PR217", "source_mesh_sha256": source_sha256,
        "topology": "quad_tri", "sampling": "fixed16_vertex_mean_experimental",
        "classification": "REAL_SOURCE_GEOMETRY_NOT_COMPARABLE_SIZING_STUDY",
        "accepted_adaptive_epochs": 0, "quad": 42, "tri_aft": 36,
    }]
    return result
