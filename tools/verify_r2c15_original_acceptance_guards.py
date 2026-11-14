#!/usr/bin/env python3
"""Prove only source-evaluable historical stable acceptance guard violations.

A violated conjunct excludes an original stable GeneratorAdaptive candidate
without relaxing acceptance rules. Non-stable modes and unlogged predicates
remain unclassified, never accepted by inference.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re


SOURCE_ANCHORS = (
    "current_overshoot_ratio_ <= 1.22",
    "current_overshoot_ratio_ <= 1.28",
    "current_transition_coherence_penalty_ <= 0.20",
    "current_transition_coherence_penalty_ <= transition_penalty_cap",
    "((this->step_ >= 4 && current_policy_.stable_mode) ? 0.42 : 0.25)",
    "current_underresolved_transition_fraction_real_ <= 0.05",
    "current_underresolved_transition_fraction_real_ <= 0.03",
    "current_transition_imbalance_max_real_ <= 0.12",
    "current_transition_imbalance_max_real_ <= 0.10",
    "(improvement > 0.15",
    "(improvement > 0.20",
    "current_policy_.stable_mode && this->step_ >= 2",
)


def require(value, reason):
    if not value:
        raise ValueError(reason)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_key_values(path):
    attrs = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            require(key not in attrs, f"Repeated original log key {key}")
            attrs[key] = value
    return attrs


def value(attrs, name):
    require(name in attrs, f"Original candidate missing {name}")
    answer = float(attrs[name])
    require(math.isfinite(answer), f"Nonfinite original candidate field {name}")
    return answer


def same_number(a, b):
    # Native logs are rounded for display but SHA-bound to the source report.
    return abs(a - b) <= 2e-5 * max(1.0, abs(a), abs(b))


def mode_from_source(root, model, case):
    text = (root / "configs" / model / "article.conf").read_text(encoding="utf-8")
    found = re.findall(r"^ADAPTIVE_MODE=([^\s]+)$", text, flags=re.MULTILINE)
    require(len(found) == 1, "Original experiment does not have unique adaptive mode")
    mode = case.get("overrides", {}).get("ADAPTIVE_MODE", found[0])
    require(mode in ("adaptive_stable", "research_debug", "adaptive_classic"),
            "Unknown original acceptance mode; cannot infer stable guards")
    return mode


def source_stable_guards(step, attrs):
    """Replicate only necessary conjuncts under current stable-mode source."""
    if step <= 1:
        return {}
    improvement = value(attrs, "error_improvement")
    overshoot = value(attrs, "overshoot_ratio")
    underresolved = value(attrs, "underresolved_transition_fraction_real")
    underresolved_count = int(value(
        attrs, "underresolved_transition_patch_count_real"))
    imbalance = value(attrs, "transition_imbalance_max_real")
    penalty = value(attrs, "transition_coherence_penalty")
    if step == 2:
        return {
            "stable_step2_overshoot_ok":
                overshoot <= 1.22 or
                (improvement > 0.15 and underresolved <= 0.05
                 and imbalance <= 0.12),
            "transition_coherence_ok":
                underresolved_count == 0 and imbalance <= 0.12
                and penalty <= 0.20,
            "stable_transition_ready":
                underresolved <= 0.10 and imbalance <= 0.12,
        }
    transition_cap = 0.42 if step >= 4 else 0.25
    guards = {
        "stable_progressive_overshoot_ok":
            overshoot <= 1.28 or
            (improvement > 0.20 and underresolved <= 0.03
             and imbalance <= 0.10),
        "transition_coherence_ok": penalty <= transition_cap,
        "stable_transition_ready":
            underresolved <= (0.25 if step >= 4 else 0.10)
            and imbalance <= (0.18 if step >= 4 else 0.12),
    }
    return guards


def run(directory, root, engine_source):
    code = engine_source.read_text(encoding="utf-8")
    for anchor in SOURCE_ANCHORS:
        require(anchor in code, f"Historical acceptance source changed: {anchor}")
    old = directory / "r2c14_generator_rejection_forensics.json"
    data = json.loads(old.read_text(encoding="utf-8"))
    parent = json.loads((directory / "r2c13_accepted_generator_epochs.json")
                        .read_text(encoding="utf-8"))
    require(data["schema"] ==
            "apmesh.quad.r2c14.original_generator_rejection_forensics.v1"
            and parent["schema"] ==
            "apmesh.quad.r2c13.actual_production_generator_epochs.v1"
            and data["parent_r2c13_report_sha256"] ==
            digest(directory / "r2c13_accepted_generator_epochs.json")
            and parent["all_models_two_accepted_epochs"] is False,
            "Missing authenticated original rejected candidate provenance")

    result = {
        "schema": "apmesh.quad.r2c15.read_only_original_acceptance_guards.v1",
        "engine_source_sha256": digest(engine_source),
        "source_r2c14_report_sha256": digest(old),
        "source_r2c13_report_sha256":
            digest(directory / "r2c13_accepted_generator_epochs.json"),
        "models": {},
        "all_models_two_accepted_epochs": False,
        "original_scientific_approval": False,
        "production_acceptance_modified": False,
        "physical_source_nodes_welded": False,
    }
    for model, cases in data["models"].items():
        require(model in ("eistute", "book"), "Unexpected original model")
        parent_cases = {
            c["profile"]: c
            for c in parent["models"][model]["cases"]
        }
        evaluated = []
        for case in cases:
            profile = case["profile"]
            require(profile in parent_cases, "Unknown original runtime profile")
            mode = mode_from_source(root, model, parent_cases[profile])
            prefix = directory / f"{model}_{profile}" / f"{model}_{profile}"
            classified = []
            for candidate in case["rejected_original_candidates"]:
                step = candidate["step"]
                log = Path(str(prefix) +
                           f"_passo_{step}_acceptance_rejected.log")
                attrs = parse_key_values(log)
                require(digest(log) ==
                        candidate["rejected_acceptance_log_sha256"] and
                        attrs["step"] == str(step) and attrs["accepted"] == "0"
                        and attrs["acceptance_mode"] == "0",
                        "Cannot classify modified or non-mode-0 original candidate")
                for report_key, source_key in (
                    ("error_improvement_fraction", "error_improvement"),
                    ("original_element_growth_factor", "element_growth_factor"),
                    ("overshoot_ratio", "overshoot_ratio"),
                    ("transition_coherence_penalty",
                     "transition_coherence_penalty"),
                    ("transition_imbalance_max",
                     "transition_imbalance_max_real"),
                    ("underresolved_transition_fraction",
                     "underresolved_transition_fraction_real"),
                ):
                    require(same_number(candidate[report_key],
                                        value(attrs, source_key)),
                            "Original rejected candidate report/log metric mismatch")

                guards = (source_stable_guards(step, attrs)
                          if mode == "adaptive_stable" else {})
                failures = [key for key, outcome in guards.items()
                            if not outcome]
                classified.append({
                    "step": step,
                    "actual_status": "REJECTED_NOT_COMMITTED",
                    "original_adaptive_mode": mode,
                    "stable_guard_values": guards,
                    "source_proven_necessary_guard_failures": failures,
                    "some_original_conjunct_proven_false": bool(failures),
                    "precise_all_boolean_acceptance_gate_known": False,
                    "original_rejected_log_sha256": digest(log),
                    "candidate_overshoot_ratio":
                        value(attrs, "overshoot_ratio"),
                    "candidate_transition_penalty":
                        value(attrs, "transition_coherence_penalty"),
                    "candidate_underresolved_fraction":
                        value(attrs, "underresolved_transition_fraction_real"),
                })
            evaluated.append({
                "profile": profile,
                "mode": mode,
                "accepted_committed_source_epochs":
                    len(parent_cases[profile].get("accepted_step_ids", [])),
                "rejected_candidates": classified,
            })
        result["models"][model] = evaluated

    eistute = result["models"]["eistute"]
    ep = next(case for case in eistute if case["profile"] == "pinned_article")
    step4 = next(c for c in ep["rejected_candidates"] if c["step"] == 4)
    require("stable_progressive_overshoot_ok" in
            step4["source_proven_necessary_guard_failures"] and
            "transition_coherence_ok" in
            step4["source_proven_necessary_guard_failures"] and
            "stable_transition_ready" in
            step4["source_proven_necessary_guard_failures"],
            "Eistute step4 original original source stable safety gates changed")
    book = next(case for case in result["models"]["book"]
                if case["profile"] == "stable_small_increment")
    require(any(c["source_proven_necessary_guard_failures"]
                for c in book["rejected_candidates"] if c["step"] >= 2),
            "Book stable original transition/overshoot guards no longer fail")
    output = directory / "r2c15_original_acceptance_guard_inequalities.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("R2C15_REAL_SOURCE_GUARD_INEQUALITIES",
          json.dumps({
              model: {
                  case["profile"]: {
                      str(candidate["step"]):
                          candidate["source_proven_necessary_guard_failures"]
                      for candidate in case["rejected_candidates"]
                  }
                  for case in cases
              } for model, cases in result["models"].items()
          }, sort_keys=True),
          "accepted_second_original_generator_epoch=0",
          "production_acceptance_modified=0")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--engine-source", type=Path, required=True)
    args = parser.parse_args()
    run(args.directory.resolve(), args.root.resolve(),
        args.engine_source.resolve())


if __name__ == "__main__":
    main()
