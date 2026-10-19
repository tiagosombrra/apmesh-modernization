#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <limits>
#include <list>
#include <new>
#include <stdexcept>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/curve/curve_adaptive.h"
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/geometry.h"
#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/patch/patch_bezier.h"
#include "data/triangle_adaptive.h"
#include "generator/curve_sample_lifetime.h"
#include "estimate/initial_mesh_estimate.h"

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
  int shape, layout, degree;
  Fixture(int surface, int mask, int subdivisions)
      : shape(surface), layout(mask), degree(subdivisions) {
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
  const int degree = fixture.degree;
  const unsigned int grid = (degree + 1) * (degree + 1);
  const unsigned int centers = degree * degree;
  Require(mesh.GetNumberNos() == grid + centers && mesh.GetNumberElements() == 4 * centers,
          "analytic grid/center/triangle counts");
  Require(mesh.GetPatch() == fixture.patch && fixture.patch->GetSubMesh() == &mesh,
          "only completed mesh publishes the patch observer");
  for (unsigned int i = 0; i < grid + centers; ++i) {
    const bool center = i >= grid;
    const unsigned int local = center ? i - grid : i;
    const unsigned int width = center ? degree : degree + 1;
    const double u = (local % width + (center ? 0.5 : 0.0)) / degree;
    const double v = (local / width + (center ? 0.5 : 0.0)) / degree;
    auto* node = mesh.GetNoh(i);
    // Preserve the historical center ID: the temporary receives its ID after copying.
    Require(node->GetId() == (center ? static_cast<unsigned long>(-1) : i + 1),
            "ordered grid IDs and historical center IDs");
    Require(std::abs(node->GetX() - u) < 1e-12 && std::abs(node->GetY() - v) < 1e-12 &&
                std::abs(node->GetZ() - (fixture.shape == 0 ? 0 : 0.25 * u * v)) < 1e-12,
            "independent planar/bilinear analytic coordinates");
    Require(node->GetGa() == 0 && node->GetGd() == 0 && node->GetHa() == 0 && node->GetHd() == 0,
            "initial curvature fields remain zero");
    if (trace)
      std::printf("estimate_node=index:%u id:%lu xyz:%.17g,%.17g,%.17g adjacency:%u\n", i,
                  node->GetId(), node->GetX(), node->GetY(), node->GetZ(),
                  node->GetNumberElements());
  }
  double area = 0;
  for (unsigned int cell = 0; cell < centers; ++cell) {
    const unsigned int first = (cell / degree) * (degree + 1) + cell % degree;
    const unsigned int last = first + degree + 1;
    const unsigned int center = grid + cell;
    const std::array<std::array<unsigned int, 3>, 4> indices{{{first, first + 1, center},
                                                              {first + 1, last + 1, center},
                                                              {last + 1, last, center},
                                                              {last, first, center}}};
    for (unsigned int side = 0; side < 4; ++side) {
      const unsigned int index = 4 * cell + side;
      auto* triangle = static_cast<TriangleAdaptive*>(mesh.GetElement(index));
      Require(triangle->GetId() == index + 1, "ordered triangle IDs");
      const std::array<std::tuple<double, double>, 3> uv{
          triangle->GetParametersN1(), triangle->GetParametersN2(), triangle->GetParametersN3()};
      for (unsigned int corner = 0; corner < 3; ++corner) {
        auto* expected = mesh.GetNoh(indices[side][corner]);
        const auto vertex = triangle->GetNoh(corner + 1);
        Require(vertex.GetId() == expected->GetId() && vertex.GetX() == expected->GetX() &&
                    vertex.GetY() == expected->GetY() && vertex.GetZ() == expected->GetZ(),
                "ordered vertex values from the public copying accessor");
        Require(std::count(expected->GetElements().begin(), expected->GetElements().end(),
                           triangle) == 1,
                "exact triangle identity registered in its physical node");
        // These fixtures have identity x/y parameterization. The existing solver
        // damps an exact parameter step by 0.65 and may stop below a 1e-5 step.
        // Its remaining analytic error is at most (1 - 0.65) * 1e-5 plus roundoff.
        constexpr double inverse_error_bound = (1.0 - 0.65) * 1e-5 + 1e-12;
        Require(std::abs(std::get<0>(uv[corner]) - expected->GetX()) <= inverse_error_bound &&
                    std::abs(std::get<1>(uv[corner]) - expected->GetY()) <= inverse_error_bound,
                "inverse UV meets the existing damped-step analytic bound");
      }
      Require(triangle->GetArea() > 0, "positive triangle area");
      area += triangle->GetArea();
      if (trace)
        std::printf("estimate_triangle=index:%u id:%lu vertices:%u,%u,%u area:%.17g "
                    "uv:%.17g,%.17g;%.17g,%.17g;%.17g,%.17g\n",
                    index, triangle->GetId(), indices[side][0], indices[side][1], indices[side][2],
                    triangle->GetArea(), std::get<0>(uv[0]), std::get<1>(uv[0]), std::get<0>(uv[1]),
                    std::get<1>(uv[1]), std::get<0>(uv[2]), std::get<1>(uv[2]));
    }
  }
  if (fixture.shape == 0)
    Require(std::abs(area - 1.0) < 1e-12, "independent planar unit area");
  for (unsigned int i = 0; i < 4; ++i) {
    const auto& points = fixture.geometry.GetCurve(i)->GetPoints();
    const bool seeded = fixture.layout == 2 || (fixture.layout == 1 && i % 2 == 0) ||
                        (fixture.layout == 3 && i % 2 == 1);
    Require(points.size() == (seeded ? 2 : degree + 1), "curve sample count");
    if (seeded)
      Require(points.front()->GetId() == 500 + i && points.back()->GetId() == 600 + i,
              "preexisting sample identity and ordering");
    for (auto* point : points) {
      for (unsigned int n = 0; n < grid + centers; ++n)
        Require(point != mesh.GetNoh(n), "distinct curve samples and physical node owners");
      if (trace)
        std::printf("estimate_sample=curve:%u id:%lu xyz:%.17g,%.17g,%.17g\n", i, point->GetId(),
                    point->GetX(), point->GetY(), point->GetZ());
    }
  }
}

