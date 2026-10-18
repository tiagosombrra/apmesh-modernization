#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <memory>
#include <new>
#include <set>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/curve/curve_adaptive_parametric_hermite.h"
#include "data/geometry.h"
#include "data/mesh/sub_mesh.h"
#include "generator/curve_snapshots.h"

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;

namespace {
using apmesh::generation::CurvePointSnapshot;
using apmesh::generation::CurveSnapshots;
void require(bool condition, const char* message) {
  if (!condition) {
    // A broken original may leave dangling lists. Stop before consuming them;
    // an aborted contract case does not establish a CRT retention measurement.
    std::fprintf(stderr, "Contract failed: %s\n", message);
    std::exit(1);
  }
}
struct Tracker {
  std::array<bool, 4> alive{};
  int destroyed = 0;
};
class CountedNode : public NodeAdaptive {
public:
  CountedNode(const CurvePointSnapshot& p, unsigned int slot, Tracker& tracker)
      : NodeAdaptive(p.x, p.y, p.z, p.id), slot_(slot), tracker_(tracker) {
    tracker_.alive[slot_] = true;
  }
  ~CountedNode() override {
    tracker_.alive[slot_] = false;
    ++tracker_.destroyed;
  }

private:
  unsigned int slot_;
  Tracker& tracker_;
};
bool equal(const CurveSnapshots& a, const CurveSnapshots& b) {
  if (a.size() != b.size())
    return false;
  for (std::size_t i = 0; i < a.size(); ++i) {
    if (a[i].size() != b[i].size())
      return false;
    for (std::size_t j = 0; j < a[i].size(); ++j) {
      const auto& x = a[i][j];
      const auto& y = b[i][j];
      if (x.id != y.id || x.x != y.x || x.y != y.y || x.z != y.z)
        return false;
    }
  }
  return true;
}
struct Fixture {
  int kind, variant;
  Tracker& tracker;
  const unsigned int curve_count;
  std::array<CountedNode*, 4> original{};
  std::vector<std::list<PointAdaptive*>> original_lists;
  std::vector<std::vector<PointAdaptive* const*>> original_nodes;
  std::unique_ptr<SubMesh> mesh;
  std::array<NodeAdaptive*, 3> mesh_nodes{};
  TriangleAdaptive* triangle = nullptr;
  CurveSnapshots target;
  Geometry geometry;
  CurvePointSnapshot record(unsigned int i) const {
    return {static_cast<unsigned long>(variant == 1 && i == 3 ? 41 : 40 + i), (i + 1) * 0.5,
            -static_cast<double>(i), static_cast<double>(i * i)};
  }
  Fixture(int curve_kind, int layout, Tracker& counts)
      : kind(curve_kind), variant(layout), tracker(counts), curve_count(variant == 4 ? 1U : 3U) {
    for (unsigned int i = 0; i < curve_count; ++i) {
      std::unique_ptr<CurveAdaptive> curve;
      const PointAdaptive first_point(0, 0, 0), last_point(1, 0, 0);
      if (kind == 0)
        curve = std::make_unique<CurveAdaptive>();
      else if (kind == 1) {
        auto p = std::make_unique<CurveAdaptiveParametric>(first_point, last_point);
        Matrix4x1 coefficients;
        coefficients << 0, 0, 1, 0;
        p->SetMatGeoGx(coefficients);
        p->CalculateLengthCurve();
        curve = std::move(p);
      } else if (kind == 2)
        curve = std::make_unique<CurveAdaptiveParametricBezier>(
            first_point, PointAdaptive(1.0 / 3, 0, 0), PointAdaptive(2.0 / 3, 0, 0), last_point);
      else
        curve = std::make_unique<CurveAdaptiveParametricHermite>(
            first_point, last_point, VectorAdaptive(1, 0, 0), VectorAdaptive(1, 0, 0));
      curve->SetId(70 + i);
      if (auto* parametric = dynamic_cast<CurveAdaptiveParametric*>(curve.get()))
        parametric->UpdateParameters({1, 0.5, 0});
      geometry.InsertCurve(std::move(curve));
    }
    target = variant == 4 ? CurveSnapshots{{record(0)}}
                          : CurveSnapshots{{record(0), record(1), record(2)},
                                           {record(2), record(1), record(3)},
                                           {record(3), record(0), record(3)}};
    if (variant < 3) {
      for (unsigned int i = 0; i < 4; ++i) {
        original[i] = new CountedNode(record(i), i, tracker);
        original[i]->SetX(original[i]->GetX() + 10);
        original[i]->SetGa(7);
        original[i]->SetGd(8);
        original[i]->SetHa(9);
        original[i]->SetHd(10);
      }
      const std::array<std::array<unsigned int, 3>, 3> indices{{{0, 1, 2}, {2, 1, 3}, {3, 0, 3}}};
      for (unsigned int i = 0; i < 3; ++i)
        for (unsigned int j : indices[i])
          geometry.GetCurve(i)->InsertPoint(original[j]);
    }
    if (variant == 2)
      target = CurveSnapshots(curve_count);
    mesh = std::make_unique<SubMesh>();
    for (unsigned int i = 0; i < 3; ++i) {
      NodeAdaptive point(static_cast<double>(i), i == 2 ? 1.0 : 0.0, 0, 500 + i);
      point.SetGa(20 + i);
      mesh->SetNoh(&point);
      mesh_nodes[i] = mesh->GetNoh(i);
    }
    triangle = new TriangleAdaptive(mesh_nodes[0], mesh_nodes[1], mesh_nodes[2]);
    mesh->SetElement(triangle);
    for (auto* point : original)
      if (point)
        point->InsertElement(triangle);
    for (unsigned int i = 0; i < curve_count; ++i) {
      original_lists.push_back(geometry.GetCurve(i)->GetPoints());
      std::vector<PointAdaptive* const*> nodes;
      for (const auto& p : geometry.GetCurve(i)->GetPoints())
        nodes.push_back(std::addressof(p));
      original_nodes.push_back(std::move(nodes));
    }
  }
  ~Fixture() {
    std::set<PointAdaptive*> unique;
    for (unsigned int i = 0; i < curve_count; ++i) {
      for (auto* p : geometry.GetCurve(i)->GetPoints())
        unique.insert(p);
      geometry.GetCurve(i)->GetPoints().clear();
    }
    for (auto* p : unique)
      delete p;
  }
  void metadata() {
    for (unsigned int i = 0; i < curve_count; ++i) {
      auto* curve = geometry.GetCurve(i);
      require(curve->GetId() == 70 + i, "curve identity is unchanged");
      if (auto* p = dynamic_cast<CurveAdaptiveParametric*>(curve)) {
        require(p->parameters_ == std::list<double>({1, 0.5, 0}),
                "sample restoration does not change parameter lists");
        const auto x = p->FindPointByParameter(0.25);
        const auto d = p->CalculateGradientByParameter(0.25);
        require(std::abs(x.GetX() - 0.25) < 1e-12 && x.GetY() == 0 && x.GetZ() == 0 &&
                    std::abs(d.GetX() - 1) < 1e-12,
                "curve evaluator is unchanged");
      }
    }
    for (unsigned int i = 0; i < 3; ++i)
      require(mesh->GetNoh(i) == mesh_nodes[i] && mesh_nodes[i]->GetId() == 500 + i &&
                  mesh_nodes[i]->GetX() == i && mesh_nodes[i]->GetGa() == 20 + i &&
                  mesh_nodes[i]->GetNumberElements() == 1 &&
                  mesh_nodes[i]->GetElement(0) == triangle,
              "accepted mesh copies and adjacency remain alive and unchanged");
  }
  void unchanged() {
    require(tracker.destroyed == 0, "failed restoration destroyed live samples");
    for (unsigned int i = 0; i < curve_count; ++i) {
      auto& points = geometry.GetCurve(i)->GetPoints();
      require(points == original_lists[i], "failed operation changed a live point list");
      unsigned int j = 0;
      for (const auto& p : points)
        require(std::addressof(p) == original_nodes[i][j++],
                "failed operation changed live list-element identity");
    }
    if (variant < 3)
      for (unsigned int i = 0; i < 4; ++i) {
        require(tracker.alive[i], "old sample is alive before inspecting its values");
        auto* p = original[i];
        auto expected = record(i);
        require(p->GetId() == expected.id && p->GetX() == expected.x + 10 &&
                    p->GetY() == expected.y && p->GetZ() == expected.z && p->GetGa() == 7 &&
                    p->GetGd() == 8 && p->GetHa() == 9 && p->GetHd() == 10 &&
                    p->GetNumberElements() == 1 && p->GetElement(0) == triangle,
                "failed operation preserves live sample scalar/adjacency state");
      }
    metadata();
  }
  CurveSnapshots expected_capture() const {
    if (variant >= 3)
      return CurveSnapshots(curve_count);
    CurveSnapshots result{{record(0), record(1), record(2)},
                          {record(2), record(1), record(3)},
                          {record(3), record(0), record(3)}};
    for (auto& row : result)
      for (auto& p : row)
        p.x += 10;
    return result;
  }
  void restored(bool trace) {
    require(tracker.destroyed == (variant < 3 ? 4 : 0),
            "successful restore destroys each distinct old object once");
    std::map<unsigned long, CurvePointSnapshot> first;
    for (const auto& row : target)
      for (const auto& p : row)
        first.emplace(p.id, p);
    std::map<unsigned long, PointAdaptive*> identity;
    for (unsigned int i = 0; i < curve_count; ++i) {
      auto& points = geometry.GetCurve(i)->GetPoints();
      require(points.size() == target[i].size(), "restored point counts match the snapshot");
      auto p = points.begin();
      for (std::size_t j = 0; j < target[i].size(); ++j, ++p) {
        auto* point = *p;
        auto expected = first.at(target[i][j].id);
        require(point->GetId() == expected.id && point->GetX() == expected.x &&
                    point->GetY() == expected.y && point->GetZ() == expected.z,
                "first-encounter ID/XYZ restoration policy is preserved");
        auto [it, inserted] = identity.emplace(expected.id, point);
        require(inserted || it->second == point,
                "the same snapshot ID reuses one physical node across lists");
        auto* node = dynamic_cast<NodeAdaptive*>(point);
        require(node && node->GetGa() == 0 && node->GetGd() == 0 && node->GetHa() == 0 &&
                    node->GetHd() == 0 && node->GetNumberElements() == 0,
                "restored NodeAdaptive has the original zero curvature/adjacency initialization");
        if (trace)
          std::printf(
              "snapshot_point=kind:%d variant:%d curve:%u point:%zu id:%lu x:%a y:%a z:%a\n", kind,
              variant, i, j, point->GetId(), point->GetX(), point->GetY(), point->GetZ());
      }
    }
    require(identity.size() == first.size(),
            "positive ID reuse coverage is nonempty for populated snapshots");
    metadata();
    if (trace)
      std::printf("snapshot_restore=kind:%d variant:%d unique:%zu old-destroyed:%d mesh:1 "
                  "parameters:unchanged\n",
                  kind, variant, identity.size(), tracker.destroyed);
  }
};
void normal(int kind, int variant) {
  Tracker tracker;
  {
    Fixture fixture(kind, variant, tracker);
    apmesh::generation::RestoreCurveSnapshots(&fixture.geometry, fixture.target);
    fixture.restored(true);
    apmesh::generation::RestoreCurveSnapshots(&fixture.geometry, fixture.target);
    fixture.restored(false);
  }
  require(tracker.destroyed == (variant < 3 ? 4 : 0),
          "old samples are destroyed exactly once across repeated restoration");
}
void capture(int kind, int variant) {
  Tracker tracker;
  Fixture fixture(kind, variant, tracker);
  auto value = apmesh::generation::CaptureCurveSnapshots(&fixture.geometry);
  require(equal(value, fixture.expected_capture()),
          "capture preserves each ordered ID/XYZ including duplicate-ID coordinates");
  fixture.unchanged();
  std::printf("snapshot_capture=kind:%d variant:%d curves:%zu references:9 unchanged:1\n", kind,
              variant, value.size());
}
void guards() {
  require(apmesh::generation::CaptureCurveSnapshots(nullptr).empty(), "null capture remains empty");
  apmesh::generation::RestoreCurveSnapshots(nullptr, {});
  Geometry empty;
  require(apmesh::generation::CaptureCurveSnapshots(&empty).empty(), "empty capture remains empty");
  apmesh::generation::RestoreCurveSnapshots(&empty, {});
  Tracker tracker;
  Fixture fixture(0, 0, tracker);
  apmesh::generation::RestoreCurveSnapshots(&fixture.geometry, {});
  fixture.unchanged();
  std::puts("snapshot_guards=null:1 empty:1 count-mismatch:1");
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
void failures(int kind, int variant, bool capture_only) {
  int total = 0;
  {
    Tracker tracker;
    Fixture fixture(kind, variant, tracker);
    {
      AllocationScope hook(-1);
      if (capture_only) {
        auto value = apmesh::generation::CaptureCurveSnapshots(&fixture.geometry);
      } else
        apmesh::generation::RestoreCurveSnapshots(&fixture.geometry, fixture.target);
      total = attempts;
    }
    if (capture_only)
      fixture.unchanged();
    else
      fixture.restored(false);
  }
  require(total > 0, "failure sweep requires positive observed allocations");
  std::printf("snapshot_measured=kind:%d variant:%d capture:%d allocations:%d\n", kind, variant,
              capture_only, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    Tracker tracker;
    Fixture fixture(kind, variant, tracker);
    std::printf("snapshot_inject=ordinal:%d\n", ordinal);
    inject(ordinal, [&] {
      if (capture_only) {
        auto value = apmesh::generation::CaptureCurveSnapshots(&fixture.geometry);
      } else
        apmesh::generation::RestoreCurveSnapshots(&fixture.geometry, fixture.target);
    });
    fixture.unchanged();
    if (capture_only) {
      auto retry = apmesh::generation::CaptureCurveSnapshots(&fixture.geometry);
      require(equal(retry, fixture.expected_capture()), "capture retry completes unchanged");
      fixture.unchanged();
    } else {
      apmesh::generation::RestoreCurveSnapshots(&fixture.geometry, fixture.target);
      fixture.restored(false);
    }
  }
  std::printf(
      "snapshot_failure_sites=kind:%d variant:%d capture:%d denied:%d/%d unchanged:1 retry:1\n",
      kind, variant, capture_only, total, total);
}
#endif
bool scenario(const char* mode, const char* prefix, int& kind, int& variant) {
  auto n = std::strlen(prefix);
  if (std::strlen(mode) != n + 3 || std::strncmp(mode, prefix, n) != 0 || mode[n] < '0' ||
      mode[n] > '3' || mode[n + 1] != '-' || mode[n + 2] < '0' || mode[n + 2] > '4')
    return false;
  kind = mode[n] - '0';
  variant = mode[n + 2] - '0';
  return true;
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
    for (int k = 0; k < 4; ++k) {
      for (int v = 0; v < 5; ++v)
        normal(k, v);
      for (int v = 0; v < 2; ++v)
        capture(k, v);
    }
    guards();
  } else if (scenario(mode, "normal-", kind, variant))
    normal(kind, variant);
  else if (scenario(mode, "capture-", kind, variant) && variant < 2)
    capture(kind, variant);
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
      failures(kind, variant, false);
    else if (scenario(mode, "capture-failure-", kind, variant) && variant < 2)
      failures(kind, variant, true);
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
