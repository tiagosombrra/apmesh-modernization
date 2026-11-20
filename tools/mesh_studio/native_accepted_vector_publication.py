"""Source-attested original C++ accepted TRI UV-only vector publication.

Only the original retained postcommit C++ NDJSON, independently reaudited by
native_accepted_scene, can certify a real figure. An uploaded JSON alone is not
a source authentication. Drawn source samples are points, not welded seams.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .native_accepted_scene import (
    MAX_SCENE_BYTES, generate_original_scene_bundle,
)
from .verify_native_lineage import (
    SOURCE_MODELS, require, unique_fields, NativeLineageValidationError,
)

URI = "http://www.w3.org/2000/svg"
ET.register_namespace("", URI)
SCHEMA = "apmesh.meshstudio.v52.original_native_accepted_uv_vector.v1"
PACKAGE_SCHEMA = "apmesh.meshstudio.v52.original_native_accepted_publication.v1"
MAX_SVG_BYTES = 12_000_000
MAX_PUBLICATION_BYTES = 256_000
SOURCE_SHA = re.compile(r"^[a-f0-9]{64}$")


def _tag(name: str) -> str:
    return f"{{{URI}}}{name}"


def _digest(body: bytes) -> str:
    return sha256(body).hexdigest()


def _valid_identity(scene: dict, identity: dict) -> None:
    model = scene["model"]
    require(model in SOURCE_MODELS and identity["model"] == model and
            scene["accepted_native_step"] == identity["accepted_native_step"] and
            scene["source_ndjson_sha256"] == identity["source_ndjson_sha256"] and
            SOURCE_SHA.fullmatch(scene["source_ndjson_sha256"]) is not None,
            "v52_original_model_epoch_or_source_sha_mismatch")
    patches, curves = SOURCE_MODELS[model]
    require(scene["native_source_patches"] == patches and
            scene["native_source_curves"] == curves and
            identity["source_patch_count"] == patches and
            identity["source_curve_count"] == curves and
            scene["scientific_lod_qualified"] is False and
            identity["scientific_lod_qualified"] is False and
            identity["physical_node_welding_certified"] is False and
            identity["cross_epoch_lineage_certified"] is False and
            scene["cross_epoch_lineage_certified"] is False,
            "v52_false_source_or_scientific_admission")
    for key in ("original_model_input_sha256", "original_config_sha256"):
        require(type(identity.get(key)) is str and
                SOURCE_SHA.fullmatch(identity[key]) is not None,
                "v52_missing_original_input_or_config_digest")
    require(len(scene["source_patch_face_counts"]) == patches and
            len(scene["native_faces"]) == scene["native_tri_faces"] and
            0 < scene["native_tri_faces"] <= 12_000 and
            sum(scene["source_patch_face_counts"]) == scene["native_tri_faces"],
            "v52_original_native_face_inventory_invalid")


def _native_source_index(scene: dict) -> tuple[dict, dict]:
    face_owners: dict[int, list] = defaultdict(list)
    corners: dict[tuple[int, int], tuple[tuple[float, ...], tuple[float, ...]]] = {}
    slots = set()
    for face in scene["native_faces"]:
        require(type(face) is list and len(face) == 5 and
                type(face[4]) is list and len(face[4]) == 3,
                "v52_invalid_original_face_record")
        patch, native_patch, element_slot, native_element, vertices = face
        require(all(type(v) is int and 0 <= v <= 2**53-1
                    for v in (patch, native_patch, element_slot, native_element)) and
                patch < scene["native_source_patches"] and
                (patch, element_slot) not in slots,
                "v52_native_patch_face_key_mismatch")
        slots.add((patch, element_slot))
        for node in vertices:
            require(type(node) is list and len(node) == 6 and
                    type(node[0]) is int and 0 <= node[0] <= 2**53-1 and
                    all(type(z) in (int, float) and math.isfinite(z)
                        for z in node[1:]),
                    "v52_invalid_original_native_node_uv_xyz")
            identity = (patch, node[0])
            triple = (tuple(node[1:4]), tuple(node[4:6]))
            if identity in corners:
                require(corners[identity] == triple,
                        "v52_native_same_patch_node_changed_uv_xyz")
            corners[identity] = triple
            require(all(-1e-8 <= v <= 1+1e-8 for v in node[4:6]),
                    "v52_native_patch_uv_outside_original_unit_square")
        x1, y1 = vertices[0][4:6]
        x2, y2 = vertices[1][4:6]
        x3, y3 = vertices[2][4:6]
        signed = (x2-x1)*(y3-y1) - (y2-y1)*(x3-x1)
        require(math.isfinite(signed) and abs(signed) > 1e-13,
                "v52_original_native_face_uv_degenerate")
        face_owners[patch].append(face)
    require(set(face_owners) == set(range(scene["native_source_patches"])) and
            all(len(face_owners[p]) == scene["source_patch_face_counts"][p] and
                set(face[2] for face in face_owners[p]) ==
                set(range(len(face_owners[p])))
                for p in face_owners),
            "v52_original_native_patch_face_slots_missing")
    return face_owners, corners


def _qualified_sample_markers(identity: dict, corners: dict) -> dict[int, list]:
    markers: dict[int, list[tuple[int, int, tuple[float, float]]]] = defaultdict(list)
    curve_slots = set()
    for curve in identity["qualified_shared_source_curves"]:
        source_curve = curve["source_curve_slot"]
        require(type(source_curve) is int and source_curve not in curve_slots and
                0 <= source_curve < identity["source_curve_count"] and
                curve["physical_node_welding_certified"] is False,
                "v52_original_shared_curve_fan_forged")
        curve_slots.add(source_curve)
        patch_slots = curve["patch_slots"]
        require(len(patch_slots) >= 2 and len(set(patch_slots)) == len(patch_slots),
                "v52_original_shared_curve_patch_incidence_forged")
        require(len(curve["sample_groups"]) == curve["sample_count"] and
                curve["sample_count"] >= 2,
                "v52_original_sample_inventory_changed")
        for ordinal, group in enumerate(curve["sample_groups"]):
            require(group["ordinal"] == ordinal and
                    sorted(m["patch_slot"] for m in group["members"]) == patch_slots,
                    "v52_original_shared_curve_sample_owner_changed")
            for m in group["members"]:
                patch = m["patch_slot"]
                key = (patch, m["native_node_id"])
                require(key in corners, "v52_source_curve_sample_missing_native_corner")
                xyz, uv = corners[key]
                require(len(m["original_xyz"]) == 3 and
                        math.dist(xyz, m["original_xyz"]) <= 1e-7 and
                        math.isfinite(group["canonical_t"]) and
                        -1e-9 <= group["canonical_t"] <= 1+1e-9,
                        "v52_shared_curve_sample_forged_xyz_or_parameter")
                markers[patch].append((source_curve, ordinal, uv))
    require(curve_slots, "v52_no_qualified_original_shared_curve")
    return markers


def _fmt(n: float) -> str:
    require(math.isfinite(n), "v52_nonfinite_vector_geometry")
    return f"{n:.8f}"


def render_source_accepted_uv_svg(scene: dict, identity: dict) -> tuple[bytes, dict]:
    """Render audited original accepted faces, not original face pixels or LOD."""
    _valid_identity(scene, identity)
    face_owners, corners = _native_source_index(scene)
    markers = _qualified_sample_markers(identity, corners)
    model = scene["model"]
    columns = 2 if model == "eistute" else 7
    patches = scene["native_source_patches"]
    rows = math.ceil(patches / columns)
    cell_w = 440 if columns == 2 else 210
    cell_h = 325 if columns == 2 else 230
    chart_size = 270 if columns == 2 else 158
    pad_l, pad_t, pad_b = 35, 108, 75
    width = columns * cell_w + 2 * pad_l
    height = rows * cell_h + pad_t + pad_b
    width_mm, height_mm = (178, 140) if model == "eistute" else (190, 160)
    root = ET.Element(_tag("svg"), {
        "width": f"{width_mm}mm", "height": f"{height_mm}mm",
        "viewBox": f"0 0 {width} {height}", "version": "1.1",
        "role": "img", "aria-label": (
            f"Accepted source-native TRI {model} patch-local UV chart, step "
            f"{scene['accepted_native_step']}"),
        "data-schema": SCHEMA, "data-model": model,
        "data-original-source-ndjson-sha256": scene["source_ndjson_sha256"],
        "data-original-accepted-step": str(scene["accepted_native_step"]),
        "data-physical-welding-certified": "false",
        "data-scientific-lod-qualified": "false",
    })
    ET.SubElement(root, _tag("title")).text = (
        f"{model.upper()} — C++ original accepted TRI step {scene['accepted_native_step']}")
    ET.SubElement(root, _tag("desc")).text = (
        "True-vector local patch UV from independently revalidated real original "
        "C++ accepted postcommit NDJSON. Source shared-curve markers are only "
        "actual native corner samples; no welding, surface error bound or LOD.")
    ET.SubElement(root, _tag("rect"), {
        "width": str(width), "height": str(height), "fill": "#ffffff"})
    ET.SubElement(root, _tag("text"), {
        "x": str(pad_l), "y": "44", "font-size": "30",
        "font-family": "DejaVu Sans, sans-serif", "font-weight": "bold",
        "fill": "#102431"}).text = (
            f"{model.upper()} | Original accepted native TRI, step {scene['accepted_native_step']}")
    ET.SubElement(root, _tag("text"), {
        "x": str(pad_l), "y": "78", "font-size": "15",
        "font-family": "DejaVu Sans, sans-serif",
        "fill": "#365363"}).text = (
            f"{scene['native_tri_faces']} TRI | {patches} original patches | "
            f"{scene['native_source_curves']} original curves | UV per patch")
    for patch in range(patches):
        row, column = divmod(patch, columns)
        x0 = pad_l + column * cell_w
        y0 = pad_t + row * cell_h
        plot_x = x0 + (cell_w - chart_size)/2
        plot_y = y0 + 38
        panel = ET.SubElement(root, _tag("g"), {
            "data-original-patch-slot": str(patch),
            "data-original-native-patch-id": str(face_owners[patch][0][1]),
            "data-original-face-count": str(len(face_owners[patch])),
        })
        ET.SubElement(panel, _tag("text"), {
            "x": _fmt(x0+12), "y": _fmt(y0+18), "font-size": "15",
            "font-family": "DejaVu Sans, sans-serif",
            "fill": "#1f3e4e"}).text = (
                f"Patch {patch} | {len(face_owners[patch])} TRI")
        ET.SubElement(panel, _tag("rect"), {
            "x": _fmt(plot_x), "y": _fmt(plot_y),
            "width": str(chart_size), "height": str(chart_size),
            "fill": "#f7fafc", "stroke": "#8b9ba8", "stroke-width": "0.8",
        })

        def point(uv: tuple[float, float] | list[float]) -> str:
            u, v = uv
            return _fmt(plot_x + chart_size*u) + "," + _fmt(plot_y + chart_size*(1-v))

        native_patch_ids = {f[1] for f in face_owners[patch]}
        require(len(native_patch_ids) == 1, "v52_source_patch_native_id_inconsistent")
        for face in face_owners[patch]:
            triangles = face[4]
            ET.SubElement(panel, _tag("polygon"), {
                "points": " ".join(point(node[4:6]) for node in triangles),
                "fill": "#dcecf2", "stroke": "#244d62",
                "stroke-width": "0.25" if columns == 7 else "0.65",
                "data-original-patch-slot": str(patch),
                "data-native-patch-id": str(face[1]),
                "data-original-element-slot": str(face[2]),
                "data-native-element-id": str(face[3]),
                "data-original-native-node-ids": ",".join(str(n[0]) for n in triangles),
                "data-original-local-uv": ";".join(
                    f"{node[4]:.17g},{node[5]:.17g}" for node in triangles),
            })
        for source_slot, ordinal, uv in markers.get(patch, []):
            cx, cy = point(uv).split(",")
            ET.SubElement(panel, _tag("circle"), {
                "cx": cx, "cy": cy,
                "r": "2.6" if columns == 7 else "3.2",
                "fill": "#bd503f", "stroke": "#fff", "stroke-width": "0.4",
                "data-source-curve-slot": str(source_slot),
                "data-original-source-sample-ordinal": str(ordinal),
                "data-original-patch-slot": str(patch),
                "data-sample-identity": "original-native-corner-not-physical-welding",
            })
    ET.SubElement(root, _tag("text"), {
        "x": str(pad_l), "y": str(height-35), "font-size": "14",
        "font-family": "DejaVu Sans, sans-serif", "fill": "#39515f"}).text = (
            "Original accepted source UV | red dots: verified curve sample nodes "
            "(not physical welding) | no cross-epoch LOD")
    body = ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"
    require(len(body) <= MAX_SVG_BYTES, "v52_vector_figure_size_bound")
    info = {
        "model": model, "accepted_native_step": scene["accepted_native_step"],
        "original_source_ndjson_sha256": scene["source_ndjson_sha256"],
        "original_model_input_sha256": identity["original_model_input_sha256"],
        "original_config_sha256": identity["original_config_sha256"],
        "original_native_tri_faces": scene["native_tri_faces"],
        "original_source_patch_count": patches,
        "original_source_curve_count": scene["native_source_curves"],
        "original_patch_face_counts": scene["source_patch_face_counts"],
        "source_shared_curve_slots": sorted(
            c["source_curve_slot"] for c in identity["qualified_shared_source_curves"]),
        "observed_source_curve_sample_marker_count": sum(map(len, markers.values())),
        "original_source_face_identity": scene["face_identity"],
        "original_native_node_identity": scene["corner_identity"],
        "width_mm": width_mm, "height_mm": height_mm,
        "svg_filename": f"{model}-accepted-step{scene['accepted_native_step']}-uv.svg",
        "svg_sha256": _digest(body), "svg_size_bytes": len(body),
        "source_revalidated_from_original_postcommit_raw_ndjson": True,
        "physical_node_welding_certified": False,
        "cross_epoch_face_lineage_certified": False,
        "continuous_geometric_error_bound_certified": False,
        "scientific_lod_qualified": False,
    }
    verify_svg_original_face_identity(body, scene, info)
    return body, info


def verify_svg_original_face_identity(body: bytes, scene: dict, report: dict) -> None:
    """Recheck every SVG native source key and exact original UV numeric corner."""
    require(len(body) <= MAX_SVG_BYTES and b"<!DOCTYPE" not in body.upper(),
            "v52_svg_oversized_or_doctype")
    root = ET.fromstring(body)
    require(root.tag == _tag("svg") and root.attrib.get("data-schema") == SCHEMA and
            root.attrib.get("data-model") == scene["model"] and
            root.attrib.get("data-original-source-ndjson-sha256") ==
            scene["source_ndjson_sha256"] and
            root.attrib.get("data-original-accepted-step") ==
            str(scene["accepted_native_step"]) and
            root.attrib.get("data-physical-welding-certified") == "false" and
            root.attrib.get("data-scientific-lod-qualified") == "false" and
            _digest(body) == report["svg_sha256"],
            "v52_original_vector_source_or_figure_sha_mismatch")
    expected = {
        (f[0], f[2], f[3]): (
            f[1], [n[0] for n in f[4]],
            [[n[4], n[5]] for n in f[4]],
        ) for f in scene["native_faces"]
    }
    seen = set()
    panel_slots = set()
    by_patch = defaultdict(int)
    sample_markers = 0
    for element in root.iter():
        local = element.tag.rsplit("}", 1)[-1]
        require(local not in ("image", "script", "foreignObject", "use",
                              "filter", "feImage", "style", "animate",
                              "animateTransform", "iframe"),
                "v52_raster_active_or_external_svg_content")
        for attr, value in element.attrib.items():
            require(not attr.endswith("href") and
                    not attr.startswith("on") and
                    "url(" not in value and "data:" not in value,
                    "v52_active_external_vector_dependency")
        if local == "g" and "data-original-patch-slot" in element.attrib:
            patch = int(element.attrib["data-original-patch-slot"])
            require(patch not in panel_slots and
                    element.attrib.get("data-original-face-count") ==
                    str(scene["source_patch_face_counts"][patch]),
                    "v52_original_patch_chart_inventory_mismatch")
            panel_slots.add(patch)
        if local == "circle" and "data-original-source-sample-ordinal" in element.attrib:
            require(element.attrib.get("data-sample-identity") ==
                    "original-native-corner-not-physical-welding",
                    "v52_false_source_sample_welding")
            sample_markers += 1
        if local == "polygon":
            key = (
                int(element.attrib["data-original-patch-slot"]),
                int(element.attrib["data-original-element-slot"]),
                int(element.attrib["data-native-element-id"]),
            )
            require(key in expected and key not in seen,
                    "v52_original_face_key_missing_or_duplicate")
            source_patch, ids, uv = expected[key]
            require(element.attrib["data-native-patch-id"] == str(source_patch) and
                    element.attrib["data-original-native-node-ids"] ==
                    ",".join(map(str, ids)),
                    "v52_original_face_native_patch_node_mismatch")
            uv_serialized = [
                list(map(float, pair.split(","))) for pair in
                element.attrib["data-original-local-uv"].split(";")
            ]
            require(uv_serialized == uv, "v52_original_source_uv_numeric_changed")
            seen.add(key)
            by_patch[key[0]] += 1
    require(seen == set(expected) and
            panel_slots == set(range(scene["native_source_patches"])) and
            [by_patch[p] for p in range(scene["native_source_patches"])] ==
            scene["source_patch_face_counts"] and
            sample_markers == report["observed_source_curve_sample_marker_count"],
            "v52_original_svg_face_patch_curve_inventory_changed")


def _load_verified_scene(directory: Path, original_scene_path: Path) -> dict:
    """Independently rederive original-source scene; reject a forged sidecar."""
    require(original_scene_path.is_file() and
            original_scene_path.stat().st_size <= MAX_SCENE_BYTES,
            "v52_original_scene_sidecar_missing_or_oversized")
    original = json.loads(original_scene_path.read_bytes(),
                          object_pairs_hook=unique_fields,
                          parse_constant=lambda _: (_ for _ in ()).throw(
                              NativeLineageValidationError("v52_nonfinite_scene_json")))
    fresh = generate_original_scene_bundle(directory)
    require(original == fresh, "v52_visual_sidecar_not_same_original_source")
    return fresh


def export_accepted_native_publication(
    original_directory: Path, original_scene_path: Path, output: Path,
) -> dict:
    """Only publish if the original postcommit raw C++ evidence is retained."""
    require(not output.exists(), "v52_publication_output_must_be_new")
    scene_bundle = _load_verified_scene(original_directory, original_scene_path)
    docs = {
        (row["model"], row["accepted_native_step"]): row
        for row in scene_bundle["identity"]["documents"]
    }
    records = []
    svg_by_name = {}
    for scene in scene_bundle["scenes"]:
        identity = docs[(scene["model"], scene["accepted_native_step"])]
        svg, item = render_source_accepted_uv_svg(scene, identity)
        records.append(item)
        svg_by_name[item["svg_filename"]] = svg
    require(len(records) == len(scene_bundle["scenes"]) ==
            len(SOURCE_MODELS) and
            set(item["model"] for item in records) == set(SOURCE_MODELS),
            "v52_not_all_original_native_models_certified")
    manifest = {
        "schema": PACKAGE_SCHEMA,
        "classification": "ORIGINAL_ACCEPTED_CPP_TRI_SOURCE_VERIFIED_PATCH_UV_VECTOR",
        "source_scene_bundle_sha256": _digest(original_scene_path.read_bytes()),
        "source_cpp_raw_ndjson_reaudited": True,
        "source_cpp_accepted_epoch_counts": {
            row["model"]: 1 for row in records},
        "figures": sorted(records, key=lambda r: r["model"]),
        "source_uploaded_visual_json_alone_cannot_qualify": True,
        "native_triangles_only": True,
        "original_physical_node_welding_certified": False,
        "cross_epoch_face_lineage_certified": False,
        "continuous_geometric_error_bound_certified": False,
        "scientific_lod_qualified": False,
    }
    body = (json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False)
            + "\n").encode("utf-8")
    require(len(body) <= MAX_PUBLICATION_BYTES, "v52_publication_manifest_oversized")
    output.mkdir(parents=True, exist_ok=False)
    for name, svg in svg_by_name.items():
        (output / name).write_bytes(svg)
    (output / "manifest.json").write_bytes(body)
    return manifest


def audit_accepted_native_publication(
    original_directory: Path, original_scene_path: Path, output: Path,
) -> dict:
    """Independently re-open every published file and original raw source."""
    source = _load_verified_scene(original_directory, original_scene_path)
    raw = (output / "manifest.json").read_bytes()
    require(len(raw) <= MAX_PUBLICATION_BYTES, "v52_audit_manifest_oversized")
    report = json.loads(raw, object_pairs_hook=unique_fields)
    require(report["schema"] == PACKAGE_SCHEMA and
            report["classification"] ==
            "ORIGINAL_ACCEPTED_CPP_TRI_SOURCE_VERIFIED_PATCH_UV_VECTOR" and
            report["scientific_lod_qualified"] is False and
            report["original_physical_node_welding_certified"] is False and
            report["source_scene_bundle_sha256"] ==
            _digest(original_scene_path.read_bytes()),
            "v52_audit_original_manifest_invalid")
    docs = {(d["model"], d["accepted_native_step"]): d
            for d in source["identity"]["documents"]}
    require(len(report["figures"]) == len(source["scenes"]) ==
            len(SOURCE_MODELS), "v52_audit_original_scene_count_mismatch")
    names = {"manifest.json"}
    for scene in source["scenes"]:
        candidates = [r for r in report["figures"]
                      if r["model"] == scene["model"] and
                      r["accepted_native_step"] == scene["accepted_native_step"]]
        require(len(candidates) == 1, "v52_audit_native_scene_not_exactly_once")
        record = candidates[0]
        expected_svg, expected_record = render_source_accepted_uv_svg(
            scene, docs[(scene["model"], scene["accepted_native_step"])])
        require(record == expected_record, "v52_audit_figure_receipt_differs_from_original")
        name = record["svg_filename"]
        require(Path(name).name == name and name not in names,
                "v52_audit_original_fig_filename_invalid")
        body = (output / name).read_bytes()
        require(body == expected_svg and len(body) == record["svg_size_bytes"],
                "v52_audit_vector_output_differs_from_original")
        verify_svg_original_face_identity(body, scene, record)
        names.add(name)
    require({p.name for p in output.iterdir()} == names,
            "v52_audit_unexpected_unindexed_publication_file")
    return {
        "schema": "apmesh.meshstudio.v52.vector_publication_audit.v1",
        "original_source_cpp_ndjson_reopened": True,
        "all_original_source_face_keys_independently_matched": True,
        "original_source_models": [r["model"] for r in report["figures"]],
        "original_tri_faces": {
            r["model"]: r["original_native_tri_faces"] for r in report["figures"]},
        "original_patch_counts": {
            r["model"]: r["original_source_patch_count"] for r in report["figures"]},
        "figure_sha256": {
            r["model"]: r["svg_sha256"] for r in report["figures"]},
        "original_physical_node_welding_certified": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("export", "audit"), required=True)
    p.add_argument("--original-directory", type=Path, required=True)
    p.add_argument("--scene", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    if args.mode == "export":
        result = export_accepted_native_publication(
            args.original_directory, args.scene, args.output_dir)
        print("V52_ORIGINAL_ACCEPTED_CPP_TRI_UV_VECTORS=" +
              json.dumps({r["model"]: {
                  "native_faces": r["original_native_tri_faces"],
                  "source_patches": r["original_source_patch_count"],
                  "svg_sha256": r["svg_sha256"],
              } for r in result["figures"]}, sort_keys=True))
    else:
        print("V52_INDEPENDENT_ORIGINAL_NATIVE_VECTOR_AUDIT=" +
              json.dumps(audit_accepted_native_publication(
                  args.original_directory, args.scene, args.output_dir),
                  sort_keys=True))


if __name__ == "__main__":
    main()
