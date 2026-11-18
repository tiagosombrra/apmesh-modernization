"""R2.7.24 synthetic adversarial contracts; not generator experimental results."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.mesh_studio.native_acceptance_gate_forensics import (
    parse_original_gate_stderr,
)
from tools.mesh_studio.native_controlled_sensitivity import (
    TREATMENTS, Treatment, certify_same_run_outcomes, git_blob,
    make_single_factor_config, resolve_isolated_config,
)
from tools.mesh_studio.native_sensitivity_audit import (
    audit_preregistered_treatments,
)
from tools.mesh_studio.test_native_acceptance_gate_forensics import row
from tools.mesh_studio.test_verify_native_lineage import synthetic_receipt
from tools.mesh_studio.verify_native_lineage import (
    NativeLineageValidationError, decode_ndjson,
    validate_lineage_records,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fake_cases() -> tuple[list[dict], list[dict]]:
    entries = [row(1, True), row(2, False)]
    return entries, [{"accepted_step": 1, "retry_index": 0}]


def synthetic_artifact_tree(parent: Path):
    """Produce fake evidence files only to challenge the independent auditor."""
    original_root = parent / "fake-source-root"
    original_dir = parent / "fake-native-article-controls"
    output = parent / "fake-preregistered-treatments"
    original_dir.mkdir()
    output.mkdir()
    fake_exe = parent / "fake-not-a-compiled-generator.bin"
    fake_exe.write_bytes(b"ONLY A SYNTHETIC UNIT TEST, NOT C++")
    for variant in TREATMENTS:
        original = (PROJECT_ROOT / "configs" / variant.model /
                    "article.conf").read_bytes()
        article = original_root / "configs" / variant.model / "article.conf"
        article.parent.mkdir(parents=True, exist_ok=True)
        article.write_bytes(original)
        source_selector = next(
            x.split("=", 1)[1] for x in original.decode().splitlines()
            if x.startswith("INPUT_MODEL="))
        model = original_root / source_selector
        model.parent.mkdir(parents=True, exist_ok=True)
        model.write_bytes(("FAKE MODEL " + variant.model).encode())
        baseline = {
            "original_model": variant.model,
            "native_config_source_sha256": sha(original),
            "real_model_input_sha256": sha(model.read_bytes()),
            "research_executable_sha256": sha(fake_exe.read_bytes()),
            "native_accepted_commits": 1,
            "accepted_snapshots": [{"accepted_step": 1}],
            "second_accepted_epoch_observed": False,
        }
        (original_dir / f"r2712-{variant.model}-native-lineage-audit.json").write_text(
            json.dumps(baseline), encoding="utf-8")
        directory = output / variant.id
        directory.mkdir()
        intent = make_single_factor_config(original, variant)
        (directory / "single-factor-intent.conf").write_bytes(intent)
        resolved = resolve_isolated_config(
            intent.decode(), model.resolve(),
            (parent / "temporary-output" / variant.id).resolve())
        (directory / "resolved-execution.conf").write_text(
            resolved, encoding="utf-8", newline="\n")
        stdout = b"real_generator_outcomes=1 accepted_tri=1 restored_tri=1\n"
        gate_list = [row(1, True), row(2, False)]
        stderr = b"original C++ fake test only\n" + b"".join(
            b"R2723_NATIVE_ACCEPTANCE_GATE=" +
            json.dumps(gate, sort_keys=True).encode() + b"\n"
            for gate in gate_list)
        (directory / "original-generator-stdout.log").write_bytes(stdout)
        (directory / "original-generator-stderr.log").write_bytes(stderr)
        native_rows = synthetic_receipt(variant.model)
        native_bytes = (b"\n".join(
            json.dumps(item, separators=(",", ":")).encode()
            for item in native_rows) + b"\n")
        verified = validate_lineage_records(
            decode_ndjson(native_bytes), variant.model)
        verified["artifact_file"] = "accepted_step_1_retry_0.ndjson"
        verified["sha256"] = sha(native_bytes)
        (directory / verified["artifact_file"]).write_bytes(native_bytes)
        summary = certify_same_run_outcomes(
            parse_original_gate_stderr(stderr), [verified], 1, 1)
        report = {
            "schema": "apmesh.meshstudio.r2724.controlled_single_factor_native_sensitivity.v1",
            "id": variant.id, "source_model": variant.model,
            "treatment_role": "EXPLORATORY_CONFIG_SENSITIVITY_NOT_ARTICLE_REPLICATION",
            "preregistered_exactly_one_parameter": True,
            "parameter": variant.parameter,
            "original_value": variant.original,
            "variant_value": variant.treatment,
            "rationale": variant.rationale,
            "original_article_git_blob": git_blob(original),
            "original_article_sha256": sha(original),
            "single_factor_intent_sha256": sha(intent),
            "resolved_run_config_sha256": sha(resolved.encode()),
            "native_model_input_sha256": sha(model.read_bytes()),
            "original_compiled_cpp_executable_sha256": sha(fake_exe.read_bytes()),
            "original_stdout_sha256": sha(stdout),
            "original_stderr_sha256": sha(stderr),
            "original_stderr_contains_precommit_native_gates": True,
            "original_stderr_contains_actual_adapter_boundary_events": False,
            "process_returncode": 0,
            "accepted_real_native_face_snapshots": [verified],
            "precommit_original_gate_trace": [{
                "step": x["step"], "retry": x["retry"],
                "predicted_not_yet_committed":
                    x["predicted_branch_accept_not_committed"],
                "error_improvement_fraction": x["error_improvement_fraction"],
                "transition_coherence_ok": x["transition_coherence_ok"],
                "quality_gate_ok": x["quality_gate_ok"],
                "stable_transition_ready": x["stable_transition_ready"],
                "candidate_quality_min": x["candidate_quality_min"],
                "element_growth_factor": x["element_growth_factor"],
                "native_acceptance_mode": x["acceptance_mode"],
            } for x in gate_list],
            **summary,
        }
        (directory / "treatment-report.json").write_text(
            json.dumps(report), encoding="utf-8")
    index = {
        "schema": "apmesh.meshstudio.r2724.separate_cpp_process_treatment_index.v1",
        "scope": "EXPLORATORY_CONFIG_ONLY_UNCHANGED_CPP_ACCEPTANCE_POLICY",
        "source_input_models": ["book", "eistute"],
        "treatment_ids": [v.id for v in TREATMENTS],
        "each_treatment_is_a_distinct_cpp_process_not_a_combined_epoch": True,
        "baseline_native_article_runs_remain_separate_controls": True,
        "all_treatments_have_genuine_two_accepted_same_run_epochs": False,
        "scientific_lod_qualified": False,
    }
    (output / "index.json").write_text(json.dumps(index), encoding="utf-8")
    return original_root, original_dir, output, fake_exe


class NativeSingleFactorContracts(unittest.TestCase):
    def test_preregistered_changes_one_original_parameter_only(self):
        for variant in TREATMENTS:
            with self.subTest(model=variant.model):
                original = (PROJECT_ROOT / "configs" / variant.model /
                            "article.conf").read_bytes()
                changed = make_single_factor_config(original, variant)
                edits = [(a, b) for a, b in zip(original.splitlines(),
                                                changed.splitlines()) if a != b]
                self.assertEqual(edits, [(
                    f"{variant.parameter}={variant.original}".encode(),
                    f"{variant.parameter}={variant.treatment}".encode())])
                self.assertEqual(git_blob(original),
                                 "bd368dbad5b61515106b5d74d28cbde159780cd6"
                                 if variant.model == "eistute" else
                                 "d88116054728311df74a6ece1d38d0cd23a64466")

    def test_invented_nonoriginal_control_value_refused(self):
        original = (PROJECT_ROOT / "configs" / "eistute" /
                    "article.conf").read_bytes()
        forged = Treatment("fake", "eistute", "CURVE_POINT_GROWTH_STEPN",
                           "5.0", "2.0", "fake")
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2724_requested_parameter"):
            make_single_factor_config(original, forged)

    def test_modified_article_source_blob_refused(self):
        original = (PROJECT_ROOT / "configs" / "book" /
                    "article.conf").read_bytes() + b"\n"
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2724_original_article_config_blob_modified"):
            make_single_factor_config(original, TREATMENTS[1])

    def test_precommit_true_not_sidecar_is_never_real_second_epoch(self):
        gates, receipts = fake_cases()
        gates[1] = row(2, True)
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2724_predicted_accept_not_backed"):
            certify_same_run_outcomes(gates, receipts, 1, 1)

    def test_true_two_commits_requires_two_sidecars_in_one_run(self):
        entries = [row(1, True), row(2, True), row(3, False)]
        receipts = [{"accepted_step": 1, "retry_index": 0},
                    {"accepted_step": 2, "retry_index": 0}]
        result = certify_same_run_outcomes(entries, receipts, 2, 1)
        self.assertTrue(result["two_distinct_commits_within_THIS_single_run"])
        self.assertEqual(result["source_accepted_steps"], [1, 2])
        self.assertFalse(result["scientific_lod_qualified"])

    def test_pooled_independent_one_epoch_runs_are_not_two_epochs(self):
        entries, receipts = fake_cases()
        result = certify_same_run_outcomes(entries, receipts, 1, 1)
        self.assertFalse(result["two_distinct_commits_within_THIS_single_run"])
        self.assertFalse(result["cross_epoch_native_face_descendants_qualified"])

    def test_duplicate_original_accepted_receipt_rejected(self):
        entries, receipts = fake_cases()
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2724_duplicate_or_missing"):
            certify_same_run_outcomes(entries, receipts + receipts, 2, 0)

    def test_restored_step_count_cannot_omit_real_rejection(self):
        entries, receipts = fake_cases()
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2724_cpp_restored"):
            certify_same_run_outcomes(entries, receipts, 1, 0)

    def test_precommit_gate_without_explicit_native_outcome_refused(self):
        entries, _ = fake_cases()
        with self.assertRaises(NativeLineageValidationError):
            certify_same_run_outcomes(entries, [], 0, 0)


class IndependentTreatmentArtifactContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="r2724-synthetic-only-")
        self.root, self.original, self.out, self.exe = synthetic_artifact_tree(
            Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def audit(self):
        return audit_preregistered_treatments(
            self.root, self.original, self.out, self.exe)

    def test_synthetic_artifacts_have_independent_per_process_scopes(self):
        report = self.audit()
        self.assertEqual(len(report["treatments"]), 2)
        self.assertTrue(report["all_original_article_configs_unchanged"])
        self.assertFalse(report["scientific_lod_qualified"])
        self.assertTrue(all(
            not x["two_genuine_committed_steps_inside_one_treatment_run"]
            for x in report["treatments"].values()))

    def test_original_native_input_tampering_rejected(self):
        path = self.root / "input_models" / "book_v7a.bp"
        path.write_bytes(b"wrong synthetic model")
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2724_original_native_model_input_changed"):
            self.audit()

    def test_mutated_variant_intention_refused(self):
        path = self.out / TREATMENTS[0].id / "single-factor-intent.conf"
        path.write_bytes(path.read_bytes() + b"# forged\n")
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2724_treatment_article_input"):
            self.audit()

    def test_source_sha_in_original_native_sidecar_cannot_be_forged(self):
        path = self.out / TREATMENTS[0].id / "accepted_step_1_retry_0.ndjson"
        path.write_bytes(path.read_bytes().replace(b'"session":6306001',
                                                     b'"session":6306002'))
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2724_treatment_report_does_not_match"):
            self.audit()

    def test_forged_aggregated_two_epochs_without_two_in_any_run_refused(self):
        path = self.out / "index.json"
        content = json.loads(path.read_text())
        content["all_treatments_have_genuine_two_accepted_same_run_epochs"] = True
        path.write_text(json.dumps(content))
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2724_pooled_acceptance_misrepresented"):
            self.audit()

    def test_native_execution_config_changed_beyond_io_refused(self):
        path = self.out / TREATMENTS[0].id / "resolved-execution.conf"
        path.write_text(path.read_text().replace(
            "CURVE_POINT_GROWTH_STEPN=2.0",
            "CURVE_POINT_GROWTH_STEPN=3.0"))
        with self.assertRaisesRegex(
                NativeLineageValidationError, "r2724_resolved_config_changed_more_than_io"):
            self.audit()

    def test_independent_gate_byte_edit_rejected(self):
        path = self.out / TREATMENTS[1].id / "original-generator-stderr.log"
        path.write_bytes(path.read_bytes() + b"arbitrary tamper")
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2724_native_controlled_original_process_bytes_invalid"):
            self.audit()


if __name__ == "__main__":
    unittest.main()
