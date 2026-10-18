#include "adapter/curve_samples.h"

#include <exception>
#include <memory>
#include <vector>

#include "crab_mesh/performer/id_manager.h"
#include "data/curve/curve_adaptive_parametric.h"
#include "data/node_adaptive.h"

namespace apmesh::adaptation {
namespace {
using SampleCache = std::map<PointAdaptive*, PointAdaptive*>;
using PendingNodes = std::vector<std::unique_ptr<NodeAdaptive>>;

class CommitSamplesOnReturn {
public:
  CommitSamplesOnReturn(CurveAdaptiveParametric& curve, std::list<double>& parameters,
                        SampleCache& cache, SampleCache& changes, PendingNodes& owners)
      : curve_(curve), parameters_(parameters), cache_(cache), changes_(changes), owners_(owners),
        exceptions_(std::uncaught_exceptions()) {}
  ~CommitSamplesOnReturn() noexcept {
    if (std::uncaught_exceptions() != exceptions_)
      return;
    // Default allocators match and pointer comparison cannot throw. Transfer
    // prepared map nodes without allocating or invalidating existing entries.
    for (const auto& entry : changes_) {
      auto existing = cache_.find(entry.first);
      if (existing != cache_.end())
        existing->second = entry.second;
    }
    cache_.merge(changes_);
    curve_.parameters_.swap(parameters_);
    for (auto& owner : owners_)
      owner.release();
  }
  CommitSamplesOnReturn(const CommitSamplesOnReturn&) = delete;
  CommitSamplesOnReturn& operator=(const CommitSamplesOnReturn&) = delete;

private:
  CurveAdaptiveParametric& curve_;
  std::list<double>& parameters_;
  SampleCache& cache_;
  SampleCache& changes_;
  PendingNodes& owners_;
  int exceptions_;
};
} // namespace

std::list<PointAdaptive*> BuildCurveSamples(CurveAdaptive* curve,
                                            const std::list<PointAdaptive*>& points,
                                            const std::list<double>& parameters,
                                            std::map<PointAdaptive*, PointAdaptive*>& map_points,
                                            Performer::IdManager* id_manager) {
  auto* param_curve = static_cast<CurveAdaptiveParametric*>(curve);
  std::list<double> prepared_parameters(parameters);
  SampleCache changes;
  PendingNodes owners;
  std::list<PointAdaptive*> list_new_points;
  auto endpoint = [&](PointAdaptive* source) {
    auto staged = changes.find(source);
    if (staged != changes.end())
      return static_cast<NodeAdaptive*>(staged->second);
    auto existing = map_points.find(source);
    if (existing != map_points.end())
      return static_cast<NodeAdaptive*>(existing->second);
    auto node = std::make_unique<NodeAdaptive>(*static_cast<NodeAdaptive*>(source));
    node->SetId(id_manager->next(0));
    NodeAdaptive* result = node.get();
    owners.push_back(std::move(node));
    changes.emplace(source, result);
    return result;
  };
  NodeAdaptive* new_front = endpoint(points.front());
  NodeAdaptive* new_back = endpoint(points.back());
  list_new_points.push_back(new_front);
  for (auto it = ++parameters.begin(); it != --parameters.end(); ++it) {
    auto node = std::make_unique<NodeAdaptive>(param_curve->FindPointByParameter(*it));
    node->SetId(id_manager->next(0));
    NodeAdaptive* result = node.get();
    owners.push_back(std::move(node));
    list_new_points.push_back(result);
  }
  list_new_points.push_back(new_back);
  changes[new_front] = new_front;
  changes[new_back] = new_back;
  // The return list must be constructed before commit: optional NRVO may be
  // disabled, and a standard-library list move constructor can allocate.
  CommitSamplesOnReturn commit(*param_curve, prepared_parameters, map_points, changes, owners);
  return list_new_points;
}
} // namespace apmesh::adaptation
