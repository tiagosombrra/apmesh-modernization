"""Patch-local indexed topology audits; coordinates never imply welding."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import asdict, dataclass, replace

from .model import MeshDocument


class TopologyError(ValueError):
    """A source-indexed cell complex violates a local mesh invariant."""


@dataclass(frozen=True)
class PatchTopology:
    group: str
    face_count: int
    vertex_count: int
    edge_count: int
    boundary_edges: int
    components: int
    boundary_loops: int | None
    euler_characteristic: int
    is_indexed_disk: bool
    all_quad_fixed_boundary_even: bool | None


def audit_topology(document: MeshDocument, *, _combined: bool = False) -> dict:
    """Audit indexed connectivity separately per patch/group.

    Same XYZ in distinct patches is not evidence of approved source welding.
    """
    if not document.faces:
        raise TopologyError("empty_faces")
    by_group: dict[str, list[tuple[int, tuple[int, ...]]]] = defaultdict(list)
    owners: dict[int, set[str]] = defaultdict(set)
    for i, face in enumerate(document.faces):
        if face.element_type not in ("triangle", "quad") or len(face.vertices) != (3 if face.element_type == "triangle" else 4):
            raise TopologyError("invalid_cell_type")
        if len(set(face.vertices)) != len(face.vertices):
            raise TopologyError("repeated_cell_corner")
        if any(idx < 0 or idx >= len(document.points) for idx in face.vertices):
            raise TopologyError("foreign_point_id")
        by_group[face.group].append((i, face.vertices))
        for idx in face.vertices:
            owners[idx].add(face.group)
    reports = []
    for group, local in sorted(by_group.items()):
        edges: dict[tuple[int, int], list[tuple[int, int, int]]] = defaultdict(list)
        vertices = set()
        for index, face in local:
            vertices.update(face)
            for a, b in zip(face, face[1:] + face[:1]):
                if a == b:
                    raise TopologyError("collapsed_edge")
                edges[(min(a, b), max(a, b))].append((index, a, b))
        adjacency = {i: set() for i, _ in local}
        boundary: list[tuple[int, int]] = []
        for uses in edges.values():
            if len(uses) > 2:
                raise TopologyError(f"nonmanifold_patch_edge:{group}")
            if len(uses) == 2:
                i, a, b = uses[0]
                j, c, d = uses[1]
                if not (a == d and b == c):
                    raise TopologyError(f"inconsistent_edge_winding:{group}")
                adjacency[i].add(j)
                adjacency[j].add(i)
            else:
                _, a, b = uses[0]
                boundary.append((a, b))
        pending = set(adjacency)
        components = 0
        while pending:
            components += 1
            seen = {pending.pop()}
            queue = deque(seen)
            while queue:
                for neighbor in adjacency[queue.popleft()]:
                    if neighbor in pending:
                        pending.remove(neighbor)
                        seen.add(neighbor)
                        queue.append(neighbor)
        boundary_adj: dict[int, set[int]] = defaultdict(set)
        for a, b in boundary:
            boundary_adj[a].add(b)
            boundary_adj[b].add(a)
        boundary_loops = 0
        if boundary and all(len(neighbors) == 2 for neighbors in boundary_adj.values()):
            unvisited = set(boundary_adj)
            while unvisited:
                boundary_loops += 1
                queue = [unvisited.pop()]
                while queue:
                    for neighbor in boundary_adj[queue.pop()]:
                        if neighbor in unvisited:
                            unvisited.remove(neighbor)
                            queue.append(neighbor)
        elif boundary:
            boundary_loops = None
        chi = len(vertices) - len(edges) + len(local)
        is_disk = components == 1 and boundary_loops == 1 and chi == 1
        pure_quads = all(document.faces[i].element_type == "quad" for i, _ in local)
        reports.append(asdict(PatchTopology(
            group, len(local), len(vertices), len(edges), len(boundary),
            components, boundary_loops, chi, is_disk,
            len(boundary) % 2 == 0 if pure_quads and is_disk else None,
        )))
    reused = sorted(idx for idx, groups in owners.items() if len(groups) > 1)
    curve_records = [{
        "logical_curve_id": curve.get("curve_id", curve.get("id", "unidentified")),
        "incident_patch_count": len(curve.get("incident_patches", [])),
        "weld_approved": curve.get("topology_weld_approved") is True,
        "evidence_scope": "validated_sidecar_samples_only",
    } for curve in document.source_curves]
    # Wavefront groups may classify cell types (QUAD, TRI_AFT), not patches.
    # Inspect the complete indexed complex separately, without declaring
    # source-global patch identity or welding coincident XYZ coordinates.
    combined = None
    if not _combined and document.patch_ownership != "sidecar_patch_local":
        normalized = replace(document, faces=tuple(
            replace(face, group="all_indexed_faces") for face in document.faces
        ))
        try:
            combined = audit_topology(normalized, _combined=True)["patches"][0]
        except TopologyError as exc:
            combined = {"status": "invalid_indexed_complex", "diagnostic": str(exc)}
    return {
        "patches": reports,
        "group_label_semantics": ("source_patch_ids_from_sidecar"
                                  if document.patch_ownership == "sidecar_patch_local"
                                  else "untrusted_obj_group_labels_not_patch_ids"),
        "combined_indexed_face_complex": combined,
        "total_patch_local_boundary_edges": sum(p["boundary_edges"] for p in reports),
        "reused_global_point_ids_across_groups": reused,
        "source_shared_curves": curve_records,
        "global_weld_certified": False,
        "topology_scope": "indexed_faces_only_no_original_surface_certification",
    }
