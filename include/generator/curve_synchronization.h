#ifndef APMESH_GENERATOR_CURVE_SYNCHRONIZATION_H
#define APMESH_GENERATOR_CURVE_SYNCHRONIZATION_H

#include <memory>

class CurveAdaptive;
class Geometry;
class Patch;

namespace apmesh::generation {
/// Copy initialized curve values/containers; sample and patch objects remain borrowed.
/// Return an exclusive pending owner, or null for a null source.
std::unique_ptr<CurveAdaptive> CloneCurveForPatch(const CurveAdaptive* curve, Patch* patch);

/// Preserve the existing synchronization-disabled incidence policy.
/// Each original curve commits atomically. A later failure keeps the committed prefix;
/// the failing curve is unchanged and the entire operation can be retried.
void DisableSharedCurveSynchronization(Geometry* geometry);
} // namespace apmesh::generation

#endif
