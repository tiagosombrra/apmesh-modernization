"""Compare archived mixed-mesh transitions at the same physical source sites."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import median

from quad_generation_metrics import cross, element_quality, geometry_error_at_sites, load_physical_obj
from audit_model_catalog import parse_bp
from test_m4_external_bezier_physical import bernstein
from test_m4_real_model_hybrid import golden


def edges(polygon):
    return zip(polygon, polygon[1:] + polygon[:1])


def orient(a, b, p):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def area(polygon):
    if not polygon:
        return 0.0
    a, b = polygon[0]
    return sum((p[0] - a) * (q[1] - b) - (q[0] - a) * (p[1] - b)
               for p, q in edges(polygon)) / 2


def intersection_area(face, region):
    polygon = face
    for a, b in edges(region):
        clipped = []
        for left, right in edges(polygon):
            l = orient(a, b, left)
            r = orient(a, b, right)
            if (l >= 0) != (r >= 0):
                t = l / (l - r)
                clipped.append(tuple(p + t * (q - p) for p, q in zip(left, right)))
            if r >= 0:
                clipped.append(right)
        polygon = clipped
    return max(0.0, area(polygon))


def grid_sites(grid, region=None):
    if region is None:
        return [((i+.5)/grid, (j+.5)/grid) for j in range(grid) for i in range(grid)]
    low, high = (tuple(f(column) for column in zip(*region)) for f in (min, max))
    points = [(low[0] + (i+.5)/grid * (high[0] - low[0]),
               low[1] + (j+.5)/grid * (high[1] - low[1]))
              for j in range(grid) for i in range(grid)]
    return [p for p in points if all(orient(a, b, p) >= 0 for a, b in edges(region))]


def observe(path, region, samples, global_samples, evaluate):
    xyz, uv, faces = load_physical_obj(path)
    if len(uv) != len(set(uv)) or len(xyz) != len(set(i for f in faces for i in f)):
        raise ValueError("Repeated UV site or unused mesh node")
    for physical, p in zip(xyz, uv):
        if any(v < 0 or v > 1 for v in p):
            raise ValueError("UV site outside source chart")
        if not all(math.isclose(a, b, rel_tol=2e-10, abs_tol=2e-8)
                   for a, b in zip(physical, evaluate(*p)[0])):
            raise ValueError("Mesh node differs from the analytic Bezier source")

    def normal(p):
        _, du, dv = evaluate(*p)
        return cross(du, dv)

    uses = {}
    sizes = []
    quality = []
    portions = []
    for i, face in enumerate(faces):
        quality.append(element_quality(xyz, uv, face, normal))
        portions.append(intersection_area([uv[j] for j in face], region))
        sizes.append(median(math.dist(xyz[a], xyz[b]) for a, b in edges(face)))
        for a, b in edges(face):
            uses.setdefault(tuple(sorted((a, b))), []).append((a, b, i))
    if not math.isclose(sum(portions), area(region), rel_tol=1e-8, abs_tol=1e-14):
        raise ValueError("Face coverage does not match the fixed UV region")
    contour = set()
    gradation = []
    local_gradation = []
    for incidents in uses.values():
        if len(incidents) == 1:
            a, b, _ = incidents[0]
            if not any(uv[a][k] == uv[b][k] and uv[a][k] in (0, 1) for k in (0, 1)):
                raise ValueError("Mesh has an internal boundary")
            contour.add((uv[a], uv[b]))
            continue
        if len(incidents) != 2 or incidents[0][:2] != incidents[1][:2][::-1]:
            raise ValueError("Inconsistent shared mesh edge")
        i, j = (item[2] for item in incidents)
        ratio = max(sizes[i], sizes[j]) / min(sizes[i], sizes[j])
        gradation.append(ratio)
        if portions[i] > 1e-14 or portions[j] > 1e-14:
            local_gradation.append(ratio)
    if len(xyz) - len(uses) + len(faces) != 1:
        raise ValueError("Mesh does not have single-chart disk incidence")

    def summarize(indices):
        cells = [quality[i] for i in indices]
        by_kind = {}
        for kind, score in (("TRI", "tri_q"), ("QUAD", "quad_corner_jacobian")):
            group = [q for q in cells if q["kind"] == kind]
            by_kind[kind] = dict(count=len(group),
                                 minimum_angle=min((q["min_angle_xyz"] for q in group), default=None),
                                 minimum_shape=min((q[score] for q in group), default=None))
        return dict(minimum_angle=min(q["min_angle_xyz"] for q in cells), by_kind=by_kind)

    local = [i for i, value in enumerate(portions) if value > 1e-14]
    regional_shape = summarize(local)
    for kind, summary in regional_shape["by_kind"].items():
        summary["uv_area_fraction"] = sum(portions[i] for i in local
                                          if quality[i]["kind"] == kind) / area(region)
    return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                nodes=len(uv), faces=len(faces), boundary_segments=len(contour),
                shape=summarize(range(len(faces))), regional_shape=regional_shape,
                global_error=geometry_error_at_sites(xyz, uv, faces, global_samples, evaluate),
                regional_error=geometry_error_at_sites(xyz, uv, faces, samples, evaluate),
                max_adjacent_size_ratio=max(gradation, default=None),
                max_regional_adjacent_size_ratio=max(local_gradation, default=None)), contour


def compare(baseline, candidate, region, evaluate=golden, grid=24):
    if not 4 <= grid <= 256:
        raise ValueError("Unsupported reporting grid")
    if (len(region) < 3 or any(len(p) != 2 or not all(0 <= v <= 1 for v in p) for p in region)
            or len(set(map(tuple, region))) != len(region) or area(region) <= 1e-14
            or any(orient(a, b, p) < -1e-14 for a, b in edges(region) for p in region)):
        raise ValueError("Expected a counterclockwise convex UV region")
    samples = grid_sites(grid, region)
    global_samples = grid_sites(grid)
    a, old_boundary = observe(baseline, region, samples, global_samples, evaluate)
    b, new_boundary = observe(candidate, region, samples, global_samples, evaluate)
    return dict(grid=grid, region=region, same_ordered_contour_edges=old_boundary == new_boundary,
                baseline=a, candidate=b)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--region", type=Path, required=True, help="Counterclockwise convex UV polygon in JSON")
    parser.add_argument("--source-bp", type=Path, help="Indexed cubic Bezier model (default: built-in CurvaBezier)")
    parser.add_argument("--patch", type=int, default=0, help="Zero-based source patch in the indexed model")
    parser.add_argument("--grid", type=int, default=24)
    args = parser.parse_args()
    evaluate = golden
    if args.source_bp:
        vertices, patches = parse_bp(args.source_bp.read_text(encoding="utf-8"))
        if not 0 <= args.patch < len(patches):
            parser.error("Unknown Bezier source patch")
        controls = [vertices[i] for i in patches[args.patch]]
        evaluate = lambda u, v: bernstein(controls, u, v)
    elif args.patch != 0:
        parser.error("--patch requires --source-bp")
    region = json.loads(args.region.read_text(encoding="utf-8"))
    result = compare(args.baseline, args.candidate, region, evaluate, args.grid)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
