"""Verify multiple real QUAD/TRI physical candidates on identical source sites.

The candidates belong to ONE controlled APMesh application evaluation. Except
for the original controlled output, every physical candidate is STAGED, never
an accepted adaptive epoch. The Pareto fronts are analytical diagnostics only.
"""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path

from .import_obj import import_obj
from .p1_source_oracle import bezier

SCHEMA = "apmesh.meshstudio.real_candidate_study.v1"
ORDER = ("control", "band", "west", "north", "both")
STAGED = ("band", "both", "north", "west")
MAX_REPORT_BYTES = 256_000
OBJ_HASHES = {
    "control": "cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0",
    "band": "76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6",
    "west": "ca08918f6d71fa672de22a72eb6fef7c106c90c7fd02d40cb19852972b4274ee",
    "north": "6eb4faedeaab44fbfa3d4cb2ca1ea618a3dca513dc241871c57bcc7eae26d500",
    "both": "b77afb530724f38ff81f0f3e7f06fca6c8dc0cb4a15562ce933a4013724bd36c",
}
SOURCE_GENERATOR_SHA = "27851df2625e0c0b37e12023af699a01f3d0304c"
SOURCE_RESEARCH_MERGE_SHA = "ab1dc62a815f3d56c9b25845bec00863730ddcd5"
SOURCE_CI_RUN_ID = 43664129060
SOURCE_LINUX_ARTIFACT_ID = 14141039513
SOURCE_WINDOWS_ARTIFACT_ID = 14142185137
SOURCE_REPORT_SHA256 = "9de13e6e9b8f6a5f6ae188f19acd0a6b068ddc066df2f4ff9d5579ef96f9f054"

COMMON_OBJECTIVES = {
    "max_xyz": "min", "rms_source_area": "min", "elements": "min",
    "nodes": "min", "quad_uv_area": "max", "min_scaled_jacobian": "max",
    "min_warpage_cosine": "max",
}
PROFILES = {
    "uv_area_profile": COMMON_OBJECTIVES,
    "quad_count_profile": {**COMMON_OBJECTIVES, "quads": "max"},
}


class StudyIntegrityError(ValueError):
    """A source-bound geometric, scientific, or publication invariant failed."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise StudyIntegrityError(code)


def _close(actual: float, claimed: float, label: str, *, tolerance: float = 2e-10) -> None:
    _require(type(claimed) in (float, int) and math.isfinite(claimed) and
             math.isclose(actual, claimed, abs_tol=tolerance, rel_tol=2e-8),
             "mismatched_" + label)


def _vectors(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(x-y for x, y in zip(a, b))


def _cross(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[float, ...]:
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def _dot(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return math.fsum(x*y for x, y in zip(a, b))


def _norm(a: tuple[float, ...]) -> float:
    return math.sqrt(_dot(a, a))


def _uv_area(vertices: list[tuple[float, float]]) -> float:
    return 0.5 * math.fsum(a[0]*b[1]-a[1]*b[0]
                            for a, b in zip(vertices, vertices[1:]+vertices[:1]))


def _inverse_quad(polygon: list[tuple[float, float]], u: float,
                  v: float) -> tuple[float, float, float, float]:
    """Invert the four-corner UV bilinear map without triangulating the QUAD."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = polygon
    a = (x1-x0, y1-y0)
    b = (x3-x0, y3-y0)
    c = (x0-x1+x2-x3, y0-y1+y2-y3)
    s = t = 0.5
    converged = False
    for _ in range(30):
        fx = x0+s*a[0]+t*b[0]+s*t*c[0]-u
        fy = y0+s*a[1]+t*b[1]+s*t*c[1]-v
        ds = (a[0]+t*c[0], a[1]+t*c[1])
        dt = (b[0]+s*c[0], b[1]+s*c[1])
        det = ds[0]*dt[1]-ds[1]*dt[0]
        _require(math.isfinite(det) and abs(det) > 1e-16, "invalid_bilinear_jacobian")
        step_s = (fx*dt[1]-fy*dt[0])/det
        step_t = (ds[0]*fy-ds[1]*fx)/det
        s -= step_s
        t -= step_t
        if max(abs(step_s), abs(step_t)) < 1e-14:
            converged = True
            break
    mismatch = max(abs(x0+s*a[0]+t*b[0]+s*t*c[0]-u),
                   abs(y0+s*a[1]+t*b[1]+s*t*c[1]-v))
    _require(converged and -1e-8 <= s <= 1+1e-8 and
             -1e-8 <= t <= 1+1e-8 and mismatch <= 1e-10,
             "bilinear_inverse_did_not_converge")
    return ((1-s)*(1-t), s*(1-t), s*t, (1-s)*t)


