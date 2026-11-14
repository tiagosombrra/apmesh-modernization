"""Exercise the real ap_mesh entry and independently audit its curved patch."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import uuid
import sys
from test_m4_real_model_hybrid import golden, approximately, cross, vector, dot
from independent_common_grid import common_grid_source_error
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/"research"/"quad"))
from p2d_next_band_dyadic import inspect_band


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


def verify_native_tree_trials(stdout, residual):
    # Check independently recorded error locations and native edit isolation.
    lines = stdout.decode().splitlines()
    candidates = [s for s in lines if s.startswith("QUAD_NATIVE_TREE_TRIALS ")]
    require(len(candidates) == 1, "Missing or repeated real native tree alternatives")
    values = dict(part.split("=", 1) for part in candidates[0].split()[1:])
    require(values["source"] == "generated_real_mixed_physical_candidate" and
            values["source_candidate_preserved"] == "1" and
            values["native_trial_refinements"] == "2" and
            values["actual_adaptive_epochs"] == "0",
            "Real native quadtree trials incorrectly claimed accepted adaptive epochs")
    require(int(values["baseline_leaves"]) == 19 and
            math.isclose(float(values["baseline_quad_uv_area"]), 0.25, abs_tol=1e-12),
            "Native tree baseline is not the independent fixed16 source")
    require(int(values["quad_cell_id"]) == 13 and
            int(values["quad_cell_id"]) != int(values["aft_cell_id"]) and
            int(values["quad_leaves"]) > 19 and
            int(values["aft_leaves"]) > 19,
            "Physical candidate residual did not select two distinct real tree edits")
    # A rejected region must be explicitly labeled; no rejected region may
    # silently acquire an accepted quad count.
    for region, marker in (("quad", "quad"), ("aft", "aft")):
        disk = int(values[region + "_emitted_disk"])
        require(disk in (0, 1), "Invalid real native emitted-disk status")
        if disk:
            require(int(values[region + "_faces" if region == "quad"
                               else "aft_quad_faces"]) > 0 and
                    float(values[region + "_uv_area"]) >= 0.25,
                    "Emitted native QUAD candidate lost its source region")
        else:
            require(any(s.startswith("QUAD_NATIVE_TRIAL_REJECTION region=" +
                                     marker + " reason=") for s in lines),
                    "Rejected native QUAD trial has no recorded failure reason")
    # Pin the real cross-platform negative topology witness on this fixed source.
    require(int(values["quad_leaves"]) == 22 and
            int(values["quad_emitted_disk"]) == 1 and
            int(values["quad_faces"]) == 54 and
            math.isclose(float(values["quad_uv_area"]), 0.25, abs_tol=1e-12) and
            int(values["aft_cell_id"]) == 6 and
            int(values["aft_leaves"]) == 22 and
            int(values["aft_emitted_disk"]) == 0 and
            int(values["aft_quad_faces"]) == 0 and
            math.isclose(float(values["aft_uv_area"]), 0.265625, abs_tol=1e-12),
            "Changed native boundary-island source witness without review")
    require(any(line == "QUAD_NATIVE_TRIAL_REJECTION region=aft "
                        "reason=Boundary vertex is not manifold" for line in lines),
            "Boundary-refinement nonmanifold rejection was not preserved")
    require(residual["worst_quad_face"] == 4 and
            residual["worst_triangle_face"] == 74,
            "Native trial decision no longer follows actual previous physical errors")
    return values


def independent_source_band_grid_oracle():
    # Reconstruct the proposed source-cell plan in exact 1/8 dyadic units,
    # independently of the native quadtree capture/emitter implementation.
    subdivided = {(1, 1), (0, 0), (1, 0), (0, 1)}
    leaves = []
    for x in range(4):
        for y in range(4):
            if (x, y) in subdivided:
                leaves.extend((2*x+dx, 2*y+dy, 2*x+dx+1, 2*y+dy+1)
                              for dx in (0, 1) for dy in (0, 1))
            else:
                leaves.append((2*x, 2*y, 2*x+2, 2*y+2))
    require(len(leaves) == 28, "Independent source band leaf count changed")
    eligible = [tile for tile in leaves
                if tile[0] > 0 and tile[1] > 0 and
                   tile[2] < 8 and tile[3] < 8]
    tiles = {(u, v) for x0, y0, x1, y1 in eligible
             for u in range(x0, x1) for v in range(y0, y1)}
    require(len(tiles) == 21, "Independent source band grid area changed")
    # Four-neighbor connectivity, not point contact, is essential for a disk.
    pending = [next(iter(tiles))]
    seen = set()
    while pending:
        xy = pending.pop()
        if xy in seen:
            continue
        seen.add(xy)
        pending.extend((xy[0]+du, xy[1]+dv)
                       for du, dv in ((1, 0), (-1, 0), (0, 1), (0, -1))
                       if (xy[0]+du, xy[1]+dv) in tiles and
                       (xy[0]+du, xy[1]+dv) not in seen)
    require(seen == tiles, "Independent source band is not edge-connected")
    # Reject an enclosed hole with a separate complement flood-fill.
    outside = {(u, v) for u in range(8) for v in range(8)} - tiles
    start = {(u, v) for u, v in outside
             if u in (0, 7) or v in (0, 7)}
    frontier = list(start)
    reachable = set()
    while frontier:
        xy = frontier.pop()
        if xy in reachable:
            continue
        reachable.add(xy)
        frontier.extend((xy[0]+du, xy[1]+dv)
                        for du, dv in ((1, 0), (-1, 0), (0, 1), (0, -1))
                        if (xy[0]+du, xy[1]+dv) in outside and
                        (xy[0]+du, xy[1]+dv) not in reachable)
    require(reachable == outside, "Independent source band contains a UV hole")
    return len(tiles) / 64.0


def verify_connected_aft_band(stdout, source_residual):
    # The band edits a separate native tree, never the accepted physical mesh.
    lines = stdout.decode().splitlines()
    entries = [line for line in lines if line.startswith("QUAD_CONNECTED_BAND_TRIAL ")]
    require(len(entries) == 1, "Connected AFT band result missing or duplicated")
    record = dict(token.split("=", 1) for token in entries[0].split()[1:])
    require(record["source"] == "real_candidate_worst_aft_triangle" and
            int(record["source_cell_id"]) == 6 and
            len({int(record[key]) for key in ("source_cell_id", "bridge_east_cell_id",
                "bridge_north_cell_id")}) == 3 and
            int(record["baseline_leaves"]) == 19 and
            int(record["refined_leaves"]) >= 28 and
            int(record["native_leaf_edits"]) == 3 and
            record["prior_physical_owner_preserved"] == "1" and
            record["actual_aft_retriangulations"] == "0" and
            record["adaptive_epochs"] == "0",
            "Connected band has false tree, physical or adaptive epoch provenance")
    admitted = int(record["admitted_uv_disk"])
    require(admitted in (0, 1), "Connected band has an invalid UV-disk status")
    if admitted:
        require(float(record["quad_uv_area"]) > 0.265625 and
                int(record["emitted_quads"]) > 0,
                "Connected band claimed a disk without expanding QUAD coverage")
        require(not any(line.startswith("QUAD_CONNECTED_BAND_REJECTION ")
                        for line in lines),
                "Connected band both admitted and rejected the same source trial")
    else:
        require(int(record["emitted_quads"]) == 0 and
                any(line.startswith("QUAD_CONNECTED_BAND_REJECTION reason=")
                    for line in lines),
                "Rejected source band failed to disclose the topology blocker")
    # Freeze this source-specific result; any changed topology needs explicit review.
    require(int(record["bridge_east_cell_id"]) == 7 and
            int(record["bridge_north_cell_id"]) == 9 and
            int(record["refined_leaves"]) == 28 and
            int(record["admitted_uv_disk"]) == 1 and
            int(record["emitted_quads"]) == 62 and
            math.isclose(float(record["quad_uv_area"]), 0.328125, abs_tol=1e-12),
            "Connected source band changed its qualified 2:1 manifold witness")
    require(math.isclose(float(record["quad_uv_area"]),
                         independent_source_band_grid_oracle(), abs_tol=1e-12),
            "Real source band differs from independent dyadic union oracle")
    require(source_residual["worst_triangle_face"] == 74,
            "Connected band did not track real initial AFT source error")
    return record


def verify_second_native_band(stdout, previous_physical_residual):
    # Match actual native C++ Quadtree trials to a separate dyadic topology oracle.
    require(previous_physical_residual["worst_triangle_face"] == 103 and
            math.isclose(previous_physical_residual["tri_sample_u"], 0.8, abs_tol=1e-12) and
            math.isclose(previous_physical_residual["tri_sample_v"], 0.1, abs_tol=1e-12),
            "Second native trial did not start from the staged previous AFT source error")
    lines = stdout.decode().splitlines()
    prefixes = {
        "corner": ((3, 0),),
        "west": ((3, 0), (2, 0)),
        "north": ((3, 0), (3, 1)),
        "both": ((3, 0), (2, 0), (3, 1)),
    }
    actual = {}
    for line in lines:
        if not line.startswith("QUAD_SECOND_NATIVE_BAND "):
            continue
        values = dict(token.split("=", 1) for token in line.split()[1:])
        name = values.get("variant")
        require(name in prefixes and name not in actual and
                values["source"] == "staged_previous_physical_worst_aft" and
                values["previous_physical_owner_preserved"] == "1" and
                values["actual_second_aft_retriangulations"] == "0" and
                values["adaptive_epochs"] == "0",
                "Second native AFT-band result has duplicate or false provenance")
        predicted = inspect_band(prefixes[name])
        admitted = int(values["admitted_uv_disk"])
        require(admitted in (0, 1) and int(values["baseline_leaves"]) == 28 and
                int(values["native_leaf_edits"]) == len(predicted.selected) and
                int(values["refined_leaves"]) >= predicted.leaves and
                math.isclose(float(values["quad_uv_area"]), predicted.uv_area,
                             rel_tol=0, abs_tol=1e-12) and
                len({int(values[key]) for key in
                     ("selected_native_id", "west_native_id", "north_native_id")}) == 3,
                "Original native second-band tree differs from independent source grid")
        rejected = any(value.startswith("QUAD_SECOND_NATIVE_BAND_REJECTION variant=" +
                                       name + " reason=") for value in lines)
        if admitted:
            require(predicted.admitted_disk and int(values["emitted_quads"]) > 0 and
                    not rejected,
                    "Native second-band disk was accepted without independent UV support")
        else:
            require(int(values["emitted_quads"]) == 0 and rejected,
                    "Native second-band rejection lost its mandatory reason")
        actual[name] = {"admitted_uv_disk": admitted,
                        "leaves": int(values["refined_leaves"]),
                        "quad_uv_area": float(values["quad_uv_area"]),
                        "emitted_quads": int(values["emitted_quads"])}
    require(set(actual) == set(prefixes) and actual["corner"]["admitted_uv_disk"] == 0,
            "Next AFT-error native tree did not reject the isolated corner")
    require(any(actual[key]["admitted_uv_disk"] for key in ("west", "north", "both")),
            "No native-connected bridge to the next source-error AFT island succeeded")
    return actual


def verify_physical_band_candidate(stdout, prefix):
    # A separate file is only an experimental *candidate*, never an adopted epoch.
    lines = stdout.decode().splitlines()
    records = [line for line in lines if line.startswith("QUAD_BAND_PHYSICAL_CANDIDATE ")]
    require(len(records) == 1, "Missing or duplicate physical native-AFT band attempt")
    values = dict(token.split("=", 1) for token in records[0].split()[1:])
    require(values["source"] == "original_native_connected_band" and
            values["previous_physical_owner_preserved"] == "1" and
            values["original_aft_pipeline_requested"] == "1" and
            values["adaptive_epochs"] == "0",
            "Physical band incorrectly claimed ownership/adaptation admission")
    candidate_path = Path(str(prefix) + ".band-candidate.obj")
    status = values["status"]
    require(status in ("staged_unaccepted", "rejected"), "Unknown physical band status")
    if status == "rejected":
        require(values["exported_candidate"] == "0" and
                not candidate_path.exists() and
                any(s.startswith("QUAD_BAND_PHYSICAL_REJECTION reason=") for s in lines),
                "Rejected physical AFT band published an unverified candidate")
        return {"status": "rejected"}
    require(values["exported_candidate"] == "1" and candidate_path.is_file(),
            "Full original native AFT candidate was not exported for independent audit")
    topology = audit(candidate_path)
    quality = independent_quad_physical_quality(candidate_path)
    errors = independent_mixed_surface_residual(candidate_path)
    require(topology["quads"] == quality["quads"] == 62 and
            topology["triangles"] > 0 and topology["boundary"] == 16 and
            topology["nodes"] == int(values["physical_nodes"]) and
            topology["triangles"] == int(values["physical_triangles"]) and
            topology["quads"] == int(values["physical_quads"]),
            "Physical connected source band has wrong typed topology")
    require(quality["min_scaled_jacobian"] > 0.0 and
            quality["min_warpage_cosine"] > 0.0 and
            errors["maximum"] > 0.0 and
            errors["samples"] == 5 * topology["quads"] + 4 * topology["triangles"],
            "Physical native band source/quality is not independently admissible")
    for actual, field in (("maximum", "max_source_error"),
                          ("quad_maximum", "max_quad_error"),
                          ("triangle_maximum", "max_aft_error")):
        require(math.isclose(errors[actual], float(values[field]), rel_tol=1e-8,
                             abs_tol=1e-9),
                "Reported native AFT source residual differs from Bernstein OBJ oracle")
    require(float(values["min_facet_quality"]) > 0.0,
            "Candidate physical facet quality was not positive")
    second_native = verify_second_native_band(stdout, errors)
    return {"status": status, "topology": topology,
            "errors": errors, "physical_quality": quality,
            "second_native_band_trials": second_native,
            "candidate_sha256": hashlib.sha256(candidate_path.read_bytes()).hexdigest()}


def verify_same_site_fixed_grid_error(original_path, candidate_path):
    # The previous per-element metric uses different numbers of samples as
    # topology changes. Only a fixed independent grid can compare both meshes.
    prior = common_grid_source_error(original_path, grid=64)
    revised = common_grid_source_error(candidate_path, grid=64)
    require(prior["sample_count"] == revised["sample_count"] == 4096 and
            prior["quad_sites"] == 1024 and prior["tri_sites"] == 3072 and
            revised["quad_sites"] == 1344 and revised["tri_sites"] == 2752,
            "Real native QUAD band changed fixed-grid coverage")
    for name, prev, curr in (
            ("max_xyz", .06564122093160714, .05160741345747398),
            ("rms_uv", .017295203854736017, .012518000838243337),
            ("rms_source_area", .015981265663966727, .011810324643012932)):
        require(math.isclose(prior[name], prev, rel_tol=1e-8, abs_tol=1e-9) and
                math.isclose(revised[name], curr, rel_tol=1e-8, abs_tol=1e-9) and
                revised[name] < prior[name],
                "Same-site source-error reduction witness changed: " + name)
    return {"fixed_64x64_original": prior, "fixed_64x64_band": revised,
            "adaptive_epochs": 0, "continuous_error_bound": False}


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
    trials = verify_native_tree_trials(r.stdout, residual)
    band = verify_connected_aft_band(r.stdout, residual)
    physical_band = verify_physical_band_candidate(r.stdout, root/"accepted")
    require(physical_band["status"] == "staged_unaccepted",
            "Pinned native connected-band physical candidate is no longer valid")
    grid_audit = verify_same_site_fixed_grid_error(root/"accepted.obj",
                                                   root/"accepted.band-candidate.obj")
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
    require(verify_native_tree_trials(r.stdout, residual) == trials,
            "Rollback native tree trial provenance differs from accepted control")
    require(verify_connected_aft_band(r.stdout, residual) == band,
            "Rollback native connected band provenance differs")
    require(verify_physical_band_candidate(r.stdout, root/"rollback") == physical_band,
            "Rollback changed actual physical native-AFT band candidate result")
    r = execute("unsupported", model="missing.bp")
    require(not (root/"unsupported.band-candidate.obj").exists(),
            "Unsupported source staged an illegal physical band candidate")
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
              "real_native_tree_trials": trials,
              "connected_native_refinement_band": band,
              "physical_native_band_candidate": physical_band,
              "same_site_source_error": grid_audit,
              "OBJ_sha256": hashlib.sha256(initial).hexdigest(), "adaptive_epochs": 0}
    (root/"report.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
