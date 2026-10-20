#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <stdexcept>
#include <type_traits>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "estimate/charge_estimate_process.h"

double EPSYLON = 1e-8, TOLERANCE = 1e-8, DELTA = 1e-8, MAX_TIME = 1e10;
double TIME_READ_FILE = 0, TRIANGLE_MEDIO = 0, ESTIMATIVE_TOLERANCE = 0;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};
std::string INPUT_MODEL, WRITE_MESH = "h", NAME_MODEL, NUMBER_PROCESS;

namespace {
void Require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Charge input contract failed: %s\n", message);
    std::exit(1);
  }
}

std::uint64_t Bits(double value) {
  std::uint64_t bits;
  std::memcpy(&bits, &value, sizeof(bits));
  return bits;
}

int calls = 0, throw_step = 0;
struct EvaluationFailure {};

void Step(int stage, PatchBezier* patch, int argument) {
  ++calls;
  std::printf("charge_step=index:%d stage:%d argument:%d x:%016llx\n", calls, stage, argument,
              static_cast<unsigned long long>(Bits(patch->GetPt00().GetX())));
  if (calls == throw_step)
    throw EvaluationFailure{};
}

struct Fixture {
  Timer timer;
  ChargeEstimateProcess estimate;
  Geometry geometry;
  std::array<CurveAdaptive*, 4> borrowed{};
  Patch* preceding = nullptr;

  Fixture(int shape, bool seed) {
    if (!seed)
      return;
    auto old = std::make_unique<PatchBezier>();
    preceding = old.get();
    geometry.InsertPatch(std::move(old));
    std::array<PointAdaptive, 16> p;
    for (int v = 0; v < 4; ++v)
      for (int u = 0; u < 4; ++u) {
        const double x = u / 3.0, y = v / 3.0;
        p[v * 4 + u] = PointAdaptive(x, y, shape == 0 ? 0 : (x * x + y * y) / 8);
      }
    const std::array<std::array<int, 4>, 4> slots{
        {{0, 1, 2, 3}, {3, 7, 11, 15}, {12, 13, 14, 15}, {0, 4, 8, 12}}};
    for (unsigned int i = 0; i < borrowed.size(); ++i) {
      const auto& s = slots[i];
      auto curve =
          std::make_unique<CurveAdaptiveParametricBezier>(p[s[0]], p[s[1]], p[s[2]], p[s[3]]);
      borrowed[i] = curve.get();
      curve->InsertPatch(preceding);
      curve->InsertPatch(nullptr);
      curve->InsertPatch(preceding);
      geometry.InsertCurve(std::move(curve));
    }
  }

  bool LivePrefix() {
    for (auto* curve : borrowed)
      if (curve && (curve->GetNumBerPatches() < 3 || curve->GetPatch(0) != preceding ||
                    curve->GetPatch(1) != nullptr || curve->GetPatch(2) != preceding))
        return false;
    for (unsigned int i = 0; i < geometry.GetNumberCurves(); ++i) {
      auto* curve = geometry.GetCurve(i);
      for (unsigned int j = 0; j < curve->GetNumBerPatches(); ++j) {
        auto* observer = curve->GetPatch(j);
        bool owned = observer == nullptr;
        for (unsigned int k = 0; k < geometry.GetNumberPatches(); ++k)
          owned |= geometry.GetPatch(k) == observer;
        if (!owned)
          return false;
      }
      unsigned int expected = 0;
      for (auto* old : borrowed)
        if (old == curve)
          expected += 3;
      for (unsigned int k = preceding ? 1 : 0; k < geometry.GetNumberPatches(); ++k) {
        auto* patch = static_cast<PatchBezier*>(geometry.GetPatch(k));
        for (unsigned int slot = 0; slot < 4; ++slot)
          expected += patch->GetCurve(slot) == curve;
      }
      if (curve->GetNumBerPatches() != expected)
        return false;
    }
    return true;
  }
};

