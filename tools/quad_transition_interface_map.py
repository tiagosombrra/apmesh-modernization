"""Map native curve and protected template actions on a certified mixed archive."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from math import dist, floor
from pathlib import Path

from quad_adjacent_group_selector import (
    _GRADATION_RATIO, arc_lengths, edge_set, inside, leaves_in, neighbors,
    owning_box, project_parent,
)
from quad_budgeted_transition_trial import face_upper_bound, overlaps, projected_seed, read
from quad_generation_metrics import cross, element_quality, load_physical_obj
from quad_grouping_trial import digest, original_curve_witness, write_json
from quad_portable_feedback_trial import source_hashes
from quad_progressive_admission import (
    CHILD_CERTIFICATE_SCHEMA, boundary_certificate, load_profile, ordered_sites, source_evaluator,
)


def interval_lineage(original, final, certificate):
    sites = {row[3]: row[2] for row in final}
    parents = {row["parent_interval"]: row for row in certificate["splits"]}
    split = certificate["child_split"]
    names = {}
    for i, (a, b) in enumerate(zip(original, original[1:] + original[:1])):
        a, b = a[2], b[2]
        if i not in parents:
            names[a, b] = ("curve", i)
            continue
        mid = sites[parents[i]["inserted_id"]]
        for child, edge in enumerate(((a, mid), (mid, b))):
            if (i, child) != (certificate["child_request"]["interval"],
                               certificate["child_request"]["child"]):
                names[edge] = ("curve_child", i, child)
                continue
            p = sites[split["inserted_id"]]
            names[edge[0], p] = ("deeper_interval", i, child, 0)
            names[p, edge[1]] = ("deeper_interval", i, child, 1)
    return names


def group_children(parent, tree, original_tree, prior_groups, requests):
    children = leaves_in(parent, tree)
    if len(children) != 4 or not children <= set(original_tree):
        return None, "not_four_original_leaf_children", []
    protected_cells = [parent, *(b for side in neighbors(parent, original_tree) for b in side)]
    protected = [r["face"] for r in requests if any(inside(r["site"], b) for b in protected_cells)]
    if protected:
        return None, "protected_requests", protected
    if any(overlaps(parent, other) for other in prior_groups):
        return None, "overlapping_retained_groups", []
    return children, "eligible_for_projection", []


def map_interfaces(root, ungrouped, profile_path):
    receipt, prior = read(root / "result.json"), read(ungrouped / "result.json")
    f = root / "successor.steps/feedback"
    ungrouped_feedback = ungrouped / "successor.steps/feedback"
    profile, fingerprint = load_profile(profile_path)
    original = root / "source.steps/source.obj"
    candidate = f / "candidate.obj"
    if (source_hashes(root / "source.steps") != receipt["source_sha256"]
            or source_hashes(ungrouped / "source.steps") != receipt["source_sha256"]
            or prior["source_sha256"] != receipt["source_sha256"]
            or digest(root / "successor.plan") != receipt["trial_plan_sha256"]
            or digest(ungrouped / "successor.plan") != prior["trial_plan_sha256"]
            or digest(candidate) != receipt["successor"]["candidate_sha256"]
            or digest(ungrouped_feedback / "candidate.obj") != prior["successor"]["candidate_sha256"]
            or digest(f / "requests.csv") != digest(ungrouped_feedback / "requests.csv")
            or receipt["progressive_admission"]["profile_sha256"] != fingerprint):
        raise ValueError("Unbound mixed control or ungrouped request archive")
    boundary_certificate(original, candidate, f, receipt)
    certificate = read(f / "boundary_refinement.json")
    front = read(f / "candidate_front/front.json")
    if (certificate["schema"] != CHILD_CERTIFICATE_SCHEMA
            or front["clearance"]["policy"] != "minimum_cell_segment_uv_v1"
            or any("introduced_vertex" in step for step in front["commits"])):
        raise ValueError("Expected a fixed-vertex mixed archive with one certified child split")
    final = ordered_sites(candidate)
    names = interval_lineage(ordered_sites(original), final, certificate)
    contour = [p[2] for p in final]
    curve_edges = list(zip(contour, contour[1:] + contour[:1]))
    if set(names) != set(curve_edges):
        raise ValueError("Curve request lineage does not match the archived contour")
    tree = list(map(tuple, front["leaves"]))
    ungrouped_tree = list(map(tuple, read(ungrouped_feedback / "candidate_front/front.json")["leaves"]))
    retained = list(map(tuple, receipt["grouping"]["parents"]))
    removed = set().union(*(leaves_in(p, ungrouped_tree) for p in retained))
    if set(tree) != (set(ungrouped_tree) - removed) | set(retained):
        raise ValueError("Archived tree does not match the native groups")
    clearance = front["clearance"]["factor"]
    seed = projected_seed(tree, curve_edges, clearance)
    seed_quads = len(front["seed_faces"])
    birth_xyz, birth_uv, birth_faces = load_physical_obj(f / "smoothing_comparison/before.obj")
    seed_ids = {v for face in front["seed_faces"] for v in face}
    if (seed_quads != len(seed) or len(birth_uv) != len(seed_ids) + len(contour)
            or len({v for face in seed for v in face}) != len(seed_ids)
            or list(map(list, birth_uv)) != front["vertices"]):
        raise ValueError("Archived template seeds or vertices do not match the projection")

    evaluate = source_evaluator(root, receipt)
    normal = lambda at: cross(*evaluate(*at)[1:])
    side_lengths = arc_lengths(evaluate)
    arc = {}
    for line in original_curve_witness(candidate):
        if line.startswith(b"# source_site "):
            row = line.split()
            arc[tuple(map(float, row[4:6]))] = (float(row[12]) * side_lengths[int(row[2])],
                                                tuple(map(float, row[10:12])))
    available = defaultdict(list)
    seed_owners = defaultdict(list)
    for a, b in curve_edges:
        available[a].append((a, b))
        available[b].append((a, b))
    for face in front["seed_faces"]:
        ring = [birth_uv[v] for v in face]
        cell = owning_box(ring, tree)
        for edge in edge_set(ring):
            seed_owners[edge].append(cell)
    physical, uv, faces = load_physical_obj(candidate)
    by_face = {frozenset(face): i for i, face in enumerate(birth_faces)}
    limit = profile["safety_floors"]["TRI"]
    contour_ids = {i for i, p in enumerate(uv) if p in available}
    trace = []
    actions = defaultdict(list)
    by_edge = defaultdict(list)
    for face in faces:
        endpoints = contour_ids.intersection(face)
        if len(face) != 3 or len(endpoints) != 1:
            continue
        apex, = endpoints
        final_score = element_quality(physical, uv, face, normal)
        if final_score["min_angle_xyz"] >= limit["min_angle_deg"] and final_score["tri_q"] >= limit["min_shape"]:
            continue
        base = tuple(sorted(birth_uv[v] for v in face if v != apex))
        birth_index = by_face[frozenset(face)]
        op = birth_index - seed_quads + 1
        score = element_quality(birth_xyz, birth_uv, face, normal)
        row = dict(operation=op, angle=final_score["min_angle_xyz"], birth_angle=score["min_angle_xyz"],
                   base=base, contour_vertex=uv[apex], curve_actions=[])
        trace.append(row)
        if len(seed_owners[base]) != 1:
            continue
        first = birth_faces[birth_index]
        a, b = next((birth_uv[i], birth_uv[j]) for i, j in zip(first, first[1:] + first[:1])
                    if apex not in (i, j))
        length = dist(evaluate(*a)[0], evaluate(*b)[0])
        parent = project_parent(seed_owners[base][0])
        _, status, protected = group_children(parent, tree, ungrouped_tree, retained, receipt["face_requests"])
        row["direct_group"] = dict(parent=parent, status=status, protected_requests=protected)
        by_edge[base].append(op)
        for edge in available[uv[apex]]:
            size, mid = arc[edge[0]]
            trial = [a, b, mid]
            try:
                q = element_quality([evaluate(*p)[0] for p in trial], trial, [0, 1, 2], normal)
            except ValueError:
                q = {}
            angle, shape = q.get("min_angle_xyz"), q.get("tri_q")
            improves = angle is not None and angle > score["min_angle_xyz"] and shape >= score["tri_q"]
            name = names[edge]
            observation = dict(action=name, operation=op, angle=angle, shape=shape,
                               improves_birth=improves, edge=edge, midpoint=mid, arc_to_base=size / length)
            row["curve_actions"].append(observation)
            if name[0] != "deeper_interval" and size > _GRADATION_RATIO * length:
                actions[name].append(observation)
    trace.sort(key=lambda row: (row["angle"], row["operation"]))

    maximum = min(profile["max_total_faces"],
                  floor(len(load_physical_obj(original)[2]) * (1 + profile["max_face_growth"])))
    options = {project_parent(p) for p in tree if p != (0, 0, 1, 1)}
    possible_groups = {}
    for p in sorted(options):
        children, _, _ = group_children(p, tree, ungrouped_tree, retained, receipt["face_requests"])
        if children is not None:
            possible_groups[p] = children
    sets = [(p,) for p in possible_groups]
    sets.extend((p, q) for p, q in combinations(possible_groups, 2)
                if not overlaps(p, q) and any(q in side for side in neighbors(p, (p, q))))
    groups = []
    for pair in sets:
        leaves = (set(tree) - set().union(*(possible_groups[p] for p in pair))) | set(pair)
        try:
            revised = projected_seed(sorted(leaves), curve_edges, clearance)
        except ValueError:
            continue
        current = Counter(edge for face in revised for edge in edge_set(face))
        affected = sorted(op for base, ops in by_edge.items() if not current[base] for op in ops)
        groups.append(dict(parents=pair, removes_seed_edges_at=affected,
                           face_upper_bound=face_upper_bound(revised, len(contour), len(revised))))

    helpful = [name for name, rows in sorted(actions.items()) if any(r["improves_birth"] for r in rows)]
    batches = []
    for count in range(1, min(3, len(helpful)) + 1):
        for batch in combinations(helpful, count):
            replace = {actions[name][0]["edge"] for name in batch}
            retained_edges = [edge for edge in curve_edges if edge not in replace]
            optimistic = projected_seed(tree, retained_edges, clearance)
            upper = face_upper_bound(optimistic, len(contour) + count, seed_quads)
            improve_ops = {r["operation"] for a in batch for r in actions[a] if r["improves_birth"]}
            batches.append(dict(actions=batch, face_upper_bound=upper, fits_budget=upper <= maximum,
                                representable=all(a[0] == "curve" for a in batch),
                                projected_gain_operations=sorted(improve_ops)))
    return dict(source_sha256=receipt["source_sha256"], candidate_sha256=digest(candidate),
                profile_sha256=fingerprint, face_budget=maximum, current_faces=len(faces),
                transition_triangles=trace, group_parents_examined=len(options),
                eligible_group_projections=groups, curve_batches=batches)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for label in ("control", "ungrouped", "profile", "out"):
        parser.add_argument(f"--{label}", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = map_interfaces(args.control, args.ungrouped, args.profile)
        write_json(args.out, result)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(1, f"Transition interface mapping failed: {error}\n")
    print(json.dumps({k: result[k] for k in ("face_budget", "current_faces", "curve_batches")}))


if __name__ == "__main__":
    main()
