#ifndef APMESH_RESEARCH_QUAD_SOURCE_TREE_REPLAY_H
#define APMESH_RESEARCH_QUAD_SOURCE_TREE_REPLAY_H

#include "adapter_capture.h"
#include "crab_mesh/aft/quadtree.h"

#include <cstddef>
#include <memory>

namespace apmesh::quad {

// The source Quadtree and original Adapter stay borrowed and immutable.
// This research witness owns its independent Boundary and native Quadtree.
struct NativeSourceTreeReplay {
  std::unique_ptr<Par2DJMesh::AFT::Quadtree> owned_tree;
  std::size_t source_boundary_segments = 0;
  std::size_t replayed_source_vertices = 0;
  std::size_t original_leaves = 0;
  std::size_t replayed_leaves = 0;
  std::size_t matched_leaf_neighbors = 0;
  std::size_t max_source_depth = 0;
};

// Replay the ACTUAL existing serial Adapter chart boundary and the complete
// refined 2:1 Quadtree hierarchy into new owners, with no shared live vertex,
// edge, cell, face or curve objects. Original source leaf-list order and cell
// IDs need not match: dyadic bounds, depth, neighboring boxes and directed
// boundary geometry MUST match exactly. Aborts before exposing candidate data.
// This is structural source reconstruction, not a physical QUAD mesh commit.
NativeSourceTreeReplay ReplayNativeSourceTree(
    Par2DJMesh::AFT::Quadtree& original,
    const AdapterBoundaryCapture& source);

}  // namespace apmesh::quad

#endif  // APMESH_RESEARCH_QUAD_SOURCE_TREE_REPLAY_H
