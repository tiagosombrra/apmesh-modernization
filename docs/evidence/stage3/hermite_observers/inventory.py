"""Inventory literal Hermite constructors and possible observer consumers, without alias proof."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = '21542d8e739d98604b68fa92414332c694f4642d'


def mask(text):
    pattern = r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    return re.sub(pattern, lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), text)


def expression(text, start):
    depth, cursor = 1, start
    while depth and cursor < len(text):
        depth += (text[cursor] == '(') - (text[cursor] == ')')
        cursor += 1
    assert depth == 0
    return text[start:cursor - 1].strip()


def inventory():
    constructors = re.compile(r'\b(?:new\s+PatchHermite\s*\('
                              r'|(?:std::)?make_unique\s*<\s*PatchHermite\s*>\s*\('
                              r'|MakePatch\s*<\s*PatchHermite\s*>\s*\()')
    patterns = {
        'constructions': constructors,
        'patch_getter_spellings': re.compile(r'\bGetPatch\s*\('),
        'observer_api_spellings': re.compile(r'\b(?:InsertPatch|RemovePatchObservers|ClearPatches|'
                                           r'TruncatePatchObservers|ReplaceCurve)\s*\('),
        'hermite_loader_spellings': re.compile(r'\bLoaderBPFileHermite\s*\('),
        'base_square_model_spellings': re.compile(r'\bModelBaseQuadrada\s*\(')}
    rows = {name: [] for name in patterns}
    inputs = {}
    names = subprocess.check_output(['git', 'ls-files', 'src', 'include'], cwd=ROOT, text=True).splitlines()
    for name in names:
        path = ROOT / name
        if path.suffix not in {'.cpp', '.h', '.hpp'}:
            continue
        text = path.read_text(encoding='utf-8')
        clean = mask(text)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        for category, pattern in patterns.items():
            for match in pattern.finditer(clean):
                line = clean.count('\n', 0, match.start()) + 1
                row = {'path': name, 'line': line, 'source': text.splitlines()[line - 1].strip(),
                       'arguments': expression(clean, match.end()), 'file_sha256': digest}
                if category == 'constructions':
                    functions = list(re.finditer(r'^Geometry\* Models3d::(\w+)\(', clean[:match.start()], re.M))
                    row['enclosing_model'] = functions[-1].group(1) if functions else None
                rows[category].append(row)
                inputs[name] = digest
        if re.search(r'\bPatchHermite\b', clean):
            inputs[name] = digest
    header = mask((ROOT / 'include/data/patch/patch_hermite.h').read_text(encoding='utf-8'))
    implementation = mask((ROOT / 'src/data/patch/patch_hermite.cpp').read_text(encoding='utf-8'))
    assert '~PatchHermite() override = default;' in header
    assert len(re.findall(r'static_cast<CurveAdaptiveParametricHermite\*>\(curve[1-4]\)->InsertPatch\(this\)',
                          implementation)) == 4
    assert not re.search(r'\b(?:RemovePatchObservers|PatchObserverScope|TruncatePatchObservers)\b', implementation)
    return {
        'source_base': BASE, 'classification': 'engineering-only literal source audit',
        'construction_count': len(rows['constructions']),
        'construction_counts': dict(sorted(Counter(r['path'] for r in rows['constructions']).items())),
        'model_construction_counts': dict(sorted(Counter(r['enclosing_model'] for r in rows['constructions']
                                                        if r['enclosing_model']).items())),
        **rows, 'input_files': dict(sorted(inputs.items())),
        'source_observations': [
            'Four ordered reciprocal constructor publications; default derived/base destructors do not deregister.',
            'No Hermite constructor observer rollback scope is present; failed construction remains unmeasured.',
            'Models3d MakePatch owns the pending result and consumes it through Geometry adoption.',
            'Geometry has no individual patch erasure API; complete destruction retires patches before curves.',
            'GetPatch spellings include geometry, mesh and curve APIs, declarations and definitions; manual context is required.'],
        'limits': 'Comments and quoted literals are masked while preserving line offsets. This is a literal '
                  'inventory, not a C++ parser, alias/macro/template-instantiation proof or executed caller coverage. '
                  'Generic GetPatch spellings are potential review roots, not all Hermite consumers. No serial CLI failure is inferred.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('callers.json'))
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = inventory()
    if args.check:
        assert json.loads(args.output.read_text(encoding='utf-8')) == report
    else:
        args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: report[k] for k in ['construction_count', 'construction_counts', 'model_construction_counts']}))
    print(json.dumps({k: len(report[k]) for k in ['patch_getter_spellings', 'observer_api_spellings',
                                               'hermite_loader_spellings', 'base_square_model_spellings']}))


if __name__ == '__main__':
    main()
