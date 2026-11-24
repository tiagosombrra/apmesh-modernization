#!/usr/bin/env python3
"""S3.R: source-identified conforming patch retopology for original S40.

Only de Casteljau subdivision is permitted on preexisting BP patches. Source
EDGE_CURVE identity, not geometric proximity, authorizes the four face joins.
All emitted CAD-derived BP coordinates remain private research artifacts.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepClass import BRepClass_FaceClassifier
from OCP.TopAbs import TopAbs_OUT
from OCP.gp import gp_Pnt2d

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import SOURCES
from s3i_joint_source_atlas import _serialize
from s3j_radial_support_enclosure import certify_patch
from s3k_native_uv_trim_gate import classify_patch
from s3q_s40_hole_preserving_island import (
    BUDGET_MM, FACE_ID, PREEXISTING_GENERATORS,
    _boundary_distance, _boundary_sides, _native_edges,
    audit_nonconforming_join, audit_original as audit_island,
    build_island, source_partition,
)

TARGET_SPLIT_PATCHES = 19
ORIGINAL_PATCHES = 77
ORIGINAL_CONTROLS = 864
ISLAND_PATCHES = 30
CONTROL_TOL = 1e-8
PINNED_S3P_BP_SHA256 = "c7aa9f71e05d340ad99af6d087011e7f722e5fd2f19bbc87ab39f716845d1ce9"
PINNED_S3P_MANIFEST_SHA256 = "3c86bbadabd0689a93527a397560b36033e18f60db661b442eaa698f8b5c5bbe"


def _side(patch, label):
    return tuple({
        'bottom':patch[:4], 'top':patch[-4:],
        'left':patch[::4], 'right':patch[3::4],
    }[label])


def _edge_adjacency(patches):
    adjacency=defaultdict(list)
    for i,patch in enumerate(patches):
        for name in ('bottom','top','left','right'):
            ids=_side(patch,name)
            adjacency[tuple(sorted(ids))].append((i,name,ids))
    if any(len(rows)>2 for rows in adjacency.values()):
        raise ValueError('Source-indexed BP has non-manifold control-side incidence')
    return adjacency


def _point_split(points, t):
    if not 0<t<1:
        raise ValueError('de Casteljau split must be strictly interior')
    p0,p1,p2,p3=points
    def mid(a,b):return tuple((1-t)*x+t*y for x,y in zip(a,b))
    a=mid(p0,p1);b=mid(p1,p2);c=mid(p2,p3)
    d=mid(a,b);e=mid(b,c);f=mid(d,e)
    return (p0,a,d,f),(f,e,c,p3)


def _nets_split(net,axis,t):
    if axis=='u':
        L=[];R=[]
        for row in range(4):
            l,r=_point_split(net[row*4:row*4+4],t)
            L.extend(l);R.extend(r)
        return (tuple(L),tuple(R))
    if axis=='v':
        cols=[_point_split(net[c::4],t) for c in range(4)]
        return tuple(tuple(cols[c][half][row] for row in range(4) for c in range(4)) for half in (0,1))
    raise ValueError('Unknown split axis')


def _source_split_fraction(patch,side,points,frame,axial_v):
    ids=_side(patch,side)
    a=points[ids[0]];b=points[ids[-1]]
    origin=frame['origin'];axis=frame['axis']
    za=sum((a[i]-origin[i])*axis[i] for i in range(3))
    zb=sum((b[i]-origin[i])*axis[i] for i in range(3))
    if abs(zb-za)<1e-12:
        raise ValueError('Split generator has no axial extent')
    fraction=(axial_v-za)/(zb-za)
    if not 1e-8<fraction<1-1e-8:
        raise ValueError('Source split outside old indexed generator')
    return fraction


def propagation(source,points,patches,baseline_manifest,island_manifest):
    """Propagate each original source-edge split across full indexed patch strips."""
    part=source_partition(source)
    adjacency=_edge_adjacency(patches)
    registry=baseline_manifest['original_global_source_key_to_control_index']
    boundaries,_=_boundary_sides(part,island_manifest['added_patches'])
    queue=deque();seeds=[]
    for eid in PREEXISTING_GENERATORS:
        row=next(r for r in part['source_edges'] if r['edge_id']==eid)
        ids=[registry.get(f'vertex:{row["start_vertex_id"]}'),
             registry.get(f'edge:{eid}:1'),registry.get(f'edge:{eid}:2'),
             registry.get(f'vertex:{row["end_vertex_id"]}')]
        if any(i is None for i in ids):
            raise ValueError(f'Missing preexisting original source controls for #{eid}')
        found=adjacency.get(tuple(sorted(ids)),[])
        if len(found)!=1 or len(boundaries[eid])!=2:
            raise ValueError(f'Original #{eid} is not a unique one-piece-to-two-piece join')
        pid,name,original_side=found[0]
        target=part['breakpoints_v'][1 if eid in (281,303) else 3]
        t=_source_split_fraction(patches[pid],name,points,part['frame'],target)
        axis='u' if name in ('bottom','top') else 'v'
        queue.append((pid,axis,t,eid))
        seeds.append({'edge_curve_id':eid,'original_parent_patch_id':pid,
                      'parent_side':name,'split_parameter':t,
                      'original_control_ids':list(original_side),
                      'source_axial_break_mm':target})
    found={}
    while queue:
        pid,axis,t,source_eid=queue.popleft()
        key=(pid,axis)
        if key in found:
            if abs(found[key][0]-t)>1e-9:
                raise ValueError('Conflicting source-induced split positions')
            continue
        if not 1e-8<t<1-1e-8:
            raise ValueError('Propagated split outside original patch')
        found[key]=(t,source_eid)
        for name in (('bottom','top') if axis=='u' else ('left','right')):
            old=_side(patches[pid],name)
            adjacent=adjacency[tuple(sorted(old))]
            if len(adjacent)!=2:
                continue
            for nid,nname,nside in adjacent:
                if nid==pid:continue
                if nside==old: nt=t
                elif nside==tuple(reversed(old)):nt=1-t
                else:raise ValueError('Incompatible source indexed edge orientation')
                new_axis='u' if nname in ('bottom','top') else 'v'
                queue.append((nid,new_axis,nt,source_eid))
    if any(sum(pid==k for k,axis in found)>1 for pid,axis in found):
        raise ValueError('Multiple-axis propagation is not admitted by S3.R pilot')
    if len(found)!=TARGET_SPLIT_PATCHES:
        raise ValueError(f'Unexpected original source split closure: {len(found)}')
    return found,seeds


def _old_side_label(original,side,half,position):
    """Return a canonical ID key along the original shared control edge."""
    controls=_side(original,side)
    forward=controls<=controls[::-1]
    signature=controls if forward else controls[::-1]
    canonical_half=half if forward else 1-half
    canonical_i=position if forward else 3-position
    if canonical_half==0 and canonical_i==0:return ('old',signature[0])
    if canonical_half==1 and canonical_i==3:return ('old',signature[-1])
    if (canonical_half,canonical_i) in ((0,3),(1,0)):
        return ('derived_original_edge_split_node',signature)
    return ('derived_original_edge',signature,canonical_half,canonical_i)


def _derived_key(original,patch_id,axis,half,row,col):
    """Assign a vertex identity without spatial welding or altering old owners."""
    if axis=='u':
        if row==0 or row==3:
            return _old_side_label(original,'bottom' if row==0 else 'top',half,col)
        if half==0 and col==0:return ('old',original[4*row])
        if half==1 and col==3:return ('old',original[4*row+3])
        if (half==0 and col==3) or (half==1 and col==0):
            return ('new_cut',patch_id,'u',row)
    else:
        if col==0 or col==3:
            return _old_side_label(original,'left' if col==0 else 'right',half,row)
        if half==0 and row==0:return ('old',original[col])
        if half==1 and row==3:return ('old',original[12+col])
        if (half==0 and row==3) or (half==1 and row==0):
            return ('new_cut',patch_id,'v',col)
    return ('new_interior',patch_id,axis,half,row,col)


def build_join(source,prior_bp,prior_manifest,island_bp,island_manifest,*,budget_mm=BUDGET_MM):
    """Retopologize the 77-patch original atlas and join the holed face by ID."""
    if budget_mm!=BUDGET_MM:
        raise ValueError('The original experimental budget is immutable')
    part=source_partition(source)
    if prior_manifest.get('source_sha256')!=part['source_sha256'] or prior_manifest.get('combined_patch_count')!=77:
        raise ValueError('Original 77-patch S40 atlas missing')
    if sha256(prior_bp.encode()).hexdigest()!=PINNED_S3P_BP_SHA256 or (
            prior_manifest.get('combined_bp_sha256')!=PINNED_S3P_BP_SHA256):
        raise ValueError('Original 77-patch BP does not match the pinned original')
    manifest_bytes=(json.dumps(prior_manifest,sort_keys=True,indent=2)+'\n').encode()
    if sha256(manifest_bytes).hexdigest()!=PINNED_S3P_MANIFEST_SHA256:
        raise ValueError('Original 77-patch manifest differs from frozen S3.P')
    if len(prior_manifest.get('original_global_source_key_to_control_index',{}))!=864:
        raise ValueError('Incomplete original source control registry')
    expected_island,expected_manifest=build_island(source)
    if island_bp!=expected_island or island_manifest!=expected_manifest:
        raise ValueError('Original S3.Q island or manifest was modified')
    audit_nonconforming_join(source,island_manifest,prior_bp,prior_manifest)
    initial,original_patches=read_bp(prior_bp)
    island_vertices,island_patches=read_bp(island_bp)
    if len(initial)!=ORIGINAL_CONTROLS or len(original_patches)!=ORIGINAL_PATCHES:
        raise ValueError('Wrong original BP inventory')
    if len(island_patches)!=ISLAND_PATCHES:
        raise ValueError('Wrong isolated holed-face inventory')
    required,seeds=propagation(source,initial,original_patches,prior_manifest,island_manifest)
    points=list(initial)
    new_keys={};new_patches=[];children={}
    def intern(key,xyz):
        if key[0]=='old':
            idx=key[1]
            if math.dist(points[idx],xyz)>CONTROL_TOL:
                raise ValueError('Retopology changed existing source control coordinates')
            return idx
        if key in new_keys:
            idx=new_keys[key]
            if math.dist(points[idx],xyz)>CONTROL_TOL:
                raise ValueError('Inconsistent source-identified split controls')
            return idx
        idx=len(points);new_keys[key]=idx;points.append(tuple(xyz));return idx
    for pid,original in enumerate(original_patches):
        if not any(k==pid for k,axis in required):
            children[pid]=[len(new_patches)]
            new_patches.append(tuple(original))
            continue
        axis=next(axis for k,axis in required if k==pid)
        t=required[(pid,axis)][0]
        parts=_nets_split([initial[idx] for idx in original],axis,t)
        children[pid]=[]
        for half,net in enumerate(parts):
            ids=[]
            for row in range(4):
                for col in range(4):
                    key=_derived_key(original,pid,axis,half,row,col)
                    ids.append(intern(key,net[row*4+col]))
            children[pid].append(len(new_patches))
            new_patches.append(tuple(ids))
    if len(new_patches)!=ORIGINAL_PATCHES+TARGET_SPLIT_PATCHES:
        raise ValueError('Old patch closure not conformingly split')
    replaced=defaultdict(list)
    for seed in seeds:
        eid=seed['edge_curve_id'];pid=seed['original_parent_patch_id'];side=seed['parent_side']
        candidates=[]
        for child_id in children[pid]:
            child=new_patches[child_id]
            side_ids=_side(child,side)
            expected=_side(original_patches[pid],side)
            if set(side_ids)==set(expected):
                raise ValueError('Source original generator was not subdivided')
            candidates.append((child_id,side,side_ids))
        if len(candidates)!=2:
            raise ValueError('Original generator does not have two child sides')
        replaced[eid]=candidates
    # The S3.Q island boundary is joined only by the four source EDGE_CURVE IDs.
    island_boundary,_=_boundary_sides(part,island_manifest['added_patches'])
    island_to_global={};per_edge={}
    for eid in PREEXISTING_GENERATORS:
        previous=replaced[eid]
        old_segments=[]
        for child_id,side,ids in previous:
            old_segments.append((child_id,side,ids))
        matched=[]
        for local_patch,side,_,_,_,_ in island_boundary[eid]:
            ids=_side(island_patches[local_patch],side)
            coords=[island_vertices[i] for i in ids]
            candidates=[]
            for child_id,parent_side,child_ids in old_segments:
                if any(child_id==i for i,j in matched):continue
                xyz=[points[i] for i in child_ids]
                direct=max(math.dist(a,b) for a,b in zip(coords,xyz))
                reverse=max(math.dist(a,b) for a,b in zip(coords,xyz[::-1]))
                if min(direct,reverse)<=CONTROL_TOL:
                    candidates.append((child_id,child_ids,reverse<direct,min(direct,reverse)))
            if len(candidates)!=1:
                raise ValueError(f'Nonunique original source edge #{eid} correspondence')
            child_id,child_ids,rev,discrepancy=candidates[0]
            global_ids=child_ids[::-1] if rev else child_ids
            for lid,gid in zip(ids,global_ids):
                if lid in island_to_global and island_to_global[lid]!=gid:
                    raise ValueError('Original source canonical control collision')
                island_to_global[lid]=gid
            matched.append((child_id,local_patch))
        if len(matched)!=2 or len({i for i,_ in matched})!=2:
            raise ValueError('Not exactly two original source pieces on both sides')
        per_edge[eid]={'previous_children':sorted(i for i,j in matched),
                       'island_patches':sorted(j for i,j in matched),
                       'original_source_edge_id':eid,'source_to_native_certified_in_s3q':True}
    for local,xyz in enumerate(island_vertices):
        if local in island_to_global:
            idx=island_to_global[local]
            if math.dist(points[idx],xyz)>CONTROL_TOL:
                raise ValueError('Source edge controls differ beyond predeclared threshold')
        else:
            idx=intern(('s3q_island_original_control',local),xyz)
            island_to_global[local]=idx
    island_start=len(new_patches)
    new_patches.extend(tuple(island_to_global[idx] for idx in p) for p in island_patches)
    # Every original shared generator must have exactly two two-sided pieces.
    final_edges=_edge_adjacency(new_patches)
    for eid,meta in per_edge.items():
        for child in meta['previous_children']:
            side=next(s for c,s,ids in replaced[eid] if c==child)
            key=tuple(sorted(_side(new_patches[child],side)))
            if len(final_edges[key])!=2 or not any(j>=island_start for j,_,_ in final_edges[key]):
                raise ValueError(f'Original source edge #{eid} is not two-sided after retopology')
    if any(len(v)>2 for v in final_edges.values()):
        raise ValueError('Non-manifold indexed source side introduced')
    joined=_serialize(points,new_patches)
    active_control_ids={idx for patch in new_patches for idx in patch}
    unused_historical_ids=[i for i in range(ORIGINAL_CONTROLS)
                           if i not in active_control_ids]
    if (len(active_control_ids)!=1349 or len(unused_historical_ids)!=118 or
            any(i not in active_control_ids for i in range(ORIGINAL_CONTROLS,len(points)))):
        raise ValueError('Unexpected active-control ownership after original subdivision')
    # Keep original control IDs as historical provenance, even when inactive.
    # A separate compact export removes these unused declarations for consumers.
    report={'schema':'apmesh-s3r-original-s40-conforming-218-join-v1',
            'source_sha256':part['source_sha256'],'original_baseline_bp_sha256':sha256(prior_bp.encode()).hexdigest(),
            'original_island_bp_sha256':sha256(island_bp.encode()).hexdigest(),
            'joined_bp_sha256':sha256(joined.encode()).hexdigest(),
            'prior_patches':77,'prior_controls':864,'source_faces_prior':16,
            'propagated_parent_patch_count':len({pid for pid,axis in required}),
            'propagated_split_records':[
                {'parent_patch_id':pid,'axis':axis,'t':t,'source_root':eid}
                for (pid,axis),(t,eid) in sorted(required.items())],
            'source_seed_edges':seeds,'retopologized_old_patch_count':island_start,
            'island_original_face_id':FACE_ID,'island_patches_added':30,
            'joined_patch_count':len(new_patches),'joined_control_count':len(points),
            'active_referenced_control_count':len(active_control_ids),
            'unused_historical_control_count':len(unused_historical_ids),
            'unused_historical_control_indices':unused_historical_ids,
            'source_original_face_coverage':17,'source_face_count':43,
            'joined_original_generator_controls':per_edge,
            'two_sided_indexed_seam_count':sum(len(x)==2 for x in final_edges.values()),
            'boundary_indexed_side_count':sum(len(x)==1 for x in final_edges.values()),
            'source_inner_hole_retained':True,'pilot_budget_mm':budget_mm,
            'source_nonmanifold_3plus':'NOT_ESTABLISHED',
            'apmesh_tri_quad_mesh':'NOT_RUN',
            'joined_control_comparison_tolerance_mm':CONTROL_TOL,
            'source_seam_identity_method':'ORIGINAL_EDGE_CURVE_AND_PARENT_CONTROL_LINEAGE_NOT_COORDINATE_WELD',
            'old_patch_child_map':{str(k):v for k,v in children.items()},
            'island_first_patch_id':island_start}
    return joined,report


def audit_join(source,native,bp,report,prior_bp,prior_manifest,island_bp,island_manifest):
    if report.get('pilot_budget_mm')!=BUDGET_MM:
        raise ValueError('Modified experimental budget')
    recreated,expected=build_join(source,prior_bp,prior_manifest,island_bp,island_manifest)
    if recreated!=bp or expected!=report:
        raise ValueError('Changed or forged joined BP/manifest; recomputation fails')
    part=source_partition(source)
    points,patches=read_bp(bp)
    old_points,old_patches=read_bp(prior_bp)
    if len(patches)!=report['joined_patch_count'] or len(points)!=report['joined_control_count']:
        raise ValueError('Joined BP inventory mismatch')
    active_control_ids={idx for patch in patches for idx in patch}
    if (len(active_control_ids)!=report['active_referenced_control_count'] or
            sum(i not in active_control_ids for i in range(ORIGINAL_CONTROLS))!=report['unused_historical_control_count'] or
            any(i not in active_control_ids for i in range(ORIGINAL_CONTROLS,len(points)))):
        raise ValueError('Original retired control ownership changed')
    # Exact de Casteljau subdivision preserves all 77 old surfaces.
    max_unchanged=0
    for pid,original in enumerate(old_patches):
        kids=report['old_patch_child_map'][str(pid)]
        values=[old_points[i] for i in original]
        if len(kids)==1:
            test=[points[i] for i in patches[kids[0]]]
            for u,v in ((0,0),(0.37,0.51),(1,1)):
                max_unchanged=max(max_unchanged,math.dist(surface(values,u,v),surface(test,u,v)))
        else:
            info=next(row for row in report['propagated_split_records'] if row['parent_patch_id']==pid)
            axis=info['axis'];t=info['t']
            for child_half,kid in enumerate(kids):
                test=[points[i] for i in patches[kid]]
                for u,v in ((0,0),(0.25,0.75),(0.5,0.5),(1,1)):
                    old_u=(t*u if child_half==0 else t+(1-t)*u) if axis=='u' else u
                    old_v=(t*v if child_half==0 else t+(1-t)*v) if axis=='v' else v
                    gap=math.dist(surface(values,old_u,old_v),surface(test,u,v))
                    max_unchanged=max(max_unchanged,gap)
    if max_unchanged>CONTROL_TOL:
        raise ValueError('de Casteljau split moved original surface')
    face=native.Faces()[1]
    if face.geomType()!='CYLINDER' or len(face.Wires())!=2:
        raise ValueError('Missing original holed native BRep face')
    island_start=report['island_first_patch_id']
    original_island=audit_island(source,native,island_bp,island_manifest)
    boundary,frontier=_boundary_sides(part,island_manifest['added_patches'])
    native_edges=_native_edges(part,native,1)
    edge_stats=_boundary_distance(part,points,patches[island_start:],native_edges,boundary,face,BUDGET_MM)
    max_projection=0;max_radial=0;counts=Counter()
    for local,row in enumerate(island_manifest['added_patches']):
        a,b,z0,z1=row['source_uv_rectangle']
        geom={'frame':part['frame'],'face_id':FACE_ID,'zmin':z0,'zmax':z1,
              'start_u':a,'signed_sweep_rad':b-a}
        cert=certify_patch(points,patches[island_start+local],geom,0,1)
        if cert['radial_support_error_upper_mm']>BUDGET_MM:
            raise ValueError('Reindexed island violates radial support bound')
        native_check=classify_patch(face,points,patches[island_start+local],
                                    distance_budget_mm=BUDGET_MM,interior_grid=9,boundary_grid=11)
        counts.update(native_check['classification_histogram'])
        max_projection=max(max_projection,native_check['max_native_cylinder_projection_distance_mm'])
        max_radial=max(max_radial,cert['radial_support_error_upper_mm'])
    # Independently recheck the retopologized original cylinder children.
    # This is distinct from the exact de Casteljau old-surface invariance.
    from s3m_s40_complex_trim_inventory import inventory
    native_original=inventory(source,native)
    native_index={r['source_advanced_face_id']:r['native_face_index']
                  for r in native_original['faces']}
    if native_index.get(1986)!=17 or native_index.get(1519)!=12:
        raise ValueError('Prior source to native cylinder face indices changed')
    retopology_native_samples=Counter()
    retopology_native_children=0
    retopology_max_distance=0.0
    for item in report['propagated_split_records']:
        pid=item['parent_patch_id']
        source_face=1986 if 25<=pid<=42 else 1519 if 43<=pid<=58 else None
        if source_face is None:
            continue
        indexed_native=native.Faces()[native_index[source_face]]
        for child in report['old_patch_child_map'][str(pid)]:
            native_result=classify_patch(indexed_native,points,patches[child],
                              distance_budget_mm=BUDGET_MM,interior_grid=7,boundary_grid=9)
            retopology_native_children+=1
            retopology_native_samples.update(native_result['classification_histogram'])
            retopology_max_distance=max(retopology_max_distance,
                          native_result['max_native_cylinder_projection_distance_mm'])
    if retopology_native_children!=34:
        raise ValueError('Unverified original cylinder child in closure')
    hole_out=0
    U=part['breakpoints_u'];V=part['breakpoints_v']
    for i in range(1,8):
        for j in range(1,8):
            uv=gp_Pnt2d(U[2]+(U[3]-U[2])*i/8,V[1]+(V[3]-V[1])*j/8)
            if BRepClass_FaceClassifier(face.wrapped,uv,1e-7).State()!=TopAbs_OUT:
                raise ValueError('S3.R unexpectedly filled the original hole')
            hole_out+=1
    return {'schema':'apmesh-s3r-original-native-conforming-joint-audit-v1',
            'joined_bp_sha256':report['joined_bp_sha256'],
            'active_referenced_control_count':len(active_control_ids),
            'unused_historical_control_count':report['unused_historical_control_count'],
            'native_hole_OUT_samples':hole_out,
            'native_island_trim_classification_histogram':dict(counts),
            'original_source_native_boundary_count':len(edge_stats),
            'original_inner_hole_native_edge_count':sum(x['wire']=='HOLE' for x in edge_stats),
            'max_native_source_edge_distance_mm':max(x['max_sampled_native_3d_edge_distance_mm'] for x in edge_stats),
            'max_native_cylinder_projection_distance_mm':max_projection,
            'max_guarded_radial_support_bound_mm':max_radial,
            'max_original_surface_reparameterization_sample_difference_mm':max_unchanged,
            'retopologized_original_native_cylinder_children':retopology_native_children,
            'retopologized_original_native_sample_histogram':dict(retopology_native_samples),
            'retopologized_original_native_max_projection_distance_mm':retopology_max_distance,
            'pilot_budget_mm':BUDGET_MM,
            'coverage_scope':'ONLY_REINDEXED_ORIGINAL_HOLED_FACE_AND_UNCHANGED_OLD_GEOMETRY',
            'continuous_trim_or_hole_topology_certificate':'NOT_ESTABLISHED',
            'apmesh_tri_quad_mesh':'NOT_RUN'}



def compact_join(bp,manifest):
    """Produce a consumer-oriented dense BP with an explicit provenance map.

    This never welds controls: it only deletes unreferenced records and renumbers
    the remaining original integer-indexed vertices in stable ascending order.
    """
    if sha256(bp.encode()).hexdigest()!=manifest.get('joined_bp_sha256'):
        raise ValueError('Cannot compact an altered source-indexed joined BP')
    points,patches=read_bp(bp)
    referenced=sorted({index for patch in patches for index in patch})
    omitted=[i for i in range(len(points)) if i not in set(referenced)]
    if (len(referenced)!=manifest['active_referenced_control_count'] or
            omitted!=manifest['unused_historical_control_indices'] or
            any(i>=ORIGINAL_CONTROLS for i in omitted)):
        raise ValueError('Compact BP cannot retire a live source control')
    remap={i:j for j,i in enumerate(referenced)}
    compact=_serialize([points[i] for i in referenced],
                       [tuple(remap[index] for index in patch) for patch in patches])
    compact_points,compact_patches=read_bp(compact)
    if len(compact_points)!=len(referenced) or len(compact_patches)!=len(patches):
        raise ValueError('Compact BP topology count changed')
    for original,rewritten in zip(patches,compact_patches):
        if [points[i] for i in original]!=[compact_points[i] for i in rewritten]:
            raise ValueError('Compact BP changed original indexed surface controls')
    receipt={
        'schema':'apmesh-s3r-source-identity-preserving-compact-bp-v1',
        'source_joined_bp_sha256':manifest['joined_bp_sha256'],
        'compact_bp_sha256':sha256(compact.encode()).hexdigest(),
        'source_vertex_declarations':len(points),
        'compact_vertex_declarations':len(compact_points),
        'original_historical_unreferenced_vertices':len(omitted),
        'old_control_index_to_compact_index':{str(i):j for i,j in remap.items()},
        'unreferenced_old_indices_retired':omitted,
        'patch_count':len(patches),
        'control_nets_match_original_exactly':True,
        'original_source_curve_identity_registry':'PRESERVED_IN_ORIGINAL_MANIFEST_AND_MAP',
        'apmesh_tri_quad':'NOT_RUN',
    }
    return compact,receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original-step',required=True)
    p.add_argument('--prior-bp',required=True)
    p.add_argument('--prior-manifest',required=True)
    p.add_argument('--island-bp',required=True)
    p.add_argument('--island-manifest',required=True)
    p.add_argument('--output-dir',required=True)
    args=p.parse_args()
    original=Path(args.original_step)
    raw=original.read_bytes()
    if sha256(raw).hexdigest()!=SOURCES['S40'][1]:raise ValueError('Original STEP SHA-256 mismatch')
    source=raw.decode('utf-8')
    prior_bp=Path(args.prior_bp).read_text()
    prior_manifest=json.loads(Path(args.prior_manifest).read_text())
    island_bp=Path(args.island_bp).read_text()
    island_manifest=json.loads(Path(args.island_manifest).read_text())
    bp,manifest=build_join(source,prior_bp,prior_manifest,island_bp,island_manifest)
    native=cq.importers.importStep(str(original)).val()
    receipt=audit_join(source,native,bp,manifest,prior_bp,prior_manifest,island_bp,island_manifest)
    compact_bp,compact_manifest=compact_join(bp,manifest)
    directory=Path(args.output_dir);directory.mkdir(parents=True,exist_ok=True)
    (directory/'s40_218_conforming.partial.bp').write_text(bp)
    (directory/'s40_218_conforming_manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    (directory/'s40_218_conforming_native_receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    (directory/'s40_218_conforming_compact.partial.bp').write_text(compact_bp)
    (directory/'s40_218_conforming_compact_id_map.json').write_text(json.dumps(compact_manifest,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='native_island_trim_classification_histogram'},indent=2))

if __name__=='__main__':main()
