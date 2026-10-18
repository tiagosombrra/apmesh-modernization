#ifndef APMESH_ADAPTER_CURVE_SAMPLES_H
#define APMESH_ADAPTER_CURVE_SAMPLES_H

#include <list>
#include <map>

class CurveAdaptive;
class PointAdaptive;
namespace Performer {
class IdManager;
}

namespace apmesh::adaptation {
/// Build samples from the serial adapter's captured points and selected parameters.
/// Initialized parametric curves, NodeAdaptive endpoints/cache values, a live ID
/// manager and at least two captured points/parameters are required.
/// Input/cache samples remain borrowed. On success the caller must delete unique
/// newly created result nodes under the existing collective sample lifetime policy.
/// Failure preserves parameters, cache entries and borrowed samples; IDs consumed
/// and evaluator scratch state are not rolled back. Curve point lists are not published.
std::list<PointAdaptive*> BuildCurveSamples(CurveAdaptive* curve,
                                            const std::list<PointAdaptive*>& points,
                                            const std::list<double>& parameters,
                                            std::map<PointAdaptive*, PointAdaptive*>& map_points,
                                            Performer::IdManager* id_manager);
} // namespace apmesh::adaptation

#endif
