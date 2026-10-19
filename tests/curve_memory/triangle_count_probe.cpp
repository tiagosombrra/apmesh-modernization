#include <array>
#include <atomic>
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <memory>
#include <new>
#include <stdexcept>
#include <tuple>
#include <utility>
#include <vector>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/geometry.h"
#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/patch/patch_bezier.h"
#include "data/triangle_adaptive.h"
#include "estimate/triangle_count_estimate.h"
#include "generator/curve_sample_lifetime.h"

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void Require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Triangle count contract failed: %s\n", message);
    std::exit(1);
  }
}

struct Fixture {
  Geometry geometry;
  apmesh::generation::CurveSampleLifetime samples{geometry};
  SubMesh previous;
  std::unique_ptr<TriangleAdaptive> borrowed_parent;
  PatchBezier* patch;
  int shape, layout;

  Fixture(int surface, int mask) : shape(surface), layout(mask) {
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
    patch->SetId(42);
    patch->SetAreaTriangle(2.75);
    for (unsigned int slot = 0; slot < 4; ++slot) {
      auto* curve = static_cast<CurveAdaptiveParametricBezier*>(patch->GetCurve(slot));
      geometry.InsertCurve(curve);
      // Preserve list-node identity even when a curve's points are initially empty.
      curve->UpdateParameters({0.125, 0.625, 0.875});
      if (mask == 2 || (mask == 1 && slot % 2 == 0) || (mask == 3 && slot % 2 == 1)) {
        auto first = std::make_unique<NodeAdaptive>(curve->GetPoint0());
        auto second = std::make_unique<NodeAdaptive>(curve->GetPoint3());
        first->SetId(500 + slot);
        second->SetId(600 + slot);
        curve->InsertPoint(first.get());
        first.release();
        curve->InsertPoint(nullptr);
        curve->InsertPoint(second.get());
        second.release();
      }
    }
    geometry.InsertPatch(std::move(value));
    if (mask == 4) {
      std::array<std::unique_ptr<NodeAdaptive>, 4> corners;
      for (unsigned int i = 0; i < corners.size(); ++i) {
        corners[i] = std::make_unique<NodeAdaptive>(i % 2, i / 2, 0);
        corners[i]->SetId(700 + i);
        corners[i]->SetGa(1.25 + i);
        corners[i]->SetGd(2.25 + i);
        corners[i]->SetHa(3.25 + i);
        corners[i]->SetHd(4.25 + i);
        corners[i]->InsertElement(nullptr);
      }
      const std::array<std::array<unsigned int, 2>, 4> edges{{{0, 1}, {1, 3}, {2, 3}, {0, 2}}};
      for (unsigned int slot = 0; slot < 4; ++slot) {
        auto* curve = patch->GetCurve(slot);
        curve->InsertPoint(corners[edges[slot][0]].get());
        curve->InsertPoint(nullptr);
        curve->InsertPoint(corners[edges[slot][1]].get());
      }
      borrowed_parent =
          std::make_unique<TriangleAdaptive>(corners[0].get(), corners[1].get(), corners[2].get());
      for (auto& point : corners)
        point.release();
    }
    if (mask == 5) {
      // Repeated curve incidence and repeated sample aliases are lifetime guards.
      patch->ReplaceCurve(1, patch->GetCurve(0));
      patch->ReplaceCurve(3, patch->GetCurve(2));
    }
    previous.AddNoh(std::make_unique<NodeAdaptive>(0, 0, 0, 801));
    previous.AddNoh(std::make_unique<NodeAdaptive>(1, 0, 0, 802));
    previous.AddNoh(std::make_unique<NodeAdaptive>(0, 1, 0, 803));
    previous.AddElement(std::make_unique<TriangleAdaptive>(previous.GetNoh(0), previous.GetNoh(1),
                                                           previous.GetNoh(2)));
    previous.SetPatch(patch);
    patch->SetSubMesh(mask == 6 ? nullptr : &previous);
  }
};

struct NodeState {
  NodeAdaptive* node;
  unsigned long id;
  std::array<double, 7> scalars;
  std::vector<std::pair<ElementAdaptive* const*, ElementAdaptive*>> observers;
};
struct CurveState {
  CurveAdaptive* curve;
  std::vector<std::pair<PointAdaptive* const*, PointAdaptive*>> points;
  std::vector<std::pair<const double*, double>> parameters;
};

