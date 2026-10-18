#ifndef APMESH_GENERATOR_CURVE_REBUILD_H
#define APMESH_GENERATOR_CURVE_REBUILD_H

#include <list>

class CurveAdaptive;
class PointAdaptive;
namespace Performer {
class IdManager;
}

namespace apmesh::generation {
/// Rebuild the supplied points and the initialized parametric curve's parameters.
/// Removable interior samples must be distinct and exclusively deletable here.
/// Shared endpoints survive; successful removal invalidates external observers.
/// Failure preserves both lists and samples, but consumed IDs remain consumed.
/// The curve's point observers and later Generator publication are not committed here.
void RebuildCurveWithTarget(CurveAdaptive* curve, std::list<PointAdaptive*>& points,
                            int target_count, Performer::IdManager* id_manager);
} // namespace apmesh::generation

#endif
