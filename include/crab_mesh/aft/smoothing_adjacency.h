#ifndef AP_MESH_SMOOTHING_ADJACENCY_H
#define AP_MESH_SMOOTHING_ADJACENCY_H

#include <list>
#include <stdexcept>
#include <unordered_map>
#include <vector>

namespace Par2DJMesh {
namespace AFT {

// Non-owning incidence lists for a scope in which face endpoints and mesh order stay fixed.
// Coordinate updates remain live through the stored face observers.
template <typename VertexPointer, typename FaceList> class SmoothingFaceAdjacency {
public:
  using IncidenceList = std::vector<typename FaceList::value_type>;

  explicit SmoothingFaceAdjacency(const FaceList& faces) {
    // Count unique endpoints per entry before allocating each contiguous sequence.
    VisitIncidences(faces, [&](VertexPointer vertex, auto*) { ++faces_[vertex].count; });
    for (auto& entry : faces_)
      entry.second.faces.reserve(entry.second.count);
    VisitIncidences(
        faces, [&](VertexPointer vertex, auto* face) { faces_.at(vertex).faces.push_back(face); });
  }

  const IncidenceList& Find(VertexPointer vertex) const {
    const auto found = faces_.find(vertex);
    return found == faces_.end() ? empty_ : found->second.faces;
  }

private:
  struct Bucket {
    std::size_t count = 0;
    IncidenceList faces;
  };

  template <typename Visitor> static void VisitIncidences(const FaceList& faces, Visitor visit) {
    for (auto* face : faces) {
      const auto first = face->getV1();
      const auto second = face->getV2();
      const auto third = face->getV3();
      visit(first, face);
      if (second != first)
        visit(second, face);
      if (third != first && third != second)
        visit(third, face);
    }
  }

  std::unordered_map<VertexPointer, Bucket> faces_;
  const IncidenceList empty_;
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
