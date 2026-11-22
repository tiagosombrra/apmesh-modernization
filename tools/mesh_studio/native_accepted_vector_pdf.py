"""Deterministic, independently audited original-native accepted TRI vector PDF.

Only operate on same-run original C++ postcommit NDJSON source already audited
by V5.2. Never promote an uploaded scene or SVG alone to original evidence.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from importlib.metadata import version as package_version
from io import BytesIO
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

SCHEMA = "apmesh.meshstudio.v53.original_native_article_vector_pdf.v1"
PDF_NAME = "accepted-original-tri-uv-article.pdf"
RECIPE_NAME = "recipe.json"
SVG_NS = "http://www.w3.org/2000/svg"
FIGURE_SCHEMA = "apmesh.meshstudio.v52.original_native_accepted_uv_vector.v1"
MAX_PDF_SIZE = 15_000_000
HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")
ALLOWED_TAGS = {"svg", "title", "desc", "rect", "text", "g", "polygon", "circle"}
MODELS = ("eistute", "book")


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _number(value: str) -> float:
    result = float(value)
    _require(math.isfinite(result), "v53_nonfinite_original_svg_coordinate")
    return result


def _color(value: str):
    from reportlab.lib.colors import HexColor
    _require(bool(HEX_COLOR.fullmatch(value)), "v53_nonliteral_vector_rgb")
    if len(value) == 4:
        value = "#" + "".join(a*2 for a in value[1:])
    return HexColor(value)


def _original_svg(svg: bytes, name: str, figure: dict) -> tuple[ET.Element, tuple[float, float, float, float]]:
    from reportlab.lib.units import mm
    _require(len(svg) < 12_000_000 and b"<!DOCTYPE" not in svg.upper()
             and b"<!ENTITY" not in svg.upper(), "v53_untrusted_original_svg")
    root = ET.fromstring(svg)
    _require(root.tag == f"{{{SVG_NS}}}svg" and root.get("data-schema") == FIGURE_SCHEMA
             and root.get("data-model") == name and
             root.get("data-original-source-ndjson-sha256") ==
             figure["original_source_ndjson_sha256"] and
             root.get("data-original-accepted-step") == "1" and
             root.get("data-physical-welding-certified") == "false" and
             root.get("data-scientific-lod-qualified") == "false",
             "v53_original_native_svg_identity_not_qualified")
    width, height = figure["width_mm"] * mm, figure["height_mm"] * mm
    _require(root.get("width") == f'{figure["width_mm"]}mm' and
             root.get("height") == f'{figure["height_mm"]}mm' and
             root.get("preserveAspectRatio", "xMidYMid meet") == "xMidYMid meet",
             "v53_original_native_svg_physical_size_changed")
    vb = [_number(a) for a in root.attrib["viewBox"].split()]
    _require(len(vb) == 4 and vb[0] == vb[1] == 0 and
             0 < vb[2] <= 10000 and 0 < vb[3] <= 10000,
             "v53_original_native_svg_viewbox_invalid")
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        _require(node.tag.startswith(f"{{{SVG_NS}}}") and
                 tag in ALLOWED_TAGS, "v53_svg_active_raster_or_unknown_primitive")
        for attr, value in node.attrib.items():
            _require(not attr.lower().startswith("on") and
                     not attr.lower().endswith("href") and
                     "url(" not in value.lower() and
                     "data:" not in value.lower() and
                     "javascript:" not in value.lower() and
                     "transform" not in attr.lower(),
                     "v53_svg_external_script_or_transform_not_supported")
        if tag == "polygon":
            _require(node.get("fill") == "#dcecf2" and
                     node.get("stroke") == "#244d62" and
                     node.get("data-original-native-node-ids") is not None and
                     node.get("data-original-local-uv") is not None,
                     "v53_source_polygon_identity_not_preserved")
        if tag == "circle":
            _require(node.get("fill") == "#bd503f" and
                     node.get("data-sample-identity") ==
                     "original-native-corner-not-physical-welding",
                     "v53_original_native_sample_provenance_not_qualified")
    return root, (width, height, vb[2], vb[3])


def _transform(width: float, height: float, vw: float, vh: float):
    # Reproduce SVG's default xMidYMid meet letterboxing, not anisotropic distortion.
    scale = min(width/vw, height/vh)
    return scale, (width - vw*scale)/2, (height - vh*scale)/2


def _font() -> str:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import matplotlib
    filename = Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans.ttf"
    _require(filename.is_file(), "v53_embedded_font_from_pinned_matplotlib_missing")
    key = "V53LocalDejaVu"
    if key not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(key, str(filename)))
    return key


def _draw_svg(c, root: ET.Element, page: tuple[float, float, float, float], font: str) -> tuple[int, int]:
    width, height, vw, vh = page
    scale, left, top = _transform(width, height, vw, vh)
    faces = samples = 0
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag not in ("rect", "text", "polygon", "circle"):
            continue
        fill = node.get("fill")
        if fill:
            c.setFillColor(_color(fill))
        stroke = node.get("stroke")
        if stroke:
            c.setStrokeColor(_color(stroke))
        if node.get("stroke-width"):
            c.setLineWidth(_number(node.attrib["stroke-width"]) * scale)
        if tag == "rect":
            x, y = _number(node.get("x", "0")), _number(node.get("y", "0"))
            w, h = _number(node.attrib["width"]), _number(node.attrib["height"])
            _require(w > 0 and h > 0, "v53_svg_negative_rect_size")
            c.rect(left + x*scale, height-top-(y+h)*scale,
                   w*scale, h*scale, fill=1, stroke=int(bool(stroke)))
        elif tag == "polygon":
            pts = [tuple(_number(v) for v in pair.split(","))
                   for pair in node.attrib["points"].split()]
            _require(len(pts) == 3 and all(len(p) == 2 for p in pts),
                     "v53_original_native_tri_polygon_not_three_corners")
            path = c.beginPath()
            path.moveTo(left+pts[0][0]*scale, height-top-pts[0][1]*scale)
            for x, y in pts[1:]:
                path.lineTo(left+x*scale, height-top-y*scale)
            path.close()
            c.drawPath(path, fill=1, stroke=1)
            faces += 1
        elif tag == "circle":
            radius = _number(node.attrib["r"])
            _require(radius > 0, "v53_zero_sample_radius")
            c.circle(left+_number(node.attrib["cx"])*scale,
                     height-top-_number(node.attrib["cy"])*scale,
                     radius*scale, fill=1, stroke=1)
            samples += 1
        else:
            _require(node.text is not None and len(node.text) < 400,
                     "v53_source_text_missing_or_unbounded")
            c.setFont(font, _number(node.attrib["font-size"])*scale)
            c.drawString(left+_number(node.attrib["x"])*scale,
                         height-top-_number(node.attrib["y"])*scale,
                         node.text)
    return faces, samples


def _source_figures(v52_dir: Path) -> tuple[dict, list[tuple[dict, ET.Element, tuple[float,float,float,float],bytes]]]:
    raw = (v52_dir / "manifest.json").read_bytes()
    _require(len(raw) < 256_000, "v53_unbounded_source_manifest")
    receipt = json.loads(raw)
    _require(receipt["schema"] == "apmesh.meshstudio.v52.original_native_accepted_publication.v1" and
             receipt["classification"] == "ORIGINAL_ACCEPTED_CPP_TRI_SOURCE_VERIFIED_PATCH_UV_VECTOR" and
             receipt["source_cpp_raw_ndjson_reaudited"] is True and
             receipt["original_physical_node_welding_certified"] is False and
             receipt["scientific_lod_qualified"] is False and
             len(receipt["figures"]) == 2,
             "v53_original_cpp_acceptance_manifest_missing")
    figures = []
    for name in MODELS:
        matches = [entry for entry in receipt["figures"] if entry["model"] == name]
        _require(len(matches) == 1, "v53_original_native_source_not_unique")
        item = matches[0]
        _require(item["accepted_native_step"] == 1 and
                 item["scientific_lod_qualified"] is False and
                 item["physical_node_welding_certified"] is False and
                 item["source_revalidated_from_original_postcommit_raw_ndjson"] is True,
                 "v53_original_cpp_accepted_step_or_scope_changed")
        path = v52_dir / item["svg_filename"]
        _require(path.name == f"{name}-accepted-step1-uv.svg" and
                 path.is_file(), "v53_original_source_figure_filename_invalid")
        svg = path.read_bytes()
        _require(_digest(svg) == item["svg_sha256"] and len(svg) == item["svg_size_bytes"],
                 "v53_original_source_svg_sha_mismatch")
        root, page = _original_svg(svg, name, item)
        faces = root.findall(f".//{{{SVG_NS}}}polygon")
        samples = root.findall(f".//{{{SVG_NS}}}circle")
        _require(len(faces) == item["original_native_tri_faces"] and
                 len(samples) == item["observed_source_curve_sample_marker_count"] and
                 len(root.findall(f".//{{{SVG_NS}}}g")) == item["original_source_patch_count"],
                 "v53_original_svg_face_patch_samples_changed")
        figures.append((item,root,page,svg))
    return receipt, figures


def render_pdf_from_source_vectors(v52_dir: Path) -> tuple[bytes, dict]:
    """Only compositional rendering; caller must first attest original raw C++."""
    from reportlab.pdfgen import canvas
    source, figures = _source_figures(v52_dir)
    font = _font()
    sink = BytesIO()
    c = canvas.Canvas(sink, pagesize=figures[0][2][:2],
                      invariant=1, pageCompression=1, initialFontName=font)
    c.setTitle("APMesh original accepted TRI patch-local UV figures")
    c.setAuthor("APMesh Mesh Studio - original C++ source")
    c.setSubject("Native C++ original accepted step 1, patch-local UV vector; not physical welding or LOD")
    page_receipts = []
    for index, (item,root,page,svg) in enumerate(figures):
        if index:
            c.setPageSize(page[:2])
        count, markers = _draw_svg(c, root, page, font)
        _require(count == item["original_native_tri_faces"] and
                 markers == item["observed_source_curve_sample_marker_count"],
                 "v53_incomplete_original_source_pdf_vector_primitives")
        page_receipts.append({
            "page": index+1, "model": item["model"],
            "accepted_native_step": 1, "original_source_ndjson_sha256": item["original_source_ndjson_sha256"],
            "original_model_input_sha256": item["original_model_input_sha256"],
            "original_config_sha256": item["original_config_sha256"],
            "source_svg_sha256": item["svg_sha256"],
            "source_tri_faces": count, "source_patch_count": item["original_source_patch_count"],
            "source_sample_markers": markers,
            "physical_width_mm": item["width_mm"], "physical_height_mm": item["height_mm"],
        })
        c.showPage()
    c.save()
    pdf = sink.getvalue()
    _require(1000 < len(pdf) < MAX_PDF_SIZE, "v53_invalid_pdf_byte_capacity")
    recipe = {
        "schema": SCHEMA,
        "classification": "ORIGINAL_ACCEPTED_CPP_TRI_2PAGE_TRUE_VECTOR_PDF_NOT_LOD",
        "document": PDF_NAME, "source_scene_bundle_sha256": source["source_scene_bundle_sha256"],
        "source_v52_manifest_sha256": _digest((v52_dir / "manifest.json").read_bytes()),
        "pdf_sha256": _digest(pdf), "pdf_size_bytes": len(pdf),
        "page_count": 2, "pages": page_receipts,
        "render_engine": {
            "library": "reportlab", "version": package_version("reportlab"),
            "invariant_document": True, "embedded_font": "DejaVuSans",
            "vector_transform": "xMidYMid meet",
        },
        "vector_only_no_raster_images": True, "font_embedded_in_pdf": True,
        "source_cpp_ndjson_must_be_independently_reaudited": True,
        "physical_node_welding_certified": False,
        "continuous_geometric_error_bound_certified": False,
        "cross_epoch_face_lineage_certified": False,
        "scientific_lod_qualified": False,
    }
    return pdf, recipe


def audit_vector_pdf_bytes(pdf: bytes, receipt: dict, v52_dir: Path) -> dict:
    """Independently inspect actual PDF paths, page boxes, text and embedded fonts."""
    from pypdf import PdfReader
    from pypdf.generic import ContentStream
    import fitz
    _require(_digest(pdf) == receipt["pdf_sha256"] and
             len(pdf) == receipt["pdf_size_bytes"] and
             receipt["schema"] == SCHEMA and
             receipt.get("render_engine", {}).get("library") == "reportlab" and
             receipt["render_engine"]["embedded_font"] == "DejaVuSans" and
             receipt["render_engine"]["vector_transform"] == "xMidYMid meet" and
             receipt["render_engine"]["invariant_document"] is True and
             receipt["scientific_lod_qualified"] is False and
             receipt["physical_node_welding_certified"] is False,
             "v53_pdf_receipt_or_bytes_changed")
    _, figures = _source_figures(v52_dir)
    reader = PdfReader(BytesIO(pdf), strict=True)
    _require(len(reader.pages) == len(figures) == 2,
             "v53_pdf_original_native_page_count_changed")
    verified = []
    with fitz.open(stream=pdf,filetype="pdf") as actual:
        for idx,(item,root,geometry,svg) in enumerate(figures):
            page = reader.pages[idx]
            width,height,vw,vh = geometry
            fitzpage = actual[idx]
            _require(abs(float(page.mediabox.width)-width) < 0.1 and
                     abs(float(page.mediabox.height)-height) < 0.1 and
                     abs(fitzpage.rect.width-width) < .1 and
                     abs(fitzpage.rect.height-height) < .1,
                     "v53_pdf_wrong_physical_article_dimensions")
            _require(not fitzpage.get_images(full=True),
                     "v53_pdf_contains_raster_image_xobject")
            stream = ContentStream(page.get_contents(),reader)
            _require(all(op not in (b"INLINE IMAGE",b"BI",b"Do")
                         for _,op in stream.operations),
                     "v53_pdf_contains_inline_image_or_external_xobject")
            fonts=fitzpage.get_fonts(full=True)
            _require(bool(fonts) and all(fitzpage.parent.extract_font(row[0])[-1]
                                         for row in fonts) and
                     all("DejaVuSans" in row[3] for row in fonts),
                     "v53_pdf_font_missing_or_not_embedded")
            drawings = fitzpage.get_drawings()
            def match(fill:tuple[float,float,float]|None,rgb:tuple[int,int,int]):
                return (fill is not None and len(fill)==3 and
                        all(abs(a-b/255.0)<.002 for a,b in zip(fill,rgb)))
            tri = [v for v in drawings if match(v.get("fill"),(220,236,242))]
            circles=[v for v in drawings if match(v.get("fill"),(189,80,63))]
            triangles = root.findall(f".//{{{SVG_NS}}}polygon")
            markers = root.findall(f".//{{{SVG_NS}}}circle")
            _require(len(tri)==len(triangles)==item["original_native_tri_faces"] and
                     len(circles)==len(markers)==item["observed_source_curve_sample_marker_count"],
                     "v53_pdf_original_face_or_marker_drawings_missing")
            scale,left,top=_transform(*geometry)
            for polygon,drawing in zip(triangles,tri):
                coords = [tuple(_number(v) for v in p.split(","))
                          for p in polygon.attrib["points"].split()]
                expected=[(left+x*scale,top+y*scale) for x,y in coords]
                lines=drawing["items"]
                _require(len(lines)==3 and all(edge[0]=="l" for edge in lines),
                         "v53_pdf_original_triangle_changed_to_nonvector_path")
                for k,edge in enumerate(lines):
                    a,b = edge[1],edge[2]
                    for actual_point,expected_point in ((a,expected[k]),(b,expected[(k+1)%3])):
                        _require(math.dist((actual_point.x,actual_point.y),expected_point)<.003,
                                 "v53_pdf_original_uv_face_geometry_changed")
            for marker,drawing in zip(markers,circles):
                cx=left+_number(marker.attrib["cx"])*scale
                cy=top+_number(marker.attrib["cy"])*scale
                radius=_number(marker.attrib["r"])*scale
                box=drawing["rect"]
                _require(abs((box.x0+box.x1)/2-cx)<.003 and
                         abs((box.y0+box.y1)/2-cy)<.003 and
                         abs(box.width-2*radius)<.003 and
                         abs(box.height-2*radius)<.003,
                         "v53_pdf_original_native_curve_sample_position_changed")
            text=fitzpage.get_text()
            _require(item["model"].upper() in text and
                     "Original accepted native TRI" in text,
                     "v53_pdf_source_title_not_searchable")
            _require(receipt["pages"][idx]["original_source_ndjson_sha256"]==
                     item["original_source_ndjson_sha256"] and
                     receipt["pages"][idx]["source_tri_faces"]==len(tri),
                     "v53_pdf_face_count_or_source_receipt_mismatch")
            verified.append({"model":item["model"],"source_tri_faces":len(tri),
                             "source_curve_sample_markers":len(circles),
                             "page_width_mm":item["width_mm"],
                             "page_height_mm":item["height_mm"],
                             "fonts_embedded":len(fonts)})
    return {"schema":"apmesh.meshstudio.v53.native_original_vector_pdf_audit.v1",
            "classification":"INDEPENDENT_ACTUAL_PDF_BYTES_VECTOR_PATH_SOURCE_MATCH",
            "pdf_sha256":_digest(pdf),"pages":verified,
            "all_original_cpp_tri_uv_polygons_pdf_matched":True,
            "raster_xobjects_or_inline_images":0,
            "scientific_lod_qualified":False,"physical_node_welding_certified":False}


def export_pdf(original_directory: Path, source_scene: Path, v52_dir: Path, output: Path) -> dict:
    """CLI's non-optional independent original raw C++ source admission gate."""
    from .native_accepted_vector_publication import audit_accepted_native_publication
    _require(not output.exists(), "v53_output_directory_must_be_new")
    source_audit=audit_accepted_native_publication(original_directory,source_scene,v52_dir)
    _require(source_audit["all_original_source_face_keys_independently_matched"] is True,
             "v53_original_cpp_raw_accepted_faces_unqualified")
    pdf,receipt=render_pdf_from_source_vectors(v52_dir)
    report=audit_vector_pdf_bytes(pdf,receipt,v52_dir)
    output.mkdir(parents=True,exist_ok=False)
    (output/PDF_NAME).write_bytes(pdf)
    (output/RECIPE_NAME).write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",
                                    encoding="utf-8")
    return report


