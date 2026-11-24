#!/usr/bin/env python3
"""Screen pinned original STEP topology for source-eligible planar bicubic faces.

This is a reference-graph analysis, not a native BRep import or mesh generator.
Only exact original EDGE_CURVE identities count as topological connections.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import re

SOURCES = {
    "M5": ("i05o_m5.step", "895f67c0669096b287077ac1bb56dad0e117cd96f78334d3129d783fd78b96cb", 41, 6),
    "S40": ("i25o_s40.step", "b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b", 43, 9),
    "S27": ("i22o_s27.step", "b4a60c43cabd3c72bf61d54a23f36e6e539ad985015d2a7c377885b5d170f8c5", 52, 20),
    "M3": ("i03o_m3.step", "c42862fa6bc1e94a9bb70e43a7dc9901aa5281d7b58de6ee4699494088286008", 60, 10),
}
ENTITY = re.compile(
    r"#(\d+)\s*=\s*(?:([A-Z][A-Z_0-9]*)\s*\(([\s\S]*?)\)|\(([\s\S]*?)\))\s*;"
)
REFERENCE = re.compile(r"#(\d+)")
COORDINATES = re.compile(r"\(([-+\d.eE,\s]+)\)\s*$")
CURVE_WRAPPERS = frozenset(("SURFACE_CURVE", "SEAM_CURVE", "INTERSECTION_CURVE"))


def refs(payload: str) -> list[int]:
    return [int(n) for n in REFERENCE.findall(payload)]


def parse_entities(source: str) -> dict[int, tuple[str, str]]:
    """Read STEP entities without relying on the position or reuse of IDs."""
    if "ISO-10303-21;" not in source or "END-ISO-10303-21;" not in source:
        raise ValueError("Truncated or invalid STEP envelope")
    found = {}
    for match in ENTITY.finditer(source):
        entity_id, category = int(match[1]), match[2]
        if category is None:
            body = match[4]
            # Complex STEP entities have multiple inherited type constructors.
            category = ("COMPLEX_RATIONAL_B_SPLINE_SURFACE"
                        if "RATIONAL_B_SPLINE_SURFACE(" in body else
                        "COMPLEX_B_SPLINE_SURFACE"
                        if "B_SPLINE_SURFACE(" in body else "COMPLEX_ENTITY")
        else:
            body = match[3]
        if entity_id in found:
            raise ValueError(f"Duplicate entity ID #{entity_id}")
        found[entity_id] = (category, body)
    if not found:
        raise ValueError("STEP source has no traversable entities")
    return found


def entity(table, entity_id, expected_type=None):
    item = table.get(entity_id)
    if item is None or (expected_type is not None and item[0] != expected_type):
        raise ValueError(f"Missing or unexpected STEP entity #{entity_id}")
    return item


def curve_geometry(table, curve_id: int) -> str:
    """Resolve a SURFACE_CURVE's 3D master geometry, not its 2D PCURVE."""
    for _ in range(4):
        kind, body = entity(table, curve_id)
        if kind not in CURVE_WRAPPERS:
            return kind
        paths = refs(body)
        if not paths:
            raise ValueError("Curve wrapper missing 3D source geometry")
        curve_id = paths[0]
    raise ValueError("Curve wrapper nesting exceeds bound")


def coordinates(table, vertex_id):
    _, body = entity(table, vertex_id, "VERTEX_POINT")
    point_id = refs(body)
    if len(point_id) != 1:
        raise ValueError("Invalid vertex point reference")
    _, raw = entity(table, point_id[0], "CARTESIAN_POINT")
    match = COORDINATES.search(raw)
    if match is None:
        raise ValueError("Invalid 3D point record")
    result = tuple(float(x) for x in match[1].split(","))
    if len(result) != 3 or not all(math.isfinite(x) for x in result):
        raise ValueError("Invalid 3D Cartesian coordinates")
    return result


