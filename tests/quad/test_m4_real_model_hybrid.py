#!/usr/bin/env python3
"""Independent M4 audit of native C++ QUAD/M5 TRI on an actual APMesh Bezier model.

The control points below are pinned independently from production
Models3d::ModelCurvaBezier. This is a built-in curved model, NOT imported CAD,
the historical 1993 exterior algorithm, or production QUAD publication.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

from test_m5_constrained_delaunay import edges, read_obj, require, validate

# Independent, explicit control-net golden from the production model's
# 16 documented controls (i is the u Bernstein index, j the v index).
CONTROLS = (
    ((1.0, -1.0, 0.0), (0.5, -1.0, 0.0), (-0.5, -1.0, 0.0), (-1.0, -1.0, 0.0)),
    ((0.5, -0.5, 0.0), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.0), (-1.0, -0.5, 0.0)),
    ((0.5, 0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0), (-1.0, 0.5, 0.0)),
    ((1.0, 1.0, 0.0), (0.5, 1.0, 0.0), (-0.5, 1.0, 0.0), (-1.0, 1.0, 0.0)),
)


def basis(t):
    s = 1.0 - t
    return ((s*s*s, 3.0*t*s*s, 3.0*t*t*s, t*t*t),
            (-3.0*s*s, 3.0*s*(1.0-3.0*t),
             3.0*t*(2.0-3.0*t), 3.0*t*t))


def golden(u, v, controls=CONTROLS):
    bu, du = basis(u)
    bv, dv = basis(v)
    results = []
    for weights_u, weights_v in ((bu, bv), (du, bv), (bu, dv)):
        results.append(tuple(
            sum(weights_u[i] * weights_v[j] * controls[i][j][axis]
                for i in range(4) for j in range(4))
            for axis in range(3)))
    return tuple(results)


def vector(a, b):
    return tuple(y-x for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1],
            a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def magnitude(v):
    return math.sqrt(dot(v, v))


def approximately(a, b):
    return all(math.isfinite(x) and math.isfinite(y)
               and math.isclose(x, y, abs_tol=5e-10, rel_tol=5e-11)
               for x, y in zip(a, b))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_manifest(manifest, folder):
    require(manifest["status"] ==
            "RESEARCH_CONSTRAINED_LOCALLY_DELAUNAY_NOT_HISTORICAL"
            and manifest["native_cpp_quads_unchanged"] is True
            and manifest["vertices"] == 69
            and manifest["quad_count"] == 42
            and manifest["tri_count"] == 36
            and manifest["quad_tri_seam_edges"] == 20,
            "Wrong M5 provenance or historic status")
    for name, expected in manifest["native_input_sha256"].items():
        require(name in ("tree_regions.csv", "quads_vertex_mean.obj",
                         "quads_area_centroid.obj") and
                sha256(folder / name) == expected,
                "Native C++ provenance checksum mismatch")


def parse_samples(path):
    with path.open(newline="", encoding="ascii") as stream:
        rows = list(csv.DictReader(stream))
    require(len(rows) == 69, "Physical differential sample inventory changed")
    expected_columns = ("id", "u", "v", "x", "y", "z",
                        "qu_x", "qu_y", "qu_z", "qv_x", "qv_y",
                        "qv_z", "jacobian_norm")
    require(tuple(rows[0]) == expected_columns, "Physical CSV schema changed")
    return rows


def audit(uv, quads, triangles, xyz, mapped_quads, mapped_triangles,
          rows, seam, controls=CONTROLS):
    require(len(uv) == len(xyz) == len(rows) == 69,
            "UV/XYZ correspondence count changed")
    require(quads == mapped_quads and triangles == mapped_triangles,
            "The physical lift changed source face IDs or orientation")
    require(len(set(xyz)) == 69, "Physical mapping collapsed distinct UV IDs")
    tangent_errors = []
    normals = []
    for i, ((u, v, z), p, row) in enumerate(zip(uv, xyz, rows)):
        require(z == 0.0 and 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0,
                "Invalid source parametric sample")
        require(int(row["id"]) == i, "Reordered physical sample IDs")
        expected_xyz, expected_du, expected_dv = golden(u, v, controls)
        actual_xyz = tuple(float(row[key]) for key in ("x", "y", "z"))
        actual_du = tuple(float(row[key]) for key in ("qu_x", "qu_y", "qu_z"))
        actual_dv = tuple(float(row[key]) for key in ("qv_x", "qv_y", "qv_z"))
        require(approximately(p, expected_xyz)
                and approximately(p, actual_xyz)
                and approximately(actual_du, expected_du)
                and approximately(actual_dv, expected_dv)
                and approximately((float(row["u"]), float(row["v"])), (u, v)),
                "Physical XYZ or derivatives differ from independent Bernstein")
        normal = cross(actual_du, actual_dv)
        jacobian = magnitude(normal)
        require(normal[2] > 1e-12 and jacobian > 1e-12
                and math.isclose(jacobian, float(row["jacobian_norm"]),
                                 abs_tol=5e-10, rel_tol=5e-11),
                "Invalid physical tangent Jacobian")
        normals.append(normal)
        tangent_errors.append(max(abs(a-b) for a, b in
                                  zip(actual_du + actual_dv,
                                      expected_du + expected_dv)))
    incidence = {}
    for kind, faces in (("QUAD", quads), ("TRI", triangles)):
        for face in faces:
            for a, b in zip(face, face[1:]+face[:1]):
                incidence.setdefault(tuple(sorted((a, b))), []).append(kind)
    physical_seam = sorted(edge for edge, owners in incidence.items()
                           if len(owners) == 2 and owners[0] != owners[1])
    require(physical_seam == seam and len(seam) == 20,
            "QUAD/TRI physical interface differs from native source")
    outer = [edge for edge, owners in incidence.items() if len(owners) == 1]
    require(len(outer) == 16, "Physical outer boundary edge count changed")
    maximum_facet_deviation = 0.0
    for a, b in incidence:
        um = (uv[a][0]+uv[b][0])*0.5
        vm = (uv[a][1]+uv[b][1])*0.5
        expected, _, _ = golden(um, vm)
        midpoint = tuple((x+y)*0.5 for x, y in zip(xyz[a], xyz[b]))
        maximum_facet_deviation = max(
            maximum_facet_deviation, magnitude(vector(midpoint, expected)))
    boundary_midpoint_errors = []
    for a, b in outer:
        require((uv[a][0] == uv[b][0] and uv[a][0] in (0.0, 1.0))
                or (uv[a][1] == uv[b][1] and uv[a][1] in (0.0, 1.0)),
                "Outer edge is not on model parameter boundary")
        # The true boundary is curved. Report rather than falsely require
        # a straight OBJ chord to lie on the exact Bezier boundary curve.
        um = (uv[a][0]+uv[b][0])*0.5
        vm = (uv[a][1]+uv[b][1])*0.5
        true_midpoint, _, _ = golden(um, vm)
        chord_midpoint = tuple((x+y)*0.5 for x, y in zip(xyz[a], xyz[b]))
        boundary_midpoint_errors.append(magnitude(vector(chord_midpoint, true_midpoint)))
    min_alignment = 1.0
    min_projected_twice_area = float("inf")
    subtriangles = 0
    for face in [*quads, *triangles]:
        local = ((face[0], face[1], face[2]),
                 (face[0], face[2], face[3])) if len(face) == 4 else (face,)
        for i, j, k in local:
            area_normal = cross(vector(xyz[i], xyz[j]),
                                vector(xyz[i], xyz[k]))
            u = (uv[i][0]+uv[j][0]+uv[k][0])/3.0
            v = (uv[i][1]+uv[j][1]+uv[k][1])/3.0
            _, du, dv = golden(u, v)
            true_normal = cross(du, dv)
            projected = dot(area_normal, true_normal)
            denom = magnitude(area_normal)*magnitude(true_normal)
            require(math.isfinite(projected) and projected > 1e-12
                    and denom > 1e-12 and area_normal[2] > 1e-12,
                    "Inverted or degenerate lifted physical face")
            min_alignment = min(min_alignment, projected/denom)
            min_projected_twice_area = min(min_projected_twice_area, projected)
            subtriangles += 1
    require(subtriangles == 120, "Missing 120 oriented physical subtriangles")
    require(min_alignment > 0.0 and math.isfinite(maximum_facet_deviation),
            "Nonfinite physical faceting or orientation")
    return {"vertices": len(uv), "native_cpp_quads": len(quads),
            "research_m5_triangles": len(triangles),
            "shared_seam_edges": len(seam), "outer_boundary_edges": len(outer),
            "audited_oriented_subtriangles": subtriangles,
            "minimum_normal_alignment": min_alignment,
            "minimum_projected_twice_area": min_projected_twice_area,
            "maximum_xyz_facet_edge_midpoint_deviation": maximum_facet_deviation,
            "maximum_boundary_chord_midpoint_deviation": max(boundary_midpoint_errors),
            "max_tangent_component_error": max(tangent_errors)}


def refuse(callback, description):
    try:
        callback()
    except (ValueError, AssertionError, KeyError, IndexError, TypeError, OverflowError):
        return
    raise AssertionError(f"Negative mutation not rejected: {description}")


def execute(command, *, success=True):
    outcome = subprocess.run(command, capture_output=True, text=True,
                             timeout=120, check=False)
    if (outcome.returncode == 0) != success:
        raise AssertionError(f"Unexpected command status {outcome.returncode}: "
                             f"{command}\n{outcome.stdout[-1200:]}\n"
                             f"{outcome.stderr[-1200:]}")
    return outcome


def verify_negative_controls(folder, lift_exe, uv, quads, triangles, xyz,
                             rows, seam, source_path):
    controls = 0
    # Independent map, connectivity, differential, control-net and source claims.
    damaged_xyz = list(xyz)
    damaged_xyz[1] = (xyz[1][0]+0.02, xyz[1][1], xyz[1][2])
    refuse(lambda: audit(uv, quads, triangles, damaged_xyz,
                         quads, triangles, rows, seam),
           "perturbed mapped XYZ")
    controls += 1
    reversed_triangles = [triangles[0][::-1], *triangles[1:]]
    refuse(lambda: validate(uv, quads, reversed_triangles),
           "reversed source TRI")
    controls += 1
    missing_seam = [triangles[0][:-1]+(triangles[0][0],), *triangles[1:]]
    refuse(lambda: validate(uv, quads, missing_seam),
           "corrupted TRI endpoint")
    controls += 1
    changed_rows = copy.deepcopy(rows)
    changed_rows[0]["qu_x"] = str(float(rows[0]["qu_x"]) + 0.2)
    refuse(lambda: audit(uv, quads, triangles, xyz, quads, triangles,
                         changed_rows, seam), "false derivative")
    controls += 1
    changed_grid = [[list(p) for p in row] for row in CONTROLS]
    changed_grid[1][1][2] += 0.5
    refuse(lambda: audit(uv, quads, triangles, xyz, quads, triangles,
                         rows, seam, changed_grid), "changed control grid")
    controls += 1
    manifest = json.loads((folder / "research_local_delaunay_manifest.json").read_text())
    manifest["native_input_sha256"]["tree_regions.csv"] = "0"*64
    refuse(lambda: require_manifest(manifest, folder), "incorrect source checksum")
    controls += 1
    lines = source_path.read_text(encoding="ascii").splitlines()
    index = next(i for i, line in enumerate(lines) if line.startswith("v "))
    face_index = next(i for i, line in enumerate(lines) if line.startswith("f "))
    mutation_lines = [
        ("outside_uv", {index: "v 1.1 0.4 0"}),
        ("nonfinite_uv", {index: "v nan 0.4 0"}),
        ("invalid_face_index", {face_index: "f 1 2 3 9000"}),
        ("reversed_quad", {
            face_index: "f " + " ".join(reversed(lines[face_index].split()[1:]))}),
        ("invalid_group", {
            next(i for i, line in enumerate(lines)
                 if line.startswith("g QUAD_")): "g INVALID_GROUP"}),
    ]
    for name, edits in mutation_lines:
        damaged = list(lines)
        for line_number, value in edits.items():
            damaged[line_number] = value
        bad_path = folder / f"negative_m4_{name}.obj"
        bad_path.write_text("\n".join(damaged)+"\n", encoding="ascii")
        execute([str(lift_exe), str(bad_path),
                 str(folder / "negative_output.obj"),
                 str(folder / "negative_samples.csv")], success=False)
        controls += 1
    require(controls == 11, "Physical research negative inventory weakened")
    return controls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree-exe", type=Path, required=True)
    parser.add_argument("--lift-exe", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    folder = args.directory.resolve()
    # The path is a dedicated CMake build-tree output, not a source directory.
    folder.mkdir(parents=True, exist_ok=True)
    tree = args.tree_exe.resolve()
    lift = args.lift_exe.resolve()
    execute([str(tree), str(folder)])
    quad_manifest = json.loads((folder / "manifest.json").read_text())
    require(quad_manifest["source"] == "real_APMesh_CXX_Quadtree_fixture"
            and quad_manifest["mean_quads"] == quad_manifest["centroid_quads"] == 42,
            "Source is not native C++ Quadtree")
    root = Path(__file__).resolve().parent
    for script in ("test_m5_exterior_interface.py", "test_m5_constrained_delaunay.py"):
        execute([sys.executable, str(root / script), "--directory", str(folder)])
    m5 = json.loads((folder / "research_local_delaunay_manifest.json").read_text())
    require_manifest(m5, folder)
    results = []
    all_negative = 0
    for mode in ("vertex_mean", "area_centroid"):
        source = folder / f"hybrid_research_local_delaunay_{mode}.obj"
        original = folder / f"quads_{mode}.obj"
        uv, quads, triangles = read_obj(source)
        native, original_quads, native_triangles = read_obj(original)
        require(len(native) == 53 and uv[:53] == native and
                quads == original_quads and not native_triangles,
                "Source native QUAD geometry was altered")
        seam = validate(uv, quads, triangles)
        lifted = folder / f"physical_model_hybrid_{mode}.obj"
        sample_path = folder / f"physical_model_hybrid_{mode}.csv"
        execute([str(lift), str(source), str(lifted), str(sample_path)])
        xyz, mapped_quads, mapped_triangles = read_obj(lifted)
        rows = parse_samples(sample_path)
        quality = audit(uv, quads, triangles, xyz, mapped_quads,
                        mapped_triangles, rows, seam)
        negative = verify_negative_controls(folder, lift, uv, quads,
                                            triangles, xyz, rows, seam, source)
        all_negative += negative
        results.append({"center_rule": mode,
                        "input_native_sha256": sha256(original),
                        "input_hybrid_uv_sha256": sha256(source),
                        "physical_obj_sha256": sha256(lifted),
                        "physical_samples_sha256": sha256(sample_path),
                        "metrics": quality, "negative_mutations_rejected": negative})
    require(all_negative == 22, "Did not execute both physical negative suites")
    manifest = {
        "schema": 1,
        "status": "REAL_BUILTIN_APMESH_BEZIER_RESEARCH_HYBRID_NOT_PRODUCTION",
        "model": "Models3d::ModelCurvaBezier",
        "source_tree": "actual native C++ 19-leaf Quadtree",
        "exterior_algorithm": "M5 research constrained local Lawson NOT historical 1993",
        "imported_cad_model_tested": False,
        "four_node_physical_element_created": False,
        "production_hybrid_enabled": False,
        "centroid_historically_approved": False,
        "historical_delaunay_and_contraction_complete": False,
        "negative_controls": all_negative,
        "outcomes": results,
    }
    (folder / "physical_model_hybrid_manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print("m4_real_builtin_bezier=ok native_cpp_quad=42 m5_research_tri=36 "
          "uv_xyz_ids=69 seam=20 subtriangles=120 controls=22 "
          "NOT_imported_CAD NOT_historical_1993 NOT_production")


if __name__ == "__main__":
    main()
