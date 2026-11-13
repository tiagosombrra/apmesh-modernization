#!/usr/bin/env python3
"""Independently verify every physical 3D face in original accepted TRI OBJ.

Original GeneratorAdaptive writes full 3D OBJ on each accepted source step.
The Wavefront file has no original patch groups, so this checks model-wide
face geometry only; it cannot certify patch owners or non-manifold sheets.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path


ORIGINALS = {
    "eistute": {
        "profile": "aft_postprocess_quality_0p80",
        "source": "r2c18",
        "sha256": "fdce4714524b88f536ec9f8eddc467e54e638dc6e765784ab68edc9a366a0a3f",
        "expected_faces": {1: 1168, 2: 2008, 4: 4032},
    },
    "book": {
        "profile": "pinned_article",
        "source": "r2c13",
        "sha256": "3c4255cbd2f46bd2dce5f0e86b8e7ee9ac0c58df949d4563dd821deedcd8412d",
        "expected_faces": {1: 4256},
    },
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_source_obj(lines):
    vertices, triangles = [], []
    for index, raw in enumerate(lines, 1):
        fields = raw.split()
        if not fields or fields[0].startswith("#"):
            continue
        if fields[0] == "v":
            require(len(fields) == 4,
                    f"Original OBJ physical vertex does not have XYZ at {index}")
            xyz = tuple(float(n) for n in fields[1:])
            require(all(math.isfinite(n) for n in xyz),
                    "Nonfinite original source OBJ physical vertex")
            vertices.append(xyz)
        elif fields[0] == "f":
            require(len(fields) == 4,
                    f"Original accepted TRI OBJ face is not a triangle at {index}")
            require(all(field.isdecimal() for field in fields[1:]),
                    "Original TRI OBJ face has non-canonical node indexing")
            triangles.append(tuple(int(field) for field in fields[1:]))
        else:
            raise ValueError(
                f"Unsupported original accepted TRI OBJ record {fields[0]} at {index}")
    require(vertices and triangles,
            "Original accepted TRI OBJ export is empty")
    observed = set()
    min_area = math.inf
    max_area = 0.0
    minimum_shape = math.inf
    total_area = 0.0
    referenced = set()
    for idx, (a, b, c) in enumerate(triangles, 1):
        require(len({a, b, c}) == 3 and
                all(1 <= item <= len(vertices) for item in (a, b, c)),
                f"Original OBJ face #{idx} has repeated or foreign node indices")
        face_key = tuple(sorted((a, b, c)))
        require(face_key not in observed,
                f"Duplicate source TRI face node identity #{idx}")
        observed.add(face_key)
        referenced.update((a, b, c))
        va, vb, vc = vertices[a - 1], vertices[b - 1], vertices[c - 1]
        ab = tuple(vb[i] - va[i] for i in range(3))
        ac = tuple(vc[i] - va[i] for i in range(3))
        bc = tuple(vc[i] - vb[i] for i in range(3))
        cross = (ab[1] * ac[2] - ab[2] * ac[1],
                 ab[2] * ac[0] - ab[0] * ac[2],
                 ab[0] * ac[1] - ab[1] * ac[0])
        twice_area = math.hypot(*cross)
        squared_lengths = sum(v * v for edge in (ab, ac, bc)
                              for v in edge)
        require(math.isfinite(twice_area) and
                math.isfinite(squared_lengths) and
                squared_lengths > 0.0 and twice_area > 0.0,
                f"Original accepted TRI physical face #{idx} has zero/nonfinite 3D area")
        quality = 2.0 * math.sqrt(3.0) * twice_area / squared_lengths
        require(math.isfinite(quality) and quality > 0.0 and
                quality <= 1.0 + 1e-9,
                f"Original accepted TRI physical face #{idx} has invalid independent shape")
        area = 0.5 * twice_area
        min_area = min(min_area, area)
        max_area = max(max_area, area)
        minimum_shape = min(minimum_shape, quality)
        total_area += area
    return {
        "exported_3d_vertices": len(vertices),
        "exported_3d_TRI_faces": len(triangles),
        "referenced_3d_vertices": len(referenced),
        "unreferenced_exported_vertices": len(vertices) - len(referenced),
        "all_faces_finite_and_nonzero_3d_area": True,
        "all_face_indices_local_to_export_and_unique": True,
        "physical_min_face_area": min_area,
        "physical_max_face_area": max_area,
        "physical_sum_unsigned_face_areas": total_area,
        "physical_min_independent_tri_shape_quality": minimum_shape,
        "independent_face_orientation_and_global_self_intersection_qualified": False,
        "original_patch_group_ownership_qualified": False,
        "accepted_global_nonmanifold_QUAD_AFT_mesh": False,
    }


def negative_controls():
    base = ["v 0 0 0", "v 1 0 0", "v 0 1 0", "f 1 2 3"]
    malformed = {
        "repeated_vertex": base[:-1] + ["f 1 1 3"],
        "foreign_index": base[:-1] + ["f 1 2 99"],
        "zero_area": ["v 0 0 0", "v 1 0 0", "v 2 0 0", "f 1 2 3"],
        "not_finite": ["v nan 0 0", *base[1:]],
        "duplicated_face": base + ["f 3 2 1"],
    }
    for name, broken in malformed.items():
        try:
            read_source_obj(broken)
        except ValueError:
            continue
        raise ValueError(f"Original 3D TRI face negative control passed incorrectly: {name}")
    return len(malformed)


def validate_original_case(model, spec, profile_root, actual, expected):
    prefix = profile_root / f"{model}_{spec['profile']}"
    receipts = {int(item["step"]): item
                for item in actual["per_accepted_step_receipts"]}
    observed = {}
    for step, exact_faces in expected.items():
        require(step in receipts, "Missing actual original source TRI accepted epoch")
        acceptance = Path(f"{prefix}_passo_{step}_acceptance_accepted.log")
        mesh = Path(f"{prefix}_passo_{step}_malha_{step}.obj")
        require(acceptance.is_file() and mesh.is_file(),
                f"Original accepted source TRI OBJ missing for {model} step {step}")
        require(sha(acceptance) == receipts[step]["acceptance_log_sha256"],
                "Original accepted TRI OBJ is not backed by matching accepted source log")
        fields = {}
        for line in acceptance.read_text(encoding="utf-8").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                fields[key] = value
        require(fields.get("step") == str(step) and fields.get("accepted") == "1"
                and float(fields["quality_min_3d"]) > 0.0
                and float(fields["quality_min_uv"]) > 0.0,
                "Original accepted TRI source quality/commit mismatch")
        mesh_data = read_source_obj(mesh.read_text(encoding="utf-8").splitlines())
        require(mesh_data["exported_3d_TRI_faces"] == exact_faces,
                f"Original {model} TRI OBJ face count deviated from native evidence")
        observed[str(step)] = {
            **mesh_data,
            "original_accepted_source_epoch": step,
            "original_model": model,
            "original_3d_OBJ_sha256": sha(mesh),
            "source_acceptance_log_sha256": sha(acceptance),
            "original_current_accepted_global_min_quality_3d":
                float(fields["quality_min_3d"]),
            "original_current_accepted_global_min_quality_uv":
                float(fields["quality_min_uv"]),
        }
    return observed


def run(r2c13, r2c18, output):
    source13 = r2c13 / "r2c13_accepted_generator_epochs.json"
    source18 = r2c18 / "r2c18_original_aft_postprocess_profiles.json"
    data13 = json.loads(source13.read_text(encoding="utf-8"))
    data18 = json.loads(source18.read_text(encoding="utf-8"))
    require(data13["schema"] ==
            "apmesh.quad.r2c13.actual_production_generator_epochs.v1"
            and data18["schema"] ==
            "apmesh.quad.r2c18.original_tri_aft_postprocess_sensitivity.v1",
            "Wrong original GeneratorAdaptive source epoch report")
    controls = negative_controls()
    result = {
        "schema": "apmesh.quad.r2c20.original_accepted_tri_3d_obj_face_audit.v1",
        "original_r2c13_report_sha256": sha(source13),
        "original_r2c18_report_sha256": sha(source18),
        "independent_adversarial_negative_controls_passed": controls,
        "scope": "original accepted global source TRI 3D OBJ geometry",
        "not_an_original_patchwise_mesh_quality_proof": True,
        "not_an_original_UV_3d_orientation_admission": True,
        "not_a_global_nonmanifold_QUAD_AFT_welding_approval": True,
        "models": {},
    }
    for model, spec in ORIGINALS.items():
        if spec["source"] == "r2c18":
            cases = data18["models"][model]["scenarios"]
            directory = r2c18
        else:
            cases = data13["models"][model]["cases"]
            directory = r2c13
        actual = next((c for c in cases
                       if c["profile"] == spec["profile"]), None)
        require(actual is not None and
                actual["original_input_model_sha256"] == spec["sha256"] and
                set(actual.get("accepted_step_ids", [])) ==
                set(spec["expected_faces"]),
                "Original true accepted TRI epochs or model SHA-256 drifted")
        profile_dir = directory / f"{model}_{spec['profile']}"
        result["models"][model] = {
            "profile": spec["profile"],
            "original_model_sha256": spec["sha256"],
            "all_original_accepted_3d_TRI_faces":
                validate_original_case(model, spec, profile_dir,
                                       actual, spec["expected_faces"]),
        }
    output.mkdir(parents=True, exist_ok=True)
    target = output / "r2c20_original_accepted_tri_3d_face_integrity.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print("R2C20_ALL_ACCEPTED_ORIGINAL_TRI_3D_OBJ_FACE_INTEGRITY",
          json.dumps({
              name: {
                  "accepted_source_steps": list(
                      model["all_original_accepted_3d_TRI_faces"]),
                  "audited_actual_original_TRI_faces": sum(
                      step["exported_3d_TRI_faces"] for step in
                      model["all_original_accepted_3d_TRI_faces"].values()),
                  "minimum_face_area": min(
                      step["physical_min_face_area"] for step in
                      model["all_original_accepted_3d_TRI_faces"].values())
              } for name, model in result["models"].items()
          }, sort_keys=True),
          "adversarial_negative_controls=5",
          "current_patchwise_quality_unqualified=1",
          "nonmanifold_welding_approved=0")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--r2c13", required=True, type=Path)
    parser.add_argument("--r2c18", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    a = parser.parse_args()
    run(a.r2c13.resolve(), a.r2c18.resolve(), a.output.resolve())


if __name__ == "__main__":
    main()
