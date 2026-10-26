"""Independent controls for acceptance, geometry, coverage and regression checks."""

import csv
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from verify_generation import compare_runs, inspect_mesh, require_accepted_artifact, verify_run


class GenerationVerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.root = Path(self.temp.name)
        (self.root / "process.json").write_text(json.dumps({"model": "control", "status": "completed", "exit_code": 0}))
        self.quality = 2 * (math.sqrt(2) - 1)
        for step, state in [(0, "accepted"), (1, "rejected")]:
            (self.root / f"control_passo_{step}_malha_{step}.obj").write_text("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n")
            (self.root / f"control_passo_{step}_acceptance_{state}.log").write_text(
                f"step={step}\naccepted={int(state == 'accepted')}\nquality_min_3d={self.quality}\nquality_mean_3d={self.quality}\n")
        with (self.root / "control_metrics.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["step", "nodes", "elements", "stop_reason"])
            writer.writeheader()
            for step in [0, 1]:
                writer.writerow({"step": step, "nodes": 3, "elements": 1, "stop_reason": "control"})

    def tearDown(self):
        self.temp.cleanup()

    def test_last_accepted_state_is_selected(self):
        result = verify_run(self.root)
        self.assertEqual(result["last_accepted_step"], 0)
        self.assertEqual(result["rejected_steps"], [1])
        self.assertEqual(result["boundary_compatibility"], "unmeasured")
        self.assertEqual(result["physical_quality_coverage"], "unavailable_without_snapshot")

    def test_rejected_target_is_not_a_valid_accepted_artifact(self):
        with self.assertRaises(ValueError):
            require_accepted_artifact(self.root / "control_passo_1_malha_1.obj")
        with self.assertRaises(ValueError):
            verify_run(self.root, required_step=1)

    def test_missing_log_fails(self):
        (self.root / "control_passo_0_acceptance_accepted.log").unlink()
        with self.assertRaises(ValueError):
            verify_run(self.root)

    def test_contradictory_filename_and_state_fails(self):
        path = self.root / "control_passo_1_acceptance_rejected.log"
        path.write_text(path.read_text().replace("accepted=0", "accepted=1"))
        with self.assertRaises(ValueError):
            verify_run(self.root)

    def test_failed_process_fails(self):
        (self.root / "process.json").write_text('{"model":"control","status":"timeout","exit_code":null}')
        with self.assertRaises(ValueError):
            verify_run(self.root)

    def test_missing_metrics_fails(self):
        (self.root / "control_metrics.csv").unlink()
        with self.assertRaises(ValueError):
            verify_run(self.root)

    def test_duplicate_metrics_header_fails(self):
        path = self.root / "control_metrics.csv"
        text = path.read_text().replace("stop_reason", "elements", 1)
        path.write_text(text)
        with self.assertRaisesRegex(ValueError, "duplicate metrics header"):
            verify_run(self.root)

    def test_wrong_mesh_count_fails(self):
        path = self.root / "control_metrics.csv"
        path.write_text(path.read_text().replace(",3,1,", ",3,2,"))
        with self.assertRaises(ValueError):
            verify_run(self.root)

    def test_quality_is_recomputed(self):
        path = self.root / "control_passo_0_acceptance_accepted.log"
        path.write_text(path.read_text().replace(str(self.quality), "1.0"))
        with self.assertRaises(ValueError):
            verify_run(self.root)

    def test_nan_vertices_fail(self):
        path = self.root / "bad.obj"
        path.write_text("v nan 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n")
        with self.assertRaises(ValueError):
            inspect_mesh(path)

    def test_out_of_bounds_indices_fail(self):
        path = self.root / "bad.obj"
        path.write_text("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 4\n")
        with self.assertRaises(ValueError):
            inspect_mesh(path)

    def test_degenerate_triangle_fails(self):
        path = self.root / "bad.obj"
        path.write_text("v 0 0 0\nv 1 0 0\nv 2 0 0\nf 1 2 3\n")
        with self.assertRaises(ValueError):
            inspect_mesh(path)

    def test_duplicate_faces_fail(self):
        path = self.root / "bad.obj"
        path.write_text("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\nf 3 2 1\n")
        with self.assertRaises(ValueError):
            inspect_mesh(path)

    def test_equilateral_analytic_quality(self):
        path = self.root / "equilateral.obj"
        path.write_text(f"v 0 0 0\nv 1 0 0\nv 0.5 {math.sqrt(3)/2} 0\nf 1 2 3\n")
        self.assertAlmostEqual(inspect_mesh(path)["quality_min_3d"], 1)

    def test_no_boundary_coverage_is_not_positive_evidence(self):
        with self.assertRaises(ValueError):
            verify_run(self.root, require_boundary=True)

    def test_legacy_groups_do_not_prove_incidence_coverage(self):
        (self.root / "control_compatibility_summary.csv").write_text(
            "compared_groups,desynchronized_groups,compat_error_mean,compat_error_max\n2,0,0,0\n")
        with self.assertRaises(ValueError):
            verify_run(self.root, require_boundary=True)

    def test_identical_run_comparison_passes(self):
        result = verify_run(self.root)
        self.assertTrue(compare_runs(result, result)["all_obj_byte_identical"])

    def test_valid_but_changed_geometry_is_a_regression(self):
        before = verify_run(self.root)
        path = self.root / "control_passo_0_malha_0.obj"
        path.write_text(path.read_text().replace("v 1 0 0", "v 2 0 0").replace("v 0 1 0", "v 0 2 0"))
        after = verify_run(self.root)
        with self.assertRaises(ValueError):
            compare_runs(before, after)

    def test_numeric_report_drift_is_not_silenced(self):
        before = verify_run(self.root)
        path = self.root / "control_passo_0_acceptance_accepted.log"
        path.write_text(path.read_text() + "error_improvement=0.1\n")
        with self.assertRaises(ValueError):
            compare_runs(before, verify_run(self.root))

    def test_csv_node_incidences_are_not_unique_obj_vertices(self):
        path = self.root / "control_metrics.csv"
        path.write_text(path.read_text().replace(",3,1,", ",4,1,"))
        self.assertEqual(verify_run(self.root)["meshes"][0]["csv_node_incidences"], 4)

    def test_insufficient_node_incidences_fail(self):
        path = self.root / "control_metrics.csv"
        path.write_text(path.read_text().replace(",3,1,", ",2,1,"))
        with self.assertRaises(ValueError):
            verify_run(self.root)


if __name__ == "__main__":
    unittest.main()
