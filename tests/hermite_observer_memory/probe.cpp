#include <array>
#include <atomic>
#include <cmath>
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
#include "data/patch/patch_hermite.h"
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
    std::fprintf(stderr, "Hermite observer contract failed: %s\n", message);
    std::exit(1);
  }
}
std::uint64_t Bits(double value) {
  std::uint64_t result;
  std::memcpy(&result, &value, sizeof(result));
  return result;
}

struct Fixture {
  PatchHermite parent;
  Geometry geometry;
  std::array<CurveAdaptive*, 4> slots{};
  std::array<std::unique_ptr<PatchHermite>, 3> patches;
  Fixture(int layout, int shape, int mask, bool populated) {
    parent.SetId(77);
    const double z = shape * 0.25;
    PointAdaptive p00(0, 0, 0), p10(1, 0, 0), p01(0, 1, 0), p11(1, 1, z);
    VectorAdaptive u0(1, 0, 0), u1(1, 0, z), v0(0, 1, 0), v1(0, 1, z), twist(0, 0, z);
    std::array<std::unique_ptr<CurveAdaptive>, 4> curves{
        std::make_unique<CurveAdaptiveParametricHermite>(p00, p10, u0, u0),
        std::make_unique<CurveAdaptiveParametricHermite>(p10, p11, v1, v1),
        std::make_unique<CurveAdaptiveParametricHermite>(p01, p11, u1, u1),
        std::make_unique<CurveAdaptiveParametricHermite>(p00, p01, v0, v0)};
    for (unsigned int i = 0; i < curves.size(); ++i) {
      curves[i]->SetId(800 + i);
      if (populated) {
        curves[i]->InsertPatch(&parent);
        curves[i]->InsertPatch(nullptr);
        curves[i]->InsertPatch(&parent);
      }
      geometry.InsertCurve(std::move(curves[i]));
    }
    for (unsigned int i = 0; i < slots.size(); ++i)
      slots[i] = geometry.GetCurve(layout == 0 ? i : layout == 1 ? i / 2 : 0);
    for (unsigned int i = 0; i < patches.size(); ++i) {
      patches[i] = std::make_unique<PatchHermite>(
          slots[0], slots[1], slots[2], slots[3], twist, twist, twist, twist, (mask & 1) == 0,
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
  bool MatchesExcept(Patch* retired, CurveAdaptive* selected_curve = nullptr) const {
    for (unsigned int i = 0; i < size; ++i) {
      unsigned int cursor = 0;
      for (unsigned int j = 0; j < counts[i]; ++j)
        if (retired == nullptr || entries[i][j] != retired ||
            (selected_curve != nullptr && curves[i] != selected_curve)) {
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

void AddRepeatedObservers(Fixture& fixture, PatchHermite* patch) {
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

void Trace(Fixture& fixture, int layout, int shape) {
  for (const auto& owner : fixture.patches) {
    const auto& patch = *owner;
    std::printf("observer_live_patch=id:%u curves:%u\n", patch.GetId(), patch.GetNumBerCurves());
    for (unsigned int i = 0; i < patch.GetNumBerCurves(); ++i)
      std::printf("observer_incidence=curve:%lu reversed:%d\n", patch.GetCurve(i)->GetId(),
                  patch.IsCurveReversed(i));
    for (const auto& uv : std::array<std::array<double, 2>, 3>{{{0, 0}, {0.25, 0.75}, {1, 1}}}) {
      const double u = uv[0], v = uv[1], z = shape * 0.25;
      auto* value = owner.get();
      const auto p = value->Parameterize(u, v);
      const auto qu = value->Qu(u, v), qv = value->Qv(u, v), quu = value->Quu(u, v);
      const auto quv = value->Quv(u, v), qvu = value->Qvu(u, v), qvv = value->Qvv(u, v);
      auto emit = [&](const auto& vector, double x, double y, double height) {
        if (layout == 0)
          Require(std::abs(vector.GetX() - x) < 1e-12 && std::abs(vector.GetY() - y) < 1e-12 &&
                      std::abs(vector.GetZ() - height) < 1e-12,
                  "independent analytic fixture");
        for (double scalar : {vector.GetX(), vector.GetY(), vector.GetZ()})
          std::printf("observer_scalar=bits:%016llx\n",
                      static_cast<unsigned long long>(Bits(scalar)));
      };
      emit(p, u, v, z * u * v);
      emit(qu, 1, 0, z * v);
      emit(qv, 0, 1, z * u);
      emit(quu, 0, 0, 0);
      emit(quv, 0, 0, z);
      emit(qvu, 0, 0, z);
      emit(qvv, 0, 0, 0);
    }
  }
  // Compare live initialized values only. Clear registrations while patches are
  // alive so the immutable original also has a valid terminal teardown.
  for (unsigned int i = 0; i < fixture.geometry.GetNumberCurves(); ++i)
    fixture.geometry.GetCurve(i)->ClearPatches();
}

struct Tracker {
  int live_curves = 0, destroyed_curves = 0, destroyed_patches = 0;
  bool valid_order = true, consume = false;
};
class TrackedCurve : public CurveAdaptiveParametricHermite {
public:
  TrackedCurve(Tracker& tracker, const PointAdaptive& a, const PointAdaptive& b,
               const VectorAdaptive& c, const VectorAdaptive& d)
      : CurveAdaptiveParametricHermite(a, b, c, d), tracker_(tracker) {
    ++tracker_.live_curves;
  }
  ~TrackedCurve() override {
    tracker_.valid_order &= GetNumBerPatches() == 0;
    --tracker_.live_curves;
    ++tracker_.destroyed_curves;
  }

private:
  Tracker& tracker_;
};
class TrackedPatch : public PatchHermite {
public:
  TrackedPatch(Tracker& tracker, const std::array<CurveAdaptive*, 4>& curves)
      : PatchHermite(curves[0], curves[1], curves[2], curves[3], VectorAdaptive(), VectorAdaptive(),
                     VectorAdaptive(), VectorAdaptive()),
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
        std::make_unique<TrackedCurve>(tracker, PointAdaptive(0, 0, 0), PointAdaptive(1, 0, 0),
                                       VectorAdaptive(1, 0, 0), VectorAdaptive(1, 0, 0));
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
bool ReplacementScenario(bool bezier, bool noalloc) {
  Patch foreign;
  Geometry geometry;
  std::unique_ptr<PatchCoons> patch;
  if (bezier) {
    std::array<PointAdaptive, 16> p;
    for (unsigned int i = 0; i < p.size(); ++i)
      p[i] = PointAdaptive((i / 4) / 3.0, (i % 4) / 3.0, 0);
    patch = std::make_unique<PatchBezier>(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8],
                                          p[9], p[10], p[11], p[12], p[13], p[14], p[15]);
    for (unsigned int i = 0; i < 4; ++i)
      geometry.InsertCurve(std::unique_ptr<CurveAdaptive>(patch->GetCurve(i)));
  } else {
    const PointAdaptive p00(0, 0, 0), p10(1, 0, 0), p01(0, 1, 0), p11(1, 1, 0);
    const VectorAdaptive u(1, 0, 0), v(0, 1, 0), twist;
    geometry.InsertCurve(std::make_unique<CurveAdaptiveParametricHermite>(p00, p10, u, u));
    geometry.InsertCurve(std::make_unique<CurveAdaptiveParametricHermite>(p10, p11, v, v));
    geometry.InsertCurve(std::make_unique<CurveAdaptiveParametricHermite>(p01, p11, u, u));
    geometry.InsertCurve(std::make_unique<CurveAdaptiveParametricHermite>(p00, p01, v, v));
    patch = std::make_unique<PatchHermite>(geometry.GetCurve(0), geometry.GetCurve(1),
                                           geometry.GetCurve(2), geometry.GetCurve(3), twist, twist,
                                           twist, twist);
  }
  auto* identity = patch.get();
  auto* previous = patch->GetCurve(0);
  // Reuse the existing repeated-slot lifetime arrangement, with four live slots.
  patch->ReplaceCurve(1, previous);
  previous->InsertPatch(&foreign);
  previous->InsertPatch(nullptr);
  previous->InsertPatch(identity);
  previous->InsertPatch(&foreign);
  auto replacement = apmesh::generation::CloneCurveForPatch(previous, identity);
  auto* destination = replacement.get();
  destination->InsertPatch(nullptr);
  destination->InsertPatch(&foreign);
  geometry.InsertCurve(std::move(replacement));
  Snapshot before(geometry);
  const auto sample = [](PatchCoons& value) {
    const auto point = value.Parameterize(0.25, 0.75);
    const auto gradient = value.Qu(0.25, 0.75);
    return std::array<std::uint64_t, 6>{Bits(point.GetX()),    Bits(point.GetY()),
                                        Bits(point.GetZ()),    Bits(gradient.GetX()),
                                        Bits(gradient.GetY()), Bits(gradient.GetZ())};
  };
  const auto numeric_before = sample(*patch);
  bool guards = false, repeated = false, retired = false, destination_preserved = false;
  bool numeric = false, final = false;
  const auto exercise = [&]() {
    patch->ReplaceCurve(99, destination);
    patch->ReplaceCurve(0, previous);
    guards = before.MatchesExcept(nullptr);
    patch->ReplaceCurve(0, destination);
    repeated = before.MatchesExcept(nullptr) && patch->GetCurve(1) == previous;
    patch->ReplaceCurve(1, destination);
    retired = before.MatchesExcept(identity, previous);
    destination_preserved =
        destination->GetNumBerPatches() == 3 && destination->GetPatch(0) == identity &&
        destination->GetPatch(1) == nullptr && destination->GetPatch(2) == &foreign;
    numeric = sample(*patch) == numeric_before;
    patch->ReplaceCurve(0, nullptr);
    repeated = repeated && destination->GetPatch(0) == identity;
    patch->ReplaceCurve(0, destination);
    destination_preserved = destination_preserved && destination->GetNumBerPatches() == 3;
    patch.reset();
    final = before.MatchesExcept(identity);
  };
#if defined(_MSC_VER) && defined(_DEBUG)
  if (noalloc) {
    AllocationScope hook;
    exercise();
  } else
#endif
    exercise();
  std::printf("observer_replacement=kind:%s guards:%d repeated:%d retired:%d destination:%d "
              "numeric:%d final:%d\n",
              bezier ? "bezier" : "hermite", guards, repeated, retired, destination_preserved,
              numeric, final);
#if defined(_MSC_VER) && defined(_DEBUG)
  if (noalloc) {
    std::printf("observer_replacement_allocation=attempts:%d denied:%d\n", attempts, denied);
    if (attempts != 0 || denied != 0)
      return false;
  }
#else
  (void)noalloc;
#endif
  return guards && repeated && retired && destination_preserved && numeric && final;
}

bool EmptyScenario(const char* mode, bool noalloc) {
  Fixture fixture(0, 1, 15, true);
  fixture.patches[0]->Parameterize(0.25, 0.75);
  std::unique_ptr<PatchHermite> owner;
  if (std::strcmp(mode, "empty-detached") == 0)
    owner = std::make_unique<PatchHermite>(fixture.patches[0].get());
  else {
    owner = std::make_unique<PatchHermite>();
    if (std::strcmp(mode, "null-current") == 0) {
      owner->InsertCurve(nullptr);
      owner->InsertCurve(nullptr);
    }
  }
  Snapshot before(fixture.geometry);
#if defined(_MSC_VER) && defined(_DEBUG)
  if (noalloc) {
    AllocationScope hook;
    owner.reset();
  } else
    owner.reset();
  if (noalloc)
    std::printf("observer_noalloc=attempts:%d denied:%d restored:%d\n", attempts, denied,
                before.MatchesExcept(nullptr));
  Require(!noalloc || (attempts == 0 && denied == 0),
          "empty topology retirement allocates nothing");
#else
  Require(!noalloc, "CRT instrument required for noallocation");
  owner.reset();
#endif
  std::printf("observer_empty=mode:%s unchanged:%d\n", mode, before.MatchesExcept(nullptr));
  return before.MatchesExcept(nullptr);
}
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
    passed &= ReplacementScenario(false, false);
    passed &= ReplacementScenario(true, false);
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
    for (const char* mode : {"empty-default", "empty-detached", "null-current"})
      passed &= EmptyScenario(mode, false);
  } else if (std::strcmp(argv[1], "replacement-bezier") == 0 ||
             std::strcmp(argv[1], "replacement-hermite") == 0 ||
             std::strcmp(argv[1], "noalloc-replacement-bezier") == 0 ||
             std::strcmp(argv[1], "noalloc-replacement-hermite") == 0) {
    passed = ReplacementScenario(std::strstr(argv[1], "bezier") != nullptr,
                                 std::strncmp(argv[1], "noalloc-", 8) == 0);
  } else if (std::sscanf(argv[1], "normal-%d-%d-%d-%d", &layout, &shape, &victim, &seed) == 4) {
    for (int signs = 0; signs < 16; ++signs) {
      Fixture fixture(layout, shape, signs, seed != 0);
      passed &= Retire(fixture, victim, false);
    }
  } else if (std::sscanf(argv[1], "trace-%d-%d", &layout, &shape) == 2) {
    for (int signs = 0; signs < 16; ++signs)
      for (bool populated : {false, true}) {
        Fixture fixture(layout, shape, signs, populated);
        Trace(fixture, layout, shape);
      }
  } else if (std::sscanf(argv[1], "sync-%d", &shape) == 1) {
    Fixture fixture(0, shape, 0, false);
    apmesh::generation::DisableSharedCurveSynchronization(&fixture.geometry);
    passed = Retire(fixture, 1, false);
  } else if (std::sscanf(argv[1], "consume-%d-%d", &layout, &victim) == 2) {
    Require(layout >= 0 && layout < 3 && victim >= 0 && victim < 3, "bounded consume case");
    Fixture fixture(layout, 1, 0, true);
    passed = Retire(fixture, victim, true);
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
  } else if (std::strcmp(argv[1], "order-negative-control") == 0) {
    Fixture fixture(0, 1, 0, true);
    Snapshot expected(fixture.geometry);
    auto* curve = fixture.geometry.GetCurve(0);
    curve->ClearPatches();
    for (unsigned int j = expected.counts[0]; j > 0; --j)
      curve->InsertPatch(expected.entries[0][j - 1]);
    Require(curve->GetNumBerPatches() == expected.counts[0] && !expected.MatchesExcept(nullptr),
            "same-count order corruption rejected");
    std::puts("observer_order_control=rejected");
  } else if (std::strcmp(argv[1], "empty-default") == 0 ||
             std::strcmp(argv[1], "empty-detached") == 0 ||
             std::strcmp(argv[1], "null-current") == 0) {
    passed = EmptyScenario(argv[1], false);
  } else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  } else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::strcmp(argv[1], "noalloc-empty-default") == 0 ||
        std::strcmp(argv[1], "noalloc-empty-detached") == 0 ||
        std::strcmp(argv[1], "noalloc-null-current") == 0)
      passed = EmptyScenario(argv[1] + 8, true);
    else if (std::sscanf(argv[1], "noalloc-%d-%d-%d", &layout, &victim, &seed) == 3)
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
