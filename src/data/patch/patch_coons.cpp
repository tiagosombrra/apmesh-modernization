#include "data/patch/patch_coons.h"

#include <algorithm>

#include "data/curve/curve_adaptive.h"

PatchCoons::PatchCoons() = default;

PatchCoons::PatchCoons(PatchCoons* patch_coons) : Patch(patch_coons) {}

PatchCoons::PatchCoons(const std::vector<CurveAdaptive*>& curves) : curves_(curves) {}

PatchCoons::~PatchCoons() = default;

void PatchCoons::InsertCurve(CurveAdaptive* curve) { curves_.push_back(curve); }

void PatchCoons::ReplaceCurve(unsigned int position, CurveAdaptive* curve) {
  if (position >= curves_.size() || curves_[position] == curve)
    return;
  CurveAdaptive* previous = curves_[position];
  curves_[position] = curve;
  // Destination publication remains caller-managed. Retire old observers only
  // after the last current incidence leaves their live borrowed curve.
  if (previous != nullptr && std::find(curves_.begin(), curves_.end(), previous) == curves_.end())
    previous->RemovePatchObservers(this);
}

unsigned int PatchCoons::GetNumBerCurves() const noexcept {
  return static_cast<unsigned int>(curves_.size());
}

CurveAdaptive* PatchCoons::GetCurve(unsigned int position) noexcept {
  return (position < curves_.size()) ? curves_[position] : nullptr;
}

const CurveAdaptive* PatchCoons::GetCurve(unsigned int position) const noexcept {
  return (position < curves_.size()) ? curves_[position] : nullptr;
}
