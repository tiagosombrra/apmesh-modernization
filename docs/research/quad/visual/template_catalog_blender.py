"""Append a native template gallery to a copy of an existing Blender history.

Blender --background source.blend --python this-file -- --catalog catalog.json
--output new-file.blend. The original file is never overwritten.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Euler, Vector


def snapshot(scene):
    return [(obj.name, [tuple(v.co) for v in obj.data.vertices],
             [tuple(p.vertices) for p in obj.data.polygons])
            for obj in scene.objects if obj.type == "MESH"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    original = Path(bpy.data.filepath)
    output = args.output.resolve()
    if not original.is_file() or output.exists() or output == original.resolve():
        raise ValueError("Require an existing source history and a new output file")
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    if catalog["schema"] != "apmesh.quad.native_template_catalog.v1" or len(catalog["panels"]) != 6:
        raise ValueError("Expected the six-family native catalog")
    original_hash = hashlib.sha256(original.read_bytes()).hexdigest()
    old_scenes = {scene.name: snapshot(scene) for scene in bpy.data.scenes}
    old_scene_names = list(old_scenes)
    name = "Template catalog - TRI and QUAD"
    if name in bpy.data.scenes:
        raise ValueError("Template gallery already exists")
    scene = bpy.data.scenes.new(name)
    bpy.context.window.scene = scene

    def material(name, color):
        value = bpy.data.materials.new("Template gallery - " + name)
        value.diffuse_color = (*color, 1)
        return value

    orange = material("original TRI", (0.93, 0.47, 0.12))
    teal = material("experimental QUAD", (0.04, 0.67, 0.70))
    white = material("text and source nodes", (0.94, 0.96, 1))
    black = material("native edges", (0.025, 0.035, 0.045))
    yellow = material("split neighbor sides", (1, 0.77, 0.12))

    def label(text, x, y, size=0.16, color=white):
        data = bpy.data.curves.new(text, "FONT")
        data.body, data.size, data.align_x = text, size, "CENTER"
        data.materials.append(color)
        obj = bpy.data.objects.new("Catalog label - " + text, data)
        obj.location = (x, y, 0.06)
        scene.collection.objects.link(obj)

    def lines(name, segments, color, radius=0.007):
        data = bpy.data.curves.new(name, "CURVE")
        data.dimensions = "3D"
        data.bevel_depth, data.bevel_resolution = radius, 1
        data.materials.append(color)
        for a, b in segments:
            spline = data.splines.new("POLY")
            spline.points.add(1)
            spline.points[0].co = (*a, 1)
            spline.points[1].co = (*b, 1)
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)

    records = []
    descriptions = ["No split sides", "1 split side", "2 opposite sides",
                    "2 adjacent sides", "3 split sides", "4 split sides"]
    label("Native template catalog | source families T1-T6", 0, 4.15, 0.31)
    label("Original TRI above | experimental QUAD below | same neighbor signature",
          0, 3.7, 0.18)
    size = 1.8
    for column, panel in enumerate(catalog["panels"]):
        x = (column - 2.5) * 2.75
        label(panel["type"], x, 3.12, 0.27)
        label(descriptions[column], x, 2.78, 0.16)
        for kind, y, color in (("tri", 1.0, orange), ("quad", -2.35, teal)):
            value = panel[kind]
            coordinates = [(x + (u - 0.5) * size, y + (v - 0.5) * size, 0)
                           for u, v in value["vertices"]]
            data = bpy.data.meshes.new(panel["type"] + " native " + kind.upper())
            data.from_pydata(coordinates, [], value["faces"])
            data.materials.append(color)
            data.update()
            obj = bpy.data.objects.new(data.name, data)
            obj["source_sha"] = catalog["source_sha"]
            obj["native_template_family"] = panel["type"]
            obj["source_split_mask"] = panel["split_mask"]
            obj["display_only"] = True
            obj["point_rule"] = "none" if kind == "tri" else catalog["point_rule"]
            scene.collection.objects.link(obj)
            edges = {tuple(sorted((a, b))) for face in value["faces"]
                     for a, b in zip(face, face[1:] + face[:1])}
            lines(data.name + " edges", [(tuple((*coordinates[a][:2], 0.02)),
                                          tuple((*coordinates[b][:2], 0.02)))
                                         for a, b in sorted(edges)], black)
            dots, disks = [], []
            for px, py, _ in coordinates:
                start = len(dots)
                dots.extend((px + 0.020 * math.cos(i * math.tau / 12),
                             py + 0.020 * math.sin(i * math.tau / 12), 0.045)
                            for i in range(12))
                disks.append(tuple(range(start, start + 12)))
            points = bpy.data.meshes.new(data.name + " vertices")
            points.from_pydata(dots, [], disks)
            points.materials.append(white)
            scene.collection.objects.link(bpy.data.objects.new(points.name, points))
            corners = [(x-size/2, y-size/2, 0.04), (x+size/2, y-size/2, 0.04),
                       (x+size/2, y+size/2, 0.04), (x-size/2, y+size/2, 0.04)]
            split_edges = [(corners[i], corners[(i+1) % 4]) for i in range(4)
                           if panel["split_mask"] & (1 << i)]
            if split_edges:
                lines(data.name + " split sides", split_edges, yellow, 0.013)
            title = "Original TRI" if kind == "tri" else "QUAD - vertex mean"
            label(title, x, y + 1.13, 0.16, color)
            label(f"{len(value['faces'])} {kind.upper()} | {len(value['vertices'])} nodes",
                  x, y - 1.16, 0.16)
            records.append({"object": obj.name, "type": panel["type"], "kind": kind,
                            "nodes": len(value["vertices"]), "faces": len(value["faces"])})
    label("Yellow: side adjacent to two finer cells | white dots: actual emitted vertices",
          0, -4.05, 0.17)
    label("Canonical native examples; quality branches and rotations can change diagonals",
          0, -4.4, 0.16)
    label("Exterior AFT triangles are generated dynamically; they are not fixed templates",
          0, -4.75, 0.16)
    label("Other scene: original analytic model and TRI / QUAD-TRI generation steps",
          0, -5.1, 0.17)
    for old_name, before in old_scenes.items():
        if snapshot(bpy.data.scenes[old_name]) != before:
            raise ValueError("Existing generation mesh changed")
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            view = area.spaces.active
            view.shading.type, view.shading.color_type = "SOLID", "MATERIAL"
            view.overlay.show_floor = view.overlay.show_cursor = False
            view.overlay.show_axis_x = view.overlay.show_axis_y = False
            view.region_3d.view_rotation = Euler((0, 0, 0)).to_quaternion()
            view.region_3d.view_location = Vector((0, -0.4, 0))
            view.region_3d.view_distance = 13.5
            view.region_3d.view_perspective = "ORTHO"
    provenance = {"blender": bpy.app.version_string,
                  "catalog_sha256": hashlib.sha256(args.catalog.read_bytes()).hexdigest(),
                  "original_blend_sha256": original_hash, "original_scenes": old_scene_names,
                  "original_mesh_geometry_unchanged": True, "gallery_scene": scene.name,
                  "source_sha": catalog["source_sha"], "panels": records,
                  "scope": catalog["scope"], "aft_note": catalog["aft_note"]}
    text = bpy.data.texts.new("Native template gallery provenance")
    text.write(json.dumps(provenance, indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    if hashlib.sha256(original.read_bytes()).hexdigest() != original_hash:
        raise ValueError("Original history file changed")
    output.with_suffix(".json").write_text(json.dumps(provenance, indent=2) + "\n",
                                          encoding="utf-8", newline="\n")
    print("NATIVE_TEMPLATE_GALLERY_SAVED", output)


if __name__ == "__main__":
    main()
