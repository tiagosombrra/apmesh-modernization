#!/usr/bin/env python3
"""Generate self-identifying synthetic APMesh Mesh Studio fixture data.

Every case is synthetic and must never be presented as APMesh research output.
The generator is deterministic and uses Python's standard library only.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "cases"
EXPERIMENTS = ROOT / "experiments"
SCHEMA = "apmesh.meshstudio.synthetic.v1"


def add_case(case_id, nodes, faces, *, expected_valid=True, diagnostic=None,
             reference_normal=None, curves=None, surface=None, note="",
             obj_mutation=None):
    """Write a small visible OBJ and its explicit semantic sidecar."""
    assert case_id.startswith("synthetic_")
    record = {
        "schema": SCHEMA,
        "case_id": case_id,
        "synthetic": True,
        "watermark": "SYNTHETIC TEST FIXTURE — NOT AN APMesh SCIENTIFIC RESULT",
        "coordinate_space": "XYZ",
        "topology_scope": "patch_local",
        "source_model": "analytically_created_fixture",
        "expected": {
            "valid": expected_valid,
            "diagnostic": diagnostic,
            "node_count": len(nodes),
            "triangle_count": sum(f["kind"] == "triangle" for f in faces),
            "quad_count": sum(f["kind"] == "quad" for f in faces),
        },
        "reference_normal": reference_normal,
        "nodes": nodes,
        "faces": faces,
        "curves": curves or [],
        "surface": surface,
        "notes": note,
    }
    obj = ["# SYNTHETIC TEST FIXTURE - NOT AN APMesh SCIENTIFIC RESULT",
           "# " + case_id]
    for node in nodes:
        obj.append("v " + " ".join(format(c, ".17g") for c in node))
    last_patch = None
    for face in faces:
        if face["patch_id"] != last_patch:
            last_patch = face["patch_id"]
            obj.append("g " + last_patch)
        obj.append("f " + " ".join(str(i + 1) for i in face["nodes"]))
    content = "\n".join(obj) + "\n"
    if obj_mutation:
        content = obj_mutation(content)
    (CASES / f"{case_id}.obj").write_text(content, encoding="utf-8")
    record["obj_sha256"] = hashlib.sha256(content.encode("utf-8")).hexdigest()
    (CASES / f"{case_id}.json").write_text(
        json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return record


def face(kind, nodes, uv, patch="patch_0"):
    return {"kind": kind, "patch_id": patch, "nodes": list(nodes),
            "uv": [[float(v) for v in pair] for pair in uv]}


def create_grid(quads=True, curved=False):
    n = 3
    xy = [(i / (n - 1), j / (n - 1)) for j in range(n) for i in range(n)]
    nodes = [[u, v, .2 * u * u + .1 * v * v if curved else 0.0] for u, v in xy]
    faces = []
    for j in range(n - 1):
        for i in range(n - 1):
            a, b, c, d = j * n + i, j * n + i + 1, (j + 1) * n + i + 1, (j + 1) * n + i
            if quads:
                faces.append(face("quad", [a, b, c, d], [xy[k] for k in [a, b, c, d]]))
            else:
                faces.append(face("triangle", [a, b, c], [xy[k] for k in [a, b, c]]))
                faces.append(face("triangle", [a, c, d], [xy[k] for k in [a, c, d]]))
    return nodes, faces


def create_annulus():
    outer = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    inner = [(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)]
    xy = outer + inner
    nodes = [[u, v, 0.0] for u, v in xy]
    faces = [face("quad", [4, 5, 6, 7], [inner[k] for k in range(4)])]
    for i in range(4):
        j = (i + 1) % 4
        for node_ids in ([i, j, 4 + j], [i, 4 + j, 4 + i]):
            faces.append(face("triangle", node_ids, [xy[k] for k in node_ids]))
    return nodes, faces


def create_fan(valence, mismatch=False):
    nodes, faces = [], []
    shared = [[x, 0.0, 0.0] for x in [0.0, 0.5, 1.0]]
    by_patch_samples = {}
    for patch in range(valence):
        angle = 2 * math.pi * patch / valence
        c, s = math.cos(angle), math.sin(angle)
        start = len(nodes)
        points = [[x, r * c, r * s] for r in [0.0, 1.0] for x in [0.0, 0.5, 1.0]]
        if mismatch and patch == valence - 1:
            points[1][0] = 0.51
        nodes.extend(points)
        patch_id = f"patch_{patch}"
        by_patch_samples[patch_id] = [[p[0], p[1], p[2]] for p in points[:3]]
        for i in range(2):
            ids = [start + i, start + i + 1, start + 3 + i + 1, start + 3 + i]
            uv = [[j / 2, k] for j, k in [(i, 0), (i + 1, 0), (i + 1, 1), (i, 1)]]
            faces.append(face("quad", ids, uv, patch_id))
    curves = [{
        "curve_id": "shared_axis_0",
        "sample_parameters": [0.0, 0.5, 1.0],
        "canonical_xyz": shared,
        "incident_patches": [f"patch_{i}" for i in range(valence)],
        "by_patch_xyz": by_patch_samples,
        "topology_weld_approved": False,
    }]
    return nodes, faces, curves


def history():
    records = [
        ("synthetic_bezier", "tri", 0, "accepted", 1.00, 16, 0.42, 0.100),
        ("synthetic_bezier", "tri", 1, "accepted", 0.55, 38, 0.57, 0.144),
        ("synthetic_bezier", "tri", 2, "rejected", 0.74, 72, 0.49, 0.201),
        ("synthetic_bezier", "tri", 3, "accepted", 0.31, 96, 0.63, 0.258),
        ("synthetic_bezier", "hybrid", 0, "accepted", 1.00, 12, 0.51, 0.083),
        ("synthetic_bezier", "hybrid", 1, "accepted", 0.43, 28, 0.61, 0.112),
        ("synthetic_bezier", "hybrid", 2, "rejected", 0.58, 51, 0.55, 0.166),
        ("synthetic_bezier", "hybrid", 3, "accepted", 0.25, 64, 0.70, 0.194),
    ]
    with (EXPERIMENTS / "synthetic_nonmonotone_epochs.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(("dataset", "method", "epoch", "acceptance", "normalized_error",
                         "elements", "shape_quality_median", "wall_seconds", "synthetic"))
        for record in records:
            writer.writerow((*record, True))


def main():
    CASES.mkdir(parents=True, exist_ok=True)
    EXPERIMENTS.mkdir(parents=True, exist_ok=True)
    for old in CASES.glob("synthetic_*.*"):
        old.unlink()
    add_case("synthetic_single_triangle",
             [[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]],
             [face("triangle", [0, 1, 2], [(0, 0), (1, 0), (0, 1)])],
             reference_normal=[0, 0, 1], note="Positive triangle calibration.")
    add_case("synthetic_single_quad",
             [[0., 0., 0.], [1., 0., 0.], [1., 1., 0.], [0., 1., 0.]],
             [face("quad", [0, 1, 2, 3], [(0, 0), (1, 0), (1, 1), (0, 1)])],
             reference_normal=[0, 0, 1], note="Four positive planar UV turns.")
    nodes, faces = create_grid(quads=False)
    add_case("synthetic_planar_tri_grid", nodes, faces, reference_normal=[0, 0, 1])
    nodes, faces = create_grid(quads=True)
    add_case("synthetic_planar_quad_grid", nodes, faces, reference_normal=[0, 0, 1])
    nodes, faces = create_grid(quads=True, curved=True)
    add_case("synthetic_curved_bezier_grid", nodes, faces,
             surface={"expression": "[u,v,0.2*u*u+0.1*v*v]",
                      "source_derivatives": ["[1,0,0.4*u]", "[0,1,0.2*v]"],
                      "parameter_domain": [[0, 1], [0, 1]],
                      "evaluation": "analytical_synthetic_not_original_Bezier"},
             note="An analytically specified polynomial representable by a Bezier patch.")
    nodes, faces = create_annulus()
    add_case("synthetic_quad_aft_transition", nodes, faces,
             reference_normal=[0, 0, 1],
             note="One interior QUAD and eight exterior TRI: 4 QUAD/TRI seam edges.")
    for n in (2, 3, 4, 28):
        nodes, faces, curves = create_fan(n)
        add_case(f"synthetic_shared_curve_fan{n}", nodes, faces, curves=curves,
                 note=f"{n} distinct patch-local sheets share logical curve samples; not welded.")
    base_quad_nodes = [[0., 0., 0.], [1., 0., 0.], [1., 1., 0.], [0., 1., 0.]]
    add_case("synthetic_concave_uv", base_quad_nodes,
             [face("quad", [0, 1, 2, 3], [(0, 0), (1, 0), (.25, .25), (0, 1)])],
             expected_valid=False, diagnostic="concave_uv",
             reference_normal=[0, 0, 1],
             note="Physical square remains convex while UV is deliberately concave.")
    add_case("synthetic_inverted_triangle", [[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]],
             [face("triangle", [0, 2, 1], [(0, 0), (0, 1), (1, 0)])],
             expected_valid=False, diagnostic="uv_winding",
             reference_normal=[0, 0, 1])
    add_case("synthetic_degenerate_quad", base_quad_nodes,
             [face("quad", [0, 1, 1, 3], [(0, 0), (1, 0), (1, 0), (0, 1)])],
             expected_valid=False, diagnostic="repeated_vertex")
    add_case("synthetic_out_of_range_index", base_quad_nodes,
             [face("quad", [0, 1, 4, 3], [(0, 0), (1, 0), (1, 1), (0, 1)])],
             expected_valid=False, diagnostic="out_of_range_index")
    add_case("synthetic_nonfinite_coordinate", base_quad_nodes,
             [face("quad", [0, 1, 2, 3], [(0, 0), (1, 0), (1, 1), (0, 1)])],
             expected_valid=False, diagnostic="nonfinite_coordinate",
             obj_mutation=lambda s: s.replace("v 0 0 0", "v nan 0 0", 1))
    nodes, faces, curves = create_fan(3, mismatch=True)
    add_case("synthetic_shared_curve_mismatch", nodes, faces, curves=curves,
             expected_valid=False, diagnostic="shared_curve_mismatch")
    history()
    manifests = []
    for path in sorted(CASES.glob("*.json")):
        r = json.loads(path.read_text(encoding="utf-8"))
        manifests.append({"case_id": r["case_id"], "expected": r["expected"],
                          "obj_sha256": r["obj_sha256"]})
    manifest = {"schema": SCHEMA, "synthetic": True,
                "fixture_cases": manifests,
                "experiment_file": "experiments/synthetic_nonmonotone_epochs.csv",
                "publication_warning": "Never report synthetic fixture measurements as actual APMesh scientific experiments."}
    (ROOT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"generated={len(manifests)} synthetic_cases")


if __name__ == "__main__":
    main()
