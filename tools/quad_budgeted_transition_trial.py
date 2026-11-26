"""Project one realizable native action at the worst reachable transition TRI."""

import argparse
from collections import Counter, defaultdict
import json
from math import dist, floor
from pathlib import Path

from quad_adjacent_group_selector import (
    _GRADATION_RATIO, arc_lengths, box_segment_distance, edge_set, inside, leaves_in,
    neighbors, owning_box, pattern_on, project_parent, qualify_geometry, sides_mask,
)
from quad_generation_metrics import cross, element_quality, load_physical_obj
from quad_grouping_trial import digest, original_curve_witness, write_json
from quad_portable_feedback_trial import source_hashes
from quad_progressive_admission import boundary_certificate, load_profile, ordered_sites, source_evaluator


def read(path):
    return json.loads(path.read_bytes())


def fringe(box):
    return box[0] == 0 or box[1] == 0 or box[2] == 1 or box[3] == 1


def overlaps(a, b):
    return all(max(a[k], b[k]) < min(a[k + 2], b[k + 2]) for k in (0, 1))


def projected_seed(tree, contour, clearance):
    faces = []
    for leaf in tree:
        mask = sides_mask(leaf, tree)
        if mask is None:
            raise ValueError("Unbalanced template projection")
        if fringe(leaf) or any(box_segment_distance(leaf, a, b) < clearance * dist(a, b)
                              for a, b in contour):
            continue
        faces.extend(pattern_on(leaf, mask)[1])
    return faces


def face_upper_bound(template_faces, segments, minimum_quads):
    # A conforming disk has T + 2Q = 2V - B - 2. Seed sites and
    # certified contour sites account for all vertices in this trial.
    vertices = {site for face in template_faces for site in face}
    return 2 * len(vertices) + segments - 2 - minimum_quads


