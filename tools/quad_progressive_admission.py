"""Evaluate a staged single-patch successor with an explicit progressive profile."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from quad_generation_metrics import load_physical_obj
from quad_grouping_trial import digest, original_curve_witness
from quad_regional_quality_guards import (
    CHART, GROUPS, METRICS, collect_region_metrics, validate_profile, within,
)
from quad_transition_comparison import bernstein, compare, golden, parse_bp

SOURCE_FILES = ("tri.obj", "source.obj", "source_tree.txt")
GRIDS = (24, 48)
CERTIFICATE_SCHEMA = "apmesh.quad.boundary_refinement.v1"
CHILD_CERTIFICATE_SCHEMA = "apmesh.quad.boundary_refinement.v2"


def load_profile(path):
    raw = path.read_bytes()
    profile = json.loads(raw)
    expected = {"safety_floors", "regional_targets", "min_relative_rms_gain",
                "max_face_growth", "max_total_faces", "error_targets"}
    if not isinstance(profile, dict) or set(profile) != expected:
        raise ValueError("Provide all progressive admission limits explicitly")
    targets = profile["regional_targets"]
    validate_profile(dict(max_face_growth=profile["max_face_growth"], regional_floors=targets))
    floors = profile["safety_floors"]
    if not isinstance(floors, dict) or set(floors) != {"TRI", "QUAD"}:
        raise ValueError("Provide separate TRI and QUAD safety floors")
    for kind, limits in floors.items():
        upper = (60 if kind == "TRI" else 90, 1)
        if (not isinstance(limits, dict) or set(limits) != set(METRICS)
                or not all(within(limits[k], maximum) and limits[k] > 0
                           for k, maximum in zip(METRICS, upper))):
            raise ValueError(f"Invalid {kind} safety floor")
        if any(targets[group][key] < limits[key]
               for group in GROUPS if group.endswith(kind) for key in METRICS):
            raise ValueError(f"{kind} regional targets must include the safety floors")
    if not within(profile["min_relative_rms_gain"], 1) or profile["min_relative_rms_gain"] == 0:
        raise ValueError("Minimum relative RMS gain must be positive and at most one")
    total = profile["max_total_faces"]
    if type(total) is not int or total <= 0:
        raise ValueError("Total face budget must be a positive integer")
    errors = profile["error_targets"]
    if (not isinstance(errors, dict) or set(errors) != {"rms_source_area", "max_xyz"}
            or not all(within(x, float("inf")) for x in errors.values())):
        raise ValueError("Provide finite nonnegative geometric stopping targets")
    return profile, sha256(raw).hexdigest()


def regional_metric(previous, candidate, safety, target):
    old_min = min(previous, default=None)
    new_min = min(candidate, default=None)
    old_count = sum(value < target for value in previous)
    new_count = sum(value < target for value in candidate)
    if new_min is None:
        status = "removed" if previous else "absent"
    elif new_min < safety:
        status = "below_safety_floor"
    elif new_min >= target:
        status = "meets_target"
    elif (old_min is None or new_min < old_min or new_count > old_count
          or new_count * len(previous) > old_count * len(candidate)):
        status = "regional_regression"
    else:
        status = "below_target_without_regression"
    return dict(status=status, predecessor_min=old_min, candidate_min=new_min, safety_floor=safety,
                target=target, predecessor_below_target=old_count, candidate_below_target=new_count)


def measure_progress(previous, candidate, comparisons, profile):
    if any(grid not in comparisons for grid in GRIDS):
        raise ValueError("Both common geometry grids are required")
    regions, blockers = {}, []
    for group in GROUPS:
        old, new = previous.get(group, ()), candidate.get(group, ())
        safety = profile["safety_floors"][group.rsplit("_", 1)[1]]
        targets = profile["regional_targets"][group]
        metrics = {key: regional_metric([row[i] for row in old], [row[i] for row in new],
                                        safety[key], targets[key])
                   for i, key in enumerate(METRICS)}
        regions[group] = dict(predecessor_faces=len(old), candidate_faces=len(new), metrics=metrics)
        blockers.extend(f"{group}.{key}.{row['status']}" for key, row in metrics.items()
                        if row["status"] in ("below_safety_floor", "regional_regression"))
    old_total = sum(map(len, previous.values()))
    new_total = sum(map(len, candidate.values()))
    if not old_total or not new_total:
        raise ValueError("Evaluation requires two nonempty meshes")
    growth = (new_total - old_total) / old_total
    if growth > profile["max_face_growth"]:
        blockers.append("face_growth")
    if new_total > profile["max_total_faces"]:
        blockers.append("total_face_budget")

    geometry, errors_met = {}, True
    for grid in GRIDS:
        before, after = (comparisons[grid][key]["global_error"] for key in ("baseline", "candidate"))
        if any(row["sample_count"] != grid * grid for row in (before, after)):
            raise ValueError("Incomplete common geometry evaluation")
        old_rms, new_rms = before["rms_source_area"], after["rms_source_area"]
        gain = (old_rms - new_rms) / old_rms if old_rms > 0 else None
        if gain is None or gain < profile["min_relative_rms_gain"]:
            blockers.append(f"relative_rms_gain_{grid}")
        if after["max_xyz"] > before["max_xyz"]:
            blockers.append(f"maximum_deviation_{grid}")
        errors_met = errors_met and all(after[k] <= v for k, v in profile["error_targets"].items())
        geometry[grid] = dict(predecessor=before, candidate=after, relative_rms_gain=gain)
    quality_met = all(metric["status"] in ("meets_target", "removed", "absent")
                      for stats in regions.values() for metric in stats["metrics"].values())
    status = "blocked" if blockers else "eligible"
    return dict(status=status, blockers=blockers, quality_targets_met=quality_met,
                error_targets_met=errors_met, stop_targets_met=not blockers and quality_met and errors_met,
                regions=regions, geometry=geometry, face_growth=growth,
                predecessor_faces=old_total, candidate_faces=new_total)


def ordered_sites(path):
    xyz, uv, faces = load_physical_obj(path)
    at = dict(zip(uv, xyz))
    edges = {(a, b) for face in faces for a, b in zip(face, face[1:] + face[:1])}
    boundary = {(uv[a], uv[b]) for a, b in edges if (b, a) not in edges}
    sites = []
    for line in original_curve_witness(path):
        if not line.startswith(b"# source_site "):
            continue
        _, _, side, parameter, u, v, name, *point = line.split()[:10]
        site = (float(u), float(v))
        physical = tuple(map(float, point))
        if at.get(site) != physical:
            raise ValueError("Original site placement differs from its mesh node")
        sites.append((int(side), float(parameter), site, int(name), physical))
    positions = [site[2] for site in sites]
    if (not sites or len(set(positions)) != len(sites)
            or set(zip(positions, positions[1:] + positions[:1])) != boundary):
        raise ValueError("Original sites do not describe the directed mesh contour")
    return sites


def verify_curve_rows(parent, candidate, inserts):
    def records(path):
        return [tuple(line.split()[2:]) for line in original_curve_witness(path)
                if line.startswith(b"# original_curve ")]

    previous, current = records(parent), records(candidate)
    retained = set(previous)
    if not previous or [row for row in current if row in retained] != previous:
        raise ValueError("Candidate changes an original curve sample")
    direction = {int(row[0]): int(row[1]) for row in previous}
    extras = Counter()
    for row in current:
        if row in retained:
            continue
        side, orientation, parameter, identifier, *point = row
        if direction.get(int(side)) != int(orientation):
            raise ValueError("Inserted original curve sample changes orientation")
        extras[int(side), float(parameter), int(identifier), tuple(map(float, point))] += 1
    if extras != Counter((side, parameter, identifier, point) for side, parameter, _, identifier, point in inserts):
        raise ValueError("Inserted contour sites differ from original curve samples")


def _subdivision_steps(old, new):
    index, expected, inserts = 0, [], []
    previous_ids = {row[3] for row in old}
    for j, start in enumerate(old):
        if index >= len(new) or new[index] != start:
            raise ValueError("Candidate changes an ordered predecessor site")
        index += 1
        end = old[(j + 1) % len(old)]
        if new[index % len(new)] == end:
            continue
        if index == len(new):
            raise ValueError("Candidate does not retain the full predecessor contour")
        site = new[index]
        side, parameter, uv, identifier, _ = site
        a, b = start[2], end[2]
        if identifier in previous_ids or not any(
            a[axis] == b[axis] == uv[axis]
            and min(a[1-axis], b[1-axis]) < uv[1-axis] < max(a[1-axis], b[1-axis])
            for axis in (0, 1)
        ):
            raise ValueError("Inserted site is not in its directed parent interval")
        previous_ids.add(identifier)
        expected.append(dict(parent_interval=j, start_id=start[3], end_id=end[3],
                             inserted_id=identifier, side=side, parameter=parameter))
        inserts.append(site)
        index += 1
    if index != len(new):
        raise ValueError("Candidate contour has unbound sites")
    return expected, inserts


def subdivision_certificate(old, new, requested, child_request=None):
    intermediate = new
    if child_request is not None:
        if (not isinstance(child_request, dict) or set(child_request) != {"interval", "child"}
                or type(child_request["interval"]) is not int
                or type(child_request["child"]) is not int
                or child_request["child"] not in (0, 1)
                or requested.count(child_request["interval"]) != 1):
            raise ValueError("Child subdivision needs one recorded original interval")
        # The second native pass assigns its single new node after every
        # original and first-pass node ID.
        last_id = max(row[3] for row in new)
        intermediate = [row for row in new if row[3] != last_id]
        if len(intermediate) + 1 != len(new):
            raise ValueError("Child subdivision has no unique new node")
    expected, inserts = _subdivision_steps(old, intermediate)
    if [row["parent_interval"] for row in expected] != sorted(requested):
        raise ValueError("Candidate contour does not realize the recorded curve requests")
    certificate = dict(schema=CERTIFICATE_SCHEMA, parent_sites=len(old),
                       candidate_sites=len(new), splits=expected)
    if child_request is not None:
        parent, = [row for row in expected if row["parent_interval"] == child_request["interval"]]
        split_at, = [i for i, row in enumerate(intermediate) if row[3] == parent["inserted_id"]]
        child = split_at - 1 + child_request["child"]
        steps, extra = _subdivision_steps(intermediate, new)
        if len(steps) != 1 or steps[0]["parent_interval"] != child:
            raise ValueError("Candidate contour split a different child interval")
        certificate.update(schema=CHILD_CERTIFICATE_SCHEMA, intermediate_sites=len(intermediate),
                           child_request=child_request, child_split=steps[0])
        inserts.extend(extra)
    return certificate, inserts


def boundary_certificate(parent, candidate, feedback, receipt):
    old, new = ordered_sites(parent), ordered_sites(candidate)
    certificate, inserts = subdivision_certificate(
        old, new, [row["interval"] for row in receipt["curve_requests"]],
        receipt.get("child_curve_request"))
    expected_hash = receipt.get("boundary_refinement_sha256")
    if expected_hash is None:
        if inserts or original_curve_witness(parent) != original_curve_witness(candidate):
            raise ValueError("Changed original curve requires a native certificate")
        return None
    raw = (feedback / "boundary_refinement.json").read_bytes()
    if sha256(raw).hexdigest() != expected_hash or json.loads(raw) != certificate:
        raise ValueError("Native certificate does not match the bound curve subdivision")
    verify_curve_rows(parent, candidate, inserts)
    return expected_hash


def source_evaluator(root, receipt):
    model = receipt["model"]
    if model == "builtin:curva_bezier" and receipt["model_fingerprint"] == model:
        return golden
    if model != "source.bp":
        raise ValueError("Unknown bound single-patch surface")
    raw = (root / model).read_bytes()
    if sha256(raw).hexdigest() != receipt["model_fingerprint"]:
        raise ValueError("Analytic source differs from its native receipt")
    points, patches = parse_bp(raw.decode("utf-8"))
    if len(patches) != 1:
        raise ValueError("Progressive evaluation requires one bound patch")
    controls = [points[i] for i in patches[0]]
    return lambda u, v: bernstein(controls, u, v)


def assess_trial(root, receipt, loaded_profile):
    profile, fingerprint = loaded_profile
    source = root / "source.steps"
    replay = root / "successor.steps"
    feedback = replay / "feedback"
    binding = receipt["source_sha256"]
    def verify(archive):
        if {name: digest(archive / name) for name in SOURCE_FILES} != binding:
            raise ValueError("Original TRI, mixed predecessor or native tree differs from the receipt")

    verify(source)
    proposal = receipt["successor"]
    native = proposal["status"]
    base = dict(profile_sha256=fingerprint, predecessor_sha256=binding["source.obj"],
                native_status=native, mixed_adaptive_epochs=0)
    has_requests = bool(receipt["face_requests"] or receipt["curve_requests"])
    if native == "no_action" and not has_requests:
        return dict(base, status="no_action", blockers=[])
    verify(replay)
    lines = (feedback / "result.txt").read_text(encoding="ascii").splitlines()
    if len(lines) != 4 or lines[0] != native:
        raise ValueError("Native outcome differs from its receipt")
    if native in ("rejected", "no_action"):
        if (feedback / "candidate.obj").exists():
            raise ValueError("A non-staged native outcome has a candidate artifact")
        reason = lines[2] if native == "rejected" else "no_realized_request"
        return dict(base, status="blocked", blockers=[reason])
    if native != "staged" or not has_requests:
        raise ValueError("Unknown or unrequested progressive candidate")

    predecessor, candidate = source / "source.obj", feedback / "candidate.obj"
    candidate_hash = digest(candidate)
    if candidate_hash != proposal["candidate_sha256"] or candidate_hash == binding["source.obj"]:
        raise ValueError("Staged candidate is unchanged or differs from the native receipt")
    evaluate = source_evaluator(root, receipt)
    certificate = boundary_certificate(predecessor, candidate, feedback, receipt)
    _, _, _, edits = map(int, lines[1].split())
    old_segments, new_segments = map(int, lines[3].split())
    if edits <= 0 and new_segments <= old_segments:
        raise ValueError("The staged candidate has no recorded realized feedback")
    pairs = {grid: compare(predecessor, candidate, CHART, evaluate, grid) for grid in GRIDS}
    for grid, pair in pairs.items():
        if ((pair["baseline"]["sha256"], pair["candidate"]["sha256"]) != (binding["source.obj"], candidate_hash)
                or (pair["baseline"]["boundary_segments"], pair["candidate"]["boundary_segments"])
                != (old_segments, new_segments)):
            raise ValueError(f"Native feedback and common-grid evidence disagree on grid {grid}")
    result = measure_progress(collect_region_metrics(predecessor, evaluate),
                              collect_region_metrics(candidate, evaluate), pairs, profile)
    verify(source)
    verify(replay)
    if digest(candidate) != candidate_hash:
        raise ValueError("Candidate changed during progressive evaluation")
    if certificate is not None and digest(feedback / "boundary_refinement.json") != certificate:
        raise ValueError("Native certificate changed during progressive evaluation")
    if receipt["model"] == "source.bp" and digest(root / "source.bp") != receipt["model_fingerprint"]:
        raise ValueError("Analytic source changed during progressive evaluation")
    return dict(base, **result, candidate_sha256=candidate_hash, boundary_certificate_sha256=certificate,
                max_adjacent_physical_size_ratio={key: pairs[48][key]["max_adjacent_size_ratio"]
                                                  for key in ("baseline", "candidate")})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    args = parser.parse_args()
    try:
        receipt = json.loads((args.archive / "result.json").read_bytes())
        report = assess_trial(args.archive, receipt, load_profile(args.profile))
    except (KeyError, OSError, TypeError, ValueError) as error:
        parser.exit(1, f"Progressive assessment failed: {error}\n")
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
