#!/usr/bin/env python3
"""Inventory potential literal includes and validate source-backed review anchors.

This is a lexical development tool, not a preprocessor, ownership analyzer or
proof of runtime reachability. Conditional branches are intentionally retained.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = {".h", ".hh", ".hpp", ".hxx", ".inc", ".inl", ".cpp", ".cc", ".cxx"}
TRANSLATION_UNITS = {".cpp", ".cc", ".cxx"}
COMMENTS = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', re.S)
INCLUDES = re.compile(r'^[ \t]*#[ \t]*include[ \t]*(["<])([^">\n]+)[">]', re.M)


def remove_comments(text):
    """Preserve string literals and line numbers while removing ordinary comments."""
    return COMMENTS.sub(lambda match: re.sub(r"[^\n]", " ", match[0])
                        if match[0].startswith(("//", "/*")) else match[0], text)


def source_files(root):
    paths = []
    for folder in ("include", "src"):
        directory = root / folder
        if not directory.is_dir():
            raise ValueError(f"Missing source root: {folder}")
        selected = []
        for path in directory.rglob("*"):
            if path.is_symlink():
                raise ValueError(f"Symbolic links cannot establish source coverage: {path}")
            if path.is_file() and path.suffix in SUFFIXES:
                selected.append(path)
        if not selected:
            raise ValueError(f"Empty source root: {folder}")
        paths.extend(selected)
    return sorted(paths)


def component(name):
    path = Path(name)
    parent = Path(*path.parts[1:]).parent.as_posix()
    return "cli" if parent == "." else parent


def cycles(graph):
    """Return deterministic strongly connected sets in the potential include graph."""
    indices, low, stack, active, result = {}, {}, [], set(), []

    def visit(node):
        indices[node] = low[node] = len(indices)
        stack.append(node)
        active.add(node)
        for other in sorted(graph[node]):
            if other not in indices:
                visit(other)
                low[node] = min(low[node], low[other])
            elif other in active:
                low[node] = min(low[node], indices[other])
        if low[node] == indices[node]:
            group = []
            while True:
                member = stack.pop()
                active.remove(member)
                group.append(member)
                if member == node:
                    break
            if len(group) > 1 or node in graph[node]:
                result.append(sorted(group))

    for node in sorted(graph):
        if node not in indices:
            visit(node)
    return sorted(result)


def inventory(root):
    root = root.resolve()
    paths = source_files(root)
    names = {path.relative_to(root).as_posix() for path in paths}
    graph = {name: set() for name in names}
    files, cross_component, unresolved = [], Counter(), Counter()
    for path in paths:
        name = path.relative_to(root).as_posix()
        data = path.read_bytes()
        text = remove_comments(data.decode("utf-8"))
        includes = []
        for match in INCLUDES.finditer(text):
            form, spelling = match.groups()
            candidates = ([path.parent / spelling] if form == '"' else [])
            candidates += [root / "include" / spelling, root / spelling]
            target = None
            for candidate in candidates:
                candidate = candidate.resolve()
                if candidate.is_relative_to(root) and candidate.is_file():
                    target = candidate.relative_to(root).as_posix()
                    break
            scope = ("first_party" if target in names else
                     "vendor" if target and target.startswith("libs/") else
                     "repository_other" if target else "toolchain_or_unresolved")
            item = {"line": text.count("\n", 0, match.start()) + 1,
                    "spelling": spelling, "form": "quote" if form == '"' else "angle",
                    "scope": scope, "target": target}
            includes.append(item)
            if scope == "first_party":
                graph[name].add(target)
                if component(name) != component(target):
                    cross_component[(component(name), component(target))] += 1
            elif target is None:
                unresolved[spelling] += 1
        files.append({"path": name, "component_by_directory": component(name),
                      "kind": "translation_unit" if path.suffix in TRANSLATION_UNITS else "header",
                      "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                      "includes": includes})
    build_paths = [root / "CMakeLists.txt", root / "CMakePresets.json"]
    build_paths.extend(sorted((root / "cmake").glob("*.cmake")))
    build_inputs = [{"path": path.relative_to(root).as_posix(),
                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                    for path in build_paths if path.is_file()]
    return {"schema": "apmesh-source-inventory-v1",
            "scope": "all first-party include/src C++ files; potential literal includes, all conditions",
            "limitations": ["No preprocessor or raw-string grammar expansion",
                            "No system include search, ownership inference or runtime proof",
                            "Directory components describe source organization, not semantic layers"],
            "summary": {"files": len(files), "translation_units": sum(f["kind"] == "translation_unit" for f in files),
                        "headers": sum(f["kind"] == "header" for f in files),
                        "directory_components": dict(sorted(Counter(f["component_by_directory"] for f in files).items())),
                        "literal_include_directives": sum(len(f["includes"]) for f in files),
                        "first_party_include_edges": sum(len(targets) for targets in graph.values())},
            "cross_component_directives": [{"from": a, "to": b, "count": count}
                                           for (a, b), count in sorted(cross_component.items())],
            "potential_include_cycles": cycles(graph),
            "toolchain_or_unresolved_headers": dict(sorted(unresolved.items())),
            "build_inputs": build_inputs, "files": files}


def validate_contracts(root, document, known_paths):
    """Check traceability only; the human interpretation still needs code review."""
    root = root.resolve()
    if document.get("schema") != "apmesh-architecture-contracts-v1" or not document.get("contracts"):
        raise ValueError("Missing contract schema or empty contract coverage")
    ids, evidence_count = set(), 0
    for contract in document["contracts"]:
        identifier = contract.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in ids:
            raise ValueError("Missing or duplicate contract identity")
        ids.add(identifier)
        if not contract.get("statement") or not contract.get("limits") or not contract.get("evidence"):
            raise ValueError(f"Incomplete semantic contract: {identifier}")
        for item in contract["evidence"]:
            name, anchor = item.get("path"), item.get("anchor")
            if not isinstance(name, str) or name not in known_paths:
                raise ValueError(f"Unknown source/build evidence path: {name}")
            path = (root / name).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError(f"Invalid evidence path: {name}")
            if not isinstance(anchor, str) or not anchor or anchor not in path.read_text(encoding="utf-8"):
                raise ValueError(f"Missing source anchor for {identifier}: {name}")
            evidence_count += 1
    return {"contracts": len(ids), "source_anchors": evidence_count,
            "scope": "source anchors exist; semantic statements require independent review"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="Fail if the retained inventory differs")
    parser.add_argument("--contracts", type=Path)
    args = parser.parse_args()
    result = inventory(args.root)
    if args.contracts:
        result["contract_traceability"] = validate_contracts(
            args.root, json.loads(args.contracts.read_text(encoding="utf-8")),
            {f["path"] for f in result["files"] + result["build_inputs"]})
    if args.check:
        if json.loads(args.output.read_text(encoding="utf-8")) != result:
            raise ValueError("Retained architecture inventory is stale or incomplete")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "passed", **result["summary"],
                      "potential_include_cycles": len(result["potential_include_cycles"]),
                      "contract_traceability": result.get("contract_traceability")}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, UnicodeError) as error:
        raise SystemExit(f"Architecture inventory failed: {error}")
