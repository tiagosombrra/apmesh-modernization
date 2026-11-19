"""R2.7.32 read-only source-native PRE-AFT UV capture admissibility audit.

Real captures describe selected local Quadtree inputs, never generated TRI.
No source scientific generator, numerical policy or CAD geometry is changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from .native_controlled_sensitivity import git_blob
from .native_local_selection_provenance import (
    SCHEMA as PRIOR_SCHEMA,
    EVENT_PATTERN,
    attest_original_selection_source,
    join_selected_local_to_native_csv,
    parse_native_local_selection,
)
from .verify_native_lineage import require

SCHEMA = "apmesh.meshstudio.r2732.source_selected_local_pre_aft_uv_observability.v1"
REGISTRATION_PATH = (
    "docs/mesh-studio/"
    "R2_7_32_PREREGISTERED_SELECTED_LOCAL_PREAFT_UV_GEOMETRY_20261119.md"
)
REGISTRATION_BLOB = "4e716e3333e50beeb2c4755a00af44ddf618d9e3"
PROBE_PATH = "tests/quad/generator_selected_uv_probe.cpp"
PROBE_BLOB = "eda1d37a7ca7fdbe70422de196bd88398e37c797"
ROLES = ("original", "variant")
MAX_STDOUT = 3_000_000
MAX_REPORT = 3_000_000
MAX_SIDECAR = 30_000_000

UV_PREFIX = b"R2732_UV_CAPTURE="
NUMERIC_FIELDS = (
    "ordinal", "outer_epoch", "outer_retry", "step", "retry", "patch", "local",
    "leaves", "excluded", "vertices", "polygons",
)
FLOAT_FIELDS = ("area", "u_min", "v_min", "u_max", "v_max")
SOURCE_KEYS = (
    "outer_epoch", "outer_retry", "step", "retry", "patch", "local",
)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read(path: Path, maximum: int) -> bytes:
    require(path.is_file() and 0 < path.stat().st_size <= maximum,
            "r2732_original_native_evidence_missing_or_unbounded")
    return path.read_bytes()


def attest_source(root: Path) -> dict:
    """Check prior original C++ source and the distinct preregistered observer."""
    prior = attest_original_selection_source(root)
    for path, expected in (
        (REGISTRATION_PATH, REGISTRATION_BLOB),
        (PROBE_PATH, PROBE_BLOB),
    ):
        raw = _read(root / path, 100_000)
        require(git_blob(raw) == expected,
                "r2732_original_registered_uv_observer_or_protocol_drifted")
        prior[path] = {"git_blob": expected, "sha256": _sha(raw)}
    original = _read(
        root / "tests/quad/generator_local_selection_probe.cpp", 100_000)
    observer = _read(root / PROBE_PATH, 100_000)
    require(original != observer and
            b"R2732_UV_CAPTURE=ordinal=" in observer and
            b"CaptureLeafPolygons(tree)" in observer and
            b"R2730_LOCAL_SELECTION=ordinal=" in observer and
            b"return best.sub_mesh.release();" in
            (root / "src/adapter/adapter.cpp").read_bytes(),
            "r2732_pre_aft_observer_is_not_distinct_and_read_only")
    return prior


def parse_original_native_uv_captures(stdout: bytes) -> list[dict]:
    """Accept only bounded original Chromium-independent C++ UV records."""
    require(0 < len(stdout) <= MAX_STDOUT and UV_PREFIX in stdout,
            "r2732_original_cpp_uv_capture_stream_missing")
    captures = []
    for line in stdout.splitlines():
        if not line.startswith(UV_PREFIX):
            continue
        raw_fields = line[len(UV_PREFIX):].split(b",")
        require(len(raw_fields) == 23,
                "r2732_native_uv_summary_field_count_invalid")
        pairs = []
        for field in raw_fields:
            require(field.count(b"=") == 1,
                    "r2732_native_uv_field_invalid")
            key, raw = field.split(b"=", 1)
            try:
                pairs.append((key.decode("ascii"), raw.decode("ascii")))
            except UnicodeDecodeError as exc:
                raise ValueError("r2732_nonascii_original_uv_field") from exc
        fields = {}
        patterns = []
        for key, raw in pairs:
            if key == "pattern":
                try:
                    patterns.append(int(raw))
                except ValueError as exc:
                    raise ValueError("r2732_invalid_uv_pattern_integer") from exc
            else:
                require(key not in fields, "r2732_duplicate_original_uv_field")
                fields[key] = raw
        require(set(fields) == set(NUMERIC_FIELDS) | set(FLOAT_FIELDS) |
                {"status"} and len(patterns) == 6,
                "r2732_original_uv_field_schema_drifted")
        try:
            row = {key: int(fields[key]) for key in NUMERIC_FIELDS}
            row.update({key: float(fields[key]) for key in FLOAT_FIELDS})
        except (ValueError, OverflowError) as exc:
            raise ValueError("r2732_native_uv_numeric_field_corrupt") from exc
        row["status"] = fields["status"]
        row["patterns"] = patterns
        require(row["ordinal"] == len(captures) + 1 and
                row["outer_epoch"] > 0 and row["outer_retry"] in (0, 1) and
                1 <= row["step"] <= 4 and row["retry"] in (0, 1) and
                row["patch"] in range(4) and row["local"] in range(4) and
                row["leaves"] > 0 and row["leaves"] <= 1_000_000 and
                row["excluded"] <= row["leaves"] and
                row["vertices"] >= 0 and row["polygons"] >= 0 and
                all(p >= 0 for p in patterns) and
                all(math.isfinite(row[f]) for f in FLOAT_FIELDS),
                "r2732_nonfinite_or_out_of_scope_pre_aft_uv_capture")
        if row["status"] == "qualified":
            require(row["vertices"] >= 3 and row["polygons"] >= 1 and
                    sum(patterns) == row["polygons"] and
                    row["area"] > 0 and
                    0 <= row["u_min"] <= row["u_max"] <= 1 and
                    0 <= row["v_min"] <= row["v_max"] <= 1,
                    "r2732_original_source_tree_geometry_not_qualified")
        elif row["status"] == "unsupported":
            require(row["vertices"] == 0 and row["polygons"] == 0 and
                    row["excluded"] == 0 and row["area"] == 0 and
                    all(row[f] == 0 for f in FLOAT_FIELDS if f != "area") and
                    sum(patterns) == 0,
                    "r2732_unsupported_original_quadtree_must_not_claim_geometry")
        else:
            require(False, "r2732_original_pre_aft_observer_status_unknown")
        captures.append(row)
    require(len(captures) in (104, 112),
            "r2732_original_pre_aft_capture_multiplicity_not_certified")
    return captures


def correlate_original_selected_pre_aft_uv(stdout: bytes, raw_csv: bytes,
                                            role: str) -> dict:
    """Join one source Quadtree capture per original local C++ attempt by ordinal."""
    require(role in ROLES, "r2732_original_source_process_role_unknown")
    captured = parse_original_native_uv_captures(stdout)
    original_events = parse_native_local_selection(stdout)
    prior = join_selected_local_to_native_csv(stdout, raw_csv, role)
    expected = 104 if role == "original" else 112
    require(len(captured) == len(original_events) ==
            prior["original_cpp_all_local_event_rows"] == expected,
            "r2732_original_uv_capture_not_one_to_one_with_native_cpp_attempts")
    for observed, event in zip(captured, original_events, strict=True):
        match = EVENT_PATTERN.fullmatch(
            next(line for line in stdout.splitlines()
                 if line.startswith(b"R2730_LOCAL_SELECTION=ordinal=" +
                                    str(event["ordinal"]).encode() + b",")))
        require(match is not None, "r2732_invalid_original_local_event_order")
        outer_retry = int(match.group(4))
        require(all(observed[k] == event[k] for k in
                    ("ordinal", "outer_epoch", "step", "retry",
                     "patch", "local")) and
                observed["outer_retry"] == outer_retry,
                "r2732_pre_aft_uv_observation_wrong_original_local_candidate")
    selections = [captured[i] for i, event in
                  enumerate(original_events) if event["kind"] == "selected"]
    chosen = prior["selected_local_returns"]
    require(len(selections) == len(chosen) == 40,
            "r2732_original_cpp_selected_pre_aft_uv_count_changed")
    for row, selected in zip(selections, chosen, strict=True):
        require(all(row[k] == selected[k] for k in
                    ("outer_epoch", "step", "retry", "patch")) and
                row["local"] == selected["original_selected_local_attempt"],
                "r2732_original_pre_aft_capture_did_not_match_selected_return")
    step4 = [r for r in selections if r["step"] == 4]
    require(len(step4) == 16 and
            all(sum(row["patch"] == p for row in step4) == 4
                for p in range(4)),
            "r2732_selected_pre_aft_per_original_patch_scope_incomplete")
    return {
        "original_cpp_all_local_attempts": expected,
        "original_cpp_distinct_selected_adapter_invocations": 40,
        "selected_local_pre_aft_uv_step4": 16,
        "pre_aft_uv_supported_all_attempts":
            sum(r["status"] == "qualified" for r in captured),
        "pre_aft_uv_unsupported_all_attempts":
            sum(r["status"] == "unsupported" for r in captured),
        "pre_aft_uv_qualified_selected_step4":
            sum(r["status"] == "qualified" for r in step4),
        "pre_aft_uv_unsupported_selected_step4":
            sum(r["status"] == "unsupported" for r in step4),
        "original_source_per_patch_selected_pre_aft": {
            str(p): [r for r in step4 if r["patch"] == p] for p in range(4)
        },
        "selected_pre_aft_uv_capture_row_statuses": step4,
        "original_accepted_tri_step1_cannot_be_used_as_step4_local_tri": True,
        "capture_is_pre_aft_uv_not_post_aft_selected_tri": True,
        "selected_source_tri_face_geometry_observed": False,
        "physical_shared_curve_welding_observed": False,
        "scientific_lod_qualified": False,
    }


def audit(root: Path, captures: Path, prior_report: Path) -> dict:
    """Reopen two actual original serial process copies and prior source audit."""
    sources = attest_source(root)
    raw_prior = _read(prior_report, MAX_REPORT)
    earlier = json.loads(raw_prior)
    require(earlier.get("schema") == PRIOR_SCHEMA and
            earlier.get("scientific_lod_qualified") is False and
            earlier.get("second_same_run_accepted_tri_epoch") is False and
            set(earlier.get("two_processes", {})) == set(ROLES),
            "r2732_prior_original_cpp_independent_selection_audit_invalid")
    results = {}
    for role in ROLES:
        folder = captures / role
        stdout = _read(folder / "original-selection-stdout.log", MAX_STDOUT)
        csv = _read(folder / "original-adapter-domain-adaptation.csv", 2_000_000)
        faces = _read(folder / "accepted_step_1_retry_0.ndjson", MAX_SIDECAR)
        observation = json.loads(_read(
            folder / "observation-report.json", MAX_REPORT))
        selected = correlate_original_selected_pre_aft_uv(stdout, csv, role)
        prev = earlier["two_processes"][role]
        require(observation.get("stdout_sha256") == _sha(stdout) and
                observation.get("source_adapter_csv_sha256") == _sha(csv) and
                observation.get("genuine_source_accepted_face_sha256") ==
                _sha(faces) and
                prev["native_source_cpp_selected_csv_sha256"] == _sha(csv) and
                prev["genuine_original_cpp_postcommit_sha256"] == _sha(faces) and
                prev["actual_original_cpp_accepted_steps"] == [1] and
                prev["real_global_rejected_restored_steps"] == 3 and
                prev["selected_step4_source_native_adapter_returns"] == 16 and
                prev["not_two_same_cpp_process_accepted_epochs"] is True,
                "r2732_original_native_accepted_source_or_csv_drifted")
        results[role] = {
            "original_cpp_selection_and_uv_stdout_sha256": _sha(stdout),
            "original_source_adapter_csv_sha256": _sha(csv),
            "genuine_accepted_step1_tri_sha256": _sha(faces),
            "observed_pre_aft_uv": selected,
        }
    return {
        "schema": SCHEMA,
        "registered_protocol_git_blob": REGISTRATION_BLOB,
        "source_original_cpp_blob_attestation": sources,
        "prior_same_run_cpp_selection_audit_sha256": _sha(raw_prior),
        "real_original_and_min13_cpp_processes_not_pooled": True,
        "two_separate_real_cpp_processes": results,
        "observed_selected_local_pre_aft_uv_only": True,
        "selected_post_aft_tri_xyz_uv_not_observed": True,
        "global_cpp_original_source_accepted_steps_per_process": [1],
        "scientific_lod_qualified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--prior-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "r2732_source_audit_report_must_be_new")
    result = audit(args.root, args.capture_dir, args.prior_report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(
        result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8")
    print("R2732_NATIVE_SELECTED_PREAFT_UV_OBSERVABILITY=" +
          json.dumps({
              role: {
                  "selected_step4_uv_qualified": result[
                      "two_separate_real_cpp_processes"][role][
                      "observed_pre_aft_uv"]["pre_aft_uv_qualified_selected_step4"],
                  "selected_step4_uv_unsupported": result[
                      "two_separate_real_cpp_processes"][role][
                      "observed_pre_aft_uv"]["pre_aft_uv_unsupported_selected_step4"],
                  "selected_post_aft_tri_qualified": False,
                  "original_global_accepted_steps": [1],
              } for role in ROLES
          }, sort_keys=True))


if __name__ == "__main__":
    main()
