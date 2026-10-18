#include "generator/curve_synchronization.h"

#include <vector>

#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/curve/curve_adaptive_parametric_hermite.h"
#include "data/geometry.h"
#include "data/patch/patch_coons.h"

namespace apmesh::generation {
std::unique_ptr<CurveAdaptive> CloneCurveForPatch(const CurveAdaptive* curve, Patch* patch) {
  if (curve == nullptr)
    return nullptr;
  std::unique_ptr<CurveAdaptive> clone;
  if (const auto* bezier = dynamic_cast<const CurveAdaptiveParametricBezier*>(curve))
    clone = std::make_unique<CurveAdaptiveParametricBezier>(
        const_cast<CurveAdaptiveParametricBezier*>(bezier));
  else if (const auto* hermite = dynamic_cast<const CurveAdaptiveParametricHermite*>(curve))
    clone = std::make_unique<CurveAdaptiveParametricHermite>(
        const_cast<CurveAdaptiveParametricHermite*>(hermite));
  else if (const auto* parametric = dynamic_cast<const CurveAdaptiveParametric*>(curve))
    clone =
        std::make_unique<CurveAdaptiveParametric>(const_cast<CurveAdaptiveParametric*>(parametric));
  else
    clone = std::make_unique<CurveAdaptive>(const_cast<CurveAdaptive*>(curve));
  clone->ClearPatches();
  if (patch != nullptr)
    clone->InsertPatch(patch);
  return clone;
}

void DisableSharedCurveSynchronization(Geometry* geometry) {
  if (geometry == nullptr)
    return;
  for (unsigned int curve_index = 0; curve_index < geometry->GetNumberCurves(); ++curve_index) {
    CurveAdaptive* curve = geometry->GetCurve(curve_index);
    if (curve == nullptr || curve->GetNumBerPatches() <= 1U)
      continue;

    std::vector<Patch*> incident_patches;
    incident_patches.reserve(curve->GetNumBerPatches());
    for (unsigned int i = 0; i < curve->GetNumBerPatches(); ++i)
      if (Patch* patch = curve->GetPatch(i))
        incident_patches.push_back(patch);
    if (incident_patches.size() <= 1U)
      continue;

    std::vector<std::unique_ptr<CurveAdaptive>> pending;
    pending.reserve(incident_patches.size() - 1);
    for (std::size_t i = 1; i < incident_patches.size(); ++i)
      if (auto* patch = dynamic_cast<PatchCoons*>(incident_patches[i]))
        pending.push_back(CloneCurveForPatch(curve, patch));

    unsigned int next_clone = geometry->GetNumberCurves();
    geometry->InsertCurves(std::move(pending));
    // The source already has capacity for multiple incidences. Clearing and
    // reinserting one pointer cannot allocate; patch replacement only assigns.
    curve->ClearPatches();
    curve->InsertPatch(incident_patches.front());
    for (std::size_t i = 0; i < incident_patches.size(); ++i) {
      auto* patch = dynamic_cast<PatchCoons*>(incident_patches[i]);
      if (patch == nullptr)
        continue;
      CurveAdaptive* replacement = i == 0 ? curve : geometry->GetCurve(next_clone++);
      for (unsigned int e = 0; e < patch->GetNumBerCurves(); ++e)
        if (patch->GetCurve(e) == curve)
          patch->ReplaceCurve(e, replacement);
    }
  }
}
} // namespace apmesh::generation
