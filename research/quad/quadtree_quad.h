#ifndef APMESH_RESEARCH_QUAD_QUADTREE_QUAD_H
#define APMESH_RESEARCH_QUAD_QUADTREE_QUAD_H

#include "uv_mesh.h"

#include <functional>

namespace Par2DJMesh::AFT {
class Quadtree;
}

namespace apmesh::quad {

enum class LeafPattern { T1 = 1, T2, T3, T4, T5, T6 };

struct LeafPolygonOrigin {
  long cell_id;
  std::size_t leaf_ordinal;
  unsigned relative_depth;
  LeafPattern pattern;
  std::size_t polygon_ordinal;
};

struct LeafPolygonMesh {
  PolygonMesh input;
  std::vector<LeafPolygonOrigin> origins;
  std::size_t source_leaves = 0;
  std::size_t excluded_boundary_leaves = 0;
  long double interior_area = 0;
};

using PolygonPointSelector =
    std::function<UvVertex(const LeafPolygonOrigin&, const std::vector<UvVertex>&)>;

// Read the existing tree without sorting/refining/publishing legacy objects.
// Preserve getLeaves() order and the current empty-neighbor boundary exclusion.
// Canonical IDs come from the root's dyadic hierarchy, not coordinate welding.
// Require a consistent reciprocal 2:1 tree, at most 30 levels below the root,
// and at least one included leaf. Throws on malformed/unsupported input.
LeafPolygonMesh CaptureLeafPolygons(Par2DJMesh::AFT::Quadtree& tree);

// The selector supplies the scientific point rule; no centroid is chosen here.
// It receives only value metadata/coordinates and must not mutate the source.
// Current UvMesh validation requires the included region to be a single disk.
UvMesh EmitLeafQuads(Par2DJMesh::AFT::Quadtree& tree, const PolygonPointSelector& selector,
                     long double relative_tolerance = 1.0e-12L);

} // namespace apmesh::quad

#endif
