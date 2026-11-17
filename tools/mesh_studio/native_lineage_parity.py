"""R2.7.13 fail-closed numerical parity for native lineage OFF versus ON.

Both real serial GeneratorAdaptive builds run the same original model/config
with only input/output relocation. Original scientific files must be byte-equal.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

from .verify_native_lineage import (
    SOURCE_MODELS, decode_ndjson, sha256_file, validate_lineage_records,
)

SCHEMA = "apmesh.meshstudio.r2713.default_off_optin_numerical_parity.v1"
SCIENTIFIC_SUFFIXES = {".obj", ".pos", ".csv", ".json"}
MAX_SCIENTIFIC_FILES = 600
MAX_SCIENTIFIC_FILE_BYTES = 100_000_000
EXPECTED_ACCEPTED_STEPS = {"eistute": [1], "book": [1]}


class NativeLineageParityError(ValueError):
    """A scientific source, event or generated output diverged between builds."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise NativeLineageParityError(reason)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare_original_config(root: Path, model: str, workspace: Path) -> tuple[Path, Path, Path]:
    require(model in SOURCE_MODELS, "unknown_original_source")
    source_config = root / "configs" / model / "article.conf"
    require(source_config.is_file(), "original_config_missing")
    original_text = source_config.read_text(encoding="utf-8")
    input_match = re.search(r"^INPUT_MODEL=(.+)$", original_text, flags=re.M)
    output_match = re.search(r"^OUTPUT_PREFIX=(.+)$", original_text, flags=re.M)
    require(input_match is not None and output_match is not None and
            len(re.findall(r"^INPUT_MODEL=", original_text, flags=re.M)) == 1 and
            len(re.findall(r"^OUTPUT_PREFIX=", original_text, flags=re.M)) == 1,
            "original_config_source_paths_ambiguous")
    model_path = (root / input_match.group(1).strip()).resolve()
    require(model_path.is_file(), "original_input_mesh_missing")
    config = re.sub(r"^INPUT_MODEL=.+$",
                    lambda _: "INPUT_MODEL=" + model_path.as_posix(),
                    original_text, count=1, flags=re.M)
    config = re.sub(r"^OUTPUT_PREFIX=.+$",
                    lambda _: "OUTPUT_PREFIX=" + (workspace / model).as_posix(),
                    config, count=1, flags=re.M)
    config_file = workspace / "original_article.conf"
    config_file.write_text(config, encoding="utf-8", newline="\n")
    return source_config, model_path, config_file


def output_inventory(workspace: Path) -> tuple[dict[str, dict], list[str]]:
    result = {}
    excluded = []
    for item in sorted(workspace.rglob("*")):
        if not item.is_file():
            continue
        relative = item.relative_to(workspace).as_posix()
        require(not item.is_symlink(), "scientific_output_symlink_rejected")
        if relative == "original_article.conf" or relative.startswith("lineage/"):
            continue
        if item.suffix.lower() not in SCIENTIFIC_SUFFIXES:
            excluded.append(relative)
            continue
        require(item.stat().st_size <= MAX_SCIENTIFIC_FILE_BYTES,
                "oversized_scientific_output_" + relative)
        result[relative] = {
            "sha256": sha256_file(item),
            "bytes": item.stat().st_size,
            "class": item.suffix.lower(),
        }
        require(len(result) <= MAX_SCIENTIFIC_FILES,
                "scientific_output_file_limit_exceeded")
    return result, excluded


def compare_exact_scientific_inventories(off: dict, on: dict) -> dict:
    require(off and on, "missing_scientific_outputs")
    require(set(off) == set(on), "off_on_scientific_file_set_differs")
    classes = Counter()
    for name in sorted(off):
        left, right = off[name], on[name]
        require(left.get("class") in SCIENTIFIC_SUFFIXES and
                right.get("class") == left["class"], "unknown_output_class_" + name)
        require(left.get("bytes") == right.get("bytes") and
                left.get("sha256") == right.get("sha256"),
                "scientific_bytes_diverged_" + name)
        classes[left["class"]] += 1
    for mandatory in (".obj", ".csv", ".json"):
        require(classes[mandatory] >= 1,
                "mandatory_source_geometry_or_metric_file_missing_" + mandatory)
    return {
        "scientific_files_exactly_byte_equal": True,
        "compared_file_count": len(off),
        "classes": dict(sorted(classes.items())),
        "scientific_file_sha256": {key: off[key]["sha256"] for key in sorted(off)},
    }


