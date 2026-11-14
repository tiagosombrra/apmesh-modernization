"""Immutable mesh data types that never depend on UI or rendering libraries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

Xyz: TypeAlias = tuple[float, float, float]
Uv: TypeAlias = tuple[float, float]


@dataclass(frozen=True)
class MeshFace:
    vertices: tuple[int, ...]
    uv: tuple[Uv, ...] | None
    group: str
    element_type: str
    line_number: int


@dataclass(frozen=True)
class MeshDocument:
    points: tuple[Xyz, ...]
    faces: tuple[MeshFace, ...]
    source_sha256: str
    source_name: str
    source_kind: str
    synthetic: bool
    patch_ownership: str
    source_curves: tuple[dict, ...]
    semantic_sidecar_sha256: str | None

    @property
    def triangles(self) -> int:
        return sum(face.element_type == "triangle" for face in self.faces)

    @property
    def quads(self) -> int:
        return sum(face.element_type == "quad" for face in self.faces)

    @property
    def groups(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(face.group for face in self.faces))
