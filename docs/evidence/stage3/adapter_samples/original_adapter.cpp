#include "adapter/curve_samples.h"
#include "data/curve/curve_adaptive_parametric.h"
#include "data/node_adaptive.h"
#include "crab_mesh/performer/id_manager.h"
namespace apmesh::adaptation {
std::list<PointAdaptive*> BuildCurveSamples(CurveAdaptive* curve, const std::list<PointAdaptive*>& points, const std::list<double>& parameters, std::map<PointAdaptive*, PointAdaptive*>& map_points, Performer::IdManager* id_manager) {
  static_cast<CurveAdaptiveParametric*>(curve)->UpdateParameters(parameters);

  list<PointAdaptive*> list_new_points;

  // IMPORTANT: Do not change IDs of original endpoints here.
  NodeAdaptive* point_front = static_cast<NodeAdaptive*>(points.front());
  NodeAdaptive* point_back = static_cast<NodeAdaptive*>(points.back());

  NodeAdaptive* new_front = nullptr;
  NodeAdaptive* new_back = nullptr;

  // Reuse or clone front.
  {
    auto it = map_points.find(point_front);
    if (it == map_points.end()) {
      new_front = new NodeAdaptive(*point_front);
      new_front->SetId(id_manager->next(0));
      map_points.emplace(point_front, new_front);
    } else {
      new_front = static_cast<NodeAdaptive*>(it->second);
    }
  }

  // Reuse or clone back.
  {
    auto it = map_points.find(point_back);
    if (it == map_points.end()) {
      new_back = new NodeAdaptive(*point_back);
      new_back->SetId(id_manager->next(0));
      map_points.emplace(point_back, new_back);
    } else {
      new_back = static_cast<NodeAdaptive*>(it->second);
    }
  }

  list_new_points.push_back(new_front);

  for (auto it = ++parameters.begin(); it != --parameters.end(); ++it) {
    NodeAdaptive* node = new NodeAdaptive(
        static_cast<CurveAdaptiveParametric*>(curve)->FindPointByParameter(*it));
    node->SetId(id_manager->next(0));
    list_new_points.push_back(node);
  }

  list_new_points.push_back(new_back);

  // Allow subsequent passes to hit the cache using the current endpoints too.
  map_points[new_front] = new_front;
  map_points[new_back] = new_back;

  return list_new_points;
}
}
