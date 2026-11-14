"""Exercise the real ap_mesh entry and independently audit its curved patch."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import uuid
from test_m4_real_model_hybrid import golden, approximately, cross, vector, dot


def require(value, message):
    if not value:
        raise AssertionError(message)


def audit(path):
    xyz, uv, faces = [], [], []
    for line in path.read_text().splitlines():
        row = line.split()
        if not row:
            continue
        if row[0] == "v":
            xyz.append(tuple(map(float, row[1:])))
        elif row[0] == "vt":
            uv.append(tuple(map(float, row[1:])))
        elif row[0] == "f":
            ids = []
            for item in row[1:]:
                a, b = map(int, item.split("/"))
                require(a == b and a > 0, "Foreign physical/UV index")
                ids.append(a - 1)
            faces.append(ids)
    return inspect(xyz, uv, faces)


def inspect(xyz, uv, faces):
    require(len(xyz) == len(uv) > 0 and faces, "Empty application output")
    require(any(len(f) == 4 for f in faces) and any(len(f) == 3 for f in faces),
            "Application did not generate both element types")
    for p, q in zip(xyz, uv):
        require(len(q) == 2 and all(math.isfinite(x) and 0 <= x <= 1 for x in q),
                "Invalid exported UV")
        require(approximately(p, golden(*q)[0]), "Source Bezier mapping mismatch")
    edges = {}
    area = 0.
    for face in faces:
        require(len(face) in (3, 4) and len(set(face)) == len(face), "Invalid face")
        require(all(0 <= i < len(uv) for i in face), "Foreign index")
        for a, b in zip(face, face[1:] + face[:1]):
            edges.setdefault(tuple(sorted((a, b))), []).append((a, b))
        for slots in ((0, 1, 2), (0, 2, 3)) if len(face) == 4 else ((0, 1, 2),):
            ids = [face[k] for k in slots]
            a, b, c = [uv[i] for i in ids]
            twice = (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
            require(twice > 0, "Inverted UV facet")
            area += twice / 2
            center = tuple(sum(uv[i][k] for i in ids)/3 for k in range(2))
            _, du, dv = golden(*center)
            physical = cross(vector(xyz[ids[0]], xyz[ids[1]]),
                             vector(xyz[ids[0]], xyz[ids[2]]))
            require(dot(physical, cross(du, dv)) > 0, "Reversed physical facet")
    boundary = 0
    for uses in edges.values():
        require(len(uses) <= 2, "Nonmanifold edge")
        if len(uses) == 2:
            require(uses[0] == uses[1][::-1], "Shared winding mismatch")
        else:
            a, b = [uv[i] for i in uses[0]]
            require(any(a[k] == b[k] and a[k] in (0, 1) for k in (0, 1)),
                    "Interior gap")
            boundary += 1
    require(boundary == 16 and len(xyz)-len(edges)+len(faces) == 1,
            "Source boundary/disk differs")
    require(abs(area - 1) < 1e-8, "Incomplete or overlapping UV area")
    return {"nodes": len(xyz), "quads": sum(len(f) == 4 for f in faces),
            "triangles": sum(len(f) == 3 for f in faces), "boundary": boundary}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--exe", required=True, type=Path)
    p.add_argument("--directory", required=True, type=Path)
    args = p.parse_args()
    root = args.directory.resolve() / ("run-" + uuid.uuid4().hex)
    root.mkdir(parents=True, exist_ok=False)
    def execute(name, rollback=False, model="builtin:curva_bezier"):
        config = root/(name+".conf")
        config.write_text(f"INPUT_MODEL={model}\nOUTPUT_PREFIX={root/name}\n"
                          "MESH_ELEMENT_KIND=quad_uv\n"
                          "QUAD_EXPERIMENTAL_CASE=curved_bezier_fixed16_vertex_mean_v1\n"
                          f"QUAD_VERIFY_ROLLBACK={int(rollback)}\nNUM_THREADS=1\nNUM_PROCESSES=1\n")
        r = subprocess.run([str(args.exe.resolve()), "--config", str(config)],
                           capture_output=True, timeout=60)
        (root/(name+".stdout")).write_bytes(r.stdout)
        (root/(name+".stderr")).write_bytes(r.stderr)
        return r
    r = execute("accepted")
    require(r.returncode == 0 and b"ids_unique=1 published=1" in r.stdout,
            "Real CLI generation or physical identities failed")
    require(b"QUAD_TYPED_HISTORY_CLONE accepted_clone=1 partial_failure_rollback=1" in r.stdout and
            b"source_observers_preserved=1 adaptive_epochs=0" in r.stdout,
            "Typed QUAD/TRI history clone or rollback guard did not run")
    result = audit(root/"accepted.obj")
    initial = (root/"accepted.obj").read_bytes()
    r = subprocess.run([str(args.exe.resolve()), "--config", str(root/"accepted.conf")],
                       capture_output=True, timeout=60)
    require(r.returncode != 0 and (root/"accepted.obj").read_bytes() == initial,
            "Existing output was overwritten")
    r = execute("rollback", True)
    require(b"QUAD_TYPED_HISTORY_CLONE accepted_clone=1 partial_failure_rollback=1" in r.stdout,
            "Rollback case did not preserve the typed history probe")
    require(r.returncode == 1 and b"QUAD_ROLLBACK preserved=1 previous_nonempty=1" in r.stdout,
            "Nonempty physical publication rollback not demonstrated")
    require(audit(root/"rollback.obj") == result, "Rollback lost prior valid output")
    r = execute("unsupported", model="missing.bp")
    require(r.returncode != 0 and not (root/"unsupported.obj").exists(),
            "Invalid source was published")
    # Independently reject a physical corruption and reversed topology.
    text = (root/"accepted.obj").read_text()
    for i, changed in enumerate((text.replace("v ", "v 999 ", 1),
                                 text.replace("f ", "f 1/1 ", 1))):
        bad = root/f"corrupt-{i}.obj"
        bad.write_text(changed)
        try:
            audit(bad)
        except (AssertionError, ValueError, IndexError):
            continue
        raise AssertionError("Corrupted physical mesh passed independent audit")
    report = {"actual_ap_mesh_entry": True, "model": "Models3d::ModelCurvaBezier",
              "result": result, "rollback_nonempty": True,
              "native_AFT": True, "independent_Bezier_oracle": True,
              "typed_history_clone_guard": True,
              "OBJ_sha256": hashlib.sha256(initial).hexdigest(), "adaptive_epochs": 0}
    (root/"report.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
