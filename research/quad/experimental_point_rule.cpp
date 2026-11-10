#include "experimental_point_rule.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <utility>
#include <vector>

namespace apmesh::quad {
namespace {

struct Point {
  long double x;
  long double y;
};

long double Cross(const Point& a, const Point& b, const Point& c) {
  return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

void Require(bool condition, const char* reason) {
  if (!condition) {
    throw std::invalid_argument(reason);
  }
}

} // namespace

UvVertex ExperimentalInteriorPoint(const std::vector<UvVertex>& polygon,
                                   ExperimentalPointRule rule,
                                   long double relative_tolerance) {
  Require(std::isfinite(relative_tolerance) && relative_tolerance > 0.0L &&
              relative_tolerance < 1.0L,
          "Invalid experimental point tolerance");
  Require(polygon.size() >= 3, "Experimental polygon requires at least three vertices");
  Require(rule == ExperimentalPointRule::VertexArithmeticMean ||
              rule == ExperimentalPointRule::PolygonAreaCentroid,
          "Experimental point rule must be explicitly recognized");

  double low_u = polygon.front().u;
  double high_u = low_u;
  double low_v = polygon.front().v;
  double high_v = low_v;
  for (const auto& point : polygon) {
    Require(std::isfinite(point.u) && std::isfinite(point.v),
            "Nonfinite experimental polygon vertex");
    low_u = std::min(low_u, point.u);
    high_u = std::max(high_u, point.u);
    low_v = std::min(low_v, point.v);
    high_v = std::max(high_v, point.v);
  }
  const long double extent =
      std::max(static_cast<long double>(high_u) - low_u,
               static_cast<long double>(high_v) - low_v);
  const long double tolerance = relative_tolerance * extent * extent;
  Require(extent > 0.0L && std::isfinite(tolerance) && tolerance > 0.0L,
          "Degenerate experimental polygon extent");

  // Translate first to reduce cancellation in polygon moment calculations.
  const long double origin_u = polygon.front().u;
  const long double origin_v = polygon.front().v;
  std::vector<Point> local;
  local.reserve(polygon.size());
  for (const auto& point : polygon) {
    local.push_back({static_cast<long double>(point.u) - origin_u,
                     static_cast<long double>(point.v) - origin_v});
  }

  // Check every nonincident vertex, not merely successive edge turns.
  for (std::size_t i = 0; i < local.size(); ++i) {
    const std::size_t next = (i + 1) % local.size();
    for (std::size_t j = 0; j < local.size(); ++j) {
      if (j != i && j != next) {
        Require(Cross(local[i], local[next], local[j]) > tolerance,
                "Experimental polygon must be strictly convex and CCW");
      }
    }
  }

  Point result{0.0L, 0.0L};
  if (rule == ExperimentalPointRule::VertexArithmeticMean) {
    for (const auto& point : local) {
      result.x += point.x;
      result.y += point.y;
    }
    const long double size = static_cast<long double>(local.size());
    result.x /= size;
    result.y /= size;
  } else {
    // Fan triangulation gives the signed-area centroid for a convex polygon.
    long double twice_area = 0.0L;
    for (std::size_t i = 1; i + 1 < local.size(); ++i) {
      const long double weight = Cross(local.front(), local[i], local[i + 1]);
      Require(std::isfinite(weight) && weight > tolerance,
              "Degenerate experimental polygon triangle");
      twice_area += weight;
      result.x += weight * (local.front().x + local[i].x + local[i + 1].x) / 3.0L;
      result.y += weight * (local.front().y + local[i].y + local[i + 1].y) / 3.0L;
    }
    Require(twice_area > tolerance && std::isfinite(twice_area),
            "Degenerate experimental polygon area");
    result.x /= twice_area;
    result.y /= twice_area;
  }

  Require(std::isfinite(result.x) && std::isfinite(result.y),
          "Nonfinite experimental point arithmetic");
  const long double global_u = origin_u + result.x;
  const long double global_v = origin_v + result.y;
  Require(std::isfinite(global_u) && std::isfinite(global_v) &&
              std::abs(global_u) <= std::numeric_limits<double>::max() &&
              std::abs(global_v) <= std::numeric_limits<double>::max(),
          "Experimental point exceeds UV representation");
  const UvVertex output{static_cast<double>(global_u), static_cast<double>(global_v)};
  const Point rounded{static_cast<long double>(output.u) - origin_u,
                      static_cast<long double>(output.v) - origin_v};
  for (std::size_t i = 0; i < local.size(); ++i) {
    Require(Cross(local[i], local[(i + 1) % local.size()], rounded) > tolerance,
            "Experimental point is not strictly inside the polygon");
  }
  return output;
}

} // namespace apmesh::quad
