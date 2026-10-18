#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <set>
#include <vector>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif
#include "crab_mesh/performer/ranged_id_manager.h"
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/curve/curve_adaptive_parametric_hermite.h"
#include "data/node_adaptive.h"
#include "generator/curve_rebuild.h"

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;

namespace {
void require(bool condition, const char* message) {
  if (!condition) {
    // Stop before consuming a broken original's dangling observers. Aborted
    // contract cases do not establish a CRT retention measurement.
    std::fprintf(stderr, "Contract failed: %s\n", message);
    std::exit(1);
  }
}
struct Tracker {
  std::array<bool, 7> alive{};
  int destroyed = 0;
};
class CountedNode : public NodeAdaptive {
public:
  CountedNode(double x, unsigned int slot, Tracker& tracker)
      : NodeAdaptive(x, 0, 0, 40 + slot), slot_(slot), tracker_(tracker) {
    tracker_.alive[slot_] = true;
    SetGa(7);
    SetGd(8);
    SetHa(9);
    SetHd(10);
  }
  ~CountedNode() override {
    tracker_.alive[slot_] = false;
    ++tracker_.destroyed;
  }

private:
  unsigned int slot_;
  Tracker& tracker_;
};
struct Fixture {
  int kind, variant, target, count;
  Tracker& tracker;
  std::unique_ptr<CurveAdaptiveParametric> curve;
  std::array<CountedNode*, 7> original{};
  std::list<PointAdaptive*> points, original_points;
  std::list<double> original_parameters;
  std::vector<PointAdaptive* const*> point_nodes;
  std::vector<const double*> parameter_nodes;
  std::array<std::list<PointAdaptive*>, 3> endpoint_views;
  Performer::RangedIdManager manager;
  Fixture(int type, int layout, Tracker& counts)
      : kind(type), variant(layout), tracker(counts),
        manager(variant == 9 ? 0 : 100, 0, 1000, 1000) {
    count = (variant == 1 || variant == 3 || variant == 8) ? 7
            : variant == 5                                 ? 1
            : variant == 11                                ? 0
                                                           : 3;
    target = variant == 0   ? 6
             : variant == 1 ? 4
             : variant == 3 ? 3
             : variant == 4 ? 3
             : variant == 7 ? 4
             : variant == 8 ? -3
                            : 5;
    if (variant == 12) {
      count = 2;
      target = 4;
    }
    manager.setId(variant == 9 ? 0 : 100);
    require(manager.current() == static_cast<Performer::ULInt>(variant == 9 ? 0 : 100),
            "explicit actual ID-manager start is initialized");
    const PointAdaptive first(0, 0, 0), last(1, 0, 0);
    if (kind == 0) {
      curve = std::make_unique<CurveAdaptiveParametric>(first, last);
      Matrix4x1 coefficients;
      coefficients << 0, 0, 1, 0;
      curve->SetMatGeoGx(coefficients);
      curve->CalculateLengthCurve();
    } else if (kind == 1)
      curve = std::make_unique<CurveAdaptiveParametricBezier>(first, PointAdaptive(1.0 / 3, 0, 0),
                                                              PointAdaptive(2.0 / 3, 0, 0), last);
    else
      curve = std::make_unique<CurveAdaptiveParametricHermite>(first, last, VectorAdaptive(1, 0, 0),
                                                               VectorAdaptive(1, 0, 0));
    curve->SetId(77);
    for (int i = 0; i < count; ++i) {
      const double fraction =
          count < 2 ? 0.0 : static_cast<double>(i) / static_cast<double>(count - 1);
      const double t = (variant == 2 || variant == 3) ? 1.0 - fraction : fraction;
      if (variant == 7 && i == count - 1)
        points.push_back(original[0]);
      else {
        original[static_cast<std::size_t>(i)] =
            new CountedNode(t, static_cast<unsigned int>(i), tracker);
        points.push_back(original[static_cast<std::size_t>(i)]);
      }
      curve->parameters_.push_back(t);
    }
    if (variant == 6)
      curve->parameters_.pop_back();
    curve->SetPoints(points);
    original_points = points;
    original_parameters = curve->parameters_;
    for (const auto& p : points)
      point_nodes.push_back(std::addressof(p));
    for (const double& t : curve->parameters_)
      parameter_nodes.push_back(std::addressof(t));
    if (count >= 2) {
      endpoint_views[0] = {points.front(), points.back()};
      endpoint_views[1] = {points.back(), points.front()};
      endpoint_views[2] = {points.front(), points.back()};
    }
  }
  ~Fixture() {
    curve->GetPoints().clear();
    std::set<PointAdaptive*> unique(points.begin(), points.end());
    for (auto* p : unique)
      delete p;
  }
  Performer::IdManager* ids() { return variant == 10 ? nullptr : &manager; }
  bool noop() const { return variant == 4 || variant == 5 || variant == 6 || variant == 11; }
  void metadata() {
    require(curve->GetId() == 77, "curve identity is preserved");
    const auto p = curve->FindPointByParameter(0.25);
    require(std::abs(p.GetX() - 0.25) < 1e-12 && p.GetY() == 0 && p.GetZ() == 0,
            "analytic curve geometry is unchanged");
    if (count >= 2)
      for (const auto& view : endpoint_views) {
        require(view.size() == 2, "three endpoint observer views remain intact");
        for (auto* endpoint : view)
          require((endpoint == original_points.front() || endpoint == original_points.back()) &&
                      endpoint->GetX() ==
                          (endpoint == original_points.front()
                               ? original[0]->GetX()
                               : original[static_cast<std::size_t>(count - 1)]->GetX()) &&
                      static_cast<NodeAdaptive*>(endpoint)->GetGa() == 7,
                  "shared endpoint values, objects and curvature survive");
      }
  }
  void unchanged() {
    require(tracker.destroyed == 0, "failed rebuild deleted live samples");
    require(points == original_points && curve->GetPoints() == original_points,
            "failed rebuild preserves live point lists");
    require(curve->parameters_ == original_parameters,
            "failed rebuild preserves paired parameters");
    std::size_t i = 0;
    for (const auto& p : points)
      require(std::addressof(p) == point_nodes[i++], "failure preserves point list nodes");
    i = 0;
    for (const double& t : curve->parameters_)
      require(std::addressof(t) == parameter_nodes[i++], "failure preserves parameter list nodes");
    for (std::size_t j = 0; j < original.size(); ++j)
      if (original[j]) {
        require(tracker.alive[j], "original sample remains alive");
        const double fraction =
            count < 2 ? 0.0 : static_cast<double>(j) / static_cast<double>(count - 1);
        const double expected = (variant == 2 || variant == 3) ? 1.0 - fraction : fraction;
        require(original[j]->GetX() == expected && original[j]->GetY() == 0 &&
                    original[j]->GetZ() == 0,
                "failure preserves original XYZ");
        require(original[j]->GetId() == 40 + j && original[j]->GetGa() == 7 &&
                    original[j]->GetGd() == 8 && original[j]->GetHa() == 9 &&
                    original[j]->GetHd() == 10 && original[j]->GetNumberElements() == 0,
                "original node fields are preserved");
      }
    metadata();
  }
  void rebuilt(unsigned long first_id, bool trace) {
    if (noop()) {
      unchanged();
      require(manager.current() == first_id, "no-op does not consume IDs");
    } else {
      const bool growth = target > count;
      const int size = std::max(2, target);
      std::vector<int> selected;
      if (!growth)
        selected = variant == 1   ? std::vector<int>{0, 2, 4, 6}
                   : variant == 3 ? std::vector<int>{0, 3, 6}
                                  : std::vector<int>{0, 6};
      require(points.size() == static_cast<std::size_t>(size) &&
                  curve->parameters_.size() == points.size(),
              "point/parameter cardinality commits together");
      require(points.front() == original_points.front() && points.back() == original_points.back(),
              "endpoints reuse original objects");
      const int original_count = variant == 7 ? 2 : count;
      const int survivors = growth ? (variant == 7 ? 1 : 2) : size;
      require(tracker.destroyed == original_count - survivors,
              "only removed original interior samples are deleted once");
      auto p = points.begin();
      auto t = curve->parameters_.begin();
      for (int i = 0; i < size; ++i, ++p, ++t) {
        const double expected =
            growth ? static_cast<double>(i) / static_cast<double>(size - 1)
                   : (variant == 3
                          ? 1.0 - static_cast<double>(selected[static_cast<std::size_t>(i)]) / 6.0
                          : static_cast<double>(selected[static_cast<std::size_t>(i)]) / 6.0);
        require(*t == expected, "original parameter generation or selection is preserved exactly");
        if (!growth)
          require(*p == original[static_cast<std::size_t>(selected[static_cast<std::size_t>(i)])],
                  "shrink reuses independently selected original samples");
        if (growth && i > 0 && i < size - 1) {
          auto* node = dynamic_cast<NodeAdaptive*>(*p);
          require(node && std::abs(node->GetX() - expected) < 1e-12 && node->GetY() == 0 &&
                      node->GetZ() == 0 && node->GetGa() == 0 && node->GetGd() == 0 &&
                      node->GetHa() == 0 && node->GetHd() == 0 && node->GetNumberElements() == 0,
                  "new nodes preserve analytic XYZ and zero scalar/adjacency initialization");
          const unsigned long expected_id =
              ids() ? first_id + static_cast<unsigned long>(i - 1) : 0;
          require(node->GetId() == expected_id,
                  "successful ID request order and zero/null-manager behavior are preserved");
        }
        if (trace)
          std::printf("rebuild_point=kind:%d variant:%d index:%d id:%lu t:%a x:%a y:%a z:%a\n",
                      kind, variant, i, (*p)->GetId(), *t, (*p)->GetX(), (*p)->GetY(),
                      (*p)->GetZ());
      }
      require(manager.current() ==
                  first_id + static_cast<unsigned long>(growth && ids() ? size - 2 : 0),
              "exact successful ID request count");
      metadata();
    }
    if (trace)
      std::printf(
          "rebuild_normal=kind:%d variant:%d points:%zu parameters:%zu destroyed:%d manager:%lu\n",
          kind, variant, points.size(), curve->parameters_.size(), tracker.destroyed,
          manager.current());
  }
};
void normal(int kind, int variant) {
  Tracker tracker;
  Fixture fixture(kind, variant, tracker);
  const unsigned long start = fixture.manager.current();
  apmesh::generation::RebuildCurveWithTarget(fixture.curve.get(), fixture.points, fixture.target,
                                             fixture.ids());
  fixture.rebuilt(start, true);
  const auto repeated_points = fixture.points;
  const auto repeated_parameters = fixture.curve->parameters_;
  const auto repeated_id = fixture.manager.current();
  apmesh::generation::RebuildCurveWithTarget(
      fixture.curve.get(), fixture.points, static_cast<int>(fixture.points.size()), fixture.ids());
  require(fixture.points == repeated_points && fixture.curve->parameters_ == repeated_parameters &&
              fixture.manager.current() == repeated_id,
          "repeated same-count rebuild is a no-op");
}
// Allocation sweeps and deliberate controls use the same actual CRT instrument.
#if defined(_MSC_VER) && defined(_DEBUG)
int attempts = 0, denied = 0, fail_after = -1;
int allocation_hook(int kind, void*, std::size_t, int, long, const unsigned char*, int) {
  if (kind == _HOOK_ALLOC || kind == _HOOK_REALLOC) {
    ++attempts;
    if (fail_after-- == 0) {
      ++denied;
      return FALSE;
    }
  }
  return TRUE;
}
class AllocationScope {
public:
  explicit AllocationScope(int ordinal) {
    attempts = denied = 0;
    fail_after = ordinal;
    previous_ = _CrtSetAllocHook(allocation_hook);
  }
  ~AllocationScope() { _CrtSetAllocHook(previous_); }
  AllocationScope(const AllocationScope&) = delete;
  AllocationScope& operator=(const AllocationScope&) = delete;

private:
  _CRT_ALLOC_HOOK previous_;
};
template <class Action> void inject(int ordinal, Action action) {
  bool caught = false;
  {
    AllocationScope hook(ordinal);
    try {
      action();
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  require(caught && denied == 1, "each calibrated allocation denial propagates exactly once");
}
void failures(int kind, int variant) {
  int total = 0;
  {
    Tracker tracker;
    Fixture fixture(kind, variant, tracker);
    const auto start = fixture.manager.current();
    {
      AllocationScope hook(-1);
      apmesh::generation::RebuildCurveWithTarget(fixture.curve.get(), fixture.points,
                                                 fixture.target, fixture.ids());
      total = attempts;
    }
    fixture.rebuilt(start, false);
  }
  require(total > 0, "failure sweep requires positive observed allocations");
  std::printf("rebuild_measured=kind:%d variant:%d allocations:%d\n", kind, variant, total);
  int consumed_failures = 0;
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    Tracker tracker;
    Fixture fixture(kind, variant, tracker);
    const auto start = fixture.manager.current();
    std::printf("rebuild_inject=ordinal:%d\n", ordinal);
    inject(ordinal, [&] {
      apmesh::generation::RebuildCurveWithTarget(fixture.curve.get(), fixture.points,
                                                 fixture.target, fixture.ids());
    });
    fixture.unchanged();
    const auto consumed = fixture.manager.current();
    if (consumed > start)
      ++consumed_failures;
    require(consumed >= start &&
                consumed <= start + static_cast<unsigned long>(std::max(0, fixture.target - 2)),
            "consumed IDs are not rolled back or unexpectedly advanced");
    if (fixture.noop() || fixture.target < fixture.count || fixture.ids() == nullptr)
      require(consumed == start, "no-op/shrink/null manager does not request IDs");
    apmesh::generation::RebuildCurveWithTarget(fixture.curve.get(), fixture.points, fixture.target,
                                               fixture.ids());
    fixture.rebuilt(consumed, false);
  }
  if (!(variant == 4 || variant == 5 || variant == 6 || variant == 1 || variant == 3 ||
        variant == 8 || variant == 10))
    require(consumed_failures > 0 && consumed_failures < total,
            "growth failures include consumed and unconsumed ID controls");
  std::printf("rebuild_consumed=kind:%d variant:%d failed_calls:%d\n", kind, variant,
              consumed_failures);
  std::printf(
      "rebuild_failure_sites=kind:%d variant:%d denied:%d/%d unchanged:1 retry:1 ids:consumed\n",
      kind, variant, total, total);
}
#endif
bool scenario(const char* mode, const char* prefix, int& kind, int& variant) {
  int consumed = 0;
  if (std::strncmp(mode, prefix, std::strlen(prefix)) != 0)
    return false;
  const char* suffix = mode + std::strlen(prefix);
  return std::sscanf(suffix, "%d-%d%n", &kind, &variant, &consumed) == 2 &&
         suffix[consumed] == '\0' && kind >= 0 && kind < 3 && variant >= 0 && variant < 13;
}
} // namespace
int main(int argc, char** argv) {
  require(argc == 2, "one scenario required");
  std::setvbuf(stdout, nullptr, _IONBF, 0);
#if defined(_WIN32)
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
#endif
#if defined(_MSC_VER) && defined(_DEBUG)
  for (int report : {_CRT_WARN, _CRT_ERROR, _CRT_ASSERT}) {
    _CrtSetReportMode(report, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(report, _CRTDBG_FILE_STDERR);
  }
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  auto* mode = argv[1];
  int kind = -1, variant = -1;
  if (std::strcmp(mode, "contracts") == 0) {
    for (int k = 0; k < 3; ++k)
      for (int v = 0; v < 13; ++v)
        normal(k, v);
  } else if (scenario(mode, "normal-", kind, variant))
    normal(kind, variant);
  else if (std::strcmp(mode, "use-after-free") == 0) {
    auto* p = new PointAdaptive(1, 2, 3);
    delete p;
    std::printf("expired=%g\n", p->GetX());
  } else if (std::strcmp(mode, "leak") == 0)
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (scenario(mode, "failure-", kind, variant) && variant != 11)
      failures(kind, variant);
    else if (std::strcmp(mode, "allocation-hook-control") == 0) {
      inject(0, [] { auto p = std::make_unique<PointAdaptive>(); });
      std::puts("allocation_hook_control=detected");
    } else
      require(false, "unknown scenario");
#else
    require(false, "Debug CRT allocation hook required");
#endif
  }
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  if (delta.lCounts[_NORMAL_BLOCK] != 0) {
    _CrtMemDumpAllObjectsSince(&before);
    return 1;
  }
#endif
  std::puts("PASS");
}
