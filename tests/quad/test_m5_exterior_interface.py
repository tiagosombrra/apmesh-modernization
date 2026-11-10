#!/usr/bin/env python3
"""Real C++ Quadtree exterior-interface experiment; NOT historical Delaunay.

Input QUAD OBJ and leaf CSV are emitted by actual C++ in the native test.
Experimental exterior TRI fans close the interface only in the UV unit square.
No production/historical centroid or all-QUAD claim is made.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path


def require(value, message):
    if not value:
        raise ValueError(message)


def native_obj(path):
    vertices, faces = [], []
    for line in path.read_text(encoding="ascii").splitlines():
        words = line.split()
        if not words:
            continue
        if words[0] == "v":
            vertices.append(tuple(map(float, words[1:4])))
        elif words[0] == "f":
            faces.append(tuple(int(x) - 1 for x in words[1:]))
    require(len(vertices) == 53 and len(faces) == 42 and
            all(len(f) == 4 for f in faces), "Real native C++ QUAD changed")
    return vertices, faces


def area(vertices, face):
    pts = [vertices[i] for i in face]
    return sum(a[0]*b[1] - b[0]*a[1]
               for a, b in zip(pts, pts[1:] + pts[:1])) / 2


def audit(vertices, quads, tris):
    require(len(set(vertices)) == len(vertices), "Duplicate coordinates/IDs")
    require(len(quads) == 42 and len(tris) == 60, "Wrong mixed element inventory")
    edges = defaultdict(list)
    used = set()
    a_quad = a_tri = 0.0
    for kind, faces in (("QUAD", quads), ("TRI", tris)):
        for face in faces:
            require(len(face) == (4 if kind == "QUAD" else 3) and
                    len(set(face)) == len(face) and
                    all(0 <= i < len(vertices) for i in face), "Invalid face indices")
            a = area(vertices, face)
            require(a > 1e-14, "Zero/negative orientation")
            if kind == "QUAD":
                a_quad += a
            else:
                a_tri += a
            used.update(face)
            for i, p in enumerate(face):
                q = face[(i + 1) % len(face)]
                edges[tuple(sorted((p, q)))].append((kind, p, q))
    require(used == set(range(len(vertices))), "Orphan vertices")
    require(abs(a_quad - .25) < 1e-12 and abs(a_tri - .75) < 1e-12,
            "Total area or area partition differs")
    seam, outer = [], []
    for edge, references in edges.items():
        require(len(references) in (1, 2), "Nonmanifold edge")
        if len(references) == 2:
            a, b = references
            require(a[1:] == b[1:][::-1], "Shared edge winding incorrect")
            if a[0] != b[0]:
                seam.append(edge)
        else:
            outer.append(edge)
    require(len(seam) == 20 and len(outer) == 16, "Interface/outer edge count changed")
    require(len(vertices) - len(edges) + len(quads) + len(tris) == 1,
            "UV combined graph is not a single disk")
    for a, b in outer:
        p, q = vertices[a], vertices[b]
        require((p[0] == q[0] and p[0] in (0, 1)) or
                (p[1] == q[1] and p[1] in (0, 1)),
                "Uncovered internal edge")
    graph = defaultdict(set)
    for a, b in seam:
        graph[a].add(b)
        graph[b].add(a)
    require(all(len(v) == 2 for v in graph.values()) and len(graph) == 20,
            "Interface not simple closed polyline")
    seen, pending = set(), [next(iter(graph))]
    while pending:
        x = pending.pop()
        if x not in seen:
            seen.add(x)
            pending.extend(graph[x] - seen)
    require(seen == set(graph), "Disconnected interface loops")
    require(abs(sum(math.dist(vertices[a][:2], vertices[b][:2])
                    for a, b in seam) - 2.0) < 1e-12, "Seam length changed")
    for a, b in edges:
        x, y, _ = vertices[a]
        xx, yy, _ = vertices[b]
        for k, (u, v, _) in enumerate(vertices):
            if k in (a, b):
                continue
            if (min(x, xx) < u < max(x, xx) or
                    min(y, yy) < v < max(y, yy)):
                require(abs((xx - x)*(v - y) - (yy - y)*(u - x)) > 1e-13,
                        "Hanging T-junction on mesh edge")
    return sorted(seam)


def negatives(vertices, quads, tris):
    mutations = [tris[1:], [tris[0][::-1]] + tris[1:],
                 tris + [tris[0]]]
    for altered in mutations:
        try:
            audit(vertices, quads, altered)
        except ValueError:
            continue
        raise AssertionError("Negative geometry mutation was not rejected")
    damaged = list(vertices)
    damaged[-1] = damaged[0]
    try:
        audit(damaged, quads, tris)
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate vertex mutation was not rejected")


def write_obj(path, vertices, quads, tris):
    with path.open("w", encoding="ascii", newline="\n") as out:
        out.write("# UV research: C++ QUAD + experimental exterior TRI fan; NOT Delaunay.\n")
        for x, y, z in vertices:
            out.write(f"v {x:.17g} {y:.17g} {z:.17g}\n")
        out.write("g QUAD_cpp_interior\n")
        for face in quads:
            out.write("f " + " ".join(str(i+1) for i in face) + "\n")
        out.write("g TRI_experimental_external_fan\n")
        for face in tris:
            out.write("f " + " ".join(str(i+1) for i in face) + "\n")


def svg(path, models):
    result = ['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="740" '
              'viewBox="0 0 1400 740" data-origin="actual-cpp-quad-plus-experimental-fan">',
              '<rect width="1400" height="740" fill="#fbfdff"/>',
              '<text x="30" y="38" font-family="Arial" font-size="25">'
              'APMesh: native C++ QUAD / experimental exterior TRI (UV)</text>']
    for idx, (name, v, q, t, seam) in enumerate(models):
        offset = 65 + idx * 685
        result.append(f'<text x="{offset}" y="77" font-family="Arial" font-size="17">'
                      f'{name}</text>')
        for kind, faces, color in (("tri", t, "#efc1a8"), ("quad", q, "#b1d4ec")):
            for face in faces:
                points = " ".join(f"{offset+560*v[j][0]:.4f},{650-560*v[j][1]:.4f}"
                                  for j in face)
                result.append(f'<polygon data-kind="{kind}" points="{points}" '
                              f'fill="{color}" stroke="#304b5b" stroke-width="0.85"/>')
        for a, b in seam:
            result.append(f'<line x1="{offset+560*v[a][0]:.4f}" '
                          f'y1="{650-560*v[a][1]:.4f}" '
                          f'x2="{offset+560*v[b][0]:.4f}" '
                          f'y2="{650-560*v[b][1]:.4f}" '
                          'stroke="#c23b54" stroke-width="2.6"/>')
        result.append(f'<rect x="{offset}" y="90" width="560" height="560" '
                      'fill="none" stroke="#203849" stroke-width="2.1"/>')
    result.append('<text x="30" y="718" font-family="Arial" font-size="14">'
                  '42 QUAD C++ + 60 TRI experimental fan; NOT historical Delaunay; Z=0.</text>')
    result.append('</svg>')
    path.write_text("\n".join(result) + "\n", encoding="utf-8")


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--directory", type=Path, required=True)
    folder = cli.parse_args().directory
    previous = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    require(previous["source"] == "real_APMesh_CXX_Quadtree_fixture" and
            previous["triangles_emitted"] == 0 and
            previous["excluded_boundary_unmeshed_leaves"] == 12,
            "Input does not come from real native C++ unmeshed Quadtree")
    with (folder / "tree_regions.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    require(len(rows) == 19 and
            Counter(r["region"] for r in rows) ==
            {"quad_candidate": 7, "excluded_boundary_unmeshed": 12},
            "Input Quadtree classification changed")
    boxes = [tuple(float(r[k]) for k in
             ("min_u", "min_v", "max_u", "max_v")) for r in rows]
    models = []
    for mode in ("vertex_mean", "area_centroid"):
        vertices, quads = native_obj(folder / f"quads_{mode}.obj")
        require(len(set(vertices)) == len(vertices), "C++ source coordinate IDs differ")
        known = {(x, y): i for i, (x, y, z) in enumerate(vertices)}
        candidates = set(known)
        for x0, y0, x1, y1 in boxes:
            candidates.update(((x0, y0), (x1, y0), (x1, y1), (x0, y1)))
        def point_id(p):
            if p not in known:
                known[p] = len(vertices)
                vertices.append((p[0], p[1], 0.0))
            return known[p]
        triangles = []
        for row, (x0, y0, x1, y1) in zip(rows, boxes):
            if row["region"] != "excluded_boundary_unmeshed":
                continue
            frame = (((x0,y0),(x1,y0)), ((x1,y0),(x1,y1)),
                     ((x1,y1),(x0,y1)), ((x0,y1),(x0,y0)))
            perimeter = []
            for a, b in frame:
                dx, dy = b[0]-a[0], b[1]-a[1]
                nodes = [p for p in candidates
                         if abs(dx*(p[1]-a[1]) - dy*(p[0]-a[0])) < 1e-14
                         and min(a[0],b[0]) <= p[0] <= max(a[0],b[0])
                         and min(a[1],b[1]) <= p[1] <= max(a[1],b[1])]
                nodes.sort(key=lambda p:(p[0]-a[0])*dx + (p[1]-a[1])*dy)
                require(len(nodes) >= 2 and nodes[0] == a and nodes[-1] == b,
                        "Quadtree exterior side not represented")
                perimeter.extend(nodes[:-1])
            require(len(perimeter) >= 4 and len(set(perimeter)) == len(perimeter),
                    "External fan perimeter invalid")
            center = point_id(((x0+x1)/2, (y0+y1)/2))
            for a, b in zip(perimeter, perimeter[1:] + perimeter[:1]):
                triangles.append((point_id(a), point_id(b), center))
        seam = audit(vertices, quads, triangles)
        negatives(vertices, quads, triangles)
        write_obj(folder / f"hybrid_experimental_{mode}.obj", vertices, quads, triangles)
        models.append((mode, vertices, quads, triangles, seam))
    require(models[0][2] == models[1][2] and models[0][3] == models[1][3],
            "Center rule unexpectedly changed hybrid connectivity")
    with (folder / "quad_tri_interface.csv").open("w", newline="", encoding="ascii") as out:
        writer = csv.writer(out)
        writer.writerow(("vertex_a", "vertex_b", "u_a", "v_a", "u_b", "v_b"))
        for a, b in models[0][4]:
            va, vb = models[0][1][a], models[0][1][b]
            writer.writerow((a, b, f"{va[0]:.17g}", f"{va[1]:.17g}",
                             f"{vb[0]:.17g}", f"{vb[1]:.17g}"))
    svg(folder / "experimental_hybrid.svg", models)
    manifest = {
        "schema": 1,
        "source": "native_CPP_Quadtree_OBJs_and_leaf_CSV",
        "status": "UV_conforming_experimental_fan_NOT_historical_Delaunay",
        "historical_hybrid_complete": False,
        "all_quad_enabled": False,
        "historic_centroid_approved": False,
        "quad_count": 42, "tri_count": 60, "interface_edge_count": 20,
        "interface_one_closed_loop": True, "quad_area": .25,
        "tri_area": .75, "total_area": 1.0,
        "mutations_rejected": 4,
        "source_sha256": {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
                          for name in ("tree_regions.csv", "quads_vertex_mean.obj",
                                       "quads_area_centroid.obj", "manifest.json")},
    }
    (folder / "experimental_hybrid_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("m5_experimental_seam=ok cpp_quads=42 experimental_tri=60 "
          "seam=20 area=1.0 negative_mutations=4 historical_Delaunay=NOT_DONE")


if __name__ == "__main__":
    main()
