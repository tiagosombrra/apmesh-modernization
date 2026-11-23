"""Synthetic-only adversarial tests for a source-preserving Book print-layout tool.

These fixtures are not original C++ acceptance evidence. Original native
qualification is performed separately by the same-run source CI.
"""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET

from .native_book_print_layout import (
    APPENDIX, APPENDIX_SLOTS, EXAMPLE, EXAMPLE_SLOTS, SVG_NS,
    _source_book, audit_pdf_bytes, render_pdf, render_pair,
)


def synthetic_book(directory: Path) -> Path:
    """Generate all slot/face/marker keys as a synthetic source-only fixture."""
    directory.mkdir()
    attrib = {
        "data-schema": "apmesh.meshstudio.v52.original_native_accepted_uv_vector.v1",
        "data-model": "book",
        "data-original-source-ndjson-sha256": "e" * 64,
        "data-original-accepted-step": "1",
        "data-physical-welding-certified": "false",
        "data-scientific-lod-qualified": "false",
    }
    root = ET.Element(f"{{{SVG_NS}}}svg", attrib)
    for slot in range(28):
        group = ET.SubElement(root, f"{{{SVG_NS}}}g", {
            "data-original-patch-slot": str(slot),
            "data-original-native-patch-id": "0",
            "data-original-face-count": "152",
        })
        ET.SubElement(group, f"{{{SVG_NS}}}text").text = f"Patch {slot}"
        ET.SubElement(group, f"{{{SVG_NS}}}rect", {
            "x": "0", "y": "0", "width": "158", "height": "158",
            "fill": "#f7fafc",
        })
        for element_slot in range(152):
            ET.SubElement(group, f"{{{SVG_NS}}}polygon", {
                "points": "0,0 9.875,0 0,9.875",
                "fill": "#dcecf2", "stroke": "#244d62",
                "data-original-patch-slot": str(slot),
                "data-native-patch-id": "0",
                "data-original-element-slot": str(element_slot),
                "data-native-element-id": str(113 + slot * 152 + element_slot),
                "data-original-native-node-ids": "1,2,3",
                "data-original-local-uv": "0,1;0.0625,1;0,0.9375",
            })
        for ordinal in range(13):
            ET.SubElement(group, f"{{{SVG_NS}}}circle", {
                "cx": "0", "cy": str(ordinal * 9.875),
                "r": "2.6", "fill": "#bd503f",
                "data-original-patch-slot": str(slot),
                "data-source-curve-slot": "3",
                "data-original-source-sample-ordinal": str(ordinal),
                "data-sample-identity": "original-native-corner-not-physical-welding",
            })
    raw = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    (directory / "book-accepted-step1-uv.svg").write_bytes(raw)
    item = {
        "model": "book", "accepted_native_step": 1,
        "original_source_patch_count": 28,
        "original_native_tri_faces": 4256,
        "observed_source_curve_sample_marker_count": 364,
        "source_revalidated_from_original_postcommit_raw_ndjson": True,
        "scientific_lod_qualified": False,
        "physical_node_welding_certified": False,
        "svg_filename": "book-accepted-step1-uv.svg",
        "svg_sha256": sha256(raw).hexdigest(),
        "svg_size_bytes": len(raw),
        "original_source_ndjson_sha256": "e" * 64,
    }
    (directory / "manifest.json").write_text(json.dumps({
        "schema": "apmesh.meshstudio.v52.original_native_accepted_publication.v1",
        "source_cpp_raw_ndjson_reaudited": True,
        "scientific_lod_qualified": False,
        "original_physical_node_welding_certified": False,
        "figures": [item],
    }), encoding="utf-8")
    return directory


