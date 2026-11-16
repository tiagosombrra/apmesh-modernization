#!/usr/bin/env python3
"""Original S40 bounded second-ring partial BP and independent native audits.

Only four original, native 4-sided cylindrical faces are admitted. Complex
S40 cylinders remain excluded. This never creates a complete model or mesh.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq

from audit_analytic_bp import read_bp, surface
from original_cad_planar_atlas import native_distance, same_index
from s3c_step_source_gate import SOURCES, coordinates, entity, oriented_edges, parse_entities, refs
from s3e_native_feature_bijection import correlate, verify_certificate
from s3f_first_ring_native_faces import first_ring, recompute_audit
from s3h_source_cylinder_bp import construct as cylinder_construct, face_geometry
from s3i_joint_source_atlas import _linear_controls, _serialize
from s3j_radial_support_enclosure import certify_patch
from s3k_native_uv_trim_gate import classify_patch


S40_CYLINDER_FACES = (2882, 2936, 2990, 3127)
EXPECTED_S40_SOURCE_FACES = 43
# STEP 3D CIRCLE and 2D generator PCURVE endpoints differ at finite precision.
# This angular *source-consistency* tolerance is distinct from the 0.001-mm
# approximation budget and is checked before any geometry is built.
SOURCE_3D_2D_ANGLE_CLOSURE_TOLERANCE_RAD = 1e-8


def _pcurve_constrained_geometry(original):
    """Use actual STEP generator PCURVE endpoints after checking 3D arc orientation."""
    generators = {g['edge_curve_id']: g for g in original['generators']}
    start = generators[original['start_generator_edge']]['u']
    end = generators[original['end_generator_edge']]['u']
    source_sweep = original['signed_sweep_rad']
    raw_difference = end - start
    turns = round((source_sweep - raw_difference) / (2 * math.pi))
    adjusted_sweep = raw_difference + turns * 2 * math.pi
    closure = adjusted_sweep - source_sweep
    if abs(closure) > SOURCE_3D_2D_ANGLE_CLOSURE_TOLERANCE_RAD:
        raise ValueError('Original CIRCLE and generator PCURVE angular closure mismatch')
    if source_sweep * adjusted_sweep <= 0:
        raise ValueError('Original directed CIRCLE and PCURVE have opposite winding')
    geometry = {**original, 'signed_sweep_rad': adjusted_sweep}
    return geometry, {
        'source_face_id': original['face_id'],
        'signed_original_3d_circle_sweep_rad': source_sweep,
        'signed_generator_pcurve_sweep_rad': adjusted_sweep,
        'absolute_original_3d_2d_angular_closure_residual_rad': abs(closure),
        'predeclared_3d_2d_closure_tolerance_rad': SOURCE_3D_2D_ANGLE_CLOSURE_TOLERANCE_RAD,
        'alignment': 'SOURCE_GENERATOR_PCURVE_ANGULAR_ENDPOINTS_WITH_3D_CIRCLE_WINDING',
    }



def _source_identity(step_text, *, model, source_sha256):
    if model != 'S40' or source_sha256 != SOURCES['S40'][1]:
        raise ValueError('S3.L only admits the pinned original S40 model')
    if sha256(step_text.encode('utf-8')).hexdigest() != source_sha256:
        raise ValueError('Original STEP SHA-256 mismatch')


def _native_source_edge(native_faces, native_edges, source_table, source_edge_id,
                        source_face_indices, tolerance):
    """Require the same TopoDS edge on both faces, never coordinate welding."""
    _, raw = entity(source_table, source_edge_id, 'EDGE_CURVE')
    start, end = refs(raw)[:2]
    expected = (coordinates(source_table, start), coordinates(source_table, end))
    resolved = []
    for native_face_id in source_face_indices:
        candidates = []
        for edge in native_faces[native_face_id].Edges():
            if edge.geomType() != 'LINE' or len(edge.Vertices()) != 2:
                continue
            points = [tuple(float(q) for q in (v.Center().x, v.Center().y, v.Center().z))
                      for v in edge.Vertices()]
            if (all(math.dist(points[i], expected[i]) <= tolerance for i in (0, 1))
                    or all(math.dist(points[i], expected[1-i]) <= tolerance for i in (0, 1))):
                edge_id = same_index(native_edges, edge)
                if edge_id is None:
                    raise ValueError('Source edge not present in native graph')
                candidates.append(edge_id)
        if len(candidates) != 1:
            raise ValueError('Ambiguous or missing original/native EDGE_CURVE correspondence')
        resolved.append(candidates[0])
    if len(set(resolved)) != 1:
        raise ValueError('Two source faces do not share the same native TopoDS_Edge')
    return resolved[0]


def _source_prerequisites(step_text, native_shape, *, model, source_sha256):
    _source_identity(step_text, model=model, source_sha256=source_sha256)
    cert = correlate(step_text, native_shape, model=model, source_sha256=source_sha256)
    verify_certificate(step_text, native_shape, cert,
                       model=model, source_sha256=source_sha256)
    ring = first_ring(step_text, native_shape, cert,
                      model=model, source_sha256=source_sha256)
    recompute_audit(step_text, native_shape, ring,
                    model=model, source_sha256=source_sha256)
    planar = {entry['step_advanced_face_id']: entry['native_face_index']
              for entry in cert['candidate_bindings']}
    neighbors = {entry['source_advanced_face_id']: entry['native_face_index']
                 for entry in ring['excluded_face_mapping']}
    if len(planar) != 9 or len(native_shape.Faces()) != EXPECTED_S40_SOURCE_FACES:
        raise ValueError('Original S40 frozen source/native face census changed')
    for fid in S40_CYLINDER_FACES:
        if fid not in neighbors or native_shape.Faces()[neighbors[fid]].geomType() != 'CYLINDER':
            raise ValueError(f'Original S40 source face #{fid} lacks verified native cylinder binding')
    return cert, ring, planar, neighbors


def construct_partial(step_text, native_shape, *, model, source_sha256,
                      sectors=4, sampled_budget_mm=.001):
    """Merge all S40 eligible source planar faces and four bounded cylinders."""
    if not isinstance(sectors, int) or not 1 <= sectors <= 64:
        raise ValueError('Sector count must be an integer in [1,64]')
    if not math.isfinite(sampled_budget_mm) or sampled_budget_mm <= 0:
        raise ValueError('Budget must be finite and positive')
    cert, ring, planar, neighbors = _source_prerequisites(
        step_text, native_shape, model=model, source_sha256=source_sha256)
    source_table = parse_entities(step_text)
    source_interface_by_face = defaultdict(set)
    for entry in cert['boundary_interfaces']:
        source_interface_by_face[entry['source_neighbor_face_id']].add(
            entry['source_edge_curve_id'])
    points, keys_to_ids, labels, patches, source_face_edges = [], {}, [], [], defaultdict(set)
    pcurve_alignment = []

    def intern(key, point):
        coord = tuple(map(float, point))
        if not all(math.isfinite(x) for x in coord):
            raise ValueError('Nonfinite source control')
        if key in keys_to_ids:
            index = keys_to_ids[key]
            if math.dist(points[index], coord) > 1e-9:
                raise ValueError('A source-identified control was reused with incompatible geometry')
            return index
        index = len(points)
        keys_to_ids[key] = index
        points.append(coord)
        return index

    for fid, native_idx in sorted(planar.items()):
        support, wires = oriented_edges(source_table, fid)
        if support != 'PLANE' or len(wires) != 1:
            raise ValueError('Original eligible planar face changed')
        _, net, names = _linear_controls(source_table, wires[0])
        names = [name if name is not None else f'planar_interior:{fid}:{i}'
                 for i, name in enumerate(names)]
        ids = [intern(name, point) for name, point in zip(names, net)]
        patches.append(ids)
        labels.append({'kind': 'SOURCE_EXACT_PLANAR_QUAD',
                       'source_face_id': fid, 'source_native_face_index': native_idx,
                       'local_segment': 0, 'control_vertex_ids': ids})
        source_face_edges[fid].update(x['edge_curve_id'] for x in wires[0])

    for fid in S40_CYLINDER_FACES:
        geo = face_geometry(step_text, face_id=fid, model=model,
                            source_sha256=source_sha256, require_anchored=False)
        geo, alignment = _pcurve_constrained_geometry(geo)
        pcurve_alignment.append(alignment)
        if len(source_interface_by_face[fid] &
               {x['edge_curve_id'] for x in geo['generators']}) != 1:
            raise ValueError('S40 cylinder requires exactly one source-to-planar generator anchor')
        bp, local_manifest = cylinder_construct(
            geo, sectors=sectors, absolute_budget_mm=sampled_budget_mm)
        locals_xyz, locals_patches = read_bp(bp)
        global_indices = [intern(key, coord) for key, coord in
                          zip(local_manifest['control_keys'], locals_xyz)]
        for segment, local_ids in enumerate(locals_patches):
            ids = [global_indices[k] for k in local_ids]
            patches.append(ids)
            labels.append({'kind': 'SOURCE_CYLINDER_APPROX_CANDIDATE',
                           'source_face_id': fid,
                           'source_native_face_index': neighbors[fid],
                           'local_segment': segment, 'control_vertex_ids': ids})
        source_face_edges[fid].update(x['edge_curve_id'] for x in geo['generators'])

    original_edge_owners = defaultdict(list)
    for fid, edges in source_face_edges.items():
        for eid in edges:
            original_edge_owners[eid].append(fid)
    shared = []
    faces = native_shape.Faces()
    edges = native_shape.Edges()
    global_ids = {**planar, **neighbors}
    tolerance = max(1e-8, native_shape.BoundingBox().DiagonalLength * 1e-9)
    for eid, owners in sorted(original_edge_owners.items()):
        if len(owners) > 2:
            raise ValueError('Original S40 model unexpectedly has three admitted face owners')
        if len(owners) != 2:
            continue
        original, original_end = refs(entity(source_table, eid, 'EDGE_CURVE')[1])[:2]
        names = [f'vertex:{original}', f'edge:{eid}:1',
                 f'edge:{eid}:2', f'vertex:{original_end}']
        if any(name not in keys_to_ids for name in names):
            raise ValueError('Shared STEP edge is not represented by canonical controls')
        ids = [keys_to_ids[name] for name in names]
        for owner in owners:
            participating = [p for p, label in zip(patches, labels)
                             if label['source_face_id'] == owner]
            if not participating or not set(ids).issubset(
                    set(i for patch in participating for i in patch)):
                raise ValueError('Shared source feature missing from an incident BP face')
        native_eid = _native_source_edge(faces, edges, source_table, eid,
                                         [global_ids[owner] for owner in owners], tolerance)
        shared.append({'source_edge_curve_id': eid,
                       'source_face_ids': sorted(owners),
                       'source_native_face_indices': [global_ids[i] for i in sorted(owners)],
                       'native_topods_edge_index': native_eid,
                       'shared_global_control_ids': ids})

    output_bp = _serialize(points, patches)
    report = {
        'schema': 'apmesh-s3l-s40-original-partial-second-ring-bp-v1',
        'source_model': model, 'source_sha256': source_sha256,
        'original_faces': EXPECTED_S40_SOURCE_FACES,
        'admitted_planar_faces': len(planar),
        'admitted_cylinder_faces': len(S40_CYLINDER_FACES),
        'excluded_unrepresented_faces': EXPECTED_S40_SOURCE_FACES - len(planar) - len(S40_CYLINDER_FACES),
        'cylinder_face_ids': list(S40_CYLINDER_FACES),
        'sectors_per_cylinder': sectors, 'experimental_sampled_budget_mm': sampled_budget_mm,
        'patch_count': len(patches), 'control_count': len(points),
        'shared_original_edge_count': len(shared),
        'shared_original_edges': shared,
        'source_3d_circle_2d_pcurve_alignment': pcurve_alignment,
        'candidate_bindings': cert['certificate_sha256'],
        'first_ring_bindings': ring['report_sha256'],
        'control_key_to_id': keys_to_ids, 'patches': labels,
        'bp_sha256': sha256(output_bp.encode('utf-8')).hexdigest(),
        'complex_trimmed_S40_cylinders_admitted': False,
        'cylinder_original_curved_boundary_fit': 'NOT_RUN',
        'complete_original_S40_atlas': False,
        'accepted_apmesh_tri_quad': 'NOT_RUN',
        'genuine_external_nonmanifold_positive': 'NOT_ESTABLISHED',
    }
    return output_bp, report


def audit_native(step_text, native_shape, bp, manifest, *, model, source_sha256,
                 declared_budget_mm, interior_grid=9, boundary_grid=11):
    """Fail closed on source changes, fake identities, and trimmed UV violations."""
    _source_identity(step_text, model=model, source_sha256=source_sha256)
    if sha256(bp.encode('utf-8')).hexdigest() != manifest.get('bp_sha256'):
        raise ValueError('BP digest mismatch')
    if not math.isfinite(declared_budget_mm) or declared_budget_mm <= 0:
        raise ValueError('Independent geometric budget invalid')
    if declared_budget_mm != manifest.get('experimental_sampled_budget_mm'):
        raise ValueError('Post-hoc widening of geometric budget forbidden')
    # Reconstruct the entire canonical source graph and metadata rather than
    # trusting a manipulated sidecar with a recomputed checksum.
    expected_bp, expected_report = construct_partial(
        step_text, native_shape, model=model, source_sha256=source_sha256,
        sectors=manifest['sectors_per_cylinder'],
        sampled_budget_mm=declared_budget_mm)
    if bp != expected_bp or manifest != expected_report:
        raise ValueError('Original S40 BP/manifest disagrees with source recomputation')
    vertices, patch_ids = read_bp(bp)
    if len(patch_ids) != len(manifest['patches']) or len(vertices) != manifest['control_count']:
        raise ValueError('Indexed BP source inventory mismatch')
    planar_max, cylinder_max, radial_max = 0., 0., 0.
    native_faces = native_shape.Faces()
    internal, boundary = 0, 0
    byface = defaultdict(list)
    for indices, label in zip(patch_ids, manifest['patches']):
        face = native_faces[label['source_native_face_index']]
        if list(indices) != label['control_vertex_ids']:
            raise ValueError('BP global controls do not match source patches')
        if label['kind'] == 'SOURCE_EXACT_PLANAR_QUAD':
            for row in range(5):
                for col in range(5):
                    point = surface([vertices[i] for i in indices], col/4, row/4)
                    planar_max = max(planar_max, native_distance(face, point))
        else:
            fid = label['source_face_id']
            geom = face_geometry(step_text, face_id=fid, model=model,
                                 source_sha256=source_sha256, require_anchored=False)
            geom, _ = _pcurve_constrained_geometry(geom)
            bounded = certify_patch(vertices, indices, geom,
                                    label['local_segment'], manifest['sectors_per_cylinder'])
            radial_max = max(radial_max, bounded['radial_support_error_upper_mm'])
            if bounded['radial_support_error_upper_mm'] > declared_budget_mm:
                raise ValueError('Cylinder Bernstein support exceeds predeclared budget')
            trimmed = classify_patch(face, vertices, indices,
                                     interior_grid=interior_grid,
                                     boundary_grid=boundary_grid,
                                     distance_budget_mm=declared_budget_mm)
            cylinder_max = max(cylinder_max,
                               trimmed['max_native_cylinder_projection_distance_mm'])
            internal += trimmed['interior_sample_count']
            boundary += trimmed['boundary_sample_count']
            byface[fid].append(trimmed)
    if planar_max > 1e-7:
        raise ValueError('Original S40 planar native distance exceeds tolerance')
    for fid, entries in byface.items():
        bounds = entries[0]['native_trim_bounds_uv']
        recorded = [a['observed_patch_uv_bounds'] for a in entries]
        extrema = (min(a[0] for a in recorded), max(a[1] for a in recorded),
                   min(a[2] for a in recorded), max(a[3] for a in recorded))
        if any(abs(a-b)>1e-5 for a,b in zip(bounds,extrema)):
            raise ValueError('S40 admitted cylinder patches do not cover native UV bounds')
    return {
        'schema': 'apmesh-s3l-s40-native-trim-and-boundary-sampled-audit-v1',
        'original_S40_raw_sha256_verified': source_sha256,
        'original_source_faces': manifest['original_faces'],
        'admitted_planar_source_faces': manifest['admitted_planar_faces'],
        'admitted_cylinder_source_faces': manifest['admitted_cylinder_faces'],
        'partial_bp_patch_count': len(patch_ids),
        'global_control_count': len(vertices),
        'shared_original_source_edges_native_IsSame': len(manifest['shared_original_edges']),
        'globally_reused_original_source_control_ids': 4 * len(manifest['shared_original_edges']),
        'original_cylinders_independent_native_uv_interior_samples': internal,
        'original_cylinders_independent_native_uv_boundary_samples': boundary,
        'max_sampled_planar_native_face_distance_mm': planar_max,
        'max_sampled_cylinder_native_projection_distance_mm': cylinder_max,
        'max_guarded_bernstein_radial_support_mm': radial_max,
        'predeclared_budget_mm': declared_budget_mm,
        'native_trim_scope': 'DISCRETE_BREPCLASS_WITH_PERIODIC_U_AND_BERNSTEIN_FLOAT_GUARD',
        'continuous_trimmed_surface_equivalence_certified': False,
        'complex_S40_first_ring_cylinders': 'EXCLUDED_FROM_BP',
        'original_model_full_patch_coverage': False,
        'apmesh_tri_quad': 'NOT_RUN',
        'original_three_plus_incident_source': 'NOT_ESTABLISHED',
        'audit_pass': True,
    }


def run(step_file, output_dir, *, sectors=4, budget_mm=.001):
    source_path = Path(step_file)
    raw = source_path.read_bytes()
    digest = sha256(raw).hexdigest()
    if digest != SOURCES['S40'][1]:
        raise ValueError('S40 raw source SHA-256 differs from frozen reference')
    step_text = raw.decode('utf-8')
    imported = cq.importers.importStep(str(source_path)).val()
    bp, report = construct_partial(step_text, imported, model='S40',
                                    source_sha256=digest, sectors=sectors,
                                    sampled_budget_mm=budget_mm)
    audit = audit_native(step_text, imported, bp, report, model='S40',
                         source_sha256=digest, declared_budget_mm=budget_mm)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out/'s40_second_ring.partial.bp').write_text(bp, encoding='utf-8')
    (out/'s40_second_ring_manifest.json').write_text(
        json.dumps(report, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    (out/'s40_second_ring_native_audit.json').write_text(
        json.dumps(audit, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    return report, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-step', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sectors', type=int, default=4)
    parser.add_argument('--budget-mm', type=float, default=.001)
    args = parser.parse_args()
    report, audit = run(args.source_step, args.output,
                        sectors=args.sectors, budget_mm=args.budget_mm)
    print(json.dumps({'model': report['source_model'],
                      'patches': report['patch_count'],
                      'controls': report['control_count'],
                      'shared_source_edges': report['shared_original_edge_count'],
                      'sampled_native_distance_mm': audit['max_sampled_cylinder_native_projection_distance_mm'],
                      'status': 'S40_PARTIAL_EXPERIMENTAL_ONLY'}, sort_keys=True))


if __name__ == '__main__':
    main()
