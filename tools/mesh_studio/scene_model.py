"""Headless, immutable view state and indexed geometry for an optional desktop GUI.

View representation is not a scientific or topological qualification.  Source
face IDs are preserved through filtering, and UV is always per face corner.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
import math
from pathlib import Path

from .model import MeshDocument

SCENE_SCHEMA = "apmesh.meshstudio.scene.v1"
Vector3 = tuple[float, float, float]


class SceneError(ValueError):
    """Invalid scientific visualization state or provenance."""


@dataclass(frozen=True)
class CameraPose:
    position: Vector3
    focal_point: Vector3
    view_up: Vector3
    parallel_scale: float
    parallel: bool

    def __post_init__(self) -> None:
        values = (*self.position, *self.focal_point, *self.view_up, self.parallel_scale)
        if (not all(math.isfinite(x) for x in values) or self.parallel_scale <= 0
                or math.dist(self.position, self.focal_point) <= 1e-12):
            raise SceneError("invalid_camera")
        direction = tuple(a-b for a, b in zip(self.focal_point, self.position))
        normal = (direction[1]*self.view_up[2]-direction[2]*self.view_up[1],
                  direction[2]*self.view_up[0]-direction[0]*self.view_up[2],
                  direction[0]*self.view_up[1]-direction[1]*self.view_up[0])
        if math.hypot(*normal) <= 1e-12:
            raise SceneError("invalid_camera_up_vector")


@dataclass(frozen=True)
class SceneState:
    source_sha256: str
    show_tri: bool = True
    show_quad: bool = True
    show_edges: bool = True
    selected_face: int | None = None
    camera_xyz: CameraPose | None = None
    camera_uv: CameraPose | None = None

    def __post_init__(self) -> None:
        if len(self.source_sha256) != 64 or any(c not in '0123456789abcdef' for c in self.source_sha256):
            raise SceneError("invalid_source_sha")
        if self.selected_face is not None and (not isinstance(self.selected_face, int) or self.selected_face < 0):
            raise SceneError("invalid_selected_face")


@dataclass(frozen=True)
class GeometryBatch:
    """Ordered cells and original IDs; no topology welding or triangulation."""

    points: tuple[Vector3, ...]
    faces: tuple[tuple[int, ...], ...]
    source_face_ids: tuple[int, ...]
    element_type: str
    coordinates: str

    @property
    def number_of_cells(self) -> int:
        return len(self.faces)


def initial_scene(document: MeshDocument) -> SceneState:
    return SceneState(source_sha256=document.source_sha256)


def visible_face_ids(document: MeshDocument, state: SceneState) -> tuple[int, ...]:
    if state.source_sha256 != document.source_sha256:
        raise SceneError("scene_source_mismatch")
    return tuple(i for i, face in enumerate(document.faces)
                 if (face.element_type == 'triangle' and state.show_tri)
                 or (face.element_type == 'quad' and state.show_quad))


def select_face(document: MeshDocument, state: SceneState, face_id: int | None) -> SceneState:
    visible = visible_face_ids(document, state)
    if face_id is not None and face_id not in visible:
        raise SceneError("selected_face_not_visible")
    return replace(state, selected_face=face_id)


def with_visibility(document: MeshDocument, state: SceneState, *,
                    triangles: bool | None = None,
                    quads: bool | None = None,
                    edges: bool | None = None) -> SceneState:
    updated = replace(state,
                      show_tri=state.show_tri if triangles is None else triangles,
                      show_quad=state.show_quad if quads is None else quads,
                      show_edges=state.show_edges if edges is None else edges)
    if updated.selected_face not in visible_face_ids(document, updated):
        updated = replace(updated, selected_face=None)
    return updated


def build_batch(document: MeshDocument, state: SceneState, *,
                coordinates: str, element_type: str,
                selected_only: bool = False) -> GeometryBatch:
    """Build exact index-preserving XYZ or per-corner UV cell arrays.

    UV intentionally duplicates each face corner: one XYZ vertex may have
    several valid UV corner coordinates along a seam.  XYZ uses the original
    source vertex indices and never merges distinct point identities.
    """
    if coordinates not in ('xyz', 'uv') or element_type not in ('triangle', 'quad'):
        raise SceneError("invalid_scene_query")
    visible = visible_face_ids(document, state)
    cell_indices = tuple(i for i in visible
                         if document.faces[i].element_type == element_type
                         and (not selected_only or state.selected_face == i))
    if coordinates == 'xyz':
        return GeometryBatch(document.points,
                             tuple(document.faces[i].vertices for i in cell_indices),
                             cell_indices, element_type, coordinates)
    points: list[Vector3] = []
    cells: list[tuple[int, ...]] = []
    ids: list[int] = []
    for i in cell_indices:
        uv = document.faces[i].uv
        if uv is None:
            continue
        start = len(points)
        points.extend((float(u), float(v), 0.0) for u, v in uv)
        cells.append(tuple(range(start, start+len(uv))))
        ids.append(i)
    return GeometryBatch(tuple(points), tuple(cells), tuple(ids),
                         element_type, coordinates)


def face_detail(document: MeshDocument, face_id: int) -> dict:
    if not isinstance(face_id, int) or not (0 <= face_id < len(document.faces)):
        raise SceneError("unknown_face_id")
    face = document.faces[face_id]
    return {
        "source_sha256": document.source_sha256,
        "source_face_id": face_id,
        "element_type": face.element_type,
        "group": face.group,
        "vertex_indices": list(face.vertices),
        "xyz": [list(document.points[i]) for i in face.vertices],
        "uv": [list(p) for p in face.uv] if face.uv is not None else None,
        "line_in_obj": face.line_number,
        "synthetic": document.synthetic,
        "patch_ownership": document.patch_ownership,
        "quality_status": "NOT_CERTIFIED_BY_VIEWER",
    }


def scene_json(state: SceneState) -> str:
    return json.dumps({"schema": SCENE_SCHEMA, "state": asdict(state)},
                      sort_keys=True, indent=2, allow_nan=False) + "\n"


def parse_scene(text: str, document: MeshDocument) -> SceneState:
    try:
        payload = json.loads(text)
        if not isinstance(payload, dict) or payload.get('schema') != SCENE_SCHEMA:
            raise SceneError("invalid_scene_schema")
        value = payload['state']
        if not isinstance(value, dict) or set(value) != {"source_sha256", "show_tri", "show_quad", "show_edges", "selected_face", "camera_xyz", "camera_uv"}:
            raise SceneError("invalid_scene_fields")
        if any(not isinstance(value[key], bool) for key in ('show_tri', 'show_quad', 'show_edges')):
            raise SceneError("invalid_scene_flags")
        cams = {}
        for name in ('camera_xyz', 'camera_uv'):
            camera = value[name]
            if camera is not None:
                if not isinstance(camera, dict) or set(camera) != {'position','focal_point','view_up','parallel_scale','parallel'}:
                    raise SceneError('invalid_camera')
                if not isinstance(camera['parallel'], bool) or any(
                        not isinstance(camera[x], list) or len(camera[x]) != 3 for x in ('position', 'focal_point', 'view_up')):
                    raise SceneError('invalid_camera')
                cams[name] = CameraPose(
                    tuple(camera['position']), tuple(camera['focal_point']),
                    tuple(camera['view_up']), camera['parallel_scale'], camera['parallel'])
            else:
                cams[name] = None
        result = SceneState(source_sha256=value['source_sha256'],
                            show_tri=value['show_tri'], show_quad=value['show_quad'],
                            show_edges=value['show_edges'], selected_face=value['selected_face'],
                            camera_xyz=cams['camera_xyz'], camera_uv=cams['camera_uv'])
    except (KeyError, TypeError, OverflowError, ValueError) as exc:
        if isinstance(exc, SceneError):
            raise
        raise SceneError('invalid_scene_json') from exc
    if result.source_sha256 != document.source_sha256:
        raise SceneError('scene_source_mismatch')
    if result.selected_face is not None and result.selected_face not in visible_face_ids(document, result):
        raise SceneError('selected_face_not_visible')
    return result


def write_scene(path: Path | str, state: SceneState) -> None:
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(scene_json(state))


def load_scene(path: Path | str, document: MeshDocument) -> SceneState:
    location = Path(path)
    if location.stat().st_size > 64_000:
        raise SceneError('scene_file_too_large')
    return parse_scene(location.read_text(encoding='utf-8'), document)
