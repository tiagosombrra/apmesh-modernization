"""Audit real original curve partitions against the live physical QUAD/AFT OBJ."""
import argparse
import csv
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
import uuid

from independent_common_grid import load_physical_obj
from test_controlled_application import inspect, require
from test_m4_real_model_hybrid import approximately, golden


def audit(path):
    xyz, uv, faces = load_physical_obj(path)
    curves = {i: [] for i in range(4)}
    sites, identities = [], {}
    source_records = []
    for line in path.read_text().splitlines():
        row = line.split()
        if row[:2] == ["#", "original_curve"]:
            require(len(row) == 9, "Incomplete original curve witness")
            side, reverse, t, identity, x, y, z = row[2:]
            require(int(side) in curves and reverse in ("0", "1"), "Foreign curve side")
            curves[int(side)].append((int(reverse), float(t), int(identity),
                                       (float(x), float(y), float(z))))
        elif row[:2] == ["#", "source_site"]:
            require(len(row) == 14 and float(row[13]) == -1,
                    "Incomplete native site or wrong original refined-edge phase")
            sites.append((int(row[2]), float(row[3]), (float(row[4]), float(row[5])),
                          int(row[6]), tuple(map(float, row[7:10])),
                          tuple(map(float, row[10:12])), float(row[12])))
        elif row[:2] == ["#", "node_id"]:
            index, identity = map(int, row[2:])
            require(index not in identities, "Duplicate physical node identity witness")
            identities[index] = identity
        elif row[:2] == ["#", "original_source"]:
            source_records.append(dict(v.split("=", 1) for v in row[2:]))
    require(len(source_records) == 1, "Missing or repeated original source provenance")
    source = source_records[0]
    require(int(source["step"]) > 0 and int(source["leaves"]) > 0,
            "Source is not an actual adapted original tree")
    require(source.get("reference_tri_accepted") in ("0", "1"),
            "Missing actual global TRI reference outcome")
    require(int(source.get("domain_generation", "0")) > 0,
            "Missing selected domain invocation provenance")
    expected, nonuniform, reversed_sides = {}, 0, 0
    for side, samples in curves.items():
        require(len(samples) >= 2, "Missing original source curve")
        reversals = {sample[0] for sample in samples}
        ts = [sample[1] for sample in samples]
        require(len(reversals) == 1 and ts[0] == 0 and ts[-1] == 1 and
                all(math.isfinite(t) and a < t for a, t in zip(ts, ts[1:])),
                "Original curve partition lost endpoints or monotonicity")
        reversed_sides += samples[0][0]
        gaps = [b-a for a, b in zip(ts, ts[1:])]
        nonuniform += any(abs(gap-gaps[0]) > 1e-12 for gap in gaps[1:])
        for reverse, t, identity, point in samples:
            s = 1-t if reverse else t
            at = ((s, 0), (1, s), (s, 1), (0, s))[side]
            require(approximately(point, golden(*at)[0]), "Original curve XYZ differs from Bernstein source")
            if at in expected:
                require(expected[at] == (identity, point), "Shared source endpoint identity differs")
            expected[at] = identity, point
    require(nonuniform == int(source["nonuniform_sides"]) and
            reversed_sides == int(source["reversed_sides"]),
            "Original source does not prove its nonuniform/reversal claims")
    require(len(sites) == len(expected) and len({site[2] for site in sites}) == len(sites),
            "Native contour dropped or duplicated original source samples")
    topology = inspect(xyz, uv, faces, expected_boundary=len(expected), require_mixed=False)
    require(set(identities) == set(range(1, len(xyz)+1)) and
            len(set(identities.values())) == len(xyz), "Missing or aliased physical node identities")
    positions = {at: i for i, at in enumerate(uv)}
    require(len(positions) == len(uv), "Duplicate physical UV node")
    directed = Counter((a, b) for face in faces for a, b in zip(face, face[1:]+face[:1]))
    source_edges = set()
    for i, (side, t, at, identity, point, middle, length) in enumerate(sites):
        require(at in expected and expected[at] == (identity, point),
                "Native boundary sample differs from original curve witness")
        reverse = curves[side][0][0]
        parameter = at[side % 2]
        require(t == (1-parameter if reverse else parameter), "Native source traversal differs")
        require(math.isfinite(length) and length > 0 and all(math.isfinite(x) for x in middle),
                "Invalid native parametric edge metric")
        require(at in positions, "Missing physical original boundary sample")
        a, b = positions[at], positions[sites[(i+1) % len(sites)][2]]
        require(identities[a+1] == identity and xyz[a] == point,
                "Physical mesh changed original source node ID or exact XYZ")
        require(directed[a, b] == 1 and directed[b, a] == 0,
                "Physical mesh changed an original oriented curve interval")
        source_edges.add((a, b))
    actual_edges = {(a, b) for a, b in directed if directed[b, a] == 0}
    require(actual_edges == source_edges, "Foreign or missing physical boundary interval")
    return dict(topology, source_step=int(source["step"]), native_leaves=int(source["leaves"]),
                domain_generation=int(source["domain_generation"]),
                nonuniform_sides=nonuniform, reversed_sides=reversed_sides,
                reference_tri_accepted=bool(int(source["reference_tri_accepted"])),
                mixed_adaptive_epochs=0)


