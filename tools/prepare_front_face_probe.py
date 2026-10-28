#!/usr/bin/env python3
"""Prepare reversible, allocation-free observations of native interception."""
import argparse
import hashlib
import json
from pathlib import Path


def prepare(root, output, metadata, source=None):
    source = source or root / 'src/crab_mesh/aft/advancing_front.cpp'
    original = source.read_text(encoding='utf-8')
    text = original
    edits = []

    def change(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('Missing or ambiguous interception observer anchor')
        text = text.replace(old, new)
        edits.append((old, new))

    change('#include "../../../include/crab_mesh/aft/advancing_front.h"',
           '#include "../../../include/crab_mesh/aft/advancing_front.h"\n#include "front_face_hooks.h"')
    change('    Face f;', '    front_face_test::Begin();\n    Face f;\n'
           '    front_face_test::Stage(1);\n    front_face_test::Cache(f, 0);')
    change('    f.setVertices(e->getV1(), e->getV2(), candidate);',
           '    f.setVertices(e->getV1(), e->getV2(), candidate);\n'
           '    front_face_test::Stage(2);\n    front_face_test::Observe(f);\n'
           '    front_face_test::Cache(f, 1);')
    change('    f.setVertices(nullptr, nullptr, nullptr);',
           '    front_face_test::Stage(3);\n    f.setVertices(nullptr, nullptr, nullptr);\n'
           '    front_face_test::Stage(4);\n    front_face_test::Cache(f, 2);\n    front_face_test::End();')
    restored = text
    for old, new in reversed(edits):
        if restored.count(new) != 1:
            raise ValueError('Interception observation cannot be reversed')
        restored = restored.replace(new, old)
    if restored != original:
        raise ValueError('Observation changed native source')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding='utf-8', newline='\n')
    result = {'status': 'passed', 'source': str(source),
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'generated_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
              'reversible_edits': len(edits),
              'scope': 'Allocation-free observation; exact source reversal; no formula or branch changes'}
    metadata.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root, args.output, args.metadata, args.source)))
