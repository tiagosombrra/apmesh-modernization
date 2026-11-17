"""R2.7.13 offline mutation tests; no synthetic result is native scientific evidence."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest

from tools.mesh_studio.native_lineage_parity import (
    NativeLineageParityError,
    compare_exact_scientific_inventories,
    original_outcome_marker,
    output_inventory,
    prepare_original_config,
)

ROOT = Path(__file__).resolve().parents[2]
MARKER = (
    "real_generator_outcomes=1 accepted_tri=1 restored_tri=3"
    " budget_evaluations=3 growth_evaluations=1"
    " uv_captures=10 local_selected=10 global_epochs=4 truncated=0"
)


def sample() -> dict:
    return {
        "mesh.obj": {"class": ".obj", "bytes": 10, "sha256": "a" * 64},
        "mesh_n.process_0_metrics_rank_-1.csv": {
            "class": ".csv", "bytes": 20, "sha256": "b" * 64,
        },
        "mesh_passo_1_incidences.json": {
            "class": ".json", "bytes": 30, "sha256": "c" * 64,
        },
        "mesh_passo_1_malha_1.pos": {
            "class": ".pos", "bytes": 40, "sha256": "d" * 64,
        },
    }


class NativeLineageNumericalParityUnitTests(unittest.TestCase):
    def test_exact_scientific_output_parity_contract(self) -> None:
        original = sample()
        report = compare_exact_scientific_inventories(original, deepcopy(original))
        self.assertTrue(report["scientific_files_exactly_byte_equal"])
        self.assertEqual(report["compared_file_count"], 4)
        self.assertEqual(report["classes"][".obj"], 1)

    def test_changed_native_obj_bytes_rejected(self) -> None:
        on = sample()
        on["mesh.obj"]["sha256"] = "e" * 64
        with self.assertRaisesRegex(
            NativeLineageParityError, "scientific_bytes_diverged_mesh.obj"
        ):
            compare_exact_scientific_inventories(sample(), on)

    def test_changed_native_scientific_metric_bytes_rejected(self) -> None:
        on = sample()
        on["mesh_n.process_0_metrics_rank_-1.csv"]["bytes"] += 1
        with self.assertRaisesRegex(
            NativeLineageParityError, "scientific_bytes_diverged"
        ):
            compare_exact_scientific_inventories(sample(), on)

    def test_missing_incidence_file_rejected(self) -> None:
        on = sample()
        del on["mesh_passo_1_incidences.json"]
        with self.assertRaisesRegex(
            NativeLineageParityError, "off_on_scientific_file_set_differs"
        ):
            compare_exact_scientific_inventories(sample(), on)

    def test_no_native_geometry_or_metrics_rejected(self) -> None:
        on = {"one.csv": sample()["mesh_n.process_0_metrics_rank_-1.csv"],
              "one.json": sample()["mesh_passo_1_incidences.json"]}
        with self.assertRaisesRegex(
            NativeLineageParityError,
            "mandatory_source_geometry_or_metric_file_missing_.obj",
        ):
            compare_exact_scientific_inventories(on, deepcopy(on))

    def test_real_native_outcome_marker_with_all_counts(self) -> None:
        actual, accepted, restored = original_outcome_marker(
            "context\n" + MARKER + "\n")
        self.assertEqual(actual, MARKER)
        self.assertEqual((accepted, restored), (1, 3))

    def test_rejected_event_count_or_truncated_stream_rejected(self) -> None:
        for marker in (
            MARKER.replace("restored_tri=3", "restored_tri=0"),
            MARKER.replace("truncated=0", "truncated=1"),
            "real_generator_outcomes=1 accepted_tri=0 restored_tri=3",
        ):
            with self.subTest(marker=marker):
                with self.assertRaisesRegex(
                    NativeLineageParityError,
                    "native_global_outcome_schema_mismatch|original_global_outcome_incomplete",
                ):
                    original_outcome_marker(marker)

    def test_duplicated_global_outcome_marker_rejected(self) -> None:
        with self.assertRaisesRegex(
            NativeLineageParityError, "missing_or_duplicate_native_global_outcome"
        ):
            original_outcome_marker(MARKER + "\n" + MARKER)

    def test_output_inventory_distinguishes_scientific_vs_diagnostics(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "mesh.obj").write_text("v 0 0 0\n", encoding="utf-8")
            (workspace / "debug.log").write_text("timing 100ms\n", encoding="utf-8")
            (workspace / "original_article.conf").write_text(
                "ignored\n", encoding="utf-8")
            (workspace / "lineage").mkdir()
            (workspace / "lineage" / "accepted.ndjson").write_text(
                "{}\n", encoding="utf-8")
            files, excluded = output_inventory(workspace)
            self.assertEqual(list(files), ["mesh.obj"])
            self.assertEqual(excluded, ["debug.log"])

    def test_original_article_config_changes_only_input_output_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            _, original_input, conf = prepare_original_config(
                ROOT, "eistute", Path(tmp))
            text = conf.read_text(encoding="utf-8")
            self.assertEqual(len(re.findall(r"^INPUT_MODEL=", text, re.M)), 1)
            self.assertEqual(len(re.findall(r"^OUTPUT_PREFIX=", text, re.M)), 1)
            self.assertIn("INPUT_MODEL=" + original_input.as_posix(), text)
            self.assertIn("ADAPTIVE_MODE=adaptive_stable", text)


if __name__ == "__main__":
    unittest.main()
