"""Adversarial controls for a restricted STEP face-edge reference screen."""
from __future__ import annotations

import copy
import unittest
from step_graph_screen import screen


def example(faces=3, distinct_edges=False):
    """Build a STEP reference graph, not a geometric CAD fixture."""
    out = ["ISO-10303-21;", "DATA;"]
    for k in range(faces):
        edge_id = 1 + k if distinct_edges else 1
        if distinct_edges or k == 0:
            out.append(f"#{edge_id}=EDGE_CURVE('',#500,#501,#502,.T.);")
        out += [
            f"#{100+k}=ORIENTED_EDGE('',*,*,#{edge_id},.T.);",
            f"#{200+k}=EDGE_LOOP('',(#{100+k}));",
            f"#{300+k}=FACE_OUTER_BOUND('',#{200+k},.T.);",
            f"#{400+k}=ADVANCED_FACE('',(#{300+k}),#1000,.T.);",
        ]
    out.append("ENDSEC;")
    return "\n".join(out)


class TestSTEPGraphScreen(unittest.TestCase):
    def test_three_face_incidence_is_detected(self):
        s = screen(example(3))
        self.assertEqual(s["explicit_three_plus_face_edges"], 1)
        self.assertEqual(s["face_incidence_per_explicit_edge_histogram"], {3: 1})
        self.assertTrue(s["complete_explicit_edge_graph"])
        self.assertEqual(s["nonmanifold_admission"], "NOT_DETERMINED")

    def test_equal_geometry_different_entities_not_fused(self):
        s = screen(example(3, distinct_edges=True))
        self.assertEqual(s["face_incidence_per_explicit_edge_histogram"], {1: 3})
        self.assertEqual(s["explicit_three_plus_face_edges"], 0)

    def test_duplicate_id_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            screen(example(1) + "\n#1=EDGE_CURVE('',#500,#501,#502,.T.);")

    def test_non_step_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid STEP"):
            screen("NOT A STEP")

    def test_vertex_loop_reports_unresolved(self):
        source = example(1).replace("#200=EDGE_LOOP('',(#100));", "#200=VERTEX_LOOP('',#500);")
        s = screen(source)
        self.assertFalse(s["complete_explicit_edge_graph"])
        self.assertEqual(s["unresolved_face_edge_references"], 1)
        self.assertEqual(s["unreferenced_edge_curves"], 1)

    def test_intra_face_seam_not_three_distinct_faces(self):
        source = example(2).replace("#200=EDGE_LOOP('',(#100));", "#200=EDGE_LOOP('',(#100,#100,#100));")
        s = screen(source)
        self.assertEqual(s["within_face_repeated_edge_uses"], 2)
        self.assertEqual(s["face_incidence_per_explicit_edge_histogram"], {2: 1})


if __name__ == "__main__":
    unittest.main()
