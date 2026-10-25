#include "data/geometry.h"
#include "data/patch/patch_hermite.h"
#include "input_output/models_3d.h"

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
#if defined(_WIN32)
#include <windows.h>
#endif

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace injection {
bool enabled = false;
int attempts = 0, denied = 0, remaining = -1;
bool Allow() {
  if (!enabled)
    return true;
  ++attempts;
  if (remaining-- == 0) {
    ++denied;
    return false;
  }
  return true;
}
} // namespace injection

// The isolated probe replaces ordinary new only outside the Debug CRT build.
// The latter uses the independent CRT normal-block allocation hook instead.
#if !defined(_MSC_VER) || !defined(_DEBUG)
void* operator new(std::size_t size) {
  if (!injection::Allow())
    throw std::bad_alloc();
  if (void* value = std::malloc(size == 0 ? 1 : size))
    return value;
  throw std::bad_alloc();
}
void* operator new[](std::size_t size) { return ::operator new(size); }
void operator delete(void* value) noexcept { std::free(value); }
void operator delete[](void* value) noexcept { std::free(value); }
void operator delete(void* value, std::size_t) noexcept { std::free(value); }
void operator delete[](void* value, std::size_t) noexcept { std::free(value); }
#endif

namespace {
void Require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Hermite construction contract failed: %s\n", message);
    std::exit(2);
  }
}

#if defined(_MSC_VER) && defined(_DEBUG)
int __cdecl AllocationHook(int kind, void*, std::size_t, int block, long, const unsigned char*,
                           int) {
  return kind != _HOOK_ALLOC || block != _NORMAL_BLOCK || injection::Allow();
}
#endif
class AllocationScope {
public:
  explicit AllocationScope(int ordinal) {
    injection::attempts = injection::denied = 0;
    injection::remaining = ordinal;
    injection::enabled = true;
#if defined(_MSC_VER) && defined(_DEBUG)
    previous_ = _CrtSetAllocHook(AllocationHook);
#endif
  }
  ~AllocationScope() {
    injection::enabled = false;
#if defined(_MSC_VER) && defined(_DEBUG)
    _CrtSetAllocHook(previous_);
#endif
  }

private:
#if defined(_MSC_VER) && defined(_DEBUG)
  _CRT_ALLOC_HOOK previous_;
#endif
};

struct Fixture {
  Patch parent;
  std::array<std::unique_ptr<CurveAdaptive>, 4> curves;
  std::array<CurveAdaptive*, 4> slots{};
  unsigned int prefix;
  Fixture(int layout, int seed) : prefix(static_cast<unsigned int>(seed)) {
    parent.SetId(77);
    PointAdaptive p00(0, 0, 0), p10(1, 0, 0), p01(0, 1, 0), p11(1, 1, 0.25);
    VectorAdaptive u0(1, 0, 0), u1(1, 0, 0.25), v0(0, 1, 0), v1(0, 1, 0.25);
    curves[0] = std::make_unique<CurveAdaptiveParametricHermite>(p00, p10, u0, u0);
    curves[1] = std::make_unique<CurveAdaptiveParametricHermite>(p10, p11, v1, v1);
    curves[2] = std::make_unique<CurveAdaptiveParametricHermite>(p01, p11, u1, u1);
    curves[3] = std::make_unique<CurveAdaptiveParametricHermite>(p00, p01, v0, v0);
    for (auto& curve : curves)
      for (unsigned int i = 0; i < prefix; ++i)
        curve->InsertPatch(i % 2 == 0 ? &parent : nullptr);
    for (unsigned int i = 0; i < slots.size(); ++i)
      slots[i] = curves[layout == 0 ? i : layout == 1 ? i / 2 : 0].get();
  }
  std::unique_ptr<PatchHermite> Construct(int flags = 15) {
    VectorAdaptive twist(0, 0, 0.25);
    return std::make_unique<PatchHermite>(slots[0], slots[1], slots[2], slots[3], twist, twist,
                                          twist, twist, (flags & 1) != 0, (flags & 2) != 0,
                                          (flags & 4) != 0, (flags & 8) != 0);
  }
  bool PrefixMatches() const {
    for (const auto& curve : curves) {
      if (curve->GetNumBerPatches() < prefix)
        return false;
      for (unsigned int i = 0; i < prefix; ++i)
        if (curve->GetPatch(i) != (i % 2 == 0 ? &parent : nullptr))
          return false;
    }
    return true;
  }
  unsigned int Observe(Patch* live, bool consume) {
    unsigned int suffix = 0;
    unsigned long sum = 0;
    Require(PrefixMatches(), "foreign/null prefix identities and order preserved");
    for (auto& curve : curves) {
      for (unsigned int i = prefix; i < curve->GetNumBerPatches(); ++i) {
        auto* observer = curve->GetPatch(i);
        Require(observer != nullptr && (live == nullptr || observer == live),
                "non-null appended address");
        ++suffix;
        if (consume)
          sum += observer->GetId();
      }
    }
    if (consume)
      std::printf("consumed_id_sum=%lu\n", sum);
    return suffix;
  }
  void ReferenceCleanup() {
    for (auto& curve : curves)
      curve->TruncatePatchObservers(prefix);
  }
};

