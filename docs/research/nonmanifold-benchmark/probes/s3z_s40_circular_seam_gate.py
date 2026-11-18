#!/usr/bin/env python3
"""S3.Z: fail-closed two-sided repair trials for original S40 circular seams.

Requires the authorized original STEP, the SHA-pinned S3.W private BP, and the
published S3.Y source-backed builder. Candidate geometry is private; no C++ or
APMesh TRI/QUAD meshing is performed by this module.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from hashlib import sha256
from pathlib import Path

# The code is intentionally imported on demand so syntax/unit contracts can be
# checked without redistributing or loading the original third-party CAD.

ORIGINAL_STEP_SHA = "b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b"
S3W_PARENT_SHA = "c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174"
S3Y_SELECTED_SHA = "af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177"
TARGET_FACES = (1827, 1907)
TARGET_CIRCLES = {1827: (1523, 252, 1834, 1886), 1907: (1911, 1962, 326, 1593)}
# A coordinate displacement is NOT an error tolerance. Every trial still uses
# the previously declared source geometry budget of 0.001 mm.
FIXED_BUDGET_MM = 0.001
TRIAL_BIASES_MM = (0.0, .0002, .0004, .0006, .0008, .0010, .0012, .0014)


def check_input_hashes(source: bytes, parent: bytes, *, budget_mm: float = FIXED_BUDGET_MM) -> None:
    """Require exact source and immutable frozen-parent bytes."""
    if budget_mm != FIXED_BUDGET_MM:
        raise ValueError("The original pilot geometry budget cannot be modified")
    if sha256(source).hexdigest() != ORIGINAL_STEP_SHA:
        raise ValueError("Original STEP SHA-256 mismatch")
    if sha256(parent).hexdigest() != S3W_PARENT_SHA:
        raise ValueError("S3.W parent BP SHA-256 mismatch")


def unit(v):
    """Normalize a 3-vector with an explicit degeneracy gate."""
    norm = math.sqrt(sum(x*x for x in v))
    if not math.isfinite(norm) or norm < 1e-14:
        raise ValueError("Degenerate or non-finite source tangent")
    return tuple(x / norm for x in v)


def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def bernstein_point(pts, ids, t):
    weights = ((1-t)**3, 3*t*(1-t)**2, 3*t*t*(1-t), t**3)
    return tuple(sum(weights[k]*pts[ids[k]][j] for k in range(4)) for j in range(3))


def control_bias_directions(points, ids, normal, inward_test, *, probe_mm=0.01):
    """Return per-control inward directions determined by native trim sidedness.

    inward_test is a function(point) -> boolean indicating native TopAbs_IN.
    Both sides must differ; an ambiguous classifier is a hard failure.
    """
    directions = []
    for j in (1,2):
        t = j/3
        p1 = bernstein_point(points, ids, t-1e-4)
        p2 = bernstein_point(points, ids, t+1e-4)
        tangent = unit(tuple(p2[k]-p1[k] for k in range(3)))
        direction = unit(cross(normal,tangent))
        center = bernstein_point(points, ids, .5)
        positive = inward_test(tuple(center[k]+probe_mm*direction[k] for k in range(3)))
        negative = inward_test(tuple(center[k]-probe_mm*direction[k] for k in range(3)))
        if positive == negative:
            raise ValueError("Ambiguous inward direction on original trimmed face")
        if negative:
            direction = tuple(-x for x in direction)
        directions.append(direction)
    return tuple(directions)


def coons_interior(net_edges):
    """Return exact degree-three Coons net preserving all four cubic boundaries.

    Edges are supplied in the oriented order: bottom left->right,
    right bottom->top, top right->left, left top->bottom.
    """
    g = [[None for _ in range(4)] for _ in range(4)]
    for c,p in enumerate(net_edges[0]):g[0][c] = tuple(p)
    for r,p in enumerate(net_edges[1]):g[r][3] = tuple(p)
    for c,p in enumerate(reversed(net_edges[2])):g[3][c] = tuple(p)
    for r,p in enumerate(reversed(net_edges[3])):g[r][0] = tuple(p)
    for r in (1,2):
        s=r/3
        for c in (1,2):
            t=c/3
            bilinear=tuple((1-s)*((1-t)*g[0][0][k]+t*g[0][3][k]) +
                           s*((1-t)*g[3][0][k]+t*g[3][3][k]) for k in range(3))
            g[r][c]=tuple((1-t)*g[r][0][k]+t*g[r][3][k] +
                            (1-s)*g[0][c][k]+s*g[3][c][k]-bilinear[k]
                            for k in range(3))
    return tuple(tuple(x for x in row) for row in g)


def compose_controls(original, patches, moved, *, first_new=156):
    """Update shared controls and re-evaluate only new planar Coons interiors.

    Previous 156 source-indexed patches preserve topology; the 156-patch
    geometry may change only at the explicitly audited prior shared IDs.
    """
    from s3r_s40_conforming_hole_join import _side

    points=list(original)
    for idx,new_xyz in moved.items():
        if not 0 <= idx < len(original):
            raise ValueError("A moved shared-control index does not exist")
        points[idx]=tuple(new_xyz)
    reinterior=set()
    for patch in patches[first_new:]:
        bounds = [tuple(points[i] for i in _side(patch, name)) for name in ("bottom","right","top","left")]
        # Convert top/left orientation to the source Coons boundary convention.
        net=coons_interior((bounds[0],bounds[1],bounds[2][::-1],bounds[3][::-1]))
        for r in (1,2):
            for c in (1,2):
                idx=patch[4*r+c]
                if idx in moved or idx in reinterior:
                    raise ValueError("New planar interiors overlap shared boundary controls")
                reinterior.add(idx)
                points[idx]=net[r][c]
    return points,reinterior


def _sample_native_trim(face, point):
    """Check a point against a real native plane/cylinder trimmed TopoDS_Face."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepClass import BRepClass_FaceClassifier
    from OCP.ElSLib import ElSLib
    from OCP.TopAbs import TopAbs_IN, TopAbs_ON
    from OCP.gp import gp_Pnt, gp_Pnt2d

    adaptor=BRepAdaptor_Surface(face.wrapped)
    kind=face.geomType()
    if kind=="PLANE":uv=ElSLib.Parameters_s(adaptor.Plane(),gp_Pnt(*point))
    elif kind=="CYLINDER":uv=ElSLib.Parameters_s(adaptor.Cylinder(),gp_Pnt(*point))
    else:raise ValueError("Unsupported adjacent original surface type")
    return BRepClass_FaceClassifier(face.wrapped,gp_Pnt2d(*uv),1e-7).State() in (TopAbs_IN, TopAbs_ON)


