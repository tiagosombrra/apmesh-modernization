#!/usr/bin/env python3
"""Audit files produced by the actual C++ real Quadtree exporter."""

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def verify(test, message):
    if not test:
        raise AssertionError(message)


def parse_obj(path):
    vertices, faces = [], []
    for line in path.read_text(encoding="ascii").splitlines():
        if line.startswith("v "):
            vertices.append(tuple(float(x) for x in line.split()[1:4]))
        elif line.startswith("f "):
            face = [int(x) - 1 for x in line.split()[1:]]
            verify(len(face) == 4 and len(set(face)) == 4, "Not a 4-node face")
            faces.append(face)
    verify(len(vertices) == 53 and len(faces) == 42,
           "Real included source-tree mesh inventory changed")
    edges = Counter()
    area = 0.0
    for face in faces:
        verify(all(0 <= i < len(vertices) for i in face),
               "OBJ has an invalid vertex index")
        pts = [vertices[i] for i in face]
        twice = sum(a[0] * b[1] - a[1] * b[0]
                    for a, b in zip(pts, pts[1:] + pts[:1]))
        verify(twice > 1e-14, "Inverted or degenerate research QUAD")
        area += twice / 2
        for a, b in zip(face, face[1:] + face[:1]):
            edges[tuple(sorted((a, b)))] += 1
    verify(abs(area - 0.25) < 1e-12, "UV mesh area changed")
    verify(all(1 <= incidence <= 2 for incidence in edges.values()),
           "Nonmanifold real-tree QUAD edges")
    verify(len(vertices) + len(faces) == len(edges) + 1,
           "Source-tree emitted graph is not one topological disk")
    return vertices, faces


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    path = parser.parse_args().directory
    meta = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    verify(meta["source"] == "real_APMesh_CXX_Quadtree_fixture" and
           meta["status"] == "UV_research_not_physical_hybrid" and
           meta["source_leaves"] == 19 and
           meta["included_quad_leaves"] == 7 and
           meta["excluded_boundary_unmeshed_leaves"] == 12 and
           meta["triangles_emitted"] == 0 and
           meta["mean_quads"] == meta["centroid_quads"] == 42 and
           meta["historical_centroid_approved"] is False,
           "Incorrect generated mesh provenance or status")
    with (path / "tree_regions.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    verify(len(rows) == 19 and
           [int(row["ordinal"]) for row in rows] == list(range(19)),
           "Actual source leaf CSV incomplete")
    kind = Counter(row["region"] for row in rows)
    verify(kind == {"quad_candidate": 7, "excluded_boundary_unmeshed": 12},
           "Boundary is falsely labeled as already triangulated")
    area, total = 0.0, 0
    for row in rows:
        a, b, c, d = (float(row[key]) for key in
                      ("min_u", "min_v", "max_u", "max_v"))
        verify(0 <= a < c <= 1 and 0 <= b < d <= 1,
               "Actual source-tree bounds invalid")
        if row["region"] == "quad_candidate":
            verify(row["pattern"] in {"T1", "T2", "T3", "T4", "T5", "T6"},
                   "Missing actual source classifier pattern")
            area += (c - a) * (d - b)
            total += int(row["quads"])
        else:
            verify(not row["pattern"] and int(row["quads"]) == 0,
                   "Unmeshed boundary was allocated elements")
    verify(abs(area - 0.25) < 1e-12 and total == 42,
           "Classified interior source tree geometry changed")
    vertices_a, faces_a = parse_obj(path / "quads_vertex_mean.obj")
    vertices_b, faces_b = parse_obj(path / "quads_area_centroid.obj")
    verify(faces_a == faces_b, "Center rule modified mesh connectivity")
    verify(any(a != b for a, b in zip(vertices_a, vertices_b)),
           "Competing candidate formulas did not affect any vertices")
    svg = ET.parse(path / "tree_visual.svg").getroot()
    ns = "{http://www.w3.org/2000/svg}"
    groups = {x.get("id"): x for x in svg.iter(ns + "g")}
    verify({"source-tree", "quad-vertex-mean", "quad-area-centroid"} <=
           groups.keys(), "SVG missing real Quadtree comparison")
    for label in ("quad-vertex-mean", "quad-area-centroid"):
        verify(len(list(groups[label].iter(ns + "polygon"))) == 42,
               "SVG polygons differ from actual native OBJ output")
    verify(svg.get("data-source") == "real-apmesh-cpp-quadtree-fixture",
           "SVG has lost real runtime source provenance")
    print("real_tree_visual_verified=1 leaves=19 included=7 "
          "boundary_not_meshed=12 quads=42 triangles_emitted=0 area=0.25")


if __name__ == "__main__":
    main()
