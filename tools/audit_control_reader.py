#!/usr/bin/env python3
"""Expand only the shared control reader and compare literal-preserving tokens."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = "bccd5c1e7af3c058f62085f8fb908f5ccd5db78b"
FILES = ("include/input_output/patch_reader.h", "src/input_output/patch_reader.cpp",
         "src/input_output/control_patch_reader.cpp")
TOKEN = re.compile(r'\s+|//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|'
                   r'[A-Za-z_]\w*|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|::|->|\+\+|--|&&|\|\||'
                   r'==|!=|<=|>=|<<|>>|\+=|-=|\*=|/=|.', re.S)
DECLARATION = ("private: std::list<std::unique_ptr<PatchBezier>> "
               "ReadBezierControlPatches(const std::string& filename, const char* empty_message);")


def tokens(text):
    return [m.group() for m in TOKEN.finditer(text)
            if not m.group().isspace() and not m.group().startswith(("//", "/*"))]


def function(text, name, result_type=r"std::list<std::unique_ptr<PatchBezier>>"):
    pattern = result_type + r"\s+PatchReader::" + name + r"\s*\([^)]*\)\s*\{"
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        raise ValueError("Missing or duplicate control reader: " + name)
    match = matches[0]
    opening, depth = match.end() - 1, 0
    for token in TOKEN.finditer(text, opening):
        if token.group() == "{":
            depth += 1
        elif token.group() == "}":
            depth -= 1
            if depth == 0:
                return match.start(), token.end(), text[opening + 1:token.start()], text[match.start():opening]
    raise ValueError("Incomplete control reader: " + name)


def rename(body, names):
    return "".join(names.get(m.group(), m.group()) for m in TOKEN.finditer(body))


def expand_borrowed_lookup(sources):
    result = dict(sources)
    control = result.get(FILES[2], "")
    if "PatchReader::FindControlPoint(" not in control:
        return result
    start, end, body, signature = function(control, "FindControlPoint", "PointAdaptive")
    expected = ("PointAdaptive PatchReader::FindControlPoint("
                "const std::vector<PointAdaptive>& vectorPoints, unsigned long idPoint)")
    if tokens(signature) != tokens(expected) or body.count("std::vector<PointAdaptive>::const_iterator") != 1:
        raise ValueError("Borrowed lookup signature or const iteration changed")
    legacy = body.replace("std::vector<PointAdaptive>::const_iterator", "std::vector<PointAdaptive>::iterator")
    control = control[:start] + control[end:]
    start, end, wrapper, signature = function(control, "GetPointVectorControlPoints", "PointAdaptive")
    if tokens(wrapper) != tokens("return FindControlPoint(vectorPoints, idPoint);"):
        raise ValueError("Public lookup compatibility delegate changed")
    control = control[:start] + signature + "{" + legacy + "}" + control[end:]
    start, end, shared, signature = function(control, "ReadBezierControlPatches")
    if tokens(shared).count("FindControlPoint") != 16 or "GetPointVectorControlPoints" in tokens(shared):
        raise ValueError("All sixteen internal control lookups must borrow")
    shared = rename(shared, {"FindControlPoint": "GetPointVectorControlPoints"})
    result[FILES[2]] = control[:start] + signature + "{" + shared + "}" + control[end:]
    header = result[FILES[0]]
    declarations = list(re.finditer(r"static\s+PointAdaptive\s+FindControlPoint\([^;]*\);", header))
    expected = ("static PointAdaptive FindControlPoint("
                "const std::vector<PointAdaptive>& vectorPoints, unsigned long idPoint);")
    if len(declarations) != 1 or tokens(declarations[0].group()) != tokens(expected):
        raise ValueError("Borrowed lookup declaration changed")
    declaration = declarations[0]
    result[FILES[0]] = header[:declaration.start()] + header[declaration.end():]
    return result


def expand_shared_reader(sources):
    """Return an inline view for the unchanged historical ownership oracle."""
    result = expand_borrowed_lookup(sources)
    control = result.get(FILES[2], "")
    if "PatchReader::ReadBezierControlPatches(" not in control:
        return result
    start, end, body, signature = function(control, "ReadBezierControlPatches")
    expected = ("std::list<std::unique_ptr<PatchBezier>> PatchReader::ReadBezierControlPatches("
                "const std::string& filename, const char* empty_message)")
    if tokens(signature) != tokens(expected):
        raise ValueError("Shared reader signature changed")
    result[FILES[2]] = control[:start] + control[end:]
    header = result[FILES[0]]
    declaration = re.search(r"private:\s*std::list<std::unique_ptr<PatchBezier>>\s*"
                            r"ReadBezierControlPatches\([^;]*\);", header)
    if not declaration or tokens(declaration.group()) != tokens(DECLARATION):
        raise ValueError("Shared reader declaration or access changed")
    result[FILES[0]] = header[:declaration.start()] + header[declaration.end():]
    for file, name, parameter, diagnostic, validate in (
            (FILES[2], "LoaderBPFile", "filename", '"Error opening the .bp file"', ""),
            (FILES[1], "LoaderBezierPatchFile", "fileName", '"Erro ao abrir o arquivo .bp"',
             "apmesh::io::ValidateBezierPatchInput(fileName);")):
        source = result[file]
        start, end, wrapper, signature = function(source, name)
        if tokens(wrapper) != tokens(validate + "return ReadBezierControlPatches(" + parameter + "," + diagnostic + ");"):
            raise ValueError("Public control reader validation/diagnostic delegate changed")
        expanded = rename(body, {"filename": parameter, "empty_message": diagnostic})
        result[file] = source[:start] + signature + "{" + validate + expanded + "}" + source[end:]
    return result


def originals(root):
    return {name: subprocess.check_output(["git", "show", BASE + ":" + name], cwd=root).decode("utf-8")
            for name in FILES}


def verify(reference, candidates):
    if "PatchReader::ReadBezierControlPatches(" not in candidates[FILES[2]]:
        raise ValueError("Shared implementation is absent")
    expanded = expand_shared_reader(candidates)
    for name in FILES:
        if tokens(reference[name]) != tokens(expanded[name]):
            raise ValueError("Unexpected parser/API/lookup/resource/diagnostic delta: " + name)
    return {name: hashlib.sha256(json.dumps(tokens(expanded[name])).encode()).hexdigest() for name in FILES}


def audit(root):
    reference = originals(root)
    candidates = {name: (root / name).read_text(encoding="utf-8") for name in FILES}
    proof = verify(reference, candidates)
    mutations = [(FILES[2], "patch->SetPt10(", "patch->SetPt01("),
                 (FILES[2], "fin.exceptions(std::ios::badbit);", ""),
                 (FILES[2], "patches.push_back(std::move(patch));", "patches.push_front(std::move(patch));"),
                 (FILES[2], '"Error opening the .bp file"', '"Error  opening the .bp file"'),
                 (FILES[1], "apmesh::io::ValidateBezierPatchInput(fileName);", ""),
                 (FILES[1], 'return ReadBezierControlPatches(fileName, "Erro ao abrir o arquivo .bp");',
                  'return ReadBezierControlPatches(fileName, "Error opening the .bp file");'),
                 (FILES[0], "const char* empty_message", "std::string empty_message"),
                 (FILES[2], "long id_ponto = 0;", "long id_ponto = 1;")]
    for name, before, after in mutations:
        if candidates[name].count(before) != 1:
            raise ValueError("Mutation admission failed: " + before)
        changed = dict(candidates)
        changed[name] = changed[name].replace(before, after, 1)
        try:
            verify(reference, changed)
        except ValueError:
            continue
        raise ValueError("Control reader mutation escaped: " + before)
    return {"status": "passed", "base": BASE, "rejected_mutations": len(mutations),
            "expanded_tokens_sha256": proof,
            "candidate_sha256": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in candidates.items()},
            "scope": "One private reader expansion; both wrapper policies and every other token, including string literals, match the immutable entry source"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.root)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result))
