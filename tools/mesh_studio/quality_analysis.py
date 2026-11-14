"""Independent, unit-declared cell-quality estimators for scientific inspection.

Discrete element checks cannot certify an entire smooth source surface.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import statistics
from typing import Callable

from .metric2d import Metric2D
from .model import MeshDocument, Uv, Xyz
from .topology_audit import audit_topology


class QualityError(ValueError):
    """A cell or prescribed metric is not numerically evaluable."""


def _vector(a: Xyz, b: Xyz) -> Xyz:
    return (b[0] - a[0], b[1] - a[1], b[2] - a[2])


def _cross(a: Xyz, b: Xyz) -> Xyz:
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def _dot(a: Xyz, b: Xyz) -> float:
    return sum(x*y for x, y in zip(a, b))


def _norm(x: Xyz) -> float:
    return math.hypot(*x)


def _triangle_cross(a: Xyz, b: Xyz, c: Xyz) -> Xyz:
    return _cross(_vector(a, b), _vector(a, c))


def _uv_area(uv: tuple[Uv, ...]) -> float:
    return 0.5 * sum(p[0]*q[1]-q[0]*p[1] for p, q in zip(uv, uv[1:] + uv[:1]))


def _uv_turn(a: Uv, b: Uv, c: Uv) -> float:
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def _triangle_shape(a: Xyz, b: Xyz, c: Xyz) -> float:
    """Mean ratio: 4 sqrt(3) A / (a²+b²+c²); equilateral yields 1."""
    edges = (_vector(a, b), _vector(b, c), _vector(c, a))
    denominator = sum(_dot(edge, edge) for edge in edges)
    if denominator <= 0 or not math.isfinite(denominator):
        raise QualityError("degenerate_triangle")
    value = 2 * math.sqrt(3) * _norm(_triangle_cross(a, b, c)) / denominator
    if not math.isfinite(value) or value <= 0:
        raise QualityError("degenerate_triangle")
    return min(1.0, value)


def _normal_for_quad(points: tuple[Xyz, ...]) -> Xyz:
    """Return the first-facet unit normal, not an original Bezier normal."""
    n = _triangle_cross(points[0], points[1], points[2])
    magnitude = _norm(n)
    if magnitude == 0:
        raise QualityError("degenerate_quad")
    return tuple(x / magnitude for x in n)


def _planar_quad_scaled_jacobian(points: tuple[Xyz, ...], n: Xyz) -> float:
    values = []
    for i in range(4):
        origin = points[i]
        forward = _vector(origin, points[(i+1) % 4])
        backward = _vector(origin, points[(i-1) % 4])
        denominator = _norm(forward)*_norm(backward)
        if denominator <= 0:
            raise QualityError("degenerate_quad")
        # The preceding corner edge points into the current corner.
        values.append(_dot(_cross(forward, backward), n) / denominator)
    return min(values)


def _quad_planarity(points: tuple[Xyz, ...], n: Xyz) -> float:
    edges = [_norm(_vector(points[i], points[(i+1) % 4])) for i in range(4)]
    diameter = max(edges)
    if diameter <= 0:
        raise QualityError("degenerate_quad")
    return abs(_dot(_vector(points[0], points[3]), n)) / diameter


def _unit_normal(value: Xyz) -> Xyz:
    if not all(math.isfinite(x) for x in value):
        raise QualityError("nonfinite_source_normal")
    size = _norm(value)
    if size <= 1e-14:
        raise QualityError("degenerate_source_normal")
    return tuple(x / size for x in value)


def _percentiles(values: list[float]) -> dict | None:
    if not values:
        return None
    sorted_values = sorted(values)
    def at(p: float) -> float:
        position = p*(len(sorted_values)-1)
        left = int(position)
        weight = position-left
        return sorted_values[left]*(1-weight)+sorted_values[min(left+1,len(sorted_values)-1)]*weight
    return {"count": len(values), "min": sorted_values[0], "p05": at(.05),
            "median": statistics.median(sorted_values), "p95": at(.95),
            "max": sorted_values[-1], "mean": statistics.fmean(sorted_values)}


def edge_metric_length(a: Uv, b: Uv, field: Metric2D | Callable[[float, float], Metric2D]) -> float:
    """Integrate line length under SPD metric using 2-point Gauss quadrature.

    Constant metric fields are integrated exactly; varying fields require an
    explicit quadrature-accuracy statement, not a convergence claim.
    """
    if not all(math.isfinite(x) for x in (*a, *b)):
        raise QualityError("nonfinite_uv")
    dx, dy = b[0]-a[0], b[1]-a[1]
    if isinstance(field, Metric2D):
        return field.length(dx, dy)
    nodes = (.5-.5/math.sqrt(3), .5+.5/math.sqrt(3))
    result = 0.0
    for t in nodes:
        sampled = field(a[0]+t*dx, a[1]+t*dy)
        if not isinstance(sampled, Metric2D):
            raise QualityError("invalid_metric_sample")
        result += .5*sampled.length(dx, dy)
    return result


@dataclass(frozen=True)
class CellQuality:
    index: int
    group: str
    element_type: str
    physical_area: float
    uv_signed_area: float | None
    triangle_mean_ratio: float | None
    planar_quad_min_scaled_jacobian: float | None
    quad_relative_planarity: float | None
    physical_orientation: str
    metric_edge_lengths: tuple[float, ...] | None


def analyze_mesh(document: MeshDocument, *,
                 source_normal: Callable[[float, float], Xyz] | None = None,
                 metric_field: Metric2D | Callable[[float, float], Metric2D] | None = None,
                 metric_frame: str | None = None) -> dict:
    """Return a deterministic measurement report without changing input data.

    The caller must separately justify source_normal and metric_field as
    analytic or measured sources. Unknown normals yield UNVERIFIED, not PASS.
    """
    if metric_field is not None and metric_frame != "uv":
        raise QualityError("metric_frame_required_uv")
    if source_normal is not None and not callable(source_normal):
        raise QualityError("invalid_source_normal_oracle")
    topology = audit_topology(document)
    quality: list[CellQuality] = []
    tri_scores: list[float] = []
    quad_scores: list[float] = []
    epsilon = 1e-14
    for i, face in enumerate(document.faces):
        points = tuple(document.points[index] for index in face.vertices)
        if not all(math.isfinite(v) for point in points for v in point):
            raise QualityError("nonfinite_physical_coordinate")
        triangles = ((0,1,2),) if face.element_type == "triangle" else ((0,1,2),(0,2,3))
        cross = [_triangle_cross(*(points[j] for j in indices)) for indices in triangles]
        areas = [0.5*_norm(v) for v in cross]
        if any(not math.isfinite(area) or area <= epsilon for area in areas):
            raise QualityError("degenerate_physical_facet")
        physical_area = sum(areas)
        uv = face.uv
        if uv is not None and any(not math.isfinite(z) for t in uv for z in t):
            raise QualityError("nonfinite_uv")
        uv_area = _uv_area(uv) if uv is not None else None
        if uv_area is not None and uv_area <= epsilon:
            raise QualityError("invalid_uv_winding")
        if uv is not None and face.element_type == "quad":
            if any(_uv_turn(uv[k], uv[(k+1)%4], uv[(k+2)%4]) <= epsilon
                   for k in range(4)):
                raise QualityError("invalid_uv_quad_corner")
        physical_orientation = "UNVERIFIED_NO_SOURCE_NORMAL"
        if source_normal is not None:
            if uv is None:
                physical_orientation = "UNVERIFIED_NO_UV"
            else:
                for indices, n in zip(triangles, cross):
                    u = sum(uv[j][0] for j in indices) / 3
                    v = sum(uv[j][1] for j in indices) / 3
                    reference = _unit_normal(source_normal(u,v))
                    if _dot(n, reference) <= epsilon:
                        raise QualityError("inverted_physical_facet")
                physical_orientation = "POSITIVE_AT_FACET_SAMPLES_ONLY"
        mean_ratio = None
        scaled_jacobian = None
        relative_planarity = None
        if face.element_type == "triangle":
            mean_ratio = _triangle_shape(*points)
            tri_scores.append(mean_ratio)
        else:
            unit_normal = _normal_for_quad(points)
            relative_planarity = _quad_planarity(points, unit_normal)
            # Planarity uses a strict scale-relative threshold; nonplanar quads
            # do not receive a misleading planar Jacobian score.
            if relative_planarity <= 1e-10:
                scaled_jacobian = _planar_quad_scaled_jacobian(points, unit_normal)
                if scaled_jacobian <= 0:
                    raise QualityError("folded_planar_quad")
                quad_scores.append(scaled_jacobian)
        metric_lengths = None
        if metric_field is not None:
            if uv is None:
                raise QualityError("metric_requires_uv")
            metric_lengths = tuple(edge_metric_length(a,b,metric_field)
                                   for a,b in zip(uv,uv[1:]+uv[:1]))
        quality.append(CellQuality(i, face.group, face.element_type, physical_area,
                                   uv_area, mean_ratio, scaled_jacobian,
                                   relative_planarity,physical_orientation,metric_lengths))
    return {
        "schema": "apmesh.meshstudio.quality_report.v1",
        "source_sha256": document.source_sha256,
        "source_kind": document.source_kind,
        "synthetic": document.synthetic,
        "cell_inventory": {"triangle": document.triangles, "quad": document.quads},
        "measures": {
            "triangle_mean_ratio_3d_v1": _percentiles(tri_scores),
            "planar_quad_min_scaled_jacobian_3d_v1": _percentiles(quad_scores),
            "metric_basis": metric_frame if metric_field is not None else None,
            "metric_quadrature": "constant_exact_or_gauss_2point_approx" if metric_field is not None else None,
        },
        "cells": [asdict(cell) for cell in quality],
        "topology": topology,
        "source_surface_global_certification": False,
        "physical_area_definition": "triangle_facet_area_or_quad_diagonal_0_2_facet_sum",
        "physical_area_units": "squared_source_xyz_coordinate_units_unspecified",
        "uv_area_units": "squared_source_parametric_coordinate_units_unspecified",
        "source_normal_provenance": (
            "CALLER_SUPPLIED_UNAUTHENTICATED" if source_normal else "NOT_PROVIDED"
        ),
        "metric_field_provenance": (
            "CALLER_SUPPLIED_UNAUTHENTICATED" if metric_field is not None
            else "NOT_PROVIDED"
        ),
        "warning": "Facets and indexed charts only; no continuous Bezier Jacobian or global self-intersection proof.",
    }
