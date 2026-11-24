#!/usr/bin/env python3
"""Conservative STEP explicit face/edge reference screen for research triage.

This is not a CAD-kernel validation, a collision detector or a model-admission gate.
It does not infer geometric coincidence between different EDGE_CURVE identities.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

ENTITY = re.compile(r"#(\d+)\s*=\s*([A-Z0-9_]+)\s*\(([\s\S]*?)\)\s*;")
REF = re.compile(r"#(\d+)")
COMMENT = re.compile(r"/\*[\s\S]*?\*/")
FACE_BOUND_TYPES = {"FACE_BOUND", "FACE_OUTER_BOUND"}
INTERESTING_SURFACES = {
    "PLANE", "CYLINDRICAL_SURFACE", "CONICAL_SURFACE", "TOROIDAL_SURFACE",
    "SPHERICAL_SURFACE", "SURFACE_OF_REVOLUTION", "B_SPLINE_SURFACE_WITH_KNOTS",
    "B_SPLINE_SURFACE", "BEZIER_SURFACE", "RECTANGULAR_TRIMMED_SURFACE",
    "OFFSET_SURFACE", "SURFACE_OF_LINEAR_EXTRUSION",
}


def references(value: str) -> list[int]:
    """Extract entity references from a restricted STEP argument expression."""
    return [int(x) for x in REF.findall(value)]


def screen(content: str) -> dict:
    """Count distinct ADVANCED_FACE identities using each explicit EDGE_CURVE."""
    if "ISO-10303-21" not in content or "DATA;" not in content:
        raise ValueError("Invalid STEP Part 21 header or DATA section")
    entities: dict[int, tuple[str, str]] = {}
    kinds = Counter()
    for match in ENTITY.finditer(COMMENT.sub(" ", content)):
        identifier, name, arguments = int(match[1]), match[2], match[3]
        if identifier in entities:
            raise ValueError("Duplicate STEP entity identifier")
        entities[identifier] = (name, arguments)
        kinds[name] += 1
    oriented = {
        i: references(a)[-1] for i, (name, a) in entities.items()
        if name == "ORIENTED_EDGE" and references(a)
    }
    loops = {
        i: references(a) for i, (name, a) in entities.items()
        if name == "EDGE_LOOP"
    }
    bounds = {
        i: references(a)[0] for i, (name, a) in entities.items()
        if name in FACE_BOUND_TYPES and references(a)
    }
    incidence = defaultdict(set)
    unresolved = repeated_within_face = 0
    for face_id, (name, argument) in entities.items():
        if name != "ADVANCED_FACE":
            continue
        face_uses = []
        # The final referenced ADVANCED_FACE argument is its support surface.
        for b in references(argument)[:-1]:
            edge_loop = loops.get(bounds.get(b))
            if edge_loop is None:
                unresolved += 1
                continue
            for oriented_edge in edge_loop:
                edge_id = oriented.get(oriented_edge)
                if edge_id is None or entities.get(edge_id, (None,))[0] != "EDGE_CURVE":
                    unresolved += 1
                    continue
                face_uses.append(edge_id)
        unique = set(face_uses)
        repeated_within_face += len(face_uses) - len(unique)
        for edge_id in unique:
            incidence[edge_id].add(face_id)
    hist = Counter(len(users) for users in incidence.values())
    unreferenced = kinds["EDGE_CURVE"] - len(incidence)
    return {
        "schema": "apmesh-complex-step-explicit-reference-screen-v1",
        "scope": "SOURCE_STEP_ENTITY_REFERENCES_ONLY_NOT_CAD_KERNEL",
        "entity_count": len(entities),
        "advanced_face_count": kinds["ADVANCED_FACE"],
        "edge_curve_count": kinds["EDGE_CURVE"],
        "manifold_solid_brep_entities": kinds["MANIFOLD_SOLID_BREP"],
        "closed_shell_entities": kinds["CLOSED_SHELL"],
        "open_shell_entities": kinds["OPEN_SHELL"],
        "shell_based_surface_model_entities": kinds["SHELL_BASED_SURFACE_MODEL"],
        "source_surface_entities": dict(sorted((k, kinds[k]) for k in INTERESTING_SURFACES if kinds[k])),
        "face_incidence_per_explicit_edge_histogram": dict(sorted(hist.items())),
        "explicit_three_plus_face_edges": sum(v for i, v in hist.items() if i >= 3),
        "within_face_repeated_edge_uses": repeated_within_face,
        "unreferenced_edge_curves": unreferenced,
        "unresolved_face_edge_references": unresolved,
        "complete_explicit_edge_graph": unresolved == 0 and unreferenced == 0,
        "geometrically_coincident_distinct_edges": "NOT_ASSESSED",
        "nonmanifold_admission": "NOT_DETERMINED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    import hashlib
    result = {}
    for path in args.files:
        data = path.read_bytes()
        report = screen(data.decode("utf-8"))
        report.update({"source_bytes": len(data), "raw_sha256": hashlib.sha256(data).hexdigest()})
        result[path.name] = report
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
