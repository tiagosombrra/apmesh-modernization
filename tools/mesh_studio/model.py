"""Immutable mesh data types that never depend on UI or rendering libraries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias, Any, Mapping
from types import MappingProxyType
import json
import hashlib

Xyz: TypeAlias = tuple[float, float, float]
Uv: TypeAlias = tuple[float, float]


def immutable_science_metadata(value: Any) -> Any:
    """Deep-freeze data without silently losing nested source semantics."""
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): immutable_science_metadata(v)
                                 for k, v in value.items()})
    if isinstance(value, (tuple, list)):
        return tuple(immutable_science_metadata(x) for x in value)
    if value is None or type(value) in (str, float, int, bool):
        return value
    raise TypeError('invalid_scientific_metadata_type')


def source_metadata_digest(raw: Mapping[str, Any]) -> str:
    """Bind semantic metadata to an exact deterministic JSON representation."""
    payload = json.dumps(raw, sort_keys=True, separators=(',', ':'),
                         ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class MeshFace:
    vertices: tuple[int, ...]
    uv: tuple[Uv, ...] | None
    group: str
    element_type: str
    line_number: int
    patch_id: str | None = None


@dataclass(frozen=True)
class MeshDocument:
    points: tuple[Xyz, ...]
    faces: tuple[MeshFace, ...]
    source_sha256: str
    source_name: str
    source_kind: str
    synthetic: bool
    patch_ownership: str
    source_curves: tuple[Mapping[str, Any], ...]
    semantic_sidecar_sha256: str | None
    semantic_metadata_sha256: str | None = None
    source_model_sha256: str | None = None
    source_generator_commit: str | None = None
    source_patches: tuple[str, ...] = ()

    @property
    def triangles(self) -> int:
        return sum(face.element_type == "triangle" for face in self.faces)

    @property
    def quads(self) -> int:
        return sum(face.element_type == "quad" for face in self.faces)

    @property
    def groups(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(face.group for face in self.faces))
