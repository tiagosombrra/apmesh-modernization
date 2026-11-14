"""Semantic and negative tests for synthetic narrative SVG output."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from .metric2d import Metric2D, rotated_diagonal
from .storyboards import (quadrilateral_boundary_parity, render_all_quad_parity,
                          render_anisotropy_story, render_hybrid_story)
from .svg_figure import audit_svg

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "cases" / "synthetic_quad_aft_transition.obj"


class StoryboardsTests(unittest.TestCase):
    def test_hybrid_six_panels_and_true_face_inventory(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"hybrid.svg"
            r=render_hybrid_story(FIXTURE,path)
            self.assertEqual((r["panel_count"],r["observed_generator_events"]),(6,0))
            self.assertEqual(r["metadata"]["cells"],{"quad":1,"triangle":8})
            root=ET.parse(path).getroot()
            faces=[el for el in root.iter() if "data-panel-face" in el.attrib]
            self.assertEqual(sum(f.attrib["data-panel-face"]=="5" for f in faces),9)
            self.assertEqual(sum(f.attrib["data-panel-face"]=="6" for f in faces),9)
            self.assertTrue(all(f.attrib.get("data-cell-type") in ("triangle","quad") for f in faces))
            self.assertEqual(root.attrib["data-provenance"],"SIMULATED")
            self.assertTrue(audit_svg(path)["vector_only"])

    def test_hybrid_repeatability_and_bound_to_fixture(self):
        with tempfile.TemporaryDirectory() as td:
            a,b=Path(td)/"a.svg",Path(td)/"b.svg"
            x=render_hybrid_story(FIXTURE,a)
            y=render_hybrid_story(FIXTURE,b)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            self.assertEqual(x["svg_sha256"],y["svg_sha256"])
            self.assertEqual(hashlib.sha256(a.read_bytes()).hexdigest(),x["svg_sha256"])
            self.assertEqual(x["metadata"]["stage_types"],["simulated"]*6)

    def test_hybrid_rejects_wrong_fixture_and_unmarked_source(self):
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/"bad.obj"
            f.write_text(FIXTURE.read_text())
            with self.assertRaisesRegex(ValueError,"unexpected_synthetic_hybrid_fixture"):
                render_hybrid_story(f,Path(td)/"out.svg")

    def test_all_quad_parity_and_vector_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"parity.svg"
            receipt=render_all_quad_parity(path)
            self.assertEqual(receipt["panel_count"],2)
            self.assertEqual(receipt["metadata"]["positive"]["boundary_edges"],8)
            self.assertFalse(receipt["metadata"]["negative"]["conforming_all_quad_disk_exists"])
            self.assertTrue(audit_svg(path)["vector_only"])
            self.assertIn(b"SIMULATED",path.read_bytes())

    def test_reject_broken_or_nonmanifold_quad_topology(self):
        with self.assertRaisesRegex(ValueError,"invalid_all_quad_cell"):
            quadrilateral_boundary_parity([(0,1,1,3)])
        with self.assertRaisesRegex(ValueError,"nonmanifold_quad_edge"):
            quadrilateral_boundary_parity([(0,1,4,3),(1,0,5,6),(0,1,7,8)])

    def test_symmetric_positive_definite_metric_oracles(self):
        iso=Metric2D(1,0,1)
        ani=Metric2D(16,0,1)
        self.assertEqual(iso.eigenvalues,(1,1))
        self.assertEqual(ani.eigenvalues,(1,16))
        self.assertAlmostEqual(ani.length(.25,0),1)
        self.assertAlmostEqual(ani.length(0,1),1)
        self.assertAlmostEqual(ani.length(1,0),4)
        self.assertAlmostEqual(ani.unit_ellipse_axes()[0],.25)
        self.assertAlmostEqual(ani.unit_ellipse_axes()[1],1)

    def test_metric_rotation_covariance(self):
        angle=math.pi/4
        metric=rotated_diagonal(16,1,angle)
        c,s=math.cos(angle),math.sin(angle)
        self.assertAlmostEqual(metric.length(c*.25,s*.25),1)
        self.assertAlmostEqual(metric.length(-s,c),1)
        self.assertAlmostEqual(metric.squared_length(c,s),16)
        self.assertAlmostEqual(metric.eigenvalues[0],1)
        self.assertAlmostEqual(metric.eigenvalues[1],16)

    def test_metric_negative_and_nonfinite(self):
        for values in [(1,0,0),(1,0,-1),(1,2,1),(0,0,1)]:
            with self.subTest(values=values),self.assertRaisesRegex(ValueError,"metric_not_spd"):
                Metric2D(*values)
        with self.assertRaisesRegex(ValueError,"nonfinite_metric"):
            Metric2D(math.nan,0,1)
        with self.assertRaisesRegex(ValueError,"nonfinite_edge"):
            Metric2D(1,0,1).length(math.inf,0)

    def test_metric_story_is_vector_and_reproducible(self):
        with tempfile.TemporaryDirectory() as td:
            a,b=Path(td)/"first.svg",Path(td)/"second.svg"
            x=render_anisotropy_story(a)
            render_anisotropy_story(b)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            self.assertEqual(x["panel_count"],2)
            self.assertEqual(x["metadata"]["tensor_source"],"synthetic_prescribed")
            self.assertTrue(audit_svg(a)["vector_only"])


if __name__ == "__main__":
    unittest.main()
