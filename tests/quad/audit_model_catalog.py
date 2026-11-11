#!/usr/bin/env python3
"""Research-only model inventory and topology readiness audit.

This is an independent CONTROL-NET diagnostic. It does not instantiate
APMesh, generate physical QUAD, or approve historical 1993 procedures.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

INPUT_MODELS = {
    "Eistute": ("input_models/eistute2.fixed.bp", 4),
    "Book": ("input_models/book_v7a.bp", 28),
    "Ribbed Bracket": ("input_models/ribbed_bracket_nm_decor.bp", 13),
}
REFERENCE_METHODS = {
    "ModelPlanBook": (5, 0),
    "ModelTresPatches": (3, 0),
    "ModelDoisPatchesPlanosCurva1": (2, 0),
    "ModelDoisPatchesPlanosCurva": (2, 0),
    "ModelCurvaBezier": (1, 0),
    "ModelParaboloide": (0, 1),
    "ModelPneu": (0, 2),
    "ModelLadoDescendente": (0, 1),
    "ModelBaseCircular": (0, 1),
    "ModelBaseQuadrada": (0, 1),
    "ModelBordaCurva": (0, 1),
    "ModelDoisPatches": (0, 2),
    "ModelNariz": (0, 14),
    "ModelUtahteapot": (32, 0),
}
UV_EDGES = ((0, 1, 2, 3), (3, 7, 11, 15),
            (12, 13, 14, 15), (0, 4, 8, 12))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_bp(content: str) -> tuple[list[tuple[float, float, float]],
                                   list[tuple[int, ...]]]:
    vertices: list[tuple[float, float, float]] = []
    patches: list[tuple[int, ...]] = []
    for lineno, line in enumerate(content.splitlines(), 1):
        tokens = line.split()
        if not tokens or tokens[0].startswith(("//", "#")):
            continue
        if tokens[0] == "v":
            require(len(tokens) == 4, f"Invalid .bp vertex arity at line {lineno}")
            try:
                xyz = tuple(float(v) for v in tokens[1:])
            except ValueError as error:
                raise ValueError(f"Non-numeric vertex at line {lineno}") from error
            require(all(math.isfinite(v) for v in xyz),
                    f"Nonfinite .bp vertex at line {lineno}")
            vertices.append(xyz)
        elif tokens[0] == "p":
            require(len(tokens) == 17,
                    f"Bezier patch must have 16 control indices at line {lineno}")
            require(all(re.fullmatch(r"\d+", v) for v in tokens[1:]),
                    f"Invalid patch index at line {lineno}")
            indices = tuple(int(v) for v in tokens[1:])
            require(all(0 <= i < len(vertices) for i in indices),
                    f"Patch uses missing control vertex at line {lineno}")
            require(len(set(indices)) == 16,
                    f"Repeated control index within patch at line {lineno}")
            patches.append(indices)
        else:
            raise ValueError(f"Unsupported .bp record at line {lineno}")
    require(len(vertices) > 0 and len(patches) > 0,
            "Empty or incomplete Bezier control model")
    return vertices, patches


def basis(t: float) -> tuple[tuple[float, ...], tuple[float, ...]]:
    s = 1.0 - t
    return ((s*s*s, 3*t*s*s, 3*t*t*s, t*t*t),
            (-3*s*s, 3*s*(1-3*t),
             3*t*(2-3*t), 3*t*t))


def physical_normal(controls: list[tuple[float, float, float]],
                    u: float, v: float) -> tuple[float, float, float]:
    # .bp stores P00,P10,P20,P30,P01,... (four u-points per v row).
    bu, du = basis(u)
    bv, dv = basis(v)
    qu = [0.0, 0.0, 0.0]
    qv = [0.0, 0.0, 0.0]
    for j in range(4):
        for i in range(4):
            p = controls[4*j+i]
            for axis in range(3):
                qu[axis] += p[axis] * du[i] * bv[j]
                qv[axis] += p[axis] * bu[i] * dv[j]
    return (qu[1]*qv[2]-qu[2]*qv[1],
            qu[2]*qv[0]-qu[0]*qv[2],
            qu[0]*qv[1]-qu[1]*qv[0])


def quantize(point: tuple[float, float, float]) -> tuple[int, int, int]:
    # Fixed diagnostic tolerance mirrors the strict control sharing policy.
    return tuple(round(v * 10_000_000) for v in point)


def edge_key(points: list[tuple[float, float, float]]) -> tuple:
    sequence = tuple(map(quantize, points))
    reverse = tuple(reversed(sequence))
    return min(sequence, reverse)


def audit_bp(name: str, path: Path, relative_path: str,
             expected_patches: int) -> dict[str, Any]:
    raw = path.read_bytes()
    vertices, patches = parse_bp(raw.decode("utf-8"))
    require(len(patches) == expected_patches,
            f"{name} patch-count regression: {len(patches)} != {expected_patches}")
    edge_occurrences: dict[tuple, list[dict[str, int]]] = defaultdict(list)
    used = set()
    for patch_id, indices in enumerate(patches):
        used.update(indices)
        for edge_id, corners in enumerate(UV_EDGES):
            control_points = [vertices[indices[i]] for i in corners]
            edge_occurrences[edge_key(control_points)].append(
                {"patch": patch_id, "edge": edge_id})

    valences = Counter(len(owners) for owners in edge_occurrences.values())
    edge_incidence = {
        "distinct_physical_control_curves": len(edge_occurrences),
        "outer_singly_incident_curves": valences[1],
        "paired_shared_curves": valences[2],
        "high_valence_curves": sum(v for k, v in valences.items() if k > 2),
        "maximum_curve_valence": max(valences),
        "high_valence_members": sorted(
            ({"degree": len(owners), "patches": sorted(o["patch"] for o in owners)}
             for owners in edge_occurrences.values() if len(owners) > 2),
            key=lambda record: (-record["degree"], record["patches"])),
    }

    min_jac = math.inf
    max_jac = 0.0
    low_jac = []
    normal_reversals = []
    negative_dots = 0
    for patch_id, indices in enumerate(patches):
        controls = [vertices[i] for i in indices]
        ref = physical_normal(controls, 0.5, 0.5)
        ref_magnitude = math.hypot(*ref)
        if ref_magnitude <= 1e-12:
            low_jac.append(patch_id)
            continue
        has_negative = False
        for j in range(9):
            for i in range(9):
                n = physical_normal(controls, i/8, j/8)
                jac = math.hypot(*n)
                min_jac = min(min_jac, jac)
                max_jac = max(max_jac, jac)
                if not math.isfinite(jac) or jac <= 1e-12:
                    if patch_id not in low_jac:
                        low_jac.append(patch_id)
                if sum(a*b for a, b in zip(n, ref)) < -1e-10:
                    has_negative = True
                    negative_dots += 1
        if has_negative:
            normal_reversals.append(patch_id)

    actual_coordinates = set(map(quantize, vertices))
    return {
        "name": name,
        "input": relative_path,
        "sha256": sha256(raw),
        "format": "cubic Bezier .bp (16 ordered controls per patch)",
        "vertex_records": len(vertices),
        "patches": len(patches),
        "used_vertex_records": len(used),
        "distinct_control_coordinates_at_1e-7": len(actual_coordinates),
        "source_control_edges": edge_incidence,
        "sampled_differential_geometry": {
            "basis": "independent bicubic Bernstein",
            "sampling": "9x9 samples per patch (including boundary)",
            "minimum_cross_derivative_magnitude": min_jac,
            "maximum_cross_derivative_magnitude": max_jac,
            "near_zero_jacobian_patch_indices": low_jac,
            "normal_opposite_to_patch_center_patch_indices": normal_reversals,
            "opposite_normal_samples": negative_dots,
            "note": "Sampled diagnostics only; not a certified global Jacobian bound."
        },
        "research_admission": (
            "REQUIRES_HIGH_VALENCE_BOUNDARY_POLICY"
            if valences and max(valences) > 2 else
            "REQUIRES_PAIRWISE_BOUNDARY_AND_ORIENTATION_TESTS"
        ),
        "validated_complete_hybrid": False,
    }


def method_inventory(source: str) -> dict[str, dict[str, int]]:
    declarations = list(re.finditer(
        r"Geometry\s*\*\s*Models3d::(\w+)\s*\(\s*Geometry\s*\*\s*\w+\s*\)\s*\{",
        source))
    result = {}
    for match in declarations:
        opening = source.index("{", match.start())
        depth = 0
        end = None
        for index in range(opening, len(source)):
            if source[index] == "{":
                depth += 1
            elif source[index] == "}":
                depth -= 1
                if depth == 0:
                    end = index
                    break
        require(end is not None, "Unbalanced built-in model method")
        body = source[opening:end]
        bezier = len(re.findall(r"MakePatch\s*<\s*PatchBezier", body))
        hermite = len(re.findall(r"MakePatch\s*<\s*PatchHermite", body))
        require(bezier + hermite > 0,
                f"No registered patch factory in {match.group(1)}")
        result[match.group(1)] = {
            "patches_declared_in_source": bezier + hermite,
            "bezier": bezier,
            "hermite": hermite,
            "category": "Bezier" if bezier and not hermite
                        else "Hermite" if hermite and not bezier else "Mixed",
            "reader_path": "Models3d C++ constructor (not an input_models/*.bp file)",
            "runtime_hybrid_qualified": False,
        }
    require(set(result) == set(REFERENCE_METHODS),
            "Built-in model inventory changed; explicitly review registrations")
    for name, expected in REFERENCE_METHODS.items():
        require((result[name]["bezier"], result[name]["hermite"]) == expected,
                f"Built-in model control count changed: {name}")
    return dict(sorted(result.items()))


def negative_controls() -> int:
    valid = "\n".join(
        ["v 0 0 0", "v 1 0 0", "v 2 0 0", "v 3 0 0",
         "v 0 1 0", "v 1 1 0", "v 2 1 0", "v 3 1 0",
         "v 0 2 0", "v 1 2 0", "v 2 2 0", "v 3 2 0",
         "v 0 3 0", "v 1 3 0", "v 2 3 0", "v 3 3 0",
         "p " + " ".join(str(i) for i in range(16))])
    require(len(parse_bp(valid)[1]) == 1, "Positive .bp parser control failed")
    variants = [
        valid.replace("v 0 0 0", "v NaN 0 0", 1),
        valid.replace("p 0 1", "p 999 1", 1),
        valid.replace("p 0 1", "p 0 0", 1),
        valid.replace("p 0 1 2", "p 0 1", 1),
        valid.replace("v 0 0 0", "v 0 0", 1),
        valid.replace("p 0 1", "x 0 1", 1),
        "v 0 0 0\np " + " ".join(str(i) for i in range(16)),
    ]
    for index, damaged in enumerate(variants):
        try:
            parse_bp(damaged)
        except ValueError:
            continue
        raise AssertionError(f"Malformed .bp negative control {index} accepted")
    return len(variants)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    root = args.root.resolve()

    inputs = {}
    for name, (relative, count) in INPUT_MODELS.items():
        inputs[name] = audit_bp(name, root / relative, relative, count)
    models_cpp = root / "src/input_output/models_3d.cpp"
    raw_cpp = models_cpp.read_bytes()
    constructors = method_inventory(raw_cpp.decode("utf-8"))
    negative = negative_controls()

    report = {
        "schema": 1,
        "status": "SOURCE_MODEL_AUDIT_ONLY_NO_HYBRID_MESH_GENERATED",
        "historical_1993_method_implemented": False,
        "production_quad_enabled": False,
        "input_bp_models": inputs,
        "builtin_models": constructors,
        "builtin_models_source": str(models_cpp.relative_to(root)),
        "builtin_models_source_sha256": sha256(raw_cpp),
        "summary": {
            "versioned_bp_input_files": len(inputs),
            "bp_total_patches": sum(x["patches"] for x in inputs.values()),
            "builtin_model_constructors": len(constructors),
            "builtin_bezier_patches_declared": sum(
                x["bezier"] for x in constructors.values()),
            "builtin_hermite_patches_declared": sum(
                x["hermite"] for x in constructors.values()),
            "requested_bolha_model_identified": False,
            "requested_bolha_note":
                "No ModelBolha factory or tracked input_models/bolha asset was found.",
            "rejected_malformed_bp_controls": negative,
        },
        "limits": {
            "file_format_coverage": ".bp control grids, no historical CAD importer",
            "builtin_model_verification": "Static MakePatch factory census, not runtime",
            "normal_checks": "9x9 sample diagnostic, not a global Jacobian proof",
            "edge_incidence": "1e-7 rounded control curve matching, not topological welding",
            "quad_hybrid_output": "not produced",
            "patch_boundaries_and_lifecycle": "not qualified across patches",
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True,
                                      allow_nan=False) + "\n", encoding="utf-8")
    print("quad_model_catalog=ok bp_models=3 bp_patches=45 "
          "builtin_models=14 builtin_Bezier=45 builtin_Hermite=23 "
          "malformed_bp_rejected=7 bolha=NOT_TRACKED "
          "NOT_hybrid_model_generation")


if __name__ == "__main__":
    main()