def _triangle_weights(polygon: list[tuple[float, float]], u: float,
                      v: float) -> tuple[float, float, float]:
    (ax, ay), (bx, by), (cx, cy) = polygon
    det = (bx-ax)*(cy-ay)-(by-ay)*(cx-ax)
    _require(det > 1e-15, "invalid_triangle_determinant")
    s = ((u-ax)*(cy-ay)-(v-ay)*(cx-ax))/det
    t = ((bx-ax)*(v-ay)-(by-ay)*(u-ax))/det
    return (1-s-t, s, t)


def _mesh_vertex_uv(document) -> tuple[tuple[float, float], ...]:
    vertex_uv: dict[int, tuple[float, float]] = {}
    for face in document.faces:
        _require(face.uv is not None, "missing_source_uv")
        for idx, uv in zip(face.vertices, face.uv):
            _require(idx not in vertex_uv or vertex_uv[idx] == uv,
                     "multiple_uv_for_one_source_vertex")
            vertex_uv[idx] = uv
    _require(len(vertex_uv) == len(document.points), "incomplete_source_uv_inventory")
    uv_list = tuple(vertex_uv[i] for i in range(len(document.points)))
    for xyz, uv in zip(document.points, uv_list):
        expected, _, _ = bezier(*uv)
        _require(all(math.isclose(a,b,rel_tol=5e-11,abs_tol=5e-10)
                     for a,b in zip(xyz,expected)), "bezier_vertex_position_mismatch")
    return uv_list


def _geometry_checks(document) -> tuple[dict, tuple[tuple[float, float], ...]]:
    """Rebuild typed, UV and indexed-disk invariants directly from source OBJ."""
    _require(not document.synthetic and document.patch_ownership == "unknown" and
             not document.source_curves, "unexpected_source_patch_claim")
    _require(document.groups == ("QUAD", "TRI_AFT"), "invalid_original_group_order")
    _require(all((f.group == "QUAD") == (f.element_type == "quad")
                 for f in document.faces), "misclassified_face_type")
    uv = _mesh_vertex_uv(document)
    incidences: dict[tuple[int, int], list[tuple[int,int,str]]] = defaultdict(list)
    quad_area = 0.0
    minimum_jacobian = 1.0
    minimum_warpage = 1.0
    area = 0.0
    for face in document.faces:
        face_uv = [uv[i] for i in face.vertices]
        planar_uv_area = _uv_area(face_uv)
        _require(planar_uv_area > 0, "inverted_uv_polygon")
        area += planar_uv_area
        if face.element_type == "quad":
            quad_area += planar_uv_area
            points = [document.points[i] for i in face.vertices]
            for k, idx in enumerate(face.vertices):
                current = points[k]
                right = _vectors(points[(k+1) % 4], current)
                left = _vectors(points[(k+3) % 4], current)
                _, du, dv = bezier(*uv[idx])
                ref = _cross(du,dv)
                denom = _norm(right)*_norm(left)*_norm(ref)
                _require(denom > 1e-16, "degenerate_quad_corner")
                q = _dot(_cross(right,left),ref)/denom
                minimum_jacobian = min(minimum_jacobian,q)
            n0 = _cross(_vectors(points[1],points[0]),_vectors(points[2],points[0]))
            n1 = _cross(_vectors(points[2],points[0]),_vectors(points[3],points[0]))
            _require(_norm(n0) > 0 and _norm(n1) > 0, "degenerate_quad_split")
            minimum_warpage = min(minimum_warpage, _dot(n0,n1)/(_norm(n0)*_norm(n1)))
        for x,y in zip(face.vertices,face.vertices[1:]+face.vertices[:1]):
            incidences[tuple(sorted((x,y)))].append((x,y,face.group))
    _require(math.isclose(area,1,rel_tol=0,abs_tol=1e-10), "uv_area_not_unit_disk")
    boundary = [uses for uses in incidences.values() if len(uses)==1]
    seam = [uses for uses in incidences.values()
            if len(uses)==2 and uses[0][2]!=uses[1][2]]
    _require(len(boundary)==16 and len(document.points)-len(incidences)+len(document.faces)==1,
             "noncanonical_original_disk")
    for uses in incidences.values():
        _require(len(uses)<=2,"invalid_indexed_edge_incidence")
        if len(uses)==2:
            _require(uses[0][:2]==uses[1][:2][::-1],"inconsistent_shared_winding")
    for uses in boundary:
        u,v=uv[uses[0][0]],uv[uses[0][1]]
        _require((u[0]==v[0] and u[0] in (0.0,1.0)) or
                 (u[1]==v[1] and u[1] in (0.0,1.0)),"boundary_not_on_source_chart")
    _require(minimum_jacobian>0 and minimum_warpage>0,"invalid_physical_quad_quality")
    report={
        "nodes":len(document.points),"quads":document.quads,
        "triangles":document.triangles,"elements":len(document.faces),
        "boundary_edges":len(boundary),"quad_tri_seam_edges":len(seam),
        "quad_uv_area":quad_area,"min_scaled_jacobian":minimum_jacobian,
        "min_warpage_cosine":minimum_warpage,
        "indexed_euler_characteristic":len(document.points)-len(incidences)+len(document.faces),
    }
    return report,uv


