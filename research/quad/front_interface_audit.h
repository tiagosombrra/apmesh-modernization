#ifndef APMESH_RESEARCH_QUAD_FRONT_INTERFACE_AUDIT_H
#define APMESH_RESEARCH_QUAD_FRONT_INTERFACE_AUDIT_H

#include "interior_template_dispatch.h"

#include <array>
#include <cstddef>
#include <vector>

namespace Par2DJMesh::AFT {
class Quadtree;
}

namespace apmesh::quad {

// Value-only, directed UV geometry. Never owns AFT vertices or edges.
struct UvFrontSegment {
  UvVertex first;
  UvVertex second;
};

struct FrontInterfaceAudit {
  std::size_t legacy_segments = 0;
  std::size_t quad_segments = 0;
  std::size_t original_unsplit_segments = 0;
  std::size_t original_split_segments = 0;
  std::size_t new_split_points = 0;
  std::size_t max_parts_per_legacy_segment = 0;
  long double legacy_total_length = 0;
  long double quad_total_length = 0;
  bool opposite_winding = false;
  bool complete_coverage = false;
};

// Read original, fully published TRI-template AFT front into immutable UV
// values. The source Quadtree and its ownership remain entirely unchanged.
std::vector<UvFrontSegment> SnapshotLegacyFront(
    const Par2DJMesh::AFT::Quadtree& legacy_tree);

// Compare exact axis-aligned source geometry on the same refined tree.
// One original front edge must be tiled by one or more QUAD front edges.
// QUAD face CCW winding is reversed relative to the exterior TRI AFT.
// This is a research-only geometric audit, NOT a physical AFT publication.
// Fail closed on gaps, overlaps, missing/extra edges, duplicates,
// orientation mismatch, diagonal/degenerate/nonfinite segments or
// inconsistent QUAD face incidence and directed front ownership.
FrontInterfaceAudit CompareLegacyAndQuadFront(
    const std::vector<UvFrontSegment>& legacy_front, const UvMesh& quad_mesh,
    const std::vector<std::array<VertexId, 2>>& quad_region_boundary);

}  // namespace apmesh::quad

#endif  // APMESH_RESEARCH_QUAD_FRONT_INTERFACE_AUDIT_H
