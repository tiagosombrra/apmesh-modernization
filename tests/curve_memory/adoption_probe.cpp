#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <memory>
#include <new>
#include <stdexcept>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/curve/curve_adaptive_parametric_hermite.h"
#include "data/geometry.h"

double TOLERANCE = 1e-8;
double DELTA = 1e-8;
double EPSYLON = 1e-8;

namespace {
void require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}
template <class Curve> class CountedCurve : public Curve {
public:
  CountedCurve(Curve* source, int& destroyed) : Curve(source), destroyed_(destroyed) {}
  ~CountedCurve() override { ++destroyed_; }

private:
  int& destroyed_;
};
class CountedPatch : public Patch {
public:
  explicit CountedPatch(int& destroyed) : destroyed_(destroyed) { SetId(73); }
  ~CountedPatch() override { ++destroyed_; }

private:
  int& destroyed_;
};
struct Fixture {
  int kind, prefix;
  int& destroyed;
  std::array<PointAdaptive, 3> points{PointAdaptive(0, 0, 0, 10), PointAdaptive(0.5, 0, 0, 11),
                                      PointAdaptive(1, 0, 0, 12)};
  Patch patch;
  std::unique_ptr<CurveAdaptiveParametric> source;
  std::array<CurveAdaptive*, 2> old_curves{};
  std::array<Patch*, 2> old_patches{};
  Geometry geometry;
  Fixture(int curve_kind, int populated, int& counter)
      : kind(curve_kind), prefix(populated), destroyed(counter) {
    patch.SetId(91);
    if (kind == 0) {
      source = std::make_unique<CurveAdaptiveParametric>(points.front(), points.back());
      Matrix4x1 coefficients;
      coefficients << 0, 0, 1, 0;
      source->SetMatGeoGx(coefficients);
      source->CalculateLengthCurve();
    } else if (kind == 1)
      source = std::make_unique<CurveAdaptiveParametricBezier>(
          points.front(), PointAdaptive(1.0 / 3, 0, 0), PointAdaptive(2.0 / 3, 0, 0),
          points.back());
    else if (kind == 2)
      source = std::make_unique<CurveAdaptiveParametricHermite>(
          points.front(), points.back(), VectorAdaptive(1, 0, 0), VectorAdaptive(1, 0, 0));
    if (source) {
      source->SetId(73);
      source->InsertPatch(&patch);
      for (auto& point : points)
        source->InsertPoint(&point);
      source->UpdateParameters({0, 0.5, 1});
    }
    for (int i = 0; i < prefix; ++i) {
      auto curve = std::make_unique<CurveAdaptive>();
      curve->SetId(100 + i);
      old_curves[i] = curve.get();
      geometry.InsertCurve(std::move(curve));
      auto owned_patch = std::make_unique<Patch>();
      owned_patch->SetId(200 + i);
      old_patches[i] = owned_patch.get();
      geometry.InsertPatch(std::move(owned_patch));
    }
  }
  std::unique_ptr<CurveAdaptive> clone() {
    if (kind == 0)
      return std::make_unique<CountedCurve<CurveAdaptiveParametric>>(source.get(), destroyed);
    if (kind == 1)
      return std::make_unique<CountedCurve<CurveAdaptiveParametricBezier>>(
          static_cast<CurveAdaptiveParametricBezier*>(source.get()), destroyed);
    return std::make_unique<CountedCurve<CurveAdaptiveParametricHermite>>(
        static_cast<CurveAdaptiveParametricHermite*>(source.get()), destroyed);
  }
  void check_curve(CurveAdaptiveParametric& curve) {
    require(curve.GetId() == 73 && curve.parameters_ == std::list<double>({0, 0.5, 1}),
            "initialized clone preserves ID and parameter values");
    require(curve.GetNumBerPatches() == 1 && curve.GetPatch(0) == &patch &&
                curve.GetNumBerPoints() == points.size(),
            "borrowed incidence and samples survive adoption");
    for (unsigned int i = 0; i < points.size(); ++i) {
      const double t = i * 0.5;
      const auto p = curve.FindPointByParameter(t);
      const auto d = curve.CalculateGradientByParameter(t);
      require(curve.GetPoint(i) == &points[i] && points[i].GetId() == 10 + i &&
                  points[i].GetX() == t && points[i].GetY() == 0 && points[i].GetZ() == 0 &&
                  std::abs(p.GetX() - t) < 1e-12 && p.GetY() == 0 && p.GetZ() == 0 &&
                  std::abs(d.GetX() - 1) < 1e-12 && d.GetY() == 0 && d.GetZ() == 0,
              "clone agrees with independent straight-line position and derivative");
    }
    require(std::abs(curve.GetLength() - 1) < 1e-12 && patch.GetId() == 91,
            "source length and external patch remain unchanged");
  }
  void check_prefix(unsigned int extra) {
    require(geometry.GetNumberCurves() == prefix + (kind != 3 ? extra : 0) &&
                geometry.GetNumberPatches() == prefix + (kind == 3 ? extra : 0),
            "destination counts commit only on successful adoption");
    const Geometry& view = geometry;
    for (int i = 0; i < prefix; ++i)
      require(view.GetCurve(i) == old_curves[i] && view.GetCurve(i)->GetId() == 100U + i &&
                  view.GetPatch(i) == old_patches[i] && view.GetPatch(i)->GetId() == 200U + i,
              "existing owned objects retain identity, order and values");
    require(view.GetCurve(geometry.GetNumberCurves()) == nullptr &&
                view.GetPatch(geometry.GetNumberPatches()) == nullptr,
            "out-of-range access remains null");
    if (source)
      check_curve(*source);
  }
  template <class Action> void insert(bool unique, Action action) {
    if (kind == 3) {
      auto owner = std::make_unique<CountedPatch>(destroyed);
      auto* identity = owner.get();
      // Prepare and relinquish before the measured call for both overloads.
      Patch* raw = owner.release();
      action([&] {
        if (unique)
          geometry.InsertPatch(std::unique_ptr<Patch>(raw));
        else
          geometry.InsertPatch(raw);
      });
      if (geometry.GetNumberPatches() == static_cast<unsigned int>(prefix + 1))
        require(geometry.GetPatch(prefix) == identity && identity->GetId() == 73,
                "successful patch adoption preserves identity");
    } else {
      auto owner = clone();
      auto* identity = owner.get();
      CurveAdaptive* raw = owner.release();
      action([&] {
        if (unique)
          geometry.InsertCurve(std::unique_ptr<CurveAdaptive>(raw));
        else
          geometry.InsertCurve(raw);
      });
      if (geometry.GetNumberCurves() == static_cast<unsigned int>(prefix + 1)) {
        require(geometry.GetCurve(prefix) == identity,
                "successful curve adoption preserves identity");
        check_curve(*static_cast<CurveAdaptiveParametric*>(identity));
      }
    }
  }
};
void normal(int kind, int prefix, bool unique) {
  int destroyed = 0;
  {
    Fixture fixture(kind, prefix, destroyed);
    fixture.insert(unique, [](auto call) { call(); });
    fixture.check_prefix(1);
    require(destroyed == 0, "successful insertion leaves the new owner alive");
  }
  require(destroyed == 1, "Geometry destroys adopted objects exactly once");
  std::printf(
      "adoption_normal=kind:%d prefix:%d unique:%d order:1 identity:1 source:1 destroyed:%d\n",
      kind, prefix, unique, destroyed);
}
void nulls() {
  Geometry geometry;
  geometry.InsertCurve(static_cast<CurveAdaptive*>(nullptr));
  geometry.InsertCurve(std::unique_ptr<CurveAdaptive>());
  geometry.InsertPatch(static_cast<Patch*>(nullptr));
  geometry.InsertPatch(std::unique_ptr<Patch>());
  require(geometry.GetNumberCurves() == 2 && geometry.GetNumberPatches() == 2 &&
              geometry.GetCurve(0) == nullptr && geometry.GetCurve(1) == nullptr &&
              geometry.GetPatch(0) == nullptr && geometry.GetPatch(1) == nullptr,
          "null adoption preserves existing empty-slot semantics");
  std::puts("adoption_null=raw:1 unique:1 slots:2");
}
bool scenario(const char* mode, const char* name, int& kind, int& prefix, int& unique) {
  const auto n = std::strlen(name);
  if (std::strlen(mode) != n + 5 || std::strncmp(mode, name, n) != 0 || mode[n] < '0' ||
      mode[n] > '3' || mode[n + 1] != '-' || mode[n + 2] < '0' || mode[n + 2] > '1' ||
      mode[n + 3] != '-' || mode[n + 4] < '0' || mode[n + 4] > '1')
    return false;
  kind = mode[n] - '0';
  prefix = mode[n + 2] - '0';
  unique = mode[n + 4] - '0';
  return true;
}
#if defined(_MSC_VER) && defined(_DEBUG)
int attempts = 0, denied = 0, fail_after = -1;
int allocation_hook(int kind, void*, std::size_t, int, long, const unsigned char*, int) {
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
    previous_ = _CrtSetAllocHook(allocation_hook);
  }
  ~AllocationScope() { _CrtSetAllocHook(previous_); }
  AllocationScope(const AllocationScope&) = delete;
  AllocationScope& operator=(const AllocationScope&) = delete;

