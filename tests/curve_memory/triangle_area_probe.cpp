#include <array>
#include <cmath>
#include <cstdint>
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
#include "estimate/charge_estimate_process.h"
#include "generator/curve_sample_lifetime.h"

double ESTIMATIVE_TOLERANCE = 0, MAX_TIME = 1e10, TIME_READ_FILE = 0;
std::string NAME_MODEL, NUMBER_PROCESS;

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void Require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Triangle area contract failed: %s\n", message);
    std::exit(1);
  }
}

struct Fixture {
  Timer timer;
  ChargeEstimateProcess estimate;
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
  explicit Snapshot(Fixture& fixture)
      : fixture_(fixture), previous_(fixture.patch->GetSubMesh()),
        area_before_(fixture.patch->GetAreaTriangle()) {
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

  bool Matches(bool trace) const { return MatchesArea(trace, area_before_); }

  bool MatchesArea(bool trace, double expected_area) const {
    const bool patch = fixture_.patch->GetSubMesh() == previous_ && fixture_.patch->GetId() == 42 &&
                       fixture_.patch->GetAreaTriangle() == expected_area;
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
      std::printf("area_state=patch:%d points:%d parameters:%d borrowed_nodes:%d previous_live:%d "
                  "borrowed_entries:%zu\n",
                  patch, points, parameters, nodes, previous_live, nodes_.size());
    return patch && points && parameters && nodes && previous_live;
  }

private:
  Fixture& fixture_;
  SubMesh* previous_;
  double area_before_;
  std::array<CurveState, 4> curves_{};
  std::vector<NodeState> nodes_;
};

std::uint64_t Bits(double value) {
  std::uint64_t bits = 0;
  static_assert(sizeof bits == sizeof value);
  std::memcpy(&bits, &value, sizeof bits);
  return bits;
}
struct Step {
  int degree;
  unsigned nodes, elements;
  std::uint64_t area;
};
std::array<Step, 8> steps{};
int scenario = 0, calls = 0;
struct EvaluationFailure {};
int InitialDegree(int path) { return path == 3 ? 4 : 1; }
int SelectedDegree(int path) {
  return path == 1 || path == 6 ? 2 : (path == 3 ? 4 : (path == 4 ? 0 : 1));
}
void Prepare(Fixture& fixture, int path) {
  scenario = path;
  calls = 0;
  steps = {};
  fixture.estimate.minor_error_ = 10000;
  fixture.estimate.minor_degree_ = 17;
  ESTIMATIVE_TOLERANCE = std::numeric_limits<double>::infinity();
}
bool Operation(Fixture& fixture, const Snapshot& before, int path, bool trace) {
  Prepare(fixture, path);
  const auto uv_before = FINDUV_TOTAL_CALLS.load();
  double result = 0;
  int exception = 0;
  try {
    result = fixture.estimate.CalculateAreaTriangleMedio(fixture.patch, &fixture.timer,
                                                         InitialDegree(path));
  } catch (const std::invalid_argument&) {
    exception = 1;
  } catch (const EvaluationFailure&) {
    exception = 2;
  }
#if AP_MESH_AREA_REAL_ERROR
  Require(path == 0 && exception == 0 && FINDUV_TOTAL_CALLS.load() > uv_before,
          "actual serial evaluator executes and returns through area ownership");
#else
  (void)uv_before;
  Require(exception == (path == 4 ? 1 : (path >= 5 ? 2 : 0)),
          "original exception category propagates");
  const int expected_calls = path == 1 || path == 2 || path == 3 || path == 6 ? 2 : 1;
  Require(calls == expected_calls,
          "error is evaluated before the degree cap and after each replacement");
  Require(steps[0].degree == InitialDegree(path), "initial degree reaches the predicate");
  if (expected_calls == 2)
    Require(steps[1].degree == InitialDegree(path) + 1,
            "incremental degree, no recomputation or skipped evaluation");
#endif
  Require(fixture.estimate.minor_degree_ == SelectedDegree(path) &&
              fixture.estimate.minor_error_ == 10000,
          "selected degree and unchanged minor_error survive orchestration and exceptions");
  if (exception == 0) {
    const double degree = SelectedDegree(path);
    const double slope = fixture.shape == 0 ? 0 : 0.125 / degree;
    const double analytic = std::sqrt(1 + slope * slope) / (4 * degree * degree);
    Require(Bits(result) == Bits(analytic) &&
                Bits(fixture.patch->GetAreaTriangle()) == Bits(result),
            "independent analytic first-triangle area at selected dyadic degree");
  }
  const bool restored = exception ? before.Matches(trace) : before.MatchesArea(trace, result);
  if (trace) {
    for (int i = 0; i < calls; ++i)
      std::printf("area_step=index:%d degree:%d nodes:%u elements:%u bits:%016llx\n", i,
                  steps[i].degree, steps[i].nodes, steps[i].elements,
                  static_cast<unsigned long long>(steps[i].area));
    std::printf("area_result=shape:%d layout:%d path:%d selected:%d exception:%d bits:%016llx "
                "restored:%d\n",
                fixture.shape, fixture.layout, path, fixture.estimate.minor_degree_, exception,
                static_cast<unsigned long long>(Bits(result)), restored);
  }
  return restored;
}
bool Guards(Fixture& fixture, const Snapshot& before) {
  bool restored = true;
  for (int invalid : {0, -1, std::numeric_limits<int>::min()}) {
    Prepare(fixture, 0);
    bool caught = false;
    try {
      fixture.estimate.CalculateAreaTriangleMedio(fixture.patch, &fixture.timer, invalid);
    } catch (const std::invalid_argument&) {
      caught = true;
    }
    Require(caught && calls == 0 && fixture.estimate.minor_degree_ == 17,
            "invalid degree precedes evaluation");
    const bool unchanged = before.Matches(false);
    restored &= unchanged;
    std::printf("area_guard=degree:%d restored:%d\n", invalid, unchanged);
  }
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

bool Failures(int shape, int layout, int path, int first) {
  int total = 0;
  {
    Fixture fixture(shape, layout);
    Prepare(fixture, path);
    AllocationScope hook(-1);
    fixture.estimate.CalculateAreaTriangleMedio(fixture.patch, &fixture.timer, InitialDegree(path));
    total = attempts;
  }
  Require(total > 0 && first >= 0 && first < total,
          "positive nonempty actual area allocation interval");
  std::printf("area_measured=shape:%d layout:%d path:%d allocations:%d\n", shape, layout, path,
              total);
  const int end = total - first < 32 ? total : first + 32;
  for (int ordinal = first; ordinal < end; ++ordinal) {
    Fixture fixture(shape, layout);
    Snapshot snapshot(fixture);
    Prepare(fixture, path);
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    bool caught = false;
    {
      AllocationScope hook(ordinal);
      try {
        fixture.estimate.CalculateAreaTriangleMedio(fixture.patch, &fixture.timer,
                                                    InitialDegree(path));
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    Require(caught && denied == 1 && attempts == ordinal + 1,
            "one denial propagates without allocating during unwinding");
    const bool restored = snapshot.Matches(false);
    std::printf("area_denied=shape:%d layout:%d path:%d ordinal:%d live_blocks:%td live_bytes:%td "
                "restored:%d\n",
                shape, layout, path, ordinal,
                static_cast<std::ptrdiff_t>(delta.lCounts[_NORMAL_BLOCK]),
                static_cast<std::ptrdiff_t>(delta.lSizes[_NORMAL_BLOCK]), restored);
    if (!restored || delta.lCounts[_NORMAL_BLOCK] != 0 || delta.lSizes[_NORMAL_BLOCK] != 0)
      return false;
  }
  std::printf("area_failure_range=shape:%d layout:%d path:%d first:%d end:%d total:%d\n", shape,
              layout, path, first, end, total);
  return true;
}
#endif
} // namespace

#if !AP_MESH_AREA_REAL_ERROR
bool ChargeEstimateProcess::CalculateErroEstimative(MeshAdaptive* mesh, Timer*, int degree) {
  Require(calls < static_cast<int>(steps.size()) && mesh->GetNumberSubMeshesAdaptive() == 1,
          "one live current physical graph");
  auto* submesh = mesh->GetSubMeshAdaptiveByPosition(0);
  Require(submesh->GetPatch()->GetSubMesh() == submesh, "new mesh is published before evaluation");
  steps[calls++] = {degree, submesh->GetNumberNos(), submesh->GetNumberElements(),
                    Bits(submesh->GetElement(0)->GetArea())};
  if (scenario == 1 || scenario == 6)
    minor_degree_ = degree;
  else
    minor_degree_ = SelectedDegree(scenario);
  if (scenario == 5 || (scenario == 6 && calls == 2))
    throw EvaluationFailure{};
  if (scenario == 3)
    return true;
  return (scenario == 1 || scenario == 2 || scenario == 6) && calls == 1;
}
#endif

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
  int shape = -1, layout = -1, path = -1;
  if (std::strcmp(argv[1], "contracts") == 0) {
    for (int surface = 0; surface < 2; ++surface)
      for (int mask = 0; mask < 7; ++mask) {
        Fixture fixture(surface, mask);
        Snapshot snapshot(fixture);
#if AP_MESH_AREA_REAL_ERROR
        for (int repeat = 0; repeat < 3; ++repeat)
          passed &= Operation(fixture, snapshot, 0, true);
#else
        for (int scenario_index = 0; scenario_index < 7; ++scenario_index) {
          Fixture value(surface, mask);
          Snapshot state(value);
          passed &= Operation(value, state, scenario_index, true);
        }
        passed &= Guards(fixture, snapshot);
#endif
      }
  } else if (std::sscanf(argv[1], "normal-%d-%d-%d", &shape, &layout, &path) == 3 && shape >= 0 &&
             shape < 2 && layout >= 0 && layout < 7 && path >= 0 && path < 7) {
    Fixture fixture(shape, layout);
    Snapshot snapshot(fixture);
#if AP_MESH_AREA_REAL_ERROR
    for (int repeat = 0; repeat < 3; ++repeat)
      passed &= Operation(fixture, snapshot, path, true);
#else
    passed = Operation(fixture, snapshot, path, true);
#endif
  } else if (std::sscanf(argv[1], "repeat-%d-%d", &shape, &layout) == 2 && shape >= 0 &&
             shape < 2 && layout >= 0 && layout < 7) {
    Fixture fixture(shape, layout);
    Snapshot snapshot(fixture);
    for (int index : {0, 1, 2})
      passed &= Operation(fixture, snapshot, index, true);
  } else if (std::sscanf(argv[1], "guard-%d-%d", &shape, &layout) == 2 && shape >= 0 && shape < 2 &&
             layout >= 0 && layout < 7) {
    Fixture fixture(shape, layout);
    Snapshot snapshot(fixture);
    passed = Guards(fixture, snapshot);
  } else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  } else {
#if defined(_MSC_VER) && defined(_DEBUG)
    int first = -1;
    if (std::sscanf(argv[1], "failure-%d-%d-%d-%d", &shape, &layout, &path, &first) == 4 &&
        shape >= 0 && shape < 2 && layout >= 0 && layout < 7 && path >= 0 && path < 4)
      passed = Failures(shape, layout, path, first);
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
    Require(false, "unknown scenario or unavailable CRT hook");
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