def _uniform_sample_metrics(document, uv, grid:int=64) -> dict:
    """Evaluate true Bernstein vs TRI barycentric / QUAD bilinear XYZ at fixed sites."""
    _require(type(grid) is int and grid==64,"unapproved_common_sample_grid")
    boxes=[]
    for face in document.faces:
        coords=[uv[i] for i in face.vertices]
        boxes.append((face,coords,min(x for x,y in coords),max(x for x,y in coords),
                      min(y for x,y in coords),max(y for x,y in coords)))
    error2=0.0
    weighted_error2=0.0
    total_area=0.0
    max_error=0.0
    quad_sites=tri_sites=0
    for iy in range(grid):
        v=(iy+0.5)/grid
        for ix in range(grid):
            u=(ix+0.5)/grid
            located=None
            for face,coords,umin,umax,vmin,vmax in boxes:
                if not (umin-1e-13<=u<=umax+1e-13 and
                        vmin-1e-13<=v<=vmax+1e-13):
                    continue
                if all((b[0]-a[0])*(v-a[1])-(b[1]-a[1])*(u-a[0])>=-1e-12
                       for a,b in zip(coords,coords[1:]+coords[:1])):
                    located=(face,coords)
                    break
            _require(located is not None,"uncovered_common_grid_site")
            face,coords=located
            weights=(_triangle_weights(coords,u,v) if len(coords)==3 else
                     _inverse_quad(coords,u,v))
            interpolated=tuple(math.fsum(w*document.points[index][axis]
                                         for w,index in zip(weights,face.vertices))
                               for axis in range(3))
            exact,du,dv=bezier(u,v)
            square=math.fsum((a-b)**2 for a,b in zip(exact,interpolated))
            jacobian=_norm(_cross(du,dv))
            _require(math.isfinite(square) and jacobian>0 and math.isfinite(jacobian),
                     "nonfinite_common_site_error")
            error2+=square
            weighted_error2+=square*jacobian
            total_area+=jacobian
            max_error=max(max_error,math.sqrt(square))
            if len(face.vertices)==4:quad_sites+=1
            else:tri_sites+=1
    _require(quad_sites+tri_sites==4096 and quad_sites>0 and tri_sites>0,
             "invalid_source_sample_distribution")
    return {"source_grid":64,"sample_count":4096,"max_xyz":max_error,
            "rms_uv":math.sqrt(error2/4096),
            "rms_source_area":math.sqrt(weighted_error2/total_area),
            "quad_sites":quad_sites,"tri_sites":tri_sites}


def _dominates(a:dict,b:dict,directions:dict,eps:float=1e-12)->bool:
    strictly_better=False
    for name,mode in directions.items():
        x,y=a[name],b[name]
        _require(mode in ("min","max"),"invalid_pareto_direction")
        if mode=="min":
            if x>y+eps:return False
            strictly_better|=x<y-eps
        else:
            if x<y-eps:return False
            strictly_better|=x>y+eps
    return strictly_better


