#!/usr/bin/env python3
"""Build a private, conservative bicubic BP representation of a pinned binary STL.

Every STL triangle is split into three bilinear quadrilaterals, degree elevated
into bicubic Bézier patches. No smoothing, repair, source rights or native APMesh
meshing is inferred. No third-party geometry belongs in the research repository.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import struct
import zipfile

F17_INPUT_SHA256 = '4a222346223cf2c207c34d7a3d4e8ea297b004ff862b06b6e4c7c2eeac9f761a'
F17_ZIP_GIT_SHA1 = '359c26b16664e9ba8d2415ca065a85bd27504d5f'
MODEL_ID = 293137
MAX_ZIP_BYTES = 1_000_000
MAX_STL_BYTES = 3_000_000
MERGE_TOLERANCE = 1e-7
SIDES = ((0, 1, 2, 3), (3, 7, 11, 15), (12, 13, 14, 15), (0, 4, 8, 12))


@dataclass(frozen=True)
class Pin:
    model_id: int
    git_zip_sha1: str
    raw_stl_sha256: str
    triangles: int
    zip_size: int | None = None


PIN = Pin(MODEL_ID, F17_ZIP_GIT_SHA1, F17_INPUT_SHA256, 292, 7073)


def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode('ascii') + data).hexdigest()


def read_pinned_binary_stl_zip(path: Path, pin: Pin = PIN) -> bytes:
    require(path.is_file() and 0 < path.stat().st_size <= MAX_ZIP_BYTES,
            'Missing or oversized source ZIP')
    raw_zip = path.read_bytes()
    if pin.zip_size is not None:
        require(len(raw_zip) == pin.zip_size, 'Source ZIP byte size changed')
    require(git_blob_sha(raw_zip) == pin.git_zip_sha1, 'Original ZIP Git blob mismatch')
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        require(len(members) == 1 and members[0].filename == f'{pin.model_id}.stl',
                'Unexpected STL ZIP member identity')
        item = members[0]
        require(not item.is_dir() and item.flag_bits & 1 == 0 and
                item.file_size == 84 + 50 * pin.triangles and
                0 < item.compress_size <= MAX_ZIP_BYTES and
                item.file_size <= MAX_STL_BYTES,
                'Source ZIP member does not match expected bounded binary STL')
        stl = archive.read(item)  # zipfile validates original ZIP entry CRC32.
    require(len(stl) == 84 + 50 * pin.triangles, 'Unexpected binary STL byte length')
    require(hashlib.sha256(stl).hexdigest() == pin.raw_stl_sha256,
            'Original decompressed STL SHA-256 mismatch')
    require(struct.unpack_from('<I', stl, 80)[0] == pin.triangles,
            'Source STL facet header count changed')
    return stl


def vec_sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def length(v):
    return math.sqrt(dot(v, v))


def vec_mean3(a, b, c):
    return tuple((x + y + z) / 3.0 for x, y, z in zip(a, b, c))


def vec_mid(a, b):
    return tuple((x + y) / 2.0 for x, y in zip(a, b))


def parse_source(stl: bytes, expected_triangles: int):
    require(len(stl) == 84 + 50 * expected_triangles, 'STL size mismatches triangle count')
    require(struct.unpack_from('<I', stl, 80)[0] == expected_triangles,
            'STL header/count mismatch')
    vertices, index, faces = [], {}, []
    for t in range(expected_triangles):
        offset = 84 + t * 50
        points = struct.unpack_from('<9f', stl, offset + 12)
        require(all(math.isfinite(v) for v in points), 'Nonfinite STL coordinates')
        face = []
        for k in range(3):
            p = tuple(float(points[3 * k + d]) for d in range(3))
            # Reconstruct STL connectivity with exact float32 XYZ, never epsilon weld.
            if p not in index:
                index[p] = len(vertices)
                vertices.append(p)
            face.append(index[p])
        require(len(set(face)) == 3, 'Repeated source triangle vertex')
        a, b, c = (vertices[q] for q in face)
        require(length(cross(vec_sub(b, a), vec_sub(c, a))) > 0,
                'Degenerate source triangle')
        faces.append(tuple(face))
    return vertices, faces


def source_edges(vertices, faces):
    uses = defaultdict(list)
    fkeys = set()
    normal = []
    for fi, face in enumerate(faces):
        fkey = tuple(sorted(face))
        require(fkey not in fkeys, 'Duplicate source triangle')
        fkeys.add(fkey)
        a, b, c = (vertices[i] for i in face)
        n = cross(vec_sub(b, a), vec_sub(c, a))
        normal.append(tuple(x / length(n) for x in n))
        for i in range(3):
            s, t = face[i], face[(i + 1) % 3]
            uses[(min(s, t), max(s, t))].append((fi, s, t))
    require(all(len(e) == 2 and e[0][1] == e[1][2] and e[0][2] == e[1][1]
                for e in uses.values()), 'Source not a closed consistently oriented triangle surface')
    neighbors = defaultdict(set)
    for edge, occurrences in uses.items():
        (f1, _, _), (f2, _, _) = occurrences
        neighbors[f1].add(f2)
        neighbors[f2].add(f1)
    stack = [0]
    visited = set()
    while stack:
        x = stack.pop()
        if x not in visited:
            visited.add(x)
            stack.extend(neighbors[x] - visited)
    require(len(visited) == len(faces), 'Source contains disconnected face components')
    # Verify each source vertex has a single closed fan, not merely bivalent edges.
    incident_faces = defaultdict(set)
    for fi, face in enumerate(faces):
        for v in face:
            incident_faces[v].add(fi)
    for vertex, incident in incident_faces.items():
        local = {fi: set() for fi in incident}
        for edge, occurrences in uses.items():
            if vertex in edge:
                fi, fj = occurrences[0][0], occurrences[1][0]
                local[fi].add(fj)
                local[fj].add(fi)
        reached = set()
        todo = [next(iter(incident))]
        while todo:
            f = todo.pop()
            if f not in reached:
                reached.add(f)
                todo.extend(local[f] - reached)
        require(reached == incident and all(len(x) == 2 for x in local.values()),
                'Source contains singular vertex links')
    chi = len(vertices) - len(uses) + len(faces)
    require(chi <= 2 and (2 - chi) % 2 == 0,
            'Source Euler is not a connected closed orientable surface')
    feature = 0
    for occurrences in uses.values():
        i, j = occurrences[0][0], occurrences[1][0]
        angle = math.degrees(math.acos(max(-1.0, min(1.0, dot(normal[i], normal[j])))))
        if angle >= 30.0:
            feature += 1
    return uses, {'source_exact_vertices': len(vertices), 'source_edges': len(uses),
                  'source_triangles': len(faces), 'source_euler': chi,
                  'source_genus': (2 - chi) // 2,
                  'feature_edges_at_30deg_proxy': feature}


def linear_net(a, b):
    """Canonical deterministic cubic controls of a straight shared edge."""
    return (a, tuple((2 * a[d] + b[d]) / 3 for d in range(3)),
            tuple((a[d] + 2 * b[d]) / 3 for d in range(3)), b)


def bilinear(corners, u, v):
    a, b, c, d = corners
    return tuple((1 - u) * (1 - v) * a[k] + u * (1 - v) * b[k] +
                 u * v * c[k] + (1 - u) * v * d[k] for k in range(3))


def controls_for_quad(corners, ids):
    net = [None] * 16
    for j in range(4):
        for i in range(4):
            net[j * 4 + i] = bilinear(corners, i / 3, j / 3)
    lookup = dict(zip(ids, corners))
    for side in SIDES:
        # Map the four sides in BP indexing to their quadrilateral corner IDs.
        if side == SIDES[0]:
            a_id, b_id = ids[0], ids[1]
        elif side == SIDES[1]:
            a_id, b_id = ids[1], ids[2]
        elif side == SIDES[2]:
            a_id, b_id = ids[3], ids[2]
        else:
            a_id, b_id = ids[0], ids[3]
        if a_id < b_id:
            points = linear_net(lookup[a_id], lookup[b_id])
        else:
            points = tuple(reversed(linear_net(lookup[b_id], lookup[a_id])))
        for i, loc in enumerate(side):
            net[loc] = points[i]
    require(all(v is not None for v in net), 'Uninitialized control point')
    return tuple(net)


def jacobian_ratios(corners, tri_vertices):
    a, b, c, d = corners
    p, q, r = tri_vertices
    n = cross(vec_sub(q, p), vec_sub(r, p))
    den = dot(n, n)
    require(den > 0, 'Source triangle has zero cross-product area')
    samples = (
        (vec_sub(b, a), vec_sub(d, a)),
        (vec_sub(b, a), vec_sub(c, b)),
        (vec_sub(c, d), vec_sub(c, b)),
        (vec_sub(c, d), vec_sub(d, a)),
    )
    ratios = [dot(cross(du, dv), n) / den for du, dv in samples]
    require(all(x > 0 and math.isfinite(x) for x in ratios), 'Nonpositive bilinear Jacobian')
    return ratios


def collision_counts(points: list[tuple[float, float, float]], tol: float = MERGE_TOLERANCE):
    """Bounded spatial hash mimics the legacy component-wise reader merge criterion."""
    grid = defaultdict(list)
    count = 0
    for p in points:
        cell = tuple(math.floor(v / tol) for v in p)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for other in grid.get((cell[0]+dx,cell[1]+dy,cell[2]+dz), ()):
                        if p != other and all(abs(x-y) <= tol for x,y in zip(p,other)):
                            count += 1
        grid[cell].append(p)
    return count


def build_patch_domain(vertices, faces, edge_uses):
    """Construct 3F index-quad patches with shared deterministic cubic seam nets."""
    original_count = len(vertices)
    ekeys = sorted(edge_uses)
    patch_vertices = list(vertices)
    midindex = {}
    for key in ekeys:
        midindex[key] = len(patch_vertices)
        patch_vertices.append(vec_mid(vertices[key[0]], vertices[key[1]]))
    centroids = []
    for face in faces:
        centroids.append(len(patch_vertices))
        patch_vertices.append(vec_mean3(*(vertices[i] for i in face)))
    quads, nets, min_ratio, max_ratio = [], [], math.inf, -math.inf
    sample_errors = []
    for fi, face in enumerate(faces):
        a, b, c = face
        eab = midindex[(min(a,b),max(a,b))]
        ebc = midindex[(min(b,c),max(b,c))]
        eca = midindex[(min(c,a),max(c,a))]
        for quad in ((a,eab,centroids[fi],eca),
                     (b,ebc,centroids[fi],eab),
                     (c,eca,centroids[fi],ebc)):
            corners = tuple(patch_vertices[i] for i in quad)
            ratios = jacobian_ratios(corners, tuple(vertices[i] for i in face))
            min_ratio, max_ratio = min(min_ratio, *ratios), max(max_ratio, *ratios)
            net = controls_for_quad(corners, quad)
            # Compare an independent de Casteljau evaluation with direct bilinear geometry.
            for u,v in ((0.25,0.375),(0.5,0.5),(0.75,0.125)):
                evalp = eval_bicubic(net, u, v)
                truep = bilinear(corners, u, v)
                sample_errors.append(length(vec_sub(evalp, truep)))
            quads.append(quad)
            nets.append(net)
    seam_uses = defaultdict(list)
    for qi, quad in enumerate(quads):
        for side in range(4):
            x, y = quad[side], quad[(side+1)%4]
            if side == 0:
                seq = tuple(nets[qi][i] for i in SIDES[0])
            elif side == 1:
                seq = tuple(nets[qi][i] for i in SIDES[1])
            elif side == 2:
                seq = tuple(reversed(tuple(nets[qi][i] for i in SIDES[2])))
            else:
                seq = tuple(reversed(tuple(nets[qi][i] for i in SIDES[3])))
            seam_uses[(min(x,y),max(x,y))].append((qi,x,y,seq))
    require(all(len(uses)==2 for uses in seam_uses.values()),
            'Unexpected unpaired quad-domain edge')
    for uses in seam_uses.values():
        (fa,a,b,seq1),(fb,c,d,seq2) = uses
        require(fa!=fb and a==d and b==c and seq1==tuple(reversed(seq2)),
                'Shared source curve control mismatch or orientation conflict')
    chi = len(patch_vertices) - len(seam_uses) + len(quads)
    require(chi == len(vertices) - len(edge_uses) + len(faces),
            'Four-sided patch partition changes source Euler')
    require(len(quads) == 3*len(faces) and
            len(patch_vertices)==len(vertices)+len(edge_uses)+len(faces) and
            len(seam_uses)==2*len(edge_uses)+3*len(faces),
            'Unexpected quad split combinatorics')
    interned = {}
    controls = []
    patch_indices=[]
    for net in nets:
        inds=[]
        for p in net:
            if p not in interned:
                interned[p] = len(controls)
                controls.append(p)
            inds.append(interned[p])
        patch_indices.append(tuple(inds))
    collisions=collision_counts(controls)
    return {
        'patch_vertices':len(patch_vertices),
        'patch_edges':len(seam_uses),
        'bicubic_patches':len(quads),
        'euler':chi,
        'two_patch_seams':len(seam_uses),
        'unpaired_or_multiple_seams':0,
        'unique_bp_control_vertices':len(controls),
        'legacy_reader_near_distinct_control_pairs':collisions,
        'normalized_min_bilinear_jacobian_corner':min_ratio,
        'normalized_max_bilinear_jacobian_corner':max_ratio,
        'sample_bicubic_vs_source_bilinear_max_distance':max(sample_errors,default=None),
        'no_native_apmesh_execution':True,
        'no_cad_smoothing':True,
    },controls,patch_indices


def eval_cubic_curve(cp,t):
    a=list(cp)
    while len(a)>1:
        a=[tuple((1-t)*x+t*y for x,y in zip(a[i],a[i+1])) for i in range(len(a)-1)]
    return a[0]


def eval_bicubic(net,u,v):
    rows=[eval_cubic_curve(net[j*4:(j+1)*4],u) for j in range(4)]
    return eval_cubic_curve(rows,v)


def serialize_bp(controls,patch_indices):
    def coord(x):
        return format(x,'.17g')
    lines=['v '+' '.join(map(coord,p)) for p in controls]
    lines += ['p '+' '.join(map(str,indices)) for indices in patch_indices]
    return ('\n'.join(lines)+'\n').encode('utf-8')


def execute(path:Path,pin:Pin=PIN):
    raw = read_pinned_binary_stl_zip(path,pin)
    vertices,faces=parse_source(raw,pin.triangles)
    edges,source=source_edges(vertices,faces)
    domain,controls,patches=build_patch_domain(vertices,faces,edges)
    if pin==PIN:
        require((source['source_exact_vertices'],source['source_edges'],source['source_triangles'],source['source_genus'])
                ==(148,438,292,0), 'Pinned source topology differs from F17')
    model=serialize_bp(controls,patches)
    status=('CANDIDATE_BP_GEOMETRY_CONSTRUCTED_READER_MERGE_RISK' if domain['legacy_reader_near_distinct_control_pairs'] else
            'CANDIDATE_BP_GEOMETRY_CONSTRUCTED_NOT_APMESH_TESTED')
    receipt={
        'schema':'apmesh-thingi10k-f21-private-piecewise-linear-bicubic-v1',
        'source_model_id':pin.model_id,
        'source_mirror_zip_git_blob_sha1':pin.git_zip_sha1,
        'source_binary_stl_sha256':pin.raw_stl_sha256,
        'status':status,
        'source':source,'patch_domain':domain,
        'patch_bp_sha256':hashlib.sha256(model).hexdigest(),
        'patch_bp_bytes':len(model),
        'geometry_interpretation':'piecewise_linear_surface_exact_in_real_arithmetic_no_smoothing',
        'source_stl_units_known':False,
        'upstream_original_author_equivalence_proved':False,
        'third_party_license_cleared':False,
        'private_bp_candidate_written':False,
        'third_party_geometry_published':False,
        'native_apmesh_patch_reader_executed':False,
        'native_apmesh_tri_or_quad_meshing_executed':False,
        'scientific_model_admission':False,
    }
    return receipt,model


def write_private_result(receipt: dict, bp: bytes, receipt_path: Path,
                         bp_path: Path | None) -> None:
    """Publish only into new private files; roll back both on partial failures."""
    require(bp_path is None or bp_path != receipt_path,
            'BP and receipt output paths must differ')
    require(receipt_path.parent.is_dir() and
            (bp_path is None or bp_path.parent.is_dir()),
            'A private output parent directory does not exist')
    require(not receipt_path.exists() and (bp_path is None or not bp_path.exists()),
            'Refuse to replace an existing original or result')
    require(hashlib.sha256(bp).hexdigest() == receipt['patch_bp_sha256'],
            'Candidate BP changed after geometry audit')
    require(bp_path is None or receipt['patch_domain']['legacy_reader_near_distinct_control_pairs'] == 0,
            'BP candidate not written: legacy loader may merge distinct control points')
    report = dict(receipt)
    if bp_path is not None:
        report['private_bp_candidate_written'] = True
        report['private_candidate_bp_path'] = str(bp_path)
    created_bp = created_receipt = False
    try:
        if bp_path is not None:
            with bp_path.open('xb') as stream:
                created_bp = True
                stream.write(bp)
        with receipt_path.open('x', encoding='utf-8') as stream:
            created_receipt = True
            json.dump(report, stream, sort_keys=True, indent=2)
            stream.write('\n')
    except BaseException:
        if created_receipt:
            receipt_path.unlink(missing_ok=True)
        if created_bp:
            bp_path.unlink(missing_ok=True)
        raise


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-zip',type=Path,required=True)
    p.add_argument('--private-output-bp',type=Path)
    p.add_argument('--private-receipt',type=Path,required=True)
    a=p.parse_args(argv)
    require(not a.private_receipt.exists() and
            (a.private_output_bp is None or not a.private_output_bp.exists()),
            'Refuse to replace an existing original or result')
    receipt, bp = execute(a.source_zip)
    write_private_result(receipt, bp, a.private_receipt, a.private_output_bp)
    print(json.dumps({**receipt, 'private_bp_candidate_written':
                      a.private_output_bp is not None},sort_keys=True,indent=2))
    return 0


if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (OSError,ValueError,zipfile.BadZipFile) as exc:
        raise SystemExit('F21 candidate blocked: '+str(exc)) from exc
