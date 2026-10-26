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
import statistics
import sys

from check_compatibility import validate as validate_compatibility
from check_boundary_incidence import inspect_snapshot, reject_constant, unique_object

MESH = re.compile(r"(.+)_passo_(\d+)_malha_(\d+)\.obj$")
LOG = re.compile(r"(.+)_passo_(\d+)_acceptance_(accepted|rejected)\.log$")
# The historical OBJ and log writers round to six significant digits.
EXPORTED_QUALITY_ABS_TOLERANCE = 2e-4
# Independent arithmetic comparison budget, not a scientific quality threshold.
SNAPSHOT_QUALITY_ABS_TOLERANCE = 1e-10


class RegressionMismatch(ValueError):
    def __init__(self, report):
        self.report = report
        super().__init__(f"Strict generation regression: {len(report['differences'])} differing fields")


class BoundaryCoverageMismatch(ValueError):
    def __init__(self, report):
        self.report = report
        super().__init__("Independent boundary incidence validation failed")


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


def triangle_quality(points) -> float:
    """Compute 2r/R with scaled stable Heron arithmetic, independently of C++."""
    a, b, c = points
    lengths = sorted([math.dist(a, b), math.dist(b, c), math.dist(c, a)], reverse=True)
    scale = lengths[0]
    if scale == 0 or not math.isfinite(scale):
        raise ValueError("Invalid triangle edge lengths")
    x, y, z = (length / scale for length in lengths)
    product = (x + (y + z)) * (z - (x - y)) * (z + (x - y)) * (x + (y - z))
    if product <= 0 or z == 0 or not math.isfinite(product):
        raise ValueError("Degenerate exported triangle")
    return product / ((x + y + z) * x * y * z)


def check_quality_fields(expected: dict, row: dict, percentages: set, space: str) -> None:
    """Compare dimensionless statistics and percentages with native CSV rounding."""
    for field, value in expected.items():
        actual = float(row[field])
        low, high = value - SNAPSHOT_QUALITY_ABS_TOLERANCE, value + SNAPSHOT_QUALITY_ABS_TOLERANCE
        low = min(low, float(format(low, ".6g")))
        high = max(high, float(format(high, ".6g")))
        maximum = 100.0 if field in percentages else 1.0
        if not math.isfinite(actual) or not 0 <= actual <= maximum or not low <= actual <= high:
            raise ValueError(f"Independent {space} quality disagrees with CSV {field}")


def inspect_physical_quality(snapshot: Path, row: dict) -> dict:
    """Audit CSV quality after the snapshot passes geometry/incidence validation."""
    document = json.loads(snapshot.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_object, parse_constant=reject_constant)
    qualities, patches = [], []
    for patch in document["patches"]:
        values = [triangle_quality([corner[3:6] for corner in face[1:]])
                  for face in patch["faces"]]
        if not values:
            raise ValueError("Physical quality snapshot has an empty patch")
        qualities.extend(values)
        patches.append({"patch": patch["index"], "triangles": len(values),
                        "poor_triangles_lt_0_30": sum(q < 0.3 for q in values)})
    if not qualities:
        raise ValueError("Physical quality snapshot contains no triangles")
    distance = min(abs(q - threshold) for q in qualities for threshold in (0.3, 0.6, 0.8))
    if distance <= SNAPSHOT_QUALITY_ABS_TOLERANCE:
        raise ValueError("Physical quality threshold is numerically unresolved; counts are unqualified")
    counts = {"poor_triangles_lt_0_30": sum(q < 0.3 for q in qualities),
              "good_triangles_ge_0_60": sum(q >= 0.6 for q in qualities),
              "excellent_triangles_ge_0_80": sum(q >= 0.8 for q in qualities)}
    expected = {"quality_min": min(qualities), "quality_mean": math.fsum(qualities) / len(qualities),
                "poor_ratio_lt_0_30": 100.0 * counts["poor_triangles_lt_0_30"] / len(qualities),
                "q_ge_0_60": 100.0 * counts["good_triangles_ge_0_60"] / len(qualities),
                "excellent_ratio_ge_0_80": 100.0 * counts["excellent_triangles_ge_0_80"] / len(qualities)}
    check_quality_fields(expected, row, {"poor_ratio_lt_0_30", "q_ge_0_60", "excellent_ratio_ge_0_80"}, "physical")
    return {"triangles": len(qualities), "quality_min": expected["quality_min"],
            "quality_mean": expected["quality_mean"], "counts": counts, "patches": patches,
            "csv_fields_compared": len(expected), "minimum_threshold_distance": distance,
            "arithmetic_abs_tolerance": SNAPSHOT_QUALITY_ABS_TOLERANCE}


