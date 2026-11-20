"""Conservative STEP face-to-edge reference screen, not a CAD-kernel validator."""

from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

_ENTITY = re.compile(r"#(\d+)\s*=\s*([A-Z0-9_]+)\s*\(([\s\S]*?)\)\s*;")
_REF = re.compile(r"#(\d+)")
_BLOCK_COMMENT = re.compile(r"/\*[\s\S]*?\*/")


def refs(value: str) -> list[int]:
    """Extract STEP entity identifiers."""
    return [int(item) for item in _REF.findall(value)]


def screen(text: str) -> dict:
    """Count distinct ADVANCED_FACE users per explicit EDGE_CURVE identity."""
    if "ISO-10303-21" not in text or "DATA;" not in text:
        raise ValueError("Not an ISO 10303-21 DATA section")
    entities = {}
    types = Counter()
    for match in _ENTITY.finditer(_BLOCK_COMMENT.sub(" ", text)):
        identifier = int(match.group(1))
        if identifier in entities:
            raise ValueError(f"Duplicate STEP entity identifier {identifier}")
        kind, args = match.group(2), match.group(3)
        entities[identifier] = (kind, args)
        types[kind] += 1
    oriented = {
        index: refs(args)[-1]
        for index, (kind, args) in entities.items()
        if kind == "ORIENTED_EDGE" and refs(args)
    }
    loops = {
        index: refs(args)
        for index, (kind, args) in entities.items()
        if kind == "EDGE_LOOP"
    }
    bounds = {
        index: refs(args)[0]
        for index, (kind, args) in entities.items()
        if kind in ("FACE_BOUND", "FACE_OUTER_BOUND") and refs(args)
    }
    incidence = defaultdict(set)
    unresolved_bounds = 0
    unresolved_edges = 0
    for face_id, (kind, args) in entities.items():
        if kind != "ADVANCED_FACE":
            continue
        # The final referenced entity is the support surface.
        for bound_id in refs(args)[:-1]:
            loop = loops.get(bounds.get(bound_id))
            if loop is None:
                unresolved_bounds += 1
                continue
            for oriented_id in loop:
                edge_id = oriented.get(oriented_id)
                if edge_id is None or entities.get(edge_id, (None,))[0] != "EDGE_CURVE":
                    unresolved_edges += 1
                    continue
                incidence[edge_id].add(face_id)
    histogram = dict(sorted(Counter(len(faces) for faces in incidence.values()).items()))
    complete = (
        unresolved_bounds == 0
        and unresolved_edges == 0
        and len(incidence) == types["EDGE_CURVE"]
    )
    return {
        "schema": "apmesh-step-structural-screen-v1",
        "qualifier": "REFERENCE_INCIDENCE_ONLY_NOT_KERNEL_VALIDATED",
        "entity_count": len(entities),
        "advanced_face_count": types["ADVANCED_FACE"],
        "edge_curve_count": types["EDGE_CURVE"],
        "closed_shell_count": types["CLOSED_SHELL"],
        "open_shell_count": types["OPEN_SHELL"],
        "manifold_solid_brep_count": types["MANIFOLD_SOLID_BREP"],
        "vertex_loop_count": types["VERTEX_LOOP"],
        "edge_to_distinct_face_incidence_histogram": histogram,
        "unreferenced_edge_curve_count": types["EDGE_CURVE"] - len(incidence),
        "unresolved_face_bound_count": unresolved_bounds,
        "unresolved_oriented_edge_count": unresolved_edges,
        "has_explicit_three_plus_face_edge": any(n >= 3 for n in histogram),
        "complete_screen": complete,
        "admission_decision": "NOT_DETERMINED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step_file", type=Path)
    args = parser.parse_args()
    report = screen(args.step_file.read_text(encoding="utf-8"))
    report["source_path"] = str(args.step_file)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