def negative_controls(path, directory):
    rows = path.read_text().splitlines()
    curve = next(i for i, line in enumerate(rows) if line.startswith("# original_curve "))
    site = next(i for i, line in enumerate(rows) if line.startswith("# source_site "))
    _, uv, _ = load_physical_obj(path)
    first_site = rows[site].split()
    boundary_index = uv.index((float(first_site[4]), float(first_site[5]))) + 1
    node = next(i for i, line in enumerate(rows)
                if line.startswith("# node_id ") and int(line.split()[2]) == boundary_index)
    vertex = next(i for i, line in enumerate(rows) if line.startswith("v "))
    face = next(i for i, line in enumerate(rows) if line.startswith("f "))
    cases = []
    for index in (curve, site, face):
        cases.append(rows[:index] + rows[index+1:])
    cases.append(rows[:curve] + [rows[curve]] + rows[curve:])
    for index, field, value in ((site, 6, "999999999"), (node, 3, "999999999"),
                                 (curve, 4, "0.125"), (vertex, 3, "9")):
        altered = rows.copy()
        fields = altered[index].split()
        fields[field] = value
        altered[index] = " ".join(fields)
        cases.append(altered)
    altered = rows.copy()
    fields = altered[face].split()
    altered[face] = "f " + " ".join(reversed(fields[1:]))
    cases.append(altered)
    for i, lines in enumerate(cases):
        output = directory / f"corrupt-{i}.obj"
        output.write_text("\n".join(lines) + "\n")
        try:
            audit(output)
        except (AssertionError, ValueError, KeyError, IndexError):
            continue
        raise AssertionError(f"Corrupted source/physical witness accepted: {i}")
    return len(cases)


