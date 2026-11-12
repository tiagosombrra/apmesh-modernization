#ifndef APMESH_RESEARCH_QUAD_OWNED_AFT_FRONT_H
#define APMESH_RESEARCH_QUAD_OWNED_AFT_FRONT_H

#include "front_interface_audit.h"
#include "crab_mesh/aft/advancing_front.h"

#include <cstddef>
#include <vector>

namespace apmesh::quad {

// R2b is a research-only active AFT front adapter, not a production mode.
// The supplied Quadtree must remain owned by AdvancingFront throughout the run.
// Only exterior TRI AFT edges are seeded; no interior TRI template faces exist.
struct OwnedAftFrontReport {
  std::size_t patch_boundary_edges = 0;
  std::size_t quad_interface_edges = 0;
  std::size_t distinct_quad_front_vertices = 0;
  std::size_t attached_exterior_cells = 0;
  std::size_t total_active_front_edges = 0;
  bool physical_quads_published = false;
  bool exterior_triangles_qualified = false;
};

// Derivation accesses the existing protected AFT front and owner lists without
// any modification to production AdvancingFront or Quadtree implementations.
// The legacy AFT class owns its Quadtree, boundary, new edges and new vertices.
class OwnedQuadAftFront final : public Par2DJMesh::AFT::AdvancingFront {
 public:
  OwnedQuadAftFront(Par2DJMesh::AFT::Boundary* boundary,
                    Par2DJMesh::AFT::Quadtree* tree);

  // Validate a disjoint, fully source-linked QUAD front; then seed AFT-owned
  // Vertex/Edge records with reversed winding and real exterior cell observers.
  // Only the first accepted call is permitted. Failed preflight leaves
  // protected AFT owner/front lists unchanged and allows a corrected retry.
  OwnedAftFrontReport Seed(const InteriorTemplateSelection& selected,
                           const std::vector<UvFrontSegment>& original_tri_front);

  bool IsSeeded() const noexcept { return seeded_; }
  const Par2DJMesh::Basics::EdgeList& ActiveFront() const noexcept { return front; }
  const Par2DJMesh::Basics::EdgeList& OwnedSeamEdges() const noexcept {
    return innerEdges;
  }
  const Par2DJMesh::Basics::VertexList& OwnedSeamVertices() const noexcept {
    return innerVertices;
  }
  const Par2DJMesh::Basics::FaceList& Triangles() const noexcept { return mesh; }

 private:
  bool seeded_ = false;
};

}  // namespace apmesh::quad

#endif  // APMESH_RESEARCH_QUAD_OWNED_AFT_FRONT_H