def _pareto_profiles(records:dict[str,dict])->dict:
    _require(type(records) is dict and set(records)==set(STAGED),
             "invalid_pareto_candidate_set")
    required=set(COMMON_OBJECTIVES)|{"quads"}
    for name, item in records.items():
        _require(type(item) is dict and set(item)==required,
                 "invalid_pareto_objectives_"+name)
        for key, value in item.items():
            _require(type(value) in (float, int) and math.isfinite(value)
                     and value>0, "nonfinite_pareto_measurement_"+key)
        _require(0 < item["quad_uv_area"] < 1 and
                 0 < item["min_scaled_jacobian"] <= 1 and
                 0 < item["min_warpage_cosine"] <= 1 and
                 type(item["elements"]) is int and
                 type(item["nodes"]) is int and
                 type(item["quads"]) is int and
                 item["quads"] < item["elements"],
                 "invalid_pareto_physical_inventory")
    result={}
    for name,directions in PROFILES.items():
        dominated={candidate:[other for other in STAGED if other!=candidate and
                              _dominates(records[other],records[candidate],directions)]
                   for candidate in STAGED}
        result[name]={"objectives":dict(directions),
                      "nondominated":[candidate for candidate in STAGED
                                      if not dominated[candidate]],
                      "dominated_by":dominated}
    return result


def _load_report(path:Path) -> tuple[dict,str]:
    _require(path.is_file() and path.stat().st_size<MAX_REPORT_BYTES,
             "missing_or_large_original_report")
    raw=path.read_bytes();digest=sha256(raw).hexdigest()
    _require(digest==SOURCE_REPORT_SHA256,"original_generator_report_sha_mismatch")
    try:source=json.loads(raw.decode("utf-8"))
    except (ValueError,UnicodeError) as e:raise StudyIntegrityError("invalid_source_report") from e
    _require(source["model"]=="Models3d::ModelCurvaBezier" and
             source["actual_ap_mesh_entry"] is True and
             source["native_AFT"] is True and
             source["adaptive_epochs"]==0 and
             source["OBJ_sha256"]==OBJ_HASHES["control"],
             "invalid_source_execution_identity")
    return source,digest


def _source_claims(source:dict,kind:str)->tuple[dict,dict,dict]:
    band=source["physical_native_band_candidate"]
    second=band["second_physical_aft_candidates"]
    if kind=="control":
        inventory={"nodes":69,"quads":42,"triangles":36,"boundary":16}
        record=source["same_site_source_error"]["fixed_64x64_original"]
        quality=source["typed_physical_quad_quality"]
        area=0.25
    elif kind=="band":
        _require(band["status"]=="staged_unaccepted","first_band_was_accepted")
        inventory=band["topology"]
        record=source["same_site_source_error"]["fixed_64x64_band"]
        quality=band["physical_quality"]
        area=float(source["connected_native_refinement_band"]["quad_uv_area"])
        _require(band["candidate_sha256"]==OBJ_HASHES[kind],"first_band_original_sha_mismatch")
    else:
        case=second["alternatives"][kind]
        _require(case["status"]=="staged_unaccepted","second_band_was_accepted")
        inventory=case["topology"]
        record=case["same_site_source_error"]
        quality=case["physical_quality"]
        area=case["quad_uv_area"]
        _require(case["candidate_sha256"]==OBJ_HASHES[kind],"second_band_original_sha_mismatch")
    return inventory,record,{"quad_uv_area":area,**quality}


