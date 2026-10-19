#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <memory>
#include <new>
#include <set>
#include <string>
#include <vector>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif
#include "adapter/curve_samples.h"
#include "generator/curve_rebuild.h"
#include <type_traits>
#include <stdexcept>
#ifdef AP_MESH_PUBLICATION_HEADER
#include AP_MESH_PUBLICATION_HEADER
#else
#include "generator/curve_publication.h"
#endif
#include "crab_mesh/performer/ranged_id_manager.h"
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/curve/curve_adaptive_parametric_hermite.h"
#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
namespace {
void require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Contract failed: %s\n", message);
    std::exit(1);
  }
}
struct Tracker {
  int destroyed = 0;
};
class CountedNode : public NodeAdaptive {
public:
  CountedNode(double t, unsigned long id, Tracker& tracker)
      : NodeAdaptive(t, t * (1 - t), 0, id), tracker_(tracker) {}
  ~CountedNode() override { ++tracker_.destroyed; }

private:
  Tracker& tracker_;
};
using Cache = std::map<PointAdaptive*, PointAdaptive*>;
struct Fixture {
  int kind, variant;
  bool completed = false;
  int curve_calls = 0, surface_calls = 0;
  std::list<double> second{0, 0.2, 0.5, 0.8, 1};
  Tracker& tracker;
  std::unique_ptr<CurveAdaptiveParametric> curve;
  std::array<std::unique_ptr<CountedNode>, 3> source;
  std::array<NodeAdaptive, 4> borrowed;
  std::array<NodeAdaptive, 3> triangle_nodes;
  std::unique_ptr<TriangleAdaptive> triangle;
  std::list<PointAdaptive*> captured, live_points, output, second_output;
  std::list<double> selected, old_parameters{1, 0.5, 0};
  std::vector<const double*> parameter_nodes;
  std::vector<PointAdaptive* const*> point_nodes;
  Cache cache, old_cache;
  std::map<PointAdaptive*, const Cache::value_type*> cache_nodes;
  Performer::RangedIdManager manager;
  Fixture(int type, int layout, Tracker& counts)
      : kind(type), variant(layout), tracker(counts), manager(0, 0, 1000, 1000) {
    manager.setId(variant == 6 ? 0 : 100);
    const PointAdaptive a(0, 0, 0), b(1, 0, 0);
    if (kind == 0) {
      curve = std::make_unique<CurveAdaptiveParametric>(a, b);
      Matrix4x1 x, y;
      x << 0, 0, 1, 0;
      y << 0, -1, 1, 0;
      curve->SetMatGeoGx(x);
      curve->SetMatGeoGy(y);
      curve->CalculateLengthCurve();
    } else if (kind == 1)
      curve = std::make_unique<CurveAdaptiveParametricBezier>(
          a, PointAdaptive(1.0 / 3, 1.0 / 3, 0), PointAdaptive(2.0 / 3, 1.0 / 3, 0), b);
    else
      curve = std::make_unique<CurveAdaptiveParametricHermite>(a, b, VectorAdaptive(1, 1, 0),
                                                               VectorAdaptive(1, -1, 0));
    triangle_nodes[0] = NodeAdaptive(0, 0, 0);
    triangle_nodes[1] = NodeAdaptive(1, 0, 0);
    triangle_nodes[2] = NodeAdaptive(0, 1, 0);
    triangle = std::make_unique<TriangleAdaptive>(&triangle_nodes[0], &triangle_nodes[1],
                                                  &triangle_nodes[2]);
    for (unsigned int i = 0; i < 3; ++i) {
      const double t = variant == 5 ? 1.0 - static_cast<double>(i) / 2 : static_cast<double>(i) / 2;
      source[i] = std::make_unique<CountedNode>(t, 40 + i, tracker);
      source[i]->SetGa(7);
      source[i]->SetGd(8);
      source[i]->SetHa(9);
      source[i]->SetHd(10);
      source[i]->InsertElement(triangle.get());
    }
    captured = {source[0].get(), source[1].get(), variant == 3 ? source[0].get() : source[2].get()};
    if (variant == 4 || variant == 7)
      captured = {source[0].get(), source[2].get()};
    curve->SetPoints(captured);
    curve->GetPoints().reverse();
    live_points = curve->GetPoints();
    curve->UpdateParameters(old_parameters);
    for (const auto& p : curve->GetPoints())
      point_nodes.push_back(std::addressof(p));
    for (const auto& t : curve->parameters_)
      parameter_nodes.push_back(std::addressof(t));
    selected = variant == 2                     ? std::list<double>{0, 0.5, 1}
               : variant == 3                   ? std::list<double>{0, 0.2, 0.5, 0.8, 1}
               : (variant == 4 || variant == 7) ? std::list<double>{0, 1}
               : variant == 5                   ? std::list<double>{1, 0.75, 0.25, 0}
               : variant == 8                   ? old_parameters
                                                : std::list<double>{0, 0.25, 0.75, 1};
    for (unsigned int i = 0; i < borrowed.size(); ++i) {
      const auto* p = i == 0 ? captured.front() : captured.back();
      borrowed[i] = NodeAdaptive(p->GetX(), p->GetY(), p->GetZ(), 200 + i);
      borrowed[i].SetGa(20 + i);
      borrowed[i].SetGd(30 + i);
      borrowed[i].SetHa(40 + i);
      borrowed[i].SetHd(50 + i);
      borrowed[i].InsertElement(triangle.get());
    }
    cache[&borrowed[2]] = &borrowed[3];
    if (variant == 1 || variant == 2 || variant == 7 || variant == 8) {
      cache[captured.front()] = &borrowed[0];
      cache[&borrowed[0]] = (variant == 1 || variant == 2) ? &borrowed[2] : &borrowed[0];
    }
    if (variant == 2 || variant == 7 || variant == 8) {
      cache[captured.back()] = &borrowed[1];
      cache[&borrowed[1]] = variant == 2 ? &borrowed[3] : &borrowed[1];
    }
    old_cache = cache;
    for (const auto& entry : cache)
      cache_nodes.emplace(entry.first, std::addressof(entry));
  }
  bool is_borrowed(PointAdaptive* p) const {
    for (const auto& s : source)
      if (s.get() == p)
        return true;
    for (const auto& b : borrowed)
      if (&b == p)
        return true;
    return false;
  }
  ~Fixture() {
    // Retention experiments allow partial original cache publication, without
    // claiming rollback. Reclaim every reachable nonborrowed node exactly once.
    std::set<PointAdaptive*> nodes(output.begin(), output.end());
    nodes.insert(curve->GetPoints().begin(), curve->GetPoints().end());
    nodes.insert(second_output.begin(), second_output.end());
    for (const auto& e : cache)
      nodes.insert(e.second);
    for (auto* p : nodes)
      if (!is_borrowed(p))
        delete p;
  }

