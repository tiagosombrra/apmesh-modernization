"""Directed positive, adversarial and missing-original controls for S3.D."""
from __future__ import annotations

from hashlib import sha256
import copy
import re
import tempfile
from pathlib import Path
import unittest

import cadquery as cq

from s3d_canonical_feature_curves import audit, construct, interface_inventory
from s3c_step_source_gate import SOURCES


class FeatureGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/"box.step"
            cq.exporters.export(cq.Workplane().box(2,3,4).val(),str(source))
            cls.original = source.read_text()
        # A modified STEP supports a source-graph test, not valid native CAD.
        first = re.search(r"(#\d+)\s*=\s*PLANE\([^;]*;", cls.original)
        if first is None:
            raise AssertionError("Fixture missing STEP plane")
        replacement = first[1]+" = ( BOUNDED_SURFACE() B_SPLINE_SURFACE(1,2,()) RATIONAL_B_SPLINE_SURFACE(((1.,0.7))) SURFACE() );"
        cls.one_excluded = cls.original.replace(first[0], replacement)

    def graph(self, text):
        return construct(text, model="SYNTHETIC",source_sha256=sha256(text.encode()).hexdigest())

    def check(self, text, result):
        return audit(text,result,expected_model="SYNTHETIC",source_sha256=sha256(text.encode()).hexdigest())

    def test_whole_box_has_zero_excluded_interfaces(self):
        graph=self.graph(self.original)
        self.assertEqual(graph["candidate_to_excluded_edges"],0)
        self.assertEqual(self.check(self.original,graph)["source_edges_checked"],0)
        self.assertEqual(graph["apmesh_generation"],"NOT_RUN")

    def test_five_candidate_faces_share_four_exact_original_lines(self):
        graph=self.graph(self.one_excluded)
        self.assertEqual(graph["candidate_face_count"],5)
        self.assertEqual(graph["candidate_to_excluded_edges"],4)
        self.assertEqual(graph["neighbor_support_histogram"],{"COMPLEX_RATIONAL_B_SPLINE_SURFACE":4})
        self.assertEqual(graph["source_master_edge_types"],{"LINE":4})
        self.assertEqual(len(graph["global_control_points_xyz_mm"]),12)
        audit_report=self.check(self.one_excluded,graph)
        self.assertEqual(audit_report["source_edges_checked"],4)
        self.assertEqual(audit_report["sample_count"],28)
        self.assertLess(audit_report["maximum_sampled_pointwise_residual_mm"],1e-12)

    def test_original_edge_ids_not_coordinate_welded(self):
        a=cq.Workplane().box(1,1,1).val()
        b=cq.Workplane().box(1,1,1).translate((1+1e-10,0,0)).val()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"two.step"
            cq.exporters.export(cq.Compound.makeCompound([a,b]),str(p))
            source=p.read_text()
        plane=re.search(r"(#\d+)\s*=\s*PLANE\([^;]*;",source)
        modified=source.replace(plane[0],plane[1]+" = ( BOUNDED_SURFACE() B_SPLINE_SURFACE(1,2,()) RATIONAL_B_SPLINE_SURFACE(((1.,0.8))) SURFACE() );")
        graph=self.graph(modified)
        self.assertEqual(graph["candidate_to_excluded_edges"],4)
        self.assertEqual(self.check(modified,graph)["source_edges_checked"],4)
        self.assertEqual(graph["source_topological_identity_only"],True)

    def test_reshuffled_feature_records_do_not_misassign_source_ids(self):
        graph=self.graph(self.one_excluded)
        forged=copy.deepcopy(graph)
        forged["feature_curves"][0]["original_edge_curve_id"] += 100000
        with self.assertRaisesRegex(ValueError,"checksum"):
            self.check(self.one_excluded,forged)

    def test_forged_checksum_does_not_allow_changed_source_edge_id(self):
        import json
        graph=self.graph(self.one_excluded)
        forged=copy.deepcopy(graph)
        forged["feature_curves"][0]["original_edge_curve_id"] += 100000
        raw={k:v for k,v in forged.items() if k!="graph_sha256"}
        forged["graph_sha256"]=sha256(json.dumps(raw,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,"source edge identity"):
            self.check(self.one_excluded,forged)

    def test_control_tampering_cannot_pass_even_with_recomputed_checksum(self):
        import json
        graph=self.graph(self.one_excluded)
        forged=copy.deepcopy(graph)
        forged["global_control_points_xyz_mm"][0]=[1000.,1000.,1000.]
        raw={k:v for k,v in forged.items() if k!="graph_sha256"}
        forged["graph_sha256"]=sha256(json.dumps(raw,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,"line segments|infinite LINE"):
            self.check(self.one_excluded,forged)

    def test_reverse_face_side_is_preserved(self):
        graph=self.graph(self.one_excluded)
        for item in graph["feature_curves"]:
            ids=item["canonical_cubic_control_ids"]
            expected=ids if item["planar_face_uses_canonical_direction"] else ids[::-1]
            self.assertEqual(item["selected_face_side_control_ids"],expected)

    def test_source_graph_records_no_accepted_mesh(self):
        graph=self.graph(self.one_excluded)
        self.assertFalse(graph["complete_original_atlas"])
        self.assertEqual(graph["independent_native_brep_edge_map"],"NOT_RUN")
        self.assertEqual(graph["external_nonmanifold_positive"],"NOT_GRANTED")

    def test_missing_originals_skip_is_explicit(self):
        import os
        ws=os.environ.get("APMESH_REAL_CAD_WORKSPACE")
        if not ws:
            self.skipTest("Original MAMBO STEP files absent; this does not count as validation")
        for model,(name,digest,faces,candidates) in SOURCES.items():
            data=(Path(ws)/"sources"/name).read_bytes()
            self.assertEqual(sha256(data).hexdigest(),digest)
            graph=construct(data.decode(),model=model,source_sha256=digest)
            self.assertEqual(graph["candidate_face_count"],candidates)
            self.assertGreater(graph["candidate_to_excluded_edges"],0)
            self.check(data.decode(),graph)


if __name__=="__main__":
    unittest.main()
