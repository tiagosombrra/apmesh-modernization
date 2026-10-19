#include "generator/curve_publication.h"

#include <algorithm>

#include "data/curve/curve_adaptive_parametric.h"

namespace apmesh::generation::detail {
CurveSampleTransaction::CurveSampleTransaction(CurveAdaptive* curve,
                                               std::map<PointAdaptive*, PointAdaptive*>& cache)
    : curve_(curve), cache_(cache), original_points_(curve->GetPoints()),
      original_parameters_(static_cast<CurveAdaptiveParametric*>(curve)->parameters_),
      original_cache_(cache) {
  // All allocation precedes mutation. Park the actual original list nodes;
  // serial passes operate on equivalent prepared observer/parameter lists.
  original_points_.swap(curve_->GetPoints());
  original_parameters_.swap(static_cast<CurveAdaptiveParametric*>(curve_)->parameters_);
}

bool CurveSampleTransaction::IsBorrowed(PointAdaptive* point) const noexcept {
  if (std::find(original_points_.begin(), original_points_.end(), point) != original_points_.end())
    return true;
  return std::any_of(original_cache_.begin(), original_cache_.end(),
                     [point](const auto& entry) { return entry.second == point; });
}

void CurveSampleTransaction::DeletePending(bool preserve_surface) noexcept {
  const auto clear_aliases = [](std::list<PointAdaptive*>& points, PointAdaptive* removed) {
    for (auto& point : points)
      if (point == removed)
        point = nullptr;
  };
  const auto dispose = [&](std::list<PointAdaptive*>& points) {
    for (auto* point : points) {
      if (point == nullptr || IsBorrowed(point))
        continue;
      if (preserve_surface && std::find(surface_samples_.begin(), surface_samples_.end(), point) !=
                                  surface_samples_.end())
        continue;
      // Remove every pending alias before deletion; no allocation or access to
      // discarded curve observers (which rebuild may already have invalidated).
      clear_aliases(curve_samples_, point);
      clear_aliases(surface_samples_, point);
      delete point;
    }
  };
  dispose(curve_samples_);
  if (!preserve_surface)
    dispose(surface_samples_);
}

CurveSampleTransaction::~CurveSampleTransaction() {
  if (committed_)
    return;
  // Qualified passes insert keys or overwrite values, never erase entry keys.
  // Erase only new keys and restore values in place, retaining original nodes.
  for (auto entry = cache_.begin(); entry != cache_.end();) {
    const auto original = original_cache_.find(entry->first);
    if (original == original_cache_.end())
      entry = cache_.erase(entry);
    else {
      entry->second = original->second;
      ++entry;
    }
  }
  DeletePending(false);
  original_points_.swap(curve_->GetPoints());
  original_parameters_.swap(static_cast<CurveAdaptiveParametric*>(curve_)->parameters_);
}

void CurveSampleTransaction::Commit() noexcept {
  DeletePending(true);
  committed_ = true;
}
} // namespace apmesh::generation::detail
