#!/usr/bin/env python3
"""Audit detached QUAD/AFT source patch indexed edges, without cross-patch welding.

OBJ exposes XYZ and ordered face node indices, not source UV or differential
normals. No global non-manifold sheet decision is inferred from this check.
"""

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

from verify_r2c10_mesh_export import EXPECTED, verify


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def parse_obj(lines, patch_count):
    vertices, patches, groups = {}, defaultdict(list), []
    group = None
    for line_no, raw in enumerate(lines, 1):
        fields = raw.split()
        if not fields or fields[0] in ("#", "o"):
            continue
        if fields[0] == "g":
            require(len(fields) == 2 and fields[1].startswith("patch_") and
                    fields[1][6:].isdecimal(), "Invalid original patch group")
            group = int(fields[1][6:])
            require(group == len(groups) and group < patch_count,
                    "Original patch grouping order changed")
            groups.append(group)
        elif fields[0] == "v":
            require(group is not None and len(fields) == 4,
                    "Unowned original physical vertex")
            xyz = tuple(float(x) for x in fields[1:])
            require(all(math.isfinite(x) for x in xyz),
                    "Nonfinite physical XYZ vertex")
            vertices[len(vertices) + 1] = (group, xyz)
        elif fields[0] == "f":
            require(group is not None and len(fields) in (4, 5) and
                    all(x.isdecimal() for x in fields[1:]),
                    "Unexpected original TRI/QUAD face")
            face = tuple(map(int, fields[1:]))
            require(len(set(face)) == len(face) and
                    all(v in vertices and vertices[v][0] == group for v in face),
                    f"Physical face has foreign/repeated node at line {line_no}")
            patches[group].append(face)
        else:
            raise ValueError(f"Unexpected source OBJ record at line {line_no}")
    require(groups == list(range(patch_count)),
            "Original source OBJ patch groups incomplete")
    return vertices, patches


