#ifndef AP_MESH_PENDING_TEMPLATE_H
#define AP_MESH_PENDING_TEMPLATE_H

#include <memory>

#include "../../../include/crab_mesh/aft/edge.h"
#include "../../../include/crab_mesh/aft/face.h"

namespace apmesh::memory {
struct PendingEdgeDeleter {
  void operator()(Edge* edge) const noexcept {
    if (!edge)
      return;
    if (edge->getV1())
      edge->getV1()->removeAdjacentEdge(edge);
    if (edge->getV2())
      edge->getV2()->removeAdjacentEdge(edge);
    edge->DetachVertices();
    delete edge;
  }
};

using PendingEdge = std::unique_ptr<Edge, PendingEdgeDeleter>;

// Keep the original buffer/object allocation and registration order. Registered
// prefixes belong to Quadtree; only the unregistered suffixes are destroyed here.
class TemplateStorage {
public:
  TemplateStorage(int edge_count, int face_count, int vertex_count = 0)
      : edge_count_(edge_count), face_count_(face_count), vertex_count_(vertex_count),
        edges_(std::make_unique<Edge*[]>(edge_count)),
        faces_(std::make_unique<Face*[]>(face_count)),
        vertices_(vertex_count ? std::make_unique<Vertex*[]>(vertex_count)
                               : std::unique_ptr<Vertex*[]>{}) {}

  ~TemplateStorage() {
    for (int i = adopted_faces_; i < face_count_; ++i) {
      if (faces_[i]) {
        faces_[i]->DetachVertices();
        delete faces_[i];
      }
    }
    for (int i = adopted_edges_; i < edge_count_; ++i)
      PendingEdgeDeleter{}(edges_[i]);
    for (int i = adopted_vertices_; i < vertex_count_; ++i)
      delete vertices_[i];
    // Retain the successful path's original buffer destruction order too.
    edges_.reset();
    faces_.reset();
    vertices_.reset();
  }
  TemplateStorage(const TemplateStorage&) = delete;
  TemplateStorage& operator=(const TemplateStorage&) = delete;

  Edge** edges() const noexcept { return edges_.get(); }
  Face** faces() const noexcept { return faces_.get(); }
  Vertex** vertices() const noexcept { return vertices_.get(); }
  void AdoptedEdge() noexcept { ++adopted_edges_; }
  void AdoptedFace() noexcept { ++adopted_faces_; }
  void AdoptedVertex() noexcept { ++adopted_vertices_; }

private:
  int edge_count_;
  int face_count_;
  int vertex_count_;
  int adopted_edges_ = 0;
  int adopted_faces_ = 0;
  int adopted_vertices_ = 0;
  std::unique_ptr<Edge*[]> edges_;
  std::unique_ptr<Face*[]> faces_;
  std::unique_ptr<Vertex*[]> vertices_;
};
} // namespace apmesh::memory

#endif
