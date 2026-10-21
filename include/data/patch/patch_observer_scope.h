#ifndef DATA_PATCH_PATCH_OBSERVER_SCOPE_H
#define DATA_PATCH_PATCH_OBSERVER_SCOPE_H

#include <array>
#include <cstddef>

#include "../curve/curve_adaptive.h"

namespace apmesh::detail {
// Restore only exclusively appended patch observers. Curves and their existing
// prefix remain borrowed and must outlive this scope. No foreign publication
// or intermediate consumption of a pending patch is supported.
class PatchObserverScope {
public:
  explicit PatchObserverScope(std::array<CurveAdaptive*, 4> curves) noexcept : curves_(curves) {
    for (std::size_t index = 0; index < curves_.size(); ++index)
      counts_[index] = curves_[index]->GetNumBerPatches();
  }
  ~PatchObserverScope() {
    if (active_)
      for (std::size_t index = 0; index < curves_.size(); ++index)
        curves_[index]->TruncatePatchObservers(counts_[index]);
  }
  PatchObserverScope(const PatchObserverScope&) = delete;
  PatchObserverScope& operator=(const PatchObserverScope&) = delete;
  void Commit() noexcept { active_ = false; }

private:
  std::array<CurveAdaptive*, 4> curves_;
  std::array<unsigned int, 4> counts_{};
  bool active_ = true;
};
} // namespace apmesh::detail

#endif // DATA_PATCH_PATCH_OBSERVER_SCOPE_H
