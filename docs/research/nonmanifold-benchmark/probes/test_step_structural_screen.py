"""Adversarial controls for the bounded STEP structural screen."""

import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location(
    "step_structural_screen", Path(__file__).parent / "step_structural_screen.py"
)
step = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(step)


def example(n_faces: int, distinct_edges: bool = False) -> str:
    """Build a minimal reference graph, not a geometric STEP solid."""
    rows = ["ISO-10303-21;", "DATA;"]
    if not distinct_edges:
        rows.append("#1=EDGE_CURVE('',#100,#101,#102,.T.);")
    for n in range(n_faces):
        edge_id = 1 + n if distinct_edges else 1
        if distinct_edges:
            rows.append(f"#{edge_id}=EDGE_CURVE('',#100,#101,#102,.T.);")
        rows.extend([
            f"#{10+n}=ORIENTED_EDGE('',*,*,#{edge_id},.T.);",
            f"#{20+n}=EDGE_LOOP('',(#{10+n}));",
            f"#{30+n}=FACE_OUTER_BOUND('',#{20+n},.T.);",
            f"#{40+n}=ADVANCED_FACE('',(#{30+n}),#200,.T.);",
        ])
    return "\n".join(rows) + "\nENDSEC; END-ISO-10303-21;"


class StepStructuralScreenTests(unittest.TestCase):
    def test_three_faces_sharing_exact_edge(self):
        report = step.screen(example(3))
        self.assertEqual(report["edge_to_distinct_face_incidence_histogram"], {3: 1})
        self.assertTrue(report["has_explicit_three_plus_face_edge"])
        self.assertTrue(report["complete_screen"])
        self.assertEqual(report["admission_decision"], "NOT_DETERMINED")

    def test_two_faces_per_edge(self):
        report = step.screen(example(2))
        self.assertEqual(report["edge_to_distinct_face_incidence_histogram"], {2: 1})
        self.assertFalse(report["has_explicit_three_plus_face_edge"])

    def test_identical_geometry_distinct_topology(self):
        report = step.screen(example(3, distinct_edges=True))
        self.assertEqual(report["edge_to_distinct_face_incidence_histogram"], {1: 3})
        self.assertFalse(report["has_explicit_three_plus_face_edge"])

    def test_vertex_loop_not_fabricated_as_shared_edge(self):
        text = example(1).replace("#20=EDGE_LOOP('',(#10));", "#20=VERTEX_LOOP('',#100);")
        report = step.screen(text)
        self.assertFalse(report["complete_screen"])
        self.assertEqual(report["unresolved_face_bound_count"], 1)

    def test_duplicate_identifier_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            step.screen(example(1) + "\n#1=EDGE_CURVE('',#100,#101,#102,.T.);")

    def test_non_step_rejected(self):
        with self.assertRaises(ValueError):
            step.screen("not a STEP file")


if __name__ == "__main__":
    unittest.main()
