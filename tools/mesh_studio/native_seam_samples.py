"""R2.7.15 original native shared-curve UV/XYZ/logical-node seam audit.

Only compare sampled boundary triangles in one genuine accepted TRI snapshot.
Matching original native node IDs does not establish shared C++ node ownership,
and sampled correspondence does not prove continuous surface coincidence.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path

from .audit_retained_native_lineage import audit_retained_directory
from .native_source_adjacency import analyze_source_incidences
from .verify_native_lineage import (
    SOURCE_MODELS, decode_ndjson, require, sha256_file, validate_lineage_records,
)

SCHEMA = "apmesh.meshstudio.r2715.original_native_sampled_seam.v1"
UV_TOL = 1.0e-9
XYZ_ABS_TOL = 1.0e-9
XYZ_REL_TOL = 1.0e-9


def close_xyz(a: list[float], b: list[float]) -> bool:
    """Use an explicit scale-aware diagnostic threshold, not a welding rule."""
    delta = math.dist(a, b)
    scale = max(1.0, *(abs(x) for x in a), *(abs(x) for x in b))
    return delta <= XYZ_ABS_TOL + XYZ_REL_TOL * scale


def side_parameter(uv: list[float], edge_slot: int) -> tuple[bool, float]:
    """Match the original Adapter's four local UV boundary equations."""
    require(edge_slot in range(4), "invalid_original_patch_edge_slot")
    u, v = uv
    on_side = (
        abs(v) <= UV_TOL if edge_slot == 0 else
        abs(u - 1.0) <= UV_TOL if edge_slot == 1 else
        abs(v - 1.0) <= UV_TOL if edge_slot == 2 else
        abs(u) <= UV_TOL
    )
    return on_side, (u if edge_slot in (0, 2) else v)


def extract_native_side(
    faces: list[dict], patch_slot: int, edge_slot: int, reversed_incidence: bool,
) -> dict:
    """Recover a complete sampled side from original face UV and native IDs."""
    nodes: dict[int, dict] = {}
    edge_use: Counter[tuple[int, int]] = Counter()
    edge_errors: list[str] = []
    for face in faces:
        require(face["patch_slot"] == patch_slot,
                "source_side_face_patch_owner_changed")
        vertices = face["vertices"]
        on_side = [side_parameter(vertex["uv"], edge_slot) for vertex in vertices]
        for i, (is_boundary, local) in enumerate(on_side):
            if not is_boundary:
                continue
            require(-UV_TOL <= local <= 1.0 + UV_TOL,
                    "original_native_boundary_parameter_out_of_range")
            vertex = vertices[i]
            node_id = vertex["native_node_id"]
            t = 1.0 - local if reversed_incidence else local
            sample = {"t": t, "xyz": vertex["xyz"], "native_node_id": node_id}
            if node_id in nodes:
                old = nodes[node_id]
                require(abs(old["t"] - t) <= UV_TOL and
                        close_xyz(old["xyz"], vertex["xyz"]),
                        "same_patch_native_node_inconsistent_uv_or_xyz")
            else:
                nodes[node_id] = sample
        for i in range(3):
            j = (i + 1) % 3
            if not (on_side[i][0] and on_side[j][0]):
                continue
            left = vertices[i]["native_node_id"]
            right = vertices[j]["native_node_id"]
            if left == right:
                edge_errors.append("zero_id_boundary_edge")
            elif abs(on_side[i][1] - on_side[j][1]) <= UV_TOL:
                edge_errors.append("zero_parameter_boundary_edge")
            else:
                edge_use[tuple(sorted((left, right)))] += 1
    ordered = sorted(nodes.values(), key=lambda row: (row["t"], row["native_node_id"]))
    for left, right in zip(ordered, ordered[1:]):
        if abs(left["t"] - right["t"]) <= UV_TOL:
            edge_errors.append("two_native_nodes_at_one_curve_parameter")
    for edge, count in edge_use.items():
        if count != 1:
            edge_errors.append("boundary_edge_not_unique")
    expected = {
        tuple(sorted((a["native_node_id"], b["native_node_id"])))
        for a, b in zip(ordered, ordered[1:])
    }
    if set(edge_use) != expected:
        edge_errors.append("boundary_edge_chain_incomplete_or_branched")
    if len(ordered) < 2 or abs(ordered[0]["t"]) > UV_TOL or (
        abs(ordered[-1]["t"] - 1.0) > UV_TOL
    ):
        edge_errors.append("source_curve_endpoints_missing")
    return {
        "patch_slot": patch_slot,
        "edge_slot": edge_slot,
        "reversed": reversed_incidence,
        "native_boundary_nodes": ordered,
        "unique_boundary_node_count": len(ordered),
        "observed_boundary_edge_count": len(edge_use),
        "sampled_uv_edge_chain_complete": not edge_errors,
        "edge_diagnostics": sorted(set(edge_errors)),
    }


