#!/usr/bin/env python3
"""Bounded model-bound sensitivity experiments on the original GeneratorAdaptive.

Only source discretization or Quadtree-depth inputs change in isolated
research configs. The native scientific TRI admission, rollback and source
curve ownership remain unchanged; a green CI is never two accepted epochs.
"""

import argparse
import json
from pathlib import Path

from test_r2c13_m7_accepted_epochs import MODELS, require, scenario


# Each one-variable experiment isolates a specific observed source bottleneck.
# No acceptance thresholds, error definitions or runtime TRI code are changed.
CASES = {
    "eistute": (
        ("curve_growth_stepn_1p5", {
            "CURVE_POINT_GROWTH_STEPN": "1.5",
        }),
        ("quadtree_stepn_depth3", {
            "PATCH_QUADTREE_DEPTH_STEPN": "3",
        }),
    ),
    "book": (
        ("debug_curve_growth_stepn_1p5", {
            "CURVE_POINT_GROWTH_STEPN": "1.5",
        }),
        ("stable_quadtree_stepn_depth2", {
            "ADAPTIVE_MODE": "adaptive_stable",
            "PATCH_QUADTREE_DEPTH_STEPN": "2",
        }),
    ),
}


def run(exe, root, directory):
    directory.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "apmesh.quad.r2c16.original_generator_controlled_profiles.v1",
        "protocol": "single_source_knob_research_profiles",
        "original_source_models_sha256_verified": True,
        "original_TRI_scientific_acceptance_modified": False,
        "original_1993_rule_approved": False,
        "physical_source_node_welding": False,
        "global_QUAD_AFT_mesh_accepted": False,
        "models": {},
    }
    for model, spec in MODELS.items():
        tests = []
        for name, override in CASES[model]:
            result = scenario(exe, root, directory, model, spec, name, override)
            require(result["model"] == model and
                    result["profile"] == name and result["overrides"] == override,
                    "Original GeneratorAdaptive experiment provenance changed")
            tests.append(result)
        report["models"][model] = {
            "scenarios": tests,
            "experiment_has_two_accepted_source_epochs": any(
                r["accepted_two_original_generator_epochs"] for r in tests),
            "real_committed_step_sets": [
                r.get("accepted_step_ids", []) for r in tests
            ],
        }
    report["both_models_have_controlled_two_accepted_source_epochs"] = all(
        r["experiment_has_two_accepted_source_epochs"]
        for r in report["models"].values()
    )
    output = directory / "r2c16_original_generator_controlled_profiles.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("R2C16_CONTROLLED_ORIGINAL_GENERATOR_SENSITIVITY",
          json.dumps({
              m: [{
                  "profile": r["profile"], "status": r["status"],
                  "accepted": r.get("accepted_committed_steps", 0),
                  "restored": r.get("rejected_restored_steps", 0),
                  "two_accepted": r["accepted_two_original_generator_epochs"]
              } for r in data["scenarios"]]
              for m, data in report["models"].items()
          }, sort_keys=True),
          "both_models_two_accepted=" +
          str(int(report["both_models_have_controlled_two_accepted_source_epochs"])),
          "production_TRI_acceptance_unchanged=1")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    run(args.exe.resolve(), args.root.resolve(), args.directory.resolve())


if __name__ == "__main__":
    main()
