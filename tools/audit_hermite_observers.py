#!/usr/bin/env python3
"""Guard completed Hermite observer retirement and preserve all other production tokens."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from audit_find_uv_recording import restore_find_uv_recording, validate_find_uv_header

from audit_hermite_construction import restore_hermite_construction

BASE = "6669a29e03e868ecaa781e6da2a5299a19ddeae5"
FILES = ["src/data/patch/patch_hermite.cpp", "include/data/patch/patch_hermite.h"]
DESTRUCTOR = ("PatchHermite::~PatchHermite(){for(auto*curve:curves_)"
              "if(curve!=nullptr)curve->RemovePatchObservers(this);}")
DECLARATION = "~PatchHermite()override;"
ORIGINAL_DECLARATION = "~PatchHermite()override=default;"


def code(text):
    text = restore_find_uv_recording(text)
    return re.sub(r"\s+", "", re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S))


def restore_hermite_retirement(source):
    """Older guards normalize only the exact independently checked implementation."""
    source = restore_hermite_construction(source)
    for before, after in [(DESTRUCTOR, ""), (DECLARATION, ORIGINAL_DECLARATION)]:
        if before in source:
            if source.count(before) != 1:
                raise ValueError("Duplicate Hermite retirement definition/declaration")
            source = source.replace(before, after, 1)
    return source


def verify(originals, candidates):
    preserved = {}
    for name, expected in zip(FILES, [DESTRUCTOR, DECLARATION]):
        source = code(candidates[name])
        if source.count(expected) != 1:
            raise ValueError("Missing or changed Hermite retirement contract: " + name)
        source = restore_hermite_retirement(source)
        if source != code(originals[name]):
            raise ValueError("Unexpected constructor/numerical/API/layout delta: " + name)
        preserved[name] = hashlib.sha256(source.encode()).hexdigest()
    return preserved


def audit(candidate_root, original_root=None):
    originals = {name: ((original_root / name).read_text(encoding="utf-8") if original_root else
                       subprocess.check_output(["git", "show", f"{BASE}:{name}"],
                                               cwd=candidate_root).decode("utf-8")) for name in FILES}
    candidates = {name: (candidate_root / name).read_text(encoding="utf-8") for name in FILES}
    validate_find_uv_header(candidate_root, candidates.values())
    preserved = verify(originals, candidates)
    mutations = [
        (FILES[0], "curve->RemovePatchObservers(this);", "curve->ClearPatches();"),
        (FILES[0], "curve->RemovePatchObservers(this);", "curve->RemovePatchObservers(nullptr);"),
        (FILES[0], "if (curve != nullptr)", "if (curve == nullptr)"),
        (FILES[0], "for (auto* curve : curves_)", "for (auto* curve : std::vector<CurveAdaptive*>{curves_.front()})"),
        (FILES[0], "PatchHermite::~PatchHermite() {", "PatchHermite::~PatchHermite() { auto scratch = curves_;"),
        (FILES[0], "u * u * u", "u * u"),
        (FILES[0], "this->pt00_ = patch_hermite->pt00_;", "this->pt00_ = patch_hermite->pt10_;"),
        (FILES[1], "bool signal_curve1 = true", "bool signal_curve1 = false"),
    ]
    for name, before, after in mutations:
        changed = dict(candidates)
        if before not in changed[name]:
            raise ValueError("Independent Hermite mutation was not applied")
        changed[name] = changed[name].replace(before, after, 1)
        try:
            verify(originals, changed)
        except ValueError:
            continue
        raise ValueError("Independent Hermite mutation escaped the guard")
    return {"status": "passed", "original_revision": BASE, "rejected_mutations": len(mutations),
            "preserved_tokens_sha256": preserved,
            "source_identities": {label: {name: hashlib.sha256(text.encode()).hexdigest()
                                          for name, text in files.items()}
                                  for label, files in [("original", originals), ("candidate", candidates)]},
            "finduv_recording": "Exact entry/I_MAX slots normalized after pinned helper validation",
            "scope": "Only the exact completed Hermite destructor declaration/body changes after normalizing "
                     "the separately guarded constructor rollback scope. Every other constructor, "
                     "numeric read/formula/order, public signature/layout, direction default and detached-copy "
                     "token otherwise matches immutable main. Eight independent lifetime, allocation, numeric, "
                     "control and direction mutations are rejected. Actual retirement/noallocation and "
                     "original/candidate traces remain required; constructor failure is not covered."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", type=Path, default=Path("."))
    parser.add_argument("--original-root", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.candidate_root, args.original_root)))
