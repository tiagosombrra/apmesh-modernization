"""A bounded, semantics-preserving Wavefront OBJ and APMesh fixture importer."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from .model import MeshDocument, MeshFace

MAX_SOURCE_BYTES = 20 * 1024 * 1024
MAX_POINTS = 800_000
MAX_FACES = 800_000
EPS = 1e-14


class MeshImportError(ValueError):
    """Import failure with a stable diagnostic and the actual source line."""

    def __init__(self, code: str, line: int = 0, detail: str = ""):
        self.code = code
        self.line = line
        super().__init__(f"{code} at line {line}" + (f": {detail}" if detail else ""))


def _check(ok: bool, code: str, line: int = 0) -> None:
    if not ok:
        raise MeshImportError(code, line)


def _float(word: str, line: int) -> float:
    try:
        result = float(word)
    except (TypeError, ValueError) as exc:
        raise MeshImportError("invalid_float", line, word) from exc
    _check(math.isfinite(result), "nonfinite_coordinate", line)
    return result


def _index(token: str, count: int, line: int) -> int:
    try:
        value = int(token)
    except ValueError as exc:
        raise MeshImportError("invalid_index", line, token) from exc
    _check(value != 0, "out_of_range_index", line)
    resolved = value - 1 if value > 0 else count + value
    _check(0 <= resolved < count, "out_of_range_index", line)
    return resolved


def _cross(a: tuple[float, ...], b: tuple[float, ...], c: tuple[float, ...]):
    x = tuple(b[k] - a[k] for k in range(3))
    y = tuple(c[k] - a[k] for k in range(3))
    return (x[1] * y[2] - x[2] * y[1],
            x[2] * y[0] - x[0] * y[2],
            x[0] * y[1] - x[1] * y[0])


def _turn(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _validate_geometry(points, faces, reference_normal=None):
    for face in faces:
        idx = face.vertices
        _check(len(set(idx)) == len(idx), "repeated_vertex", face.line_number)
        if face.uv is not None:
            uv = face.uv
            _check(all(math.isfinite(x) for pair in uv for x in pair),
                   "nonfinite_uv", face.line_number)
            if len(idx) == 3:
                _check(_turn(*uv) > EPS, "uv_winding", face.line_number)
            else:
                _check(all(_turn(uv[i], uv[(i + 1) % 4], uv[(i + 2) % 4]) > EPS
                           for i in range(4)), "concave_uv", face.line_number)
        for positions in ((0, 1, 2), (0, 2, 3)) if len(idx) == 4 else ((0, 1, 2),):
            a, b, c = (points[idx[k]] for k in positions)
            cross = _cross(a, b, c)
            _check(math.hypot(*cross) > EPS, "degenerate_physical_facet", face.line_number)
            if reference_normal is not None:
                _check(sum(cross[k] * reference_normal[k] for k in range(3)) > EPS,
                       "inverted_physical_facet", face.line_number)


def _read_sidecar(path: Path | None, obj_hash: str):
    if path is None:
        return None, None
    content = path.read_bytes()
    _check(len(content) <= MAX_SOURCE_BYTES, "file_too_large")
    try:
        sidecar = json.loads(content)
    except (ValueError, UnicodeError) as exc:
        raise MeshImportError("invalid_sidecar_json") from exc
    _check(isinstance(sidecar, dict), "invalid_sidecar_json")
    _check(sidecar.get("schema") == "apmesh.meshstudio.synthetic.v1" and
           sidecar.get("synthetic") is True, "unsupported_sidecar_schema")
    _check(sidecar.get("obj_sha256") == obj_hash, "source_sha_mismatch")
    return sidecar, hashlib.sha256(content).hexdigest()


def _parse(text: str):
    points, uv_coords, normals, faces = [], [], [], []
    group = "ungrouped"
    legacy = False
    legacy_next_count = None
    declared = {}
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            if line == "# of vertices":
                legacy_next_count = "vertices"
            elif line == "# of faces":
                legacy_next_count = "faces"
            continue
        if line == "File Wavefront OBJ generated apMesh":
            _check(not faces and not points, "invalid_legacy_header", number)
            legacy = True
            continue
        if legacy and legacy_next_count is not None and line.isdecimal():
            declared[legacy_next_count] = int(line)
            legacy_next_count = None
            continue
        tokens = line.split()
        op, values = tokens[0], tokens[1:]
        if op == "v":
            _check(len(values) == 3, "invalid_vertex_arity", number)
            _check(len(points) < MAX_POINTS, "point_limit", number)
            points.append(tuple(_float(x, number) for x in values))
        elif op == "vt":
            _check(len(values) == 2, "invalid_uv_arity", number)
            uv_coords.append(tuple(_float(x, number) for x in values))
        elif op == "vn":
            _check(len(values) == 3, "invalid_normal_arity", number)
            normals.append(tuple(_float(x, number) for x in values))
        elif op == "g":
            _check(len(values) == 1, "invalid_group", number)
            group = values[0]
        elif op == "o":
            _check(len(values) == 1, "invalid_object", number)
            group = values[0]
        elif op in ("s", "usemtl"):
            _check(len(values) == 1, "invalid_record", number)
        elif op == "f":
            _check(len(values) in (3, 4), "invalid_face_arity", number)
            _check(len(faces) < MAX_FACES, "face_limit", number)
            ids, t_ids = [], []
            for vertex in values:
                parts = vertex.split("/")
                _check(1 <= len(parts) <= 3 and parts[0] != "", "invalid_index", number)
                ids.append(_index(parts[0], len(points), number))
                t_ids.append(_index(parts[1], len(uv_coords), number)
                             if len(parts) >= 2 and parts[1] else None)
                if len(parts) == 3 and parts[2]:
                    _index(parts[2], len(normals), number)
            _check(len(set(ids)) == len(ids), "repeated_vertex", number)
            _check(all(x is None for x in t_ids) or all(x is not None for x in t_ids),
                   "partial_face_uv", number)
            uv = tuple(uv_coords[i] for i in t_ids) if t_ids[0] is not None else None
            faces.append(MeshFace(tuple(ids), uv, group,
                                  "triangle" if len(ids) == 3 else "quad", number))
        elif op == "mtllib":
            raise MeshImportError("external_material_not_allowed", number)
        else:
            raise MeshImportError("unexpected_obj_record", number, op)
    _check(bool(points) and bool(faces), "empty_geometry")
    if legacy:
        _check(declared.get("vertices") == len(points) and
               declared.get("faces") == len(faces), "legacy_count_mismatch")
    return points, faces, legacy


def import_obj(path: Path | str, sidecar_path: Path | str | None = None,
               *, auto_sidecar: bool = True) -> MeshDocument:
    """Import strict geometry, preserving independent per-corner UV coordinates."""
    path = Path(path)
    _check(path.is_file(), "missing_obj")
    _check(path.stat().st_size <= MAX_SOURCE_BYTES, "file_too_large")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeError as exc:
        raise MeshImportError("invalid_utf8") from exc
    source_hash = hashlib.sha256(raw).hexdigest()
    points, faces, legacy = _parse(text)
    if sidecar_path is None and auto_sidecar and path.with_suffix(".json").is_file():
        sidecar_path = path.with_suffix(".json")
    sidecar, sidecar_hash = _read_sidecar(Path(sidecar_path) if sidecar_path else None, source_hash)
    curves = []
    if sidecar is not None:
        _check(len(sidecar.get("nodes", [])) == len(points) and
               len(sidecar.get("faces", [])) == len(faces), "sidecar_inventory")
        _check(all(tuple(row) == point for row, point in zip(sidecar["nodes"], points)),
               "obj_sidecar_xyz_mismatch")
        reconciled = []
        for face, meta in zip(faces, sidecar["faces"]):
            uv = tuple(tuple(pair) for pair in meta["uv"])
            _check(meta["nodes"] == list(face.vertices) and
                   meta["patch_id"] == face.group and
                   meta["kind"] == face.element_type and len(uv) == len(face.vertices),
                   "face_sidecar_mismatch", face.line_number)
            if face.uv is not None:
                _check(face.uv == uv, "uv_sidecar_mismatch", face.line_number)
            reconciled.append(MeshFace(face.vertices, uv, face.group,
                                       face.element_type, face.line_number))
        faces = reconciled
        point_groups = {}
        for face in faces:
            for index in face.vertices:
                _check(index not in point_groups or point_groups[index] == face.group,
                       "cross_patch_node_alias", face.line_number)
                point_groups[index] = face.group
        for curve in sidecar.get("curves", []):
            canonical = curve["canonical_xyz"]
            _check(len(curve["sample_parameters"]) == len(canonical),
                   "shared_curve_sample_count")
            for patch in curve["incident_patches"]:
                candidates = curve["by_patch_xyz"][patch]
                _check(len(candidates) == len(canonical) and
                       all(math.dist(a, b) <= 1e-10 for a, b in zip(candidates, canonical)),
                       "shared_curve_mismatch")
            _check(curve["topology_weld_approved"] is False,
                   "source_welding_unsupported")
            curves.append(curve)
    _validate_geometry(points, faces, sidecar.get("reference_normal") if sidecar else None)
    return MeshDocument(
        points=tuple(points), faces=tuple(faces), source_sha256=source_hash,
        source_name=path.name, source_kind="synthetic_sidecar" if sidecar else
        "legacy_apmesh_obj" if legacy else "wavefront_obj",
        synthetic=bool(sidecar), patch_ownership="sidecar_patch_local" if sidecar else "unknown",
        source_curves=tuple(curves), semantic_sidecar_sha256=sidecar_hash,
    )
