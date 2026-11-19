"""R2.7.28: preserve unmodified Adapter per-patch CSV in two real Eistute C++ replays.

Original and one-factor-variant processes remain separate. Raw local attempts
are not selected outer candidates, native commits, or scientific LOD epochs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

from .native_acceptance_gate_forensics import parse_original_gate_stderr
from .native_active_generation_study import TRIALS, audit as audit_r2726
from .native_controlled_sensitivity import (
    certify_same_run_outcomes, git_blob, make_single_factor_config,
    resolve_isolated_config,
)
from .native_transition_coherence_audit import audit as audit_r2727
from .verify_native_lineage import (
    SOURCE_MODELS, decode_ndjson, require, sha256_file,
    validate_lineage_records,
)

SCHEMA = "apmesh.meshstudio.r2728.original_adapter_patch_csv_observation.v1"
PROTOCOL_BLOB = "62e5bb49a3cb502e877f9dcacfac4269d078c315"
ADAPTER_BLOB = "78f821411f33a8ca7594c8e357bbe4a79e5d33f9"
RUNTIME_BLOB = "d21ceb3397c7825bb50534be072261908c9b0e49"
GENERATOR_BLOB = "844673ea764f3092330e5e9ebb01d8eb339869bc"
ARTICLE_BLOB = "bd368dbad5b61515106b5d74d28cbde159780cd6"
MAX_CSV_BYTES = 2_000_000
MAX_LOG_BYTES = 12_000_000
MAX_SIDECAR_BYTES = 30_000_000
REQUIRED_CSV = {
    "step", "retry", "patch_id", "local_regen_attempt",
    "generation_status", "transition_underresolved", "transition_floor",
    "transition_element_ratio", "internal_element_ratio",
    "interior_transition_imbalance", "generated_faces",
    "quadtree_leaves", "curve_domain_balance",
}


def attest_original_sources(root: Path) -> dict:
    """Pin all pre-existing C++ numerical and CSV-generation logic."""
    sources = {
        "docs/mesh-studio/R2_7_28_PREREGISTERED_EXISTING_ADAPTER_PATCH_CSV_20261119.md":
            PROTOCOL_BLOB,
        "src/adapter/adapter.cpp": ADAPTER_BLOB,
        "src/application/runtime_state.cpp": RUNTIME_BLOB,
        "src/generator/generator_adaptive.cpp": GENERATOR_BLOB,
    }
    out = {}
    for name, expected in sources.items():
        raw = (root / name).read_bytes()
        require(git_blob(raw) == expected,
                "r2728_original_cpp_or_preregistration_bytes_changed")
        out[name] = {"git_blob": expected,
                     "sha256": hashlib.sha256(raw).hexdigest()}
    adapter = (root / "src/adapter/adapter.cpp").read_text(encoding="utf-8")
    runtime = (root / "src/application/runtime_state.cpp").read_text(
        encoding="utf-8")
    require(
        "int WRITE_ADAPTATION_DEBUG = 1;" in runtime
        and '<< "_domain_adaptation.csv";' in adapter
        and "if (!write_adaptation_debug || output_prefix.empty())" in adapter
        and "const bool interior_dominant = aft_stats.internal_element_ratio > 0.66;" in adapter
        and "aft_stats.transition_element_ratio + 1.0e-9 < transition_floor" in adapter,
        "r2728_original_cpp_csv_trigger_or_default_not_proven")
    return out


def _file_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_original_patch_csv(raw: bytes, gate_rows: list[dict]) -> dict:
    """Independently validate actual adapter local attempts, not accepted faces."""
    require(0 < len(raw) <= MAX_CSV_BYTES and b"\x00" not in raw
            and b"\r" not in raw and raw.endswith(b"\n"),
            "r2728_missing_oversized_or_noncanonical_native_patch_csv")
    try:
        data = raw.decode("utf-8")
        reader = csv.DictReader(io.StringIO(data, newline=""))
        columns = reader.fieldnames
        require(columns is not None and len(columns) == len(set(columns))
                and REQUIRED_CSV.issubset(set(columns))
                and len(columns) <= 96,
                "r2728_original_adapter_csv_missing_or_duplicate_headers")
        rows = list(reader)
    except (ValueError, UnicodeDecodeError, csv.Error) as exc:
        raise ValueError("r2728_original_csv_invalid_UTF8_or_syntax") from exc
    require(1 <= len(rows) <= 256,
            "r2728_original_adapter_csv_empty_or_unbounded_rows")
    original_gate_keys = [(g["step"], g["retry"]) for g in gate_rows]
    require(len(original_gate_keys) == 7 and
            original_gate_keys == sorted(set(original_gate_keys)),
            "r2728_not_original_seven_eistute_cpp_gate_attempts")
    by_outer = {}
    uncertain = 0
    clean_rows = []
    unique = set()
    for rec in rows:
        require(None not in rec and all(
                type(value) is str and 0 < len(value) <= 100
                for value in rec.values()),
                "r2728_original_adapter_csv_wrong_column_count_or_empty_cell")
        try:
            step = int(rec["step"])
            retry = int(rec["retry"])
            patch = int(rec["patch_id"])
            local = int(rec["local_regen_attempt"])
            flagged = int(rec["transition_underresolved"])
            generated = int(rec["generated_faces"])
            leaves = int(rec["quadtree_leaves"])
            floor = float(rec["transition_floor"])
            transition = float(rec["transition_element_ratio"])
            internal = float(rec["internal_element_ratio"])
            imbalance = float(rec["interior_transition_imbalance"])
            balance = float(rec["curve_domain_balance"])
        except ValueError as exc:
            raise ValueError("r2728_original_adapter_csv_bad_typed_field") from exc
        key = (step, retry, patch, local)
        require((step, retry) in original_gate_keys and
                0 <= patch < SOURCE_MODELS["eistute"][0] and
                0 <= local <= 3 and key not in unique and
                flagged in (0, 1) and generated >= 0 and leaves >= 0,
                "r2728_original_adapter_csv_wrong_outer_or_duplicate_local_attempt")
        unique.add(key)
        require(
            all(math.isfinite(value) for value in (
                floor, transition, internal, imbalance, balance))
            and 0.08 - 1e-5 <= floor <= 0.24 + 1e-5
            and 0 <= transition <= 1.00001 and
            0 <= internal <= 1.00001 and
            0 <= imbalance < 4 and 0 <= balance <= 2.00001
            and re.fullmatch(r"[a-z_]{2,64}", rec["generation_status"]) is not None,
            "r2728_original_adapter_csv_nonfinite_or_unphysical_metric")
        # Recompute the separately pinned original Adapter imbalance formula.
        # Original ostream rounding prevents binary-exact float comparison.
        computed_imbalance = (
            max(0.0, floor - transition) +
            0.5 * max(0.0, internal - 0.65)
        )
        require(abs(imbalance - computed_imbalance) <= 5e-6,
                "r2728_original_cpp_interior_transition_imbalance_forged")
        # The original CSV uses default C++ stream precision, so a value
        # within 5e-6 of a strict source inequality is inconclusive.
        close = (abs(internal - 0.66) <= 5e-6 or
                 abs(transition - floor) <= 5e-6)
        expected_flag = int(
            internal > 0.66 and transition + 1e-9 < floor)
        if close:
            uncertain += 1
        else:
            require(flagged == expected_flag,
                    "r2728_original_cpp_transition_underresolved_formula_forged")
        by_outer.setdefault((step, retry, patch), set()).add(local)
        clean_rows.append({
            "step": step, "retry": retry, "patch_slot": patch,
            "local_regen_attempt": local,
            "transition_underresolved": bool(flagged),
            "generation_status": rec["generation_status"],
            "internal_element_ratio": internal,
            "transition_element_ratio": transition,
            "transition_floor": floor,
            "interior_transition_imbalance": imbalance,
            "generated_faces": generated,
            "curve_domain_balance": balance,
            "flag_reconstruction_from_rounded_csv_conclusive": not close,
        })
    expected = {(step, retry, patch)
                for step, retry in original_gate_keys for patch in range(4)}
    require(set(by_outer) == expected and
            all(0 in locals_ for locals_ in by_outer.values()) and
            all(locals_ == set(range(max(locals_) + 1))
                for locals_ in by_outer.values()),
            "r2728_original_adapter_missing_patch_or_noncontiguous_local_attempt")
    require(sum(r["step"] == 4 for r in clean_rows) >= 8,
            "r2728_original_step4_patch_attempts_missing")
    # Retain local fallback choices as an explicit SET of possible candidates;
    # do not infer selected outer C++ structural stats from a max retry index.
    step4 = [{
        "retry": retry, "patch_slot": patch,
        "local_attempts": sorted(
            [r for r in clean_rows if
             r["step"] == 4 and r["retry"] == retry and
             r["patch_slot"] == patch],
            key=lambda row: row["local_regen_attempt"]),
        "all_recorded_local_attempts_underresolved": all(
            r["transition_underresolved"] for r in clean_rows if
            r["step"] == 4 and r["retry"] == retry and
            r["patch_slot"] == patch),
    } for retry in (0, 1) for patch in range(4)]
    return {
        "schema": SCHEMA,
        "real_original_outer_cpp_attempts": 7,
        "original_patch_slots_per_cpp_attempt": 4,
        "native_local_patch_attempt_rows": len(clean_rows),
        "local_attempts_not_assumed_selected": True,
        "n_rounding_ambiguous_strict_conditions": uncertain,
        "raw_csv_sha256": _file_hash(raw),
        "step4_local_candidate_sets_by_patch": step4,
        "per_local_attempt": clean_rows,
        "source_native_adapter_csv_directly_observed": True,
        "selected_patch_slots_inferred_only_from_original_cpp_gate": True,
        "scientific_lod_qualified": False,
    }


def _reference(root: Path, exe: Path, original: Path,
               old_trials: Path) -> dict:
    """Verify previous original accepted C++ source and one-factor receipt."""
    require(SOURCE_MODELS["eistute"] == (4, 13),
            "r2728_original_eistute_source_topology_changed")
    article = (root / "configs/eistute/article.conf").read_bytes()
    require(git_blob(article) == ARTICLE_BLOB and
            b"WRITE_ADAPTATION_DEBUG=" not in article and
            b"\r" not in article and article.endswith(b"\n"),
            "r2728_original_article_not_byte_identical_or_debug_override")
    selector = re.search(rb"^INPUT_MODEL=(.+)$", article, re.M)
    require(selector is not None, "r2728_original_native_input_selector_missing")
    model = (root / selector.group(1).decode().strip()).resolve()
    control = json.loads((original /
                          "r2712-eistute-native-lineage-audit.json")
                         .read_text(encoding="utf-8"))
    previous = json.loads((old_trials / "eistute_curve_min_13" /
                           "treatment-report.json").read_text(encoding="utf-8"))
    require(model.is_relative_to(root) and model.is_file() and
            control["native_config_source_sha256"] ==
            _file_hash(article) and
            control["real_model_input_sha256"] == sha256_file(model) ==
            previous["native_model_input_sha256"] and
            control["research_executable_sha256"] == sha256_file(exe) ==
            previous["original_compiled_cpp_executable_sha256"] and
            control["native_accepted_commits"] == 1 and
            previous["source_accepted_steps"] == [1] and
            control["native_rejected_restored"] ==
            previous["restored_native_steps"] == 3 and
            len(control["accepted_snapshots"]) ==
            len(previous["accepted_real_native_face_snapshots"]) == 1,
            "r2728_original_cpp_prior_source_or_variant_not_certified")
    return {
        "article_bytes": article,
        "model_path": model,
        "native_executable_sha256": sha256_file(exe),
        "original_config_sha256": _file_hash(article),
        "real_input_sha256": sha256_file(model),
        "control": control,
        "variant": previous,
        "variant_bytes": make_single_factor_config(
            article, next(x for x in TRIALS if x.model == "eistute")),
    }


def _expected_accepted_sha(ref: dict, role: str) -> str:
    if role == "original":
        return ref["control"]["accepted_snapshots"][0]["source_file_sha256"]
    return ref["variant"]["accepted_real_native_face_snapshots"][0]["sha256"]


def _run_one(exe: Path, root: Path, ref: dict,
             dest: Path, role: str, timeout: int) -> dict:
    dest.mkdir(parents=True, exist_ok=False)
    intent = ref["article_bytes"] if role == "original" else ref["variant_bytes"]
    (dest / "original-intent.conf").write_bytes(intent)
    with TemporaryDirectory(prefix=f"r2728-eistute-{role}-") as tmp:
        work = Path(tmp)
        lineage = work / "accepted-source"
        lineage.mkdir()
        prefix = work / f"eistute-{role}"
        config_bytes = resolve_isolated_config(
            intent.decode("utf-8"), ref["model_path"], prefix).encode("utf-8")
        config = work / "original-isolated-run.conf"
        config.write_bytes(config_bytes)
        (dest / "resolved-execution.conf").write_bytes(config_bytes)
        env = dict(os.environ,
                   APMESH_RESEARCH_LINEAGE_DIR=str(lineage),
                   APMESH_RESEARCH_ACCEPTANCE_GATES="1",
                   APMESH_RESEARCH_EFFECTIVE_BUDGETS="1")
        execution = subprocess.run(
            [str(exe), str(config)], cwd=root, env=env,
            capture_output=True, check=False, timeout=timeout)
        require(len(execution.stdout) <= 3_000_000 and
                len(execution.stderr) <= MAX_LOG_BYTES,
                "r2728_original_cpp_output_log_exceeded_limit")
        (dest / "original-generator-stdout.log").write_bytes(execution.stdout)
        (dest / "original-generator-stderr.log").write_bytes(execution.stderr)
        csv_file = Path(str(prefix) + "_domain_adaptation.csv")
        require(csv_file.is_file() and not csv_file.is_symlink() and
                0 < csv_file.stat().st_size <= MAX_CSV_BYTES,
                "r2728_existing_original_adapter_debug_csv_not_generated")
        raw = csv_file.read_bytes()
        (dest / "original-adapter-domain-adaptation.csv").write_bytes(raw)
        require(execution.returncode == 0 and
                b"R2712_NATIVE_LINEAGE_ERROR=" not in execution.stderr,
                "r2728_original_serial_cpp_process_failed")
        events = parse_original_gate_stderr(execution.stderr)
        marker = re.findall(
            rb"^real_generator_outcomes=1 accepted_tri=(\d+) restored_tri=(\d+)",
            execution.stdout, re.M)
        require(len(marker) == 1 and
                tuple(map(int, marker[0])) == (1, 3),
                "r2728_original_generator_genuine_commit_counts_changed")
        files = list(lineage.glob("*.ndjson"))
        require(len(files) == 1 and not list(lineage.glob("*.pending")),
                "r2728_original_native_postcommit_lineage_missing")
        sidecar = files[0].read_bytes()
        receipt = validate_lineage_records(decode_ndjson(sidecar), "eistute")
        receipt["sha256"] = _file_hash(sidecar)
        require(receipt["accepted_step"] == 1 and receipt["retry_index"] == 0
                and receipt["sha256"] == _expected_accepted_sha(ref, role),
                "r2728_original_cpp_accepted_native_face_bytes_not_identical")
        (dest / "accepted_step_1_retry_0.ndjson").write_bytes(sidecar)
        acceptance = certify_same_run_outcomes(events, [receipt], 1, 3)
        patch = parse_original_patch_csv(raw, events)
        report = {
            "schema": SCHEMA,
            "role": role,
            "true_original_cpp_source_replay": True,
            "article_original_config_sha256": ref["original_config_sha256"],
            "intention_config_sha256": _file_hash(intent),
            "resolved_io_config_sha256": _file_hash(config_bytes),
            "native_model_input_sha256": ref["real_input_sha256"],
            "original_cpp_executable_sha256": ref["native_executable_sha256"],
            "stdout_sha256": _file_hash(execution.stdout),
            "stderr_sha256": _file_hash(execution.stderr),
            "accepted_original_face_sha256": receipt["sha256"],
            "patch_csv_sha256": patch["raw_csv_sha256"],
            "patch_csv_observation": patch,
            "original_cpp_acceptance": acceptance,
            "original_native_accepted_steps": [1],
            "original_cpp_rejected_restored_steps": 3,
            "scientific_lod_qualified": False,
        }
        (dest / "observation-report.json").write_text(
            json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8", newline="\n")
        return report


def capture(root: Path, exe: Path, original: Path, old_trials: Path,
            output: Path, timeout: int = 300) -> dict:
    root, exe = root.resolve(), exe.resolve()
    require(not output.exists() and 10 <= timeout <= 600,
            "r2728_unsafe_observation_directory_or_timeout")
    sources = attest_original_sources(root)
    refs = _reference(root, exe, original, old_trials)
    output.mkdir(parents=True)
    result = [_run_one(exe, root, refs, output / role, role, timeout)
              for role in ("original", "variant")]
    index = {
        "schema": SCHEMA,
        "observation_only_not_new_preregistered_treatment": True,
        "source_attestation": sources,
        "previous_cpp_accepted_face_sha256": [
            _expected_accepted_sha(refs, role)
            for role in ("original", "variant")],
        "replay_roles": ["original", "variant"],
        "actual_source_original_and_variant_in_distinct_cpp_processes": True,
        "source_original_and_variant_each_genuinely_accepted": [1, 1],
        "source_original_and_variant_each_restored": [3, 3],
        "scientific_lod_qualified": False,
    }
    (output / "index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print("R2728_SOURCE_NATIVE_PATCH_CSV_CAPTURE=" + json.dumps({
        role: {"csv_rows": item["patch_csv_observation"][
            "native_local_patch_attempt_rows"],
            "accepted_step": item["original_native_accepted_steps"],
            "original_csv_sha256": item["patch_csv_sha256"],
        } for role, item in zip(("original", "variant"), result)},
        sort_keys=True))
    return index


def audit(root: Path, exe: Path, original: Path, old_trials: Path,
          directory: Path) -> dict:
    """Independently reopen every raw source file with no experiment execution."""
    root, exe = root.resolve(), exe.resolve()
    sources = attest_original_sources(root)
    refs = _reference(root, exe, original, old_trials)
    index = json.loads((directory / "index.json").read_text(encoding="utf-8"))
    require(index.get("schema") == SCHEMA and
            index.get("source_attestation") == sources and
            index.get("replay_roles") == ["original", "variant"] and
            index.get("scientific_lod_qualified") is False and
            index.get("observation_only_not_new_preregistered_treatment") is True
            and set(x.name for x in directory.iterdir()) ==
            {"index.json", "original", "variant"},
            "r2728_original_native_csv_capture_index_forged")
    observations = {}
    for role in ("original", "variant"):
        folder = directory / role
        require(set(x.name for x in folder.iterdir()) == {
            "original-intent.conf", "resolved-execution.conf",
            "original-generator-stdout.log", "original-generator-stderr.log",
            "original-adapter-domain-adaptation.csv",
            "accepted_step_1_retry_0.ndjson", "observation-report.json"},
            "r2728_missing_or_extra_observed_original_cpp_files")
        original_intent = (
            refs["article_bytes"] if role == "original" else refs["variant_bytes"])
        intent = (folder / "original-intent.conf").read_bytes()
        resolved = (folder / "resolved-execution.conf").read_bytes()
        prefix_match = re.search(rb"^OUTPUT_PREFIX=(.+)$", resolved, re.M)
        require(prefix_match is not None and
                intent == original_intent and b"\r" not in resolved,
                "r2728_replay_intent_source_or_output_selector_changed")
        prefix = Path(prefix_match.group(1).decode("utf-8").strip())
        require(prefix.is_absolute() and
                resolved == resolve_isolated_config(
                    intent.decode("utf-8"), refs["model_path"],
                    prefix).encode("utf-8"),
                "r2728_observed_native_config_modified_more_than_io")
        stdout = (folder / "original-generator-stdout.log").read_bytes()
        stderr = (folder / "original-generator-stderr.log").read_bytes()
        gates = parse_original_gate_stderr(stderr)
        marker = re.findall(
            rb"^real_generator_outcomes=1 accepted_tri=(\d+) restored_tri=(\d+)",
            stdout, re.M)
        require(len(marker) == 1 and tuple(map(int, marker[0])) == (1, 3),
                "r2728_replayed_original_cpp_outcomes_not_one_epoch")
        sidecar = (folder / "accepted_step_1_retry_0.ndjson").read_bytes()
        receipt = validate_lineage_records(decode_ndjson(sidecar), "eistute")
        receipt["sha256"] = _file_hash(sidecar)
        require(receipt["sha256"] == _expected_accepted_sha(refs, role),
                "r2728_replayed_accepted_original_tri_faces_not_source_bound")
        acceptance = certify_same_run_outcomes(gates, [receipt], 1, 3)
        raw_csv = (folder / "original-adapter-domain-adaptation.csv").read_bytes()
        patch = parse_original_patch_csv(raw_csv, gates)
        stored = json.loads(
            (folder / "observation-report.json").read_text(encoding="utf-8"))
        require(stored.get("schema") == SCHEMA and
                stored.get("role") == role and
                stored.get("true_original_cpp_source_replay") is True and
                stored.get("intention_config_sha256") == _file_hash(intent) and
                stored.get("resolved_io_config_sha256") == _file_hash(resolved)
                and stored.get("article_original_config_sha256") ==
                refs["original_config_sha256"] and
                stored.get("native_model_input_sha256") ==
                refs["real_input_sha256"] and
                stored.get("original_cpp_executable_sha256") ==
                refs["native_executable_sha256"] and
                stored.get("stdout_sha256") == _file_hash(stdout) and
                stored.get("stderr_sha256") == _file_hash(stderr) and
                stored.get("accepted_original_face_sha256") ==
                receipt["sha256"] and
                stored.get("patch_csv_sha256") == _file_hash(raw_csv) and
                stored.get("patch_csv_observation") == patch and
                stored.get("original_cpp_acceptance") == acceptance and
                stored.get("original_native_accepted_steps") == [1] and
                stored.get("original_cpp_rejected_restored_steps") == 3 and
                stored.get("scientific_lod_qualified") is False,
                "r2728_original_cpp_patch_csv_or_report_not_independently_verified")
        observations[role] = {
            "source_cpp_executable_sha256": refs["native_executable_sha256"],
            "original_source_config_sha256": refs["original_config_sha256"],
            "real_native_accepted_steps": [1],
            "real_native_restored_steps": 3,
            "accepted_original_tri_sha256": receipt["sha256"],
            "native_source_stderr_sha256": _file_hash(stderr),
            "native_adapter_csv_sha256": _file_hash(raw_csv),
            "local_patch_attempts": patch["native_local_patch_attempt_rows"],
            "ambiguous_precision_rows":
                patch["n_rounding_ambiguous_strict_conditions"],
            "patch_rows_for_step4": [
                x for x in patch["per_local_attempt"] if x["step"] == 4],
        }
    require(index["previous_cpp_accepted_face_sha256"] ==
            [_expected_accepted_sha(refs, r)
             for r in ("original", "variant")],
            "r2728_source_native_accepted_face_prior_hash_mismatch")
    return {
        "schema": SCHEMA,
        "original_cpp_source_and_existing_adapter_debug_attested": sources,
        "raw_local_attempts_independently_reaudited": True,
        "original_article_and_cad_input_unmodified": True,
        "original_generator_acceptance_policy_unchanged": True,
        "local_fallback_attempt_not_assumed_selected": True,
        "previous_accepted_faces_identical_to_certified_R2726": True,
        "observations": observations,
        "second_true_same_process_accepted_epoch_observed": False,
        "continuous_source_surface_error_certified": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("capture", "audit"), required=True)
    p.add_argument("--exe", type=Path, required=True)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--original-directory", type=Path, required=True)
    p.add_argument("--r2726-trials", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--report", type=Path)
    p.add_argument("--timeout", type=int, default=300)
    args = p.parse_args()
    if args.mode == "capture":
        capture(args.root, args.exe, args.original_directory,
                args.r2726_trials, args.output_dir, args.timeout)
        return
    require(args.report is not None and not args.report.exists(),
            "r2728_refuse_overwriting_native_audit_report")
    result = audit(args.root, args.exe, args.original_directory,
                   args.r2726_trials, args.output_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n")
    print("R2728_VERIFIED_ORIGINAL_ADAPTER_PATCH_CSV=" + json.dumps({
        k: {"original_cpp_local_rows": v["local_patch_attempts"],
            "accepted_steps": v["real_native_accepted_steps"],
            "step4_rows": len(v["patch_rows_for_step4"])}
        for k, v in result["observations"].items()
    }, sort_keys=True))


if __name__ == "__main__":
    main()