def parametric_triangle_quality(points) -> float:
    """Independently audit the nondegenerate domain of the native UV metric."""
    a, b, c = points
    lengths = [math.dist(a, b), math.dist(b, c), math.dist(c, a)]
    perimeter = sum(lengths)
    area = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / 2
    # The native writer returns a zero sentinel at these binary64-epsilon guards.
    # Such samples are outside this independent nondegenerate 2r/R qualification.
    if perimeter <= sys.float_info.epsilon or area <= sys.float_info.epsilon:
        raise ValueError("UV quality is outside the qualified nondegenerate metric domain")
    radius = math.prod(lengths) / (4 * area)
    if radius <= sys.float_info.epsilon:
        raise ValueError("UV quality is outside the qualified nondegenerate metric domain")
    return triangle_quality(points)


def inspect_parametric_quality(snapshot: Path, row: dict) -> dict:
    """Audit all ten UV fields after full snapshot geometry/incidence validation."""
    document = json.loads(snapshot.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_object, parse_constant=reject_constant)
    qualities, patches = [], []
    for patch in document["patches"]:
        values = [parametric_triangle_quality([corner[1:3] for corner in face[1:]])
                  for face in patch["faces"]]
        if not values:
            raise ValueError("UV quality snapshot has an empty patch")
        qualities.extend(values)
        patches.append({"patch": patch["index"], "triangles": len(values),
                        "quality_min": min(values), "quality_mean": statistics.mean(values),
                        "poor_triangles_lt_0_30": sum(q < 0.3 for q in values)})
    if not qualities:
        raise ValueError("UV quality snapshot contains no triangles")
    distance = min(abs(q - threshold) for q in qualities for threshold in (0.3, 0.6, 0.8))
    if distance <= SNAPSHOT_QUALITY_ABS_TOLERANCE:
        raise ValueError("UV quality threshold is numerically unresolved; counts are unqualified")
    ordered = sorted(qualities)

    def percentile(fraction):
        position = fraction * (len(ordered) - 1)
        lo, hi = math.floor(position), math.ceil(position)
        return ordered[lo] + (position - lo) * (ordered[hi] - ordered[lo])

    stats = {"min": ordered[0], "p05": percentile(0.05), "p50": percentile(0.5),
             "p95": percentile(0.95), "max": ordered[-1], "mean": statistics.mean(qualities),
             "std": statistics.stdev(qualities) if len(qualities) > 1 else 0.0}
    counts = {"poor_triangles_lt_0_30": sum(q < 0.3 for q in qualities),
              "good_triangles_ge_0_60": sum(q >= 0.6 for q in qualities),
              "excellent_triangles_ge_0_80": sum(q >= 0.8 for q in qualities)}
    percentages = {"quality_uv_poor_ratio_lt_0_30": 100.0 * counts["poor_triangles_lt_0_30"] / len(qualities),
                   "quality_uv_q_ge_0_60": 100.0 * counts["good_triangles_ge_0_60"] / len(qualities),
                   "quality_uv_excellent_ratio_ge_0_80": 100.0 * counts["excellent_triangles_ge_0_80"] / len(qualities)}
    expected = {**{"quality_uv_" + key: value for key, value in stats.items()}, **percentages}
    check_quality_fields(expected, row, set(percentages), "UV")
    return {"triangles": len(qualities), "statistics": stats, "counts": counts, "patches": patches,
            "csv_fields_compared": len(expected), "minimum_threshold_distance": distance,
            "arithmetic_abs_tolerance": SNAPSHOT_QUALITY_ABS_TOLERANCE}


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
        quality.append(triangle_quality((a, b, c)))
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
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("Missing or duplicate metrics header")
        rows = list(reader)
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
            if not str(error).startswith(("Compatibility is unmeasured", "Compatibility report contains no observations")):
                raise
    elif len(compatibility_paths) > 1:
        raise ValueError("Boundary compatibility report is missing or ambiguous")
    snapshots = list(root.glob("*_incidences.json"))
    incidence_reports = {}
    physical_quality = {}
    parametric_quality = {}
    coverage = "not_available_in_legacy_export"
    if snapshots:
        expected_paths = {root / f"{prefix}_passo_{step}_incidences.json" for step in meshes}
        if set(snapshots) != expected_paths:
            raise ValueError("Incidence snapshots must cover exactly every attempted state")
        model = Path(process.get("input_model", ""))
        if not model.is_file() or not process.get("input_model_sha256"):
            raise ValueError("Incidence verification requires the recorded input model identity")
        if hashlib.sha256(model.read_bytes()).hexdigest() != process["input_model_sha256"]:
            raise ValueError("Input model differs from the executed generation")
        for step, mesh in sorted(meshes.items()):
            path = root / f"{prefix}_passo_{step}_incidences.json"
            boundary = inspect_snapshot(path, model, mesh, step)
            if boundary["node_incidences"] != statistics[step]["csv_node_incidences"]:
                raise ValueError("Snapshot node incidences disagree with metrics")
            incidence_reports[step] = boundary
        if any(item["status"] != "passed" for item in incidence_reports.values()):
            raise BoundaryCoverageMismatch({"status": "failed", "model": process["model"],
                                            "boundary_incidences": incidence_reports})
        for step in sorted(meshes):
            physical_quality[step] = inspect_physical_quality(
                root / f"{prefix}_passo_{step}_incidences.json", metrics[step])
            parametric_quality[step] = inspect_parametric_quality(
                root / f"{prefix}_passo_{step}_incidences.json", metrics[step])
        coverage = ("verified" if all(item["compared_incidences"] > 0 for item in incidence_reports.values())
                    else "no_shared_boundary_comparisons")
    if require_boundary and coverage != "verified":
        if coverage == "no_shared_boundary_comparisons":
            raise ValueError("Shared-boundary incidence validation contains no comparisons")
        raise ValueError("Per-incidence boundary coverage is unavailable in the legacy export")
    # Legacy group summaries do not prove per-sheet incidence coverage.
    return {"model": process["model"], "accepted_steps": accepted, "rejected_steps": rejected,
            "source_config_sha256": process.get("source_config_sha256"),
            "last_accepted_step": accepted[-1], "meshes": statistics, "decisions": decisions,
            "stop_reason": metrics[max(decisions)]["stop_reason"], "metrics": metrics,
            "boundary_compatibility": compatibility,
            "boundary_incidence_coverage": coverage, "boundary_incidences": incidence_reports,
            "input_model_sha256": process.get("input_model_sha256"),
            "physical_quality_coverage": "full_precision_snapshot" if physical_quality else "unavailable_without_snapshot",
            "physical_quality": physical_quality,
            "parametric_quality_coverage": "full_precision_snapshot" if parametric_quality else "unavailable_without_snapshot",
            "parametric_quality": parametric_quality,
            "quality_comparison_abs_tolerance": EXPORTED_QUALITY_ABS_TOLERANCE}


def compare_runs(reference: dict, candidate: dict) -> dict:
    differences = []
    for key in ["model", "source_config_sha256", "accepted_steps", "rejected_steps", "last_accepted_step", "decisions", "metrics", "stop_reason"]:
        differences.extend(differing_fields(reference[key], candidate[key], key))
    if reference.get("input_model_sha256") and candidate.get("input_model_sha256"):
        differences.extend(differing_fields(reference["input_model_sha256"], candidate["input_model_sha256"], "input_model_sha256"))
    boundary_comparison = "not_compared_legacy_reference"
    if reference.get("boundary_incidences") and candidate.get("boundary_incidences"):
        differences.extend(differing_fields(reference["boundary_incidences"], candidate["boundary_incidences"], "boundary_incidences"))
        boundary_comparison = "exact"
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
            "boundary_incidence_coverage": candidate["boundary_incidence_coverage"],
            "boundary_regression": boundary_comparison}


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
    except (RegressionMismatch, BoundaryCoverageMismatch) as error:
        if args.report:
            args.report.write_text(json.dumps(error.report, indent=2) + "\n", encoding="utf-8", newline="\n")
        parser.exit(1, f"{error}\n")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Generation verification failed: {error}\n")
