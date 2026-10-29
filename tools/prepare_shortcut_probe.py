#!/usr/bin/env python3
"""Observe public three-edge Face ownership with exactly reversible hooks."""
import argparse
import hashlib
import json
from pathlib import Path


def prepare(root,output,metadata,source=None):
    source=source or root/'src/crab_mesh/aft/advancing_front.cpp'
    original=source.read_text(encoding='utf-8')
    text=original;edits=[]

    def change(old,new):
        nonlocal text
        if text.count(old)!=1:
            raise ValueError('Missing or ambiguous three-edge observation anchor')
        text=text.replace(old,new);edits.append((old,new))

    change('#include "../../../include/crab_mesh/aft/advancing_front.h"',
           '#include "../../../include/crab_mesh/aft/advancing_front.h"\n#include "shortcut_hooks.h"')
    owned='std::unique_ptr<Face, ShortcutFaceDelete> pending_face(' in text
    declaration=('    std::unique_ptr<Face, ShortcutFaceDelete> pending_face(\n'
                 '        new Face(front.front()->getV1(), v, front.back()->getV1(), ++lastFaceId));') if owned else (
                 '    Face* f = new Face(front.front()->getV1(), v, front.back()->getV1(), ++lastFaceId);')
    pointer='pending_face.get()' if owned else 'f'
    change(declaration,'    shortcut_test::Begin(mesh.size(), lastFaceId);\n'+declaration+
           '\n    shortcut_test::Built('+pointer+');')
    publication=('    mesh.push_back(pending_face.get());\n    pending_face.release();' if owned
                 else '    mesh.push_back(f);')
    context='    shortcut_test::Built('+pointer+');\n'+('\n' if owned else '')+publication
    change(context,context+'\n    shortcut_test::Adopted(mesh.size());')
    if owned:
        start=text.index('    struct ShortcutFaceDelete {')
        end=text.index('    std::unique_ptr<Face, ShortcutFaceDelete>',start)
        block=text[start:end]
        observed=block.replace('      void operator()(Face* face) const noexcept {',
                               '      void operator()(Face* face) const noexcept {\n        shortcut_test::BeginCleanup();')
        observed=observed.replace('        delete face;','        delete face;\n        shortcut_test::EndCleanup();')
        if observed==block:
            raise ValueError('Missing actual shortcut cleanup observation')
        change(block,observed)
    restored=text
    for old,new in reversed(edits):
        if restored.count(new)!=1:
            raise ValueError('Three-edge observation cannot be reversed')
        restored=restored.replace(new,old)
    if restored!=original:
        raise ValueError('Three-edge observation changed native source')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(text,encoding='utf-8',newline='\n')
    report={'status':'passed','source':str(source),'owned_shortcut':owned,
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'generated_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'reversible_edits':len(edits),'scope':'Allocation-free public-wrapper observation; exact source reversal'}
    metadata.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--source',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--metadata',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(prepare(args.root,args.output,args.metadata,args.source)))
