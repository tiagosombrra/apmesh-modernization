#!/usr/bin/env python3
"""Independently inspect the isolated S40-F6 indexed BP and private sidecar.

This audit does not invoke the S40-F6 builder or treat original STEP-derived
surrogates as a native import of the complete original industrial CAD model.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

EXPECTED_F5_BP_SHA = '2fd7d00234aea44aefdca4fce12f8dd8b2e9397122c366ed025c77bff714810d'
EXPECTED_F6_SPEC_SHA = '356d508c4b14f02bbc63f391e40128c41cdf0e170bfb219282594feaa792e671'
SOURCE_SHA = 'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b'
FACES = (1279, 1279, 1386, 1386, 3269, 3269, 3485, 3485)


def read_bp(content):
    """Parse indexed BP independently; require all point records before patches."""
    control,patches=[],[]
    in_patches=False
    for no,raw in enumerate(content.splitlines(),1):
        line=raw.split('//',1)[0].strip()
        if not line:continue
        r=line.split()
        if r[0]=='v' and len(r)==4 and not in_patches:
            value=tuple(float(x) for x in r[1:])
            if not all(math.isfinite(x) for x in value):raise ValueError('Nonfinite control')
            control.append(value)
        elif r[0]=='p' and len(r)==17:
            in_patches=True
            value=tuple(int(x) for x in r[1:])
            if any(v<0 or v>=len(control) for v in value):raise ValueError('Invalid control index')
            patches.append(value)
        else:raise ValueError(f'Malformed indexed BP line {no}')
    return control,patches


def edges(patch):
    """Yield CCW oriented sides even though patch storage is row-major."""
    return [tuple(patch[:4]),tuple(patch[3::4]),
            tuple(reversed(patch[-4:])),tuple(reversed(patch[::4]))]


def cubic(points, t):
    w=((1-t)**3,3*t*(1-t)**2,3*t*t*(1-t),t**3)
    return tuple(sum(w[j]*points[j][k] for j in range(4)) for k in range(3))


def planar_integrity(points,patches,spec):
    """Audit the four added face patches against their independent plane data."""
    samples=0
    for i in range(4,8):
        fid=FACES[i]
        raw=spec['faces'][str(fid)]
        normal=tuple(raw['plane_axis']);base=raw['plane_location']
        patch=patches[i]
        if any(abs(sum(normal[k]*(points[idx][k]-base[k]) for k in range(3)))>1e-7 for idx in patch):
            raise ValueError('Indexed control left original source support plane')
        net=[points[j] for j in patch]
        for t in (0.17,0.39,0.71):
            for u in (0.21,0.55,0.81):
                w=lambda x:((1-x)**3,3*x*(1-x)**2,3*x*x*(1-x),x**3)
                d=lambda x:(-3*(1-x)**2,3*(1-x)**2-6*x*(1-x),6*x*(1-x)-3*x*x,3*x*x)
                du=[sum(w(u)[j]*d(t)[k]*net[4*j+k][c] for j in range(4) for k in range(4)) for c in range(3)]
                dv=[sum(d(u)[j]*w(t)[k]*net[4*j+k][c] for j in range(4) for k in range(4)) for c in range(3)]
                cross=(du[1]*dv[2]-du[2]*dv[1],du[2]*dv[0]-du[0]*dv[2],du[0]*dv[1]-du[1]*dv[0])
                if sum(cross[k]*normal[k] for k in range(3))<=0:
                    raise ValueError('Source face has nonpositive oriented Jacobian')
                samples+=1
    return samples


def audit(bp_path,sidecar_path,f5_bp_path,f6_spec_path):
    """Fail closed on input identity, indexed incidence or source-lineage drift."""
    bp=Path(bp_path).read_bytes();old=Path(f5_bp_path).read_bytes()
    spec=Path(f6_spec_path).read_bytes();receipt=json.loads(Path(sidecar_path).read_bytes())
    if hashlib.sha256(old).hexdigest()!=EXPECTED_F5_BP_SHA:
        raise ValueError('Wrong frozen original F5 parent')
    if hashlib.sha256(spec).hexdigest()!=EXPECTED_F6_SPEC_SHA:
        raise ValueError('Wrong original-source-derived vertical face specification')
    if (receipt.get('bp_sha256')!=hashlib.sha256(bp).hexdigest() or
            receipt.get('f5_original_bp_sha256')!=EXPECTED_F5_BP_SHA or
            receipt.get('f6_source_private_spec_sha256')!=EXPECTED_F6_SPEC_SHA or
            receipt.get('step_original_sha256_reference')!=SOURCE_SHA or
            receipt.get('parent_S3Y_joined') is not False or
            receipt.get('newly_admitted_original_source_faces')!=0):
        raise ValueError('Candidate sidecar authenticity/status mismatch')
    points,patches=read_bp(bp.decode('utf-8'));prior,oldpatches=read_bp(old.decode('utf-8'))
    if len(points)!=104 or len(patches)!=8 or len(prior)!=56 or len(oldpatches)!=4:
        raise ValueError('Unexpected source-island cardinality')
    if points[:len(prior)]!=prior or patches[:len(oldpatches)]!=oldpatches:
        raise ValueError('Frozen 56-control/4-patch F5 prefix changed')
    if tuple(receipt.get('face_ids_per_patch',()))!=FACES:
        raise ValueError('Original source face per patch mapping changed')
    incidence=defaultdict(list)
    for pid,patch in enumerate(patches):
        for side in edges(patch):
            incidence[tuple(sorted(side))].append((pid,side))
    if any(len(x)>2 for x in incidence.values()):raise ValueError('Unexpected 3+ control-side users')
    pairs=[x for x in incidence.values() if len(x)==2]
    opens=[x[0][1] for x in incidence.values() if len(x)==1]
    if len(pairs)!=6 or len(opens)!=20:raise ValueError('Wrong global seam/open-side counts')
    for x in pairs:
        if x[0][1]!=x[1][1][::-1]:raise ValueError('Indexed seam orientation mismatch')
    registry=receipt.get('source_segment_ids')
    if not isinstance(registry,dict) or len(registry)!=20:
        raise ValueError('Missing original STEP source-side registry')
    expected={tuple(sorted(v)):str(k) for k,v in registry.items()}
    if len(expected)!=20 or set(expected)!={tuple(sorted(x)) for x in opens}:
        raise ValueError('Open indexed side not exactly source-registered')
    f6=json.loads(spec)
    checks=planar_integrity(points,patches,f6)
    needed={3269:1392,3485:1365}
    cross=[]
    for face,edge in needed.items():
        exact=[(a,b) for a,b in pairs if {FACES[a[0]],FACES[b[0]]}=={face,1386 if face==3269 else 1279}]
        if len(exact)!=1:raise ValueError('Original vertical/horizontal seam not paired exactly once')
        cross.append({'original_step_edge_id':edge,'source_face_pair':sorted([face,1386 if face==3269 else 1279])})
    for face in (3269,3485):
        detail=receipt['new_reconstructed_faces'][str(face)]
        split=int(detail['split_source_edge_id'])
        if (split in (1392,1365,1057,1030) or
                [f'new:{split}:{j}' in registry for j in (0,1)]!=[True,True]):
            raise ValueError('Split source edge is inherited or not explicitly tracked')
    return {'state':'INDEPENDENT_ISOLATED_INDEXED_BP_PASS',
            'four_original_source_face_ids':sorted(set(FACES)),
            'patches':len(patches),'global_controls':len(points),
            'two_sided_seams':len(pairs),'registered_open_sides':len(opens),
            'original_source_face_cross_interfaces':cross,
            'new_patch_oriented_jacobian_samples':checks,
            'parent_F5_exact_numeric_prefix_preserved':True,
            'fully_native_original_STEP_imported':False,
            'joined_to_156_patch_S3Y':False,'source_faces_admitted_to_S3Y':0}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('bp','sidecar','f5-bp','f6-spec'):p.add_argument('--'+key,required=True)
    args=p.parse_args()
    print(json.dumps(audit(args.bp,args.sidecar,args.f5_bp,args.f6_spec),indent=2,sort_keys=True))


if __name__=='__main__':main()
