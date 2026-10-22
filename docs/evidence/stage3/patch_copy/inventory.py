"""Inventory literal patch construction routes without interpreting them as complete clone calls."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = 'b48070fa733e09b3b5974f00616dc7da968b881d'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mask(text):
    # Keep character and line offsets. This is a literal inventory, not a C++ parser.
    pattern = r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    return re.sub(pattern, lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), text)


def arguments(text, start):
    depth = 1
    end = start
    while depth:
        depth += (text[end] == '(') - (text[end] == ')')
        end += 1
    content = text[start:end - 1]
    nesting = 0
    arity = int(bool(content.strip()))
    for char in content:
        if char in '([{':
            nesting += 1
        elif char in ')]}':
            nesting -= 1
        elif char == ',' and nesting == 0:
            arity += 1
    return end, arity


def inventory():
    construction = re.compile(r'\b(?:new\s+Patch(?:Bezier|Hermite)\s*\('
                              r'|(?:std::)?make_unique\s*<\s*Patch(?:Bezier|Hermite)\s*>\s*\('
                              r'|MakePatch\s*<\s*Patch(?:Bezier|Hermite)\s*>\s*\()')
    direct = re.compile(r'\bPatch(?:Bezier|Hermite|Coons)\s*\(')
    named = re.compile(r'\bPatch(?:Bezier|Hermite)\s+\w+\s*[({]')
    rows, direct_rows, named_rows = [], [], []
    paths = subprocess.check_output(['git', 'ls-files', 'src', 'include'], cwd=ROOT,
                                    text=True).splitlines()
    inputs = {}
    for name in paths:
        path = ROOT / name
        if path.suffix not in {'.h', '.hpp', '.cpp'}:
            continue
        text = path.read_text(encoding='utf-8')
        clean = mask(text)
        if re.search(r'\bPatch(?:Bezier|Hermite|Coons)\b', clean):
            inputs[name] = sha(path)
        for pattern, target in [(construction, rows), (direct, direct_rows), (named, named_rows)]:
            for match in pattern.finditer(clean):
                line = clean.count('\n', 0, match.start()) + 1
                row = {'path': name, 'line': line, 'source': text.splitlines()[line - 1].strip(),
                       'file_sha256': sha(path)}
                if pattern is not named:
                    end, arity = arguments(clean, match.end())
                    row.update(arity=arity, expression=clean[match.start():end].strip())
                target.append(row)
    assignments = {}
    for kind in ['bezier', 'hermite']:
        path = ROOT / f'src/data/patch/patch_{kind}.cpp'
        text = mask(path.read_text(encoding='utf-8'))
        type_name = 'Patch' + kind.title()
        anchor = f'{type_name}::{type_name}({type_name}*'
        start = text.index('{', text.index(anchor)) + 1
        end, depth = start, 1
        while depth:
            depth += (text[end] == '{') - (text[end] == '}')
            end += 1
        assignments[type_name] = sorted(set(re.findall(r'\b(\w+_)\s*=', text[start:end - 1])))
    return {'source_base': BASE, 'classification': 'engineering-only literal source audit',
            'construction_count': len(rows), 'single_argument_constructions': sum(r['arity'] == 1 for r in rows),
            'construction_counts': dict(sorted(Counter(r['path'] for r in rows).items())),
            'constructions': rows, 'direct_constructor_spelling': direct_rows,
            'named_object_constructions': named_rows, 'copy_body_assigned_members': assignments,
            'input_files': inputs,
            'limits': 'Comments and quoted literals are masked. Balanced argument lists and concrete MakePatch calls are counted. '
                      'Declarations, definitions and base-constructor calls are retained separately for manual review. '
                      'No complete alias, macro-expansion, template-instantiation, external-client or dynamic caller proof.'}


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
    print(json.dumps({key: report[key] for key in ['construction_count', 'single_argument_constructions',
                                                 'construction_counts', 'copy_body_assigned_members']}))


if __name__ == '__main__':
    main()
