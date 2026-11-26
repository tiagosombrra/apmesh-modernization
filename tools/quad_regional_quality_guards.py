"""Assess explicit regional quality floors on a staged single-patch mixed pair."""

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path

from quad_generation_metrics import cross, element_quality, load_physical_obj
from quad_transition_comparison import bernstein, compare, golden, parse_bp

CHART = [(0, 0), (1, 0), (1, 1), (0, 1)]
METRICS = ("min_angle_deg", "min_shape")
GROUPS = tuple(f"{region}_{kind}" for region in ("contour_edge", "contour_vertex", "interior")
               for kind in ("TRI", "QUAD"))
SHAPE_SCORE = {"TRI": "tri_q", "QUAD": "quad_corner_jacobian"}


def within(value, maximum):
    return (type(value) in (float, int) and 0 <= value <= maximum and isfinite(value))


def validate_profile(profile):
    if not isinstance(profile, dict) or set(profile) != {"max_face_growth", "regional_floors"}:
        raise ValueError("Provide max_face_growth and regional_floors explicitly")
    if not within(profile["max_face_growth"], float("inf")):
        raise ValueError("Face growth limit must be finite and nonnegative")
    floors = profile["regional_floors"]
    if not isinstance(floors, dict) or set(floors) != set(GROUPS):
        raise ValueError("Provide a floor for each regional TRI and QUAD group")
    for group in GROUPS:
        pair = floors[group]
        maximum_angle = 60 if group.endswith("_TRI") else 90
        if (not isinstance(pair, dict) or set(pair) != set(METRICS)
                or not within(pair["min_angle_deg"], maximum_angle)
                or not within(pair["min_shape"], 1)):
            raise ValueError(f"Invalid angle or shape floor for {group}")


def collect_region_metrics(path, evaluate):
    xyz, uv, faces = load_physical_obj(path)

    def normal(at):
        _, du, dv = evaluate(*at)
        return cross(du, dv)

    groups = defaultdict(list)
    for face in faces:
        sites = [uv[i] for i in face]
        edge = any(a[k] == b[k] and a[k] in (0, 1)
                   for a, b in zip(sites, sites[1:] + sites[:1]) for k in (0, 1))
        vertex = any(component in (0, 1) for point in sites for component in point)
        zone = "contour_edge" if edge else "contour_vertex" if vertex else "interior"
        quality = element_quality(xyz, uv, face, normal)
        kind = quality["kind"]
        groups[f"{zone}_{kind}"].append((quality["min_angle_xyz"], quality[SHAPE_SCORE[kind]]))
    return groups


def measure_metric(before, after, floor):
    old_min = min(before, default=None)
    new_min = min(after, default=None)
    if new_min is None:
        status = "absent" if old_min is None else "removed"
    elif new_min >= floor:
        status = "meets_floor"
    elif old_min is not None and old_min < floor and new_min > old_min:
        status = "improved_below_floor"
    else:
        status = "blocked"
    return dict(floor=floor, predecessor_min=old_min, candidate_min=new_min,
                predecessor_below_floor=sum(val < floor for val in before),
                candidate_below_floor=sum(val < floor for val in after), status=status)


def assess_guards(before, after, profile):
    validate_profile(profile)
    baseline_faces = sum(map(len, before.values()))
    candidate_faces = sum(map(len, after.values()))
    if not baseline_faces or not candidate_faces:
        raise ValueError("Regional assessment needs two nonempty meshes")
    growth = (candidate_faces - baseline_faces) / baseline_faces
    blocked = []
    if growth > profile["max_face_growth"]:
        blocked.append("face_growth")
    regions = {}
    for group in GROUPS:
        baseline = before.get(group, ())
        candidate = after.get(group, ())
        measures = dict(predecessor_count=len(baseline), candidate_count=len(candidate))
        for index, metric in enumerate(METRICS):
            result = measure_metric([row[index] for row in baseline],
                                    [row[index] for row in candidate],
                                    profile["regional_floors"][group][metric])
            if result["status"] == "blocked":
                blocked.append(f"{group}.{metric}")
            measures[metric] = result
        regions[group] = measures
    return dict(status="blocked" if blocked else "passes_configured_guards",
                blocking_guards=blocked,
                growth=dict(predecessor_faces=baseline_faces, candidate_faces=candidate_faces,
                            fraction=growth, limit=profile["max_face_growth"]),
                regions=regions)


def assess_archives(predecessor, candidate, profile, evaluate=golden):
    validate_profile(profile)
    hashes = [sha256(path.read_bytes()).hexdigest() for path in (predecessor, candidate)]
    guards = assess_guards(collect_region_metrics(predecessor, evaluate),
                           collect_region_metrics(candidate, evaluate), profile)
    paired = {str(n): compare(predecessor, candidate, CHART, evaluate, n) for n in (24, 48)}
    for report in paired.values():
        if hashes != [report[stage]["sha256"] for stage in ("baseline", "candidate")]:
            raise ValueError("Physical archive changed during regional assessment")
    if hashes != [sha256(path.read_bytes()).hexdigest() for path in (predecessor, candidate)]:
        raise ValueError("Physical archive changed during regional assessment")
    return dict(profile=profile, guards=guards, geometric_comparison=paired, mixed_adaptive_epochs=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predecessor", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--source-bp", type=Path)
    parser.add_argument("--patch", type=int, default=0)
    args = parser.parse_args()
    try:
        evaluate = golden
        source = {"model": "builtin:curva_bezier"}
        if args.source_bp:
            raw_model = args.source_bp.read_bytes()
            points, patches = parse_bp(raw_model.decode("utf-8"))
            source = {"source_bp_sha256": sha256(raw_model).hexdigest(), "patch": args.patch}
            if not 0 <= args.patch < len(patches):
                raise ValueError("Unknown original Bezier source patch")
            controls = [points[i] for i in patches[args.patch]]
            evaluate = lambda u, v: bernstein(controls, u, v)
        elif args.patch != 0:
            raise ValueError("--patch requires --source-bp")
        payload = args.profile.read_bytes()
        output = assess_archives(args.predecessor, args.candidate, json.loads(payload), evaluate)
        output["profile_sha256"] = sha256(payload).hexdigest()
        output["source"] = source
    except (ValueError, KeyError, OSError, OverflowError) as error:
        parser.exit(1, f"Regional quality assessment failed: {error}\n")
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
