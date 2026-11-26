"""Select one witnessed post-smoothing repair from a native single-patch archive."""

import argparse
from collections import Counter, defaultdict
import csv
from functools import lru_cache
from itertools import combinations
import json
from math import atan2, dist, floor, isfinite
from pathlib import Path
from statistics import median

from quad_generation_metrics import cross, element_quality, load_physical_obj
from quad_grouping_trial import digest, write_json
from quad_portable_feedback_trial import source_hashes
from quad_progressive_admission import boundary_certificate, load_profile, source_evaluator
from quad_transition_comparison import edges, intersection_area, orient


MAX_FRONT_FACES = 6
MAX_SITES = 14
MAX_LAYOUTS = 1024
MAX_RETENTION_TRIALS = 1024
MAX_STATES = 25000
EPS = 1e-14
SIZE_EPS = 2e-13


def canonical(face):
    face = tuple(face)
    start = face.index(min(face))
    return face[start:] + face[:start]


def directed_ring(faces):
    counts = Counter(edge for face in faces for edge in edges(face))
    if any(n != 1 for n in counts.values()):
        return ()
    boundary = [(a, b) for a, b in counts if (b, a) not in counts]
    pending = dict(boundary)
    if not pending or len(pending) != len(boundary):
        return ()
    first = min(pending)
    ring = [first]
    while ring[-1] in pending:
        target = pending.pop(ring[-1])
        if target == first:
            return tuple(ring) if not pending else ()
        ring.append(target)
    return ()


def on_segment(a, b, p):
    return abs(orient(a, b, p)) <= EPS and all(
        min(x, y) <= z <= max(x, y) for x, y, z in zip(a, b, p))


def inside_ring(p, ring):
    inside = False
    for a, b in edges(ring):
        if on_segment(a, b, p):
            return True
        if (a[1] > p[1]) != (b[1] > p[1]):
            cut = a[0] + (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1])
            inside ^= p[0] < cut
    return inside


def strictly_opposite(a, b):
    return min(a, b) < -EPS and max(a, b) > EPS


def contains(polygon, site):
    return all(orient(a, b, site) >= -SIZE_EPS for a, b in edges(polygon))


def quality(xyz, uv, face, normal, floors):
    metrics = element_quality(xyz, uv, face, normal)
    kind = metrics["kind"]
    limits = floors[kind]
    shape = metrics["tri_q"] if kind == "TRI" else metrics["quad_corner_jacobian"]
    angle = metrics["min_angle_xyz"]
    return min(angle / limits["min_angle_deg"], shape / limits["min_shape"]), metrics


def find_layout(ring, inner, uv, xyz, normal, floors, claims, budget, states):
    """Tile the directed ring with convex faces at the given existing sites."""
    sites = ring + inner
    required = set(sites)
    perimeter = frozenset(edges(ring))
    boundary = [uv[i] for i in ring]
    by_edge = defaultdict(list)
    polygons = {}

    @lru_cache(None)
    def edge_ok(a, b):
        if (b, a) in perimeter:
            return False
        if (a, b) in perimeter:
            return True
        p, q = uv[a], uv[b]
        if any(j not in (a, b) and on_segment(p, q, uv[j]) for j in sites):
            return False
        if any(strictly_opposite(orient(p, q, r), orient(p, q, s))
               and strictly_opposite(orient(r, s, p), orient(r, s, q))
               for r, s in edges(boundary)):
            return False
        return inside_ring(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), boundary)

    for arity in (3, 4):
        for ids in combinations(sites, arity):
            u, v = (sum(uv[i][axis] for i in ids) / arity for axis in (0, 1))
            face = canonical(sorted(ids, key=lambda i: atan2(uv[i][1] - v, uv[i][0] - u)))
            if any(not edge_ok(a, b) for a, b in edges(face)):
                continue
            polygon = [uv[i] for i in face]
            if any(contains(polygon, uv[i]) for i in sites if i not in face):
                continue
            try:
                margin, metrics = quality(xyz, uv, face, normal, floors)
            except ValueError:
                continue
            if margin < 1 or (arity == 4 and metrics["S_uv"] > 1.5):
                continue
            h = median(dist(xyz[a], xyz[b]) for a, b in edges(face))
            if any(h > size and contains(polygon, site) for site, size in claims):
                continue
            polygons[face] = polygon
            for edge in edges(face):
                by_edge[edge].append(face)

    @lru_cache(None)
    def overlap(left, right):
        return intersection_area(polygons[left], polygons[right]) > EPS

    def search(open_edges, patch, covered):
        if not open_edges:
            return patch if covered == required else None
        if len(patch) >= budget or states["states"] >= MAX_STATES:
            return None
        states["states"] += 1
        edge = min(open_edges, key=lambda item: (len(by_edge[item]), item))
        for face in by_edge[edge]:
            sides = set(edges(face))
            reverse = {(b, a) for a, b in sides}
            if (face in patch or reverse & open_edges
                    or any(overlap(*sorted((face, other))) for other in patch)):
                continue
            remaining = (open_edges - sides) | {(b, a) for a, b in sides - open_edges}
            found = search(remaining, (*patch, face), covered.union(face))
            if found:
                return found
        return None

    return search(perimeter, (), set())


