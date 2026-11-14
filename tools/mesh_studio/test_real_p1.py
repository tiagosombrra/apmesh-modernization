"""Independent actual P1 artifact integration and adversarial integrity tests."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from .import_obj import import_obj, MeshImportError
from .p1_source_oracle import (SOURCE_OBJ_SHA256, P1QualificationError,
                               audit_original_surface, qualify_p1)
from .real_p1_cli import execute
from .svg_figure import audit_svg

ROOT = Path(__file__).parent / "fixtures" / "real_p1"


class RealP1IntegrationTests(unittest.TestCase):
    def document(self):
        return import_obj(ROOT/"accepted.obj")

    def receipt(self):
        return json.loads((ROOT/"generator_report.json").read_text(encoding="utf-8"))

    def test_exact_real_source_artifact_and_groups(self):
        doc=self.document()
        self.assertEqual(doc.source_sha256,SOURCE_OBJ_SHA256)
        self.assertFalse(doc.synthetic)
        self.assertEqual((len(doc.points),doc.quads,doc.triangles),(69,42,36))
        self.assertEqual(doc.groups,("QUAD","TRI_AFT"))
        self.assertIsNone(doc.semantic_sidecar_sha256)

    def test_original_ci_report_exact_source_binding(self):
        result=qualify_p1(self.document(),self.receipt())
        self.assertEqual(result["source"]["quad_tri_seam_edges"],20)
        self.assertEqual(result["source"]["outer_boundary_edges"],16)
        self.assertEqual(result["source"]["oriented_physical_facets"],120)
        self.assertGreater(result["source"]["minimum_facet_normal_alignment"],0.98)
        self.assertFalse(result["source"]["assertions"]["mixed_adaptive_epoch_qualified"])
        self.assertEqual(result["source"]["region_topology"]["tri_aft"],"indexed_annulus")

    def test_existing_source_corruption_controls_are_rejected(self):
        for suffix,expected in ((0,"invalid_vertex_arity"),(1,"invalid_face_arity")):
            with self.subTest(suffix=suffix):
                with self.assertRaises(MeshImportError) as ctx:
                    import_obj(ROOT/f"corrupt-{suffix}.obj")
                self.assertEqual(ctx.exception.code,expected)

    def test_false_generator_report_rejected(self):
        forged=self.receipt()
        forged["adaptive_epochs"]=2
        with self.assertRaisesRegex(P1QualificationError,"source_generator_receipt_mismatch"):
            qualify_p1(self.document(),forged)

    def test_missing_native_aft_receipt_rejected(self):
        forged=self.receipt()
        forged["native_AFT"]=False
        with self.assertRaisesRegex(P1QualificationError,"source_generator_receipt_mismatch"):
            qualify_p1(self.document(),forged)

    def test_wrong_obj_digest_rejected_even_if_geometry_is_valid(self):
        original=self.document()
        forged=replace(original,source_sha256="0"*64)
        with self.assertRaisesRegex(P1QualificationError,"source_digest_mismatch"):
            qualify_p1(forged,self.receipt())

    def test_bad_bezier_xyz_rejected_by_oracle_independent_of_sha(self):
        original=self.document()
        coords=list(original.points)
        coords[1]=(coords[1][0]+.01,*coords[1][1:])
        with self.assertRaisesRegex(P1QualificationError,"original_bezier_xyz_mismatch"):
            audit_original_surface(replace(original,points=tuple(coords)))

    def test_quad_triangle_source_group_mislabel_rejected(self):
        original=self.document()
        faces=list(original.faces)
        faces[0]=replace(faces[0],group="TRI_AFT")
        with self.assertRaisesRegex(P1QualificationError,"changed_element_class_groups|element_group_type_mismatch"):
            audit_original_surface(replace(original,faces=tuple(faces)))

    def test_invalid_seam_orientation_rejected(self):
        original=self.document()
        faces=list(original.faces)
        idx=next(i for i,face in enumerate(faces) if face.group=="TRI_AFT")
        f=faces[idx]
        faces[idx]=replace(f,vertices=f.vertices[::-1],uv=f.uv[::-1])
        with self.assertRaises(P1QualificationError):
            audit_original_surface(replace(original,faces=tuple(faces)))

    def test_reproducible_real_source_vector_figure_and_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a=execute(ROOT/"accepted.obj",ROOT/"generator_report.json",root/"run-a")
            b=execute(ROOT/"accepted.obj",ROOT/"generator_report.json",root/"run-b")
            self.assertEqual(a,b)
            self.assertEqual(a["source_obj_sha256"],SOURCE_OBJ_SHA256)
            self.assertEqual(audit_svg(root/"run-a"/"P1_real_hybrid_uv.svg",78)["polygon_count"],78)
            summary=json.loads((root/"run-a"/"P1_real_hybrid_audit.json").read_text())
            self.assertEqual(summary["real_mesh_quality"]["planar_quad_count_evaluated"],0)
            self.assertIsNone(summary["real_mesh_quality"]["planar_quad_min_scaled_jacobian_3d_v1"])
            self.assertEqual(summary["real_mesh_quality"]["triangle_mean_ratio_3d_v1"]["count"],36)
            self.assertEqual(summary["figure"]["vector_audit"]["raster_image_count"],0)
            self.assertFalse(a["synthetic"])

    def test_prevent_unintentional_output_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"figure"
            execute(ROOT/"accepted.obj",ROOT/"generator_report.json",p)
            with self.assertRaises(FileExistsError):
                execute(ROOT/"accepted.obj",ROOT/"generator_report.json",p)

    def test_source_raw_report_checksum_pinned(self):
        original=hashlib.sha256((ROOT/"accepted.obj").read_bytes()).hexdigest()
        self.assertEqual(original,self.receipt()["OBJ_sha256"])


if __name__ == "__main__":
    unittest.main()
