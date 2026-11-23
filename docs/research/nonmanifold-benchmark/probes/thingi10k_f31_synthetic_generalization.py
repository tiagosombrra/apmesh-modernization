#!/usr/bin/env python3
"""Probe F30 quad-center quality on GENERATED topology-diverse synthetic surfaces.

This is NOT a native APMesh QUAD generator, real-model cohort, independent
reference comparison, or generic curved-patch validation. No original mesh bytes.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

import thingi10k_f30_feature_locked_quad_center_optimizer as f30

SCHEMA = 'apmesh-s40-f31-generated-surface-generalization-v1'
F30_GIT_BLOB = '69e184d62032fa47ab03e5f71ba9979c3e4eea31'
SOURCE_LICENSE = 'generated-in-this-research-no-third-party-geometry'
SOURCE_FAMILIES = ('regular_tetra', 'distorted_tetra', 'regular_octa',
                   'stretched_octa', 'triangulated_cube', 'icosahedron',
                   'capped_prism', 'torus', 'corrugated_torus')
RIGID_TEST_SCALE = 2.0
NUMERIC_GUARD = 1e-9
RELATIVE_AREA_GUARD = 1e-10


def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(f'blob {len(raw)}\0'.encode('ascii') + raw).hexdigest()


def source_dep_is_pinned(root: Path) -> bool:
    path = root / 'docs/research/nonmanifold-benchmark/probes/thingi10k_f30_feature_locked_quad_center_optimizer.py'
    return path.is_file() and blob_sha1(path.read_bytes()) == F30_GIT_BLOB


def coords(vertices: Iterable[tuple[float, float, float]], faces: list[tuple[int, int, int]]):
    return [tuple(tuple(vertices[index]) for index in face) for face in faces]


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def subtract(a,b):
    return tuple(a[i]-b[i] for i in range(3))


def dot(a,b):
    return sum(a[i]*b[i] for i in range(3))


def face_outward(vertices, face, origin=(0.,0.,0.)):
    a,b,c=(vertices[i] for i in face)
    normal=cross(subtract(b,a),subtract(c,a))
    centroid=tuple(math.fsum(p[i] for p in (a,b,c))/3 for i in range(3))
    return face if dot(normal,subtract(centroid,origin))>0 else (face[0],face[2],face[1])


def closed_convex(vertices,faces):
    return tuple(vertices), tuple(face_outward(vertices,face) for face in faces)


def tetra(distorted=False):
    verts=[(1.,1.,1.),(-1.,-1.,1.),(-1.,1.,-1.),(1.,-1.,-1.)]
    if distorted:
        verts[3]=(0.985,-0.99,-0.965)
    faces=[(0,1,2),(0,3,1),(0,2,3),(1,3,2)]
    return closed_convex(verts,faces)


def octa(stretched=False):
    verts=[(1.,0.,0.),(-1.,0.,0.),(0.,1.,0.),(0.,-1.,0.),(0.,0.,1.),(0.,0.,-1.)]
    if stretched:
        verts=[(x*2.,y*0.17,z*1.3) for x,y,z in verts]
    faces=[(i,j,k) for i,j in ((0,2),(2,1),(1,3),(3,0)) for k in (4,5)]
    return closed_convex(verts,faces)


def cube():
    frames=[((1,0,0),(0,1,0),(0,0,1)),((-1,0,0),(0,0,1),(0,1,0)),
            ((0,1,0),(0,0,1),(1,0,0)),((0,-1,0),(1,0,0),(0,0,1)),
            ((0,0,1),(1,0,0),(0,1,0)),((0,0,-1),(0,1,0),(1,0,0))]
    verts=[];index={};faces=[]
    for normal,u,v in frames:
        cycle=[]
        for s,t in ((-1,-1),(1,-1),(1,1),(-1,1)):
            xyz=tuple(float(normal[i]+s*u[i]+t*v[i]) for i in range(3))
            if xyz not in index:
                index[xyz]=len(verts);verts.append(xyz)
            cycle.append(index[xyz])
        faces.extend([(cycle[0],cycle[1],cycle[2]),(cycle[0],cycle[2],cycle[3])])
    return tuple(verts),tuple(faces)


def icosahedron():
    t=(1.+math.sqrt(5.))/2.
    verts=[(-1,t,0),(1,t,0),(-1,-t,0),(1,-t,0),(0,-1,t),(0,1,t),
           (0,-1,-t),(0,1,-t),(t,0,-1),(t,0,1),(-t,0,-1),(-t,0,1)]
    faces=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),
           (5,11,4),(11,10,2),(10,7,6),(7,1,8),(3,9,4),(3,4,2),
           (3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),
           (8,6,7),(9,8,1)]
    return closed_convex(verts,faces)


def capped_prism(n=8):
    require(n>=3,'Prism requires at least three side edges')
    verts=[]
    for z,r in ((-1.,1.2),(1.,0.65)):
        for j in range(n):
            u=2*math.pi*j/n
            verts.append((r*math.cos(u),r*math.sin(u),z))
    verts.extend([(0.,0.,-1.),(0.,0.,1.)]);low=2*n;high=low+1
    faces=[]
    for j in range(n):
        k=(j+1)%n
        faces.extend([(j,k,n+k),(j,n+k,n+j),(low,k,j),(high,n+j,n+k)])
    return tuple(verts),tuple(faces)


def torus(corrugated=False, nu=12, nv=8):
    require(nu>=4 and nv>=4,'Minimum periodic torus subdivision')
    verts=[]
    for i in range(nu):
        u=2*math.pi*i/nu
        for j in range(nv):
            v=2*math.pi*j/nv
            radial=0.65*(1+0.19*math.cos(3*u)*math.sin(2*v)) if corrugated else 0.65
            R=2.0+radial*math.cos(v)
            verts.append((R*math.cos(u),R*math.sin(u),radial*math.sin(v)))
    faces=[]
    idx=lambda i,j:(i%nu)*nv+j%nv
    for i in range(nu):
        for j in range(nv):
            a,b,c,d=idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1)
            faces.extend([(a,b,c),(a,c,d)])
    return tuple(verts),tuple(faces)


def build_sources():
    cases={'regular_tetra':tetra(), 'distorted_tetra':tetra(True),
           'regular_octa':octa(), 'stretched_octa':octa(True),
           'triangulated_cube':cube(), 'icosahedron':icosahedron(),
           'capped_prism':capped_prism(), 'torus':torus(),
           'corrugated_torus':torus(True)}
    require(set(cases)==set(SOURCE_FAMILIES),'Generated corpus changed')
    return {k:cases[k] for k in SOURCE_FAMILIES}


def edge_key(a,b):
    require(a!=b,'Self-edge is invalid')
    return (a,b) if a<b else (b,a)


def topology(vertices,faces,*,expected_genus:int, require_connected=True):
    require(isinstance(expected_genus,int) and expected_genus>=0,'Invalid genus')
    require(len(vertices)>0 and len(faces)>0,'Empty closed source')
    require(all(len(p)==3 and all(math.isfinite(v) for v in p) for p in vertices),
            'Malformed source XYZ')
    counts=defaultdict(list);vertex_links=defaultdict(list)
    for i,face in enumerate(faces):
        require(len(face) in (3,4) and len(set(face))==len(face),
                'Faces must contain three or four unique vertices')
        require(all(isinstance(v,int) and 0<=v<len(vertices) for v in face),
                'Invalid face index')
        for j,u in enumerate(face):
            v=face[(j+1)%len(face)]
            counts[edge_key(u,v)].append((i,1 if u<v else -1))
            vertex_links[u].append((face[(j-1)%len(face)],v))
    require(len(vertex_links)==len(vertices),'Unreferenced source vertices')
    require(all(len(inc)==2 for inc in counts.values()),'Boundary/nonmanifold edge')
    require(all(a[0][1]!=a[1][1] for a in counts.values()),
            'Opposed edge orientation mismatch')
    # The vertex-link graph must form exactly one connected cycle at each vertex.
    for incident in vertex_links.values():
        link=defaultdict(set)
        for a,b in incident:
            require(a!=b,'Pinched vertex link')
            link[a].add(b);link[b].add(a)
        require(all(len(neighbors)==2 for neighbors in link.values()),
                'Nonmanifold or singular vertex link')
        start=next(iter(link));seen={start};queue=[start]
        while queue:
            current=queue.pop()
            for other in link[current]:
                if other not in seen:
                    seen.add(other);queue.append(other)
        require(len(seen)==len(link),'Disconnected vertex link / pinch')
    face_neighbors=defaultdict(set)
    for incidence in counts.values():
        a,b=incidence
        face_neighbors[a[0]].add(b[0]);face_neighbors[b[0]].add(a[0])
    reached={0};queue=[0]
    while queue:
        for other in face_neighbors[queue.pop()]:
            if other not in reached:
                reached.add(other);queue.append(other)
    require(not require_connected or len(reached)==len(faces),
            'Disconnected closed surface does not meet corpus gate')
    chi=len(vertices)-len(counts)+len(faces)
    require(chi==2-2*expected_genus and len(reached)==len(faces),
            'Source genus or connectivity mismatch')
    return {'vertices':len(vertices),'edges':len(counts),'faces':len(faces),
            'euler':chi,'genus':expected_genus,'components':1,'border_edges':0,
            'nonmanifold_edges':0,'orientation_conflicts':0}


def derive_sector_quad_complex(vertices,faces):
    # Identity tags are topological. Do not weld unrelated source vertices by XYZ.
    tags=set(('v',i) for i in range(len(vertices)))
    surface=[]
    for facet, (a,b,c) in enumerate(faces):
        center=('c',facet)
        tags.add(center)
        for u,v in ((a,b),(b,c),(c,a)):
            tags.add(('e',edge_key(u,v)))
        for before,here,after in ((c,a,b),(a,b,c),(b,c,a)):
            surface.append((('v',here),('e',edge_key(here,after)),center,
                            ('e',edge_key(before,here))))
    ordered=sorted(tags)
    index={tag:j for j,tag in enumerate(ordered)}
    points=[]
    for tag in ordered:
        if tag[0]=='v':
            points.append(vertices[tag[1]])
        elif tag[0]=='e':
            u,v=tag[1]
            points.append(f30.midpoint(vertices[u],vertices[v]))
        else:
            a,b,c=faces[tag[1]]
            points.append(f30.barycentric((vertices[a],vertices[b],vertices[c]),
                                          (1/3,1/3,1/3)))
    return tuple(points),tuple(tuple(index[tag] for tag in face) for face in surface)


def _models_result(name,source):
    vertices,faces=source
    genus=int(name in ('torus','corrugated_torus'))
    before=topology(vertices,faces,expected_genus=genus)
    quadv,quadf=derive_sector_quad_complex(vertices,faces)
    after=topology(quadv,quadf,expected_genus=genus)
    require(after['faces']==3*before['faces'] and
            after['vertices']==before['vertices']+before['edges']+before['faces'] and
            after['edges']==2*before['edges']+3*before['faces'],
            'Three-quad sector topology fails Euler-preserving subdivision')
    solution=f30.optimize_source(coords(vertices,faces))
    initial=solution['baseline_quality']
    final=solution['optimized_quality']
    require(initial['quads']==after['faces']==final['quads'],
            'Source facets and metrics disagree')
    require(final['count_min_angle_below_30_deg']<=initial['count_min_angle_below_30_deg']
            and final['count_max_angle_above_150_deg']<=initial['count_max_angle_above_150_deg']
            and final['mean_min_scaled_jacobian']+NUMERIC_GUARD>=
                initial['mean_min_scaled_jacobian'],
            'Generated surface has a Pareto regression')
    # Per-facet source topology and edges stay unchanged by center-only optimization.
    for facet,record in enumerate(solution['facets']):
        require(f30.dominates_or_equals(record['optimized'],record['baseline']),
                f'Facet {facet} has a per-quad regression')
    return {'model':name,'source_provenance':SOURCE_LICENSE,
            'source_tri_topology':before,'derived_quad_topology':after,
            'changed_facet_centers':solution['changed_source_facet_centers'],
            'total_facet_centers':len(faces),
            'baseline_quality':initial, 'optimized_quality':final,
            'max_normalized_center_displacement':
                solution['max_center_displacement_over_source_edge'],
            'candidate_count_per_facet':solution['rational_candidate_count_per_facet'],
            'scientific_model_admitted':False,'native_apmesh_quad_executed':False}


def produce_receipt(root: Path) -> dict:
    require(source_dep_is_pinned(root),'Original F30 implementation Git blob differs')
    records=[_models_result(name,source) for name,source in build_sources().items()]
    before=[r['baseline_quality'] for r in records]
    after=[r['optimized_quality'] for r in records]
    total_source=sum(r['source_tri_topology']['faces'] for r in records)
    total_quads=sum(r['derived_quad_topology']['faces'] for r in records)
    macro_before=math.fsum(x['mean_min_scaled_jacobian'] for x in before)/len(before)
    macro_after=math.fsum(x['mean_min_scaled_jacobian'] for x in after)/len(after)
    micro_before=math.fsum(x['mean_min_scaled_jacobian']*x['quads'] for x in before)/total_quads
    micro_after=math.fsum(x['mean_min_scaled_jacobian']*x['quads'] for x in after)/total_quads
    require(total_quads==3*total_source and macro_after+NUMERIC_GUARD>=macro_before,
            'Independent corpus-level invariant violated')
    return {'schema':SCHEMA,'synthetic_only':True,
            'third_party_geometries_loaded':False,
            'reference_quad_meshes_loaded':False,'native_apmesh_quad_executed':False,
            'not_scientific_benchmark_admitted':True,
            'f30_git_blob':F30_GIT_BLOB,
            'model_count':len(records),'synthetic_source_triangles':total_source,
            'synthetic_derived_quads':total_quads,
            'changed_source_centers':sum(r['changed_facet_centers'] for r in records),
            'models_improving_mean_sj':sum(r['optimized_quality']['mean_min_scaled_jacobian']>
                                            r['baseline_quality']['mean_min_scaled_jacobian']+1e-9
                                            for r in records),
            'macro_mean_min_sj_before':macro_before,
            'macro_mean_min_sj_after':macro_after,
            'micro_mean_min_sj_before':micro_before,
            'micro_mean_min_sj_after':micro_after,
            'models':records}


def safe_output(path:Path,receipt:dict):
    require(not path.exists(), 'Existing output must not be overwritten')
    path.parent.mkdir(parents=True,exist_ok=True)
    encoded=(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True,
                        allow_nan=False)+'\n').encode('utf-8')
    # Exclusive creation prevents replacing a previous, possibly reviewed, receipt.
    with path.open('xb') as out:
        out.write(encoded)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    safe_output(args.output,produce_receipt(args.root))
    print('F31 synthetic generalization and topology gate PASS')


if __name__=='__main__':
    main()
