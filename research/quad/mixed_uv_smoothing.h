#ifndef APMESH_RESEARCH_MIXED_UV_SMOOTHING_H
#define APMESH_RESEARCH_MIXED_UV_SMOOTHING_H

#include "uv_mesh.h"

#include <algorithm>
#include <cmath>
#include <functional>
#include <map>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>

namespace apmesh::quad {
struct MixedUvSmoothingTrace {
  std::vector<VertexId> boundary;
  std::vector<std::vector<UvVertex>> passes;
};
using MixedUvPassValidator = std::function<void(std::size_t, const std::vector<UvVertex>&)>;
using MixedUvPassFilter =
    std::function<void(std::size_t, const std::vector<UvVertex>&, std::vector<UvVertex>&)>;

// Confirmed research interpretation: distinct other vertices of incident faces,
// including opposite QUAD corners, ascending retained ID order, five Jacobi
// passes and fixed original contour. Caller validates/lifts every complete pass.
// All values remain local until success; input and physical owners are untouched.
inline MixedUvSmoothingTrace SmoothMixedUv(const std::vector<UvVertex>& input,
                                           const std::vector<std::vector<VertexId>>& faces,
                                           const MixedUvPassValidator& validate,
                                           const MixedUvPassFilter& filter = {}) {
  const auto require = [](bool condition, const char* reason) {
    if (!condition)
      throw std::invalid_argument(reason);
  };
  require(!input.empty() && !faces.empty() && static_cast<bool>(validate),
          "Mixed smoothing requires geometry and a pass validator");
  for (const auto p : input)
    require(std::isfinite(p.u) && std::isfinite(p.v), "Nonfinite mixed smoothing input");
  std::vector<std::set<VertexId>> neighbors(input.size());
  struct EdgeUse {
    unsigned count = 0;
    VertexId first = 0, second = 0;
  };
  std::map<std::pair<VertexId, VertexId>, EdgeUse> edges;
  for (const auto& face : faces) {
    require((face.size() == 3 || face.size() == 4) &&
                std::set<VertexId>(face.begin(), face.end()).size() == face.size(),
            "Invalid mixed smoothing face");
    for (const auto id : face)
      require(id < input.size(), "Mixed smoothing vertex index out of range");
    for (std::size_t i = 0; i < face.size(); ++i) {
      const auto a = face[i], b = face[(i + 1) % face.size()];
      auto& use = edges[std::minmax(a, b)];
      require(use.count < 2 && (use.count == 0 || (use.first == b && use.second == a)),
              "Nonmanifold or inconsistent mixed smoothing incidence");
      use.first = a;
      use.second = b;
      ++use.count;
      for (const auto other : face)
        if (other != a)
          neighbors[a].insert(other);
    }
  }
  MixedUvSmoothingTrace trace;
  std::set<VertexId> fixed;
  for (const auto& [edge, use] : edges)
    if (use.count == 1) {
      fixed.insert(edge.first);
      fixed.insert(edge.second);
    }
  require(!fixed.empty(), "Mixed smoothing has no contour");
  trace.boundary.assign(fixed.begin(), fixed.end());
  for (const auto& adjacent : neighbors)
    require(!adjacent.empty(), "Unused mixed smoothing node");
  auto current = input;
  for (std::size_t pass = 1; pass <= 5; ++pass) {
    auto next = current;
    for (VertexId i = 0; i < current.size(); ++i) {
      if (fixed.count(i))
        continue;
      UvVertex mean{0, 0};
      for (const auto other : neighbors[i]) {
        mean.u += current[other].u;
        mean.v += current[other].v;
      }
      const auto count = static_cast<double>(neighbors[i].size());
      mean.u /= count;
      mean.v /= count;
      require(std::isfinite(mean.u) && std::isfinite(mean.v), "Nonfinite mixed smoothing mean");
      next[i] = mean;
    }
    if (filter)
      filter(pass, current, next);
    validate(pass, next);
    trace.passes.push_back(next);
    current = std::move(next);
  }
  return trace;
}
} // namespace apmesh::quad
#endif