def recompute_synthetic_svg_digest(directory: Path, root: ET.Element) -> None:
    raw = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    (directory / "book-accepted-step1-uv.svg").write_bytes(raw)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    manifest["figures"][0]["svg_sha256"] = sha256(raw).hexdigest()
    manifest["figures"][0]["svg_size_bytes"] = len(raw)
    (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class BookPrintLayoutSyntheticContracts(unittest.TestCase):
    def test_exact_four_panel_cover_and_vector_pdf(self):
        with TemporaryDirectory(prefix="v57-synthetic-pdf-") as folder:
            root = Path(folder)
            fixture = synthetic_book(root / "fixture")
            pdf, recipe = render_pdf(fixture, APPENDIX_SLOTS, APPENDIX)
            audit = audit_pdf_bytes(pdf, recipe, fixture)
            self.assertEqual(len(audit["pages"]), 7)
            self.assertEqual(audit["original_face_paths_matched"], 4256)
            self.assertEqual(audit["original_marker_positions_matched"], 364)
            self.assertTrue(all(p["min_font_pt"] >= 9 for p in audit["pages"]))
            self.assertEqual(audit["raster_images"], 0)
            self.assertFalse(audit["scientific_lod_qualified"])
            again, same = render_pdf(fixture, APPENDIX_SLOTS, APPENDIX)
            self.assertEqual((pdf, recipe), (again, same))
            example, subset = render_pdf(fixture, (EXAMPLE_SLOTS,), EXAMPLE)
            result = audit_pdf_bytes(example, subset, fixture)
            self.assertEqual(result["original_face_paths_matched"], 608)
            self.assertEqual(result["original_marker_positions_matched"], 52)

    def test_preview_does_not_claim_original_cpp_reauthentication(self):
        with TemporaryDirectory(prefix="v57-synthetic-preview-") as folder:
            root = Path(folder)
            fixture = synthetic_book(root / "fixture")
            result = render_pair(fixture, root / "output")
            self.assertTrue(result["prototype_only_without_original_cpp"])
            self.assertFalse(result["native_source_reauthenticated_in_same_run"])

    def test_missing_patch_rejected_even_with_rehashed_svg(self):
        with TemporaryDirectory(prefix="v57-synthetic-missing-") as folder:
            fixture = synthetic_book(Path(folder) / "fixture")
            path = fixture / "book-accepted-step1-uv.svg"
            root = ET.fromstring(path.read_bytes())
            group = root.find(f"{{{SVG_NS}}}g")
            root.remove(group)
            recompute_synthetic_svg_digest(fixture, root)
            with self.assertRaisesRegex(ValueError, "missing_original_book_faces_or_charts"):
                _source_book(fixture)

    def test_duplicate_patch_slot_rejected_even_with_rehashed_svg(self):
        with TemporaryDirectory(prefix="v57-synthetic-duplicate-") as folder:
            fixture = synthetic_book(Path(folder) / "fixture")
            root = ET.fromstring((fixture / "book-accepted-step1-uv.svg").read_bytes())
            group = root.findall(f"{{{SVG_NS}}}g")[1]
            group.set("data-original-patch-slot", "0")
            recompute_synthetic_svg_digest(fixture, root)
            with self.assertRaisesRegex(ValueError, "duplicate_or_outside_book_patch_slot"):
                _source_book(fixture)

    def test_tampered_uv_does_not_pass_by_changing_source_hash(self):
        with TemporaryDirectory(prefix="v57-synthetic-uv-") as folder:
            fixture = synthetic_book(Path(folder) / "fixture")
            root = ET.fromstring((fixture / "book-accepted-step1-uv.svg").read_bytes())
            first = root.find(f".//{{{SVG_NS}}}polygon")
            first.set("points", "0,0 14.875,0 0,9.875")
            recompute_synthetic_svg_digest(fixture, root)
            with self.assertRaisesRegex(ValueError, "source_polygon_point_not_original_uv"):
                _source_book(fixture)

    def test_fake_second_accepted_epoch_blocks_print(self):
        with TemporaryDirectory(prefix="v57-synthetic-fake-lod-") as folder:
            fixture = synthetic_book(Path(folder) / "fixture")
            manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
            manifest["figures"][0]["accepted_native_step"] = 2
            (fixture / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source_book_outside_certified_scope"):
                _source_book(fixture)

    def test_extra_path_and_wrong_page_box_rejected(self):
        import fitz
        with TemporaryDirectory(prefix="v57-synthetic-pdf-mutate-") as folder:
            fixture = synthetic_book(Path(folder) / "fixture")
            pdf, recipe = render_pdf(fixture, (EXAMPLE_SLOTS,), EXAMPLE)
            with fitz.open(stream=pdf, filetype="pdf") as doc:
                doc[0].draw_rect(fitz.Rect(10, 10, 25, 25))
                changed = doc.tobytes()
            forged = dict(recipe, pdf_sha256=sha256(changed).hexdigest(),
                          pdf_size_bytes=len(changed))
            with self.assertRaisesRegex(ValueError, "pdf_unexpected_or_missing_vector_drawable"):
                audit_pdf_bytes(changed, forged, fixture)
            with fitz.open(stream=pdf, filetype="pdf") as doc:
                doc[0].set_mediabox(fitz.Rect(0, 0, 900, 900))
                changed = doc.tobytes()
            forged = dict(recipe, pdf_sha256=sha256(changed).hexdigest(),
                          pdf_size_bytes=len(changed))
            with self.assertRaisesRegex(ValueError, "wrong_physical_media_box"):
                audit_pdf_bytes(changed, forged, fixture)

    def test_hidden_raster_xobject_rejected(self):
        import fitz
        from PIL import Image
        with TemporaryDirectory(prefix="v57-synthetic-raster-") as folder:
            fixture = synthetic_book(Path(folder) / "fixture")
            pdf, recipe = render_pdf(fixture, (EXAMPLE_SLOTS,), EXAMPLE)
            stream = BytesIO()
            Image.new("RGB", (2, 2), (255, 0, 0)).save(stream, format="PNG")
            with fitz.open(stream=pdf, filetype="pdf") as doc:
                doc[0].insert_image(fitz.Rect(10, 10, 12, 12), stream=stream.getvalue())
                changed = doc.tobytes()
            forged = dict(recipe, pdf_sha256=sha256(changed).hexdigest(),
                          pdf_size_bytes=len(changed))
            with self.assertRaisesRegex(ValueError, "raster_xobject_forbidden"):
                audit_pdf_bytes(changed, forged, fixture)


if __name__ == "__main__":
    unittest.main()
