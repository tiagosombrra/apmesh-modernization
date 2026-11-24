"""Protect research CI source-path admission from silent regression."""

from __future__ import annotations

import json
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
            "- '!tools/mesh_studio/web/src/style.css'",
        ])

    def test_real_browser_scientific_provenance_depends_on_native_run(self):
        self.assertIn("  browser-spike:", self.source)
        self.assertIn("    needs: native-lineage-optin", self.source)
        self.assertIn("  native-lineage-optin:", self.source)
        self.assertIn("mesh-studio-r2720-native-accepted-scene-", self.source)

    def test_new_push_drops_stale_automatic_run_but_preserves_manual_capture(self):
        # Only superseded automatic pushes may be cancelled.
        self.assertIn(
            "group: ${{ github.event_name == 'workflow_dispatch' && format('mesh-studio-manual-{0}', github.ref) || format('mesh-studio-{0}', github.ref) }}",
            self.source)
        self.assertIn(
            "cancel-in-progress: ${{ github.event_name == 'push' }}",
            self.source)
        self.assertIn("  workflow_dispatch:", self.source)
        self.assertIn("  native-lineage-optin:", self.source)

    def test_active_review_branch_and_evidence_sources_are_covered(self):
        registry = json.loads((ROOT / "docs/mesh-studio/EVIDENCE_REGISTRY.json")
                              .read_text(encoding="utf-8"))
        branch = registry["current_review_branch"]
        for name in ("mesh-studio-validation.yml", "mesh-studio-fast-web.yml",
                     "mesh-studio-v511-built-reviewer.yml",
                     "mesh-studio-v511-installed-license-audit.yml",
                     "mesh-studio-v511-notice-candidate.yml"):
            with self.subTest(workflow=name):
                source = (ROOT / ".github/workflows" / name).read_text(
                    encoding="utf-8")
                self.assertIn(f"      - {branch}", source)
        reviewer = (ROOT / ".github/workflows/mesh-studio-v511-built-reviewer.yml"
                    ).read_text(encoding="utf-8")
        notice = (ROOT / ".github/workflows/mesh-studio-v511-notice-candidate.yml"
                  ).read_text(encoding="utf-8")
        mirror = registry["original_native"]["mirror"]
        self.assertIn(str(mirror["run"]), reviewer)
        self.assertIn(mirror["commit"], reviewer)
        self.assertIn(str(registry["license_sources"]["run"]), notice)
        self.assertIn(registry["license_sources"]["commit"], notice)
        self.assertFalse(registry["open_gates"]["r28_qualified"])
        self.assertFalse(registry["notice_candidate"]["spark_md5_license_elected"])

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
