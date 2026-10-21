#!/usr/bin/env python3
"""Prove the sampler edit is limited to storage, casts and local spelling.

This is a mechanical scope check in addition to actual numerical comparison.
It deliberately retains every arithmetic token, threshold, branch, argument,
sample order, accumulation order and final division in its identity.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re


def body(root):
    small = root / "src/estimate/curvature_sample_estimate.cpp"
    source = small if small.exists() else root / "src/estimate/charge_estimate_process.cpp"
    text = source.read_text(encoding="utf-8")
    first = text.index("double ChargeEstimateProcess::CalculateKaMedioPatch(")
    text = text[first:]
    if not small.exists():
        text = text[:text.index("double ChargeEstimateProcess::CalculateAreaPatch(")]
    return text


def normalize(text):
    if "new PointAdaptive()" in text:
        text, count = re.subn(
            r"PointAdaptive\* ponto_([a-z]) = new PointAdaptive\(\);\s*"
            r"PointAdaptive ponto_\1\1 = (patch->Parameterize\([^;]+\));\s*"
            r"ponto_\1 = &ponto_\1\1;", r"PointAdaptive sample_\1 = \2;", text)
        if count != 25:
            raise ValueError("Original sample construction layout changed")
        text, count = re.subn(r"\*\(static_cast<NodeAdaptive\*>\(ponto_([a-z])\)\)",
                             r"sample_\1", text)
        if count != 25:
            raise ValueError("Original derived cast layout changed")
        text = text.replace("*(static_cast<PatchCoons*>(patch))", "*patch")
        text = text.replace("double array_kam[points];", "std::array<double, 25> curvatures;")
        text = text.replace("array_kam", "curvatures")
        text = re.sub(r"\bk([a-z])_ponto_\1\b", r"curvature_\1", text)
        text = re.sub(r"\bka([a-z])\b", r"analytical_\1", text)
    text = re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S)
    # Only this existing early-return diagnostic is intentionally translated.
    text, count = re.subn(r'(if\s*\(points < 4\)\s*\{)\s*cout\s*<<.*?<<\s*endl;',
                         r'\1 DIAGNOSTIC;', text, flags=re.S)
    if count != 1:
        raise ValueError("Sampler diagnostic guard changed")
    return re.sub(r"\s+", "", text)


def audit(original_root, candidate_root):
    original, candidate = body(original_root), body(candidate_root)
    reference = normalize(original)
    if reference != normalize(candidate):
        raise ValueError("Sampler arithmetic/control/sample-order tokens changed")
    mutations = [candidate.replace("result / points", "result / i"),
                 candidate.replace("points >= 9", "points >= 8"),
                 candidate.replace("Parameterize(0.25, 0.25)", "Parameterize(0.75, 0.25)", 1),
                 candidate.replace("result += curvatures[j]", "result = curvatures[j] + result")]
    if len(set(mutations)) != 4 or any(text == candidate or normalize(text) == reference for text in mutations):
        raise ValueError("A numerical mutation escaped the independent token guard")
    return {"status": "passed", "sample_positions": 25, "rejected_mutations": 4,
            "original_sha256": hashlib.sha256(original.encode()).hexdigest(),
            "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
            "preserved_tokens_sha256": hashlib.sha256(reference.encode()).hexdigest(),
            "scope": "Only overwritten allocations/aliases, invalid derived casts, bounded scratch extent, local spelling, comments and the early diagnostic are normalized. Actual numerical traces are separately required."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.original_root, args.candidate_root)))
