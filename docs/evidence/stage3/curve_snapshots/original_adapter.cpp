#include "generator/curve_snapshots.h"
#include <list>
#include <unordered_map>
#include <unordered_set>
#include "data/geometry.h"
#include "data/curve/curve_adaptive.h"
#include "data/node_adaptive.h"
namespace apmesh::generation {
CurveSnapshots CaptureCurveSnapshots(Geometry* geometry) {
    std::vector<std::vector<CurvePointSnapshot>> snapshots;
    if (!geometry) {
      return snapshots;
    }
    snapshots.resize(geometry->GetNumberCurves());
    for (unsigned int curve_index = 0; curve_index < geometry->GetNumberCurves();
         ++curve_index) {
      for (PointAdaptive* point : geometry->GetCurve(curve_index)->GetPoints()) {
        snapshots[curve_index].push_back(
            {point->GetId(), point->GetX(), point->GetY(), point->GetZ()});
      }
    }
    return snapshots;
  }
void RestoreCurveSnapshots(Geometry* geometry, const CurveSnapshots& snapshots) {
    if (!geometry || snapshots.size() != geometry->GetNumberCurves()) {
      return;
    }

    std::unordered_set<PointAdaptive*> unique_points;
    for (unsigned int curve_index = 0; curve_index < geometry->GetNumberCurves();
         ++curve_index) {
      for (PointAdaptive* point : geometry->GetCurve(curve_index)->GetPoints()) {
        unique_points.insert(point);
      }
    }
    for (PointAdaptive* point : unique_points) {
      delete point;
    }

    std::unordered_map<unsigned long, PointAdaptive*> point_by_id;
    for (unsigned int curve_index = 0; curve_index < geometry->GetNumberCurves();
         ++curve_index) {
      std::list<PointAdaptive*> restored_points;
      for (const CurvePointSnapshot& point : snapshots[curve_index]) {
        PointAdaptive* restored = nullptr;
        auto it = point_by_id.find(point.id);
        if (it != point_by_id.end()) {
          restored = it->second;
        } else {
          restored = new NodeAdaptive(point.x, point.y, point.z, point.id);
          point_by_id[point.id] = restored;
        }
        restored_points.push_back(restored);
      }
      geometry->GetCurve(curve_index)->SetPoints(std::move(restored_points));
    }
  }
}
