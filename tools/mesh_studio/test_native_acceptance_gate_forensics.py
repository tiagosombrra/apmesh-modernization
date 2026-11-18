"""Synthetic R2.7.23 acceptance telemetry adversarial contracts only.

These tests never claim a genuine C++ source accepted epoch.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import unittest

from tools.mesh_studio.native_acceptance_gate_forensics import (
    BOOL_FIELDS, NUMBER_FIELDS, SCHEMA, audit_original_gate_model,
    parse_original_gate_stderr,
)
from tools.mesh_studio.verify_native_lineage import NativeLineageValidationError


def row(step:int, accepted:bool, retry:int=0)->dict:
    """A fully synthetic mode-zero gate consistent with the native formula."""
    booleans={key:True for key in BOOL_FIELDS}
    booleans.update({
        "stable_mode":True,
        "score_ok":accepted,
        "small_mesh_progress_override":False,
        "predicted_branch_accept_not_committed":accepted,
        "stable_mid_explore_accept":False,
        "stable_late_explore_accept":False,
        "step1_override":False,
        "budget_driven_step1_ok":False,
    })
    numbers={key:0.5 for key in NUMBER_FIELDS}
    numbers.update({
        "error_improvement_fraction":0.12 if accepted else -0.17,
        "previous_error":1.0,
        "candidate_error":0.88 if accepted else 1.17,
        "element_growth_factor":1.2,
        "candidate_quality_min":0.45,
        "candidate_quality_good_ratio_ge_0_60":0.65,
        "candidate_quality_poor_ratio":0.2,
    })
    return {
        "schema":SCHEMA, "step":step, "retry":retry,
        "acceptance_mode":0, **booleans, **numbers,
        "scientific_lod_admitted":False,
    }


def synthetic_source():
    rows=[row(1,True),row(2,False),row(3,False),row(4,False)]
    stderr=b"native debug only\n" + b"".join(
        b"R2723_NATIVE_ACCEPTANCE_GATE="+
        json.dumps(r,sort_keys=True).encode()+b"\n" for r in rows)
    report={
        "original_model":"eistute",
        "native_stderr_sha256":hashlib.sha256(stderr).hexdigest(),
        "r2718_original_stderr_sha256":hashlib.sha256(stderr).hexdigest(),
        "accepted_snapshots":[{
            "accepted_step":1, "retry_index":0,
            "source_file_sha256":"a"*64,
        }],
        "native_accepted_commits":1,
        "native_rejected_restored":3,
        "second_accepted_epoch_observed":False,
        "real_model_input_sha256":"b"*64,
        "native_config_source_sha256":"c"*64,
        "research_executable_sha256":"d"*64,
    }
    return rows,stderr,report


def encode(rows):
    return b"header\n"+b"".join(
        b"R2723_NATIVE_ACCEPTANCE_GATE="+
        json.dumps(r,sort_keys=True).encode()+b"\n" for r in rows)


class OriginalNativeAcceptanceGateContracts(unittest.TestCase):
    def test_postcommit_provenance_not_inferred_from_predicted_gate(self):
        _rows,stderr,report=synthetic_source()
        audited=audit_original_gate_model("eistute",stderr,report)
        self.assertEqual(audited["original_native_accepted_steps"],[1])
        self.assertEqual(audited["original_rejected_restored_steps"],3)
        self.assertEqual(audited["original_gate_local_attempt_count"],4)
        self.assertFalse(audited["two_independently_accepted_source_epochs"])
        self.assertFalse(audited["scientific_lod_qualified"])
        for step in audited["actual_original_precommit_attempts"][1:]:
            self.assertIsNone(step["source_accepted_sidecar_sha256"])

    def test_forged_second_precommit_accept_without_sidecar_rejected(self):
        rows,_,report=synthetic_source()
        rows[1]=row(2,True)
        stderr=encode(rows)
        report["native_stderr_sha256"]=hashlib.sha256(stderr).hexdigest()
        report["r2718_original_stderr_sha256"]=report["native_stderr_sha256"]
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2723_original_precommit_decision_not_matched"):
            audit_original_gate_model("eistute",stderr,report)

    def test_native_original_stderr_sha_changed_rejected(self):
        _,stderr,report=synthetic_source()
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2723_original_cpp_stderr_sha"):
            audit_original_gate_model("eistute",stderr+b"tampered",report)

    def test_duplicate_original_step_retry_rejected(self):
        rows,_,_=synthetic_source()
        rows.append(deepcopy(rows[-1]))
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2723_duplicate_original_local"):
            parse_original_gate_stderr(encode(rows))

    def test_untrusted_json_duplicate_field_rejected(self):
        rows,_,_=synthetic_source()
        raw=json.dumps(rows[0]).encode()
        duplicate=raw[:-1]+b',"step":42}'
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2723_duplicate_original_gate_json"):
            parse_original_gate_stderr(
                b"R2723_NATIVE_ACCEPTANCE_GATE="+duplicate+b"\n")

    def test_inconsistent_native_mode_zero_predicate_rejected(self):
        rows,_,_=synthetic_source()
        rows[1]["score_ok"]=True
        rows[1]["predicted_branch_accept_not_committed"]=True
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2723_original_cpp_stable_score_gate"):
            parse_original_gate_stderr(encode(rows))

    def test_missing_original_restoration_rejected(self):
        rows,_,report=synthetic_source()
        stderr=encode(rows)
        report["native_stderr_sha256"]=hashlib.sha256(stderr).hexdigest()
        report["r2718_original_stderr_sha256"]=report["native_stderr_sha256"]
        report["native_rejected_restored"]=2
        with self.assertRaisesRegex(
                NativeLineageValidationError,
                "r2723_original_failed_steps_not_equal_restored"):
            audit_original_gate_model("eistute",stderr,report)

    def test_nonfinite_quality_number_rejected(self):
        rows,_,_=synthetic_source()
        rows[0]["candidate_quality_min"]=float("nan")
        with self.assertRaisesRegex(ValueError,"r2723_invalid_cpp_gate_json"):
            parse_original_gate_stderr(encode(rows))

    def test_malformed_scope_field_rejected(self):
        rows,_,_=synthetic_source()
        rows[0]["scientific_lod_admitted"]=True
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2723_original_acceptance_gate_schema"):
            parse_original_gate_stderr(encode(rows))

    def test_original_model_relabelled_rejected(self):
        _,stderr,report=synthetic_source()
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2723_original_cpp_stderr_sha"):
            audit_original_gate_model("book",stderr,report)

    def test_false_boolean_with_nonboolean_value_rejected(self):
        rows,_,_=synthetic_source()
        rows[2]["quality_gate_ok"]=0
        with self.assertRaisesRegex(
                NativeLineageValidationError,"r2723_original_acceptance_gate_schema"):
            parse_original_gate_stderr(encode(rows))


if __name__=="__main__":
    unittest.main()
