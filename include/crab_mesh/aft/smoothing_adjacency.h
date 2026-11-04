#ifndef AP_MESH_SMOOTHING_ADJACENCY_H
#define AP_MESH_SMOOTHING_ADJACENCY_H

#include <list>
#include <stdexcept>
#include <unordered_map>

namespace Par2DJMesh {
namespace AFT {

// Non-owning incidence lists for a scope in which face endpoints and mesh order stay fixed.
// Coordinate updates remain live through the stored face observers.
template <typename VertexPointer, typename FaceList> class SmoothingFaceAdjacency {
public:
  explicit SmoothingFaceAdjacency(const FaceList& faces) {
    for (auto* face : faces) {
      const auto first = face->getV1();
      const auto second = face->getV2();
      const auto third = face->getV3();
      faces_[first].push_back(face);
      if (second != first)
        faces_[second].push_back(face);
      if (third != first && third != second)
        faces_[third].push_back(face);
    }
  }

  const FaceList& Find(VertexPointer vertex) const {
    const auto found = faces_.find(vertex);
    return found == faces_.end() ? empty_ : found->second;
  }

private:
  std::unordered_map<VertexPointer, FaceList> faces_;
  const FaceList empty_;
};

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
