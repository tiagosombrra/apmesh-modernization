"""Independent analytic, metamorphic, and negative tests for Studio S2."""

from __future__ import annotations

from dataclasses import replace
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from .import_obj import import_obj
from .metric2d import Metric2D, rotated_diagonal
from .model import MeshDocument, MeshFace
from .quality_analysis import QualityError, analyze_mesh, edge_metric_length
from .topology_audit import TopologyError, audit_topology

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "cases"


def fixture(name: str) -> MeshDocument:
    return import_obj(FIXTURES / (name + ".obj"))


class ScientificGeometryTests(unittest.TestCase):
    def test_analytic_right_triangle_mean_ratio_and_area(self):
        report = analyze_mesh(fixture("synthetic_single_triangle"))
        face = report["cells"][0]
        self.assertAlmostEqual(face["triangle_mean_ratio"], math.sqrt(3)/2)
        self.assertAlmostEqual(face["physical_area"], .5)
        self.assertAlmostEqual(face["uv_signed_area"], .5)
        self.assertIsNone(face["planar_quad_min_scaled_jacobian"])
        self.assertEqual(face["physical_orientation"], "UNVERIFIED_NO_SOURCE_NORMAL")
        self.assertIsNone(report["measures"]["planar_quad_min_scaled_jacobian_3d_v1"])
        self.assertFalse(report["source_surface_global_certification"])

    def test_independent_equilateral_triangle_reference(self):
        sqrt3=math.sqrt(3)
        document = replace(fixture("synthetic_single_triangle"),
                           points=((0,0,0),(1,0,0),(.5,sqrt3/2,0)))
        report=analyze_mesh(document)
        self.assertAlmostEqual(report["cells"][0]["triangle_mean_ratio"],1)
        self.assertAlmostEqual(report["cells"][0]["physical_area"],sqrt3/4)

    def test_rigid_motion_preserves_shape_scores_and_physical_areas(self):
        original=fixture("synthetic_quad_aft_transition")
        a=analyze_mesh(original)
        # A rigid motion must preserve all Euclidean cell-quality measures.
        rotated=replace(original,points=tuple((-y+3,x-2,z+5) for x,y,z in original.points))
        b=analyze_mesh(rotated)
        for left,right in zip(a["cells"],b["cells"]):
            self.assertAlmostEqual(left["physical_area"],right["physical_area"])
            self.assertEqual(left["triangle_mean_ratio"],right["triangle_mean_ratio"])
            self.assertAlmostEqual(left["planar_quad_min_scaled_jacobian"] or 0,
                                   right["planar_quad_min_scaled_jacobian"] or 0)
        self.assertEqual(a["topology"],b["topology"])

    def test_square_quad_planar_min_scaled_jacobian(self):
        report = analyze_mesh(fixture("synthetic_single_quad"))
        face = report["cells"][0]
        self.assertAlmostEqual(face["planar_quad_min_scaled_jacobian"], 1)
        self.assertAlmostEqual(face["quad_relative_planarity"],0)
        self.assertAlmostEqual(face["physical_area"],1)
        self.assertAlmostEqual(face["uv_signed_area"],1)
        self.assertIsNone(face["triangle_mean_ratio"])

    def test_curved_nonplanar_quads_not_given_planar_quality(self):
        baseline=fixture("synthetic_curved_bezier_grid")
        # This separable reference has individually coplanar quad corners.
        # Perturb one shared XYZ vertex to force nonplanar quads without
        # replacing the immutable original fixture or its UV coordinates.
        altered=list(baseline.points)
        x,y,z=altered[4]
        altered[4]=(x,y,z+0.125)
        report=analyze_mesh(replace(baseline,points=tuple(altered)))
        self.assertEqual(report["cell_inventory"],{"triangle":0,"quad":4})
        self.assertTrue(any(row["quad_relative_planarity"]>1e-10 for row in report["cells"]))
        for cell in report["cells"]:
            if cell["quad_relative_planarity"]>1e-10:
                self.assertIsNone(cell["planar_quad_min_scaled_jacobian"])
        self.assertFalse(report["source_surface_global_certification"])

    def test_analytic_curved_bezier_surface_facet_orientations(self):
        def normal(u, v):
            return (-.4*u,-.2*v,1)
        report=analyze_mesh(fixture("synthetic_curved_bezier_grid"),source_normal=normal)
        self.assertTrue(all(cell["physical_orientation"]=="POSITIVE_AT_FACET_SAMPLES_ONLY"
                            for cell in report["cells"]))

    def test_bad_reference_normal_rejects_inverted_physical_facet(self):
        with self.assertRaisesRegex(QualityError,"inverted_physical_facet"):
            analyze_mesh(fixture("synthetic_single_triangle"),source_normal=lambda u,v:(0,0,-1))
        with self.assertRaisesRegex(QualityError,"degenerate_source_normal"):
            analyze_mesh(fixture("synthetic_single_triangle"),source_normal=lambda u,v:(0,0,0))
        with self.assertRaisesRegex(QualityError,"nonfinite_source_normal"):
            analyze_mesh(fixture("synthetic_single_triangle"),source_normal=lambda u,v:(0,0,math.nan))

    def test_uv_valid_but_physically_concave_planar_quad_rejects(self):
        source=fixture("synthetic_single_quad")
        # The quad preserves a convex UV square but has a concave XYZ polygon.
        doc=replace(source,points=((0,0,0),(1,0,0),(.25,.25,0),(0,1,0)))
        with self.assertRaisesRegex(QualityError,"folded_planar_quad"):
            analyze_mesh(doc)

    def test_positive_area_but_concave_uv_direct_document_rejected(self):
        source=fixture("synthetic_single_quad")
        # This quadrilateral has positive signed UV area, but one turn is negative.
        changed=replace(source.faces[0], uv=((0,0),(1,0),(.25,.25),(0,1)))
        with self.assertRaisesRegex(QualityError,"invalid_uv_quad_corner"):
            analyze_mesh(replace(source,faces=(changed,)))

    def test_physical_degeneration_and_nonfinite_rejection(self):
        source=fixture("synthetic_single_triangle")
        with self.assertRaisesRegex(QualityError,"degenerate_physical_facet"):
            analyze_mesh(replace(source,points=((0,0,0),(1,0,0),(2,0,0))))
        with self.assertRaisesRegex(QualityError,"nonfinite_physical_coordinate"):
            analyze_mesh(replace(source,points=((0,0,0),(1,0,math.nan),(0,1,0))))

    def test_separate_type_stats_and_no_averaging(self):
        report=analyze_mesh(fixture("synthetic_quad_aft_transition"))
        self.assertEqual(report["cell_inventory"],{"triangle":8,"quad":1})
        self.assertEqual(report["measures"]["triangle_mean_ratio_3d_v1"]["count"],8)
        self.assertEqual(report["measures"]["planar_quad_min_scaled_jacobian_3d_v1"]["count"],1)
        self.assertNotIn("mixed_quality_score",report["measures"])