def inspect_patch(xyz, faces):
    require(faces, "An original physical source chart has no faces")
    uses, identities, referenced, normals = defaultdict(list), set(), set(), []
    for face_id, face in enumerate(faces):
        require(len(face) in (3, 4) and len(set(face)) == len(face) and
                all(v in xyz for v in face), "Bad original patch face")
        identity = tuple(sorted(face))
        require(identity not in identities, "Duplicated physical face")
        identities.add(identity)
        referenced.update(face)
        for a, b in zip(face, face[1:] + face[:1]):
            uses[tuple(sorted((a, b)))].append((face_id, a, b))
        points = [xyz[v] for v in face]
        nx = ny = nz = 0.0
        for a, b in zip(points, points[1:] + points[:1]):
            nx += (a[1] - b[1]) * (a[2] + b[2])
            ny += (a[2] - b[2]) * (a[0] + b[0])
            nz += (a[0] - b[0]) * (a[1] + b[1])
        length = math.hypot(nx, ny, nz)
        require(math.isfinite(length) and length > 0.0,
                "Zero or nonfinite physical Newell normal")
        normals.append((nx/length, ny/length, nz/length))
    parent = list(range(len(faces)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def unite(i, j):
        parent[root(i)] = root(j)

    degree = defaultdict(int)
    boundary = pairs = wrong = nonmanifold = 0
    minimum_normal_dot = 1.0
    for (a, b), edge_faces in uses.items():
        if len(edge_faces) == 1:
            boundary += 1
            degree[a] += 1
            degree[b] += 1
        elif len(edge_faces) == 2:
            (i, ai, bi), (j, aj, bj) = edge_faces
            require(i != j, "A physical face repeats one indexed edge")
            unite(i, j)
            if ai == bj and bi == aj:
                pairs += 1
            else:
                wrong += 1
            dot = sum(x*y for x, y in zip(normals[i], normals[j]))
            minimum_normal_dot = min(minimum_normal_dot,
                                     max(-1.0, min(1.0, dot)))
        else:
            nonmanifold += 1
            for item in edge_faces[1:]:
                unite(edge_faces[0][0], item[0])
    components = len({root(i) for i in range(len(faces))})
    bad_degree = sum(x != 2 for x in degree.values())
    accepted = (wrong == 0 and nonmanifold == 0 and components == 1
                and bad_degree == 0 and boundary > 0)
    return {
        "TRI_faces": sum(len(f) == 3 for f in faces),
        "QUAD_faces": sum(len(f) == 4 for f in faces),
        "referenced_vertices": len(referenced),
        "indexed_edges": len(uses),
        "boundary_edges": boundary,
        "oppositely_oriented_shared_edges": pairs,
        "same_direction_shared_edges": wrong,
        "overfull_edges": nonmanifold,
        "face_edge_components": components,
        "boundary_vertices_with_degree_not_two": bad_degree,
        "min_adjacent_unit_Newell_normal_dot":
            minimum_normal_dot if pairs + wrong else None,
        "indexed_patch_topology_gate": accepted,
        "source_UV_and_differential_normal_qualified": False,
        "cross_patch_welding_approved": False,
        "global_nonmanifold_sheet_qualified": False,
    }


def negative_controls():
    plane = {1:(0.,0.,0.), 2:(1.,0.,0.), 3:(0.,1.,0.),
             4:(1.,1.,0.), 5:(0.5,-1.,0.)}
    require(inspect_patch(plane, [(1,2,3), (2,4,3)])
            ["indexed_patch_topology_gate"], "Positive patch fixture rejected")
    for faces in (
        [(1,2,3), (2,3,4)],
        [(1,2,3), (2,1,4), (1,2,5)],
        [(1,2,3), (4,5,2)],
    ):
        try:
            outcome = inspect_patch(plane, faces)
        except ValueError:
            continue
        require(not outcome["indexed_patch_topology_gate"],
                "Corrupt indexed topology passed")
    for faces in ([(1,2,3), (3,2,1)], [(1,2,99)]):
        try:
            inspect_patch(plane, faces)
        except ValueError:
            continue
        raise ValueError("Invalid original source physical face passed")
    for lines, count in (
        (["g patch_0","v 0 0 0","v 1 0 0","v 0 1 0",
          "g patch_1","v 1 1 0","v 2 1 0","f 2 4 5"], 2),
        (["g patch_0","v nan 0 0","f 1 1 1"], 1),
    ):
        try:
            parse_obj(lines, count)
        except ValueError:
            continue
        raise ValueError("Corrupt original detached OBJ passed")
    return 7


def run(directory, output):
    controls = negative_controls()
    report = {
        "schema": "apmesh.quad.r2c21.original_detached_indexed_patch_topology.v1",
        "original_TRI_source_changed": False,
        "original_UV_or_patch_differential_normals_exported": False,
        "cross_patch_node_welding_performed": False,
        "global_nonmanifold_mesh_scientifically_approved": False,
        "negative_controls_passed": controls,
        "models": {},
    }
    for model, spec in EXPECTED.items():
        receipt = verify(directory, model, spec)
        obj = directory / f"{model}_all_sides_detached_quad_aft.obj"
        vertices, groups = parse_obj(
            obj.read_text(encoding="utf-8").splitlines(), spec["patches"])
        patches = {}
        for patch, faces in sorted(groups.items()):
            local = {i: p for i, (owner, p) in vertices.items() if owner == patch}
            patches[str(patch)] = inspect_patch(local, faces)
        require(len(patches) == spec["patches"], "Original patch scope changed")
        failed = [p for p, data in patches.items()
                  if not data["indexed_patch_topology_gate"]]
        report["models"][model] = {
            "source_model_sha256": spec["source_sha256"],
            "OBJ_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
            "r2c10_verified_original_receipt": receipt,
            "patches": patches,
            "failed_patch_ids": failed,
        }
    output.mkdir(parents=True, exist_ok=True)
    file = output / "r2c21_original_detached_indexed_patch_topology.json"
    file.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n",
                    encoding="utf-8")
    print("R2C21_ORIGINAL_PATCH_LOCAL_INDEXED_TOPOLOGY",
          json.dumps({k: {"patches": len(v["patches"]),
                          "failed_patch_ids": v["failed_patch_ids"]}
                      for k, v in report["models"].items()}, sort_keys=True),
          "negative_controls=7", "scientific_global_mesh_approved=0")
    require(all(not v["failed_patch_ids"] for v in report["models"].values()),
            "Original detached QUAD/AFT chart has invalid indexed topology")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.directory.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
