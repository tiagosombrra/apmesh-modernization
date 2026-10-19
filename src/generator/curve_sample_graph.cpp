#include "generator/curve_sample_graph.h"

#include "data/curve/curve_adaptive_parametric.h"
#include "data/geometry.h"

namespace apmesh::generation {
CurveSampleGraphTransaction::Entry::Entry(CurveAdaptive* source)
    : curve(source), points(source->GetPoints()),
      parameters(static_cast<CurveAdaptiveParametric*>(source)->parameters_) {}

CurveSampleGraphTransaction::CurveSampleGraphTransaction(Geometry* geometry) {
  entries_.reserve(geometry->GetNumberCurves());
  for (unsigned int i = 0; i < geometry->GetNumberCurves(); ++i) {
    auto* curve = geometry->GetCurve(i);
    entries_.emplace_back(curve);
    for (auto* point : curve->GetPoints())
      initial_samples_.insert(point);
  }
  // All potentially throwing preparation precedes parking original list nodes.
  for (auto& entry : entries_) {
    entry.points.swap(entry.curve->GetPoints());
    entry.parameters.swap(static_cast<CurveAdaptiveParametric*>(entry.curve)->parameters_);
  }
}

void CurveSampleGraphTransaction::DeleteNewSamples() noexcept {
  for (auto& entry : entries_) {
    for (auto* point : entry.curve->GetPoints()) {
      if (point == nullptr || initial_samples_.find(point) != initial_samples_.end())
        continue;
      // Inner per-curve transactions have already unwound. Only current live
      // graph lists are consumed here; erase every shared alias before deletion.
      for (auto& other : entries_)
        for (auto& observer : other.curve->GetPoints())
          if (observer == point)
            observer = nullptr;
      delete point;
    }
  }
}

CurveSampleGraphTransaction::~CurveSampleGraphTransaction() {
  if (committed_)
    return;
  cache_.clear();
  DeleteNewSamples();
  for (auto& entry : entries_) {
    entry.points.swap(entry.curve->GetPoints());
    entry.parameters.swap(static_cast<CurveAdaptiveParametric*>(entry.curve)->parameters_);
  }
}

void CurveSampleGraphTransaction::Commit() noexcept {
  cache_.clear();
  for (auto* point : initial_samples_)
    delete point;
  committed_ = true;
}
} // namespace apmesh::generation
