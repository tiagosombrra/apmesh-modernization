#!/usr/bin/env python3
"""Guard the exact serial ownership/resource delta against immutable source."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from audit_control_reader import expand_shared_reader

BASE = "f9c7d22c0028e8864da4de5a05bdc19489da52bf"
FILES = ["include/input_output/patch_reader.h", "src/input_output/patch_reader.cpp",
         "include/input_output/input_validation.h"]


def code(text):
    text = re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*#include[^\n]*", "", text, flags=re.M)
    return re.sub(r"\s+", "", text)


def replace_once(text, new, old):
    if text.count(new) != 1:
        raise ValueError("Missing or changed exact ownership boundary: " + new)
    return text.replace(new, old, 1)


def verify(originals, candidates):
    hashes = {}
    for name in FILES:
        candidate = code(candidates[name])
        if name == FILES[0]:
            candidate = replace_once(candidate, "std::list<std::unique_ptr<PatchBezier>>LoaderBezierPatchFile(stringfileName);",
                                     "std::list<PatchBezier*>LoaderBezierPatchFile(stringfileName);")
        if name == FILES[1]:
            start = candidate.index("std::list<std::unique_ptr<PatchBezier>>PatchReader::LoaderBezierPatchFile(")
            end = candidate.index("Geometry*PatchReader::ReaderFilePatches(", start)
            part = candidate[start:end]
            part = replace_once(part, "std::list<std::unique_ptr<PatchBezier>>PatchReader::LoaderBezierPatchFile(",
                                "std::list<PatchBezier*>PatchReader::LoaderBezierPatchFile(")
            part = replace_once(part, "std::list<std::unique_ptr<PatchBezier>>patches;autopatch=std::make_unique<PatchBezier>();", "patch_=newPatchBezier();")
            part = replace_once(part, "patches.push_back(std::move(patch));patch=std::make_unique<PatchBezier>();",
                                "patches_.push_back(patch_);patch_=newPatchBezier();")
            part = replace_once(part, "returnpatches;", "returnpatches_;")
            if part.count("patch->SetPt") != 16 or part.count("iss.exceptions(std::ios::badbit);") != 2:
                raise ValueError("Control or resource-mask inventory changed")
            part = part.replace("patch->SetPt", "patch_->SetPt")
            part = part.replace("iss.exceptions(std::ios::badbit);", "")
            part = replace_once(part, "fin.exceptions(std::ios::badbit);", "")
            candidate = candidate[:start]+part+candidate[end:]
            candidate = replace_once(candidate, "autopatches=patch_reader.LoaderBezierPatchFile(file_name);",
                                     "std::list<PatchBezier*>patches=patch_reader.LoaderBezierPatchFile(file_name);")
            candidate = replace_once(candidate, "for(autoit=patches.begin();", "for(std::list<PatchBezier*>::iteratorit=patches.begin();")
            candidate = replace_once(candidate, "autopending_patch=std::make_unique<PatchBezier>(patch_c1,", "(*it)=newPatchBezier(patch_c1,")
            candidate = replace_once(candidate, "geometry->InsertPatch(std::move(pending_patch));", "geometry->InsertPatch((*it));")
        if candidate != code(originals[name]):
            raise ValueError("Unexpected API/layout/parser/validation/interning/direction/numerical delta: " + name)
        hashes[name] = hashlib.sha256(candidate.encode()).hexdigest()
    return hashes


def audit(candidate_root, original_root=None):
    originals = {name: ((original_root/name).read_text(encoding="utf-8") if original_root else
                       subprocess.check_output(["git", "show", f"{BASE}:{name}"],cwd=candidate_root).decode("utf-8")) for name in FILES}
    raw_candidates = {name: (candidate_root/name).read_text(encoding="utf-8") for name in FILES}
    control = "src/input_output/control_patch_reader.cpp"
    if (candidate_root/control).is_file():
        raw_candidates[control] = (candidate_root/control).read_text(encoding="utf-8")
    candidates = expand_shared_reader(raw_candidates)
    preserved = verify(originals, candidates)
    mutations = [("fin.exceptions(std::ios::badbit);", ""),
                 ("patch->SetPt10(", "patch->SetPt01("),
                 ("kBpControlMergeTol = 1e-7", "kBpControlMergeTol = 1e-6"),
                 ("UsesForwardControls(patch_c1,", "!UsesForwardControls(patch_c1,"),
                 ("geometry->InsertPatch(std::move(pending_patch));", "geometry->InsertPatch(pending_patch.get());"),
                 ("patches.push_back(std::move(patch));", "patches.push_back(std::unique_ptr<PatchBezier>(patch.get()));")]
    for before, after in mutations:
        if before not in candidates[FILES[1]]:
            raise ValueError("Independent mutation was not applied")
        changed = dict(candidates)
        changed[FILES[1]] = changed[FILES[1]].replace(before,after,1)
        try:
            verify(originals, changed)
        except ValueError:
            continue
        raise ValueError("Independent mutation escaped preservation guard")
    return {"status": "passed", "original_revision": BASE, "rejected_mutations": len(mutations),
            "preserved_tokens_sha256": preserved,
            "source_identities": {label: {name: hashlib.sha256(text.encode()).hexdigest() for name,text in files.items()}
                                  for label,files in [("original",originals),("candidate",raw_candidates)]},
            "shared_control_reader_expansion": candidates != raw_candidates,
            "scope": "Three historical files, with exact shared-reader expansion when present. Exact owning return/local result/pending handoff and three badbit masks only. Every other parser, validation, interning, orientation, public layout and numerical token matches immutable main. Shared helper/wrapper drift is also challenged by audit_control_reader. Normal paired traces and full fault instruments remain separate."}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root",type=Path,default=Path("."))
    parser.add_argument("--original-root",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=audit(args.candidate_root,args.original_root)
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result))
