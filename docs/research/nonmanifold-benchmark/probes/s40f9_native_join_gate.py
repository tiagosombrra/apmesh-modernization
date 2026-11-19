#!/usr/bin/env python3
"""Fail-closed original-STEP S40-F9 -> frozen S3.Y native join preflight.

Unlike the older F7 gate, this entrypoint uses the exact-regular F9 island,
never the rejected frozen F6 island. It does not claim execution without the
original S40 STEP and original private S3.Y BP, both hash-pinned.
"""
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
import sys

import s40f7_parent_lineage_rebase as f7
import s40f9_independent_certificate as independent
import s40f9_regularized_source_island as f9


def private_f9_native_trial(*, original_step_path, s3y_bp_path,
                            original_f6_bp_path, original_f6_manifest_path,
                            f9_bp_path, f9_manifest_path,
                            original_f5_spec_path, original_f6_spec_path,
                            parent_source_lineage_path=None):
    """Do not perform original CAD import until every private digest matches."""
    source=Path(original_step_path).read_bytes()
    if sha256(source).hexdigest()!=f7.SOURCE_SHA:
        raise ValueError('Original source STEP digest not frozen S40 SHA-256')
    parent=Path(s3y_bp_path).read_bytes()
    if sha256(parent).hexdigest()!=f7.S3Y_SHA:
        raise ValueError('Frozen 156-patch S3.Y parent SHA-256 mismatch')
    old=Path(original_f6_bp_path).read_bytes()
    if sha256(old).hexdigest()!=independent.FROZEN_F6_SHA:
        raise ValueError('Original F6 candidate BP digest mismatch')
    candidate=Path(f9_bp_path).read_bytes()
    if sha256(candidate).hexdigest()!=independent.F9_SHA:
        raise ValueError('Regularized F9 candidate BP digest mismatch')
    original_manifest=json.loads(Path(original_f6_manifest_path).read_bytes())
    candidate_manifest=json.loads(Path(f9_manifest_path).read_bytes())
    f5_spec=Path(original_f5_spec_path).read_bytes()
    f6_spec=Path(original_f6_spec_path).read_bytes()
    independent_proof=independent.audit_candidate_independent(
        old,candidate,original_manifest,candidate_manifest)
    canonical,proof=f9.regularize_frozen_f6(old,original_manifest,f5_spec,f6_spec)
    if canonical.encode()!=candidate or proof!=candidate_manifest:
        raise ValueError('F9 exact-regular BP not the deterministic pinned reproduction')
    if independent_proof['strict_positive_full_domain_count']!=8:
        raise ValueError('F9 exact Bernstein regularity not certified')
    source_graph=f7.source_graph_gate(source)
    parent_points,parent_patches=f7.read_indexed_bp(parent.decode('utf-8'))
    if (len(parent_points),len(parent_patches))!=(1665,156):
        raise ValueError('Frozen S3.Y control or patch count changed')
    _,_,inventory=f7.isolated_gate(old,original_manifest)
    child_points,child_patches=f7.read_indexed_bp(candidate.decode('utf-8'))
    if (len(child_points),len(child_patches))!=(104,8):
        raise ValueError('Regularized candidate topology malformed')
    import cadquery as cq
    from s3s_full_original_face_census import full_correspondence
    native=cq.importers.importStep(str(original_step_path)).val()
    source_mapping=full_correspondence(source.decode('ascii'),native)
    if parent_source_lineage_path is None:
        lineage,lineage_proof=f7.discover_original_parent_lineage(
            source,native,source_mapping,parent,parent_points,parent_patches)
    else:
        lineage=f7.validate_lineage(
            json.loads(Path(parent_source_lineage_path).read_bytes()),parent)
        lineage_proof={'source_lineage_discovery':'EXPLICIT_SOURCE_LINEAGE_NATIVE_OWNER_CHECK'}
    points,patches,rebased=f7.rebase_core(parent_points,parent_patches,
        child_points,child_patches,original_manifest,lineage,
        parent_expected_seams=264,parent_expected_open=96)
    if (len(points),len(patches))!=(1743,164):
        raise ValueError('164-patch structural source join cardinality changed')
    # Reindexing may substitute parent control coordinates; certify the final BP.
    from s40f10_postrebase_exact_certificate import certify_postrebase_eight
    serialized_joined_bp=f7.serialize_bp(points,patches)
    postrebase_proof=certify_postrebase_eight(serialized_joined_bp.encode('utf-8'))
    native_proof=f7.original_native_gate(
        source,original_step_path,points,patches,original_manifest,rebased,
        preimported_native=native,preverified_mapping=source_mapping)
    if native_proof.get('status')!='PASS_SAMPLED_ORIGINAL_NATIVE_GATES':
        raise ValueError('Native original CAD audit not PASS')
    report={**rebased,**source_graph,**lineage_proof,
            'stage':'S40-F9_SOURCE_ORIGINAL_NATIVE_RECONCILIATION',
            'classification':'ORIGINAL_NATIVE_SAMPLED_RESEARCH_CANDIDATE',
            'original_s3y_parent_bp_sha256':f7.S3Y_SHA,
            'regularized_island_bp_sha256':independent.F9_SHA,
            'exact_bernstein_strict_positive_eight':True,
            'postrebase_exact_jacobian_proof':postrebase_proof,
            'all_original_native_trim_and_edge_gates_executed':True,
            'original_native_audit':native_proof,
            'apmesh_cpp_tri_quad_executed':False,
            'full_43_face_atlas_complete':False,
            'formal_continuous_original_STEP_hausdorff_certified':False}
    return serialized_joined_bp,report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('original-step','s3y-bp','original-f6-bp','original-f6-manifest',
                'f9-bp','f9-manifest','original-f5-spec','original-f6-spec','output-dir'):
        p.add_argument('--'+key,required=True)
    p.add_argument('--parent-source-lineage',default=None)
    a=vars(p.parse_args())
    # Never allow an earlier candidate directory to masquerade as this run.
    from s40f11_atomic_candidate_delivery import (
        publish_native_candidate, require_fresh_destination,
    )
    try:
        require_fresh_destination(a['output_dir'])
        candidate,receipt=private_f9_native_trial(
            original_step_path=a['original_step'],
            s3y_bp_path=a['s3y_bp'],
            original_f6_bp_path=a['original_f6_bp'],
            original_f6_manifest_path=a['original_f6_manifest'],
            f9_bp_path=a['f9_bp'],f9_manifest_path=a['f9_manifest'],
            original_f5_spec_path=a['original_f5_spec'],
            original_f6_spec_path=a['original_f6_spec'],
            parent_source_lineage_path=a['parent_source_lineage'])
        publish_native_candidate(a['output_dir'],candidate,receipt)
    except (OSError,ValueError,KeyError,TypeError,UnicodeError) as error:
        output_target=Path(a['output_dir'])
        print(json.dumps({'classification':'BLOCKED_NO_NATIVE_ADMISSION',
                          'error':type(error).__name__+': '+str(error),
                          'new_candidate_emitted_this_run':False,
                          'output_destination_preexisting':output_target.exists() or output_target.is_symlink(),
                          'new_source_faces_admitted':0},
                         sort_keys=True),file=sys.stderr)
        return 3
    print(json.dumps({'classification':receipt['classification'],
                      'candidate_patches':164,'candidate_original_source_faces':26,
                      'new_source_faces_homologated':0,
                      'continuous_original_STEP_geometry_proof':False,
                      'apmesh_cpp_tri_quad_executed':False},sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
