#ifndef APMESH_RESEARCH_QUAD_EXPERIMENTAL_POINT_RULE_H
#define APMESH_RESEARCH_QUAD_EXPERIMENTAL_POINT_RULE_H

#include "uv_mesh.h"

#include <vector>

namespace apmesh::quad {

// Competing research witnesses only. Neither value certifies the 1993 rule.
// No implicit/default rule: a scientific caller must choose explicitly.
enum class ExperimentalPointRule { VertexArithmeticMean, PolygonAreaCentroid };

// Strictly convex, CCW polygons only. Input is untouched.
// Reject malformed, nonfinite, degenerate and near-boundary configurations.
// This is intentionally not installed by the production Adapter/CLI.
UvVertex ExperimentalInteriorPoint(const std::vector<UvVertex>& polygon,
                                   ExperimentalPointRule rule,
                                   long double relative_tolerance = 1.0e-12L);

} // namespace apmesh::quad

#endif