def qualify_real_study(folder:Path|str)->dict:
    """Reconstruct exactly five true source meshes, their discrete errors and Pareto."""
    root=Path(folder)
    source,report_hash=_load_report(root/"generator_report.json")
    second=source["physical_native_band_candidate"]["second_physical_aft_candidates"]
    _require(second["accepted_adaptive_epochs"]==0,"source_second_band_claims_adaptation")
    results={}
    for name in ORDER:
        path=root/(name+".obj")
        _require(path.is_file() and path.stat().st_size<20_000_000,"missing_source_obj")
        actual_sha=sha256(path.read_bytes()).hexdigest()
        _require(actual_sha==OBJ_HASHES[name],"source_candidate_sha_mismatch_"+name)
        document=import_obj(path,auto_sidecar=False)
        _require(document.source_sha256==actual_sha and not document.synthetic,
                 "altered_real_mesh_document")
        geometry,uv=_geometry_checks(document)
        same_sites=_uniform_sample_metrics(document,uv)
        inventory,reported,quality=_source_claims(source,name)
        for key in ("nodes","quads","triangles"):
            _require(geometry[key]==inventory[key],"source_inventory_mismatch_"+name+"_"+key)
        _require(geometry["boundary_edges"]==inventory["boundary"],
                 "source_boundary_mismatch_"+name)
        for key,value in same_sites.items():
            if key in ("quad_sites","tri_sites","source_grid","sample_count"):
                _require(value==reported[key],"source_sample_count_mismatch_"+name+"_"+key)
            else:_close(value,reported[key],name+"_"+key)
        for key in ("quad_uv_area","min_scaled_jacobian","min_warpage_cosine"):
            _close(geometry[key],quality[key],name+"_"+key)
        results[name]={"source_mesh_sha256":actual_sha,
                       "state":"controlled_nonadaptive_output" if name=="control" else "staged_unaccepted",
                       "geometry":geometry,"same_site_error":same_sites}
    profile_data={}
    for name in STAGED:
        item=results[name]
        g,e=item["geometry"],item["same_site_error"]
        profile_data[name]={"max_xyz":e["max_xyz"],"rms_source_area":e["rms_source_area"],
                            "elements":g["elements"],"nodes":g["nodes"],
                            "quad_uv_area":g["quad_uv_area"],
                            "min_scaled_jacobian":g["min_scaled_jacobian"],
                            "min_warpage_cosine":g["min_warpage_cosine"],
                            "quads":g["quads"]}
    profiles=_pareto_profiles(profile_data)
    expected=source["physical_native_band_candidate"]["profiled_dominance"]["profiles"]
    for name,profile in profiles.items():
        _require(profile["nondominated"]==expected[name]["nondominated"],
                 "pareto_source_front_mismatch_"+name)
        _require(profile["dominated_by"]==expected[name]["dominated_by"],
                 "pareto_source_dominators_mismatch_"+name)
    _require(profiles["uv_area_profile"]["dominated_by"]["west"]==["north"] and
             profiles["quad_count_profile"]["dominated_by"]["west"]==[],
             "missing_objective_profile_sensitivity")
    return {
        "schema":SCHEMA,
        "source_evidence_kind":"ORIGINAL_CI_REAL_MESHES_SINGLE_CONTROLLED_RUN",
        "source_model":"Models3d::ModelCurvaBezier original pinned control net",
        "source_sampling":{"grid":"64x64_uv_cell_midpoints","sites":4096,
                           "same_site_all_meshes":True,
                           "metric":"source_bezier_discrete_xyz_interpolation_error_v1",
                           "continuous_error_bound":False,
                           "physical_PDE_error":False},
        "provenance":{"source_candidate_revision":SOURCE_GENERATOR_SHA,
                      "source_research_merge_revision":SOURCE_RESEARCH_MERGE_SHA,
                      "original_actions_run":SOURCE_CI_RUN_ID,
                      "linux_artifact_id":SOURCE_LINUX_ARTIFACT_ID,
                      "windows_artifact_id":SOURCE_WINDOWS_ARTIFACT_ID,
                      "original_source_report_sha256":report_hash,
                      "original_source_mesh_hashes_match_linux_windows":True,
                      "platform_digest_verified_during_fixture_intake_not_rechecked_each_run":True},
        "physical_candidates":results,
        "pareto_evidence":{"scope":"STAGED_ONLY_NO_AUTOMATIC_ADMISSION",
                           "profiles":profiles},
        "scientific_status":{"accepted_adaptive_epochs":0,
                             "staged_candidates_are_not_accepted_epochs":True,
                             "real_all_quad_generator_certified":False,
                             "real_anisotropic_generator_certified":False,
                             "not_a_statistical_multi_run_comparison":True,
                             "source_family":"single_controlled_bezier_fixed16"},
    }


def write_real_study_report(folder:Path|str, output:Path|str)->dict:
    """Write a stable source-bound JSON report; never mutate original fixtures."""
    report=qualify_real_study(folder)
    destination=Path(output)
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=True)+"\n",
                           encoding="utf-8")
    return report
