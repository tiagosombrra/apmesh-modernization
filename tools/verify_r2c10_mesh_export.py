#!/usr/bin/env python3
"""Independently audit detached original QUAD/AFT OBJ exports.

This is a research geometry consistency check, not an approval of shared-node
non-manifold topology or the original production generator's adaptive epoch.
"""

import argparse
import json
import math
from pathlib import Path


EXPECTED = {
    "eistute": {
        "patches": 4, "nodes": 220, "quads": 64, "tris": 184,
        "source_sha256": "fdce4714524b88f536ec9f8eddc467e54e638dc6e765784ab68edc9a366a0a3f",
    },
    "book": {
        "patches": 28, "nodes": 1524, "quads": 448, "tris": 1272,
        "source_sha256": "3c4255cbd2f46bd2dce5f0e86b8e7ee9ac0c58df949d4563dd821deedcd8412d",
    },
}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def triangle_cross_squared(a, b, c):
    ab = tuple(b[i] - a[i] for i in range(3))
    ac = tuple(c[i] - a[i] for i in range(3))
    xyz = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )
    return sum(value * value for value in xyz)


def verify(directory, model, expected):
    obj_path = directory / f"{model}_all_sides_detached_quad_aft.obj"
    manifest_path = directory / f"{model}_all_sides_detached_quad_aft.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    n = expected["patches"]
    check(manifest["model"] == model, "Wrong original model identity")
    check(manifest["original_patches"] == n, "Incorrect original patch count")
    check(manifest["expected_model_sha256_from_r2c6_evidence_not_recomputed"] ==
          expected["source_sha256"], "Changed documented source SHA-256")
    check(manifest["all_four_original_sides_adapted"] is True,
          "Four original adapted sides were not certified")
    check(manifest["disconnected_physical_chart_owners"] is True and
          manifest["cross_patch_welding"] is False and
          manifest["original_generator_adapt_domain_accepted"] is False and
          manifest["global_scientific_mesh_approved"] is False,
          "Unexpected physical model scientific approval/ownership claim")
    check(len(manifest["patches"]) == n, "Missing original patch in manifest")
    check((manifest["physical_nodes"], manifest["typed_QUAD"],
           manifest["typed_TRI"]) ==
          (expected["nodes"], expected["quads"], expected["tris"]),
          "Serialized global element totals differ from qualified R2c9")
    groups = {}
    index_range = {}
    first = 1
    for i, item in enumerate(manifest["patches"]):
        check(item["patch_id"] == i, "Patch manifest order or identity changed")
        check(item["vertices"] > 0 and item["quads"] > 0 and item["tris"] > 0,
              "Empty original patch physical group")
        groups[i] = {"vertices": 0, "quads": 0, "tris": 0}
        index_range[i] = (first, first + item["vertices"] - 1)
        first += item["vertices"]
    check(first - 1 == expected["nodes"], "Patch vertex ranges do not cover model")

    vertices = []
    current_patch = None
    observed_groups = []
    for line in obj_path.read_text(encoding="utf-8").splitlines():
        tokens = line.split()
        if not tokens or tokens[0] in {"#", "o"}:
            continue
        if tokens[0] == "g":
            check(len(tokens) == 2 and tokens[1].startswith("patch_"),
                  "Foreign OBJ patch group")
            current_patch = int(tokens[1][6:])
            check(current_patch in groups and current_patch not in observed_groups,
                  "Duplicate or foreign OBJ patch group")
            observed_groups.append(current_patch)
        elif tokens[0] == "v":
            check(current_patch is not None and len(tokens) == 4,
                  "OBJ physical vertex without original Patch group")
            xyz = tuple(map(float, tokens[1:]))
            check(all(math.isfinite(value) for value in xyz),
                  "Non-finite original physical vertex")
            vertices.append(xyz)
            groups[current_patch]["vertices"] += 1
        elif tokens[0] == "f":
            check(current_patch is not None and len(tokens) in (4, 5),
                  "Non-TRI/QUAD physical face")
            face = [int(value) for value in tokens[1:]]
            start, end = index_range[current_patch]
            check(len(set(face)) == len(face) and
                  all(start <= index <= end for index in face) and
                  all(index <= len(vertices) for index in face),
                  "Face borrows a foreign/future/duplicate physical vertex")
            triangles = [face] if len(face) == 3 else [
                (face[0], face[1], face[2]),
                (face[0], face[2], face[3]),
            ]
            for triangle in triangles:
                a, b, c = (vertices[index - 1] for index in triangle)
                squared = triangle_cross_squared(a, b, c)
                check(math.isfinite(squared) and squared > 0.0,
                      "Physical element has degenerate or nonfinite area")
            groups[current_patch]["tris" if len(face) == 3 else "quads"] += 1
        else:
            raise ValueError(f"Unexpected original physical OBJ record: {line}")

    check(observed_groups == list(range(n)), "Original patch OBJ group order changed")
    check(len(vertices) == expected["nodes"], "Wrong total physical OBJ vertices")
    for p in manifest["patches"]:
        actual = groups[p["patch_id"]]
        check(actual == {"vertices": p["vertices"],
                         "quads": p["quads"], "tris": p["tris"]},
              "OBJ and original source patch manifest counts diverge")
    check(sum(item["quads"] for item in groups.values()) == expected["quads"]
          and sum(item["tris"] for item in groups.values()) == expected["tris"],
          "Original native typed QUAD/TRI physical counts changed")
    return {
        "original_patches": n,
        "physical_nodes": len(vertices),
        "typed_QUAD": expected["quads"],
        "typed_TRI": expected["tris"],
        "patch_group_node_ranges_disjoint": True,
        "nonzero_finite_physical_face_areas": True,
        "matches_native_R2c9_receipts": True,
        "global_nonmanifold_sheet_approved": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    arguments = parser.parse_args()
    evidence = {
        name: verify(arguments.directory, name, spec)
        for name, spec in EXPECTED.items()
    }
    target = arguments.directory / "r2c10_independent_obj_verification.json"
    target.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("R2C10_INDEPENDENT_OBJ_VERIFICATION", json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    main()
