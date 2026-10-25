#!/usr/bin/env python3
"""Actual null-input controls and independent curvature-report checks."""

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import subprocess
import shutil
import tempfile


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def difference(a, b):
    return tuple(x-y for x, y in zip(a, b))


def check_curvature(root, curved):
    fixture = json.loads((root / "fixture.json").read_text(encoding="utf-8"))
    nodes = {node[0]: node for node in fixture["nodes"]}
    faces = fixture["faces"]
    assert len(nodes) == 5 and len(faces) == 4
    edges = Counter(tuple(sorted((face[a], face[b]))) for face in faces for a, b in ((0, 1), (1, 2), (2, 0)))
    boundary = {node for edge, count in edges.items() if count == 1 for node in edge}
    numerator, denominator, inverse_residuals = [], [], []
    for identity, node in nodes.items():
        point = node[1:4]
        exact_u, exact_v = point[0]+.5, .5-point[2]
        u, v = node[6:8]
        assert 0 <= u <= 1 and 0 <= v <= 1
        if curved:
            assert math.isclose(point[1], 20*exact_u*(1-exact_u)*exact_v*(1-exact_v), abs_tol=1e-12)
            # Validate the unchanged evaluator's actual recovered parameters.
            # Curvature at approximate inverse parameters is not exact point curvature.
            inverse_residuals.append(math.dist(point, (u-.5, 20*u*(1-u)*v*(1-v), .5-v)))
            fu, fv = 20*(1-2*u)*v*(1-v), 20*u*(1-u)*(1-2*v)
            fuu, fvv, fuv = -40*v*(1-v), -40*u*(1-u), 20*(1-2*u)*(1-2*v)
            analytic = (fuu*fvv-fuv*fuv)/(1+fu*fu+fv*fv)**2
            assert abs(analytic) > 1
        else:
            assert point[2] == 0
            analytic = 0
        assert math.isclose(node[4], analytic, rel_tol=1e-11, abs_tol=1e-11)
        areas, angles = [], []
        for face in faces:
            if identity not in face:
                continue
            others = [nodes[index][1:4] for index in face if index != identity]
            a, b = (difference(other, point) for other in others)
            norm = math.sqrt(math.fsum(x*x for x in cross(a, b)))
            areas.append(norm/2)
            angles.append(math.atan2(norm, math.fsum(x*y for x, y in zip(a, b))))
        discrete = 3*((math.pi if identity in boundary else 2*math.pi)-math.fsum(angles))/math.fsum(areas)
        assert math.isclose(node[5], discrete, rel_tol=1e-11, abs_tol=1e-11)
        if curved:
            numerator.append((discrete-analytic)**2)
            denominator.append(analytic**2)
    expected = math.sqrt(math.fsum(numerator)/math.fsum(denominator))/len(nodes) if curved else 0
    summaries = re.findall(rb"^submesh_curvature_error\[(\d+)\]=([^\r\n]+)",
                           (root / "0erro0.log").read_bytes(), re.M)
    assert len(summaries) == 1 and summaries[0][0] == b"0", "Missing or ambiguous submesh summary"
    actual = float(summaries[0][1])
    assert math.isfinite(actual) and math.isclose(actual, expected, rel_tol=5e-6, abs_tol=1e-12), (actual, expected)
    assert (actual > 0) == curved
    return {"nodes": len(nodes), "triangles": len(faces), "independent_error": expected,
            "reported_error": actual, "analytic_surface": "20*u*(1-u)*v*(1-v)" if curved else "plane",
            "max_inverse_spatial_residual": max(inverse_residuals, default=0),
            "limit": "Analytic curvature is checked at actual recovered parameters, not exact physical-point parameters."}


def run(executable, workspace):
    workspace.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="run-", dir=workspace)).resolve()
    report = {"status": "running", "cases": {}}
    try:
        for mode in ("null-geometry", "null-mesh", "null-both", "curved", "planar"):
            with (root / f"{mode}.stdout.log").open("wb") as stdout, (root / f"{mode}.stderr.log").open("wb") as stderr:
                process = subprocess.run([str(executable), mode, str(root / mode)], stdout=stdout,
                                         stderr=stderr, timeout=30)
            report["cases"][mode] = {"exit_code": process.returncode}
            assert process.returncode == 0, (mode, process.returncode, root)
            if mode in ("curved", "planar"):
                report["cases"][mode].update(check_curvature(root / mode, mode == "curved"))
        report["checker_negative_controls"] = []
        for label, value in (("wrong-zero", b"0"), ("nonfinite", b"nan"), ("missing", None)):
            broken = root / label
            broken.mkdir()
            shutil.copy2(root / "curved/fixture.json", broken / "fixture.json")
            data = (root / "curved/0erro0.log").read_bytes()
            altered = re.sub(rb"^submesh_curvature_error\[0\]=[^\r\n]+", b"" if value is None else
                             b"submesh_curvature_error[0]="+value, data, flags=re.M)
            assert data != altered
            (broken / "0erro0.log").write_bytes(altered)
            detected = False
            try:
                check_curvature(broken, True)
            except AssertionError:
                detected = True
            assert detected, label
            report["checker_negative_controls"].append(label)
        report["status"] = "passed"
    except Exception as error:
        report["status"], report["failure"] = "failed", repr(error)
        raise
    finally:
        (root / "report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    return {**report, "report": str(root / "report.json")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.exe.resolve(), args.workspace.resolve())))