class Snapshot {
public:
  explicit Snapshot(Fixture& fixture) : fixture_(fixture), previous_(fixture.patch->GetSubMesh()) {
    for (unsigned int slot = 0; slot < curves_.size(); ++slot) {
      auto& saved = curves_[slot];
      saved.curve = fixture.patch->GetCurve(slot);
      for (const auto& point : saved.curve->GetPoints()) {
        saved.points.emplace_back(&point, point);
        if (point != nullptr) {
          auto* node = static_cast<NodeAdaptive*>(point);
          NodeState state{node,
                          node->GetId(),
                          {node->GetX(), node->GetY(), node->GetZ(), node->GetGa(), node->GetGd(),
                           node->GetHa(), node->GetHd()},
                          {}};
          for (const auto& observer : node->GetElements())
            state.observers.emplace_back(&observer, observer);
          nodes_.push_back(std::move(state));
        }
      }
      for (const auto& parameter : static_cast<CurveAdaptiveParametric*>(saved.curve)->parameters_)
        saved.parameters.emplace_back(&parameter, parameter);
    }
  }

  bool Matches(bool trace) const {
    const bool patch = fixture_.patch->GetSubMesh() == previous_ && fixture_.patch->GetId() == 42 &&
                       fixture_.patch->GetAreaTriangle() == 2.75;
    bool points = true, parameters = true, nodes = true;
    for (unsigned int slot = 0; slot < curves_.size(); ++slot) {
      const auto& saved = curves_[slot];
      points &= saved.curve == fixture_.patch->GetCurve(slot);
      points &= saved.curve->GetPoints().size() == saved.points.size();
      unsigned int index = 0;
      for (const auto& point : saved.curve->GetPoints()) {
        if (index >= saved.points.size()) {
          points = false;
          break;
        }
        points &= &point == saved.points[index].first && point == saved.points[index].second;
        ++index;
      }
      const auto& values = static_cast<CurveAdaptiveParametric*>(saved.curve)->parameters_;
      parameters &= values.size() == saved.parameters.size();
      index = 0;
      for (const auto& value : values) {
        if (index >= saved.parameters.size()) {
          parameters = false;
          break;
        }
        parameters &=
            &value == saved.parameters[index].first && value == saved.parameters[index].second;
        ++index;
      }
    }
    for (const auto& saved : nodes_) {
      auto* node = saved.node;
      nodes &= node->GetId() == saved.id;
      nodes &= saved.scalars == std::array<double, 7>{node->GetX(),  node->GetY(),  node->GetZ(),
                                                      node->GetGa(), node->GetGd(), node->GetHa(),
                                                      node->GetHd()};
      nodes &= node->GetElements().size() == saved.observers.size();
      unsigned int index = 0;
      for (const auto& observer : node->GetElements()) {
        if (index >= saved.observers.size()) {
          nodes = false;
          break;
        }
        nodes &=
            &observer == saved.observers[index].first && observer == saved.observers[index].second;
        ++index;
      }
    }
    const bool previous_live =
        fixture_.previous.GetNumberNos() == 3 && fixture_.previous.GetNumberElements() == 1 &&
        fixture_.previous.GetElement(0)->GetArea() == 0.5 &&
        fixture_.previous.GetNoh(0)->GetElement(0) == fixture_.previous.GetElement(0);
    if (patch && previous_ != nullptr)
      Require(fixture_.patch->GetSubMesh()->GetElement(0)->GetArea() == 0.5,
              "restored patch observer can traverse its preceding physical graph");
    if (trace)
      std::printf("count_state=patch:%d points:%d parameters:%d borrowed_nodes:%d previous_live:%d "
                  "borrowed_entries:%zu\n",
                  patch, points, parameters, nodes, previous_live, nodes_.size());
    return patch && points && parameters && nodes && previous_live;
  }

private:
  Fixture& fixture_;
  SubMesh* previous_;
  std::array<CurveState, 4> curves_{};
  std::vector<NodeState> nodes_;
};

