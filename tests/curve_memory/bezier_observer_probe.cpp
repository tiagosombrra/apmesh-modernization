#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <utility>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif
#include "data/geometry.h"
#include "data/patch/patch_bezier.h"
#include "generator/curve_synchronization.h"

#if defined(_WIN32)
#include <windows.h>
#endif

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void Require(bool value, const char* message) {
  if (!value) {
    std::fprintf(stderr, "Bezier observer contract failed: %s\n", message);
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
  Geometry geometry;
  std::array<PointAdaptive, 16> points;
  std::array<CurveAdaptive*, 4> slots{};
  std::array<std::unique_ptr<PatchBezier>, 3> patches;
  Fixture(int layout, int shape, int mask, bool populated) {
    parent.SetId(77);
    for (unsigned int i = 0; i < points.size(); ++i) {
      const double u = (i / 4) / 3.0, v = (i % 4) / 3.0;
      points[i] = PointAdaptive(u, v, shape == 0 ? 0 : 0.25 * u * v, 300 + i);
    }
    const std::array<std::array<unsigned int, 4>, 4> controls{
        {{0, 4, 8, 12}, {12, 13, 14, 15}, {3, 7, 11, 15}, {0, 1, 2, 3}}};
    for (unsigned int i = 0; i < controls.size(); ++i) {
      const auto& c = controls[i];
      auto curve = std::make_unique<CurveAdaptiveParametricBezier>(points[c[0]], points[c[1]],
                                                                   points[c[2]], points[c[3]]);
      curve->SetId(800 + i);
      if (populated) {
        curve->InsertPatch(&parent);
        curve->InsertPatch(nullptr);
        curve->InsertPatch(&parent);
      }
      geometry.InsertCurve(std::move(curve));
    }
    // Paired slots need both source curves to exist before assigning all slots.
    for (unsigned int i = 0; i < slots.size(); ++i)
      slots[i] = geometry.GetCurve(layout == 0 ? i : layout == 1 ? i / 2 : 0);
    for (unsigned int i = 0; i < patches.size(); ++i) {
      patches[i] = std::make_unique<PatchBezier>(slots[0], slots[1], slots[2], slots[3], points[5],
                                                 points[9], points[6], points[10], (mask & 1) == 0,
                                                 (mask & 2) == 0, (mask & 4) == 0, (mask & 8) == 0);
      patches[i]->SetId(100 + i);
    }
  }
};

struct Snapshot {
  std::array<CurveAdaptive*, 32> curves{};
  std::array<std::array<Patch*, 32>, 32> entries{};
  std::array<unsigned int, 32> counts{};
  unsigned int size = 0;
  explicit Snapshot(Geometry& geometry) : size(geometry.GetNumberCurves()) {
    Require(size <= curves.size(), "bounded curve inventory");
    for (unsigned int i = 0; i < size; ++i) {
      curves[i] = geometry.GetCurve(i);
      counts[i] = curves[i]->GetNumBerPatches();
      Require(counts[i] <= entries[i].size(), "bounded observer inventory");
      for (unsigned int j = 0; j < counts[i]; ++j)
        entries[i][j] = curves[i]->GetPatch(j);
    }
  }
  bool MatchesExcept(Patch* retired) const {
    for (unsigned int i = 0; i < size; ++i) {
      unsigned int cursor = 0;
      for (unsigned int j = 0; j < counts[i]; ++j)
        if (retired == nullptr || entries[i][j] != retired) {
          if (curves[i]->GetPatch(cursor) != entries[i][j])
            return false;
          ++cursor;
        }
      if (curves[i]->GetNumBerPatches() != cursor)
        return false;
    }
    return true;
  }
};

void AddRepeatedObservers(Fixture& fixture, PatchBezier* patch) {
  for (unsigned int i = 0; i < fixture.geometry.GetNumberCurves(); ++i) {
    auto* curve = fixture.geometry.GetCurve(i);
    bool used = false;
    for (unsigned int slot = 0; slot < patch->GetNumBerCurves(); ++slot)
      used |= patch->GetCurve(slot) == curve;
    if (used) {
      curve->InsertPatch(patch);
      curve->InsertPatch(nullptr);
      curve->InsertPatch(patch);
    }
  }
}

bool Retire(Fixture& fixture, unsigned int victim, bool consume) {
  auto* retired = fixture.patches[victim].get();
  AddRepeatedObservers(fixture, retired);
  Snapshot before(fixture.geometry);
  fixture.patches[victim].reset();
  const bool restored = before.MatchesExcept(retired);
  if (consume) {
    unsigned long total = 0;
    for (unsigned int i = 0; i < fixture.geometry.GetNumberCurves(); ++i) {
      auto* curve = fixture.geometry.GetCurve(i);
      for (unsigned int j = 0; j < curve->GetNumBerPatches(); ++j)
        if (auto* patch = curve->GetPatch(j))
          total += patch->GetId();
    }
    std::printf("observer_live_id_sum=%lu\n", total);
  }
  std::printf("observer_retired=victim:%u restored:%d curves:%u\n", victim, restored,
              fixture.geometry.GetNumberCurves());
  return restored;
}

void Trace(Fixture& fixture) {
  for (const auto& owner : fixture.patches) {
    const auto& patch = *owner;
    std::printf("observer_live_patch=id:%u curves:%u\n", patch.GetId(), patch.GetNumBerCurves());
    for (unsigned int i = 0; i < patch.GetNumBerCurves(); ++i)
      std::printf("observer_incidence=curve:%lu reversed:%d\n", patch.GetCurve(i)->GetId(),
                  patch.IsCurveReversed(i));
    for (const auto& uv : std::array<std::array<double, 2>, 3>{{{0, 0}, {0.25, 0.75}, {1, 1}}}) {
      auto* value = owner.get();
      const auto p = value->Parameterize(uv[0], uv[1]);
      const auto u = value->Qu(uv[0], uv[1]), v = value->Qv(uv[0], uv[1]);
      for (double scalar : {p.GetX(), p.GetY(), p.GetZ(), u.GetX(), u.GetY(), u.GetZ(), v.GetX(),
                            v.GetY(), v.GetZ()})
        std::printf("observer_scalar=bits:%016llx\n",
                    static_cast<unsigned long long>(Bits(scalar)));
    }
  }
  // This mode measures live numerical/incidence preservation only. Retire its
  // registrations while every patch is alive, allowing the original comparison.
  for (unsigned int i = 0; i < fixture.geometry.GetNumberCurves(); ++i)
    fixture.geometry.GetCurve(i)->ClearPatches();
}

struct Tracker {
  int live_curves = 0, destroyed_curves = 0, destroyed_patches = 0;
  bool valid_order = true, consume = false;
};
class TrackedCurve : public CurveAdaptiveParametricBezier {
public:
  TrackedCurve(Tracker& tracker, const PointAdaptive& a, const PointAdaptive& b,
               const PointAdaptive& c, const PointAdaptive& d)
      : CurveAdaptiveParametricBezier(a, b, c, d), tracker_(tracker) {
    ++tracker_.live_curves;
  }
  ~TrackedCurve() override {
    --tracker_.live_curves;
    ++tracker_.destroyed_curves;
  }

private:
  Tracker& tracker_;
};
class TrackedPatch : public PatchBezier {
public:
  TrackedPatch(Tracker& tracker, const std::array<CurveAdaptive*, 4>& curves)
      : PatchBezier(curves[0], curves[1], curves[2], curves[3], PointAdaptive(), PointAdaptive(),
                    PointAdaptive(), PointAdaptive()),
        tracker_(tracker) {}
  ~TrackedPatch() override {
    tracker_.valid_order &= tracker_.live_curves == 4;
    ++tracker_.destroyed_patches;
    if (tracker_.consume)
      std::printf("observer_destructor_curve=%lu\n", GetCurve(0)->GetId());
  }

private:
  Tracker& tracker_;
};
void Fill(Geometry& geometry, Tracker& tracker) {
  std::array<CurveAdaptive*, 4> curves{};
  for (unsigned int i = 0; i < curves.size(); ++i) {
    auto curve =
        std::make_unique<TrackedCurve>(tracker, PointAdaptive(0, 0, 0), PointAdaptive(0.25, 0, 0),
                                       PointAdaptive(0.75, 0, 0), PointAdaptive(1, 0, 0));
    curve->SetId(900 + i);
    curves[i] = curve.get();
    geometry.InsertCurve(std::move(curve));
  }
  for (unsigned int i = 0; i < 2; ++i) {
    auto patch = std::make_unique<TrackedPatch>(tracker, curves);
    patch->SetId(500 + i);
    geometry.InsertPatch(std::move(patch));
  }
}
bool Finished(const Tracker& tracker) {
  return tracker.valid_order && tracker.live_curves == 0 && tracker.destroyed_curves == 4 &&
         tracker.destroyed_patches == 2;
}
bool GeometryScenario(const char* mode) {
  Tracker previous, incoming;
  bool identities = true;
  {
    Geometry destination;
    Fill(destination, previous);
    if (std::strcmp(mode, "geometry-move-construct") == 0) {
      auto* patch = destination.GetPatch(0);
      Geometry moved(std::move(destination));
      identities &= moved.GetPatch(0) == patch;
    } else if (std::strcmp(mode, "geometry-self-move") == 0) {
      auto& same = destination;
      destination = std::move(same);
    } else if (std::strcmp(mode, "geometry-destroy") != 0) {
      Geometry source;
      Fill(source, incoming);
      previous.consume = std::strcmp(mode, "geometry-move-consume") == 0;
      auto* curve = source.GetCurve(0);
      auto* patch = source.GetPatch(0);
      destination = std::move(source);
      identities &= destination.GetCurve(0) == curve && destination.GetPatch(0) == patch;
    }
  }
  const bool used_incoming = std::strcmp(mode, "geometry-move-assign") == 0 ||
                             std::strcmp(mode, "geometry-move-consume") == 0;
  const bool result = identities && Finished(previous) && (!used_incoming || Finished(incoming));
  std::printf("observer_geometry=mode:%s old_order:%d new_order:%d identities:%d\n", mode,
              previous.valid_order, incoming.valid_order, identities);
  return result;
}

#if defined(_MSC_VER) && defined(_DEBUG)
int attempts = 0, denied = 0;
int __cdecl AllocationHook(int kind, void*, std::size_t, int block, long, const unsigned char*,
                           int) {
  if (kind == _HOOK_ALLOC && block == _NORMAL_BLOCK) {
    ++attempts;
    ++denied;
    return FALSE;
  }
  return TRUE;
}
class AllocationScope {
public:
  AllocationScope() {
    attempts = denied = 0;
    previous_ = _CrtSetAllocHook(AllocationHook);
  }
  ~AllocationScope() { _CrtSetAllocHook(previous_); }

private:
  _CRT_ALLOC_HOOK previous_;
};
bool NoAllocation(int layout, unsigned int victim, bool populated) {
  Fixture fixture(layout, 1, 15, populated);
  auto* retired = fixture.patches[victim].get();
  AddRepeatedObservers(fixture, retired);
  Snapshot before(fixture.geometry);
  {
    AllocationScope hook;
    fixture.patches[victim].reset();
  }
  const bool restored = before.MatchesExcept(retired);
  std::printf("observer_noalloc=attempts:%d denied:%d restored:%d\n", attempts, denied, restored);
  return attempts == 0 && denied == 0 && restored;
}
bool NoAllocationMove() {
  Tracker previous, incoming;
  bool result;
  {
    Geometry destination, source;
    Fill(destination, previous);
    Fill(source, incoming);
    {
      AllocationScope hook;
      destination = std::move(source);
    }
    std::printf("observer_noalloc=attempts:%d denied:%d restored:%d\n", attempts, denied,
                previous.valid_order);
    result = attempts == 0 && denied == 0 && previous.valid_order;
  }
  return result && Finished(previous) && Finished(incoming);
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
  int layout = -1, shape = -1, victim = -1, seed = -1;
  bool passed = true;
  if (std::strcmp(argv[1], "contracts") == 0) {
    for (int form = 0; form < 3; ++form)
      for (int surface = 0; surface < 2; ++surface)
        for (int position = 0; position < 3; ++position)
          for (bool populated : {false, true})
            for (int signs = 0; signs < 16; ++signs) {
              Fixture fixture(form, surface, signs, populated);
              passed &= Retire(fixture, position, false);
            }
    for (const char* mode : {"geometry-destroy", "geometry-move-construct", "geometry-move-assign",
                             "geometry-self-move", "geometry-move-consume"})
      passed &= GeometryScenario(mode);
  } else if (std::sscanf(argv[1], "normal-%d-%d-%d-%d", &layout, &shape, &victim, &seed) == 4) {
    for (int signs = 0; signs < 16; ++signs) {
      Fixture fixture(layout, shape, signs, seed != 0);
      passed &= Retire(fixture, victim, false);
    }
  } else if (std::sscanf(argv[1], "trace-%d-%d", &layout, &shape) == 2) {
    for (int signs = 0; signs < 16; ++signs)
      for (bool populated : {false, true}) {
        Fixture fixture(layout, shape, signs, populated);
        Trace(fixture);
      }
  } else if (std::sscanf(argv[1], "sync-%d", &shape) == 1) {
    Fixture fixture(0, shape, 0, false);
    apmesh::generation::DisableSharedCurveSynchronization(&fixture.geometry);
    passed = Retire(fixture, 1, false);
  } else if (std::strcmp(argv[1], "consume-expired") == 0) {
    Fixture fixture(0, 0, 0, true);
    passed = Retire(fixture, 1, true);
  } else if (std::strncmp(argv[1], "geometry-", 9) == 0) {
    Require(std::strcmp(argv[1], "geometry-destroy") == 0 ||
                std::strcmp(argv[1], "geometry-move-construct") == 0 ||
                std::strcmp(argv[1], "geometry-move-assign") == 0 ||
                std::strcmp(argv[1], "geometry-move-consume") == 0 ||
                std::strcmp(argv[1], "geometry-self-move") == 0,
            "known geometry scenario");
    passed = GeometryScenario(argv[1]);
  } else if (std::strcmp(argv[1], "prefix-negative-control") == 0) {
    Fixture fixture(0, 0, 0, true);
    Snapshot expected(fixture.geometry);
    Require(expected.MatchesExcept(nullptr), "unchanged prefix must be accepted");
    fixture.geometry.GetCurve(0)->InsertPatch(&fixture.parent);
    Require(!expected.MatchesExcept(nullptr), "extra prefix observer must be rejected");
    std::puts("observer_prefix_control=rejected");
  } else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  } else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::sscanf(argv[1], "noalloc-%d-%d-%d", &layout, &victim, &seed) == 3)
      passed = NoAllocation(layout, victim, seed != 0);
    else if (std::strcmp(argv[1], "noalloc-move") == 0)
      passed = NoAllocationMove();
    else {
      Require(std::strcmp(argv[1], "allocation-hook-control") == 0, "known CRT scenario");
      bool caught = false;
      {
        AllocationScope hook;
        try {
          auto value = std::make_unique<PointAdaptive>();
        } catch (const std::bad_alloc&) {
          caught = true;
        }
      }
      Require(caught && attempts == 1 && denied == 1, "actual allocation denial");
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
