"""Protect research CI source-path admission from silent regression."""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/mesh-studio-validation.yml"


class StudioCiScopePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = WORKFLOW.read_text(encoding="utf-8")

    def test_original_scientific_source_and_model_changes_trigger_pipeline(self):
        required_paths = (
            "src/**", "include/**", "research/quad/**",
            "research/mesh_studio/**", "tests/quad/**", "configs/**",
            "input_models/**", "reference/**", "MANIFEST.sha256",
            "CMakeLists.txt", "CMakePresets.json",
            "docs/mesh-studio/*PREREGISTERED*.md",
            ".github/workflows/mesh-studio-validation.yml",
        )
        for source_path in required_paths:
            with self.subTest(source_path=source_path):
                self.assertIn(f"      - '{source_path}'", self.source)

    def test_only_explicit_readmes_bypass_source_replay(self):
        exclusions = [
            line.strip() for line in self.source.splitlines()
            if line.strip().startswith("- '!")
        ]
        self.assertEqual(exclusions, [
            "- '!tools/mesh_studio/README.md'",
            "- '!tools/mesh_studio/web/README.md'",
            "- '!tools/mesh_studio/fixtures/README.md'",
        ])

    def test_real_browser_scientific_provenance_depends_on_native_run(self):
        self.assertIn("  browser-spike:", self.source)
        self.assertIn("    needs: native-lineage-optin", self.source)
        self.assertIn("  native-lineage-optin:", self.source)
        self.assertIn("mesh-studio-r2720-native-accepted-scene-", self.source)

    def test_original_native_audits_and_wrapper_are_not_casually_removed(self):
        for anchor in (
            "quad_generator_outcome_probe",
            "native_lineage_parity",
            "quad_generator_selected_curve_seam_probe",
            "native_selected_curve_seam",
            "native_selected_tri_return",
        ):
            with self.subTest(anchor=anchor):
                self.assertIn(anchor, self.source)


if __name__ == "__main__":
    unittest.main()
