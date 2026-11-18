"""Create a Blender inspection scene from the actual per-step generation archive.

Run with Blender: --background --factory-startup --python <this-file> --
--archive <prefix.steps> --output <new-file.blend>.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Euler, Vector


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--metrics", type=Path, help="Existing generation_metrics.v1 JSON; otherwise compute and export beside the scene")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    archive, output = args.archive.resolve(), args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    rows = list(csv.DictReader((archive / "manifest.csv").open()))
    if not rows:
        raise ValueError("Empty generation archive")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests/quad"))
    from independent_common_grid import load_physical_obj
    from test_m4_real_model_hybrid import golden
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from quad_generation_metrics import collect_archive, write_report
    if args.metrics:
        metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
    else:
        metrics = collect_archive(archive)
        write_report(metrics, output.with_suffix(".metrics"))
    if metrics["schema"] != "apmesh.quad.generation_metrics.v1" or metrics["manifest_sha256"] != hashlib.sha256((archive/"manifest.csv").read_bytes()).hexdigest():
        raise ValueError("Metrics do not belong to this generation archive")
    measured = {(s["step"], s["epoch"], s["retry"], s["domain_generation"], s["reference_tri_accepted"], s["scheme"]): s for s in metrics["stages"]}
    if len(measured) != len(rows)*2:
        raise ValueError("Missing or duplicate measured stages")
    def number(value):
        return "N/A" if value is None else f"{value:.5g}"

    scene = bpy.context.scene
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    scene.name = "Original curvature flow - generation steps"

    def material(name, rgba):
        result = bpy.data.materials.new(name)
        result.diffuse_color = rgba
        return result

    teal = material("QUAD", (0.04, 0.64, 0.68, 1))
    amber = material("TRI", (0.92, 0.43, 0.08, 1))
    white = material("Analytic source - display guide", (0.95, 0.97, 1, 1))
    green = material("Accepted reference", (0.25, 0.95, 0.45, 1))
    red = material("Rejected reference", (1, 0.25, 0.2, 1))
    yellow = material("Discretized curve points", (1, 0.85, 0.1, 1))
    blue = material("Analytic model display", (0.18, 0.43, 0.85, 1))

    def label(body, x, y, size=0.15, color=white):
        data = bpy.data.curves.new(body, "FONT")
        data.body, data.size, data.align_x = body, size, "CENTER"
        obj = bpy.data.objects.new(body, data)
        scene.collection.objects.link(obj)
        obj.location = (x, y, 0.02)
        data.materials.append(color)

    def line(name, positions, color, radius):
        data = bpy.data.curves.new(name, "CURVE")
        data.dimensions = "3D"
        data.bevel_depth, data.bevel_resolution = radius, 1
        spline = data.splines.new("POLY")
        spline.points.add(len(positions)-1)
        for point, xyz in zip(spline.points, positions):
            point.co = (*xyz, 1)
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.show_in_front = True
        data.materials.append(color)

    # Dense evaluation is a display reference, never a generated/accepted mesh.
    analytic_x = -len(rows)*3.45/2
    grid = 64
    analytic_xyz = [golden(u/grid, v/grid)[0]
                    for v in range(grid+1) for u in range(grid+1)]
    analytic_faces = [(v*(grid+1)+u, v*(grid+1)+u+1,
                       (v+1)*(grid+1)+u+1, (v+1)*(grid+1)+u)
                      for v in range(grid) for u in range(grid)]
    analytic_mesh = bpy.data.meshes.new("Analytic source - display evaluation")
    analytic_mesh.from_pydata(analytic_xyz, [], analytic_faces)
    analytic_mesh.update()
    analytic_mesh.materials.append(blue)
    for face in analytic_mesh.polygons:
        face.use_smooth = True
    analytic_object = bpy.data.objects.new(analytic_mesh.name, analytic_mesh)
    scene.collection.objects.link(analytic_object)
    analytic_object.location = (analytic_x, 0, 0)
    analytic_object["display_reference_only"] = True
    analytic_object["sampling_grid"] = grid
    label("Analytic Bezier model", analytic_x, 1.45, 0.2, blue)
    label("Original source geometry", analytic_x, 1.2, 0.15)
    label("Display evaluation only", analytic_x, -1.3, 0.14)
    label("Not a generated/accepted mesh", analytic_x, -1.55, 0.12)

    records = []
    for column, row in enumerate(rows):
        x = (column + 1 - len(rows)/2) * 3.45
        accepted = row["reference_tri_accepted"] == "1"
        status = "ACCEPTED TRI reference" if accepted else "REJECTED TRI reference"
        label(f"Step {row['step']} | {status}", x, 4.1, 0.15, green if accepted else red)
        label(row["reason"], x, 3.9, 0.12)
        for key, y, title in (("tri_obj", 2.1, "Actual TRI state"),
                              ("quad_tri_obj", -2.8, "QUAD/TRI from this source")):
            path = archive / row[key]
            if path.parent != archive:
                raise ValueError("Foreign archive path")
            xyz, uv, faces = load_physical_obj(path)
            mesh = bpy.data.meshes.new(f"Step {row['step']} - {key}")
            mesh.from_pydata(xyz, [], faces)
            mesh.update()
            mesh.materials.append(teal)
            mesh.materials.append(amber)
            for polygon in mesh.polygons:
                polygon.material_index = 0 if len(polygon.vertices) == 4 else 1
                polygon.use_smooth = False
            obj = bpy.data.objects.new(mesh.name, mesh)
            scene.collection.objects.link(obj)
            obj.location = (x, y, 0)
            obj.show_wire, obj.show_all_edges = True, True
            obj["source_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            obj["reference_tri_accepted"] = accepted
            obj["mixed_adaptive_epochs"] = 0
            obj["presentation"] = "Translation only; no subdivision, smoothing or height scaling"
            scheme = "TRI" if key == "tri_obj" else "QUAD_TRI"
            scope = tuple(int(row[k]) for k in ("step", "epoch", "retry", "domain_generation")) + (accepted, scheme)
            observation = measured[scope]
            if observation["sha256"] != obj["source_sha256"] or len(observation["elements"]) != len(faces):
                raise ValueError("Measured geometry differs from displayed mesh")
            error, quality = observation["geometry_error"], observation["quality"]
            obj["geometry_rms_xyz"] = error["rms_source_area"]
            obj["geometry_max_xyz"] = error["max_xyz"]
            obj["quality_min_angle_xyz"] = quality["min_angle_xyz"]
            obj["quality_max_edge_ratio_xyz"] = quality["max_edge_ratio_xyz"]
            obj["element_metrics"] = json.dumps(observation["elements"])
            obj["tri_reference_adaptive_error"] = number(observation["tri_reference_adaptive_error"])
            label(f"Geom RMS {number(error['rms_source_area'])} | Max {number(error['max_xyz'])}", x, y-1.43, 0.115)
            label(f"TRI area-Q min/avg {number(quality['tri_q']['minimum'])} / {number(quality['tri_q']['mean'])}", x, y-1.62, 0.115)
            label(f"QUAD J min/avg {number(quality['quad_corner_jacobian']['minimum'])} / {number(quality['quad_corner_jacobian']['mean'])}", x, y-1.81, 0.115)
            label(f"Angle min {quality['min_angle_xyz']:.2f} deg | Edge ratio max {quality['max_edge_ratio_xyz']:.2f}", x, y-2.0, 0.115)
            if scheme == "TRI":
                label(f"TRI adaptive curvature E {number(observation['tri_reference_adaptive_error'])}", x, y+1.38, 0.115)
                native_q = observation.get("tri_reference_native_quality") or {}
                label(f"TRI logged quality min/avg {number(native_q.get('quality_min'))} / {number(native_q.get('quality_mean'))}", x, y+1.59, 0.11)
            else:
                label("Mixed adaptive error: N/A (not implemented)", x, y+1.38, 0.115)
            quads = sum(len(face) == 4 for face in faces)
            label(title, x, y+1.15, 0.14)
            label(f"{len(xyz)} nodes | {quads} QUAD | {len(faces)-quads} TRI", x, y-1.2, 0.13)
            guide = []
            for t in range(257):
                p = golden(t/256, 0)[0]
                guide.append((p[0]+x, p[1]+y, p[2]+0.006))
            line(f"Step {row['step']} analytic curved side - {key}", guide, white, 0.009)
            boundary = sorted((at[0], p) for at, p in zip(uv, xyz) if at[1] == 0)
            line(f"Step {row['step']} actual curved-side chords - {key}",
                 [(p[0]+x, p[1]+y, p[2]+0.012) for _, p in boundary], yellow, 0.012)
            records.append({"file": path.name, "sha256": obj["source_sha256"],
                            "nodes": len(xyz), "quads": quads,
                            "triangles": len(faces)-quads})

    trace = list(csv.DictReader((archive / "curve_stages.csv").open()))
    curve_rows = [r for r in trace if r["curve"] == "0" and r["step"] == "1"]
    counts = {r["stage"]: int(r["parameter_count"]) for r in curve_rows}
    label("White: analytic curved boundary | Yellow: actual mesh chords", 0, -5.15, 0.16)
    label(f"Step 1 curve points: curve pass {counts.get('curve_pass')} -> "
          f"surface pass {counts.get('surface_pass')} -> final {counts.get('final_budget')}",
          0, -5.4, 0.15)
    label("Original curvature workflow | mixed accepted adaptive epochs: 0", 0, -5.65, 0.14)
    label("Rejected proposals are displayed for inspection; they are not accepted states", 0, -5.9, 0.12)
    metrics_note = bpy.data.texts.new("Per-step error and element quality")
    metrics_note.write(json.dumps(metrics, indent=2))
    label("Geometry errors: 576 fixed UV sites; model units | Q and J are separate scales", 0, -6.15, 0.13)
    note = bpy.data.texts.new("Generation provenance")
    note.write(json.dumps({"artifacts": records, "manifest": rows,
                           "curve_stage_counts_step1": counts,
                           "analytic_guide": "257 display samples, +0.006 Z offset; not mesh nodes",
                           "analytic_model": "Original Bezier evaluation on a 64x64 display grid; not generated mesh",
                           "mesh_geometry": "Unmodified source coordinates; native Blender storage precision",
                           "mixed_feedback": False}, indent=2))
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            view = area.spaces.active
            view.shading.type, view.shading.color_type = "SOLID", "MATERIAL"
            view.overlay.show_floor = False
            view.overlay.show_axis_x = view.overlay.show_axis_y = False
            view.overlay.show_cursor = False
            view.region_3d.view_rotation = Euler((math.radians(8), 0, 0), "XYZ").to_quaternion()
            view.region_3d.view_location = Vector((0, -0.55, 0))
            view.region_3d.view_distance = max(17, (len(rows)+1)*4.2)
            view.region_3d.view_perspective = "ORTHO"
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    output.with_suffix(".json").write_text(json.dumps({"blender": bpy.app.version_string,
        "artifacts": records, "steps": len(rows), "mixed_adaptive_epochs": 0,
        "analytic_display_grid": grid, "error_quality_stages": len(metrics["stages"]),
        "metrics_manifest_sha256": metrics["manifest_sha256"]}, indent=2)+"\n")
    print("QUAD_GENERATION_SCENE_SAVED", output)


if __name__ == "__main__":
    main()