# The known rejected S3.Y three-face union joins twelve original source sides
# and adds two interior diagonals. A source-indexed seam has at most two sides.
JOINT_EXPECTED_PATCHES = 160
JOINT_EXPECTED_CONTROLS = 1685
JOINT_EXPECTED_TWO_SIDED_SEAMS = 278
JOINT_EXPECTED_OPEN_SIDES = 84
SELECTED_S3Y_PATCHES = 156
SELECTED_S3Y_CONTROLS = 1665
IMMUTABLE_HOLE_PATCH_RANGE = range(96, 126)
IMMUTABLE_SELECTED_3044_PATCH_RANGE = range(148, 156)


def _indexed_side(patch, label):
    """Return the original 4x4 patch-edge global control-index sequence."""
    if len(patch) != 16:
        raise ValueError('Expected exactly sixteen indexed bicubic controls')
    sides = {
        'bottom': tuple(patch[:4]), 'top': tuple(patch[-4:]),
        'left': tuple(patch[::4]), 'right': tuple(patch[3::4]),
    }
    if label not in sides:
        raise ValueError('Unknown indexed patch side')
    return sides[label]


def _directed_side(patch, label):
    """Use actual counterclockwise patch-boundary orientation.

    Raw grid rows and columns run left-to-right / bottom-to-top. The top
    and left sides therefore run in reverse when traversing a patch CCW.
    Comparing raw grid sides in reverse is not a valid general seam test.
    """
    ids = _indexed_side(patch, label)
    return ids[::-1] if label in ('top', 'left') else ids


def _sides_by_original_indices(patches):
    """Compute complete 1/2-sided incidence, without coordinate welding."""
    owners = {}
    for patch_id, patch in enumerate(patches):
        for side_name in ('bottom','right','top','left'):
            indices = _indexed_side(patch, side_name)
            if len(set(indices)) != 4:
                raise ValueError('Degenerate four-control indexed side')
            key = tuple(sorted(indices))
            owners.setdefault(key, []).append((patch_id, side_name, indices))
            if len(owners[key]) > 2:
                raise ValueError('Overincident global indexed interface')
    return owners


