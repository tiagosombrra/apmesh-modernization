#ifndef APMESH_QUAD_MIXED_FEEDBACK_GRAPH_H
#define APMESH_QUAD_MIXED_FEEDBACK_GRAPH_H

#include <algorithm>
#include <cstddef>
#include <map>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>

namespace apmesh::quad {

using FeedbackEdge = std::pair<std::size_t, std::size_t>;

// Graph IDs are the input face indices followed by the ordered source intervals.
struct MixedFeedbackGraph {
  std::vector<std::vector<std::size_t>> neighbors;
  std::vector<std::size_t> interval_faces;
};

// Build an owned graph from the previous typed mesh. The input contour uses
// that mesh's node indices and the original source traversal.
inline MixedFeedbackGraph
BuildMixedFeedbackGraph(std::size_t node_count, const std::vector<std::vector<std::size_t>>& faces,
                        const std::vector<FeedbackEdge>& intervals) {
  if (node_count < 3 || faces.empty() || intervals.size() < 3)
    throw std::invalid_argument("Incomplete mixed feedback topology");

  struct EdgeIncidence {
    FeedbackEdge direction;
    std::size_t face;
    bool paired = false;
  };
  std::map<FeedbackEdge, EdgeIncidence> edges;
  MixedFeedbackGraph result;
  result.neighbors.resize(faces.size() + intervals.size());
  result.interval_faces.reserve(intervals.size());
  const auto connect = [&](std::size_t a, std::size_t b) {
    result.neighbors[a].push_back(b);
    result.neighbors[b].push_back(a);
  };
  bool has_triangle = false;
  bool has_quad = false;
  for (std::size_t f = 0; f < faces.size(); ++f) {
    const auto& face = faces[f];
    if ((face.size() != 3 && face.size() != 4) ||
        std::set<std::size_t>(face.begin(), face.end()).size() != face.size() ||
        std::any_of(face.begin(), face.end(), [node_count](auto v) { return v >= node_count; }))
      throw std::invalid_argument("Invalid mixed feedback face");
    has_triangle |= face.size() == 3;
    has_quad |= face.size() == 4;
    for (std::size_t k = 0; k < face.size(); ++k) {
      const FeedbackEdge edge{face[k], face[(k + 1) % face.size()]};
      auto [entry, inserted] =
          edges.emplace(std::minmax(edge.first, edge.second), EdgeIncidence{edge, f});
      if (inserted)
        continue;
      auto& other = entry->second;
      if (other.paired || other.direction != FeedbackEdge{edge.second, edge.first})
        throw std::invalid_argument("Nonmanifold or inconsistently oriented mixed feedback edge");
      other.paired = true;
      connect(other.face, f);
    }
  }
  if (!has_triangle || !has_quad)
    throw std::invalid_argument("Mixed feedback requires both TRI and QUAD faces");

  std::set<std::size_t> contour_starts;
  for (std::size_t i = 0; i < intervals.size(); ++i) {
    const auto edge = intervals[i];
    const auto next = (i + 1) % intervals.size();
    const auto entry = edges.find(std::minmax(edge.first, edge.second));
    if (!contour_starts.insert(edge.first).second || edge.second != intervals[next].first ||
        entry == edges.end() || entry->second.paired || entry->second.direction != edge)
      throw std::invalid_argument("Invalid original contour interval for mixed feedback");
    result.interval_faces.push_back(entry->second.face);
    connect(faces.size() + i, entry->second.face);
    connect(faces.size() + i, faces.size() + next);
  }
  const auto boundary_count = std::count_if(edges.begin(), edges.end(),
                                            [](const auto& edge) { return !edge.second.paired; });
  if (static_cast<std::size_t>(boundary_count) != intervals.size())
    throw std::invalid_argument("Mixed feedback did not account for every contour edge");

  for (auto& ids : result.neighbors) {
    std::sort(ids.begin(), ids.end());
    ids.erase(std::unique(ids.begin(), ids.end()), ids.end());
  }
  return result;
}

} // namespace apmesh::quad

#endif
