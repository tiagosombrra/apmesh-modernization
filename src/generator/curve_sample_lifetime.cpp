#include "generator/curve_sample_lifetime.h"

#include "data/curve/curve_adaptive.h"
#include "data/geometry.h"

namespace apmesh::generation {
CurveSampleLifetime::~CurveSampleLifetime() noexcept { Release(); }

void CurveSampleLifetime::Release() noexcept {
  for (unsigned int i = 0; i < geometry_.GetNumberCurves(); ++i) {
    auto* curve = geometry_.GetCurve(i);
    if (curve == nullptr)
      continue;
    for (auto* point : curve->GetPoints()) {
      if (point == nullptr)
        continue;
      // Clear every live alias before deleting a shared object. Earlier lists
      // are already empty, so only the current and later curves remain.
      for (unsigned int j = i; j < geometry_.GetNumberCurves(); ++j) {
        auto* other = geometry_.GetCurve(j);
        if (other == nullptr)
          continue;
        for (auto& observer : other->GetPoints())
          if (observer == point)
            observer = nullptr;
      }
      delete point;
    }
    curve->GetPoints().clear();
  }
}
} // namespace apmesh::generation
