#!/usr/bin/env python3
"""Fail-closed source STEP screening for plane-to-cylinder generator boundaries.

This reports original STEP source geometry. It never upgrades a trimmed
cylinder into an admitted Bézier patch or an accepted APMesh mesh.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path

from s3c_step_source_gate import (COORDINATES, SOURCES, coordinates, entity,
                                  oriented_edges, refs)
from s3d_canonical_feature_curves import interface_inventory


def _point(table, identifier, *, expected=None):
    kind, payload = entity(table, identifier, expected)
    if kind not in ("DIRECTION", "CARTESIAN_POINT"):
        raise ValueError("Expected a native STEP 3D direction or point")
    match = COORDINATES.search(payload)
    if not match:
        raise ValueError("Invalid STEP 3D coordinate payload")
    result = tuple(map(float, match[1].split(",")))
    if len(result) != 3 or not all(math.isfinite(x) for x in result):
        raise ValueError("Nonfinite or non-3D native STEP vector")
    return result


def _sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1],
            a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def _norm(x):
    return math.sqrt(_dot(x, x))


def _axis_support(table, face_id):
    """Get native STEP cylinder axis and radius without fitting coordinates."""
    _, raw = entity(table, face_id, "ADVANCED_FACE")
    surface_id = refs(raw)[-1]
    _, cylinder = entity(table, surface_id, "CYLINDRICAL_SURFACE")
    links = refs(cylinder)
    if len(links) != 1:
        raise ValueError("Invalid original cylindrical support placement")
    _, placement = entity(table, links[0], "AXIS2_PLACEMENT_3D")
    frame = refs(placement)
    if len(frame) not in (2, 3):
        raise ValueError("Unsupported native cylindrical axis frame")
    origin = _point(table, frame[0], expected="CARTESIAN_POINT")
    axis_raw = _point(table, frame[1], expected="DIRECTION")
    norm = _norm(axis_raw)
    if norm <= 1e-14:
        raise ValueError("Degenerate original cylinder axis")
    axis = tuple(x/norm for x in axis_raw)
    radius_text = cylinder.rsplit(",", 1)[-1].strip()
    try:
        radius = float(radius_text)
    except ValueError as error:
        raise ValueError("Invalid source cylinder radius") from error
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError("Nonpositive original cylinder radius")
    return surface_id, origin, axis, radius


def _generator_geometry(table, edge_id, origin, axis, radius):
    _, raw = entity(table, edge_id, "EDGE_CURVE")
    references = refs(raw)
    if len(references) != 3:
        raise ValueError("Invalid generator EDGE_CURVE references")
    a = coordinates(table, references[0])
    b = coordinates(table, references[1])
    direction = _sub(b, a)
    length = _norm(direction)
    if length <= 1e-14:
        raise ValueError("Degenerate STEP generator edge")
    radial_offsets = []
    axial_heights = []
    for point in (a, b):
        delta = _sub(point, origin)
        z = _dot(delta, axis)
        axial_heights.append(z)
        radial_offsets.append(_sub(delta, tuple(z*q for q in axis)))
    radial_error = max(abs(_norm(q)-radius) for q in radial_offsets)
    lateral = _norm(_cross(direction, axis))
    return {
        "source_edge_curve_id": edge_id,
        "source_length_mm": length,
        "maximum_endpoint_radial_residual_mm": radial_error,
        "axis_parallel_lateral_displacement_mm": lateral,
        "axis_parallel_sine": lateral/length,
        "axial_extent_mm": sorted(axial_heights),
        "unit_radial_at_start": tuple(x/_norm(radial_offsets[0]) for x in radial_offsets[0]),
    }


def _checksum(payload):
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def screen(step_text, *, model, source_sha256):
    """Audit source-graph axial generators, but do not assume a native UV trim."""
    observed = sha256(step_text.encode("utf-8")).hexdigest()
    if observed != source_sha256:
        raise ValueError("Raw source STEP SHA-256 mismatch")
    if model in SOURCES and SOURCES[model][1] != observed:
        raise ValueError("Pinned original STEP SHA-256 mismatch")
    table, source, interfaces = interface_inventory(
        step_text, model=model, source_sha256=source_sha256)
    cylinder_owners = defaultdict(list)
    for entry in interfaces:
        if entry["excluded_neighbor_support"] == "CYLINDRICAL_SURFACE":
            cylinder_owners[entry["excluded_neighbor_face_id"]].append(entry)
    results = []
    for face_id, anchored in sorted(cylinder_owners.items()):
        support_id, origin, axis, radius = _axis_support(table, face_id)
        category, wires = oriented_edges(table, face_id)
        if category != "CYLINDRICAL_SURFACE":
            raise ValueError("Original neighbor support type changed")
        geometries = []
        for a in anchored:
            geometries.append(_generator_geometry(table, a["original_edge_curve_id"],
                                                   origin, axis, radius))
        curve_counter = Counter(e["master_3d_curve"] for wire in wires for e in wire)
        wire_edges = [len(w) for w in wires]
        anchor_ids = {e["source_edge_curve_id"] for e in geometries}
        statuses = []
        # The original cylinder may have multiple trims, split edges, or
        # only one anchored source generator. None is silently sewn.
        if len(wires) != 1:
            statuses.append("MULTIPLE_TRIM_WIRES")
        if wire_edges != [4]:
            statuses.append("NONFOURSIDE_TRIM")
        if curve_counter != Counter({"LINE": 2, "CIRCLE": 2}):
            statuses.append("OTHER_OR_SPLIT_MASTER_EDGE_GEOMETRY")
        if len(anchored) != 2 or len(anchor_ids) != 2:
            statuses.append("MISSING_OR_DUPLICATE_ORIGINAL_CANDIDATE_GENERATOR")
        native_line_ids = {e["edge_curve_id"] for wire in wires for e in wire
                           if e["master_3d_curve"] == "LINE"}
        if not anchor_ids.issubset(native_line_ids):
            statuses.append("ANCHORED_EDGE_NOT_NATIVE_STEP_GENERATOR")
        scale = max(1., radius, *(g["source_length_mm"] for g in geometries))
        # Numeric source-consistency tolerance is NOT a surface fitting budget.
        source_tolerance = max(1e-8, 1e-9*scale)
        if any(g["maximum_endpoint_radial_residual_mm"] > source_tolerance or
               g["axis_parallel_lateral_displacement_mm"] > source_tolerance
               for g in geometries):
            statuses.append("SOURCE_GENERATOR_AXIS_OR_RADIUS_INCONSISTENCY")
        span_delta = None
        minor_angle = None
        minimum_pieces = None
        if len(geometries) == 2:
            a, b = geometries
            span_delta = max(abs(x-y) for x, y in zip(a["axial_extent_mm"], b["axial_extent_mm"]))
            if span_delta > source_tolerance:
                statuses.append("SOURCE_ANCHORED_AXIAL_EXTENTS_DIFFER")
            cosine = max(-1., min(1., _dot(a["unit_radial_at_start"],
                                              b["unit_radial_at_start"])))
            minor_angle = math.acos(cosine)
            if minor_angle <= 1e-12:
                statuses.append("COINCIDENT_GENERATOR_DIRECTIONS")
            else:
                minimum_pieces = max(1, math.ceil(minor_angle/(math.pi/2)-1e-12))
        status = ("SOURCE_TWO_GENERATOR_RECTANGLE_CANDIDATE" if not statuses
                  else "SOURCE_ONLY_TRIM_RECONSTRUCTION_REQUIRED")
        results.append({
            "source_advanced_face_id": face_id,
            "source_cylindrical_support_entity_id": support_id,
            "radius_mm": radius,
            "anchored_original_edge_curve_ids": sorted(anchor_ids),
            "original_anchor_count": len(anchored),
            "source_wire_count": len(wires),
            "source_wire_edge_counts": wire_edges,
            "source_master_curve_histogram": dict(sorted(curve_counter.items())),
            "generator_checks": geometries,
            "source_consistency_tolerance_mm": source_tolerance,
            "anchored_axis_extent_difference_mm": span_delta,
            "minimum_angular_separation_rad": minor_angle,
            "minor_arc_lower_bound_on_quarter_turn_segments": minimum_pieces,
            "classification": status,
            "exclusion_reasons": statuses,
            "actual_trimmed_u_interval": "NOT_DETERMINED_FROM_SOURCE_GRAPH",
            "exact_original_native_brep_mapping": "NOT_RUN",
            "curved_patch_fit": "NOT_RUN",
        })
    disposition = Counter(x["classification"] for x in results)
    report = {
        "schema": "apmesh-s3g-original-cylindrical-generator-source-gate-v1",
        "model": model,
        "source_raw_sha256": observed,
        "original_step_advanced_faces": source["original_advanced_faces"],
        "source_planar_candidate_faces": source["candidate_faces"],
        "source_candidate_to_excluded_original_edges": source["candidate_edge_neighbors"].get("CANDIDATE_TO_EXCLUDED", 0),
        "source_planar_to_cylinder_generator_edges": sum(len(v) for v in cylinder_owners.values()),
        "source_adjacent_cylinder_faces": len(results),
        "candidate_histogram": dict(sorted(disposition.items())),
        "original_cylindrical_face_screens": results,
        "raw_step_source_distributed": False,
        "native_original_cad_import": "NOT_RUN",
        "original_native_face_id_mapping": "NOT_RUN",
        "original_cylinder_bp_conversion": "NOT_RUN",
        "apmesh_tri_quad": "NOT_RUN",
        "original_nonmanifold_positive": "NOT_GRANTED",
    }
    report["report_sha256"] = _checksum(report)
    return report


def recompute_audit(step_text, report, *, model, source_sha256):
    """Reconstruct the report from source entities; do not trust a sidecar hash."""
    stored = dict(report)
    digest = stored.pop("report_sha256", None)
    if digest != _checksum(stored):
        raise ValueError("S3.G report checksum mismatch")
    other = screen(step_text, model=model, source_sha256=source_sha256)
    if other != report:
        raise ValueError("S3.G source geometry graph disagrees with source recomputation")
    return {"schema": "apmesh-s3g-source-recomputed-audit-v1",
            "source_generator_edges_verified": other["source_planar_to_cylinder_generator_edges"],
            "source_rectangle_candidates": other["candidate_histogram"].get(
                "SOURCE_TWO_GENERATOR_RECTANGLE_CANDIDATE", 0),
            "native_source_brep_fit": "NOT_RUN",
            "audit_pass": True}




def native_support_crosscheck(step_text, native_shape, *, model, source_sha256):
    """Cross-check STEP cylinder support against uniquely mapped native faces.

    Recomputing S3.E/S3.F first-ring certificates is mandatory. This proves
    original/native support parameter equivalence only, NOT UV trim fitting.
    """
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from s3e_native_feature_bijection import correlate
    from s3f_first_ring_native_faces import first_ring, recompute_audit

    source = screen(step_text, model=model, source_sha256=source_sha256)
    certificate = correlate(step_text, native_shape, model=model,
                            source_sha256=source_sha256)
    ring = first_ring(step_text, native_shape, certificate, model=model,
                      source_sha256=source_sha256)
    recompute_audit(step_text, native_shape, ring, model=model,
                    source_sha256=source_sha256)
    native_faces = native_shape.Faces()
    mapping = {f["source_advanced_face_id"]: f for f in ring["excluded_face_mapping"]}
    table, _, _ = interface_inventory(step_text, model=model,
                                      source_sha256=source_sha256)
    observed = []
    for face in source["original_cylindrical_face_screens"]:
        source_id = face["source_advanced_face_id"]
        if source_id not in mapping:
            raise ValueError("Cylinder source face has no certified native correspondence")
        idx = mapping[source_id]["native_face_index"]
        native = native_faces[idx]
        if native.geomType() != "CYLINDER":
            raise ValueError("Native first-ring face has no cylindrical support")
        native_surface = BRepAdaptor_Surface(native.wrapped, True).Cylinder()
        _, origin, axis, radius = _axis_support(table, source_id)
        native_radius = float(native_surface.Radius())
        native_axis = native_surface.Axis()
        native_origin = (float(native_axis.Location().X()),
                         float(native_axis.Location().Y()),
                         float(native_axis.Location().Z()))
        native_dir = (float(native_axis.Direction().X()),
                      float(native_axis.Direction().Y()),
                      float(native_axis.Direction().Z()))
        angular_sine = _norm(_cross(axis, native_dir))
        axis_separation = _norm(_cross(_sub(origin, native_origin), axis))
        tol = max(1e-8, 1e-9*max(radius, native_radius,
                                  native_shape.BoundingBox().DiagonalLength))
        if (abs(radius-native_radius) > tol or angular_sine > 1e-8 or
                axis_separation > tol):
            raise ValueError("Original STEP/native cylindrical support mismatch")
        if mapping[source_id]["original_edge_anchor_count"] != face["original_anchor_count"]:
            raise ValueError("Cylinder original/native anchor count mismatch")
        observed.append({"step_advanced_face_id": source_id,
                         "native_face_index": idx,
                         "original_radius_mm": radius,
                         "native_radius_mm": native_radius,
                         "radius_residual_mm": abs(radius-native_radius),
                         "axis_line_separation_mm": axis_separation,
                         "absolute_axis_direction_sine": angular_sine,
                         "original_edge_anchor_count": face["original_anchor_count"],
                         "original_native_face_id_verified": True,
                         "native_trim_parameter_interval_certified": False})
    return {"schema": "apmesh-s3g-native-original-cylinder-support-oracle-v1",
            "source_model": model,
            "source_sha256": source_sha256,
            "s3f_first_ring_audit_pass": True,
            "native_cylindrical_source_face_ids_checked": len(observed),
            "original_cylindrical_faces": observed,
            "curved_boundary_fit": "NOT_RUN",
            "continuous_surface_approximation_bound": "NOT_CERTIFIED",
            "apmesh_generation": "NOT_RUN"}


def run_step(source_path, output_path, *, model, expected_sha256=None, native=False):
    """Produce no evidence files unless all requested source/native gates pass."""
    raw = Path(source_path).read_bytes()
    actual = sha256(raw).hexdigest()
    if model not in SOURCES and expected_sha256 is None:
        raise ValueError("Unpinned STEP requires an explicit expected SHA-256")
    if expected_sha256 is not None and expected_sha256 != actual:
        raise ValueError("Expected raw STEP SHA-256 mismatch")
    step_text = raw.decode("utf-8")
    report = screen(step_text, model=model, source_sha256=actual)
    source_audit = recompute_audit(step_text, report, model=model,
                                   source_sha256=actual)
    outcome = {"source": report, "source_recomputed_audit": source_audit}
    if native:
        import cadquery as cq
        shape = cq.importers.importStep(str(source_path)).val()
        outcome["native_support_crosscheck"] = native_support_crosscheck(
            step_text, shape, model=model, source_sha256=actual)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(outcome, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-step", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--native", action="store_true",
                        help="Require import and exact native first-ring support check")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    outcome = run_step(args.source_step, args.output, model=args.model,
                       expected_sha256=args.expected_sha256,
                       native=args.native)
    r = outcome["source"]
    print(json.dumps({"model": args.model,
                      "native_checked": "native_support_crosscheck" in outcome,
                      "source_face_candidates": r["candidate_histogram"],
                      "source_cylinders": r["source_adjacent_cylinder_faces"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
