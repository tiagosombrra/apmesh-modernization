#!/usr/bin/env python3
"""Add reversible, allocation-free observations to pending Face publication."""
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
            raise ValueError('Missing or ambiguous pending Face observation anchor')
        text = text.replace(old, new)
        edits.append((old, new))

    change('#include "../../../include/crab_mesh/aft/advancing_front.h"',
           '#include "../../../include/crab_mesh/aft/advancing_front.h"\n#include "face_adoption_hooks.h"')
    owned = 'std::unique_ptr<Face, PendingFaceDelete> f(' in text
    declaration = ('    std::unique_ptr<Face, PendingFaceDelete> f(\n'
                   '        new Face(e->getV1(), e->getV2(), best, ++lastFaceId));') if owned else (
                   '    Face* f = new Face(e->getV1(), e->getV2(), best, ++lastFaceId);')
    pointer = 'f.get()' if owned else 'f'
    change(declaration, '    face_adoption_test::Begin(mesh.size(), lastFaceId);\n'+declaration+
           f'\n    face_adoption_test::Built({pointer});')
    publication = ('    mesh.push_back(f.get());\n    f.release();' if owned else '    mesh.push_back(f);')
    context = f'    face_adoption_test::Built({pointer});\n\n'+publication
    change(context, context+'\n    face_adoption_test::Adopted(mesh.size());')
    restored = text
    for old, new in reversed(edits):
        if restored.count(new) != 1:
            raise ValueError('Pending Face observation cannot be reversed')
        restored = restored.replace(new, old)
    if restored != original:
        raise ValueError('Pending Face observation changed native source')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding='utf-8', newline='\n')
    report = {'status':'passed', 'source':str(source), 'owned_pending_face':owned,
              'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'generated_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
              'reversible_edits':len(edits), 'scope':'Allocation-free observation; exact native source restoration'}
    metadata.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--source',type=Path)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--metadata',type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(prepare(a.root,a.output,a.metadata,a.source)))
