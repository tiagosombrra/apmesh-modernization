#include "interior_template_dispatch.h"

#include "crab_mesh/aft/quadtree.h"

#include <algorithm>
#include <map>
#include <stdexcept>
#include <utility>

namespace apmesh::quad {
namespace {

std::vector<std::array<VertexId, 2>> BoundaryOf(const UvMesh& mesh) {
  // QUAD edges inherit CCW orientation; a count-one edge bounds the region.
  using EdgeKey = std::pair<VertexId, VertexId>;
  struct EdgeUse {
    std::size_t count = 0;
    std::array<VertexId, 2> directed{};
  };
  std::map<EdgeKey, EdgeUse> uses;
  for (const auto& quad : mesh.quads) {
    for (std::size_t i = 0; i < quad.vertices.size(); ++i) {
      const VertexId a = quad.vertices[i];
      const VertexId b = quad.vertices[(i + 1) % quad.vertices.size()];
      auto& use = uses[std::minmax(a, b)];
      if (++use.count > 2) {
        throw std::invalid_argument("An experimental QUAD edge has more than two owners");
      }
      use.directed = {a, b};
    }
  }
  std::vector<std::array<VertexId, 2>> result;
  for (const auto& [key, use] : uses) {
    (void)key;
    if (use.count == 1) {
      result.push_back(use.directed);
    }
  }
  if (result.empty()) {
    throw std::invalid_argument("Experimental QUAD region has no directed interface");
  }
  return result;
}

}  // namespace

InteriorTemplateSelection InteriorTemplateDispatcher::Select(
    InteriorTemplateMode mode, const PolygonPointSelector& point_selector) {
  if (selected_) {
    throw std::invalid_argument("Interior template choice already committed for this attempt");
  }
  if (mode != InteriorTemplateMode::LegacyTri &&
      mode != InteriorTemplateMode::ExperimentalQuad) {
    throw std::invalid_argument("Unsupported interior template selection");
  }
  if (!tree_.GetTemplateFaces().empty() || !tree_.GetTemplateVertices().empty() ||
      !tree_.GetTemplateEdges().empty() || !tree_.GetFrontEdges().empty()) {
    throw std::invalid_argument("Interior templates are already published on this tree");
  }

  InteriorTemplateSelection result;
  result.mode = mode;
  result.source_leaves = tree_.GetLeafCount();
  if (mode == InteriorTemplateMode::LegacyTri) {
    if (point_selector) {
      throw std::invalid_argument("Legacy TRI templates must not receive a QUAD point rule");
    }
    // Call the unchanged TRI publication path exactly once.
    tree_.makeTemplateBasedMesh();
    result.legacy_tri_faces = tree_.GetTemplateFaces().size();
  } else {
    if (!point_selector) {
      throw std::invalid_argument("Research QUAD needs an explicit interior-point rule");
    }
    // Read the real refined tree before any legacy triangle publication.
    const auto captured = CaptureLeafPolygons(tree_);
    result.excluded_boundary_leaves = captured.excluded_boundary_leaves;
    result.quad_region_area = captured.interior_area;
    result.uv_quads = EmitLeafQuads(tree_, point_selector);
    result.quad_region_boundary = BoundaryOf(result.uv_quads);
    if (!tree_.GetTemplateFaces().empty() || !tree_.GetTemplateEdges().empty() ||
        !tree_.GetFrontEdges().empty()) {
      throw std::invalid_argument("Research QUAD would overlap published TRI templates");
    }
  }
  selected_ = true;
  return result;
}

}  // namespace apmesh::quad