def compare_two_sides(a: dict, b: dict) -> dict:
    """Compare the canonical sampled curve only when both chains are complete."""
    left, right = a["native_boundary_nodes"], b["native_boundary_nodes"]
    complete = a["sampled_uv_edge_chain_complete"] and b["sampled_uv_edge_chain_complete"]
    equal_count = len(left) == len(right)
    node_ids_equal = equal_count and all(
        x["native_node_id"] == y["native_node_id"] for x, y in zip(left, right))
    max_t_delta = max((abs(x["t"] - y["t"]) for x, y in zip(left, right)),
                      default=None) if equal_count else None
    max_xyz_delta = max((math.dist(x["xyz"], y["xyz"])
                         for x, y in zip(left, right)), default=None) if equal_count else None
    canonical_t_aligned = equal_count and all(
        abs(x["t"] - y["t"]) <= UV_TOL for x, y in zip(left, right))
    xyz_aligned = equal_count and all(
        close_xyz(x["xyz"], y["xyz"]) for x, y in zip(left, right))
    return {
        "patch_slots": [a["patch_slot"], b["patch_slot"]],
        "edge_slots": [a["edge_slot"], b["edge_slot"]],
        "sample_counts": [len(left), len(right)],
        "source_boundary_chains_complete": complete,
        "same_sample_count": equal_count,
        "canonical_t_aligned_with_tolerance": canonical_t_aligned,
        "xyz_aligned_with_explicit_tolerance": xyz_aligned,
        "native_logical_node_ids_equal": node_ids_equal,
        "max_paired_t_delta": max_t_delta,
        "max_paired_xyz_delta": max_xyz_delta,
        "sampled_uv_xyz_logical_id_concordance_observed": (
            complete and canonical_t_aligned and xyz_aligned and node_ids_equal
        ),
        "shared_physical_cpp_node_ownership_certified": False,
        "analytic_continuous_curve_coincidence_certified": False,
    }


def analyze_sampled_seams(records: list[dict]) -> dict:
    """Compare all native-source shared incidences without mapping across epochs."""
    graph = analyze_source_incidences(records)
    faces = defaultdict(list)
    for record in records:
        if record.get("type") == "face":
            faces[record["patch_slot"]].append(record)
    shared = []
    compared_pairs = 0
    concordant_pairs = 0
    for curve in graph["source_curve_incidences"]:
        incidences = curve["incidences"]
        if len({item["patch_slot"] for item in incidences}) < 2:
            continue
        sides = [
            extract_native_side(
                faces[incidence["patch_slot"]],
                incidence["patch_slot"], incidence["edge_slot"],
                incidence["reversed"])
            for incidence in incidences
        ]
        comparisons = []
        for i, left in enumerate(sides):
            for right in sides[i + 1:]:
                if left["patch_slot"] == right["patch_slot"]:
                    continue
                result = compare_two_sides(left, right)
                comparisons.append(result)
                compared_pairs += 1
                concordant_pairs += bool(
                    result["sampled_uv_xyz_logical_id_concordance_observed"])
        shared.append({
            "source_curve_slot": curve["source_curve_slot"],
            "native_curve_id": curve["native_curve_id"],
            "distinct_owner_patch_slots": curve["unique_owner_patch_slots"],
            "native_patch_sides": sides,
            "pairwise_sample_comparisons": comparisons,
        })
    return {
        "source_patch_count": graph["source_patch_count"],
        "source_curve_count": graph["source_curve_count"],
        "shared_source_curve_count": len(shared),
        "pairwise_owner_edge_comparisons": compared_pairs,
        "pairwise_sampled_concordance_observed": concordant_pairs,
        "shared_original_source_seams": shared,
        "uv_boundary_side_rule": "edge0_v0_edge1_u1_edge2_v1_edge3_u0",
        "reversed_curve_parameter_rule": "canonical_t_1_minus_local_on_reversed",
        "uv_absolute_tolerance": UV_TOL,
        "xyz_absolute_tolerance": XYZ_ABS_TOL,
        "xyz_relative_tolerance": XYZ_REL_TOL,
        "physical_node_welding_certified": False,
        "continuous_geometric_error_certified": False,
        "cross_epoch_lineage_certified": False,
    }


def audit_original_sampled_seams(directory: Path) -> dict:
    """Anchor every tested sampled seam to the real native retained record."""
    retained = audit_retained_directory(directory)
    models = {}
    for model in SOURCE_MODELS:
        summary = json.loads(
            (directory / ("r2712-" + model + "-native-lineage-audit.json"))
            .read_text(encoding="utf-8"))
        snapshots = []
        for observation in summary["accepted_snapshots"]:
            raw_path = directory / observation["raw_native_ndjson_artifact_name"]
            records = decode_ndjson(raw_path.read_bytes())
            validation = validate_lineage_records(records, model)
            require(sha256_file(raw_path) == observation["source_file_sha256"] and
                    validation["accepted_step"] == observation["accepted_step"],
                    "native_source_seam_original_snapshot_rejected")
            snapshots.append({
                "original_native_accepted_step": validation["accepted_step"],
                "original_native_source_sha256": observation["source_file_sha256"],
                "sampled_boundary": analyze_sampled_seams(records),
            })
        require([s["original_native_accepted_step"] for s in snapshots] ==
                retained["original_native_models"][model]["accepted_native_steps"],
                "original_native_sampled_seam_epoch_mismatch")
        models[model] = snapshots
    return {
        "schema": SCHEMA,
        "source_evidence": "ORIGINAL_NATIVE_ACCEPTED_TRI_PER_FACE_UV_XYZ_AND_ID",
        "original_native_models": models,
        "sampled_curves_are_not_physical_welding": True,
        "scientific_lod_qualified": False,
        "physical_gpu_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit_original_sampled_seams(args.directory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    compact = {
        model: [{
            "step": item["original_native_accepted_step"],
            "shared_curves": item["sampled_boundary"]["shared_source_curve_count"],
            "pairs": item["sampled_boundary"]["pairwise_owner_edge_comparisons"],
            "concordant_pairs": item["sampled_boundary"][
                "pairwise_sampled_concordance_observed"],
        } for item in snapshots]
        for model, snapshots in result["original_native_models"].items()
    }
    print("R2715_ORIGINAL_NATIVE_SAMPLED_SEAMS=" + json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