bool Operation(Fixture& fixture, const Snapshot& before, int degree, bool trace) {
  const long result = apmesh::estimation::CountEstimateTriangles(fixture.patch, degree);
  Require(result == 4L * degree * degree, "independent analytic triangle count");
  const bool restored = before.Matches(trace);
  if (trace)
    std::printf("count_result=shape:%d layout:%d degree:%d value:%ld restored:%d\n", fixture.shape,
                fixture.layout, degree, result, restored);
  return restored;
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
  bool calibrated_state = false;
  {
    Fixture fixture(shape, layout);
    Snapshot before(fixture);
    {
      AllocationScope hook(-1);
      Require(apmesh::estimation::CountEstimateTriangles(fixture.patch, degree) ==
                  4L * degree * degree,
              "actual wrapper allocation calibration result");
      total = attempts;
    }
    calibrated_state = before.Matches(false);
  }
  Require(total > 0, "positive actual wrapper allocation calibration");
  std::printf(
      "count_measured=shape:%d layout:%d degree:%d allocations:%d calibration_restored:%d\n", shape,
      layout, degree, total, calibrated_state);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    Fixture fixture(shape, layout);
    Snapshot snapshot(fixture);
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    bool caught = false;
    {
      AllocationScope hook(ordinal);
      try {
        auto count = apmesh::estimation::CountEstimateTriangles(fixture.patch, degree);
        (void)count;
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    Require(caught && denied == 1 && attempts == ordinal + 1,
            "one denial propagates without later allocation during unwinding");
    const bool restored = snapshot.Matches(false);
    std::printf("count_denied=shape:%d layout:%d degree:%d ordinal:%d live_blocks:%td "
                "live_bytes:%td restored:%d\n",
                shape, layout, degree, ordinal,
                static_cast<std::ptrdiff_t>(delta.lCounts[_NORMAL_BLOCK]),
                static_cast<std::ptrdiff_t>(delta.lSizes[_NORMAL_BLOCK]), restored);
    if (!restored || delta.lCounts[_NORMAL_BLOCK] != 0 || delta.lSizes[_NORMAL_BLOCK] != 0)
      return false;
  }
  std::printf("count_failure_sites=shape:%d layout:%d degree:%d denied:%d/%d\n", shape, layout,
              degree, total, total);
  return calibrated_state;
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
      for (int l = 0; l < 7; ++l)
        for (int d : {1, 2, 4}) {
          Fixture fixture(s, l);
          Snapshot snapshot(fixture);
          passed &= Operation(fixture, snapshot, d, true);
        }
  } else if (std::sscanf(argv[1], "normal-%d-%d-%d", &shape, &layout, &degree) == 3 && shape >= 0 &&
             shape < 2 && layout >= 0 && layout < 7 &&
             (degree == 1 || degree == 2 || degree == 4)) {
    Fixture fixture(shape, layout);
    Snapshot snapshot(fixture);
    passed = Operation(fixture, snapshot, degree, true);
  } else if (std::sscanf(argv[1], "repeat-%d-%d", &shape, &layout) == 2 && shape >= 0 &&
             shape < 2 && layout >= 0 && layout < 7) {
    Fixture fixture(shape, layout);
    Snapshot snapshot(fixture);
    for (int d : {1, 2, 4})
      passed &= Operation(fixture, snapshot, d, true);
  } else if (std::strcmp(argv[1], "invalid-degree") == 0) {
    Fixture fixture(1, 4);
    Snapshot snapshot(fixture);
    for (int invalid : {0, -1, std::numeric_limits<int>::min()}) {
      bool caught = false;
      try {
        auto count = apmesh::estimation::CountEstimateTriangles(fixture.patch, invalid);
        (void)count;
      } catch (const std::invalid_argument&) {
        caught = true;
      }
      Require(caught && snapshot.Matches(false), "invalid degree preserves the borrowed graph");
      std::printf("count_degree_guard=degree:%d unchanged:1\n", invalid);
    }
  } else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  } else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::sscanf(argv[1], "failure-%d-%d-%d", &shape, &layout, &degree) == 3 && shape >= 0 &&
        shape < 2 && layout >= 0 && layout < 7 && (degree == 1 || degree == 2 || degree == 4))
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
