#!/usr/bin/env python3
"""Build a conservative, read-only sheet/curve incidence hypergraph.

The source is an actual production PatchReader/PatchBezier physical-sampling
run, validated independently in the previous M4 CTest. No topological welding
or physical element ownership is implemented by this research experiment.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path

from audit_model_catalog import INPUT_MODELS, parse_bp
from test_m4_external_bezier_physical import (
    CENTER_RULES, EXPECTED, FIELDS, bernstein, cross, curve_groups,
    dot, incidence_from_cpp, norm, approximately,
    SEAM_DIAGNOSTIC_THRESHOLD,
)
from test_m5_constrained_delaunay import read_obj, require

SITES_PER_EDGE = 5
# Diagnostic thresholds are NOT an approved CAD welding or meshing policy.
TANGENT_COS_MIN = 1.0 - 1e-7
SECTOR_SEPARATION_RAD_MIN = 1e-3
MIN_TANGENT = 1e-11
MODEL_KEYS = {"Eistute": "eistute", "Book": "book",
              "Ribbed Bracket": "ribbed_bracket"}
ZERO_VEC = (0.0, 0.0, 0.0)


def vec_scale(a, factor):
    return tuple(x * factor for x in a)


def vec_sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def normalise(a):
    magnitude = norm(a)
    return None if not math.isfinite(magnitude) or magnitude < MIN_TANGENT else (
        tuple(x / magnitude for x in a)
    )


def edge_uv(side, u, v):
    return ((side == 0 and v == 0.0)
            or (side == 1 and u == 1.0)
            or (side == 2 and v == 1.0)
            or (side == 3 and u == 0.0))


def ordered_sites(uv, physical, side, reversed_curve):
    sites = []
    for vertex_id, ((u, v, unused), sample) in enumerate(zip(uv, physical)):
        require(unused == 0.0, "Native UV source is not planar")
        if not edge_uv(side, u, v):
            continue
        local_t = u if side in (0, 2) else v
        t = 1.0 - local_t if reversed_curve else local_t
        tangent = sample["du"] if side in (0, 2) else sample["dv"]
        tangent = vec_scale(tangent, -1.0 if reversed_curve else 1.0)
        inward = {
            0: sample["dv"],
            1: vec_scale(sample["du"], -1),
            2: vec_scale(sample["dv"], -1),
            3: sample["du"],
        }[side]
        direction = normalise(tangent)
        projected = ZERO_VEC if direction is None else vec_sub(
            inward, vec_scale(direction, dot(direction, inward))
        )
        sector = normalise(projected)
        sites.append({"t": round(t, 12), "id": vertex_id,
                      "xyz": sample["xyz"], "tangent": direction,
                      "sector": sector})
    sites.sort(key=lambda row: row["t"])
    require(len(sites) == SITES_PER_EDGE and
            [row["t"] for row in sites] == [0.0, .25, .5, .75, 1.0],
            "Native QUAD/M5 shared boundary no longer has five canonical sites")
    return sites


def physical_rows(filename, patch_count, uv):
    with filename.open(encoding="ascii", newline="") as stream:
        table = list(csv.DictReader(stream))
    require(len(table) == patch_count * len(uv)
            and tuple(table[0]) == FIELDS,
            "Production PatchBezier sample CSV schema/count changed")
    results = [[] for _ in range(patch_count)]
    for ordinal, row in enumerate(table):
        pid, vid = divmod(ordinal, len(uv))
        require(int(row["patch"]) == pid and int(row["id"]) == vid
                and approximately(
                    (float(row["u"]), float(row["v"])),
                    uv[vid][:2], absolute=1e-11),
                "Production samples are not in native UV source order")
        xyz = tuple(float(row[k]) for k in ("x", "y", "z"))
        qu = tuple(float(row[k]) for k in ("qu_x", "qu_y", "qu_z"))
        qv = tuple(float(row[k]) for k in ("qv_x", "qv_y", "qv_z"))
        require(all(math.isfinite(x) for x in xyz+qu+qv),
                "Nonfinite source-linked sample")
        result = {"xyz": xyz, "du": qu, "dv": qv}
        cross_norm = norm(cross(qu, qv))
        require(math.isfinite(cross_norm) and math.isclose(
                cross_norm, float(row["jacobian_norm"]),
                rel_tol=2e-10, abs_tol=5e-7),
                "Incorrect production tangent cross-derivative magnitude")
        results[pid].append(result)
    return results


def pair_measure(first, second):
    require([site["t"] for site in first] ==
            [site["t"] for site in second],
            "Mismatched canonical parameter location on an incidence")
    gaps, tangent_cos = [], []
    for left, right in zip(first, second):
        gaps.append(math.dist(left["xyz"], right["xyz"]))
        a, b = left["tangent"], right["tangent"]
        tangent_cos.append(None if a is None or b is None
                           else max(-1.0, min(1.0, dot(a, b))))
    sector_a, sector_b = first[2]["sector"], second[2]["sector"]
    sector_angle = None
    if sector_a is not None and sector_b is not None:
        sector_angle = math.acos(max(-1.0, min(1.0, dot(
            sector_a, sector_b
        ))))
    return {
        "maximum_sampled_position_gap": max(gaps),
        "minimum_canonical_tangent_dot": (
            min(x for x in tangent_cos if x is not None)
            if all(x is not None for x in tangent_cos) else None
        ),
        "interior_sector_angle_rad_at_midpoint": sector_angle,
        "paired_native_vertex_ids": [
            [int(a["id"]), int(b["id"])]
            for a, b in zip(first, second)
        ],
    }


def winding_sign(side, reverse):
    # Local Bezier patch boundary winds CCW in the UV chart.
    local_boundary_forward = 1 if side in (0, 1) else -1
    return local_boundary_forward * (-1 if reverse else 1)


def classify_pair(first, second, measurement, valence):
    if valence > 2:
        return "QUARANTINED_HIGH_VALENCE_NO_AUTOMATIC_WELD"
    if valence != 2:
        raise ValueError("Only a pair of curve incidences can be classified")
    gap = measurement["maximum_sampled_position_gap"]
    tangent = measurement["minimum_canonical_tangent_dot"]
    angle = measurement["interior_sector_angle_rad_at_midpoint"]
    if gap > SEAM_DIAGNOSTIC_THRESHOLD:
        return "BLOCKED_NONCOINCIDENT_PHYSICAL_SEAM"
    if tangent is None or tangent < TANGENT_COS_MIN:
        return "BLOCKED_TANGENT_MISMATCH_OR_DEGENERACY"
    if angle is None or angle <= SECTOR_SEPARATION_RAD_MIN:
        return "BLOCKED_COINCIDENT_OR_DEGENERATE_INTERIOR_SECTOR"
    if first["winding_sign"] == second["winding_sign"]:
        return "ORIENTATION_REVIEW_NOT_AUTOMATICALLY_WELDABLE"
    return "PAIRWISE_GEOMETRY_CANDIDATE_REQUIRES_SCIENTIFIC_APPROVAL"


def approve_selected_pairs(graph, proposals, *, scientifically_approved=False):
    # This is an explicit fail-closed interface, not a welding implementation.
    require(scientifically_approved,
            "Explicit scientific sheet-pair approval missing: no welding permitted")
    lookup = {pair["pair_key"]: pair for curve in graph["curves"]
              for pair in curve["pairs"]}
    require(len(proposals) == len(set(proposals)),
            "Duplicate scientific boundary admission")
    for pair_id in proposals:
        require(pair_id in lookup, "Unknown curve/sheet pairing proposed")
        require(lookup[pair_id]["classification"] ==
                "PAIRWISE_GEOMETRY_CANDIDATE_REQUIRES_SCIENTIFIC_APPROVAL",
                "Rejected, ambiguous or high-valence curve pairing requested")
    # Even explicit eligible selection never performs physical node adoption.
    return {"approved_pair_keys": list(proposals),
            "physical_nodes_welded": False,
            "weld_implementation_exists": False}


def test_admission_negative_controls(graph, physical, uv):
    cases = 0
    all_pairs = [p for c in graph["curves"] for p in c["pairs"]]
    high = [p for p in all_pairs
            if p["classification"].startswith("QUARANTINED_HIGH_VALENCE")]
    require(high, "Expected adversarial high-valence source curve not detected")
    try:
        approve_selected_pairs(graph, [high[0]["pair_key"]],
                               scientifically_approved=True)
    except ValueError:
        cases += 1
    else:
        raise AssertionError("High-valence sheet pairing was admitted")
    try:
        approve_selected_pairs(graph, [],
                               scientifically_approved=False)
    except ValueError:
        cases += 1
    else:
        raise AssertionError("Implicit boundary admission was allowed")
    try:
        approve_selected_pairs(graph, ["fabricated:0:1"],
                               scientifically_approved=True)
    except ValueError:
        cases += 1
    else:
        raise AssertionError("Unknown sheet pairing was admitted")

    # The same measured curve cannot remain C0-coincident after an XYZ crack.
    a = [{"t": t, "xyz": (t, 0.0, 0.0),
          "id": k, "tangent": (1.0, 0.0, 0.0),
          "sector": (0.0, 1.0, 0.0)}
         for k, t in enumerate((0.0, .25, .5, .75, 1.0))]
    b = [{"t": x["t"], "xyz": x["xyz"], "id": x["id"]+5,
          "tangent": x["tangent"], "sector": (0.0, -1.0, 0.0)}
         for x in a]
    left, right = {"winding_sign": 1}, {"winding_sign": -1}
    require(classify_pair(left, right, pair_measure(a, b), 2) ==
            "PAIRWISE_GEOMETRY_CANDIDATE_REQUIRES_SCIENTIFIC_APPROVAL",
            "Positive two-sheet geometry control failed")
    cases += 1
    cracked = [dict(x) for x in b]
    cracked[2]["xyz"] = (0.5, 0.1, 0.0)
    require(classify_pair(left, right, pair_measure(a, cracked), 2) ==
            "BLOCKED_NONCOINCIDENT_PHYSICAL_SEAM",
            "Altered physical seam remained a share candidate")
    cases += 1
    backward = [dict(x) for x in b]
    backward[1]["tangent"] = (-1.0, 0.0, 0.0)
    require(classify_pair(left, right, pair_measure(a, backward), 2) ==
            "BLOCKED_TANGENT_MISMATCH_OR_DEGENERACY",
            "Reversed shared tangent was not rejected")
    cases += 1
    coincident = [dict(x) for x in b]
    coincident[2]["sector"] = (0.0, 1.0, 0.0)
    require(classify_pair(left, right, pair_measure(a, coincident), 2) ==
            "BLOCKED_COINCIDENT_OR_DEGENERATE_INTERIOR_SECTOR",
            "Overlapping physical sheets were not rejected")
    cases += 1
    require(classify_pair(left, {"winding_sign": 1},
                          pair_measure(a, b), 2) ==
            "ORIENTATION_REVIEW_NOT_AUTOMATICALLY_WELDABLE",
            "Same-sign face winding was silently admitted")
    cases += 1
    require(classify_pair(left, right, pair_measure(a, b), 28) ==
            "QUARANTINED_HIGH_VALENCE_NO_AUTOMATIC_WELD",
            "Even compatible high-valence incidences were silently paired")
    cases += 1
    require(cases == 9, "Incomplete selected/negative pairing controls")
    return cases


def graph_components(patch_count, curves):
    parent = list(range(patch_count))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for curve in curves:
        for pair in curve["pairs"]:
            if pair["classification"] != (
                    "PAIRWISE_GEOMETRY_CANDIDATE_REQUIRES_SCIENTIFIC_APPROVAL"):
                continue
            a, b = pair["patches"]
            parent[find(a)] = find(b)
    groups = defaultdict(list)
    for patch_id in range(patch_count):
        groups[find(patch_id)].append(patch_id)
    return sorted((sorted(s) for s in groups.values()),
                  key=lambda group: group[0])


def build_model_graph(name, path, physical_csv, curve_csv, uv):
    raw = path.read_bytes()
    control_vertices, patches = parse_bp(raw.decode("utf-8"))
    count = EXPECTED[name][0]
    require(len(patches) == count, "A versioned BP patch count changed")
    owned_groups, orientations = incidence_from_cpp(curve_csv, count)
    require(owned_groups == curve_groups(control_vertices, patches),
            "Production Geometry-owned curve graph differs from BP control net")
    physical = physical_rows(physical_csv, count, uv)
    for patch_id, indices in enumerate(patches):
        # Independent geometric cross-check at every physical boundary vertex.
        controls = [control_vertices[k] for k in indices]
        for uv_id, (u, v, _) in enumerate(uv):
            if not (u in (0.0, 1.0) or v in (0.0, 1.0)):
                continue
            xyz, qu, qv = bernstein(controls, u, v)
            sample = physical[patch_id][uv_id]
            require(approximately(sample["xyz"], xyz) and
                    approximately(sample["du"], qu) and
                    approximately(sample["dv"], qv),
                    "Observed C++ boundary differs from independent Bernstein")
    curves = []
    for curve_id, owners in enumerate(owned_groups):
        # Independent canonical group ordering need not equal the production
        # curve numeric ID; locate the real recorded curve ID via first owner.
        incidence_by_owner = {}
        with curve_csv.open(encoding="ascii", newline="") as stream:
            for row in csv.DictReader(stream):
                incidence_by_owner[(int(row["patch"]), int(row["side"]))] = int(
                    row["curve_id"]
                )
        real_id = incidence_by_owner[owners[0]]
        require(all(incidence_by_owner[o] == real_id for o in owners),
                "Source control curve ownership differs from C++ registry")
        instances = []
        for patch_id, side in owners:
            reverse = orientations[(patch_id, side)]
            sites = ordered_sites(uv, physical[patch_id], side, reverse)
            instances.append({
                "patch": patch_id, "side": side,
                "node_key": f"patch:{patch_id}:side:{side}",
                "curve_reversed": reverse,
                "winding_sign": winding_sign(side, reverse),
                "sites": sites,
            })
        pairs = []
        for i in range(len(instances)):
            for j in range(i+1, len(instances)):
                left, right = instances[i], instances[j]
                measures = pair_measure(left["sites"], right["sites"])
                classification = classify_pair(
                    left, right, measures, len(owners)
                )
                pairs.append({
                    "pair_key": (
                        f"curve:{real_id}:"
                        f"{left['patch']}:{left['side']}~"
                        f"{right['patch']}:{right['side']}"
                    ),
                    "incidences": [left["node_key"], right["node_key"]],
                    "patches": [left["patch"], right["patch"]],
                    "classification": classification,
                    "physical_geometry": measures,
                    "winding_signs": [left["winding_sign"],
                                      right["winding_sign"]],
                    "weld_performed": False,
                })
        curves.append({
            "curve_id": real_id,
            "degree": len(owners),
            "incidences": [{
                "patch": s["patch"], "side": s["side"],
                "node_key": s["node_key"], "curve_reversed": s["curve_reversed"],
                "winding_sign": s["winding_sign"],
                "canonical_source_uv_node_ids": [x["id"] for x in s["sites"]],
                "canonical_sample_t": [x["t"] for x in s["sites"]],
                "canonical_sample_xyz": [list(x["xyz"]) for x in s["sites"]],
            } for s in instances],
            "pairs": pairs,
            "high_valence_quarantined": len(owners) > 2,
        })
    curves.sort(key=lambda c: c["curve_id"])
    degrees = Counter(c["degree"] for c in curves)
    ex = EXPECTED[name]
    require((degrees[1], degrees[2],
             sum(v for k, v in degrees.items() if k > 2),
             max(degrees)) == ex[2:],
            "Model incidence graph degrees do not match versioned baseline")
    classes = Counter(p["classification"]
                      for c in curves for p in c["pairs"])
    require(classes["QUARANTINED_HIGH_VALENCE_NO_AUTOMATIC_WELD"] > 0,
            "Model-specific nonmanifold adversary disappeared")
    for c in curves:
        if c["degree"] > 2:
            require(all(p["classification"] ==
                        "QUARANTINED_HIGH_VALENCE_NO_AUTOMATIC_WELD"
                        for p in c["pairs"]),
                    "A higher-valence curve received an implicit welding edge")
    components = graph_components(count, curves)
    return {
        "model": name,
        "source_path": str(path.as_posix()),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "patch_count": count,
        "curve_count": len(curves),
        "source_incidence_sha256": hashlib.sha256(curve_csv.read_bytes()).hexdigest(),
        "source_physical_sha256": hashlib.sha256(physical_csv.read_bytes()).hexdigest(),
        "interface_pair_classes": dict(sorted(classes.items())),
        "candidate_only_patch_components": components,
        "candidate_components_are_not_actual_welded_sheets": True,
        "curve_degrees": dict(sorted(degrees.items())),
        "curves": curves,
        "no_node_adoption_or_weld": True,
        "high_valence_sheet_policy_approved": False,
    }


def graph_summary(graph):
    classes = graph["interface_pair_classes"]
    return {
        "model": graph["model"],
        "patches": graph["patch_count"],
        "curves": graph["curve_count"],
        "high_valence_curves": sum(c["degree"] > 2 for c in graph["curves"]),
        "higher_valence_incidence_pairs_quarantined": classes.get(
            "QUARANTINED_HIGH_VALENCE_NO_AUTOMATIC_WELD", 0),
        "pairwise_geometry_candidates_needing_approval": classes.get(
            "PAIRWISE_GEOMETRY_CANDIDATE_REQUIRES_SCIENTIFIC_APPROVAL", 0),
        "pairwise_review_or_block_count": sum(
            value for key, value in classes.items()
            if not key.startswith(("QUARANTINED_HIGH_VALENCE",
                                   "PAIRWISE_GEOMETRY_CANDIDATE"))
        ),
        "candidate_only_components": len(graph[
            "candidate_only_patch_components"]),
    }


def write_dot(path, graph):
    # Bipartite hypergraph: no fictitious pairwise welding at high valence.
    lines = ["graph research_patch_incidence {",
             '  graph [label="Research only: no physical node welding"];',
             "  rankdir=LR;"]
    for patch in range(graph["patch_count"]):
        lines.append(f'  p{patch} [label="Patch {patch}",shape=box];')
    for curve in graph["curves"]:
        cid = curve["curve_id"]
        degree = curve["degree"]
        color = "red" if degree > 2 else (
            "gray" if degree == 1 else "blue")
        lines.append(f'  c{cid} [label="Curve {cid} (d={degree})",'
                     f'color="{color}",shape=ellipse];')
        for owner in curve["incidences"]:
            lines.append(f'  p{owner["patch"]} -- c{cid}'
                         f' [label="s{owner["side"]}",color="{color}"];')
    lines.append("}")
    path.write_text("\n".join(lines)+"\n", encoding="ascii")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--physical-directory", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    source_dir = args.physical_directory.resolve()
    output_dir = args.directory.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    prior_path = source_dir / "m4_external_bezier_physical_manifest.json"
    require(prior_path.is_file(),
            "Run the independent production physical M4 CTest before graph audit")
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    require(prior["status"] ==
            "REAL_EXTERNAL_BEZIER_PER_PATCH_PHYSICAL_CANDIDATES_DIAGNOSTIC_ONLY"
            and prior["model_patches"] == 45
            and prior["negative_mutations_rejected"] == 4
            and len(prior["outcomes"]) == 6
            and prior["actual_global_node_welding"] is False,
            "Prior exact-source physical validation was missing or weakened")
    baseline = {}
    graphs = []
    total_negatives = 0
    for center in CENTER_RULES:
        original = source_dir / f"hybrid_research_local_delaunay_{center}.obj"
        uv, quad, tri = read_obj(original)
        require(len(uv) == 69 and len(quad) == 42 and len(tri) == 36,
                "Actual native QUAD/M5 Lawson source UV changed")
        for model, (relative, _) in INPUT_MODELS.items():
            name = MODEL_KEYS[model]
            graph = build_model_graph(
                model, root / relative,
                source_dir / f"real_{name}_{center}_samples.csv",
                source_dir / f"real_{name}_{center}_curves.csv", uv
            )
            totals = graph_summary(graph)
            if center == CENTER_RULES[0]:
                total_negatives += test_admission_negative_controls(graph, [], uv)
                baseline[model] = totals
            else:
                # Two unapproved interior centroid rules must NOT modify
                # source curve topology, admission classification or owners.
                old = baseline[model]
                require({k: v for k, v in totals.items() if k != "model"} ==
                        {k: v for k, v in old.items() if k != "model"},
                        "Interior center rule altered real source sheet graph")
            graph["center_rule"] = center
            target = output_dir / f"sheet_graph_{name}_{center}.json"
            target.write_text(json.dumps(graph, indent=2, allow_nan=False) +
                              "\n", encoding="utf-8")
            write_dot(output_dir / f"sheet_graph_{name}_{center}.dot", graph)
            graphs.append({"model": model, "center_rule": center,
                           "json": target.name, "summary": totals,
                           "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    require(total_negatives == 27 and len(graphs) == 6,
            "All high-valence and controlled admission failures are required")
    result = {
        "schema": 1,
        "status": "SOURCE_LINKED_PATCH_CURVE_INCIDENCE_GRAPH_NO_WELDING",
        "physical_samples_checked_against_production": True,
        "source_models": list(INPUT_MODELS),
        "real_model_patches": 45,
        "center_rule_cases": 6,
        "negative_or_positive_admission_controls": total_negatives,
        "actual_node_welding": False,
        "element_ownership_created": False,
        "high_valence_pair_weld_enabled": False,
        "approved_scientific_sheet_policy": False,
        "historical_1993_contour_or_delaunay": False,
        "production_quad_enabled": False,
        "diagnostic_thresholds_are_not_welding_tolerances": True,
        "prior_source_physical_manifest_sha256": hashlib.sha256(
            prior_path.read_bytes()).hexdigest(),
        "outcomes": graphs,
    }
    (output_dir / "m4_sheet_incidence_manifest.json").write_text(
        json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8"
    )
    print("m4_sheet_incidence=ok models=3 patches=45 cases=6 "
          "production_PatchReader_provenance=1 diagnostic_pairs_only=1 "
          "negative_and_positive_controls=27 "
          "high_valence=QUARANTINED no_global_welding=1 NOT_production")


if __name__ == "__main__":
    main()
