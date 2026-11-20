#!/usr/bin/env python3
"""Native STEP-like CAD source-mirror partial-contact decomposition (research R3.C2).

Only planar, fully contacting smaller-face/host-face rectangles are supported.
No production model, source solid or historical APMesh algorithm is modified.
"""
from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

UPSTREAM = {
    "repository": "fusion-energy/model_benchmark_zoo",
    "revision": "3a2e69fe62209e33a1e176d816609d69a2aebadc",
    "source_mode": "PINNED_DEFAULTS_RECREATED_NOT_UPSTREAM_EXECUTION",
}
BOUNDS = 1.0e-8
SOURCE_CONTACT_DISTANCE_BUDGET = 1.0e-12


class UnsupportedContact(ValueError):
    """A source contact lies outside the intentionally limited R3.C2 domain."""


def source_solids(case: str, *, gap: float = 0., penetration: float = 0.,
                  arm_height_scale: float = 1., offset_x: float = 0.,
                  arm_width_scale: float = 1.):
    """Mirror pinned CadQuery recipes, retaining each independent source body."""
    if not all(math.isfinite(x) for x in (gap, penetration, arm_height_scale, offset_x, arm_width_scale)):
        raise ValueError("Non-finite source parameter")
    if gap < 0 or penetration < 0 or (gap and penetration):
        raise ValueError("Invalid gap or penetration")
    if arm_height_scale <= 0 or arm_width_scale <= 0:
        raise ValueError("Invalid shape scale")
    if case == "t_junction":
        main = cq.Workplane("XY").box(20, 5, 5).val()
        arm = cq.Workplane("XY").transformed(
            offset=(offset_x, 7.5 + gap - penetration, 0)
        ).box(5 * arm_width_scale, 10, 5 * arm_height_scale).val()
        return {"main": main, "branch": arm}
    if case == "cross_junction":
        main = cq.Workplane("XY").box(20, 4, 4).val()
        top = cq.Workplane("XY").transformed(
            offset=(offset_x, 6 + gap - penetration, 0)
        ).box(4 * arm_width_scale, 8, 4 * arm_height_scale).val()
        bottom = cq.Workplane("XY").transformed(
            offset=(0, -6, 0)
        ).box(4, 8, 4).val()
        return {"main": main, "top_arm": top, "bottom_arm": bottom}
    raise ValueError(f"Unknown source case: {case}")


def _native_boolean(kind: str, first, second):
    """Run an OCCT Boolean and refuse a partially failed native operation."""
    cls = BRepAlgoAPI_Common if kind == "common" else BRepAlgoAPI_Cut
    operation = cls(first.wrapped, second.wrapped)
    operation.Build()
    if not operation.IsDone():
        raise UnsupportedContact(f"Open CASCADE {kind} operation failed")
    return cq.Shape(operation.Shape())


def _quad(face):
    """Validate a nondegenerate, single-wire planar four-sided native face."""
    if (not face.isValid() or face.geomType() != "PLANE" or
            len(face.Wires()) != 1 or len(face.Edges()) != 4 or
            len(face.Vertices()) != 4 or face.Area() < 1e-9):
        raise UnsupportedContact("Trimmed, periodic, hole or nonquad face not supported")
    if any(edge.geomType() != "LINE" for edge in face.Edges()):
        raise UnsupportedContact("Nonlinear boundary needs R3 curved segmentation")
    return face


def _faces_incident_on_edge(shape, edge):
    return [(i, face) for i, face in enumerate(shape.Faces())
            if any(candidate.wrapped.IsSame(edge.wrapped) for candidate in face.Edges())]


def _vertical_side_edges(face):
    result = []
    for edge in face.Edges():
        vertices = edge.Vertices()
        if len(vertices) != 2:
            continue
        a, b = (v.toTuple() for v in vertices)
        if (abs(a[0]-b[0]) < BOUNDS and abs(a[1]-b[1]) < BOUNDS
                and abs(a[2]-b[2]) > BOUNDS):
            result.append(edge)
    if len(result) != 2:
        raise UnsupportedContact("Contact does not have two full-height vertical edges")
    return result


