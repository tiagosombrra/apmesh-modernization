#!/usr/bin/env python3
"""Audit original APMesh QUAD capability and recover an EXTERNAL derived quad surface.

The F27 original TRI OBJ and F28 source-aware stitched TRI OBJ remain immutable.
No QUAD generator is claimed in the native APMesh engine. The recovered QUAD
faces are a controlled post-processing inverse of the F21 original-STL triangle
partition, NOT a native, independently optimized, CAD-authored QUAD mesh.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

import thingi10k_f27_native_tri_evidence as f27
import thingi10k_f28_topology_aware_stitch as f28

NATIVE_BLOBS = {
    'include/data/triangle_adaptive.h': '9bfcff6bd128d62374daf39b47a7b5255b1416a6',
    'include/crab_mesh/aft/face.h': 'c615cd59c555152a43daad7d999b8caa3bf6da65',
    'src/generator/generator_adaptive.cpp': '60400e9c532ae80c8605a9e833ac4dfd70bfcb73',
    'src/input_output/write_obj_file.cpp': '453416ed67f9bbc985e26ebea3a18c39da168807',
    'include/input_output/input_validation.h': 'bc7988e862383f2f264f9d3a2a7691fe5c028592',
}
F28_STITCHED_SHA256 = 'b93995d1319e702649574044b2167fa01fe90644b1e5e02a295f3b47cdfdc46b'
F28_STITCHED_BYTES = 98801
EXPECTED_NATIVE_TRIS = 3504
EXPECTED_PATCHES = 876
EXPECTED_SOURCE_FACETS = 292
EXPECTED_QUAD_VERTICES = 878
EXPECTED_SOURCE_EDGES = 438
EXPECTED_SOURCE_SHARPS = 205
MAX_CORNER_PLANE_RESIDUAL = 1e-10
MAX_RELATIVE_AREA_ERROR = 1e-11


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit_native_original_quad_capability(root: Path) -> dict:
    """Hash-lock structural facts; QUADTREE and WRITE_MODE=q are not QUAD faces."""
    texts = {}
    for path, expected in NATIVE_BLOBS.items():
        file = root / path
        require(file.is_file() and f27.git_blob(file.read_bytes()) == expected,
                f'Native source identity differs: {path}')
        texts[path] = file.read_text(encoding='utf-8')
    triangle = texts['include/data/triangle_adaptive.h']
    face = texts['include/crab_mesh/aft/face.h']
    generator = texts['src/generator/generator_adaptive.cpp']
    original_writer = texts['src/input_output/write_obj_file.cpp']
    validation = texts['include/input_output/input_validation.h']
    require('class TriangleAdaptive : public ElementAdaptive' in triangle and
            'NodeAdaptive GetNoh(' in triangle,
            'Original physical element contract is no longer explicitly triangle-based')
    require('Vertex *v[3];' in face,
            'Original temporary advancing-front Face is no longer triangular')
    # Scope the check to SaveMesh rather than unrelated legacy source fragments.
    start = generator.find('void GeneratorAdaptive::SaveMesh(')
    end = generator.find('void GeneratorAdaptive::SaveErrorMesh(', start)
    require(start != -1 and end > start, 'Cannot locate original native SaveMesh')
    writer = generator[start:end]
    quality_branch = 'if (WriteMode() == std::string("q"))'
    require(quality_branch in writer and
            'WriteQualityMesh(saved_mesh, step_, attempt);' in writer and
            'WriteMesh(saved_mesh, step_, this->error_step_);' in writer,
            'Original WRITE_MODE=q/m/h export contract changed')
    segment = writer.split(quality_branch)[-1].split('} else if')[0]
    require('WriteQualityMesh(saved_mesh, step_, attempt);' in segment and
            'WriteMesh(' not in segment,
            'WRITE_MODE=q is not exclusively a quality report')
    require('WriteMeshOBJFile(MeshAdaptive* mesh' in original_writer and
            'TriangleAdaptive* t =' in original_writer and
            't->GetNoh(3)' in original_writer,
            'Original legacy OBJ face writer has changed')
    require('"WRITE_MODE"' in validation and '"q"' in validation,
            'Original write mode validation changed')
    return {
        'schema': 'apmesh-s40-f29-original-quad-capability-v1',
        'engine_quad_generator_executed': False,
        'audited_default_native_physical_element': 'TriangleAdaptive',
        'audited_native_uv_front_face_vertices': 3,
        'write_mode_q_meaning': 'native quality reports; not quadrilateral surface faces',
        'quad_prefix_meaning': 'quadtree cell directions and controls; not physical quads',
        'quad_output_supported_by_audited_native_tri_path': False,
        'pinned_cpp_git_blobs': NATIVE_BLOBS,
    }


def recover_quad_from_star(faces: list[tuple[int, int, int]]) -> tuple[tuple[int, ...], int]:
    """Replace four exactly oriented center-star TRI with one boundary QUAD."""
    require(len(faces) == 4 and all(len(face) == 3 for face in faces),
            'Patch requires exactly four TRI faces')
    a, b, c, d = faces
    center = a[2]
    require(a[1] == b[0] and b[1] == c[0] and c[1] == d[0] and
            d[1] == a[0] and all(face[2] == center for face in faces),
            'Not a consistent four-triangle patch-center fan')
    quad = (a[0], a[1], b[1], c[1])
    require(len(set(quad)) == 4 and center not in quad and
            all(type(i) is int and i >= 0 for i in (*quad, center)),
            'Degenerate patch or invalid node indices')
    return quad, center


def reconstruct_patch_quads(vertices: list[tuple[float, ...]],
                            tris: list[tuple[int, ...]],
                            tags: list[tuple] | None = None) -> dict:
    """Drop exactly one private patch-center vertex per original Bezier patch."""
    require(len(tris) > 0 and len(tris) % 4 == 0 and
            all(len(face) == 3 for face in tris), 'Expected nonempty 4-TRI patches')
    require(all(len(v) == 3 and all(math.isfinite(x) for x in v) for v in vertices),
            'Nonfinite or malformed XYZ coordinates')
    quads = []
    centers = []
    for offset in range(0, len(tris), 4):
        quad, center = recover_quad_from_star(tris[offset:offset+4])
        require(all(v < len(vertices) for v in (*quad, center)),
                'Native TRI refers to missing vertex')
        quads.append(quad)
        centers.append(center)
    used = sorted({v for face in quads for v in face})
    unused = set(range(len(vertices))) - set(used)
    require(len(centers) == len(set(centers)) and unused == set(centers),
            'The removed nodes must be exactly independent patch centers')
    if tags is not None:
        require(len(tags) == len(vertices) and
                all(tags[v][0] == 'patch_interior' for v in centers) and
                all(tags[v][0] != 'patch_interior' for v in used),
                'Source identities do not authorize discarding these vertices')
    remap = {old: new for new, old in enumerate(used)}
    return {'vertices': [vertices[i] for i in used],
            'full_original_vertex_indices': used,
            'quads': [tuple(remap[v] for v in face) for face in quads],
            'removed_patch_centers': len(centers),
            'removed_centers': centers}


def quad_topology(vertex_count: int, faces: list[tuple[int, ...]]) -> dict:
    """Audit edge incidence, directed winding, link cycles, connectivity and Euler."""
    require(vertex_count > 0 and len(faces) > 0, 'Missing QUAD surface')
    incidences = defaultdict(list)
    links = defaultdict(list)
    neighbor = defaultdict(set)
    referenced = set()
    for fid, face in enumerate(faces):
        require(len(face) == 4 and len(set(face)) == 4 and
                all(type(i) is int and 0 <= i < vertex_count for i in face),
                'Malformed QUAD indices')
        referenced.update(face)
        for j in range(4):
            a, b, c = face[(j-1)%4], face[j], face[(j+1)%4]
            key = tuple(sorted((b, c)))
            incidences[key].append((fid, b, c))
            neighbor[b].update((a, c))
            links[b].append((a, c))
    require(len(referenced) == vertex_count, 'Unused exported QUAD vertex')
    boundary = sum(len(vals) == 1 for vals in incidences.values())
    nonmanifold_edges = sum(len(vals) > 2 for vals in incidences.values())
    winding_conflicts = sum(len(vals) == 2 and
                            not (vals[0][1] == vals[1][2] and vals[0][2] == vals[1][1])
                            for vals in incidences.values())
    require(boundary == 0 and nonmanifold_edges == 0 and winding_conflicts == 0 and
            all(len(vals) == 2 for vals in incidences.values()),
            'QUAD surface is not consistently oriented and edge-manifold closed')
    singular = 0
    for v in referenced:
        graph = defaultdict(set)
        for a,b in links[v]:
            graph[a].add(b)
            graph[b].add(a)
        if not graph or any(len(n) != 2 for n in graph.values()):
            singular += 1
            continue
        seed = next(iter(graph))
        reached = {seed}
        stack = [seed]
        while stack:
            x = stack.pop()
            for y in graph[x]:
                if y not in reached:
                    reached.add(y)
                    stack.append(y)
        if len(reached) != len(graph):
            singular += 1
    require(singular == 0, 'QUAD has singular vertex-link topology')
    seen = set()
    components = 0
    for seed in referenced:
        if seed in seen:
            continue
        components += 1
        seen.add(seed)
        queue = [seed]
        while queue:
            v = queue.pop()
            for w in neighbor[v]:
                if w not in seen:
                    seen.add(w)
                    queue.append(w)
    return {'vertices': vertex_count, 'edges': len(incidences), 'faces': len(faces),
            'components': components, 'boundary_edges': boundary,
            'nonmanifold_edges': nonmanifold_edges, 'winding_conflicts': winding_conflicts,
            'singular_vertex_links': singular,
            'euler': vertex_count - len(incidences) + len(faces)}


def normal(a, b, c):
    return f27.cross(f27.vec(b, a), f27.vec(c, a))


def quad_metric(face: tuple[int, ...], xyz: list[tuple[float, ...]],
                reference_normal: tuple[float, ...]) -> dict:
    """Validate convex planar winding and compute dimensionless corner metrics."""
    points = [xyz[i] for i in face]
    normal_len = math.sqrt(f27.dot(reference_normal, reference_normal))
    require(normal_len > 0, 'Reference STL facet has zero area')
    n = tuple(x/normal_len for x in reference_normal)
    signed_jacobians = []
    angles = []
    plane = [abs(f27.dot(f27.vec(p, points[0]), n)) for p in points]
    require(max(plane) <= MAX_CORNER_PLANE_RESIDUAL,
            'QUAD is not planar on the original source facet')
    for j in range(4):
        prev = f27.vec(points[(j-1)%4], points[j])
        nxt = f27.vec(points[(j+1)%4], points[j])
        a = math.sqrt(f27.dot(prev, prev))
        b = math.sqrt(f27.dot(nxt, nxt))
        require(min(a,b) > 0 and math.isfinite(a*b), 'Degenerate QUAD side')
        cross = f27.cross(nxt, prev)
        signed = f27.dot(cross, n)
        require(signed > 0, 'Reflex, reversed, or zero-area quadrilateral corner')
        signed_jacobians.append(signed/(a*b))
        angles.append(math.degrees(math.atan2(signed, f27.dot(prev, nxt))))
    area = f27.area(points[0], points[1], points[2]) + f27.area(points[0], points[2], points[3])
    require(area > 0 and math.isfinite(area), 'Zero-area quadrilateral')
    return {'area': area, 'min_angle_deg': min(angles), 'max_angle_deg': max(angles),
            'min_scaled_jacobian': min(signed_jacobians),
            'max_plane_residual': max(plane)}


def source_edge_feature_coverage(source, original_tags, retained_indices, faces):
    """Ensure the original STL edges and creases survive as paired QUAD edges."""
    tag_to_reindexed = {original_tags[old]: new for new, old in enumerate(retained_indices)}
    require(len(tag_to_reindexed) == len(retained_indices), 'Distinct source entities were collapsed')
    incidence = defaultdict(list)
    for qi, q in enumerate(faces):
        for i in range(4):
            incidence[tuple(sorted((q[i], q[(i+1)%4])))].append(qi//3)
    source_edge_faces = defaultdict(list)
    source_normals = []
    for fid, tri in enumerate(source):
        n = normal(*tri)
        nlen = math.sqrt(f27.dot(n, n))
        require(nlen > 0, 'Degenerate original STL normal')
        source_normals.append(tuple(x/nlen for x in n))
        for i in range(3):
            source_edge_faces[f28.edge_key(tri[i],tri[(i+1)%3])].append(fid)
    require(len(source_edge_faces) == EXPECTED_SOURCE_EDGES and
            all(len(owners) == 2 for owners in source_edge_faces.values()),
            'Original STL is not the expected closed manifold')
    sharp = 0
    for (a,b), owners in source_edge_faces.items():
        ix_a = tag_to_reindexed[('vertex', a)]
        ix_b = tag_to_reindexed[('vertex', b)]
        mid = tag_to_reindexed[('edge', f28.edge_key(a,b))]
        for u,v in ((ix_a,mid),(mid,ix_b)):
            actual = incidence[tuple(sorted((u,v)))]
            require(len(actual) == 2 and set(actual) == set(owners),
                    'Original STL crease/source edge was removed or wrongly crossed')
        cosine = max(-1., min(1., f27.dot(source_normals[owners[0]],source_normals[owners[1]])))
        sharp += math.degrees(math.acos(cosine)) >= 30.0
    require(sharp == EXPECTED_SOURCE_SHARPS, 'Original sharp-edge census changed')
    return {'original_stl_edges': EXPECTED_SOURCE_EDGES,
            'source_edge_segments_retained': 2*EXPECTED_SOURCE_EDGES,
            'original_sharp30_edges': sharp,
            'sharp30_segments_retained': 2*sharp,
            'facet_crossing_pairs': 0}


def verify_real_quad(source, expected_stitched_bytes: bytes, result) -> dict:
    """Reconstruct original quad patch footprint from validated F27/F28 TRI graph."""
    require(len(source) == EXPECTED_SOURCE_FACETS and len(result['faces']) == EXPECTED_NATIVE_TRIS,
            'Original model/source records not fully covered')
    require(sha256_bytes(expected_stitched_bytes) == F28_STITCHED_SHA256 and
            len(expected_stitched_bytes) == F28_STITCHED_BYTES,
            'F28 source-topology-stitched input identity changed')
    recovered = reconstruct_patch_quads(result['vertices'], result['faces'], result['tags'])
    require(len(recovered['quads']) == EXPECTED_PATCHES and
            len(recovered['vertices']) == EXPECTED_QUAD_VERTICES and
            recovered['removed_patch_centers'] == EXPECTED_PATCHES,
            'Expected original STL three-QUAD-per-TRI partition changed')
    topo = quad_topology(len(recovered['vertices']), recovered['quads'])
    require((topo['vertices'], topo['edges'], topo['faces'], topo['components'], topo['euler']) ==
            (878, 1752, 876, 1, 2), 'Derived QUAD topology fails closed genus-zero gate')
    full = result['full_xyz']
    full_indices = recovered['full_original_vertex_indices']
    full_reindexed = [full[i] for i in full_indices]
    metrics = []
    max_area_error = 0.0
    for i, q in enumerate(recovered['quads']):
        source_triangle = source[i//3]
        reference = normal(*source_triangle)
        metric = quad_metric(q, full_reindexed, reference)
        triangles = result['faces'][4*i:4*i+4]
        original_4tri_area = math.fsum(f27.area(full[t[0]], full[t[1]], full[t[2]])
                                       for t in triangles)
        relative = abs(metric['area']-original_4tri_area)/max(original_4tri_area,1e-100)
        require(relative <= MAX_RELATIVE_AREA_ERROR,
                'Recovered quad loses area relative to original native four TRI')
        max_area_error = max(max_area_error,relative)
        metrics.append(metric)
    source_total = math.fsum(f27.area(*tri) for tri in source)
    quad_total = math.fsum(m['area'] for m in metrics)
    require(abs(source_total-quad_total)/source_total <= MAX_RELATIVE_AREA_ERROR,
            'Recovered original QUAD patch area not equal to original STL area')
    crease = source_edge_feature_coverage(source,result['tags'],full_indices,recovered['quads'])
    angles_lo = [m['min_angle_deg'] for m in metrics]
    angles_hi = [m['max_angle_deg'] for m in metrics]
    jac = [m['min_scaled_jacobian'] for m in metrics]
    require(min(jac) > 0 and all(math.isfinite(x) for x in jac),
            'Recovered QUAD has zero or invalid scaled Jacobian')
    return {'reconstructed': recovered, 'topology': topo,
            'quality': {'min_angle_deg': min(angles_lo), 'max_angle_deg': max(angles_hi),
                        'mean_min_angle_deg': math.fsum(angles_lo)/len(angles_lo),
                        'min_scaled_jacobian': min(jac),
                        'mean_min_scaled_jacobian': math.fsum(jac)/len(jac),
                        'count_min_angle_below_10_deg': sum(a < 10 for a in angles_lo),
                        'count_min_angle_below_30_deg': sum(a < 30 for a in angles_lo),
                        'count_max_angle_above_150_deg': sum(a > 150 for a in angles_hi),
                        'max_relative_quad_to_native_tri_patch_area_error': max_area_error,
                        'max_quad_plane_residual': max(m['max_plane_residual'] for m in metrics)},
            'source_facet_area': source_total,'quad_area_full_precision': quad_total,
            'source_feature_retention': crease}


def emit_private_quad_obj(stitched_obj: Path, recovered: dict) -> bytes:
    """Reindex the already verified F28 XYZ lines; emit explicit four-node faces."""
    lines = stitched_obj.read_text(encoding='utf-8').splitlines()
    vertices = [x for x in lines if x.startswith('v ')]
    require(len(vertices) == len(recovered['full_original_vertex_indices']) +
            recovered['removed_patch_centers'], 'Unexpected F28 OBJ node count')
    original_faces = [x for x in lines if x.startswith('f ')]
    require(len(original_faces) == 4 * len(recovered['quads']),
            'Unexpected input source TRI mesh count')
    rows = [
        '# Experimental recovered original-STL patch QUAD; NOT native APMesh QUAD output',
        '# Source F28 stitched private TRI SHA256 ' + f27.sha256(stitched_obj),
        '# Each QUAD replaces one verified original Bezier patch 4-TRI center fan',
        '# No smoothing, new XYZ, arbitrary triangle pairing or silent seam welding',
    ]
    rows.extend(vertices[i] for i in recovered['full_original_vertex_indices'])
    rows.extend('f ' + ' '.join(str(i+1) for i in q) for q in recovered['quads'])
    return ('\n'.join(rows) + '\n').encode('utf-8')


def run_real_private(zip_path: Path, bp: Path, first: Path, second: Path,
                     stitched_obj: Path, private_out: Path, receipt_path: Path) -> dict:
    """Verify two genuine native runs before creating a separate private QUAD artifact."""
    require(not private_out.exists() and not receipt_path.exists(),
            'Refuse to overwrite private QUAD output or public receipt')
    a = f28.evaluate_run(zip_path,bp,first)
    b = f28.evaluate_run(zip_path,bp,second)
    require(a[-1] == b[-1] == stitched_obj.read_bytes(),
            'F28 recovery input differs between original native runs')
    source = f27.parse_source(zip_path)
    res_a = verify_real_quad(source,a[-1],a[1])
    res_b = verify_real_quad(source,b[-1],b[1])
    quad_bytes_a = emit_private_quad_obj(stitched_obj,res_a['reconstructed'])
    quad_bytes_b = emit_private_quad_obj(stitched_obj,res_b['reconstructed'])
    require(quad_bytes_a == quad_bytes_b, 'Derived QUAD not byte identical across runs')
    require(res_a['topology'] == res_b['topology'] and res_a['quality'] == res_b['quality'],
            'Derived QUAD quantitative evidence not identical across runs')
    private_out.mkdir(parents=True,mode=0o700)
    obj_file = private_out/'293137_derived_patch_quad_NOT_NATIVE_APMESH.obj'
    with obj_file.open('xb') as f:
        f.write(quad_bytes_a)
    receipt = {
        'schema': 'apmesh-s40-f29-external-quad-patch-recovery-v1',
        'status': 'PRIVATE_DERIVED_QUAD_PATCH_RECOVERY_VALIDATED_NOT_NATIVE_APMESH_QUAD',
        'original_native_tri_run_count': 2,
        'model_id': 293137,
        'original_stl_sha256': f27.STL_SHA256,
        'input_bp_sha256': f27.BP_SHA256,
        'original_native_tri_obj_sha256': f27.sha256(first/'bunny_passo_0_malha_0.obj'),
        'f28_private_stitched_tri_obj_sha256': F28_STITCHED_SHA256,
        'private_derived_quad_obj_sha256': sha256_bytes(quad_bytes_a),
        'private_derived_quad_obj_size_bytes': len(quad_bytes_a),
        'quad_topology': res_a['topology'],
        'quad_quality_nontriangular_metrics': res_a['quality'],
        'source_stl_total_area_full_precision': res_a['source_facet_area'],
        'quad_total_area_full_precision': res_a['quad_area_full_precision'],
        'source_feature_retention': res_a['source_feature_retention'],
        'discarded_original_patch_center_nodes': res_a['reconstructed']['removed_patch_centers'],
        'new_vertex_coordinates_added': 0,
        'native_original_quad_generator_executed': False,
        'native_tri_mesher_original_output_untouched': True,
        'source_stl_cad_freeform_restored': False,
        'scientific_reference_comparison_admitted': False,
        'copyright_license_cleared': False,
        'published_source_or_derived_geometry': False,
    }
    with receipt_path.open('x',encoding='utf-8') as f:
        json.dump(receipt,f,indent=2,sort_keys=True,allow_nan=False)
        f.write('\n')
    return receipt


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root',type=Path)
    parser.add_argument('--source-zip',type=Path)
    parser.add_argument('--private-bp',type=Path)
    parser.add_argument('--native-run-1',type=Path)
    parser.add_argument('--native-run-2',type=Path)
    parser.add_argument('--f28-private-stitched-obj',type=Path)
    parser.add_argument('--private-output-dir',type=Path)
    parser.add_argument('--public-receipt',type=Path)
    args=parser.parse_args()
    if args.source_root:
        print(json.dumps(audit_native_original_quad_capability(args.source_root),sort_keys=True))
        return
    required=(args.source_zip,args.private_bp,args.native_run_1,args.native_run_2,
              args.f28_private_stitched_obj,args.private_output_dir,args.public_receipt)
    require(all(x is not None for x in required),'Missing private QUAD replay arguments')
    receipt=run_real_private(*required)
    print(json.dumps({'status':receipt['status'],'quad_faces':receipt['quad_topology']['faces'],
                      'quad_vertices':receipt['quad_topology']['vertices'],
                      'output_sha256':receipt['private_derived_quad_obj_sha256']},sort_keys=True))


if __name__=='__main__':
    try:
        main()
    except (ValueError,TypeError,IndexError,KeyError,OSError) as ex:
        raise SystemExit('F29 QUAD evidence gate rejected: '+str(ex)) from ex
