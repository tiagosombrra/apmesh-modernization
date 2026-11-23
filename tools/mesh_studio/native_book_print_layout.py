"""Original C++ accepted TRI Book print layouts, with source-bound vector auditing.

The only scientific admission gate for publishing is the existing independent
native raw-postcommit auditor. Local artifact preview is not native admission.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from io import BytesIO
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import matplotlib

SCHEMA = "apmesh.meshstudio.v57.source_attested_book_print_layout.v1"
SVG_NS = "http://www.w3.org/2000/svg"
APPENDIX = "book-accepted-step1-uv-appendix.pdf"
EXAMPLE = "book-accepted-step1-uv-paper-example.pdf"
PAGE_W, PAGE_H = 210 * mm, 297 * mm
SOURCE_SLOTS = tuple(range(28))
APPENDIX_SLOTS = tuple(tuple(range(i, i + 4)) for i in range(0, 28, 4))
EXAMPLE_SLOTS = (0, 9, 18, 27)
PAGE_PLOT_SIDE = 77 * mm
PAPER_FONT_MINIMUM_PT = 9.0  # Engineering readability screen, not venue authorization.


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError("v57_" + code)


def _sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _number(text: str) -> float:
    value = float(text)
    require(math.isfinite(value), "nonfinite_numeric_source")
    return value


def _source_book(directory: Path):
    manifest = json.loads((directory / "manifest.json").read_bytes())
    require(manifest.get("schema") == "apmesh.meshstudio.v52.original_native_accepted_publication.v1" and
            manifest.get("source_cpp_raw_ndjson_reaudited") is True and
            manifest.get("scientific_lod_qualified") is False and
            manifest.get("original_physical_node_welding_certified") is False,
            "invalid_original_source_manifest")
    matches = [x for x in manifest["figures"] if x.get("model") == "book"]
    require(len(matches) == 1, "duplicate_or_missing_source_book")
    item = matches[0]
    require(item["accepted_native_step"] == 1 and
            item["original_source_patch_count"] == 28 and
            item["original_native_tri_faces"] == 4256 and
            item["observed_source_curve_sample_marker_count"] == 364 and
            item["source_revalidated_from_original_postcommit_raw_ndjson"] is True and
            item["scientific_lod_qualified"] is False and
            item["physical_node_welding_certified"] is False,
            "source_book_outside_certified_scope")
    require(item["svg_filename"] == "book-accepted-step1-uv.svg", "untrusted_svg_filename")
    raw = (directory / item["svg_filename"]).read_bytes()
    require(len(raw) == item["svg_size_bytes"] and _sha(raw) == item["svg_sha256"] and
            len(raw) < 12_000_000 and b"<!DOCTYPE" not in raw.upper() and
            b"<!ENTITY" not in raw.upper(), "source_svg_sha_or_xml_prelude_changed")
    root = ET.fromstring(raw)
    require(root.get("data-schema") == "apmesh.meshstudio.v52.original_native_accepted_uv_vector.v1" and
            root.get("data-model") == "book" and
            root.get("data-original-source-ndjson-sha256") == item["original_source_ndjson_sha256"] and
            root.get("data-original-accepted-step") == "1" and
            root.get("data-physical-welding-certified") == "false" and
            root.get("data-scientific-lod-qualified") == "false",
            "source_svg_attestation_attributes_changed")
    allowed = {"svg", "title", "desc", "rect", "text", "g", "polygon", "circle"}
    for node in root.iter():
        require(node.tag.startswith("{" + SVG_NS + "}") and
                node.tag.rsplit("}", 1)[-1] in allowed,
                "source_svg_active_or_raster_tag")
        for attr, value in node.attrib.items():
            require(not attr.lower().startswith("on") and
                    not attr.lower().endswith("href") and
                    "javascript:" not in value.lower() and
                    "data:" not in value.lower() and
                    "url(" not in value.lower() and
                    "transform" not in attr.lower(), "source_svg_active_attribute")
    panels = {}
    seen_faces = set()
    for group in root.findall(f"{{{SVG_NS}}}g"):
        slot = int(group.get("data-original-patch-slot", "-1"))
        require(slot in SOURCE_SLOTS and slot not in panels, "duplicate_or_outside_book_patch_slot")
        require(group.get("data-original-native-patch-id") == "0" and
                group.get("data-original-face-count") == "152", "patch_local_identity_changed")
        shapes = list(group)
        require(len(shapes) == 167 and
                Counter(x.tag.rsplit("}", 1)[-1] for x in shapes) ==
                Counter({"text": 1, "rect": 1, "polygon": 152, "circle": 13}),
                "invalid_original_chart_primitive_inventory")
        rectangle = group.find(f"{{{SVG_NS}}}rect")
        bounds = tuple(_number(rectangle.get(k)) for k in ("x", "y", "width", "height"))
        require(bounds[2] == bounds[3] == 158.0 and
                rectangle.get("fill") == "#f7fafc", "source_chart_boundaries_changed")
        elements = set()
        samples = set()
        for element in group.findall(f"{{{SVG_NS}}}polygon"):
            require(element.get("data-original-patch-slot") == str(slot) and
                    element.get("data-native-patch-id") == "0" and
                    element.get("fill") == "#dcecf2" and
                    element.get("stroke") == "#244d62", "source_face_identity_or_style_changed")
            face = (1, slot, int(element.get("data-original-element-slot")),
                    int(element.get("data-native-element-id")))
            require(face not in seen_faces and face[2] not in elements, "duplicate_original_face_key")
            seen_faces.add(face)
            elements.add(face[2])
            ids = element.get("data-original-native-node-ids", "").split(",")
            uv = element.get("data-original-local-uv", "").split(";")
            points = element.get("points", "").split()
            require(len(ids) == len(uv) == len(points) == 3 and all(i.isdigit() for i in ids),
                    "malformed_native_node_or_uv_identity")
            for p, u in zip(points, uv):
                xy = tuple(_number(x) for x in p.split(","))
                ab = tuple(_number(x) for x in u.split(","))
                require(len(xy) == len(ab) == 2 and
                        all(-1e-9 <= x <= 1 + 1e-9 for x in ab) and
                        abs(xy[0] - (bounds[0] + ab[0] * 158)) < .00001 and
                        abs(xy[1] - (bounds[1] + (1 - ab[1]) * 158)) < .00001,
                        "source_polygon_point_not_original_uv")
        require(elements == set(range(152)), "incomplete_source_element_slots")
        for marker in group.findall(f"{{{SVG_NS}}}circle"):
            require(marker.get("data-original-patch-slot") == str(slot) and
                    marker.get("data-sample-identity") ==
                    "original-native-corner-not-physical-welding" and
                    marker.get("data-source-curve-slot") == "3" and
                    marker.get("fill") == "#bd503f", "forged_source_marker")
            ordinal = int(marker.get("data-original-source-sample-ordinal", "-1"))
            require(ordinal not in samples, "duplicate_source_sample")
            samples.add(ordinal)
        require(samples == set(range(13)), "incomplete_source_marker_ordinals")
        panels[slot] = (group, bounds)
    require(set(panels) == set(SOURCE_SLOTS) and len(seen_faces) == 4256,
            "missing_original_book_faces_or_charts")
    return item, panels


def _font() -> str:
    file = Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans.ttf"
    require(file.is_file(), "pinned_vector_font_missing")
    name = "V57OriginalDejaVu"
    if name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(name, str(file)))
    return name


def _chart_position(slot_in_page: int) -> tuple[float, float]:
    # Pages are A4 portrait with four charts in a consistent reading order.
    column = slot_in_page % 2
    row = slot_in_page // 2
    return (12 + column * (89 + 8)) * mm, (146 - row * (118 + 8)) * mm


def _plot_position(slot_in_page: int) -> tuple[float, float]:
    x, y = _chart_position(slot_in_page)
    return x + 6 * mm, y + 15 * mm


def _map(x: float, y: float, box: tuple, slot_in_page: int) -> tuple[float, float]:
    px, py = _plot_position(slot_in_page)
    sx, sy, sw, sh = box
    scale = PAGE_PLOT_SIDE / sw
    return px + (x - sx) * scale, py + PAGE_PLOT_SIDE - (y - sy) * scale


def _draw_panel(c, group: ET.Element, box: tuple, panel: int, slot: int, font: str) -> None:
    cx, cy = _chart_position(panel)
    c.setFillColor(colors.HexColor("#fbfcfd"))
    c.setStrokeColor(colors.HexColor("#d1dbe2"))
    c.setLineWidth(.7)
    c.roundRect(cx, cy, 89 * mm, 118 * mm, 5 * mm, stroke=1, fill=1)
    c.setFillColor(colors.HexColor("#102431"))
    c.setFont(font, 11.5)
    c.drawString(cx + 6 * mm, cy + 110 * mm, f"Patch slot {slot:02d}")
    c.setFillColor(colors.HexColor("#365363"))
    c.setFont(font, 9.4)
    c.drawString(cx + 6 * mm, cy + 101 * mm, "152 source TRI | 13 observed markers")
    bx, by = _plot_position(panel)
    c.setFillColor(colors.HexColor("#f7fafc"))
    c.setStrokeColor(colors.HexColor("#8b9ba8"))
    c.setLineWidth(.65)
    c.rect(bx, by, PAGE_PLOT_SIDE, PAGE_PLOT_SIDE, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#dcecf2"))
    c.setStrokeColor(colors.HexColor("#244d62"))
    c.setLineWidth(.30)
    for poly in group.findall(f"{{{SVG_NS}}}polygon"):
        vertices = [tuple(_number(v) for v in point.split(","))
                    for point in poly.get("points").split()]
        path = c.beginPath()
        x, y = _map(*vertices[0], box, panel)
        path.moveTo(x, y)
        for xy in vertices[1:]:
            x, y = _map(*xy, box, panel)
            path.lineTo(x, y)
        path.close()
        c.drawPath(path, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#bd503f"))
    c.setStrokeColor(colors.HexColor("#ffffff"))
    c.setLineWidth(.5)
    for marker in group.findall(f"{{{SVG_NS}}}circle"):
        x, y = _map(_number(marker.get("cx")), _number(marker.get("cy")), box, panel)
        r = _number(marker.get("r")) * PAGE_PLOT_SIDE / box[2]
        c.circle(x, y, r, stroke=1, fill=1)
    c.setFont(font, 9.1)
    c.setFillColor(colors.HexColor("#365363"))
    c.drawString(cx + 6 * mm, cy + 7.2 * mm, "Original native UV | no physical welding")


def render_pdf(directory: Path, selected_pages: tuple[tuple[int, ...], ...], name: str):
    item, groups = _source_book(directory)
    require(name in (APPENDIX, EXAMPLE), "invalid_output_name")
    require((name == APPENDIX and selected_pages == APPENDIX_SLOTS) or
            (name == EXAMPLE and selected_pages == (EXAMPLE_SLOTS,)),
            "unregistered_patch_selection")
    font = _font()
    sink = BytesIO()
    c = canvas.Canvas(sink, pagesize=(PAGE_W, PAGE_H),
                      invariant=1, pageCompression=1, initialFontName=font)
    c.setTitle("APMesh original C++ Book source patch-local UV - " + name)
    c.setAuthor("APMesh - original-native patch-local source figure")
    c.setSubject("Accepted TRI epoch 1; no welded seams, geometry LOD or accepted later epochs")
    page_receipts = []
    for index, slots in enumerate(selected_pages):
        c.setFillColor(colors.white)
        c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#102431"))
        c.setFont(font, 16)
        c.drawString(12 * mm, PAGE_H - 17 * mm, "BOOK | Source-accepted TRI, step 1")
        c.setFont(font, 9.3)
        c.setFillColor(colors.HexColor("#365363"))
        c.drawString(12 * mm, PAGE_H - 25 * mm,
                     "Patch-local original C++ UV; samples are observed points, not continuous seams")
        for panel, slot in enumerate(slots):
            group, bounds = groups[slot]
            _draw_panel(c, group, bounds, panel, slot, font)
        c.setFont(font, 9.0)
        c.drawString(12 * mm, 10 * mm,
                     "Experimental source evidence | no LOD, no physical patch welding")
        c.drawRightString(PAGE_W - 12 * mm, 10 * mm, f"Page {index + 1}/{len(selected_pages)}")
        page_receipts.append({"page": index + 1, "source_patch_slots": list(slots),
                              "native_faces": 152 * len(slots),
                              "observed_source_markers": 13 * len(slots)})
        c.showPage()
    c.save()
    pdf = sink.getvalue()
    require(2000 < len(pdf) < 20_000_000, "unexpected_pdf_size")
    recipe = {
        "schema": SCHEMA,
        "classification": "ORIGINAL_NATIVE_SOURCE_ANNOTATED_PRINT_LAYOUT_NOT_LOD",
        "model": "book", "accepted_step": 1, "scientific_lod_qualified": False,
        "physical_node_welding_certified": False,
        "selection": "all-28-source-slots" if name == APPENDIX else "evenly-spaced-source-slot-order-only",
        "selected_source_patch_slots": [s for x in selected_pages for s in x],
        "source_svg_sha256": item["svg_sha256"],
        "original_source_ndjson_sha256": item["original_source_ndjson_sha256"],
        "pdf_name": name, "pdf_sha256": _sha(pdf), "pdf_size_bytes": len(pdf),
        "physical_width_mm": 210, "physical_height_mm": 297,
        "target_min_font_pt": PAPER_FONT_MINIMUM_PT,
        "pages": page_receipts,
        "source_faces_in_selected_pages": sum(p["native_faces"] for p in page_receipts),
        "source_markers_in_selected_pages": sum(p["observed_source_markers"] for p in page_receipts),
    }
    return pdf, recipe


def audit_pdf_bytes(pdf: bytes, recipe: dict, directory: Path):
    """Independently inspect the delivered PDF's actual vector paths and positions."""
    import fitz
    from pypdf import PdfReader
    from pypdf.generic import ContentStream
    item, groups = _source_book(directory)
    require(_sha(pdf) == recipe["pdf_sha256"] and len(pdf) == recipe["pdf_size_bytes"] and
            recipe["source_svg_sha256"] == item["svg_sha256"] and
            recipe["original_source_ndjson_sha256"] == item["original_source_ndjson_sha256"] and
            recipe["schema"] == SCHEMA and recipe["accepted_step"] == 1 and
            recipe["scientific_lod_qualified"] is False and
            recipe["physical_node_welding_certified"] is False,
            "report_or_original_source_binding_invalid")
    all_slots = [s for p in recipe["pages"] for s in p["source_patch_slots"]]
    expected = SOURCE_SLOTS if recipe["pdf_name"] == APPENDIX else EXAMPLE_SLOTS
    expected_pages = APPENDIX_SLOTS if recipe["pdf_name"] == APPENDIX else (EXAMPLE_SLOTS,)
    require(tuple(all_slots) == expected and
            tuple(tuple(p["source_patch_slots"]) for p in recipe["pages"]) == expected_pages,
            "source_chart_coverage_missing_or_repeated")
    doc = PdfReader(BytesIO(pdf), strict=True)
    require(len(doc.pages) == len(expected_pages), "wrong_number_of_pdf_pages")
    pages = []
    with fitz.open(stream=pdf, filetype="pdf") as fitzdoc:
        for page_index, (slots, layout_page) in enumerate(zip(expected_pages, fitzdoc)):
            page = doc.pages[page_index]
            require(abs(float(page.mediabox.width) - PAGE_W) < .1 and
                    abs(float(page.mediabox.height) - PAGE_H) < .1,
                    "wrong_physical_media_box")
            require(not layout_page.get_images(full=True), "raster_xobject_forbidden")
            stream = ContentStream(page.get_contents(), doc)
            require(all(op not in (b"INLINE IMAGE", b"BI", b"Do")
                        for args, op in stream.operations), "inline_or_external_xobject_forbidden")
            fonts = layout_page.get_fonts(full=True)
            require(bool(fonts) and all("DejaVuSans" in font[3] and
                    layout_page.parent.extract_font(font[0])[-1] for font in fonts),
                    "unembedded_or_unapproved_font")
            spans = [span for block in layout_page.get_text("dict")["blocks"]
                     if "lines" in block for line in block["lines"] for span in line["spans"]]
            require(bool(spans), "pdf_lost_text_layer")
            min_size = min(span["size"] for span in spans)
            require(min_size >= PAPER_FONT_MINIMUM_PT - .02, "legibility_font_floor_not_met")
            text = layout_page.get_text()
            require("no LOD" in text and "no physical patch welding" in text and
                    all(f"Patch slot {slot:02d}" in text for slot in slots),
                    "original_patch_title_or_scientific_disclaimer_missing")
            drawings = layout_page.get_drawings()
            def color_match(fill, rgb):
                return fill is not None and len(fill) == 3 and all(
                    abs(value - component / 255) < .002 for value, component in zip(fill, rgb))
            tris = [drawing for drawing in drawings
                    if color_match(drawing.get("fill"), (220, 236, 242))]
            markers = [drawing for drawing in drawings
                       if color_match(drawing.get("fill"), (189, 80, 63))]
            require(len(tris) == 152 * len(slots) and len(markers) == 13 * len(slots),
                    "pdf_face_or_marker_count_drift")
            face_index = marker_index = 0
            for panel, slot in enumerate(slots):
                group, source_bounds = groups[slot]
                for polygon in group.findall(f"{{{SVG_NS}}}polygon"):
                    drawing = tris[face_index]
                    face_index += 1
                    edges = drawing["items"]
                    require(len(edges) == 3 and all(edge[0] == "l" for edge in edges),
                            "face_not_true_vector_triangle")
                    vertices = [tuple(_number(v) for v in point.split(","))
                                for point in polygon.get("points").split()]
                    pts = [_map(*pt, source_bounds, panel) for pt in vertices]
                    expected_top = [(x, PAGE_H - y) for x, y in pts]
                    for line_index, line in enumerate(edges):
                        for actual, expected_point in ((line[1], expected_top[line_index]),
                            (line[2], expected_top[(line_index + 1) % 3])):
                            require(math.dist((actual.x, actual.y), expected_point) < .004,
                                    "actual_pdf_polygon_coordinate_vs_native_uv_drift")
                for marker in group.findall(f"{{{SVG_NS}}}circle"):
                    drawing = markers[marker_index]
                    marker_index += 1
                    x, y = _map(_number(marker.get("cx")), _number(marker.get("cy")),
                                source_bounds, panel)
                    radius = _number(marker.get("r")) * PAGE_PLOT_SIDE / source_bounds[2]
                    rect = drawing["rect"]
                    require(abs((rect.x0 + rect.x1) / 2 - x) < .004 and
                            abs((rect.y0 + rect.y1) / 2 - (PAGE_H - y)) < .004 and
                            abs(rect.width - 2 * radius) < .004 and
                            abs(rect.height - 2 * radius) < .004,
                            "actual_pdf_source_marker_changed")
            pages.append({"page": page_index + 1, "source_slots": list(slots),
                          "native_triangles": len(tris), "markers": len(markers),
                          "min_font_pt": round(min_size, 3), "raster_images": 0,
                          "physical_width_mm": 210, "physical_height_mm": 297})
    return {"schema": "apmesh.meshstudio.v57.source_book_print_pdf_audit.v1",
            "classification": "ACTUAL_PRINT_PDF_ALL_SOURCE_UV_FACES_MATCH_NOT_LOD",
            "pdf_sha256": _sha(pdf), "pages": pages,
            "original_face_paths_matched": sum(p["native_triangles"] for p in pages),
            "original_marker_positions_matched": sum(p["markers"] for p in pages),
            "raster_images": 0, "scientific_lod_qualified": False}


