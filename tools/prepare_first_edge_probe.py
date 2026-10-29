#!/usr/bin/env python3
"""Add exactly reversible observations to the first new-edge adoption path."""
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
            raise ValueError('Missing or ambiguous first-edge observation anchor')
        text = text.replace(old, new)
        edits.append((old, new))

    change('#include <memory>', '#include <memory>\n#include "first_edge_hooks.h"')
    owned = 'std::unique_ptr<Edge, PendingEdgeDelete> pending_edge(' in text
    declaration = ('      std::unique_ptr<Edge, PendingEdgeDelete> pending_edge(\n'
                   '          new Edge(e->getV1(), best, ++lastEdgeId));\n'
                   '      e1 = pending_edge.get();') if owned else (
                   '      e1 = new Edge(e->getV1(), best, ++lastEdgeId);')
    change(declaration, '      first_edge_test::Begin(lastEdgeId, innerEdges.size(), '
           + ('true' if owned else 'false') + ');\n' + declaration
           + '\n      first_edge_test::Built(e1);')
    for anchor, phase in [('      e->getV1()->addAdjacentEdge(e1);', 2),
                          ('      best->addAdjacentEdge(e1);', 3),
                          ('      innerEdges.push_back(e1);', 4),
                          ('      edges.push_back(e1);', 5)]:
        change(anchor, anchor + f'\n      first_edge_test::Step({phase});')
    anchor = '      quadtree->findCell(e1);'
    change(anchor, '      first_edge_test::Step(6);\n' + anchor
           + '\n      first_edge_test::End();')
    if owned:
        start = text.index('      struct PendingEdgeDelete {')
        end = text.index('      };', start) + len('      };')
        block = text[start:end]
        observed = block.replace('        void operator()(Edge* edge) const noexcept {',
                                 '        void operator()(Edge* edge) const noexcept {\n'
                                 '          first_edge_test::BeginCleanup();')
        observed = observed.replace('          delete edge;',
                                    '          delete edge;\n          first_edge_test::EndCleanup();')
        if observed == block or observed.count('first_edge_test::') != 2:
            raise ValueError('Missing actual first-edge cleanup observation')
        change(block, observed)
    restored = text
    for old, new in reversed(edits):
        if restored.count(new) != 1:
            raise ValueError('First-edge observation cannot be reversed')
        restored = restored.replace(new, old)
    if restored != original:
        raise ValueError('First-edge observation changed native source')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding='utf-8', newline='\n')
    result = {'status': 'passed', 'source': str(source), 'owned': owned,
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'generated_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
              'reversible_edits': len(edits)}
    metadata.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root, args.output, args.metadata, args.source)))
