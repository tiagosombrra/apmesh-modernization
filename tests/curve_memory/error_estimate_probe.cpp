#include <array>
#include <atomic>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <memory>
#include <new>
#include <utility>
#include <vector>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "estimate/charge_estimate_process.h"
#include "estimate/initial_mesh_estimate.h"
#include "generator/curve_sample_lifetime.h"
#include "generator/generator_adaptive.h"

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
double ESTIMATIVE_TOLERANCE = 0, MAX_TIME = 1e10, TIME_READ_FILE = 0;
unsigned int I_MAX = 100;
std::string NAME_MODEL, NUMBER_PROCESS;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void Require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Error estimator contract failed: %s\n", message);
    std::exit(1);
  }
}

std::uint64_t Bits(double value) {
  std::uint64_t bits = 0;
  static_assert(sizeof bits == sizeof value);
  std::memcpy(&bits, &value, sizeof bits);
  return bits;
}

struct Fixture {
  Geometry geometry;
  apmesh::generation::CurveSampleLifetime samples{geometry};
  MeshAdaptive mesh;
  Timer timer;
  ChargeEstimateProcess estimate;
  int shape, degree;

  Fixture(int surface, int resolution) : shape(surface), degree(resolution) {
    if (shape == 3)
      return;
    for (int part = 0; part < (shape == 4 ? 2 : 1); ++part) {
      const int form = shape == 4 ? part + 1 : shape;
      std::array<PointAdaptive, 16> points;
      for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j) {
          const double u = i / 3.0, v = j / 3.0;
          const double z = form == 0 ? 0 : (form == 1 ? 0.25 * u * v : i * (i - 1) / 24.0);
          points[4 * i + j] = PointAdaptive(u, v, z);
        }
      auto patch = std::make_unique<PatchBezier>(
          points[0], points[1], points[2], points[3], points[4], points[5], points[6], points[7],
          points[8], points[9], points[10], points[11], points[12], points[13], points[14],
          points[15], true, true, true, true);
      for (unsigned slot = 0; slot < 4; ++slot)
        geometry.InsertCurve(patch->GetCurve(slot));
      auto submesh = apmesh::estimation::BuildInitialEstimateSubMesh(patch.get(), degree);
      geometry.InsertPatch(std::move(patch));
      mesh.InsertSubMeshAdaptive(submesh.release());
    }
  }

  ~Fixture() {
    for (unsigned i = 0; i < mesh.GetNumberSubMeshesAdaptive(); ++i)
      mesh.GetSubMeshAdaptiveByPosition(i)->GetPatch()->SetSubMesh(nullptr);
  }
};

struct NodeState {
  NodeAdaptive* node;
  std::array<std::uint64_t, 3> coordinates;
  unsigned long id;
  std::vector<std::pair<ElementAdaptive* const*, ElementAdaptive*>> adjacency;
};
class Snapshot {
public:
  explicit Snapshot(Fixture& fixture) : fixture_(fixture) {
    for (unsigned i = 0; i < fixture.mesh.GetNumberSubMeshesAdaptive(); ++i) {
      auto* submesh = fixture.mesh.GetSubMeshAdaptiveByPosition(i);
      meshes_.push_back(submesh);
      for (unsigned j = 0; j < submesh->GetNumberNos(); ++j) {
        auto* node = submesh->GetNoh(j);
        NodeState state{
            node, {Bits(node->GetX()), Bits(node->GetY()), Bits(node->GetZ())}, node->GetId(), {}};
        for (const auto& observer : node->GetElements())
          state.adjacency.emplace_back(&observer, observer);
        nodes_.push_back(std::move(state));
      }
    }
  }

  bool Matches() const {
    if (fixture_.mesh.GetNumberSubMeshesAdaptive() != meshes_.size())
      return false;
    for (unsigned i = 0; i < meshes_.size(); ++i)
      if (fixture_.mesh.GetSubMeshAdaptiveByPosition(i) != meshes_[i] ||
          meshes_[i]->GetPatch()->GetSubMesh() != meshes_[i])
        return false;
    for (const auto& state : nodes_) {
      auto* node = state.node;
      if (node->GetId() != state.id ||
          state.coordinates != std::array<std::uint64_t, 3>{Bits(node->GetX()), Bits(node->GetY()),
                                                            Bits(node->GetZ())} ||
          node->GetElements().size() != state.adjacency.size())
        return false;
      unsigned index = 0;
      for (const auto& observer : node->GetElements()) {
        if (&observer != state.adjacency[index].first || observer != state.adjacency[index].second)
          return false;
        ++index;
      }
    }
    return true;
  }

  std::vector<std::uint64_t> Curvatures() const {
    std::vector<std::uint64_t> values;
    for (const auto& state : nodes_) {
      auto* node = state.node;
      for (double value : {node->GetGa(), node->GetGd(), node->GetHa(), node->GetHd()})
        values.push_back(Bits(value));
    }
    return values;
  }

  void ResetCurvatures() const {
    for (const auto& state : nodes_) {
      state.node->SetGa(71);
      state.node->SetGd(72);
      state.node->SetHa(73);
      state.node->SetHd(74);
    }
  }

private:
  Fixture& fixture_;
  std::vector<SubMesh*> meshes_;
  std::vector<NodeState> nodes_;
};

