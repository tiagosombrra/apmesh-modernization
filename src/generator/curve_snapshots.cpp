#include "generator/curve_snapshots.h"

#include <list>
#include <memory>
#include <unordered_map>
#include <unordered_set>

#include "data/curve/curve_adaptive.h"
#include "data/geometry.h"
#include "data/node_adaptive.h"

namespace apmesh::generation {
CurveSnapshots CaptureCurveSnapshots(Geometry* geometry) {
  CurveSnapshots snapshots;
  if (geometry == nullptr)
    return snapshots;
  snapshots.resize(geometry->GetNumberCurves());
  for (unsigned int i = 0; i < geometry->GetNumberCurves(); ++i)
    for (PointAdaptive* point : geometry->GetCurve(i)->GetPoints())
      snapshots[i].push_back({point->GetId(), point->GetX(), point->GetY(), point->GetZ()});
  return snapshots;
}

void RestoreCurveSnapshots(Geometry* geometry, const CurveSnapshots& snapshots) {
  if (geometry == nullptr || snapshots.size() != geometry->GetNumberCurves())
    return;

  std::unordered_set<PointAdaptive*> old_points;
  for (unsigned int i = 0; i < geometry->GetNumberCurves(); ++i)
    for (PointAdaptive* point : geometry->GetCurve(i)->GetPoints())
      old_points.insert(point);

  std::unordered_map<unsigned long, std::unique_ptr<NodeAdaptive>> point_by_id;
  std::vector<std::list<PointAdaptive*>> restored_points(snapshots.size());
  for (unsigned int i = 0; i < geometry->GetNumberCurves(); ++i) {
    for (const CurvePointSnapshot& point : snapshots[i]) {
      auto it = point_by_id.find(point.id);
      if (it == point_by_id.end())
        it = point_by_id
                 .emplace(point.id,
                          std::make_unique<NodeAdaptive>(point.x, point.y, point.z, point.id))
                 .first;
      restored_points[i].push_back(it->second.get());
    }
  }

  // Swap the existing lists directly: a by-value SetPoints call can allocate
  // during argument construction on some standard-library implementations.
  for (unsigned int i = 0; i < geometry->GetNumberCurves(); ++i)
    geometry->GetCurve(i)->GetPoints().swap(restored_points[i]);
  for (auto& entry : point_by_id)
    entry.second.release();
  for (PointAdaptive* point : old_points)
    delete point;
}
} // namespace apmesh::generation
