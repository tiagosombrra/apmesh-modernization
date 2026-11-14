#!/usr/bin/env python3
"""Check original physical QUAD/AFT face UV against native PatchBezier normals.

No global non-manifold sheet inference or independent control-net
reconstruction is claimed from these original C++ differential evaluations.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from verify_r2c10_mesh_export import EXPECTED, verify
from verify_r2c21_detached_chart_topology import parse_obj, inspect_patch


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def rows(path):
    require(path.is_file(), "Missing original native UV or normal CSV")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def audit_triangle(uv, xyz, normal):
    require(len(uv) == len(xyz) == len(normal) == 3 or
            (len(uv) == len(xyz) == 3 and len(normal) == 3),
            "Original Bezier facet arity mismatch")
    require(all(math.isfinite(a) for p in (*uv, *xyz) for a in p) and
            all(math.isfinite(a) for a in normal),
            "Nonfinite UV/XYZ/Bezier source normal")
    signed_uv = ((uv[1][0]-uv[0][0])*(uv[2][1]-uv[0][1]) -
                 (uv[1][1]-uv[0][1])*(uv[2][0]-uv[0][0]))
    require(signed_uv > 1e-12, "Original physical facet UV inverted or degenerate")
    ab = [xyz[1][k]-xyz[0][k] for k in range(3)]
    ac = [xyz[2][k]-xyz[0][k] for k in range(3)]
    cross = (ab[1]*ac[2]-ab[2]*ac[1],
             ab[2]*ac[0]-ab[0]*ac[2],
             ab[0]*ac[1]-ab[1]*ac[0])
    length = math.hypot(*cross)*math.hypot(*normal)
    require(math.isfinite(length) and length > 1e-14,
            "Original facet/Bezier normal is degenerate")
    cosine = sum(a*b for a,b in zip(cross,normal))/length
    require(math.isfinite(cosine) and 0.0 < cosine <= 1.0+1e-10,
            "Original physical facet opposes differential Bezier normal")
    return cosine


def negative_controls():
    uv = ((0.,0.),(1.,0.),(0.,1.))
    xyz = ((0.,0.,0.),(1.,0.,0.),(0.,1.,0.))
    source = (0.,0.,1.)
    require(abs(audit_triangle(uv,xyz,source)-1.0) < 1e-12,
            "Known valid original UV/XYZ/normal calibration failed")
    trials = (
        ((uv[0],uv[2],uv[1]),xyz,source),
        (uv,xyz,(0.,0.,-1.)),
        (uv,xyz,(0.,0.,0.)),
        (uv,(xyz[0],xyz[1],xyz[0]),source),
        (uv,xyz,(float("nan"),0.,1.)),
    )
    for test in trials:
        try:
            audit_triangle(*test)
        except ValueError:
            continue
        raise ValueError("Corrupted source UV/XYZ/normal passed")
    return len(trials)


def verify_original(directory, model, spec):
    original = verify(directory,model,spec)
    obj = directory/f"{model}_all_sides_detached_quad_aft.obj"
    uv_file = directory/f"{model}_original_patch_uv_vertices.csv"
    n_file = directory/f"{model}_original_bezier_facet_normals.csv"
    vertices, patches = parse_obj(
        obj.read_text(encoding="utf-8").splitlines(),spec["patches"])
    uv_rows = rows(uv_file)
    normal_rows = rows(n_file)
    require(len(uv_rows) == spec["nodes"] and
            len(normal_rows) == spec["quads"]*2+spec["tris"],
            "Original model UV/Bezier facet source coverage incomplete")
    uv_by_index = {}
    for r in uv_rows:
        patch, i = int(r["patch_id"]),int(r["obj_vertex_index"])
        point=(float(r["u"]),float(r["v"]))
        source=tuple(float(r[x]) for x in ("bezier_x","bezier_y","bezier_z"))
        require(i in vertices and vertices[i][0] == patch and
                i not in uv_by_index and
                all(math.isfinite(x) for x in (*point,*source)) and
                all(0.0 <= x <= 1.0 for x in point),
                "Invalid or duplicated native source UV node")
        xyz=vertices[i][1]
        scale=max(1.,math.hypot(*xyz),math.hypot(*source))
        require(math.dist(xyz,source) <= 2e-7*scale,
                "Real physical OBJ differs from original Bezier XYZ")
        uv_by_index[i]=point
    source_normals={}
    for r in normal_rows:
        key=tuple(int(r[x]) for x in
                  ("patch_id","face_ordinal","facet_ordinal"))
        point=(float(r["center_u"]),float(r["center_v"]))
        normal=tuple(float(r[x]) for x in
                     ("bezier_nx","bezier_ny","bezier_nz"))
        require(key not in source_normals and
                all(math.isfinite(x) for x in (*point,*normal)),
                "Repeated or nonfinite original differential normal")
        source_normals[key]=(point,normal)
    observed=set()
    total=0
    minimum=1.0
    by_patch={}
    for patch in range(spec["patches"]):
        faces=patches[patch]
        local={i:point for i,(owner,point) in vertices.items() if owner==patch}
        require(inspect_patch(local,faces)["indexed_patch_topology_gate"],
                "Original source patch indexed topology regressed")
        local_count=0
        local_min=1.0
        for j,face in enumerate(faces):
            parts=((0,1,2),(0,2,3)) if len(face)==4 else ((0,1,2),)
            for facet,slots in enumerate(parts):
                key=(patch,j,facet)
                require(key in source_normals,
                        "An original detached facet lacks Bezier differential normal")
                native_uv,normal=source_normals[key]
                uv=[uv_by_index[face[k]] for k in slots]
                xyz=[local[face[k]] for k in slots]
                midpoint=[sum(point[d] for point in uv)/3. for d in range(2)]
                require(all(abs(a-b) <= 1e-12 for a,b in
                            zip(midpoint,native_uv)),
                        "Source normal sampled at a foreign UV centroid")
                cosine=audit_triangle(uv,xyz,normal)
                local_min=min(local_min,cosine)
                local_count+=1
                observed.add(key)
        by_patch[str(patch)]={"facets":local_count,"min_normal_alignment":local_min}
        total+=local_count
        minimum=min(minimum,local_min)
    require(observed == set(source_normals),
            "Unexpected extra/missing original Bezier differential facet")
    return {
        "source_model_sha256_from_R2c10":spec["source_sha256"],
        "OBJ_sha256":hashlib.sha256(obj.read_bytes()).hexdigest(),
        "UV_csv_sha256":hashlib.sha256(uv_file.read_bytes()).hexdigest(),
        "Bezier_normals_csv_sha256":hashlib.sha256(n_file.read_bytes()).hexdigest(),
        "physical_uv_vertices":len(uv_by_index),
        "verified_facet_normals":total,
        "minimum_independent_normal_alignment":minimum,
        "patches":by_patch,
        "R2c10_original_detached_inventory_reverified":original,
        "independent_original_Bezier_control_net_re_evaluation":False,
        "global_sheet_or_cross_patch_welding_approved":False,
    }


def run(directory,output):
    report={
        "schema":"apmesh.quad.r2c22.original_detached_uv_bezier_orientation.v1",
        "negative_controls_passed":negative_controls(),
        "production_TRI_modified":False,
        "source_Bezier_normals_from_original_native_Qu_Qv":True,
        "model_global_nonmanifold_welding_approved":False,
        "models":{name:verify_original(directory,name,spec)
                  for name,spec in EXPECTED.items()},
    }
    output.mkdir(parents=True,exist_ok=True)
    (output/"r2c22_original_patch_uv_bezier_orientation.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("R2C22_ORIGINAL_PATCH_UV_BEZIER_ORIENTATION",
          json.dumps({k:{"patches":len(v["patches"]),
                         "facets":v["verified_facet_normals"],
                         "min_alignment":v["minimum_independent_normal_alignment"]}
                      for k,v in report["models"].items()},sort_keys=True),
          "negative_controls=5","global_sheet_approved=0")
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--directory",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    run(args.directory.resolve(),args.output.resolve())


if __name__=="__main__":
    main()