class IndexedTopologyTests(unittest.TestCase):
    def test_single_tri_quad_and_hybrid_disk_chi(self):
        for case in ("synthetic_single_triangle","synthetic_single_quad","synthetic_quad_aft_transition"):
            with self.subTest(case=case):
                patch=audit_topology(fixture(case))["patches"][0]
                self.assertTrue(patch["is_indexed_disk"])
                self.assertEqual(patch["components"],1)
                self.assertEqual(patch["boundary_loops"],1)
                self.assertEqual(patch["euler_characteristic"],1)
                if case=="synthetic_single_quad":
                    self.assertTrue(patch["all_quad_fixed_boundary_even"])
                else:
                    self.assertIsNone(patch["all_quad_fixed_boundary_even"])

    def test_four_and_twenty_eight_patch_fans_stay_detached(self):
        for count in (4,28):
            doc=fixture(f"synthetic_shared_curve_fan{count}")
            report=audit_topology(doc)
            self.assertEqual(len(report["patches"]),count)
            self.assertEqual(len(report["source_shared_curves"]),1)
            self.assertEqual(report["source_shared_curves"][0]["incident_patch_count"],count)
            self.assertFalse(report["global_weld_certified"])
            self.assertEqual(report["reused_global_point_ids_across_groups"],[])
            self.assertTrue(all(p["is_indexed_disk"] for p in report["patches"]))

    def test_duplicate_physical_coordinates_do_not_create_weld(self):
        original=fixture("synthetic_shared_curve_fan3")
        # Repeated XYZ coordinates remain independent according to source IDs.
        self.assertTrue(len(set(original.points))<len(original.points))
        self.assertFalse(audit_topology(original)["global_weld_certified"])

    def test_obj_groups_may_classify_quad_vs_aft_not_patches(self):
        original=fixture("synthetic_quad_aft_transition")
        # P1-style groups distinguish algorithms, not physical patches.
        labeled=tuple(replace(f,group="QUAD" if f.element_type=="quad" else "TRI_AFT")
                      for f in original.faces)
        doc=replace(original,faces=labeled,patch_ownership="unknown",source_curves=())
        report=audit_topology(doc)
        self.assertEqual(report["group_label_semantics"],"untrusted_obj_group_labels_not_patch_ids")
        self.assertEqual(len(report["patches"]),2)
        self.assertTrue(report["combined_indexed_face_complex"]["is_indexed_disk"])
        self.assertEqual(report["combined_indexed_face_complex"]["face_count"],9)
        self.assertFalse(report["global_weld_certified"])

    def test_reused_global_ids_between_groups_explicitly_reported(self):
        base=fixture("synthetic_single_triangle")
        reused=replace(base,faces=base.faces+(replace(base.faces[0],group="other",line_number=999),))
        report=audit_topology(reused)
        self.assertEqual(report["reused_global_point_ids_across_groups"],[0,1,2])
        self.assertFalse(report["global_weld_certified"])

    def test_wrong_shared_winding_rejected(self):
        base=fixture("synthetic_planar_quad_grid")
        badfaces=list(base.faces)
        old=badfaces[1]
        badfaces[1]=replace(old,vertices=tuple(reversed(old.vertices)))
        with self.assertRaisesRegex(TopologyError,"inconsistent_edge_winding"):
            audit_topology(replace(base,faces=tuple(badfaces)))

    def test_nonmanifold_three_incident_edge_rejected(self):
        base=fixture("synthetic_single_triangle")
        a,b,c=base.faces[0].vertices
        faces=(base.faces[0],replace(base.faces[0],vertices=(b,a,c)),base.faces[0])
        with self.assertRaisesRegex(TopologyError,"nonmanifold_patch_edge"):
            audit_topology(replace(base,faces=faces))

    def test_disconnected_disks_not_declared_single_disk(self):
        doc=fixture("synthetic_planar_quad_grid")
        faces=(doc.faces[0],doc.faces[-1])
        # The quads at diagonal corners meet only at a point, not an edge.
        stats=audit_topology(replace(doc,faces=faces))["patches"][0]
        self.assertFalse(stats["is_indexed_disk"])
        self.assertEqual(stats["components"],2)


