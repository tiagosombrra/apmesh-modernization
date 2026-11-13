#!/usr/bin/env python3
"""Measure accepted source epochs of the genuine serial GeneratorAdaptive.

The original model, engine, TRI acceptance criteria, frozen article configs,
and production source are unchanged. A successful diagnostic execution is NOT
proof of two accepted epochs unless the native committed-event marker says so.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory


MODELS = {
    "eistute": {
        "input": "input_models/eistute2.fixed.bp",
        "sha256": "fdce4714524b88f536ec9f8eddc467e54e638dc6e765784ab68edc9a366a0a3f",
        "patches": 4,
        "curves": 13,
    },
    "book": {
        "input": "input_models/book_v7a.bp",
        "sha256": "3c4255cbd2f46bd2dce5f0e86b8e7ee9ac0c58df949d4563dd821deedcd8412d",
        "patches": 28,
        "curves": 85,
    },
}

# Config profiles are research experiments, NOT historical reference settings.
# Each override is recorded with the source config SHA and a separate output.
PROFILES = {
    "pinned_article": {},
    "stable_small_increment": {
        "ADAPTIVE_MODE": "adaptive_stable",
        "ADAPTIVE_INTENSITY": "0.12",
        "ADAPTIVE_TARGET_GROWTH": "1.08",
        "ADAPTIVE_MAX_STEPS": "4",
    },
    "debug_low_intensity": {
        "ADAPTIVE_MODE": "research_debug",
        "ADAPTIVE_INTENSITY": "0.02",
        "ADAPTIVE_TARGET_GROWTH": "1.05",
        "ADAPTIVE_MAX_STEPS": "4",
    },
}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key_values(line):
    return dict(re.findall(r"([a-z_]+)=([^\s]+)", line))


def integer(fields, name):
    require(name in fields, f"Native accepted-step marker missing {name}")
    value = int(fields[name])
    require(value >= 0, "Negative generator count")
    return value


def monotone_identifiers(value, size):
    try:
        found = [int(x) for x in value.split(",") if x]
    except (ValueError, TypeError) as exc:
        raise ValueError("Missing accepted original source IDs") from exc
    require(len(found) == size and len(set(found)) == len(found)
            and all(a < b for a, b in zip(found, found[1:])),
            "Accepted generator identifiers are repeated or not chronological")
    return found


def acceptance_logs(prefix, steps, curve_count):
    receipts = []
    for step in steps:
        base = prefix.parent / f"{prefix.name}_passo_{step}_"
        acceptance_path = Path(str(base) + "acceptance_accepted.log")
        curve_path = Path(str(base) + "curve_adaptation_accepted.csv")
        patch_path = Path(str(base) + "patch_adaptation_accepted.csv")
        incident_path = Path(str(base) + "incidences.json")
        require(acceptance_path.is_file() and curve_path.is_file()
                and patch_path.is_file() and incident_path.is_file(),
                f"An actual accepted source step {step} is missing committed output")
        fields = dict(row.split("=", 1) for row in
                      acceptance_path.read_text(encoding="utf-8").splitlines()
                      if "=" in row)
        require(fields.get("step") == str(step)
                and fields.get("accepted") == "1",
                "Accepted original step has a rejected/mismatched acceptance log")
        with curve_path.open(newline="", encoding="utf-8") as src:
            curves = list(csv.DictReader(src))
        require(len(curves) == curve_count,
                "Accepted original curve adaptation log lost a Geometry curve")
        for curve in curves:
            require(int(curve["actual_curve_points"]) >= 2
                    and int(curve["target_curve_points"]) >= 2,
                    "Original accepted curve target/subdivision is incomplete")
        with patch_path.open(newline="", encoding="utf-8") as src:
            patch_rows = list(csv.DictReader(src))
        require(len(patch_rows) > 0,
                "Original accepted patch adaptation has no actual patches")
        incidence = json.loads(incident_path.read_text(encoding="utf-8"))
        require(isinstance(incidence, (dict, list)),
                "Accepted original source incidence snapshot is invalid")
        receipts.append({
            "step": step,
            "acceptance_log_sha256": sha(acceptance_path),
            "curve_adaptation_csv_sha256": sha(curve_path),
            "patch_adaptation_csv_sha256": sha(patch_path),
            "incidence_json_sha256": sha(incident_path),
            "curves": len(curves),
            "patch_adaptation_rows": len(patch_rows),
            "retry_count": fields.get("budget_retry_count"),
            "budget_final_status": fields.get("budget_final_status"),
        })
    return receipts


def scenario(exe, root, directory, model, spec, profile_name, overrides):
    base_config_path = root / "configs" / model / "article.conf"
    config_text = base_config_path.read_text(encoding="utf-8")
    require("MESH_ELEMENT_KIND" not in config_text or
            re.search(r"^MESH_ELEMENT_KIND=tri$", config_text, re.M),
            "A source configuration selected non-TRI production")
    input_path = (root / spec["input"]).resolve()
    require(sha(input_path) == spec["sha256"],
            "The original Bézier input model SHA-256 changed")
    original_config_sha = sha(base_config_path)
    sub = directory / f"{model}_{profile_name}"
    sub.mkdir(parents=True)
    prefix = sub / f"{model}_{profile_name}"
    config_text, count = re.subn(
        r"^INPUT_MODEL=.*$",
        lambda _: "INPUT_MODEL=" + input_path.as_posix(),
        config_text, flags=re.M)
    require(count == 1, "Input model path is not uniquely configurable")
    config_text, count = re.subn(
        r"^OUTPUT_PREFIX=.*$",
        lambda _: "OUTPUT_PREFIX=" + prefix.as_posix(),
        config_text, flags=re.M)
    require(count == 1, "Original model output path was missing")
    for key, value in overrides.items():
        pattern = rf"^{re.escape(key)}=.*$"
        if re.search(pattern, config_text, re.M):
            config_text = re.sub(pattern, lambda _: f"{key}={value}",
                                 config_text, flags=re.M)
        else:
            config_text += f"\n{key}={value}\n"
    config_file = sub / "research.conf"
    config_file.write_text(config_text, encoding="utf-8")
    result = {
        "model": model, "profile": profile_name,
        "original_input_model_sha256": spec["sha256"],
        "original_article_config_sha256": original_config_sha,
        "executed_research_config_sha256": sha(config_file),
        "overrides": overrides,
        "accepted_two_original_generator_epochs": False,
        "global_physically_welded_quad_mesh": False,
    }
    try:
        execution = subprocess.run(
            [str(exe.resolve()), str(config_file)],
            cwd=root, capture_output=True, text=True, timeout=100,
            check=False)
    except subprocess.TimeoutExpired:
        result.update(status="timeout", reason="100-second bounded research budget")
        return result
    (sub / "generator_stdout.log").write_text(execution.stdout, encoding="utf-8")
    (sub / "generator_stderr.log").write_text(execution.stderr, encoding="utf-8")
    result["native_exit_code"] = execution.returncode
    summary = [line for line in execution.stdout.splitlines()
               if line.startswith("R2C13_REAL_GENERATOR_ACCEPTED_EPOCHS ")]
    prior = [line for line in execution.stdout.splitlines()
             if line.startswith("real_generator_outcomes=1 ")]
    if execution.returncode != 0 or len(summary) != 1 or len(prior) != 1:
        result.update(status="unqualified_native_run",
                      reason="Missing coherent original committed-event output",
                      stderr_tail=execution.stderr[-400:],
                      stdout_tail=execution.stdout[-400:])
        return result
    fields = key_values(summary[0])
    counts = key_values(prior[0])
    accepted = integer(fields, "accepted_committed_steps")
    full = integer(fields, "accepted_full_source_patch_coverage_epochs")
    distinct = integer(fields, "accepted_distinct_outer_epochs")
    reject = integer(fields, "rejected_restored_original_steps")
    require(accepted == full == distinct
            and accepted == integer(counts, "accepted_tri")
            and reject == integer(counts, "restored_tri")
            and integer(fields, "original_patches") == spec["patches"]
            and integer(fields, "globally_connected_QUAD_AFT_mesh_accepted") == 0
            and integer(fields, "research_nonmanifold_sheet_approved") == 0,
            "Native source GeneratorAdaptive commit/rollback evidence inconsistent")
    steps = monotone_identifiers(fields.get("accepted_step_ids"), accepted)
    epochs = monotone_identifiers(fields.get("accepted_outer_epoch_ids"), accepted)
    witnesses = acceptance_logs(prefix, steps, spec["curves"])
    qualified = accepted >= 2 and len(witnesses) >= 2
    require(qualified ==
            (integer(fields, "two_accepted_original_generator_epochs") == 1),
            "Native two-epoch claim is inconsistent with actual accepted steps")
    result.update(
        status="qualified_two_accepted_epochs" if qualified
               else "observed_but_fewer_than_two_accepted_epochs",
        accepted_committed_steps=accepted,
        accepted_step_ids=steps,
        accepted_outer_epoch_ids=epochs,
        rejected_restored_steps=reject,
        source_boundary_vertex_witnesses=integer(
            fields, "accepted_source_boundary_vertex_observations"),
        per_accepted_step_receipts=witnesses,
        accepted_two_original_generator_epochs=qualified,
    )
    return result


def run(args):
    output = args.directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    result = {"schema": "apmesh.quad.r2c13.actual_production_generator_epochs.v1",
              "models": {}, "all_models_two_accepted_epochs": False,
              "global_quad_aft_model_approved": False,
              "physical_nodes_welded": False}
    for model, spec in MODELS.items():
        cases = []
        for profile, overrides in PROFILES.items():
            cases.append(scenario(args.exe, args.root, output,
                                  model, spec, profile, overrides))
        result["models"][model] = {
            "cases": cases,
            "qualified_profiles": [
                case["profile"] for case in cases
                if case["accepted_two_original_generator_epochs"]
            ],
        }
        require(cases[0]["status"] in {
            "qualified_two_accepted_epochs",
            "observed_but_fewer_than_two_accepted_epochs"
        }, f"Original {model} pinned native fixture unexpectedly failed")
    result["all_models_two_accepted_epochs"] = all(
        bool(model_data["qualified_profiles"])
        for model_data in result["models"].values())
    report = output / "r2c13_accepted_generator_epochs.json"
    report.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8")
    print("R2C13_M7_ORIGINAL_ACCEPTED_GENERATOR_DIAGNOSTIC",
          json.dumps({
              model: [{
                  "profile": case["profile"],
                  "status": case["status"],
                  "accepted": case.get("accepted_committed_steps", 0),
                  "restored": case.get("rejected_restored_steps", 0),
              } for case in evidence["cases"]]
              for model, evidence in result["models"].items()
          }, sort_keys=True),
          "all_models_two_accepted_epochs=" +
          str(int(result["all_models_two_accepted_epochs"])),
          "global_physical_quad_mesh_approved=0")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    run(parser.parse_args())