bool Operation(int shape, bool seed, int failure, int repeats, bool emit) {
  Fixture fixture(shape, seed);
  calls = 0;
  throw_step = failure;
  for (int repeat = 0; repeat < repeats; ++repeat) {
    bool caught = false;
    std::list<PatchBezier*> result;
    try {
      result = fixture.estimate.ChargeEstimate(&fixture.geometry, &fixture.timer);
    } catch (const EvaluationFailure&) {
      caught = true;
    }
    Require(caught == (failure != 0), "controlled evaluation exception propagates");
    const bool live = fixture.LivePrefix();
    if (emit) {
      std::printf("charge_result=repeat:%d caught:%d patches:%u curves:%u results:%zu "
                  "curvatures:%zu live:%d\n",
                  repeat, caught, fixture.geometry.GetNumberPatches(),
                  fixture.geometry.GetNumberCurves(), result.size(),
                  fixture.estimate.curvatures_.size(), live);
      for (auto* patch : result) {
        unsigned int index = 0;
        while (index < fixture.geometry.GetNumberPatches() &&
               fixture.geometry.GetPatch(index) != patch)
          ++index;
        Require(index < fixture.geometry.GetNumberPatches(), "returned observer is geometry-owned");
        std::printf(
            "charge_patch=index:%u area:%016llx curvature:%016llx triangle:%016llx count:%016llx\n",
            index, static_cast<unsigned long long>(Bits(patch->GetArea())),
            static_cast<unsigned long long>(Bits(patch->GetKaMedio())),
            static_cast<unsigned long long>(Bits(patch->GetAreaTriangle())),
            static_cast<unsigned long long>(Bits(patch->GetNumberTriangle())));
        const std::array<PointAdaptive, 16> controls{
            patch->GetPt00(), patch->GetPt10(), patch->GetPt20(), patch->GetPt30(),
            patch->GetPt01(), patch->GetPt11(), patch->GetPt21(), patch->GetPt31(),
            patch->GetPt02(), patch->GetPt12(), patch->GetPt22(), patch->GetPt32(),
            patch->GetPt03(), patch->GetPt13(), patch->GetPt23(), patch->GetPt33()};
        for (unsigned int slot = 0; slot < controls.size(); ++slot) {
          const auto& point = controls[slot];
          std::printf("charge_control=patch:%u slot:%u id:%lu x:%016llx y:%016llx z:%016llx\n",
                      index, slot, point.GetId(),
                      static_cast<unsigned long long>(Bits(point.GetX())),
                      static_cast<unsigned long long>(Bits(point.GetY())),
                      static_cast<unsigned long long>(Bits(point.GetZ())));
        }
        for (unsigned int slot = 0; slot < 4; ++slot) {
          unsigned int curve = 0;
          while (curve < fixture.geometry.GetNumberCurves() &&
                 fixture.geometry.GetCurve(curve) != patch->GetCurve(slot))
            ++curve;
          std::printf("charge_incidence=patch:%u slot:%u curve:%u\n", index, slot, curve);
        }
      }
    }
    if (!live)
      return false;
    if (!caught) {
      const std::size_t expected = shape < 2 ? 1 : 3;
      Require(result.size() == expected, "complete nonempty output inventory");
      auto* previous = result.front();
      for (auto* patch : result) {
        Require(!(patch->GetKaMedio() > previous->GetKaMedio()), "descending curvature order");
        if (patch->GetKaMedio() == previous->GetKaMedio()) {
          unsigned int first = 0, second = 0;
          while (fixture.geometry.GetPatch(first) != previous)
            ++first;
          while (fixture.geometry.GetPatch(second) != patch)
            ++second;
          Require(first <= second, "equal-curvature insertion order is stable");
        }
        previous = patch;
      }
    }
  }
  return true;
}

template <class T> PatchBezier* Observer(T& value) {
  if constexpr (std::is_pointer_v<T>)
    return value;
  else
    return value.get();
}
template <class T> void DestroyOriginal(T& value) {
  if constexpr (std::is_pointer_v<T>)
    delete value;
}

bool Read() {
  PatchReader reader;
  auto patches = reader.LoaderBPFile(INPUT_MODEL);
  unsigned int index = 0;
  for (auto& owner : patches) {
    auto* patch = Observer(owner);
    std::printf("charge_read=index:%u x:%016llx y:%016llx z:%016llx id:%lu curves:%u\n", index++,
                static_cast<unsigned long long>(Bits(patch->GetPt00().GetX())),
                static_cast<unsigned long long>(Bits(patch->GetPt00().GetY())),
                static_cast<unsigned long long>(Bits(patch->GetPt00().GetZ())),
                patch->GetPt00().GetId(), patch->GetNumBerCurves());
    DestroyOriginal(owner);
  }
  return true;
}

bool ReadReuse() {
  PatchReader reader;
  auto first = reader.LoaderBPFile(INPUT_MODEL);
  auto second = reader.LoaderBPFile(INPUT_MODEL);
  bool independent = !first.empty() && first.size() == second.size();
  for (auto& left : first)
    for (auto& right : second)
      independent &= Observer(left) != Observer(right);
  // Raw historical results alias the first prefix; delete that union only once.
  for (auto& owner : second)
    DestroyOriginal(owner);
  std::printf("charge_reuse=first:%zu second:%zu independent:%d\n", first.size(), second.size(),
              independent);
  return independent;
}

