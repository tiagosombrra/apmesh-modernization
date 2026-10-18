#include "generator/curve_rebuild.h"

#include <algorithm>
#include <cmath>
#include <memory>
#include <unordered_set>
#include <vector>

#include "crab_mesh/performer/id_manager.h"
#include "data/curve/curve_adaptive_parametric.h"
#include "data/node_adaptive.h"

namespace apmesh::generation {
void RebuildCurveWithTarget(CurveAdaptive* curve, std::list<PointAdaptive*>& points,
                            int target_count, Performer::IdManager* id_manager) {
  auto* param_curve = static_cast<CurveAdaptiveParametric*>(curve);
  std::vector<PointAdaptive*> point_vec(points.begin(), points.end());
  std::vector<double> param_vec(param_curve->parameters_.begin(), param_curve->parameters_.end());
  if (point_vec.size() < 2 || param_vec.size() != point_vec.size())
    return;
  const int capped_target = std::max(2, target_count);
  if (capped_target == static_cast<int>(point_vec.size()))
    return;
  if (capped_target > static_cast<int>(point_vec.size())) {
    std::list<PointAdaptive*> rebuilt_points;
    std::list<double> rebuilt_parameters;
    std::unordered_set<PointAdaptive*> keep_existing;
    std::vector<std::unique_ptr<NodeAdaptive>> pending;
    pending.reserve(static_cast<std::size_t>(capped_target - 2));
    for (int idx = 0; idx < capped_target; ++idx) {
      const double alpha = (capped_target <= 1)
                               ? 0.0
                               : static_cast<double>(idx) / static_cast<double>(capped_target - 1);
      const double t = (idx == 0) ? 0.0 : ((idx == capped_target - 1) ? 1.0 : alpha);
      if (idx == 0) {
        rebuilt_points.push_back(point_vec.front());
        keep_existing.insert(point_vec.front());
      } else if (idx == capped_target - 1) {
        rebuilt_points.push_back(point_vec.back());
        keep_existing.insert(point_vec.back());
      } else {
        const PointAdaptive point = param_curve->FindPointByParameter(t);
        unsigned long new_id = 0UL;
        if (id_manager != nullptr)
          new_id = id_manager->next();
        if (new_id > 0UL)
          pending.push_back(
              std::make_unique<NodeAdaptive>(point.GetX(), point.GetY(), point.GetZ(), new_id));
        else
          pending.push_back(
              std::make_unique<NodeAdaptive>(point.GetX(), point.GetY(), point.GetZ()));
        rebuilt_points.push_back(pending.back().get());
      }
      rebuilt_parameters.push_back(t);
    }
    param_curve->parameters_.swap(rebuilt_parameters);
    points.swap(rebuilt_points);
    for (auto& point : pending)
      point.release();
    for (PointAdaptive* existing_point : point_vec)
      if (keep_existing.find(existing_point) == keep_existing.end())
        delete existing_point;
    return;
  }
  std::vector<int> selected_indices;
  selected_indices.reserve(static_cast<std::size_t>(capped_target));
  selected_indices.push_back(0);
  for (int idx = 1; idx < capped_target - 1; ++idx) {
    const double alpha = static_cast<double>(idx) / static_cast<double>(capped_target - 1);
    const int selected =
        static_cast<int>(std::round(alpha * static_cast<double>(point_vec.size() - 1)));
    if (selected > selected_indices.back() && selected < static_cast<int>(point_vec.size() - 1))
      selected_indices.push_back(selected);
  }
  selected_indices.push_back(static_cast<int>(point_vec.size() - 1));
  std::sort(selected_indices.begin(), selected_indices.end());
  selected_indices.erase(std::unique(selected_indices.begin(), selected_indices.end()),
                         selected_indices.end());
  std::unordered_set<int> keep_indices(selected_indices.begin(), selected_indices.end());
  std::list<PointAdaptive*> trimmed_points;
  std::list<double> trimmed_parameters;
  for (int idx = 0; idx < static_cast<int>(point_vec.size()); ++idx) {
    if (keep_indices.find(idx) != keep_indices.end()) {
      trimmed_points.push_back(point_vec[static_cast<std::size_t>(idx)]);
      trimmed_parameters.push_back(param_vec[static_cast<std::size_t>(idx)]);
    }
  }
  param_curve->parameters_.swap(trimmed_parameters);
  points.swap(trimmed_points);
  for (int idx = 0; idx < static_cast<int>(point_vec.size()); ++idx)
    if (keep_indices.find(idx) == keep_indices.end())
      delete point_vec[static_cast<std::size_t>(idx)];
}
} // namespace apmesh::generation