void Live(int layout, int seed, int flags = 15) {
  Fixture fixture(layout, seed);
  auto patch = fixture.Construct(flags);
  patch->SetId(101);
  Require(fixture.Observe(patch.get(), true) == 4, "four completed publications");
  for (unsigned int i = 0; i < 4; ++i)
    Require(patch->GetCurve(i) == fixture.slots[i], "ordered slot identity");
  unsigned int points = 0;
  for (double u : {0.0, 0.25, 0.5, 0.75, 1.0})
    for (double v : {0.0, 0.25, 0.5, 0.75, 1.0}) {
      const auto p = patch->Parameterize(u, v);
      Require(std::isfinite(p.GetX()) && std::isfinite(p.GetY()) && std::isfinite(p.GetZ()),
              "finite initialized surface");
      if (layout == 0)
        Require(std::abs(p.GetX() - u) < 1e-12 && std::abs(p.GetY() - v) < 1e-12 &&
                    std::abs(p.GetZ() - 0.25 * u * v) < 1e-12,
                "independent bilinear fixture");
      ++points;
    }
  patch.reset();
  Require(fixture.Observe(nullptr, true) == 0, "completed destructor restores prefix");
  std::printf("live_points=%u completed_publications=4 retirement_restored=1\n", points);
}

unsigned int Failed(int layout, int seed, int ordinal, int flags = 15) {
  Fixture fixture(layout, seed);
  bool caught = false;
  {
    AllocationScope hook(ordinal);
    try {
      auto patch = fixture.Construct(flags);
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  Require(caught && injection::denied == 1 && injection::attempts == ordinal + 1,
          "one denial propagates without rollback allocation");
  const auto stale = fixture.Observe(nullptr, false);
  std::printf("denied ordinal=%d attempts=%d denials=%d caught=1 stale=%u prefix_preserved=1\n",
              ordinal, injection::attempts, injection::denied, stale);
  Require(stale == 0, "failed construction restores the complete observer prefix");
  auto retried = fixture.Construct(flags);
  Require(fixture.Observe(retried.get(), true) == 4, "retry publishes exactly four observers");
  retried.reset();
  Require(fixture.Observe(nullptr, true) == 0, "retry retirement restores prefix");
  return stale;
}

void SweepFlags(int layout, int seed, int flags) {
  int total;
  {
    Fixture fixture(layout, seed);
    {
      AllocationScope hook(-1);
      auto patch = fixture.Construct(flags);
      total = injection::attempts;
      Require(fixture.Observe(patch.get(), false) == 4, "calibrated completed publication");
    }
    Require(fixture.Observe(nullptr, false) == 0, "calibration retirement");
  }
  Require(total > 0 && total < 100, "bounded positive calibration");
  unsigned int stale_cases = 0;
  for (int ordinal = 0; ordinal < total; ++ordinal)
    stale_cases += Failed(layout, seed, ordinal, flags) > 0;
  Require(stale_cases == 0, "all calibrated failures restore observers");
  std::printf("sweep flags=%d allocations=%d denials=%d stale_cases=%u complete=1\n", flags, total,
              total, stale_cases);
}

void Sweep(int layout, int seed) {
  for (int flags = 0; flags < 16; ++flags)
    SweepFlags(layout, seed, flags);
}

void Adoption(int layout, int seed) {
  Fixture fixture(layout, seed);
  Geometry geometry;
  auto prior = std::make_unique<Patch>();
  auto* prefix = prior.get();
  geometry.InsertPatch(std::move(prior));
  auto pending = fixture.Construct();
  bool caught = false;
  {
    AllocationScope hook(0);
    try {
      geometry.InsertPatch(std::move(pending));
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  Require(caught && injection::denied == 1 && !pending, "failed consuming Geometry adoption");
  Require(geometry.GetNumberPatches() == 1 && geometry.GetPatch(0) == prefix,
          "committed Geometry prefix preserved");
  Require(fixture.Observe(nullptr, true) == 0,
          "completed Hermite destructor after adoption failure");
  std::puts("adoption_denied=1 geometry_prefix_preserved=1 stale=0");
}

unsigned int ModelObservers(Geometry& geometry, bool consume) {
  unsigned int stale = 0;
  for (unsigned int c = 0; c < geometry.GetNumberCurves(); ++c) {
    auto* curve = geometry.GetCurve(c);
    for (unsigned int i = 0; i < curve->GetNumBerPatches(); ++i) {
      auto* observer = curve->GetPatch(i);
      bool owned = false;
      for (unsigned int p = 0; p < geometry.GetNumberPatches(); ++p)
        owned |= observer == geometry.GetPatch(p);
      if (!owned) {
        ++stale;
        if (consume) {
          std::puts("consuming_actual_model_stale_observer=1");
          std::printf("model_expired_id=%u\n", observer->GetId());
        }
      }
    }
  }
  return stale;
}

int Model(int ordinal) {
  Geometry geometry;
  Models3d models;
  bool caught = false;
  {
    AllocationScope hook(ordinal);
    try {
      Require(models.ModelBaseQuadrada(&geometry) == &geometry, "actual model return identity");
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  const auto stale = ModelObservers(geometry, false);
  std::printf("model ordinal=%d attempts=%d denied=%d caught=%d curves=%u patches=%u stale=%u\n",
              ordinal, injection::attempts, injection::denied, caught, geometry.GetNumberCurves(),
              geometry.GetNumberPatches(), stale);
  if (ordinal >= 0)
    Require(caught && injection::denied == 1, "actual model resource failure propagated");
  else
    Require(!caught && geometry.GetNumberCurves() == 4 && geometry.GetNumberPatches() == 1 &&
                stale == 0,
            "complete actual model graph");
  Require(stale == 0, "actual model failure has only live owned patch observers");
  return injection::attempts;
}

void ModelSweep() {
  const auto total = Model(-1);
  Require(total > 0 && total < 200, "positive bounded actual model calibration");
  for (int ordinal = 0; ordinal < total; ++ordinal)
    Model(ordinal);
  std::printf("model_sweep allocations=%d denials=%d stale_cases=0 complete=1\n", total, total);
}
} // namespace

int main(int argc, char** argv) {
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
  Require(argc >= 2, "mode required");
  const char* mode = argv[1];
  if (std::strcmp(mode, "contracts") == 0) {
    for (int layout = 0; layout < 3; ++layout)
      for (int seed : {0, 3, 4, 7}) {
        for (int flags = 0; flags < 16; ++flags)
          Live(layout, seed, flags);
        Sweep(layout, seed);
        Adoption(layout, seed);
      }
    ModelSweep();
  } else if (std::strcmp(mode, "model-sweep") == 0) {
    ModelSweep();
  } else if (std::strcmp(mode, "model") == 0) {
    Require(argc == 3, "model ordinal required");
    Model(std::atoi(argv[2]));
  } else if (std::strcmp(mode, "hook") == 0) {
    bool caught = false;
    {
      AllocationScope hook(0);
      try {
        auto point = std::make_unique<PointAdaptive>();
        std::printf("unexpected_point=%p\n", static_cast<void*>(point.get()));
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    Require(caught && injection::denied == 1 && injection::attempts == 1,
            "independent denial control");
    std::puts("denial_control=detected");
  } else if (std::strcmp(mode, "oracle") == 0) {
    Fixture fixture(0, 3);
    fixture.curves[0]->InsertPatch(&fixture.parent);
    Require(fixture.Observe(nullptr, false) == 1, "count corruption detected");
    fixture.ReferenceCleanup();
    fixture.curves[0]->ClearPatches();
    fixture.curves[0]->InsertPatch(nullptr);
    fixture.curves[0]->InsertPatch(&fixture.parent);
    fixture.curves[0]->InsertPatch(&fixture.parent);
    // The independent fixed expected order differs, despite identical counts.
    Require(fixture.curves[0]->GetNumBerPatches() == 3 && !fixture.PrefixMatches(),
            "same-count order corruption detected");
    std::puts("oracle_corruptions=2 detected=2");
  } else if (std::strcmp(mode, "uaf") == 0) {
    auto* patch = new Patch;
    patch->SetId(431);
    delete patch;
    std::printf("independent_expired_id=%u\n", patch->GetId());
  } else if (std::strcmp(mode, "leak") == 0) {
    std::printf("deliberate_leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  } else {
    Require(argc >= 4, "layout and seed required");
    const auto layout = std::atoi(argv[2]), seed = std::atoi(argv[3]);
    Require(layout >= 0 && layout < 3 && (seed == 0 || seed == 3 || seed == 4 || seed == 7),
            "bounded layout and seed");
    if (std::strcmp(mode, "live") == 0) {
      for (int flags = 0; flags < 16; ++flags)
        Live(layout, seed, flags);
    } else if (std::strcmp(mode, "sweep") == 0)
      Sweep(layout, seed);
    else if (std::strcmp(mode, "adoption") == 0)
      Adoption(layout, seed);
    else {
      Require(argc == 5, "failure ordinal required");
      Require(std::strcmp(mode, "failed") == 0, "known failure mode");
      Failed(layout, seed, std::atoi(argv[4]));
    }
  }
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  const bool retained = delta.lCounts[_NORMAL_BLOCK] != 0 || delta.lSizes[_NORMAL_BLOCK] != 0;
  Require(retained == (std::strcmp(mode, "leak") == 0), "independent normal-block retention");
  if (retained)
    return 1;
#endif
  std::puts("PASS");
  return 0;
}
