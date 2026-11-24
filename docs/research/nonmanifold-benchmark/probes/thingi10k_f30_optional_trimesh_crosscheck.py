#!/usr/bin/env python3
"""Independently cross-check private F29/F30 quad topology using Trimesh.

The original OBJ geometry is never copied into the output JSON or source tree.
Trimesh triangulates four-sided OBJ faces internally for its own measurements.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import thingi10k_f30_feature_locked_quad_center_optimizer as f30

EXPECTED_F30_QUAD_SHA256 = '7714c25de7774521d59157ba49e0733d315d462ab05117e2b578dcc57f596be4'
EXPECTED_F30_OBJ_BYTES = 39150


def verify(path_f29: Path, path_f30: Path, output: Path) -> dict:
    import trimesh
    f30.require(not output.exists(), 'Refuse to overwrite an external check receipt')
    src=path_f29.read_bytes()
    dst=path_f30.read_bytes()
    f30.require(len(src)==f30.F29_QUAD_BYTES and
                hashlib.sha256(src).hexdigest()==f30.F29_QUAD_SHA256,
                'F29 source identity mismatch')
    f30.require(len(dst)==EXPECTED_F30_OBJ_BYTES and
                hashlib.sha256(dst).hexdigest()==EXPECTED_F30_QUAD_SHA256,
                'F30 optimized geometry identity mismatch')
    text_a=src.decode('utf-8').splitlines()
    text_b=dst.decode('utf-8').splitlines()
    faces_a=[x for x in text_a if x.startswith('f ')]
    faces_b=[x for x in text_b if x.startswith('f ')]
    vertices_a=[x for x in text_a if x.startswith('v ')]
    vertices_b=[x for x in text_b if x.startswith('v ')]
    f30.require(faces_a==faces_b and len(faces_a)==876 and
                all(len(row.split())==5 for row in faces_a),
                'F30 topology/face order changed')
    f30.require(len(vertices_a)==len(vertices_b)==878,
                'F30 changed mesh vertex count')
    changed=sum(a!=b for a,b in zip(vertices_a,vertices_b))
    f30.require(changed==189,'Wrong number of modified facet-centroid vertices')
    before=trimesh.load(path_f29,force='mesh',process=False)
    after=trimesh.load(path_f30,force='mesh',process=False)
    for mesh in (before,after):
        f30.require(len(mesh.vertices)==878 and len(mesh.faces)==1752 and
                    mesh.is_watertight and mesh.is_winding_consistent and
                    mesh.is_volume and mesh.body_count==1 and mesh.euler_number==2 and
                    math.isfinite(mesh.area) and math.isfinite(mesh.volume) and mesh.volume>0,
                    'Trimesh independently rejects derived QUAD representation')
    # Rounded OBJ coordinates can be slightly nonplanar; this is diagnostic only.
    report={'schema':'apmesh-s40-f30-independent-trimesh-v1',
            'status':'EXTERNAL_F30_DERIVED_QUAD_TOPOLOGY_CROSSCHECK_PASS',
            'trimesh_version':trimesh.__version__,
            'f29_quad_sha256':f30.F29_QUAD_SHA256,
            'f30_derived_quad_sha256':EXPECTED_F30_QUAD_SHA256,
            'per_face_original_four_vertex_obj':True,
            'exact_face_connectivity_and_order_retained':True,
            'changed_exported_vertex_rows':changed,
            'before':{'vertices':len(before.vertices),'triangulated_faces':len(before.faces),
                      'body_count':before.body_count,'euler':before.euler_number,
                      'watertight':bool(before.is_watertight),
                      'winding_consistent':bool(before.is_winding_consistent),
                      'area_export_precision':float(before.area),
                      'volume_export_precision':float(before.volume)},
            'after':{'vertices':len(after.vertices),'triangulated_faces':len(after.faces),
                      'body_count':after.body_count,'euler':after.euler_number,
                      'watertight':bool(after.is_watertight),
                      'winding_consistent':bool(after.is_winding_consistent),
                      'area_export_precision':float(after.area),
                      'volume_export_precision':float(after.volume)},
            'export_rounding_relative_area_difference':float(abs(before.area-after.area)/before.area),
            'export_rounding_relative_volume_difference':float(abs(before.volume-after.volume)/before.volume),
            'original_geometry_or_derived_OBJ_published':False,
            'independent_matched_literature_benchmark_admitted':False,
            'native_apmesh_quad_generator_executed':False,
            'global_self_intersections_certified_absent':False}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2,sort_keys=True,allow_nan=False)
        stream.write('\n')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--f29-private-quad',type=Path,required=True)
    p.add_argument('--f30-private-quad',type=Path,required=True)
    p.add_argument('--public-receipt',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(verify(args.f29_private_quad,args.f30_private_quad,args.public_receipt),
                     sort_keys=True,allow_nan=False))
