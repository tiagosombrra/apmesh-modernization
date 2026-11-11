#!/usr/bin/env python3
"""Research-only UV-to-XYZ analytic surface lift of real C++ QUAD and M5 TRI.

This is not a physical APMesh CAD/model boundary, a 1993 hybrid generator,
an adviser-approved historical centroid, or a production mesh mode.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

from test_m5_constrained_delaunay import edges, read_obj, require, validate


def height(u: float, v: float, curvature: float) -> float:
    return curvature * u * (1.0 - u) * v * (1.0 - v)


def surface_normal(u: float, v: float, curvature: float):
    return (-curvature * (1.0 - 2.0 * u) * v * (1.0 - v),
            -curvature * u * (1.0 - u) * (1.0 - 2.0 * v), 1.0)


def surface_lift(vertices, curvature):
    require(math.isfinite(curvature) and abs(curvature) <= 4.0,
            "Invalid experimental curvature")
    mapped = []
    for u, v, z in vertices:
        require(all(math.isfinite(x) for x in (u, v, z))
                and 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0 and abs(z) < 1e-14,
                "Expected finite parametric UV in unit square with z=0")
        mapped.append((u, v, height(u, v, curvature)))
    require(len(set(mapped)) == len(mapped), "Lift collapsed distinct UV vertices")
    return mapped


def vector(a, b):
    return tuple(y - x for x, y in zip(a, b))


def cross3(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def physical_quality(uv, xyz, quads, tris, seam, curvature):
    require(len(uv) == len(xyz) == 69, "Unexpected mapped vertex inventory")
    require(all(a[0] == b[0] and a[1] == b[1] for a, b in zip(uv, xyz)),
            "Analytic lift changed parameter coordinates")
    require(len(quads) == 42 and len(tris) == 36 and len(seam) == 20,
            "Unexpected native research topology")
    incidence = defaultdict(list)
    for kind, faces in (("QUAD", quads), ("TRI", tris)):
        for face in faces:
            for a,b in zip(face, face[1:] + face[:1]):
                incidence[tuple(sorted((a,b)))].append((kind,a,b))
    seam_from_xyz = sorted(e for e, adjacent in incidence.items()
                           if len(adjacent) == 2 and adjacent[0][0] != adjacent[1][0])
    require(seam_from_xyz == seam, "Physical interface changed vertex IDs")
    require(all(xyz[a] != xyz[b] for a,b in seam), "Collapsed mapped seam edge")
    outer = [e for e, refs in incidence.items() if len(refs) == 1]
    require(len(outer) == 16, "Outer boundary edge count changed")
    for a,b in outer:
        require(abs(xyz[a][2]) < 1e-13 and abs(xyz[b][2]) < 1e-13,
                "Synthetic analytical boundary was not preserved")
    smallest_normal_alignment = 1.0
    min_projected_jacobian = float("inf")
    subtriangles = 0
    for face in [*quads, *tris]:
        local_triangles = ((face[0], face[1], face[2]),
                           (face[0], face[2], face[3])) if len(face) == 4 else (face,)
        for i,j,k in local_triangles:
            normal = cross3(vector(xyz[i], xyz[j]), vector(xyz[i], xyz[k]))
            u = (uv[i][0]+uv[j][0]+uv[k][0])/3.0
            v = (uv[i][1]+uv[j][1]+uv[k][1])/3.0
            analytic = surface_normal(u,v,curvature)
            projected = dot(normal, analytic)
            require(math.isfinite(projected) and projected > 1e-14 and normal[2] > 1e-14,
                    "Inverted or collapsed physical triangle relative to surface tangent")
            length = math.sqrt(dot(normal,normal)*dot(analytic,analytic))
            alignment = projected / length
            require(alignment > 0.98, "Surface approximation normal misalignment")
            smallest_normal_alignment = min(smallest_normal_alignment,alignment)
            min_projected_jacobian = min(min_projected_jacobian,projected)
            subtriangles += 1
    require(subtriangles == 120, "Wrong triangle decomposition of 42 QUAD + 36 TRI")
    # Sample midpoint displacement: a faceted OBJ approximates, not equals, the surface.
    errors = []
    for a,b in incidence:
        u=(uv[a][0]+uv[b][0])/2.0
        v=(uv[a][1]+uv[b][1])/2.0
        linear_z=(xyz[a][2]+xyz[b][2])/2.0
        errors.append(abs(height(u,v,curvature)-linear_z))
    return {
        "surface_curvature": curvature,
        "xyz_subtriangles_audited": subtriangles,
        "smallest_tangent_normal_alignment": smallest_normal_alignment,
        "min_projected_twice_area": min_projected_jacobian,
        "maximum_linear_edge_midpoint_height_error": max(errors),
        "max_abs_z": max(abs(p[2]) for p in xyz),
        "outer_boundary_z_zero": True,
        "quad_tri_shared_seam_ids": len(seam),
    }


def negative_inputs(uv, quads, tris, seam):
    cases=0
    for bad_curvature in (float("nan"), float("inf"), 4.0001):
        try:
            surface_lift(uv,bad_curvature)
        except ValueError:
            cases += 1
    for damaged in (
        [*uv[:-1], (float("nan"),0.25,0.0)],
        [*uv[:-1], (0.25,0.25,0.01)],
        [*uv[:-1], uv[0]],
    ):
        try:
            surface_lift(damaged,1.6)
        except ValueError:
            cases += 1
    lifted=surface_lift(uv,1.6)
    try:
        physical_quality(uv,lifted,quads, [tris[0][::-1], *tris[1:]], seam,1.6)
    except ValueError:
        cases += 1
    swapped=[(u,1.0-v,z) for u,v,z in lifted]
    try:
        physical_quality(uv,swapped,quads,tris,seam,1.6)
    except ValueError:
        cases += 1
    require(cases == 8, "Analytic lift negative controls were weakened")
    return cases


def write_obj(path, vertices, quads, tris):
    with path.open("w",encoding="ascii",newline="\n") as f:
        f.write("# Analytic XYZ research lift; native QUAD + M5 TRI; NOT historical physical APMesh\n")
        for x,y,z in vertices:
            f.write(f"v {x:.17g} {y:.17g} {z:.17g}\n")
        f.write("g QUAD_native_CXX_lifted\n")
        for face in quads:
            f.write("f " + " ".join(str(i+1) for i in face) + "\n")
        f.write("g TRI_exterior_research_lifted\n")
        for face in tris:
            f.write("f " + " ".join(str(i+1) for i in face) + "\n")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--directory",type=Path,required=True)
    path=parser.parse_args().directory
    source=json.loads((path/"research_local_delaunay_manifest.json").read_text())
    require(source["status"]=="RESEARCH_CONSTRAINED_LOCALLY_DELAUNAY_NOT_HISTORICAL"
            and source["quad_count"]==42 and source["tri_count"]==36,
            "Source is not qualified native QUAD plus M5 research TRI")
    results=[]
    for mode in ("vertex_mean","area_centroid"):
        uv, quads, tris = read_obj(path/f"hybrid_research_local_delaunay_{mode}.obj")
        native, original_quads, original_tris=read_obj(path/f"quads_{mode}.obj")
        require(not original_tris and uv[:len(native)] == native
                and original_quads == quads and len(native)==53,
                "Native C++ QUAD topology/vertices changed")
        seam=validate(uv,quads,tris)
        require(negative_inputs(uv,quads,tris,seam)==8,
                "Synthetic negative cases were not rejected")
        checks=[]
        for curvature in (0.0,1.6,-1.6):
            xyz=surface_lift(uv,curvature)
            checks.append(physical_quality(uv,xyz,quads,tris,seam,curvature))
            if curvature==1.6:
                write_obj(path/f"analytic_surface_research_{mode}.obj",xyz,quads,tris)
        require(checks[0]["max_abs_z"]==0.0
                and checks[1]["max_abs_z"]>0
                and checks[2]["max_abs_z"]>0,
                "Flat versus curved analytical witness was not differentiated")
        results.append({"mode":mode,"checks":checks,
                        "source_native_quad_sha256":
                        hashlib.sha256((path/f"quads_{mode}.obj").read_bytes()).hexdigest()})
    report={"schema":1,"status":"ANALYTIC_SYNTHETIC_XYZ_RESEARCH_NOT_PHYSICAL_MODEL",
            "real_apmesh_curved_models_tested":False,"historical_hybrid_complete":False,
            "all_quad_extension_enabled":False,"production_code_changed":False,
            "source":"actual C++ 19-leaf tree QUAD and M5 research locally Delaunay exterior",
            "mapping":"(u,v,k*u*(1-u)*v*(1-v))","quad_count":42,"tri_count":36,
            "vertices":69,"seam_edges":20,"negative_cases":8,"results":results}
    (path/"analytic_surface_research_manifest.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("m6_analytic_xyz=ok native_cpp_quad=42 exterior_research_tri=36 "
          "seam=20 synthetic_curvatures=3 rules=2 negatives=8 NOT_physical_APMesh")

if __name__=="__main__":
    main()
