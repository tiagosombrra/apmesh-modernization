#!/usr/bin/env python3
"""Independent BP/native-BRep audit for a partial original CAD planar atlas.

A sampled residual is not a certified bound for arbitrary trimmed/curved faces.
This auditor only accepts convex single-wire planar four-edge source faces.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq
from audit_analytic_bp import read_bp, surface
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.gp import gp_Pnt

SLOTS = ((0,1,2,3), (3,7,11,15), (12,13,14,15), (0,4,8,12))


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def source_distance(face, point):
    probe=BRepBuilderAPI_MakeVertex(gp_Pnt(*point)).Vertex()
    distance=BRepExtrema_DistShapeShape(probe,face.wrapped)
    distance.Perform()
    ensure(distance.IsDone(),'Independent native distance failed')
    return distance.Value()


def audit(source_shape, bp_text, sidecar, *, source_sha256):
    ensure(sidecar.get('schema')=='apmesh-original-cad-partial-planar-atlas-v1','Wrong atlas schema')
    ensure(sidecar.get('source_sha256')==source_sha256,'Source raw SHA-256 mismatch')
    ensure(sidecar.get('bp_sha256')==sha256(bp_text.encode()).hexdigest(),'BP checksum mismatch')
    ensure(sidecar.get('apmesh_generation')=='NOT_RUN','Unsupported meshing claim')
    ensure(sidecar.get('independent_external_nonmanifold_admission')=='NOT_GRANTED',
           'Unsupported topology admission')
    vertices,patches=read_bp(bp_text)
    face_list=source_shape.Faces()
    edge_list=source_shape.Edges()
    ensure(len(vertices)==sidecar['unique_controls'],'Wrong global control count')
    ensure(len(patches)==sidecar['converted_face_count']==len(sidecar['patches']),
           'Missing or duplicated patch mapping')
    ensure(sidecar['excluded_face_count']+len(patches)==len(face_list),
           'Excluded source faces not accounted for')
    included=set()
    uses=defaultdict(list)
    maximum=0.0
    grid=(0,.125,.25,.5,.75,.875,1)
    for i,(ids,record) in enumerate(zip(patches,sidecar['patches'])):
        face_id=record['source_face']
        ensure(0<=face_id<len(face_list) and face_id not in included,'Invalid source face mapping')
        included.add(face_id)
        face=face_list[face_id]
        ensure(face.geomType()=='PLANE' and len(face.Wires())==1,
               'Unsupported source surface included')
        ensure(len(face.outerWire().Edges())==4 and len(face.outerWire().Vertices())==4,
               'Unsupported source trim included')
        ensure(list(ids)==record['control_vertex_ids'],'Patch control map mismatch')
        ensure(len(record['sides'])==4,'Missing side records')
        for slot, offsets in enumerate(SLOTS):
            s=record['sides'][slot]
            eid=s['source_edge']
            ensure(s['slot']==slot and 0<=eid<len(edge_list),'Invalid native edge ID')
            ensure(s['control_vertex_ids']==[ids[x] for x in offsets],
                   'Side vertex IDs differ from BP')
            ensure(any(edge.wrapped.IsSame(edge_list[eid].wrapped) for edge in face.Edges()),
                   'Source edge not incident to mapped source face')
            uses[eid].append(s['control_vertex_ids'])
        control_net=[vertices[x] for x in ids]
        for u in grid:
            for v in grid:
                p=surface(control_net,u,v)
                ensure(all(math.isfinite(x) for x in p),'Nonfinite evaluated BP point')
                maximum=max(maximum,source_distance(face,p))
    for eid,side_uses in uses.items():
        ensure(len(side_uses)<=2,'Unexpected 3+ source edge on manifold CAD cohort')
        for ids in side_uses[1:]:
            ensure(ids in (side_uses[0],side_uses[0][::-1]),
                   f'Broken global source edge identity: {eid}')
    diag=source_shape.BoundingBox().DiagonalLength
    budget=max(1e-8,diag*1e-9)
    ensure(maximum<=budget,'Partial BP does not lie on original CAD face')
    ensure(set(range(len(face_list))) == included | {r['source_face'] for r in sidecar['exclusions']},
           'Unaccounted source face')
    return {'schema':'apmesh-original-cad-independent-planar-audit-v1',
            'result':'PARTIAL_FACE_ATLAS_AUDITED',
            'source_model':sidecar['source_model'],'source_sha256':source_sha256,
            'validated_patches':len(patches),'excluded_source_faces':sidecar['excluded_face_count'],
            'distinct_source_edges_in_atlas':len(uses),
            'maximum_source_edge_incidence_in_atlas':max(map(len,uses.values()),default=0),
            'independent_sample_count':len(patches)*len(grid)**2,
            'maximum_native_distance_mm':maximum,'budget_mm':budget,
            'complete_original_model':'NOT_CLAIMED',
            'apmesh_accepted_mesh':'NOT_RUN'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--bp',type=Path,required=True)
    parser.add_argument('--sidecar',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    args=parser.parse_args()
    digest=sha256(args.source.read_bytes()).hexdigest()
    ensure(digest==args.expected_sha256,'Pinned source file mismatch')
    result=audit(cq.importers.importStep(str(args.source)).val(),
                 args.bp.read_text(),json.loads(args.sidecar.read_text()),source_sha256=digest)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':
    main()
