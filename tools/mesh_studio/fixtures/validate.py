#!/usr/bin/env python3
"""Run a deterministic standalone fixture audit with no rendering dependencies.

The validator checks its own mathematical invariants and expected failure modes.
It is a starter fixture oracle, not a proof of the future production importer.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "cases"
EPS = 1e-14


class FixtureError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(condition, code):
    if not condition:
        raise FixtureError(code)


def parse_obj(path):
    nodes, faces = [], []
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        words = line.split()
        if words[0] == "v":
            require(len(words) == 4, "invalid_vertex_arity")
            point = [float(v) for v in words[1:]]
            require(all(math.isfinite(v) for v in point), "nonfinite_coordinate")
            nodes.append(point)
        elif words[0] == "g":
            require(len(words) == 2, "invalid_group")
            current = words[1]
        elif words[0] == "f":
            require(current is not None, "missing_face_patch")
            require(len(words) in (4, 5), "invalid_face_arity")
            ids = [int(word) - 1 for word in words[1:]]
            require(all(0 <= i < len(nodes) for i in ids), "out_of_range_index")
            require(len(set(ids)) == len(ids), "repeated_vertex")
            faces.append((current, ids))
        else:
            raise FixtureError("unexpected_obj_record")
    return nodes, faces


def uv_turn(a, b, c):
    return ((b[0] - a[0]) * (c[1] - a[1]) -
            (b[1] - a[1]) * (c[0] - a[0]))


def physical_cross(a, b, c):
    x = [b[k] - a[k] for k in range(3)]
    y = [c[k] - a[k] for k in range(3)]
    return [x[1] * y[2] - x[2] * y[1],
            x[2] * y[0] - x[0] * y[2],
            x[0] * y[1] - x[1] * y[0]]


def verify_data(data, nodes, faces):
    require(data["synthetic"] is True and data["schema"] ==
            "apmesh.meshstudio.synthetic.v1", "missing_synthetic_label")
    require(len(nodes) == data["expected"]["node_count"], "node_count")
    require(len(faces) == len(data["faces"]), "face_count")
    require(nodes == data["nodes"], "obj_sidecar_xyz_mismatch")
    actual_counts = Counter("triangle" if len(f[1]) == 3 else "quad" for f in faces)
    require(actual_counts["triangle"] == data["expected"]["triangle_count"]
            and actual_counts["quad"] == data["expected"]["quad_count"],
            "element_count")
    for (_, face_ids), semantic in zip(faces, data["faces"]):
        require(semantic["nodes"] == face_ids and
                semantic["patch_id"] == _ and
                len(semantic["uv"]) == len(face_ids), "face_sidecar_mismatch")
        uv = semantic["uv"]
        require(all(math.isfinite(c) for pair in uv for c in pair),
                "nonfinite_uv")
        if len(uv) == 3:
            require(uv_turn(*uv) > EPS, "uv_winding")
            pieces = [(0, 1, 2)]
        else:
            require(all(uv_turn(uv[k], uv[(k + 1) % 4], uv[(k + 2) % 4]) > EPS
                        for k in range(4)), "concave_uv")
            pieces = [(0, 1, 2), (0, 2, 3)]
        for part in pieces:
            geom = [nodes[face_ids[k]] for k in part]
            normal = physical_cross(*geom)
            require(math.hypot(*normal) > EPS, "degenerate_physical_facet")
            reference = data.get("reference_normal")
            if reference is not None:
                require(sum(normal[k] * reference[k] for k in range(3)) > EPS,
                        "inverted_physical_facet")
    # Check indexed patch-local edge incidence and observer-independent owners.
    patch_points = defaultdict(set)
    edge_owners = defaultdict(list)
    for (_, face_ids), semantic in zip(faces, data["faces"]):
        patch_id = semantic["patch_id"]
        patch_points[patch_id].update(face_ids)
        for i in range(len(face_ids)):
            a, b = face_ids[i], face_ids[(i + 1) % len(face_ids)]
            edge = tuple(sorted((a, b)))
            edge_owners[(patch_id, edge)].append((a, b, semantic["kind"]))
    owner_by_point = {}
    for patch_id, ids in patch_points.items():
        for index in ids:
            require(index not in owner_by_point, "cross_patch_node_alias")
            owner_by_point[index] = patch_id
    for records in edge_owners.values():
        require(1 <= len(records) <= 2, "nonmanifold_patch_edge")
        if len(records) == 2:
            require(records[0][0] == records[1][1] and
                    records[0][1] == records[1][0], "incorrect_shared_edge_winding")
    if data["case_id"] == "synthetic_quad_aft_transition":
        boundary = sum(len(records) == 1 for records in edge_owners.values())
        seams = sum(len(records) == 2 and
                    {records[0][2], records[1][2]} == {"quad", "triangle"}
                    for records in edge_owners.values())
        require(boundary == 4 and seams == 4, "quad_aft_seam_inventory")
        require(len(nodes) - len(edge_owners) + len(faces) == 1,
                "quad_aft_patch_euler")
    if data["case_id"] == "synthetic_curved_bezier_grid":
        require(all(abs(z - (.2 * u * u + .1 * v * v)) <= 1e-14
                    for u, v, z in nodes), "analytic_bezier_xyz")
    for curve in data.get("curves", []):
        canonical = curve["canonical_xyz"]
        require(len(curve["sample_parameters"]) == len(canonical),
                "shared_curve_sample_count")
        for patch_id in curve["incident_patches"]:
            points = curve["by_patch_xyz"][patch_id]
            require(len(points) == len(canonical) and all(
                math.dist(a, b) <= 1e-10 for a, b in zip(points, canonical)),
                "shared_curve_mismatch")
        require(curve["topology_weld_approved"] is False,
                "synthetic_curve_welding_misrepresented")
    return True


def validate_case(path):
    record = json.loads(path.read_text(encoding="utf-8"))
    obj = path.with_suffix(".obj")
    digest = hashlib.sha256(obj.read_bytes()).hexdigest()
    assert digest == record["obj_sha256"], path
    try:
        nodes, faces = parse_obj(obj)
        verify_data(record, nodes, faces)
        observed = None
    except FixtureError as exc:
        observed = exc.code
    expected = record["expected"]
    assert (observed is None) == expected["valid"], (path.name, observed, expected)
    assert observed == expected["diagnostic"], (path.name, observed, expected)
    return record["case_id"], observed


def validate_experiments():
    p = ROOT / "experiments" / "synthetic_nonmonotone_epochs.csv"
    with p.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 8
    groups = defaultdict(list)
    for row in rows:
        assert row["synthetic"] == "True"
        assert row["acceptance"] in ("accepted", "rejected")
        assert math.isfinite(float(row["normalized_error"]))
        groups[row["method"]].append(row)
    assert set(groups) == {"tri", "hybrid"}
    for group in groups.values():
        assert len(group) == 4
        assert [int(r["epoch"]) for r in group] == [0, 1, 2, 3]
        assert group[2]["acceptance"] == "rejected"
        assert float(group[2]["normalized_error"]) > float(group[1]["normalized_error"])
        assert float(group[3]["normalized_error"]) < float(group[1]["normalized_error"])
    return True


def main():
    registry = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    ids = [r["case_id"] for r in registry["fixture_cases"]]
    assert len(ids) == len(set(ids)) == len(list(CASES.glob("*.obj")))
    expected_diagnostics = {r["case_id"]: r["expected"]["diagnostic"]
                            for r in registry["fixture_cases"]}
    report = [validate_case(CASES / f"{case_id}.json") for case_id in ids]
    assert dict(report) == expected_diagnostics
    assert validate_experiments()
    good = sum(code is None for _, code in report)
    bad = len(report) - good
    assert good == 10 and bad == 6, (good, bad)
    print(f"fixture_audit=PASS valid={good} negative={bad} total={len(report)} "
          f"experiment_rows=8 synthetic_only=true")


if __name__ == "__main__":
    main()
