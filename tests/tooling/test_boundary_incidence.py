"""Analytic non-manifold/reversal fixtures and deliberate boundary corruption."""

import copy
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from check_boundary_incidence import SIDES, inspect_snapshot
from verify_generation import inspect_mesh, verify_run, compare_runs


def analytic_fixture(sheet_count=3, reverse_last=True, extra_partition=False, shifted_partition=False):
    """Construct planar fans with a known shared axis, independent of the mesher."""
    vectors = [(1, 0), (-1, 1), (0, -1)]
    thirds = [0.0, 1 / 3, 2 / 3, 1.0]
    document = {"schema": "apmesh-incidence-v1", "step": 0, "patches": []}
    for index, (dx, dy) in enumerate(vectors[:sheet_count]):
        reversed_side = reverse_last and index == sheet_count - 1
        heights = thirds[::-1] if reversed_side else thirds
        controls = [[dx * u, dy * u, v] for v in heights for u in thirds]

        def physical(u, v):
            return [dx * u, dy * u, 1 - v if reversed_side else v]

        boundary = [(0, 0), (0.5, 0), (1, 0), (1, 0.5), (1, 1), (0.5, 1), (0, 1), (0, 0.5)]
        if index == sheet_count - 1 and extra_partition:
            boundary = boundary[:-1] + [(0, 0.75), (0, 0.5), (0, 0.25)]
        if index == sheet_count - 1 and shifted_partition:
            boundary[-1] = (0, 0.4)
        coordinates = boundary + [(0.5, 0.5)]
        ids = [index * 100 + i for i in range(len(coordinates))]
        nodes = [[node, *physical(*uv)] for node, uv in zip(ids, coordinates)]
        faces = []
        for i in range(len(boundary)):
            corners = (i, (i + 1) % len(boundary), len(boundary))
            faces.append([i] + [[ids[j], *coordinates[j], *physical(*coordinates[j])] for j in corners])
        document["patches"].append({"index": index, "control_points": controls, "curves": [],
                                    "nodes": nodes, "faces": faces})
    groups = {}
    for patch in document["patches"]:
        for side in SIDES:
            controls = tuple(tuple(patch["control_points"][i]) for i in side)
            key = min(controls, controls[::-1])
            groups.setdefault(key, len(groups))
            patch["curves"].append(groups[key])
    return document