def original_outcome_marker(stdout: str) -> tuple[str, int, int]:
    markers = [line.strip() for line in stdout.splitlines()
               if line.startswith("real_generator_outcomes=")]
    require(len(markers) == 1, "missing_or_duplicate_native_global_outcome")
    match = re.fullmatch(
        r"real_generator_outcomes=1 accepted_tri=(\d+) restored_tri=(\d+)"
        r" budget_evaluations=(\d+) growth_evaluations=(\d+)"
        r" uv_captures=(\d+) local_selected=(\d+) global_epochs=(\d+)"
        r" truncated=0", markers[0])
    require(match is not None, "native_global_outcome_schema_mismatch")
    accepted, restored, *other = [int(v) for v in match.groups()]
    require(accepted >= 1 and restored >= 1 and all(n >= 0 for n in other),
            "original_global_outcome_incomplete")
    return markers[0], accepted, restored


def execute(executable: Path, root: Path, model: str, workspace: Path,
            instrumented: bool, timeout: int) -> dict:
    workspace.mkdir()
    source_config, model_path, config_file = prepare_original_config(
        root, model, workspace)
    environment = dict(os.environ)
    environment.pop("APMESH_RESEARCH_LINEAGE_DIR", None)
    if instrumented:
        environment["APMESH_RESEARCH_LINEAGE_DIR"] = str(workspace / "lineage")
    result = subprocess.run(
        [str(executable), str(config_file)],
        cwd=workspace, env=environment, text=True, capture_output=True,
        timeout=timeout, check=False)
    require(result.returncode == 0, "original_generator_execution_failed_" +
            ("on" if instrumented else "off"))
    require("R2712_NATIVE_LINEAGE_ERROR=" not in result.stderr,
            "native_observation_error_during_parity_run")
    marker, accepted, restored = original_outcome_marker(result.stdout)
    outputs, excluded = output_inventory(workspace)
    lineage = workspace / "lineage"
    sidecars = sorted(lineage.glob("*.ndjson")) if lineage.exists() else []
    if instrumented:
        require(len(sidecars) == accepted and
                not list(lineage.glob("*.pending")),
                "on_build_native_commit_sidecar_mismatch")
    else:
        require(not sidecars and not lineage.exists() and
                "R2712_NATIVE_LINEAGE_WRITTEN" not in result.stderr,
                "off_build_leaked_experimental_lineage")
    accepted_steps = []
    source_face_counts = []
    sidecar_sha = {}
    for sidecar in sidecars:
        raw = sidecar.read_bytes()
        receipt = validate_lineage_records(decode_ndjson(raw), model)
        require(receipt["has_typed_outer_scope"],
                "missing_original_typed_global_outcome_in_parity")
        accepted_steps.append(receipt["accepted_step"])
        source_face_counts.append(receipt["native_tri_faces"])
        sidecar_sha[sidecar.name] = sha_bytes(raw)
    if instrumented:
        require(accepted_steps == sorted(set(accepted_steps)) ==
                EXPECTED_ACCEPTED_STEPS[model],
                "unexpected_original_accepted_step_sequence")
    else:
        require(accepted == len(EXPECTED_ACCEPTED_STEPS[model]),
                "unexpected_uninstrumented_committed_step_count")
    return {
        "executable_sha256": sha256_file(executable),
        "source_config_sha256": sha256_file(source_config),
        "input_model_sha256": sha256_file(model_path),
        "relocated_config_sha256": sha256_file(config_file),
        "global_outcome_marker": marker,
        "accepted": accepted,
        "restored": restored,
        "scientific_outputs": outputs,
        "excluded_non_scientific_files": excluded,
        "raw_native_sidecar_sha256": sidecar_sha,
        "accepted_native_step_ids": accepted_steps,
        "accepted_native_tri_faces": source_face_counts,
        "stdout_sha256_not_parity_comparable": sha_bytes(result.stdout.encode()),
        "stderr_sha256_not_parity_comparable": sha_bytes(result.stderr.encode()),
    }