def audit_global_repair_scope(selected_points, selected_patches, trial_points,
                              joint_patches, moved_ids, inherited_side_lineage,
                              neighbor_old_patch_ids, *, bias_mm, enforce_original_counts=True):
    """Fail closed on untracked patch/control edits, seams and old-face holes.

    This is a pure integer-topology gate; original CAD/native sidedness is an
    additional mandatory geometric check, never substituted by this function.
    """
    if not math.isfinite(bias_mm) or bias_mm < 0 or bias_mm > 0.0014:
        raise ValueError('Invalid repair displacement')
    if len(trial_points) < len(selected_points):
        raise ValueError('Repair deleted source controls')
    if tuple(tuple(x) for x in joint_patches[:len(selected_patches)]) != tuple(
            tuple(x) for x in selected_patches):
        raise ValueError('Previously accepted patch indices changed')
    moved = set(moved_ids)
    if any(not isinstance(i,int) or not 0<=i<len(selected_points) for i in moved):
        raise ValueError('Moved control outside frozen selected atlas')
    actual = {i for i in range(len(selected_points)) if
              tuple(selected_points[i]) != tuple(trial_points[i])}
    expected = moved if bias_mm > 0 else set()
    if actual != expected:
        raise ValueError('Unexpected source-canonical global control mutation')
    influenced = {pid for pid,patch in enumerate(selected_patches)
                  if moved.intersection(patch)}
    if influenced != set(neighbor_old_patch_ids):
        raise ValueError('Untracked old patch affected by shared control movement')
    if influenced.intersection(IMMUTABLE_HOLE_PATCH_RANGE):
        raise ValueError('Original source #218 hole patch controls changed')
    if influenced.intersection(IMMUTABLE_SELECTED_3044_PATCH_RANGE):
        raise ValueError('Original source #3044 accepted patch controls changed')
    original_owners = _sides_by_original_indices(selected_patches)
    repaired_owners = _sides_by_original_indices(joint_patches)
    new_patch_ids = set(range(len(selected_patches),len(joint_patches)))
    seen_old_seams = set()
    for face_id,edge_map in inherited_side_lineage.items():
        for edge_id,side_records in edge_map.items():
            if edge_id not in TARGET_CIRCLES.get(face_id,()) and len(side_records)>1:
                raise ValueError('Unexpected multi-piece original source lineage')
            for old_pid,old_side in side_records:
                if not 0 <= old_pid < len(selected_patches):
                    raise ValueError('Old original source side no longer in parent')
                old_key = tuple(sorted(_indexed_side(selected_patches[old_pid], old_side)))
                if old_key in seen_old_seams:
                    raise ValueError('Repeated or aliased original inherited source side')
                seen_old_seams.add(old_key)
                if len(original_owners.get(old_key,())) != 1:
                    raise ValueError('Inherited STEP edge is not an open old interface')
                joined = repaired_owners.get(old_key,())
                if len(joined) != 2:
                    raise ValueError('Original indexed source edge failed to join two sides')
                joint_patch_ids = {x[0] for x in joined}
                if old_pid not in joint_patch_ids or len(joint_patch_ids & new_patch_ids) != 1:
                    raise ValueError('Source edge not joined to exactly one new planar patch')
                old_side_record = next(row for row in joined if row[0] == old_pid)
                new_side_record = next(row for row in joined if row[0] in new_patch_ids)
                old_side_ids = _directed_side(selected_patches[old_pid], old_side_record[1])
                new_side_ids = _directed_side(joint_patches[new_side_record[0]], new_side_record[1])
                if old_side_ids != tuple(reversed(new_side_ids)):
                    raise ValueError('Source seam has equal indices but inconsistent CCW boundary orientation')
    paired = sum(len(x)==2 for x in repaired_owners.values())
    opened = sum(len(x)==1 for x in repaired_owners.values())
    if enforce_original_counts and (
            len(selected_points),len(selected_patches),
            len(trial_points),len(joint_patches),paired,opened) != (
            SELECTED_S3Y_CONTROLS,SELECTED_S3Y_PATCHES,
            JOINT_EXPECTED_CONTROLS,JOINT_EXPECTED_PATCHES,
            JOINT_EXPECTED_TWO_SIDED_SEAMS,JOINT_EXPECTED_OPEN_SIDES):
        raise ValueError('Original S3.Y indexed seam counts or cardinality changed')
    return {'changed_prior_source_control_count':len(actual),
            'affected_prior_source_patch_ids':sorted(influenced),
            'joined_original_source_side_count':len(seen_old_seams),
            'global_two_sided_seams':paired,'global_open_sides':opened,
            'source_hole_218_patches_unchanged':True,
            'selected_3044_patches_unchanged':True}


