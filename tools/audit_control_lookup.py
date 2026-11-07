#!/usr/bin/env python3
"""Prove the internal lookup borrows while the public value boundary remains."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from audit_control_reader import FILES, expand_borrowed_lookup, tokens

BASE = "ee677a34fd9c9303eb83b70d525c6b966c6a240f"


def verify(originals, candidates):
    if "PatchReader::FindControlPoint(" not in candidates[FILES[2]]:
        raise ValueError("Borrowed lookup is absent")
    expanded = expand_borrowed_lookup(candidates)
    for name in FILES:
        if tokens(expanded[name]) != tokens(originals[name]):
            raise ValueError("Lookup selection, value boundary or unrelated source changed: " + name)
    return {name: hashlib.sha256(json.dumps(tokens(expanded[name])).encode()).hexdigest() for name in FILES}


def audit(root):
    originals = {name: subprocess.check_output(["git", "show", BASE + ":" + name], cwd=root).decode("utf-8")
                 for name in FILES}
    candidates = {name: (root / name).read_text(encoding="utf-8") for name in FILES}
    hashes = verify(originals, candidates)
    mutations = [(FILES[0], "GetPointVectorControlPoints(std::vector<PointAdaptive>, unsigned long)",
                  "GetPointVectorControlPoints(const std::vector<PointAdaptive>&, unsigned long)"),
                 (FILES[0], "const std::vector<PointAdaptive>& vectorPoints", "std::vector<PointAdaptive> vectorPoints"),
                 (FILES[2], "const std::vector<PointAdaptive>& vectorPoints", "std::vector<PointAdaptive> vectorPoints"),
                 (FILES[2], "::const_iterator", "::iterator"),
                 (FILES[2], "(*it).GetId() == idPoint", "(*it).GetId() != idPoint"),
                 (FILES[2], "PointAdaptive ponto;", "PointAdaptive ponto(1, 2, 3);"),
                 (FILES[2], "FindControlPoint(vectorControlPoints, p[i])", "GetPointVectorControlPoints(vectorControlPoints, p[i])"),
                 (FILES[2], "return FindControlPoint(vectorPoints, idPoint);", "return PointAdaptive{};"),
                 (FILES[2], "return (*it);", "return PointAdaptive{};")]
    for name, before, after in mutations:
        if before not in candidates[name]:
            raise ValueError("Lookup mutation was not applied: " + before)
        changed = dict(candidates)
        changed[name] = changed[name].replace(before, after, 1)
        try:
            verify(originals, changed)
        except ValueError:
            continue
        raise ValueError("Lookup mutation escaped: " + before)
    return {"status": "passed", "base": BASE, "rejected_mutations": len(mutations),
            "expanded_tokens_sha256": hashes,
            "source_sha256": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in candidates.items()},
            "scope": "Only sixteen borrowed calls, private const-reference scan and public by-value delegate; first-match/default/return and every other token/literal preserved"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result))
