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
    nodes.insert(second_output.begin(), second_output.end());
    for (const auto& e : cache)
      nodes.insert(e.second);
    for (auto* p : nodes)
      if (!is_borrowed(p))
        delete p;
  }
  std::list<PointAdaptive*> run() {
    return apmesh::adaptation::BuildCurveSamples(curve.get(), captured, selected, cache, &manager);
  }
  void borrowed_unchanged() {
    require(tracker.destroyed == 0, "borrowed source nodes remain alive");
    require(curve->GetPoints() == live_points, "helper does not publish curve point observers");
    std::size_t j = 0;
    for (const auto& p : curve->GetPoints())
      require(std::addressof(p) == point_nodes[j++], "curve point list nodes remain stable");
    for (unsigned int i = 0; i < 3; ++i) {
      const double t = variant == 5 ? 1.0 - static_cast<double>(i) / 2 : static_cast<double>(i) / 2;
      require(source[i]->GetId() == 40 + i && source[i]->GetX() == t &&
                  source[i]->GetY() == t * (1 - t) && source[i]->GetZ() == 0 &&
                  source[i]->GetGa() == 7 && source[i]->GetGd() == 8 && source[i]->GetHa() == 9 &&
                  source[i]->GetHd() == 10 && source[i]->GetNumberElements() == 1 &&
                  source[i]->GetElement(0) == triangle.get(),
              "borrowed source fields and adjacency remain unchanged");
    }
    for (unsigned int i = 0; i < borrowed.size(); ++i)
      require(borrowed[i].GetId() == 200 + i && borrowed[i].GetGa() == 20 + i &&
                  borrowed[i].GetGd() == 30 + i && borrowed[i].GetHa() == 40 + i &&
                  borrowed[i].GetHd() == 50 + i && borrowed[i].GetNumberElements() == 1 &&
                  borrowed[i].GetElement(0) == triangle.get(),
              "caller-owned cache fields and adjacency remain unchanged");
  }
  void unchanged() {
    borrowed_unchanged();
    require(curve->parameters_ == old_parameters,
            "failed sample construction preserves parameter values");
    require(cache == old_cache, "failed sample construction preserves cache entries and values");
    std::size_t j = 0;
    for (const auto& t : curve->parameters_)
      require(std::addressof(t) == parameter_nodes[j++],
              "failed sample construction preserves parameter list nodes");
    for (const auto& e : cache)
      require(std::addressof(e) == cache_nodes.at(e.first),
              "failed sample construction preserves cache entry nodes");
  }
  std::string label(PointAdaptive* p) const {
    for (unsigned int i = 0; i < source.size(); ++i)
      if (source[i].get() == p)
        return "S" + std::to_string(i);
    for (unsigned int i = 0; i < borrowed.size(); ++i)
      if (&borrowed[i] == p)
        return "B" + std::to_string(i);
    unsigned int i = 0;
    for (auto* q : output) {
      if (p == q)
        return "R" + std::to_string(i);
      ++i;
    }
    require(false, "every published pointer has an observed role");
    return {};
  }
  void built(unsigned long start, bool trace) {
    borrowed_unchanged();
    require(output.size() == selected.size() && output.size() >= 2,
            "positive output sample/parameter cardinality");
    require(curve->parameters_ == selected, "selected parameter values/order commit on success");
    auto old_front = old_cache.find(captured.front());
    auto old_back = old_cache.find(captured.back());
    auto* front = old_front == old_cache.end() ? output.front() : old_front->second;
    auto* back = captured.front() == captured.back() ? front
                 : old_back == old_cache.end()       ? output.back()
                                                     : old_back->second;
    require(output.front() == front && output.back() == back,
            "cached and closed endpoints preserve reuse identity");
    Cache expected = old_cache;
    expected[captured.front()] = front;
    expected[captured.back()] = back;
    expected[front] = front;
    expected[back] = back;
    require(cache == expected,
            "source mappings and current-endpoint alias overwrites preserve policy");
    for (const auto& e : old_cache)
      require(std::addressof(*cache.find(e.first)) == cache_nodes.at(e.first),
              "success preserves pre-existing cache entry nodes");
    unsigned long next = start;
    for (auto pair :
         {std::make_pair(front, captured.front()), std::make_pair(back, captured.back())}) {
      if (pair.first == front && pair.second == captured.back() &&
          captured.front() == captured.back() && next != start)
        continue;
      if (old_cache.find(pair.second) == old_cache.end()) {
        auto* node = static_cast<NodeAdaptive*>(pair.first);
        auto* old = static_cast<NodeAdaptive*>(pair.second);
        require(node->GetId() == next++ && node->GetX() == old->GetX() &&
                    node->GetY() == old->GetY() && node->GetZ() == old->GetZ() &&
                    node->GetGa() == old->GetGa() && node->GetGd() == old->GetGd() &&
                    node->GetHa() == old->GetHa() && node->GetHd() == old->GetHd() &&
                    node->GetElements() == old->GetElements(),
                "endpoint clone preserves scalar/adjacency copy policy and ID order");
      }
    }
    auto t = selected.begin();
    std::size_t i = 0;
    for (auto* point : output) {
      auto* node = dynamic_cast<NodeAdaptive*>(point);
      require(node != nullptr, "actual node dynamic type");
      if (i > 0 && i + 1 < output.size()) {
        require(node->GetId() == next++ && std::abs(node->GetX() - *t) < 1e-12 &&
                    std::abs(node->GetY() - *t * (1 - *t)) < 1e-12 && node->GetZ() == 0 &&
                    node->GetGa() == 0 && node->GetGd() == 0 && node->GetHa() == 0 &&
                    node->GetHd() == 0 && node->GetNumberElements() == 0,
                "analytic curved interior, IDs and zero initialization");
      }
      if (trace)
        std::printf("sample_point=kind:%d variant:%d index:%zu id:%lu t:%a x:%a y:%a z:%a ga:%a "
                    "adjacency:%u\n",
                    kind, variant, i, node->GetId(), *t, node->GetX(), node->GetY(), node->GetZ(),
                    node->GetGa(), node->GetNumberElements());
      ++t;
      ++i;
    }
    require(manager.current() == next, "exact successful ID request count");
    if (trace) {
      std::vector<std::pair<std::string, std::string>> entries;
      for (const auto& e : cache)
        entries.emplace_back(label(e.first), label(e.second));
      std::sort(entries.begin(), entries.end());
      for (const auto& e : entries)
        std::printf("sample_cache=key:%s value:%s\n", e.first.c_str(), e.second.c_str());
      std::printf("sample_normal=kind:%d variant:%d points:%zu cache:%zu manager:%lu\n", kind,
                  variant, output.size(), cache.size(),
                  static_cast<unsigned long>(manager.current()));
    }
  }
};
void normal(int kind, int variant) {
  Tracker tracker;
  Fixture fixture(kind, variant, tracker);
  const auto start = fixture.manager.current();
  fixture.output = fixture.run();
  fixture.built(static_cast<unsigned long>(start), true);
  const auto cache = fixture.cache;
  const auto next = fixture.manager.current();
  fixture.second_output = fixture.run();
  require(fixture.second_output.front() == fixture.output.front() &&
              fixture.second_output.back() == fixture.output.back() && fixture.cache == cache &&
              fixture.manager.current() == next + fixture.selected.size() - 2,
          "repeat reuses endpoints and only regenerates interiors");
  fixture.borrowed_unchanged();
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
void failures(int kind, int variant, bool retention_only) {
  int total = 0;
  unsigned long requests = 0;
  {
    Tracker tracker;
    Fixture fixture(kind, variant, tracker);
    const auto start = fixture.manager.current();
    {
      AllocationScope hook(-1);
      fixture.output = fixture.run();
      total = attempts;
    }
    requests = static_cast<unsigned long>(fixture.manager.current() - start);
    fixture.built(static_cast<unsigned long>(start), false);
  }
  require(total > 0, "positive calibrated sample allocations required");
  std::printf("sample_measured=kind:%d variant:%d retention:%d allocations:%d\n", kind, variant,
              retention_only, total);
  int consumed_calls = 0;
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    Tracker tracker;
    Fixture fixture(kind, variant, tracker);
    const auto start = fixture.manager.current();
    std::printf("sample_inject=ordinal:%d\n", ordinal);
    inject(ordinal, [&] { fixture.output = fixture.run(); });
    fixture.borrowed_unchanged();
    if (!retention_only) {
      fixture.unchanged();
      const auto next = fixture.manager.current();
      if (ordinal == total - 1) {
        require(next == start + requests,
                "last denied allocation occurs after all sample ID requests");
        std::printf("sample_return_edge=kind:%d variant:%d ordinal:%d requests:%lu preserved:1\n",
                    kind, variant, ordinal, requests);
      }
      if (next > start)
        ++consumed_calls;
      require(next >= start && next <= start + fixture.selected.size(),
              "IDs consumed before failure remain consumed within the observed request bound");
      fixture.output = fixture.run();
      fixture.built(static_cast<unsigned long>(next), false);
    }
  }
  if (!retention_only && variant != 7)
    require(consumed_calls > 0 && consumed_calls < total,
            "consumed and unconsumed ID failure controls");
  std::printf(
      "sample_failure_sites=kind:%d variant:%d retention:%d denied:%d/%d retry:%d consumed:%d\n",
      kind, variant, retention_only, total, total, !retention_only, consumed_calls);
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
  else if (std::strcmp(mode, "use-after-free") == 0) {
    auto* p = new PointAdaptive(1, 2, 3);
    delete p;
    std::printf("expired=%g\n", p->GetX());
  } else if (std::strcmp(mode, "leak") == 0)
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (scenario(mode, "failure-", kind, variant) && true)
      failures(kind, variant, false);
    else if (scenario(mode, "retention-", kind, variant) && variant == 0)
      failures(kind, variant, true);
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
