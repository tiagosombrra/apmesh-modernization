#!/usr/bin/env python3
"""Research-only source-STEP constrained cylinder-to-bicubic BP construction.

Requires explicit source arc orientation and original EDGE_CURVE canonical keys.
Even a passing result does not prove native OCCT UV trim or APMesh acceptance.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

from audit_analytic_bp import read_bp, surface
from s3c_step_source_gate import (COORDINATES, SOURCES, coordinates,
                                  entity, oriented_edges, parse_entities, refs)
from s3g_cylindrical_source_constraints import (_axis_support, _cross, _dot,
                                                 _norm, _point, _sub)


def _unit(x):
    n = _norm(x)
    if n < 1e-14:
        raise ValueError('Degenerate native STEP direction')
    return tuple(v / n for v in x)


def _scale(a, c):
    return tuple(c * x for x in a)


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _point2(table, identifier):
    _, value = entity(table, identifier, 'CARTESIAN_POINT')
    matched = COORDINATES.search(value)
    if not matched:
        raise ValueError('Invalid source UV coordinate')
    xy = tuple(map(float, matched[1].split(',')))
    if len(xy) != 2 or not all(math.isfinite(c) for c in xy):
        raise ValueError('Expected finite source UV pair')
    return xy


def _source_cylinder_frame(table, face_id):
    support_id, origin, axis, radius = _axis_support(table, face_id)
    _, cylinder = entity(table, support_id, 'CYLINDRICAL_SURFACE')
    placement_id = refs(cylinder)[0]
    _, placement = entity(table, placement_id, 'AXIS2_PLACEMENT_3D')
    frame = refs(placement)
    if len(frame) != 3:
        raise ValueError('Source cylinder missing azimuth reference direction')
    x = _unit(_point(table, frame[2], expected='DIRECTION'))
    if abs(_dot(x, axis)) > 1e-9:
        raise ValueError('Cylinder axis and azimuth reference not perpendicular')
    y = _unit(_cross(axis, x))
    return {'id': support_id, 'origin': origin, 'axis': axis,
            'radius': radius, 'x': x, 'y': y}


def _source_pcurve_const_u(table, original_edge_id, support_id):
    _, edge = entity(table, original_edge_id, 'EDGE_CURVE')
    wrapper_id = refs(edge)[2]
    for _ in range(4):
        kind, wrapper = entity(table, wrapper_id)
        if kind == 'LINE':
            raise ValueError('Missing source cylinder PCURVE wrapper')
        if kind not in ('SURFACE_CURVE', 'SEAM_CURVE', 'INTERSECTION_CURVE'):
            raise ValueError('Unsupported original generator PCURVE wrapper')
        for candidate in refs(wrapper)[1:]:
            typ, payload = entity(table, candidate)
            if typ != 'PCURVE':
                continue
            target, rep = refs(payload)
            if target != support_id:
                continue
            _, representation = entity(table, rep, 'DEFINITIONAL_REPRESENTATION')
            curve_id = refs(representation)[0]
            _, pcurve = entity(table, curve_id, 'LINE')
            cp, vector = refs(pcurve)
            xy = _point2(table, cp)
            _, vector_raw = entity(table, vector, 'VECTOR')
            vecid = refs(vector_raw)[0]
            _, direction = entity(table, vecid, 'DIRECTION')
            m = COORDINATES.search(direction)
            if not m:
                raise ValueError('Invalid source UV PCURVE direction')
            d = tuple(map(float, m[1].split(',')))
            if len(d) != 2 or abs(d[0]) > 1e-9 or abs(d[1]) < 1e-12:
                raise ValueError('Source generator pcurve is not constant-U')
            return xy[0]
        wrapper_id = refs(wrapper)[0]
    raise ValueError('Missing source generator cylinder PCURVE')


def _canonical_source_keys(table, edge_id, axial_axis, origin):
    _, edge = entity(table, edge_id, 'EDGE_CURVE')
    a_id, b_id = refs(edge)[:2]
    a, b = coordinates(table, a_id), coordinates(table, b_id)
    za = _dot(_sub(a, origin), axial_axis)
    zb = _dot(_sub(b, origin), axial_axis)
    if abs(zb - za) < 1e-12:
        raise ValueError('Source generator has no axial length')
    if za < zb:
        order = [(('vertex', a_id), a), (('edge', edge_id, 1), None),
                 (('edge', edge_id, 2), None), (('vertex', b_id), b)]
    else:
        order = [(('vertex', b_id), b), (('edge', edge_id, 2), None),
                 (('edge', edge_id, 1), None), (('vertex', a_id), a)]
    points = [tuple((1-t)*x+t*y for x,y in zip(a if za<zb else b,
                                               b if za<zb else a))
              for t in (0,1/3,2/3,1)]
    return [(key, point) for (key,_),point in zip(order,points)]


def _circle_edge_sweep(table, edge_record, frame):
    edge_id = edge_record['edge_curve_id']
    _, edge = entity(table, edge_id, 'EDGE_CURVE')
    edge_refs = refs(edge)
    wrapper = edge_refs[2]
    for _ in range(4):
        kind, payload = entity(table, wrapper)
        if kind not in ('SURFACE_CURVE','SEAM_CURVE','INTERSECTION_CURVE'):
            break
        wrapper = refs(payload)[0]
    _, circle = entity(table, wrapper, 'CIRCLE')
    pids = refs(circle)
    if len(pids) != 1:
        raise ValueError('Invalid source CIRCLE placement')
    radius = float(circle.rsplit(',', 1)[-1])
    _, placement = entity(table, pids[0], 'AXIS2_PLACEMENT_3D')
    frame_ids = refs(placement)
    if len(frame_ids) != 3:
        raise ValueError('Missing oriented source CIRCLE frame')
    origin = _point(table,frame_ids[0],expected='CARTESIAN_POINT')
    normal = _unit(_point(table,frame_ids[1],expected='DIRECTION'))
    x = _unit(_point(table,frame_ids[2],expected='DIRECTION'))
    y = _unit(_cross(normal,x))
    if abs(abs(_dot(normal,frame['axis']))-1) > 1e-8:
        raise ValueError('Original CIRCLE axis differs from CYLINDRICAL_SURFACE')
    if abs(radius-frame['radius']) > 1e-8:
        raise ValueError('Original CIRCLE radius differs from cylinder')
    offset = _sub(origin,frame['origin'])
    if _norm(_cross(offset,frame['axis'])) > 1e-8:
        raise ValueError('Original CIRCLE not concentric with cylinder')
    start = coordinates(table,edge_record['start_vertex_id'])
    end = coordinates(table,edge_record['end_vertex_id'])
    def phi(point):
        r = _sub(point,origin)
        if abs(_norm(r)-radius)>1e-7:
            raise ValueError('Original circular edge vertex off circle')
        return math.atan2(_dot(r,y),_dot(r,x)) % (2*math.pi)
    start_phi,end_phi = phi(start),phi(end)
    original_start_id= edge_refs[0]
    oriented_forward=(original_start_id == edge_record['start_vertex_id'])
    same_sense=edge.strip().endswith('.T.')
    forward_curve = oriented_forward == same_sense
    sweep=((end_phi-start_phi)%(2*math.pi))
    if not forward_curve:
        sweep -= 2*math.pi
    if abs(sweep) < 1e-8 or abs(sweep) >= 2*math.pi-1e-8:
        raise ValueError('Degenerate/closed circular arc not admitted')
    signed_on_cylinder = sweep * (1 if _dot(normal,frame['axis']) > 0 else -1)
    return {'edge_curve_id':edge_id, 'sweep_rad_signed':signed_on_cylinder,
            'sweep_rad_absolute':abs(sweep),
            'start_vertex_id':edge_record['start_vertex_id'],
            'end_vertex_id':edge_record['end_vertex_id']}


def face_geometry(step_text, *, face_id, model, source_sha256, require_anchored=False):
    digest=sha256(step_text.encode('utf-8')).hexdigest()
    if digest != source_sha256 or (model in SOURCES and SOURCES[model][1] != digest):
        raise ValueError('Pinned STEP source SHA-256 mismatch')
    table=parse_entities(step_text)
    support,wires=oriented_edges(table,face_id)
    if support!='CYLINDRICAL_SURFACE' or len(wires)!=1 or len(wires[0])!=4:
        raise ValueError('Source face is not a single four-edge cylindrical wire')
    wire=wires[0]
    generators=[x for x in wire if x['master_3d_curve']=='LINE']
    arcs=[x for x in wire if x['master_3d_curve']=='CIRCLE']
    if len(generators)!=2 or len(arcs)!=2:
        raise ValueError('Source face lacks exactly two LINE generators and two CIRCLE arcs')
    frame=_source_cylinder_frame(table,face_id)
    # Both original generator edges must also be anchored to original planar
    # candidates when requiring a model-specific industrial conversion.
    if require_anchored:
        from s3d_canonical_feature_curves import interface_inventory
        _,_,inventory=interface_inventory(step_text,model=model,source_sha256=source_sha256)
        anchored={x['original_edge_curve_id'] for x in inventory
                  if x['excluded_neighbor_face_id']==face_id and
                     x['excluded_neighbor_support']=='CYLINDRICAL_SURFACE'}
        if anchored != {x['edge_curve_id'] for x in generators}:
            raise ValueError('Source generator not anchored to planar candidate')
    gs=[]
    for edge in generators:
        curveid=edge['edge_curve_id']
        u=_source_pcurve_const_u(table,curveid,frame['id'])
        keys=_canonical_source_keys(table,curveid,frame['axis'],frame['origin'])
        gs.append({'edge_curve_id':curveid,'u':u,'controls':keys,
                   'vertex_ids':[edge['start_vertex_id'],edge['end_vertex_id']]})
    zvals=[_dot(_sub(p,frame['origin']),frame['axis']) for g in gs for _,p in g['controls']]
    zmin,zmax=min(zvals),max(zvals)
    if abs(zvals[0]-zvals[4])>1e-7 or abs(zvals[3]-zvals[7])>1e-7 or zmax-zmin<1e-8:
        raise ValueError('Original generator V spans disagree')
    arc_data=[_circle_edge_sweep(table,e,frame) for e in arcs]
    if abs(arc_data[0]['sweep_rad_signed']+arc_data[1]['sweep_rad_signed'])>1e-7:
        raise ValueError('Original circular boundary arcs disagree in sweep')
    sweep=arc_data[0]['sweep_rad_signed']
    generator_by_vertex={vertex_id:g for g in gs for vertex_id in g['vertex_ids']}
    start=generator_by_vertex[arc_data[0]['start_vertex_id']]
    end=generator_by_vertex[arc_data[0]['end_vertex_id']]
    if start is end:
        raise ValueError('Source CIRCLE does not connect distinct generators')
    src_phi_start=start['u']; src_phi_end=end['u']
    expected_phi=(src_phi_start+sweep)%(2*math.pi)
    if abs((src_phi_end-expected_phi+math.pi)%(2*math.pi)-math.pi)>1e-7:
        raise ValueError('Circular arc sweep contradicts original generator PCURVE U')
    # Confirm constant-U source pcurve is consistent with the STEP cylinder frame.
    for generator in gs:
        for _,P in generator['controls'][::3]:
            delta=_sub(P,frame['origin']); z=_dot(delta,frame['axis'])
            radial=_sub(delta,_scale(frame['axis'],z))
            ref=_add(_scale(frame['x'],math.cos(generator['u'])),
                     _scale(frame['y'],math.sin(generator['u'])))
            if math.dist(radial,_scale(ref,frame['radius']))>1e-7:
                raise ValueError('Original STEP cylinder PCURVE U mismatches 3D vertex')
    # The reversed original CIRCLE must connect the same two generators.
    opposite=arc_data[1]
    if generator_by_vertex.get(opposite['start_vertex_id']) is not end or generator_by_vertex.get(opposite['end_vertex_id']) is not start:
        raise ValueError('Second CIRCLE does not close same source generator pair')
    return {'frame':frame,'face_id':face_id,'source_model':model,'source_sha256':digest,
            'generators':gs,'start_generator_edge':start['edge_curve_id'],
            'end_generator_edge':end['edge_curve_id'],'start_u':src_phi_start,
            'signed_sweep_rad':sweep,'original_circle_records':arc_data,
            'zmin':zmin,'zmax':zmax,'original_wire_edge_ids':[x['edge_curve_id'] for x in wire]}


def _encode_key(key):
    return ':'.join(map(str,key))


def construct(geometry, *, sectors, absolute_budget_mm):
    if not isinstance(sectors,int) or not 1<=sectors<=64:
        raise ValueError('Sector count must be in [1,64]')
    if not math.isfinite(absolute_budget_mm) or absolute_budget_mm<=0:
        raise ValueError('Budget must be finite and positive')
    f=geometry['frame']; face=geometry['face_id']; delta=geometry['signed_sweep_rad']/sectors
    start=next(g for g in geometry['generators'] if g['edge_curve_id']==geometry['start_generator_edge'])
    end=next(g for g in geometry['generators'] if g['edge_curve_id']==geometry['end_generator_edge'])
    registry={};points=[];keys=[];patches=[];details=[]
    def intern(key,coord):
        token=_encode_key(key)
        if token in registry:
            i=registry[token]
            if math.dist(points[i],coord)>1e-9:
                raise ValueError('Canonical source/derived control mismatch')
            return i
        i=len(points);registry[token]=i;points.append(tuple(coord));keys.append(token);return i
    def boundary(seam,row):
        if seam==0:return start['controls'][row]
        if seam==sectors:return end['controls'][row]
        u=geometry['start_u']+delta*seam
        z=geometry['zmin']+(geometry['zmax']-geometry['zmin'])*row/3
        radial=_add(_scale(f['x'],math.cos(u)),_scale(f['y'],math.sin(u)))
        P=_add(_add(f['origin'],_scale(f['axis'],z)),_scale(radial,f['radius']))
        return (('derived_u_seam',face,seam,row),P)
    for part in range(sectors):
        ids=[]
        for row in range(4):
            leftkey,A=boundary(part,row);rightkey,B=boundary(part+1,row)
            ua=geometry['start_u']+delta*part;ub=ua+delta
            ta=_scale(_add(_scale(f['x'],-math.sin(ua)),_scale(f['y'],math.cos(ua))),f['radius']*delta/3)
            tb=_scale(_add(_scale(f['x'],-math.sin(ub)),_scale(f['y'],math.cos(ub))),f['radius']*delta/3)
            local=[A,_add(A,ta),_sub(B,tb),B]
            for col,P in enumerate(local):
                key=leftkey if col==0 else rightkey if col==3 else ('interior',face,part,row,col)
                ids.append(intern(key,P))
        patches.append(ids)
        details.append({'patch':part,'u_range':[geometry['start_u']+delta*part,
                                               geometry['start_u']+delta*(part+1)],
                        'source_face_id':face,'source_start_edge':start['edge_curve_id'],
                        'source_end_edge':end['edge_curve_id']})
    lines=[f'// Source STEP constrained cylindrical research face #{face}; NOT APMesh accepted mesh']
    lines.extend('v '+' '.join(format(x,'.17g') for x in p) for p in points)
    lines.extend('p '+' '.join(map(str,indices)) for indices in patches)
    bp='\n'.join(lines)+'\n'
    manifest={'schema':'apmesh-s3h-source-cylinder-bicubic-v1',
              'source_face_id':face,'source_model':geometry['source_model'],
              'source_sha256':geometry['source_sha256'],
              'source_original_circle_ids':[x['edge_curve_id'] for x in geometry['original_circle_records']],
              'source_start_generator_edge':start['edge_curve_id'],
              'source_end_generator_edge':end['edge_curve_id'],
              'start_u':geometry['start_u'],'signed_sweep_rad':geometry['signed_sweep_rad'],
              'source_axial_extent_mm':[geometry['zmin'],geometry['zmax']],
              'sectors':sectors,'maximum_sector_angle_rad':abs(delta),
              'prespecified_absolute_sample_budget_mm':absolute_budget_mm,
              'patches':details,'control_keys':keys,'control_count':len(points),
              'bp_sha256':sha256(bp.encode()).hexdigest(),
              'source_native_trim_verified':False,
              'cylinder_bp_candidate_only':True,
              'complete_source_atlas':False,'apmesh_generation':'NOT_RUN'}
    return bp,manifest


def independent_audit(source_text, bp, manifest, *, model, source_sha256, grid=35):
    if grid<9 or grid%2!=1:
        raise ValueError('Independent grid must be odd and at least 9')
    if sha256(bp.encode()).hexdigest()!=manifest['bp_sha256']:
        raise ValueError('BP hash mismatch')
    if manifest['source_model'] != model or manifest['source_sha256'] != source_sha256:
        raise ValueError('Source binding mismatch')
    g=face_geometry(source_text, face_id=manifest['source_face_id'], model=model,
                    source_sha256=source_sha256,require_anchored=(model in SOURCES))
    bp_points,patches=read_bp(bp)
    if len(bp_points)!=manifest['control_count'] or len(patches)!=manifest['sectors']:
        raise ValueError('BP patch/control inventory mismatch')
    if len(manifest['control_keys'])!=len(bp_points) or len(set(manifest['control_keys']))!=len(bp_points):
        raise ValueError('Global control keys not unique')
    if g['signed_sweep_rad']!=manifest['signed_sweep_rad'] or g['start_u']!=manifest['start_u']:
        raise ValueError('Source arc disposition differs')
    if manifest['source_original_circle_ids'] != [a['edge_curve_id'] for a in g['original_circle_records']]:
        raise ValueError('Source circular edge identity was changed')
    if manifest['source_start_generator_edge'] != g['start_generator_edge'] or manifest['source_end_generator_edge'] != g['end_generator_edge']:
        raise ValueError('Source generator edge identity was changed')
    if manifest['source_axial_extent_mm'] != [g['zmin'], g['zmax']]:
        raise ValueError('Source axial interval was changed')
    if not math.isclose(manifest['maximum_sector_angle_rad'],abs(g['signed_sweep_rad'])/len(patches),rel_tol=0,abs_tol=1e-12):
        raise ValueError('Source sector angle was changed')
    if len(manifest['patches']) != len(patches):
        raise ValueError('Source segment metadata count mismatch')
    registry={key:idx for idx,key in enumerate(manifest['control_keys'])}
    for gg in g['generators']:
        for key,P in gg['controls']:
            encoded=_encode_key(key)
            if encoded not in registry:
                raise ValueError('Original generator control was not retained')
            if math.dist(bp_points[registry[encoded]],P)>1e-11:
                raise ValueError('Source generator canonical control mismatch')
    # The independent geometric oracle is an analytic native cylinder reference,
    # never the same Hermite interpolation used in construction.
    axis=g['frame']['axis'];origin=g['frame']['origin'];x=g['frame']['x'];y=g['frame']['y'];r=g['frame']['radius']
    maxerr=0.;rmssum=0.;count=0
    for i,ids in enumerate(patches):
        if len(ids)!=16 or list(ids)!=[int(x) for x in ids]:
            raise ValueError('Malformed patch control id list')
        net=[bp_points[k] for k in ids]
        for jj in range(grid):
            v=jj/(grid-1)
            z=g['zmin']+(g['zmax']-g['zmin'])*v
            for ii in range(grid):
                u=ii/(grid-1)
                theta=g['start_u']+g['signed_sweep_rad']*(i+u)/len(patches)
                radial=_add(_scale(x,math.cos(theta)),_scale(y,math.sin(theta)))
                exact=_add(_add(origin,_scale(axis,z)),_scale(radial,r))
                candidate=surface(net,u,v)
                err=math.dist(exact,candidate)
                maxerr=max(maxerr,err);rmssum+=err*err;count+=1
        if i>0:
            previous=patches[i-1]
            for row in range(4):
                if previous[4*row+3]!=ids[4*row]:
                    raise ValueError('Adjacent derived seam lacks identical global control index')
    for e,is_start in ((g['start_generator_edge'],True),(g['end_generator_edge'],False)):
        gen=next(x for x in g['generators'] if x['edge_curve_id']==e)
        patch=patches[0] if is_start else patches[-1]
        col=0 if is_start else 3
        for row,(key,P) in enumerate(gen['controls']):
            expected=registry.get(_encode_key(key))
            if patch[row*4+col]!=expected:
                raise ValueError('Original STEP generator identity not exposed on patch boundary')
    return {'schema':'apmesh-s3h-independent-cylinder-audit-v1',
            'source_face_id':g['face_id'],'source_sweep_rad_verified':g['signed_sweep_rad'],
            'original_generator_edges_checked':2,
            'derived_seams_verified':len(patches)-1,
            'independent_samples':count,
            'maximum_sampled_distance_mm':maxerr,
            'rms_sampled_distance_mm':math.sqrt(rmssum/count),
            'prespecified_budget_mm':manifest['prespecified_absolute_sample_budget_mm'],
            'sampled_budget_pass':maxerr<=manifest['prespecified_absolute_sample_budget_mm'],
            'continuous_error_bound':'NOT_CERTIFIED',
            'native_source_face_trim':'NOT_RUN',
            'apmesh_generation':'NOT_RUN'}


def run(source_path, output_dir, *, model, face_ids, sectors, absolute_budget_mm, expected_sha256=None):
    if not face_ids or len(set(face_ids)) != len(face_ids):
        raise ValueError('Face IDs must be nonempty and unique')
    raw=Path(source_path).read_bytes();digest=sha256(raw).hexdigest()
    if model in SOURCES:
        if digest!=SOURCES[model][1]:
            raise ValueError('Pinned original STEP SHA-256 mismatch')
    elif digest!=expected_sha256:
        raise ValueError('Explicit synthetic STEP SHA-256 mismatch')
    text=raw.decode('utf-8')
    output_dir=Path(output_dir)
    receipts=[];files=[]
    for face in face_ids:
        geo=face_geometry(text,face_id=face,model=model,source_sha256=digest,require_anchored=(model in SOURCES))
        bp,manifest=construct(geo,sectors=sectors,absolute_budget_mm=absolute_budget_mm)
        audit=independent_audit(text,bp,manifest,model=model,source_sha256=digest)
        receipts.append(audit)
        files.append((face,bp,manifest,audit))
    if any(not x['sampled_budget_pass'] for x in receipts):
        raise ValueError('Source-derived cylinder fit exceeds prespecified sampled budget')
    output_dir.mkdir(parents=True,exist_ok=True)
    for face,bp,manifest,audit in files:
        prefix=output_dir/f'face_{face}_segments_{sectors}'
        prefix.with_suffix('.bp').write_text(bp,encoding='utf-8')
        prefix.with_suffix('.json').write_text(json.dumps({'manifest':manifest,'audit':audit},indent=2)+'\n',encoding='utf-8')
    return receipts


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-step',required=True,type=Path)
    p.add_argument('--model',required=True,choices=(*SOURCES,'SYNTHETIC'))
    p.add_argument('--face-ids',required=True,nargs='+',type=int)
    p.add_argument('--sectors',required=True,type=int)
    p.add_argument('--absolute-budget-mm',required=True,type=float)
    p.add_argument('--expected-sha256')
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(run(a.source_step,a.output,model=a.model,face_ids=a.face_ids,
                         sectors=a.sectors,absolute_budget_mm=a.absolute_budget_mm,
                         expected_sha256=a.expected_sha256),indent=2))


if __name__=='__main__':
    main()
