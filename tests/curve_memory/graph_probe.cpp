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
#include "data/geometry.h"
#include "data/mesh/sub_mesh.h"
#include "data/triangle_adaptive.h"
#include "generator/curve_publication.h"
#ifdef AP_MESH_SAMPLE_GRAPH_HEADER
#include AP_MESH_SAMPLE_GRAPH_HEADER
#else
#include "generator/curve_sample_graph.h"
#endif

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
namespace {
void require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Contract failed: %s\n", message);
    std::exit(1);
  }
}
struct Stop {};
struct Tracker {
  std::array<bool, 32> alive{};
  int created = 0, destroyed = 0;
};
class CountedNode : public NodeAdaptive {
public:
  CountedNode(double t, unsigned int slot, Tracker& tracker)
      : NodeAdaptive(t, t * (1 - t), 0, 40 + slot), slot_(slot), tracker_(tracker) {
    tracker_.alive[slot] = true;
    ++tracker_.created;
  }
  ~CountedNode() override {
    tracker_.alive[slot_] = false;
    ++tracker_.destroyed;
  }

private:
  unsigned int slot_;
  Tracker& tracker_;
};
struct Sample {
  NodeAdaptive* point;
  unsigned long id;
  std::array<double, 7> values;
  std::vector<ElementAdaptive*> elements;
};
struct Fixture {
  int kind, variant, committed_curves = 0;
  bool completed = false;
  Tracker& tracker;
  Geometry geometry;
  SubMesh mesh;
  std::array<NodeAdaptive*, 3> mesh_nodes{};
  TriangleAdaptive* triangle = nullptr;
  Performer::RangedIdManager manager{0, 0, 100000, 100000};
  std::vector<std::list<PointAdaptive*>> entry_points;
  std::vector<std::list<double>> entry_parameters;
  std::vector<std::vector<PointAdaptive* const*>> point_nodes;
  std::vector<std::vector<const double*>> parameter_nodes;
  std::vector<Sample> samples;
  std::array<std::list<double>, 4> selected, surface;
  Fixture(int type, int layout, Tracker& counts) : kind(type), variant(layout), tracker(counts) {
    manager.setId(variant == 4 ? 0 : 100);
    for (unsigned int i = 0; i < 3; ++i) {
      NodeAdaptive value(i, i == 2 ? 1.0 : 0.0, 0, 500 + i);
      value.SetGa(20 + i);
      mesh.SetNoh(&value);
      mesh_nodes[i] = mesh.GetNoh(i);
    }
    triangle = new TriangleAdaptive(mesh_nodes[0], mesh_nodes[1], mesh_nodes[2]);
    mesh.SetElement(triangle);
    std::vector<std::unique_ptr<CountedNode>> pending;
    const auto node = [&](double t) {
      const auto slot = static_cast<unsigned int>(pending.size());
      auto value = std::make_unique<CountedNode>(t, slot, tracker);
      value->SetGa(7);
      value->SetGd(8);
      value->SetHa(9);
      value->SetHd(10);
      value->InsertElement(triangle);
      auto* observer = value.get();
      pending.push_back(std::move(value));
      return observer;
    };
    auto* shared_first = variant == 4 ? nullptr : node(0);
    auto* shared_last = variant == 4 ? nullptr : node(1);
    for (unsigned int i = 0; i < 4; ++i) {
      const int curve_kind = variant == 5 ? (kind + static_cast<int>(i)) % 3 : kind;
      const PointAdaptive a(0, 0, 0), b(1, 0, 0);
      std::unique_ptr<CurveAdaptiveParametric> curve;
      if (curve_kind == 0) {
        curve = std::make_unique<CurveAdaptiveParametric>(a, b);
        Matrix4x1 x, y;
        x << 0, 0, 1, 0;
        y << 0, -1, 1, 0;
        curve->SetMatGeoGx(x);
        curve->SetMatGeoGy(y);
        curve->CalculateLengthCurve();
      } else if (curve_kind == 1)
        curve = std::make_unique<CurveAdaptiveParametricBezier>(
            a, PointAdaptive(1.0 / 3, 1.0 / 3, 0), PointAdaptive(2.0 / 3, 1.0 / 3, 0), b);
      else
        curve = std::make_unique<CurveAdaptiveParametricHermite>(a, b, VectorAdaptive(1, 1, 0),
                                                                 VectorAdaptive(1, -1, 0));
      curve->SetId(70 + i);
      auto* first = variant == 4 ? node(0) : shared_first;
      auto* endpoint_last = variant == 4 ? node(1) : shared_last;
      if (variant == 2 && i == 3)
        endpoint_last = first;
      const bool two = variant == 3 && (i == 0 || i == 3);
      std::list<PointAdaptive*> points{first};
      if (!two)
        points.push_back(node(0.5));
      points.push_back(endpoint_last);
      std::list<double> parameters = two ? std::list<double>{0, 1} : std::list<double>{0, 0.5, 1};
      const bool reversed = variant == 1 && i % 2 == 1;
      if (reversed) {
        points.reverse();
        parameters.reverse();
      }
      curve->SetPoints(points);
      curve->UpdateParameters(parameters);
      selected[i] =
          reversed ? std::list<double>{1, 0.75, 0.25, 0} : std::list<double>{0, 0.25, 0.75, 1};
      surface[i] = reversed ? std::list<double>{1, 0.8, 0.5, 0.2, 0}
                            : std::list<double>{0, 0.2, 0.5, 0.8, 1};
      geometry.InsertCurve(std::move(curve));
    }
    for (auto& value : pending)
      value.release();
    CaptureEntry();
    // Exercise a later operation whose initial objects came from actual sample
    // construction, rather than the counted initial fixture nodes.
    if (variant == 5) {
      run();
      CaptureEntry();
    }
  }
  ~Fixture() {
    std::set<PointAdaptive*> unique;
    for (unsigned int i = 0; i < geometry.GetNumberCurves(); ++i)
      for (auto* point : geometry.GetCurve(i)->GetPoints())
        unique.insert(point);
    for (auto* point : unique)
      delete point;
  }
  void CaptureEntry() {
    entry_points.clear();
    entry_parameters.clear();
    point_nodes.clear();
    parameter_nodes.clear();
    samples.clear();
    std::set<PointAdaptive*> unique;
    for (unsigned int i = 0; i < 4; ++i) {
      auto* curve = static_cast<CurveAdaptiveParametric*>(geometry.GetCurve(i));
      entry_points.push_back(curve->GetPoints());
      entry_parameters.push_back(curve->parameters_);
      std::vector<PointAdaptive* const*> pnodes;
      for (const auto& point : curve->GetPoints()) {
        pnodes.push_back(std::addressof(point));
        if (unique.insert(point).second) {
          auto* n = static_cast<NodeAdaptive*>(point);
          Sample record{
              n,
              n->GetId(),
              {n->GetX(), n->GetY(), n->GetZ(), n->GetGa(), n->GetGd(), n->GetHa(), n->GetHd()},
              {}};
          for (unsigned int e = 0; e < n->GetNumberElements(); ++e)
            record.elements.push_back(n->GetElement(e));
          samples.push_back(std::move(record));
        }
      }
      point_nodes.push_back(std::move(pnodes));
      std::vector<const double*> tnodes;
      for (const auto& t : curve->parameters_)
        tnodes.push_back(std::addressof(t));
      parameter_nodes.push_back(std::move(tnodes));
    }
    completed = false;
    committed_curves = 0;
  }
  int target(unsigned int i) const { return i == 0 ? 7 : i == 1 ? 3 : 5; }
  void MeshUnchanged() {
    require(mesh.GetNumberNos() == 3 && mesh.GetNumberElements() == 1 &&
                mesh.GetElement(0) == triangle,
            "independent physical mesh ownership/observers remain unchanged");
    for (unsigned int i = 0; i < 3; ++i)
      require(mesh.GetNoh(i) == mesh_nodes[i] && mesh_nodes[i]->GetId() == 500 + i &&
                  mesh_nodes[i]->GetGa() == 20 + i && mesh_nodes[i]->GetNumberElements() == 1 &&
                  mesh_nodes[i]->GetElement(0) == triangle,
              "physical mesh scalar/adjacency state remains unchanged");
  }
  void Unchanged() {
    require(!completed, "failure cannot complete the graph operation");
    for (unsigned int i = 0; i < 4; ++i) {
      auto* curve = static_cast<CurveAdaptiveParametric*>(geometry.GetCurve(i));
      require(curve->GetId() == 70 + i && curve->GetPoints() == entry_points[i],
              "failed graph operation restores every point list and shared object");
      require(curve->parameters_ == entry_parameters[i],
              "failed graph operation restores every parameter list");
      std::size_t j = 0;
      for (const auto& point : curve->GetPoints())
        require(std::addressof(point) == point_nodes[i][j++],
                "failed graph operation restores original point list nodes");
      j = 0;
      for (const auto& t : curve->parameters_)
        require(std::addressof(t) == parameter_nodes[i][j++],
                "failed graph operation restores original parameter list nodes");
    }
    for (const auto& sample : samples) {
      auto* n = sample.point;
      require(n->GetId() == sample.id &&
                  std::array<double, 7>{n->GetX(), n->GetY(), n->GetZ(), n->GetGa(), n->GetGd(),
                                        n->GetHa(), n->GetHd()} == sample.values &&
                  n->GetNumberElements() == sample.elements.size(),
              "initial sample scalar/adjacency state remains alive and unchanged");
      for (unsigned int e = 0; e < n->GetNumberElements(); ++e)
        require(n->GetElement(e) == sample.elements[e],
                "initial sample adjacency observers remain unchanged");
    }
    MeshUnchanged();
  }
  void run(int stop = -1) {
    completed = false;
    committed_curves = 0;
    const auto destroyed_before = tracker.destroyed;
    apmesh::generation::CurveSampleGraphTransaction graph(&geometry);
    auto& cache = graph.Cache();
    if (stop == 0)
      throw Stop{};
    for (unsigned int i = 0; i < 4; ++i) {
      auto* curve = geometry.GetCurve(i);
      apmesh::generation::RefineCurveSamples(
          curve, cache,
          [&] {
            if (stop == 10 + static_cast<int>(i))
              throw Stop{};
            const auto points = curve->GetPoints();
            curve->GetPoints().reverse();
            return apmesh::adaptation::BuildCurveSamples(curve, points, selected[i], cache,
                                                         &manager);
          },
          [&] {
            if (stop == 20 + static_cast<int>(i))
              throw Stop{};
            const auto points = curve->GetPoints();
            curve->GetPoints().reverse();
            return apmesh::adaptation::BuildCurveSamples(curve, points, surface[i], cache,
                                                         &manager);
          },
          i != 3, target(i), &manager);
      ++committed_curves;
      require(tracker.destroyed == destroyed_before,
              "initial objects remain alive across committed prefixes");
      if (stop == committed_curves)
        throw Stop{};
    }
    for (unsigned int i = 0; i < 4; ++i) {
      auto* curve = geometry.GetCurve(i);
      for (auto pair : {std::make_pair(entry_points[i].front(), curve->GetPoints().front()),
                        std::make_pair(entry_points[i].back(), curve->GetPoints().back())}) {
        const auto original = cache.find(pair.first), alias = cache.find(pair.second);
        require(
            original != cache.end() && alias != cache.end() && original->second == pair.second &&
                alias->second == pair.second,
            "operation cache preserves source mappings and current endpoint aliases across curves");
      }
    }
    graph.Commit();
    completed = true;
  }
  std::string label(PointAdaptive* point) {
    for (unsigned int i = 0; i < 4; ++i) {
      unsigned int j = 0;
      for (auto* current : geometry.GetCurve(i)->GetPoints()) {
        if (current == point)
          return "C" + std::to_string(i) + "P" + std::to_string(j);
        ++j;
      }
    }
    require(false, "every final sample has a graph role");
    return {};
  }
  void Built(bool trace) {
    require(completed && committed_curves == 4 && tracker.destroyed == tracker.created,
            "complete commit retires every counted initial object exactly once");
    MeshUnchanged();
    for (unsigned int i = 0; i < 4; ++i) {
      auto* curve = static_cast<CurveAdaptiveParametric*>(geometry.GetCurve(i));
      const auto& points = curve->GetPoints();
      require(points.size() == curve->parameters_.size() &&
                  points.size() == static_cast<std::size_t>(target(i)),
              "positive final paired curve sample cardinality");
      unsigned int j = 0;
      auto t = curve->parameters_.begin();
      for (auto* point : points) {
        const double parameter = *t++;
        auto* n = static_cast<NodeAdaptive*>(point);
        if (j > 0 && j + 1 < points.size())
          require(std::abs(n->GetX() - parameter) < 1e-12 &&
                      std::abs(n->GetY() - parameter * (1 - parameter)) < 1e-12 && n->GetZ() == 0 &&
                      n->GetGa() == 0 && n->GetGd() == 0 && n->GetHa() == 0 && n->GetHd() == 0 &&
                      n->GetNumberElements() == 0,
                  "independent analytic interior geometry and zero curvature/adjacency policy");
        else
          require(n->GetNumberElements() == 1 && n->GetElement(0) == triangle,
                  "endpoint adjacency observers preserve the original copy policy");
        if (trace)
          std::printf("graph_point=curve:%u index:%u role:%s id:%lu t:%.17g xyz:%.17g,%.17g,%.17g "
                      "curvature:%.17g,%.17g,%.17g,%.17g adjacency:%u\n",
                      i, j, label(n).c_str(), n->GetId(), parameter, n->GetX(), n->GetY(),
                      n->GetZ(), n->GetGa(), n->GetGd(), n->GetHa(), n->GetHd(),
                      n->GetNumberElements());
        ++j;
      }
      for (unsigned int other = 0; other < 4; ++other)
        for (auto a : {std::make_pair(entry_points[i].front(), points.front()),
                       std::make_pair(entry_points[i].back(), points.back())})
          for (auto b : {std::make_pair(entry_points[other].front(),
                                        geometry.GetCurve(other)->GetPoints().front()),
                         std::make_pair(entry_points[other].back(),
                                        geometry.GetCurve(other)->GetPoints().back())})
            require((a.first == b.first) == (a.second == b.second),
                    "endpoint sharing is exactly source identity, including non-manifold and "
                    "closed aliases");
    }
    if (trace)
      std::printf("graph_normal=kind:%d variant:%d curves:4 old_destroyed:%d next_id:%llu\n", kind,
                  variant, tracker.destroyed, static_cast<unsigned long long>(manager.current()));
  }
  std::size_t Orphans() {
    std::set<PointAdaptive*> live;
    for (unsigned int i = 0; i < 4; ++i)
      for (auto* point : geometry.GetCurve(i)->GetPoints())
        live.insert(point);
    return static_cast<std::size_t>(
        std::count_if(samples.begin(), samples.end(),
                      [&](const auto& s) { return live.find(s.point) == live.end(); }));
  }
};
void normal(int kind, int variant) {
  Tracker tracker;
  Fixture fixture(kind, variant, tracker);
  fixture.run();
  fixture.Built(true);
  fixture.CaptureEntry();
  fixture.run();
  fixture.Built(true);
}
void abort_case(int kind, int variant, int stop, bool retention) {
  std::size_t orphaned = 0;
  {
    Tracker tracker;
    Fixture fixture(kind, variant, tracker);
    const auto start = fixture.manager.current();
    bool caught = false;
    try {
      fixture.run(stop);
    } catch (const Stop&) {
      caught = true;
    }
    require(caught, "controlled graph failure is observed");
    if (retention)
      orphaned = fixture.Orphans();
    else {
      fixture.Unchanged();
      const auto next = fixture.manager.current();
      require(next >= start && (stop == 0 ? next == start : next > start),
              "consumed IDs are preserved without rewind");
      fixture.run();
      fixture.Built(false);
    }
  }
  std::printf("graph_abort=kind:%d variant:%d stop:%d retention:%d orphaned:%zu retry:%d\n", kind,
              variant, stop, retention, orphaned, !retention);
}
void guards() {
  Geometry geometry;
  {
    apmesh::generation::CurveSampleGraphTransaction graph(&geometry);
    require(graph.Cache().empty(), "empty graph has an empty operation cache");
    graph.Commit();
  }
  try {
    apmesh::generation::CurveSampleGraphTransaction graph(&geometry);
    throw Stop{};
  } catch (const Stop&) {
  }
  std::puts("graph_guards=empty_commit_and_abort:no_positive_graph_coverage");
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
  unsigned long long requests = 0;
  {
    Tracker tracker;
    Fixture fixture(kind, variant, tracker);
    const auto start = fixture.manager.current();
    {
      AllocationScope hook(-1);
      fixture.run();
      total = attempts;
    }
    requests = fixture.manager.current() - start;
    fixture.Built(false);
  }
  require(total > 0 && requests > 0, "positive graph allocation and ID calibration required");
  std::printf("graph_measured=kind:%d variant:%d allocations:%d requests:%llu\n", kind, variant,
              total, requests);
  int prefixes = 0, consumed = 0;
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    Tracker tracker;
    Fixture fixture(kind, variant, tracker);
    const auto start = fixture.manager.current();
    std::printf("graph_inject=ordinal:%d\n", ordinal);
    inject(ordinal, [&] { fixture.run(); });
    require(attempts == ordinal + 1, "whole graph rollback performs no allocation after denial");
    fixture.Unchanged();
    const auto next = fixture.manager.current();
    require(next >= start && next <= start + requests,
            "graph failure preserves consumed ID prefix");
    if (fixture.committed_curves > 0)
      ++prefixes;
    if (next > start)
      ++consumed;
    if (ordinal == total - 1) {
      require(fixture.committed_curves == 3 && next == start + requests,
              "last denial follows three committed curves and all ID requests");
      std::printf("graph_final_edge=kind:%d variant:%d prefix:3 requests:%llu restored:1\n", kind,
                  variant, requests);
    }
    fixture.run();
    fixture.Built(false);
  }
  require(prefixes > 0 && consumed > 0 && consumed < total,
          "positive committed/uncommitted and consumed/unconsumed failure coverage");
  std::printf(
      "graph_failure_sites=kind:%d variant:%d denied:%d/%d retry:1 prefixes:%d consumed:%d\n", kind,
      variant, total, total, prefixes, consumed);
}
#endif
bool scenario(const char* mode, const char* prefix, int& kind, int& variant) {
  int consumed = 0;
  if (std::strncmp(mode, prefix, std::strlen(prefix)) != 0)
    return false;
  const auto* suffix = mode + std::strlen(prefix);
  return std::sscanf(suffix, "%d-%d%n", &kind, &variant, &consumed) == 2 &&
         suffix[consumed] == '\0' && kind >= 0 && kind < 3 && variant >= 0 && variant < 6;
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
  const auto* mode = argv[1];
  int kind = -1, variant = -1;
  if (std::strcmp(mode, "contracts") == 0) {
    for (int k = 0; k < 3; ++k)
      for (int v = 0; v < 6; ++v)
        normal(k, v);
    guards();
  } else if (scenario(mode, "normal-", kind, variant))
    normal(kind, variant);
  else if (scenario(mode, "abort-prefix-", kind, variant))
    abort_case(kind, variant, 1 + variant % 4, false);
  else if (scenario(mode, "abort-surface-", kind, variant))
    abort_case(kind, variant, 20 + variant % 4, false);
  else if (scenario(mode, "abort-before-", kind, variant))
    abort_case(kind, variant, 0, false);
  else if (scenario(mode, "retention-", kind, variant))
    abort_case(kind, variant, 1 + variant % 4, true);
  else if (std::strcmp(mode, "guards") == 0)
    guards();
  else if (std::strcmp(mode, "use-after-free") == 0) {
    auto* p = new PointAdaptive(1, 2, 3);
    delete p;
    std::printf("expired=%g\n", p->GetX());
  } else if (std::strcmp(mode, "leak") == 0)
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (scenario(mode, "failure-", kind, variant))
      failures(kind, variant);
    else if (std::strcmp(mode, "return-move-control") == 0) {
      std::list<PointAdaptive*> source{nullptr};
      inject(0, [&] { std::list<PointAdaptive*> moved(std::move(source)); });
      require(source.size() == 1 && source.front() == nullptr,
              "actual MSVC list move denial preserves its source");
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
