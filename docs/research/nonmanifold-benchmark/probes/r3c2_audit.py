#!/usr/bin/env python3
"""Independent R3.C2 audit of indexed bicubic BP and native split-face topology.

This verifier does not import the R3.C2 builder or derive expected source sizes
from a generator result. Geometry and native-incidence checks are separate gates.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt

SLOTS = ((0,1,2,3),(3,7,11,15),(12,13,14,15),(0,4,8,12))
CASE_EXPECTATIONS = {
    't_junction': {
        'bodies': {'main':500.,'branch':250.},
        'contacts':1,'patches':5,'edges':16,'triple':2,
        'blocks': [('branch',2.5,2.5,25.,(37.5,37.5),50.)],
    },
    'cross_junction': {
        'bodies': {'main':320.,'top_arm':128.,'bottom_arm':128.},
        'contacts':2,'patches':10,'edges':32,'triple':4,
        'blocks': [('bottom_arm',-2.,2.,16.,(32.,32.),32.),
                   ('top_arm',2.,2.,16.,(32.,32.),32.)],
    }
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bp(text):
    """Parse zero-based indexed BP records without importing conversion code."""
    vertices=[]
    patches=[]
    for lineno,line in enumerate(text.splitlines(),1):
        data=line.split('//',1)[0].split('#',1)[0].split()
        if not data:
            continue
        if data[0]=='v':
            require(len(data)==4,f'BP vertex arity at line {lineno}')
            try:p=tuple(float(x) for x in data[1:])
            except (ValueError,OverflowError) as error:raise ValueError('Malformed vertex') from error
            require(all(math.isfinite(x) for x in p),'Nonfinite BP coordinate')
            vertices.append(p)
        elif data[0]=='p':
            require(len(data)==17,f'BP patch arity at line {lineno}')
            try:indices=tuple(int(x) for x in data[1:])
            except ValueError as error:raise ValueError('Malformed index') from error
            require(all(0<=i<len(vertices) for i in indices),'Out-of-range/forward index')
            patches.append(indices)
        else:
            raise ValueError(f'Unsupported BP record at line {lineno}')
    require(bool(patches),'Empty BP')
    return vertices,patches


def cubic(ctrl,t):
    """Independent de Casteljau polynomial evaluator in physical XYZ."""
    cur=list(ctrl)
    while len(cur)>1:
        cur=[tuple((1-t)*a+t*b for a,b in zip(x,y)) for x,y in zip(cur,cur[1:])]
    return cur[0]


def surface(poles,u,v):
    return cubic([cubic(poles[4*j:4*j+4],u) for j in range(4)],v)


def distance(p,q):
    return max(abs(a-b) for a,b in zip(p,q))


def _face_endpoints(face):
    points=[v.toTuple() for v in face.Vertices()]
    require(len(points)==4,'Native face not four-sided')
    zlo=min(p[2] for p in points)
    zhi=max(p[2] for p in points)
    low=sorted((p for p in points if abs(p[2]-zlo)<1e-8),key=lambda p:(p[0],p[1]))
    high=sorted((p for p in points if abs(p[2]-zhi)<1e-8),key=lambda p:(p[0],p[1]))
    require(len(low)==2 and len(high)==2,'Native source not vertical rectangle')
    return low[0],low[1],high[0],high[1]


def _native_edges(shape):
    edges=[]
    for i,face in enumerate(shape.Faces()):
        for edge in face.Edges():
            record=next((r for r in edges if r['edge'].wrapped.IsSame(edge.wrapped)),None)
            if record is None:
                record={'edge':edge,'uses':set()}
                edges.append(record)
            record['uses'].add(i)
    return Counter(len(record['uses']) for record in edges)


def audit(bp, metadata, native):
    """Check provenance labels, source dimensions, curve IDs and native geometry."""
    require(metadata.get('schema')=='apmesh-r3c2-partial-interface-bp-v1','Incorrect research sidecar schema')
    case=metadata.get('case')
    require(case in CASE_EXPECTATIONS,'Unknown control case')
    expected=CASE_EXPECTATIONS[case]
    require(hashlib.sha256(bp.encode('utf-8')).hexdigest()==metadata.get('bp_sha256'),'BP SHA-256 mismatch')
    require(metadata.get('scientific_scope')=='BOUNDED_PLANAR_RECTANGULAR_NATIVE_BREP_FACES_ONLY','False converter scope')
    require(metadata.get('external_model_admission')=='NOT_GRANTED','False external admission')
    require(metadata.get('apmesh_generation')=='NOT_RUN','False APMesh TRI claim')
    source=metadata.get('source_graph')
    require(source.get('case')==case and source.get('schema')=='apmesh-r3c2-occt-contact-v1','Invalid native graph scope')
    require(source['upstream']['source_mode']=='PINNED_DEFAULTS_RECREATED_NOT_UPSTREAM_EXECUTION','False upstream execution')
    require(set(source['source_bodies'])==set(expected['bodies']),'Original source body roster changed')
    for name,vol in expected['bodies'].items():
        body=source['source_bodies'][name]
        require(body['faces']==6 and body['edges']==12 and abs(body['volume']-vol)<1e-9,
                'Original source geometry changed')
    require(source['contact_count']==expected['contacts'],'Incorrect material contacts')
    require(len(source['contact_records'])==expected['contacts'],'Missing contact provenance')
    for record,(name,y,halfwidth,area,wings,flank) in zip(source['contact_records'],expected['blocks']):
        require(record['arm_body']==name and record['host_body']=='main','Source ownership drift')
        require(abs(record['overlap_area']-area)<1e-8,'Incorrect face overlap area')
        require(record['wings_area']==list(wings),'Incorrect source split areas')
        require(record['generated_sheet_count']==5,'Incomplete source face decomposition')
    vertices,patches=read_bp(bp)
    require(len(patches)==expected['patches'],'Wrong number of source-derived bicubic patches')
    require(metadata['patch_count']==len(patches) and len(metadata['patches'])==len(patches),'Declared patch count drift')
    require(native.isValid() and len(native.Faces())==len(patches),'Native source mesh/shell not valid')
    native_hist=_native_edges(native)
    require(native_hist==Counter({1:expected['edges']-expected['triple'],3:expected['triple']}),
            'Actual native edge incidence differs from expected source contact topology')
    labels=[]
    unique_controls=set()
    curves=defaultdict(list)
    max_analytic=0.
    max_native=0.
    for pindex,(ids,meta) in enumerate(zip(patches,metadata['patches'])):
        require(meta['patch_index']==pindex and meta['control_vertex_ids']==list(ids),'Control-index map mismatch')
        require(len(set(ids))==16,'Repeated controls within one quadrilateral')
        require(len(meta['sides'])==4,'Four sides required')
        require(len(meta['source_faces']) in (1,2),'Wrong source face provenance')
        role=meta['role'];regions=meta['regions']
        if role=='interface':
            require(len(meta['source_faces'])==2 and set(regions)=={m['body'] for m in meta['source_faces']},'Interface face owners disagree')
        elif role.startswith('host_exterior_'):
            require(regions==['main','VOID'] and len(meta['source_faces'])==1 and meta['source_faces'][0]['body']=='main', 'Host exterior provenance mismatch')
        elif role.startswith('arm_exterior_'):
            require('VOID' in regions and len(meta['source_faces'])==1 and meta['source_faces'][0]['body'] in regions, 'Arm exterior provenance mismatch')
        else:
            raise ValueError('Unknown split face type')
        labels.append(role)
        net=[vertices[i] for i in ids]
        for slot,offsets in enumerate(SLOTS):
            side=meta['sides'][slot]
            require(side['slot']==slot and side['control_vertex_ids']==[ids[i] for i in offsets],'Side control identity drift')
            require(side['orientation'] in ('forward','reversed'),'Unknown edge orientation')
            require(side['curve_id']==f"E{side['native_edge_id']}", 'Curve identity mismatched')
            indices=tuple(side['control_vertex_ids'])
            curves[side['curve_id']].append(indices)
        native_index=meta['sewn_face_index']
        require(type(native_index) is int and 0<=native_index<len(native.Faces()),'Invalid native face mapping')
        face=native.Faces()[native_index]
        require(len(face.Edges())==4 and face.geomType()=='PLANE','Native source is not a four-sided plane')
        require(abs(face.Area()-meta['expected_area'])<1e-8,'Native source area differs from sidecar')
        centroid=face.Center().toTuple()
        require(distance(centroid,meta['expected_centroid'])<1e-8,'Native face identity mismatch')
        a,b,c,d=_face_endpoints(face)
        for row in range(7):
            v=row/6
            for col in range(7):
                u=col/6
                target=tuple((1-u)*(1-v)*a[i]+u*(1-v)*b[i]+(1-u)*v*c[i]+u*v*d[i] for i in range(3))
                point=surface(net,u,v)
                error=distance(point,target)
                max_analytic=max(max_analytic,error)
                require(error<=2e-12,'BP fails independent native-rectangle analytic reconstruction')
        # Test strictly interior points against the exact mapped native B-Rep face.
        for row in range(1,6):
            v=row/6
            for col in range(1,6):
                u=col/6
                point=surface(net,u,v)
                vertex=BRepBuilderAPI_MakeVertex(gp_Pnt(*point)).Vertex()
                evaluator=BRepExtrema_DistShapeShape(vertex,face.wrapped)
                evaluator.Perform()
                require(evaluator.IsDone(),'Native OCCT distance oracle failed')
                err=evaluator.Value()
                max_native=max(max_native,err)
                require(err<=1e-8,'BP does not lie on intended native source face')
        unique_controls.update(ids)
    require(len(set(meta['sewn_face_index'] for meta in metadata['patches']))==len(patches),'Native face mapped twice')
    require(len(unique_controls)==len(vertices),'Orphaned or unexpected global BP control')
    hist=Counter(len(records) for records in curves.values())
    require(hist==native_hist,'BP curve references do not match independent native TopoDS incidence')
    require(len(curves)==expected['edges'],'Unexpected distinct curves')
    for curve_id,uses in curves.items():
        for ids in uses[1:]:
            require(ids==uses[0] or ids==tuple(reversed(uses[0])),f'Shared edge control IDs diverged: {curve_id}')
    require(sum(role=='interface' for role in labels)==expected['contacts'],'Unexpected interface sheet count')
    require(sum(role.startswith('host_exterior_') for role in labels)==2*expected['contacts'],'Missing host wings')
    require(sum(role.startswith('arm_exterior_') for role in labels)==2*expected['contacts'],'Missing branch flanks')
    return {'schema':'apmesh-r3c2-independent-validation-v1','case':case,
            'classification':'PINNED_SOURCE_RECIPE_CONTROL_ONLY',
            'patch_count':len(patches),'unique_control_vertices':len(vertices),
            'unique_boundary_curves':len(curves),
            'shared_three_face_curves':hist[3],
            'curve_incidence_histogram':dict(sorted(hist.items())),
            'surface_samples':49*len(patches),'native_interior_samples':25*len(patches),
            'max_analytic_coordinate_error':max_analytic,
            'max_native_surface_distance':max_native,
            'external_model_admission':'NOT_GRANTED',
            'apmesh_generation':'NOT_RUN'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bp',type=Path,required=True)
    p.add_argument('--sidecar',type=Path,required=True)
    p.add_argument('--brep',type=Path,required=True)
    args=p.parse_args()
    data=audit(args.bp.read_text(encoding='utf-8'),json.loads(args.sidecar.read_text(encoding='utf-8')),
               cq.Shape.importBrep(str(args.brep)))
    print(json.dumps(data,sort_keys=True,indent=2))

if __name__=='__main__':
    main()