def plan_action(root, ungrouped, profile_path):
    receipt = read(root / "result.json")
    control = read(ungrouped / "result.json")
    fb = root / "successor.steps/feedback"
    pregroup = ungrouped / "successor.steps/feedback"
    profile, fingerprint = load_profile(profile_path)
    plan = root / "successor.plan"
    predecessor = root / "source.steps/source.obj"
    candidate = fb / "candidate.obj"
    if (control["source_sha256"] != receipt["source_sha256"]
            or source_hashes(root / "source.steps") != receipt["source_sha256"]
            or source_hashes(ungrouped / "source.steps") != receipt["source_sha256"]
            or digest(ungrouped / "successor.plan") != control["trial_plan_sha256"]
            or digest(pregroup / "candidate.obj") != control["successor"]["candidate_sha256"]
            or digest(plan) != receipt["trial_plan_sha256"]
            or digest(candidate) != receipt["successor"]["candidate_sha256"]
            or digest(fb / "requests.csv") != digest(pregroup / "requests.csv")
            or digest(fb / "boundary_refinement.json") != digest(pregroup / "boundary_refinement.json")
            or receipt["progressive_admission"]["profile_sha256"] != fingerprint
            or control.get("grouping")):
        raise ValueError("Incompatible grouped control and ungrouped request archive")
    boundary_certificate(predecessor, candidate, fb, receipt)
    source_sites = ordered_sites(predecessor)
    curve = [site[2] for site in ordered_sites(candidate)]
    curve_edges = list(zip(curve, curve[1:] + curve[:1]))
    original = [site[2] for site in source_sites]
    original_edges = list(zip(original, original[1:] + original[:1]))
    incident = defaultdict(list)
    for index, (a, b) in enumerate(original_edges):
        incident[a].append(index)
        incident[b].append(index)
    split = {row["interval"] for row in receipt["curve_requests"]}

    front = read(fb / "candidate_front/front.json")
    tree = list(map(tuple, front["leaves"]))
    before_group = list(map(tuple, read(pregroup / "candidate_front/front.json")["leaves"]))
    parents = [tuple(p) for p in receipt["grouping"]["parents"]]
    clearance = front["clearance"]
    if clearance["policy"] != "minimum_cell_segment_uv_v1":
        raise ValueError("Budget projection needs the fixed-vertex article front")
    factor = clearance["factor"]
    birth = fb / "smoothing_comparison/before.obj"
    _, initial_uv, initial_faces = load_physical_obj(birth)
    xyz, uv, faces = load_physical_obj(candidate)
    template_faces = projected_seed(tree, curve_edges, factor)
    seed_faces = front["seed_faces"]
    seed_ids = {v for f in seed_faces for v in f}
    expected_sites = {site for f in template_faces for site in f}
    removed = set().union(*(leaves_in(p, before_group) for p in parents))
    projected_grouped_tree = (set(before_group) - removed) | set(parents)
    if (list(map(list, initial_uv)) != front["vertices"]
            or any("introduced_vertex" in s for s in front["commits"])
            or len(initial_uv) != len(seed_ids) + len(curve)
            or len(template_faces) != len(seed_faces) or len(expected_sites) != len(seed_ids)
            or set(tree) != projected_grouped_tree):
        raise ValueError("Native fixed-vertex control does not match the seed projection")
    prior_faces = len(load_physical_obj(predecessor)[2])
    budget = min(profile["max_total_faces"], floor(prior_faces * (1 + profile["max_face_growth"])))
    if len(faces) > budget:
        raise ValueError("Grouped control exceeds the frozen face budget")
    control_bound = face_upper_bound(template_faces, len(curve), len(seed_faces))
    if len(faces) > control_bound:
        raise ValueError("Native control exceeds its disk face bound")

    evaluate = source_evaluator(root, receipt)
    side_sizes = arc_lengths(evaluate)
    arcs = [float(row.split()[12]) * side_sizes[int(row.split()[2])]
            for row in original_curve_witness(predecessor) if row.startswith(b"# source_site ")]
    seed_edges = Counter(e for f in seed_faces for e in edge_set(f))
    owners = {e: owning_box([initial_uv[v] for v in f], tree)
              for f in seed_faces for e in edge_set(f) if seed_edges[e] == 1}
    curves = set(curve)
    floor_tri = profile["safety_floors"]["TRI"]
    normal = lambda at: cross(*evaluate(*at)[1:])
    candidates = []
    for i, face in enumerate(faces):
        on_curve = [v for v in face if uv[v] in curves]
        if len(face) != 3 or len(on_curve) != 1:
            continue
        score = element_quality(xyz, uv, face, normal)
        if score["min_angle_xyz"] >= floor_tri["min_angle_deg"] and score["tri_q"] >= floor_tri["min_shape"]:
            continue
        edge = tuple(sorted(v for v in face if v != on_curve[0]))
        candidates.append(dict(face=i, angle=score["min_angle_xyz"], shape=score["tri_q"],
                               edge=edge, contour_vertex=uv[on_curve[0]]))
    candidates.sort(key=lambda row: (row["angle"], row["shape"], row["face"]))
    birth_index = {frozenset(f): i for i, f in enumerate(initial_faces)}
    geometric = {row["face"]: row for row in qualify_geometry(front, birth, evaluate)}
    grouped_projections = {}
    examined = []
    selected = None
    for tri in candidates:
        entry = dict(triangle=tri, actions=[])
        examined.append(entry)
        if tri["edge"] not in owners:
            entry["reason"] = "no_exposed_template_edge"
            continue
        support = dist(*(evaluate(*initial_uv[v])[0] for v in tri["edge"]))
        for i in sorted(incident[tri["contour_vertex"]], key=lambda index: (-arcs[index], index)):
            if i in split:
                entry["actions"].append(dict(kind="curve", interval=i, status="original_interval_already_split"))
                continue
            if arcs[i] <= _GRADATION_RATIO * support:
                continue
            # Removing this clearance constraint includes every leaf any
            # subdivision of the interval could admit. Prior seeded cells stay.
            possible = projected_seed(tree, [e for e in curve_edges if e != original_edges[i]], factor)
            upper = face_upper_bound(possible, len(curve) + 1, len(seed_faces))
            action = dict(kind="curve", interval=i, old_arc=arcs[i], support_edge=support,
                          face_upper_bound=upper, status="eligible" if upper <= budget else "budget")
            entry["actions"].append(action)
            if upper <= budget:
                selected = dict(action, triangle=tri)
                break
        if selected:
            break

        parent = project_parent(owners[tri["edge"]])
        children = leaves_in(parent, tree)
        action = dict(kind="group", parent=parent)
        entry["actions"].append(action)
        if len(children) != 4 or not children <= set(before_group) or any(overlaps(parent, p) for p in parents):
            action["status"] = "not_four_disjoint_original_leaves"
            continue
        protected = [parent, *(b for sides in neighbors(parent, before_group) for b in sides)]
        requests = [r["face"] for r in receipt["face_requests"] if any(inside(r["site"], b) for b in protected)]
        if requests:
            action.update(status="protected_size_request", protected_faces=requests)
            continue
        if not fringe(parent):
            witness = geometric.get(birth_index[frozenset(faces[tri["face"]])], {})
            if witness.get("disposition") != "eligible":
                action["status"] = "no_projected_template_size_improvement"
                continue
        if parent not in grouped_projections:
            updated = sorted(set(tree) - children | {parent})
            try:
                grouped_projections[parent] = projected_seed(updated, curve_edges, factor)
            except ValueError:
                grouped_projections[parent] = None
        projected = grouped_projections[parent]
        if projected is None:
            action["status"] = "would_break_two_to_one"
            continue
        base = tuple(sorted(initial_uv[v] for v in tri["edge"]))
        if fringe(parent) and any(base in edge_set(face) for face in projected):
            action["status"] = "handoff_keeps_short_template_edge"
            continue
        quads = len(projected)
        upper = face_upper_bound(projected, len(curve), quads)
        action.update(face_upper_bound=upper, projected_seed_quads=quads,
                      status="eligible" if upper <= budget else "budget")
        if upper <= budget:
            selected = dict(action, triangle=tri, contour_parent=fringe(parent))
            break
    return dict(selected=selected, examined=examined, predecessor_faces=prior_faces,
                control_faces=len(faces), control_upper_bound=control_bound, maximum_faces=budget,
                profile_sha256=fingerprint, control_plan_sha256=digest(plan),
                control_receipt_sha256=digest(root / "result.json"), source_sha256=receipt["source_sha256"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", required=True, type=Path)
    parser.add_argument("--ungrouped", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = plan_action(args.control, args.ungrouped, args.profile)
        write_json(args.out, result)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Budgeted transition projection failed: {error}\n")
    print(json.dumps(result["selected"]))


if __name__ == "__main__":
    main()
