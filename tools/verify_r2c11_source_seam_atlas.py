#!/usr/bin/env python3
"""Audit native source-curve seam sites against detached original QUAD/AFT OBJ.

Source ID and point equality is not authorization to weld non-manifold sheets.
"""

import argparse
import csv
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path


ORIGINAL = {
    "eistute": {
        "patches": 4, "curves": 13, "source_points": 115,
        "side_sites": 136, "shared_valence": 4, "shared_pairs": 6,
    },
    "book": {
        "patches": 28, "curves": 85, "source_points": 747,
        "side_sites": 936, "shared_valence": 28, "shared_pairs": 378,
    },
}


def require(value, problem):
    if not value:
        raise ValueError(problem)


def near_xyz(a, b):
    delta = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
    normalizer = max(1.0, math.sqrt(sum(x * x for x in a)),
                     math.sqrt(sum(y * y for y in b)))
    return math.isfinite(delta) and delta <= 2e-7 * normalizer


def read_exported_obj(obj_path):
    points = {}
    group = None
    by_group = defaultdict(list)
    for line in obj_path.read_text(encoding="utf-8").splitlines():
        values = line.split()
        if not values or values[0] in {"#", "o"}:
            continue
        if values[0] == "g":
            require(len(values) == 2 and values[1].startswith("patch_"),
                    "Unexpected original physical group")
            group = int(values[1][6:])
        elif values[0] == "v":
            require(group is not None and len(values) == 4,
                    "Detached original source vertex has no patch owner")
            xyz = tuple(map(float, values[1:]))
            require(all(math.isfinite(x) for x in xyz),
                    "Invalid exported physical vertex")
            global_index = len(points) + 1
            points[global_index] = (group, xyz)
            by_group[group].append(global_index)
    return points, by_group


def verify_one_model(directory, model, spec):
    meta = json.loads((directory / f"{model}_all_sides_detached_quad_aft.json")
                      .read_text(encoding="utf-8"))
    vertices, groups = read_exported_obj(
        directory / f"{model}_all_sides_detached_quad_aft.obj")
    require(meta["original_patches"] == spec["patches"] and
            len(meta["patches"]) == spec["patches"],
            "Source chart scope does not match original model")
    require(set(groups) == set(range(spec["patches"])),
            "Original physical OBJ is missing patch groups")
    require(meta["cross_patch_welding"] is False,
            "Cannot use this checker to certify a physically welded model")

    filepath = directory / f"{model}_original_source_seam_atlas.csv"
    with filepath.open(newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))
    require(len(records) == spec["side_sites"],
            "Original source seam atlas lost an adapted incidence site")
    by_side = defaultdict(list)
    by_curve = defaultdict(list)
    source_witnesses = set()
    for r in records:
        patch = int(r["patch_id"])
        side = int(r["side"])
        curve = int(r["curve_id"])
        node = int(r["source_node_id"])
        t = float(r["source_parameter"])
        xyz = (float(r["source_x"]), float(r["source_y"]),
               float(r["source_z"]))
        index = int(r["obj_vertex_index"])
        terminal = int(r["is_terminal"])
        require(0 <= patch < spec["patches"] and 0 <= side < 4 and
                node > 0 and 0.0 <= t <= 1.0 and terminal in (0, 1),
                "Bad original source curve incidence provenance")
        require(index in vertices and vertices[index][0] == patch,
                "Original source site referenced another patch's physical node")
        require(all(math.isfinite(x) for x in xyz) and
                near_xyz(xyz, vertices[index][1]),
                "Adapted source site has no corresponding exported physical node")
        by_side[(patch, side)].append((curve, node, t, xyz, terminal))
        by_curve[curve].append((patch, side, node, t, xyz, terminal))
        source_witnesses.add((patch, side, node, t, index))

    require(len(source_witnesses) == len(records),
            "Repeated source patch-side knots in atlas")
    require(len(by_side) == 4 * spec["patches"],
            "Not every one of the original four sides has source witnesses")
    require(len(by_curve) == spec["curves"],
            "The actual source atlas does not cover all original curves")
    for key, values in by_side.items():
        require(len(values) >= 3 and sum(x[4] for x in values) == 1,
                f"Original side {key} lost refined knots or its terminal")
        require(len({x[0] for x in values}) == 1,
                "One patch side references different original source curves")
        t = [x[2] for x in values]
        increasing = all(a < b for a, b in zip(t, t[1:]))
        decreasing = all(a > b for a, b in zip(t, t[1:]))
        require(increasing or decreasing,
                "Adapted original curve orientation/order is not monotone")
        require(values[-1][4] == 1,
                "Terminal source sample was not last on chart side")

    source_points = 0
    shared_valences = []
    compared_pairs = 0
    compared_sites = 0
    for curve, values in by_curve.items():
        incidences = defaultdict(list)
        for patch, side, node, t, xyz, terminal in values:
            incidences[(patch, side)].append((t, node, xyz))
        order = sorted(incidences)
        canonical = sorted(incidences[order[0]])
        require(len({t for t, _, _ in canonical}) == len(canonical),
                "Original source curve contains duplicated parameters")
        source_points += len(canonical)
        for site in order[1:]:
            observed = sorted(incidences[site])
            require(len(observed) == len(canonical),
                    "Original source curve subdivision differs by patch")
            for a, b in zip(canonical, observed):
                require(a[0] == b[0] and a[1] == b[1] and
                        near_xyz(a[2], b[2]),
                        "Shared source curve physical site or source node mismatch")
        if len(order) > 1:
            shared_valences.append(len(order))
            for left, right in itertools.combinations(order, 2):
                a = sorted(incidences[left])
                b = sorted(incidences[right])
                require(len(a) == len(b),
                        "Shared original source sites have different counts")
                compared_pairs += 1
                compared_sites += len(a)
    require(source_points == spec["source_points"],
            "Actual source atlas does not recover all original curve points")
    require(shared_valences == [spec["shared_valence"]],
            "Unexpected non-manifold original source curve valences")
    require(compared_pairs == spec["shared_pairs"],
            "Original shared radial incidence comparison count differs")

    return {
        "patches": spec["patches"],
        "source_curves": len(by_curve),
        "unique_source_curve_points": source_points,
        "physical_obj_source_witnesses": len(records),
        "all_original_patch_sides": len(by_side),
        "shared_nonmanifold_curve_valence": shared_valences[0],
        "verified_shared_incidence_pairs": compared_pairs,
        "verified_shared_incidence_sites": compared_sites,
        "per_patch_physical_ownership_preserved": True,
        "globally_welded_or_scientifically_approved": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, type=Path)
    args = parser.parse_args()
    results = {
        name: verify_one_model(args.directory, name, spec)
        for name, spec in ORIGINAL.items()
    }
    report = args.directory / "r2c11_source_seam_atlas_verification.json"
    report.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("R2C11_ORIGINAL_SOURCE_SEAM_AUDIT",
          json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
