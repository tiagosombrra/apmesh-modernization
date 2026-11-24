#!/usr/bin/env python3
"""Bounded native planar-quadrilateral BRep-to-bicubic BP writer for R3.C2.

Topological edges/vertices, never coordinate rounding or tolerance-based welding,
select the global BP identities. Only source-mirror T/Cross partial contacts.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from r3c2_native import extract, _topology, UnsupportedContact

SIDES = ((0, 1, 2, 3), (3, 7, 11, 15), (12, 13, 14, 15), (0, 4, 8, 12))


def _equal_topology(a, b):
    return a.wrapped.IsSame(b.wrapped)


def _position(v):
    return tuple(float(x) for x in v.toTuple())


def _distance(a, b):
    return max(abs(x-y) for x, y in zip(a, b))


def _frame(face):
    """Select four canonical rectangular corners by native vertex IDs."""
    vertices = face.Vertices()
    if len(vertices) != 4 or len(face.Edges()) != 4:
        raise UnsupportedContact('Expected one native quadrilateral')
    zmin = min(v.Z for v in vertices)
    zmax = max(v.Z for v in vertices)
    if zmax-zmin < 1e-9:
        raise UnsupportedContact('Degenerate vertical rectangular plane')
    bottom = sorted((v for v in vertices if abs(v.Z-zmin)<1e-9), key=lambda v: (v.X,v.Y))
    top = sorted((v for v in vertices if abs(v.Z-zmax)<1e-9), key=lambda v: (v.X,v.Y))
    if len(bottom) != 2 or len(top) != 2:
        raise UnsupportedContact('Cannot identify four paired vertical corners')
    for a,b in zip(bottom,top):
        if _distance(_position(a)[:2], _position(b)[:2])>1e-9:
            raise UnsupportedContact('Non-vertical quadrilateral not yet supported')
    corners = ((bottom[0], bottom[1]), (top[0], top[1]))
    return corners


def _native_face_edge(face, a, b):
    """Resolve the exact TopoDS_Edge with both prescribed TopoDS_Vertex IDs."""
    for edge in face.Edges():
        verts = edge.Vertices()
        if len(verts)==2 and (all(any(_equal_topology(v,z) for v in verts) for z in (a,b))):
            return edge
    raise UnsupportedContact('Source-derived side did not map to a native edge')


def convert(case, shape=None, report=None):
    """Produce an indexed bicubic BP plus source and edge-incidence metadata."""
    if shape is None or report is None:
        shape, report = extract(case)
    if report['case'] != case or not report['native_topology']['kernel_valid']:
        raise ValueError('Native source report does not match input')
    if report['g2_external_admission'] != 'NOT_GRANTED':
        raise ValueError('External admission claim must remain blocked')
    edges, histogram, triples = _topology(shape)
    if histogram.get(3,0) != (2 if case=='t_junction' else 4):
        raise UnsupportedContact('Missing required native triple-incidence edges')
    if len(shape.Faces()) != report['sheet_count']:
        raise ValueError('Native shape has changed since source graph was created')
    vertex_records=[]
    edge_records=[]
    controls=[]
    by_key={}
    patches=[]
    use_hist=Counter()

    def vertex_id(vertex):
        record = next((r for r in vertex_records if _equal_topology(r['vertex'],vertex)), None)
        if record is None:
            record={'vertex':vertex,'vid':len(vertex_records)}
            vertex_records.append(record)
        return record['vid']

    def edge_id(edge):
        record=next((r for r in edge_records if _equal_topology(r['edge'],edge)),None)
        if record is None:
            vertices=edge.Vertices()
            if len(vertices)!=2:
                raise UnsupportedContact('Non-two-vertex edge')
            canonical = sorted(vertices, key=lambda v: _position(v))
            record={'edge':edge,'eid':len(edge_records),'start':canonical[0],'end':canonical[1]}
            edge_records.append(record)
        return record

    def intern(key, coordinates):
        if key not in by_key:
            by_key[key]=len(controls)
            controls.append(tuple(float(x) for x in coordinates))
        else:
            if _distance(controls[by_key[key]],coordinates)>1e-10:
                raise UnsupportedContact('Source TopoDS identity has incompatible geometry')
        return by_key[key]

    for info in report['source_face_to_subface']:
        index=info['sewn_face_index']
        face=shape.Faces()[index]
        frame=_frame(face)
        bl, br = frame[0]
        tl, tr = frame[1]
        # The canonical BP row order is v ascending, u ascending.
        side_ends=((bl,br),(br,tr),(tl,tr),(bl,tl))
        sidemeta=[]
        native_sides=[]
        for slot, (start,end) in enumerate(side_ends):
            edge=_native_face_edge(face,start,end)
            key=edge_id(edge)
            forward=_equal_topology(start,key['start'])
            native_sides.append((key,forward))
            use_hist[key['eid']]+=1
            sidemeta.append({'slot':slot,'curve_id':f'E{key["eid"]}',
                             'orientation':'forward' if forward else 'reversed',
                             'native_edge_id':key['eid']})
        patch_ids=[]
        for row in range(4):
            v=row/3.
            for col in range(4):
                u=col/3.
                if row in (0,3) and col in (0,3):
                    vertex=frame[0 if row==0 else 1][0 if col==0 else 1]
                    key=('V',vertex_id(vertex))
                    coords=_position(vertex)
                elif row in (0,3) or col in (0,3):
                    if row==0:slot=0; t=col
                    elif col==3:slot=1; t=row
                    elif row==3:slot=2; t=col
                    else:slot=3; t=row
                    edge, forward=native_sides[slot]
                    ordinal = t if forward else 3-t
                    key=('E',edge['eid'],ordinal)
                    a,b=_position(edge['start']),_position(edge['end'])
                    coords=tuple(a[i]*(1-ordinal/3)+b[i]*ordinal/3 for i in range(3))
                else:
                    # Degree-elevation of a bilinear plane using source corners.
                    a,b,c,d=map(_position,(bl,br,tl,tr))
                    coords=tuple((1-u)*(1-v)*a[i]+u*(1-v)*b[i]
                                 +(1-u)*v*c[i]+u*v*d[i] for i in range(3))
                    key=('P',len(patches),row,col)
                patch_ids.append(intern(key,coords))
        for slot, offsets in enumerate(SIDES):
            sidemeta[slot]['control_vertex_ids']=[patch_ids[i] for i in offsets]
        patches.append({'patch_index':len(patches), 'sewn_face_index':index,
                        'role':info['role'], 'regions':info['regions'],
                        'source_faces':info['source_faces'],
                        'control_vertex_ids':patch_ids,'sides':sidemeta,
                        'expected_area':info['area'], 'expected_centroid':info['centroid']})
    # Derive actual BP incidence from original Open CASCADE edge identity.
    expected_native = Counter(len(entry['face_ids']) for entry in edges)
    actual_bp = Counter(use_hist.values())
    if expected_native != actual_bp or len(edges)!=len(edge_records):
        raise ValueError('BP side-curve incidences differ from native TopoDS edge graph')
    for curve in edge_records:
        ids=[]
        for p in patches:
            ids.extend(side['control_vertex_ids'] for side in p['sides'] if side['native_edge_id']==curve['eid'])
        if not ids:
            raise ValueError('Unreferenced native edge')
        for values in ids[1:]:
            if values!=ids[0] and values!=list(reversed(ids[0])):
                raise ValueError('Canonical shared curve identities do not match')
    rows=['// R3.C2 bounded STEP-like native face-splitting BP control',
          '// Not a general CAD converter and not an admitted external model']
    rows.extend('v '+' '.join(format(x,'.17g') for x in xyz) for xyz in controls)
    rows.extend('p '+' '.join(map(str,p['control_vertex_ids'])) for p in patches)
    bp='\n'.join(rows)+'\n'
    manifest={
        'schema':'apmesh-r3c2-partial-interface-bp-v1',
        'case':case,'input_classification':'PINNED_SOURCE_RECIPE_MIRROR',
        'scientific_scope':'BOUNDED_PLANAR_RECTANGULAR_NATIVE_BREP_FACES_ONLY',
        'external_model_admission':'NOT_GRANTED','apmesh_generation':'NOT_RUN',
        'source_graph':report,
        'patch_count':len(patches),
        'unique_control_vertices':len(controls),
        'unique_boundary_curve_count':len(edge_records),
        'native_edge_incidence_histogram':dict(sorted(histogram.items())),
        'bp_edge_incidence_histogram':dict(sorted(actual_bp.items())),
        'triple_edge_curves':sorted(f'E{k}' for k,n in use_hist.items() if n==3),
        'patches':patches,
        'bp_sha256':hashlib.sha256(bp.encode()).hexdigest(),
    }
    return bp,manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',choices=('t_junction','cross_junction'),required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args()
    bp,sidecar=convert(args.case)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/f'{args.case}.bp').write_text(bp,encoding='utf-8')
    (args.output_dir/f'{args.case}.sidecar.json').write_text(
        json.dumps(sidecar,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'case':args.case,'patches':sidecar['patch_count'],
                      'triple_curves':len(sidecar['triple_edge_curves']),
                      'controls':sidecar['unique_control_vertices'],
                      'bp_sha256':sidecar['bp_sha256']}))

if __name__=='__main__':
    main()
