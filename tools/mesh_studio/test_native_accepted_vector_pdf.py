"""Synthetic-only negative controls for V5.3 source PDF protocol.

These generated test figures are never accepted original C++ scientific data.
The actual native CI must independently re-open original postcommit NDJSON.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET

from .native_accepted_vector_pdf import (
    PDF_NAME, _source_figures, audit_vector_pdf_bytes,
    render_pdf_from_source_vectors, export_pdf,
)
from .native_accepted_vector_publication import render_source_accepted_uv_svg
from .test_native_accepted_vector_publication import native_synthetic_vector_fixture


def synthetic_vector_package(root: Path) -> Path:
    """Build two bounded synthetic protocol figures, never source evidence."""
    directory = root / "synthetic-native-v52"
    directory.mkdir()
    entries = []
    for model in ("book", "eistute"):
        source, identity = native_synthetic_vector_fixture(model)
        svg, item = render_source_accepted_uv_svg(source, identity)
        (directory / item["svg_filename"]).write_bytes(svg)
        entries.append(item)
    (directory / "manifest.json").write_text(json.dumps({
        "schema": "apmesh.meshstudio.v52.original_native_accepted_publication.v1",
        "classification": "ORIGINAL_ACCEPTED_CPP_TRI_SOURCE_VERIFIED_PATCH_UV_VECTOR",
        "source_cpp_raw_ndjson_reaudited": True,
        "source_scene_bundle_sha256": "f" * 64,
        "original_physical_node_welding_certified": False,
        "scientific_lod_qualified": False,
        "figures": entries,
    }, sort_keys=True), encoding="utf-8")
    return directory


def rewrite_receipt(directory: Path, index: int, svg: bytes) -> None:
    manifest_file = directory / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    entry = manifest["figures"][index]
    (directory / entry["svg_filename"]).write_bytes(svg)
    entry["svg_sha256"] = sha256(svg).hexdigest()
    entry["svg_size_bytes"] = len(svg)
    manifest_file.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")


class OriginalNativeArticlePdfSyntheticContracts(unittest.TestCase):
    def test_deterministic_vector_pdf_embedded_font_all_source_shape_paths(self):
        with TemporaryDirectory() as folder:
            path = synthetic_vector_package(Path(folder))
            pdf, recipe = render_pdf_from_source_vectors(path)
            again, again_recipe = render_pdf_from_source_vectors(path)
            self.assertEqual(pdf, again)
            self.assertEqual(recipe, again_recipe)
            self.assertEqual(recipe["page_count"], 2)
            self.assertEqual([x["model"] for x in recipe["pages"]],
                             ["eistute", "book"])
            self.assertEqual([x["source_tri_faces"] for x in recipe["pages"]],
                             [4, 28])
            self.assertEqual([x["source_sample_markers"] for x in recipe["pages"]],
                             [8, 56])
            result = audit_vector_pdf_bytes(pdf, recipe, path)
            self.assertTrue(result["all_original_cpp_tri_uv_polygons_pdf_matched"])
            self.assertEqual(result["raster_xobjects_or_inline_images"], 0)
            self.assertEqual([p["fonts_embedded"] for p in result["pages"]], [1, 1])
            self.assertFalse(result["scientific_lod_qualified"])

    def test_missing_original_cpp_raw_evidence_blocks_publication(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            path = synthetic_vector_package(root)
            from .verify_native_lineage import NativeLineageValidationError
            with self.assertRaises((NativeLineageValidationError, ValueError)):
                export_pdf(root / "does-not-exist", root / "fake-scene.json",
                           path, root / "not-created")
            self.assertFalse((root / "not-created").exists())

    def test_forged_second_accepted_epoch_or_lod_refused(self):
        for field, value in (("accepted_native_step", 2),
                             ("scientific_lod_qualified", True),
                             ("physical_node_welding_certified", True)):
            with self.subTest(field=field), TemporaryDirectory() as folder:
                path = synthetic_vector_package(Path(folder))
                manifest_file = path / "manifest.json"
                manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                manifest["figures"][0][field] = value
                manifest_file.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaises(ValueError):
                    render_pdf_from_source_vectors(path)

    def test_changed_source_svg_without_original_digest_fails_closed(self):
        with TemporaryDirectory() as folder:
            path = synthetic_vector_package(Path(folder))
            svg = path / "book-accepted-step1-uv.svg"
            svg.write_bytes(svg.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "v53_original_source_svg_sha_mismatch"):
                render_pdf_from_source_vectors(path)

    def test_svg_active_raster_even_with_forged_matching_digest_rejected(self):
        for component in (b"<image href='https://example.org/x'/>",
                          b"<script>alert(1)</script>",
                          b"<foreignObject>wrong</foreignObject>"):
            with self.subTest(component=component), TemporaryDirectory() as folder:
                path = synthetic_vector_package(Path(folder))
                original = (path / "book-accepted-step1-uv.svg").read_bytes()
                injected = original.replace(b"</svg>", component+b"</svg>")
                rewrite_receipt(path, 0, injected)
                with self.assertRaises(ValueError):
                    render_pdf_from_source_vectors(path)

    def test_source_markers_missing_even_if_svg_hash_forged_is_rejected(self):
        with TemporaryDirectory() as folder:
            path = synthetic_vector_package(Path(folder))
            svgfile = path / "book-accepted-step1-uv.svg"
            root = ET.fromstring(svgfile.read_bytes())
            circle = root.find('.//{http://www.w3.org/2000/svg}circle')
            self.assertIsNotNone(circle)
            panel = root.find('.//{http://www.w3.org/2000/svg}g')
            self.assertIsNotNone(panel)
            panel.remove(circle)
            rewrite_receipt(path, 0, ET.tostring(root, encoding="utf-8"))
            with self.assertRaisesRegex(ValueError, "v53_original_svg_face_patch_samples_changed"):
                render_pdf_from_source_vectors(path)

    def test_pdf_wrong_physical_page_dimensions_rejected(self):
        import fitz
        with TemporaryDirectory() as folder:
            path = synthetic_vector_package(Path(folder))
            pdf, receipt = render_pdf_from_source_vectors(path)
            with fitz.open(stream=pdf, filetype="pdf") as doc:
                doc[0].set_mediabox(fitz.Rect(0, 0, 900, 900))
                changed = doc.tobytes()
            forged = dict(receipt, pdf_sha256=sha256(changed).hexdigest(),
                          pdf_size_bytes=len(changed))
            with self.assertRaisesRegex(ValueError, "v53_pdf_wrong_physical_article_dimensions"):
                audit_vector_pdf_bytes(changed, forged, path)

    def test_pdf_extra_native_looking_polygon_rejected(self):
        import fitz
        with TemporaryDirectory() as folder:
            path = synthetic_vector_package(Path(folder))
            pdf, receipt = render_pdf_from_source_vectors(path)
            with fitz.open(stream=pdf, filetype="pdf") as doc:
                doc[0].draw_rect(fitz.Rect(10, 10, 30, 30),
                    color=(36/255,77/255,98/255), fill=(220/255,236/255,242/255))
                changed = doc.tobytes()
            forged = dict(receipt, pdf_sha256=sha256(changed).hexdigest(),
                          pdf_size_bytes=len(changed))
            with self.assertRaisesRegex(ValueError, "v53_pdf_original_face_or_marker_drawings_missing"):
                audit_vector_pdf_bytes(changed, forged, path)

    def test_pdf_hidden_raster_xobject_rejected(self):
        import fitz
        from PIL import Image
        from io import BytesIO
        with TemporaryDirectory() as folder:
            path = synthetic_vector_package(Path(folder))
            pdf, receipt = render_pdf_from_source_vectors(path)
            stream = BytesIO()
            Image.new("RGB", (2, 2), (255, 0, 0)).save(stream, format="PNG")
            with fitz.open(stream=pdf, filetype="pdf") as doc:
                doc[0].insert_image(fitz.Rect(0, 0, 3, 3), stream=stream.getvalue())
                changed = doc.tobytes()
            forged = dict(receipt, pdf_sha256=sha256(changed).hexdigest(),
                          pdf_size_bytes=len(changed))
            with self.assertRaisesRegex(ValueError, "v53_pdf_contains_raster_image_xobject"):
                audit_vector_pdf_bytes(changed, forged, path)

    def test_pdf_additional_unembedded_font_rejected(self):
        import fitz
        with TemporaryDirectory() as folder:
            path = synthetic_vector_package(Path(folder))
            pdf, receipt = render_pdf_from_source_vectors(path)
            with fitz.open(stream=pdf, filetype="pdf") as doc:
                doc[0].insert_text((20, 20), "FAKE", fontname="helv", fontsize=7)
                changed = doc.tobytes()
            forged = dict(receipt, pdf_sha256=sha256(changed).hexdigest(),
                          pdf_size_bytes=len(changed))
            with self.assertRaisesRegex(ValueError, "v53_pdf_font_missing_or_not_embedded"):
                audit_vector_pdf_bytes(changed, forged, path)


if __name__ == "__main__":
    unittest.main()