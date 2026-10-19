#ifndef APMESH_GENERATOR_CURVE_PUBLICATION_H
#define APMESH_GENERATOR_CURVE_PUBLICATION_H

#include <list>
#include <map>
#include <type_traits>

#include "data/curve/curve_adaptive.h"
#include "generator/curve_rebuild.h"

namespace apmesh::generation {
namespace detail {
// Owns newly returned samples collectively. Entry samples/cache values are
// borrowed, including endpoints already published by a preceding curve.
class CurveSampleTransaction {
public:
  CurveSampleTransaction(CurveAdaptive* curve, std::map<PointAdaptive*, PointAdaptive*>& cache);
  ~CurveSampleTransaction();
  CurveSampleTransaction(const CurveSampleTransaction&) = delete;
  CurveSampleTransaction& operator=(const CurveSampleTransaction&) = delete;

  std::list<PointAdaptive*>& CurveSamples() noexcept { return curve_samples_; }
  std::list<PointAdaptive*>& SurfaceSamples() noexcept { return surface_samples_; }
  void Commit() noexcept;

private:
  bool IsBorrowed(PointAdaptive* point) const noexcept;
  void DeletePending(bool preserve_surface) noexcept;

  CurveAdaptive* curve_;
  std::map<PointAdaptive*, PointAdaptive*>& cache_;
  std::list<PointAdaptive*> original_points_;
  std::list<double> original_parameters_;
  std::map<PointAdaptive*, PointAdaptive*> original_cache_;
  std::list<PointAdaptive*> curve_samples_;
  std::list<PointAdaptive*> surface_samples_;
  bool committed_ = false;
};
} // namespace detail

// Initialized parametric curves and the two serial Adapter passes only. Each
// pass returns caller-owned samples through the qualified construction tail;
// entry samples and cache values remain borrowed. Rebuild may delete distinct
// surface interiors. No caller may consume intermediate observers concurrently.
// Failure restores entry point/parameter nodes and cache entries, reclaiming new
// samples. Consumed IDs, evaluator scratch and earlier curves are not restored.
// Success invalidates old list observers and transfers final samples to the
// existing collectively owned graph. This is not a whole-AdaptCurve transaction.
template <class CurvePass, class SurfacePass>
void RefineCurveSamples(CurveAdaptive* curve, std::map<PointAdaptive*, PointAdaptive*>& cache,
                        CurvePass&& curve_pass, SurfacePass&& surface_pass, bool rebuild,
                        int target_count, Performer::IdManager* id_manager) {
  static_assert(std::is_nothrow_move_assignable_v<std::list<PointAdaptive*>>);
  detail::CurveSampleTransaction pending(curve, cache);
  pending.CurveSamples() = curve_pass();
  curve->SetPoints(pending.CurveSamples());
  pending.SurfaceSamples() = surface_pass();
  curve->SetPoints(pending.SurfaceSamples());
  if (rebuild) {
    RebuildCurveWithTarget(curve, pending.SurfaceSamples(), target_count, id_manager);
    curve->SetPoints(pending.SurfaceSamples());
  }
  pending.Commit();
}
} // namespace apmesh::generation
#endif
