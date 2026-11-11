#!/usr/bin/env python3
"""Audited two-sheet physical QUAD/TRI candidates from actual native C++ UV.

The per-patch OBJs are research witnesses, not an owned global mesh.  The
exterior M5 Lawson implementation and both centroid rules remain experimental.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

from test_m4_real_model_hybrid import require_manifest
from test_m5_constrained_delaunay import edges, read_obj, require, validate

BEND = 0.18
XYZ_TOLERANCE = 5e-10
CSV_COLUMNS = (
    "patch", "id", "u", "v", "x", "y", "z",
    "qu_x", "qu_y", "qu_z", "qv_x", "qv_y", "qv_z", "jacobian_norm",
)
MODES = ("aligned", "reparameterized")
CENTERS = ("vertex_mean", "area_centroid")


def execute(args: list[str], success: bool = True) -> str:
    completed = subprocess.run(args, capture_output=True, text=True,
                               timeout=160, check=False)
    require((completed.returncode == 0) == success,
            f"Unexpected command exit {completed.returncode}: {args}\n"
            f"{completed.stdout[-1400:]}\n{completed.stderr[-1400:]}")
    return completed.stdout


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a: float, b: float) -> bool:
    return math.isfinite(a) and math.isfinite(b) and math.isclose(
        a, b, rel_tol=5e-11, abs_tol=XYZ_TOLERANCE)


def close_xyz(a, b) -> bool:
    return len(a) == len(b) and all(close(x, y) for x, y in zip(a, b))


def analytic(patch: int, u: float, v: float, mode: str):
    reverse = mode == "reparameterized" and patch == 1
    x = u if patch == 0 else (2.0 - u if reverse else 1.0 + u)
    y = 1.0 - v if reverse else v
    sx, sy = (-1.0, -1.0) if reverse else (1.0, 1.0)
    return (
        (x, y, BEND * y * (1.0 - y)),
        (sx, 0.0, 0.0),
        (0.0, sy, BEND * (1.0 - 2.0 * y) * sy),
    )


def write_uv_csv(path: Path, uv) -> None:
    with path.open("w", newline="", encoding="ascii") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("id", "u", "v"))
        for identifier, (u, v, z) in enumerate(uv):
            require(z == 0.0, "Native source UV has an unexpected Z ordinate")
            writer.writerow((identifier, format(u, ".17g"), format(v, ".17g")))


def read_samples(path: Path, uv, mode: str):
    with path.open(newline="", encoding="ascii") as stream:
        rows = list(csv.DictReader(stream))
    require(len(rows) == 138 and tuple(rows[0]) == CSV_COLUMNS,
            "Production sampler schema/count changed")
    xyz = [[], []]
    for sequence, row in enumerate(rows):
        patch, identifier = divmod(sequence, 69)
        require(row["patch"] == str(patch) and
                row["id"] == str(identifier),
                "A production physical sample was reordered")
        u, v, z = uv[identifier]
        require(close(float(row["u"]), u) and
                close(float(row["v"]), v) and z == 0.0,
                "Physical sampler changed the native source UV identity")
        position, du, dv = analytic(patch, u, v, mode)
        mapped = tuple(float(row[k]) for k in ("x", "y", "z"))
        got_du = tuple(float(row[k]) for k in ("qu_x", "qu_y", "qu_z"))
        got_dv = tuple(float(row[k]) for k in ("qv_x", "qv_y", "qv_z"))
        require(close_xyz(mapped, position) and
                close_xyz(got_du, du) and close_xyz(got_dv, dv),
                "Physical XYZ or derivatives differ from independent golden")
        cross = (got_du[1]*got_dv[2] - got_du[2]*got_dv[1],
                 got_du[2]*got_dv[0] - got_du[0]*got_dv[2],
                 got_du[0]*got_dv[1] - got_du[1]*got_dv[0])
        jac = math.sqrt(sum(x*x for x in cross))
        require(cross[2] > 1e-12 and
                close(jac, float(row["jacobian_norm"])),
                "Physical patch Jacobian or chart orientation incorrect")
        xyz[patch].append(mapped)
    require(all(len(p) == len(set(p)) == 69 for p in xyz),
            "Separate patch-local physical vertex identities have collapsed")
    return xyz


def write_obj(path: Path, xyz, quads, triangles, patch: int):
    with path.open("w", encoding="ascii", newline="\n") as stream:
        stream.write("# Real PatchReader + native C++ Quadtree + M5 Lawson\n")
        stream.write("# RESEARCH PER PATCH; NOT a welded/owned or historical mesh\n")
        stream.write(f"# patch_local_id={patch}; physical geometry\n")
        for x, y, z in xyz:
            stream.write(f"v {x:.17g} {y:.17g} {z:.17g}\n")
        for group, faces in (("QUAD_native_cpp", quads),
                             ("TRI_M5_experimental", triangles)):
            stream.write(f"g {group}\n")
            for face in faces:
                stream.write("f " + " ".join(str(i+1) for i in face) + "\n")


def verify_obj(path: Path, original_xyz, quads, triangles):
    xyz, read_quads, read_triangles = read_obj(path)
    require(len(xyz) == len(original_xyz) == 69 and
            read_quads == quads and read_triangles == triangles and
            all(close_xyz(a, b) for a, b in zip(xyz, original_xyz)),
            "Physical OBJ altered native QUAD/TRI faces or mapped XYZ")
    subtriangle_count = 0
    for face in list(quads) + list(triangles):
        sets = ((face[:3], (face[0], face[2], face[3]))
                if len(face) == 4 else (face,))
        for a, b, c in sets:
            pa, pb, pc = xyz[a], xyz[b], xyz[c]
            oriented = ((pb[0]-pa[0])*(pc[1]-pa[1]) -
                        (pb[1]-pa[1])*(pc[0]-pa[0]))
            require(oriented > 1e-12,
                    "Physical QUAD subtriangle or TRI has reversed/zero XY area")
            subtriangle_count += 1
    require(subtriangle_count == 120,
            "The native hybrid's two-subtriangle QUAD orientation changed")


def coordinate_key(point):
    return tuple(round(value, 10) for value in point)


def physical_edge_key(a, b):
    return tuple(sorted((coordinate_key(a), coordinate_key(b))))


def audit_boundary(uv, quads, triangles, xyz, mode: str):
    all_edges = edges(quads + triangles)
    outer = {edge: owners[0][1:] for edge, owners in all_edges.items()
             if len(owners) == 1}
    require(len(outer) == 16, "Native mixed UV mesh outer contour changed")
    left = [directed for (a, b), directed in outer.items()
            if uv[a][0] == uv[b][0] == 1.0]
    right_u = 1.0 if mode == "reparameterized" else 0.0
    right = [directed for (a, b), directed in outer.items()
             if uv[a][0] == uv[b][0] == right_u]
    require(len(left) == len(right) == 4,
            "No complete four-edge shared patch-to-patch seam")
    lmap = {physical_edge_key(xyz[0][a], xyz[0][b]):
            (xyz[0][a], xyz[0][b], a, b) for a, b in left}
    rmap = {physical_edge_key(xyz[1][a], xyz[1][b]):
            (xyz[1][a], xyz[1][b], a, b) for a, b in right}
    require(len(lmap) == len(rmap) == 4 and set(lmap) == set(rmap),
            "Physical interpatch seam is cracked, unsynchronized or duplicated")
    left_ids, right_ids = set(), set()
    for key in lmap:
        left_a, left_b, a, b = lmap[key]
        right_a, right_b, c, d = rmap[key]
        left_ids.update((a, b))
        right_ids.update((c, d))
        require(close_xyz(left_a, right_b) and
                close_xyz(left_b, right_a),
                "Shared physical edge lacks opposite boundary orientation")
    require(len(left_ids) == len(right_ids) == 5,
            "Five independent seam vertex locations are required")
    lpoints = {coordinate_key(xyz[0][i]) for i in left_ids}
    rpoints = {coordinate_key(xyz[1][i]) for i in right_ids}
    require(len(lpoints) == len(rpoints) == 5 and lpoints == rpoints,
            "The virtual global node identity is not one-to-one on the seam")
    return {"shared_curve_edges": 4,
            "shared_seam_vertices": 5,
            "per_patch_outer_edges": 16,
            "virtual_combined_unique_vertices": 133,
            "patches_have_distinct_node_ownership": True,
            "shared_nodes_actually_welded": False}


def rejects(func, description):
    try:
        func()
    except (ValueError, AssertionError):
        return 1
    raise ValueError(f"Invalid boundary/mesh mutation accepted: {description}")


def audit_candidates(folder: Path, mode: str, center: str, uv,
                     quads, triangles, sampler: Path, uv_csv: Path):
    model = folder / f"pair_{mode}.bp"
    output_csv = folder / f"pairwise_{mode}_{center}.csv"
    execute([str(sampler), str(model), str(uv_csv),
             str(output_csv), mode])
    mapped = read_samples(output_csv, uv, mode)
    objects = []
    for patch in range(2):
        file = folder / f"pairwise_{mode}_{center}_patch_{patch}.obj"
        write_obj(file, mapped[patch], quads, triangles, patch)
        verify_obj(file, mapped[patch], quads, triangles)
        objects.append(file)
    seam = audit_boundary(uv, quads, triangles, mapped, mode)
    # Both experimental centroid rules must independently retain the exact
    # same native outer-boundary geometry, regardless of their interior points.
    shared_sites = sorted({
        coordinate_key(mapped[0][index])
        for index, (u, _, _) in enumerate(uv) if u == 1.0
    })
    require(len(shared_sites) == 5,
            "Unexpected shared physical boundary vertex inventory")

    negatives = 0
    # A modified physical sample must be rejected independently of the C++ producer.
    with output_csv.open(newline="", encoding="ascii") as stream:
        rows = list(csv.DictReader(stream))
    damaged = copy.deepcopy(rows)
    damaged[70]["z"] = str(float(damaged[70]["z"]) + 0.125)
    corrupted = folder / f"negative_{mode}_{center}_physical.csv"
    with corrupted.open("w", newline="", encoding="ascii") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS,
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(damaged)
    negatives += rejects(lambda: read_samples(corrupted, uv, mode),
                         "altered model XYZ")

    # A face reversal must never preserve the native source topology oracle.
    file_lines = objects[0].read_text(encoding="ascii").splitlines()
    first_face = next(i for i, line in enumerate(file_lines)
                      if line.startswith("f "))
    tokens = file_lines[first_face].split()
    tokens[1], tokens[2] = tokens[2], tokens[1]
    file_lines[first_face] = " ".join(tokens)
    bad_obj = folder / f"negative_{mode}_{center}_face.obj"
    bad_obj.write_text("\n".join(file_lines) + "\n", encoding="ascii")
    negatives += rejects(lambda: verify_obj(bad_obj, mapped[0],
                                            quads, triangles), "inverted face")

    # Independently reject an otherwise valid topology with a cracked seam.
    wrong = copy.deepcopy(mapped)
    seam_id = next(i for i, v in enumerate(uv)
                   if v[0] == (1.0 if mode == "reparameterized" else 0.0))
    x, y, z = wrong[1][seam_id]
    wrong[1][seam_id] = (x+0.025, y, z)
    negatives += rejects(lambda: audit_boundary(uv, quads, triangles,
                                                wrong, mode), "cracked seam")
    require(negatives == 3, "Not all three independent mutations were rejected")
    return {"mode": mode, "center_rule": center,
            "native_uv_sha256": sha256(folder /
                f"hybrid_research_local_delaunay_{center}.obj"),
            "physical_samples_sha256": sha256(output_csv),
            "physical_obj_sha256": {p.name: sha256(p) for p in objects},
            "per_patch_nodes": 69, "per_patch_quads": 42,
            "per_patch_triangles": 36, "per_patch_subtriangles": 120,
            "seam": seam,
            "shared_seam_coordinates": shared_sites,
            "negative_output_mutations_rejected": negatives}


def probe_input_rejections(folder: Path, sampler: Path, valid_uv: Path):
    negative_models = (
        "displaced_seam.bp", "reversed_chart_normal.bp",
        "triple_incidence.bp",
    )
    rejected = 0
    for name in negative_models:
        execute([str(sampler), str(folder / name), str(valid_uv),
                 str(folder / "negative_model_samples.csv"), "aligned"],
                success=False)
        rejected += 1
    raw = valid_uv.read_text(encoding="ascii").splitlines()
    require(len(raw) == 70 and raw[0] == "id,u,v",
            "Expected deterministic 69-entry UV CSV")
    bad_variants = {
        "missing_vertex": raw[:-1],
        "nonfinite_uv": raw[:1] + ["0,nan,0.5"] + raw[2:],
        "wrong_id": raw[:1] + ["99,0.0,0.0"] + raw[2:],
        "duplicated_uv": raw[:2] + [raw[2].split(",")[0] + "," +
                                    ",".join(raw[1].split(",")[1:])] + raw[3:],
    }
    for name, lines in bad_variants.items():
        bad = folder / f"negative_native_uv_{name}.csv"
        bad.write_text("\n".join(lines) + "\n", encoding="ascii")
        execute([str(sampler), str(folder / "pair_aligned.bp"), str(bad),
                 str(folder / "negative_uv_samples.csv"), "aligned"],
                success=False)
        rejected += 1
    require(rejected == 7, "Not all negative input controls were executed")
    return rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree-exe", type=Path, required=True)
    parser.add_argument("--fixture-exe", type=Path, required=True)
    parser.add_argument("--sampler-exe", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    folder = args.directory.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parent

    # Existing independent M5 script consumes C++ 19-leaf Quadtree outputs.
    execute([str(args.tree_exe.resolve()), str(folder)])
    source_manifest = json.loads((folder / "manifest.json").read_text())
    require(source_manifest["source"] == "real_APMesh_CXX_Quadtree_fixture"
            and source_manifest["mean_quads"] == 42,
            "Input is not the actual native source C++ Quadtree")
    for script in ("test_m5_exterior_interface.py",
                   "test_m5_constrained_delaunay.py"):
        execute([sys.executable, str(root / script),
                 "--directory", str(folder)])
    m5 = json.loads((folder / "research_local_delaunay_manifest.json").read_text())
    require_manifest(m5, folder)

    fixture = args.fixture_exe.resolve()
    sampler = args.sampler_exe.resolve()
    require("quad_m4_pairwise_boundary=ok" in
            execute([str(fixture), str(folder)]),
            "Prior real PatchReader pairwise model preflight failed")

    results = []
    negative_inputs = 0
    for center in CENTERS:
        source = folder / f"hybrid_research_local_delaunay_{center}.obj"
        original = folder / f"quads_{center}.obj"
        uv, quads, triangles = read_obj(source)
        native, native_quads, native_tris = read_obj(original)
        require(len(native) == 53 and uv[:53] == native and
                quads == native_quads and not native_tris,
                "Actual C++ 42 QUAD source changed during physical candidate lift")
        require(len(validate(uv, quads, triangles)) == 20,
                "Native QUAD/TRI interior seam lost its 20 edges")
        uv_csv = folder / f"native_uv_{center}.csv"
        write_uv_csv(uv_csv, uv)
        for mode in MODES:
            results.append(audit_candidates(folder, mode, center, uv,
                                            quads, triangles, sampler, uv_csv))
        if center == CENTERS[0]:
            negative_inputs += probe_input_rejections(folder, sampler, uv_csv)

    require(len(results) == 4 and
            sum(x["negative_output_mutations_rejected"] for x in results) == 12
            and negative_inputs == 7,
            "Did not execute all physical model and mutation controls")
    for mode in MODES:
        witnesses = [x for x in results if x["mode"] == mode]
        require(len(witnesses) == 2 and
                witnesses[0]["shared_seam_coordinates"] ==
                witnesses[1]["shared_seam_coordinates"],
                "An experimental centroid rule altered shared physical boundary sites")
    manifest = {
        "schema": 1,
        "status": "TWO_PATCH_LOCAL_PHYSICAL_CANDIDATES_NO_GLOBAL_WELD",
        "source": "actual_CPP_Quadtree_M5_Lawson_and_production_PatchReader",
        "models": "temporary analytic Bezier .bp (not Eistute/Book)",
        "two_patch_model": True,
        "original_source_quads_per_patch": 42,
        "experimental_exterior_tri_per_patch": 36,
        "physical_vertices_per_patch": 69,
        "center_rules_scientifically_approved": False,
        "model_wide_hybrid": False,
        "quad_elements_globally_owned": False,
        "shared_seam_globally_welded": False,
        "historical_1993_insertion_and_contraction": False,
        "all_quad_production_enabled": False,
        "source_tree_sha256": sha256(folder / "tree_regions.csv"),
        "negative_input_controls": negative_inputs,
        "negative_output_controls": 12,
        "outcomes": results,
    }
    evidence = folder / "pairwise_physical_manifest.json"
    evidence.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n",
                        encoding="utf-8")
    print("m4_pairwise_physical=ok real_cpp_quad=42 experimental_m5_tri=36 "
          "per_patch=69 pairs=2 center_rules=2 interfaces=4x4 "
          "negative_inputs=7 negative_outputs=12 global_welding=NO "
          "NOT_Eistute_Book NOT_1993 NOT_production\n")


if __name__ == "__main__":
    main()
