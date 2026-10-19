#include <list>
#include <map>
#include <vector>
#include <unordered_set>
#include "data/curve/curve_adaptive.h"
#include "generator/curve_rebuild.h"
namespace apmesh::generation {
template <class CurvePass, class SurfacePass>
void RefineCurveSamples(CurveAdaptive* curve, std::map<PointAdaptive*, PointAdaptive*>&,
 CurvePass&& curve_pass, SurfacePass&& surface_pass, bool rebuild, int target_count,
 Performer::IdManager* id_manager) {
 std::vector<std::list<PointAdaptive*>> new_points(1);
    auto curve_refined = curve_pass();
    curve->SetPoints(curve_refined);

    auto surface_refined = surface_pass();
    curve->SetPoints(surface_refined);
    if (rebuild) {
      RebuildCurveWithTarget(curve, surface_refined, target_count, id_manager);
      curve->SetPoints(surface_refined);
    }

    std::unordered_set<PointAdaptive*> keep(surface_refined.begin(),
                                            surface_refined.end());
    for (auto* p : curve_refined) {
      if (keep.find(p) == keep.end()) {
        delete p;
      }
    }

    new_points[0] = std::move(surface_refined);
}
}