def audit_pdf(original_directory: Path, source_scene: Path, v52_dir: Path, output: Path) -> dict:
    """Source-reaudit plus byte-exact deterministic PDF reconstruction."""
    from .native_accepted_vector_publication import audit_accepted_native_publication
    source_audit=audit_accepted_native_publication(original_directory,source_scene,v52_dir)
    _require(source_audit["all_original_source_face_keys_independently_matched"] is True,
             "v53_original_cpp_raw_accepted_faces_unqualified")
    actual=(output/PDF_NAME).read_bytes()
    receipt=json.loads((output/RECIPE_NAME).read_text(encoding="utf-8"))
    expected_pdf,expected_receipt=render_pdf_from_source_vectors(v52_dir)
    _require(actual==expected_pdf and receipt==expected_receipt and
             {p.name for p in output.iterdir()}=={PDF_NAME,RECIPE_NAME},
             "v53_pdf_not_byte_reproducible_from_original_source")
    return audit_vector_pdf_bytes(actual,receipt,v52_dir)


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode",choices=("export","audit"),required=True)
    parser.add_argument("--original-directory",type=Path,required=True)
    parser.add_argument("--scene",type=Path,required=True)
    parser.add_argument("--v52-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    method=export_pdf if args.mode=="export" else audit_pdf
    print("V53_ORIGINAL_CPP_ACCEPTED_VECTOR_PDF="+json.dumps(
        method(args.original_directory,args.scene,args.v52_dir,args.output_dir),
        sort_keys=True))

if __name__=="__main__":
    main()