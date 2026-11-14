"""Exercise the real ap_mesh entry and independently audit its curved patch."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import uuid
from test_m4_real_model_hybrid import golden, approximately, cross, vector, dot


def require(value, message):
    if not value:
        raise AssertionError(message)


def audit(path):
    xyz, uv, faces = [], [], []
    for line in path.read_text().splitlines():
        row = line.split()
        if not row:
            continue
        if row[0] == "v":
            xyz.append(tuple(map(float, row[1:])))
        elif row[0] == "vt":
            uv.append(tuple(map(float, row[1:])))
        elif row[0] == "f":
            ids = []
            for item in row[1:]:
                a, b = map(int, item.split("/"))
                require(a == b and a > 0, "Foreign physical/UV index")
                ids.append(a - 1)
            faces.append(ids)
    return inspect(xyz, uv, faces)


def inspect(xyz, uv, faces):
    require(len(xyz) == len(uv) > 0 and faces, "Empty application output")
    require(any(len(f) == 4 for f in faces) and any(len(f) == 3 for f in faces),
            "Application did not generate both element types")
    for p, q in zip(xyz, uv):
        require(len(q) == 2 and all(math.isfinite(x) and 0 <= x <= 1 for x in q),
                "Invalid exported UV")
        require(approximately(p, golden(*q)[0]), "Source Bezier mapping mismatch")
    edges = {}
    area = 0.
    for face in faces:
        require(len(face) in (3, 4) and len(set(face)) == len(face), "Invalid face")
        require(all(0 <= i < len(uv) for i in face), "Foreign index")
        for a, b in zip(face, face[1:] + face[:1]):
            edges.setdefault(tuple(sorted((a, b))), []).append((a, b))
        for slots in ((0, 1, 2), (0, 2, 3)) if len(face) == 4 else ((0, 1, 2),):
            ids = [face[k] for k in slots]
            a, b, c = [uv[i] for i in ids]
            twice = (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
            require(twice > 0, "Inverted UV facet")
            area += twice / 2
            center = tuple(sum(uv[i][k] for i in ids)/3 for k in range(2))
            _, du, dv = golden(*center)
            physical = cross(vector(xyz[ids[0]], xyz[ids[1]]),
                             vector(xyz[ids[0]], xyz[ids[2]]))
            require(dot(physical, cross(du, dv)) > 0, "Reversed physical facet")
    boundary = 0
    for uses in edges.values():
        require(len(uses) <= 2, "Nonmanifold edge")
        if len(uses) == 2:
            require(uses[0] == uses[1][::-1], "Shared winding mismatch")
        else:
            a, b = [uv[i] for i in uses[0]]
            require(any(a[k] == b[k] and a[k] in (0, 1) for k in (0, 1)),
                    "Interior gap")
            boundary += 1
    require(boundary == 16 and len(xyz)-len(edges)+len(faces) == 1,
            "Source boundary/disk differs")
    require(abs(area - 1) < 1e-8, "Incomplete or overlapping UV area")
    return {"nodes": len(xyz), "quads": sum(len(f) == 4 for f in faces),
            "triangles": sum(len(f) == 3 for f in faces), "boundary": boundary}


def independent_mixed_angle_defect(path):
    # Recompute the metric from physical OBJ edges using the cosine law,
    # independent of the C++ vector-dot/cross angle implementation.
    positions, faces = [], []
    for line in path.read_text().splitlines():
        words = line.split()
        if words and words[0] == "v":
            positions.append(tuple(map(float, words[1:])))
        elif words and words[0] == "f":
            faces.append([int(token.split("/")[0]) - 1 for token in words[1:]])
    edge_use = {}
    for face in faces:
        for a, b in zip(face, face[1:] + face[:1]):
            edge_use.setdefault(tuple(sorted((a, b))), 0)
            edge_use[tuple(sorted((a, b)))] += 1
    boundary = set()
    for (a, b), count in edge_use.items():
        if count == 1:
            boundary.update((a, b))
    angles = [0.0] * len(positions)
    dual_area = [0.0] * len(positions)
    for face in faces:
        triples = ((0, 1, 2), (0, 2, 3)) if len(face) == 4 else ((0, 1, 2),)
        for slots in triples:
            a, b, c = (face[k] for k in slots)
            la = math.dist(positions[b], positions[c])
            lb = math.dist(positions[a], positions[c])
            lc = math.dist(positions[a], positions[b])
            semi = (la + lb + lc) / 2.0
            area = math.sqrt(max(0.0, semi * (semi-la) * (semi-lb) * (semi-lc)))
            require(area > 0.0, "Independent mixed metric has zero-area facet")
            for vertex, adjacent_a, adjacent_b, opposite in (
                    (a, lb, lc, la), (b, la, lc, lb), (c, la, lb, lc)):
                cosine = (adjacent_a**2 + adjacent_b**2 - opposite**2) / (
                    2.0 * adjacent_a * adjacent_b)
                angles[vertex] += math.acos(max(-1.0, min(1.0, cosine)))
                dual_area[vertex] += area / 3.0
    defect = sum((math.pi if i in boundary else 2.0 * math.pi) - value
                 for i, value in enumerate(angles))
    return {"angle_defect_total": defect, "min_barycentric_area": min(dual_area),
            "interior_vertices": len(positions)-len(boundary),
            "boundary_vertices": len(boundary), "boundary_edges":
            sum(value == 1 for value in edge_use.values())}


def verify_mixed_curvature(stdout, path):
    entries = [line for line in stdout.decode().splitlines()
               if line.startswith("QUAD_TYPED_CURVATURE ")]
    require(len(entries) == 1, "Mixed curvature diagnostic missing or duplicated")
    values = dict(field.split("=", 1) for field in entries[0].split()[1:])
    oracle = independent_mixed_angle_defect(path)
    for name in ("boundary_edges", "boundary_vertices", "interior_vertices"):
        require(int(values[name]) == oracle[name], "Mixed topology diagnostic differs: " + name)
    require(int(values["quad"]) == 42 and int(values["tri"]) == 36 and
            int(values["negative_cases"]) == 5 and
            values["policy"] == "triangulated_barycentric_probe" and
            values["adaptive_epochs"] == "0",
            "Mixed diagnostic wrong type/negative-case/epoch contract")
    for name in ("angle_defect_total", "min_barycentric_area"):
        actual, expected = float(values[name]), oracle[name]
        require(math.isfinite(actual) and math.isclose(actual, expected, rel_tol=1e-8,
                                                        abs_tol=1e-8),
                "Independent mixed curvature oracle disagrees: " + name)
    require(oracle["min_barycentric_area"] > 0.0 and
            math.isclose(oracle["angle_defect_total"], 2.0 * math.pi, abs_tol=1e-8),
            "Mixed physical disk metric is invalid")
    return oracle


def independent_quad_physical_quality(path):
    # Re-evaluate every retained four-node physical QUAD from OBJ and the
    # independent source Bezier derivatives, not C++ element quality fields.
    positions, uv, faces = [], [], []
    for line in path.read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "v":
            positions.append(tuple(map(float, fields[1:])))
        elif fields[0] == "vt":
            uv.append(tuple(map(float, fields[1:])))
        elif fields[0] == "f":
            faces.append([int(token.split("/")[0]) - 1 for token in fields[1:]])
    metrics = {"quads": 0, "min_scaled_jacobian": 1.0,
               "min_warpage_cosine": 1.0, "max_edge_ratio": 1.0}
    def magnitude(v):
        return math.sqrt(dot(v, v))
    for face in faces:
        if len(face) != 4:
            continue
        metrics["quads"] += 1
        points = [positions[i] for i in face]
        lengths = []
        for k, idx in enumerate(face):
            current = points[k]
            next_edge = vector(current, points[(k+1) % 4])
            prev_edge = vector(current, points[(k+3) % 4])
            lengths.append(magnitude(next_edge))
            _, du, dv = golden(*uv[idx])
            reference = cross(du, dv)
            denominator = magnitude(next_edge) * magnitude(prev_edge) * magnitude(reference)
            require(denominator > 0, "Independent QUAD corner has zero metric denominator")
            scaled = dot(cross(next_edge, prev_edge), reference) / denominator
            metrics["min_scaled_jacobian"] = min(metrics["min_scaled_jacobian"], scaled)
        normal_first = cross(vector(points[0], points[1]), vector(points[0], points[2]))
        normal_second = cross(vector(points[0], points[2]), vector(points[0], points[3]))
        warp = dot(normal_first, normal_second) / (
            magnitude(normal_first) * magnitude(normal_second))
        metrics["min_warpage_cosine"] = min(metrics["min_warpage_cosine"], warp)
        metrics["max_edge_ratio"] = max(metrics["max_edge_ratio"],
                                         max(lengths) / min(lengths))
    return metrics


def verify_quad_physical_quality(stdout, path):
    entries = [line for line in stdout.decode().splitlines()
               if line.startswith("QUAD_TYPED_QUALITY ")]
    require(len(entries) == 1, "Physical QUAD quality diagnostic missing or duplicated")
    values = dict(field.split("=", 1) for field in entries[0].split()[1:])
    independent = independent_quad_physical_quality(path)
    require(int(values["quads"]) == independent["quads"] == 42 and
            int(values["negative_cases"]) == 4 and
            values["policy"] == "corner_normal_metric_probe" and
            values["adaptive_epochs"] == "0",
            "Physical QUAD metric type, policy or negative witness invalid")
    for field in ("min_scaled_jacobian", "min_warpage_cosine", "max_edge_ratio"):
        actual, expected = float(values[field]), independent[field]
        require(math.isfinite(actual) and math.isclose(actual, expected,
                abs_tol=1e-8, rel_tol=1e-8),
                "Independent physical QUAD quality metric disagrees: " + field)
    require(independent["min_scaled_jacobian"] > 0.0 and
            independent["min_warpage_cosine"] > 0.0 and
            independent["max_edge_ratio"] >= 1.0,
            "Physical QUAD metric is degenerate or reversed")
    return independent


def independent_mixed_surface_residual(path):
    # Apply independent Bernstein source evaluation at TRI barycentric and
    # QUAD bilinear sample locations parsed only from the exported physical OBJ.
    xyz, uv, faces = [], [], []
    for line in path.read_text().splitlines():
        words = line.split()
        if not words:
            continue
        if words[0] == "v":
            xyz.append(tuple(map(float, words[1:])))
        elif words[0] == "vt":
            uv.append(tuple(map(float, words[1:])))
        elif words[0] == "f":
            faces.append([int(w.split("/")[0])-1 for w in words[1:]])
    triangle_weights = (
        (1/3, 1/3, 1/3), (.6, .2, .2), (.2, .6, .2), (.2, .2, .6))
    quadrilateral_samples = (
        (.5, .5), (.25, .25), (.75, .25), (.75, .75), (.25, .75))
    result = {"maximum": 0.0, "rms": 0.0, "quad_maximum": 0.0,
              "triangle_maximum": 0.0, "worst_quad_face": 0, "worst_triangle_face": 0,
              "tri_sample_u": 0.0, "tri_sample_v": 0.0,
              "quads": 0, "triangles": 0, "samples": 0,
              "select_u": 0.0, "select_v": 0.0}
    squares = []
    for i, face in enumerate(faces):
        if len(face) == 3:
            samples = [w for w in triangle_weights]
        else:
            samples = [( (1-s)*(1-t), s*(1-t), s*t, (1-s)*t)
                       for s, t in quadrilateral_samples]
        face_max = -1.0
        face_uv = None
        for weights in samples:
            at = tuple(sum(weight * uv[index][axis]
                           for index, weight in zip(face, weights))
                       for axis in (0, 1))
            approximate = tuple(sum(weight * xyz[index][axis]
                                    for index, weight in zip(face, weights))
                                for axis in (0, 1, 2))
            exact = golden(*at)[0]
            distance = math.dist(exact, approximate)
            squares.append(distance * distance)
            if distance > face_max:
                face_max = distance
                face_uv = at
            result["maximum"] = max(result["maximum"], distance)
            result["samples"] += 1
        if len(face) == 4:
            if result["quads"] == 0 or face_max > result["quad_maximum"]:
                result["worst_quad_face"] = i
                result["select_u"], result["select_v"] = face_uv
            result["quads"] += 1
            result["quad_maximum"] = max(result["quad_maximum"], face_max)
        else:
            if result["triangles"] == 0 or face_max > result["triangle_maximum"]:
                result["worst_triangle_face"] = i
                result["tri_sample_u"], result["tri_sample_v"] = face_uv
            result["triangles"] += 1
            result["triangle_maximum"] = max(result["triangle_maximum"], face_max)
    result["rms"] = math.sqrt(math.fsum(squares) / result["samples"])
    result["dominant_region"] = ("tri_aft" if result["triangle_maximum"] > result["quad_maximum"]
                                 else "quad_interior")
    return result


def verify_mixed_surface_residual(stdout, path):
    matches = [line for line in stdout.decode().splitlines()
               if line.startswith("QUAD_SOURCE_RESIDUAL ")]
    require(len(matches) == 1, "Mixed Bezier source residual missing or duplicated")
    observed = dict(part.split("=", 1) for part in matches[0].split()[1:])
    expected = independent_mixed_surface_residual(path)
    for name in ("samples", "quads", "triangles", "worst_quad_face",
                 "worst_triangle_face"):
        require(int(observed[name]) == expected[name],
                "Mixed surface residual identity differs: " + name)
    for name in ("maximum", "rms", "quad_maximum", "triangle_maximum",
                 "select_u", "select_v", "tri_sample_u", "tri_sample_v"):
        require(math.isclose(float(observed[name]), expected[name],
                             abs_tol=1e-9, rel_tol=1e-8),
                "Independent physical source residual differs: " + name)
    require(observed["dominant_region"] == expected["dominant_region"] and
            observed["policy"] == "physical_bilinear_quad_tri_barycentric_v1" and
            observed["real_tree_edits"] == "0" and observed["adaptive_epochs"] == "0" and
            int(observed["real_leaf_ordinal"]) >= 0 and
            int(observed["real_cell_id"]) >= 0 and
            int(observed["source_depth"]) in (2, 3),
            "Source residual incorrectly claims an adapted native tree")
    require(expected["quads"] == 42 and expected["triangles"] == 36 and
            expected["samples"] == 354 and expected["maximum"] > 0.0,
            "Controlled physical residual has unexpected topology or error")
    return expected


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--exe", required=True, type=Path)
    p.add_argument("--directory", required=True, type=Path)
    args = p.parse_args()
    root = args.directory.resolve() / ("run-" + uuid.uuid4().hex)
    root.mkdir(parents=True, exist_ok=False)
    def execute(name, rollback=False, model="builtin:curva_bezier"):
        config = root/(name+".conf")
        config.write_text(f"INPUT_MODEL={model}\nOUTPUT_PREFIX={root/name}\n"
                          "MESH_ELEMENT_KIND=quad_uv\n"
                          "QUAD_EXPERIMENTAL_CASE=curved_bezier_fixed16_vertex_mean_v1\n"
                          f"QUAD_VERIFY_ROLLBACK={int(rollback)}\nNUM_THREADS=1\nNUM_PROCESSES=1\n")
        r = subprocess.run([str(args.exe.resolve()), "--config", str(config)],
                           capture_output=True, timeout=60)
        (root/(name+".stdout")).write_bytes(r.stdout)
        (root/(name+".stderr")).write_bytes(r.stderr)
        return r
    r = execute("accepted")
    require(r.returncode == 0 and b"ids_unique=1 published=1" in r.stdout,
            "Real CLI generation or physical identities failed")
    require(b"QUAD_TYPED_HISTORY_CLONE accepted_clone=1 partial_failure_rollback=1" in r.stdout and
            b"source_observers_preserved=1 adaptive_epochs=0" in r.stdout,
            "Typed QUAD/TRI history clone or rollback guard did not run")
    result = audit(root/"accepted.obj")
    metric = verify_mixed_curvature(r.stdout, root/"accepted.obj")
    quality = verify_quad_physical_quality(r.stdout, root/"accepted.obj")
    residual = verify_mixed_surface_residual(r.stdout, root/"accepted.obj")
    initial = (root/"accepted.obj").read_bytes()
    r = subprocess.run([str(args.exe.resolve()), "--config", str(root/"accepted.conf")],
                       capture_output=True, timeout=60)
    require(r.returncode != 0 and (root/"accepted.obj").read_bytes() == initial,
            "Existing output was overwritten")
    r = execute("rollback", True)
    require(b"QUAD_TYPED_HISTORY_CLONE accepted_clone=1 partial_failure_rollback=1" in r.stdout,
            "Rollback case did not preserve the typed history probe")
    require(r.returncode == 1 and b"QUAD_ROLLBACK preserved=1 previous_nonempty=1" in r.stdout,
            "Nonempty physical publication rollback not demonstrated")
    require(audit(root/"rollback.obj") == result, "Rollback lost prior valid output")
    require(verify_mixed_curvature(r.stdout, root/"rollback.obj") == metric,
            "Rollback changed mixed curvature metrics")
    require(verify_quad_physical_quality(r.stdout, root/"rollback.obj") == quality,
            "Rollback changed typed QUAD physical quality")
    require(verify_mixed_surface_residual(r.stdout, root/"rollback.obj") == residual,
            "Rollback changed history-dependent source residual")
    r = execute("unsupported", model="missing.bp")
    require(r.returncode != 0 and not (root/"unsupported.obj").exists(),
            "Invalid source was published")
    # Independently reject a physical corruption and reversed topology.
    text = (root/"accepted.obj").read_text()
    for i, changed in enumerate((text.replace("v ", "v 999 ", 1),
                                 text.replace("f ", "f 1/1 ", 1))):
        bad = root/f"corrupt-{i}.obj"
        bad.write_text(changed)
        try:
            audit(bad)
        except (AssertionError, ValueError, IndexError):
            continue
        raise AssertionError("Corrupted physical mesh passed independent audit")
    report = {"actual_ap_mesh_entry": True, "model": "Models3d::ModelCurvaBezier",
              "result": result, "rollback_nonempty": True,
              "native_AFT": True, "independent_Bezier_oracle": True,
              "typed_history_clone_guard": True,
              "typed_mixed_curvature_diagnostic": metric,
              "typed_physical_quad_quality": quality,
              "mixed_surface_residual": residual,
              "OBJ_sha256": hashlib.sha256(initial).hexdigest(), "adaptive_epochs": 0}
    (root/"report.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