void Operation(Fixture& fixture, bool trace) {
  apmesh::generation::CurveSampleLifetime samples(fixture.geometry);
  std::unique_ptr<SubMesh> mesh;
  try {
    mesh = apmesh::estimation::BuildInitialEstimateSubMesh(fixture.patch, fixture.degree);
  } catch (...) {
    Require(fixture.patch->GetSubMesh() == &fixture.previous,
            "failed construction preserves the prior patch observer");
    throw;
  }
  if (trace)
    Validate(fixture, *mesh, true);
  fixture.patch->SetSubMesh(&fixture.previous);
  samples.Release();
  Require(mesh->GetNumberNos() > 0 && mesh->GetNumberElements() > 0,
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
bool Failures(int shape, int layout, int degree) {
  int total = 0;
  {
    Fixture fixture(shape, layout, degree);
    AllocationScope hook(-1);
    Operation(fixture, false);
    total = attempts;
  }
  Require(total > 0, "positive actual-construction allocation calibration");
  std::printf("estimate_measured=shape:%d layout:%d degree:%d allocations:%d\n", shape, layout,
              degree, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    bool caught = false;
    {
      Fixture fixture(shape, layout, degree);
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
    }
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    std::printf("estimate_denied=shape:%d layout:%d degree:%d ordinal:%d retained:%zu\n", shape,
                layout, degree, ordinal, delta.lCounts[_NORMAL_BLOCK]);
    if (delta.lCounts[_NORMAL_BLOCK] != 0)
      return false;
  }
  std::printf("estimate_failure_sites=shape:%d layout:%d degree:%d denied:%d/%d\n", shape, layout,
              degree, total, total);
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
  int shape = -1, layout = -1, degree = -1;
  if (std::strcmp(argv[1], "contracts") == 0) {
    for (int s = 0; s < 2; ++s)
      for (int l = 0; l < 4; ++l) {
        for (int d : {1, 2, 4}) {
          Fixture fixture(s, l, d);
          Operation(fixture, true);
        }
      }
  } else if (std::sscanf(argv[1], "normal-%d-%d-%d", &shape, &layout, &degree) == 3 && shape >= 0 &&
             shape < 2 && layout >= 0 && layout < 4 &&
             (degree == 1 || degree == 2 || degree == 4)) {
    Fixture fixture(shape, layout, degree);
    Operation(fixture, true);
  } else if (std::strcmp(argv[1], "invalid-degree") == 0) {
    Fixture fixture(1, 1, 1);
    std::array<std::list<PointAdaptive*>, 4> before;
    for (unsigned int i = 0; i < 4; ++i)
      before[i] = fixture.patch->GetCurve(i)->GetPoints();
    for (int invalid : {0, -1, std::numeric_limits<int>::min()}) {
      bool caught = false;
      try {
        auto mesh = apmesh::estimation::BuildInitialEstimateSubMesh(fixture.patch, invalid);
      } catch (const std::invalid_argument&) {
        caught = true;
      }
      Require(caught, "nonpositive degree rejected before construction");
      Require(fixture.patch->GetSubMesh() == &fixture.previous,
              "invalid degree preserves patch observer");
      for (unsigned int i = 0; i < 4; ++i)
        Require(before[i] == fixture.patch->GetCurve(i)->GetPoints(),
                "invalid degree preserves curve samples");
      std::printf("estimate_degree_guard=degree:%d unchanged:1\n", invalid);
    }
    apmesh::generation::CurveSampleLifetime samples(fixture.geometry);
  } else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  } else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::sscanf(argv[1], "failure-%d-%d-%d", &shape, &layout, &degree) == 3 && shape >= 0 &&
        shape < 2 && layout >= 0 && layout < 4 && (degree == 1 || degree == 2 || degree == 4))
      passed = Failures(shape, layout, degree);
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