def render_pair(directory: Path, output: Path, *, native_source_verified: bool = False):
    """Produce preview or post-admission output; the flag is not source proof."""
    output.mkdir(parents=True, exist_ok=False)
    rendered = {}
    for name, slots in ((APPENDIX, APPENDIX_SLOTS), (EXAMPLE, (EXAMPLE_SLOTS,))):
        pdf, receipt = render_pdf(directory, slots, name)
        check = audit_pdf_bytes(pdf, receipt, directory)
        (output / name).write_bytes(pdf)
        rendered[name] = {"receipt": receipt, "audit": check}
    manifest = {"schema": SCHEMA, "model": "book",
                "native_source_reauthenticated_in_same_run": native_source_verified,
                "prototype_only_without_original_cpp": not native_source_verified,
                "outputs": rendered}
    (output / "print-layout-receipt.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preview", "export", "audit"), required=True)
    parser.add_argument("--v52-dir", type=Path, required=True)
    parser.add_argument("--original-directory", type=Path)
    parser.add_argument("--scene", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "preview":
        report = render_pair(args.v52_dir, args.output_dir, native_source_verified=False)
    else:
        require(args.original_directory is not None and args.scene is not None,
                "original_native_raw_source_arguments_required")
        from tools.mesh_studio.native_accepted_vector_publication import audit_accepted_native_publication
        source = audit_accepted_native_publication(args.original_directory, args.scene, args.v52_dir)
        require(source["all_original_source_face_keys_independently_matched"] is True,
                "original_cpp_native_face_audit_failed")
        if args.mode == "export":
            report = render_pair(args.v52_dir, args.output_dir, native_source_verified=True)
        else:
            old = json.loads((args.output_dir / "print-layout-receipt.json").read_text(encoding="utf-8"))
            require(old["native_source_reauthenticated_in_same_run"] is True,
                    "prior_qualifier_missing")
            with TemporaryDirectory(prefix="v57-repro-") as folder:
                candidate = render_pair(args.v52_dir, Path(folder) / "export",
                                        native_source_verified=True)
                for file in (APPENDIX, EXAMPLE, "print-layout-receipt.json"):
                    require((args.output_dir / file).read_bytes() ==
                            (Path(folder) / "export" / file).read_bytes(),
                            "non_reproducible_pdf_or_receipt")
            report = candidate
    print("V57_BOOK_PRINT_LAYOUT=" + json.dumps({
        "source_verified_in_this_command": args.mode != "preview",
        "outputs": {k: {"sha256": v["receipt"]["pdf_sha256"],
                        "faces": v["audit"]["original_face_paths_matched"],
                        "markers": v["audit"]["original_marker_positions_matched"],
                        "pages": len(v["audit"]["pages"])}
                    for k, v in report["outputs"].items()}}, sort_keys=True))


if __name__ == "__main__":
    main()
