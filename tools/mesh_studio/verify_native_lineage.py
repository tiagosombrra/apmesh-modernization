"""R2.7.12 independent validator for original native accepted-epoch NDJSON.

Fake fixtures in unit tests validate this parser only; actual research evidence
requires the opt-in compiled original C++ generator and a real accepted commit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

SCHEMA = "apmesh.meshstudio.r2712.native_lineage_ndjson.v1"
REPORT_SCHEMA = "apmesh.meshstudio.r2712.native_lineage_validation.v1"
SOURCE_MODELS = {"eistute": (4, 13), "book": (28, 85)}
MAX_BYTES = 100_000_000
MAX_RECORDS = 150_000


class NativeLineageValidationError(ValueError):
    """An incomplete or fabricated accepted native source record was encountered."""


def require(value: bool, message: str) -> None:
    if not value:
        raise NativeLineageValidationError(message)


def unique_fields(items):
    fields = {}
    for key, value in items:
        require(key not in fields, "duplicate_json_key_" + key)
        fields[key] = value
    return fields


def integer(value) -> bool:
    return type(value) is int and value >= 0


def finite_number(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def decode_ndjson(raw: bytes) -> list[dict]:
    require(len(raw) <= MAX_BYTES and raw.endswith(b"\n"),
            "truncated_or_oversized_lineage")
    require(b"\r" not in raw and b"\0" not in raw, "noncanonical_lineage_bytes")
    lines = raw.splitlines()
    require(3 <= len(lines) <= MAX_RECORDS, "invalid_lineage_record_count")
    entries = []
    for line in lines:
        require(len(line) <= 16384, "oversized_lineage_record")
        record = json.loads(line.decode("utf-8"), object_pairs_hook=unique_fields,
                            parse_constant=lambda value: (_ for _ in ()).throw(
                                NativeLineageValidationError("nonfinite_json_" + value)))
        require(type(record) is dict, "invalid_lineage_record")
        entries.append(record)
    return entries


def validate_lineage_records(records: list[dict], expected_model: str) -> dict:
    require(expected_model in SOURCE_MODELS, "unknown_original_native_source_model")
    patches_expected, curves_expected = SOURCE_MODELS[expected_model]
    require(type(records) is list and len(records) >= 3,
            "missing_native_lineage_records")
    first, last = records[0], records[-1]
    require(first.get("schema") == SCHEMA and first.get("type") == "accepted_commit" and
            first.get("native_id_semantics") == "snapshot_local_not_cross_epoch" and
            first.get("face_record_semantics") ==
            "native_element_id_plus_patch_slot_not_obj_ordinal" and
            first.get("scientific_lod_admitted") is False,
            "invalid_or_forged_native_commit_header")
    require(integer(first.get("step")) and first["step"] > 0 and
            integer(first.get("retry")) and
            first.get("source_patch_count") == patches_expected and
            first.get("source_curve_count") == curves_expected,
            "invalid_native_commit_source_scope")
    has_outer = first.get("has_typed_outer_scope")
    require(type(has_outer) is bool, "missing_native_outer_scope_classification")
    require(integer(first.get("session")) and integer(first.get("outer_epoch")) and
            type(first.get("global_retry")) is int,
            "invalid_native_outer_namespace")
    require((first["session"] > 0 and first["outer_epoch"] > 0 and
             first["global_retry"] >= 0) if has_outer else
            (first["session"] == 0 and first["outer_epoch"] == 0 and
             first["global_retry"] == -1), "invalid_partial_native_outer_scope")
    require(last.get("type") == "complete" and
            last.get("patch_records") == patches_expected and
            last.get("fully_accepted_source_face_lineage_across_epochs") is False,
            "invalid_or_forged_lineage_completion")
    observed_patches: dict[int, dict] = {}
    face_slots: dict[int, set[int]] = {}
    curve_slots: dict[int, int] = {}
    curve_patch_incidence: dict[int, set[int]] = {}
    face_count = 0
    for record in records[1:-1]:
        kind = record.get("type")
        patch_slot = record.get("patch_slot")
        require(integer(patch_slot) and patch_slot < patches_expected,
                "invalid_native_patch_slot")
        if kind == "patch":
            require(patch_slot not in observed_patches, "duplicate_native_patch_record")
            require(integer(record.get("native_patch_id")) and
                    integer(record.get("node_count")) and
                    integer(record.get("face_count")) and
                    type(record.get("source_curves")) is list and
                    len(record["source_curves"]) == 4,
                    "invalid_native_patch_membership")
            observed_patches[patch_slot] = record
            face_slots[patch_slot] = set()
            for edge, curve in enumerate(record["source_curves"]):
                require(type(curve) is dict and
                        curve.get("edge_slot") == edge and
                        integer(curve.get("source_curve_slot")) and
                        curve["source_curve_slot"] < curves_expected and
                        integer(curve.get("native_curve_id")) and
                        type(curve.get("reversed")) is bool and
                        integer(curve.get("reported_curve_patch_observers")),
                        "invalid_native_curve_incidence")
                slot = curve["source_curve_slot"]
                native = curve["native_curve_id"]
                require(slot not in curve_slots or curve_slots[slot] == native,
                        "cross_patch_source_curve_id_disagreement")
                curve_slots[slot] = native
                curve_patch_incidence.setdefault(slot, set()).add(patch_slot)
        elif kind == "face":
            require(patch_slot in observed_patches and
                    record.get("native_patch_id") ==
                    observed_patches[patch_slot]["native_patch_id"] and
                    integer(record.get("native_element_id")) and
                    integer(record.get("element_slot")) and
                    record["element_slot"] not in face_slots[patch_slot],
                    "invalid_native_face_or_patch_owner")
            face_slots[patch_slot].add(record["element_slot"])
            vertices = record.get("vertices")
            require(type(vertices) is list and len(vertices) == 3,
                    "invalid_native_triangle_vertex_count")
            for vertex in vertices:
                require(type(vertex) is dict and
                        integer(vertex.get("native_node_id")) and
                        type(vertex.get("xyz")) is list and len(vertex["xyz"]) == 3 and
                        all(finite_number(x) for x in vertex["xyz"]) and
                        type(vertex.get("uv")) is list and len(vertex["uv"]) == 2 and
                        all(finite_number(x) for x in vertex["uv"]),
                        "invalid_native_vertex_or_source_uv")
            face_count += 1
        else:
            raise NativeLineageValidationError("unknown_or_out_of_order_lineage_event")
    require(set(observed_patches) == set(range(patches_expected)),
            "native_source_patch_incomplete")
    require(set(curve_slots) == set(range(curves_expected)),
            "native_source_curve_incomplete")
    for slot, patch in observed_patches.items():
        require(face_slots[slot] == set(range(patch["face_count"])),
                "missing_or_noncontiguous_native_element_slots")
    require(face_count == last.get("face_records") ==
            sum(p["face_count"] for p in observed_patches.values()) and
            last.get("node_records_counted_per_patch") ==
            sum(p["node_count"] for p in observed_patches.values()),
            "lineage_face_or_node_counts_inconsistent")
    require(face_count > 0, "empty_native_accepted_mesh")
    # Matching source curve pointers across patches establish source adjacency
    # only; they never prove globally welded physical mesh nodes.
    shared = {slot: sorted(owners) for slot, owners in curve_patch_incidence.items()
              if len(owners) >= 2}
    require(bool(shared), "no_original_shared_source_curve_incidence")
    return {
        "schema": REPORT_SCHEMA,
        "model": expected_model,
        "accepted_step": first["step"],
        "retry_index": first["retry"],
        "has_typed_outer_scope": has_outer,
        "typed_session": first["session"],
        "typed_outer_epoch": first["outer_epoch"],
        "native_source_patches": len(observed_patches),
        "native_source_curves": len(curve_slots),
        "native_tri_faces": face_count,
        "shared_source_curve_slots": len(shared),
        "source_patch_curve_orientation_recorded": True,
        "native_face_ids_recorded_not_obj_face_ordinals": True,
        "native_ids_persistent_across_accepted_epochs_verified": False,
        "global_shared_physical_node_welding_verified": False,
        "scientific_lod_qualified": False,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_original_generator_run(
    executable: Path, root: Path, model: str, artifact_dir: Path,
    *, timeout: int = 300,
) -> dict:
    require(model in SOURCE_MODELS, "unknown_original_model")
    executable = executable.resolve()
    root = root.resolve()
    config_path = root / "configs" / model / "article.conf"
    require(executable.is_file() and config_path.is_file(),
            "missing_original_generator_or_model_configuration")
    original_config = config_path.read_text(encoding="utf-8")
    source_line = re.search(r"^INPUT_MODEL=(.+)$", original_config, flags=re.M)
    require(source_line is not None, "original_config_missing_input")
    native_input = (root / source_line.group(1).strip()).resolve()
    require(native_input.is_file(), "original_model_input_missing")
    with TemporaryDirectory(prefix="apmesh-r2712-native-") as directory:
        local = Path(directory)
        lineagedir = local / "lineage"
        lineagedir.mkdir()
        source_prefix = local / model
        conf = re.sub(r"^INPUT_MODEL=.+$", "INPUT_MODEL=" + native_input.as_posix(),
                      original_config, flags=re.M)
        conf = re.sub(r"^OUTPUT_PREFIX=.+$", "OUTPUT_PREFIX=" + source_prefix.as_posix(),
                      conf, flags=re.M)
        path = local / "original_native.conf"
        path.write_text(conf, encoding="utf-8", newline="\n")
        env = dict(os.environ, APMESH_RESEARCH_LINEAGE_DIR=str(lineagedir))
        process = subprocess.run([str(executable), str(path)], cwd=root, env=env,
                                 text=True, capture_output=True, timeout=timeout,
                                 check=False)
        require(process.returncode == 0, "native_generator_run_failed")
        require("R2712_NATIVE_LINEAGE_ERROR=" not in process.stderr,
                "native_lineage_exporter_reported_failure")
        marker = re.search(r"^real_generator_outcomes=1 accepted_tri=(\d+) restored_tri=(\d+)",
                           process.stdout, flags=re.M)
        require(marker is not None, "missing_actual_native_acceptance_hook_result")
        accepted_count, restored_count = map(int, marker.groups())
        require(accepted_count >= 1 and restored_count >= 1,
                "missing_real_native_accepted_and_restored_outcomes")
        receipts = sorted(lineagedir.glob("*.ndjson"))
        require(len(receipts) == accepted_count, "native_commit_count_vs_sidecar_mismatch")
        require(not list(lineagedir.glob("*.pending")), "unfinished_native_receipt")
        results = []
        raw_snapshots = []
        last_step = 0
        for sidecar in receipts:
            data = sidecar.read_bytes()
            verified = validate_lineage_records(decode_ndjson(data), model)
            require(verified["has_typed_outer_scope"],
                    "native_original_generator_missing_typed_global_outcome")
            require(verified["accepted_step"] > last_step,
                    "repeated_or_out_of_order_native_committed_step")
            last_step = verified["accepted_step"]
            verified["source_file_sha256"] = hashlib.sha256(data).hexdigest()
            retained_name = "r2712-" + model + "-" + sidecar.name
            verified["raw_native_ndjson_artifact_name"] = retained_name
            raw_snapshots.append((retained_name, data, verified["source_file_sha256"]))
            results.append(verified)
        summary = {
            "schema": REPORT_SCHEMA,
            "classification": "REAL_NATIVE_SERIAL_SOURCE_COMMIT_NOT_SCIENTIFIC_LOD",
            "original_model": model,
            "native_config_source_sha256": sha256_file(config_path),
            "real_model_input_sha256": sha256_file(native_input),
            "research_executable_sha256": sha256_file(executable),
            "resolved_research_config_sha256": sha256_file(path),
            "native_stdout_sha256": hashlib.sha256(
                process.stdout.encode("utf-8")).hexdigest(),
            "native_stderr_sha256": hashlib.sha256(
                process.stderr.encode("utf-8")).hexdigest(),
            "native_accepted_commits": accepted_count,
            "native_rejected_restored": restored_count,
            "accepted_snapshots": results,
            "second_accepted_epoch_observed": accepted_count >= 2,
            "cross_epoch_original_face_id_lineage_qualified": False,
            "source_shared_curve_incidence_not_welded_nodes": True,
            "continuous_error_qualified": False,
            "scientific_lod_qualified": False,
            "operator_physical_gpu_qualified": False,
        }
        # Retain byte-exact original per-face evidence after full native validation.
        # No synthetic fixture or rejected candidate is exported as qualified.
        artifact_dir.mkdir(parents=True, exist_ok=True)
        for filename, data, expected_sha in raw_snapshots:
            original = artifact_dir / filename
            with original.open("xb") as output:
                output.write(data)
            require(sha256_file(original) == expected_sha,
                    "retained_native_sidecar_byte_mismatch")
        out = artifact_dir / ("r2712-" + model + "-native-lineage-audit.json")
        with out.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print("R2712_NATIVE_LINEAGE_QUALIFIED=" + json.dumps({
            "model": model, "accepted": accepted_count, "restored": restored_count,
            "faces_per_accepted_step": [x["native_tri_faces"] for x in results],
            "source_patches": SOURCE_MODELS[model][0],
            "source_curves": SOURCE_MODELS[model][1],
            "second_epoch_seen": accepted_count >= 2,
            "cross_epoch_lineage_qualified": False,
        }, sort_keys=True))
        return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model", choices=tuple(SOURCE_MODELS), required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    options = parser.parse_args()
    verify_original_generator_run(options.exe, options.root, options.model,
                                  options.out_dir)


if __name__ == "__main__":
    main()
