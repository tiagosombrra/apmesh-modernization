#!/usr/bin/env python3
"""Fail-closed source-edge S40-F6 -> frozen S3.Y indexed BP reconciliation.

This module can assemble a candidate, but it never admits new faces on its
own. The public CLI requires original pinned STEP bytes, the frozen S3.Y BP,
explicit source-edge lineage, and independent original-native face checks.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys

from s40f6_four_face_source_island import read_indexed_bp, side_ids

SOURCE_SHA = 'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b'
S3Y_SHA = 'af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177'
F6_SHA = '72b8756c948a7a7da19c9f2a9a7099673e81a30573f19e4820abf27ba720f0a7'
F6_RECEIPT_SCHEMA = 'apmesh-s40f6-four-source-face-isolated-bp-v1'
LINEAGE_SCHEMA = 'apmesh-s40f7-original-s40-parent-edge-lineage-v1'
INTERFACE_KEYS = {
    1002: 'old:1002',
    1080: 'old:1080',
    1139: 'old:1139',
    1259: 'old:1259',
    1284: 'old:1284',
    1473: 'old:1473',
    1030: 'new:1030:0',
    1057: 'new:1057:0',
}
# The second face is the existing S3.Y owner of the source STEP edge.
SOURCE_FACE_OWNERS = {
    1002: (1279, 912), 1080: (1386, 912),
    1139: (1279, 1105), 1259: (1386, 1230),
    1284: (1279, 3737), 1473: (1386, 3737),
    1030: (3485, 912), 1057: (3269, 912),
}
FACE_IDS = (1279, 1386, 3269, 3485)
SIDE_NAMES = ('bottom', 'right', 'top', 'left')
CONTROL_COORD_TOLERANCE_MM = 1e-8


def fingerprint(text: bytes) -> str:
    """Produce a SHA-256 over the exact bytes, not normalized text."""
    return hashlib.sha256(text).hexdigest()


def _directed(patch: tuple[int, ...], side: str) -> tuple[int, ...]:
    """Convert a raw bicubic side into its CCW perimeter traversal."""
    ids = side_ids(patch, side)
    return ids[::-1] if side in ('top', 'left') else ids


def side_inventory(patches: list[tuple[int, ...]]):
    """Enumerate exact indexed control-side equivalences without tolerance weld."""
    rows = defaultdict(list)
    for pid, patch in enumerate(patches):
        if len(patch) != 16:
            raise ValueError('Malformed indexed bicubic patch')
        for side in SIDE_NAMES:
            ids = side_ids(patch, side)
            if len(set(ids)) != 4:
                raise ValueError('Collapsed or duplicated side control')
            rows[tuple(sorted(ids))].append((pid, side, ids, _directed(patch, side)))
    if any(len(users) > 2 for users in rows.values()):
        raise ValueError('Unexpected three-plus indexed sides')
    for users in rows.values():
        if len(users) == 2 and users[0][3] != users[1][3][::-1]:
            raise ValueError('Two-sided seam orientation is not reversed')
    return rows


def _match_position(a, b, *, tol=CONTROL_COORD_TOLERANCE_MM):
    if not all(math.isfinite(x) for x in a + b):
        raise ValueError('Non-finite interface control')
    return math.dist(a, b) <= tol


def isolated_gate(f6_bp: bytes, f6_receipt: dict):
    """Verify the exact delivered eight-patch island before any reindexing."""
    if fingerprint(f6_bp) != F6_SHA:
        raise ValueError('F6 byte-frozen isolated BP SHA-256 mismatch')
    if f6_receipt.get('schema') != F6_RECEIPT_SCHEMA or f6_receipt.get('bp_sha256') != F6_SHA:
        raise ValueError('F6 private sidecar not consistent with the pinned BP')
    if f6_receipt.get('step_original_sha256_reference') != SOURCE_SHA:
        raise ValueError('F6 candidate belongs to a different original STEP')
    points, patches = read_indexed_bp(f6_bp.decode('utf-8'))
    if len(points) != 104 or len(patches) != 8:
        raise ValueError('F6 source island control/patch counts changed')
    if tuple(f6_receipt.get('face_ids_per_patch', ())) != (1279, 1279, 1386, 1386, 3269, 3269, 3485, 3485):
        raise ValueError('F6 source face per patch identity has changed')
    source_segments = f6_receipt['source_segment_ids']
    if set(source_segments) != set(f6_receipt['indexed_audit']['source_boundary_segment_keys']):
        raise ValueError('F6 source boundary registration mismatched')
    rows = side_inventory(patches)
    if sum(len(users) == 2 for users in rows.values()) != 6:
        raise ValueError('Expected six internally indexed F6 seams')
    if sum(len(users) == 1 for users in rows.values()) != 20:
        raise ValueError('Expected 20 F6 source boundary sides')
    for edge, source_key in INTERFACE_KEYS.items():
        ids = tuple(source_segments.get(source_key, ()))
        if len(ids) != 4 or len(rows.get(tuple(sorted(ids)), ())) != 1:
            raise ValueError(f'Original inherited edge #{edge} is not a unique F6 open side')
    return points, patches, rows


def validate_lineage(data: dict, parent_bp: bytes):
    """Require explicit, complete, source-ID-based parent boundary provenance."""
    if data.get('schema') != LINEAGE_SCHEMA or data.get('original_step_sha256') != SOURCE_SHA:
        raise ValueError('Source identity lineage schema or original STEP SHA mismatch')
    if data.get('s3y_bp_sha256') != fingerprint(parent_bp):
        raise ValueError('Lineage source does not match the exact provided parent BP')
    raw = data.get('original_edge_to_parent_open_side')
    if not isinstance(raw, dict) or set(raw) != {str(x) for x in INTERFACE_KEYS}:
        raise ValueError('Lineage must cover exactly eight original source EDGE_CURVE IDs')
    mapping = {}
    for source_id, entry in raw.items():
        if not isinstance(entry, dict) or set(entry) != {'patch', 'side', 'original_parent_face_id'}:
            raise ValueError('Missing or ambiguous source original edge lineage entry')
        if type(entry['patch']) is not int or entry['patch'] < 0 or entry['side'] not in SIDE_NAMES:
            raise ValueError('Invalid parent patch ID or bicubic side name')
        eid = int(source_id)
        if type(entry['original_parent_face_id']) is not int or entry['original_parent_face_id'] != SOURCE_FACE_OWNERS[eid][1]:
            raise ValueError('Original source parent face owner mismatch')
        mapping[eid] = (entry['patch'], entry['side'], entry['original_parent_face_id'])
    if len(set(x[:2] for x in mapping.values())) != 8:
        raise ValueError('Two original STEP edges alias the same parent patch side')
    return mapping


def source_graph_gate(source: bytes) -> dict:
    """Check original eight source edges, native shared owners, and LINE supports.

    This is an independent original STEP graph check, *not* BRep import.
    """
    if fingerprint(source) != SOURCE_SHA:
        raise ValueError('Original S40 STEP bytes do not match the pinned source')
    import re
    entity_re = re.compile(r'#(\d+)\s*=\s*(?:([A-Z][A-Z_0-9]*)\s*\(([\s\S]*?)\)|\(([\s\S]*?)\))\s*;')
    t = {}
    for mat in entity_re.finditer(source.decode('ascii')):
        t[int(mat[1])] = (mat[2] or 'COMPLEX_ENTITY', mat[3] if mat[2] else mat[4])
    def refs(b): return [int(m) for m in re.findall(r'#(\d+)', b)]
    owners = defaultdict(set)
    face_edges = {}
    for fid, (type_name, body) in t.items():
        if type_name != 'ADVANCED_FACE':
            continue
        ids = refs(body)
        edge_list = []
        for bound in ids[:-1]:
            loop_id = refs(t[bound][1])[0]
            for oriented in refs(t[loop_id][1]):
                eid = refs(t[oriented][1])[0]
                edge_list.append(eid)
                owners[eid].add(fid)
        face_edges[fid] = edge_list
    if len(face_edges) != 43 or len(owners) != 117 or any(len(v) != 2 for v in owners.values()):
        raise ValueError('Original S40 STEP topology changed')
    for eid, expected_faces in SOURCE_FACE_OWNERS.items():
        if owners[eid] != set(expected_faces):
            raise ValueError(f'Original EDGE_CURVE #{eid} has incorrect intended face users')
        original = t[eid]
        if original[0] != 'EDGE_CURVE':
            raise ValueError(f'Original EDGE_CURVE #{eid} missing')
        curve_id = refs(original[1])[2]
        for _ in range(4):
            curve_type, curve_body = t[curve_id]
            if curve_type not in ('SURFACE_CURVE', 'SEAM_CURVE', 'INTERSECTION_CURVE'):
                break
            curve_id = refs(curve_body)[0]
        if curve_type != 'LINE':
            raise ValueError(f'Inherited source EDGE_CURVE #{eid} is not analytic LINE')
    return {'source_original_face_count': 43, 'source_original_edge_count': 117,
            'source_original_nonmanifold_edge_count': 0,
            'validated_parent_interface_source_edge_ids': sorted(INTERFACE_KEYS)}


def rebase_core(parent_points, parent_patches, child_points, child_patches,
                child_receipt, lineage, *, parent_expected_seams=None,
                parent_expected_open=None):
    """Reindex an unchanged source-derived child onto explicit parent identities.

    Only a CANDIDATE can be built: original STEP trimmed-native admission is
    deliberately an independent subsequent operation.
    """
    if len(child_points) != 104 or len(child_patches) != 8:
        raise ValueError('F6 isolated child cardinality differs')
    before = side_inventory(parent_patches)
    after_child = side_inventory(child_patches)
    if parent_expected_seams is not None:
        if sum(len(v) == 2 for v in before.values()) != parent_expected_seams:
            raise ValueError('Parent prior exact indexed seam count changed')
        if sum(len(v) == 1 for v in before.values()) != parent_expected_open:
            raise ValueError('Parent prior exact indexed open side count changed')
    if sum(len(v) == 2 for v in after_child.values()) != 6 or sum(len(v) == 1 for v in after_child.values()) != 20:
        raise ValueError('F6 child internal topology differs from isolated evidence')
    local_to_parent = {}
    resolved = []
    for eid, source_key in INTERFACE_KEYS.items():
        src_ids = tuple(child_receipt['source_segment_ids'][source_key])
        child_user = after_child.get(tuple(sorted(src_ids)), ())
        if len(child_user) != 1:
            raise ValueError('Unexpected indexed island source side incidence')
        pid, side, source_parent_face_id = lineage[eid]
        if source_parent_face_id != SOURCE_FACE_OWNERS[eid][1]:
            raise ValueError('Original STEP parent face ownership changed')
        if pid >= len(parent_patches):
            raise ValueError(f'Parent source edge #{eid} references nonexistent patch')
        parent_raw = side_ids(parent_patches[pid], side)
        parent_users = before.get(tuple(sorted(parent_raw)), ())
        if len(parent_users) != 1 or parent_users[0][:2] != (pid, side):
            raise ValueError(f'Parent source edge #{eid} is not exactly one open side')
        parent_ccw = _directed(parent_patches[pid], side)
        child_ccw = child_user[0][3]
        # Match in CCW topological orientation. Parent must oppose child.
        for child_id, parent_id in zip(child_ccw, parent_ccw[::-1]):
            if not _match_position(tuple(child_points[child_id]), tuple(parent_points[parent_id])):
                raise ValueError(f'Original source edge #{eid} has incompatible parent control geometry')
            old = local_to_parent.get(child_id)
            if old is not None and old != parent_id:
                raise ValueError(f'Original source vertex identity is split in S3.Y on edge #{eid}')
            local_to_parent[child_id] = parent_id
        resolved.append({'original_source_edge_id': eid, 'source_island_key': source_key,
                         'source_parent_patch': pid, 'source_parent_side': side,
                         'original_parent_face_id': source_parent_face_id,
                         'local_control_ids': list(child_ccw),
                         'resolved_global_control_ids': list(parent_ccw[::-1])})
    if len(local_to_parent) != 26 or len(set(local_to_parent.values())) != 26:
        raise ValueError('Unexpected inherited global control identity count; no epsilon-welding allowed')
    joined_points = list(parent_points)
    appended = []
    for i, point in enumerate(child_points):
        if i in local_to_parent:
            appended.append(local_to_parent[i])
        else:
            appended.append(len(joined_points))
            joined_points.append(tuple(point))
    joined_patches = list(parent_patches) + [tuple(appended[k] for k in p) for p in child_patches]
    if joined_patches[:len(parent_patches)] != list(parent_patches) or joined_points[:len(parent_points)] != list(parent_points):
        raise ValueError('The previously accepted parent atlas changed')
    incidence = side_inventory(joined_patches)
    before_sides = sum(len(v) == 2 for v in before.values())
    before_open = sum(len(v) == 1 for v in before.values())
    expected_internal = before_sides + 6 + 8
    expected_open = before_open + 20 - 2 * 8
    if sum(len(v) == 2 for v in incidence.values()) != expected_internal or sum(len(v) == 1 for v in incidence.values()) != expected_open:
        raise ValueError('Rebased parent and child have unexpected indexed seam/open-side counts')
    for item in resolved:
        e = item['original_source_edge_id']
        ids = tuple(item['resolved_global_control_ids'])
        users = incidence.get(tuple(sorted(ids)), ())
        if len(users) != 2 or not ({u[0] for u in users} & set(range(len(parent_patches)))):
            raise ValueError(f'Original source edge #{e} has not become a two-sided join')
    return joined_points, joined_patches, {
        'classification': 'STRUCTURAL_JOIN_CANDIDATE_NOT_NATIVE_ADMITTED',
        'source_s40_f6_child_patch_count': 8,
        'source_s40_f6_child_controls_reused_from_parent': 26,
        'source_s40_f6_child_appended_controls': 78,
        'indexed_two_sided_seams': expected_internal,
        'indexed_open_sides': expected_open,
        'original_source_interfaces_joined': resolved,
        'parent_original_patches_unchanged': True,
        'parent_original_controls_unchanged': True,
        'original_native_cad_trim_audit_executed': False,
        'new_original_source_faces_admitted': 0,
        'child_to_joined_global_control_index': appended,
    }


def serialize_bp(points, patches):
    """Write the indexed BP grammar without silently changing parent indices."""
    return '\n'.join([
        '// S40-F7 source-indexed joined CANDIDATE; NOT native admitted',
        '// No parent existing controls or patch nets were modified',
        *('v ' + ' '.join(format(v, '.17g') for v in p) for p in points),
        *('p ' + ' '.join(str(v) for v in patch) for patch in patches),
    ]) + '\n'



def discover_original_parent_lineage(source: bytes, native, original_mapping,
                                     parent_bp: bytes, parent_points, parent_patches):
    """Independently find the eight *source-identified* parent open sides.

    Original CAD edge correspondence is verified by a separate S3.S bijection.
    Native curve proximity only screens unique lineage candidates; index
    identities are reused only after the complete source chain is recovered.
    """
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from s3c_step_source_gate import parse_entities, oriented_edges
    from s40f1_six_edge_planar_builder import (
        indexed_open_sides, recover_inherited_source_chain)

    table = parse_entities(source.decode('ascii'))
    available = indexed_open_sides(parent_patches)
    if len(available) != 96:
        raise ValueError('Frozen original S3.Y parent must contain 96 open indexed sides')
    recovered = {}
    details = {}
    for eid in INTERFACE_KEYS:
        child_source_face, parent_source_face = SOURCE_FACE_OWNERS[eid]
        support, wires = oriented_edges(table, child_source_face)
        if support != 'PLANE':
            raise ValueError(f'Original child face #{child_source_face} changed support')
        entries = [e for wire in wires for e in wire if e['edge_curve_id'] == eid]
        if len(entries) != 1:
            raise ValueError(f'Original source STEP edge #{eid} has ambiguous face use')
        native_edge = original_mapping['native_edges'][original_mapping['edge_map'][eid]]
        original_native_curve = BRepAdaptor_Curve(native_edge.wrapped)
        chain = recover_inherited_source_chain(
            table, entries[0], original_native_curve, parent_points, available)
        if len(chain) != 1:
            raise ValueError(f'Original S3.Y inherited source edge #{eid} is split or ambiguous')
        pid, side, ids = chain[0]
        if tuple(sorted(ids)) != tuple(sorted(side_ids(parent_patches[pid], side))):
            raise ValueError('Recovered original source chain is not a raw parent patch side')
        recovered[str(eid)] = {'patch': pid, 'side': side,
                               'original_parent_face_id': parent_source_face}
        details[str(eid)] = {'source_child_face': child_source_face,
                             'source_parent_face': parent_source_face,
                             'recovered_segment_count': len(chain),
                             'recovered_original_edge_curve_id': eid}
    raw = {'schema': LINEAGE_SCHEMA, 'original_step_sha256': SOURCE_SHA,
           's3y_bp_sha256': fingerprint(parent_bp),
           'original_edge_to_parent_open_side': recovered}
    mapping = validate_lineage(raw, parent_bp)
    return mapping, {'source_lineage_discovery': 'ORIGINAL_STEP_NATIVE_CANDIDATE_UNIQUENESS',
                     'source_edge_details': details,
                     'source_lineage': raw}


def original_native_gate(source: bytes, step_path, joined_points, joined_patches,
                         f6_receipt: dict, report: dict, *,
                         preimported_native=None, preverified_mapping=None):
    """Audit all four patches groups on the ORIGINAL imported trimmed STEP faces.

    The verified source/native edge and face bijection is independently supplied
    by S3.S; analytic reconstructed surrogate faces cannot enter this routine.
    """
    if fingerprint(source) != SOURCE_SHA:
        raise ValueError('Native audit source is not byte-pinned S40 original')
    import cadquery as cq
    from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
    from OCP.BRepClass import BRepClass_FaceClassifier
    from OCP.ElSLib import ElSLib
    from OCP.TopAbs import TopAbs_IN, TopAbs_ON
    from OCP.gp import gp_Pnt, gp_Pnt2d
    from audit_analytic_bp import surface
    from s3s_full_original_face_census import full_correspondence
    from s3y_s40_curved_planar_rings import audit_native_patch_coverage
    from s40f1_six_edge_planar_builder import (
        check_curve_fit, native_curve_to_bezier_chain_distance)

    native = preimported_native or cq.importers.importStep(str(step_path)).val()
    native_mapping = preverified_mapping or full_correspondence(source.decode('ascii'), native)
    expected_faces = tuple(f6_receipt['face_ids_per_patch'])
    if expected_faces != (1279, 1279, 1386, 1386, 3269, 3269, 3485, 3485):
        raise ValueError('Source patch-face ownership changes in native audit')
    groups = {}
    for k, fid in enumerate(expected_faces):
        groups.setdefault(fid, []).append(joined_patches[156 + k])
    all_in, all_bound, max_plane = 0, 0, 0.0
    per_face = {}
    for joined_edge in report['original_source_interfaces_joined']:
        source_parent_face = joined_edge['original_parent_face_id']
        parent_patch_index = joined_edge['source_parent_patch']
        parent_patch_side = joined_edge['source_parent_side']
        native_owner = native.Faces()[native_mapping['face_map'][source_parent_face]]
        native_support = BRepAdaptor_Surface(native_owner.wrapped)
        coord = {'bottom': (0.5, 0.1), 'right': (0.9, 0.5),
                 'top': (0.5, 0.9), 'left': (0.1, 0.5)}[parent_patch_side]
        original_parent_patch = joined_patches[parent_patch_index]
        parent_sample = surface([joined_points[i] for i in original_parent_patch], *coord)
        if native_support.GetType() == GeomAbs_Plane:
            analytic_surface = native_support.Plane()
            uv = ElSLib.Parameters_s(analytic_surface, gp_Pnt(*parent_sample))
            support_dev = analytic_surface.Distance(gp_Pnt(*parent_sample))
            if support_dev >= 1e-7:
                raise ValueError('Claimed original source parent patch is not on its native plane')
        elif native_support.GetType() == GeomAbs_Cylinder:
            analytic_surface = native_support.Cylinder()
            uv = ElSLib.Parameters_s(analytic_surface, gp_Pnt(*parent_sample))
            p0 = analytic_surface.Location().Coord()
            axis = analytic_surface.Axis().Direction().Coord()
            delta = tuple(parent_sample[i] - p0[i] for i in range(3))
            vdot = sum(delta[i]*axis[i] for i in range(3))
            rho = math.sqrt(sum((delta[i] - vdot*axis[i])**2 for i in range(3)))
            if abs(rho - analytic_surface.Radius()) >= 0.001:
                raise ValueError('Claimed original source parent patch leaves native cylinder support')
        else:
            raise ValueError('Unsupported native parent support for original source edge lineage')
        if BRepClass_FaceClassifier(native_owner.wrapped, gp_Pnt2d(*uv), 1e-7).State() != TopAbs_IN:
            raise ValueError('Claimed source parent patch is outside its original native owner face')
    for fid in FACE_IDS:
        native_face = native.Faces()[native_mapping['face_map'][fid]]
        plane = BRepAdaptor_Surface(native_face.wrapped).Plane()
        result = audit_native_patch_coverage(native_face, joined_points, groups[fid])
        inside, boundary = 0, 0
        for patch in groups[fid]:
            control = [joined_points[k] for k in patch]
            for i in range(15):
                for j in range(15):
                    p = surface(control, (i + 0.5) / 15, (j + 0.5) / 15)
                    uv = ElSLib.Parameters_s(plane, gp_Pnt(*p))
                    state = BRepClass_FaceClassifier(
                        native_face.wrapped, gp_Pnt2d(*uv), 1e-7).State()
                    if state != TopAbs_IN:
                        raise ValueError(f'Original STEP native trim interior rejects face #{fid}')
                    inside += 1
                    max_plane = max(max_plane, plane.Distance(gp_Pnt(*p)))
            for label in SIDE_NAMES:
                ids = side_ids(patch, label)
                for j in range(51):
                    u = j / 50
                    a = [joined_points[k] for k in ids]
                    p = tuple((1-u)**3 * a[0][q] + 3*u*(1-u)**2 * a[1][q]
                              + 3*u*u*(1-u) * a[2][q] + u**3 * a[3][q]
                              for q in range(3))
                    uv = ElSLib.Parameters_s(plane, gp_Pnt(*p))
                    state = BRepClass_FaceClassifier(
                        native_face.wrapped, gp_Pnt2d(*uv), 1e-7).State()
                    if state not in (TopAbs_IN, TopAbs_ON):
                        raise ValueError(f'Original STEP native trim boundary rejects face #{fid}')
                    boundary += 1
        all_in += inside
        all_bound += boundary
        per_face[str(fid)] = dict(result, interior_IN=inside,
                                  boundary_IN_or_ON=boundary, boundary_OUT=0)
    if all_in != 1800 or all_bound != 1632 or max_plane > 1e-7:
        raise ValueError('Original native plane or trimmed sample coverage gate failed')

    local_to_joined = report['child_to_joined_global_control_index']
    curve_groups = defaultdict(list)
    max_curve = 0.0
    for source_key, old_ids in f6_receipt['source_segment_ids'].items():
        eid = int(source_key.split(':')[1])
        native_edge = native_mapping['native_edges'][native_mapping['edge_map'][eid]]
        curve = BRepAdaptor_Curve(native_edge.wrapped)
        ids = tuple(local_to_joined[k] for k in old_ids)
        net = tuple(joined_points[i] for i in ids)
        deviation, ok = check_curve_fit(joined_points, ids, curve,
                                        samples=25, limit=0.001)
        if not ok:
            raise ValueError(f'Original native EDGE_CURVE #{eid} budget exceeded')
        max_curve = max(max_curve, deviation)
        curve_groups[eid].append(net)
    for eid, pieces in curve_groups.items():
        native_edge = native_mapping['native_edges'][native_mapping['edge_map'][eid]]
        curve = BRepAdaptor_Curve(native_edge.wrapped)
        inverse = native_curve_to_bezier_chain_distance(curve, pieces, samples=65)
        if inverse >= 0.001:
            raise ValueError(f'Original native EDGE_CURVE #{eid} inverse coverage exceeded')
        max_curve = max(max_curve, inverse)
    return {
        'status': 'PASS_SAMPLED_ORIGINAL_NATIVE_GATES',
        'source_byte_hash_verified': True,
        'source_native_brep_import_and_unique_face_correspondence': True,
        'source_faces_checked': list(FACE_IDS),
        'original_native_interior_IN': all_in,
        'original_native_boundary_IN_or_ON': all_bound,
        'original_native_boundary_OUT': 0,
        'max_native_plane_distance_mm': max_plane,
        'max_sampled_bidirectional_original_edge_distance_mm': max_curve,
        'original_native_boundary_edge_ids_checked': sorted(curve_groups),
        'original_cad_continuous_hausdorff_certified': False,
        'apmesh_cpp_tri_quad_executed': False,
        'native_face_reports': per_face,
    }


def prepare_private_trial(original_step_path, s3y_bp_path, lineage_path,
                          f6_bp_path, f6_receipt_path):
    """Load all pinned real inputs; reject missing ones without producing a BP."""
    source = Path(original_step_path).read_bytes()
    parent = Path(s3y_bp_path).read_bytes()
    child = Path(f6_bp_path).read_bytes()
    receipt = json.loads(Path(f6_receipt_path).read_text())
    lineages = json.loads(Path(lineage_path).read_text()) if lineage_path else None
    source_record = source_graph_gate(source)
    if fingerprint(parent) != S3Y_SHA:
        raise ValueError('Frozen accepted S3.Y BP SHA-256 mismatch')
    parent_points, parent_patches = read_indexed_bp(parent.decode('utf-8'))
    if len(parent_points) != 1665 or len(parent_patches) != 156:
        raise ValueError('Frozen 156-patch S3.Y source baseline cardinality changed')
    child_points, child_patches, _ = isolated_gate(child, receipt)
    native_preloaded = None
    original_mapping = None
    if lineages is None:
        import cadquery as cq
        from s3s_full_original_face_census import full_correspondence
        native_preloaded = cq.importers.importStep(str(original_step_path)).val()
        original_mapping = full_correspondence(source.decode('ascii'), native_preloaded)
        actual_lineage, lineage_report = discover_original_parent_lineage(
            source, native_preloaded, original_mapping, parent,
            parent_points, parent_patches)
    else:
        actual_lineage = validate_lineage(lineages, parent)
        lineage_report = {'source_lineage_discovery': 'EXPLICIT_LINEAGE_NATIVE_OWNER_AUDIT_REQUIRED'}
    joined_points, joined_patches, report = rebase_core(
        parent_points, parent_patches, child_points, child_patches, receipt,
        actual_lineage, parent_expected_seams=264, parent_expected_open=96)
    if (len(joined_points), len(joined_patches)) != (1743, 164):
        raise ValueError('Source parent/child candidate cardinality changed')
    report.update(source_record)
    native = original_native_gate(
        source, original_step_path, joined_points, joined_patches, receipt, report,
        preimported_native=native_preloaded, preverified_mapping=original_mapping)
    report.update(lineage_report)
    report['original_native_audit'] = native
    report['original_native_cad_trim_audit_executed'] = True
    report['original_parent_bp_sha256'] = S3Y_SHA
    report['isolated_child_bp_sha256'] = F6_SHA
    return serialize_bp(joined_points, joined_patches), report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-step', required=True)
    parser.add_argument('--s3y-bp', required=True)
    parser.add_argument('--parent-source-lineage', default=None,
                        help='Optional independent original-edge lineage; omit to discover it from native CAD')
    parser.add_argument('--island-f6-bp', required=True)
    parser.add_argument('--island-f6-receipt', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    try:
        candidate, report = prepare_private_trial(
            args.original_step, args.s3y_bp, args.parent_source_lineage,
            args.island_f6_bp, args.island_f6_receipt)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as error:
        print(json.dumps({'classification': 'BLOCKED_NO_NATIVE_ADMISSION',
                          'reason': type(error).__name__ + ': ' + str(error),
                          'candidate_bp_emitted': False,
                          'new_original_source_faces_admitted': 0}), file=sys.stderr)
        return 3
    # Source-indexed controls are structural only: the native trim/curve gate
    # is still necessary before any candidate may be promoted to admitted.
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / 's40f7_s40_source_joined.CANDIDATE.bp').write_text(candidate)
    (out / 's40f7_structural_join_receipt.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'classification': report['classification'],
                      'indexed_patch_count': 164,
                      'previously_admitted_source_faces': 22,
                      'original_native_trim_audit_executed': True,
                      'original_native_audit_status': report['original_native_audit']['status'],
                      'apmesh_tri_quad_executed': False}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
