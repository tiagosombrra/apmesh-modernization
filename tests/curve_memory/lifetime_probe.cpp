#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>

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
#include "generator/curve_sample_graph.h"
#ifdef AP_MESH_SAMPLE_LIFETIME_HEADER
#include AP_MESH_SAMPLE_LIFETIME_HEADER
#else
#include "generator/curve_sample_lifetime.h"
#endif

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;

namespace {
void Require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Lifetime contract failed: %s\n", message);
    std::exit(1);
  }
}
struct Stop {};
struct Tracker {
  int created = 0, destroyed = 0;
  bool aliases_cleared = true;
};
class CountedNode : public NodeAdaptive {
public:
  CountedNode(double t, Geometry& geometry, Tracker& tracker)
      : NodeAdaptive(t, t * (1 - t), 0, 40 + tracker.created), geometry_(geometry),
        tracker_(tracker) {
    ++tracker_.created;
  }
  ~CountedNode() override {
    for (unsigned int i = 0; i < geometry_.GetNumberCurves(); ++i)
      for (auto* point : geometry_.GetCurve(i)->GetPoints())
        if (point == this)
          tracker_.aliases_cleared = false;
    ++tracker_.destroyed;
  }

private:
  Geometry& geometry_;
  Tracker& tracker_;
};

struct Fixture {
  Geometry geometry;
  SubMesh mesh;
  Performer::RangedIdManager manager{0, 0, 100000, 100000};
  int kind, variant;
  Fixture(Tracker& tracker, int type, int layout) : kind(type), variant(layout) {
    manager.setId(100);
    std::vector<std::unique_ptr<CountedNode>> pending;
    const auto node = [&](double t) {
      auto value = std::make_unique<CountedNode>(t, geometry, tracker);
      auto* result = value.get();
      pending.push_back(std::move(value));
      return result;
    };
    auto* shared_first = node(0);
    auto* shared_last = node(1);
    for (unsigned int i = 0; i < 3; ++i) {
      std::unique_ptr<CurveAdaptiveParametric> curve;
      const PointAdaptive first(0, 0, 0), endpoint(1, 0, 0);
      if (type == 0) {
        curve = std::make_unique<CurveAdaptiveParametric>(first, endpoint);
        Matrix4x1 x, y;
        x << 0, 0, 1, 0;
        y << 0, -1, 1, 0;
        curve->SetMatGeoGx(x);
        curve->SetMatGeoGy(y);
        curve->CalculateLengthCurve();
      } else if (type == 1) {
        curve = std::make_unique<CurveAdaptiveParametricBezier>(
            first, PointAdaptive(1.0 / 3, 1.0 / 3, 0), PointAdaptive(2.0 / 3, 1.0 / 3, 0),
            endpoint);
      } else {
        curve = std::make_unique<CurveAdaptiveParametricHermite>(
            first, endpoint, VectorAdaptive(1, 1, 0), VectorAdaptive(1, -1, 0));
      }
      auto* a = variant == 1 && i > 0 ? node(0) : shared_first;
      auto* b = variant == 1 && i > 0 ? node(1) : shared_last;
      curve->SetPoints({a, node(0.5), b});
      curve->UpdateParameters({0, 0.5, 1});
      geometry.InsertCurve(std::move(curve));
    }
    for (auto& value : pending)
      value.release();
    for (auto point : {PointAdaptive(0, 0, 0), PointAdaptive(1, 0, 0), PointAdaptive(0, 1, 0)}) {
      NodeAdaptive node_value(point);
      mesh.SetNoh(&node_value);
    }
    mesh.SetElement(new TriangleAdaptive(mesh.GetNoh(0), mesh.GetNoh(1), mesh.GetNoh(2)));
  }
  void Adapt(int stop) {
    apmesh::generation::CurveSampleGraphTransaction graph(&geometry);
    for (unsigned int i = 0; i < 3; ++i) {
      auto* curve = geometry.GetCurve(i);
      const auto sample = [&] {
        return apmesh::adaptation::BuildCurveSamples(curve, curve->GetPoints(),
                                                     std::list<double>{0, 0.25, 0.5, 0.75, 1},
                                                     graph.Cache(), &manager);
      };
      apmesh::generation::RefineCurveSamples(curve, graph.Cache(), sample, sample, false, 5,
                                             &manager);
      if (stop == static_cast<int>(i + 1))
        throw Stop{};
    }
    graph.Commit();
  }
  bool Empty() {
    for (unsigned int i = 0; i < geometry.GetNumberCurves(); ++i)
      if (!geometry.GetCurve(i)->GetPoints().empty())
        return false;
    return true;
  }
  void Trace() {
    for (unsigned int i = 0; i < 3; ++i) {
      const auto* curve = static_cast<CurveAdaptiveParametric*>(geometry.GetCurve(i));
      auto parameter = curve->parameters_.begin();
      for (auto* point : geometry.GetCurve(i)->GetPoints()) {
        std::printf("lifetime_point=curve:%u id:%lu t:%.17g xyz:%.17g,%.17g,%.17g\n", i,
                    point->GetId(), *parameter++, point->GetX(), point->GetY(), point->GetZ());
      }
    }
  }
  void MeshUnchanged() {
    Require(mesh.GetNumberNos() == 3 && mesh.GetNumberElements() == 1,
            "physical mesh copies remain owned independently");
    auto* triangle = static_cast<TriangleAdaptive*>(mesh.GetElement(0));
    Require(triangle->GetNoh(1) == mesh.GetNoh(0) && triangle->GetNoh(2) == mesh.GetNoh(1) &&
                triangle->GetNoh(3) == mesh.GetNoh(2) && mesh.GetNoh(1)->GetX() == 1 &&
                mesh.GetNoh(2)->GetY() == 1,
            "physical nodes and element observers survive sample release");
  }
};

