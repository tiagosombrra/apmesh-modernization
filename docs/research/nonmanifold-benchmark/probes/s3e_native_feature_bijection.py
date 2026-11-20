#!/usr/bin/env python3
"""Conservatively correlate original STEP face/edge entities with native BRep.

This is an isolated, fail-closed partial-atlas provenance gate. Correspondence
is inferred from multiple topology/geometric invariants; the STEP source ID is
NOT the same identifier as a TopoDS object. No curved patch fit is attempted.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq

from audit_original_cad_planar_atlas import audit as audit_partial_atlas
from original_cad_planar_atlas import build_atlas, eligibility, same_index
from s3c_step_source_gate import SOURCES, analyze, coordinates, parse_entities
from s3d_canonical_feature_curves import (
    interface_inventory, construct as construct_original_curves,
    audit as audit_original_curves,
)

SUPPORT_MAP = {
    "PLANE": "PLANE",
    "CYLINDRICAL_SURFACE": "CYLINDER",
    "CONICAL_SURFACE": "CONE",
    "TOROIDAL_SURFACE": "TORUS",
    "SPHERICAL_SURFACE": "SPHERE",
}


def _point(v):
    return (float(v.Center().x), float(v.Center().y), float(v.Center().z))


def _cyclic_correspondences(source, native, tolerance):
    """Return all valid cycle/reversal vertex index assignments."""
    if len(source) != 4 or len(native) != 4:
        return []
    solutions = []
    for first in range(4):
        for direction in (-1, 1):
            mapping = tuple((first + direction * i) % 4 for i in range(4))
            if all(math.dist(source[i], native[mapping[i]]) <= tolerance
                   for i in range(4)):
                solutions.append(mapping)
    return solutions


def _source_graph_candidates(step_text, *, model, digest):
    screen = analyze(step_text, model=model, source_sha256=digest)
    table = parse_entities(step_text)
    results = []
    for candidate in screen["candidate_source_entity_graph"]:
        record = dict(candidate)
        record["corner_xyz"] = [coordinates(table, vertex)
                                for vertex in record["source_oriented_vertex_ids"]]
        results.append(record)
    return screen, table, results


def _native_edge_to_face_indices(native_faces, native_edges):
    owners = defaultdict(set)
    for face_idx, face in enumerate(native_faces):
        for edge in face.Edges():
            edge_idx = same_index(native_edges, edge)
            if edge_idx is None:
                raise ValueError("Native face-edge identity absent from imported BRep")
            owners[edge_idx].add(face_idx)
    return owners


def correlate(step_text, native_shape, *, model, source_sha256):
    """Admit only unique and consistent local source-to-native interfaces."""
    actual_source_digest = sha256(step_text.encode("utf-8")).hexdigest()
    if actual_source_digest != source_sha256:
        raise ValueError("STEP source raw SHA-256 mismatch")
    pinned = SOURCES.get(model)
    if pinned and source_sha256 != pinned[1]:
        raise ValueError("Original STEP model has incorrect pinned SHA-256")
    if not native_shape.isValid():
        raise ValueError("Native imported BRep is invalid")
    screen, source_table, candidates = _source_graph_candidates(
        step_text, model=model, digest=source_sha256)
    if pinned and (screen["original_advanced_faces"], screen["candidate_faces"]) != pinned[2:]:
        raise ValueError("Frozen original source face/candidate inventory mismatch")
    faces, edges, vertices = (native_shape.Faces(), native_shape.Edges(),
                             native_shape.Vertices())
    if len(faces) != screen["original_advanced_faces"]:
        raise ValueError("Source/native face inventory mismatch")
    scale = native_shape.BoundingBox().DiagonalLength
    if scale <= 0 or not math.isfinite(scale):
        raise ValueError("Native BRep has invalid scale")
    # This tolerance checks source-to-import numeric fidelity; it MUST NOT
    # weld vertices or edges. Ambiguous matching is rejected independently.
    tolerance = max(1e-8, scale * 1e-9)
    native_candidates = []
    for face_idx, face in enumerate(faces):
        admissible, reason = eligibility(face, scale)
        if admissible is None:
            continue
        wire_vertices, corners, wire_edges = admissible
        native_candidates.append((face_idx, wire_vertices, corners, wire_edges))
    if len(native_candidates) != len(candidates):
        raise ValueError("STEP/native eligible planar face count mismatch")
    assigned_face_ids, assigned_vertex_ids, source_edge_to_native = {}, {}, {}
    inverse_vertex_ids = {}
    reverse_native_faces = set()
    max_vertex_deviation = 0.0
    binding = []
    for source in candidates:
        face_id = source["source_advanced_face_id"]
        possibilities = []
        for face_idx, native_vs, native_xyz, native_es in native_candidates:
            matches = _cyclic_correspondences(source["corner_xyz"], native_xyz,
                                             tolerance)
            for order in matches:
                possibilities.append((face_idx, native_vs, native_es, order))
        if len(possibilities) != 1:
            raise ValueError(f"Ambiguous/missing source-to-native face #{face_id}: "
                             f"{len(possibilities)} matches")
        native_id, native_vs, native_es, order = possibilities[0]
        if native_id in reverse_native_faces:
            raise ValueError("Two STEP source faces matched the same native face")
        reverse_native_faces.add(native_id)
        assigned_face_ids[face_id] = native_id
        current_vertices = []
        for i, native_corner in enumerate(order):
            source_vertex_id = source["source_oriented_vertex_ids"][i]
            native_vertex_id = same_index(vertices, native_vs[native_corner])
            if native_vertex_id is None:
                raise ValueError("Native vertex not in global BRep identity table")
            old = assigned_vertex_ids.setdefault(source_vertex_id, native_vertex_id)
            if old != native_vertex_id:
                raise ValueError("Original vertex identity maps to two native vertices")
            prior_source = inverse_vertex_ids.setdefault(native_vertex_id, source_vertex_id)
            if prior_source != source_vertex_id:
                raise ValueError("Two original vertex IDs mapped to the same native vertex")
            deviation = math.dist(source["corner_xyz"][i],
                                  _point(native_vs[native_corner]))
            max_vertex_deviation = max(max_vertex_deviation, deviation)
            current_vertices.append(native_vertex_id)
        native_edge_ids = []
        for i, source_eid in enumerate(source["source_edge_curve_ids"]):
            a, b = native_vs[order[i]], native_vs[order[(i + 1) % 4]]
            incident = [e for e in native_es if len(e.Vertices()) == 2 and
                        all(any(v.wrapped.IsSame(endpoint.wrapped)
                                for v in e.Vertices()) for endpoint in (a, b))]
            if len(incident) != 1:
                raise ValueError("Source side has ambiguous native edge connectivity")
            native_edge_id = same_index(edges, incident[0])
            if native_edge_id is None or incident[0].geomType() != "LINE":
                raise ValueError("Source master LINE has no native straight edge")
            previous = source_edge_to_native.setdefault(source_eid, native_edge_id)
            if previous != native_edge_id:
                raise ValueError("One STEP original EDGE_CURVE maps to two TopoDS edges")
            native_edge_ids.append(native_edge_id)
        binding.append({
            "step_advanced_face_id": face_id,
            "native_face_index": native_id,
            "step_oriented_vertex_ids": source["source_oriented_vertex_ids"],
            "native_oriented_vertex_indices": current_vertices,
            "step_edge_curve_ids": source["source_edge_curve_ids"],
            "native_edge_indices": native_edge_ids,
            "native_vertex_order_cycle": list(order),
        })
    # One native edge must never be assigned two different original source IDs.
    inverted_edges = {}
    for step_eid, native_eid in source_edge_to_native.items():
        if native_eid in inverted_edges and inverted_edges[native_eid] != step_eid:
            raise ValueError("Two distinct original edges were proximity-welded")
        inverted_edges[native_eid] = step_eid
    _, _, source_interfaces = interface_inventory(
        step_text, model=model, source_sha256=source_sha256)
    native_owners = _native_edge_to_face_indices(faces, edges)
    inspected = []
    neighbor_counts = Counter()
    for interface in source_interfaces:
        edge_id = interface["original_edge_curve_id"]
        native_eid = source_edge_to_native.get(edge_id)
        if native_eid is None:
            raise ValueError("Source interface lost its native candidate-side edge")
        face_idx = assigned_face_ids[interface["selected_planar_face_id"]]
        incident_native_faces = native_owners[native_eid]
        if len(incident_native_faces) != 2 or face_idx not in incident_native_faces:
            raise ValueError("Original interface does not retain two native owners")
        neighbor_idx = next(iter(incident_native_faces - {face_idx}))
        original_neighbor_type = interface["excluded_neighbor_support"]
        admitted_type = SUPPORT_MAP.get(original_neighbor_type)
        if admitted_type is None:
            raise ValueError("Source neighbor geometry has no recognized type")
        if faces[neighbor_idx].geomType() != admitted_type:
            raise ValueError("Original neighbor support disagrees with native BRep")
        if neighbor_idx in reverse_native_faces:
            raise ValueError("Excluded source neighbor mapped to admitted planar face")
        original_edge_vertices = (
            interface["source_start_vertex_id"],
            interface["source_end_vertex_id"])
        actual_vertices = [same_index(vertices, vertex)
                           for vertex in edges[native_eid].Vertices()]
        if len(actual_vertices) != 2:
            raise ValueError("Native original interface is degenerate")
        expected_vertices = [assigned_vertex_ids.get(i) for i in original_edge_vertices]
        if any(i is None for i in expected_vertices) or set(expected_vertices) != set(actual_vertices):
            raise ValueError("Source-to-native interface endpoints not preserved")
        start = coordinates(source_table, original_edge_vertices[0])
        end = coordinates(source_table, original_edge_vertices[1])
        source_length = math.dist(start, end)
        if abs(edges[native_eid].Length() - source_length) > tolerance:
            raise ValueError("Source LINE and native edge length differ")
        neighbor_counts[admitted_type] += 1
        inspected.append({
            "source_edge_curve_id": edge_id,
            "source_candidate_face_id": interface["selected_planar_face_id"],
            "source_neighbor_face_id": interface["excluded_neighbor_face_id"],
            "source_neighbor_support": original_neighbor_type,
            "native_edge_index": native_eid,
            "native_candidate_face_index": face_idx,
            "native_adjacent_face_index_by_edge": neighbor_idx,
            "source_neighbor_face_id_bijective_match": "NOT_ESTABLISHED",
            "edge_endpoint_vertex_id_correspondence": "CHECKED",
        })
    if len(inspected) != screen["candidate_edge_neighbors"].get("CANDIDATE_TO_EXCLUDED", 0):
        raise ValueError("Incomplete source/native interface inventory")
    result = {
        "schema": "apmesh-s3e-local-source-native-feature-correspondence-v1",
        "scope": "UNIQUE_PLANAR_CANDIDATES_AND_DIRECTLY_ADJACENT_NATIVE_EDGE_SUPPORT",
        "model": model, "source_raw_sha256": source_sha256,
        "source_advanced_face_total": screen["original_advanced_faces"],
        "native_brep_faces_total": len(faces),
        "eligible_source_faces": len(candidates),
        "eligible_native_faces": len(native_candidates),
        "uniquely_mapped_source_candidate_faces": len(binding),
        "uniquely_mapped_source_side_edges": len(source_edge_to_native),
        "source_to_excluded_native_interfaces": len(inspected),
        "source_to_excluded_native_cylinder_interfaces": neighbor_counts["CYLINDER"],
        "native_neighbor_support_histogram": dict(sorted(neighbor_counts.items())),
        "source_native_correspondence_tolerance_mm": tolerance,
        "maximum_source_native_candidate_vertex_delta_mm": max_vertex_deviation,
        "candidate_bindings": binding, "boundary_interfaces": inspected,
        "full_original_source_native_face_bijection": "NOT_ESTABLISHED",
        "excluded_neighbor_STEP_face_id_bijection": "NOT_ESTABLISHED",
        "source_curved_neighbor_patch_fitting": "NOT_RUN",
        "original_nonmanifold_3plus_source": "NOT_ADMITTED",
        "apmesh_generation": "NOT_RUN",
    }
    payload = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["certificate_sha256"] = sha256(payload.encode()).hexdigest()
    return result


def verify_certificate(step_text, native_shape, certificate, *, model, source_sha256):
    """Recompute correspondence independently of any provided face/edge claims."""
    digest = certificate.get("certificate_sha256")
    content = dict(certificate)
    content.pop("certificate_sha256", None)
    actual = sha256(json.dumps(content, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if actual != digest:
        raise ValueError("Certificate checksum mismatch")
    expected = correlate(step_text, native_shape, model=model, source_sha256=source_sha256)
    if certificate != expected:
        raise ValueError("Certificate fields differ from source/native recomputation")
    return {
        "schema": "apmesh-s3e-certificate-recomputation-v1",
        "certificate_valid": True,
        "candidate_face_bindings_checked": len(certificate["candidate_bindings"]),
        "original_boundary_interfaces_checked": len(certificate["boundary_interfaces"]),
        "complete_original_model_meshed": False,
    }


def run_one(step_path, output_dir, *, model, expected_sha256=None,
            expected_face_count=None, expected_candidates=None):
    raw = Path(step_path).read_bytes()
    digest = sha256(raw).hexdigest()
    pinned = SOURCES.get(model)
    if pinned:
        if digest != pinned[1]:
            raise ValueError("Pinned original STEP SHA-256 mismatch")
        expected_face_count, expected_candidates = pinned[2], pinned[3]
    elif not expected_sha256:
        raise ValueError("Unpinned source needs an explicit matching SHA-256")
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("Requested source SHA-256 mismatch")
    step_text = raw.decode("utf-8")
    native_shape = cq.importers.importStep(str(step_path)).val()
    certificate = correlate(step_text, native_shape, model=model, source_sha256=digest)
    if expected_face_count is not None and certificate["source_advanced_face_total"] != expected_face_count:
        raise ValueError("Frozen original source face inventory mismatch")
    if expected_candidates is not None and certificate["eligible_source_faces"] != expected_candidates:
        raise ValueError("Frozen original source candidate inventory mismatch")
    verified = verify_certificate(step_text, native_shape, certificate,
                                  model=model, source_sha256=digest)
    feature_graph = construct_original_curves(step_text, model=model,
                                             source_sha256=digest)
    feature_audit = audit_original_curves(
        step_text, feature_graph, expected_model=model, source_sha256=digest)
    if feature_audit["source_edges_checked"] != certificate["source_to_excluded_native_interfaces"]:
        raise ValueError("Unverified original feature curve in native correspondence")
    partial_bp, atlas = build_atlas(native_shape, model, digest)
    audited = audit_partial_atlas(native_shape, partial_bp, atlas,
                                  source_sha256=digest)
    if atlas["converted_face_count"] != certificate["uniquely_mapped_source_candidate_faces"]:
        raise ValueError("Correlated planar sources missing from BP atlas")
    indexed_atlas = {p["source_face"]: p for p in atlas["patches"]}
    for binding in certificate["candidate_bindings"]:
        patch = indexed_atlas.get(binding["native_face_index"])
        if patch is None or set(patch["source_edge_ids"]) != set(binding["native_edge_indices"]):
            raise ValueError("BP patch does not match source-to-native edge mapping")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "source_feature_curves.json").write_text(
        json.dumps(feature_graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "independent_source_curve_audit.json").write_text(
        json.dumps(feature_audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "native_correspondence.json").write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "independent_correspondence.json").write_text(
        json.dumps(verified, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "planar.partial.bp").write_text(partial_bp, encoding="utf-8")
    (output_dir / "partial_atlas.json").write_text(
        json.dumps(atlas, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "independent_partial_bp_audit.json").write_text(
        json.dumps(audited, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "source_file": Path(step_path).name,
        "source_sha256": digest,
        "status": "LOCAL_PLANAR_AND_INTERFACE_CORRESPONDENCE_AUDITED",
        "candidate_faces": certificate["uniquely_mapped_source_candidate_faces"],
        "matched_interfaces": certificate["source_to_excluded_native_interfaces"],
        "matched_cylinder_interfaces": certificate["source_to_excluded_native_cylinder_interfaces"],
        "source_neighbor_advanced_face_ids_verified": False,
        "native_curved_surface_patches": "NOT_RUN",
        "complete_mesh": "NOT_RUN",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-step", type=Path, required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--expected-sha256")
    args = p.parse_args()
    report = run_one(args.source_step, args.output, model=args.model,
                     expected_sha256=args.expected_sha256)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
