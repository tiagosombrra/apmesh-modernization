#include "estimate/estimate_mesh_scope.h"

#include "data/curve/curve_adaptive.h"
#include "data/patch/patch_bezier.h"

namespace apmesh::estimation::detail {
EstimateMeshScope::EstimateMeshScope(PatchBezier& patch) noexcept
    : patch_(patch), previous_mesh_(patch.GetSubMesh()) {
  for (unsigned int slot = 0; slot < curves_.size(); ++slot) {
    curves_[slot] = patch.GetCurve(slot);
    owns_samples_[slot] = curves_[slot]->GetPoints().empty();
  }
}

EstimateMeshScope::~EstimateMeshScope() noexcept {
  patch_.SetSubMesh(previous_mesh_);
  for (unsigned int slot = 0; slot < curves_.size(); ++slot) {
    if (!owns_samples_[slot])
      continue;
    auto* curve = curves_[slot];
    for (auto* point : curve->GetPoints()) {
      if (point == nullptr)
        continue;
      // Clear every owned alias before deleting a shared corner once.
      for (unsigned int other = 0; other < curves_.size(); ++other) {
        if (owns_samples_[other]) {
          for (auto& observer : curves_[other]->GetPoints())
            if (observer == point)
              observer = nullptr;
        }
      }
      delete point;
    }
    curve->GetPoints().clear();
  }
}
} // namespace apmesh::estimation::detail
