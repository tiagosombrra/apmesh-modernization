#!/usr/bin/env python3
"""Check the bounded observer/Geometry delta and reject independent mutations."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from audit_find_uv_recording import restore_find_uv_recording, validate_find_uv_header

from audit_patch_copy import restore_bezier_copy_initialization


BASE = "061223689ad6d2caa15243dbcfa6a4e45ba7ce96"
FILES = ["include/data/curve/curve_adaptive.h", "include/data/geometry.h",
         "include/data/patch/patch_bezier.h", "src/data/curve/curve_adaptive.cpp",
         "src/data/geometry.cpp", "src/data/patch/patch_bezier.cpp"]
EMPTY_DESTRUCTOR = "PatchBezier::~PatchBezier(){}"
RETIRED_DESTRUCTOR = ("PatchBezier::~PatchBezier(){for(auto*curve:curves_)"
                      "if(curve!=nullptr)curve->RemovePatchObservers(this);}")


def code(text):
    text = restore_find_uv_recording(text)
    text = re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*#include[^\n]*", "", text, flags=re.M)
    return re.sub(r"\s+", "", text)


def restore_patch_destructor(source):
    """Normalize only the exact separately qualified retirement implementation."""
    if RETIRED_DESTRUCTOR in source:
        if source.count(RETIRED_DESTRUCTOR) != 1:
            raise ValueError("Duplicate Bezier retirement destructor")
        return source.replace(RETIRED_DESTRUCTOR, EMPTY_DESTRUCTOR)
    return source


def verify(originals, candidates):
    removal = ("voidCurveAdaptive::RemovePatchObservers(constPatch*patch)noexcept{"
               "patches_.erase(std::remove(patches_.begin(),patches_.end(),patch),patches_.end());}")
    assignment = ("Geometry&Geometry::operator=(Geometry&&other)noexcept{"
                  "if(this==&other)return*this;Geometryincoming(std::move(other));"
                  "points_.swap(incoming.points_);vectors_.swap(incoming.vectors_);"
                  "curves_.swap(incoming.curves_);patches_.swap(incoming.patches_);return*this;}")
    allowed = {
        FILES[0]: ("voidRemovePatchObservers(constPatch*patch)noexcept;", ""),
        FILES[3]: (removal, ""),
        FILES[4]: (assignment, "Geometry&Geometry::operator=(Geometry&&)noexcept=default;"),
        FILES[5]: (RETIRED_DESTRUCTOR, EMPTY_DESTRUCTOR),
    }
    hashes = {}
    for name in FILES:
        original, candidate = code(originals[name]), code(candidates[name])
        if name == FILES[5]:
            candidate = restore_bezier_copy_initialization(candidate)
        if name in allowed:
            new, old = allowed[name]
            if candidate.count(new) != 1:
                raise ValueError(f"Missing or changed bounded implementation: {name}")
            candidate = candidate.replace(new, old)
        if original != candidate:
            raise ValueError(f"Unexpected API/layout/numerical/caller delta: {name}")
        hashes[name] = hashlib.sha256(candidate.encode()).hexdigest()
    return hashes


def audit(candidate_root, original_root=None):
    originals = {name: ((original_root / name).read_text(encoding="utf-8") if original_root
                       else subprocess.check_output(["git", "show", f"{BASE}:{name}"],
                            cwd=candidate_root).decode("utf-8")) for name in FILES}
    candidates = {name: (candidate_root / name).read_text(encoding="utf-8") for name in FILES}
    validate_find_uv_header(candidate_root, candidates.values())
    preserved = verify(originals, candidates)
    # Each control changes a different preservation or lifetime obligation.
    mutations = [
        (FILES[5], "curve->RemovePatchObservers(this);", "curve->ClearPatches();"),
        (FILES[3], "std::remove(", "std::find("),
        (FILES[4], "Geometry incoming(std::move(other));", "curves_.clear(); Geometry incoming(std::move(other));"),
        (FILES[5], "this->GetB() * this->GetGx()", "this->GetGx() * this->GetB()"),
        (FILES[5], "signal_curve2;", "!signal_curve2;"),
        (FILES[4], "return *this;", "return other;"),
    ]
    for name, before, after in mutations:
        changed = dict(candidates)
        if before not in changed[name]:
            raise ValueError("Independent mutation was not applied")
        changed[name] = changed[name].replace(before, after, 1)
        try:
            verify(originals, changed)
        except ValueError:
            continue
        raise ValueError("An independent mutation escaped the preservation guard")
    return {"status": "passed", "original_revision": BASE if not original_root else None,
            "rejected_mutations": len(mutations), "preserved_tokens_sha256": preserved,
            "source_identities": {label: {name: hashlib.sha256(text.encode()).hexdigest()
                                          for name, text in files.items()}
                                  for label, files in [("original", originals), ("candidate", candidates)]},
            "finduv_recording": "Exact entry/I_MAX slots normalized after pinned helper validation",
            "scope": "Six actual production files. Only the exact observer-removal declaration/body, "
                     "completed Bezier destructor, Geometry dependent retirement assignment and exact separately "
                     "checked detached-copy initialization prefix are normalized. "
                     "All other numerical, constructor, API/layout and method tokens must match immutable main. "
                     "Six independent lifetime/numerical mutations must be rejected. Dynamic safety, normal "
                     "traces and allocation-free teardown remain separate required gates."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", type=Path, default=Path("."))
    parser.add_argument("--original-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.candidate_root, args.original_root)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result))
