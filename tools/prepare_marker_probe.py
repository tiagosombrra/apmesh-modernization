#!/usr/bin/env python3
"""Observe native marker ownership with allocation-free reversible hooks."""
import argparse
import hashlib
import json
from pathlib import Path


def prepare(root, output, metadata, source=None):
    source = source or root/'src/crab_mesh/aft/advancing_front.cpp'
    original = source.read_text(encoding='utf-8')
    text = original
    edits = []

    def change(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('Missing or ambiguous marker observation anchor')
        text = text.replace(old, new)
        edits.append((old, new))

    change('#include "../../../include/crab_mesh/aft/advancing_front.h"',
           '#include "../../../include/crab_mesh/aft/advancing_front.h"\n#include "marker_hooks.h"')
    owned = 'std::unique_ptr<Edge, MarkerDelete> marker(' in text
    creation = ('    marker.reset(new Edge());\n    last = marker.get();' if owned
                else '    last = new Edge();')
    change(creation, '    marker_test::BeginMarker();\n'+creation+
           '\n    marker_test::Constructed(last);')
    change('    front.push_back(last);',
           '    front.push_back(last);\n    marker_test::Published();')
    retirement = '      marker.reset();' if owned else '      delete last;'
    change(retirement+'\n      last = nullptr;',
           '      marker_test::Retiring(last);\n'+retirement+'\n      last = nullptr;')
    change('    bool existed = findBestVertex(e, best, geometryPhase);',
           '    marker_test::BeginSelection();\n    bool existed = findBestVertex(e, best, geometryPhase);\n    marker_test::EndWindow();')
    declaration = ('    std::unique_ptr<Face, PendingFaceDelete> f(\n'
                   '        new Face(e->getV1(), e->getV2(), best, ++lastFaceId));')
    change(declaration, '    marker_test::BeginFace();\n'+declaration)
    change('    mesh.push_back(f.get());\n    f.release();',
           '    mesh.push_back(f.get());\n    f.release();\n    marker_test::EndWindow();')
    if owned:
        def change_marker(old, new):
            anchor = '  struct MarkerDelete {\n'
            if text.count(anchor) != 1:
                raise ValueError('Missing or ambiguous marker cleanup scope')
            start = text.index(anchor)
            end = text.index('\n  };', start) + len('\n  };')
            block = text[start:end]
            if block.count(old) != 1:
                raise ValueError('Missing or ambiguous marker cleanup observation')
            change(block, block.replace(old, new))

        change_marker('    void operator()(Edge* edge) const noexcept {',
                      '    void operator()(Edge* edge) const noexcept {\n      marker_test::BeginCleanup();')
        change_marker('      delete edge;\n    }\n  };',
                      '      delete edge;\n      marker_test::EndCleanup();\n    }\n  };')
    restored = text
    for old, new in reversed(edits):
        if restored.count(new) != 1:
            raise ValueError('Marker observation is not independently reversible')
        restored = restored.replace(new, old)
    if restored != original:
        raise ValueError('Marker observation changed native source')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding='utf-8', newline='\n')
    report = {'status':'passed', 'source':str(source), 'owned_marker':owned,
              'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'generated_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
              'reversible_edits':len(edits),
              'scope':'Allocation-free observation; exact native source reversal'}
    metadata.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--source',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--metadata',type=Path,required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root,args.output,args.metadata,args.source)))