#if defined(_MSC_VER) && defined(_DEBUG)
int attempts = 0, denied = 0, fail_after = -1;
int AllocationHook(int kind, void*, std::size_t, int, long, const unsigned char*, int) {
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
    previous_ = _CrtSetAllocHook(AllocationHook);
  }
  ~AllocationScope() { _CrtSetAllocHook(previous_); }
  AllocationScope(const AllocationScope&) = delete;
  AllocationScope& operator=(const AllocationScope&) = delete;

private:
  _CRT_ALLOC_HOOK previous_;
};
#endif

bool Run(const char* mode, int kind, int variant) {
  Tracker tracker;
  bool empty = false, caught = false;
  {
    Fixture fixture(tracker, kind, variant);
    if (std::strcmp(mode, "normal") == 0) {
      apmesh::generation::CurveSampleLifetime lifetime(fixture.geometry);
      fixture.Adapt(-1);
      fixture.Trace();
      lifetime.Release();
      empty = fixture.Empty();
      lifetime.Release();
    } else if (std::strcmp(mode, "abort") == 0 || std::strcmp(mode, "inner") == 0) {
      try {
        apmesh::generation::CurveSampleLifetime lifetime(fixture.geometry);
        if (std::strcmp(mode, "inner") == 0)
          fixture.Adapt(1 + variant);
        throw Stop{};
      } catch (const Stop&) {
        caught = true;
      }
      empty = fixture.Empty();
    } else {
#if defined(_MSC_VER) && defined(_DEBUG)
      AllocationScope hook(0);
      try {
        apmesh::generation::CurveSampleLifetime lifetime(fixture.geometry);
        if (std::strcmp(mode, "fault") == 0) {
          auto point = std::make_unique<PointAdaptive>();
          Require(point != nullptr, "positive allocation failure request");
        }
        lifetime.Release();
      } catch (const std::bad_alloc&) {
        caught = true;
      }
      empty = fixture.Empty();
      const bool fault = std::strcmp(mode, "fault") == 0;
      std::printf("lifetime_allocations=mode:%s attempts:%d denied:%d caught:%d\n", mode, attempts,
                  denied, caught);
      empty = empty && (fault ? (caught && attempts == 1 && denied == 1)
                              : (!caught && attempts == 0 && denied == 0));
#else
      Require(false, "actual Debug CRT allocation hook required");
#endif
    }
    fixture.MeshUnchanged();
  }
  std::printf("lifetime_result=mode:%s kind:%d variant:%d created:%d destroyed:%d "
              "empty:%d aliases_cleared:%d caught:%d\n",
              mode, kind, variant, tracker.created, tracker.destroyed, empty,
              tracker.aliases_cleared, caught);
  return empty && tracker.created > 0 && tracker.created == tracker.destroyed &&
         tracker.aliases_cleared;
}
} // namespace

int main(int argc, char** argv) {
  Require(argc == 2, "one scenario required");
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
  bool passed = true;
  int kind = -1, variant = -1;
  char mode[24]{};
  if (std::strcmp(argv[1], "contracts") == 0) {
    for (int k = 0; k < 3; ++k)
      for (int v = 0; v < 2; ++v)
        for (const auto* scenario : {"normal", "abort", "inner"})
          passed = Run(scenario, k, v) && passed;
  } else if (std::sscanf(argv[1], "%23[^-]-%d-%d", mode, &kind, &variant) == 3 && kind >= 0 &&
             kind < 3 && variant >= 0 && variant < 2) {
    Require(std::strcmp(mode, "normal") == 0 || std::strcmp(mode, "abort") == 0 ||
                std::strcmp(mode, "inner") == 0 || std::strcmp(mode, "release") == 0 ||
                std::strcmp(mode, "fault") == 0,
            "known scenario");
    passed = Run(mode, kind, variant);
  } else if (std::strcmp(argv[1], "guards") == 0) {
    Geometry empty;
    apmesh::generation::CurveSampleLifetime lifetime(empty);
    lifetime.Release();
    lifetime.Release();
    std::puts("lifetime_guard=empty_and_repeat:no_positive_coverage");
  } else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  } else {
#if defined(_MSC_VER) && defined(_DEBUG)
    Require(std::strcmp(argv[1], "allocation-hook-control") == 0, "known CRT control");
    bool caught = false;
    {
      AllocationScope hook(0);
      try {
        auto point = std::make_unique<PointAdaptive>();
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    Require(caught && attempts == 1 && denied == 1, "actual allocation hook detects failure");
    std::puts("allocation_hook_control=detected");
#else
    Require(false, "unknown scenario or unavailable CRT control");
#endif
  }
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  if (delta.lCounts[_NORMAL_BLOCK] != 0) {
    _CrtMemDumpAllObjectsSince(&before);
    passed = false;
  }
#endif
  std::puts(passed ? "PASS" : "FAIL");
  return passed ? 0 : 1;
}
