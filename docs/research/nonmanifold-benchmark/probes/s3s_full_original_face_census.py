#!/usr/bin/env python3
"""S3.S: certify original S40 STEP/native topology and classify atlas gaps.

This is a source-identity research diagnostic, not a new patch or mesh generator.
Third-party STEP bytes and derived control coordinates are never emitted.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepTools import BRepTools
from s3c_step_source_gate import SOURCES, analyze, coordinates, curve_geometry, entity, oriented_edges, parse_entities, refs
from s3e_native_feature_bijection import SUPPORT_MAP
from original_cad_planar_atlas import same_index

SOURCE_MODEL = "S40"
SOURCE_REVISION = "8f00f02579037cc893042f2ee2c910b20e3fb1b0"
ADMITTED_CURVED_FACE_IDS = frozenset((2882, 2936, 2990, 3127, 1986, 1519, 2457, 218))
S3R_EXPECTED_PATCHES = 126
S3R_EXPECTED_SOURCE_FACES = 17
S3R_JOIN_SHA = "98ff4cbfad08ce3f587607fddf3bb5e1a3697e1513a8ca86889bb28406e4028d"
SUPPORT_TO_NATIVE = {**SUPPORT_MAP,
    "B_SPLINE_SURFACE_WITH_KNOTS": "BSPLINE",
    "COMPLEX_RATIONAL_B_SPLINE_SURFACE": "BSPLINE",
    "COMPLEX_B_SPLINE_SURFACE": "BSPLINE"}
EDGE_TO_NATIVE = {"LINE": "LINE", "CIRCLE": "CIRCLE",
    "B_SPLINE_CURVE_WITH_KNOTS": "BSPLINE", "COMPLEX_B_SPLINE_CURVE": "BSPLINE",
    "ELLIPSE": "ELLIPSE", "BEZIER_CURVE": "BEZIER"}
POSITION_TOL_MM = 1e-6


def _hex_digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False).encode("utf-8")).hexdigest()


def source_gate(raw: bytes, *, model: str = SOURCE_MODEL) -> tuple[str, str]:
    """Admit exactly the frozen original source bytes before native import."""
    if model != SOURCE_MODEL:
        raise ValueError("S3.S only accepts frozen original S40")
    actual = sha256(raw).hexdigest()
    if actual != SOURCES[SOURCE_MODEL][1]:
        raise ValueError("Original S40 raw SHA-256 mismatch")
    return raw.decode("utf-8"), actual


def _native_positions(edge):
    return [(v.Center().x, v.Center().y, v.Center().z)
            for v in edge.Vertices()]


def _compatible_vertices(source_a, source_b, native_points, tol):
    if len(native_points) == 1:
        return (math.dist(native_points[0], source_a) <= tol
                and math.dist(native_points[0], source_b) <= tol)
    if len(native_points) != 2:
        return False
    return ((math.dist(native_points[0], source_a) <= tol
             and math.dist(native_points[1], source_b) <= tol)
            or (math.dist(native_points[0], source_b) <= tol
                and math.dist(native_points[1], source_a) <= tol))


def _has_bijection(source_edges, native_edges, edge_candidates):
    """Require a unique-edge-per-side assignment on one native face."""
    if len(source_edges) != len(native_edges):
        return False
    native = set(native_edges)
    options = {key: set(edge_candidates[key]) & native for key in source_edges}
    if any(not value for value in options.values()) or set().union(*options.values()) != native:
        return False
    ordered = sorted(source_edges, key=lambda e: (len(options[e]), e))

    def walk(index, used):
        if index == len(ordered):
            return True
        return any(walk(index + 1, used | {n}) for n in sorted(options[ordered[index]] - used))

    return walk(0, set())


def _source_graph(table):
    faces = {}
    edge_owners, source_edges, vertex_edges = defaultdict(set), {}, defaultdict(set)
    for face_id, (kind, _) in table.items():
        if kind != "ADVANCED_FACE":
            continue
        support, wires = oriented_edges(table, face_id)
        faces[face_id] = (support, wires)
        for wire in wires:
            for row in wire:
                edge_id = row["edge_curve_id"]
                edge_owners[edge_id].add(face_id)
                source_edges.setdefault(edge_id, row)
                vertex_edges[row["start_vertex_id"]].add(edge_id)
                vertex_edges[row["end_vertex_id"]].add(edge_id)
    return faces, edge_owners, source_edges, vertex_edges


def _native_graph(native):
    nfaces, nedges, nvertices = native.Faces(), native.Edges(), native.Vertices()
    face_edges, edge_owners, vertex_edges = [], defaultdict(set), defaultdict(set)
    for face_id, face in enumerate(nfaces):
        edges = {same_index(nedges, edge) for edge in face.Edges()}
        if None in edges:
            raise ValueError("Native face references an edge outside native global BRep")
        face_edges.append(edges)
        for edge in edges:
            edge_owners[edge].add(face_id)
    for eid, edge in enumerate(nedges):
        for v in edge.Vertices():
            vid = same_index(nvertices, v)
            if vid is None:
                raise ValueError("Native edge vertex not in global BRep identity table")
            vertex_edges[vid].add(eid)
    return nfaces, nedges, nvertices, face_edges, edge_owners, vertex_edges


def full_correspondence(source_text, native, *, tol=POSITION_TOL_MM):
    """Close source/native face, edge and vertex bijections using topology.

    Geometric endpoint screening alone cannot distinguish original circular
    STEP edges #378/#1991. Full face-edge incidence resolves them uniquely.
    Any remaining ambiguity or collision stops the audit.
    """
    if not native.isValid():
        raise ValueError("Imported native BRep invalid")
    table = parse_entities(source_text)
    faces, owners, source_edges, source_vertex_edges = _source_graph(table)
    nfaces, nedges, nvertices, face_edges, native_owners, native_vertex_edges = _native_graph(native)
    if len(faces) != 43 or len(nfaces) != 43:
        raise ValueError("Original face census mismatch")
    candidates = {}
    for eid, record in source_edges.items():
        kind = EDGE_TO_NATIVE.get(record["master_3d_curve"])
        if kind is None:
            raise ValueError("Unsupported source master curve kind on original S40")
        p = coordinates(table, record["start_vertex_id"])
        q = coordinates(table, record["end_vertex_id"])
        possibilities = [i for i, e in enumerate(nedges)
                         if e.geomType() == kind and _compatible_vertices(
                             p, q, _native_positions(e), tol)]
        if not possibilities:
            raise ValueError(f"No native candidate for original EDGE_CURVE #{eid}")
        candidates[eid] = possibilities
    source_to_native_faces = {}
    for sid, (support, wires) in faces.items():
        etype = SUPPORT_TO_NATIVE.get(support)
        if etype is None:
            raise ValueError(f"Unsupported original surface type {support}")
        source_ids = sorted({e["edge_curve_id"] for wire in wires for e in wire})
        source_wire_counts = sorted(len(wire) for wire in wires)
        possibilities = []
        for fid, face in enumerate(nfaces):
            if face.geomType() != etype:
                continue
            if sorted(len(wire.Edges()) for wire in face.Wires()) != source_wire_counts:
                continue
            if _has_bijection(source_ids, face_edges[fid], candidates):
                possibilities.append(fid)
        if len(possibilities) != 1:
            raise ValueError(f"Original face #{sid} has {len(possibilities)} unique native matches")
        source_to_native_faces[sid] = possibilities[0]
    if len(set(source_to_native_faces.values())) != len(nfaces):
        raise ValueError("Original/native face mapping is not injective")

    edge_mapping = {}
    for eid, original_owners in owners.items():
        mapped_owners = {source_to_native_faces[sid] for sid in original_owners}
        unique = [nid for nid in candidates[eid] if native_owners[nid] == mapped_owners]
        if len(unique) != 1:
            raise ValueError(f"Original edge #{eid} has {len(unique)} native matches after incidence")
        edge_mapping[eid] = unique[0]
    if len(edge_mapping) != len(nedges) or len(set(edge_mapping.values())) != len(nedges):
        raise ValueError("Source/native EDGE_CURVE is not bijective")
    for sid, (_, wires) in faces.items():
        original = {e["edge_curve_id"] for w in wires for e in w}
        if {edge_mapping[e] for e in original} != face_edges[source_to_native_faces[sid]]:
            raise ValueError("Face source/native edge-set certificate mismatch")

    vertex_mapping = {}
    for sid, original_edge_ids in source_vertex_edges.items():
        position = coordinates(table, sid)
        mapped_edges = {edge_mapping[eid] for eid in original_edge_ids}
        possible = [i for i, v in enumerate(nvertices)
                    if math.dist(position, (v.Center().x, v.Center().y, v.Center().z)) <= tol
                    and native_vertex_edges[i] == mapped_edges]
        if len(possible) != 1:
            raise ValueError(f"Original VERTEX_POINT #{sid} has {len(possible)} native matches")
        vertex_mapping[sid] = possible[0]
    if len(vertex_mapping) != len(nvertices) or len(set(vertex_mapping.values())) != len(nvertices):
        raise ValueError("Original/native VERTEX_POINT is not bijective")

    return {"source_faces": faces, "source_edges": source_edges, "owners": owners,
            "face_map": source_to_native_faces, "edge_map": edge_mapping,
            "vertex_map": vertex_mapping, "table": table,
            "native_faces": nfaces, "native_edges": nedges,
            "initial_geometrically_ambiguous_source_edge_ids": sorted(
                eid for eid, matches in candidates.items() if len(matches) > 1)}


def _pcurve_kinds(table, edge_id, support_id):
    """Inspect STEP face-side PCURVEs without exporting geometric controls."""
    _, raw = entity(table, edge_id, "EDGE_CURVE")
    curve_id = refs(raw)[2]
    kind, body = entity(table, curve_id)
    if kind not in ("SURFACE_CURVE", "SEAM_CURVE", "INTERSECTION_CURVE"):
        return []
    kinds = []
    for pid in refs(body)[1:]:
        if entity(table, pid)[0] != "PCURVE":
            continue
        support, representation = refs(entity(table, pid)[1])
        if support != support_id:
            continue
        kinds.append(entity(table, refs(entity(table, representation)[1])[0])[0])
    return kinds


def represented_source_faces(source_text, joined_bp: bytes, manifest: dict):
    """Crosscheck frozen S3.R BP source coverage against source candidates."""
    if sha256(joined_bp).hexdigest() != S3R_JOIN_SHA:
        raise ValueError("Original S3.R BP SHA-256 mismatch")
    if manifest.get("joined_bp_sha256") != S3R_JOIN_SHA or manifest.get("joined_patch_count") != S3R_EXPECTED_PATCHES:
        raise ValueError("Original S3.R manifest mismatch")
    if manifest.get("source_sha256") != SOURCES[SOURCE_MODEL][1]:
        raise ValueError("S3.R manifest has incorrect original STEP SHA")
    if not manifest.get("source_inner_hole_retained"):
        raise ValueError("S3.R source inner hole is not certified retained")
    if manifest.get("source_original_face_coverage") != S3R_EXPECTED_SOURCE_FACES:
        raise ValueError("S3.R original face coverage changed")
    screen = analyze(source_text, model=SOURCE_MODEL, source_sha256=SOURCES[SOURCE_MODEL][1])
    planar = {x["source_advanced_face_id"] for x in screen["candidate_source_entity_graph"]}
    if len(planar) != 9 or planar & ADMITTED_CURVED_FACE_IDS:
        raise ValueError("Original admitted planar source set is not frozen")
    if len(planar | ADMITTED_CURVED_FACE_IDS) != S3R_EXPECTED_SOURCE_FACES:
        raise ValueError("Source atlas face inventory does not equal original S3.R claim")
    return planar | ADMITTED_CURVED_FACE_IDS


def _classification(info, represented):
    """Reproducible heuristic ranking, not a patch-acceptance criterion."""
    support = info["support_type"]
    strips = info["source_boundary_edge_count"]
    holes = info["inner_wire_count"]
    splines = info["3d_bspline_edge_count"] + info["parametric_bspline_occurrences"]
    connected = info["incident_represented_edge_count"]
    score = (60 if support == "PLANE" else 40 if support == "CYLINDRICAL_SURFACE"
             else 15 if support in ("CONICAL_SURFACE", "TOROIDAL_SURFACE", "SPHERICAL_SURFACE")
             else 5)
    score += 7 * min(connected, 4)
    score -= 2 * max(0, strips - 4)
    score -= 15 * holes
    score -= 5 * splines
    score -= 6 * info["3d_circle_edge_count"]
    if info["source_wire_count"] > 2:
        score -= 20 * (info["source_wire_count"] - 2)
    return score


def classify(source_text, native, bp: bytes, manifest: dict):
    """Produce a non-geometric original-S40 26-face risk and priority inventory."""
    digest = sha256(source_text.encode("utf-8")).hexdigest()
    if digest != SOURCES[SOURCE_MODEL][1]:
        raise ValueError("Original S40 digest mismatch")
    represented = represented_source_faces(source_text, bp, manifest)
    mapping = full_correspondence(source_text, native)
    original_faces, source_edges, owners, faces = (mapping["source_faces"],
        mapping["source_edges"], mapping["owners"], mapping["native_faces"])
    if len(original_faces) - len(represented) != 26:
        raise ValueError("Original S40 excluded-face count changed")
    face_adjacency = defaultdict(set)
    for edge_owners in owners.values():
        for a in edge_owners:
            face_adjacency[a].update(edge_owners - {a})
    distance = {sid: 0 for sid in represented}
    pending = deque(sorted(represented))
    while pending:
        current = pending.popleft()
        for neighbor in sorted(face_adjacency[current]):
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                pending.append(neighbor)
    if len(distance) != len(original_faces):
        raise ValueError("Original source shell contains faces disconnected from atlas")
    unrepresented = []
    for sid, (support, wires) in sorted(original_faces.items()):
        if sid in represented:
            continue
        edgeids = {e["edge_curve_id"] for wire in wires for e in wire}
        incident = [(e, other) for e in sorted(edgeids) for other in sorted(owners[e] - {sid})]
        used_neighbor_edges = sorted(e for e, n in incident if n in represented)
        non3d = Counter(e["master_3d_curve"] for wire in wires for e in wire)
        support_id = refs(entity(mapping["table"], sid, "ADVANCED_FACE")[1])[-1]
        pcurves = Counter(p for wire in wires for e in wire
                         for p in _pcurve_kinds(mapping["table"], e["edge_curve_id"], support_id))
        nf = faces[mapping["face_map"][sid]]
        outer = BRepTools.OuterWire_s(nf.wrapped)
        num_inner = sum(not w.wrapped.IsSame(outer) for w in nf.Wires())
        row = {
            "source_advanced_face_id": sid,
            "native_face_index": mapping["face_map"][sid],
            "support_type": support,
            "native_support_type": nf.geomType(),
            "source_wire_count": len(wires),
            "source_wire_edge_counts": [len(wire) for wire in wires],
            "source_boundary_edge_count": sum(len(wire) for wire in wires),
            "inner_wire_count": num_inner,
            "3d_master_curve_histogram": dict(sorted(non3d.items())),
            "3d_bspline_edge_count": sum(v for k, v in non3d.items() if "SPLINE" in k),
            "3d_circle_edge_count": non3d.get("CIRCLE", 0),
            "pcurve_histogram": dict(sorted(pcurves.items())),
            "parametric_bspline_occurrences": sum(v for k, v in pcurves.items() if "SPLINE" in k),
            "incident_represented_face_ids": sorted({n for e, n in incident if n in represented}),
            "incident_represented_original_edge_curve_ids": used_neighbor_edges,
            "incident_represented_edge_count": len(used_neighbor_edges),
            "incident_unrepresented_face_ids": sorted({n for e, n in incident if n not in represented}),
            "incident_unrepresented_edge_count": sum(1 for e, n in incident if n not in represented),
            "minimum_original_edge_hops_from_represented_atlas": distance[sid],
            "native_brep_has_valid_face_shape": bool(nf.isValid()),
            "candidate_admission_status": "NOT_GENERATED_AND_NOT_AUDITED",
        }
        row["research_priority_score_heuristic"] = _classification(row, represented)
        unrepresented.append(row)
    unrepresented.sort(key=lambda r: (-r["research_priority_score_heuristic"], r["source_advanced_face_id"]))
    for i, row in enumerate(unrepresented):
        row["research_priority_ordinal_not_a_scientific_rank"] = i + 1
    histogram = Counter(x["support_type"] for x in unrepresented)
    distance_histogram = Counter(str(x["minimum_original_edge_hops_from_represented_atlas"]) for x in unrepresented)
    covered = sum(x["incident_represented_edge_count"] > 0 for x in unrepresented)
    report = {
        "schema": "apmesh-s3s-s40-full-original-source-native-gap-census-v1",
        "source": "cgg-bern/hex-me-if-you-can/original/i25o_s40.step",
        "source_revision": SOURCE_REVISION,
        "source_raw_sha256": digest,
        "s3r_baseline_bp_sha256": S3R_JOIN_SHA,
        "baseline_integrated_patches": S3R_EXPECTED_PATCHES,
        "baseline_represented_original_face_count": len(represented),
        "baseline_original_face_ids": sorted(represented),
        "original_source_face_count": len(original_faces),
        "native_face_count": len(faces),
        "original_source_native_bijective_face_count": len(mapping["face_map"]),
        "original_source_native_bijective_edge_count": len(mapping["edge_map"]),
        "original_source_native_bijective_vertex_count": len(mapping["vertex_map"]),
        "original_same_endpoint_ambiguous_edges_disambiguated_by_incidence": mapping["initial_geometrically_ambiguous_source_edge_ids"],
        "max_original_source_edge_owner_count": max(len(s) for s in owners.values()),
        "original_source_multi_sheet_nonmanifold_3plus": sum(len(s) >= 3 for s in owners.values()),
        "excluded_original_face_count": len(unrepresented),
        "excluded_support_histogram": dict(sorted(histogram.items())),
        "excluded_minimum_source_edge_hops_histogram": dict(sorted(distance_histogram.items())),
        "excluded_faces_with_direct_indexed_atlas_adjacency": covered,
        "excluded_faces_without_direct_indexed_atlas_adjacency": len(unrepresented) - covered,
        "classified_original_faces": unrepresented,
        "priority_policy": "HEURISTIC_ONLY; prioritizes source-edge adjacency and fewer curved/spline boundary constraints; not geometry acceptance",
        "new_patches_generated": 0,
        "s3r_atlas_mutated": False,
        "apmesh_tri_quad_meshing": "NOT_RUN",
        "production_cpp_regression": "NOT_RUN",
    }
    report["report_sha256"] = _hex_digest(report)
    return report


def audit_report(source_text, native, bp, manifest, report):
    """Reject modified or stale receipts by complete independent recomputation."""
    supplied = deepcopy(report)
    checksum = supplied.pop("report_sha256", None)
    if checksum != _hex_digest(supplied):
        raise ValueError("S3.S receipt checksum mismatch")
    if report != classify(source_text, native, bp, manifest):
        raise ValueError("S3.S report differs from pinned source/native recomputation")
    return {"audit_pass": True, "source_faces_checked": 43,
            "source_edges_checked": report["original_source_native_bijective_edge_count"],
            "excluded_faces_checked": 26}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-step", required=True, type=Path)
    p.add_argument("--baseline-bp", required=True, type=Path)
    p.add_argument("--baseline-manifest", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    raw = a.source_step.read_bytes()
    text, digest = source_gate(raw)
    native = cq.importers.importStep(str(a.source_step)).val()
    bp = a.baseline_bp.read_bytes()
    manifest = json.loads(a.baseline_manifest.read_text("utf-8"))
    report = classify(text, native, bp, manifest)
    audit = audit_report(text, native, bp, manifest, report)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", **audit,
                      "excluded_support_histogram": report["excluded_support_histogram"],
                      "top_priorities": [x["source_advanced_face_id"] for x in report["classified_original_faces"][:6]]}, sort_keys=True))


if __name__ == "__main__":
    main()