bool Normal(int shape, int degree) {
  Fixture fixture(shape, degree);
  Snapshot snapshot(fixture);
  double error = 0;
  {
    GeneratorAdaptive reference;
    error = reference.ErrorGlobal(&fixture.mesh, &fixture.timer);
  }
  Require(std::isfinite(error) && error >= 0, "finite nonnegative direct serial reference");
  Require((shape == 0 || shape == 3) ? error == 0 : error > 0,
          "analytic plane/empty zero and curved nonzero controls");
  const auto curvatures = snapshot.Curvatures();
  std::printf("error_reference=shape:%d degree:%d bits:%016llx nodes:%zu\n", shape, degree,
              static_cast<unsigned long long>(Bits(error)), curvatures.size() / 4);
  const double lower = std::nextafter(error, -std::numeric_limits<double>::infinity());
  const double upper = std::nextafter(error, std::numeric_limits<double>::infinity());
  const double nan = std::numeric_limits<double>::quiet_NaN();
  const double inf = std::numeric_limits<double>::infinity();
  const std::array<std::array<double, 2>, 9> policies{{{{error, error}},
                                                       {{lower, upper}},
                                                       {{upper, lower}},
                                                       {{nan, error}},
                                                       {{upper, nan}},
                                                       {{inf, inf}},
                                                       {{-inf, -inf}},
                                                       {{10000, 0}},
                                                       {{upper, error}}}};
  for (unsigned policy = 0; policy < policies.size(); ++policy) {
    snapshot.ResetCurvatures();
    fixture.estimate.minor_error_ = policies[policy][0];
    fixture.estimate.minor_degree_ = 17;
    ESTIMATIVE_TOLERANCE = policies[policy][1];
    const bool result =
        fixture.estimate.CalculateErroEstimative(&fixture.mesh, &fixture.timer, degree);
    const bool expected = !(error <= ESTIMATIVE_TOLERANCE);
    const int expected_degree = error < policies[policy][0] ? degree : 17;
    Require(result == expected && fixture.estimate.minor_degree_ == expected_degree,
            "strict degree update and inclusive stopping threshold, including NaN/infinity");
    Require(Bits(fixture.estimate.minor_error_) == Bits(policies[policy][0]),
            "historical minor_error_ remains unchanged");
    Require(snapshot.Matches() && snapshot.Curvatures() == curvatures,
            "borrowed graph identity and exact per-node curvature writes");
    std::printf(
        "error_policy=shape:%d degree:%d case:%u continue:%d selected:%d graph:1 curvature:1\n",
        shape, degree, policy, result, fixture.estimate.minor_degree_);
  }
  for (std::size_t index = 0; index < curvatures.size(); ++index)
    std::printf("error_curvature=index:%zu bits:%016llx\n", index,
                static_cast<unsigned long long>(curvatures[index]));
  return true;
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

bool Failures(int shape, int degree, int first) {
  int total = 0;
  Fixture fixture(shape, degree);
  {
    AllocationScope hook(-1);
    fixture.estimate.CalculateErroEstimative(&fixture.mesh, &fixture.timer, degree);
    total = attempts;
  }
  Require(total > 0, "positive actual-wrapper allocation calibration");
  Require(first >= 0 && first < total, "nonempty allocation interval");
  std::printf("error_measured=shape:%d degree:%d allocations:%d\n", shape, degree, total);
  const int end = (total - first < 32) ? total : first + 32;
  Snapshot snapshot(fixture);
  for (int ordinal = first; ordinal < end; ++ordinal) {
    fixture.estimate.minor_error_ = std::numeric_limits<double>::infinity();
    fixture.estimate.minor_degree_ = 17;
    ESTIMATIVE_TOLERANCE = 0;
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    bool caught = false;
    {
      AllocationScope hook(ordinal);
      try {
        fixture.estimate.CalculateErroEstimative(&fixture.mesh, &fixture.timer, degree);
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    Require(caught && denied == 1 && attempts == ordinal + 1,
            "one denial propagates without later allocation during unwinding");
    const bool preserved = snapshot.Matches() && fixture.estimate.minor_degree_ == 17 &&
                           std::isinf(fixture.estimate.minor_error_);
    std::printf(
        "error_denied=shape:%d degree:%d ordinal:%d live_blocks:%td live_bytes:%td graph:%d\n",
        shape, degree, ordinal, static_cast<std::ptrdiff_t>(delta.lCounts[_NORMAL_BLOCK]),
        static_cast<std::ptrdiff_t>(delta.lSizes[_NORMAL_BLOCK]), preserved);
    if (!preserved || delta.lCounts[_NORMAL_BLOCK] != 0 || delta.lSizes[_NORMAL_BLOCK] != 0)
      return false;
  }
  std::printf("error_failure_range=shape:%d degree:%d first:%d end:%d total:%d\n", shape, degree,
              first, end, total);
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
  int shape = -1, degree = -1;
  if (std::strcmp(argv[1], "contracts") == 0) {
    for (int surface = 0; surface < 5; ++surface)
      for (int resolution : {1, 2, 4})
        passed &= Normal(surface, resolution);
  } else if (std::sscanf(argv[1], "normal-%d-%d", &shape, &degree) == 2 && shape >= 0 &&
             shape < 5 && (degree == 1 || degree == 2 || degree == 4)) {
    passed = Normal(shape, degree);
  } else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  } else {
#if defined(_MSC_VER) && defined(_DEBUG)
    int first = -1;
    if (std::sscanf(argv[1], "failure-%d-%d-%d", &shape, &degree, &first) == 3 && shape >= 0 &&
        shape < 5 && (degree == 1 || degree == 2 || degree == 4))
      passed = Failures(shape, degree, first);
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
      Require(caught && denied == 1 && attempts == 1, "actual hook detects allocation denial");
      std::puts("allocation_hook_control=detected");
    }
#else
    Require(false, "unknown scenario or unavailable CRT allocation hook");
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
