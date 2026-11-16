#!/usr/bin/env python3
"""Construct canonical cubic feature curves on exact original STEP edge identities.

Research-only boundary graph. A shared curve is not an admitted BP patch,
closed atlas, original non-manifold positive, or accepted APMesh generation.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path

from s3c_step_source_gate import (
    SOURCES, COORDINATES, analyze, coordinates, curve_geometry,
    entity, oriented_edges, parse_entities, refs,
)


def _point3(table, point_id):
    kind, payload = entity(table, point_id)
    if kind not in ("CARTESIAN_POINT", "DIRECTION"):
        raise ValueError("Unsupported source line coordinate reference")
    match = COORDINATES.search(payload)
    if match is None:
        raise ValueError("Invalid source line coordinates")
    values = tuple(float(x) for x in match[1].split(","))
    if len(values) != 3 or not all(math.isfinite(x) for x in values):
        raise ValueError("Nonfinite or non-three-dimensional source line")
    return values


def _master_line(table, master_id):
    """Resolve STEP SURFACE_CURVE wrappers to its LINE and VECTOR direction."""
    for _ in range(4):
        kind, payload = entity(table, master_id)
        if kind not in ("SURFACE_CURVE", "SEAM_CURVE", "INTERSECTION_CURVE"):
            break
        master_id = refs(payload)[0]
    line_kind, line = entity(table, master_id)
    if line_kind != "LINE":
        raise ValueError("Only original exact LINE edge curves are eligible")
    line_refs = refs(line)
    if len(line_refs) != 2:
        raise ValueError("Invalid source LINE geometry")
    vec_refs = refs(entity(table, line_refs[1], "VECTOR")[1])
    if len(vec_refs) != 1:
        raise ValueError("Invalid source direction vector")
    return _point3(table, line_refs[0]), _point3(table, vec_refs[0])


def _line_residual(point, anchor, direction):
    delta = tuple(x - y for x, y in zip(point, anchor))
    sq = sum(x*x for x in direction)
    if sq <= 1e-28:
        raise ValueError("Degenerate original STEP line direction")
    scale = sum(a*b for a, b in zip(delta, direction)) / sq
    return math.dist(delta, tuple(scale*d for d in direction))


def interface_inventory(step_text, *, model, source_sha256):
    """Select exactly one eligible planar owner and one excluded source owner."""
    source_report = analyze(step_text, model=model, source_sha256=source_sha256)
    table = parse_entities(step_text)
    selected = {r["source_advanced_face_id"] for r in source_report["candidate_source_entity_graph"]}
    edge_users = defaultdict(set)
    face_support = {}
    face_edges = {}
    for face_id in sorted(i for i, (kind, _) in table.items() if kind == "ADVANCED_FACE"):
        support, wires = oriented_edges(table, face_id)
        face_support[face_id] = support
        edges = [e for wire in wires for e in wire]
        face_edges[face_id] = edges
        for edge in edges:
            edge_users[edge["edge_curve_id"]].add(face_id)
    candidate_edges = {e["edge_curve_id"] for face in selected for e in face_edges[face]}
    inventory = []
    for edge_id in sorted(candidate_edges):
        users = edge_users[edge_id]
        candidate_users = users & selected
        if len(candidate_users) != 1 or len(users) != 2:
            continue
        candidate = next(iter(candidate_users))
        neighbor = next(iter(users - selected))
        edge_kind, edge_payload = entity(table, edge_id, "EDGE_CURVE")
        arguments = refs(edge_payload)
        if len(arguments) != 3:
            raise ValueError("Invalid original edge entity")
        master_type = curve_geometry(table, arguments[2])
        if master_type != "LINE":
            raise ValueError(f"Unadmitted nonline interface edge #{edge_id}: {master_type}")
        uses = [e for e in face_edges[candidate] if e["edge_curve_id"] == edge_id]
        if len(uses) != 1:
            raise ValueError("Repeated selected face side prevents unique boundary mapping")
        canonical_vertices = arguments[:2]
        if canonical_vertices[0] == canonical_vertices[1]:
            raise ValueError("Degenerate source feature edge")
        is_forward = (uses[0]["start_vertex_id"], uses[0]["end_vertex_id"]) == tuple(canonical_vertices)
        if not is_forward and (uses[0]["end_vertex_id"], uses[0]["start_vertex_id"]) != tuple(canonical_vertices):
            raise ValueError("Selected face edge differs from canonical source edge vertices")
        inventory.append({
            "original_edge_curve_id": edge_id,
            "selected_planar_face_id": candidate,
            "excluded_neighbor_face_id": neighbor,
            "excluded_neighbor_support": face_support[neighbor],
            "source_master_3d_curve": master_type,
            "source_start_vertex_id": canonical_vertices[0],
            "source_end_vertex_id": canonical_vertices[1],
            "planar_face_uses_canonical_direction": is_forward,
            "source_master_geometry_id": arguments[2],
        })
    expected = source_report["candidate_edge_neighbors"].get("CANDIDATE_TO_EXCLUDED", 0)
    if len(inventory) != expected:
        raise ValueError("Boundary inventory differs from original face-incidence census")
    return table, source_report, inventory


def construct(step_text, *, model, source_sha256):
    """Index canonical cubic controls without coordinate-based vertex merging."""
    table, source, interfaces = interface_inventory(
        step_text, model=model, source_sha256=source_sha256)
    global_points = []
    key_to_global = {}
    records = []
    maximum_line_residual = 0.0
    for entry in interfaces:
        edge = entry["original_edge_curve_id"]
        start_id, end_id = entry["source_start_vertex_id"], entry["source_end_vertex_id"]
        a, d = coordinates(table, start_id), coordinates(table, end_id)
        if math.dist(a, d) <= 1e-14:
            raise ValueError("Coincident or degenerate original source edge endpoints")
        anchor, axis = _master_line(table, entry["source_master_geometry_id"])
        residual = max(_line_residual(a, anchor, axis), _line_residual(d, anchor, axis))
        # Kernel/source numeric consistency threshold only, never a fitting budget.
        size = max(1., *(abs(x) for x in (*a, *d, *anchor)))
        if residual > 1e-8 * size:
            raise ValueError("Original edge endpoints disagree with source master LINE")
        maximum_line_residual = max(maximum_line_residual, residual)
        control_ids = []
        for j in range(4):
            t = j/3
            point = tuple((1-t)*x + t*y for x, y in zip(a, d))
            key = ("vertex", start_id) if j == 0 else (
                ("vertex", end_id) if j == 3 else ("edge", edge, j))
            if key not in key_to_global:
                key_to_global[key] = len(global_points)
                global_points.append(point)
            index = key_to_global[key]
            if math.dist(global_points[index], point) > 1e-10 * size:
                raise ValueError("Shared topological vertex has inconsistent source coordinates")
            control_ids.append(index)
        records.append({**entry, "canonical_cubic_control_ids": control_ids,
                        "selected_face_side_control_ids": (
                            control_ids if entry["planar_face_uses_canonical_direction"]
                            else control_ids[::-1]),
                        "source_endpoint_to_master_line_residual_mm": residual})
    by_support = Counter(r["excluded_neighbor_support"] for r in records)
    graph = {
        "schema": "apmesh-s3d-canonical-source-feature-curves-v1",
        "scope": "ORIGINAL_STEP_SOURCE_GRAPH_CUBIC_BOUNDARIES_NOT_BP_SURFACE",
        "model": model,
        "source_raw_sha256": source_sha256,
        "source_face_count": source["original_advanced_faces"],
        "candidate_face_count": source["candidate_faces"],
        "candidate_to_excluded_edges": len(records),
        "neighbor_support_histogram": dict(sorted(by_support.items())),
        "source_master_edge_types": {"LINE": len(records)},
        "source_endpoint_to_master_line_max_residual_mm": maximum_line_residual,
        "global_control_points_xyz_mm": global_points,
        "feature_curves": records,
        "source_topological_identity_only": True,
        "independent_native_brep_edge_map": "NOT_RUN",
        "source_adjacent_surface_fit": "NOT_RUN",
        "complete_original_atlas": False,
        "apmesh_generation": "NOT_RUN",
        "external_nonmanifold_positive": "NOT_GRANTED",
    }
    canonical = json.dumps(graph, sort_keys=True, separators=(",", ":"))
    graph["graph_sha256"] = sha256(canonical.encode("utf-8")).hexdigest()
    return graph


def de_casteljau(controls, t):
    """Evaluate using independent recursive interpolation, not a power basis."""
    layer = [tuple(point) for point in controls]
    while len(layer) > 1:
        layer = [tuple((1-t)*x + t*y for x, y in zip(a, b))
                 for a, b in zip(layer, layer[1:])]
    return layer[0]


def audit(step_text, graph, *, expected_model, source_sha256):
    """Independently check controls against original vertex and LINE records."""
    raw = dict(graph)
    alleged = raw.pop("graph_sha256", None)
    digest = sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if alleged != digest:
        raise ValueError("Tampered feature graph checksum")
    if graph["model"] != expected_model or graph["source_raw_sha256"] != source_sha256:
        raise ValueError("Wrong source model or pinned source digest")
    table, source, inventory = interface_inventory(step_text, model=expected_model, source_sha256=source_sha256)
    indexed = {r["original_edge_curve_id"]: r for r in inventory}
    if len(graph["feature_curves"]) != len(indexed) or len(graph["feature_curves"]) != source["candidate_edge_neighbors"].get("CANDIDATE_TO_EXCLUDED", 0):
        raise ValueError("Missing or duplicated original interface")
    checked = set()
    samples = (0., 0.125, 0.25, 0.5, 0.75, 0.875, 1.)
    maximum = 0.0
    controls = graph["global_control_points_xyz_mm"]
    vertex_controls = {}
    for feature in graph["feature_curves"]:
        edge = feature["original_edge_curve_id"]
        if edge in checked or edge not in indexed:
            raise ValueError("Duplicated or foreign original source edge identity")
        checked.add(edge)
        expected = indexed[edge]
        for field, value in expected.items():
            if feature.get(field) != value:
                raise ValueError(f"Wrong exact source feature graph field: {field}")
        ids = feature["canonical_cubic_control_ids"]
        if len(ids) != 4 or len(set(ids)) != 4 or any(not isinstance(i, int) or i < 0 or i >= len(controls) for i in ids):
            raise ValueError("Invalid indexed cubic controls")
        a = coordinates(table, feature["source_start_vertex_id"])
        b = coordinates(table, feature["source_end_vertex_id"])
        for vid, control_id in ((feature["source_start_vertex_id"], ids[0]),
                                (feature["source_end_vertex_id"], ids[3])):
            if vid in vertex_controls and vertex_controls[vid] != control_id:
                raise ValueError("Shared source vertex lost its global control identity")
            vertex_controls[vid] = control_id
        wanted = ids if feature["planar_face_uses_canonical_direction"] else ids[::-1]
        if feature["selected_face_side_control_ids"] != wanted:
            raise ValueError("Incorrect reversed face-side control references")
        net = [controls[i] for i in ids]
        anchor, axis = _master_line(table, feature["source_master_geometry_id"])
        for t in samples:
            expected_xyz = tuple((1-t)*x + t*y for x, y in zip(a, b))
            actual_xyz = de_casteljau(net, t)
            maximum = max(maximum, math.dist(expected_xyz, actual_xyz))
            if _line_residual(actual_xyz, anchor, axis) > 1e-8 * max(1., *(abs(x) for x in actual_xyz)):
                raise ValueError("Curve departs from original STEP infinite LINE")
    if maximum > 5e-11 * max([1.] + [abs(v) for p in controls for v in p]):
        raise ValueError("Cubic controls deviate from exact original line segments")
    return {
        "schema": "apmesh-s3d-independent-analytic-feature-audit-v1",
        "source_model": expected_model,
        "source_edges_checked": len(indexed),
        "sample_count": len(indexed)*len(samples),
        "maximum_sampled_pointwise_residual_mm": maximum,
        "source_topological_vertex_identity": "CHECKED",
        "original_source_native_brep": "NOT_RUN",
        "adjacent_surface_control_compatibility": "NOT_RUN",
        "apmesh_generation": "NOT_RUN",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", choices=SOURCES, required=True)
    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    filename, expected_sha, expected_faces, expected_candidates = SOURCES[args.model]
    path = args.sources / filename
    raw = path.read_bytes()
    actual_sha = sha256(raw).hexdigest()
    if actual_sha != expected_sha:
        raise ValueError("Pinned raw source SHA-256 mismatch")
    text = raw.decode("utf-8")
    graph = construct(text, model=args.model, source_sha256=actual_sha)
    if graph["source_face_count"] != expected_faces or graph["candidate_face_count"] != expected_candidates:
        raise ValueError("Pinned original source model face inventory drift")
    audit_report = audit(text, graph, expected_model=args.model, source_sha256=actual_sha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(graph, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    args.output.with_suffix(".audit.json").write_text(
        json.dumps(audit_report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"model": args.model, "edges": audit_report["source_edges_checked"],
                      "maximum_mm": audit_report["maximum_sampled_pointwise_residual_mm"]}, sort_keys=True))


if __name__ == "__main__":
    main()
