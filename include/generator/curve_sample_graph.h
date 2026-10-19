#ifndef APMESH_GENERATOR_CURVE_SAMPLE_GRAPH_H
#define APMESH_GENERATOR_CURVE_SAMPLE_GRAPH_H

#include <list>
#include <map>
#include <unordered_set>
#include <vector>

class CurveAdaptive;
class Geometry;
class PointAdaptive;

namespace apmesh::generation {
// Serial AdaptCurve point/parameter graph boundary with fixed curve topology.
// Initial samples are collectively owned by the caller, with no competing
// geometry/control-point or mesh owner. Keep them alive until complete commit.
// Use only the qualified serial sample/publication/rebuild operations: they
// publish every new live sample in the graph and preserve entry objects.
// Failure restores all original list nodes/sharing and deletes new graph samples
// once. Success retires initial samples and leaves final graph ownership with
// the caller. IDs, evaluator scratch and orchestration metadata are not restored.
class CurveSampleGraphTransaction {
public:
  explicit CurveSampleGraphTransaction(Geometry* geometry);
  ~CurveSampleGraphTransaction();
  CurveSampleGraphTransaction(const CurveSampleGraphTransaction&) = delete;
  CurveSampleGraphTransaction& operator=(const CurveSampleGraphTransaction&) = delete;

  std::map<PointAdaptive*, PointAdaptive*>& Cache() noexcept { return cache_; }
  void Commit() noexcept;

private:
  struct Entry {
    explicit Entry(CurveAdaptive* source);
    CurveAdaptive* curve;
    std::list<PointAdaptive*> points;
    std::list<double> parameters;
  };
  void DeleteNewSamples() noexcept;

  std::map<PointAdaptive*, PointAdaptive*> cache_;
  std::vector<Entry> entries_;
  std::unordered_set<PointAdaptive*> initial_samples_;
  bool committed_ = false;
};
} // namespace apmesh::generation
#endif
