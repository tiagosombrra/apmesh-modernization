#ifndef APMESH_RESEARCH_QUAD_BOUNDARY_PAIR_CANDIDATES_H
#define APMESH_RESEARCH_QUAD_BOUNDARY_PAIR_CANDIDATES_H

#include <algorithm>
#include <array>
#include <cstddef>
#include <map>
#include <stdexcept>
#include <utility>
#include <vector>

namespace apmesh::quad {

// A value-only topological possibility, not a selected or geometry-qualified QUAD.
// Triangle and vertex indices belong to the caller's unchanged source arrays.
struct BoundaryPairCandidate {
  std::size_t first_triangle;
  std::size_t second_triangle;
  std::array<std::size_t, 2> shared_edge;
  std::array<std::size_t, 4> boundary_cycle;
};

// Inventory adjacent TRI pairs in completed AFT output. This is not the article's
// in-front selection algorithm: candidates may conflict or be geometrically bad.
inline std::vector<BoundaryPairCandidate>
CollectBoundaryPairCandidates(std::size_t vertex_count,
                              const std::vector<std::array<std::size_t, 3>>& triangles) {
  struct EdgeUse {
    std::size_t triangle;
    std::size_t from;
    std::size_t to;
    std::size_t opposite;
    unsigned count;
  };
  std::map<std::pair<std::size_t, std::size_t>, EdgeUse> edges;
  std::vector<BoundaryPairCandidate> result;
  for (std::size_t i = 0; i < triangles.size(); ++i) {
    const auto& triangle = triangles[i];
    for (auto id : triangle) {
      if (id >= vertex_count)
        throw std::invalid_argument("Boundary pair contains a foreign vertex index");
    }
    if (triangle[0] == triangle[1] || triangle[1] == triangle[2] || triangle[2] == triangle[0])
      throw std::invalid_argument("Boundary pair contains a repeated triangle vertex");
    for (std::size_t side = 0; side < 3; ++side) {
      const auto from = triangle[side];
      const auto to = triangle[(side + 1) % 3];
      const auto opposite = triangle[(side + 2) % 3];
      const std::pair<std::size_t, std::size_t> key = std::minmax(from, to);
      const auto inserted = edges.emplace(key, EdgeUse{i, from, to, opposite, 1});
      if (inserted.second)
        continue;
      auto& previous = inserted.first->second;
      if (previous.count != 1)
        throw std::invalid_argument("Boundary pair edge has more than two triangle owners");
      if (previous.from != to || previous.to != from)
        throw std::invalid_argument("Boundary pair shared edge has inconsistent orientation");
      if (previous.opposite == opposite)
        throw std::invalid_argument("Boundary pair has fewer than four distinct vertices");
      std::array<std::size_t, 4> cycle{previous.from, opposite, previous.to, previous.opposite};
      std::rotate(cycle.begin(), std::min_element(cycle.begin(), cycle.end()), cycle.end());
      result.push_back({previous.triangle, i, {key.first, key.second}, cycle});
      ++previous.count;
    }
  }
  return result;
}

} // namespace apmesh::quad
#endif
