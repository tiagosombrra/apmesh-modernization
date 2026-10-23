#!/usr/bin/env python3
"""Guard initialized detached patch copies while preserving all other production tokens."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from audit_hermite_observers import restore_hermite_retirement

BASE = "ace7abf0ce1b559d20b5c94f8e9120013c093f81"
FILES = ["src/data/patch/patch_bezier.cpp", "src/data/patch/patch_hermite.cpp",
         "include/data/patch/patch_bezier.h", "include/data/patch/patch_hermite.h"]
OLD_BEZIER = "PatchBezier::PatchBezier(PatchBezier* patch_bezier) : PatchCoons(patch_bezier) {"
NEW_BEZIER = """PatchBezier::PatchBezier(PatchBezier* patch_bezier)
    : PatchCoons(patch_bezier), mat_base_(StartBezierMatrix()), area_(0), ka_medio_(0),
      segment_medio_(0), area_triangle_(0), number_triangle_(0), id_process_(0), id_patch_bezier_(0) {"""
OLD_HERMITE = "PatchHermite::PatchHermite(PatchHermite* patch_hermite) : PatchCoons(patch_hermite) {"
NEW_HERMITE = """PatchHermite::PatchHermite(PatchHermite* patch_hermite)
    : PatchCoons(patch_hermite), signal_curve1_(true), signal_curve2_(true),
      signal_curve3_(true), signal_curve4_(true) {"""


def code(text):
    text = re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"\s+", "", text)


def restore_bezier_copy_initialization(source):
    """Legacy guards accept only this exact separately checked constructor prefix."""
    new, old = code(NEW_BEZIER), code(OLD_BEZIER)
    if new in source:
        if source.count(new) != 1:
            raise ValueError("Duplicate detached Bezier copy constructor")
        return source.replace(new, old, 1)
    return source


def verify(originals, candidates):
    hashes = {}
    for name in FILES:
        source = code(candidates[name])
        if name in [FILES[1], FILES[3]]:
            source = restore_hermite_retirement(source)
        if name == FILES[0]:
            if source.count(code(NEW_BEZIER)) != 1:
                raise ValueError("Detached Bezier initialization contract changed")
            source = restore_bezier_copy_initialization(source)
        elif name == FILES[1]:
            if source.count(code(NEW_HERMITE)) != 1:
                raise ValueError("Detached Hermite initialization contract changed")
            source = source.replace(code(NEW_HERMITE), code(OLD_HERMITE), 1)
        if source != code(originals[name]):
            raise ValueError("Unexpected patch numerical/control/topology/API/layout delta: " + name)
        hashes[name] = hashlib.sha256(source.encode()).hexdigest()
    return hashes


def audit(candidate_root, original_root=None):
    originals = {name: ((original_root/name).read_text(encoding="utf-8") if original_root else
                       subprocess.check_output(["git", "show", f"{BASE}:{name}"],
                                               cwd=candidate_root).decode("utf-8")) for name in FILES}
    candidates = {name: (candidate_root/name).read_text(encoding="utf-8") for name in FILES}
    preserved = verify(originals, candidates)
    mutations = [
        (FILES[0], "mat_base_(StartBezierMatrix())", "mat_base_(Matrix4x4::Zero())"),
        (FILES[0], "area_(0)", "area_(patch_bezier->area_)"),
        (FILES[1], "signal_curve1_(true)", "signal_curve1_(false)"),
        (FILES[0], "PatchCoons(patch_bezier)", "PatchCoons()"),
        (FILES[0], "this->pt03_ = patch_bezier->pt03_;", "this->pt03_ = patch_bezier->pt13_;"),
        (FILES[0], "this->mat_base_v_ = patch_bezier->mat_base_v_;",
         "this->mat_base_v_ = patch_bezier->mat_base_v_; curves_ = patch_bezier->curves_;"),
        (FILES[0], "signal_curve1_ = patch_bezier->signal_curve1_;",
         "signal_curve1_ = !patch_bezier->signal_curve1_;"),
        (FILES[0], "u * u * u", "u * u"),
    ]
    for name, before, after in mutations:
        changed = dict(candidates)
        if before not in changed[name]:
            raise ValueError("Independent patch-copy mutation was not applied")
        # area_(0) also occurs in the default constructor; mutate only the copy prefix.
        if before == "area_(0)":
            start = changed[name].index("PatchBezier::PatchBezier(PatchBezier*")
            changed[name] = changed[name][:start] + changed[name][start:].replace(before, after, 1)
        else:
            changed[name] = changed[name].replace(before, after, 1)
        try:
            verify(originals, changed)
        except ValueError:
            continue
        raise ValueError("Independent patch-copy mutation escaped the guard")
    return {"status": "passed", "original_revision": BASE, "rejected_mutations": len(mutations),
            "preserved_tokens_sha256": preserved,
            "source_identities": {label: {name: hashlib.sha256(text.encode()).hexdigest()
                                          for name, text in files.items()}
                                  for label, files in [("original", originals), ("candidate", candidates)]},
            "scope": "Only the exact Bezier copy basis/zero-metadata and Hermite copy true-direction initializers change; "
                     "the exact independently guarded completed Hermite retirement declaration/body is normalized. "
                     "Header code and all other complete-unit tokens, numerical order, source-field reads, detached "
                     "topology, signatures and layouts match immutable main. Eight independent basis, metadata-read, "
                     "direction, ID, control, topology, orientation and numerical mutations are rejected. "
                     "Actual initialized-value, incidence, nonallocation and original/candidate traces remain required."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", type=Path, default=Path("."))
    parser.add_argument("--original-root", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.candidate_root, args.original_root)))
