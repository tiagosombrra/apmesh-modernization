#!/usr/bin/env python3
"""Independently inspect private native/derived TRI topology with optional Trimesh.

This auxiliary check is not a self-intersection certificate and never exports
any original or derived third-party geometry. Trimesh is an OPTIONAL dependency;
the primary seam guard and its hermetic tests use the standard library only.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import trimesh

import thingi10k_f27_native_tri_evidence as f27

NATIVE_OBJ_SHA = '145b40c2f542a9d1d18bcda6eccc01c8861be83d247418af96fa18b4c860c325'
DERIVED_OBJ_SHA = 'b93995d1319e702649574044b2167fa01fe90644b1e5e02a295f3b47cdfdc46b'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def record(mesh):
    return {'vertices': int(len(mesh.vertices)), 'faces': int(len(mesh.faces)),
            'is_watertight': bool(mesh.is_watertight),
            'is_winding_consistent': bool(mesh.is_winding_consistent),
            'is_volume': bool(mesh.is_volume),
            'connected_component_count': int(mesh.body_count),
            'euler_number': int(mesh.euler_number),
            'triangle_surface_area_export_precision': float(mesh.area),
            'signed_volume_export_precision': float(mesh.volume)}


def verify(source_zip: Path, native_obj: Path, derived_obj: Path):
    require(f27.sha256(native_obj) == NATIVE_OBJ_SHA, 'Native original OBJ SHA mismatch')
    require(f27.sha256(derived_obj) == DERIVED_OBJ_SHA, 'F28 derived OBJ SHA mismatch')
    triangles = f27.parse_source(source_zip)
    coords = list(dict.fromkeys(p for tri in triangles for p in tri))
    index = {p:i for i,p in enumerate(coords)}
    source_mesh = trimesh.Trimesh(vertices=np.asarray(coords),
        faces=np.asarray([[index[p] for p in tri] for tri in triangles]), process=False)
    native = trimesh.load_mesh(native_obj, process=False)
    stitched = trimesh.load_mesh(derived_obj, process=False)
    src = record(source_mesh)
    raw = record(native)
    final = record(stitched)
    require((src['vertices'],src['faces'],src['connected_component_count'],src['euler_number'])
            == (148,292,1,2) and src['is_volume'], 'Original source STL topology mismatch')
    require((raw['vertices'],raw['faces'],raw['connected_component_count'],raw['euler_number'])
            == (4380,3504,876,876) and not raw['is_watertight'],
            'Raw native OBJ topology differs from independent audit')
    require((final['vertices'],final['faces'],final['connected_component_count'],final['euler_number'])
            == (1754,3504,1,2) and final['is_volume'] and final['is_winding_consistent'],
            'Derived private OBJ is not a consistently oriented closed volume')
    require(raw['triangle_surface_area_export_precision'] ==
            final['triangle_surface_area_export_precision'] and
            raw['signed_volume_export_precision'] == final['signed_volume_export_precision'],
            'Seam-only operation changed native OBJ geometry/volume')
    area_rel = abs(final['triangle_surface_area_export_precision'] -
                   src['triangle_surface_area_export_precision']) / src['triangle_surface_area_export_precision']
    vol_rel = abs(final['signed_volume_export_precision'] -
                  src['signed_volume_export_precision']) / abs(src['signed_volume_export_precision'])
    require(math.isfinite(area_rel) and math.isfinite(vol_rel) and
            area_rel < 5e-6 and vol_rel < 5e-6,
            'Six-digit OBJ export quantization exceeds declared geometric comparison budget')
    return {'schema': 'apmesh-s40-f28-optional-trimesh-crosscheck-v1',
            'external_library': 'trimesh', 'external_library_version': trimesh.__version__,
            'source_binary_stl_sha256': f27.STL_SHA256,
            'native_original_obj_sha256': NATIVE_OBJ_SHA,
            'private_derived_obj_sha256': DERIVED_OBJ_SHA,
            'source_original_stl': src,
            'original_native_obj': raw,
            'private_derived_obj': final,
            'relative_obj_area_error_vs_original_stl': area_rel,
            'relative_obj_volume_error_vs_original_stl': vol_rel,
            'six_significant_digit_export_rounding_is_nonnegligible': True,
            'self_intersections_certified_absent': False,
            'published_geometry': False,
            'scientific_benchmark_admitted': False,
            'status': 'INDEPENDENT_EXTERNAL_TOPOLOGY_AND_QUANTIZATION_CHECK_PASS'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-zip',type=Path,required=True)
    p.add_argument('--native-obj',type=Path,required=True)
    p.add_argument('--derived-obj',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True)
    args=p.parse_args()
    require(not args.receipt.exists(),'Refuse to overwrite external evidence')
    result=verify(args.source_zip,args.native_obj,args.derived_obj)
    with args.receipt.open('x',encoding='utf-8') as out:
        json.dump(result,out,indent=2,sort_keys=True,allow_nan=False)
        out.write('\n')
    print(json.dumps({'status':result['status'],
                      'source_watertight':result['source_original_stl']['is_watertight'],
                      'native_watertight':result['original_native_obj']['is_watertight'],
                      'derived_watertight':result['private_derived_obj']['is_watertight']}))


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,TypeError,KeyError) as e:
        raise SystemExit(f'F28 external cross-check failed: {e}') from e