def audit_history(prefix, profile):
    directory = Path(str(prefix) + ".steps")
    rows = list(csv.DictReader((directory / "manifest.csv").open()))
    original = profile == "original_curvature"
    require([int(row["step"]) for row in rows] == ([0, 1, 2, 3] if original else [0, 1, 2]),
            "Missing or reordered physical step")
    require([row["reference_tri_accepted"] for row in rows] ==
            (["1", "1", "0", "0"] if original else ["1", "1", "0"]),
            "Rejected reference step was promoted or accepted state was lost")
    require(rows[-1]["reason"] == ("global_error_increased" if original else "hybrid_criterion_rejected"),
            "Actual stop reason was lost")
    expected = ([(5, 0, 4, 4), (165, 120, 68, 20), (953, 784, 224, 112), (953, 784, 224, 112)]
                if original else [(5, 0, 4, 4), (5, 0, 4, 4), (37, 16, 28, 12)])
    for row, counts in zip(rows, expected):
        for column in ("tri_obj", "quad_tri_obj"):
            path = directory / row[column]
            require(path.parent == directory and path.suffix == ".obj", "Foreign history path")
            xyz, uv, faces = load_physical_obj(path)
            physical = inspect(xyz, uv, faces, expected_boundary=counts[3], require_mixed=False)
            markers = [dict(item.split("=", 1) for item in line.split()[2:])
                       for line in path.read_text().splitlines()
                       if line.startswith("# generation_stage ")]
            require(len(markers) == 1 and markers[0]["step"] == row["step"] and
                    markers[0]["reference_tri_accepted"] == row["reference_tri_accepted"] and
                    markers[0]["reason"] == row["reason"] and
                    markers[0]["mixed_adaptive_epochs"] == "0", "Forged history state")
            if int(row["step"]) > 0:
                source = audit(path)
                require(source["reference_tri_accepted"] == bool(int(row["reference_tri_accepted"])),
                        "History source outcome differs from its physical stage")
                require(source["domain_generation"] == int(row["domain_generation"]),
                        "History source belongs to another domain invocation")
            if column == "quad_tri_obj":
                actual = tuple(physical[key] for key in ("nodes", "quads", "triangles", "boundary"))
                require(actual == counts and actual[:3] ==
                        tuple(int(row[key]) for key in ("nodes", "quads", "triangles")),
                        "History geometry or manifest counts differ")
            else:
                # The legacy OBJ has six significant digits. Use the existing
                # full-precision native incidence snapshot for exact geometry.
                incidence_path = Path(str(prefix) + f"_passo_{row['step']}_incidences.json")
                snapshot = json.loads(incidence_path.read_text())["patches"][0]
                original_xyz = [tuple(node[1:4]) for node in snapshot["nodes"]]
                indices = {node[0]: i for i, node in enumerate(snapshot["nodes"])}
                original_faces = [tuple(indices[node[0]] for node in face[1:])
                                  for face in snapshot["faces"]]
                require(xyz == original_xyz and faces == original_faces and
                        all(uv[indices[node[0]]] == tuple(node[1:3])
                            for face in snapshot["faces"] for node in face[1:]),
                        "TRI history is not the actual original reference geometry")
    accepted = directory / rows[1]["quad_tri_obj"]
    require(prefix.with_suffix(".obj").read_bytes() == accepted.read_bytes(),
            "Main output did not retain the last accepted source")
    trace = list(csv.DictReader((directory / "curve_stages.csv").open()))
    groups = {}
    for row in trace:
        parameters = [float(t) for t in row["parameters"].split("|") if t]
        require(len(parameters) == int(row["parameter_count"]) and
                all(math.isfinite(t) and 0 <= t <= 1 for t in parameters), "Invalid curve trace")
        key = (row["step"], row["epoch"], row["retry"], row["curve"])
        groups.setdefault(key, []).append(row)
    require(groups and all([r["stage"] for r in group] ==
                          ["input", "curve_pass", "surface_pass", "final_budget"]
                          for group in groups.values()), "Incomplete curve-pass provenance")
    if original:
        require(all(group[-1]["parameters"] == group[-2]["parameters"]
                    for group in groups.values()), "Curvature output was clipped by a point budget")
        require(all(int(group[-1]["parameter_count"]) ==
                    ((9 if key[0] == "1" else 65) if key[-1] == "0" else
                     (5 if key[0] == "1" else 17)) for key, group in groups.items()),
                "Original curvature partition changed")
    else:
        require(all(int(group[-1]["parameter_count"]) == (2 if key[0] == "1" else 4)
                    for key, group in groups.items()), "Stable-control point budget changed")
    return {"physical_steps": len(rows), "curve_attempts": len(groups),
            "profile": profile, "last_accepted_step": 1, "rejected_steps": [2, 3] if original else [2]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--directory", required=True, type=Path)
    args = parser.parse_args()
    out = args.directory.resolve() / ("run-" + uuid.uuid4().hex)
    out.mkdir(parents=True)
    config = (Path(__file__).resolve().parents[2] / "configs/quad/curved_patch_original_curves.conf").read_text()
    records = []
    for name, rollback, profile in (("accepted", False, "original_curvature"),
                                     ("rollback", True, "original_curvature"),
                                     ("stable-accepted", False, "stable_control"),
                                     ("stable-rollback", True, "stable_control")):
        prefix = out / name
        text = config.replace("OUTPUT_PREFIX=build/quad_original_curves", f"OUTPUT_PREFIX={prefix.as_posix()}")
        if profile == "stable_control":
            text = text.replace("ADAPTIVE_MODE=legacy", "ADAPTIVE_MODE=adaptive_stable")
            text = text.replace("# Original curvature-driven workflow; stable-mode point budgets are not enabled.",
                                "# Stable-budget control: original point clipping is intentionally retained.")
            text += "\nADAPTIVE_MAX_ITERATIONS=2\n"
        if rollback:
            text += "\nQUAD_VERIFY_ROLLBACK=1\n"
        conf = prefix.with_suffix(".conf")
        conf.write_text(text)
        process = subprocess.run([str(args.exe.resolve()), "--config", str(conf)], cwd=out,
                                 capture_output=True, timeout=180)
        prefix.with_suffix(".stdout").write_bytes(process.stdout)
        prefix.with_suffix(".stderr").write_bytes(process.stderr)
        require(process.returncode == int(rollback), f"Real-boundary application failed: {process.returncode}; {out}")
        obj = prefix.with_suffix(".obj")
        record = audit(obj)
        require(record["reference_tri_accepted"] and record["source_step"] == 1 and
                (record["boundary"], record["quads"]) ==
                ((20, 120) if profile == "original_curvature" else (4, 0)),
                "Main output promoted a rejected source or fabricated a coarse QUAD region")
        record["history"] = audit_history(prefix, profile)
        manifest = Path(str(prefix) + ".steps") / "manifest.csv"
        original_manifest = manifest.read_text()
        rejected_reason = "global_error_increased" if profile == "original_curvature" else "hybrid_criterion_rejected"
        forged = [original_manifest.replace(rejected_reason, "accepted"),
                  original_manifest.replace(",0," + rejected_reason, ",1," + rejected_reason),
                  "\n".join(original_manifest.splitlines()[:-1]) + "\n"]
        for altered in forged:
            require(altered != original_manifest, "Inactive history negative control")
            manifest.write_text(altered)
            try:
                audit_history(prefix, profile)
            except AssertionError:
                pass
            else:
                raise AssertionError("Forged or incomplete history accepted")
            finally:
                manifest.write_text(original_manifest)
        record["history_negative_controls_rejected"] = len(forged)
        if rollback:
            require(b"QUAD_REAL_BOUNDARY_ROLLBACK previous_nonempty=1 preserved=1" in process.stdout,
                    "Missing nonempty real-boundary rollback witness")
        require(process.stdout.count(b"QUAD_REAL_BOUNDARY source=") == 1 and
                b"mixed_adaptive_epochs=0" in process.stdout,
                "Missing or misleading real-boundary publication receipt")
        negative_dir = out / (name + "-negative")
        negative_dir.mkdir()
        record["negative_controls_rejected"] = negative_controls(obj, negative_dir)
        record["obj_sha256"] = hashlib.sha256(obj.read_bytes()).hexdigest()
        original_bytes = obj.read_bytes()
        blocked = subprocess.run([str(args.exe.resolve()), "--config", str(conf)], cwd=out,
                                 capture_output=True, timeout=15)
        prefix.with_suffix(".existing.stdout").write_bytes(blocked.stdout)
        prefix.with_suffix(".existing.stderr").write_bytes(blocked.stderr)
        require(blocked.returncode != 0 and not blocked.stdout and
                b"output or pending publication already exists" in blocked.stderr and
                obj.read_bytes() == original_bytes,
                "Existing output was not refused before original workflow execution")
        record["existing_output_rejected"] = True
        records.append(record)
    require(records[0] == records[1] and records[2] == records[3],
            "Rollback changed original or stable-control generation")
    report = {"actual_ap_mesh_entry": True, "original_generator_curve_workflow": True,
              "original_native_tree": True, "normal_and_rollback": records[:2],
              "stable_control_normal_and_rollback": records[2:],
              "mixed_adaptive_epochs": 0}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
