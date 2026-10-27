#!/usr/bin/env python3
"""Extract unchanged evaluator bodies for a narrow serial ownership probe.

The full historical generator translation unit contains variable-length arrays
unsupported by MSVC. This adapter retains the actual class, constructor and
serial evaluator bodies; it does not substitute a numerical implementation.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re


def extract(root, output):
    path = root / "src/generator/generator_adaptive.cpp"
    source = path.read_text(encoding="utf-8")
    constructor = "GeneratorAdaptive::GeneratorAdaptive() {}"
    assert source.count(constructor) == 1, "Constructor changed; review adapter scope"
    start = source.index("double GeneratorAdaptive::ErrorGlobal(")
    boundaries = list(re.finditer(
        r"^std::unique_ptr<Performer::IdManager>\s+GeneratorAdaptive::MakeIdManager\(",
        source, re.M))
    assert len(boundaries) == 1 and boundaries[0].start() > start, "Evaluator boundary changed"
    end = boundaries[0].start()
    evaluator = source[start:end].rstrip() + "\n"
    assert evaluator.endswith("return Nj;\n}\n"), "Evaluator boundary changed"
    charge_path = root / "src/estimate/charge_estimate_process.cpp"
    charge_source = charge_path.read_text(encoding="utf-8")
    charge_start = charge_source.index("ChargeEstimateProcess::ChargeEstimateProcess()")
    destructor = "ChargeEstimateProcess::~ChargeEstimateProcess() {}"
    charge_end = charge_source.index(destructor, charge_start) + len(destructor)
    charge_lifetime = charge_source[charge_start:charge_end].rstrip() + "\n\n"
    assert charge_lifetime.count("{}") == 2, "Estimator construction changed; review adapter scope"
    text = ('#include "generator/generator_adaptive.h"\n\n' + constructor + "\n\n" +
            charge_lifetime + evaluator)
    output.write_text(text, encoding="utf-8", newline="\n")
    record = {"source": str(path), "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "constructor_sha256": hashlib.sha256(constructor.encode()).hexdigest(),
              "evaluator_sha256": hashlib.sha256(evaluator.encode()).hexdigest(),
              "charge_lifetime_sha256": hashlib.sha256(charge_lifetime.encode()).hexdigest(),
              "adapter_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
              "scope": "Exact constructor/serial ErrorGlobal bodies and actual class layout; not the full generator TU, OpenMP evaluator or full process."}
    output.with_suffix(".json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(extract(arguments.root, arguments.output)))