private:
  _CRT_ALLOC_HOOK previous_;
};
template <class Action> void inject(int ordinal, Action call) {
  bool caught = false;
  {
    AllocationScope hook(ordinal);
    try {
      call();
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  require(caught && denied == 1, "each measured denial throws exactly once");
}
void failures(int kind, int prefix, bool unique) {
  int total = 0, destroyed = 0;
  {
    Fixture fixture(kind, prefix, destroyed);
    fixture.insert(unique, [&](auto call) {
      AllocationScope hook(-1);
      call();
      total = attempts;
    });
    fixture.check_prefix(1);
  }
  require(total > 0 && destroyed == 1, "denial sweep requires positive adoption allocations");
  std::printf("adoption_measured=kind:%d prefix:%d unique:%d allocations:%d\n", kind, prefix,
              unique, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    destroyed = 0;
    {
      Fixture fixture(kind, prefix, destroyed);
      std::printf("adoption_inject=ordinal:%d\n", ordinal);
      fixture.insert(unique, [&](auto call) { inject(ordinal, call); });
      fixture.check_prefix(0);
      require(destroyed == 1, "failed adoption destroys the relinquished argument exactly once");
      fixture.insert(unique, [](auto call) { call(); });
      fixture.check_prefix(1);
      require(destroyed == 1, "retry uses a fresh live argument");
    }
    require(destroyed == 2, "retry and failure destroy their distinct arguments exactly once");
  }
  std::printf(
      "adoption_failure_sites=kind:%d prefix:%d unique:%d denied:%d/%d unchanged:1 retry:1\n", kind,
      prefix, unique, total, total);
}
#endif
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
  bool passed = true;
  try {
    require(argc == 2, "one scenario required");
    const char* mode = argv[1];
    int kind = -1, prefix = -1, unique = -1;
    if (std::strcmp(mode, "contracts") == 0) {
      for (int k = 0; k < 4; ++k)
        for (int p = 0; p < 2; ++p)
          for (int u = 0; u < 2; ++u)
            normal(k, p, u);
      nulls();
    } else if (scenario(mode, "normal-", kind, prefix, unique))
      normal(kind, prefix, unique);
    else if (std::strcmp(mode, "null") == 0)
      nulls();
    else if (std::strcmp(mode, "use-after-free") == 0) {
      auto* expired = new PointAdaptive(1, 2, 3);
      delete expired;
      std::printf("expired-x=%g\n", expired->GetX());
    } else if (std::strcmp(mode, "leak") == 0)
      std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
    else {
#if defined(_MSC_VER) && defined(_DEBUG)
      if (std::strcmp(mode, "allocation-hook-control") == 0) {
        inject(0, [] { auto point = std::make_unique<PointAdaptive>(); });
        std::puts("allocation_hook_control=detected");
      } else if (scenario(mode, "failure-", kind, prefix, unique))
        failures(kind, prefix, unique);
      else
        require(false, "unknown scenario");
#else
      require(false, "Debug CRT allocation hook required");
#endif
    }
  } catch (const std::exception& error) {
    std::fprintf(stderr, "Contract failed: %s\n", error.what());
    passed = false;
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
  if (passed)
    std::puts("PASS");
  return passed ? 0 : 1;
}