def patches(target, adjacency, seed_count):
    """Generate connected front sets and subsets of their immediately touching seed layer."""
    active = [(target,)] if target >= seed_count else [
        (j,) for j in adjacency[target] if j >= seed_count]
    active = set(active)
    seen = set()
    for _ in range(MAX_FRONT_FACES):
        following = set()
        for front in sorted(active):
            neighbors = set().union(*(adjacency[i] for i in front))
            layer = sorted(i for i in neighbors if i < seed_count)
            for n in range(1, min(len(layer), MAX_FRONT_FACES) + 1):
                for seeds in combinations(layer, n):
                    if target >= seed_count or target in seeds:
                        patch = tuple(sorted(front + seeds))
                        if patch not in seen:
                            seen.add(patch)
                            yield patch
            following.update(tuple(sorted((*front, j))) for j in neighbors
                             if j >= seed_count and j not in front)
        active = following


def select(faces, seed_count, birth_uv, uv, xyz, normal, floors, requests, protected, cap):
    incidence = defaultdict(set)
    vertex_faces = defaultdict(set)
    for i, face in enumerate(faces):
        for a, b in edges(face):
            incidence[min(a, b), max(a, b)].add(i)
        for v in face:
            vertex_faces[v].add(i)
    adjacency = [set() for _ in faces]
    for uses in incidence.values():
        for face in uses:
            adjacency[face].update(uses - {face})
    sizes = [median(dist(xyz[a], xyz[b]) for a, b in edges(face)) for face in faces]
    current = [[uv[v] for v in face] for face in faces]
    birth = [[birth_uv[v] for v in face] for face in faces]
    bound_requests = [
        (site, size, {i for i, poly in enumerate(birth) if contains(poly, site)},
         {i for i, poly in enumerate(current) if contains(poly, site)})
        for site, size in requests
    ]
    ranked = sorted((quality(xyz, uv, face, normal, floors)[0], i)
                    for i, face in enumerate(faces))
    ranked = [(margin, i) for margin, i in ranked if margin < 1]
    counts = Counter(layouts=0, states=0, ranked_faces=len(ranked))
    examined = set()
    for rank, (margin, target) in enumerate(ranked, 1):
        for patch in patches(target, adjacency, seed_count):
            if patch in examined:
                continue
            if counts["layouts"] >= MAX_LAYOUTS or counts["states"] >= MAX_STATES:
                return None, dict(counts, bound=True)
            examined.add(patch)
            counts["layouts"] += 1
            chosen = set(patch)
            ring = directed_ring([faces[i] for i in patch])
            if not ring:
                counts["not_a_disk"] += 1
                continue
            sites = {v for i in patch for v in faces[i]}
            if len(sites) > MAX_SITES:
                counts["site_limit"] += 1
                continue
            inner = sites - set(ring)
            required = {v for v in inner if v in protected or vertex_faces[v] - chosen}
            free = sorted(inner - required)
            claims = []
            for site, size, before, after in bound_requests:
                if not (before | after) & chosen:
                    continue
                outside = after - chosen
                if any(sizes[i] > size for i in outside):
                    counts["outside_size"] += 1
                    break
                if inside_ring(site, [uv[i] for i in ring]):
                    claims.append((site, size))
                elif not outside:
                    counts["missing_size_site"] += 1
                    break
            else:
                for n in range(len(free) + 1):
                    for retired in combinations(free, n):
                        if counts["retention_trials"] >= MAX_RETENTION_TRIALS:
                            return None, dict(counts, bound=True)
                        counts["retention_trials"] += 1
                        kept = tuple(sorted(inner - set(retired)))
                        witness = find_layout(ring, kept, uv, xyz, normal, floors, claims,
                                              cap - len(faces) + len(patch), counts)
                        if witness:
                            polys = [[uv[i] for i in face] for face in witness]
                            if any(not any(contains(poly, site) for poly in polys)
                                   for site, _ in claims):
                                raise ValueError("Replacement does not cover its local requests")
                            return dict(target=target, rank=rank, relative_quality=margin,
                                        replaced=patch, replacement=witness, retired=retired), dict(counts)
                        if counts["states"] >= MAX_STATES:
                            return None, dict(counts, bound=True)
    return None, dict(counts, bound=False)


