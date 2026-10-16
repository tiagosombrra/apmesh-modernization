#!/usr/bin/env python3
"""Independently verify every patch boundary against BP controls and actual faces."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys

# These budgets cover arithmetic evaluation and t -> 1-t round trips only.
# They are unrelated to meshing tolerances or scientific acceptance thresholds.
PARAMETER_ROUNDTRIP_BUDGET = 4 * sys.float_info.epsilon
EVALUATION_ROUNDOFF_FACTOR = 512 * sys.float_info.epsilon
SIDES = ((0, 1, 2, 3), (3, 7, 11, 15), (12, 13, 14, 15), (0, 4, 8, 12))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate snapshot field: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Non-finite JSON constant: {value}")


def read_model(path):
    """Preserve BP record order; never infer input identity from proximity."""
    vertices, patches = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split("#", 1)[0].split("//", 1)[0].split()
        if not fields:
            continue
        if fields[0] == "v":
            require(len(fields) == 4, "Invalid BP vertex")
            point = tuple(float(x) for x in fields[1:])
            require(all(math.isfinite(x) for x in point), "Non-finite BP control")
            vertices.append(point)
        elif fields[0] == "p":
            require(len(fields) == 17, "Invalid BP patch")
            indices = [int(x) for x in fields[1:]]
            require(all(0 <= i < len(vertices) for i in indices), "Invalid BP reference")
            patches.append(tuple(vertices[i] for i in indices))
        else:
            raise ValueError("Unsupported BP record")
    require(patches, "BP has no patches")
    return patches


def finite_row(row, size):
    return (isinstance(row, list) and len(row) == size
            and all(type(x) in (int, float) and math.isfinite(x) for x in row))


def identifier(value):
    return type(value) is int and value >= 0


def bezier(controls, parameter):
    """De Casteljau is independent of the application's power-basis evaluator."""
    points = list(controls)
    while len(points) > 1:
        points = [tuple((1 - parameter) * x + parameter * y for x, y in zip(a, b))
                  for a, b in zip(points, points[1:])]
    return points[0]


