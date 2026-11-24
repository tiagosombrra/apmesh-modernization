#!/usr/bin/env python3
"""S3.U: original S40 post-octagon gap census and native risk preflight.

The original CAD is byte-pinned. This research-only diagnostic creates no BP
patches, never serializes source coordinates, and does not run APMesh meshing.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from copy import deepcopy
from hashlib import sha256
import json
import math
import re
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepTools import BRepTools

from audit_analytic_bp import read_bp
from s3c_step_source_gate import SOURCES, analyze, entity, refs
from s3r_s40_conforming_hole_join import _edge_adjacency
from s3s_full_original_face_census import (
    ADMITTED_CURVED_FACE_IDS, _classification, _hex_digest,
    _pcurve_kinds, full_correspondence, source_gate,
)

SOURCE_REVISION = "8f00f02579037cc893042f2ee2c910b20e3fb1b0"
S3R_BP_SHA256 = "98ff4cbfad08ce3f587607fddf3bb5e1a3697e1513a8ca86889bb28406e4028d"
S3T_BP_SHA256 = "988d8ed29867927f736838dde20db9efb358c0ee04a202a4f4810ae0e23aa40d"
S3T_NEW_FACE_IDS = (912, 3737)
EXPECTED_FACES = 43
EXPECTED_PATCHES = 132
EXPECTED_CONTROLS = 1527
EXPECTED_SEAMS = 189
EXPECTED_OPEN_SIDES = 150
EXPECTED_REPRESENTED = 19
EXPECTED_PENDING = 24
NEXT_CURVED_PLANAR_IDS = (17, 2092)
NEXT_CIRCLE_PLANAR_IDS = (1279, 1386)
ODD_LINE_ONLY_IDS = (3269, 3485)
PLANE_SUPPORT_MAX_SAMPLE_COUNT = 33


def _verify_pinned_inputs(source_bytes: bytes, bp_bytes: bytes, manifest: dict,
                          s3r_bp_bytes: bytes, s3r_manifest: dict):
    """Enforce exact immutable original and prior-atlas bytes/lineage."""
    text, digest = source_gate(source_bytes)
    if sha256(bp_bytes).hexdigest() != S3T_BP_SHA256:
        raise ValueError("S3.T BP SHA-256 mismatch")
    if sha256(s3r_bp_bytes).hexdigest() != S3R_BP_SHA256:
        raise ValueError("S3.R BP SHA-256 mismatch")
    if (manifest.get("schema") != "apmesh-s3t-original-s40-source-octagon-quads-v1" or
        manifest.get("source_sha256") != digest or
        manifest.get("new_bp_sha256") != S3T_BP_SHA256 or
        manifest.get("baseline_bp_sha256") != S3R_BP_SHA256 or
        manifest.get("original_face_ids") != list(S3T_NEW_FACE_IDS) or
        manifest.get("joined_patches") != EXPECTED_PATCHES or
        manifest.get("joined_control_count") != EXPECTED_CONTROLS or
        manifest.get("source_original_faces_represented") != EXPECTED_REPRESENTED or
        manifest.get("source_inner_hole_retained") is not True or
        manifest.get("original_s3r_prefix_patches_unmodified") is not True or
        manifest.get("numerical_budget_mm") != 0.001 or
        manifest.get("global_two_sided_indexed_seams") != EXPECTED_SEAMS or
        manifest.get("global_open_indexed_sides") != EXPECTED_OPEN_SIDES or
        manifest.get("apmesh_tri_quad_generation") != "NOT_RUN" or
        manifest.get("production_cpp_regression") != "NOT_RUN"):
        raise ValueError("S3.T manifest mismatches frozen previous acceptance")
    if (s3r_manifest.get("joined_bp_sha256") != S3R_BP_SHA256 or
        s3r_manifest.get("source_inner_hole_retained") is not True or
        s3r_manifest.get("joined_patch_count") != 126):
        raise ValueError("S3.R source atlas lineage invalid")
    old_points, old_patches = read_bp(s3r_bp_bytes.decode("utf-8"))
    points, patches = read_bp(bp_bytes.decode("utf-8"))
    if (len(old_points) != 1467 or len(old_patches) != 126 or
        len(points) != EXPECTED_CONTROLS or len(patches) != EXPECTED_PATCHES or
        old_points != points[:len(old_points)] or
        old_patches != patches[:len(old_patches)]):
        raise ValueError("S3.T previous conforming atlas prefix modified")
    adjacency = _edge_adjacency(patches)
    seams = sum(len(sides) == 2 for sides in adjacency.values())
    open_sides = sum(len(sides) == 1 for sides in adjacency.values())
    if (seams, open_sides) != (EXPECTED_SEAMS, EXPECTED_OPEN_SIDES):
        raise ValueError("S3.T indexed adjacency changed")
    if any(len(sides) > 2 for sides in adjacency.values()):
        raise ValueError("S3.T indexed atlas has an oversubscribed seam")
    return text


def _admitted_faces(source_text, mapping, manifest):
    """Recompute admissions from source screening and prior explicit gates."""
    screened = analyze(source_text, model="S40", source_sha256=SOURCES["S40"][1])
    planar = {row["source_advanced_face_id"]
              for row in screened["candidate_source_entity_graph"]}
    prior = planar | ADMITTED_CURVED_FACE_IDS
    if len(planar) != 9 or len(prior) != 17:
        raise ValueError("Original S3.R source face set changed")
    new = set(S3T_NEW_FACE_IDS)
    if prior & new or not new <= set(mapping["source_faces"]):
        raise ValueError("S3.T newly represented STEP faces inconsistent")
    for sid in S3T_NEW_FACE_IDS:
        support, wires = mapping["source_faces"][sid]
        expected = manifest["source_to_original_face_ids"].get(str(sid))
        if (support != "PLANE" or len(wires) != 1 or len(wires[0]) != 8 or
            [edge["edge_curve_id"] for edge in wires[0]] != expected or
            any(edge["master_3d_curve"] != "LINE" for edge in wires[0])):
            raise ValueError("S3.T admitted polygon lost original STEP boundaries")
        if len({row["edge_curve_id"] for row in wires[0]}) != 8:
            raise ValueError("S3.T original STEP boundary ids are not unique")
    represented = prior | new
    if len(represented) != EXPECTED_REPRESENTED:
        raise ValueError("Post-S3.T represented face count mismatch")
    return represented


def _support_samples(face, edge, samples=PLANE_SUPPORT_MAX_SAMPLE_COUNT):
    """Sample original BRep edge against its original native planar support."""
    plane = BRepAdaptor_Surface(face.wrapped).Plane()
    curve = BRepAdaptor_Curve(edge.wrapped)
    first, last = curve.FirstParameter(), curve.LastParameter()
    if not all(map(math.isfinite, (first, last))) or last <= first:
        raise ValueError("Original native curve has invalid parameter interval")
    maximum = 0.0
    for i in range(samples):
        point = curve.Value(first + (last-first)*i/(samples-1))
        maximum = max(maximum, float(plane.Distance(point)))
    return maximum


def _source_boundary_owners(mapping):
    neighbors = defaultdict(set)
    for owners in mapping["owners"].values():
        for sid in owners:
            neighbors[sid].update(owners-{sid})
    return neighbors


def _distance_to_admitted(neighbors, represented, face_ids):
    distances = dict.fromkeys(represented, 0)
    queue = deque(sorted(represented))
    while queue:
        current = queue.popleft()
        for adjacent in sorted(neighbors[current]):
            if adjacent not in distances:
                distances[adjacent] = distances[current]+1
                queue.append(adjacent)
    if set(distances) != set(face_ids):
        raise ValueError("Original source face graph disconnected from partial atlas")
    return distances


def _partition_preflight(row):
    """Classify risk without treating a new source face as an admitted patch."""
    if row["inner_wire_count"]:
        return "INNER_WIRE_HOLE_PRESERVING_PARTITION_REQUIRED"
    if row["support_type"] != "PLANE":
        return "NONPLANAR_SURFACE_RECONSTRUCTION_REQUIRED"
    if row["source_wire_count"] != 1:
        return "MULTIWIRE_PLANAR_DECOMPOSITION_REQUIRED"
    if row["3d_bspline_edge_count"]:
        if row["source_boundary_edge_count"] == 4:
            return "FOUR_SIDE_CURVED_BOUNDARY_APPROXIMATION_AND_SEAM_AUDIT_REQUIRED"
        return "SPLINE_BOUNDARY_PARTITION_REQUIRED"
    if row["source_boundary_edge_count"] % 2 == 1:
        return "ODD_BOUNDARY_REQUIRES_SPLIT_OR_STEINER_VERTEX"
    if row["3d_circle_edge_count"]:
        return "CIRCULAR_BOUNDARY_APPROXIMATION_AND_QUAD_PARTITION_REQUIRED"
    return "LINE_ONLY_POLYGON_QUADRANGULATION_PRECHECK_REQUIRED"


def classify_post_octagon(source_bytes: bytes, native, bp_bytes: bytes,
                          manifest: dict, s3r_bp_bytes: bytes,
                          s3r_manifest: dict):
    """Recompute the complete post-S3.T 24-face source/native gap inventory."""
    source_text = _verify_pinned_inputs(source_bytes, bp_bytes, manifest,
                                        s3r_bp_bytes, s3r_manifest)
    mapping = full_correspondence(source_text, native)
    if (len(mapping["face_map"]) != EXPECTED_FACES or
        len(mapping["edge_map"]) != 117 or len(mapping["vertex_map"]) != 77):
        raise ValueError("Original STEP-native topology correspondence changed")
    represented = _admitted_faces(source_text, mapping, manifest)
    original_faces = mapping["source_faces"]
    owners = mapping["owners"]
    neighbors = _source_boundary_owners(mapping)
    distances = _distance_to_admitted(neighbors, represented, original_faces)
    table = mapping["table"]
    rows = []
    for sid, (support, wires) in sorted(original_faces.items()):
        if sid in represented:
            continue
        edge_records = [edge for wire in wires for edge in wire]
        edge_ids = {edge["edge_curve_id"] for edge in edge_records}
        original_edges_to_atlas = sorted(e for e in edge_ids if (owners[e]-{sid}) & represented)
        curve_hist = Counter(edge["master_3d_curve"] for edge in edge_records)
        support_id = refs(entity(table, sid, "ADVANCED_FACE")[1])[-1]
        pcurve_hist = Counter(t for edge in edge_records
                             for t in _pcurve_kinds(table, edge["edge_curve_id"], support_id))
        face = mapping["native_faces"][mapping["face_map"][sid]]
        outer = BRepTools.OuterWire_s(face.wrapped)
        hole_count = sum(not wire.wrapped.IsSame(outer) for wire in face.Wires())
        source_neighbors = sorted(neighbors[sid])
        direct_neighbors = sorted(neighbors[sid] & represented)
        if len(set(original_edges_to_atlas)) != len(original_edges_to_atlas):
            raise ValueError("Original source edge counted twice in direct atlas inventory")
        if sum(len(wire) for wire in wires) != sum(len(wire.Edges()) for wire in face.Wires()):
            raise ValueError("Original native trim-edge census differs from STEP")
        row = {
            "source_advanced_face_id": sid,
            "native_face_index": mapping["face_map"][sid],
            "source_support_type": support,
            "support_type": support,
            "native_support_type": face.geomType(),
            "original_wire_count": len(wires),
            "original_boundary_edge_count": len(edge_records),
            "source_boundary_edge_count": len(edge_records),
            "source_wire_count": len(wires),
            "source_wire_edge_counts": [len(wire) for wire in wires],
            "inner_wire_count": hole_count,
            "3d_master_curve_histogram": dict(sorted(curve_hist.items())),
            "pcurve_histogram": dict(sorted(pcurve_hist.items())),
            "3d_bspline_edge_count": sum(count for name,count in curve_hist.items() if "SPLINE" in name),
            "3d_circle_edge_count": curve_hist.get("CIRCLE", 0),
            "parametric_bspline_occurrences": sum(count for name,count in pcurve_hist.items() if "SPLINE" in name),
            "incident_represented_edge_count": len(original_edges_to_atlas),
            "incident_represented_source_edge_curve_ids": original_edges_to_atlas,
            "incident_represented_face_ids": direct_neighbors,
            "incident_unrepresented_face_ids": sorted(set(source_neighbors)-represented),
            "minimum_original_edge_hops_from_represented_atlas": distances[sid],
            "native_valid_shape": bool(face.isValid()),
            "admission_status": "NOT_GENERATED_OR_ACCEPTED",
        }
        if (not row["native_valid_shape"] or
            len(source_neighbors) != len({n for e in edge_ids for n in owners[e]-{sid}})):
            raise ValueError("Original native face or source incidence invalid")
        row["partition_preflight"] = _partition_preflight(row)
        row["research_priority_score_heuristic"] = _classification(row, represented)
        if sid in NEXT_CURVED_PLANAR_IDS:
            if support != "PLANE" or len(wires) != 1 or len(edge_records) != 4 or hole_count:
                raise ValueError("Source four-sided spline-planar candidate changed")
            if len(direct_neighbors) != 4:
                raise ValueError("Source four-sided candidate lost a represented neighbor")
            spline_edges = [edge["edge_curve_id"] for edge in edge_records
                            if "SPLINE" in edge["master_3d_curve"]]
            if len(spline_edges) != 1:
                raise ValueError("Four-sided candidate no longer has one original B-spline")
            row["original_spline_edge_curve_id"] = spline_edges[0]
            curve_id = refs(entity(table, spline_edges[0], "EDGE_CURVE")[1])[2]
            underlying_id = refs(entity(table, curve_id)[1])[0]
            curve_kind, raw_curve = entity(table, underlying_id)
            degree_match = re.match(r"^'[^']*',\s*(\d+)\s*,", raw_curve)
            if curve_kind != "B_SPLINE_CURVE_WITH_KNOTS" or not degree_match:
                raise ValueError("Original candidate spline degree cannot be established")
            row["original_master_3d_bspline_degree"] = int(degree_match.group(1))
            if row["original_master_3d_bspline_degree"] != 5:
                raise ValueError("Original source B-spline degree changed")
            row["native_original_spline_support_max_sampled_mm"] = _support_samples(
                face, mapping["native_edges"][mapping["edge_map"][spline_edges[0]]])
            row["native_original_spline_samples"] = PLANE_SUPPORT_MAX_SAMPLE_COUNT
        rows.append(row)
    if len(rows) != EXPECTED_PENDING:
        raise ValueError("Post-S3.T pending count not 24")
    rows.sort(key=lambda row:(-row["research_priority_score_heuristic"], row["source_advanced_face_id"]))
    for i, row in enumerate(rows, 1):
        row["heuristic_ordinal_not_admission"] = i
    ids = {row["source_advanced_face_id"] for row in rows}
    if ids & represented or len(ids|represented) != EXPECTED_FACES:
        raise ValueError("Post-S3.T source face coverage double counts or omits faces")
    if not set(NEXT_CURVED_PLANAR_IDS+NEXT_CIRCLE_PLANAR_IDS+ODD_LINE_ONLY_IDS) <= ids:
        raise ValueError("Next-candidate source identities unexpectedly represented or missing")
    support_hist = Counter(row["source_support_type"] for row in rows)
    hop_hist = Counter(str(row["minimum_original_edge_hops_from_represented_atlas"]) for row in rows)
    preflight_hist = Counter(row["partition_preflight"] for row in rows)
    max_owners = max(len(face_set) for face_set in owners.values())
    report = {
        "schema": "apmesh-s3u-s40-post-octagon-source-native-census-v1",
        "original_step_repo": "cgg-bern/hex-me-if-you-can",
        "original_step_revision": SOURCE_REVISION,
        "original_step_path": "original/i25o_s40.step",
        "original_step_sha256": sha256(source_bytes).hexdigest(),
        "frozen_s3r_atlas_bp_sha256": S3R_BP_SHA256,
        "frozen_s3t_atlas_bp_sha256": S3T_BP_SHA256,
        "prior_integrated_patch_count": EXPECTED_PATCHES,
        "prior_integrated_declared_control_count": EXPECTED_CONTROLS,
        "prior_integrated_original_face_count": EXPECTED_REPRESENTED,
        "covered_source_face_ids": sorted(represented),
        "original_source_face_count": EXPECTED_FACES,
        "native_correlated_face_count": len(mapping["face_map"]),
        "native_correlated_edge_count": len(mapping["edge_map"]),
        "native_correlated_vertex_count": len(mapping["vertex_map"]),
        "source_edge_max_distinct_face_owners": max_owners,
        "source_original_3plus_incident_edges": sum(len(faces)>=3 for faces in owners.values()),
        "pending_original_face_count": len(rows),
        "pending_source_support_histogram": dict(sorted(support_hist.items())),
        "pending_original_minimum_hops_histogram": dict(sorted(hop_hist.items())),
        "pending_with_direct_source_edge_to_existing_atlas": sum(row["incident_represented_edge_count"]>0 for row in rows),
        "pending_without_direct_source_edge_to_existing_atlas": sum(row["incident_represented_edge_count"]==0 for row in rows),
        "pending_partition_preflight_histogram": dict(sorted(preflight_hist.items())),
        "prioritized_next_candidate_source_faces": list(NEXT_CURVED_PLANAR_IDS),
        "analytic_arc_alternative_source_faces": list(NEXT_CIRCLE_PLANAR_IDS),
        "odd_boundary_requires_subdivision_source_faces": list(ODD_LINE_ONLY_IDS),
        "pending_faces": rows,
        "priority_note": "Heuristic only. Source/native B-spline and existing indexed BP seam conformity are not yet certified for new faces.",
        "original_hole_face_218_preserved_by_frozen_s3t_prefix": True,
        "new_bp_patches_generated": 0,
        "new_source_faces_admitted": 0,
        "apmesh_tri_quad_mesh_generation": "NOT_RUN",
        "production_cpp_regression": "NOT_RUN",
    }
    report["receipt_sha256"] = _hex_digest(report)
    return report


def audit_post_octagon(source_bytes, native, bp_bytes, manifest,
                       s3r_bp_bytes, s3r_manifest, receipt):
    """Reject stale or modified receipts, including recomputed fake checksums."""
    provided = deepcopy(receipt)
    checksum = provided.pop("receipt_sha256", None)
    if checksum != _hex_digest(provided):
        raise ValueError("S3.U receipt content hash mismatch")
    independently_computed = classify_post_octagon(
        source_bytes, native, bp_bytes, manifest, s3r_bp_bytes, s3r_manifest)
    if receipt != independently_computed:
        raise ValueError("S3.U report differs from original native source recomputation")
    return {"status": "PASS", "source_faces_checked": EXPECTED_FACES,
            "source_edges_checked": 117, "source_vertices_checked": 77,
            "pending_faces_checked": EXPECTED_PENDING}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-step", type=Path, required=True)
    parser.add_argument("--baseline-bp", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path, required=True)
    parser.add_argument("--s3r-bp", type=Path, required=True)
    parser.add_argument("--s3r-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_bytes = args.source_step.read_bytes()
    bp_bytes = args.baseline_bp.read_bytes()
    baseline_manifest = json.loads(args.baseline_manifest.read_text(encoding="utf-8"))
    s3r_bp_bytes = args.s3r_bp.read_bytes()
    s3r_manifest = json.loads(args.s3r_manifest.read_text(encoding="utf-8"))
    native = cq.importers.importStep(str(args.source_step)).val()
    report = classify_post_octagon(source_bytes, native, bp_bytes, baseline_manifest,
                                   s3r_bp_bytes, s3r_manifest)
    audit = audit_post_octagon(source_bytes, native, bp_bytes, baseline_manifest,
                              s3r_bp_bytes, s3r_manifest, report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True,
                                      ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({**audit, "pending": report["pending_original_face_count"],
                      "direct": report["pending_with_direct_source_edge_to_existing_atlas"],
                      "next": report["prioritized_next_candidate_source_faces"]}, sort_keys=True))


if __name__ == "__main__":
    main()
