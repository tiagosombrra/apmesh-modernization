#!/usr/bin/env python3
"""Observe native ideal-Vertex selection and pending cleanup reversibly."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def transform(original):
    text = original
    edits = []

    def change(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('Missing or ambiguous ideal-Vertex observation anchor: ' + old)
        text = text.replace(old, new)
        edits.append((old, new))

    change('#include <memory>', '#include <memory>\n#include "ideal_hooks.h"')
    start_marker = 'bool AdvancingFront::findBestVertex('
    end_marker = '\nvoid AdvancingFront::insertInFront('
    if text.count(start_marker) != 1 or text.count(end_marker) != 1:
        raise ValueError('Missing or ambiguous native selector scope')
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    region = text[start:end]
    owned = 'PendingIdealVertexDelete' in region
    declaration = '  best = (geometryPhase) ? makeIdealVertex(e, h) : nullptr;'
    if owned:
        matches = re.findall(
            r'  std::unique_ptr<Vertex, PendingIdealVertexDelete> pending_ideal\(\s*'
            r'\(geometryPhase\) \? makeIdealVertex\(e, h\) : nullptr,\s*'
            r'PendingIdealVertexDelete\{&frontVertices\}\);\n  best = pending_ideal.get\(\);', region)
        if len(matches) != 1:
            raise ValueError('Missing or ambiguous ideal-Vertex owner declaration')
        declaration = matches[0]
    pairs = [(declaration, '  ideal_test::Begin();\n' + declaration +
              '\n  if (geometryPhase) ideal_test::Built(best);')]
    for anchor, phase in [
        ('    bool intercept = interceptionTest(e, candidate, true, false);', 30),
        ('      bestVertices.push_back(candidate);', 31),
        ('    bool intercept = interceptionTest(e, best);', 40),
        ('        best->setId(++lastVertexId);', 49),
        ('        frontVertices.push_back(best);', 50),
        ('        innerVertices.push_back(best);', 51),
        ('        vertices.push_back(best);', 52),
    ]:
        indent = anchor[:len(anchor) - len(anchor.lstrip())]
        pairs.append((anchor, indent + f'ideal_test::Step({phase});\n' + anchor))
    retire = 'pending_ideal.reset();' if owned else 'delete best;'
    pairs += [
        ('    if (geometryPhase) {\n      ' + retire,
         '    if (geometryPhase) {\n      ideal_test::Step(60);\n      ' + retire),
        ('    best = bestVertices.front();',
         '    best = bestVertices.front();\n    ideal_test::Step(61);'),
        ('      if (dist < 0.0) {', '      if (dist < 0.0) {\n        ideal_test::Step(73);'),
        ('        bestVertices.clear();', '        ideal_test::Step(70);\n        bestVertices.clear();'),
        ('    if (intercept) {\n      ' + retire,
         '    if (intercept) {\n      ideal_test::Step(71);\n      ' + retire),
        ('      if (tooClose) {\n        ' + retire,
         '      if (tooClose) {\n        ideal_test::Step(72);\n        ' + retire),
        ('  return vertexExistedBefore;', '  ideal_test::End();\n  return vertexExistedBefore;'),
    ]
    if owned:
        pairs += [
            ('    void operator()(Vertex* vertex) const noexcept {',
             '    void operator()(Vertex* vertex) const noexcept {\n      ideal_test::BeginCleanup();'),
            ('      delete vertex;', '      delete vertex;\n      ideal_test::EndCleanup();'),
        ]
    for old, new in pairs:
        if region.count(old) != 1:
            raise ValueError('Missing or ambiguous ideal-Vertex selector anchor: ' + old)
        region = region.replace(old, new)
    observed = text[:start] + region + text[end:]
    restored = region
    for old, new in reversed(pairs):
        if restored.count(new) != 1:
            raise ValueError('Nonreversible ideal-Vertex selector observation')
        restored = restored.replace(new, old)
    restored = text[:start] + restored + text[end:]
    for old, new in reversed(edits):
        restored = restored.replace(new, old)
    if restored != original:
        raise ValueError('Native ideal-Vertex source changed during observation')
    return observed, owned, edits + pairs


def prepare(root, output, metadata, source=None):
    source = source or root / 'src/crab_mesh/aft/advancing_front.cpp'
    observed, owned, edits = transform(source.read_text(encoding='utf-8'))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(observed, encoding='utf-8', newline='\n')
    result = {'status': 'passed', 'owned': owned, 'source': str(source),
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'generated_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
              'reversible_edits': len(edits)}
    metadata.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'source', 'output', 'metadata'):
        p.add_argument('--' + name, type=Path, required=name != 'source')
    args = p.parse_args()
    print(json.dumps(prepare(args.root, args.output, args.metadata, args.source)))
