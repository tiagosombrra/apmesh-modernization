#!/usr/bin/env python3
"""Prepare a reversible observation-only copy of native angle selection."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def prepare(root, output, metadata, source=None):
    path = source or root / 'src/crab_mesh/aft/advancing_front.cpp'
    original = path.read_text(encoding='utf-8')
    text = original
    edits = []

    def change(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('Ambiguous native angle observer anchor: ' + old)
        text = text.replace(old, new)
        edits.append((old, new))

    change('#include "../../../include/crab_mesh/aft/advancing_front.h"',
           '#include "../../../include/crab_mesh/aft/advancing_front.h"\n#include "front_angle_hooks.h"')
    owned = 'std::unique_ptr<Vertex> v1(' in text
    for index in (1, 2):
        pattern = (r'    std::unique_ptr<Vertex> v' + str(index) + r'\(\s*new Vertex\([^;]+;' if owned else
                   r'    Vertex \*v' + str(index) + r' = new Vertex\([^;]+;')
        matches = re.findall(pattern, text)
        if len(matches) != 1:
            raise ValueError('Missing or ambiguous temporary declaration')
        declaration = matches[0]
        pointer = f'v{index}.get()' if owned else f'v{index}'
        change(declaration, ('    front_angle_test::Begin(geometryPhase);\n' if index == 1 else '') +
               declaration + f'\n    front_angle_test::Constructed({pointer}, {index});')
    cleanup = '    v1.reset();\n    v2.reset();' if owned else '    delete v1;\n    delete v2;'
    first, second = ('v1.get()', 'v2.get()') if owned else ('v1', 'v2')
    change(cleanup, f'    front_angle_test::Observe({first}, {second}, best, maxAngle);\n' +
           cleanup + '\n    front_angle_test::End();')
    restored = text
    for old, new in reversed(edits):
        if restored.count(new) != 1:
            raise ValueError('Observer insertion cannot be reversed')
        restored = restored.replace(new, old)
    if restored != original:
        raise ValueError('Native angle observation changed production source')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding='utf-8', newline='\n')
    report = {'status': 'passed', 'source': str(path),
              'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'generated_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
              'reversible_edits': len(edits), 'owned_temporaries': owned,
              'scope': 'Allocation-free observation hooks; original source restored exactly; no branch or formula changes'}
    metadata.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root, args.output, args.metadata, args.source)))
