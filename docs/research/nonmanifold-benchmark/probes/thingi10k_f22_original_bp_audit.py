#!/usr/bin/env python3
"""Independently inspect a private, pinned F21 BP candidate against original STL.

This script never publishes third-party source geometry or certifies APMesh meshing.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import struct
import zipfile

MODEL = 293137
ZIP_BLOB = '359c26b16664e9ba8d2415ca065a85bd27504d5f'
STL_SHA = '4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a'
BP_SHA = '6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0'
SIDE_INDEX = ((0, 1, 2, 3), (3, 7, 11, 15), (15, 14, 13, 12), (12, 8, 4, 0))


def require(test, reason):
    if not test:
        raise ValueError(reason)


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def norm(a):
    return math.sqrt(sum(x * x for x in a))


def area3(a, b, c):
    return norm(cross(sub(b, a), sub(c, a))) / 2


def midpoint(a, b):
    return tuple((x + y) / 2 for x, y in zip(a, b))


def centroid(a, b, c):
    return tuple((x + y + z) / 3 for x, y, z in zip(a, b, c))


def distance(a, b):
    return norm(sub(a, b))


def git_blob(raw):
    return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()


def original_triangles(source_zip: Path):
    require(source_zip.is_file() and source_zip.stat().st_size == 7073, 'Missing original archive')
    raw = source_zip.read_bytes()
    require(git_blob(raw) == ZIP_BLOB, 'Incorrect pinned Git ZIP blob')
    with zipfile.ZipFile(source_zip) as z:
        names = z.namelist()
        require(names == ['293137.stl'], 'Unexpected original ZIP members')
        stl = z.read(names[0])
    require(hashlib.sha256(stl).hexdigest() == STL_SHA and len(stl) == 14684,
            'Original STL does not match original SHA-256')
    require(struct.unpack_from('<I', stl, 80)[0] == 292, 'Unexpected source triangle count')
    faces = []
    for i in range(292):
        values = struct.unpack_from('<9f', stl, 84 + i * 50 + 12)
        tri = tuple(tuple(map(float, values[j*3:j*3+3])) for j in range(3))
        require(all(math.isfinite(v) for p in tri for v in p), 'Nonfinite original triangle')
        require(area3(*tri) > 0, 'Degenerate original triangle')
        faces.append(tri)
    return faces


def read_bp(path: Path, expected_sha: str = BP_SHA):
    require(path.is_file() and 0 < path.stat().st_size <= 1_000_000, 'Missing/oversized BP')
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == expected_sha, 'Candidate BP SHA-256 mismatch')
    coords, patches = [], []
    for line in raw.decode('utf-8').splitlines():
        tokens = line.split()
        require(tokens and tokens[0] in {'v', 'p'}, 'Unsupported BP record')
        if tokens[0] == 'v':
            require(len(tokens) == 4, 'Wrong number of BP coordinates')
            p = tuple(float(x) for x in tokens[1:])
            require(all(map(math.isfinite, p)), 'Nonfinite BP point')
            coords.append(p)
        else:
            require(len(tokens) == 17, 'Wrong number of BP indices')
            vals = tuple(int(s) for s in tokens[1:])
            require(all(0 <= x < len(coords) for x in vals), 'Invalid indexed BP reference')
            patches.append(vals)
    return coords, patches


def inspect(source_zip: Path, bp_path: Path, *, bp_sha: str = BP_SHA, pinned=True):
    tris = original_triangles(source_zip)
    coordinates, indices = read_bp(bp_path, bp_sha)
    require(len(indices) == len(tris) * 3, 'Not exactly three patches per original facet')
    require(len(coordinates) == 7886, 'Unexpected number of BP control points')
    sides = defaultdict(list)
    corner_nodes = set()
    total_area = 0.0
    original_area = 0.0
    max_vertex_error = 0.0
    max_face_area_error = 0.0
    max_control_planarity_error = 0.0
    max_normalized_corner_jacobian = 0.0
    min_normalized_corner_jacobian = math.inf
    diagonal = max(distance(p, q) for tri in tris for p in tri for q in tri)
    geometric_tolerance = 1e-11 * max(1, diagonal)
    for fi, tri in enumerate(tris):
        a,b,c = tri
        mn = [midpoint(a,b),midpoint(b,c),midpoint(c,a)]
        center = centroid(a,b,c)
        expected = ((a,mn[0],center,mn[2]),
                    (b,mn[1],center,mn[0]),
                    (c,mn[2],center,mn[1]))
        tri_area=area3(a,b,c)
        original_area += tri_area
        patch_area = 0.0
        N = cross(sub(b,a),sub(c,a))
        n2 = sum(x*x for x in N)
        for j in range(3):
            ids = indices[3*fi+j]
            ps = tuple(coordinates[k] for k in ids)
            corners = (ps[0],ps[3],ps[15],ps[12])
            for u,w in zip(corners,expected[j]):
                max_vertex_error = max(max_vertex_error, distance(u,w))
                require(distance(u,w) <= geometric_tolerance, 'Patch corner disagrees with original STL')
            for ip,p in enumerate(ps):
                u,v = (ip%4)/3,(ip//4)/3
                target = tuple((1-u)*(1-v)*corners[0][k] + u*(1-v)*corners[1][k]
                    + u*v*corners[2][k] + (1-u)*v*corners[3][k] for k in range(3))
                max_control_planarity_error = max(max_control_planarity_error,distance(p,target))
                require(distance(p,target)<=geometric_tolerance, 'Bicubic controls not bilinear degree-elevation')
            for order in SIDE_INDEX:
                s = tuple(ps[k] for k in order)
                key = tuple(sorted((s[0],s[3])))
                sides[key].append(s)
            corner_nodes.update(corners)
            patch_area += area3(corners[0],corners[1],corners[2])+area3(corners[0],corners[2],corners[3])
            pairs = ((sub(corners[1],corners[0]),sub(corners[3],corners[0])),
                     (sub(corners[1],corners[0]),sub(corners[2],corners[1])),
                     (sub(corners[2],corners[3]),sub(corners[2],corners[1])),
                     (sub(corners[2],corners[3]),sub(corners[3],corners[0])))
            for udir, vdir in pairs:
                r=sum(x*y for x,y in zip(cross(udir,vdir),N))/n2
                require(r>0, 'Nonpositive local corner Jacobian')
                max_normalized_corner_jacobian=max(max_normalized_corner_jacobian,r)
                min_normalized_corner_jacobian=min(min_normalized_corner_jacobian,r)
        total_area += patch_area
        max_face_area_error = max(max_face_area_error,abs(tri_area-patch_area))
        require(abs(patch_area-tri_area) < 1e-11*max(1,tri_area),'Triangle area not preserved')
    require(len(corner_nodes)==878 and len(sides)==1752, 'Unexpected quad graph topology')
    require(all(len(uses)==2 and uses[0]==uses[1][::-1] for uses in sides.values()),
            'Unpaired/inconsistent C0 patch seam')
    require(len(corner_nodes)-len(sides)+len(indices)==2, 'Quad Euler disagrees with genus-0 source')
    require(abs(total_area-original_area)<1e-10*max(1,original_area),'Total source area drift')
    return {
        'schema':'apmesh-thingi10k-f22-original-input-real-bp-independent-audit-v1',
        'case_id':MODEL,'original_stl_sha256':STL_SHA,'original_zip_git_blob_sha1':ZIP_BLOB,
        'actual_local_candidate_bp_sha256':hashlib.sha256(bp_path.read_bytes()).hexdigest(),
        'candidate_bp_bytes':bp_path.stat().st_size,'original_triangles':len(tris),
        'candidate_patches':len(indices),'candidate_control_coordinates':len(coordinates),
        'candidate_corner_vertices':len(corner_nodes),'candidate_patch_edges':len(sides),
        'quad_euler':2,'seams_with_exact_reversed_four_controls':len(sides),
        'source_total_piecewise_triangle_area':original_area,
        'candidate_total_piecewise_quad_area':total_area,
        'max_original_triangle_vs_three_quads_area_error':max_face_area_error,
        'max_expected_source_corner_deviation':max_vertex_error,
        'max_degree_elevation_control_deviation':max_control_planarity_error,
        'min_normalized_corner_jacobian':min_normalized_corner_jacobian,
        'max_normalized_corner_jacobian':max_normalized_corner_jacobian,
        'original_apmesh_cpp_reader_executed':False,
        'original_apmesh_cpp_generator_executed':False,
        'scientific_reference_mesh_admitted':False,
        'redistribution_license_cleared':False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-zip',type=Path,required=True)
    p.add_argument('--candidate-bp',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True)
    a=p.parse_args()
    require(not a.receipt.exists(),'Refusing to overwrite an existing receipt')
    r=inspect(a.source_zip,a.candidate_bp)
    with a.receipt.open('x',encoding='utf-8') as f:json.dump(r,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(r,sort_keys=True,indent=2))

if __name__=='__main__':
    main()
