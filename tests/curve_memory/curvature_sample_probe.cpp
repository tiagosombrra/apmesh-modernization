#include <array>
#include <atomic>
#include <climits>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "estimate/charge_estimate_process.h"

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
double MAX_TIME = 1e10, TIME_READ_FILE = 0, TRIANGLE_MEDIO = 0, ESTIMATIVE_TOLERANCE = 0;
std::string INPUT_MODEL, WRITE_MESH = "h", NAME_MODEL, NUMBER_PROCESS;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void Require(bool value, const char* message) {
  if (!value) {
    std::fprintf(stderr, "Curvature sample contract failed: %s\n", message);
    std::exit(1);
  }
}

std::uint64_t Bits(double value) {
  std::uint64_t result;
  std::memcpy(&result, &value, sizeof(result));
  return result;
}

struct EvaluationFailure {};
struct Event {
  int stage;
  std::array<std::uint64_t, 3> arguments;
};

// These overrides observe real operations; all successful work delegates to the
// actual PatchBezier implementation. Exceptions exercise each sampled forward
// and inverse parameterization boundary.
class TracePatch : public PatchBezier {
public:
  using PatchBezier::PatchBezier;
  std::array<Event, 50> events{};
  int count = 0, throw_step = 0;
  bool inverse_active = false;

  void Record(int stage, double u, double v, double z = 0) {
    Require(count < static_cast<int>(events.size()), "bounded complete trace");
    events[count++] = {stage, {Bits(u), Bits(v), Bits(z)}};
    if (count == throw_step)
      throw EvaluationFailure{};
  }
  PointAdaptive Parameterize(double u, double v) override {
    if (!inverse_active)
      Record(0, u, v);
    return PatchBezier::Parameterize(u, v);
  }
  std::tuple<double, double> FindUV(const PointAdaptive& point) override {
    Record(1, point.GetX(), point.GetY(), point.GetZ());
    // FindUV calls Parameterize internally. Only the caller's sample positions
    // are counted as injectable boundaries; the actual inverse solver is intact.
    struct InverseScope {
      bool& active;
      explicit InverseScope(bool& flag) : active(flag) { active = true; }
      ~InverseScope() { active = false; }
    } scope(inverse_active);
    return PatchBezier::FindUV(point);
  }
};

struct Fixture {
  std::array<std::unique_ptr<CurveAdaptive>, 4> curves;
  std::unique_ptr<TracePatch> patch;
  ChargeEstimateProcess estimate;

  explicit Fixture(int shape) {
    std::array<PointAdaptive, 16> p;
    for (int u = 0; u < 4; ++u)
      for (int v = 0; v < 4; ++v) {
        const double x = u / 3.0, y = v / 3.0;
        const double z = shape == 0 ? 0 : shape == 1 ? x * y / 4 : (x * x + y * y) / 8;
        p[u * 4 + v] = PointAdaptive(x, y, z);
      }
    patch = std::make_unique<TracePatch>(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9],
                                         p[10], p[11], p[12], p[13], p[14], p[15]);
    for (unsigned int slot = 0; slot < curves.size(); ++slot)
      curves[slot].reset(patch->GetCurve(slot));
    patch->SetId(42);
    patch->SetArea(2.75);
    patch->SetKaMedio(1.25);
  }
};

int SampleCount(int points) {
  if (points < 4 || points > 25)
    return 0;
  return points == 25 ? 25 : points >= 17 ? 17 : points >= 9 ? 9 : 4;
}

double Operation(Fixture& fixture, int points, int step, bool emit) {
  auto& patch = *fixture.patch;
  patch.count = 0;
  patch.throw_step = step;
  bool caught = false;
  double result = 0;
  try {
    result = fixture.estimate.CalculateKaMedioPatch(&patch, points);
  } catch (const EvaluationFailure&) {
    caught = true;
  }
  Require(caught == (step != 0), "controlled exception propagates");
  Require(patch.count == (step ? step : 2 * SampleCount(points)), "exact operation count");
  Require(patch.GetId() == 42 && patch.GetArea() == 2.75 && patch.GetKaMedio() == 1.25,
          "borrowed metadata is unchanged");
  for (unsigned int slot = 0; slot < fixture.curves.size(); ++slot)
    Require(patch.GetCurve(slot) == fixture.curves[slot].get(), "borrowed curve identity");
  if (emit) {
    std::printf("sample_result=points:%d caught:%d events:%d bits:%016llx\n", points, caught,
                patch.count, static_cast<unsigned long long>(Bits(result)));
    for (int index = 0; index < patch.count; ++index) {
      const auto& event = patch.events[index];
      std::printf("sample_event=index:%d stage:%d a:%016llx b:%016llx c:%016llx\n", index,
                  event.stage, static_cast<unsigned long long>(event.arguments[0]),
                  static_cast<unsigned long long>(event.arguments[1]),
                  static_cast<unsigned long long>(event.arguments[2]));
    }
  }
  return result;
}

#if defined(_MSC_VER) && defined(_DEBUG)
int attempts = 0, denied = 0, fail_after = -1;
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
#endif
  // Initialize diagnostic/iostream runtime before the measured lifetime window.
  {
    Fixture warm(0);
    Operation(warm, 0, 0, false);
  }
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  int shape = -1, points = -1, repeat = -1, step = -1;
  bool passed = true;
  if (std::strcmp(argv[1], "contracts") == 0) {
    for (int surface = 0; surface < 3; ++surface) {
      Fixture fixture(surface);
      for (int count : {INT_MIN, -1, 0, 3, 4, 5, 8, 9, 10, 16, 17, 18, 24, 25, 26, INT_MAX}) {
        double result = Operation(fixture, count, 0, true);
        if (surface == 0 || SampleCount(count) == 0)
          Require(result == 0.0, "analytic planar/empty curvature");
      }
      for (int count : {4, 9, 17, 25})
        for (int position = 1; position <= 2 * count; ++position)
          Operation(fixture, count, position, false);
    }
  } else if (std::sscanf(argv[1], "normal-%d-%d-%d", &shape, &points, &repeat) == 3) {
    Fixture fixture(shape);
    for (int index = 0; index < repeat; ++index)
      Operation(fixture, points, 0, true);
  } else if (std::sscanf(argv[1], "throw-%d-%d-%d", &shape, &points, &step) == 3) {
    Fixture fixture(shape);
    Operation(fixture, points, step, true);
  } else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0)
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::sscanf(argv[1], "noalloc-%d-%d-%d", &shape, &points, &step) == 3) {
      Fixture fixture(shape);
      // Warm actual numerical runtime before instrumenting only this operation.
      Operation(fixture, points, 0, false);
      {
        AllocationScope hook(0);
        Operation(fixture, points, step, false);
      }
      std::printf("sample_noalloc=attempts:%d denied:%d step:%d\n", attempts, denied, step);
      passed = attempts == 0 && denied == 0;
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
      Require(caught && denied == 1 && attempts == 1, "actual allocation hook works");
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
  passed &= delta.lCounts[_NORMAL_BLOCK] == 0 && delta.lSizes[_NORMAL_BLOCK] == 0;
#endif
  std::puts(passed ? "PASS" : "FAIL");
  return passed ? 0 : 1;
}