def detect_contacts(solids):
    """Identify opposing, full smaller-face contacts without volume penetration."""
    host = solids["main"]
    results = []
    for arm_name, arm in solids.items():
        if arm_name == "main":
            continue
        volume = sum(solid.Volume() for solid in _native_boolean("common", host, arm).Solids())
        if volume > 1e-9:
            raise UnsupportedContact("Overlapping source solid volumes are not contacts")
        for hi, host_face in enumerate(host.Faces()):
            for ai, arm_face in enumerate(arm.Faces()):
                if host_face.geomType() != "PLANE" or arm_face.geomType() != "PLANE":
                    continue
                common = _native_boolean("common", host_face, arm_face)
                overlap_area = sum(face.Area() for face in common.Faces())
                if overlap_area <= 1e-9:
                    continue
                # Native Booleans may report coplanar overlap for nearly
                # touching disjoint planes because of their internal fuzz.
                # Require a stricter source geometry distance independently
                # of the larger output sewing tolerance.
                proximity = BRepExtrema_DistShapeShape(host_face.wrapped, arm_face.wrapped)
                proximity.Perform()
                if not proximity.IsDone() or proximity.Value() > SOURCE_CONTACT_DISTANCE_BUDGET:
                    raise UnsupportedContact('Near-contact exceeds strict source interface distance budget')
                dot = host_face.normalAt().dot(arm_face.normalAt())
                if abs(dot + 1) > 1e-8:
                    raise UnsupportedContact("Coincident interfaces must have opposite normals")
                if abs(overlap_area - arm_face.Area()) > 1e-8:
                    raise UnsupportedContact("Partial trimming of both source faces is unsupported")
                if host_face.Area() <= arm_face.Area() + 1e-8:
                    raise UnsupportedContact("Smaller arm face must be properly interior to host face")
                faces = common.Faces()
                if len(faces) != 1:
                    raise UnsupportedContact("Multi-component contact is unsupported")
                results.append({"host_id": "main", "arm_id": arm_name,
                                "host_face_id": hi, "arm_face_id": ai,
                                "source_host": host_face, "source_arm": arm_face,
                                "contact": _quad(faces[0])})
    if len(results) != len(solids)-1:
        raise UnsupportedContact("Expected one positive-area host/arm contact per arm")
    if len({r['host_face_id'] for r in results}) != len(results):
        raise UnsupportedContact("Multiple contact arms on the same host face are not supported")
    # Two branches must not overlap or contact along another undisclosed interface.
    arms = [solid for name, solid in solids.items() if name != "main"]
    if len(arms) == 2 and sum(f.Area() for f in _native_boolean("common", arms[0], arms[1]).Faces()) > 1e-9:
        raise UnsupportedContact("Unexpected contact or overlap between separate arms")
    return sorted(results, key=lambda r: r['arm_id'])


def _face_signature(face):
    """A stable descriptor for evidence, never an alternate source-edge identity."""
    c = face.Center().toTuple()
    return (tuple(round(x, 9) for x in c), round(face.Area(), 9))


def _topology(shape):
    """Count distinct face users via native OCCT TopoDS_IsSame identity."""
    entries=[]
    for fi, face in enumerate(shape.Faces()):
        for edge in face.Edges():
            matched = next((e for e in entries if e['edge'].wrapped.IsSame(edge.wrapped)), None)
            if matched is None:
                matched = {"edge": edge, "face_ids": set()}
                entries.append(matched)
            matched['face_ids'].add(fi)
    hist = dict(sorted(Counter(len(e['face_ids']) for e in entries).items()))
    triples = []
    for e in entries:
        if len(e['face_ids']) >= 3:
            endpoints = sorted(tuple(round(x,9) for x in v.toTuple()) for v in e['edge'].Vertices())
            triples.append({"endpoints": endpoints, "face_incidence": len(e['face_ids']),
                            "length": round(e['edge'].Length(), 9)})
    triples.sort(key=lambda x: x['endpoints'])
    return entries, hist, triples