  bool rebuilding() const { return variant == 0 || variant == 1 || variant == 2 || variant == 8; }
  int target() const { return variant == 0 ? 7 : variant == 1 ? 3 : variant == 2 ? 5 : 2; }
  void run(bool abort_surface = false) {
    static_assert(std::is_nothrow_move_assignable_v<std::list<PointAdaptive*>>);
    apmesh::generation::RefineCurveSamples(
        curve.get(), cache,
        [&] {
          ++curve_calls;
          // Match the serial methods' pre-sort capture. Reversal is a controlled
          // upstream list mutation; evaluator scratch is outside this contract.
          const auto points = curve->GetPoints();
          curve->GetPoints().reverse();
          return apmesh::adaptation::BuildCurveSamples(curve.get(), points, selected, cache,
                                                       &manager);
        },
        [&] {
          ++surface_calls;
          require(curve->parameters_ == selected && curve->GetPoints().size() == selected.size(),
                  "surface pass sees the published curve pass and parameters");
          const auto points = curve->GetPoints();
          curve->GetPoints().reverse();
          if (abort_surface)
            throw std::runtime_error("controlled upstream surface failure");
          return apmesh::adaptation::BuildCurveSamples(curve.get(), points, second, cache,
                                                       &manager);
        },
        rebuilding(), target(), &manager);
    completed = true;
  }
  void borrowed_unchanged() {
    require(tracker.destroyed == 0, "entry sample objects remain borrowed and alive");
    for (unsigned int i = 0; i < 3; ++i) {
      const double t = variant == 5 ? 1.0 - static_cast<double>(i) / 2 : static_cast<double>(i) / 2;
      require(source[i]->GetId() == 40 + i && source[i]->GetX() == t &&
                  source[i]->GetY() == t * (1 - t) && source[i]->GetZ() == 0 &&
                  source[i]->GetGa() == 7 && source[i]->GetGd() == 8 && source[i]->GetHa() == 9 &&
                  source[i]->GetHd() == 10 && source[i]->GetNumberElements() == 1 &&
                  source[i]->GetElement(0) == triangle.get(),
              "source scalar and adjacency state is unchanged");
    }
    for (unsigned int i = 0; i < borrowed.size(); ++i)
      require(borrowed[i].GetId() == 200 + i && borrowed[i].GetGa() == 20 + i &&
                  borrowed[i].GetGd() == 30 + i && borrowed[i].GetHa() == 40 + i &&
                  borrowed[i].GetHd() == 50 + i && borrowed[i].GetNumberElements() == 1 &&
                  borrowed[i].GetElement(0) == triangle.get(),
              "preexisting cache values remain borrowed with original state");
  }
  void unchanged() {
    borrowed_unchanged();
    require(!completed && curve->GetPoints() == live_points,
            "failed publication restores entry point values");
    require(curve->parameters_ == old_parameters, "failed publication restores entry parameters");
    require(cache == old_cache, "failed publication restores cache keys and values");
    std::size_t j = 0;
    for (const auto& p : curve->GetPoints())
      require(std::addressof(p) == point_nodes[j++],
              "failed publication restores entry point nodes");
    j = 0;
    for (const auto& t : curve->parameters_)
      require(std::addressof(t) == parameter_nodes[j++],
              "failed publication restores entry parameter nodes");
    for (const auto& e : cache)
      require(std::addressof(e) == cache_nodes.at(e.first),
              "cache entry nodes remain stable across failure");
  }
  std::string label(PointAdaptive* p) const {
    for (unsigned int i = 0; i < source.size(); ++i)
      if (source[i].get() == p)
        return "S" + std::to_string(i);
    for (unsigned int i = 0; i < borrowed.size(); ++i)
      if (&borrowed[i] == p)
        return "B" + std::to_string(i);
    unsigned int i = 0;
    for (auto* q : curve->GetPoints()) {
      if (p == q)
        return "R" + std::to_string(i);
      ++i;
    }
    require(false, "all retained pointers have live observed roles");
    return {};
  }
  void built(unsigned long start, bool trace) {
    borrowed_unchanged();
    const auto& points = curve->GetPoints();
    const auto& parameters = curve->parameters_;
    require(completed && points.size() == parameters.size() &&
                points.size() == static_cast<std::size_t>(rebuilding() ? target() : 5),
            "positive paired final sample cardinality");
    // The fixture's entry point list is reversed, just as recorded at entry.
    auto* entry_front = live_points.front();
    auto* entry_back = live_points.back();
    const auto previous_front = old_cache.find(entry_front);
    const auto previous_back = old_cache.find(entry_back);
    if (previous_front != old_cache.end())
      require(points.front() == previous_front->second, "preexisting first endpoint is reused");
    if (previous_back != old_cache.end())
      require(points.back() == previous_back->second, "preexisting last endpoint is reused");
    require((entry_front == entry_back) == (points.front() == points.back()),
            "closed endpoint alias identity is preserved");
    Cache expected = old_cache;
    expected[entry_front] = points.front();
    expected[entry_back] = points.back();
    expected[points.front()] = points.front();
    expected[points.back()] = points.back();
    require(cache == expected, "cache source mappings and endpoint aliases preserve policy");
    for (const auto& e : old_cache)
      require(std::addressof(*cache.find(e.first)) == cache_nodes.at(e.first),
              "success preserves preexisting cache entry nodes");
    unsigned long endpoints = previous_front == old_cache.end() ? 1 : 0;
    if (entry_back != entry_front && previous_back == old_cache.end())
      ++endpoints;
    unsigned long count = endpoints + selected.size() - 2 + second.size() - 2;
    if (rebuilding() && target() > static_cast<int>(second.size()))
      count += static_cast<unsigned long>(target() - 2);
    require(manager.current() == start + count,
            "ID request count and consumed sequence are preserved");
    if (trace)
      std::printf("publication_normal=kind:%d variant:%d requests:%lu calls:%d,%d\n", kind, variant,
                  count, curve_calls, surface_calls);
    std::size_t i = 0;
    auto t = parameters.begin();
    for (auto* p : points) {
      auto* n = static_cast<NodeAdaptive*>(p);
      const double parameter = *t++;
      if (i > 0 && i + 1 < points.size()) {
        require(std::abs(p->GetX() - parameter) < 1e-12 &&
                    std::abs(p->GetY() - parameter * (1 - parameter)) < 1e-12 && p->GetZ() == 0,
                "independent analytic interior polynomial samples");
        require(n->GetGa() == 0 && n->GetGd() == 0 && n->GetHa() == 0 && n->GetHd() == 0 &&
                    n->GetNumberElements() == 0,
                "new interiors preserve zero scalar/adjacency policy");
      } else
        require(n->GetNumberElements() == 1 && n->GetElement(0) == triangle.get(),
                "endpoint adjacency remains a borrowed observer copy");
      if (trace)
        std::printf("publication_point=%zu role:%s id:%lu t:%.17g xyz:%.17g,%.17g,%.17g "
                    "curvature:%.17g,%.17g,%.17g,%.17g adjacency:%u\n",
                    i, label(p).c_str(), p->GetId(), parameter, p->GetX(), p->GetY(), p->GetZ(),
                    n->GetGa(), n->GetGd(), n->GetHa(), n->GetHd(), n->GetNumberElements());
      ++i;
    }
    if (trace) {
      std::vector<std::string> entries;
      for (const auto& e : cache)
        entries.push_back(label(e.first) + ":" + label(e.second));
      std::sort(entries.begin(), entries.end());
      for (const auto& e : entries)
        std::printf("publication_cache=%s\n", e.c_str());
    }
  }
};
void normal(int kind, int variant) {
  Tracker tracker;
  Fixture fixture(kind, variant, tracker);
  const auto start = fixture.manager.current();
  fixture.run();
  fixture.built(static_cast<unsigned long>(start), true);
}
void abort_surface(int kind, int variant) {
  Tracker tracker;
  Fixture fixture(kind, variant, tracker);
  const auto start = fixture.manager.current();
  bool caught = false;
  try {
    fixture.run(true);
  } catch (const std::runtime_error&) {
    caught = true;
  }
  require(caught && fixture.curve_calls == 1 && fixture.surface_calls == 1,
          "controlled upstream failure occurs after curve publication");
  fixture.unchanged();
  const auto consumed = fixture.manager.current();
  require(consumed >= start && (fixture.variant == 7 ? consumed == start : consumed > start),
          "upstream failure preserves the first pass ID prefix, including the cached zero-ID case");
  fixture.run();
  fixture.built(static_cast<unsigned long>(consumed), false);
  std::printf("publication_abort=kind:%d variant:%d restored:1 retry:1\n", kind, variant);
}
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
  unsigned long requests = 0;
  {
    Tracker tracker;
    Fixture fixture(kind, variant, tracker);
    const auto start = fixture.manager.current();
    {
      AllocationScope hook(-1);
      fixture.run();
      total = attempts;
    }
    requests = static_cast<unsigned long>(fixture.manager.current() - start);
    fixture.built(static_cast<unsigned long>(start), false);
  }
  require(total > 0, "positive calibrated publication allocations required");
  std::printf("publication_measured=kind:%d variant:%d allocations:%d\n", kind, variant, total);
  int consumed_calls = 0, reached_surface = 0;
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    Tracker tracker;
    Fixture fixture(kind, variant, tracker);
    const auto start = fixture.manager.current();
    std::printf("publication_inject=ordinal:%d\n", ordinal);
    inject(ordinal, [&] { fixture.run(); });
    require(attempts == ordinal + 1, "rollback performs no allocation after the denied request");
    fixture.unchanged();
    const auto next = fixture.manager.current();
    if (next > start)
      ++consumed_calls;
    if (fixture.surface_calls > 0)
      ++reached_surface;
    require(next >= start && next <= start + requests,
            "failure preserves the consumed ID prefix without rewinding");
    if (ordinal == total - 1) {
      require(next == start + requests && fixture.surface_calls == 1,
              "last denial occurs after all requested sample IDs");
      std::printf("publication_final_edge=kind:%d variant:%d requests:%lu restored:1\n", kind,
                  variant, requests);
    }
    fixture.run();
    fixture.built(static_cast<unsigned long>(next), false);
  }
  require(consumed_calls > 0 && consumed_calls < total && reached_surface > 0,
          "both unpublished and published failures plus surface paths are exercised");
  std::printf(
      "publication_failure_sites=kind:%d variant:%d denied:%d/%d retry:1 consumed:%d surface:%d\n",
      kind, variant, total, total, consumed_calls, reached_surface);
}
#endif
bool scenario(const char* mode, const char* prefix, int& kind, int& variant) {
  int consumed = 0;
  if (std::strncmp(mode, prefix, std::strlen(prefix)) != 0)
    return false;
  const char* suffix = mode + std::strlen(prefix);
  return std::sscanf(suffix, "%d-%d%n", &kind, &variant, &consumed) == 2 &&
         suffix[consumed] == '\0' && kind >= 0 && kind < 3 && variant >= 0 && variant < 9;
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
      for (int v = 0; v < 9; ++v)
        normal(k, v);
  } else if (scenario(mode, "normal-", kind, variant))
    normal(kind, variant);
  else if (scenario(mode, "abort-", kind, variant))
    abort_surface(kind, variant);
  else if (std::strcmp(mode, "use-after-free") == 0) {
    auto* p = new PointAdaptive(1, 2, 3);
    delete p;
    std::printf("expired=%g\n", p->GetX());
  } else if (std::strcmp(mode, "leak") == 0)
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (scenario(mode, "failure-", kind, variant) && true)
      failures(kind, variant);
    else if (std::strcmp(mode, "return-move-control") == 0) {
      std::list<PointAdaptive*> source{nullptr};
      inject(0, [&] { std::list<PointAdaptive*> moved(std::move(source)); });
      require(source.size() == 1 && source.front() == nullptr,
              "MSVC list move allocation denial preserves the source");
      std::puts("return_move_control=detected");
    } else if (std::strcmp(mode, "allocation-hook-control") == 0) {
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
