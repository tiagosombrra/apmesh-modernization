#!/usr/bin/env python3
"""Construct a segmented, source-attributed bicubic cylinder research fixture.

Derived seams are shared by explicit segmentation identity, never by welding
coincident but unrelated original CAD edges. No APMesh meshing is implied.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRep import BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepTools import BRepTools

from audit_analytic_bp import surface as casteljau_surface
from s3b_cylindrical_bicubic_pilot import (
    UnsupportedGeometry, approximate_cylindrical_face, synthetic_quarter_cylinder,
)


SIDES=((0,1,2,3),(3,7,11,15),(12,13,14,15),(0,4,8,12))


def construct(source_face, count, *, absolute_budget_mm, relative_budget, source_label):
    """Produce indexed BP with explicit seam provenance and per-patch audit."""
    if not isinstance(count,int) or count < 1 or count > 64:
        raise ValueError('Segment count outside bounded range [1,64]')
    if source_face.geomType()!='CYLINDER' or len(source_face.Wires())!=1 or len(source_face.Wires()[0].Edges())!=4:
        raise UnsupportedGeometry('Source must be one cylindrical four-side face')
    u0,u1,v0,v1=BRepTools.UVBounds_s(source_face.wrapped)
    if not (0 < u1-u0 <= math.pi/2+1e-9 and v1 > v0):
        raise UnsupportedGeometry('Only bounded quarter-cylinder source faces admitted')
    basis=BRep_Tool.Surface_s(source_face.wrapped)
    vertices=[]
    control_keys={}
    records=[]
    raw_errors=[]
    for part in range(count):
        lo=u0+(u1-u0)*part/count
        hi=u0+(u1-u0)*(part+1)/count
        native_derived=cq.Face(BRepBuilderAPI_MakeFace(basis,lo,hi,v0,v1,1e-7).Face())
        net,result=approximate_cylindrical_face(
            native_derived,absolute_budget_mm=absolute_budget_mm,
            relative_budget=relative_budget)
        ids=[]
        for row in range(4):
            for col in range(4):
                # Only derived split seams, explicitly identified by partition,
                # are shared; coordinate similarity never confers equivalence.
                if col==0 and part>0:
                    key=('seam',part,row)
                elif col==3 and part<count-1:
                    key=('seam',part+1,row)
                else:
                    key=('unique',part,row,col)
                xyz=net[row*4+col]
                if key in control_keys:
                    id_=control_keys[key]
                    if math.dist(vertices[id_],xyz) > 1e-10:
                        raise ValueError('Derived seam control mismatch')
                else:
                    id_=len(vertices)
                    vertices.append(xyz)
                    control_keys[key]=id_
                ids.append(id_)
        curves=[]
        for side,offsets in enumerate(SIDES):
            if side==3 and part>0:
                name=f'derived_u_seam_{part}'
            elif side==1 and part<count-1:
                name=f'derived_u_seam_{part+1}'
            else:
                name=f'part_{part}_side_{side}'
            curves.append({'local_side':side,'curve_id':name,'control_vertex_ids':[ids[k] for k in offsets],
                           'provenance':('DERIVED_PARTITION_SEAM' if name.startswith('derived_') else 'SOURCE_BOUNDARY_PORTION_NOT_NATIVE_EDGE_MATCHED')})
        records.append({'source_face_label':source_label,'segment_index':part,
                        'native_u_interval':[lo,hi], 'native_v_interval':[v0,v1],
                        'control_vertex_ids':ids,'sides':curves,
                        'max_pointwise_sampled_error_mm':result['maximum_pointwise_sampled_error_mm'],
                        'native_face_max_distance_mm':result['native_face_max_distance_mm'],
                        'budget_pass':result['budget_pass']})
        raw_errors.append(result['maximum_pointwise_sampled_error_mm'])
    # Explicitly prove the derived seam shares global IDs, possibly reversed.
    histogram=Counter(side['curve_id'] for rec in records for side in rec['sides'])
    seam_names={f'derived_u_seam_{i}' for i in range(1,count)}
    if any(histogram[name]!=2 for name in seam_names):
        raise ValueError('Derived seam is not referenced by two patches')
    if any(n!=1 for name,n in histogram.items() if name not in seam_names):
        raise ValueError('Wrong boundary multiplicity')
    if len(vertices)!=12*count+4:
        raise ValueError('Unexpected global control budget')
    lines=[f'// {count}-segment author-derived cylinder research fixture',
           '// Not an admitted original CAD model or APMesh accepted mesh']
    lines.extend('v '+' '.join(format(x,'.17g') for x in point) for point in vertices)
    lines.extend('p '+' '.join(map(str,r['control_vertex_ids'])) for r in records)
    bp='\n'.join(lines)+'\n'
    manifest={
        'schema':'apmesh-s3b-segmented-cylinder-v1','source_face_label':source_label,
        'source_kind':'SOURCE_FACE_WITH_EXPLICIT_DERIVED_U_PARTITIONS',
        'original_source_edge_adjacency':'NOT_ESTABLISHED',
        'segments':count,'patch_count':count,'unique_control_vertices':len(vertices),
        'derived_shared_seams':count-1,'curve_incidence':dict(sorted(Counter(histogram.values()).items())),
        'predeclared_absolute_budget_mm':absolute_budget_mm,
        'predeclared_relative_budget':relative_budget,
        'maximum_pointwise_sampled_error_mm':max(raw_errors),
        'all_segments_meet_budget':all(r['budget_pass'] for r in records),
        'continuum_error_certified':False,
        'patches':records,'bp_sha256':sha256(bp.encode()).hexdigest(),
        'original_external_nonmanifold_status':'NOT_GRANTED',
        'apmesh_generation':'NOT_RUN',
    }
    return bp,manifest


def independent_audit(original_face, bp, manifest):
    """Recheck seams and source geometry without reusing fit interpolation."""
    from audit_analytic_bp import read_bp
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    if sha256(bp.encode()).hexdigest()!=manifest['bp_sha256']:
        raise ValueError('Corrupted BP digest')
    vertices,patches=read_bp(bp)
    if len(patches)!=manifest['patch_count'] or len(vertices)!=manifest['unique_control_vertices']:
        raise ValueError('Patch count/vertex count mismatch')
    adaptor=BRepAdaptor_Surface(original_face.wrapped,True)
    u0,u1,v0,v1=BRepTools.UVBounds_s(original_face.wrapped)
    seams={}
    max_error=0.
    for i,(ids,rec) in enumerate(zip(patches,manifest['patches'])):
        if list(ids)!=rec['control_vertex_ids']:
            raise ValueError('Patch ids mismatch')
        net=[vertices[k] for k in ids]
        for ustep in range(35):
            u=ustep/34
            for vstep in range(35):
                v=vstep/34
                expected=adaptor.Value(u0+(u1-u0)*(i+u)/len(patches),v0+(v1-v0)*v)
                p=casteljau_surface(net,u,v)
                max_error=max(max_error,math.dist(p,(expected.X(),expected.Y(),expected.Z())))
        for side in rec['sides']:
            if side['curve_id'].startswith('derived_u_seam'):
                seams.setdefault(side['curve_id'],[]).append(side['control_vertex_ids'])
                if side['control_vertex_ids']!=[ids[k] for k in SIDES[side['local_side']]]:
                    raise ValueError('Sidecar/BP seam record mismatch')
    if len(seams)!=manifest['derived_shared_seams']:
        raise ValueError('Incorrect number of derived seams')
    for group in seams.values():
        if len(group)!=2 or (group[0]!=group[1] and group[0]!=group[1][::-1]):
            raise ValueError('Derived seam does not retain exact shared control identities')
    budget=min(manifest['predeclared_absolute_budget_mm'],
               manifest['predeclared_relative_budget']*original_face.BoundingBox().DiagonalLength)
    return {'schema':'apmesh-s3b-independent-segment-audit-v1',
            'sample_count':len(patches)*35*35,'derived_seams_checked':len(seams),
            'maximum_independent_parametric_distance_mm':max_error,
            'predeclared_original_face_budget_mm':budget,
            'audit_budget_pass':max_error<=budget,
            'continuous_distance_bound':'NOT_CERTIFIED',
            'apmesh_generation':'NOT_RUN'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--segments',type=int,required=True)
    p.add_argument('--absolute-budget-mm',type=float,required=True)
    p.add_argument('--relative-budget',type=float,required=True)
    p.add_argument('--out-bp',type=Path,required=True)
    args=p.parse_args()
    original=synthetic_quarter_cylinder()
    bp,manifest=construct(original,args.segments,
                          absolute_budget_mm=args.absolute_budget_mm,
                          relative_budget=args.relative_budget,
                          source_label='AUTHOR_CONSTRUCTED_QUARTER_CYLINDER')
    audit=independent_audit(original,bp,manifest)
    args.out_bp.parent.mkdir(parents=True,exist_ok=True)
    args.out_bp.write_text(bp)
    args.out_bp.with_suffix('.json').write_text(json.dumps({'manifest':manifest,'independent_audit':audit},indent=2,sort_keys=True)+'\n')
    print(json.dumps({'segments':args.segments,'max_mm':manifest['maximum_pointwise_sampled_error_mm'],
                      'fit_pass':manifest['all_segments_meet_budget'],
                      'independent_max_mm':audit['maximum_independent_parametric_distance_mm'],
                      'independent_pass':audit['audit_budget_pass']},sort_keys=True))


if __name__=='__main__':
    main()
