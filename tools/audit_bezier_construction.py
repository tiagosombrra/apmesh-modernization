#!/usr/bin/env python3
"""Verify constructor repairs preserve every original numerical/order token."""

import argparse
import hashlib
import json
from pathlib import Path
import re

from audit_bezier_observers import restore_patch_destructor


def code(text):
    text = re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*#include[^\n]*", "", text, flags=re.M)
    return re.sub(r"\s+", "", text)


def verify_patch(original, candidate):
    source = code(candidate)
    first = source.index("PatchBezier::PatchBezier(CurveAdaptive*curve1")
    second = source.index("PatchBezier::PatchBezier(constPointAdaptivept00", first)
    last = source.index("PatchBezier::~PatchBezier()", second)
    borrowed = source[first:second]
    fresh = source[second:last]
    scope = "apmesh::detail::PatchObserverScopeobserver_scope({curve1,curve2,curve3,curve4});"
    if not borrowed.split(":PatchCoons(){", 1)[1].startswith(scope):
        raise ValueError("Observer scope must precede publication")
    if not borrowed.endswith("observer_scope.Commit();}"):
        raise ValueError("Observer scope must cover the full constructor")
    if not fresh.endswith("for(auto&curve:pending_curves)curve.release();}"):
        raise ValueError("Fresh owners must cover the full constructor")
    source = source.replace(scope, "").replace("observer_scope.Commit();", "")
    declaration = "std::array<std::unique_ptr<CurveAdaptiveParametricBezier>,4>pending_curves{};"
    if source.count(declaration) != 1:
        raise ValueError("Fresh owner layout changed")
    source = source.replace(declaration, "")
    for index in range(4):
        pattern = (rf"pending_curves\[{index}\]=(CreateOrientedCurve\([^;]+\));"
                   rf"this->curves_\.push_back\(pending_curves\[{index}\]\.get\(\)\);")
        source, count = re.subn(pattern, r"this->curves_.push_back(\1);", source)
        if count != 1:
            raise ValueError("Curve creation/publication order changed")
    source = source.replace("for(auto&curve:pending_curves)curve.release();", "")
    source = source.replace("std::unique_ptr<CurveAdaptiveParametricBezier>CreateOrientedCurve",
                            "CurveAdaptiveParametricBezier*CreateOrientedCurve")
    source = source.replace("std::make_unique<CurveAdaptiveParametricBezier>(",
                            "newCurveAdaptiveParametricBezier(")
    # Ordinary retirement is independently checked by the observer gate. Retain
    # every constructor assertion and normalize only its exact destructor body.
    if restore_patch_destructor(source) != code(original):
        raise ValueError("Bezier numerical/control/remaining-unit tokens changed")
    return hashlib.sha256(source.encode()).hexdigest()


def scope_body(text):
    first = text.index("class PatchObserverScope")
    begin = text.index("{", first)
    depth = 0
    for index in range(begin, len(text)):
        depth += (text[index] == "{") - (text[index] == "}")
        if depth == 0:
            return code(text[first:index + 2])
    raise ValueError("Unclosed observer class")


def audit(original_root, candidate_root):
    path = "src/data/patch/patch_bezier.cpp"
    original = (original_root / path).read_text(encoding="utf-8")
    candidate = (candidate_root / path).read_text(encoding="utf-8")
    preserved = verify_patch(original, candidate)
    old_caller = (original_root / "src/estimate/charge_input_estimate.cpp").read_text(encoding="utf-8")
    new_caller = (candidate_root / "src/estimate/charge_input_estimate.cpp").read_text(encoding="utf-8")
    guard = (candidate_root / "include/data/patch/patch_observer_scope.h").read_text(encoding="utf-8")
    if scope_body(old_caller) != scope_body(guard):
        raise ValueError("Shared observer scope semantics changed")
    marker = "static bool SortByNt("
    if code(old_caller[old_caller.index(marker):]) != code(new_caller[new_caller.index(marker):].replace(
            "apmesh::detail::PatchObserverScope", "PatchObserverScope")):
        raise ValueError("Charge caller changed beyond scope qualification")
    header = "include/data/patch/patch_bezier.h"
    if code((original_root / header).read_text()) != code((candidate_root / header).read_text()):
        raise ValueError("Public Bezier class layout/API changed")
    declaration = "apmesh::detail::PatchObserverScope observer_scope({curve1, curve2, curve3, curve4});"
    mutations = [candidate.replace("pt00_, pt10_", "pt10_, pt00_", 1),
                 candidate.replace("this->GetB() * this->GetGx()", "this->GetGx() * this->GetB()", 1),
                 candidate.replace("signal_curve2;", "!signal_curve2;", 1),
                 candidate.replace("  observer_scope.Commit();", "", 1).replace(
                     declaration, declaration + "\n  observer_scope.Commit();", 1)]
    for mutation in mutations:
        if mutation == candidate:
            raise ValueError("Numerical/lifetime mutation was not applied")
        try:
            verify_patch(original, mutation)
        except ValueError:
            continue
        raise ValueError("A numerical/lifetime mutation escaped the independent guard")
    return {"status": "passed", "rejected_mutations": 4,
            "original_sha256": hashlib.sha256(original.encode()).hexdigest(),
            "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
            "preserved_tokens_sha256": preserved,
            "shared_scope_tokens_sha256": hashlib.sha256(scope_body(guard).encode()).hexdigest(),
            "scope": "Exact public API/layout, shared scope and caller semantics. All original Bezier unit tokens match after normalizing only includes/comments/spacing, owning factory/storage/publication, scope declarations/commits and the exact separately qualified ordinary retirement destructor. Commit/release positions are separately required to cover the entire constructors; four independent control/matrix/direction/early-commit mutations are rejected. The observer gate must separately reject its six lifetime/numerical mutations. Actual traces and instrument outcomes remain separately required."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.original_root, args.candidate_root)))
