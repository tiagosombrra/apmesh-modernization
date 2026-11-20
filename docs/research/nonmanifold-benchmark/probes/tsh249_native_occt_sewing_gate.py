#!/usr/bin/env python3
"""Reproduce native OCCT non-manifold sewing on byte-pinned Tsh249 STEP.

A three-face sewn edge is an explicitly reconstructed topology, not a
three-face EDGE_CURVE already shared in the original STEP source. This probe
neither admits an industrial source-positive nor runs APMesh TRI/QUAD.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha1, sha256
import importlib.metadata
import json
import math
import os
from pathlib import Path
import sys

SOURCE_GIT_BLOB_SHA1 = "ce612e8959c3e8954e2c0e565e291ecbbe6cd5ff"
SOURCE_SHA256 = "d966aa342fea76d6027890fa4fee89283e5bcb2cbcbb9552cc3240d6bbad380d"
SOURCE_UPSTREAM_COMMIT = "2a27aed219fbf930218aac5f24b07c131411b3de"
SOURCE_EDGE_IDS = (10, 38, 66)
SOURCE_FACE_IDS = (27, 55, 83)
SEW_TOLERANCE = 1.0e-7
TOPOLOGY_TOLERANCE = 2.0e-7
FACE_AREA_TOLERANCE = 1.0e-8
EXPECTED_CENTERS = ((3.0, 1.0, 0.0), (5.0, 0.0, 1.0), (7.0, -1.0, 0.0))
EXPECTED_TRIANGLE_CORNERS = (
    ((0.0, 0.0, 0.0), (6.0, 0.0, 0.0), (3.0, 3.0, 0.0)),
    ((2.0, 0.0, 0.0), (8.0, 0.0, 0.0), (5.0, 0.0, 3.0)),
    ((4.0, 0.0, 0.0), (10.0, 0.0, 0.0), (7.0, -3.0, 0.0)),
)
EXPECTED_SHARED = {
    (2.0, 4.0): (0, 1),
    (4.0, 6.0): (0, 1, 2),
    (6.0, 8.0): (1, 2),
}


def verify_pinned_step(raw: bytes) -> dict:
    """Reject mutated sources and distinguish Git-blob from raw SHA-256."""
    if sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("Tsh249 source SHA-256 mismatch")
    git_blob = sha1((f"blob {len(raw)}\0").encode("ascii") + raw).hexdigest()
    if git_blob != SOURCE_GIT_BLOB_SHA1:
        raise ValueError("Tsh249 Git blob identity mismatch")
    return {"raw_sha256": SOURCE_SHA256, "git_blob_sha1": git_blob, "original_source_git_commit": SOURCE_UPSTREAM_COMMIT,
            "original_advanced_faces": list(SOURCE_FACE_IDS), "independent_original_edges": list(SOURCE_EDGE_IDS),
            "original_source_edge_three_plus_count": 0,
            "source_original_edge_identity_census": "F12_PINNED_STRUCTURAL_AUDIT_NOT_REPEATED_BY_F13"}


def _kernel():
    """Import native OCCT modules only after checking immutable source bytes."""
    from OCP.BRep import BRep_Tool
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_VERTEX
    from OCP.TopExp import TopExp, TopExp_Explorer
    from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
    from OCP.TopoDS import TopoDS
    return locals()


def _subshapes(shape, kind, k):
    explorer = k["TopExp_Explorer"](shape, kind)
    values = []
    while explorer.More():
        values.append(explorer.Current())
        explorer.Next()
    return values


def _close(a, b, tol=TOPOLOGY_TOLERANCE):
    return len(a) == len(b) and all(abs(x - y) <= tol for x, y in zip(a, b))


def classify_centroid(point):
    """Map native triangular faces to pinned source owners without face ordering."""
    matches = [i for i, p in enumerate(EXPECTED_CENTERS) if _close(point, p)]
    if len(matches) != 1:
        raise ValueError("Native face centroid cannot be uniquely mapped to source fin")
    return matches[0]


def point_on_closed_segment(point, a, b, tol=TOPOLOGY_TOLERANCE):
    """Check bounded 3D segment membership without proximity-based welding."""
    delta = tuple(b[i] - a[i] for i in range(3))
    offset = tuple(point[i] - a[i] for i in range(3))
    squared = sum(x*x for x in delta)
    if squared <= tol*tol:
        raise ValueError("Degenerate expected source edge")
    t = sum(offset[i]*delta[i] for i in range(3)) / squared
    if t < -tol or t > 1 + tol:
        return False
    return math.sqrt(sum((offset[i] - t*delta[i])**2 for i in range(3))) <= tol


def check_source_triangle_boundary(face, source_idx, k):
    """Preserve the pinned corners and forbid off-boundary sewn vertices."""
    corners = EXPECTED_TRIANGLE_CORNERS[source_idx]
    vertices = _subshapes(face, k["TopAbs_VERTEX"], k)
    values = [tuple(k["BRep_Tool"].Pnt_s(k["TopoDS"].Vertex_s(v)).Coord())
              for v in vertices]
    if not all(any(_close(v, corner) for v in values) for corner in corners):
        raise ValueError("A source face lost an original triangle corner")
    if any(not any(point_on_closed_segment(v, corners[j], corners[(j+1)%3])
                   for j in range(3)) for v in values):
        raise ValueError("An OCCT split vertex lies outside the original triangle boundary")
    return len(values)


def edge_interval_on_source_axis(vertices):
    """Return X bounds only for a verified two-vertex edge on the X axis."""
    if len(vertices) != 2 or not all(len(v) == 3 and all(math.isfinite(x) for x in v) for v in vertices):
        raise ValueError("Native edge vertex structure malformed")
    if any(abs(v[1]) > TOPOLOGY_TOLERANCE or abs(v[2]) > TOPOLOGY_TOLERANCE for v in vertices):
        raise ValueError("Claimed shared source edge does not lie on X axis")
    lo, hi = sorted((vertices[0][0], vertices[1][0]))
    if hi - lo <= TOPOLOGY_TOLERANCE:
        raise ValueError("Zero-length or microscopic purported shared edge")
    return (lo, hi)


def inspect_native_shape(shape, k):
    """Count unique face owners per actual OCCT edge identity; retain sections."""
    faces = _subshapes(shape, k["TopAbs_FACE"], k)
    shells = _subshapes(shape, k["TopAbs_SHELL"], k)
    if len(faces) != 3:
        raise ValueError("Native shape does not retain exactly three source faces")
    face_to_index = []
    faces_report = []
    for face in faces:
        props = k["GProp_GProps"]()
        k["BRepGProp"].SurfaceProperties_s(face, props)
        area, center = props.Mass(), tuple(props.CentreOfMass().Coord())
        idx = classify_centroid(center)
        if not math.isfinite(area) or abs(area - 9.0) > FACE_AREA_TOLERANCE:
            raise ValueError("Original planar face area changed in native topology")
        if idx in face_to_index:
            raise ValueError("One source fin is duplicated in OCCT face mapping")
        retained_vertices = check_source_triangle_boundary(face, idx, k)
        face_to_index.append(idx)
        faces_report.append({"source_advanced_face_id": SOURCE_FACE_IDS[idx],
                             "source_fin_index": idx, "source_boundary_vertices_after_split": retained_vertices, "area_source_units_squared": area,
                             "centroid": [float(v) for v in center]})
    if set(face_to_index) != {0, 1, 2}:
        raise ValueError("Not all original source fin identities survived")
    indexed = k["TopTools_IndexedDataMapOfShapeListOfShape"]()
    k["TopExp"].MapShapesAndAncestors_s(shape, k["TopAbs_EDGE"], k["TopAbs_FACE"], indexed)
    histogram = Counter()
    shared_sections = []
    for eid in range(1, indexed.Extent() + 1):
        edge = indexed.FindKey(eid)
        ancestors = list(indexed.FindFromIndex(eid))
        unique_owners = []
        for ancestor in ancestors:
            if not any(ancestor.IsSame(other) for other in unique_owners):
                unique_owners.append(ancestor)
        face_ids = []
        for owner in unique_owners:
            matches = [face_to_index[j] for j, face in enumerate(faces) if face.IsSame(owner)]
            if len(matches) != 1:
                raise ValueError("Sewn edge refers to an unmapped or duplicated face")
            face_ids.append(matches[0])
        if len(set(face_ids)) != len(face_ids) or not (1 <= len(face_ids) <= 3):
            raise ValueError("Invalid native edge-face incidence count")
        histogram[len(face_ids)] += 1
        if len(face_ids) >= 2:
            vv = _subshapes(edge, k["TopAbs_VERTEX"], k)
            coords = [tuple(k["BRep_Tool"].Pnt_s(k["TopoDS"].Vertex_s(v)).Coord()) for v in vv]
            segment = edge_interval_on_source_axis(coords)
            shared_sections.append({"x_interval": [float(v) for v in segment],
                                    "source_face_ids": [SOURCE_FACE_IDS[i] for i in sorted(face_ids)],
                                    "distinct_native_face_incidence": len(face_ids)})
    shared_sections.sort(key=lambda x: x["x_interval"])
    return {"faces": len(faces), "shells": len(shells), "native_unique_edges": indexed.Extent(),
            "edge_face_incidence_histogram": {str(i): histogram[i] for i in (1, 2, 3) if histogram[i]},
            "source_faces": sorted(faces_report, key=lambda x: x["source_fin_index"]),
            "shared_axis_sections": shared_sections,
            "total_source_face_area": sum(v["area_source_units_squared"] for v in faces_report)}


def require_shared_sections(sections, expected):
    """Validate the complete source-face lineage of each shared native section."""
    if len(sections) != len(expected):
        raise ValueError("Unexpected number of shared native source-axis segments")
    matched = set()
    for row in sections:
        segment = row["x_interval"]
        choices = [a for a in expected if _close(segment, a)]
        if len(choices) != 1 or choices[0] in matched:
            raise ValueError("Unexpected, duplicated, or displaced native source-axis segment")
        matched.add(choices[0])
        wanted_faces = {SOURCE_FACE_IDS[i] for i in expected[choices[0]]}
        if set(row["source_face_ids"]) != wanted_faces or row["distinct_native_face_incidence"] != len(wanted_faces):
            raise ValueError("Native sewn section lost or gained unexpected source face owners")
    if matched != set(expected):
        raise ValueError("Native sewn graph missing expected segments")


def verify_topology(original, conventional, nonmanifold):
    """Require the non-manifold mode to change actual edge identity as predicted."""
    for label, record, faces, unique, shells, histogram in (
        ("original", original, 3, 9, 3, {"1": 9}),
        ("conventional", conventional, 3, 12, 1, {"1": 9, "2": 3}),
        ("nonmanifold", nonmanifold, 3, 11, 1, {"1": 8, "2": 2, "3": 1}),
    ):
        if (record["faces"] != faces or record["native_unique_edges"] != unique or record["shells"] != shells
                or record["edge_face_incidence_histogram"] != histogram):
            raise ValueError(f"Unexpected {label} OCCT edge incidence / shell graph")
        if abs(record["total_source_face_area"] - 27.0) > 3 * FACE_AREA_TOLERANCE:
            raise ValueError(f"{label} source area not preserved")
    require_shared_sections(conventional["shared_axis_sections"],
                            {(2.0, 4.0): (0, 1), (4.0, 6.0): (0, 1), (6.0, 8.0): (1, 2)})
    require_shared_sections(nonmanifold["shared_axis_sections"], EXPECTED_SHARED)
    # The conventional mode still contains a geometric triple intersection,
    # but splits it into pairwise distinct topological edges (not 3 owners).
    if conventional["edge_face_incidence_histogram"].get("3", 0):
        raise ValueError("Conventional sewing unexpectedly constructed non-manifold edge")


def run_original_native_reconstruction(step_file: str | Path):
    """Import authentic, byte-pinned STEP and compare both native sewing modes."""
    path = Path(step_file)
    raw = path.read_bytes()
    source = verify_pinned_step(raw)
    k = _kernel()
    rd = k["STEPControl_Reader"]()
    if rd.ReadFile(str(path)) != k["IFSelect_RetDone"]:
        raise ValueError("OCCT failed native STEP source parse")
    if rd.TransferRoots() != 1:
        raise ValueError("OCCT did not transfer the single pinned STEP root")
    native = rd.OneShape()
    if native.IsNull():
        raise ValueError("OCCT STEP source imported null topology")
    if not k["BRepCheck_Analyzer"](native).IsValid():
        raise ValueError("OCCT original STEP BRepCheck invalid")
    before = inspect_native_shape(native, k)
    before["occt_brepcheck_valid"] = True
    results = {}
    for mode in (False, True):
        sewing = k["BRepBuilderAPI_Sewing"](SEW_TOLERANCE)
        sewing.SetNonManifoldMode(mode)
        for face in _subshapes(native, k["TopAbs_FACE"], k):
            sewing.Add(face)
        sewing.Perform()
        new_shape = sewing.SewedShape()
        if new_shape.IsNull():
            raise ValueError("OCCT sewing generated an empty shape")
        if not k["BRepCheck_Analyzer"](new_shape).IsValid():
            raise ValueError("OCCT sewn BRepCheck invalid")
        result = inspect_native_shape(new_shape, k)
        result["occt_brepcheck_valid"] = True
        result["nonmanifold_mode"] = mode
        result["occt_free_edge_counter"] = sewing.NbFreeEdges()
        result["occt_contiguous_edge_counter"] = sewing.NbContigousEdges()
        result["occt_multiple_edge_counter"] = sewing.NbMultipleEdges()
        if (result["occt_free_edge_counter"] != int(result["edge_face_incidence_histogram"].get("1", 0))
                or result["occt_contiguous_edge_counter"] != int(result["edge_face_incidence_histogram"].get("2", 0))
                or result["occt_multiple_edge_counter"] != int(result["edge_face_incidence_histogram"].get("3", 0))):
            raise ValueError("OCCT native sewing counters disagree with independent face-edge mapping")
        results["nonmanifold" if mode else "conventional"] = result
    verify_topology(before, results["conventional"], results["nonmanifold"])
    if results["nonmanifold"]["occt_multiple_edge_counter"] != 1:
        raise ValueError("OCCT did not independently count one multiple edge")
    if results["conventional"]["occt_multiple_edge_counter"] != 0:
        raise ValueError("OCCT conventional mode counted multiple edge")
    return {
        "schema": "apmesh-s40f13-tsh249-native-occt-sewing-v1",
        "classification": "POST_SEWING_THREE_FACE_NATIVE_EDGE_CONFIRMED_NOT_ORIGINAL_SOURCE_POSITIVE",
        "source": source,
        "kernel": {"cadquery_ocp_version": importlib.metadata.version("cadquery-ocp"),
                   "native_sewing_tolerance_source_units": SEW_TOLERANCE},
        "before_native_sewing": before,
        "after_conventional_sewing": results["conventional"],
        "after_nonmanifold_sewing": results["nonmanifold"],
        "native_real_original_step_import_executed": True,
        "native_nonmanifold_three_face_edge_confirmed": True,
        "source_original_three_plus_edge_confirmed": False,
        "formal_continuous_surface_equivalence_certified": False,
        "native_sewn_to_apmesh_bezier_conversion_executed": False,
        "apmesh_cpp_tri_quad_executed": False,
        "new_s40_source_faces_admitted": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-step", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    try:
        if os.path.lexists(args.receipt):
            raise FileExistsError("Refusing to overwrite an existing native receipt")
        report = run_original_native_reconstruction(args.original_step)
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        # A successful immutable source/native audit is the only writing path.
        with args.receipt.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"classification": "BLOCKED_NO_NATIVE_RECONSTRUCTION_CLAIM",
                          "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True), file=sys.stderr)
        return 3
    print(json.dumps({"classification": report["classification"],
                      "actual_native_multiple_edges": report["after_nonmanifold_sewing"]["occt_multiple_edge_counter"],
                      "new_s40_source_faces_admitted": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