def run_private_trials(source: bytes, parent: bytes, parent_manifest: dict, native,
                       *, biases=TRIAL_BIASES_MM):
    """Generate *unadmitted* candidates; never declare a pass without both owners.

    The original source and S3.Y admitted child are always rebuilt from pinned
    parents before attempting any coordinate adjustment.
    """
    import importlib
    from s3zb_oriented_seam_and_coons_gate import audit_final_candidate
    from audit_analytic_bp import read_bp, surface
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from s3r_s40_conforming_hole_join import _edge_adjacency, _side
    from s3s_full_original_face_census import full_correspondence
    from s3i_joint_source_atlas import _serialize
    from s3w_s40_shared_spline_repair import (
        bound_bicubic_cylinder_radial_mm, _analytic_cylinder_distance,
        sampled_bicubic_area_mm2)
    from s3v_s40_curved_planar_closure import _source_edge_closest
    from s3zc_exact_bernstein_radial_gate import require_exact_native_cylinder_envelope
    from OCP.BRepAdaptor import BRepAdaptor_Curve

    sy=importlib.import_module("s3y_s40_curved_planar_rings")
    check_input_hashes(source,parent)
    if not biases or any(not math.isfinite(b) or b<0 or b>0.0014 for b in biases):
        raise ValueError("Unapproved shared-control displacement trial")
    selected,previous_receipt=sy.build_candidate(source,native,parent,parent_manifest,faces=(3044,))
    if sha256(selected.encode()).hexdigest()!=S3Y_SELECTED_SHA:
        raise ValueError("Frozen S3.Y admitted child changed")
    joint,joint_receipt=sy.build_candidate(source,native,parent,parent_manifest,
                                          faces=(3044,1827,1907))
    base_pts,base_patches=read_bp(selected)
    pts0,patches=read_bp(joint)
    if (len(base_pts),len(base_patches),len(patches)) != (1665,156,160):
        raise ValueError("Unexpected S3.Y selective and joint geometry cardinality")
    if base_pts != pts0[:1665] or base_patches != patches[:156]:
        raise ValueError("S3.Y previously admitted child is not an exact candidate prefix")
    table=sy.parse_entities(source.decode())
    correspondence=full_correspondence(source.decode(),native)
    parent_pts,parent_patches=read_bp(parent.decode())
    neighbors={}
    moved_directions={}
    all_inherited_source_sides={}
    for fid in TARGET_FACES:
        original=correspondence['native_faces'][correspondence['face_map'][fid]]
        normal=original.normalAt().toTuple()
        source_sides,_=sy.recover_source_sides(source,native,parent_pts,parent_patches,fid)
        all_inherited_source_sides[fid]=sy.SOURCE_SIDE_LINEAGE[fid]
        for eid in TARGET_CIRCLES[fid]:
            sides=[x for original_eid,x in source_sides if original_eid==eid]
            if len(sides)!=1:
                raise ValueError("Original circular source edge lost single-cubic identity")
            ids=sides[0]
            owners=correspondence['owners'][eid]
            if fid not in owners or len(owners)!=2:
                raise ValueError("Source STEP edge no longer has exactly two owners")
            neighbor_source=next(iter(owners-{fid}))
            neighbor=correspondence['native_faces'][correspondence['face_map'][neighbor_source]]
            if neighbor.geomType()!='CYLINDER':
                raise ValueError("Original circle source-neighbor support is not CYLINDER")
            directions=control_bias_directions(
                pts0,ids,normal,lambda p:_sample_native_trim(original,p),probe_mm=.01)
            for j,index in enumerate(ids[1:3]):
                if index in moved_directions:
                    raise ValueError("Repeated source-indexed circular interior control")
                moved_directions[index]=directions[j]
            old_patch=sy.SOURCE_SIDE_LINEAGE[fid][eid][0][0]
            if old_patch in neighbors:
                raise ValueError("Two source circles mapped to one old cylinder patch")
            neighbors[old_patch]=(fid,eid,neighbor)
    if len(moved_directions)!=16 or len(neighbors)!=8:
        raise ValueError("Incomplete circular source-control repair lineage")
    # Certify that no shared control affects an unexpected prior atlas patch.
    for pid, patch in enumerate(base_patches):
        if set(patch).intersection(moved_directions) and pid not in neighbors:
            raise ValueError('Circular source control aliases an untracked previous patch')
    pilot=[]
    for bias in biases:
        moved={idx:tuple(pts0[idx][k]+bias*vec[k] for k in range(3))
               for idx,vec in moved_directions.items()}
        points,recomputed=compose_controls(pts0,patches,moved,first_new=156)
        topology_receipt = audit_global_repair_scope(
            base_pts,base_patches,points,patches,moved_directions,
            all_inherited_source_sides,neighbors, bias_mm=bias)
        # An additional independent gate checks all new-new and new-old
        # directed boundary seams and the exact new planar Coons interiors.
        # It runs before native sampled geometry; any failure aborts the trial.
        oriented_and_coons = audit_final_candidate(base_pts,base_patches,points,patches)
        candidate=_serialize(points,patches)
        stats={'shared_control_bias_mm':bias,'changed_shared_controls':(16 if bias>0 else 0),
               'parent_156_patch_index_prefix_unchanged':True,
               'new_planar_interiors_recomputed':len(recomputed),
               'native_owner_boundary_OUT':0,'modified_neighbor_OUT':0,
               'max_radial_float_guarded_mm':0.,'max_original_curve_sampled_mm':0.,
               'exact_rational_native_cylinder_checks':0,
               'new_planar_interior_OUT':0,'new_planar_boundary_OUT':0,
               'max_native_area_relative_error':0.,'repaired_hole_218_unchanged':True,
               'status':'BLOCKED','candidate_sha256':sha256(candidate.encode()).hexdigest(),
               'indexed_topology_gate':topology_receipt,
               'oriented_and_coons_gate':oriented_and_coons}
        try:
            if any(points[i]!=base_pts[i] for patch in base_patches
                   for i in patch if i not in moved_directions):
                raise ValueError('A previously admitted unrelated control changed')
            if any(i in moved_directions for patch in base_patches[96:126] for i in patch):
                raise ValueError('The original hole #218 was modified')
            if any(points[i]!=base_pts[i] for patch in base_patches[148:156] for i in patch):
                raise ValueError('S3.Y admitted #3044 patch was modified')
            # Evaluate both faces on each source edge; old patches stay connected
            # by exact common integer IDs, never by proximity welding.
            for fid in TARGET_FACES:
                planar=correspondence['native_faces'][correspondence['face_map'][fid]]
                old_sides,_=sy.recover_source_sides(source,native,parent_pts,parent_patches,fid)
                for eid,idx in old_sides:
                    if eid not in TARGET_CIRCLES[fid]:continue
                    neighbor=neighbors[sy.SOURCE_SIDE_LINEAGE[fid][eid][0][0]][2]
                    for k in range(65):
                        xyz=bernstein_point(points,idx,k/64)
                        if not _sample_native_trim(planar,xyz):stats['native_owner_boundary_OUT']+=1
                        if not _sample_native_trim(neighbor,xyz):stats['native_owner_boundary_OUT']+=1
            # Check all four new planar patches, not only their original edges.
            for fid in TARGET_FACES:
                planar=correspondence['native_faces'][correspondence['face_map'][fid]]
                portion=joint_receipt['faces'][str(fid)]
                netlist=patches[portion['first_new_patch']:
                                portion['first_new_patch']+portion['new_patch_count']]
                min_area=0.0
                for patch in netlist:
                    net=[points[i] for i in patch]
                    area,jac=sampled_bicubic_area_mm2(net,planar.normalAt().toTuple())
                    min_area+=area
                    if jac<=0:raise ValueError('Folded planar candidate patch')
                    for i in range(13):
                        for j in range(13):
                            if not _sample_native_trim(planar,surface(net,(i+.5)/13,(j+.5)/13)):
                                stats['new_planar_interior_OUT']+=1
                    for label in ('bottom','top','left','right'):
                        ids=_side(patch,label)
                        for k in range(41):
                            if not _sample_native_trim(planar,bernstein_point(points,ids,k/40)):
                                stats['new_planar_boundary_OUT']+=1
                relative=abs(min_area-planar.Area())/planar.Area()
                stats['max_native_area_relative_error']=max(
                    stats['max_native_area_relative_error'],relative)
                if relative>=1e-4:
                    raise ValueError('Original native planar area discrepancy exceeds pilot threshold')
            for pid,(fid,eid,neighbor) in neighbors.items():
                net=[points[k] for k in patches[pid]]
                cylinder=BRepAdaptor_Surface(neighbor.wrapped).Cylinder()  # noqa: F821
                bound=bound_bicubic_cylinder_radial_mm(net,cylinder)
                require_exact_native_cylinder_envelope(net,cylinder)
                stats['exact_rational_native_cylinder_checks']+=1
                stats['max_radial_float_guarded_mm']=max(stats['max_radial_float_guarded_mm'],bound['upper_mm'])
                for i in range(13):
                    for j in range(13):
                        xyz=surface(net,(i+.5)/13,(j+.5)/13)
                        if not _sample_native_trim(neighbor,xyz):stats['modified_neighbor_OUT']+=1
            if stats['exact_rational_native_cylinder_checks'] != len(neighbors):
                raise ValueError('Incomplete original native exact-rational radial verification')
            if stats['max_radial_float_guarded_mm']>FIXED_BUDGET_MM:
                raise ValueError("Original cylinder radial envelope exceeds fixed budget")
            if (stats['native_owner_boundary_OUT'] or stats['modified_neighbor_OUT'] or
                stats['new_planar_boundary_OUT'] or stats['new_planar_interior_OUT']):
                raise ValueError('Original native two-sided or planar trim membership fails')
            # The cubic control movement may create a curve that approximates
            # its STEP original too coarsely. Check the actual native BRep edge.
            for fid in TARGET_FACES:
                source_sides,_=sy.recover_source_sides(
                    source,native,parent_pts,parent_patches,fid)
                for eid,ids in source_sides:
                    if eid not in TARGET_CIRCLES[fid]:continue
                    native_edge=correspondence['native_edges'][correspondence['edge_map'][eid]]
                    adaptor=BRepAdaptor_Curve(native_edge.wrapped)
                    for k in range(41):
                        d=_source_edge_closest(adaptor,bernstein_point(points,ids,k/40),
                                               sample_count=129)
                        stats['max_original_curve_sampled_mm']=max(
                            stats['max_original_curve_sampled_mm'],d)
            if stats['max_original_curve_sampled_mm']>FIXED_BUDGET_MM:
                raise ValueError('Original native source curve deviation exceeds fixed budget')
            # The side and sampled support checks pass, but no continuous
            # trimmed-surface equivalence or production APMesh result follows.
            stats['status']='PRELIMINARY_TWO_SIDED_TRIM_PASS_NOT_ADMITTED' 
        except (ValueError, RuntimeError) as error:
            stats['reason']=str(error)
        pilot.append(stats)
    return {'schema':'apmesh-s3z-original-s40-circular-source-identity-trials-v1',
            'source_sha256':ORIGINAL_STEP_SHA,'parent_156_patch_sha256':S3Y_SELECTED_SHA,
            'original_step_faces_blocked':list(TARGET_FACES),
            'original_circle_edge_ids':{str(k):list(v) for k,v in TARGET_CIRCLES.items()},
            'candidate_trials':pilot,'private_bp_published':False,
            'admitted_patch_count':156,'admitted_source_faces':22,
            'strict_native_admission_completed':False,
            'formal_continuous_geometry_certificate':False,
            'apmesh_tri_quad_executed':False}, None


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-step',type=Path,required=True)
    parser.add_argument('--s3w-bp',type=Path,required=True)
    parser.add_argument('--s3w-manifest',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    source=args.original_step.read_bytes()
    parent=args.s3w_bp.read_bytes()
    check_input_hashes(source,parent)
    import cadquery as cq
    native=cq.importers.importStep(str(args.original_step)).val()
    result,_=run_private_trials(source,parent,json.loads(args.s3w_manifest.read_text()),native)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':'TRIALS_ONLY_NO_ADMISSION','baseline_patches':156,
                      'attempted_biases':len(result['candidate_trials'])},sort_keys=True))


if __name__=='__main__':
    main()
