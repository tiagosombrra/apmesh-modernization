#include <unordered_set>
#include "data/geometry.h"
#include "data/curve/curve_adaptive.h"
namespace apmesh::generation {
class CurveSampleLifetime {
  Geometry* geometry;
public:
  explicit CurveSampleLifetime(Geometry& source) noexcept : geometry(&source) {}
  void Release() {
  std::unordered_set<PointAdaptive*> unique_points;
  for (unsigned int i = 0; i < geometry->GetNumberCurves(); ++i) {
    auto* curve = geometry->GetCurve(i);
    for (auto* p : curve->GetPoints()) {
      unique_points.insert(p);
    }
    curve->GetPoints().clear();
  }
  for (auto* p : unique_points) {
    delete p;
  }
  }
};
}
