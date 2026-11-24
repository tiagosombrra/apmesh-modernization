#!/usr/bin/env python3
"""Certify first-ring STEP face IDs using already verified native edge anchors.

Scope: original STEP candidate-to-excluded interface edges, not full curved
surface conversion, global CAD face bijection, or APMesh mesh acceptance.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

import cadquery as cq

from s3c_step_source_gate import SOURCES, oriented_edges, parse_entities
from s3e_native_feature_bijection import (
    SUPPORT_MAP, correlate, same_index, verify_certificate,
)


def _checksum(record):
    """Hash a deterministic source/native evidence payload."""
    raw = json.dumps(record, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def first_ring(step_text, native_shape, certificate, *, model, source_sha256):
    """Map directly adjacent excluded source face IDs without coordinate welding.

    The source face must use the exact source EDGE_CURVE whose candidate-side
    TopoDS_Edge has already passed the source/native correspondence gate.
    Mapping is injective in both directions and every anchoring edge is checked
    on the target TopoDS_Face via IsSame, rather than vertex proximity.
    """
    verified = verify_certificate(step_text, native_shape, certificate,
                                  model=model, source_sha256=source_sha256)
    if not verified["certificate_valid"]:
        raise ValueError("S3.E prerequisite correspondence certificate not verified")
    source_graph = parse_entities(step_text)
    faces, edges = native_shape.Faces(), native_shape.Edges()
    source_to_native = {}
    native_to_source = {}
    candidate_faces = set()
    for binding in certificate["candidate_bindings"]:
        original = binding["step_advanced_face_id"]
        native_id = binding["native_face_index"]
        source_to_native[original] = native_id
        native_to_source[native_id] = original
        candidate_faces.add(original)
    if len(candidate_faces) != certificate["uniquely_mapped_source_candidate_faces"]:
        raise ValueError("Duplicate original candidate bindings")

    anchors = defaultdict(list)
    edges_checked = set()
    for record in certificate["boundary_interfaces"]:
        original_face = record["source_neighbor_face_id"]
        native_face = record["native_adjacent_face_index_by_edge"]
        edge_id = record["source_edge_curve_id"]
        native_edge_idx = record["native_edge_index"]
        if not 0 <= native_face < len(faces) or not 0 <= native_edge_idx < len(edges):
            raise ValueError("Native first-ring face or edge index out of range")
        if original_face in candidate_faces:
            raise ValueError("Excluded source face is also a candidate")
        source_support, source_wires = oriented_edges(source_graph, original_face)
        source_uses = [edge for wire in source_wires for edge in wire
                       if edge["edge_curve_id"] == edge_id]
        if len(source_uses) != 1:
            raise ValueError("Excluded source face does not uniquely own original EDGE_CURVE")
        if SUPPORT_MAP.get(source_support) != faces[native_face].geomType():
            raise ValueError("Excluded source/native neighbor support mismatch")
        native_uses = [edge for edge in faces[native_face].Edges()
                       if same_index(edges, edge) == native_edge_idx]
        if len(native_uses) != 1:
            raise ValueError("Target native face does not uniquely use anchored TopoDS_Edge")
        if original_face in source_to_native and source_to_native[original_face] != native_face:
            raise ValueError("One original excluded face would map to multiple native faces")
        if native_face in native_to_source and native_to_source[native_face] != original_face:
            raise ValueError("Multiple original faces would map to one native face")
        source_to_native[original_face] = native_face
        native_to_source[native_face] = original_face
        if edge_id in edges_checked:
            raise ValueError("Duplicated source EDGE_CURVE first-ring anchor")
        edges_checked.add(edge_id)
        anchors[original_face].append({
            "source_original_edge_curve_id": edge_id,
            "native_edge_index": native_edge_idx,
            "source_candidate_face_id": record["source_candidate_face_id"],
            "native_candidate_face_index": record["native_candidate_face_index"],
            "source_neighbor_face_id": original_face,
            "native_neighbor_face_index": native_face,
        })

    excluded = []
    for original, references in sorted(anchors.items()):
        native_id = source_to_native[original]
        support, _ = oriented_edges(source_graph, original)
        excluded.append({
            "source_advanced_face_id": original,
            "native_face_index": native_id,
            "native_support_type": faces[native_id].geomType(),
            "source_support_type": support,
            "original_edge_anchor_count": len(references),
            "original_edge_anchors": sorted(references,
                                            key=lambda a: a["source_original_edge_curve_id"]),
            "all_neighbor_edges_mapped": False,
            "curved_surface_geometry_audited": False,
        })
    support_histogram = Counter(x["native_support_type"] for x in excluded)
    face_total = certificate["source_advanced_face_total"]
    mapped = len(source_to_native)
    report = {
        "schema": "apmesh-s3f-native-first-ring-source-face-ids-v1",
        "scope": "SOURCE_PLANAR_CANDIDATES_AND_EXCLUDED_DIRECT_FIRST_RING_ONLY",
        "source_model": model,
        "source_raw_sha256": source_sha256,
        "s3e_certificate_sha256": certificate["certificate_sha256"],
        "source_faces": face_total,
        "native_faces": len(faces),
        "candidate_faces_verified": len(candidate_faces),
        "excluded_source_faces_mapped_by_edge_identity": len(excluded),
        "distinct_original_first_ring_edge_anchors": len(edges_checked),
        "mapped_first_ring_source_face_ids": mapped,
        "remaining_unmapped_source_faces": face_total - mapped,
        "first_ring_mapped_face_fraction": mapped / face_total,
        "neighbor_support_histogram": dict(sorted(support_histogram.items())),
        "excluded_face_mapping": excluded,
        "first_ring_candidate_and_neighbor_face_ids_injective": True,
        "complete_original_edge_mapping": "NOT_ESTABLISHED",
        "complete_original_face_geometry_correspondence": "NOT_ESTABLISHED",
        "complete_original_model_patch_atlas": "NOT_RUN",
        "accepted_apmesh_tri_or_quad": "NOT_RUN",
        "genuine_external_nonmanifold_positive": "NOT_ESTABLISHED",
    }
    if mapped > face_total or len(faces) != face_total:
        raise ValueError("First-ring mapping inventory exceeds original source")
    report["report_sha256"] = _checksum(report)
    return report


def recompute_audit(step_text, native_shape, report, *, model, source_sha256):
    """Re-run native correlation and compare all first-ring claims to the source."""
    checksum = report.get("report_sha256")
    payload = dict(report)
    payload.pop("report_sha256", None)
    if checksum != _checksum(payload):
        raise ValueError("S3.F report checksum mismatch")
    original_certificate = correlate(step_text, native_shape, model=model,
                                     source_sha256=source_sha256)
    recomputed = first_ring(step_text, native_shape, original_certificate,
                            model=model, source_sha256=source_sha256)
    if recomputed != report:
        raise ValueError("S3.F source/native first-ring records differ from recomputation")
    return {
        "schema": "apmesh-s3f-first-ring-recomputed-audit-v1",
        "audit_pass": True,
        "original_first_ring_edges_checked": report["distinct_original_first_ring_edge_anchors"],
        "excluded_source_face_id_bindings_checked": report["excluded_source_faces_mapped_by_edge_identity"],
        "unmapped_original_source_faces": report["remaining_unmapped_source_faces"],
        "source_to_native_full_face_geometry": "NOT_ESTABLISHED",
        "accepted_apmesh_mesh": "NOT_RUN",
    }


def run_original(source_step, output_dir, *, model, expected_sha256=None):
    """Fail closed without writing output before all verification gates pass."""
    path = Path(source_step)
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    if model in SOURCES:
        if digest != SOURCES[model][1]:
            raise ValueError("Pinned original STEP raw SHA-256 mismatch")
    elif expected_sha256 is None:
        raise ValueError("Synthetic or unpinned STEP requires expected SHA-256")
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("Expected source SHA-256 mismatch")
    step_text = raw.decode("utf-8")
    native_shape = cq.importers.importStep(str(path)).val()
    certificate = correlate(step_text, native_shape, model=model,
                            source_sha256=digest)
    s3e_audit = verify_certificate(step_text, native_shape, certificate,
                                  model=model, source_sha256=digest)
    report = first_ring(step_text, native_shape, certificate, model=model,
                        source_sha256=digest)
    audit = recompute_audit(step_text, native_shape, report, model=model,
                            source_sha256=digest)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    for name, data in (("s3e_native_certificate.json", certificate),
                       ("s3e_recomputed_audit.json", s3e_audit),
                       ("s3f_first_ring_faces.json", report),
                       ("s3f_recomputed_audit.json", audit)):
        (target / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                                   encoding="utf-8")
    return {k: report[k] for k in (
        "source_model", "candidate_faces_verified",
        "excluded_source_faces_mapped_by_edge_identity",
        "distinct_original_first_ring_edge_anchors",
        "remaining_unmapped_source_faces")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-step", required=True, type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run_original(args.source_step, args.output,
                                  model=args.model,
                                  expected_sha256=args.expected_sha256), sort_keys=True))


if __name__ == "__main__":
    main()
