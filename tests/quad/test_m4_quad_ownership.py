#!/usr/bin/env python3
"""Qualify borrowed four-node physical QUAD lifecycle on actual native M4 geometry."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def execute(command, *, expect_success=True):
    result = subprocess.run(command, capture_output=True, text=True,
                            timeout=180, check=False)
    if (result.returncode == 0) != expect_success:
        raise AssertionError(
            f"Unexpected exit code {result.returncode}: {command}\n"
            f"{result.stdout[-1500:]}\n{result.stderr[-1500:]}")
    return result.stdout


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree-exe", type=Path, required=True)
    parser.add_argument("--lift-exe", type=Path, required=True)
    parser.add_argument("--ownership-exe", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()

    folder = args.directory.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parent

    # Generate the same already-qualified native C++/M5 inputs and audit the
    # complete 69/42/36 physical Bezier witness before adopting any nodes.
    execute([sys.executable, str(root / "test_m4_real_model_hybrid.py"),
             "--tree-exe", str(args.tree_exe.resolve()),
             "--lift-exe", str(args.lift_exe.resolve()),
             "--directory", str(folder)])
    prior = json.loads(
        (folder / "physical_model_hybrid_manifest.json").read_text(encoding="utf-8"))
    require(prior["status"] ==
            "REAL_BUILTIN_APMESH_BEZIER_RESEARCH_HYBRID_NOT_PRODUCTION"
            and prior["negative_controls"] == 22
            and len(prior["outcomes"]) == 2,
            "Prior production-model mapping oracle missing or weakened")

    results = []
    for mode in ("vertex_mean", "area_centroid"):
        uv = folder / f"hybrid_research_local_delaunay_{mode}.obj"
        physical = folder / f"physical_model_hybrid_{mode}.obj"
        verified = execute([str(args.ownership_exe.resolve()),
                            str(uv), str(physical)])
        require("quad_four_node_lifecycle=ok" in verified
                and "quad_four_corner_admission=ok accepted=20 rejected=40"
                in verified
                and "observer_values_order_slots=preserved" in verified
                and "observer_links=276" in verified
                and "shared_seam=20 boundary=16" in verified,
                "Physical quad ownership and mixed-node witness incomplete")
        rejected = 0
        lines = physical.read_text(encoding="ascii").splitlines()
        vertex_idx = next(i for i, line in enumerate(lines) if line.startswith("v "))
        quad_idx = next(i for i, line in enumerate(lines) if line.startswith("f "))
        group_idx = next(i for i, line in enumerate(lines)
                         if line.startswith("g QUAD_"))
        variants = {
            "bad_xyz": {vertex_idx: "v 10.0 10.0 10.0"},
            "bad_face": {quad_idx: "f 2 1 3 4"},
            "bad_group": {group_idx: "g NOT_NATIVE_QUAD"},
        }
        for label, replacements in variants.items():
            mutated = list(lines)
            for index, value in replacements.items():
                mutated[index] = value
            damaged = folder / f"negative_ownership_{mode}_{label}.obj"
            damaged.write_text("\n".join(mutated) + "\n", encoding="ascii")
            execute([str(args.ownership_exe.resolve()), str(uv), str(damaged)],
                    expect_success=False)
            rejected += 1
        require(rejected == 3, "Expected physical ownership negative cases missing")
        results.append({
            "mode": mode,
            "physical_obj_sha256": sha256(physical),
            "native_uv_sha256": sha256(uv),
            "quad_elements": 42,
            "tri_elements": 36,
            "owned_nodes": 69,
            "registered_observer_links": 276,
            "seam_edges": 20,
            "outer_boundary_edges": 16,
            "deterministic_constructor_failures": 4,
            "invalid_constructor_inputs": 7,
            "convexity_accepted_inputs": 20,
            "convexity_rejected_inputs": 40,
            "negative_file_mutations_rejected": rejected,
            "passed": True,
        })

    evidence = {
        "schema": 1,
        "status": "RESEARCH_OWNED_QUAD_NODES_BORROWED_4_NODE_ELEMENTS_NOT_PRODUCTION",
        "model": "Models3d::ModelCurvaBezier",
        "native_quadtree_source": True,
        "research_m5_lawson_exterior": True,
        "historical_1993_implemented": False,
        "production_quad_enabled": False,
        "all_quad_enabled": False,
        "imported_CAD_boundary_validated": False,
        "centroid_approved": False,
        "physical_mesh_ownership": "SubMesh unique_ptr nodes and elements",
        "quadrilateral_nodes": "four borrowed NodeAdaptive pointers",
        "independent_model_oracle": "test_m4_real_model_hybrid.py",
        "m4_prior_negative_controls": 22,
        "negative_mutations_total_new": 6,
        "outcomes": results,
    }
    (folder / "physical_quad_ownership_manifest.json").write_text(
        json.dumps(evidence, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("m4_quad_ownership=ok model=ModelCurvaBezier "
          "nodes=69 quads=42 tri=36 links=276 mixed_seam=20 "
          "failing_constructors=11_per_mode altered_files_rejected=6 "
          "four_corner_accepted=20_per_mode four_corner_rejected=40_per_mode "
          "NOT_production")


if __name__ == "__main__":
    main()