class MetricFieldTests(unittest.TestCase):
    def test_known_diagonal_unit_length_and_rotation_covariance(self):
        metric=Metric2D(16,0,1)
        self.assertAlmostEqual(edge_metric_length((0,0),(.25,0),metric),1)
        self.assertAlmostEqual(edge_metric_length((0,0),(0,1),metric),1)
        for angle in (0,math.pi/6,math.pi/4,math.pi/2):
            rotated=rotated_diagonal(16,1,angle)
            c,s=math.cos(angle),math.sin(angle)
            self.assertAlmostEqual(edge_metric_length((0,0),(.25*c,.25*s),rotated),1)
            self.assertAlmostEqual(edge_metric_length((0,0),(-s,c),rotated),1)

    def test_two_point_quadrature_linear_metric_reversed_edge(self):
        # A spatially varying metric is integrated, not evaluated at midpoint only.
        field=lambda u,v:Metric2D((1+u)**2,0,1)
        value=edge_metric_length((0,0),(1,0),field)
        self.assertAlmostEqual(value,1.5)
        self.assertAlmostEqual(value,edge_metric_length((1,0),(0,0),field))

    def test_anisotropy_length_is_not_renamed_shape_quality(self):
        report=analyze_mesh(fixture("synthetic_single_quad"),
                            metric_field=Metric2D(16,0,1),metric_frame="uv")
        self.assertEqual(report["measures"]["metric_basis"],"uv")
        self.assertEqual(report["cells"][0]["metric_edge_lengths"],(4,1,4,1))
        self.assertFalse(report["source_surface_global_certification"])
        self.assertEqual(report["measures"]["planar_quad_min_scaled_jacobian_3d_v1"]["count"],1)

    def test_metric_basis_required_and_sample_rejected(self):
        doc=fixture("synthetic_single_quad")
        with self.assertRaisesRegex(QualityError,"metric_frame_required_uv"):
            analyze_mesh(doc,metric_field=Metric2D(1,0,1))
        with self.assertRaisesRegex(QualityError,"invalid_metric_sample"):
            edge_metric_length((0,0),(1,0),lambda u,v:None)
        with self.assertRaisesRegex(QualityError,"nonfinite_uv"):
            edge_metric_length((0,0),(math.nan,0),Metric2D(1,0,1))

    def test_missing_uv_blocks_metric_but_not_geometry(self):
        original=fixture("synthetic_single_triangle")
        without_uv=replace(original,faces=(replace(original.faces[0],uv=None),))
        self.assertIsNone(analyze_mesh(without_uv)["cells"][0]["uv_signed_area"])
        with self.assertRaisesRegex(QualityError,"metric_requires_uv"):
            analyze_mesh(without_uv,metric_field=Metric2D(1,0,1),metric_frame="uv")


class HeadlessCliTests(unittest.TestCase):
    def test_cli_deterministic_structured_export(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            a,b=td/"one.json",td/"two.json"
            cmd=[sys.executable,"-m","tools.mesh_studio.analyze_cli",
                 str(FIXTURES/"synthetic_quad_aft_transition.obj"),"--output"]
            root=Path(__file__).resolve().parents[2]
            subprocess.run(cmd+[str(a),"--metric-diagonal","16","1"],cwd=root,check=True,capture_output=True)
            subprocess.run(cmd+[str(b),"--metric-diagonal","16","1"],cwd=root,check=True,capture_output=True)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            record=json.loads(a.read_text())
            self.assertEqual(record["metric_provenance"],"USER_SUPPLIED_NOT_ORIGINAL_GENERATOR_FIELD")
            self.assertEqual(record["cell_inventory"],{"quad":1,"triangle":8})
            self.assertFalse(record["source_surface_global_certification"])


if __name__ == "__main__":
    unittest.main()
