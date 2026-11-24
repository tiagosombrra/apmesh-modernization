#!/usr/bin/env python3
"""Join source-identified planar quads and bounded cylindrical Bézier patches.

This isolated scientific probe does not create a complete CAD atlas or mesh.
All shared interfaces are keyed by original STEP EDGE_CURVE and VERTEX_POINT
identities, never by welding coordinate-near controls.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq

from audit_analytic_bp import read_bp, surface
from original_cad_planar_atlas import native_distance
from s3c_step_source_gate import (SOURCES, coordinates, entity, geometry_gate,
                                  oriented_edges, parse_entities, refs)
from s3e_native_feature_bijection import correlate, verify_certificate
from s3f_first_ring_native_faces import first_ring, recompute_audit
from s3h_source_cylinder_bp import construct as cylinder_construct
from s3h_source_cylinder_bp import face_geometry, independent_audit as cylinder_audit


def _linear_controls(table, wire):
    """Return a four-sided bilinear grid with canonical source-boundary keys."""
    valid, reason = geometry_gate(table, wire)
    if not valid:
        raise ValueError('Source planar face is not an eligible exact quad: ' + reason)
    verts = [e['start_vertex_id'] for e in wire]
    corners = [coordinates(table, identifier) for identifier in verts]
    points = []
    keys = []
    for row in range(4):
        v = row / 3
        for col in range(4):
            u = col / 3
            # Bilinear interpolation is exactly planar for a planar quadrilateral.
            points.append(tuple((1-v)*((1-u)*a+u*b)+v*((1-u)*d+u*c)
                                for a,b,c,d in zip(corners[0],corners[1],corners[2],corners[3])))
            keys.append(None)
    corners_slots = {0: verts[0], 3: verts[1], 15: verts[2], 12: verts[3]}
    for idx, vertex in corners_slots.items():
        keys[idx] = f'vertex:{vertex}'
    for side, edge in enumerate(wire):
        step_indices = (
            (0, 1, 2, 3) if side == 0 else
            (3, 7, 11, 15) if side == 1 else
            (15, 14, 13, 12) if side == 2 else
            (12, 8, 4, 0)
        )
        _, source_edge = entity(table, edge['edge_curve_id'], 'EDGE_CURVE')
        head, tail = refs(source_edge)[:2]
        if (edge['start_vertex_id'], edge['end_vertex_id']) == (head, tail):
            forward = True
        elif (edge['start_vertex_id'], edge['end_vertex_id']) == (tail, head):
            forward = False
        else:
            raise ValueError('Original planar edge direction contradicts STEP identity')
        for local in (1, 2):
            idx = step_indices[local]
            step = local if forward else 3-local
            key = f'edge:{edge["edge_curve_id"]}:{step}'
            if keys[idx] is not None and keys[idx] != key:
                raise ValueError('Conflicting original source side keys')
            keys[idx] = key
    if any(k is None for idx,k in enumerate(keys) if idx in (0,1,2,3,4,7,8,11,12,13,14,15)):
        raise ValueError('Unassigned original source boundary key')
    return corners, points, keys


def _serialize(points, patches):
    return '\n'.join(['// S3.I source-anchored planar/cylinder research BP; NOT a full APMesh atlas',
                      '// Distinct source STEP entities are never welded by proximity']+
                     ['v '+' '.join(format(x,'.17g') for x in p) for p in points]+
                     ['p '+' '.join(map(str,patch)) for patch in patches])+'\n'


def construct_joint(step_text, native_shape, *, model, source_sha256,
                    cylinder_face_ids, sectors=6, sampled_budget_mm=.001):
    """Build an auditable partial atlas only after native source face mapping."""
    if sha256(step_text.encode('utf-8')).hexdigest()!=source_sha256:
        raise ValueError('Input source digest mismatch')
    if model in SOURCES and source_sha256!=SOURCES[model][1]:
        raise ValueError('Pinned industrial input SHA-256 mismatch')
    if not isinstance(sectors,int) or sectors<1 or sectors>64:
        raise ValueError('Sector count outside [1,64]')
    if not math.isfinite(sampled_budget_mm) or sampled_budget_mm<=0:
        raise ValueError('Invalid predeclared sampled budget')
    if not cylinder_face_ids or len(set(cylinder_face_ids))!=len(cylinder_face_ids):
        raise ValueError('Cylinder source face IDs must be nonempty and distinct')
    cert = correlate(step_text,native_shape,model=model,source_sha256=source_sha256)
    verify_certificate(step_text,native_shape,cert,model=model,source_sha256=source_sha256)
    ring = first_ring(step_text,native_shape,cert,model=model,source_sha256=source_sha256)
    recompute_audit(step_text,native_shape,ring,model=model,source_sha256=source_sha256)
    all_faces=native_shape.Faces()
    native_candidates={rec['step_advanced_face_id']:rec['native_face_index']
                       for rec in cert['candidate_bindings']}
    native_excluded={rec['source_advanced_face_id']:rec['native_face_index']
                     for rec in ring['excluded_face_mapping']}
    table=parse_entities(step_text)
    points=[];key_ids={};patch_ids=[];metadata=[];curved=[]
    def intern(key,point):
        point=tuple(map(float,point))
        if key in key_ids:
            index=key_ids[key]
            if math.dist(points[index],point)>1e-9:
                raise ValueError('Same original feature key has incompatible control coordinates')
            return index
        index=len(points)
        key_ids[key]=index
        points.append(point)
        return index
    for face_id,native_id in sorted(native_candidates.items()):
        support,wires=oriented_edges(table,face_id)
        if support!='PLANE' or len(wires)!=1:
            raise ValueError('Native candidate source planar geometry changed')
        corners,net,keys=_linear_controls(table,wires[0])
        for idx,key in enumerate(keys):
            if key is None:
                keys[idx]=f'planar_interior:{face_id}:{idx//4}:{idx%4}'
        indices=[intern(key,coord) for key,coord in zip(keys,net)]
        patch_ids.append(indices)
        metadata.append({'kind':'SOURCE_EXACT_PLANAR_QUAD','source_face_id':face_id,
                         'source_native_face_index':native_id,
                         'original_edge_curve_ids':[e['edge_curve_id'] for e in wires[0]],
                         'original_vertices': [e['start_vertex_id'] for e in wires[0]],
                         'control_vertex_ids':indices})
        native=all_faces[native_id]
        for v in (0,.25,.5,.75,1):
            for u in (0,.25,.5,.75,1):
                expected=surface([points[j] for j in indices],u,v)
                if native_distance(native,expected)>1e-7:
                    raise ValueError('Planar source-to-native point distance exceeds gate')
    admitted_edges={x['source_edge_curve_id']:x for x in cert['boundary_interfaces']}
    for face_id in cylinder_face_ids:
        if face_id not in native_excluded or all_faces[native_excluded[face_id]].geomType()!='CYLINDER':
            raise ValueError('Original cylinder face is not mapped to a native first-ring support')
        geo=face_geometry(step_text,face_id=face_id,model=model,source_sha256=source_sha256,
                          require_anchored=(model in SOURCES))
        for generator in geo['generators']:
            edge=generator['edge_curve_id']
            if edge not in admitted_edges or admitted_edges[edge]['source_neighbor_face_id']!=face_id:
                raise ValueError('Cylinder generator lacks verified source-to-native planar anchor')
        cylinder_bp,manifest=cylinder_construct(geo,sectors=sectors,
                                                absolute_budget_mm=sampled_budget_mm)
        source_audit=cylinder_audit(step_text,cylinder_bp,manifest,
                                    model=model,source_sha256=source_sha256)
        if not source_audit['sampled_budget_pass']:
            raise ValueError('Cylindrical sector exceeds predeclared source sampled budget')
        local_points,local_patches=read_bp(cylinder_bp)
        mapping=[intern(key,coord) for key,coord in zip(manifest['control_keys'],local_points)]
        for index,ids in enumerate(local_patches):
            global_ids=[mapping[i] for i in ids]
            patch_ids.append(global_ids)
            metadata.append({'kind':'SOURCE_CYLINDER_APPROX_CANDIDATE',
                             'source_face_id':face_id,
                             'source_native_face_index':native_excluded[face_id],
                             'local_segment':index,'control_vertex_ids':global_ids})
        curved.append({'face_id':face_id,'source_native_face_index':native_excluded[face_id],
                       'original_generator_edges':[g['edge_curve_id'] for g in geo['generators']],
                       'source_fit_audit':source_audit,'segment_count':sectors})
    # Original generator boundaries must reuse global control vertex IDs on
    # both adjacent source faces, not merely coincide numerically in XYZ.
    seams=[]
    for cyl in curved:
        fid=cyl['face_id']
        for eid in cyl['original_generator_edges']:
            sources=[x for x in metadata if x['kind']=='SOURCE_EXACT_PLANAR_QUAD'
                     and eid in x['original_edge_curve_ids']]
            targets=[x for x in metadata if x['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE'
                     and x['source_face_id']==fid]
            if len(sources)!=1:
                raise ValueError('Original cylindrical generator is not uniquely anchored to planar patch')
            planar=sources[0]
            planar_points=[planar['control_vertex_ids'][k] for k in range(16)]
            shared=[]
            for endpoint in (0,1,2,3):
                if endpoint==0:
                    # Resolve true original source start vertex rather than guess.
                    _,edge=entity(table,eid,'EDGE_CURVE')
                    vertex=refs(edge)[0]
                    key=f'vertex:{vertex}'
                elif endpoint==3:
                    vertex=refs(entity(table,eid,'EDGE_CURVE')[1])[1]
                    key=f'vertex:{vertex}'
                else:
                    key=f'edge:{eid}:{endpoint}'
                index=key_ids.get(key)
                if index is None or index not in planar_points:
                    raise ValueError('Planar BP does not expose source generator control')
                cyl_patches=[target['control_vertex_ids'] for target in targets]
                if not any(index in patch for patch in cyl_patches):
                    raise ValueError('Cylindrical BP does not expose same indexed source control')
                shared.append(index)
            seams.append({'source_edge_curve_id':eid,
                          'planar_source_face_id':planar['source_face_id'],
                          'cylinder_source_face_id':fid,
                          'shared_original_control_vertex_ids':shared})
    bp=_serialize(points,patch_ids)
    result={'schema':'apmesh-s3i-source-native-joint-partial-atlas-v1',
            'scientific_scope':'PARTIAL_SOURCE_IDENTIFIED_PLANAR_AND_CYLINDER_ONLY',
            'source_model':model,'source_sha256':source_sha256,
            'source_advanced_face_total':cert['source_advanced_face_total'],
            'source_native_candidate_face_bindings':len(native_candidates),
            'source_native_first_ring_face_bindings':ring['excluded_source_faces_mapped_by_edge_identity'],
            'admitted_planar_source_faces':len(native_candidates),
            'admitted_cylinder_source_faces':len(curved),
            'generated_partial_bp_patch_count':len(patch_ids),
            'unique_control_points':len(points),
            'shared_original_generator_edges':len(seams),
            'original_generator_shared_controls':seams,
            'source_native_certificate_sha256':cert['certificate_sha256'],
            'first_ring_report_sha256':ring['report_sha256'],
            'cylinder_fit_receipts':curved,
            'patches':metadata,'control_key_to_id':key_ids,
            'bp_sha256':sha256(bp.encode()).hexdigest(),
            'native_cylinder_face_trim_and_pcurve_mapping':'NOT_CERTIFIED',
            'native_cylinder_surface_distance_oracle':'PENDING_INDEPENDENT_SAMPLED_AUDIT',
            'continuous_error_bound':'NOT_CERTIFIED',
            'complete_original_cad_atlas':False,
            'accepted_apmesh_tri_quad':'NOT_RUN',
            'original_external_nonmanifold_positive':'NOT_ESTABLISHED'}
    return bp,result


def independently_check_joint(step_text,native_shape,bp,receipt,*,model,source_sha256):
    """Recheck source identities and geometry against original/native oracles."""
    if sha256(bp.encode()).hexdigest()!=receipt.get('bp_sha256'):
        raise ValueError('Joint BP SHA-256 mismatch')
    if receipt['source_sha256']!=source_sha256 or receipt['source_model']!=model:
        raise ValueError('Joint model/source binding mismatch')
    vertices,patches=read_bp(bp)
    if len(patches)!=receipt['generated_partial_bp_patch_count'] or len(vertices)!=receipt['unique_control_points']:
        raise ValueError('Joint BP inventory mismatch')
    labels=receipt['patches']
    if len(labels)!=len(patches):
        raise ValueError('Joint patch metadata mismatch')
    for patch,meta in zip(patches,labels):
        if list(patch)!=meta['control_vertex_ids']:
            raise ValueError('Joint patch IDs do not match source metadata')
    direct=correlate(step_text,native_shape,model=model,source_sha256=source_sha256)
    if direct['certificate_sha256']!=receipt['source_native_certificate_sha256']:
        raise ValueError('Joint source-native face mapping changed')
    first=first_ring(step_text,native_shape,direct,model=model,source_sha256=source_sha256)
    if first['report_sha256']!=receipt['first_ring_report_sha256']:
        raise ValueError('Joint native first-ring mapping changed')
    table=parse_entities(step_text)
    checked=0
    for seam in receipt['original_generator_shared_controls']:
        eid=seam['source_edge_curve_id']
        source=next((p for p in labels if p['kind']=='SOURCE_EXACT_PLANAR_QUAD'
                     and p['source_face_id']==seam['planar_source_face_id']),None)
        cylinders=[p for p in labels if p['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE'
                   and p['source_face_id']==seam['cylinder_source_face_id']]
        if source is None or not cylinders:
            raise ValueError('Missing source patch in original boundary audit')
        _,edge=entity(table,eid,'EDGE_CURVE')
        a,b=refs(edge)[:2]
        canonical=[f'vertex:{a}',f'edge:{eid}:1',f'edge:{eid}:2',f'vertex:{b}']
        indices=[receipt['control_key_to_id'].get(key) for key in canonical]
        if indices!=seam['shared_original_control_vertex_ids']:
            raise ValueError('Tampered original source boundary identity')
        if any(k is None for k in indices) or not set(indices).issubset(set(source['control_vertex_ids'])):
            raise ValueError('Planar source boundary control identity missing')
        if not set(indices).issubset(set(k for p in cylinders for k in p['control_vertex_ids'])):
            raise ValueError('Cylinder source boundary control identity missing')
        A=coordinates(table,a); B=coordinates(table,b)
        for i,k in enumerate(indices):
            expected=tuple((1-i/3)*x+(i/3)*y for x,y in zip(A,B))
            if math.dist(vertices[k],expected)>1e-9:
                raise ValueError('Original edge geometry incompatible with canonical source control')
        checked+=1
    # Independently check all generated planar patches against native imported
    # faces. Native distance oracle prevents metadata-only acceptance.
    faces=native_shape.Faces()
    expected_planar={p['step_advanced_face_id']:p['native_face_index']
                     for p in direct['candidate_bindings']}
    expected_ring={p['source_advanced_face_id']:p['native_face_index']
                   for p in first['excluded_face_mapping']}
    max_plane=0.0
    max_cylinder=0.0
    tested_cylinder=0
    for patch,meta in zip(patches,labels):
        is_planar=meta['kind']=='SOURCE_EXACT_PLANAR_QUAD'
        if is_planar:
            expected_index=expected_planar.get(meta['source_face_id'])
        elif meta['kind']=='SOURCE_CYLINDER_APPROX_CANDIDATE':
            expected_index=expected_ring.get(meta['source_face_id'])
        else:
            raise ValueError('Unsupported joint source surface classification')
        if expected_index is None or meta['source_native_face_index']!=expected_index:
            raise ValueError('Forged joint source-to-native face identity')
        native=faces[expected_index]
        for j in range(11):
            for i in range(11):
                xyz=surface([vertices[k] for k in patch],i/10,j/10)
                deviation=native_distance(native,xyz)
                if is_planar:
                    max_plane=max(max_plane,deviation)
                else:
                    max_cylinder=max(max_cylinder,deviation)
                    tested_cylinder+=1
    if max_plane>1e-7:
        raise ValueError('Joint planar face geometric oracle failed')
    budget=max(x['source_fit_audit']['prespecified_budget_mm'] for x in receipt['cylinder_fit_receipts'])
    if max_cylinder>budget+1e-7:
        raise ValueError('Joint native trimmed cylinder sampled distance exceeds budget')
    return {'schema':'apmesh-s3i-independent-joint-boundary-audit-v1',
            'source_original_generator_edges_checked':checked,
            'shared_original_generator_control_ids_checked':4*checked,
            'independent_planar_source_face_distance_max_mm':max_plane,
            'independent_native_trimmed_cylinder_distance_max_mm':max_cylinder,
            'native_cylinder_distance_sample_count':tested_cylinder,
            'prespecified_cylinder_sampled_budget_mm':budget,
            'native_source_identity_bijection_verified':True,
            'native_cylinder_uv_trim_oracle':'NOT_CERTIFIED_BY_SAMPLED_DISTANCE',
            'continuous_cylinder_error_certificate':'NOT_CERTIFIED',
            'full_cad_atlas':'NOT_RUN','apmesh_generation':'NOT_RUN'}


def run(step_file,output_dir,*,model,source_sha256=None,cylinder_face_ids,sectors=6,sampled_budget_mm=.001):
    raw=Path(step_file).read_bytes()
    actual=sha256(raw).hexdigest()
    if model in SOURCES:
        if actual!=SOURCES[model][1]:
            raise ValueError('Pinned original STEP SHA-256 mismatch')
    elif not source_sha256 or actual!=source_sha256:
        raise ValueError('Explicit synthetic STEP SHA-256 mismatch')
    text=raw.decode('utf-8')
    shape=cq.importers.importStep(str(step_file)).val()
    bp,receipt=construct_joint(text,shape,model=model,source_sha256=actual,
                               cylinder_face_ids=cylinder_face_ids,sectors=sectors,
                               sampled_budget_mm=sampled_budget_mm)
    report=independently_check_joint(text,shape,bp,receipt,model=model,source_sha256=actual)
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    (output_dir/'source_joint.partial.bp').write_text(bp,encoding='utf-8')
    (output_dir/'source_joint_manifest.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (output_dir/'independent_joint_audit.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return receipt,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-step',type=Path,required=True)
    parser.add_argument('--model',required=True)
    parser.add_argument('--expected-sha256')
    parser.add_argument('--cylinder-faces',type=int,nargs='+',required=True)
    parser.add_argument('--sectors',type=int,default=6)
    parser.add_argument('--sampled-budget-mm',type=float,default=.001)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    receipt,audit=run(args.source_step,args.output,model=args.model,
                      source_sha256=args.expected_sha256,cylinder_face_ids=args.cylinder_faces,
                      sectors=args.sectors,sampled_budget_mm=args.sampled_budget_mm)
    print(json.dumps({'model':receipt['source_model'],
                      'source_sha256':receipt['source_sha256'],
                      'patches':receipt['generated_partial_bp_patch_count'],
                      'original_shared_edges':receipt['shared_original_generator_edges'],
                      'original_control_ids_checked':audit['shared_original_generator_control_ids_checked'],
                      'status':'PARTIAL_RESEARCH_ONLY'},sort_keys=True))


if __name__=='__main__':
    main()