def extract(case, solids=None, *, nonmanifold=True):
    """Return a source-identity-preserving split-face graph and native sewn shape."""
    solids = solids or source_solids(case)
    if set(solids) != ({"main", "branch"} if case == "t_junction" else
                       {"main", "top_arm", "bottom_arm"}):
        raise ValueError("Incorrect source bodies for case")
    source = {}
    for name, solid in solids.items():
        if not solid.isValid() or len(solid.Solids()) != 1:
            raise UnsupportedContact("Invalid source solid")
        source[name] = {"faces": len(solid.Faces()), "edges": len(solid.Edges()),
                        "volume": round(solid.Volume(), 9), "valid": True}
    contacts = detect_contacts(solids)
    sheets = []
    contact_info = []
    for contact_index, contact in enumerate(contacts):
        arm_name = contact['arm_id']
        host = contact['source_host']; arm = contact['source_arm']
        remainder = _native_boolean("cut", host, arm)
        if len(remainder.Faces()) != 2:
            raise UnsupportedContact("Contact remainder is not two quadrilateral wings")
        wings = sorted((_quad(f) for f in remainder.Faces()), key=lambda f: f.Center().x)
        if abs(sum(f.Area() for f in wings) + contact['contact'].Area() - host.Area()) > 1e-8:
            raise UnsupportedContact("Contact subtraction violates native area conservation")
        contact_sheet = {"role": "interface", "regions": ["main", arm_name],
                         "source_faces": [{"body": "main", "face_index": contact['host_face_id']},
                                          {"body": arm_name, "face_index": contact['arm_face_id']}],
                         "face": contact['contact']}
        sheets.append(contact_sheet)
        for side, face in zip(("left", "right"), wings):
            sheets.append({"role": f"host_exterior_{side}", "regions": ["main", "VOID"],
                           "source_faces": [{"body": "main", "face_index": contact['host_face_id']}],
                           "face": face})
        flanks=[]
        for edge in _vertical_side_edges(arm):
            adjacent = [(idx, f) for idx, f in _faces_incident_on_edge(solids[arm_name], edge)
                        if idx != contact['arm_face_id']]
            if len(adjacent) != 1:
                raise UnsupportedContact("Source arm edge adjacency is not two-manifold")
            flanks.append(adjacent[0])
        flanks.sort(key=lambda entry: entry[1].Center().x)
        for side, (fid, face) in zip(("left", "right"), flanks):
            sheets.append({"role": f"arm_exterior_{side}", "regions": [arm_name, "VOID"],
                           "source_faces": [{"body": arm_name, "face_index": fid}],
                           "face": _quad(face)})
        contact_info.append({"contact_index": contact_index, "host_body": "main",
                             "arm_body": arm_name, "host_face_index": contact['host_face_id'],
                             "arm_face_index": contact['arm_face_id'],
                             "original_host_area": round(host.Area(), 9),
                             "original_arm_area": round(arm.Area(), 9),
                             "overlap_area": round(contact['contact'].Area(), 9),
                             "wings_area": [round(f.Area(),9) for f in wings],
                             "generated_sheet_count": 5})
    sewn = BRepBuilderAPI_Sewing(1e-8, True, True, True, True)
    sewn.SetNonManifoldMode(nonmanifold)
    for sheet in sheets:
        sewn.Add(sheet['face'].wrapped)
    sewn.Perform()
    result = cq.Shape(sewn.SewedShape())
    if not result.isValid() or len(result.Faces()) != len(sheets):
        raise UnsupportedContact("Sewn feature graph is invalid or drops faces")
    identities = {_face_signature(face): index for index, face in enumerate(result.Faces())}
    if len(identities) != len(sheets):
        raise UnsupportedContact("Ambiguous split-to-sewn face provenance")
    for sheet in sheets:
        key = _face_signature(sheet['face'])
        if key not in identities:
            raise UnsupportedContact("Source-subface identity lost during nonmanifold sewing")
        sheet['sewn_face_index'] = identities[key]
    _, histogram, triples = _topology(result)
    expected_count = 2 * len(contacts) if nonmanifold else 0
    if histogram.get(3, 0) != expected_count or any(k >= 4 for k in histogram):
        if nonmanifold:
            raise UnsupportedContact("Expected source-derived three-way edge is missing")
    for sheet in sheets:
        _quad(result.Faces()[sheet['sewn_face_index']])
    report = {"schema": "apmesh-r3c2-occt-contact-v1", "case": case,
              "upstream": UPSTREAM, "source_bodies": source,
              "source_solid_count": len(source),
              "source_solid_volumes_preserved": True,
              "nonmanifold_mode": nonmanifold,
              "sewing_tolerance": 1e-8,
              "source_contact_distance_budget": SOURCE_CONTACT_DISTANCE_BUDGET,
              "contact_count": len(contacts), "contact_records": contact_info,
              "sheet_count": len(sheets),
              "all_sheets_planar_four_sided": True,
              "source_face_to_subface": [{"index": i, "sewn_face_index": s['sewn_face_index'],
                  "role": s['role'], "regions": s['regions'],
                  "source_faces": s['source_faces'],
                  "area": round(s['face'].Area(),9),
                  "centroid": [round(x,9) for x in s['face'].Center().toTuple()]}
                                         for i,s in enumerate(sheets)],
              "native_topology": {"shape_type": result.ShapeType(),
                  "kernel_valid": bool(result.isValid()),
                  "face_count": len(result.Faces()),
                  "unique_edge_count": sum(histogram.values()),
                  "face_per_edge_histogram": histogram,
                  "triple_edges": triples},
              "classification": "BOUNDED_SOURCE_RECIPE_MIRROR_PARTIAL_CONTACT_PROOF",
              "g2_external_admission": "NOT_GRANTED",
              "apmesh_generation": "NOT_RUN"}
    return result, report


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case', required=True, choices=('t_junction', 'cross_junction'))
    p.add_argument('--output-dir', required=True, type=Path)
    args = p.parse_args()
    shape, report = extract(args.case)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir/f'{args.case}_topology.json').write_text(
        json.dumps(report, sort_keys=True, indent=2)+'\n', encoding='utf-8')
    shape.exportBrep(str(args.output_dir/f'{args.case}_interface.brep'))
    print(json.dumps({"case":args.case,"sheet_count":report['sheet_count'],
                      "triple_edges":len(report['native_topology']['triple_edges']),
                      "admission":report['g2_external_admission']}, sort_keys=True))

if __name__ == '__main__':
    main()
