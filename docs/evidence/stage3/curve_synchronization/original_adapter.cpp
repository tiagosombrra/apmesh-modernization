#include "generator/curve_synchronization.h"
#include "data/geometry.h"
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/curve/curve_adaptive_parametric_hermite.h"
#include "data/patch/patch_coons.h"
namespace {
CurveAdaptive* CloneCurveForPatch(const CurveAdaptive* curve, Patch* patch) {
  if (curve == nullptr) {
    return nullptr;
  }
  CurveAdaptive* clone = nullptr;
  if (const auto* bezier =
          dynamic_cast<const CurveAdaptiveParametricBezier*>(curve)) {
    clone = new CurveAdaptiveParametricBezier(
        const_cast<CurveAdaptiveParametricBezier*>(bezier));
  } else if (const auto* hermite =
                 dynamic_cast<const CurveAdaptiveParametricHermite*>(curve)) {
    clone = new CurveAdaptiveParametricHermite(
        const_cast<CurveAdaptiveParametricHermite*>(hermite));
  } else if (const auto* parametric =
                 dynamic_cast<const CurveAdaptiveParametric*>(curve)) {
    clone = new CurveAdaptiveParametric(
        const_cast<CurveAdaptiveParametric*>(parametric));
  } else {
    clone = new CurveAdaptive(const_cast<CurveAdaptive*>(curve));
  }
  clone->ClearPatches();
  if (patch != nullptr) {
    clone->InsertPatch(patch);
  }
  return clone;
}

void OriginalDisable(Geometry* geometry) {
  if (geometry == nullptr) {
    return;
  }

  for (unsigned int curve_index = 0; curve_index < geometry->GetNumberCurves();
       ++curve_index) {
    CurveAdaptive* curve = geometry->GetCurve(curve_index);
    if (curve == nullptr || curve->GetNumBerPatches() <= 1U) {
      continue;
    }

    std::vector<Patch*> incident_patches;
    incident_patches.reserve(curve->GetNumBerPatches());
    for (unsigned int patch_index = 0; patch_index < curve->GetNumBerPatches();
         ++patch_index) {
      Patch* patch = curve->GetPatch(patch_index);
      if (patch != nullptr) {
        incident_patches.push_back(patch);
      }
    }
    if (incident_patches.size() <= 1U) {
      continue;
    }

    curve->ClearPatches();
    curve->InsertPatch(incident_patches.front());

    for (size_t patch_pos = 0; patch_pos < incident_patches.size(); ++patch_pos) {
      PatchCoons* patch = dynamic_cast<PatchCoons*>(incident_patches[patch_pos]);
      if (patch == nullptr) {
        continue;
      }
      CurveAdaptive* replacement = curve;
      if (patch_pos > 0U) {
        replacement = CloneCurveForPatch(curve, patch);
        geometry->InsertCurve(replacement);
      }

      for (unsigned int edge_index = 0; edge_index < patch->GetNumBerCurves();
           ++edge_index) {
        if (patch->GetCurve(edge_index) == curve) {
          patch->ReplaceCurve(edge_index, replacement);
        }
      }
    }
  }
}

}
namespace apmesh::generation {
std::unique_ptr<CurveAdaptive> CloneCurveForPatch(const CurveAdaptive* curve, Patch* patch) {
  return std::unique_ptr<CurveAdaptive>(::CloneCurveForPatch(curve, patch));
}
void DisableSharedCurveSynchronization(Geometry* geometry) { OriginalDisable(geometry); }
}
