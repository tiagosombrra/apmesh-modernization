"""Export per-stage error and per-element quality of the controlled Bezier archive.

Read-only diagnostics: no generator, acceptance rule or source mesh is modified.
The source evaluator is explicitly limited to builtin:curva_bezier.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests/quad"))
from independent_common_grid import barycentric, inverse_bilinear, load_physical_obj
from test_m4_real_model_hybrid import golden


def delta(a, b):
    return tuple(x-y for x, y in zip(a, b))


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def norm(a):
    return math.sqrt(dot(a, a))


def source_normal(uv):
    _, du, dv = golden(*uv)
    return cross(du, dv)


def element_quality(xyz, uv, face, normal_at=source_normal):
    if len(face) not in (3, 4) or len(set(face)) != len(face):
        raise ValueError("Invalid reporting element")
    points = [xyz[i] for i in face]
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:]+points[:1])]
    if not all(math.isfinite(x) and x > 1e-14 for x in lengths):
        raise ValueError("Nonfinite or degenerate reporting edge")
    angles, corners, uv_angles = [], [], []
    for k, point in enumerate(points):
        a, b = delta(points[(k+1) % len(face)], point), delta(points[(k-1) % len(face)], point)
        normal = normal_at(uv[face[k]])
        denominator = norm(a)*norm(b)*norm(normal)
        if not math.isfinite(denominator) or denominator <= 0:
            raise ValueError("Invalid source normal")
        jac = dot(cross(a, b), normal)/denominator
        if not math.isfinite(jac) or jac <= 0:
            raise ValueError("Inverted physical reporting corner")
        corners.append(jac)
        angles.append(math.degrees(math.atan2(norm(cross(a, b)), dot(a, b))))
        at = uv[face[k]]
        ua = delta(uv[face[(k+1) % len(face)]], at)
        ub = delta(uv[face[(k-1) % len(face)]], at)
        det = ua[0]*ub[1]-ua[1]*ub[0]
        if det <= 0:
            raise ValueError("Nonconvex UV reporting element")
        uv_angles.append(math.degrees(math.atan2(det, dot(ua, ub))))
    tri_q = None
    if len(face) == 3:
        twice = norm(cross(delta(points[1], points[0]), delta(points[2], points[0])))
        tri_q = 2*math.sqrt(3)*twice/sum(x*x for x in lengths)
    return dict(kind="TRI" if len(face) == 3 else "QUAD", tri_q=tri_q,
                quad_corner_jacobian=min(corners) if len(face) == 4 else None,
                min_angle_xyz=min(angles), max_angle_xyz=max(angles),
                edge_ratio_xyz=max(lengths)/min(lengths),
                S_uv=1+max(abs(x-90) for x in uv_angles)/90 if len(face) == 4 else None,
                S_xyz=1+max(abs(x-90) for x in angles)/90 if len(face) == 4 else None)


def geometry_error(xyz, uv, faces, grid=24):
    """Same fixed sites and interpolation as the retained mixed-only oracle.

    This reporting routine also supports pure TRI and pure QUAD. The existing
    mixed-region validation contract is intentionally left unchanged.
    """
    if not 4 <= grid <= 256:
        raise ValueError("Unsupported reporting grid")
    boxes = [(min(uv[i][0] for i in f), max(uv[i][0] for i in f),
              min(uv[i][1] for i in f), max(uv[i][1] for i in f)) for f in faces]
    squared = weighted = area = maximum = 0.0
    visits = {"TRI": 0, "QUAD": 0}
    for iy in range(grid):
        v = (iy+0.5)/grid
        for ix in range(grid):
            u = (ix+0.5)/grid
            for face, (x0, x1, y0, y1) in zip(faces, boxes):
                if not x0-1e-13 <= u <= x1+1e-13 or not y0-1e-13 <= v <= y1+1e-13:
                    continue
                polygon = [uv[i] for i in face]
                if all((b[0]-a[0])*(v-a[1])-(b[1]-a[1])*(u-a[0]) >= -1e-12
                       for a, b in zip(polygon, polygon[1:]+polygon[:1])):
                    break
            else:
                raise ValueError("Uncovered reporting source site")
            weights = barycentric((u, v), *polygon) if len(face) == 3 else inverse_bilinear(polygon, (u, v))
            approximate = [sum(w*xyz[i][axis] for w, i in zip(weights, face)) for axis in range(3)]
            exact, du, dv = golden(u, v)
            error = sum((a-b)**2 for a, b in zip(exact, approximate))
            jacobian = norm(cross(du, dv))
            if not math.isfinite(error) or not math.isfinite(jacobian) or jacobian <= 0:
                raise ValueError("Invalid source error observation")
            squared += error
            weighted += error*jacobian
            area += jacobian
            maximum = max(maximum, math.sqrt(error))
            visits["TRI" if len(face) == 3 else "QUAD"] += 1
    return dict(grid=grid, sample_count=grid*grid, max_xyz=maximum,
                rms_uv=math.sqrt(squared/(grid*grid)), rms_source_area=math.sqrt(weighted/area),
                tri_sites=visits["TRI"], quad_sites=visits["QUAD"])


def summarize_elements(xyz, uv, faces):
    uses = {}
    for face in faces:
        for a, b in zip(face, face[1:]+face[:1]):
            key = tuple(sorted((a, b)))
            uses[key] = uses.get(key, 0)+1
    if any(n > 2 for n in uses.values()):
        raise ValueError("Nonmanifold reporting incidence")
    elements = []
    for i, face in enumerate(faces):
        item = element_quality(xyz, uv, face)
        item.update(face_id=i+1, vertices=[x+1 for x in face],
                    boundary=any(uses[tuple(sorted((a, b)))] == 1
                                 for a, b in zip(face, face[1:]+face[:1])))
        elements.append(item)
    def stats(key):
        values = [x[key] for x in elements if x[key] is not None]
        return dict(count=len(values), minimum=min(values) if values else None,
                    mean=statistics.fmean(values) if values else None)
    return dict(tri_q=stats("tri_q"), quad_corner_jacobian=stats("quad_corner_jacobian"),
                min_angle_xyz=min(x["min_angle_xyz"] for x in elements),
                max_edge_ratio_xyz=max(x["edge_ratio_xyz"] for x in elements),
                boundary_min_angle_xyz=min((x["min_angle_xyz"] for x in elements if x["boundary"]), default=None)), elements


def reference_metrics(archive):
    prefix = archive.with_suffix("")
    files = list(prefix.parent.glob(prefix.name+"_n.process__metrics_rank_*.csv"))
    if not files:
        return {}, None
    if len(files) != 1:
        raise ValueError("Ambiguous serial reference metrics")
    with files[0].open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result = {}
    for row in rows:
        key = int(row["step"]), int(row["retry_attempt"])
        if key in result:
            raise ValueError("Duplicate reference step/retry metrics")
        result[key] = row
    return result, dict(file=files[0].name, sha256=hashlib.sha256(files[0].read_bytes()).hexdigest())


def collect_archive(archive, grid=24):
    archive = Path(archive).resolve()
    with (archive/"manifest.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Empty reporting manifest")
    references, reference_source = reference_metrics(archive)
    result, seen = [], set()
    for row in rows:
        scope = tuple(row[x] for x in ("step", "epoch", "retry", "domain_generation", "reference_tri_accepted"))
        if scope in seen:
            raise ValueError("Duplicate reporting stage")
        seen.add(scope)
        tri_path = (archive/row["tri_obj"]).resolve()
        if tri_path.parent != archive:
            raise ValueError("Foreign TRI archive path")
        tx, _, tf = load_physical_obj(tri_path)
        native_key = (int(row["step"]), int(row["retry"]))
        if native_key == (0, -1) and row["epoch"] == "0" and row["reason"] == "initial":
            native_key = (0, 0)  # The initial manifest has no retry; the original log records zero.
        native = references.get(native_key)
        adaptive = None
        if native and row["reference_tri_accepted"] == "1":
            if int(native["nodes"]) != len(tx) or int(native["elements"]) != len(tf):
                raise ValueError("Reference metric belongs to another mesh")
            adaptive = float(native["error_global_surface_curvature"])
            if not math.isfinite(adaptive):
                raise ValueError("Invalid adaptive reference error")
        for scheme, key in (("TRI", "tri_obj"), ("QUAD_TRI", "quad_tri_obj")):
            path = (archive/row[key]).resolve()
            if path.parent != archive:
                raise ValueError("Foreign reporting archive path")
            xyz, uv, faces = load_physical_obj(path)
            # The existing viewer and this report evaluate the same named source.
            for point, at in zip(xyz, uv):
                if any(t < 0 or t > 1 for t in at) or math.dist(point, golden(*at)[0]) > 2e-7*max(1, norm(point)):
                    raise ValueError("Report requires builtin:curva_bezier source coordinates")
            quality, elements = summarize_elements(xyz, uv, faces)
            result.append(dict(step=int(row["step"]), epoch=int(row["epoch"]), retry=int(row["retry"]),
                               domain_generation=int(row["domain_generation"]),
                               reference_tri_accepted=row["reference_tri_accepted"] == "1", reason=row["reason"],
                               scheme=scheme, file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                               nodes=len(xyz), triangles=sum(len(f) == 3 for f in faces),
                               quads=sum(len(f) == 4 for f in faces), geometry_error=geometry_error(xyz, uv, faces, grid),
                               quality=quality, elements=elements,
                               tri_reference_adaptive_error=adaptive,
                               tri_reference_native_quality={k: float(native[k]) for k in ("quality_min", "quality_mean") if k in native} if adaptive is not None else None,
                               mixed_adaptive_error=None))
    return dict(schema="apmesh.quad.generation_metrics.v1", source="builtin:curva_bezier",
                manifest_sha256=hashlib.sha256((archive/"manifest.csv").read_bytes()).hexdigest(),
                reference_metrics_source=reference_source, stages=result,
                definitions=dict(geometry_error="Sampled XYZ distance on fixed UV sites; source-area weighted RMS; model units",
                                 adaptive_error="Original TRI relative 3D surface-curvature error; reference only; mixed estimator unavailable",
                                 tri_reference_native_quality="Original TRI quality as logged; separate from the diagnostic TRI area/edge score and QUAD corner Jacobian",
                                 tri_q="4*sqrt(3)*area/sum(edge_length_squared); equilateral TRI=1",
                                 quad_corner_jacobian="Minimum signed corner scaled Jacobian using analytic source normals; orthogonal aligned corners=1; not a continuous bound or aspect ratio",
                                 angle="Physical XYZ corner angle, degrees",
                                 edge_ratio="Longest/shortest physical edge; smaller is better; ideal equal lengths=1",
                                 scope="Diagnostics only; TRI and QUAD quality scales remain separate; no new acceptance threshold"))


def write_report(report, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output/"metrics.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    fields = ["step", "epoch", "retry", "domain_generation", "reference_tri_accepted", "scheme", "nodes", "triangles", "quads",
              "rms_source_area", "max_xyz", "tri_q_min", "tri_q_mean", "quad_J_min", "quad_J_mean", "min_angle_xyz",
              "boundary_min_angle_xyz", "max_edge_ratio_xyz", "tri_reference_adaptive_error", "mixed_adaptive_error", "tri_reference_logged_quality_min", "tri_reference_logged_quality_mean", "file", "sha256"]
    with (output/"metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fields)
        writer.writeheader()
        for s in report["stages"]:
            row = {k: s[k] for k in fields if k in s}
            row.update(rms_source_area=s["geometry_error"]["rms_source_area"], max_xyz=s["geometry_error"]["max_xyz"],
                       tri_q_min=s["quality"]["tri_q"]["minimum"], tri_q_mean=s["quality"]["tri_q"]["mean"],
                       quad_J_min=s["quality"]["quad_corner_jacobian"]["minimum"], quad_J_mean=s["quality"]["quad_corner_jacobian"]["mean"],
                       min_angle_xyz=s["quality"]["min_angle_xyz"], boundary_min_angle_xyz=s["quality"]["boundary_min_angle_xyz"],
                       max_edge_ratio_xyz=s["quality"]["max_edge_ratio_xyz"])
            row.update(tri_reference_logged_quality_min=(s["tri_reference_native_quality"] or {}).get("quality_min"),
                       tri_reference_logged_quality_mean=(s["tri_reference_native_quality"] or {}).get("quality_mean"))
            writer.writerow(row)
    with (output/"elements.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["step", "epoch", "retry", "scheme", "face_id", "kind", "boundary", "vertices", "tri_q", "quad_corner_jacobian", "S_uv", "S_xyz", "min_angle_xyz", "max_angle_xyz", "edge_ratio_xyz"]
        writer = csv.DictWriter(handle, fields)
        writer.writeheader()
        for s in report["stages"]:
            for element in s["elements"]:
                row = {k: s[k] for k in ("step", "epoch", "retry", "scheme")}
                row.update(element, vertices="|".join(map(str, element["vertices"])))
                writer.writerow(row)
    def show(x):
        return "N/A" if x is None else f"{x:.7g}"
    lines = ["# Per-stage geometry error and element quality", "",
             "Source: builtin:curva_bezier. Geometry errors use576 fixed UV sites by default and model coordinate units.",
             "The original adaptive curvature error is a TRI reference; mixed adaptive error is unavailable.", "",
             "| Step | Scheme | Nodes | TRI | QUAD | Geometry RMS | Geometry max | TRI reference curvature error |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for stage in report["stages"]:
        error = stage["geometry_error"]
        lines.append(f"| {stage['step']} | {stage['scheme']} | {stage['nodes']} | {stage['triangles']} | {stage['quads']} | {show(error['rms_source_area'])} | {show(error['max_xyz'])} | {show(stage['tri_reference_adaptive_error'])} |")
    lines += ["", "TRI area-Q and QUAD corner J are separate diagnostic scales; both have ideal reference1.",
              "Corner J does not measure aspect ratio or continuous bilinear validity; inspect the edge ratio too.", "",
              "| Step | Scheme | TRI Q min | TRI Q mean | QUAD J min | QUAD J mean | Minimum angle (deg) | Maximum edge ratio |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for stage in report["stages"]:
        q = stage["quality"]
        lines.append(f"| {stage['step']} | {stage['scheme']} | {show(q['tri_q']['minimum'])} | {show(q['tri_q']['mean'])} | {show(q['quad_corner_jacobian']['minimum'])} | {show(q['quad_corner_jacobian']['mean'])} | {show(q['min_angle_xyz'])} | {show(q['max_edge_ratio_xyz'])} |")
    lines += ["", "Per-element values and source face IDs are in elements.csv; full definitions, native logged TRI quality, source hashes and stage identity are in metrics.json.",
              "These observations do not change acceptance, smoothing, node placement or the generator.", ""]
    (output/"results.md").write_text("\n".join(lines), encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--grid", type=int, default=24)
    args = parser.parse_args()
    report = collect_archive(args.archive, args.grid)
    write_report(report, args.output)
    print(json.dumps(dict(status="written", stages=len(report["stages"]), output=str(args.output))))


if __name__ == "__main__":
    main()
