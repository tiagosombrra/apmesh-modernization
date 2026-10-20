#!/usr/bin/env python3
"""Extract the original curvature sampler for bounded differential tests.

The original MSVC adapter changes only its VLA extent to 25: every indexed
access is inside points <= 25, and the populated prefix has at most 25 entries.
The GCC reference retains the original VLA. Neither adapter changes arithmetic,
the leaked allocations or the invalid derived casts under investigation.
"""

import argparse
import hashlib
import json
from pathlib import Path


def extract(root, output, fixed_extent=False):
    source = root / "src/estimate/charge_estimate_process.cpp"
    text = source.read_text(encoding="utf-8")
    destructor = "ChargeEstimateProcess::~ChargeEstimateProcess() {}"
    first = text.index("ChargeEstimateProcess::ChargeEstimateProcess()")
    lifetime = text[first:text.index(destructor, first) + len(destructor)]
    sampler = root / "src/estimate/curvature_sample_estimate.cpp"
    original = not sampler.exists()
    body = ""
    if original:
        first = text.index("double ChargeEstimateProcess::CalculateKaMedioPatch(")
        body = text[first:text.index("double ChargeEstimateProcess::CalculateAreaPatch(", first)]
        assert body.count("double array_kam[points];") == 1
        assert body.count("new PointAdaptive()") == 25
        if fixed_extent:
            body = body.replace("double array_kam[points];", "double array_kam[25];")
    result = '#include "estimate/charge_estimate_process.h"\n\n' + lifetime + "\n\n" + body
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result, encoding="utf-8", newline="\n")
    record = {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "original": original, "fixed_extent_adapter": original and fixed_extent,
              "sampler_sha256": hashlib.sha256(body.encode()).hexdigest(),
              "adapter_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
              "scope": "Exact lifetime; original sampler with only the explicitly selected VLA extent adaptation. Current sampler is compiled from its actual unit."}
    output.with_suffix(".json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixed-extent", action="store_true")
    args = parser.parse_args()
    print(json.dumps(extract(args.root, args.output, args.fixed_extent)))
