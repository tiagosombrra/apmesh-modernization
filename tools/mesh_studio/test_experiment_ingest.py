"""Source-bound, negative-first tests for versioned scientific experiment ingestion."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from .experiment_ingest import (ExperimentIngestError, qualify_experiment,
                                 scientific_matrix_from_qualified)

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "tools/mesh_studio/fixtures/experiments/real_p1_pr217.json"
BASE = json.loads(ORIGINAL.read_text(encoding="utf-8"))


class VersionedRealP1Tests(unittest.TestCase):
    def test_pinned_source_is_verified_not_adapted(self):
        result = qualify_experiment(ORIGINAL, repository_root=ROOT)
        self.assertEqual(result.evidence_grade,
                         "REAL_P1_GEOMETRY_AND_SPECIFIED_METRICS_VERIFIED")
        self.assertEqual(result.mesh_sha256,BASE["artifacts"]["mesh"]["sha256"])
        self.assertEqual(result.adaptive_accepted_epochs,0)
        self.assertEqual(result.candidate_rejections,0)
        self.assertFalse(result.figure_comparison_eligible)
        self.assertEqual(len(result.metric_rows),3)
        self.assertEqual(result.source_model_sha256,None)

    def test_matrix_is_explicitly_unavailable(self):
        result=qualify_experiment(ORIGINAL,repository_root=ROOT)
        matrix=scientific_matrix_from_qualified((result,))
        self.assertEqual(len(matrix["cells"]),6)
        self.assertTrue(all(c["status"]=="NOT_AVAILABLE" for c in matrix["cells"]))
        self.assertEqual(matrix["excluded_runs"][0]["reason"],
                         "FIXED_SAMPLING_NOT_FACTORIAL")
        self.assertFalse(matrix["comparison_protocol_qualified"])

    def test_duplicate_qualification_run_rejected(self):
        run=qualify_experiment(ORIGINAL,repository_root=ROOT)
        with self.assertRaisesRegex(ExperimentIngestError,"invalid_qualified_run_set"):
            scientific_matrix_from_qualified((run,run))

    def test_receipt_serializable_exactly_with_no_nonfinite(self):
        result=qualify_experiment(ORIGINAL,repository_root=ROOT)
        as_text=json.dumps(result.as_receipt(),sort_keys=True,allow_nan=False)
        self.assertIn("NO_GENERATOR_ADAPTIVE_HISTORY_QUALIFICATION",as_text)
        self.assertNotIn('"comparison_eligible": true',as_text)

    def test_cli_produces_deterministic_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            first=Path(tmp)/"first"
            second=Path(tmp)/"second"
            for destination in (first,second):
                p=subprocess.run([sys.executable,"-m","tools.mesh_studio.experiment_cli",
                                  str(ORIGINAL),"--repository-root",str(ROOT),
                                  "--output-dir",str(destination)],cwd=ROOT,
                                 capture_output=True,text=True,timeout=30)
                self.assertEqual(p.returncode,0,p.stderr)
            for filename in ("qualified_run.json","scientific_matrix.json"):
                self.assertEqual((first/filename).read_bytes(),(second/filename).read_bytes())
            result=json.loads((first/"qualified_run.json").read_text())
            self.assertFalse(result["figure_comparison_eligible"])

    def test_cli_rejects_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"present";out.mkdir()
            result=subprocess.run([sys.executable,"-m","tools.mesh_studio.experiment_cli",
                                   str(ORIGINAL),"--repository-root",str(ROOT),
                                   "--output-dir",str(out)],cwd=ROOT,
                                  capture_output=True,text=True,timeout=30)
            self.assertNotEqual(result.returncode,0)


class RealManifestMutationTests(unittest.TestCase):
    def _mutate(self, callback, expected):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            obj_source=ROOT/BASE["artifacts"]["mesh"]["path"]
            report_source=ROOT/BASE["artifacts"]["generator_report"]["path"]
            (root/"mesh.obj").write_bytes(obj_source.read_bytes())
            (root/"generator_report.json").write_bytes(report_source.read_bytes())
            data=deepcopy(BASE)
            data["artifacts"]["mesh"]["path"]="mesh.obj"
            data["artifacts"]["generator_report"]["path"]="generator_report.json"
            callback(data,root)
            target=root/"experiment.json"
            target.write_text(json.dumps(data,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
            with self.assertRaisesRegex(ExperimentIngestError,expected):
                qualify_experiment(target,repository_root=root)

    def test_unsupported_version(self):
        self._mutate(lambda d,r:d.__setitem__("schema","apmesh.meshstudio.experiment_run.v2"),
                     "unsupported_run_schema")

    def test_unknown_root_property_not_ignored(self):
        self._mutate(lambda d,r:d.__setitem__("scientifically_accepted",True),
                     "invalid_run_fields")

    def test_reject_mesh_sha_mismatch(self):
        self._mutate(lambda d,r:d["artifacts"]["mesh"].__setitem__("sha256","0"*64),
                     "mesh_hash_mismatch")

    def test_reject_report_sha_mismatch(self):
        self._mutate(lambda d,r:d["artifacts"]["generator_report"].__setitem__("sha256","0"*64),
                     "generator_report_hash_mismatch")

    def test_reject_unsafe_relative_path(self):
        self._mutate(lambda d,r:d["artifacts"]["mesh"].__setitem__("path","../accepted.obj"),
                     "unsafe_mesh_path")

    def test_reject_absolute_path(self):
        self._mutate(lambda d,r:d["artifacts"]["mesh"].__setitem__("path","/tmp/file.obj"),
                     "unsafe_mesh_path")

    def test_reject_windows_backslash(self):
        self._mutate(lambda d,r:d["artifacts"]["mesh"].__setitem__("path",r"..\\accepted.obj"),
                     "invalid_mesh_path")

    def test_reject_symbolic_link_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"inside";root.mkdir()
            outside=Path(tmp)/"outside.obj";outside.write_bytes((ROOT/BASE["artifacts"]["mesh"]["path"]).read_bytes())
            (root/"escape.obj").symlink_to(outside)
            report=(root/"generator_report.json")
            report.write_bytes((ROOT/BASE["artifacts"]["generator_report"]["path"]).read_bytes())
            data=deepcopy(BASE)
            data["artifacts"]["mesh"]["path"]="escape.obj"
            data["artifacts"]["generator_report"]["path"]="generator_report.json"
            path=root/"exp.json";path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ExperimentIngestError,"unsafe_mesh_path"):
                qualify_experiment(path,repository_root=root)

    def test_reject_fake_adaptive_epoch(self):
        self._mutate(lambda d,r:d["events"][0].update(
            {"decision":"ACCEPTED_ADAPTIVE_EPOCH","adaptive_epoch":1,"trace_sha256":"a"*64}),
            "adaptive_acceptance_requires_native_trace_oracle")

    def test_reject_nonconsecutive_events(self):
        self._mutate(lambda d,r:d["events"][0].__setitem__("event_index",1),
                     "nonconsecutive_event_indices")

    def test_reject_missing_history_mesh_link(self):
        self._mutate(lambda d,r:d["events"][0].__setitem__("mesh_sha256","0"*64),
                     "history_mesh_not_linked")

    def test_reject_fake_anisotropy_claim(self):
        self._mutate(lambda d,r:d["method"].__setitem__("sizing_policy","anisotropic"),
                     "anisotropic_field_contract_not_implemented")

    def test_reject_isotropic_p1_claim(self):
        self._mutate(lambda d,r:d["method"].__setitem__("sizing_policy","isotropic"),
                     "p1_source_or_method_mismatch")

    def test_reject_all_quad_p1_claim(self):
        self._mutate(lambda d,r:d["method"].__setitem__("topology","all_quad"),
                     "topology_inventory_mismatch")

    def test_reject_fake_generator_commit(self):
        self._mutate(lambda d,r:d["execution"].__setitem__("commit","f"*40),
                     "p1_execution_not_bound")

    def test_reject_fake_workflow_id(self):
        self._mutate(lambda d,r:d["execution"].__setitem__("workflow_run",123),
                     "p1_execution_not_bound")

    def test_reject_fake_ci_artifact(self):
        self._mutate(lambda d,r:d["execution"].__setitem__("artifact_id",123),
                     "p1_execution_not_bound")

    def test_reject_wrong_model_identity(self):
        self._mutate(lambda d,r:d["source_model"].__setitem__("id","UnknownModel"),
                     "p1_source_or_method_mismatch")

    def test_reject_claimed_unverified_oracle(self):
        self._mutate(lambda d,r:d["evidence"].__setitem__("independent_oracle","fake_oracle"),
                     "unsupported_claimed_independent_oracle")

    def test_reject_synthetic_claim_for_real_mesh(self):
        self._mutate(lambda d,r:d["evidence"].update({"kind":"synthetic","synthetic":True,"independent_oracle":None}),
                     "mesh_evidence_origin_mismatch")

    def test_reject_missing_p1_metric(self):
        self._mutate(lambda d,r:d["measurements"].pop(),
                     "p1_measurement_inventory_mismatch")

    def test_reject_metric_units(self):
        self._mutate(lambda d,r:d["measurements"][0].__setitem__("units","meters"),
                     "p1_metric_definition_mismatch")

    def test_reject_metric_frame(self):
        self._mutate(lambda d,r:d["measurements"][0].__setitem__("frame","uv"),
                     "p1_metric_definition_mismatch")

    def test_reject_metric_sampling(self):
        self._mutate(lambda d,r:d["measurements"][0].__setitem__("sampling","one_vertex"),
                     "p1_metric_definition_mismatch")

    def test_reject_forged_metric_definition(self):
        self._mutate(lambda d,r:d["measurements"][0].__setitem__("definition_sha256","a"*64),
                     "p1_metric_definition_mismatch")

    def test_reject_forged_metric_value(self):
        self._mutate(lambda d,r:d["measurements"][0].__setitem__("value",1.0),
                     "p1_metric_not_independently_reproducible")

    def test_reject_source_reported_metric_claim(self):
        self._mutate(lambda d,r:d["measurements"][0].__setitem__("origin","source_reported_unverified"),
                     "p1_metric_not_independently_reproducible")

    def test_reject_nan_metric(self):
        self._mutate(lambda d,r:d["measurements"][0].__setitem__("value","nan"),
                     "invalid_metric_value")

    def test_reject_python_boolean_as_numeric(self):
        self._mutate(lambda d,r:d["measurements"][0].__setitem__("value",True),
                     "invalid_metric_value")

    def test_reject_forged_hardware_time(self):
        self._mutate(lambda d,r:d["execution"].__setitem__("wall_seconds",-2),
                     "invalid_wall_seconds")

    def test_reject_report_corruption_even_with_updated_claim_hash(self):
        def corrupt(d,root):
            p=root/"generator_report.json"
            fake=json.loads(p.read_text())
            fake["adaptive_epochs"]=2
            p.write_text(json.dumps(fake),encoding="utf-8")
            d["artifacts"]["generator_report"]["sha256"]=sha256(p.read_bytes()).hexdigest()
        # An independently pinned generator oracle rejects self-consistent lies.
        with self.assertRaisesRegex(ExperimentIngestError,"p1_generator_report_not_original"):
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                (root/"mesh.obj").write_bytes((ROOT/BASE["artifacts"]["mesh"]["path"]).read_bytes())
                (root/"generator_report.json").write_bytes((ROOT/BASE["artifacts"]["generator_report"]["path"]).read_bytes())
                data=deepcopy(BASE)
                data["artifacts"]["mesh"]["path"]="mesh.obj"
                data["artifacts"]["generator_report"]["path"]="generator_report.json"
                corrupt(data,root)
                p=root/"experiment.json";p.write_text(json.dumps(data))
                qualify_experiment(p,repository_root=root)

    def test_reject_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"dup.json"
            p.write_text('{"schema":"one","schema":"two"}',encoding='utf-8')
            with self.assertRaisesRegex(ExperimentIngestError,"duplicate_json_property"):
                qualify_experiment(p,repository_root=ROOT)

    def test_reject_oversized_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"huge.json";p.write_bytes(b"a"*(256*1024+1))
            with self.assertRaisesRegex(ExperimentIngestError,"missing_or_oversized_experiment_manifest"):
                qualify_experiment(p,repository_root=ROOT)

    def test_reject_nonfinite_json_constant(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"nan.json";p.write_text('{"value":NaN}')
            with self.assertRaisesRegex(ExperimentIngestError,"nonfinite_json_constant"):
                qualify_experiment(p,repository_root=ROOT)

    def test_unverified_source_cannot_gain_scientific_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"mesh.obj").write_bytes((ROOT/BASE["artifacts"]["mesh"]["path"]).read_bytes())
            (root/"report.json").write_bytes((ROOT/BASE["artifacts"]["generator_report"]["path"]).read_bytes())
            data=deepcopy(BASE)
            data["artifacts"]["mesh"]["path"]="mesh.obj"
            data["artifacts"]["generator_report"]["path"]="report.json"
            data["evidence"]={"kind":"source_unverified","synthetic":False,"independent_oracle":None}
            data["execution"]["workflow_run"]=999
            data["execution"]["artifact_id"]=999
            data["measurements"][0]["value"]=.1
            path=root/"unverified.json";path.write_text(json.dumps(data))
            result=qualify_experiment(path,repository_root=root)
            self.assertEqual(result.evidence_grade,"SOURCE_PROVISIONAL_NOT_SCIENTIFICALLY_QUALIFIED")
            self.assertFalse(result.figure_comparison_eligible)


if __name__ == "__main__":
    unittest.main()

# Keep P1's originally captured report and timing provenance immutable.
class P1OriginalReceiptTests(unittest.TestCase):
    def test_modified_report_cannot_gain_qualification_even_with_new_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"mesh.obj").write_bytes((ROOT/BASE["artifacts"]["mesh"]["path"]).read_bytes())
            report=deepcopy(json.loads((ROOT/BASE["artifacts"]["generator_report"]["path"]).read_text()))
            report["unverified_extra_claim"]="this data was not in source CI"
            path=root/"generator_report.json"
            path.write_text(json.dumps(report,sort_keys=True))
            d=deepcopy(BASE)
            d["artifacts"]["mesh"]["path"]="mesh.obj"
            d["artifacts"]["generator_report"]["path"]="generator_report.json"
            d["artifacts"]["generator_report"]["sha256"]=sha256(path.read_bytes()).hexdigest()
            manifest=root/"run.json";manifest.write_text(json.dumps(d))
            with self.assertRaisesRegex(ExperimentIngestError,"p1_generator_report_not_original"):
                qualify_experiment(manifest,repository_root=root)

    def test_unmeasured_p1_runtime_cannot_be_invented(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=deepcopy(BASE);d["execution"]["wall_seconds"]=12.5
            path=Path(tmp)/"run.json";path.write_text(json.dumps(d))
            with self.assertRaisesRegex(ExperimentIngestError,"p1_runtime_not_measured"):
                qualify_experiment(path,repository_root=ROOT)

class ExperimentSchemaInteropTests(unittest.TestCase):
    def test_schema_is_valid_and_real_p1_conforms(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("Optional JSON Schema interoperability dependency not installed")
        path=ROOT/"tools/mesh_studio/schemas/experiment_run_v1.schema.json"
        schema=json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(BASE)

    def test_schema_rejects_missing_or_unknown_fields(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("Optional JSON Schema interoperability dependency not installed")
        path=ROOT/"tools/mesh_studio/schemas/experiment_run_v1.schema.json"
        validator=jsonschema.Draft202012Validator(json.loads(path.read_text()))
        corrupted=deepcopy(BASE)
        corrupted["source_model"].pop("identity_basis")
        self.assertTrue(list(validator.iter_errors(corrupted)))
        corrupted=deepcopy(BASE)
        corrupted["measurements"][0]["fake_acceptance"]=True
        self.assertTrue(list(validator.iter_errors(corrupted)))

class AdditionalBoundedInputTests(unittest.TestCase):
    def test_reject_missing_baseline_mesh_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=deepcopy(BASE)
            data["events"][0]["mesh_sha256"]=None
            p=Path(tmp)/"bad.json";p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ExperimentIngestError,"baseline_mesh_not_bound"):
                qualify_experiment(p,repository_root=ROOT)

    def test_reject_windows_drive_relative_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=deepcopy(BASE)
            data["artifacts"]["mesh"]["path"]="C:artifact.obj"
            p=Path(tmp)/"bad.json";p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ExperimentIngestError,"invalid_mesh_path"):
                qualify_experiment(p,repository_root=ROOT)

class CliNegativeReceiptTests(unittest.TestCase):
    def test_invalid_manifest_cli_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/"must_not_exist"
            bad=Path(tmp)/"bad.json"
            data=deepcopy(BASE);data["measurements"][0]["value"]=-100
            bad.write_text(json.dumps(data))
            run=subprocess.run([sys.executable,"-m","tools.mesh_studio.experiment_cli",
                                str(bad),"--repository-root",str(ROOT),
                                "--output-dir",str(output)],cwd=ROOT,
                               capture_output=True,text=True,timeout=30)
            self.assertEqual(run.returncode,2)
            self.assertIn("Experiment rejected:",run.stderr)
            self.assertFalse(output.exists())
