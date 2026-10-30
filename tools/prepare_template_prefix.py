#!/usr/bin/env python3
"""Emit reversible diagnostic preflight cuts for the native template prefix."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def transform(tree, cell):
    """Preserve native expressions while checking their actual neighbor reads."""
    tree_edits = []
    for old, new in [
        ('#include <memory>', '#include <memory>\n#include "prefix_hooks.h"'),
        ('  root->sortNeighbors();',
         '  prefix_test::BeforeSort(this);\n  root->sortNeighbors();\n'
         '  prefix_test::BeforeTemplates(this);'),
    ]:
        if tree.count(old) != 1:
            raise ValueError('Missing or ambiguous tree preflight anchor')
        tree = tree.replace(old, new)
        tree_edits.append((old, new))
    cell_edits = []
    include = '#include <stdexcept>'
    if cell.count(include) != 1:
        raise ValueError('Missing or ambiguous cell include anchor')
    replacement = include + '\n#include "prefix_hooks.h"'
    cell = cell.replace(include, replacement)
    cell_edits.append((include, replacement))
    pattern = re.compile(
        r'neighbors\[(?P<first>QUAD_\w+|i)\]\.(?P<end>front|back)\(\)'
        r'(?:->neighbors\[(?P<second>QUAD_\w+)\]\.(?P<other>front|back)\(\))?')
    reads = []

    def observe(match):
        index = len(reads)
        first = (f'prefix_test::Neighbor(neighbors[{match["first"]}], '
                 f'{str(match["end"] == "back").lower()}, {2 * index}, false)')
        new = first
        if match['second']:
            new = (f'prefix_test::Neighbor({first}->neighbors[{match["second"]}], '
                   f'{str(match["other"] == "back").lower()}, {2 * index + 1}, true)')
        reads.append({'expression': match[0], 'tag': index,
                      'chained': bool(match['second'])})
        cell_edits.append((match[0], new))
        return new

    cell = pattern.sub(observe, cell)
    if len(reads) < 20 or sum(r['chained'] for r in reads) < 8:
        raise ValueError('Incomplete native neighbor-read inventory')
    return tree, cell, tree_edits, cell_edits, reads


def prepare(root, output):
    originals = [(root / 'src/crab_mesh/aft' / name).read_text(encoding='utf-8')
                 for name in ('quadtree.cpp', 'quadtree_cell.cpp')]
    tree, cell, tree_edits, cell_edits, reads = transform(*originals)
    output.mkdir(parents=True, exist_ok=True)
    records = {}
    for name, original, observed, edits in zip(
            ('quadtree.cpp', 'quadtree_cell.cpp'), originals,
            (tree, cell), (tree_edits, cell_edits)):
        restored = observed
        for old, new in reversed(edits):
            if restored.count(new) != 1:
                raise ValueError('Nonreversible prefix observation')
            restored = restored.replace(new, old)
        if restored != original:
            raise ValueError('Native template-prefix source changed')
        target = output / name
        target.write_text(observed, encoding='utf-8', newline='\n')
        records[name] = {'source_sha256': hashlib.sha256(original.encode()).hexdigest(),
                         'generated_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                         'edits': edits}
    metadata = {'status': 'reversible_preflight_prepared', 'files': records,
                'neighbor_expressions': reads}
    (output / 'preparation.json').write_text(json.dumps(metadata, indent=2) + '\n',
                                           encoding='utf-8', newline='\n')
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.root, args.output)
    print(json.dumps({'status': result['status'],
                      'neighbor_expressions': len(result['neighbor_expressions'])}))
