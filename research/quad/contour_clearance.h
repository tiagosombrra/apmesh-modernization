#ifndef APMESH_RESEARCH_QUAD_CONTOUR_CLEARANCE_H
#define APMESH_RESEARCH_QUAD_CONTOUR_CLEARANCE_H

#include "uv_mesh.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <utility>
#include <vector>

namespace apmesh::quad {

// Explicit research policy: minimum closed-cell/finite-segment distance in UV.
// Exclude strictly below one fifth of that contour segment's length.
class UvContourClearance {
public:
  explicit UvContourClearance(std::vector<UvVertex> contour) : contour_(std::move(contour)) {
    Require(contour_.size() >= 3, "Clearance needs a closed contour");
    for (std::size_t i = 0; i < contour_.size(); ++i) {
      const auto a = contour_[i], b = contour_[(i + 1) % contour_.size()];
      Require(std::isfinite(a.u) && std::isfinite(a.v), "Nonfinite clearance contour");
      const auto length = Squared(a, b);
      Require(std::isfinite(length) && length > 0, "Degenerate clearance segment");
    }
  }

  bool Excludes(UvVertex low, UvVertex high) const {
    Require(std::isfinite(low.u) && std::isfinite(low.v) && std::isfinite(high.u) &&
                std::isfinite(high.v) && low.u < high.u && low.v < high.v,
            "Invalid clearance cell");
    const std::array<UvVertex, 4> corners{low, UvVertex{high.u, low.v}, high,
                                          UvVertex{low.u, high.v}};
    for (std::size_t i = 0; i < contour_.size(); ++i) {
      const auto a = contour_[i], b = contour_[(i + 1) % contour_.size()];
      const auto inside = [&](UvVertex p) {
        return low.u <= p.u && p.u <= high.u && low.v <= p.v && p.v <= high.v;
      };
      if (inside(a) || inside(b))
        return true;
      long double distance = std::numeric_limits<long double>::infinity();
      for (std::size_t side = 0; side < corners.size(); ++side) {
        const auto c = corners[side], d = corners[(side + 1) % corners.size()];
        if (Intersects(a, b, c, d))
          return true;
        distance = std::min({distance, PointSegment(a, c, d), PointSegment(b, c, d),
                             PointSegment(c, a, b), PointSegment(d, a, b)});
      }
      // Squared comparison encodes exactly the approved factor 1/5, without a
      // new epsilon, infinite supporting lines or a cell-center approximation.
      if (distance < Squared(a, b) / 25.0L)
        return true;
    }
    return false;
  }

private:
  static void Require(bool condition, const char* reason) {
    if (!condition)
      throw std::invalid_argument(reason);
  }
  static long double Squared(UvVertex a, UvVertex b) {
    const long double x = static_cast<long double>(a.u) - b.u;
    const long double y = static_cast<long double>(a.v) - b.v;
    return x * x + y * y;
  }
  static long double Cross(UvVertex a, UvVertex b, UvVertex c) {
    return (static_cast<long double>(b.u) - a.u) * (static_cast<long double>(c.v) - a.v) -
           (static_cast<long double>(b.v) - a.v) * (static_cast<long double>(c.u) - a.u);
  }
  static bool On(UvVertex a, UvVertex b, UvVertex p) {
    return Cross(a, b, p) == 0 && std::min(a.u, b.u) <= p.u && p.u <= std::max(a.u, b.u) &&
           std::min(a.v, b.v) <= p.v && p.v <= std::max(a.v, b.v);
  }
  static bool Intersects(UvVertex a, UvVertex b, UvVertex c, UvVertex d) {
    const auto opposite = [](long double x, long double y) {
      return (x < 0 && y > 0) || (x > 0 && y < 0);
    };
    return On(a, b, c) || On(a, b, d) || On(c, d, a) || On(c, d, b) ||
           (opposite(Cross(a, b, c), Cross(a, b, d)) && opposite(Cross(c, d, a), Cross(c, d, b)));
  }
  static long double PointSegment(UvVertex p, UvVertex a, UvVertex b) {
    const long double x = static_cast<long double>(b.u) - a.u;
    const long double y = static_cast<long double>(b.v) - a.v;
    const long double px = static_cast<long double>(p.u) - a.u;
    const long double py = static_cast<long double>(p.v) - a.v;
    const auto t = std::clamp((px * x + py * y) / (x * x + y * y), 0.0L, 1.0L);
    return (px - t * x) * (px - t * x) + (py - t * y) * (py - t * y);
  }
  std::vector<UvVertex> contour_;
};
} // namespace apmesh::quad

#endif
