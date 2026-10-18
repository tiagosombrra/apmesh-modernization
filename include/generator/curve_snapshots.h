#ifndef APMESH_GENERATOR_CURVE_SNAPSHOTS_H
#define APMESH_GENERATOR_CURVE_SNAPSHOTS_H

#include <vector>

class Geometry;

namespace apmesh::generation {
struct CurvePointSnapshot {
  unsigned long id;
  double x;
  double y;
  double z;
};
using CurveSnapshots = std::vector<std::vector<CurvePointSnapshot>>;

/// Capture ordered ID/XYZ values without taking ownership or changing live curves.
CurveSnapshots CaptureCurveSnapshots(Geometry* geometry);
/// Restore by first-encounter ID reuse, preserving the existing success policy.
/// Current samples must be collectively exclusively owned/deletable through the curves.
/// Failure preserves all live samples/list nodes; success invalidates their observers.
/// Parameters, accepted meshes and their observers are not restored by this operation.
void RestoreCurveSnapshots(Geometry* geometry, const CurveSnapshots& snapshots);
} // namespace apmesh::generation

#endif
