#!/usr/bin/env python3
"""Independent JSON-only cross-check of the analytic three-box interface graph.

This audit does not import CadQuery/OCP or trust the producer's 'passed' flags.
It checks the declared source regions/sheets, their orientation and provenance.
It does NOT establish that an unrelated CAD input has the same topology.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
from pathlib import Path


def check(document):
    """Reject malformed or self-inconsistent topology and geometry claims."""
    def need(expr, reason):
        if not expr:
            raise ValueError(reason)
    need(isinstance(document, dict) and document.get('schema') == 'apmesh-r2-multibody-interface-graph-v1', 'Invalid schema')
    need(document.get('scope') == 'LOCAL_PINNED_SOURCE_MIRROR_NOT_UPSTREAM_EXECUTION', 'Invalid source scope')
    g = document['geometry']; w = g['width']
    need(type(w) in (int, float) and math.isfinite(w) and w > 0, 'Invalid width')
    need(set(g['source_bodies']) == {'A','B','C'}, 'Invalid source regions')
    for body in g['source_bodies'].values():
        need(body['is_valid'] is True and body['faces'] == 6 and body['edges'] == 12, 'Invalid source solid declaration')
        need(abs(body['volume'] - w**3) < 1e-10*w**3, 'Invalid volume')
    original = document['original_topological_identity']
    need(original['central_source_edge_shared_across_bodies'] is False, 'Original CAD edges improperly merged')
    need(original['bodies']==3 and original['central_source_edges']==3 and original['central_source_face_uses']==6, 'Original incidence mismatch')
    spine=document['reconstructed_spatial_curve']
    need(spine['curve_id']=='C0' and spine['incident_sheet_count']==4, 'Incorrect declared junction')
    need(spine['provenance']=='INFERRED_SHARED_GEOMETRY_FROM_DISTINCT_BREP_EDGES_NOT_WELDED','Incorrect provenance')
    need(spine['endpoints']==[[0.0,0.0,-w/2],[0.0,0.0,w/2]], 'Spine endpoints mismatch')
    need(abs(spine['length'] - w) < 1e-10, 'Incorrect spine length')
    # Derive each expected region pair from the four angular quadrant sectors.
    sectors=['A','B','VOID','C']  # NW, NE, SE, SW in cyclic order
    expected={frozenset((sectors[i],sectors[(i+1)%4])) for i in range(4)}
    used=set();source_faces=set();n_sources=0
    sheets=document['sheets']
    need(isinstance(sheets,list) and len(sheets)==4, 'Missing/extra sheets')
    expected_rays={frozenset(('A','B')):(0,1),frozenset(('B','VOID')):(1,0),
                   frozenset(('C','VOID')):(0,-1),frozenset(('A','C')):(-1,0)}
    for sheet in sheets:
        pair=frozenset(sheet['region_pair'])
        need(pair in expected and pair not in used, 'Unknown/duplicate interface')
        used.add(pair)
        need(sheet['spine_boundary']==spine['endpoints'], 'Curve identity drift')
        need(abs(sheet['area'] - w*w) < 1e-9, 'Wrong surface area')
        radial=sheet['radial_xy'];norm=math.hypot(*radial)
        need(norm>0 and all(abs(a/norm - b) < 1e-10 for a,b in zip(radial,expected_rays[pair])), 'Wrong radial orientation')
        sources=sheet['source_faces'];actual={s['body'] for s in sources}
        need(actual==(pair-{'VOID'}), 'Source face owners mismatch')
        need(len(sources)==(1 if 'VOID' in pair else 2), 'Wrong number of source face uses')
        normals=[]
        for s in sources:
            key=(s['body'],s['face_index'])
            need(key not in source_faces, 'Source face reused')
            source_faces.add(key); n_sources+=1
            need(abs(s['area'] - w*w) < 1e-9, 'Source face area mismatch')
            n=s['normal'];need(abs(math.sqrt(sum(a*a for a in n))-1) < 1e-10,'Nonunit source normal')
            normals.append(n)
        if len(normals)==2:
            need(abs(sum(x*y for x,y in zip(*normals))+1) < 1e-10,'Non-opposing interface normals')
    need(used==expected and n_sources==6,'Incomplete source incidence')
    need(document.get('g2_admission') != 'PASS','Unexpected G2 approval')
    return {'checker':'apmesh-r2-analytic-json-oracle-v1','status':'CONSISTENT_WITH_THREE_QUADRANT_ANALYTIC_MODEL',
            'sheets':len(sheets),'source_face_uses':n_sources,'shared_curve_count':1,
            'model_admission':'NOT_GRANTED'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report',type=Path)
    args=parser.parse_args()
    report=json.loads(args.report.read_text(encoding='utf-8'))
    print(json.dumps(check(report),sort_keys=True))


if __name__=='__main__':
    main()
