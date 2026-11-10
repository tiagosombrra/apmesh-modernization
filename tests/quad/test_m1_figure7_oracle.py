#!/usr/bin/env python3
"""Independent exact-rational topology audit of the proposed 1993 Figure 7 transcription.

This checks a schematic interpretation, NOT the scan's byte identity, an approved
numerical centroid, or production QUAD. No third-party Python dependencies.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path


Q = Fraction
GOLDEN = (
    ("T1", (), ("ABCD",), 4, 4),
    ("T2", ("W",), ("ABOW", "BCO", "WOCD"), 11, 5),
    ("T4", ("N", "W"), ("ABOW", "WOND", "OBCN"), 12, 6),
    ("T3", ("E", "W"), ("ABEW", "WECD"), 8, 6),
    ("T5", ("S", "N", "W"), ("ASW", "WSND", "SBCN"), 11, 7),
    ("T6", ("S", "E", "N", "W"), ("ASOW", "SBEO", "OECN", "WOND"), 16, 8),
)
MIDPOINTS = {"S": (Q(1, 2), Q(0)), "E": (Q(1), Q(1, 2)),
             "N": (Q(1, 2), Q(1)), "W": (Q(0), Q(1, 2))}
EXPECTED_ORBITS = {"T1": 1, "T2": 4, "T4": 4, "T3": 2, "T5": 4, "T6": 1}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def area(vertices, cycle):
    return sum((vertices[cycle[i]][0] * vertices[cycle[(i + 1) % len(cycle)]][1] -
                vertices[cycle[(i + 1) % len(cycle)]][0] * vertices[cycle[i]][1]
                for i in range(len(cycle))), Q(0)) / 2


def interior(vertices, cycle, point):
    return all(cross(vertices[cycle[i]], vertices[cycle[(i + 1) % len(cycle)]], point) > 0
               for i in range(len(cycle)))


def check_disk(vertices, polygons, expected_area=Q(1)):
    """Independently check exact orientation, incidences, Euler and geometric validity."""
    require(bool(vertices) and bool(polygons), "Missing graph data")
    require(len(set(vertices.values())) == len(vertices), "Coincident vertex coordinates")
    incidences = defaultdict(list)
    adjacency = defaultdict(set)
    used = set()
    total = Q(0)
    for face in polygons:
        require(len(face) >= 3 and len(set(face)) == len(face), "Repeated or short face")
        require(all(vertex in vertices for vertex in face), "Unknown face vertex")
        used.update(face)
        for i, start in enumerate(face):
            end = face[(i + 1) % len(face)]
            for other in face:
                if other != start and other != end:
                    require(cross(vertices[start], vertices[end], vertices[other]) > 0,
                            "Inverted, collinear, or nonconvex face")
            edge = tuple(sorted((start, end)))
            incidences[edge].append((start, end))
            adjacency[start].add(end)
            adjacency[end].add(start)
        total += area(vertices, face)
    require(used == set(vertices), "Orphan vertex")
    require(total == expected_area, "Domain area not conserved")
    boundary = Counter()
    for edge, directions in incidences.items():
        require(len(directions) <= 2, "Nonmanifold edge incidence")
        if len(directions) == 2:
            require(directions[0] == directions[1][::-1], "Inconsistent shared winding")
        else:
            boundary.update(edge)
        a, b = (vertices[name] for name in edge)
        for name, p in vertices.items():
            if name in edge:
                continue
            if cross(a, b, p) == 0:
                dot = ((p[0] - a[0]) * (p[0] - b[0]) +
                       (p[1] - a[1]) * (p[1] - b[1]))
                require(dot >= 0, "Hanging vertex on unsplit edge")
    require(all(degree == 2 for degree in boundary.values()), "Nonmanifold boundary")
    require(len(vertices) + len(polygons) == len(incidences) + 1,
            "Not a single topological disk (Euler)")
    visited = set()
    pending = [next(iter(vertices))]
    while pending:
        item = pending.pop()
        if item in visited:
            continue
        visited.add(item)
        pending.extend(adjacency[item] - visited)
    require(visited == set(vertices), "Disconnected graph")
    edges = list(incidences)
    for i, (a, b) in enumerate(edges):
        for c, d in edges[i + 1:]:
            if len({a, b, c, d}) != 4:
                continue
            abc, abd = cross(vertices[a], vertices[b], vertices[c]), cross(vertices[a], vertices[b], vertices[d])
            cda, cdb = cross(vertices[c], vertices[d], vertices[a]), cross(vertices[c], vertices[d], vertices[b])
            require(not ((abc > 0 > abd or abd > 0 > abc) and
                         (cda > 0 > cdb or cdb > 0 > cda)), "Crossing edges")
    return {"vertices": len(vertices), "faces": len(polygons),
            "edges": len(incidences), "boundary": sum(boundary.values()) // 2,
            "interior": sum(len(x) == 2 for x in incidences.values())}


def vertex_mean(vertices, cycle):
    return tuple(sum((vertices[name][axis] for name in cycle), Q(0)) / len(cycle)
                 for axis in (0, 1))


def area_centroid(vertices, cycle):
    """Exact area centroid; a competing candidate, not an approved historical rule."""
    twice_area = 2 * area(vertices, cycle)
    require(twice_area > 0, "Centroid requires positive area")
    result = []
    for axis in (0, 1):
        moment = Q(0)
        for i, name in enumerate(cycle):
            nxt = cycle[(i + 1) % len(cycle)]
            a, b = vertices[name], vertices[nxt]
            moment += (a[axis] + b[axis]) * (a[0] * b[1] - b[0] * a[1])
        result.append(moment / (3 * twice_area))
    return tuple(result)


def subdivide(vertices, polygons, rule):
    """Build independent exact-rational QUAD graph; use a test-only interior witness."""
    points = dict(vertices)
    output = []
    midpoints = {}
    for index, face in enumerate(polygons):
        point = rule(vertices, face)
        require(interior(vertices, face, point), "Witness is not strictly interior")
        center = f"c{index}"
        require(center not in points, "Duplicate center identity")
        points[center] = point
        sides = []
        for i, start in enumerate(face):
            end = face[(i + 1) % len(face)]
            edge = tuple(sorted((start, end)))
            if edge not in midpoints:
                mid = f"m{len(midpoints)}"
                midpoints[edge] = mid
                a, b = vertices[start], vertices[end]
                points[mid] = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            sides.append(midpoints[edge])
        for i, name in enumerate(face):
            output.append((name, sides[i], center, sides[i - 1]))
    return points, output


def transform(point, reflection, turns):
    x, y = point
    if reflection:
        x = 1 - x
    for _ in range(turns):
        x, y = 1 - y, x
    return x, y


def signature(vertices):
    return sum(1 << side for side, (_, point) in
               enumerate(("S", MIDPOINTS["S"]), ("E", MIDPOINTS["E"]),
                         ("N", MIDPOINTS["N"]), ("W", MIDPOINTS["W"]))
               if point in vertices.values())


def rejects(operation, reason):
    try:
        operation()
    except ValueError:
        return
    raise ValueError(f"Mutation was not rejected: {reason}")


def audit(document):
    require(document["status"] == "primary_source_transcription_for_review_not_executable_scientific_oracle",
            "Documentary status changed without scientific approval")
    require(document["paper"]["sha256"] ==
            "49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5",
            "Original scan provenance metadata changed")
    require(len(document["patterns"]) == 6, "Unexpected Figure 7 column count")
    vertices = {name: tuple(Q(str(x)) for x in coord)
                for name, coord in document["vertices"].items()}
    require(vertices == {"A": (Q(0), Q(0)), "B": (Q(1), Q(0)),
                          "C": (Q(1), Q(1)), "D": (Q(0), Q(1)),
                          "S": MIDPOINTS["S"], "E": MIDPOINTS["E"],
                          "N": MIDPOINTS["N"], "W": MIDPOINTS["W"],
                          "O": (Q(1, 2), Q(1, 2))},
            "Proposed normalized embedding changed")
    require("Centroid" not in document.get("status", ""), "Scientific policy incorrectly adopted")

    orbits = defaultdict(set)
    observations = 0
    quad_cases = 0
    disagreements = 0
    for row, (label, sides, cycles, expected_quads, expected_boundary) in zip(
            document["patterns"], GOLDEN):
        require(row["class"] == label and tuple(row["split_sides"]) == sides and
                tuple("".join(face) for face in row["polygons"]) == cycles and
                row["expected_quads_after_subdivision"] == expected_quads,
                f"Figure 7 cycle/class/golden mismatch in {label}")
        source_cycles = [tuple(cycle) for cycle in cycles]
        base = {name: vertices[name] for name in set("".join(cycles))}
        for reflection in (False, True):
            for turns in range(4):
                points = {name: transform(p, reflection, turns) for name, p in base.items()}
                faces = [tuple(reversed(face)) if reflection else face
                         for face in source_cycles]
                original = check_disk(points, faces)
                require(original["boundary"] == expected_boundary,
                        "Figure 7 source boundary incidence differs")
                orbits[label].add(signature(points))
                for rule in (vertex_mean, area_centroid):
                    emitted_points, quads = subdivide(points, faces, rule)
                    output = check_disk(emitted_points, quads)
                    require(len(quads) == expected_quads and
                            output["boundary"] == 2 * expected_boundary and
                            output["vertices"] == original["vertices"] + original["edges"] + len(faces),
                            f"Incorrect QUAD subdivision inventory for {label}")
                    quad_cases += 1
                disagreements += sum(vertex_mean(points, face) != area_centroid(points, face)
                                     for face in faces)
                observations += 1

    require(observations == 48 and quad_cases == 96, "Missing D4 or point-rule cases")
    require({key: len(value) for key, value in orbits.items()} == EXPECTED_ORBITS,
            "Figure 7 D4 orbit size changed")
    require(len(set.union(*(set(v) for v in orbits.values()))) == 16 and
            sum(len(v) for v in orbits.values()) == 16,
            "16 side split signatures do not partition uniquely")
    require(disagreements >= 8, "Competing numerical center rules were conflated")
    abow = tuple("ABOW")
    wsnd = tuple("WSND")
    require(vertex_mean(vertices, abow) == (Q(3, 8), Q(1, 4)) and
            area_centroid(vertices, abow) == (Q(7, 18), Q(2, 9)) and
            vertex_mean(vertices, wsnd) == (Q(1, 4), Q(5, 8)) and
            area_centroid(vertices, wsnd) == (Q(5, 18), Q(11, 18)),
            "Competing center-point golden coordinates changed")

    original = [tuple(v) for v in GOLDEN[4][2]]
    t5 = {name: vertices[name] for name in set("".join(original))}
    rejects(lambda: check_disk(t5, original[:-1]), "missing polygon")
    rejects(lambda: check_disk(t5, [original[0][::-1]] + original[1:]), "reversed winding")
    rejects(lambda: check_disk(t5, original + [original[-1]]), "duplicate polygon")
    repeats = original.copy()
    repeats[0] = ("A", "S", "S")
    rejects(lambda: check_disk(t5, repeats), "repeated vertex")
    with_center = dict(t5, O=vertices["O"])
    insert = original.copy()
    insert[1] = tuple("WSOND")
    rejects(lambda: check_disk(with_center, insert), "invented collinear T5 junction")
    collapsed = dict(t5, B=t5["A"])
    rejects(lambda: check_disk(collapsed, original), "zero-area edge")
    outside = (Q(2), Q(2))
    rejects(lambda: subdivide(t5, original, lambda *_: outside), "outside witness")
    rejects(lambda: subdivide(t5, original, lambda v, cycle: v[cycle[0]]),
            "boundary witness")
    wrong_label = deepcopy(document)
    wrong_label["patterns"][2]["class"] = "T3"
    rejects(lambda: audit_golden_only(wrong_label), "swapped historical labels")

    return {"figure7_patterns": len(GOLDEN), "d4_observations": observations,
            "exact_quad_graphs": quad_cases, "distinct_split_signatures": 16,
            "negative_mutations": 9, "centroid_rule_disagreements": disagreements,
            "historical_centroid_approved": False, "physical_quad_emitted": False}


def audit_golden_only(document):
    for row, (label, sides, cycles, count, _) in zip(document["patterns"], GOLDEN):
        require((row["class"], tuple(row["split_sides"]),
                 tuple("".join(face) for face in row["polygons"]),
                 row["expected_quads_after_subdivision"]) ==
                (label, sides, cycles, count), "Historical source mapping changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    args = parser.parse_args()
    result = audit(json.loads(args.fixture.read_text(encoding="utf-8")))
    print("m1_figure7_oracle=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
