#include <array>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "crab_mesh/performer/ranged_id_manager.h"
#include "data/curve/curve_adaptive.h"
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/geometry.h"
#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/patch/patch_bezier.h"
#include "data/triangle_adaptive.h"
#include "generator/curve_sample_lifetime.h"
#include "generator/initial_mesh.h"

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void Require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Initial mesh contract failed: %s\n", message);
    std::exit(1);
  }
}

struct Fixture {
  Geometry geometry;
  SubMesh previous;
  PatchBezier* patch;
  Performer::RangedIdManager manager{0, 0, 100000, 100000, 2};
  int shape, layout;
  Fixture(int surface, int mask) : shape(surface), layout(mask) {
    manager.setId(100);
    manager.setId(1, 200);
    std::array<PointAdaptive, 16> points;
    for (int index = 0; index < 16; ++index) {
      const double u = (index / 4) / 3.0;
      const double v = (index % 4) / 3.0;
      points[index] = PointAdaptive(u, v, surface == 0 ? 0 : 0.25 * u * v);
    }
    auto value = std::make_unique<PatchBezier>(
        points[0], points[1], points[2], points[3], points[4], points[5], points[6], points[7],
        points[8], points[9], points[10], points[11], points[12], points[13], points[14],
        points[15], mask == 0, mask == 0, mask == 0, mask == 0);
    patch = value.get();
    for (unsigned int i = 0; i < 4; ++i) {
      auto* curve = patch->GetCurve(i);
      geometry.InsertCurve(curve);
      if (mask == 2 || (mask == 1 && i % 2 == 0) || (mask == 3 && i % 2 == 1)) {
        auto* bezier = static_cast<CurveAdaptiveParametricBezier*>(curve);
        auto first = std::make_unique<NodeAdaptive>(bezier->GetPoint0());
        auto second = std::make_unique<NodeAdaptive>(bezier->GetPoint3());
        first->SetId(500 + i);
        second->SetId(600 + i);
        curve->InsertPoint(first.get());
        first.release();
        curve->InsertPoint(second.get());
        second.release();
      }
    }
    geometry.InsertPatch(std::move(value));
    patch->SetSubMesh(&previous);
  }
};

void Validate(Fixture& fixture, SubMesh& mesh, bool trace) {
  Require(mesh.GetNumberNos() == 5 && mesh.GetNumberElements() == 4,
          "five copied physical nodes and four triangles");
  Require(mesh.GetPatch() == fixture.patch && fixture.patch->GetSubMesh() == &mesh,
          "patch and completed mesh observers agree");
  const std::array<std::array<double, 2>, 5> uv{{{0, 0}, {1, 0}, {0, 1}, {1, 1}, {0.5, 0.5}}};
  for (unsigned int i = 0; i < 5; ++i) {
    auto* node = mesh.GetNoh(i);
    Require(node->GetId() == 100 + i, "ordered node-channel ID requests");
    Require(
        std::abs(node->GetX() - uv[i][0]) < 1e-12 && std::abs(node->GetY() - uv[i][1]) < 1e-12 &&
            std::abs(node->GetZ() - (fixture.shape == 0 ? 0 : 0.25 * uv[i][0] * uv[i][1])) < 1e-12,
        "independent planar/bilinear analytic coordinates");
    Require(node->GetGa() == 0 && node->GetGd() == 0 && node->GetHa() == 0 && node->GetHd() == 0,
            "initial curvature fields remain zero");
    if (trace)
      std::printf("initial_node=index:%u id:%lu xyz:%.17g,%.17g,%.17g adjacency:%u\n", i,
                  node->GetId(), node->GetX(), node->GetY(), node->GetZ(),
                  node->GetNumberElements());
  }
  const std::array<std::array<unsigned int, 3>, 4> indices{
      {{0, 1, 4}, {1, 3, 4}, {3, 2, 4}, {2, 0, 4}}};
  for (unsigned int i = 0; i < 4; ++i) {
    auto* triangle = static_cast<TriangleAdaptive*>(mesh.GetElement(i));
    Require(triangle->GetId() == 200 + i, "ordered element-channel ID requests");
    const std::array<std::tuple<double, double>, 3> parameters{
        triangle->GetParametersN1(), triangle->GetParametersN2(), triangle->GetParametersN3()};
    for (unsigned int corner = 0; corner < 3; ++corner) {
      Require(triangle->GetNoh(corner + 1).GetId() == mesh.GetNoh(indices[i][corner])->GetId(),
              "ordered physical-node IDs on every triangle");
      Require(std::get<0>(parameters[corner]) == uv[indices[i][corner]][0] &&
                  std::get<1>(parameters[corner]) == uv[indices[i][corner]][1],
              "ordered triangle parametric coordinates");
    }
    Require(triangle->GetArea() > 0, "positive coarse triangle area");
    if (trace)
      std::printf("initial_triangle=index:%u id:%lu vertices:%u,%u,%u area:%.17g\n", i,
                  triangle->GetId(), indices[i][0], indices[i][1], indices[i][2],
                  triangle->GetArea());
  }
  for (unsigned int i = 0; i < 4; ++i) {
    const auto& points = fixture.geometry.GetCurve(i)->GetPoints();
    Require(points.size() == 2, "each coarse curve has two samples");
    const bool seeded = fixture.layout == 2 || (fixture.layout == 1 && i % 2 == 0) ||
                        (fixture.layout == 3 && i % 2 == 1);
    if (seeded) {
      Require(points.front()->GetId() == 500 + i && points.back()->GetId() == 600 + i,
              "preexisting curve samples keep identity and ordering");
    }
    for (auto* point : points) {
      for (unsigned int n = 0; n < 5; ++n)
        Require(point != mesh.GetNoh(n),
                "curve samples and physical mesh nodes have distinct owners");
      if (trace)
        std::printf("initial_sample=curve:%u id:%lu xyz:%.17g,%.17g,%.17g\n", i, point->GetId(),
                    point->GetX(), point->GetY(), point->GetZ());
    }
  }
}

