#!/usr/bin/env python3
"""Research-only real .bp patch physical witnesses, with NO global mesh welding.

Source UV QUADs are from the actual native C++ Quadtree; exterior TRI are
the unchanged experimental M5 Lawson candidate. Production PatchReader and
PatchBezier supply physical samples, checked independently via Bernstein.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import zipfile

from audit_model_catalog import INPUT_MODELS, UV_EDGES, basis, edge_key, parse_bp
from test_m4_pairwise_physical_candidates import write_uv_csv
from test_m4_real_model_hybrid import require_manifest
from test_m5_constrained_delaunay import edges, read_obj, require, validate

CENTER_RULES = ("vertex_mean", "area_centroid")
EXPECTED = {
    "Eistute": (4, 64, 12, 0, 1, 4),
    "Book": (28, 340, 84, 0, 1, 28),
    "Ribbed Bracket": (13, 125, 6, 17, 4, 3),
}
FIELDS = ("patch", "id", "u", "v", "x", "y", "z", "qu_x", "qu_y",
          "qu_z", "qv_x", "qv_y", "qv_z", "jacobian_norm")
# These are topology/diagnostic thresholds, NOT scientific meshing tolerances.
XYZ_ABS = 2e-8
XYZ_REL = 2e-10
SEAM_DIAGNOSTIC_THRESHOLD = 1e-7


def run(args: list[str], success: bool = True) -> str:
    completed = subprocess.run(args, text=True, capture_output=True,
                               timeout=180, check=False)
    require((completed.returncode == 0) == success,
            f"Unexpected exit {completed.returncode}: {args}\n"
            f"{completed.stdout[-1600:]}\n{completed.stderr[-1600:]}")
    return completed.stdout


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def approximately(a, b, *, absolute=XYZ_ABS):
    return len(a) == len(b) and all(
        math.isfinite(x) and math.isfinite(y) and
        math.isclose(x, y, rel_tol=XYZ_REL, abs_tol=absolute)
        for x, y in zip(a, b))


def bernstein(controls, u, v):
    bu, du = basis(u)
    bv, dv = basis(v)
    out = []
    for wu, wv in ((bu, bv), (du, bv), (bu, dv)):
        out.append(tuple(sum(wu[i]*wv[j]*controls[4*j+i][axis]
                             for i in range(4) for j in range(4))
                         for axis in range(3)))
    return out


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1],
            a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def curve_groups(vertices, patches):
    groups = defaultdict(list)
    for pid, indices in enumerate(patches):
        for side, corners in enumerate(UV_EDGES):
            key = edge_key([vertices[indices[k]] for k in corners])
            groups[key].append((pid, side))
    return sorted(tuple(sorted(items)) for items in groups.values())


def incidence_from_cpp(path: Path, number: int):
    with path.open(newline="", encoding="ascii") as stream:
        rows = list(csv.DictReader(stream))
    require(len(rows) == 4 * number and
            tuple(rows[0]) == ("patch", "side", "curve_id", "reversed", "degree"),
            "Real production incidence CSV malformed")
    groups = defaultdict(list)
    orientations = {}
    for index, row in enumerate(rows):
        pid, side = divmod(index, 4)
        require(int(row["patch"]) == pid and int(row["side"]) == side,
                "Production patch/edge incidence ordering lost")
        group = int(row["curve_id"])
        require(group >= 0 and row["reversed"] in ("0", "1"),
                "Invalid physical curve identity or direction")
        groups[group].append((pid, side))
        orientations[(pid, side)] = row["reversed"] == "1"
    require(set(groups) == set(range(len(groups))),
            "Source curve identities are not dense per-model IDs")
    for row in rows:
        require(int(row["degree"]) == len(groups[int(row["curve_id"])]),
                "Reported physical curve degree is inconsistent")
    return sorted(tuple(sorted(items)) for items in groups.values()), orientations


def read_samples(path: Path, uv, controls):
    number = len(controls)
    with path.open(newline="", encoding="ascii") as stream:
        rows = list(csv.DictReader(stream))
    require(len(rows) == number * 69 and
            tuple(rows[0]) == FIELDS,
            "Real model physical sample inventory or schema changed")
    output = []
    patch_metrics = []
    for pid in range(number):
        points = []
        jacobians = []
        normals = []
        for vid, (u, v, z) in enumerate(uv):
            row = rows[pid*69+vid]
            require(row["patch"] == str(pid) and row["id"] == str(vid),
                    "Real model PatchReader sample was reordered")
            require(approximately((float(row["u"]), float(row["v"]), z),
                                  (u, v, 0.0)),
                    "Real native C++ UV source changed before surface lifting")
            xyz, du, dv = bernstein(controls[pid], u, v)
            actual_xyz = tuple(float(row[k]) for k in ("x", "y", "z"))
            actual_du = tuple(float(row[k]) for k in ("qu_x", "qu_y", "qu_z"))
            actual_dv = tuple(float(row[k]) for k in ("qv_x", "qv_y", "qv_z"))
            require(approximately(actual_xyz, xyz) and
                    approximately(actual_du, du) and
                    approximately(actual_dv, dv),
                    f"Production Bezier disagrees with independent Bernstein:"
                    f" patch={pid} vertex={vid}")
            jacobian = norm(cross(actual_du, actual_dv))
            require(math.isfinite(jacobian) and
                    approximately((jacobian,),
                                  (float(row["jacobian_norm"]),), absolute=5e-7),
                    "Physical tangent Jacobian disagrees with independent result")
            jacobians.append(jacobian)
            normals.append(cross(actual_du, actual_dv))
            points.append(actual_xyz)
        require(len(points) == 69, "Patch physical ID count changed")
        output.append(points)
        center = cross(bernstein(controls[pid], .5, .5)[1],
                       bernstein(controls[pid], .5, .5)[2])
        # Local normal rotations are diagnostic; no fixed world-Z assumption.
        opposite = sum(dot(n, center) < -1e-10 for n in normals)
        patch_metrics.append({
            "patch": pid,
            "min_sampled_jacobian": min(jacobians),
            "max_sampled_jacobian": max(jacobians),
            "near_zero_jacobian_sample_count": sum(x <= 1e-12 for x in jacobians),
            "sampled_normals_opposite_center_count": opposite,
        })
    return output, patch_metrics


def boundary_coordinates(uv, mapped, pid, side, reversed_incidence):
    sites = []
    for i, (u, v, _) in enumerate(uv):
        on_side = ((side == 0 and v == 0.0) or
                   (side == 1 and u == 1.0) or
                   (side == 2 and v == 1.0) or
                   (side == 3 and u == 0.0))
        if not on_side:
            continue
        local_t = u if side in (0, 2) else v
        canonical_t = 1.0 - local_t if reversed_incidence else local_t
        sites.append((round(canonical_t, 10), mapped[pid][i]))
    sites.sort(key=lambda item: item[0])
    require(len(sites) == 5 and len({t for t, _ in sites}) == 5,
            "Shared curve must contain five native boundary sites per owner")
    return sites


def incidence_diagnostic(uv, mapped, groups, directions):
    shared = []
    worst = 0.0
    mismatched = 0
    pairwise = high_valence = 0
    for owners in groups:
        if len(owners) == 1:
            continue
        pairwise += len(owners) == 2
        high_valence += len(owners) > 2
        first = boundary_coordinates(uv, mapped, *owners[0],
                                     directions[owners[0]])
        group_error = 0.0
        for owner in owners[1:]:
            other = boundary_coordinates(uv, mapped, *owner,
                                         directions[owner])
            require([t for t, _ in first] == [t for t, _ in other],
                    "Two real patch incidences disagree on native seam parameters")
            for (_, a), (_, b) in zip(first, other):
                gap = math.dist(a, b)
                require(math.isfinite(gap),
                        "Nonfinite real model shared-edge physical gap")
                group_error = max(group_error, gap)
        worst = max(worst, group_error)
        mismatched += group_error > SEAM_DIAGNOSTIC_THRESHOLD
        shared.append({"degree": len(owners),
                       "incidences": [list(owner) for owner in owners],
                       "maximum_sampled_seam_gap": group_error,
                       "requires_explicit_sheet_policy": len(owners) > 2})
    return {"paired_shared_control_curves": pairwise,
            "high_valence_control_curves": high_valence,
            "maximum_sampled_seam_gap": worst,
            "curves_with_gaps_over_diagnostic_1e_7": mismatched,
            "seam_points_physically_welded": False,
            "sampled_groups": shared}


def write_obj(path: Path, xyz, quads, triangles, pid):
    with path.open("w", encoding="ascii", newline="\n") as output:
        output.write("# Research-only per-patch physical QUAD/TRI candidate\n")
        output.write("# Real BP PatchReader; native C++ Quadtree + M5 experimental Lawson\n")
        output.write("# NOT model-wide/welded/1993 historical/production\n")
        output.write(f"# patch_index={pid}\n")
        for x, y, z in xyz:
            output.write(f"v {x:.17g} {y:.17g} {z:.17g}\n")
        for kind, faces in (("QUAD_native_cpp", quads),
                            ("TRI_M5_research", triangles)):
            output.write(f"g {kind}\n")
            for face in faces:
                output.write("f " + " ".join(str(i + 1) for i in face) + "\n")
    recovered, quad, tri = read_obj(path)
    require(len(recovered) == 69 and quad == quads and tri == triangles
            and all(approximately(a, b) for a, b in zip(recovered, xyz)),
            "Research candidate OBJ changed native QUAD/TRI IDs")


def facet_diagnostic(uv, xyz, quads, triangles, control):
    inverse = zero = 0
    min_alignment = 1.0
    for face in list(quads) + list(triangles):
        tris = ((face[:3], (face[0], face[2], face[3]))
                if len(face) == 4 else (face,))
        for ids in tris:
            p, q, r = (xyz[i] for i in ids)
            a = tuple(q[i] - p[i] for i in range(3))
            b = tuple(r[i] - p[i] for i in range(3))
            n = cross(a, b)
            u = sum(uv[k][0] for k in ids)/3.0
            v = sum(uv[k][1] for k in ids)/3.0
            _, du, dv = bernstein(control, u, v)
            differential = cross(du, dv)
            mag = norm(n)*norm(differential)
            if mag <= 1e-14:
                zero += 1
            else:
                alignment = dot(n, differential)/mag
                min_alignment = min(min_alignment, alignment)
                inverse += alignment <= 0.0
    return {"oriented_subtriangles_examined": 120,
            "near_degenerate_facet_samples": zero,
            "nonpositive_local_normal_alignment": inverse,
            "minimum_sampled_cos_alignment":
                min_alignment if min_alignment != 1.0 or zero == 0 else None,
            "orientation_diagnostic_only": True}


def reject_mutations(folder, first_model, native_uv_csv, sampler, model_dir,
                     sample_rows_path, incidence_path, original_groups,
                     original_uv, original_controls, original_sample,
                     original_directed):
    total = 0
    # Preserve the same model identity and demonstrate that malformed BP
    # input cannot be passed to the production loader.
    model = first_model.read_text(encoding="utf-8")
    modified = model.replace("v ", "v NaN ", 1)
    invalid_bp = folder / "negative_external_invalid.bp"
    invalid_bp.write_text(modified, encoding="utf-8")
    run([str(sampler), str(invalid_bp), str(native_uv_csv),
         str(folder / "bad_output.csv"), str(folder / "bad_curves.csv"), "4"],
        success=False)
    total += 1

    # The independent scientific oracle must reject a changed physical sample.
    with sample_rows_path.open(newline="", encoding="ascii") as stream:
        rows = list(csv.DictReader(stream))
    rows[0]["x"] = str(float(rows[0]["x"]) + 0.25)
    broken_sample = folder / "negative_external_sample.csv"
    with broken_sample.open("w", newline="", encoding="ascii") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    try:
        read_samples(broken_sample, original_uv, original_controls)
    except ValueError:
        total += 1
    else:
        raise AssertionError("Changed actual physical XYZ escaped Bernstein audit")

    # The production curve registry must match the independent control net.
    with incidence_path.open(newline="", encoding="ascii") as stream:
        curve_rows = list(csv.DictReader(stream))
    curve_rows[0]["curve_id"] = str(max(int(x["curve_id"])
                                     for x in curve_rows) + 1)
    broken_curve = folder / "negative_external_incidence.csv"
    with broken_curve.open("w", newline="", encoding="ascii") as output:
        writer = csv.DictWriter(output, fieldnames=tuple(curve_rows[0]),
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(curve_rows)
    try:
        candidate_groups, _ = incidence_from_cpp(broken_curve, 4)
        require(candidate_groups == original_groups,
                "Mutated curve registry differs from independent control graph")
    except ValueError:
        total += 1
    else:
        raise AssertionError("Changed source incidence identity escaped audit")

    # The edge-specific oracle must report, not silently weld, a large crack.
    corrupted = [list(p) for p in original_sample]
    owners = next(group for group in original_groups if len(group) > 1)
    patch, side = owners[-1]
    native_id = next(i for i, (u, v, _) in enumerate(original_uv)
                     if ((side == 0 and v == 0.0) or
                         (side == 1 and u == 1.0) or
                         (side == 2 and v == 1.0) or
                         (side == 3 and u == 0.0)))
    points = list(corrupted[patch])
    before = points[native_id]
    points[native_id] = (before[0] + 1.0, before[1], before[2])
    corrupted[patch] = points
    measured = incidence_diagnostic(original_uv, corrupted,
                                    original_groups, original_directed)
    require(measured["maximum_sampled_seam_gap"] >
            SEAM_DIAGNOSTIC_THRESHOLD,
            "Cracked shared curve went unnoticed")
    total += 1
    require(total == 4, "Incomplete external model negative mutation suite")
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--tree-exe", type=Path, required=True)
    parser.add_argument("--sampler-exe", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    folder = args.directory.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    scripts = Path(__file__).resolve().parent
    native_exe, sampler_exe = args.tree_exe.resolve(), args.sampler_exe.resolve()
    run([str(native_exe), str(folder)])
    native_manifest = json.loads((folder / "manifest.json").read_text())
    require(native_manifest["source"] == "real_APMesh_CXX_Quadtree_fixture"
            and native_manifest["mean_quads"] == 42,
            "Actual C++ Quadtree source was not produced")
    for script in ("test_m5_exterior_interface.py",
                   "test_m5_constrained_delaunay.py"):
        run([sys.executable, str(scripts/script), "--directory", str(folder)])
    m5 = json.loads((folder / "research_local_delaunay_manifest.json").read_text())
    require_manifest(m5, folder)

    results = []
    archived = []
    negatives = 0
    for center in CENTER_RULES:
        source_obj = folder / f"hybrid_research_local_delaunay_{center}.obj"
        source_quad = folder / f"quads_{center}.obj"
        uv, quads, triangles = read_obj(source_obj)
        native_uv, native_quads, native_tri = read_obj(source_quad)
        require(len(uv) == 69 and len(native_uv) == 53
                and uv[:53] == native_uv and quads == native_quads
                and not native_tri and len(validate(uv, quads, triangles)) == 20,
                "Physical candidates lost native 42 QUAD/36 M5 TRI provenance")
        uv_csv = folder / f"native_uv_external_{center}.csv"
        write_uv_csv(uv_csv, uv)
        archived.append(uv_csv)
        for name, (relative, count) in INPUT_MODELS.items():
            model_path = root / relative
            controls, patches = parse_bp(model_path.read_text(encoding="utf-8"))
            control_patches = [[controls[i] for i in ids] for ids in patches]
            expected = EXPECTED[name]
            require(len(patches) == count == expected[0] and
                    len(controls) == expected[1],
                    "Source real external model inventory changed")
            model_id = name.lower().replace(" ", "_")
            samples = folder / f"real_{model_id}_{center}_samples.csv"
            curve_csv = folder / f"real_{model_id}_{center}_curves.csv"
            run([str(sampler_exe), str(model_path), str(uv_csv),
                 str(samples), str(curve_csv), str(count)])
            cpp_groups, reversed_incidence = incidence_from_cpp(curve_csv, count)
            expected_groups = curve_groups(controls, patches)
            require(cpp_groups == expected_groups,
                    "Actual C++ curve identity does not match independent controls")
            degrees = Counter(len(owners) for owners in cpp_groups)
            require((degrees[1], degrees[2],
                     sum(v for k, v in degrees.items() if k > 2),
                     max(degrees)) == expected[2:],
                    "External model high-valence topology changed")
            mapped, metrics = read_samples(samples, uv, control_patches)
            shared = incidence_diagnostic(uv, mapped, cpp_groups,
                                          reversed_incidence)
            facets = []
            for pid, xyz in enumerate(mapped):
                obj = folder / f"real_{model_id}_{center}_patch_{pid:02d}.obj"
                write_obj(obj, xyz, quads, triangles, pid)
                archived.append(obj)
                facets.append(facet_diagnostic(uv, xyz, quads, triangles,
                                               control_patches[pid]))
            archived.extend((samples, curve_csv))
            result = {
                "model": name,
                "input_path": relative,
                "input_sha256": sha(model_path),
                "native_source_hybrid_sha256": sha(source_obj),
                "center_rule": center,
                "patch_count": count,
                "per_patch_uv_vertices": 69,
                "per_patch_native_quads": 42,
                "per_patch_M5_research_triangles": 36,
                "per_patch_facets_diagnostic": 120,
                "source_control_curve_degrees": dict(sorted(degrees.items())),
                "production_curve_count": len(cpp_groups),
                "physical_samples_sha256": sha(samples),
                "production_incidence_sha256": sha(curve_csv),
                "boundary_incidence": shared,
                "patch_local_geometry": metrics,
                "patch_local_facet_quality": facets,
                "all_patch_obj_files_are_unwelded": True,
                "full_model_mesh_validated": False,
            }
            if name == "Eistute" and center == CENTER_RULES[0]:
                negatives += reject_mutations(
                    folder, model_path, uv_csv, sampler_exe, folder, samples,
                    curve_csv, cpp_groups, uv, control_patches, mapped,
                    reversed_incidence)
            results.append(result)
    require(len(results) == 6 and negatives == 4 and
            sum(item["patch_count"] for item in results) == 90,
            "Incomplete real external Bezier experiment matrix")

    # A model's physical seam must not depend on the unapproved interior rule.
    for name in INPUT_MODELS:
        cases = [x for x in results if x["model"] == name]
        require(len(cases) == 2 and
                math.isclose(cases[0]["boundary_incidence"]
                                  ["maximum_sampled_seam_gap"],
                             cases[1]["boundary_incidence"]
                                  ["maximum_sampled_seam_gap"],
                             abs_tol=XYZ_ABS, rel_tol=XYZ_REL),
                "Different centroid rules altered real model shared physical seams")
    result = {
        "schema": 1,
        "status": "REAL_EXTERNAL_BEZIER_PER_PATCH_PHYSICAL_CANDIDATES_DIAGNOSTIC_ONLY",
        "native_source": "real_CXX_Quadtree_42_quad_53_uv_and_M5_Lawson_36_tri_69_uv",
        "production_physical_api": "PatchReader::ReaderFilePatches; PatchBezier::Parameterize/Qu/Qv",
        "model_count": 3,
        "model_patches": 45,
        "per_rule_total_patch_candidates": 45,
        "center_rule_count": 2,
        "per_patch_quads": 42,
        "per_patch_triangles": 36,
        "per_patch_vertices": 69,
        "actual_global_node_welding": False,
        "high_valence_sheet_policy_approved": False,
        "full_model_conforming_mesh_generated": False,
        "historic_1993_Delaunay_and_contour_contraction": False,
        "production_QUAD_enabled": False,
        "normal_check": "local Qu cross Qv; no global Z-positive assumption",
        "sampled_regularities_not_proofs": True,
        "negative_mutations_rejected": negatives,
        "source_tree_sha256": sha(folder / "tree_regions.csv"),
        "outcomes": results,
    }
    report = folder / "m4_external_bezier_physical_manifest.json"
    report.write_text(json.dumps(result, indent=2, sort_keys=True,
                                 allow_nan=False) + "\n", encoding="utf-8")
    # A single versioned archive retains all 90 distinct patch-local OBJ
    # witnesses and the corresponding geometry/incidence CSV provenance.
    archive = folder / "m4_external_bezier_physical_candidates.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=6) as zipped:
        for file in [report] + archived:
            zipped.write(file, arcname=file.name)
    require(archive.stat().st_size > 0 and len(archived) == 104,
            "External model physical per-patch archive is incomplete")
    print("m4_external_models=ok models=3 patches=45 "
          "physical_candidates=90 total_native_quads=3780 "
          "total_experimental_tri=3240 control_mutations=4 "
          "high_valence=DIAGNOSTIC_ONLY global_node_weld=NO "
          "NOT_full_model_mesh NOT_1993 NOT_production")


if __name__ == "__main__":
    main()
