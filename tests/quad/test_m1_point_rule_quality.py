#!/usr/bin/env python3
"""Exact-coordinate research comparison of two unapproved polygon point witnesses.

Uses the proposed normalized Figure 7 transcription; does NOT prove what the
authors implemented in 1993 or rank physical curved-mesh element quality.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import json
import math
from pathlib import Path


GOLDEN = {
    "T1": (4, 1.0, 1.0, 1.0, 1.0),
    "T2": (11, 0.6, 0.7654863137380862, 0.6, 0.753073347423271),
    "T4": (12, 0.7071067811865475, 0.8671779907288211,
           0.7071067811865475, 0.855799438273574),
    "T3": (8, 1.0, 1.0, 1.0, 1.0),
    "T5": (11, 0.6, 0.8379346824314564, 0.6, 0.831728199274049),
    "T6": (16, 1.0, 1.0, 1.0, 1.0),
}
EXPECTED_ORDER = ("T1", "T2", "T4", "T3", "T5", "T6")


def minus(b, a):
    return b[0] - a[0], b[1] - a[1]


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def transform(point, reflection, rotation):
    x, y = point
    if reflection:
        x = 1 - x
    for _ in range(rotation):
        x, y = 1 - y, x
    return x, y


def selected_point(vertices, rule):
    if rule == "vertex_mean":
        return tuple(sum(v[dim] for v in vertices) / len(vertices)
                     for dim in (0, 1))
    twice_area = sum(cross(vertices[i], vertices[(i + 1) % len(vertices)])
                     for i in range(len(vertices)))
    if twice_area <= 0:
        raise ValueError("Area centroid requires a CCW source polygon")
    return tuple(
        sum((vertices[i][dim] + vertices[(i + 1) % len(vertices)][dim])
            * cross(vertices[i], vertices[(i + 1) % len(vertices)])
            for i in range(len(vertices))) / (3 * twice_area)
        for dim in (0, 1)
    )


def corner_sine(quad, index):
    origin = quad[index]
    forward = minus(quad[(index + 1) % 4], origin)
    backward = minus(quad[(index - 1) % 4], origin)
    numerator = float(cross(forward, backward))
    length = math.hypot(float(forward[0]), float(forward[1])) * math.hypot(
        float(backward[0]), float(backward[1]))
    if length <= 0 or numerator <= 0:
        raise ValueError("Degenerate or inverted research quadrilateral")
    return numerator / length


def measured_quality(polygons, coordinates, rule, reflection=False, rotation=0):
    scores = []
    for labels in polygons:
        points = [transform(coordinates[label], reflection, rotation)
                  for label in labels]
        if reflection:
            points.reverse()
        center = selected_point(points, rule)
        for i, vertex in enumerate(points):
            previous = points[(i - 1) % len(points)]
            following = points[(i + 1) % len(points)]
            edge_midpoint = ((vertex[0] + following[0]) / 2,
                             (vertex[1] + following[1]) / 2)
            previous_midpoint = ((vertex[0] + previous[0]) / 2,
                                 (vertex[1] + previous[1]) / 2)
            quad = (vertex, edge_midpoint, center, previous_midpoint)
            scores.append(min(corner_sine(quad, j) for j in range(4)))
    if not scores:
        raise ValueError("No measurable research QUAD witnesses")
    return (len(scores), min(scores), sum(scores) / len(scores))


def run(fixture):
    doc = json.loads(fixture.read_text(encoding="utf-8"))
    patterns = doc["patterns"]
    if tuple(row["class"] for row in patterns) != EXPECTED_ORDER:
        raise ValueError("Figure 7 mapping changed")
    if doc["status"] != "primary_source_transcription_for_review_not_executable_scientific_oracle":
        raise ValueError("Scientific status was silently modified")
    vertices = {name: tuple(Q(str(value)) for value in pair)
                for name, pair in doc["vertices"].items()}
    result = {}
    samples = 0
    for row in patterns:
        expected = GOLDEN[row["class"]]
        cases = {}
        for index, rule in enumerate(("vertex_mean", "area_centroid")):
            base = measured_quality(row["polygons"], vertices, rule)
            reference_min = expected[1 if index == 0 else 3]
            reference_mean = expected[2 if index == 0 else 4]
            if (base[0] != expected[0] or
                    abs(base[1] - reference_min) > 1.0e-12 or
                    abs(base[2] - reference_mean) > 1.0e-12):
                raise ValueError("Independent numerical golden mismatch: "
                                 + row["class"] + " " + rule)
            for reflection in (False, True):
                for rotation in range(4):
                    measured = measured_quality(row["polygons"], vertices, rule,
                                                reflection, rotation)
                    if (measured[0] != base[0] or
                            abs(measured[1] - base[1]) > 1.0e-12 or
                            abs(measured[2] - base[2]) > 1.0e-12):
                        raise ValueError("D4 corner-angle metric mismatch")
                    samples += 1
            cases[rule] = {
                "worst_corner_sine": round(base[1], 12),
                "mean_of_element_worst_corner_sine": round(base[2], 12),
            }
        result[row["class"]] = {
            "quad_count": expected[0],
            **cases,
        }
        if abs(cases["vertex_mean"]["worst_corner_sine"] -
               cases["area_centroid"]["worst_corner_sine"]) > 1.0e-12:
            raise ValueError("Documented 6-template worst-case parity changed")
    if samples != 96:
        raise ValueError("Missing D4/rule sample")
    return {
        "proposed_template_count": 6,
        "d4_rule_comparisons": samples,
        "metric": "minimum signed normalized corner Jacobian = sine of interior angle",
        "summary": result,
        "historical_point_policy_approved": False,
        "physical_quad_emitted": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True, type=Path)
    args = parser.parse_args()
    print("m1_point_rule_quality=" + json.dumps(run(args.fixture), sort_keys=True))


if __name__ == "__main__":
    main()