void Operation(Fixture& fixture, bool trace) {
  apmesh::generation::CurveSampleLifetime samples(fixture.geometry);
  std::unique_ptr<SubMesh> mesh;
  try {
    mesh = apmesh::generation::BuildInitialSubMesh(fixture.patch, &fixture.manager);
  } catch (...) {
    Require(fixture.patch->GetSubMesh() == &fixture.previous,
            "failed construction preserves the prior patch observer");
    throw;
  }
  if (trace)
    Validate(fixture, *mesh, true);
  fixture.patch->SetSubMesh(&fixture.previous);
  samples.Release();
  Require(mesh->GetNumberNos() == 5 && mesh->GetNumberElements() == 4,
          "physical mesh survives sample release");
}

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
bool Failures(int shape, int layout) {
  int total = 0;
  {
    Fixture fixture(shape, layout);
    AllocationScope hook(-1);
    Operation(fixture, false);
    total = attempts;
  }
  Require(total > 0, "positive actual-construction allocation calibration");
  std::printf("initial_measured=shape:%d layout:%d allocations:%d\n", shape, layout, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    bool caught = false;
    unsigned long long consumed = 0;
    unsigned long long consumed_elements = 0;
    {
      Fixture fixture(shape, layout);
      const auto start = fixture.manager.current();
      const auto start_elements = fixture.manager.current(1);
      {
        AllocationScope hook(ordinal);
        try {
          Operation(fixture, false);
        } catch (const std::bad_alloc&) {
          caught = true;
        }
      }
      Require(caught && denied == 1 && attempts == ordinal + 1,
              "one denial propagates without allocating during resource destruction");
      consumed = fixture.manager.current() - start;
      consumed_elements = fixture.manager.current(1) - start_elements;
    }
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    std::printf(
        "initial_denied=shape:%d layout:%d ordinal:%d consumed:%llu elements:%llu retained:%zu\n",
        shape, layout, ordinal, consumed, consumed_elements, delta.lCounts[_NORMAL_BLOCK]);
    if (delta.lCounts[_NORMAL_BLOCK] != 0)
      return false;
  }
  std::printf("initial_failure_sites=shape:%d layout:%d denied:%d/%d\n", shape, layout, total,
              total);
  return true;
}
#endif
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
  int shape = -1, layout = -1;
  if (std::strcmp(argv[1], "contracts") == 0) {
    for (int s = 0; s < 2; ++s)
      for (int l = 0; l < 4; ++l) {
        Fixture fixture(s, l);
        Operation(fixture, true);
      }
  } else if (std::sscanf(argv[1], "normal-%d-%d", &shape, &layout) == 2 && shape >= 0 &&
             shape < 2 && layout >= 0 && layout < 4) {
    Fixture fixture(shape, layout);
    Operation(fixture, true);
  } else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  } else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::sscanf(argv[1], "failure-%d-%d", &shape, &layout) == 2 && shape >= 0 && shape < 2 &&
        layout >= 0 && layout < 4)
      passed = Failures(shape, layout);
    else {
      Require(std::strcmp(argv[1], "allocation-hook-control") == 0, "known CRT scenario");
      bool caught = false;
      {
        AllocationScope hook(0);
        try {
          auto point = std::make_unique<PointAdaptive>();
        } catch (const std::bad_alloc&) {
          caught = true;
        }
      }
      Require(caught && denied == 1 && attempts == 1, "actual allocation hook detects denial");
      std::puts("allocation_hook_control=detected");
    }
#else
    Require(false, "unknown scenario or unavailable Debug CRT hook");
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
