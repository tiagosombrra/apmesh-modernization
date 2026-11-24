#!/usr/bin/env python3
"""Independent fixed-input check of the S40-F9 private source-island BP.

This module never invokes the F9 geometry producer. It checks exact decimals,
unchanged S3.Y interface chains, indexed source seam orientation and all eight
rational Bernstein Jacobians. Native original STEP validation is not implied.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import json

from s40f8_exact_planar_jacobian import (
    parse_decimal_bp, jacobian_net, certify_strict_sign, FACE_IDS, NORMALS)

FROZEN_F6_SHA='72b8756c948a7a7da19c9f2a9a7099673e81a30573f19e4820abf27ba720f0a7'
F9_SHA='328ff1ca784b4a82d2bd566309c21d7263cc5134ae37e7b1f4554acd7fd26e38'
EXPECTED_INHERITED=('old:1002','old:1080','old:1139','old:1259',
                    'old:1284','old:1473','new:1030:0','new:1057:0')
EXPECTED_CHANGING_CIRCLE_EDGES=(1307,1336,1415,1444)


def audit_candidate_independent(original_bytes:bytes, candidate_bytes:bytes,
                                 original_manifest:dict, new_manifest:dict):
    """Certify the byte-pinned BP without importing the construction code."""
    if sha256(original_bytes).hexdigest()!=FROZEN_F6_SHA:
        raise ValueError('Wrong original immutable F6 input digest')
    if sha256(candidate_bytes).hexdigest()!=F9_SHA:
        raise ValueError('Wrong F9 candidate BP digest')
    if (new_manifest.get('schema')!='apmesh-s40f9-regularized-four-face-source-island-v1'
        or new_manifest.get('candidate_bp_sha256')!=F9_SHA
        or new_manifest.get('original_f6_bp_sha256')!=FROZEN_F6_SHA
        or new_manifest.get('classification')!='ISOLATED_ANALYTIC_CANDIDATE_NOT_ORIGINAL_NATIVE_ADMITTED'
        or new_manifest.get('source_faces_newly_admitted')!=0
        or new_manifest.get('parent_s3y_joined') is not False):
        raise ValueError('F9 classification or provenance altered')
    original,patches_old=parse_decimal_bp(original_bytes)
    candidate,patches=parse_decimal_bp(candidate_bytes)
    if patches!=patches_old:
        raise ValueError('Original STEP source island patch connectivity modified')
    edited=set(new_manifest['edited_circular_handle_control_ids']+new_manifest['recomputed_coons_interior_control_ids'])
    if (len(new_manifest['edited_circular_handle_control_ids'])!=8 or
        len(new_manifest['recomputed_coons_interior_control_ids'])!=16 or
        len(edited)!=24):
        raise ValueError('Unexpected source-circular or Coons edit cardinality')
    actual_changes={i for i,(a,b) in enumerate(zip(original,candidate)) if a!=b}
    if not actual_changes.issubset(edited) or not set(new_manifest['edited_circular_handle_control_ids']).issubset(actual_changes):
        raise ValueError('Unexpected original BP controls modified or circular edits absent')
    if any(candidate[i]!=original[i] for i in range(104) if i not in edited):
        raise ValueError('Inherited control changed')
    source_ids=original_manifest['source_segment_ids']
    if (new_manifest['source_segment_ids']!=source_ids
        or len(source_ids)!=20 or
        set(new_manifest['unchanged_parent_interface_source_keys'])!=set(EXPECTED_INHERITED)):
        raise ValueError('Original source edge registry changed')
    for key in EXPECTED_INHERITED:
        ids=source_ids[key]
        if any(candidate[i]!=original[i] for i in ids):
            raise ValueError('Previously represented original source edge changed')
    for eid in EXPECTED_CHANGING_CIRCLE_EDGES:
        ids=source_ids['old:'+str(eid)]
        if not (ids[1] in edited and ids[2] in edited and
                candidate[ids[0]]==original[ids[0]] and
                candidate[ids[3]]==original[ids[3]]):
            raise ValueError('Original circular STEP edge endpoint lineage changed')
    incidence=defaultdict(list)
    for pid,patch in enumerate(patches):
        sides=[patch[:4],patch[3::4],patch[-4:],patch[::4]]
        for side_index,ids in enumerate(sides):
            ids=tuple(ids)
            oriented=ids if side_index<2 else ids[::-1]
            incidence[tuple(sorted(ids))].append((pid,oriented))
    joints=[v for v in incidence.values() if len(v)==2]
    opens=[v[0] for v in incidence.values() if len(v)==1]
    if len(joints)!=6 or len(opens)!=20 or any(len(v)>2 for v in incidence.values()):
        raise ValueError('Indexed edge incidence changed')
    if any(a[1]!=b[1][::-1] for a,b in joints):
        raise ValueError('Indexed seam does not reverse orientation')
    if {tuple(sorted(row[1])) for row in opens}!={tuple(sorted(ids)) for ids in source_ids.values()}:
        raise ValueError('Open source edge identity not preserved')
    certs=[]
    for pid,patch in enumerate(patches):
        net=jacobian_net(candidate,patch,NORMALS[FACE_IDS[pid]])
        signed=certify_strict_sign(net,max_depth=12)
        if signed['status']!='CERTIFIED_POSITIVE':
            raise ValueError(f'Patch {pid} exact Jacobian is not strictly positive')
        certs.append({'patch_index':pid,'source_face_id':FACE_IDS[pid],
                      'strict_bernstein_lower_mm2':signed['strict_lower_bound_mm2'],
                      'exact_domain_positivity_certified':True})
    return {'status':'CERTIFIED_STRICT_POSITIVE_DECIMAL_BP_ISOLATED',
            'candidate_bp_sha256':F9_SHA,'patch_count':len(patches),
            'global_control_count':len(candidate),'original_source_face_ids':sorted(set(FACE_IDS)),
            'exact_positive_patch_certificates':certs,
            'strict_positive_full_domain_count':len(certs),
            'source_indexed_internal_seams':len(joints),'source_indexed_open_sides':len(opens),
            'original_f6_input_remains_unchanged':True,
            'eight_previous_parent_source_interfaces_numerically_unchanged':True,
            'original_step_native_import_executed':False,'joined_with_s3y':False,
            'source_faces_newly_admitted':0}


def main():
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('--original-f6-bp',type=Path,required=True)
    args.add_argument('--candidate-f9-bp',type=Path,required=True)
    args.add_argument('--original-f6-manifest',type=Path,required=True)
    args.add_argument('--candidate-f9-manifest',type=Path,required=True)
    args.add_argument('--output',type=Path,required=True)
    a=args.parse_args()
    proof=audit_candidate_independent(a.original_f6_bp.read_bytes(),
        a.candidate_f9_bp.read_bytes(),json.loads(a.original_f6_manifest.read_text()),
        json.loads(a.candidate_f9_manifest.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(proof,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k!='exact_positive_patch_certificates'},sort_keys=True))

if __name__=='__main__':main()
