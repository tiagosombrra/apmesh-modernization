"""Independent Bernstein control-net and indexed topology oracle for real P1.

This bounded source fixture is a controlled, single-Bezier-patch QUAD/AFT TRI
execution. The oracle must never be reused to certify unrelated models.
"""

from __future__ import annotations

from collections import defaultdict
import math

from .model import MeshDocument
from .topology_audit import audit_topology

SOURCE_OBJ_SHA256 = "cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0"
SOURCE_COMMIT = "d39bbc447f88e179c3c4ee674bd9309f59c18eed"
SOURCE_CANDIDATE = "0999769722f128d887e1143c8ec1da67da627850"
SOURCE_ACTIONS_RUN = 43588588497
SOURCE_ARTIFACT_LINUX = 14111372234
SOURCE_ARTIFACT_WINDOWS = 14111247733

# Independently pinned original 4x4 Bezier control net from APMesh source.
# First index is the u Bernstein index; second index is v.
CONTROLS = (
    ((1.0, -1.0, 0.0), (0.5, -1.0, 0.0), (-0.5, -1.0, 0.0), (-1.0, -1.0, 0.0)),
    ((0.5, -0.5, 0.0), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.0), (-1.0, -0.5, 0.0)),
    ((0.5, 0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0), (-1.0, 0.5, 0.0)),
    ((1.0, 1.0, 0.0), (0.5, 1.0, 0.0), (-0.5, 1.0, 0.0), (-1.0, 1.0, 0.0)),
)


