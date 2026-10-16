#ifndef AP_MESH_SMOOTHING_ADJACENCY_H
#define AP_MESH_SMOOTHING_ADJACENCY_H

#include <list>
#include <stdexcept>

namespace Par2DJMesh {
namespace AFT {

// Edge IDs are assigned monotonically by the boundary, quadtree and front.
// Pointer-set iteration must not determine floating-point reduction order.
template <typename EdgeRange>
std::list<typename EdgeRange::value_type> orderedSmoothingAdjacency(const EdgeRange& edges) {
  std::list<typename EdgeRange::value_type> ordered(edges.begin(), edges.end());
  ordered.sort([](auto first, auto second) { return first->getId() < second->getId(); });
  typename EdgeRange::value_type previous = nullptr;
  for (auto edge : ordered) {
    if (previous != nullptr && previous->getId() == edge->getId()) {
      throw std::logic_error("Smoothing adjacency contains duplicate edge IDs");
    }
    previous = edge;
  }
  return ordered;
}

} // namespace AFT
} // namespace Par2DJMesh

#endif
