#include <map>
#include <unordered_set>
#include "data/geometry.h"
#include "data/curve/curve_adaptive.h"
namespace apmesh::generation {
class CurveSampleGraphTransaction {
public:
 explicit CurveSampleGraphTransaction(Geometry* geometry) {
  // Capture all current curve points to delete after we swap to new ones.
  for (unsigned int i = 0; i < geometry->GetNumberCurves(); ++i) {
    for (auto* p : geometry->GetCurve(i)->GetPoints()) {
      old_points.insert(p);
    }
  }


 }
 std::map<PointAdaptive*,PointAdaptive*>& Cache() noexcept {return map_points;}
 void Commit() noexcept {
  // Delete old discretization points (shared endpoints handled by set).
  for (auto* p : old_points) {
    delete p;
  }
 }
private:
 std::map<PointAdaptive*,PointAdaptive*> map_points;
 std::unordered_set<PointAdaptive*> old_points;
};
}
