#include "data/geometry.h"
#include "data/patch/patch_hermite.h"

#include <array>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void Require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Original Hermite observation failed: %s\n", message);
    std::exit(2);
  }
}

struct Fixture {
  Patch parent;
  Geometry geometry;
  std::array<CurveAdaptive*, 4> slots{};
  std::array<std::unique_ptr<PatchHermite>, 3> patches;

  explicit Fixture(int layout) {
    parent.SetId(77);
    PointAdaptive p00(0, 0, 0), p10(1, 0, 0), p01(0, 1, 0), p11(1, 1, 0.25);
    VectorAdaptive u0(1, 0, 0), u1(1, 0, 0.25), v0(0, 1, 0), v1(0, 1, 0.25);
    std::array<std::unique_ptr<CurveAdaptive>, 4> curves{
        std::make_unique<CurveAdaptiveParametricHermite>(p00, p10, u0, u0),
        std::make_unique<CurveAdaptiveParametricHermite>(p10, p11, v1, v1),
        std::make_unique<CurveAdaptiveParametricHermite>(p01, p11, u1, u1),
        std::make_unique<CurveAdaptiveParametricHermite>(p00, p01, v0, v0)};
    for (auto& curve : curves) {
      curve->InsertPatch(&parent);
      curve->InsertPatch(nullptr);
      curve->InsertPatch(&parent);
      geometry.InsertCurve(std::move(curve));
    }
    for (unsigned int i = 0; i < slots.size(); ++i)
      slots[i] = geometry.GetCurve(layout == 0 ? i : layout == 1 ? i / 2 : 0);
    VectorAdaptive twist(0, 0, 0.25);
    for (unsigned int i = 0; i < patches.size(); ++i) {
      patches[i] = std::make_unique<PatchHermite>(slots[0], slots[1], slots[2], slots[3], twist,
                                                  twist, twist, twist);
      patches[i]->SetId(100 + i);
    }
  }

  void Remove(Patch* patch) {
    for (unsigned int i = 0; i < geometry.GetNumberCurves(); ++i)
      geometry.GetCurve(i)->RemovePatchObservers(patch);
  }
};

struct Snapshot {
  std::array<CurveAdaptive*, 4> curves{};
  std::array<std::array<Patch*, 32>, 4> entries{};
  std::array<unsigned int, 4> counts{};

  explicit Snapshot(Fixture& fixture) {
    for (unsigned int i = 0; i < curves.size(); ++i) {
      curves[i] = fixture.geometry.GetCurve(i);
      counts[i] = curves[i]->GetNumBerPatches();
      Require(counts[i] <= entries[i].size(), "bounded observer inventory");
      for (unsigned int j = 0; j < counts[i]; ++j)
        entries[i][j] = curves[i]->GetPatch(j);
    }
  }

