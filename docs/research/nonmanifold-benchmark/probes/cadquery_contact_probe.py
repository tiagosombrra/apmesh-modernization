"""Independent-of-STEP geometric endpoint contact check for mirrored CadQuery solids.

Geometric coordinate grouping is NOT topological welding and cannot detect
partial collinear overlaps. Do not use it as a non-manifold admission oracle.
"""
import json
from collections import Counter, defaultdict
import cadquery as cq


def shapes(name):
    if name == "three_touching_cuboids":
        w = 5.0
        return [cq.Workplane().transformed(offset=p).box(w, w, w).val()
                for p in [(-w/2, w/2, 0), (w/2, w/2, 0), (-w/2, -w/2, 0)]]
    if name == "t_junction":
        return [
            cq.Workplane("XY").box(20, 5, 5).val(),
            cq.Workplane("XY").transformed(offset=(0, 7.5, 0)).box(5, 10, 5).val(),
        ]
    if name == "cross_junction":
        return [
            cq.Workplane("XY").box(20, 4, 4).val(),
            cq.Workplane("XY").transformed(offset=(0, 6, 0)).box(4, 8, 4).val(),
            cq.Workplane("XY").transformed(offset=(0, -6, 0)).box(4, 8, 4).val(),
        ]
    if name == "two_touching_cuboids":
        return [
            cq.Workplane().box(10, 10, 10).val(),
            cq.Workplane().transformed(offset=(0, 7, 0)).box(10, 4, 10).val(),
        ]
    if name == "tangent_spheres":
        return [
            cq.Workplane("XY").transformed(offset=(-5, 0, 0)).sphere(5).val(),
            cq.Workplane("XY").transformed(offset=(4, 0, 0)).sphere(4).val(),
        ]
    raise ValueError(name)


def inspect(name):
    bodies = shapes(name)
    faces = [(body_index, f) for body_index, body in enumerate(bodies) for f in body.Faces()]
    uses = [(body_index, face_index, edge)
            for face_index, (body_index, face) in enumerate(faces) for edge in face.Edges()]
    topological = []
    for body_index, face_index, edge in uses:
        matched = next((record for record in topological if record[0].wrapped.IsSame(edge.wrapped)), None)
        if matched is None:
            matched = [edge, set()]
            topological.append(matched)
        matched[1].add(face_index)
    geometric = defaultdict(set)
    for body_index, face_index, edge in uses:
        vertices = edge.Vertices()
        if len(vertices) != 2:
            continue
        key = tuple(sorted(tuple(round(c, 9) for c in vertex.toTuple()) for vertex in vertices))
        if key[0] != key[1]:
            geometric[key].add((body_index, face_index))
    multibody = [
        {"endpoints": endpoints, "face_uses": len(incidence),
         "body_ids": sorted({body_index for body_index, _ in incidence})}
        for endpoints, incidence in geometric.items()
        if len(incidence) >= 3 and len({body_index for body_index, _ in incidence}) >= 2
    ]
    return {
        "model": name,
        "solids": len(bodies),
        "faces": len(faces),
        "topological_edges": len(topological),
        "topological_face_incidence_histogram": dict(sorted(Counter(len(v) for _, v in topological).items())),
        "multibody_coincident_exact_endpoint_segments": len(multibody),
        "multibody_segments": multibody,
        "qualifier": "SOURCE_MIRROR_EXACT_ENDPOINTS_ONLY_NOT_NATIVE_ORACLE",
    }


if __name__ == "__main__":
    for name in ("three_touching_cuboids", "t_junction", "cross_junction",
                 "two_touching_cuboids", "tangent_spheres"):
        print(json.dumps(inspect(name), sort_keys=True))
