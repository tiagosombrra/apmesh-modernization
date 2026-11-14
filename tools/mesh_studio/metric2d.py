"""Small independent SPD 2D metric oracle for synthetic illustrations."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Metric2D:
    """Symmetric tangent-domain metric [[m00,m01],[m01,m11]]."""

    m00: float
    m01: float
    m11: float

    def __post_init__(self) -> None:
        values = (self.m00, self.m01, self.m11)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("nonfinite_metric")
        if not (self.m00 > 0 and self.m11 > 0):
            raise ValueError("metric_not_spd")
        # The determinant criterion is necessary and sufficient for 2x2 SPD.
        determinant = self.m00 * self.m11 - self.m01 * self.m01
        if not (math.isfinite(determinant) and determinant > 0):
            raise ValueError("metric_not_spd")

    @property
    def eigenvalues(self) -> tuple[float, float]:
        center = (self.m00 + self.m11) / 2
        radius = math.hypot((self.m00 - self.m11) / 2, self.m01)
        low, high = center - radius, center + radius
        if not (low > 0 and math.isfinite(high)):
            raise ValueError("metric_numerically_singular")
        return (low, high)

    def squared_length(self, dx: float, dy: float) -> float:
        if not (math.isfinite(dx) and math.isfinite(dy)):
            raise ValueError("nonfinite_edge")
        result = self.m00 * dx * dx + 2 * self.m01 * dx * dy + self.m11 * dy * dy
        if not (math.isfinite(result) and result >= 0):
            raise ValueError("invalid_metric_length")
        return result

    def length(self, dx: float, dy: float) -> float:
        return math.sqrt(self.squared_length(dx, dy))

    def unit_ellipse_axes(self) -> tuple[float, float]:
        low, high = self.eigenvalues
        return (1 / math.sqrt(high), 1 / math.sqrt(low))


def rotated_diagonal(high: float, low: float, angle_radians: float) -> Metric2D:
    """Return R diag(high,low) R^T in its original XY coordinate frame."""
    if not all(map(math.isfinite, (high, low, angle_radians))):
        raise ValueError("nonfinite_metric")
    c, s = math.cos(angle_radians), math.sin(angle_radians)
    return Metric2D(high * c * c + low * s * s,
                    (high - low) * c * s,
                    high * s * s + low * c * c)
