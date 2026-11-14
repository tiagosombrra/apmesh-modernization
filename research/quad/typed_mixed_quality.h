#ifndef APMESH_QUAD_RESEARCH_TYPED_MIXED_QUALITY_H
#define APMESH_QUAD_RESEARCH_TYPED_MIXED_QUALITY_H

#include <algorithm>
#include <array>
#include <cmath>
#include <stdexcept>

namespace apmesh::quad::research {

// Independent per-corner metric of a retained four-node physical QUAD.
// This is NOT a certified bilinear Jacobian bound over the entire element.
using QualityPoint3 = std::array<double, 3>;
using PhysicalQuadCorners = std::array<QualityPoint3, 4>;
struct PhysicalQuadQuality {
  double min_scaled_jacobian = 1.0;
  double diagonal_normal_cosine = 1.0;
  double edge_ratio = 1.0;
};

inline PhysicalQuadQuality ObservePhysicalQuadQuality(
    const PhysicalQuadCorners& points,
    const PhysicalQuadCorners& source_normals) {
  auto require = [](bool condition, const char* reason) {
    if (!condition)
      throw std::invalid_argument(reason);
  };
  auto dot = [](const QualityPoint3& a, const QualityPoint3& b) {
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  };
  auto delta = [](const QualityPoint3& a, const QualityPoint3& b) {
    return QualityPoint3{a[0] - b[0], a[1] - b[1], a[2] - b[2]};
  };
  auto cross = [](const QualityPoint3& a, const QualityPoint3& b) {
    return QualityPoint3{a[1] * b[2] - a[2] * b[1],
                         a[2] * b[0] - a[0] * b[2],
                         a[0] * b[1] - a[1] * b[0]};
  };
  auto norm = [&](const QualityPoint3& x) { return std::sqrt(dot(x, x)); };
  for (unsigned i = 0; i < 4; ++i) {
    for (const double x : points[i])
      require(std::isfinite(x), "Nonfinite physical QUAD corner");
    for (const double x : source_normals[i])
      require(std::isfinite(x), "Nonfinite physical QUAD reference normal");
  }
  PhysicalQuadQuality result;
  double min_edge = 0.0, max_edge = 0.0;
  for (unsigned i = 0; i < 4; ++i) {
    const auto next = delta(points[(i + 1) % 4], points[i]);
    const auto prev = delta(points[(i + 3) % 4], points[i]);
    const double first = norm(next);
    const double second = norm(prev);
    const double normal_size = norm(source_normals[i]);
    require(std::isfinite(first) && std::isfinite(second) &&
                std::isfinite(normal_size) && first > 1e-14 &&
                second > 1e-14 && normal_size > 1e-12,
            "Degenerate physical QUAD edge or reference normal");
    const double scaled = dot(cross(next, prev), source_normals[i]) /
                          (first * second * normal_size);
    require(std::isfinite(scaled) && scaled > 1e-12 && scaled <= 1.0 + 1e-12,
            "Nonpositive or invalid physical QUAD corner scaled Jacobian");
    result.min_scaled_jacobian = std::min(result.min_scaled_jacobian, scaled);
    if (i == 0) min_edge = first;
    min_edge = std::min(min_edge, first);
    max_edge = std::max(max_edge, first);
  }
  result.edge_ratio = max_edge / min_edge;
  require(std::isfinite(result.edge_ratio) && result.edge_ratio >= 1.0,
          "Invalid physical QUAD edge ratio");
  const auto n1 = cross(delta(points[1], points[0]), delta(points[2], points[0]));
  const auto n2 = cross(delta(points[2], points[0]), delta(points[3], points[0]));
  const double denom = norm(n1) * norm(n2);
  require(std::isfinite(denom) && denom > 1e-14,
          "Degenerate physical QUAD diagonal subtriangle");
  result.diagonal_normal_cosine = dot(n1, n2) / denom;
  require(std::isfinite(result.diagonal_normal_cosine) &&
              result.diagonal_normal_cosine > 0.0 &&
              result.diagonal_normal_cosine <= 1.0 + 1e-12,
          "Folded or invalid physical QUAD split normal");
  return result;
}

} // namespace apmesh::quad::research
#endif // APMESH_QUAD_RESEARCH_TYPED_MIXED_QUALITY_H