def write_obj(path, document):
    indices, lines = {}, []
    for patch in document["patches"]:
        for node, *position in patch["nodes"]:
            if node not in indices:
                indices[node] = len(indices) + 1
                lines.append("v " + " ".join(format(x, ".6g") for x in position))
    for patch in document["patches"]:
        for face in patch["faces"]:
            lines.append("f " + " ".join(str(indices[corner[0]]) for corner in face[1:]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class BoundaryIncidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.root = Path(self.temp.name)
        self.document = analytic_fixture()
        self.model = self.root / "control.bp"
        self.write_model()
        self.snapshot = self.root / "control_passo_0_incidences.json"
        self.obj = self.root / "control_passo_0_malha_0.obj"

    def write_model(self):
        lines = []
        for index, patch in enumerate(self.document["patches"]):
            lines.extend("v " + " ".join(format(x, ".17g") for x in p) for p in patch["control_points"])
            lines.append("p " + " ".join(str(index * 16 + j) for j in range(16)))
        self.model.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def inspect(self):
        self.snapshot.write_text(json.dumps(self.document), encoding="utf-8")
        write_obj(self.obj, self.document)
        return inspect_snapshot(self.snapshot, self.model, self.obj, 0)

    def test_nonmanifold_reversal_is_checked_per_incidence(self):
        result = self.inspect()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["incidences"], 12)
        self.assertEqual(result["shared_incidences"], 3)
        self.assertEqual(result["compared_incidences"], 2)
        self.assertEqual(result["max_curve_incidence"], 3)
        self.assertEqual(result["nonmanifold_groups"], 1)
        self.assertEqual(result["mixed_orientation_groups"], 1)

    def test_missing_patch_fails(self):
        self.document["patches"].pop()
        with self.assertRaises(ValueError):
            self.inspect()

    def test_manifold_reversal_passes(self):
        self.document = analytic_fixture(sheet_count=2)
        self.write_model()
        result = self.inspect()
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["max_curve_incidence"], 2)
        self.assertEqual(result["nonmanifold_groups"], 0)
        self.assertEqual(result["mixed_orientation_groups"], 1)

    def test_reversed_reference_incidence_passes(self):
        patches = self.document["patches"]
        self.document["patches"] = patches[-1:] + patches[:-1]
        for index, patch in enumerate(self.document["patches"]):
            patch["index"] = index
        self.write_model()
        self.assertEqual(self.inspect()["status"], "passed")

    def test_missing_curve_fails(self):
        self.document["patches"][1]["curves"].pop()
        with self.assertRaises(ValueError):
            self.inspect()

    def test_missing_triangle_exposes_hole(self):
        self.document["patches"][1]["faces"].pop()
        with self.assertRaises(ValueError):
            self.inspect()

    def test_wrong_stage_fails(self):
        self.document["step"] = 1
        with self.assertRaises(ValueError):
            self.inspect()

    def test_unrelated_obj_fails(self):
        self.inspect()
        self.obj.write_text(self.obj.read_text().replace("v 1 0 0", "v 2 0 0"))
        with self.assertRaises(ValueError):
            inspect_snapshot(self.snapshot, self.model, self.obj, 0)

    def test_changed_exported_controls_fail(self):
        self.document["patches"][0]["control_points"][5][0] += 0.01
        self.assertIn("source_control_mismatch", self.inspect()["issues"])

    def test_valid_but_different_partitions_fail(self):
        self.document = analytic_fixture(extra_partition=True)
        self.assertIn("shared_partition_count_mismatch", self.inspect()["issues"])

    def test_equal_counts_but_different_parameters_fail(self):
        self.document = analytic_fixture(shifted_partition=True)
        self.assertIn("shared_parameter_mismatch", self.inspect()["issues"])

    def test_physical_gap_fails_even_with_consistent_obj(self):
        patch = self.document["patches"][2]
        node = patch["nodes"][7][0]
        patch["nodes"][7][1] += 1e-6
        for face in patch["faces"]:
            for corner in face[1:]:
                if corner[0] == node:
                    corner[3] += 1e-6
        result = self.inspect()
        self.assertIn("off_source_boundary", result["issues"])
        self.assertIn("shared_position_mismatch", result["issues"])

    def test_split_runtime_identity_fails(self):
        self.document["patches"][1]["curves"][3] = 1000
        self.assertIn("runtime_shared_curve_split", self.inspect()["issues"])

    def test_merged_unrelated_runtime_curves_fail(self):
        self.document["patches"][0]["curves"][0] = self.document["patches"][0]["curves"][3]
        self.assertIn("runtime_curve_merges_different_source_boundaries", self.inspect()["issues"])

    def test_nonfinite_uv_fails(self):
        self.document["patches"][0]["faces"][0][1][1] = float("nan")
        with self.assertRaises(ValueError):
            self.inspect()

    def test_outside_uv_fails(self):
        self.document["patches"][0]["faces"][0][1][1] = -0.01
        with self.assertRaises(ValueError):
            self.inspect()

    def test_duplicate_json_fields_fail(self):
        self.inspect()
        self.snapshot.write_text(self.snapshot.read_text().replace('"step": 0', '"step": 0,"step": 1'))
        with self.assertRaises(ValueError):
            inspect_snapshot(self.snapshot, self.model, self.obj, 0)

    def prepare_run(self):
        self.inspect()
        stats = inspect_mesh(self.obj)
        (self.root / "process.json").write_text(json.dumps({
            "model": "control", "status": "completed", "exit_code": 0,
            "input_model": str(self.model),
            "input_model_sha256": hashlib.sha256(self.model.read_bytes()).hexdigest()}))
        (self.root / "control_passo_0_acceptance_accepted.log").write_text(
            "step=0\naccepted=1\n" + "".join(f"{key}={stats[key]}\n" for key in ["quality_min_3d", "quality_mean_3d"]))
        # Planar fan triangles are right isosceles except on the stretched sheet:
        # its eight right triangles have q=2*(sqrt(2)+1-sqrt(3))/sqrt(3)<0.8.
        excellent = stats["triangles"] - (8 if len(self.document["patches"]) > 1 else 0)
        right_quality = 2 * (math.sqrt(2) - 1)
        stretched_quality = 2 * (math.sqrt(2) + 1 - math.sqrt(3)) / math.sqrt(3)
        minimum = stretched_quality if len(self.document["patches"]) > 1 else right_quality
        mean = (excellent * right_quality + (stats["triangles"] - excellent) * stretched_quality) / stats["triangles"]
        row = {"step": 0, "nodes": sum(len(p["nodes"]) for p in self.document["patches"]),
               "elements": stats["triangles"], "stop_reason": "control",
               "quality_min": format(minimum, ".6g"),
               "quality_mean": format(mean, ".6g"),
               "poor_ratio_lt_0_30": 0, "q_ge_0_60": 100,
               "excellent_ratio_ge_0_80": format(100 * excellent / stats["triangles"], ".6g")}
        # Every UV fan triangle is right isosceles, regardless of XYZ stretching.
        row.update({"quality_uv_" + field: format(right_quality, ".6g")
                    for field in ("min", "p05", "p50", "p95", "max", "mean")})
        row.update(quality_uv_std=0, quality_uv_poor_ratio_lt_0_30=0,
                   quality_uv_q_ge_0_60=100, quality_uv_excellent_ratio_ge_0_80=100)
        with (self.root / "control_metrics.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)
        (self.root / "control_compatibility_summary.csv").write_text(
            "compared_groups,desynchronized_groups,compat_error_mean,compat_error_max\n0,0,0,0\n")

    def test_strict_integration_uses_real_incidence_evidence(self):
        self.prepare_run()
        report = verify_run(self.root, require_boundary=True)
        self.assertEqual(report["boundary_incidence_coverage"], "verified")
        self.assertEqual(report["physical_quality_coverage"], "full_precision_snapshot")
        self.assertEqual(report["physical_quality"][0]["csv_fields_compared"], 5)
        self.assertEqual(report["parametric_quality_coverage"], "full_precision_snapshot")
        self.assertEqual(report["parametric_quality"][0]["csv_fields_compared"], 10)

    def test_wrong_uv_csv_fails_even_with_correct_physical_quality(self):
        self.prepare_run()
        path = self.root / "control_metrics.csv"
        with path.open(newline="") as stream:
            row, = csv.DictReader(stream)
        row["quality_uv_p50"] = "1"
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)
        with self.assertRaisesRegex(ValueError, "quality_uv_p50"):
            verify_run(self.root, require_boundary=True)

    def test_wrong_quality_csv_fails_even_with_correct_geometry_and_logs(self):
        self.prepare_run()
        path = self.root / "control_metrics.csv"
        with path.open(newline="") as stream:
            row, = csv.DictReader(stream)
        row["poor_ratio_lt_0_30"] = "100"
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(row))
            writer.writeheader()
            writer.writerow(row)
        with self.assertRaisesRegex(ValueError, "poor_ratio_lt_0_30"):
            verify_run(self.root, require_boundary=True)

    def test_changed_input_model_identity_fails(self):
        self.prepare_run()
        self.model.write_text(self.model.read_text() + "# changed\n")
        with self.assertRaises(ValueError):
            verify_run(self.root, require_boundary=True)

    def test_snapshot_for_unattempted_state_fails(self):
        self.prepare_run()
        self.snapshot.with_name("control_passo_1_incidences.json").write_bytes(self.snapshot.read_bytes())
        with self.assertRaises(ValueError):
            verify_run(self.root)

    def test_missing_snapshot_for_one_attempt_fails(self):
        self.prepare_run()
        self.obj.with_name("control_passo_1_malha_1.obj").write_bytes(self.obj.read_bytes())
        first_log = self.root / "control_passo_0_acceptance_accepted.log"
        (self.root / "control_passo_1_acceptance_rejected.log").write_text(
            first_log.read_text().replace("step=0", "step=1").replace("accepted=1", "accepted=0"))
        metrics = self.root / "control_metrics.csv"
        metrics.write_text(metrics.read_text() + metrics.read_text().splitlines()[1].replace("0,", "1,", 1) + "\n")
        with self.assertRaises(ValueError):
            verify_run(self.root)

    def test_zero_shared_comparisons_never_pass_strict_gate(self):
        self.document = analytic_fixture(sheet_count=1, reverse_last=False)
        self.write_model()
        self.prepare_run()
        self.assertEqual(verify_run(self.root)["boundary_incidence_coverage"], "no_shared_boundary_comparisons")
        with self.assertRaises(ValueError):
            verify_run(self.root, require_boundary=True)

    def test_default_validation_does_not_ignore_bad_snapshot(self):
        self.prepare_run()
        self.document["patches"][1]["curves"][3] = 1000
        self.inspect()
        with self.assertRaises(ValueError):
            verify_run(self.root)

    def test_strict_repetition_compares_snapshot_bytes(self):
        self.prepare_run()
        first = verify_run(self.root)
        second = copy.deepcopy(first)
        second["boundary_incidences"][0]["snapshot_sha256"] = "changed"
        with self.assertRaises(ValueError):
            compare_runs(first, second)


if __name__ == "__main__":
    unittest.main()
