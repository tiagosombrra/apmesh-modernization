#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/patch/patch_bezier.h"

#if defined(_WIN32)
#include <windows.h>
#endif

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void Require(bool value, const char* message) {
  if (!value) {
    std::fprintf(stderr, "Bezier construction contract failed: %s\n", message);
    std::exit(1);
  }
}
std::uint64_t Bits(double value) {
  std::uint64_t result;
  std::memcpy(&result, &value, sizeof(result));
  return result;
}

struct Fixture {
  PatchBezier parent;
  std::array<PointAdaptive, 16> points;
  std::array<std::unique_ptr<CurveAdaptiveParametricBezier>, 4> curves;
  std::array<CurveAdaptive*, 4> slots{};
  int kind, mask;
  unsigned int prefix;

  Fixture(int shape, int form, int signals, bool populated)
      : kind(form), mask(signals), prefix(populated ? 3 : 0) {
    for (unsigned int u = 0; u < 4; ++u)
      for (unsigned int v = 0; v < 4; ++v) {
        double x = u / 3.0, y = v / 3.0;
        points[u * 4 + v] = PointAdaptive(x, y, shape ? x * y / 4 : 0, 100 + u * 4 + v);
      }
    const std::array<std::array<unsigned int, 4>, 4> controls{
        {{0, 4, 8, 12}, {12, 13, 14, 15}, {3, 7, 11, 15}, {0, 1, 2, 3}}};
    for (unsigned int slot = 0; slot < 4; ++slot) {
      const auto& c = controls[slot];
      const bool forward = mask & (1 << slot);
      curves[slot] = forward ? std::make_unique<CurveAdaptiveParametricBezier>(
                                   points[c[0]], points[c[1]], points[c[2]], points[c[3]])
                             : std::make_unique<CurveAdaptiveParametricBezier>(
                                   points[c[3]], points[c[2]], points[c[1]], points[c[0]]);
      curves[slot]->SetId(800 + slot);
      if (populated) {
        curves[slot]->InsertPatch(&parent);
        curves[slot]->InsertPatch(nullptr);
        curves[slot]->InsertPatch(&parent);
      }
      const unsigned int owner = kind == 2 ? slot / 2 : kind == 3 ? 0 : slot;
      slots[slot] = curves[owner].get();
    }
    // Aliased slots may refer to owners created later in the setup loop.
    for (unsigned int slot = 0; slot < 4; ++slot)
      slots[slot] = curves[kind == 2 ? slot / 2 : kind == 3 ? 0 : slot].get();
  }

  std::unique_ptr<PatchBezier> Build() {
    const bool a = mask & 1, b = mask & 2, c = mask & 4, d = mask & 8;
    if (kind == 0)
      return std::make_unique<PatchBezier>(points[0], points[1], points[2], points[3], points[4],
                                           points[5], points[6], points[7], points[8], points[9],
                                           points[10], points[11], points[12], points[13],
                                           points[14], points[15], a, b, c, d);
    return std::make_unique<PatchBezier>(slots[0], slots[1], slots[2], slots[3], points[5],
                                         points[9], points[6], points[10], a, b, c, d);
  }

  bool Matches(PatchBezier* pending) {
    for (unsigned int owner = 0; owner < curves.size(); ++owner) {
      auto& curve = *curves[owner];
      unsigned int expected = prefix;
      if (pending && kind != 0)
        for (auto* slot : slots)
          expected += slot == &curve;
      if (curve.GetNumBerPatches() != expected || curve.GetId() != 800 + owner)
        return false;
      for (unsigned int i = 0; i < prefix; ++i)
        if (curve.GetPatch(i) != (i == 1 ? nullptr : &parent))
          return false;
      for (unsigned int i = prefix; i < expected; ++i)
        if (curve.GetPatch(i) != pending)
          return false;
    }
    return true;
  }
};