def plan_action(root, profile_path):
    receipt = json.loads((root / "result.json").read_bytes())
    profile, fingerprint = load_profile(profile_path)
    source = root / "source.steps"
    feedback = root / "successor.steps/feedback"
    candidate = feedback / "candidate.obj"
    plan = root / "successor.plan"
    trace_path = feedback / "candidate_front/front.json"
    birth_path = feedback / "smoothing_comparison/before.obj"
    smooth_path = feedback / "smoothing_comparison/guarded_final.obj"
    request_path = feedback / "requests.csv"
    if (receipt["successor"]["status"] != "staged"
            or source_hashes(source) != receipt["source_sha256"]
            or digest(plan) != receipt["trial_plan_sha256"]
            or digest(candidate) != receipt["successor"]["candidate_sha256"]
            or receipt["progressive_admission"]["profile_sha256"] != fingerprint):
        raise ValueError("Control archive is incompatible with its native receipt or profile")
    certificate = boundary_certificate(source / "source.obj", candidate, feedback, receipt)
    if certificate is None:
        raise ValueError("Seed-layer replacement requires a certified curve")
    plan_text = plan.read_bytes()
    commands = [line.split() for line in plan_text.decode("ascii").splitlines()]
    if any(words and words[0] in {"replace_seed_layer", "replace_seed_layer_after_smoothing"}
           for words in commands):
        raise ValueError("The control plan already contains a seed-layer replacement")

    trace = json.loads(trace_path.read_bytes())
    seed_count = len(trace["seed_faces"])
    faces = [tuple(row) for row in trace["seed_faces"]]
    faces.extend(tuple(row["polygon"]) for row in trace["commits"])
    _, birth_uv, birth_faces = load_physical_obj(birth_path)
    xyz, uv, final_faces = load_physical_obj(candidate)
    smooth_xyz, smooth_uv, smooth_faces = load_physical_obj(smooth_path)
    if (list(map(tuple, trace["vertices"])) != birth_uv or len(birth_uv) != len(uv)
            or faces != birth_faces or faces != smooth_faces
            or len(set(map(canonical, faces))) != len(faces)
            or sorted(map(canonical, faces)) != sorted(map(canonical, final_faces))
            or xyz != smooth_xyz or uv != smooth_uv):
        raise ValueError("Native birth and smoothed archives do not have the same vertex binding")
    protected = {i for i, point in enumerate(birth_uv) if any(k in (0, 1) for k in point)}
    protected.update(row["introduced_vertex"] for row in trace["commits"]
                     if row.get("introduced_vertex") is not None)
    with request_path.open(newline="", encoding="ascii") as stream:
        requests = [(int(row["face"]), (float(row["u"]), float(row["v"])),
                     float(row["requested_size"]))
                    for row in csv.DictReader(stream)]
    base_requests = []
    for words in commands:
        if words[:1] == ["face"]:
            _, face, u, v, size = words
            base_requests.append((int(face), (float(u), float(v)), float(size)))
    if not requests or requests != base_requests or any(
            not (isfinite(size) and size > 0 and all(0 <= x <= 1 for x in point))
            for _, point, size in requests):
        raise ValueError("Archived physical size requests do not match the native plan")
    _, _, predecessor = load_physical_obj(source / "source.obj")
    if len(predecessor) != receipt["progressive_admission"]["predecessor_faces"]:
        raise ValueError("Predecessor face count does not match its native receipt")
    cap = min(profile["max_total_faces"], floor(len(predecessor) * (1 + profile["max_face_growth"])))
    evaluate = source_evaluator(root, receipt)

    @lru_cache(None)
    def normal(point):
        _, du, dv = evaluate(*point)
        return cross(du, dv)

    floors = profile["safety_floors"]
    selection, counts = select(faces, seed_count, birth_uv, uv, xyz, normal, floors,
                               [(point, size) for _, point, size in requests], protected, cap)
    status = "planned" if selection else "no_action" if not counts["ranked_faces"] else "bounded_refusal"
    evidence = dict(schema="apmesh.quad.auto_seed_layer_selection.v1", selection=selection,
                    status=status,
                    search=counts, face_cap=cap, profile_sha256=fingerprint,
                    inputs={path.name: digest(path) for path in
                            (candidate, plan, trace_path, birth_path, smooth_path, request_path)})
    if not selection:
        return None, evidence

    old, new = selection["replaced"], selection["replacement"]
    sites = sorted({v for i in old for v in faces[i]})
    rules = [floors[kind][key] for kind in ("TRI", "QUAD") for key in ("min_angle_deg", "min_shape")]
    header = ("replace_seed_layer_after_smoothing", cap, *rules, len(sites), len(old), len(new))
    rows = [header]
    rows.extend((v, *birth_uv[v]) for v in sites)
    rows.extend((i, len(faces[i]), *faces[i]) for i in old)
    rows.extend((len(face), *face) for face in new)
    suffix = "".join(" ".join(map(str, row)) + "\n" for row in rows).encode("ascii")
    return plan_text.rstrip(b"\r\n") + b"\n" + suffix, evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plan, evidence = plan_action(args.archive, args.profile)
    args.output.mkdir()
    if plan is not None:
        artifact = args.output / "successor.plan"
        artifact.write_bytes(plan)
        evidence["plan_sha256"] = digest(artifact)
    write_json(args.output / "selection.json", evidence)


if __name__ == "__main__":
    main()