def oriented_edges(table, face_id):
    """Return one list of edges per oriented face bound, including inner wires."""
    _, raw = entity(table, face_id, "ADVANCED_FACE")
    ids = refs(raw)
    if len(ids) < 2:
        raise ValueError("Malformed advanced face")
    bounds, support = ids[:-1], ids[-1]
    category = entity(table, support)[0]
    wires = []
    for bound_id in bounds:
        bound_type, bound = entity(table, bound_id)
        if bound_type not in ("FACE_BOUND", "FACE_OUTER_BOUND"):
            raise ValueError("Unexpected face-bound type")
        loop_ids = refs(bound)
        if len(loop_ids) != 1:
            raise ValueError("Unexpected bound edge-loop references")
        _, wire = entity(table, loop_ids[0], "EDGE_LOOP")
        edges = []
        for occurrence in refs(wire):
            _, oriented = entity(table, occurrence, "ORIENTED_EDGE")
            original = refs(oriented)
            if len(original) != 1:
                raise ValueError("Unexpected oriented-edge reference count")
            edge_id = original[0]
            _, edge = entity(table, edge_id, "EDGE_CURVE")
            graph = refs(edge)
            if len(graph) != 3:
                raise ValueError("Malformed EDGE_CURVE")
            match = re.search(r"\.(T|F)\.\s*$", oriented)
            if match is None:
                raise ValueError("Missing oriented-edge direction")
            forward = match[1] == "T"
            edges.append({
                "edge_curve_id": edge_id,
                "start_vertex_id": graph[0] if forward else graph[1],
                "end_vertex_id": graph[1] if forward else graph[0],
                "master_3d_curve": curve_geometry(table, graph[2]),
            })
        wires.append(edges)
    return category, wires


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def geometry_gate(table, wire):
    if len(wire) != 4:
        return False, "NOT_FOUR_SIDES"
    if any(edge["master_3d_curve"] != "LINE" for edge in wire):
        return False, "NONLINE_SOURCE_EDGE"
    if any(edge["end_vertex_id"] != wire[(i+1)%4]["start_vertex_id"]
           for i, edge in enumerate(wire)):
        return False, "DISCONNECTED_ORIENTED_LOOP"
    if len({edge["start_vertex_id"] for edge in wire}) != 4:
        return False, "REPEATED_TOPOLOGICAL_VERTEX"
    points = [coordinates(table, edge["start_vertex_id"]) for edge in wire]
    maximum = max(1., *(abs(x) for p in points for x in p))
    normal = cross(sub(points[1], points[0]), sub(points[3], points[0]))
    normal_length = math.sqrt(dot(normal, normal))
    if normal_length <= 1e-14 * maximum*maximum:
        return False, "DEGENERATE_AREA"
    turns = [dot(cross(sub(points[(i+1)%4], points[i]),
                       sub(points[(i+2)%4], points[(i+1)%4])), normal)
             for i in range(4)]
    if min(turns) <= 1e-12 * normal_length * maximum*maximum:
        return False, "NONCONVEX_OR_DEGENERATE"
    distance = abs(dot(sub(points[2],points[0]), normal)) / normal_length
    if distance > 1e-8 * maximum:
        return False, "NONCOPLANAR_CORNERS"
    return True, "ELIGIBLE_SOURCE_GRAPH_ONLY"


def analyze(source_text, *, model, source_sha256):
    table = parse_entities(source_text)
    face_ids = sorted(i for i, (kind, _) in table.items() if kind == "ADVANCED_FACE")
    candidate_records, failed, support_types = [], Counter(), Counter()
    edge_face_users = defaultdict(set)
    for face_id in face_ids:
        support, wires = oriented_edges(table, face_id)
        support_types[support] += 1
        for wire in wires:
            for edge in wire:
                edge_face_users[edge["edge_curve_id"]].add(face_id)
        if support != "PLANE":
            failed["NONPLANAR_SUPPORT"] += 1
            continue
        if len(wires) != 1:
            failed["MULTIWIRE_TRIM"] += 1
            continue
        accepted, reason = geometry_gate(table, wires[0])
        if not accepted:
            failed[reason] += 1
            continue
        candidate_records.append({
            "source_advanced_face_id": face_id,
            "source_edge_curve_ids": [e["edge_curve_id"] for e in wires[0]],
            "source_oriented_vertex_ids": [e["start_vertex_id"] for e in wires[0]],
        })
    candidates = {r["source_advanced_face_id"] for r in candidate_records}
    candidate_edges = sorted({edge for rec in candidate_records for edge in rec["source_edge_curve_ids"]})
    summary = Counter()
    for edge in candidate_edges:
        owners = edge_face_users[edge]
        count = len(owners & candidates)
        if len(owners) >= 3:
            summary["UNEXPECTED_3PLUS_ORIGINAL_FACES"] += 1
        elif count == 2:
            summary["CANDIDATE_TO_CANDIDATE"] += 1
        elif len(owners) == 2:
            summary["CANDIDATE_TO_EXCLUDED"] += 1
        elif len(owners) == 1:
            summary["SOURCE_OPEN_BOUNDARY"] += 1
        else:
            summary["OTHER"] += 1
    return {
        "schema": "apmesh-s3c-step-graph-face-screen-v1",
        "scope": "PINNED_STEP_SOURCE_GRAPH_NO_NATIVE_BREP_CONVERSION",
        "model": model,
        "source_raw_sha256": source_sha256,
        "entity_count": len(table),
        "original_advanced_faces": len(face_ids),
        "source_face_support_histogram": dict(sorted(support_types.items())),
        "candidate_faces": len(candidate_records),
        "candidate_4_side_uses": sum(len(x["source_edge_curve_ids"]) for x in candidate_records),
        "candidate_distinct_original_edges": len(candidate_edges),
        "candidate_edge_neighbors": dict(sorted(summary.items())),
        "other_face_dispositions": dict(sorted(failed.items())),
        "candidate_source_entity_graph": candidate_records,
        "source_original_file_admitted_for_redistribution": False,
        "native_brep_conversion": "NOT_RUN",
        "apmesh_generation": "NOT_RUN",
        "original_external_nonmanifold_positive": "NOT_ESTABLISHED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=SOURCES, required=True)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    name, digest, expected_faces, expected_candidates = SOURCES[args.model]
    path = args.sources / name
    raw = path.read_bytes()
    actual = sha256(raw).hexdigest()
    if actual != digest:
        raise ValueError("Original STEP raw SHA-256 differs from frozen source")
    report = analyze(raw.decode("utf-8"), model=args.model, source_sha256=actual)
    if report["original_advanced_faces"] != expected_faces or report["candidate_faces"] != expected_candidates:
        raise ValueError("Original source graph does not match frozen independent observations")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "model", "original_advanced_faces", "candidate_faces", "candidate_distinct_original_edges",
        "candidate_edge_neighbors")}, sort_keys=True))


if __name__ == "__main__":
    main()