class P1QualificationError(ValueError):
    """A controlled real-model invariant is violated."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise P1QualificationError(reason)


def _basis(t: float) -> tuple[tuple[float, ...], tuple[float, ...]]:
    s = 1 - t
    return ((s**3, 3*t*s*s, 3*t*t*s, t**3),
            (-3*s*s, 3*s*(1-3*t), 3*t*(2-3*t), 3*t*t))


def bezier(u: float, v: float) -> tuple[tuple[float, ...], ...]:
    """Return position and two original surface derivatives (XYZ, Qu, Qv)."""
    _require(math.isfinite(u) and math.isfinite(v) and 0 <= u <= 1 and 0 <= v <= 1,
             "uv_outside_source_chart")
    bu, du = _basis(u)
    bv, dv = _basis(v)
    return tuple(tuple(sum(a[i]*b[j]*CONTROLS[i][j][axis]
                           for i in range(4) for j in range(4))
                       for axis in range(3))
                 for a, b in ((bu, bv), (du, bv), (bu, dv)))


def _sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _norm(a):
    return math.sqrt(_dot(a, a))


def _close(a, b):
    return all(math.isclose(x, y, abs_tol=5e-10, rel_tol=5e-11)
               for x, y in zip(a, b))


def audit_original_surface(document: MeshDocument) -> dict:
    """Verify original UV/XYZ mapping, physical normals, topology and seam."""
    _require(not document.synthetic and document.semantic_sidecar_sha256 is None,
             "unverified_fixture_sidecar")
    _require(document.patch_ownership == "unknown" and not document.source_curves,
             "unexpected_global_patch_authority")
    _require(len(document.points) == 69 and document.quads == 42 and
             document.triangles == 36 and len(document.faces) == 78,
             "unexpected_original_inventory")
    _require(document.groups == ("QUAD", "TRI_AFT"), "changed_element_class_groups")
    _require(all((face.group == "QUAD") == (face.element_type == "quad")
                 for face in document.faces), "element_group_type_mismatch")

    vertex_uv = {}
    edges = defaultdict(list)
    minimum_alignment = 1.0
    minimum_jacobian = math.inf
    oriented_facets = 0
    for face in document.faces:
        _require(face.uv is not None, "missing_original_uv")
        for index, uv in zip(face.vertices, face.uv):
            _require(index not in vertex_uv or vertex_uv[index] == uv,
                     "conflicting_uv_for_source_node")
            vertex_uv[index] = uv
        for a, b in zip(face.vertices, face.vertices[1:]+face.vertices[:1]):
            edges[tuple(sorted((a,b)))].append((face.group,a,b))
        subfaces = ((0, 1, 2), (0, 2, 3)) if face.element_type == "quad" else ((0, 1, 2),)
        for corners in subfaces:
            index = tuple(face.vertices[i] for i in corners)
            x0, x1, x2 = (document.points[i] for i in index)
            normal = _cross(_sub(x1,x0),_sub(x2,x0))
            cu = sum(face.uv[i][0] for i in corners)/3
            cv = sum(face.uv[i][1] for i in corners)/3
            _, du, dv = bezier(cu, cv)
            source_normal = _cross(du, dv)
            reference_size = _norm(source_normal)
            facet_size = _norm(normal)
            _require(reference_size > 1e-12 and facet_size > 1e-12,
                     "degenerate_source_or_physical_facet")
            alignment = _dot(normal, source_normal)/(reference_size*facet_size)
            _require(math.isfinite(alignment) and alignment > 0,
                     "inverted_original_physical_facet")
            minimum_alignment = min(minimum_alignment,alignment)
            minimum_jacobian = min(minimum_jacobian,reference_size)
            oriented_facets += 1

    _require(len(vertex_uv) == len(document.points) and oriented_facets == 120,
             "incomplete_original_vertex_or_facet_coverage")
    max_xyz_error = 0.0
    for index, xyz in enumerate(document.points):
        expected, _, _ = bezier(*vertex_uv[index])
        max_xyz_error = max(max_xyz_error, max(abs(x-y) for x,y in zip(xyz,expected)))
        _require(_close(xyz, expected), "original_bezier_xyz_mismatch")

    outer = [key for key, uses in edges.items() if len(uses) == 1]
    seam = [key for key, uses in edges.items() if len(uses) == 2
            and uses[0][0] != uses[1][0]]
    _require(len(outer) == 16 and len(seam) == 20,
             "original_boundary_or_seam_mismatch")
    for a,b in outer:
        u,v = vertex_uv[a], vertex_uv[b]
        _require((u[0] == v[0] and u[0] in (0.0,1.0)) or
                 (u[1] == v[1] and u[1] in (0.0,1.0)),
                 "source_outer_edge_not_on_original_boundary")
    for key in seam:
        u,v = edges[key]
        _require(u[1] == v[2] and u[2] == v[1], "reversed_source_seam")
    topology = audit_topology(document)
    complex_report = topology["combined_indexed_face_complex"]
    _require(complex_report["is_indexed_disk"] and
             complex_report["components"] == 1 and
             complex_report["boundary_edges"] == 16 and
             complex_report["euler_characteristic"] == 1,
             "original_indexed_disk_mismatch")
    group_reports = {p["group"]:p for p in topology["patches"]}
    _require(group_reports["QUAD"]["is_indexed_disk"] and
             group_reports["TRI_AFT"]["boundary_loops"] == 2 and
             group_reports["TRI_AFT"]["euler_characteristic"] == 0,
             "original_region_topology_mismatch")
    return {
        "schema":"apmesh.meshstudio.p1_real_surface_oracle.v1",
        "source_geometry":"Models3d::ModelCurvaBezier pinned source 4x4 control net",
        "source_topology_scope":"single_connected_controlled_patch_only",
        "total_vertices":len(document.points), "total_faces":len(document.faces),
        "quads":document.quads, "native_aft_triangles":document.triangles,
        "outer_boundary_edges":len(outer), "quad_tri_seam_edges":len(seam),
        "oriented_physical_facets":oriented_facets,
        "minimum_sampled_source_jacobian":minimum_jacobian,
        "minimum_facet_normal_alignment":minimum_alignment,
        "max_source_xyz_component_error":max_xyz_error,
        "region_topology":{
            "quad": "indexed_disk", "tri_aft":"indexed_annulus", "mixed":"indexed_disk"},
        "assertions":{
            "source_bezier_control_net_match":True,
            "indexed_uv_and_xyz_correspondence":True,
            "original_quad_tri_seam_orientation":True,
            "original_outer_curve_location":True,
            "continuous_source_jacobian_certified":False,
            "global_source_welding_certified":False,
            "mixed_adaptive_epoch_qualified":False,
            "anisotropic_adaptation_qualified":False,
        }
    }


def qualify_p1(document:MeshDocument, generator_report:dict) -> dict:
    """Bind the independent geometric oracle to exact original CI provenance."""
    _require(document.source_sha256 == SOURCE_OBJ_SHA256, "source_digest_mismatch")
    _require(document.source_kind == "wavefront_obj", "unexpected_obj_dialect")
    _require(generator_report.get("actual_ap_mesh_entry") is True and
             generator_report.get("native_AFT") is True and
             generator_report.get("independent_Bezier_oracle") is True and
             generator_report.get("model") == "Models3d::ModelCurvaBezier" and
             generator_report.get("adaptive_epochs") == 0 and
             generator_report.get("OBJ_sha256") == SOURCE_OBJ_SHA256 and
             generator_report.get("result") == {
                 "nodes":69,"quads":42,"triangles":36,"boundary":16
             } and generator_report.get("rollback_nonempty") is True,
             "source_generator_receipt_mismatch")
    surface = audit_original_surface(document)
    return {
        "schema":"apmesh.meshstudio.p1_qualification.v1",
        "evidence_kind":"REAL_SOURCE_CI_ARTIFACT_NOT_SYNTHETIC",
        "source_obj_sha256":document.source_sha256,
        "generator_revision":SOURCE_COMMIT,
        "generator_candidate_revision":SOURCE_CANDIDATE,
        "original_actions_run":SOURCE_ACTIONS_RUN,
        "original_linux_artifact":SOURCE_ARTIFACT_LINUX,
        "original_windows_artifact":SOURCE_ARTIFACT_WINDOWS,
        "verified_linux_windows_obj_sha256_equal": True,
        "generator_execution_is_not_adaptation":True,
        "source":surface,
    }
