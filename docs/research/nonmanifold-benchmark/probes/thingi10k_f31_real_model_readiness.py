#!/usr/bin/env python3
"""Reconcile immutable F17/F20 model cohort with later F27/F30 evidence.

This is a metadata admission ledger, not a download, a rights grant or a new
mesh generation. It never reads STL, BP, OBJ or their full geometric snapshots.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

SOURCE_CSV_PATH='docs/research/nonmanifold-benchmark/THINGI10K_F17_PINNED_SOURCES_23.csv'
F27_RECEIPT_PATH='docs/research/nonmanifold-benchmark/evidence/thingi10k/thingi10k_f27_real_native_tri_receipt.json'
F30_RECEIPT_PATH='docs/research/nonmanifold-benchmark/evidence/thingi10k/thingi10k_f30_final_real_pareto_receipt.json'
SOURCE_CSV_GIT_BLOB='5db6442ab09a5a06aa3736558bdc45f22943a1c7'
F27_RECEIPT_GIT_BLOB='20a7cea865749ffc0f1608654642f38fdb8d19d2'
F30_RECEIPT_GIT_BLOB='69d9424421fd1d290dbd915b18fc49ff2d6e6011'
EXPECTED_COHORT={'QUADWILD_FIG29':12,'BADIA_FIG10_TABLE1':11}
EXPECTED_IDS=(35269,37266,37881,441708,47076,550964,551021,65904,96457,
              252119,293137,44503,58012,61394,67792,69975,81877,94884,
              128001,230923,364256,423069,498974)
PILOTS={293137,37881,47076}
STRESS={550964,96457}
REFERENCE_PRIORITY={58012}
ADVERSARIAL={61394}
AUDITED={58012,61394,293137,37881,47076,550964,96457}
SCHEMA='apmesh-s40-f31-real-model-readiness-delta-v1'


def require(ok:bool,why:str)->None:
    if not ok:raise ValueError(why)


def blob(raw:bytes)->str:
    return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()


def pinned_file(root:Path,relative:str,git_blob:str)->bytes:
    file=root/relative
    require(file.is_file() and file.stat().st_size<50_000,'Missing or oversized pinned metadata')
    raw=file.read_bytes()
    require(blob(raw)==git_blob,'Historical model provenance/evidence changed')
    return raw


def role_of(mid:int)->str:
    if mid in REFERENCE_PRIORITY:return 'EXACT_AUTHOR_REFERENCE_ACQUISITION_FIRST'
    if mid in ADVERSARIAL:return 'SOURCE_TOPOLOGY_NEGATIVE_CONTROL'
    if mid in PILOTS:return 'SMALL_SOURCE_CONVERSION_PILOT'
    if mid in STRESS:return 'HIGH_GENUS_SOURCE_CONVERSION_STRESS'
    return 'SOURCE_GEOMETRY_AUDIT_REQUIRED'


def reconcile(source_raw:bytes,f27:dict,f30:dict)->dict:
    source_text=source_raw.decode('utf-8')
    source=list(csv.DictReader(io.StringIO(source_text)))
    ids=[int(x['thingi10k_file_id']) for x in source]
    require(len(ids)==23 and len(set(ids))==23 and set(ids)==set(EXPECTED_IDS),
            'The historical 23-case source cohort changed')
    require(Counter(x['literature_cohort'] for x in source)==EXPECTED_COHORT,
            'Historical cohort cardinalities changed')
    require({int(row['thingi10k_file_id']) for row in source if row['raw_stl_audit_executed']=='YES'}
            ==AUDITED,'Historical seven original STL audits changed')
    require(all(row['original_source_rights_independently_verified']=='NO' and
                row['quadwild_reference_mesh_pair_verified']=='NO' and
                row['apmesh_mesh_generated']=='NO' for row in source),
            'F17 historical snapshot must remain unchanged and conservative')
    require(f27['schema']=='apmesh-s40-f27-original-tri-stage0-audit-v1' and
            f27['source_model_id']==293137 and
            f27['native_stage0_accepted_by_engine'] is True and
            f27['asset_license_independently_cleared'] is False and
            f27['scientific_benchmark_admitted'] is False and
            f27['native_triangles']==3504,
            'F27 actual TRI evidence does not qualify the metadata transition')
    require(f30['schema']=='apmesh-s40-f30-feature-locked-pareto-center-v1' and
            f30['source_facets']==292 and f30['quad_faces']==876 and
            f30['copyright_license_cleared'] is False and
            f30['native_quad_generator_executed'] is False and
            f30['independent_matched_quad_literature_reference'] is False and
            f30['scientific_benchmark_admitted'] is False,
            'F30 external QUAD cannot be promoted to native science')
    entries=[]
    for row in sorted(source,key=lambda x:int(x['thingi10k_file_id'])):
        mid=int(row['thingi10k_file_id'])
        entries.append({'model_id':mid,'cohort':row['literature_cohort'],
                        'scientific_priority':role_of(mid),
                        'original_stl_topology_audited':mid in AUDITED,
                        'asset_rights_independently_cleared':False,
                        'original_author_quad_output_pair_verified':False,
                        'native_apmesh_tri_model_executed':mid==293137,
                        'external_derived_quad_experiment_executed':mid==293137,
                        'native_apmesh_quad_executed':False,
                        'fair_comparison_admitted':False})
    return {'schema':SCHEMA,'historical_f17_snapshot_unchanged':True,
            'followup_f27_f30_metadata_delta_only':True,
            'rights_still_uncleared':True,'original_quad_reference_pairs_verified':0,
            'native_quad_runs':0,'fair_literature_comparisons_admitted':0,
            'source_cohort_counts':dict(sorted(EXPECTED_COHORT.items())),
            'case_count':len(entries),'raw_stls_audited_in_f17':len(AUDITED),
            'new_real_native_tri_model_count_since_f17':1,
            'new_external_derived_quad_model_count_since_f17':1,
            'cases':entries}


def produce(root:Path):
    data=pinned_file(root,SOURCE_CSV_PATH,SOURCE_CSV_GIT_BLOB)
    f27=json.loads(pinned_file(root,F27_RECEIPT_PATH,F27_RECEIPT_GIT_BLOB))
    f30=json.loads(pinned_file(root,F30_RECEIPT_PATH,F30_RECEIPT_GIT_BLOB))
    return reconcile(data,f27,f30)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    data=produce(args.root)
    require(not args.output.exists(),'Existing case ledger must not be overwritten')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as f:
        json.dump(data,f,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)
        f.write('\n')
    print('F31 source-model readiness metadata gate PASS')


if __name__=='__main__':main()
