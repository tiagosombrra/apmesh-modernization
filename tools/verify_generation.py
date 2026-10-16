#!/usr/bin/env python3
"""Validate generated accepted states without treating attempted artifacts as accepted."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import re

from check_compatibility import validate as validate_compatibility

MESH = re.compile(r"(.+)_passo_(\d+)_malha_(\d+)\.obj$")
LOG = re.compile(r"(.+)_passo_(\d+)_acceptance_(accepted|rejected)\.log$")
# The historical OBJ and log writers round to six significant digits.
EXPORTED_QUALITY_ABS_TOLERANCE = 2e-4


class RegressionMismatch(ValueError):
    def __init__(self, report):
        self.report = report
        super().__init__(f"Strict generation regression: {len(report['differences'])} differing fields")


def differing_fields(left, right, path=""):
    if isinstance(left, dict) and isinstance(right, dict):
        result = []
        for key in sorted(set(left) | set(right), key=str):
            result.extend(differing_fields(left.get(key), right.get(key), f"{path}.{key}"))
        return result
    return [] if left == right else [{"field": path.lstrip("."), "reference": left, "candidate": right}]


def read_acceptance(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in values:
            raise ValueError(f"Duplicate acceptance field {key}: {path.name}")
        values[key] = value
    return values


def inspect_mesh(path: Path) -> dict:
    """Recompute finite coordinates, connectivity and 2r/R from exported geometry."""
    vertices, faces = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if not fields or fields[0].startswith("#"):
            continue
        if fields[0] == "v":
            if len(fields) != 4:
                raise ValueError("Expected exactly three OBJ vertex coordinates")
            point = tuple(float(x) for x in fields[1:])
            if not all(math.isfinite(x) for x in point):
                raise ValueError("Non-finite OBJ coordinate")
            vertices.append(point)
        elif fields[0] == "f":
            if len(fields) != 4:
                raise ValueError("Only triangular faces are valid in this regression")
            face = tuple(int(x) for x in fields[1:])
            if len(set(face)) != 3 or min(face) < 1:
                raise ValueError("Invalid or repeated OBJ face index")
            faces.append(face)
        else:
            raise ValueError(f"Unsupported OBJ record: {fields[0]}")
    if not vertices or not faces:
        raise ValueError("Mesh is empty")
    if len({tuple(sorted(face)) for face in faces}) != len(faces):
        raise ValueError("Duplicate triangular face")
    quality, edges = [], Counter()
    for face in faces:
        if max(face) > len(vertices):
            raise ValueError("OBJ face index is out of bounds")
        a, b, c = (vertices[index - 1] for index in face)
        lengths = sorted([math.dist(a, b), math.dist(b, c), math.dist(c, a)], reverse=True)
        scale = lengths[0]
        if scale == 0 or not math.isfinite(scale):
            raise ValueError("Invalid triangle edge lengths")
        x, y, z = (length / scale for length in lengths)
        # Stable Heron formula is independent of the generator's cross-product path.
        product = (x + (y + z)) * (z - (x - y)) * (z + (x - y)) * (x + (y - z))
        if product <= 0 or z == 0:
            raise ValueError("Degenerate exported triangle")
        quality.append(product / ((x + y + z) * x * y * z))
        for i, j in [(face[0], face[1]), (face[1], face[2]), (face[2], face[0])]:
            edges[tuple(sorted((i, j)))] += 1
    return {"vertices": len(vertices), "triangles": len(faces),
            "quality_min_3d": min(quality), "quality_mean_3d": math.fsum(quality) / len(quality),
            "boundary_edges_by_index": sum(count == 1 for count in edges.values()),
            "nonmanifold_edges_by_index": sum(count > 2 for count in edges.values()),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def require_accepted_artifact(mesh: Path) -> dict:
    match = MESH.fullmatch(mesh.name)
    if not match or match[2] != match[3]:
        raise ValueError("Mesh name does not identify a consistent adaptive stage")
    prefix, step = match[1], int(match[2])
    logs = list(mesh.parent.glob(f"{prefix}_passo_{step}_acceptance_*.log"))
    if len(logs) != 1:
        raise ValueError("Accepted artifact needs exactly one final acceptance log")
    values = read_acceptance(logs[0])
    if values.get("step") != str(step) or values.get("accepted") != "1" or not logs[0].name.endswith("_accepted.log"):
        raise ValueError(f"Stage {step} is rejected or lacks accepted-state evidence")
    return inspect_mesh(mesh)


def verify_run(root: Path, *, required_step: int | None = None, require_boundary: bool = False) -> dict:
    process = json.loads((root / "process.json").read_text(encoding="utf-8"))
    if process.get("status") != "completed" or process.get("exit_code") != 0:
        raise ValueError("Generation did not complete successfully")
    meshes, prefixes = {}, set()
    for path in root.glob("*.obj"):
        match = MESH.fullmatch(path.name)
        if not match or match[2] != match[3] or int(match[2]) in meshes:
            raise ValueError("Ambiguous or inconsistent mesh stage")
        prefixes.add(match[1])
        meshes[int(match[2])] = path
    if not meshes or len(prefixes) != 1:
        raise ValueError("Expected exactly one generated model with nonempty mesh coverage")
    prefix = prefixes.pop()
    decisions = {}
    for path in root.glob("*acceptance*.log"):
        match = LOG.fullmatch(path.name)
        if not match or match[1] != prefix or int(match[2]) in decisions:
            raise ValueError("Ambiguous or unrelated acceptance evidence")
        step, state = int(match[2]), match[3]
        values = read_acceptance(path)
        if values.get("step") != str(step) or values.get("accepted") != ("1" if state == "accepted" else "0"):
            raise ValueError("Acceptance filename and fields disagree")
        if state == "accepted" and values.get("budget_final_status") == "rejected":
            raise ValueError("Contradictory accepted and rejected status")
        decisions[step] = {"state": state, "fields": values}
    if set(decisions) != set(meshes) or set(decisions) != set(range(max(meshes) + 1)):
        raise ValueError("Incomplete mesh/acceptance trace")
    accepted = sorted(step for step, item in decisions.items() if item["state"] == "accepted")
    rejected = sorted(set(decisions) - set(accepted))
    if not accepted or 0 not in accepted:
        raise ValueError("Initial accepted state is missing")
    if required_step is not None and required_step not in accepted:
        raise ValueError(f"Requested stage {required_step} is absent or rejected")
    metrics_paths = list(root.glob("*metrics*.csv"))
    if len(metrics_paths) != 1:
        raise ValueError("Expected one serial accepted-state metrics file")
    with metrics_paths[0].open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    metrics = {int(row["step"]): row for row in rows}
    if len(metrics) != len(rows) or set(metrics) != set(decisions):
        raise ValueError("Metrics must cover exactly the attempted states")
    statistics = {step: inspect_mesh(path) for step, path in meshes.items()}
    for step in sorted(decisions):
        stats, row = statistics[step], metrics[step]
        if None in row or any(value is None for value in row.values()):
            raise ValueError("Malformed metrics CSV row")
        if any(value.lower() in {"nan", "+nan", "-nan", "inf", "+inf", "-inf"} for value in row.values()):
            raise ValueError("Metrics contain non-finite numerical values")
        # CSV sums submesh-node incidences; OBJ writes unique node IDs.
        # Triangle counts have the same meaning in both formats.
        stats["csv_node_incidences"] = int(row["nodes"])
        if stats["vertices"] > stats["csv_node_incidences"] or stats["triangles"] != int(row["elements"]):
            raise ValueError("Attempted mesh counts disagree with metrics")
        if decisions[step]["state"] == "accepted" and row.get("budget_final_status") == "rejected":
            raise ValueError("Metrics contradict accepted-state evidence")
        fields = decisions[step]["fields"]
        # Stage 0 writes a legacy zero placeholder before candidate counters exist.
        # Its counts are independently checked against OBJ and CSV above.
        if step > 0 and "actual_elements_step" in fields and int(float(fields["actual_elements_step"])) != stats["triangles"]:
            raise ValueError("Mesh disagrees with logged candidate element count")
        for name in ["quality_min_3d", "quality_mean_3d"]:
            logged = float(fields[name])
            if not math.isfinite(logged) or abs(logged - stats[name]) > EXPORTED_QUALITY_ABS_TOLERANCE:
                raise ValueError(f"Independent exported {name} disagrees with acceptance log")
    compatibility = "unmeasured"
    compatibility_paths = list(root.glob("*_compatibility_summary.csv"))
    if len(compatibility_paths) == 1:
        try:
            validate_compatibility(compatibility_paths[0])
            compatibility = "legacy_summary_measured"
        except ValueError as error:
            if require_boundary or not str(error).startswith(("Compatibility is unmeasured", "Compatibility report contains no observations")):
                raise
    elif require_boundary:
        raise ValueError("Boundary compatibility report is missing or ambiguous")
    if require_boundary:
        raise ValueError("Per-incidence boundary coverage is unavailable in the legacy export")
    # Legacy group summaries do not prove per-sheet incidence coverage.
    return {"model": process["model"], "accepted_steps": accepted, "rejected_steps": rejected,
            "source_config_sha256": process.get("source_config_sha256"),
            "last_accepted_step": accepted[-1], "meshes": statistics, "decisions": decisions,
            "stop_reason": metrics[max(decisions)]["stop_reason"], "metrics": metrics,
            "boundary_compatibility": compatibility,
            "boundary_incidence_coverage": "not_available_in_legacy_export",
            "quality_comparison_abs_tolerance": EXPORTED_QUALITY_ABS_TOLERANCE}


def compare_runs(reference: dict, candidate: dict) -> dict:
    differences = []
    for key in ["model", "source_config_sha256", "accepted_steps", "rejected_steps", "last_accepted_step", "decisions", "metrics", "stop_reason"]:
        differences.extend(differing_fields(reference[key], candidate[key], key))
    if set(reference["meshes"]) != set(candidate["meshes"]):
        raise ValueError("Generated mesh coverage changed")
    for step in reference["meshes"]:
        differences.extend(differing_fields(reference["meshes"][step]["sha256"],
                                             candidate["meshes"][step]["sha256"], f"mesh.{step}.sha256"))
    if differences:
        raise RegressionMismatch({"model": reference["model"], "status": "failed",
                                  "differences": differences,
                                  "all_obj_byte_identical": all(reference["meshes"][step]["sha256"] == candidate["meshes"][step]["sha256"] for step in reference["meshes"]),
                                  "accepted_rejected_steps_equal": reference["accepted_steps"] == candidate["accepted_steps"] and reference["rejected_steps"] == candidate["rejected_steps"]})
    return {"model": reference["model"], "compared_meshes": len(reference["meshes"]),
            "all_obj_byte_identical": True, "all_acceptance_fields_equal": True,
            "last_accepted_step": candidate["last_accepted_step"],
            "last_accepted_triangles": candidate["meshes"][candidate["last_accepted_step"]]["triangles"],
            "boundary_incidence_coverage": candidate["boundary_incidence_coverage"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--require-accepted-step", type=int)
    parser.add_argument("--require-boundary-coverage", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = verify_run(args.run, required_step=args.require_accepted_step,
                            require_boundary=args.require_boundary_coverage)
        if args.baseline:
            report = compare_runs(verify_run(args.baseline), report)
        if args.report:
            args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(report))
    except RegressionMismatch as error:
        if args.report:
            args.report.write_text(json.dumps(error.report, indent=2) + "\n", encoding="utf-8", newline="\n")
        parser.exit(1, f"{error}\n")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Generation verification failed: {error}\n")
