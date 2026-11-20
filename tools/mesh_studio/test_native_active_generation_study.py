"""Synthetic fail-closed R2.7.26 contracts; never original C++ evidence."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from tools.mesh_studio.native_active_generation_study import (
    PREREGISTRATION_BLOB, TRIALS, attest_predeclared_source,
)
from tools.mesh_studio.native_controlled_sensitivity import (
    Treatment, git_blob, make_single_factor_config,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError

ROOT = Path(__file__).resolve().parents[2]


class PreregisteredActiveGenerationContracts(unittest.TestCase):
    def test_original_preregistration_and_native_source_pinned(self):
        evidence = attest_predeclared_source(ROOT)
        self.assertEqual(
            evidence["docs/mesh-studio/R2_7_26_PREREGISTERED_ACTIVE_GENERATION_CONTROLS_20261118.md"]["git_blob"],
            PREREGISTRATION_BLOB)

    def test_eistute_is_one_existing_config_line_only(self):
        raw = (ROOT / "configs/eistute/article.conf").read_bytes()
        changed = make_single_factor_config(raw, TRIALS[0])
        self.assertEqual(
            [x for x in changed.splitlines() if x not in raw.splitlines()],
            [b"CURVE_POINT_MIN=13"])
        self.assertEqual(changed.replace(b"CURVE_POINT_MIN=13",
                                         b"CURVE_POINT_MIN=11"), raw)

    def test_book_inserts_one_absent_default_setting_not_a_replacement(self):
        raw = (ROOT / "configs/book/article.conf").read_bytes()
        self.assertNotIn(b"AFT_LOCAL_POSTPROCESS_PASSES=", raw)
        changed = make_single_factor_config(raw, TRIALS[1])
        self.assertEqual(changed.count(b"AFT_LOCAL_POSTPROCESS_PASSES=1\n"), 1)
        self.assertEqual(
            changed.replace(b"AFT_LOCAL_POSTPROCESS_PASSES=1\n", b""), raw)
        self.assertEqual(len(changed.splitlines()),
                         len(raw.splitlines()) + 1)

    def test_unknown_book_addition_is_not_allowed(self):
        original = (ROOT / "configs/book/article.conf").read_bytes()
        forged = replace(TRIALS[1], parameter="ADAPTIVE_TARGET_GROWTH")
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2726_unqualified_omitted_default_parameter"):
            make_single_factor_config(original, forged)

    def test_default_value_mismatch_is_not_allowed(self):
        original = (ROOT / "configs/book/article.conf").read_bytes()
        forged = replace(TRIALS[1], original="5")
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2726_unqualified_omitted_default_parameter"):
            make_single_factor_config(original, forged)

    def test_wrong_insert_anchor_cannot_change_experiment(self):
        original = (ROOT / "configs/book/article.conf").read_bytes()
        forged = replace(TRIALS[1], insert_after="NUM_PROCESSES=1")
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2726_unqualified_omitted_default_parameter"):
            make_single_factor_config(original, forged)

    def test_original_book_blob_changed_cannot_be_exploratory_input(self):
        raw = (ROOT / "configs/book/article.conf").read_bytes()
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2724_original_article_config_blob_modified"):
            make_single_factor_config(raw + b"# extra\n", TRIALS[1])

    def test_cannot_invent_one_added_key_for_eistute(self):
        raw = (ROOT / "configs/eistute/article.conf").read_bytes()
        forged = Treatment(
            "fabricated", "eistute", "AFT_LOCAL_POSTPROCESS_PASSES",
            "0", "1", "not preregistered", insert_after="CURVE_POINT_MIN=11")
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2726_unqualified_omitted_default_parameter"):
            make_single_factor_config(raw, forged)

    def test_omitted_aft_default_is_proven_in_original_parser(self):
        parser = (ROOT / "src/application/runtime_config.cpp").read_text()
        self.assertIn(
            'GetConfigValue(values, "AFT_LOCAL_POSTPROCESS_PASSES", "0")',
            parser)
        aft = (ROOT / "src/crab_mesh/aft/advancing_front.cpp").read_text()
        self.assertIn(
            "for (int pass = 0; pass < PostprocessPasses(); ++pass)", aft)

    def test_protocol_remains_prior_to_runner(self):
        raw = (ROOT / "docs/mesh-studio/R2_7_26_PREREGISTERED_ACTIVE_GENERATION_CONTROLS_20261118.md").read_bytes()
        self.assertEqual(git_blob(raw), PREREGISTRATION_BLOB)


if __name__ == "__main__":
    unittest.main()
