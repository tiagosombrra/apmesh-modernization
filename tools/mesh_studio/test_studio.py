"""Independent functional regressions for the Mesh Studio first delivery."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from .import_obj import MeshImportError, import_obj
from .svg_figure import audit_svg, render_uv_svg

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class MeshStudioTests(unittest.TestCase):
    def test_original_corpus_positive_and_negative_cases(self):
        manifest = json.loads((FIXTURES / "manifest.json").read_text())
        good = bad = 0
        for case in manifest["fixture_cases"]:
            obj = FIXTURES / "cases" / f"{case['case_id']}.obj"
            diagnostic = case["expected"]["diagnostic"]
            with self.subTest(case=case["case_id"]):
                if diagnostic is None:
                    mesh = import_obj(obj)
                    self.assertTrue(mesh.synthetic)
                    self.assertEqual(mesh.triangles, case["expected"]["triangle_count"])
                    self.assertEqual(mesh.quads, case["expected"]["quad_count"])
                    good += 1
                else:
                    with self.assertRaises(MeshImportError) as caught:
                        import_obj(obj)
                    self.assertEqual(caught.exception.code, diagnostic)
                    bad += 1
        self.assertEqual((good, bad), (10, 6))

    def test_wavefront_separate_uv_indices_and_negative_relative_indices(self):
        obj = ("v 0 0 0\nv 1 0 0\nv 0 1 0\n"
               "vt 0 0\nvt 1 0\nvt 0 1\n"
               "g patchA\nf -3/-3 -2/-1 -1/-2\n")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mesh.obj"
            path.write_text(obj)
            with self.assertRaises(MeshImportError) as err:
                import_obj(path)
            self.assertEqual(err.exception.code, "uv_winding")
            path.write_text(obj.replace("f -3/-3 -2/-1 -1/-2", "f -3/-3 -2/-2 -1/-1"))
            mesh = import_obj(path)
            self.assertEqual(mesh.faces[0].uv, ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0)))

    def test_true_vector_figure_and_repeatable_digest(self):
        path = FIXTURES / "cases" / "synthetic_quad_aft_transition.obj"
        doc = import_obj(path)
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "first.svg", Path(tmp) / "second.svg"
            receipt = render_uv_svg(doc, a)
            render_uv_svg(doc, b)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(receipt["svg_sha256"], hashlib.sha256(a.read_bytes()).hexdigest())
            self.assertEqual(audit_svg(a, 9), {"vector_only": True, "raster_image_count": 0, "polygon_count": 9})
            self.assertIn(b"SYNTHETIC", a.read_bytes())

    def test_reject_raster_disguised_as_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raster.svg"
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg"><image href="data:image/png;base64,AA=="/></svg>')
            with self.assertRaisesRegex(ValueError, "non_vector_or_active_svg_content"):
                audit_svg(path)

    def test_generic_without_uv_is_not_a_source_uv_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            obj = Path(tmp) / "triangle.obj"
            obj.write_text("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n")
            doc = import_obj(obj)
            self.assertFalse(doc.synthetic)
            self.assertIsNone(doc.faces[0].uv)
            with self.assertRaisesRegex(ValueError, "uv_required_for_vector_figure"):
                render_uv_svg(doc, Path(tmp) / "wrong.svg")

    def test_strict_legacy_apmesh_header_and_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy.obj"
            path.write_text(" File Wavefront OBJ generated apMesh\n\n# File created: 2026-11-14\n"
                            "# of vertices\n3\nv 0 0 0\nv 1 0 0\nv 0 1 0\n"
                            "# of faces\n1\nf 1 2 3\n")
            doc = import_obj(path)
            self.assertEqual(doc.source_kind, "legacy_apmesh_obj")
            path.write_text(path.read_text().replace("# of faces\n1", "# of faces\n2"))
            with self.assertRaises(MeshImportError) as err:
                import_obj(path)
            self.assertEqual(err.exception.code, "legacy_count_mismatch")

    def test_mutation_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mutation.obj"
            for text, error in [
                ("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 0 2 3\n", "out_of_range_index"),
                ("v 0 0 nan\nv 1 0 0\nv 0 1 0\nf 1 2 3\n", "nonfinite_coordinate"),
                ("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 2\n", "repeated_vertex"),
                ("v 0 0 0\nv 1 0 0\nv 0 1 0\nmtllib hidden.mtl\nf 1 2 3\n", "external_material_not_allowed"),
                ("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3 2 1\n", "invalid_face_arity"),
            ]:
                with self.subTest(error=error):
                    path.write_text(text)
                    with self.assertRaises(MeshImportError) as err:
                        import_obj(path)
                    self.assertEqual(err.exception.code, error)


if __name__ == "__main__":
    unittest.main()
