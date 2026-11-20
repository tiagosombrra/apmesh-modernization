"""R2.7.33: evidence-only original Adapter-selected TRI from a Linux ELF wrapper.

Each local Adapter return remains provisional; no rejected outer candidate is
promoted into an accepted TRI epoch. Revalidate original C++ CSV and source
accepted-sidecar bytes independently of the wrapper's sidecar claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory

from .native_acceptance_gate_forensics import parse_original_gate_stderr
from .native_controlled_sensitivity import (
    certify_same_run_outcomes, git_blob, resolve_isolated_config,
)
from .native_lineage_parity import (
    compare_exact_scientific_inventories, output_inventory,
)
from .native_local_selection_provenance import (
    attest_original_selection_source, join_selected_local_to_native_csv,
)
from .native_patch_csv_replay import _expected_accepted_sha, _reference
from .verify_native_lineage import (
    decode_ndjson, require, sha256_file, validate_lineage_records,
)

SCHEMA = "apmesh.meshstudio.r2733.source_selected_post_aft_tri_wrapper.v1"
PROTOCOL = (
    "docs/mesh-studio/"
    "R2_7_33_PREREGISTERED_ORIGINAL_SELECTED_POST_AFT_TRI_WRAPPER_20261119.md"
)
PROTOCOL_BLOB = "44184636157167e5a09548d65e4ab3d18efe3758"
PROBE = "tests/quad/generator_selected_tri_return_probe.cpp"
PROBE_BLOB = "13c0095c852273f1126791c896faa94ad60295d2"
ROLES = ("original", "variant")
EVENT = re.compile(
    rb"^R2733_TRI_RETURN=return_index=(\d+),outer_epoch=(\d+),"
    rb"outer_retry=(\d+),step=(\d+),retry=(\d+),patch=(\d+),"
    rb"local=(\d+),faces=(\d+),nodes=(\d+),"
    rb"file=(none|adapter_return_\d+\.ndjson)$",
    re.MULTILINE,
)
MAX_STDOUT = 3_000_000
MAX_STDERR = 12_000_000
MAX_SELECTED_FACES = 120_000
MAX_SELECTED_NODES = 240_000
MAX_TRI_BYTES = 80_000_000


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read(path: Path, bound: int) -> bytes:
    require(path.is_file() and not path.is_symlink() and
            0 < path.stat().st_size <= bound,
            "r2733_missing_or_oversized_source_native_research_file")
    return path.read_bytes()


def attest(root: Path) -> dict:
    """Refuse any change to previously certified original numerical C++ code."""
    attested = attest_original_selection_source(root)
    for name, expected in ((PROTOCOL, PROTOCOL_BLOB), (PROBE, PROBE_BLOB)):
        require(len(expected) == 40 and
                git_blob(_read(root / name, 100_000)) == expected,
                "r2733_cpp_wrapper_or_frozen_protocol_source_drifted")
        attested[name] = {"git_blob": expected}
    observer = _read(root / PROBE, 100_000)
    cmake = _read(root / "CMakeLists.txt", 100_000)
    require(
        b"__real__ZN7Adapter11AdaptDomainEP10PatchCoonsPN9Performer9IdManagerEddiiii" in observer
        and b"__wrap__ZN7Adapter11AdaptDomainEP10PatchCoonsPN9Performer9IdManagerEddiiii" in observer
        and b"R2733_TRI_RETURN=return_index=" in observer
        and b"target_link_options(quad_generator_selected_tri_return_probe" in cmake
        and b"LINKER:--wrap=_ZN7Adapter11AdaptDomainEP10PatchCoonsPN9Performer9IdManagerEddiiii" in cmake
        and observer != _read(
            root / "tests/quad/generator_local_selection_probe.cpp", 100_000),
        "r2733_original_adapter_elf_link_wrapper_not_source_attested",
    )
    return attested


def parse_real_adapter_returns(stdout: bytes) -> list[dict]:
    """Parse only original ABI-wrapper return records, never inferred choices."""
    require(0 < len(stdout) <= MAX_STDOUT and
            b"R2733_TRI_RETURN=" in stdout and
            b"R2733_TRI_OBSERVER_ERROR=" not in stdout,
            "r2733_original_adapter_return_stream_missing")
    parsed = []
    for match in EVENT.finditer(stdout):
        ordinal, epoch, outer_retry, step, retry, patch, local, faces, nodes = (
            int(x) for x in match.groups()[:9])
        file_name = match.group(10).decode("ascii")
        require(ordinal == len(parsed) + 1 and epoch > 0 and
                outer_retry in (0, 1) and 1 <= step <= 4 and
                retry in (0, 1) and 0 <= patch < 4 and
                0 <= local <= 3 and 0 < faces <= MAX_SELECTED_FACES and
                0 < nodes <= MAX_SELECTED_NODES and
                (file_name == "none") == (step != 4) and
                (file_name == "none" or
                 file_name == f"adapter_return_{ordinal}.ndjson"),
                "r2733_source_return_scope_count_or_file_invalid")
        parsed.append({
            "return_index": ordinal,
            "outer_epoch": epoch, "outer_retry": outer_retry,
            "step": step, "retry": retry, "patch": patch, "local": local,
            "faces": faces, "nodes": nodes, "file": file_name,
        })
    require(len(parsed) == 40 and
            len([x for x in parsed if x["step"] == 4]) == 16 and
            len(stdout.split(b"R2733_TRI_RETURN=")) == 41,
            "r2733_original_adapter_return_multiplicity_or_malformed_event")
    return parsed


def parse_original_tri_bytes(raw: bytes, expected: dict) -> dict:
    """Reopen all real selected SubMesh TRI faces and count native identities."""
    require(0 < len(raw) <= MAX_TRI_BYTES and
            raw.endswith(b"\n") and b"\r" not in raw and b"\x00" not in raw,
            "r2733_original_native_selected_tri_file_not_canonical")
    rows = [json.loads(line) for line in raw.splitlines()]
    require(len(rows) >= 3 and rows[0].get("type") ==
            "source_selected_adapter_return" and
            rows[-1].get("type") == "complete",
            "r2733_source_selected_tri_header_or_trailer_missing")
    head = rows[0]
    require(
        head.get("return_index") == expected["return_index"] and
        head.get("step") == expected["step"] == 4 and
        head.get("retry") == expected["retry"] and
        head.get("patch") == expected["patch"] and
        head.get("local") == expected["local"] and
        head.get("outer_epoch") == expected["outer_epoch"] and
        head.get("outer_retry") == expected["outer_retry"] and
        head.get("session") == 6306001 and
        head.get("face_count") == expected["faces"] and
        head.get("node_count") == expected["nodes"] and
        head.get("provisional_post_aft_selected_local_not_global_commit") is True and
        type(head.get("native_source_patch_id")) is int,
        "r2733_original_selected_native_tri_header_identity_invalid")
    curves = head.get("source_curves")
    require(type(curves) is list and len(curves) == 4 and all(
        type(c) is dict and c.get("edge_slot") == i and
        type(c.get("native_curve_id")) is int and
        type(c.get("reversed")) is bool and
        type(c.get("source_curve_points")) is int and
        2 <= c["source_curve_points"] <= 200_000
        for i, c in enumerate(curves)),
        "r2733_actual_original_source_patch_curve_incidence_invalid")
    faces = rows[1:-1]
    require(len(faces) == expected["faces"] and rows[-1] == {
        "type": "complete", "face_records": expected["faces"],
        "not_global_accepted_step": True},
        "r2733_original_selected_cpp_tri_faces_incomplete")
    element_ids = set()
    node_xyz = {}
    uv_edges = {}
    for slot, face in enumerate(faces):
        require(type(face) is dict and face.get("type") == "face" and
                face.get("element_slot") == slot and
                type(face.get("native_element_id")) is int and
                type(face.get("vertices")) is list and
                len(face["vertices"]) == 3,
                "r2733_source_face_local_slot_or_type_invalid")
        native_id = face["native_element_id"]
        require(native_id not in element_ids,
                "r2733_duplicate_native_selected_tri_element_id")
        element_ids.add(native_id)
        corners = []
        for corner in face["vertices"]:
            require(type(corner) is dict and
                    type(corner.get("native_node_id")) is int and
                    type(corner.get("xyz")) is list and
                    type(corner.get("uv")) is list and
                    len(corner["xyz"]) == 3 and
                    len(corner["uv"]) == 2,
                    "r2733_source_face_corner_not_native_node_uv_xyz")
            coords = corner["xyz"]
            uv = corner["uv"]
            require(all(type(value) in (float, int) and math.isfinite(value)
                        for value in (*coords, *uv)) and
                    -1e-6 <= uv[0] <= 1 + 1e-6 and
                    -1e-6 <= uv[1] <= 1 + 1e-6,
                    "r2733_nonfinite_or_outside_original_patch_uv")
            node_id = corner["native_node_id"]
            xyz = tuple(coords)
            if node_id in node_xyz:
                require(node_xyz[node_id] == xyz,
                        "r2733_original_native_node_id_coordinate_conflict")
            node_xyz[node_id] = xyz
            corners.append(node_id)
        require(len(set(corners)) == 3,
                "r2733_original_selected_tri_degenerate_repeated_node_id")
        for j in range(3):
            a, b = corners[j], corners[(j + 1) % 3]
            edge = tuple(sorted((a, b)))
            uv_edges[edge] = uv_edges.get(edge, 0) + 1
            require(uv_edges[edge] <= 2,
                    "r2733_nonmanifold_or_duplicate_local_tri_edge")
    require(len(node_xyz) <= expected["nodes"] and
            len(node_xyz) >= 3,
            "r2733_source_selected_native_node_count_inconsistent")
    # This is a *local* UV edge incidence check, not shared-patch welding.
    return {
        "face_records": len(faces),
        "distinct_native_element_ids": len(element_ids),
        "distinct_referenced_native_node_ids": len(node_xyz),
        "source_patch_native_id": head["native_source_patch_id"],
        "source_curve_incidence": curves,
        "local_uv_edges_with_two_faces": sum(v == 2 for v in uv_edges.values()),
        "local_uv_edges_with_one_face": sum(v == 1 for v in uv_edges.values()),
        "triangulation_scope": "actual_selected_post_aft_adapter_return_not_global_commit",
        "cross_patch_physical_node_welding_qualified": False,
        "scientific_lod_qualified": False,
    }


def inspect_selected_tri_stream(stdout: bytes, raw_csv: bytes,
                                tri_files: dict[str, bytes], role: str) -> dict:
    """Certify original callback selections bind 1:1 to ABI-wrapped returns."""
    selected = join_selected_local_to_native_csv(stdout, raw_csv, role)[
        "selected_local_returns"]
    returns = parse_real_adapter_returns(stdout)
    require(len(selected) == len(returns) == 40,
            "r2733_real_source_cpp_return_join_count_invalid")
    actual = {}
    for row, returned in zip(selected, returns, strict=True):
        require(
            row["adapter_return_index"] + 1 == returned["return_index"] and
            all(row[key] == returned[key] for key in
                ("outer_epoch", "step", "retry", "patch")) and
            row["original_selected_local_attempt"] == returned["local"] and
            row["generated_faces"] == returned["faces"] and
            row["local_selected_is_not_global_accepted_tri"] is True,
            "r2733_actual_original_adapter_pointer_not_selected_source_return")
        if returned["step"] == 4:
            name = returned["file"]
            require(name in tri_files,
                    "r2733_real_cpp_selected_native_tri_file_missing")
            actual[name] = {
                "sha256": _sha(tri_files[name]),
                "size": len(tri_files[name]),
                "original_selected_return_index": returned["return_index"],
                "source_native_tri": parse_original_tri_bytes(
                    tri_files[name], returned),
            }
    require(set(actual) == set(tri_files) and len(actual) == 16,
            "r2733_extra_missing_or_unselected_native_tri_artifacts")
    return {
        "original_adapter_returns": 40,
        "true_selected_post_aft_tri_adapter_returns_step4": 16,
        "retained_real_selected_native_tri": actual,
        "original_source_selected_returns_are_provisional": True,
        "native_global_second_accepted_step": False,
        "scientific_lod_qualified": False,
    }


def _retain_scientific_outputs(workspace: Path, inventory: dict,
                               destination: Path) -> None:
    """Preserve the raw native numerical outputs for independent byte readback."""
    require(not destination.exists() and 0 < len(inventory) <= 600,
            "r2733_invalid_or_existing_scientific_source_archive")
    destination.mkdir(parents=True)
    for relative in sorted(inventory):
        source = workspace / relative
        original = _read(source, 100_000_000)
        require(len(original) == inventory[relative]["bytes"] and
                _sha(original) == inventory[relative]["sha256"],
                "r2733_original_cpp_scientific_source_changed_while_retaining")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(original)


def _execute(exe: Path, config: Path, root: Path, output_prefix: Path,
             lineage_dir: Path, selected_dir: Path | None,
             timeout: int) -> dict:
    """Re-run actual compiled C++ with the same scientific output prefix."""
    lineage_dir.mkdir()
    if selected_dir is not None:
        selected_dir.mkdir()
    env = dict(os.environ)
    env.update(APMESH_RESEARCH_LINEAGE_DIR=str(lineage_dir),
               APMESH_RESEARCH_ACCEPTANCE_GATES="1",
               APMESH_RESEARCH_EFFECTIVE_BUDGETS="1")
    env.pop("APMESH_R2733_SELECTED_TRI_DIR", None)
    if selected_dir is not None:
        env["APMESH_R2733_SELECTED_TRI_DIR"] = str(selected_dir)
    p = subprocess.run(
        [str(exe), str(config)], cwd=root, env=env, capture_output=True,
        timeout=timeout, check=False)
    require(p.returncode == 0 and 0 < len(p.stdout) <= MAX_STDOUT and
            0 < len(p.stderr) <= MAX_STDERR and
            b"R2712_NATIVE_LINEAGE_ERROR=" not in p.stderr and
            b"R2733_TRI_OBSERVER_ERROR=" not in p.stderr,
            "r2733_real_source_cpp_process_or_selected_tri_observation_failed")
    output_files, excluded = output_inventory(output_prefix.parent)
    lineage = list(lineage_dir.glob("*.ndjson"))
    require(len(lineage) == 1 and
            len(list(lineage_dir.glob("*.pending"))) == 0,
            "r2733_original_cpp_accepted_step1_lineage_missing")
    source = _read(lineage[0], 30_000_000)
    csv = _read(Path(str(output_prefix) + "_domain_adaptation.csv"), 2_000_000)
    return {
        "stdout": p.stdout, "stderr": p.stderr, "csv": csv,
        "accepted_tri": source, "scientific": output_files,
        "excluded": excluded,
    }


def capture(root: Path, original_exe: Path, baseline_exe: Path,
            wrapper_exe: Path, original: Path, trials: Path,
            r2728_dir: Path, out: Path, timeout: int) -> dict:
    """Two independent original configs, each with paired real native runs."""
    root = root.resolve()
    original_exe, baseline_exe, wrapper_exe = (
        original_exe.resolve(), baseline_exe.resolve(), wrapper_exe.resolve())
    require(not out.exists() and 10 <= timeout <= 600 and
            len({original_exe, baseline_exe, wrapper_exe}) == 3 and
            all(x.is_file() for x in
                (original_exe, baseline_exe, wrapper_exe)),
            "r2733_invalid_distinct_original_native_executable_inputs")
    source = attest(root)
    reference = _reference(root, original_exe, original, trials)
    out.mkdir(parents=True)
    receipts = {}
    for role in ROLES:
        role_dir = out / role
        role_dir.mkdir()
        intent = reference["article_bytes"] if role == "original" else reference["variant_bytes"]
        role_csv = _read(r2728_dir / role /
                         "original-adapter-domain-adaptation.csv", 2_000_000)
        with TemporaryDirectory(prefix="r2733-original-adapter-return-") as temp:
            temp_root = Path(temp)
            same = temp_root / "same_exact_original_output_root"
            prefix = same / "original"
            def prepare() -> tuple[Path, Path, Path]:
                same.mkdir(parents=True)
                config = same / "resolved.conf"
                config.write_bytes(resolve_isolated_config(
                    intent.decode("utf-8"), reference["model_path"],
                    prefix).encode("utf-8"))
                return config, same / "source-lineage", same / "selected-native-tri"
            config, lineage, tri = prepare()
            control = _execute(
                baseline_exe, config, root, prefix, lineage, None, timeout)
            require(control["csv"] == role_csv,
                    "r2733_original_unwrapped_adapter_csv_not_prior_source")
            _retain_scientific_outputs(
                same, control["scientific"], role_dir / "scientific_unwrapped")
            config_raw = config.read_bytes()
            shutil.rmtree(same)
            config, lineage, tri = prepare()
            require(config.read_bytes() == config_raw,
                    "r2733_original_cpp_parity_config_path_changed")
            observed = _execute(
                wrapper_exe, config, root, prefix, lineage, tri, timeout)
            require(observed["csv"] == role_csv and
                    observed["accepted_tri"] == control["accepted_tri"],
                    "r2733_original_adapter_wrapper_changed_native_csv_or_commit")
            compared = compare_exact_scientific_inventories(
                control["scientific"], observed["scientific"])
            _retain_scientific_outputs(
                same, observed["scientific"], role_dir / "scientific_wrapped")
            require(len(compared["scientific_file_sha256"]) >= 1,
                    "r2733_missing_native_scientific_parity_files")
            gates = parse_original_gate_stderr(observed["stderr"])
            rec = validate_lineage_records(
                decode_ndjson(observed["accepted_tri"]), "eistute")
            rec["sha256"] = _sha(observed["accepted_tri"])
            require(rec["sha256"] == _expected_accepted_sha(reference, role),
                    "r2733_original_native_accepted_step1_tri_source_changed")
            certify_same_run_outcomes(gates, [rec], 1, 3)
            tri_files = {p.name: _read(p, MAX_TRI_BYTES)
                         for p in sorted(tri.glob("*.ndjson"))}
            require(len(tri_files) == 16 and not list(tri.glob("*.pending")),
                    "r2733_wrong_original_selected_step4_tri_sidecar_count")
            source_selected = inspect_selected_tri_stream(
                observed["stdout"], observed["csv"], tri_files, role)
            # Keep the original native evidence, not reconstructed substitutes.
            (role_dir / "original-wrapper-stdout.log").write_bytes(
                observed["stdout"])
            (role_dir / "original-wrapper-stderr.log").write_bytes(
                observed["stderr"])
            (role_dir / "original-control-stdout.log").write_bytes(
                control["stdout"])
            (role_dir / "original-control-stderr.log").write_bytes(
                control["stderr"])
            (role_dir / "original-adapter-domain-adaptation.csv").write_bytes(
                observed["csv"])
            (role_dir / "accepted_step_1_retry_0.ndjson").write_bytes(
                observed["accepted_tri"])
            (role_dir / "resolved-execution.conf").write_bytes(config_raw)
            (role_dir / "original-intent.conf").write_bytes(intent)
            sidecars = role_dir / "selected_post_aft_tri"
            sidecars.mkdir()
            for name, raw in tri_files.items():
                (sidecars / name).write_bytes(raw)
            receipts[role] = {
                "original_intent_sha256": _sha(intent),
                "resolved_original_io_config_sha256": _sha(config_raw),
                "source_native_cpp_adapter_csv_sha256": _sha(observed["csv"]),
                "accepted_original_step1_source_tri_sha256": _sha(
                    observed["accepted_tri"]),
                "unwrapped_original_cpp_stdout_sha256": _sha(control["stdout"]),
                "unwrapped_original_cpp_stderr_sha256": _sha(control["stderr"]),
                "wrapped_original_cpp_stdout_sha256": _sha(observed["stdout"]),
                "wrapped_original_cpp_stderr_sha256": _sha(observed["stderr"]),
                "real_cpp_scientific_output_parity": compared,
                "source_original_selected_native_tri": source_selected,
                "source_global_accepted_steps": [1],
                "global_rejected_restored": 3,
                "scientific_lod_qualified": False,
            }
    result = {
        "schema": SCHEMA,
        "source_original_attestation": source,
        "source_original_exe_sha256": sha256_file(original_exe),
        "source_unwrapped_probe_sha256": sha256_file(baseline_exe),
        "separate_wrapped_cpp_probe_sha256": sha256_file(wrapper_exe),
        "two_separate_roles_not_cross_epoch": list(ROLES),
        "source_cpp_original_adapter_and_aft_unmodified": True,
        "source_cpp_same_output_path_scientific_parity": True,
        "roles": receipts,
        "scientific_lod_qualified": False,
    }
    (out / "capture-manifest.json").write_text(
        json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8")
    print("R2733_CAPTURE_ORIGINAL_SELECTED_NATIVE_TRI=" + json.dumps({
        role: {
            "selected_post_aft_step4_tri": receipts[role][
                "source_original_selected_native_tri"][
                    "true_selected_post_aft_tri_adapter_returns_step4"],
            "exact_scientific_output_file_parity": receipts[role][
                "real_cpp_scientific_output_parity"]["compared_file_count"],
            "source_accepted_steps": [1], "lod": False}
        for role in ROLES}, sort_keys=True))
    return result


def audit(root: Path, out: Path) -> dict:
    """Independently reopen every archive byte and recalculate result summary."""
    source = attest(root.resolve())
    manifest = json.loads(
        _read(out / "capture-manifest.json", 1_000_000))
    require(manifest["schema"] == SCHEMA and
            manifest["source_original_attestation"] == source and
            manifest["two_separate_roles_not_cross_epoch"] == list(ROLES) and
            manifest["scientific_lod_qualified"] is False,
            "r2733_source_original_capture_index_or_protocol_invalid")
    for role in ROLES:
        folder = out / role
        row = manifest["roles"][role]
        stdout = _read(folder / "original-wrapper-stdout.log", MAX_STDOUT)
        csv = _read(folder / "original-adapter-domain-adaptation.csv", 2_000_000)
        accepted = _read(folder / "accepted_step_1_retry_0.ndjson", 30_000_000)
        tri_dir = folder / "selected_post_aft_tri"
        tri_files = {f.name: _read(f, MAX_TRI_BYTES)
                     for f in sorted(tri_dir.iterdir())}
        result = inspect_selected_tri_stream(stdout, csv, tri_files, role)
        observed_inventory, observed_excluded = output_inventory(
            folder / "scientific_wrapped")
        control_inventory, control_excluded = output_inventory(
            folder / "scientific_unwrapped")
        independently_compared = compare_exact_scientific_inventories(
            control_inventory, observed_inventory)
        require(not observed_excluded and not control_excluded and
                independently_compared ==
                row["real_cpp_scientific_output_parity"],
                "r2733_independent_raw_original_scientific_bytes_not_equal")
        require(result == row["source_original_selected_native_tri"] and
                row["wrapped_original_cpp_stdout_sha256"] == _sha(stdout) and
                row["source_native_cpp_adapter_csv_sha256"] == _sha(csv) and
                row["accepted_original_step1_source_tri_sha256"] ==
                _sha(accepted) and
                row["source_global_accepted_steps"] == [1] and
                row["global_rejected_restored"] == 3 and
                row["scientific_lod_qualified"] is False and
                row["real_cpp_scientific_output_parity"][
                    "scientific_files_exactly_byte_equal"] is True,
                "r2733_source_original_selected_tri_bytes_or_parity_forged")
        require(all(len(_read(folder / n, MAX_STDERR if "stderr" in n else
                               MAX_STDOUT if "stdout" in n else 30_000))
                    > 0 for n in (
                        "original-control-stdout.log",
                        "original-control-stderr.log",
                        "original-wrapper-stderr.log",
                        "resolved-execution.conf",
                        "original-intent.conf")),
                "r2733_original_control_and_wrapper_raw_files_missing")
    return {
        "schema": SCHEMA,
        "same_run_original_cpp_wrapper_reopened": True,
        "two_original_eistute_roles_retained": list(ROLES),
        "actual_original_selected_post_aft_tri_step4_per_role": 16,
        "genuine_source_native_global_committed_steps": [1],
        "global_original_acceptance_and_scientific_output_parity_qualified": True,
        "selected_for_adapter_return_is_not_global_commit": True,
        "cross_epoch_face_descent_qualified": False,
        "physical_welded_seam_qualified": False,
        "continuous_geometric_error_qualified": False,
        "scientific_lod_qualified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("capture", "audit"), required=True)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--original-exe", type=Path)
    p.add_argument("--baseline-exe", type=Path)
    p.add_argument("--wrapper-exe", type=Path)
    p.add_argument("--original-directory", type=Path)
    p.add_argument("--r2726-trials", type=Path)
    p.add_argument("--r2728-directory", type=Path)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--audit-report", type=Path)
    p.add_argument("--timeout", type=int, default=300)
    a = p.parse_args()
    if a.mode == "capture":
        require(all(getattr(a, v) is not None for v in (
            "original_exe", "baseline_exe", "wrapper_exe",
            "original_directory", "r2726_trials", "r2728_directory")),
            "r2733_source_native_executable_or_control_inputs_missing")
        capture(a.root, a.original_exe, a.baseline_exe,
                a.wrapper_exe, a.original_directory,
                a.r2726_trials, a.r2728_directory,
                a.output_dir, a.timeout)
    else:
        require(a.audit_report is not None and not a.audit_report.exists(),
                "r2733_audit_receipt_must_be_new")
        result = audit(a.root, a.output_dir)
        a.audit_report.parent.mkdir(parents=True, exist_ok=True)
        a.audit_report.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        print("R2733_INDEPENDENT_ORIGINAL_NATIVE_TRI_AUDIT=" +
              json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
