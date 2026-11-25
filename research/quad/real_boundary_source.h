#ifndef APMESH_QUAD_REAL_BOUNDARY_SOURCE_H
#define APMESH_QUAD_REAL_BOUNDARY_SOURCE_H

#include "interior_template_dispatch.h"
#include <array>
#include <cstddef>
#include <memory>
#include <vector>

class PatchBezier;
namespace Par2DJMesh::AFT {
class Quadtree;
}

namespace apmesh::quad {
// Values survive the original generator's curve-sample retirement. No sampled
// node, AFT edge or QuadtreeCell pointer crosses that lifetime boundary.
struct RealBoundarySite {
  UvVertex uv;
  std::array<double, 3> xyz{};
  unsigned long source_id = 0;
  unsigned side = 0;
  double parameter = 0;
  std::array<double, 2> edge_mid{};
  double normalized_length = 0;
  double refined_length = -1;
};

struct RealSourceCell {
  std::array<double, 4> box{};
  unsigned long level = 0;
  std::array<std::size_t, 4> children{};
  bool subdivided = false;
  long source_id = 0;
};

struct OriginalCurveSample {
  double parameter = 0;
  std::array<double, 3> xyz{};
  unsigned long source_id = 0;
};

struct RealBoundarySource {
  std::array<std::vector<OriginalCurveSample>, 4> original_curves;
  std::array<bool, 4> reversed_curves{};
  std::vector<RealBoundarySite> sites;
  std::vector<RealSourceCell> cells;
  std::vector<long> leaf_order;
  long tree_counter = 0;
  double tree_factor = 0;
  long tree_cap = -1;
  double face_quality = 0;
  double low_quality_h = 0;
  double template_quality = 0;
  unsigned nonuniform_sides = 0;
  unsigned reversed_sides = 0;
  int source_step = -1;
  unsigned domain_generation = 0;
  bool reference_tri_accepted = false;
  std::size_t source_leaves = 0;
};

struct CertifiedBoundarySplit {
  std::size_t parent_interval;
  std::size_t inserted_site;
};

RealBoundarySource CaptureRealBoundary(PatchBezier& patch, Par2DJMesh::AFT::Quadtree& tree);
std::unique_ptr<Par2DJMesh::AFT::Quadtree> ReplayRealSourceTree(PatchBezier& patch,
                                                                const RealBoundarySource& source);
RealBoundarySource SplitFeedbackIntervals(PatchBezier& patch, const RealBoundarySource& source,
                                          const std::vector<bool>& split, unsigned long next_id);
void ValidateRealBoundary(PatchBezier& patch, const RealBoundarySource& source);
std::vector<CertifiedBoundarySplit> CertifyBoundaryRefinement(PatchBezier& patch,
                                                              const RealBoundarySource& parent,
                                                              const RealBoundarySource& candidate,
                                                              const std::vector<bool>& requested,
                                                              unsigned long last_parent_node_id);
} // namespace apmesh::quad
#endif