  bool Matches(Patch* omitted) const {
    for (unsigned int i = 0; i < curves.size(); ++i) {
      unsigned int cursor = 0;
      for (unsigned int j = 0; j < counts[i]; ++j)
        if (omitted == nullptr || entries[i][j] != omitted) {
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

unsigned int Count(Fixture& fixture, Patch* target) {
  unsigned int count = 0;
  for (unsigned int i = 0; i < fixture.geometry.GetNumberCurves(); ++i) {
    auto* curve = fixture.geometry.GetCurve(i);
    for (unsigned int j = 0; j < curve->GetNumBerPatches(); ++j)
      count += curve->GetPatch(j) == target;
  }
  return count;
}

void Live(int layout) {
  Fixture fixture(layout);
  Snapshot before(fixture);
  unsigned int evaluated = 0;
  for (auto& patch : fixture.patches) {
    Require(Count(fixture, patch.get()) == 4, "four reciprocal constructor publications");
    for (unsigned int i = 0; i < 4; ++i)
      Require(patch->GetCurve(i) == fixture.slots[i] && !patch->IsCurveReversed(i),
              "slot identities and inherited orientation fallback");
    for (double u : {0.0, 0.25, 0.5, 0.75, 1.0})
      for (double v : {0.0, 0.25, 0.5, 0.75, 1.0}) {
        auto p = patch->Parameterize(u, v);
        Require(std::isfinite(p.GetX()) && std::isfinite(p.GetY()) && std::isfinite(p.GetZ()),
                "live finite evaluation");
        if (layout == 0)
          Require(std::abs(p.GetX() - u) < 1e-12 && std::abs(p.GetY() - v) < 1e-12 &&
                      std::abs(p.GetZ() - 0.25 * u * v) < 1e-12,
                  "independent bilinear fixture");
        ++evaluated;
      }
  }
  Require(before.Matches(nullptr), "live evaluation preserves all observer entries");
  std::printf("live layout=%d evaluated_points=%u constructor_publications=12\n", layout,
              evaluated);
  for (auto& patch : fixture.patches)
    fixture.Remove(patch.get());
}

void Retire(int layout, unsigned int victim, bool cleanup, bool consume) {
  Fixture fixture(layout);
  auto* retired = fixture.patches[victim].get();
  unsigned int used = 0;
  for (unsigned int i = 0; i < fixture.geometry.GetNumberCurves(); ++i) {
    auto* curve = fixture.geometry.GetCurve(i);
    bool present = false;
    for (auto* slot : fixture.slots)
      present |= slot == curve;
    if (present) {
      ++used;
      curve->InsertPatch(retired);
      curve->InsertPatch(nullptr);
      curve->InsertPatch(retired);
    }
  }
  Snapshot before(fixture);
  const auto expected = 4 + 2 * used;
  Require(Count(fixture, retired) == expected, "original and repeated publications present");
  if (cleanup)
    fixture.Remove(retired);
  fixture.patches[victim].reset();
  const auto stale = Count(fixture, retired);
  Require(stale == (cleanup ? 0U : expected), "original retirement observation");
  Require(before.Matches(cleanup ? retired : nullptr), "complete stable observer inventory");
  std::printf("retirement layout=%d victim=%u explicit_cleanup=%d stale_observers=%u\n", layout,
              victim, cleanup, stale);
  if (consume) {
    std::printf("consume_observers=1 expected_expired=%d\n", !cleanup);
    unsigned int total = 0;
    for (unsigned int i = 0; i < fixture.geometry.GetNumberCurves(); ++i) {
      auto* curve = fixture.geometry.GetCurve(i);
      for (unsigned int j = 0; j < curve->GetNumBerPatches(); ++j)
        if (auto* patch = curve->GetPatch(j))
          total += patch->GetId();
    }
    std::printf("observer_id_sum=%u\n", total);
  }
  // Remaining observers are inventoried without dereferencing expired entries.
  // The explicit reference path removes only the chosen live target before retirement.
}

void GeometryOwned() {
  Fixture fixture(0);
  for (auto& patch : fixture.patches)
    fixture.geometry.InsertPatch(std::move(patch));
  Require(fixture.geometry.GetNumberPatches() == 3 && fixture.geometry.GetNumberCurves() == 4,
          "actual Geometry adoption");
  std::puts("geometry_owned_curves=4 patches=3 no_post_retirement_observer_consumption=1");
}

void OracleControls() {
  Fixture fixture(0);
  Snapshot before(fixture);
  auto* curve = fixture.geometry.GetCurve(0);
  curve->InsertPatch(nullptr);
  Require(!before.Matches(nullptr), "independent count corruption rejected");
  curve->ClearPatches();
  for (unsigned int j = before.counts[0]; j > 0; --j)
    curve->InsertPatch(before.entries[0][j - 1]);
  Require(curve->GetNumBerPatches() == before.counts[0] && !before.Matches(nullptr),
          "independent same-count order corruption rejected");
  std::puts("oracle_corruptions=2 rejected=2");
}

void UafControl() {
  auto* patch = new Patch;
  patch->SetId(431);
  delete patch;
  std::printf("independent_expired_id=%u\n", patch->GetId());
}
} // namespace

int main(int argc, char** argv) {
  std::setvbuf(stdout, nullptr, _IONBF, 0);
  Require(argc >= 2, "mode required");
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  const char* mode = argv[1];
  if (std::strcmp(mode, "live") == 0) {
    Require(argc == 3, "layout required");
    Live(std::atoi(argv[2]));
  } else if (std::strcmp(mode, "inventory") == 0 || std::strcmp(mode, "cleanup") == 0 ||
             std::strcmp(mode, "consume") == 0) {
    Require(argc == 4, "layout and victim required");
    const auto layout = std::atoi(argv[2]), victim = std::atoi(argv[3]);
    Require(layout >= 0 && layout < 3 && victim >= 0 && victim < 3, "bounded layout/victim");
    Retire(layout, static_cast<unsigned int>(victim), std::strcmp(mode, "cleanup") == 0,
           std::strcmp(mode, "inventory") != 0);
  } else if (std::strcmp(mode, "default") == 0) {
    PatchHermite patch;
    Require(patch.GetNumBerCurves() == 0 && patch.GetSubMesh() == nullptr, "empty topology only");
    std::puts("default_empty_topology=1 numeric_fields_not_evaluated=1");
  } else if (std::strcmp(mode, "geometry") == 0) {
    GeometryOwned();
  } else if (std::strcmp(mode, "oracle") == 0) {
    OracleControls();
  } else if (std::strcmp(mode, "uaf-control") == 0) {
    UafControl();
  } else if (std::strcmp(mode, "leak-control") == 0) {
    auto* point = new PointAdaptive(3, 4, 5);
    std::printf("independent_leaked_point=%p\n", static_cast<void*>(point));
  } else {
    Require(false, "known mode");
  }
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  return delta.lCounts[_NORMAL_BLOCK] == 0 && delta.lSizes[_NORMAL_BLOCK] == 0 ? 0 : 1;
#else
  return 0;
#endif
}