def inspect_snapshot(snapshot: Path, model: Path, obj: Path, step: int) -> dict:
    document = json.loads(snapshot.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_object, parse_constant=reject_constant)
    require(isinstance(document, dict), "Invalid snapshot document")
    require(document.get("schema") == "apmesh-incidence-v1", "Unknown incidence schema")
    require(type(document.get("step")) is int and document["step"] == step,
            "Snapshot stage does not match mesh/decision stage")
    source = read_model(model)
    patches = document.get("patches")
    require(isinstance(patches, list) and len(patches) == len(source),
            "Snapshot does not cover every source patch")
    expected_vertices, expected_faces = [], []
    for line in obj.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if fields and fields[0] == "v":
            expected_vertices.append(tuple(float(x) for x in fields[1:]))
        elif fields and fields[0] == "f":
            expected_faces.append(tuple(int(x) for x in fields[1:]))

    issues = Counter()
    examples = []

    def issue(kind, **detail):
        issues[kind] += 1
        if len(examples) < 20:
            examples.append({"kind": kind, **detail})

    groups = defaultdict(list)
    runtime_groups = defaultdict(set)
    logical_groups = defaultdict(set)
    global_nodes, global_positions = {}, {}
    obj_vertices, obj_faces = [], []
    node_incidences = boundary_segments = reversed_incidences = 0
    max_curve_error = max_shared_gap = 0.0
    for index, (patch, controls) in enumerate(zip(patches, source)):
        require(isinstance(patch, dict), "Invalid patch record")
        require(patch.get("index") == index and type(patch["index"]) is int,
                "Missing, duplicate or reordered patch incidence")
        exported_controls = patch.get("control_points")
        require(isinstance(exported_controls, list) and len(exported_controls) == 16
                and all(finite_row(row, 3) for row in exported_controls),
                "Invalid exported patch controls")
        if tuple(map(tuple, exported_controls)) != controls:
            issue("source_control_mismatch", patch=index)
        curves = patch.get("curves")
        require(isinstance(curves, list) and len(curves) == 4 and all(map(identifier, curves)),
                "Missing or invalid curve incidence")
        nodes, uv = {}, {}
        require(isinstance(patch.get("nodes"), list) and patch["nodes"], "Missing patch nodes")
        for row in patch["nodes"]:
            require(finite_row(row, 4) and identifier(row[0]), "Invalid node record")
            node, *position = row
            require(node not in nodes, "Duplicate node identity inside a patch")
            nodes[node] = tuple(position)
            node_incidences += 1
            if node in global_positions and global_positions[node] != tuple(position):
                issue("global_node_identity_position_mismatch", patch=index, node=node)
            if node not in global_nodes:
                global_nodes[node] = len(obj_vertices) + 1
                global_positions[node] = tuple(position)
                # Match the legacy writer's six-significant-digit serialization.
                obj_vertices.append(tuple(float(format(x, ".6g")) for x in position))
        edges = Counter()
        require(isinstance(patch.get("faces"), list) and patch["faces"], "Missing patch faces")
        for face_index, face in enumerate(patch["faces"]):
            require(isinstance(face, list) and len(face) == 4 and type(face[0]) is int
                    and face[0] == face_index, "Invalid or missing patch face")
            ids = []
            for corner in face[1:]:
                require(finite_row(corner, 6) and identifier(corner[0]), "Invalid triangle corner")
                node, u, v, x, y, z = corner
                require(node in nodes and nodes[node] == (x, y, z), "Face/node coordinate mismatch")
                require(0 <= u <= 1 and 0 <= v <= 1, "Parametric coordinate outside the patch")
                require(node not in uv or uv[node] == (u, v), "Inconsistent UV for one patch node")
                uv[node] = (u, v)
                ids.append(node)
            require(len(set(ids)) == 3, "Repeated patch triangle node")
            obj_faces.append(tuple(global_nodes[node] for node in ids))
            for a, b in zip(ids, ids[1:] + ids[:1]):
                edges[tuple(sorted((a, b)))] += 1
        require(set(uv) == set(nodes), "Patch has unreferenced nodes")
        sides = [[] for _ in range(4)]
        for (a, b), count in edges.items():
            require(count <= 2, "Non-manifold edge inside one patch")
            if count != 1:
                continue
            ua, va = uv[a]
            ub, vb = uv[b]
            slots = [slot for slot, matches in enumerate((va == vb == 0, ua == ub == 1,
                                                          va == vb == 1, ua == ub == 0)) if matches]
            require(len(slots) == 1, "Patch has an interior hole or ambiguous boundary edge")
            slot = slots[0]
            ta, tb = (ua, ub) if slot in (0, 2) else (va, vb)
            require(ta != tb, "Zero-length parametric boundary segment")
            sides[slot].append((ta, tb, a, b) if ta < tb else (tb, ta, b, a))
        for slot, offsets in enumerate(SIDES):
            side_controls = tuple(controls[i] for i in offsets)
            canonical = min(side_controls, side_controls[::-1])
            reverse = canonical != side_controls
            reversed_incidences += int(reverse)
            runtime_groups[curves[slot]].add(canonical)
            logical_groups[canonical].add(curves[slot])
            segments = sorted(sides[slot])
            require(segments and segments[0][0] == 0 and segments[-1][1] == 1,
                    "Boundary incidence does not cover [0,1]")
            require(all(a[1] == b[0] and a[3] == b[2] for a, b in zip(segments, segments[1:])),
                    "Boundary incidence has a gap, overlap or disconnected node")
            sequence = [(segments[0][0], nodes[segments[0][2]])]
            sequence.extend((segment[1], nodes[segment[3]]) for segment in segments)
            scale = max(1.0, *(abs(x) for point in side_controls for x in point))
            budget = EVALUATION_ROUNDOFF_FACTOR * scale
            for t, position in sequence:
                error = max(abs(a - b) for a, b in zip(position, bezier(side_controls, t)))
                max_curve_error = max(max_curve_error, error)
                if error > budget:
                    issue("off_source_boundary", patch=index, slot=slot, parameter=t,
                          error=error, roundoff_budget=budget)
            if reverse:
                sequence = [(1 - t, position) for t, position in sequence[::-1]]
            groups[canonical].append((index, slot, sequence, budget))
            boundary_segments += len(segments)
    require(obj_vertices == expected_vertices and obj_faces == expected_faces,
            "Incidence snapshot disagrees with actual OBJ vertices/faces")
    for runtime_id, keys in runtime_groups.items():
        if len(keys) != 1:
            issue("runtime_curve_merges_different_source_boundaries", runtime_curve=runtime_id)
    for key, runtime_ids in logical_groups.items():
        if len(runtime_ids) != 1:
            issue("runtime_shared_curve_split", runtime_curves=sorted(runtime_ids))
    comparisons = shared_groups = nonmanifold_groups = shared_incidences = 0
    reversed_shared_incidences = mixed_orientation_groups = 0
    max_incidence = 0
    for canonical, incidences in groups.items():
        max_incidence = max(max_incidence, len(incidences))
        if len(incidences) < 2:
            continue
        shared_groups += 1
        shared_incidences += len(incidences)
        nonmanifold_groups += int(len(incidences) > 2)
        orientations = [tuple(source[patch][i] for i in SIDES[slot]) != canonical
                        for patch, slot, _, _ in incidences]
        reversed_shared_incidences += sum(orientations)
        mixed_orientation_groups += int(any(orientations) and not all(orientations))
        first = incidences[0][2]
        for patch, slot, sequence, budget in incidences[1:]:
            comparisons += 1
            if len(sequence) != len(first):
                issue("shared_partition_count_mismatch", patch=patch, slot=slot,
                      expected_nodes=len(first), actual_nodes=len(sequence))
                continue
            for (t, point), (reference_t, reference_point) in zip(sequence, first):
                if abs(t - reference_t) > PARAMETER_ROUNDTRIP_BUDGET:
                    issue("shared_parameter_mismatch", patch=patch, slot=slot,
                          parameter=t, reference_parameter=reference_t)
                gap = max(abs(a - b) for a, b in zip(point, reference_point))
                max_shared_gap = max(max_shared_gap, gap)
                if gap > budget:
                    issue("shared_position_mismatch", patch=patch, slot=slot,
                          gap=gap, roundoff_budget=budget)
    return {"status": "failed" if issues else "passed", "step": step,
            "patches": len(patches), "incidences": len(patches) * 4,
            "curve_groups": len(groups), "shared_groups": shared_groups,
            "shared_incidences": shared_incidences, "compared_incidences": comparisons,
            "nonmanifold_groups": nonmanifold_groups, "max_curve_incidence": max_incidence,
            "reversed_incidences": reversed_incidences, "boundary_segments": boundary_segments,
            "reversed_shared_incidences": reversed_shared_incidences,
            "mixed_orientation_groups": mixed_orientation_groups,
            "node_incidences": node_incidences, "triangles": len(obj_faces),
            "max_curve_error": max_curve_error, "max_shared_gap": max_shared_gap,
            "parameter_roundtrip_budget": PARAMETER_ROUNDTRIP_BUDGET,
            "evaluation_roundoff_factor": EVALUATION_ROUNDOFF_FACTOR,
            "issues": dict(issues), "examples": examples,
            "snapshot_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
            "input_model_sha256": hashlib.sha256(model.read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--obj", type=Path, required=True)
    parser.add_argument("--step", type=int, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = inspect_snapshot(args.snapshot, args.model, args.obj, args.step)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({k: v for k, v in report.items() if k != "examples"}))
        raise SystemExit(0 if report["status"] == "passed" else 1)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"Boundary incidence verification failed: {error}\n")
