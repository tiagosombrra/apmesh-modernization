#ifndef APMESH_RESEARCH_QUAD_INTERIOR_TEMPLATE_DISPATCH_H
#define APMESH_RESEARCH_QUAD_INTERIOR_TEMPLATE_DISPATCH_H

#include "quadtree_quad.h"

#include <array>
#include <cstddef>
#include <vector>

namespace apmesh::quad {

// This research selection is per Quadtree attempt, never per physical sheet.
// The existing application still rejects QUAD: this is not an AFT integration.
enum class InteriorTemplateMode { LegacyTri, ExperimentalQuad };

struct InteriorTemplateSelection {
  InteriorTemplateMode mode = InteriorTemplateMode::LegacyTri;
  UvMesh uv_quads;
  // One immutable source-cell/pattern origin for every emitted QUAD face.
  // Its order matches UvMesh::quads and the original leaf polygon order.
  std::vector<LeafPolygonOrigin> quad_face_origins;
  // Directed CCW QUAD-region edges. The TRI AFT does not yet consume them.
  std::vector<std::array<VertexId, 2>> quad_region_boundary;
  std::size_t legacy_tri_faces = 0;
  std::size_t source_leaves = 0;
  std::size_t excluded_boundary_leaves = 0;
  long double quad_region_area = 0;
  bool live_aft_interface_published = false;
  bool physical_elements_published = false;
};

// Selects at most one interior-template generator for one actual refined tree.
// LegacyTri invokes the unchanged Quadtree method. ExperimentalQuad creates
// an owned UV result without invoking or publishing any legacy TRI templates.
// Neither path modifies discretized model curves or physical patch boundaries.
// QUAD failure is nonpublishing and permits a corrected retry in this session.
class InteriorTemplateDispatcher final {
 public:
  explicit InteriorTemplateDispatcher(Par2DJMesh::AFT::Quadtree& tree) noexcept : tree_(tree) {}
  InteriorTemplateDispatcher(const InteriorTemplateDispatcher&) = delete;
  InteriorTemplateDispatcher& operator=(const InteriorTemplateDispatcher&) = delete;

  InteriorTemplateSelection Select(InteriorTemplateMode mode,
                                   const PolygonPointSelector& point_selector = {});

  bool HasSelected() const noexcept { return selected_; }

 private:
  Par2DJMesh::AFT::Quadtree& tree_;
  bool selected_ = false;
};

}  // namespace apmesh::quad

#endif  // APMESH_RESEARCH_QUAD_INTERIOR_TEMPLATE_DISPATCH_H
