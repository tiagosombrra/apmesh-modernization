#!/usr/bin/env python3
"""Independently inspect a PRIVATE derived QUAD OBJ with Trimesh.

Trimesh triangulates OBJ quadrilaterals internally. This is an independent
watertightness/volume diagnostic, not a native QUAD generation or CAD claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import math


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(quad: Path, stitched_tri: Path, quad_sha: str, tri_sha: str):
    import trimesh
    if digest(quad) != quad_sha or digest(stitched_tri) != tri_sha:
        raise ValueError('Original private result hash changed')
    def lines(path):
        contents=path.read_text(encoding='utf-8').splitlines()
        return [c for c in contents if c.startswith('v ')], [c for c in contents if c.startswith('f ')]
    quad_v,quad_f=lines(quad)
    tri_v,tri_f=lines(stitched_tri)
    if len(quad_v)!=878 or len(quad_f)!=876 or any(len(f.split())!=5 for f in quad_f):
        raise ValueError('Derived OBJ is not a 4-node 876-QUAD surface')
    if len(tri_v)!=1754 or len(tri_f)!=3504 or any(len(f.split())!=4 for f in tri_f):
        raise ValueError('Source stitched OBJ is not the original 3504-TRI surface')
    def inspect(path):
        mesh=trimesh.load(str(path),force='mesh',process=False)
        return {'triangulated_faces_by_trimesh':len(mesh.faces),
                'vertices':len(mesh.vertices),
                'watertight':bool(mesh.is_watertight),
                'winding_consistent':bool(mesh.is_winding_consistent),
                'is_volume':bool(mesh.is_volume),
                'euler_number':int(mesh.euler_number),
                'components':len(mesh.split(only_watertight=False)),
                'area_export_precision':float(mesh.area),
                'signed_volume_export_precision':float(mesh.volume)}
    q=inspect(quad);t=inspect(stitched_tri)
    if not (q['watertight'] and q['winding_consistent'] and q['is_volume'] and
            q['euler_number']==2 and q['components']==1 and
            t['watertight'] and t['winding_consistent'] and t['euler_number']==2):
        raise ValueError('Independent surface topology disagrees')
    area_diff=abs(q['area_export_precision']-t['area_export_precision'])
    volume_diff=abs(q['signed_volume_export_precision']-t['signed_volume_export_precision'])
    if area_diff/max(1.0,t['area_export_precision'])>=1e-6 or volume_diff/max(1.0,abs(t['signed_volume_export_precision']))>=1e-6:
        raise ValueError('Quantized OBJ quad triangulation differs substantially from TRI geometry')
    return {'schema':'apmesh-s40-f29-optional-external-quad-topology-v1',
            'status':'EXTERNAL_QUAD_TOPOLOGY_CROSSCHECK_PASS',
            'trimesh_version':trimesh.__version__,
            'tri_obj_sha256':tri_sha,
            'quad_obj_sha256':quad_sha,
            'private_stitched_tri':t,
            'private_derived_quad_triangulated_for_crosscheck':q,
            'absolute_area_difference_due_to_export_rounding_and_diagonal':area_diff,
            'absolute_volume_difference_due_to_export_rounding_and_diagonal':volume_diff,
            'native_quad_generation':False,
            'self_intersection_free_certified':False,
            'no_original_geometry_in_receipt':True,
            'scientific_benchmark_admitted':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quad',required=True,type=Path)
    parser.add_argument('--stitched-tri',required=True,type=Path)
    parser.add_argument('--quad-sha',required=True)
    parser.add_argument('--tri-sha',required=True)
    parser.add_argument('--receipt',required=True,type=Path)
    a=parser.parse_args()
    if a.receipt.exists():
        raise SystemExit('Refuse overwrite')
    r=run(a.quad,a.stitched_tri,a.quad_sha,a.tri_sha)
    with a.receipt.open('x',encoding='utf-8') as f:
        json.dump(r,f,sort_keys=True,indent=2,allow_nan=False)
        f.write('\n')
    print(json.dumps({'status':r['status'],'quad_as_tri_faces':r['private_derived_quad_triangulated_for_crosscheck']['triangulated_faces_by_trimesh']},sort_keys=True))


if __name__=='__main__':
    main()
