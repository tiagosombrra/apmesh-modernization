"""Audit the native mixed feedback graph on a retained physical OBJ."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests/quad"))
from independent_common_grid import load_physical_obj
from test_real_boundary_application import audit


def original_intervals(path, uv):
    indices = {location: node for node, location in enumerate(uv)}
    contour = []
    for line in path.read_text(encoding="ascii").splitlines():
        fields = line.split()
        if fields[:2] == ["#", "source_site"]:
            contour.append(indices[tuple(map(float, fields[4:6]))])
    return list(zip(contour, contour[1:] + contour[:1]))


def fixture_input(nodes, faces, intervals):
    rows = [[nodes, len(faces), len(intervals)]]
    rows.extend([len(face), *face] for face in faces)
    rows.extend(intervals)
    return "\n".join(" ".join(map(str, row)) for row in rows) + "\n"


def audit_graph(path, probe):
    source = audit(path)
    xyz, uv, faces = load_physical_obj(path)
    intervals = original_intervals(path, uv)
    run = subprocess.run([str(probe.resolve())],
                         input=fixture_input(len(xyz), faces, intervals),
                         capture_output=True, text=True, timeout=30, check=True)
    owners, *neighbors = [list(map(int, line.split())) for line in run.stdout.splitlines()]
    expected = [set() for _ in range(len(faces) + len(intervals))]
    incident = {}
    for i, faces_vertices in enumerate(faces):
        for a, b in zip(faces_vertices, faces_vertices[1:] + faces_vertices[:1]):
            if (b, a) in incident:
                other = incident[b, a]
                expected[i].add(other)
                expected[other].add(i)
            incident[a, b] = i

    if len(owners) != len(intervals):
        raise ValueError("Unexpected source interval owner count")
    for i, (edge, owner) in enumerate(zip(intervals, owners)):
        if incident[edge] != owner or edge[::-1] in incident:
            raise ValueError("C++ owner does not match the original contour")
        slot = len(faces) + i
        expected[owner].add(slot)
        expected[slot].update((owner,
                               len(faces) + (i - 1) % len(intervals),
                               len(faces) + (i + 1) % len(intervals)))
    if neighbors != [sorted(links) for links in expected]:
        raise ValueError("C++ graph differs from independent directional edge inventory")
    if len(intervals) != source["boundary"]:
        raise ValueError("Missing sampled curve interval")

    variants = {
        "omitted_interval": (faces, intervals[:-1]),
        "reversed_contour": (faces, [e[::-1] for e in reversed(intervals)]),
        "duplicate_interval": (faces, [*intervals, intervals[0]]),
        "duplicated_face": ([*faces, faces[0]], intervals),
    }
    for name, (bad_faces, bad_intervals) in variants.items():
        result = subprocess.run([str(probe.resolve())],
                                input=fixture_input(len(xyz), bad_faces, bad_intervals),
                                capture_output=True, text=True, timeout=30)
        if result.returncode != 1 or result.stdout or not result.stderr:
            raise ValueError(f"Malformed feedback topology was not rejected: {name}")

    return {
        "mesh": path.name,
        "mesh_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "source_tri_accepted": source["reference_tri_accepted"],
        "faces": len(faces),
        "source_intervals": len(intervals),
        "graph_edges": sum(map(len, neighbors)) // 2,
        "interval_face_links": len(owners),
        "negative_controls": list(variants),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("physical_mesh", nargs="+", type=Path)
    args = parser.parse_args()
    print(json.dumps([audit_graph(p, args.probe) for p in args.physical_mesh], indent=2))


if __name__ == "__main__":
    main()
