#!/usr/bin/env python3
"""Evaluate feature-locked patch-center relocation on PRIVATE original data.

This is an external, deliberately constrained QUAD-shape experiment, NOT a
native APMesh QUAD generator or a scientific benchmark admission. It never
publishes the original STL/BP, F27/F28/F29 meshes, or the derived F30 OBJ.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import thingi10k_f27_native_tri_evidence as f27
import thingi10k_f28_topology_aware_stitch as f28
import thingi10k_f29_quad_capability_and_recovery as f29

SCHEMA = 'apmesh-s40-f30-feature-locked-pareto-center-v1'
F29_QUAD_SHA256 = 'e2687802ec3314178a973282a33ffd86d71ee8aaa87eed3d4976b266000cf548'
F29_QUAD_BYTES = 38834
GRID_DENOMINATOR = 20
MIN_BARYCENTRIC_WEIGHT = 1 / GRID_DENOMINATOR
MAX_SCALED_JACOBIAN_REGRESSION = 1e-12
MAX_ANGLE_DEGREES_REGRESSION = 1e-10
MIN_MEANINGFUL_ANGLE_DELTA_DEGREES = 1e-6
MIN_MEANINGFUL_JACOBIAN_DELTA = 1e-8
MAX_AREA_RELATIVE_ERROR = 1e-11
EXPECTED_SOURCE_FACETS = 292
EXPECTED_QUADS = 876
EXPECTED_QUAD_VERTICES = 878
EXPECTED_FEATURE_EDGES = 205


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def distance(a, b) -> float:
    return math.dist(a, b)


def source_triangle_corners(triangle) -> tuple[float, float, float]:
    """Original STL interior angles at fixed corner vertices, in degrees."""
    require(len(triangle) == 3 and all(len(v) == 3 for v in triangle),
            'Expected one original STL triangle')
    result = []
    for j in range(3):
        origin = triangle[j]
        left = f27.vec(triangle[(j+2)%3], origin)
        right = f27.vec(triangle[(j+1)%3], origin)
        length = math.sqrt(f27.dot(left, left) * f27.dot(right, right))
        require(length > 0 and math.isfinite(length), 'Degenerate STL corner')
        value = math.degrees(math.atan2(math.sqrt(f27.dot(f27.cross(left,right),
                                                          f27.cross(left,right))),
                                            f27.dot(left,right)))
        require(math.isfinite(value) and 0 < value < 180, 'Invalid STL angle')
        result.append(value)
    return tuple(result)


def midpoint(a, b) -> tuple[float, float, float]:
    return tuple((x+y)/2 for x, y in zip(a,b))


def barycentric(triangle, weights) -> tuple[float, float, float]:
    require(len(weights) == 3 and all(math.isfinite(float(w)) for w in weights) and
            all(0 < w < 1 for w in weights) and
            abs(math.fsum(weights)-1) < 1e-14,
            'Center must be strictly inside the source triangle')
    return tuple(math.fsum(weights[i]*triangle[i][j] for i in range(3))
                 for j in range(3))


def candidate_weights() -> tuple[tuple[float, float, float], ...]:
    """Fixed deterministic rational search, independent of scientific data."""
    return tuple((i/GRID_DENOMINATOR,j/GRID_DENOMINATOR,
                  (GRID_DENOMINATOR-i-j)/GRID_DENOMINATOR)
                 for i in range(1,GRID_DENOMINATOR-1)
                 for j in range(1,GRID_DENOMINATOR-i)
                 if GRID_DENOMINATOR-i-j >= 1)


def candidate_metrics(triangle, center) -> tuple[dict, dict, dict]:
    """Compute three complete, oriented convex QUAD corner-quality records."""
    require(len(triangle) == 3 and len(center) == 3 and
            all(math.isfinite(float(z)) for vertex in triangle for z in vertex) and
            all(math.isfinite(float(z)) for z in center),
            'Invalid original facet or new center')
    middles = tuple(midpoint(triangle[i],triangle[(i+1)%3]) for i in range(3))
    reference_normal = f29.normal(*triangle)
    return tuple(f29.quad_metric((0,1,2,3),
                        [triangle[i],middles[i],center,middles[(i-1)%3]],
                        reference_normal) for i in range(3))


def dominates_or_equals(candidate, incumbent) -> bool:
    """Require no *per-QUAD* regression in three distinct shape indicators."""
    require(len(candidate) == len(incumbent) == 3,
            'Expected three source-facet quads')
    return all(new['min_angle_deg'] + MAX_ANGLE_DEGREES_REGRESSION >= old['min_angle_deg']
               and new['max_angle_deg'] <= old['max_angle_deg'] + MAX_ANGLE_DEGREES_REGRESSION
               and new['min_scaled_jacobian'] + MAX_SCALED_JACOBIAN_REGRESSION >=
                   old['min_scaled_jacobian']
               for new, old in zip(candidate, incumbent))


def meaningfully_better(candidate, incumbent) -> bool:
    return any(new['min_angle_deg'] > old['min_angle_deg'] + MIN_MEANINGFUL_ANGLE_DELTA_DEGREES
               or new['max_angle_deg'] < old['max_angle_deg'] - MIN_MEANINGFUL_ANGLE_DELTA_DEGREES
               or new['min_scaled_jacobian'] >
                   old['min_scaled_jacobian'] + MIN_MEANINGFUL_JACOBIAN_DELTA
               for new, old in zip(candidate, incumbent))


def optimize_facet(triangle) -> dict:
    """Deterministic one-pass Pareto improvement with fixed source edges."""
    original_center = barycentric(triangle,(1/3,1/3,1/3))
    original = candidate_metrics(triangle,original_center)
    chosen = original_center
    chosen_metrics = original
    winning_weights = (1/3,1/3,1/3)
    accepted = 0
    rejected_nonconvex = 0
    for weights in candidate_weights():
        trial_center = barycentric(triangle,weights)
        try:
            trial = candidate_metrics(triangle,trial_center)
        except ValueError:
            rejected_nonconvex += 1
            continue
        if (dominates_or_equals(trial,chosen_metrics) and meaningfully_better(trial,chosen_metrics)):
            chosen = trial_center
            chosen_metrics = trial
            winning_weights = weights
            accepted += 1
    require(dominates_or_equals(chosen_metrics, original),
            'Selected candidate regresses an original patch')
    # A fixed source-corner angle is also a literal QUAD corner angle.
    original_angles = source_triangle_corners(triangle)
    for i in range(3):
        require(abs(chosen_metrics[i]['min_angle_deg'] - original_angles[i]) <= 1e-7 or
                chosen_metrics[i]['min_angle_deg'] < original_angles[i] + 1e-7,
                'Source STL corner-angle invariant failed')
    original_area = f27.area(*triangle)
    recovered_area = math.fsum(item['area'] for item in chosen_metrics)
    require(original_area > 0 and abs(recovered_area-original_area)/original_area <=
            MAX_AREA_RELATIVE_ERROR, 'New source facet area differs')
    return {'original_center': original_center, 'optimized_center': chosen,
            'baseline': original, 'optimized': chosen_metrics, 'weights': winning_weights,
            'accepted_candidates': accepted, 'nonconvex_candidates': rejected_nonconvex,
            'moved': distance(original_center,chosen)>1e-10}


def describe_quality(metrics) -> dict:
    require(len(metrics) > 0 and all(0 <= m['min_scaled_jacobian'] <= 1+1e-10
                                     for m in metrics), 'Malformed QUAD metrics')
    return {'quads':len(metrics),
            'min_angle_deg':min(x['min_angle_deg'] for x in metrics),
            'max_angle_deg':max(x['max_angle_deg'] for x in metrics),
            'mean_min_angle_deg':math.fsum(x['min_angle_deg'] for x in metrics)/len(metrics),
            'min_scaled_jacobian':min(x['min_scaled_jacobian'] for x in metrics),
            'mean_min_scaled_jacobian':math.fsum(x['min_scaled_jacobian'] for x in metrics)/len(metrics),
            'count_min_angle_below_10_deg':sum(x['min_angle_deg'] < 10 for x in metrics),
            'count_min_angle_below_30_deg':sum(x['min_angle_deg'] < 30 for x in metrics),
            'count_max_angle_above_150_deg':sum(x['max_angle_deg'] > 150 for x in metrics)}


def optimize_source(source) -> dict:
    require(len(source) > 0 and all(len(tri) == 3 for tri in source),
            'Original source facets missing')
    changed = 0
    outputs = []
    baseline = []
    optimized = []
    travel_ratios = []
    source_angles = []
    for tri in source:
        record = optimize_facet(tri)
        outputs.append(record)
        baseline.extend(record['baseline'])
        optimized.extend(record['optimized'])
        changed += int(record['moved'])
        max_edge=max(distance(tri[i],tri[(i+1)%3]) for i in range(3))
        travel_ratios.append(distance(record['original_center'],record['optimized_center'])/max_edge)
        source_angles.extend(source_triangle_corners(tri))
    for candidate, initial in zip(optimized,baseline):
        require(dominates_or_equals((candidate,)*3,(initial,)*3),
                'Independent final QUAD quality regressed')
    floor=min(source_angles)
    baseline_summary=describe_quality(baseline)
    optimized_summary=describe_quality(optimized)
    # Fixed source corners set an UPPER bound on the best possible global
    # minimum, not a lower bound on a possible mesh's worst element.
    require(baseline_summary['min_angle_deg'] <= floor + 1e-7 and
            optimized_summary['min_angle_deg'] <= floor + 1e-7,
            'Fixed source-corner angle upper bound was violated')
    source_sin=min(math.sin(math.radians(angle)) for angle in source_angles)
    require(baseline_summary['min_scaled_jacobian'] <= source_sin+1e-7 and
            optimized_summary['min_scaled_jacobian'] <= source_sin+1e-7,
            'Fixed source-corner Jacobian upper bound was violated')
    return {'facets':outputs, 'baseline_quality':baseline_summary,
            'optimized_quality':optimized_summary,
            'changed_source_facet_centers':changed,
            'unchanged_source_facet_centers':len(source)-changed,
            'original_corner_angle_upper_bound_deg':floor,
            'original_corner_jacobian_upper_bound':source_sin,
            'source_corner_angle_below_30_count':sum(x < 30 for x in source_angles),
            'source_corner_angle_below_10_count':sum(x < 10 for x in source_angles),
            'source_corner_angle_above_150_count':sum(x > 150 for x in source_angles),
            'max_center_displacement_over_source_edge':max(travel_ratios),
            'mean_center_displacement_over_source_edge':math.fsum(travel_ratios)/len(travel_ratios),
            'rational_candidate_count_per_facet':len(candidate_weights())}


def updated_geometry_from_f29(original_vertices, original_tags, source, solution):
    require(len(original_vertices) == len(original_tags) == EXPECTED_QUAD_VERTICES and
            len(source) == len(solution['facets']) == EXPECTED_SOURCE_FACETS,
            'Original recovered model size changed')
    optimized=list(original_vertices)
    changed_indices=[]
    tag_to_index={}
    for i,tag in enumerate(original_tags):
        require(tag not in tag_to_index,'Duplicate original source entity in QUAD mesh')
        tag_to_index[tag]=i
    for facet,record in enumerate(solution['facets']):
        key=('centroid',facet)
        require(key in tag_to_index,'Missing source facet centroid in recovered QUAD')
        idx=tag_to_index[key]
        expected=barycentric(source[facet],(1/3,1/3,1/3))
        require(max(abs(x-y) for x,y in zip(original_vertices[idx],expected)) <= 1e-11,
                'Original private F29 centroid differs from pinned STL')
        # Preserve the exact native value when the facet did not move.
        if record['moved']:
            optimized[idx]=record['optimized_center']
            changed_indices.append(idx)
    require(len(changed_indices)==solution['changed_source_facet_centers'],
            'Center-only identity mapping changed')
    require(all(original_vertices[i] == optimized[i] or i in changed_indices
                for i in range(len(optimized))),
            'Source vertex or edge midpoint was modified')
    return optimized,changed_indices


def emit_private_f30_obj(f29_original_bytes: bytes, updated_vertices, changed_indices) -> bytes:
    """Replace only authorized facet-centroid `v` lines in a NEW private QUAD OBJ."""
    require(hashlib.sha256(f29_original_bytes).hexdigest() == F29_QUAD_SHA256 and
            len(f29_original_bytes)==F29_QUAD_BYTES,
            'Missing or altered private F29 QUAD source')
    lines=f29_original_bytes.decode('utf-8').splitlines()
    source_vertex_lines=[i for i,line in enumerate(lines) if line.startswith('v ')]
    source_face_lines=[line for line in lines if line.startswith('f ')]
    require(len(source_vertex_lines)==len(updated_vertices)==EXPECTED_QUAD_VERTICES and
            len(source_face_lines)==EXPECTED_QUADS,
            'F29 QUAD original face/index coverage differs')
    require(len(changed_indices)==len(set(changed_indices)) and
            all(0 <= i < len(updated_vertices) for i in changed_indices),
            'Duplicate or invalid private centroid indices')
    for idx in changed_indices:
        value=updated_vertices[idx]
        require(all(math.isfinite(c) for c in value), 'New center is nonfinite')
        lines[source_vertex_lines[idx]]='v ' + ' '.join(format(x,'.6g') for x in value)
    require([line for line in lines if line.startswith('f ')]==source_face_lines,
            'Original QUAD connectivity was modified')
    rows=['# EXPERIMENTAL F30 center-only QUAD derivative; NOT native APMesh QUAD output',
          '# Unmodified private F29 QUAD SHA256 '+F29_QUAD_SHA256,
          '# Source STL edges/creases and QUAD face ordering retained exactly',
          '# Only facet centroids may move; not a native APMesh engine change']
    return ('\n'.join(rows+lines)+'\n').encode('utf-8')


def replay_private(source_zip:Path,bp:Path,run1:Path,run2:Path,
                   f28_obj:Path,private_f29_obj:Path,private_output:Path,receipt_path:Path)->dict:
    """Recheck the actual F27/F28/F29 chain before emitting private F30 output."""
    require(not private_output.exists() and not receipt_path.exists(),
            'Refuse overwriting original or derived research results')
    f29_original_bytes=private_f29_obj.read_bytes()
    require(len(f29_original_bytes)==F29_QUAD_BYTES and
            hashlib.sha256(f29_original_bytes).hexdigest()==F29_QUAD_SHA256,
            'Private F29 derived QUAD identity changed')
    results=[]
    source=f27.parse_source(source_zip)
    f27.parse_bp(bp)
    for run in (run1,run2):
        prior=f28.evaluate_run(source_zip,bp,run)
        require(prior[-1] == f28_obj.read_bytes(),
                'Original F28 derived TRI does not match repeated native source')
        qa=f29.verify_real_quad(source,prior[-1],prior[1])
        emitted=f29.emit_private_quad_obj(f28_obj,qa['reconstructed'])
        require(emitted==f29_original_bytes,
                'Private F29 reconstructed OBJ differs from source identity')
        results.append((prior,qa))
    solution=optimize_source(source)
    original_recon=results[0][1]['reconstructed']
    keep=original_recon['full_original_vertex_indices']
    source_tags=[results[0][0][1]['tags'][i] for i in keep]
    full_vertices=[results[0][0][1]['full_xyz'][i] for i in keep]
    optimized_vertices,changed=updated_geometry_from_f29(full_vertices,source_tags,source,solution)
    assert len(optimized_vertices)==len(original_recon['vertices'])
    # Ensure the complete, original, source-aware seam and facet-edge graph is unchanged.
    topology=f29.quad_topology(len(optimized_vertices),original_recon['quads'])
    require(topology==results[0][1]['topology'] and
            results[0][1]['source_feature_retention']==results[1][1]['source_feature_retention'],
            'Original QUAD topology/feature preservation changed')
    metric_records=[]
    for i,q in enumerate(original_recon['quads']):
        metric_records.append(f29.quad_metric(q,optimized_vertices,
                                              f29.normal(*source[i//3])))
    actual=describe_quality(metric_records)
    for key,value in actual.items():
        expected=solution['optimized_quality'][key]
        if isinstance(value,float):
            require(abs(value-expected)<1e-8,f'Optimized full-native metric mismatch: {key}')
        else:
            require(value==expected,f'Optimized quality count mismatch: {key}')
    # The only changing XYZ entities are original facet centroids, which are not on creases.
    for i,tag in enumerate(source_tags):
        if tag[0] != 'centroid':
            require(optimized_vertices[i] == full_vertices[i],
                    'Original source or sharp-crease vertex changed')
    output=emit_private_f30_obj(f29_original_bytes,optimized_vertices,changed)
    private_output.mkdir(parents=True,mode=0o700)
    obj_path=private_output/'293137_pareto_center_optimized_quad_NOT_NATIVE_APMESH.obj'
    with obj_path.open('xb') as out:
        out.write(output)
    # A repeat must produce exactly the same bytes with source runs reversed.
    flipped=list(reversed(results))
    recon=flipped[0][1]['reconstructed']
    flipped_tags=[flipped[0][0][1]['tags'][i] for i in recon['full_original_vertex_indices']]
    flipped_vertices=[flipped[0][0][1]['full_xyz'][i] for i in recon['full_original_vertex_indices']]
    flipped_optimized,flipped_changed=updated_geometry_from_f29(flipped_vertices,flipped_tags,source,solution)
    require(emit_private_f30_obj(f29_original_bytes,flipped_optimized,flipped_changed)==output,
            'Original native run order changes F30 output bytes')
    receipt={
        'schema':SCHEMA,
        'status':'PRIVATE_DERIVED_FEATURE_LOCKED_QUAD_PARETO_CENTER_EXPERIMENT_VALIDATED',
        'source_stl_sha256':f27.STL_SHA256,
        'private_input_bp_sha256':f27.BP_SHA256,
        'original_native_tri_obj_sha256':f27.sha256(run1/'bunny_passo_0_malha_0.obj'),
        'previous_private_f29_quad_obj_sha256':F29_QUAD_SHA256,
        'private_f30_derived_quad_obj_sha256':hashlib.sha256(output).hexdigest(),
        'private_f30_derived_quad_obj_bytes':len(output),
        'f27_original_native_run_count':2,
        'private_output_byte_identical_under_native_run_order_reversal':True,
        'source_facets':len(source),'quad_faces':len(original_recon['quads']),
        'quad_topology':topology,
        'optimization':'finite deterministic rational-grid Pareto ascent, center-only, denominator 20',
        'all_original_stl_vertices_and_edge_midpoints_unchanged':True,
        'native_apmesh_engine_or_exporter_changed':False,
        'native_quad_generator_executed':False,
        'baseline_quality':solution['baseline_quality'],
        'optimized_quality':solution['optimized_quality'],
        'source_corner_angle_upper_bound_on_global_min_deg':solution['original_corner_angle_upper_bound_deg'],
        'source_corner_scaled_jacobian_upper_bound_on_global_min':solution['original_corner_jacobian_upper_bound'],
        'source_corners_below_30_immutable_count':solution['source_corner_angle_below_30_count'],
        'source_corners_below_10_immutable_count':solution['source_corner_angle_below_10_count'],
        'source_corners_above_150_immutable_count':solution['source_corner_angle_above_150_count'],
        'changed_source_facet_centers':solution['changed_source_facet_centers'],
        'unchanged_source_facet_centers':solution['unchanged_source_facet_centers'],
        'max_center_displacement_over_source_edge':solution['max_center_displacement_over_source_edge'],
        'mean_center_displacement_over_source_edge':solution['mean_center_displacement_over_source_edge'],
        'rational_candidate_count_per_facet':solution['rational_candidate_count_per_facet'],
        'feature_edge_retention':results[0][1]['source_feature_retention'],
        'new_or_changed_original_corner_or_feature_vertex_count':0,
        'source_facet_area_full_precision':results[0][1]['source_facet_area'],
        'independent_matched_quad_literature_reference':False,
        'copyright_license_cleared':False,
        'global_self_intersection_free_certified':False,
        'scientific_benchmark_admitted':False,
        'published_original_or_private_derived_geometry':False,
    }
    with receipt_path.open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,indent=2,sort_keys=True,allow_nan=False)
        stream.write('\n')
    return receipt


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-zip',type=Path,required=True)
    parser.add_argument('--private-bp',type=Path,required=True)
    parser.add_argument('--native-run-1',type=Path,required=True)
    parser.add_argument('--native-run-2',type=Path,required=True)
    parser.add_argument('--f28-private-stitched-obj',type=Path,required=True)
    parser.add_argument('--f29-private-quad-obj',type=Path,required=True)
    parser.add_argument('--private-output-dir',type=Path,required=True)
    parser.add_argument('--public-receipt',type=Path,required=True)
    args=parser.parse_args()
    summary=replay_private(args.source_zip,args.private_bp,args.native_run_1,args.native_run_2,
                           args.f28_private_stitched_obj,args.f29_private_quad_obj,
                           args.private_output_dir,args.public_receipt)
    print(json.dumps(summary,sort_keys=True,allow_nan=False))


if __name__=='__main__':
    main()