#if defined(_MSC_VER) && defined(_DEBUG)
int fail_after = -1, attempts = 0, denied = 0;
int __cdecl AllocationHook(int kind, void*, std::size_t, int block, long, const unsigned char*,
                           int) {
  if (kind == _HOOK_ALLOC && block == _NORMAL_BLOCK) {
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

private:
  _CRT_ALLOC_HOOK previous_;
};

bool Failures(int shape, bool seed, bool reader_only, int first) {
  int total = 0;
  {
    Fixture fixture(shape, seed);
    calls = throw_step = 0;
    AllocationScope hook(-1);
    if (reader_only)
      Read();
    else
      fixture.estimate.ChargeEstimate(&fixture.geometry, &fixture.timer);
    total = attempts;
  }
  Require(total > 0 && first >= 0 && first < total, "positive nonempty allocation interval");
  std::printf("charge_measured=allocations:%d\n", total);
  const int end = total - first < 32 ? total : first + 32;
  for (int ordinal = first; ordinal < end; ++ordinal) {
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    bool live = true, caught = false;
    {
      Fixture fixture(shape, seed);
      calls = throw_step = 0;
      {
        AllocationScope hook(ordinal);
        try {
          if (reader_only)
            Read();
          else
            fixture.estimate.ChargeEstimate(&fixture.geometry, &fixture.timer);
        } catch (const std::bad_alloc&) {
          caught = true;
        }
      }
      live = fixture.LivePrefix();
    }
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    Require(denied == 1, "one actual allocation denial is observed");
    std::printf("charge_denied=ordinal:%d caught:%d attempts:%d blocks:%td bytes:%td live:%d\n",
                ordinal, caught, attempts,
                static_cast<std::ptrdiff_t>(delta.lCounts[_NORMAL_BLOCK]),
                static_cast<std::ptrdiff_t>(delta.lSizes[_NORMAL_BLOCK]), live);
    if (!live || delta.lCounts[_NORMAL_BLOCK] != 0 || delta.lSizes[_NORMAL_BLOCK] != 0)
      return false;
  }
  std::printf("charge_failure_range=first:%d end:%d total:%d\n", first, end, total);
  return true;
}
#endif
} // namespace

#if !AP_MESH_CHARGE_REAL
double ChargeEstimateProcess::CalculateAreaPatch(PatchBezier* patch, int points) {
  Step(1, patch, points);
  Require(points == 4, "unchanged quadrature argument");
  return 1.0 + patch->GetPt00().GetX() / 4;
}
double ChargeEstimateProcess::CalculateKaMedioPatch(PatchBezier* patch, int points) {
  Step(2, patch, points);
  Require(points == 25, "unchanged curvature sample argument");
  return patch->GetPt00().GetX() == 1 ? 1.0 : 3.0;
}
double ChargeEstimateProcess::CalculateAreaTriangleMedioRad(PatchBezier* patch) {
  Step(3, patch, 0);
  return patch->GetKaMedio() / 8;
}
#endif

int main(int argc, char** argv) {
  Require(argc == 3, "scenario and input fixture required");
  std::setvbuf(stdout, nullptr, _IONBF, 0);
  INPUT_MODEL = argv[2];
  NAME_MODEL = "charge_input";
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
  int shape = -1, seed = -1, step = -1, first = -1, reader = -1;
  if (std::strcmp(argv[1], "read") == 0)
    passed = Read();
  else if (std::strcmp(argv[1], "reuse") == 0)
    passed = ReadReuse();
  else if (std::strcmp(argv[1], "contracts") == 0) {
    passed = ReadReuse() && Operation(3, true, 0, 3, true);
    for (int failure = 1; failure <= 9; ++failure)
      passed &= Operation(3, true, failure, 1, true);
  } else if (std::sscanf(argv[1], "normal-%d-%d", &shape, &seed) == 2)
    passed = Operation(shape, seed != 0, 0, 1, true);
  else if (std::sscanf(argv[1], "repeat-%d-%d", &shape, &seed) == 2)
    passed = Operation(shape, seed != 0, 0, 3, true);
  else if (std::sscanf(argv[1], "writer-%d-%d", &shape, &seed) == 2) {
    WRITE_MESH = "m";
    passed = Operation(shape, seed != 0, 0, 1, true);
  } else if (std::sscanf(argv[1], "throw-%d-%d-%d", &shape, &seed, &step) == 3)
    passed = Operation(shape, seed != 0, step, 1, true);
  else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0)
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::sscanf(argv[1], "failure-%d-%d-%d-%d", &shape, &seed, &reader, &first) == 4) {
      if (reader == 2)
        WRITE_MESH = "m";
      passed = Failures(shape, seed != 0, reader == 1, first);
    } else {
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
      Require(caught && denied == 1, "actual allocation hook is exercised");
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
  if (delta.lCounts[_NORMAL_BLOCK] != 0)
    passed = false;
#endif
  std::puts(passed ? "PASS" : "FAIL");
  return passed ? 0 : 1;
}