def compare_default_off_vs_on(executable_off: Path, executable_on: Path,
                              root: Path, model: str, out_dir: Path,
                              timeout: int = 300) -> dict:
    root = root.resolve()
    executable_off = executable_off.resolve()
    executable_on = executable_on.resolve()
    require(executable_off.is_file() and executable_on.is_file() and
            executable_off != executable_on,
            "must_supply_two_distinct_real_native_build_executables")
    with TemporaryDirectory(prefix="apmesh-r2713-parity-") as temp:
        folder = Path(temp)
        control = execute(executable_off, root, model, folder / "default_off",
                          False, timeout)
        observed = execute(executable_on, root, model, folder / "instrumented_on",
                           True, timeout)
        require(control["source_config_sha256"] ==
                observed["source_config_sha256"] and
                control["input_model_sha256"] ==
                observed["input_model_sha256"], "native_source_input_differs")
        require(control["global_outcome_marker"] ==
                observed["global_outcome_marker"] and
                control["accepted"] == observed["accepted"] and
                control["restored"] == observed["restored"],
                "scientific_native_accepted_rejected_events_changed")
        compared = compare_exact_scientific_inventories(
            control["scientific_outputs"], observed["scientific_outputs"])
        require(control["accepted"] == len(observed["accepted_native_step_ids"]),
                "native_observed_commits_not_same_as_default")
        report = {
            "schema": SCHEMA,
            "research_scope": "REAL_NATIVE_SAME_INPUT_DEFAULT_OFF_VS_ON_EXACT_OUTPUT_BYTES",
            "model": model,
            "pinned_source_config_sha256": control["source_config_sha256"],
            "pinned_input_model_sha256": control["input_model_sha256"],
            "executable_off_sha256": control["executable_sha256"],
            "executable_on_sha256": observed["executable_sha256"],
            "accepted_and_restored_outcome_marker_identical": True,
            "matched_original_global_outcome_marker":
                control["global_outcome_marker"],
            "native_accepted_commits": control["accepted"],
            "native_restored_rejections": control["restored"],
            "scientific_outputs": compared,
            "native_optin_step_ids": observed["accepted_native_step_ids"],
            "native_optin_accepted_face_counts":
                observed["accepted_native_tri_faces"],
            "raw_native_sidecar_sha256": observed["raw_native_sidecar_sha256"],
            "non_scientific_output_paths_not_used_for_parity": {
                "off": control["excluded_non_scientific_files"],
                "on": observed["excluded_non_scientific_files"],
            },
            "timer_stdout_stderr_intentionally_not_compared": True,
            "scientific_outputs_byte_identical_for_tested_inputs": True,
            "only_two_article_profiles_eistute_book_tested": True,
            "second_native_accepted_epoch_qualified": False,
            "persistent_cross_epoch_face_lineage_qualified": False,
            "scientific_lod_qualified": False,
        }
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / ("r2713-" + model + "-native-output-parity.json")
    with report_path.open("x", encoding="utf-8", newline="\n") as target:
        target.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("R2713_NATIVE_OUTPUT_PARITY=" + json.dumps({
        "model": model, "accepted": report["native_accepted_commits"],
        "restored": report["native_restored_rejections"],
        "scientific_files_equal": compared["compared_file_count"],
        "file_classes": compared["classes"],
        "scientific_lod_qualified": False,
    }, sort_keys=True))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe-off", required=True, type=Path)
    parser.add_argument("--exe-on", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--model", required=True, choices=tuple(SOURCE_MODELS))
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    compare_default_off_vs_on(args.exe_off, args.exe_on, args.root,
                              args.model, args.out_dir, args.timeout)


if __name__ == "__main__":
    main()
