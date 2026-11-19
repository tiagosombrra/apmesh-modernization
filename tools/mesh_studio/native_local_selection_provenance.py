"""R2.7.30: certify actual original C++ Adapter local selections without changing TRI.

New standalone probe is observability only; selected-for-Adapter-return is
not accepted by GeneratorAdaptive and is never a scientific LOD epoch.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

from .native_acceptance_gate_forensics import parse_original_gate_stderr
from .native_boundary_ownership import read_actual_adapter_events
from .native_controlled_sensitivity import (
    certify_same_run_outcomes, git_blob, resolve_isolated_config,
)
from .native_patch_csv_replay import (
    _expected_accepted_sha, _reference, audit as audit_r2728,
)
from .native_transition_classifier_semantics import (
    source_attestation as attest_r2729, inspect_csv,
)
from .verify_native_lineage import (
    decode_ndjson, require, sha256_file, validate_lineage_records,
)

SCHEMA = "apmesh.meshstudio.r2730.original_cpp_adapter_selected_local_provenance.v1"
SOURCE_PINS = {
    "docs/mesh-studio/R2_7_30_PREREGISTERED_LOCAL_SELECTION_PROVENANCE_20261119.md":
        "8b71b55e5cfe519be5a4339c8e1c6991bd0906c7",
    "tests/quad/generator_outcome_probe.cpp":
        "49736e6c207e2f728b206f8fc237c00ceef9b061",
    "tests/quad/generator_local_selection_probe.cpp":
        "8fcba75ae55d42bda610fb310977ab5f25dcfb00",
    "research/quad/adapter_capture.h":
        "c22fbe8ef19f65b2ec5ed88284adfb6d8ccbeac1",
    "docs/mesh-studio/R2_7_30A_ADAPTER_INVOCATION_EPOCH_SCOPE_CLARIFICATION_20261119.md":
        "d6b62155d96f15f23cf137ab95cbe43c829d7e52",
}
EVENT_PATTERN = re.compile(
    rb"^R2730_LOCAL_SELECTION=ordinal=(\d+),session=(\d+),"
    rb"outer_epoch=(\d+),outer_retry=(\d+),step=(\d+),"
    rb"retry=(\d+),patch=(\d+),local=(\d+),"
    rb"kind=(selected|superseded|generation_failed),"
    rb"status=([a-z_]{2,64})$",
    re.MULTILINE,
)
MAX_STDOUT = 3_000_000
MAX_STDERR = 12_000_000
MAX_CSV_BYTES = 2_000_000
MAX_SIDECAR_BYTES = 30_000_000
ROLES = ("original", "variant")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def attest_original_selection_source(root: Path) -> dict:
    """Require exact prior registered source and the distinct observer files."""
    receipt = attest_r2729(root)
    for path, expected in SOURCE_PINS.items():
        raw = (root / path).read_bytes()
        require(git_blob(raw) == expected,
                "r2730_original_cpp_observer_or_prior_registration_drifted")
        receipt[path] = {"git_blob": expected, "sha256": _sha(raw)}
    old = (root / "tests/quad/generator_outcome_probe.cpp").read_bytes()
    new = (root / "tests/quad/generator_local_selection_probe.cpp").read_bytes()
    require(new != old and
            b"R2730_LOCAL_SELECTION=ordinal=" in new and
            b"event.attempt.outer.epoch" in new and
            b"PublishLocalSelections" in (
                root / "src/adapter/adapter.cpp").read_bytes(),
            "r2730_original_selection_observer_not_separate_or_incomplete")
    return receipt


def parse_native_local_selection(stdout: bytes) -> list[dict]:
    """Parse a bounded source-native chronology, including superseded events."""
    require(0 < len(stdout) <= MAX_STDOUT and
            b"R2730_LOCAL_SELECTION=" in stdout,
            "r2730_native_cpp_selection_stream_missing_or_oversized")
    result = []
    for number, line in enumerate(stdout.splitlines()):
        if not line.startswith(b"R2730_LOCAL_SELECTION="):
            continue
        match = EVENT_PATTERN.fullmatch(line)
        require(match is not None,
                "r2730_native_cpp_local_selection_event_malformed")
        parts = match.groups()
        vals = list(map(int, parts[:8]))
        ordinal, session, epoch, outer_retry, step, retry, patch, local = vals
        kind, status = parts[8].decode("ascii"), parts[9].decode("ascii")
        require(ordinal == len(result) + 1 and
                session == 6306001 and epoch > 0 and
                1 <= step <= 4 and 0 <= patch < 4 and
                0 <= local <= 3 and outer_retry in (0, 1) and
                retry in (0, 1) and kind in (
                    "selected", "superseded", "generation_failed"),
                "r2730_original_cpp_local_selection_chronology_or_scope_invalid")
        if result:
            require(epoch >= result[-1]["outer_epoch"],
                    "r2730_original_cpp_global_epoch_not_monotone")
        result.append({
            "ordinal": ordinal, "outer_epoch": epoch,
            "step": step, "retry": retry, "patch": patch,
            "local": local, "kind": kind, "status": status,
        })
    require(24 <= len(result) <= 256,
            "r2730_original_native_cpp_adapter_events_count_out_of_scope")
    return result


def _groups(rows: list[dict], origin: str) -> list[list[dict]]:
    """Reconstruct only chronologically adjacent local-attempt groups."""
    groups: list[list[dict]] = []
    current: list[dict] = []
    for row in rows:
        local = row["local"]
        if local == 0 and current:
            groups.append(current)
            current = []
        require(local == len(current),
                "r2730_" + origin + "_local_attempt_sequence_not_contiguous")
        if current:
            require(all(
                row[key] == current[0][key]
                for key in ("step", "retry", "patch")),
                "r2730_" + origin + "_patch_group_mixed_scopes")
            if origin == "cpp":
                require(row["outer_epoch"] ==
                        current[0]["outer_epoch"],
                        "r2730_native_cpp_selection_group_mixed_epochs")
        current.append(row)
    if current:
        groups.append(current)
    require(len(groups) == 40,
            "r2730_" + origin + "_original_eistute_adapter_group_count_changed")
    return groups


def join_selected_local_to_native_csv(stdout: bytes, raw_csv: bytes,
                                      role: str) -> dict:
    """Bind observer events to original Adapter CSV by chronological runs.

    A local CSV tuple is NOT a unique identifier across native outer epochs;
    this join therefore requires every complete attempt group, original
    within-patch event order and source status to agree, not just tuple count.
    """
    require(role in ROLES and 0 < len(raw_csv) <= MAX_CSV_BYTES,
            "r2730_source_role_or_raw_csv_invalid")
    raw_events = parse_native_local_selection(stdout)
    prior = inspect_csv(raw_csv)
    native_rows = list(csv.DictReader(
        io.StringIO(raw_csv.decode("utf-8"), newline="")))
    original_rows = [{
        "step": int(row["step"]), "retry": int(row["retry"]),
        "patch": int(row["patch_id"]),
        "local": int(row["local_regen_attempt"]),
        "status": row["generation_status"],
        "raw": row,
        "derived": prior["records"][i],
    } for i, row in enumerate(native_rows)]
    require(len(original_rows) == (104 if role == "original" else 112),
            "r2730_real_original_cpp_csv_row_count_changed")
    csv_groups = _groups(original_rows, "csv")
    observer_groups = _groups(raw_events, "cpp")
    require(sum(map(len, csv_groups)) == len(raw_events),
            "r2730_native_cpp_events_not_one_to_one_with_source_csv")
    selected = []
    all_obs = []
    for index, (csv_group, event_group) in enumerate(
            zip(csv_groups, observer_groups, strict=True)):
        require(len(csv_group) == len(event_group),
                "r2730_original_cpp_selection_group_length_mismatch")
        for row, event in zip(csv_group, event_group, strict=True):
            require(all(row[key] == event[key] for key in (
                "step", "retry", "patch", "local", "status")),
                "r2730_native_cpp_local_selection_and_raw_csv_differ")
            all_obs.append({
                "ordinal": event["ordinal"], "outer_epoch": event["outer_epoch"],
                "step": event["step"], "retry": event["retry"],
                "patch": event["patch"], "local": event["local"],
                "kind": event["kind"],
                "generation_status": event["status"],
            })
        chosen = [event for event in event_group
                  if event["kind"] == "selected"]
        require(len(chosen) == 1 and
                all(event["kind"] != "generation_failed"
                    for event in event_group) and
                all(event["kind"] == "superseded"
                    for event in event_group
                    if event["ordinal"] != chosen[0]["ordinal"]),
                "r2730_original_cpp_local_return_identity_not_single_selected")
        idx = chosen[0]["local"]
        csv_row = csv_group[idx]
        derived = csv_row["derived"]
        selected.append({
            "adapter_return_index": index,
            "outer_epoch": chosen[0]["outer_epoch"],
            "step": chosen[0]["step"],
            "retry": chosen[0]["retry"], "patch": chosen[0]["patch"],
            "original_selected_local_attempt": idx,
            "generated_faces": int(csv_row["raw"]["generated_faces"]),
            "aft_stage1_transition_ratio":
                derived["aft_stage1_shape_elongation_fraction"],
            "regional_spatial_or_shape_ratio":
                derived["regional_spatial_or_shape_transition_fraction"],
            "internal_element_ratio":
                derived["aft_stage1_internal_fraction"],
            "original_transition_floor":
                derived["transition_floor_original"],
            "transition_underresolved":
                derived["original_cpp_underresolved"],
            "local_status": chosen[0]["status"],
            "local_selected_is_not_global_accepted_tri": True,
        })
    require(len(selected) == 40 and
            [r["adapter_return_index"] for r in selected] ==
            list(range(40)),
            "r2730_original_cpp_adapter_return_chronology_not_identified")
    step4 = [r for r in selected if r["step"] == 4]
    require(len(step4) == 16 and
            all(r["transition_underresolved"] and
                r["local_status"] == "curve_transition_needs_retry" and
                r["aft_stage1_transition_ratio"] <
                r["original_transition_floor"] for r in step4),
            "r2730_original_cpp_selected_step4_not_underresolved")
    return {
        "role": role,
        "original_cpp_selected_adapter_returns": len(selected),
        "original_cpp_selected_adapter_returns_at_step4": len(step4),
        "original_cpp_all_local_event_rows": len(all_obs),
        "actual_original_cpp_sole_selected_event_per_adapter_return": True,
        "exact_original_cpp_csv_status_and_group_order_reproduced": True,
        "selected_local_is_not_global_accepted_epoch": True,
        "outer_retry_and_local_retry_are_distinct_source_dimensions": True,
        "adapter_return_index_is_group_order_not_global_epoch": True,
        "source_cpp_adapter_csv_sha256": _sha(raw_csv),
        "source_cpp_selection_stdout_sha256": _sha(stdout),
        "local_observations": all_obs,
        "selected_local_returns": selected,
        "genuine_source_cpp_accepted_steps": [1],
        "scientific_lod_qualified": False,
    }


def _run_one(root: Path, selection_exe: Path, reference: dict,
             folder: Path, role: str, baseline_dir: Path,
             timeout: int) -> dict:
    """Execute original engine with standalone observer and preserve raw proof."""
    folder.mkdir(parents=True, exist_ok=False)
    original = (baseline_dir / role /
                "original-adapter-domain-adaptation.csv").read_bytes()
    intent = (reference["article_bytes"] if role == "original"
              else reference["variant_bytes"])
    (folder / "original-intent.conf").write_bytes(intent)
    with TemporaryDirectory(prefix="r2730-original-local-selection-") as tmp:
        work = Path(tmp)
        prefix = work / role
        lineage = work / "original-tri"
        lineage.mkdir()
        resolved = resolve_isolated_config(
            intent.decode("utf-8"), reference["model_path"],
            prefix).encode("utf-8")
        config = work / "resolved.conf"
        config.write_bytes(resolved)
        (folder / "resolved-execution.conf").write_bytes(resolved)
        env = dict(
            os.environ,
            APMESH_RESEARCH_LINEAGE_DIR=str(lineage),
            APMESH_RESEARCH_ACCEPTANCE_GATES="1",
            APMESH_RESEARCH_EFFECTIVE_BUDGETS="1",
        )
        p = subprocess.run(
            [str(selection_exe), str(config)], cwd=root, env=env,
            capture_output=True, timeout=timeout, check=False)
        require(p.returncode == 0 and len(p.stdout) <= MAX_STDOUT and
                len(p.stderr) <= MAX_STDERR and
                b"R2712_NATIVE_LINEAGE_ERROR=" not in p.stderr,
                "r2730_original_cpp_selected_probe_execution_failed")
        csvfile = Path(str(prefix) + "_domain_adaptation.csv")
        require(csvfile.is_file() and
                0 < csvfile.stat().st_size <= MAX_CSV_BYTES and
                csvfile.read_bytes() == original,
                "r2730_dedicated_original_cpp_observer_changed_native_csv")
        events = read_actual_adapter_events(p.stderr, "eistute")
        earlier = (104, 72) if role == "original" else (112, 80)
        require((len(events),
                 len({(e["adaptive_step"], e["retry_index"],
                       e["patch_index"], e["local_attempt"])
                      for e in events})) == earlier,
                "r2730_original_cpp_adapter_closure_changed")
        gate = parse_original_gate_stderr(p.stderr)
        marker = re.findall(
            rb"^real_generator_outcomes=1 accepted_tri=(\d+) restored_tri=(\d+)",
            p.stdout, re.M)
        require(len(marker) == 1 and
                tuple(map(int, marker[0])) == (1, 3),
                "r2730_original_cpp_global_commit_count_changed")
        files = list(lineage.glob("*.ndjson"))
        require(len(files) == 1 and
                0 < files[0].stat().st_size <= MAX_SIDECAR_BYTES,
                "r2730_original_cpp_postcommit_source_faces_missing")
        sidecar = files[0].read_bytes()
        receipt = validate_lineage_records(
            decode_ndjson(sidecar), "eistute")
        receipt["sha256"] = _sha(sidecar)
        require(receipt["sha256"] ==
                _expected_accepted_sha(reference, role),
                "r2730_selected_cpp_probe_original_accepted_tri_changed")
        certify_same_run_outcomes(gate, [receipt], 1, 3)
        selected = join_selected_local_to_native_csv(p.stdout, original, role)
        (folder / "original-selection-stdout.log").write_bytes(p.stdout)
        (folder / "original-generator-stderr.log").write_bytes(p.stderr)
        (folder / "original-adapter-domain-adaptation.csv").write_bytes(original)
        (folder / "accepted_step_1_retry_0.ndjson").write_bytes(sidecar)
        report = {
            "schema": SCHEMA, "role": role,
            "standalone_original_engine_cpp_observer_executable_sha256":
                sha256_file(selection_exe),
            "original_article_config_sha256":
                reference["original_config_sha256"],
            "model_input_sha256": reference["real_input_sha256"],
            "intention_config_sha256": _sha(intent),
            "resolved_io_config_sha256": _sha(resolved),
            "stdout_sha256": _sha(p.stdout),
            "stderr_sha256": _sha(p.stderr),
            "source_adapter_csv_sha256": _sha(original),
            "genuine_source_accepted_face_sha256": _sha(sidecar),
            "selected_observer_result": selected,
            "true_original_cpp_accepted_step": [1],
            "original_cpp_restored_steps": 3,
            "scientific_lod_qualified": False,
        }
        (folder / "observation-report.json").write_text(
            json.dumps(report, sort_keys=True, indent=2,
                       allow_nan=False) + "\n", encoding="utf-8")
        return report


def capture(root: Path, original_exe: Path, selection_exe: Path,
            original: Path, trials: Path, r2728_dir: Path, output: Path,
            timeout: int = 300) -> dict:
    """Original and trial are distinct serial research processes."""
    root, original_exe, selection_exe = (
        root.resolve(), original_exe.resolve(), selection_exe.resolve())
    require(not output.exists() and selection_exe != original_exe and
            selection_exe.is_file() and 10 <= timeout <= 600,
            "r2730_no_distinct_native_probe_or_unsafe_output_directory")
    attestation = attest_original_selection_source(root)
    reference = _reference(root, original_exe, original, trials)
    output.mkdir(parents=True)
    results = [_run_one(root, selection_exe, reference,
                        output / role, role, r2728_dir, timeout)
               for role in ROLES]
    index = {
        "schema": SCHEMA, "source_attestation": attestation,
        "original_engine_executable_sha256":
            reference["native_executable_sha256"],
        "separate_selection_observer_executable_sha256":
            sha256_file(selection_exe),
        "separate_cpp_process_roles": list(ROLES),
        "each_process_genuinely_accepted_only_step1": True,
        "original_generator_and_acceptance_policy_unchanged": True,
        "scientific_lod_qualified": False,
    }
    (output / "index.json").write_text(
        json.dumps(index, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    print("R2730_NATIVE_ORIGINAL_SELECTED_LOCAL_CAPTURE=" + json.dumps({
        role: {"adapter_returns":
               result["selected_observer_result"][
                   "original_cpp_selected_adapter_returns"],
               "step4_selected":
               result["selected_observer_result"][
                   "original_cpp_selected_adapter_returns_at_step4"],
               "accepted_original_cpp": [1]}
        for role, result in zip(ROLES, results)
    }, sort_keys=True))
    return index


def audit(root: Path, original_exe: Path, selection_exe: Path,
          original: Path, trials: Path, r2728_dir: Path,
          r2728_report: Path, directory: Path) -> dict:
    """Re-open raw C++ event stream, original TRI and CSV with source pins."""
    root = root.resolve()
    attested = attest_original_selection_source(root)
    ref = _reference(root, original_exe.resolve(), original, trials)
    prior = audit_r2728(
        root, original_exe.resolve(), original, trials, r2728_dir)
    old = json.loads(r2728_report.read_text(encoding="utf-8"))
    require(prior == old,
            "r2730_previous_original_cpp_adapter_csv_audit_not_reproduced")
    index = json.loads((directory / "index.json").read_text(encoding="utf-8"))
    require(index == {
        "schema": SCHEMA,
        "source_attestation": attested,
        "original_engine_executable_sha256":
            ref["native_executable_sha256"],
        "separate_selection_observer_executable_sha256":
            sha256_file(selection_exe),
        "separate_cpp_process_roles": list(ROLES),
        "each_process_genuinely_accepted_only_step1": True,
        "original_generator_and_acceptance_policy_unchanged": True,
        "scientific_lod_qualified": False,
    }, "r2730_original_cpp_selection_index_or_executable_forged")
    models = {}
    for role in ROLES:
        folder = directory / role
        require(set(p.name for p in folder.iterdir()) == {
            "original-intent.conf", "resolved-execution.conf",
            "original-selection-stdout.log", "original-generator-stderr.log",
            "original-adapter-domain-adaptation.csv",
            "accepted_step_1_retry_0.ndjson", "observation-report.json",
        }, "r2730_original_cpp_selected_probe_missing_original_raw_files")
        intent = (ref["article_bytes"] if role == "original"
                  else ref["variant_bytes"])
        raw_intent = (folder / "original-intent.conf").read_bytes()
        raw_config = (folder / "resolved-execution.conf").read_bytes()
        require(raw_intent == intent and
                b"OUTPUT_PREFIX=" in raw_config,
                "r2730_original_source_config_intention_changed")
        m = re.search(rb"^OUTPUT_PREFIX=(.+)$", raw_config, re.M)
        require(m is not None and raw_config ==
                resolve_isolated_config(
                    intent.decode("utf-8"), ref["model_path"],
                    Path(m.group(1).decode("utf-8").strip())).encode("utf-8"),
                "r2730_original_cpp_execution_config_not_io_only")
        stdout = (folder / "original-selection-stdout.log").read_bytes()
        stderr = (folder / "original-generator-stderr.log").read_bytes()
        raw_csv = (folder / "original-adapter-domain-adaptation.csv").read_bytes()
        source_csv = (r2728_dir / role /
                      "original-adapter-domain-adaptation.csv").read_bytes()
        require(raw_csv == source_csv and
                _sha(raw_csv) ==
                prior["observations"][role]["native_adapter_csv_sha256"],
                "r2730_selected_original_native_csv_drifted")
        events = read_actual_adapter_events(stderr, "eistute")
        require(
            len(events) == (104 if role == "original" else 112),
            "r2730_selected_original_cpp_boundary_count_changed")
        gates = parse_original_gate_stderr(stderr)
        sidecar = (folder / "accepted_step_1_retry_0.ndjson").read_bytes()
        rec = validate_lineage_records(decode_ndjson(sidecar), "eistute")
        rec["sha256"] = _sha(sidecar)
        require(rec["sha256"] == _expected_accepted_sha(ref, role),
                "r2730_original_cpp_accepted_tri_sha_changed")
        certify_same_run_outcomes(gates, [rec], 1, 3)
        selected = join_selected_local_to_native_csv(stdout, raw_csv, role)
        stored = json.loads((folder / "observation-report.json").read_text(
            encoding="utf-8"))
        require(stored == {
            "schema": SCHEMA, "role": role,
            "standalone_original_engine_cpp_observer_executable_sha256":
                sha256_file(selection_exe),
            "original_article_config_sha256":
                ref["original_config_sha256"],
            "model_input_sha256": ref["real_input_sha256"],
            "intention_config_sha256": _sha(intent),
            "resolved_io_config_sha256": _sha(raw_config),
            "stdout_sha256": _sha(stdout),
            "stderr_sha256": _sha(stderr),
            "source_adapter_csv_sha256": _sha(raw_csv),
            "genuine_source_accepted_face_sha256": _sha(sidecar),
            "selected_observer_result": selected,
            "true_original_cpp_accepted_step": [1],
            "original_cpp_restored_steps": 3,
            "scientific_lod_qualified": False,
        }, "r2730_original_cpp_selection_report_not_independently_reproduced")
        step4 = [
            e for e in selected["selected_local_returns"]
            if e["step"] == 4]
        models[role] = {
            "native_source_cpp_selected_csv_sha256": _sha(raw_csv),
            "selected_source_native_adapter_returns":
                selected["original_cpp_selected_adapter_returns"],
            "selected_step4_source_native_adapter_returns": len(step4),
            "selected_step4_local_attempt_indices":
                [r["original_selected_local_attempt"] for r in step4],
            "selected_step4_all_are_original_underresolved":
                all(e["transition_underresolved"] for e in step4),
            "selected_step4_aft_transition_ratio_mean":
                sum(r["aft_stage1_transition_ratio"] for r in step4) /
                len(step4),
            "selected_step4_regional_transition_ratio_mean":
                sum(r["regional_spatial_or_shape_ratio"] for r in step4) /
                len(step4),
            "selected_step4_by_patch": {
                str(p): [r for r in step4 if r["patch"] == p]
                for p in range(4)},
            "genuine_original_cpp_postcommit_sha256": _sha(sidecar),
            "actual_original_cpp_accepted_steps": [1],
            "real_global_rejected_restored_steps": 3,
            "not_two_same_cpp_process_accepted_epochs": True,
        }
    return {
        "schema": SCHEMA,
        "exact_original_cpp_and_preregistration_attested": attested,
        "independent_prior_cpp_replay_audit_reproduced": True,
        "new_cpp_probe_is_separate_from_certified_original_executable": True,
        "original_adapter_final_local_selection_hook_used": True,
        "two_original_eistute_cpp_processes_not_pooled": True,
        "two_processes": models,
        "global_original_cpp_acceptance_policy_unchanged": True,
        "second_same_run_accepted_tri_epoch": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("capture", "audit"), required=True)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--original-exe", type=Path, required=True)
    p.add_argument("--selection-exe", type=Path, required=True)
    p.add_argument("--original-directory", type=Path, required=True)
    p.add_argument("--r2726-trials", type=Path, required=True)
    p.add_argument("--r2728-directory", type=Path, required=True)
    p.add_argument("--r2728-report", type=Path)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--report", type=Path)
    p.add_argument("--timeout", type=int, default=300)
    a = p.parse_args()
    if a.mode == "capture":
        capture(a.root, a.original_exe, a.selection_exe,
                a.original_directory, a.r2726_trials,
                a.r2728_directory, a.output_dir, a.timeout)
        return
    require(a.r2728_report is not None and a.report is not None and
            not a.report.exists(),
            "r2730_original_native_source_audit_report_must_be_new")
    result = audit(
        a.root, a.original_exe, a.selection_exe,
        a.original_directory, a.r2726_trials, a.r2728_directory,
        a.r2728_report, a.output_dir)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(
        json.dumps(result, indent=2, sort_keys=True,
                   allow_nan=False) + "\n", encoding="utf-8")
    print("R2730_NATIVE_ORIGINAL_ADAPTER_LOCAL_SELECTED_AUDIT=" + json.dumps({
        role: {
            "selected_step4": item[
                "selected_step4_source_native_adapter_returns"],
            "all_selected_step4_underresolved": item[
                "selected_step4_all_are_original_underresolved"],
            "genuine_source_accepted_steps": [1],
            "scientific_lod_qualified": False,
        } for role, item in result["two_processes"].items()
    }, sort_keys=True))


if __name__ == "__main__":
    main()
