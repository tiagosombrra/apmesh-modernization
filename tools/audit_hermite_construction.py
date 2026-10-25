#!/usr/bin/env python3
"""Guard Hermite constructor rollback without changing numerical or publication order."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = "8eff0d6c4d69bb413674b003a22e49c3c6faca46"
FILE = "src/data/patch/patch_hermite.cpp"
INCLUDE = '#include"data/patch/patch_observer_scope.h"'
SCOPE = "apmesh::detail::PatchObserverScopeobserver_scope({curve1,curve2,curve3,curve4});"
COMMIT = "observer_scope.Commit();"
START = "boolsignal_curve4):PatchCoons(){"
END = "this->mat_geo_gz_=this->GetH()*this->GetGz()*this->GetH().transpose();"


def code(text):
    return re.sub(r"\s+", "", re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S))


def restore_hermite_construction(source):
    """Normalize only the complete, exactly located, independently guarded delta."""
    if not any(token in source for token in [INCLUDE, SCOPE, COMMIT]):
        return source
    if any(source.count(token) != 1 for token in [INCLUDE, SCOPE, COMMIT]):
        raise ValueError("Missing or duplicate Hermite constructor rollback token")
    if START + SCOPE not in source or END + COMMIT + "}" not in source:
        raise ValueError("Hermite rollback must span the complete constructor body")
    for token in [INCLUDE, SCOPE, COMMIT]:
        source = source.replace(token, "", 1)
    return source


def verify(original, candidate):
    source = code(candidate)
    restored = restore_hermite_construction(source)
    if restored == source or restored != code(original):
        raise ValueError("Unexpected Hermite constructor/numerical/publication delta")
    return hashlib.sha256(restored.encode()).hexdigest()


def audit(candidate_root, original_root=None):
    original = ((original_root / FILE).read_text(encoding="utf-8") if original_root else
                subprocess.check_output(["git", "show", f"{BASE}:{FILE}"], cwd=candidate_root).decode("utf-8"))
    candidate = (candidate_root / FILE).read_text(encoding="utf-8")
    preserved = verify(original, candidate)
    source = code(candidate)
    mutations = [
        (SCOPE, ""), (COMMIT, ""),
        (SCOPE, SCOPE + COMMIT),
        (SCOPE, SCOPE.replace("curve4", "curve3")),
        (SCOPE, SCOPE + "auto scratch=curves_;"),
        (END + COMMIT, COMMIT + END),
        ("curve2)->InsertPatch(this);", "curve1)->InsertPatch(this);"),
        ("u*u*u", "u*u"),
    ]
    for before, after in mutations:
        if before not in source:
            raise ValueError("Independent constructor mutation was not applied")
        try:
            verify(original, source.replace(before, after, 1))
        except ValueError:
            continue
        raise ValueError("Independent constructor mutation escaped")
    return {"status": "passed", "original_revision": BASE, "rejected_mutations": len(mutations),
            "preserved_tokens_sha256": preserved,
            "scope": "Only the observer scope include, entry guard and terminal commit change. "
                     "Live nonnull Hermite curves and exclusive append-only publication are required. "
                     "No foreign publication or intermediate consumption of a pending patch is supported."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-root", type=Path, default=Path("."))
    parser.add_argument("--original-root", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.candidate_root, args.original_root)))