bool Operation(Fixture& fixture, bool emit) {
  // Preserve the successful constructor's existing external ownership contract.
  std::array<std::unique_ptr<CurveAdaptive>, 4> fresh;
  auto patch = fixture.Build();
  if (fixture.kind == 0)
    for (unsigned int slot = 0; slot < fresh.size(); ++slot)
      fresh[slot].reset(patch->GetCurve(slot));
  const bool live = fixture.Matches(patch.get());
  if (emit) {
    std::printf("bezier_patch=kind:%d mask:%d curves:%u live:%d\n", fixture.kind, fixture.mask,
                patch->GetNumBerCurves(), live);
    for (unsigned int slot = 0; slot < 4; ++slot) {
      auto* curve = static_cast<CurveAdaptiveParametricBezier*>(patch->GetCurve(slot));
      for (const auto& p :
           {curve->GetPoint0(), curve->GetPoint1(), curve->GetPoint2(), curve->GetPoint3()})
        std::printf("bezier_control=slot:%u id:%lu x:%016llx y:%016llx z:%016llx\n", slot,
                    p.GetId(), static_cast<unsigned long long>(Bits(p.GetX())),
                    static_cast<unsigned long long>(Bits(p.GetY())),
                    static_cast<unsigned long long>(Bits(p.GetZ())));
      std::printf("bezier_orientation=slot:%u reversed:%d\n", slot, patch->IsCurveReversed(slot));
    }
    for (const auto& uv : std::array<std::array<double, 2>, 3>{{{0, 0}, {0.25, 0.75}, {1, 1}}}) {
      const auto p = patch->Parameterize(uv[0], uv[1]);
      const auto u = patch->Qu(uv[0], uv[1]), v = patch->Qv(uv[0], uv[1]);
      for (double value : {p.GetX(), p.GetY(), p.GetZ(), u.GetX(), u.GetY(), u.GetZ(), v.GetX(),
                           v.GetY(), v.GetZ()})
        std::printf("bezier_scalar=bits:%016llx\n", static_cast<unsigned long long>(Bits(value)));
    }
  }
  // The test owns successful observer publication and removes it while the patch
  // is alive. Failed construction is checked before any harness cleanup. Ordinary
  // PatchBezier destruction/deregistration is a separate, unqualified boundary.
  for (auto& curve : fixture.curves)
    curve->TruncatePatchObservers(fixture.prefix);
  return live && fixture.Matches(nullptr);
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

bool Failures(int kind, int shape, int mask, int seed) {
  int total;
  {
    Fixture fixture(shape, kind, mask, seed != 0);
    AllocationScope hook(-1);
    Require(Operation(fixture, false), "calibration preserves live prefixes");
    total = attempts;
  }
  Require(total > 0, "positive constructor allocation count");
  std::printf("bezier_measured=allocations:%d\n", total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    bool caught = false, restored = false;
    {
      Fixture fixture(shape, kind, mask, seed != 0);
      {
        AllocationScope hook(ordinal);
        try {
          Operation(fixture, false);
        } catch (const std::bad_alloc&) {
          caught = true;
        }
      }
      // Compare pointer values only; never consume the original expired patch.
      restored = fixture.Matches(nullptr);
    }
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    const auto blocks = static_cast<std::ptrdiff_t>(delta.lCounts[_NORMAL_BLOCK]);
    const auto bytes = static_cast<std::ptrdiff_t>(delta.lSizes[_NORMAL_BLOCK]);
    std::printf("bezier_denied=ordinal:%d attempts:%d caught:%d restored:%d blocks:%td bytes:%td\n",
                ordinal, attempts, caught, restored, blocks, bytes);
    if (denied != 1 || attempts != ordinal + 1 || !caught || !restored || blocks != 0 || bytes != 0)
      return false;
  }
  std::printf("bezier_sweep=denied:%d/%d\n", total, total);
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
  int kind = -1, shape = -1, mask = -1, seed = -1;
  bool passed = true;
  if (std::strcmp(argv[1], "contracts") == 0) {
    for (int form = 0; form < 4; ++form)
      for (int surface = 0; surface < 2; ++surface)
        for (int signs = 0; signs < 16; ++signs)
          for (bool populated : {false, true}) {
            Fixture fixture(surface, form, signs, populated);
            passed &= Operation(fixture, false) && Operation(fixture, false);
          }
  } else if (std::sscanf(argv[1], "normal-%d-%d-%d", &kind, &shape, &seed) == 3) {
    for (int signs = 0; signs < 16; ++signs) {
      Fixture fixture(shape, kind, signs, seed != 0);
      passed &= Operation(fixture, true) && Operation(fixture, true);
    }
  } else if (std::strcmp(argv[1], "prefix-negative-control") == 0) {
    Fixture fixture(0, 1, 15, true);
    fixture.curves[0]->InsertPatch(&fixture.parent);
    Require(!fixture.Matches(nullptr), "extra observer must be detected");
    fixture.curves[0]->TruncatePatchObservers(fixture.prefix);
    Require(fixture.Matches(nullptr), "fixture cleanup restores prefix");
    std::puts("bezier_prefix_control=rejected");
  } else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0)
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::sscanf(argv[1], "failure-%d-%d-%d-%d", &kind, &shape, &mask, &seed) == 4)
      passed = Failures(kind, shape, mask, seed);
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
      Require(caught && denied == 1 && attempts == 1, "actual allocation denial works");
      std::puts("allocation_hook_control=detected");
    }
#else
    Require(false, "unknown scenario or unavailable hook");
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
