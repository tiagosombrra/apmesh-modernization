#include "estimate/triangle_count_estimate.h"

#include <array>
#include <memory>

#include "data/curve/curve_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "data/patch/patch_bezier.h"
#include "estimate/initial_mesh_estimate.h"

namespace apmesh::estimation {
namespace {
class TriangleCountScope {
public:
  explicit TriangleCountScope(PatchBezier& patch) noexcept
      : patch_(patch), previous_mesh_(patch.GetSubMesh()) {
    for (unsigned int slot = 0; slot < curves_.size(); ++slot) {
      curves_[slot] = patch.GetCurve(slot);
      owns_samples_[slot] = curves_[slot]->GetPoints().empty();
    }
  }

  ~TriangleCountScope() noexcept {
    patch_.SetSubMesh(previous_mesh_);
    for (unsigned int slot = 0; slot < curves_.size(); ++slot) {
      if (!owns_samples_[slot])
        continue;
      auto* curve = curves_[slot];
      for (auto* point : curve->GetPoints()) {
        if (point == nullptr)
          continue;
        // The constructor publishes fresh samples only in these captured lists.
        // Clear every alias before deleting a shared corner once, without allocation.
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

  TriangleCountScope(const TriangleCountScope&) = delete;
  TriangleCountScope& operator=(const TriangleCountScope&) = delete;
  TriangleCountScope(TriangleCountScope&&) = delete;
  TriangleCountScope& operator=(TriangleCountScope&&) = delete;

private:
  PatchBezier& patch_;
  SubMesh* previous_mesh_;
  std::array<CurveAdaptive*, 4> curves_{};
  std::array<bool, 4> owns_samples_{};
};
} // namespace

long CountEstimateTriangles(PatchBezier* patch, int degree) {
  std::unique_ptr<SubMesh> mesh;
  // Restore the patch and retire fresh samples before releasing the physical
  // mesh; its nodes are independent copies, not owners of curve sample objects.
  TriangleCountScope scope(*patch);
  mesh = BuildInitialEstimateSubMesh(patch, degree);
  return mesh->GetNumberElements();
}
} // namespace apmesh::estimation
