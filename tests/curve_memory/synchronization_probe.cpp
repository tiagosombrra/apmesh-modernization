#include <array>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <memory>
#include <new>
#include <stdexcept>
#include <typeinfo>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/curve/curve_adaptive_parametric_hermite.h"
#include "data/geometry.h"
#include "data/patch/patch_bezier.h"
#include "generator/curve_synchronization.h"

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}
class CountedPoint : public PointAdaptive {
public:
  CountedPoint(double x, unsigned long id, int& destroyed)
      : PointAdaptive(x, 0, 0, id), destroyed_(destroyed) {}
  ~CountedPoint() override { ++destroyed_; }

private:
  int& destroyed_;
};
struct Fixture {
  int kind, variant;
  int& destroyed;
  std::array<std::unique_ptr<CountedPoint>, 6> points;
  std::array<CurveAdaptive*, 2> sources{};
  std::array<Patch*, 4> incidents{};
  std::array<std::unique_ptr<CurveAdaptive>, 16> constructor_curves;
  unsigned int incident_count;
  Geometry geometry;
  Fixture(int curve_kind, int graph_variant, int& counter)
      : kind(curve_kind), variant(graph_variant), destroyed(counter),
        incident_count(variant == 0   ? 2
                       : variant == 1 ? 3
                                      : 4) {
    for (int i = 0; i < 6; ++i)
      points[i] = std::make_unique<CountedPoint>((i % 3) * 0.5, 100 + i, destroyed);
    for (int i = 0; i < 2; ++i) {
      std::unique_ptr<CurveAdaptive> curve;
      const PointAdaptive first_point(0, 0, 0), last_point(1, 0, 0);
      if (kind == 0)
        curve = std::make_unique<CurveAdaptive>();
      else if (kind == 1) {
        auto value = std::make_unique<CurveAdaptiveParametric>(first_point, last_point);
        Matrix4x1 coefficients;
        coefficients << 0, 0, 1, 0;
        value->SetMatGeoGx(coefficients);
        value->CalculateLengthCurve();
        curve = std::move(value);
      } else if (kind == 2)
        curve = std::make_unique<CurveAdaptiveParametricBezier>(
            first_point, PointAdaptive(1.0 / 3, 0, 0), PointAdaptive(2.0 / 3, 0, 0), last_point);
      else
        curve = std::make_unique<CurveAdaptiveParametricHermite>(
            first_point, last_point, VectorAdaptive(1, 0, 0), VectorAdaptive(1, 0, 0));
      curve->SetId(70 + i);
      for (int j = 0; j < 3; ++j)
        curve->InsertPoint(points[3 * i + (i == 0 ? j : 2 - j)].get());
      if (auto* parametric = dynamic_cast<CurveAdaptiveParametric*>(curve.get()))
        parametric->UpdateParameters(i == 0 ? std::list<double>{0, 0.5, 1}
                                            : std::list<double>{1, 0.5, 0});
      sources[i] = curve.get();
      geometry.InsertCurve(std::move(curve));
    }
    for (unsigned int i = 0; i < incident_count; ++i) {
      std::unique_ptr<Patch> patch;
      if ((variant == 2 && i % 2 == 0) || variant == 3)
        patch = std::make_unique<Patch>();
      else {
        std::array<PointAdaptive, 16> p;
        for (int j = 0; j < 16; ++j)
          p[j] = PointAdaptive((j / 4) / 3.0, (j % 4) / 3.0, 0);
        auto bezier = std::make_unique<PatchBezier>(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7],
                                                    p[8], p[9], p[10], p[11], p[12], p[13], p[14],
                                                    p[15], true, false, true, false);
        // The control-net constructor creates four curves. The fixture owns those
        // while replacing their observers with the two shared sources.
        for (unsigned int e = 0; e < 4; ++e) {
          constructor_curves[4 * i + e].reset(bezier->GetCurve(e));
          bezier->ReplaceCurve(e, sources[e % 2]);
        }
        patch = std::move(bezier);
      }
      patch->SetId(90 + i);
      incidents[i] = patch.get();
      geometry.InsertPatch(std::move(patch));
    }
    for (auto* source : sources) {
      if (variant == 1)
        source->InsertPatch(nullptr);
      for (unsigned int i = 0; i < incident_count; ++i)
        source->InsertPatch(incidents[i]);
      if (variant == 1)
        source->InsertPatch(nullptr);
    }
  }
  unsigned int clone_count() const { return variant == 3 ? 0 : variant == 0 ? 1 : 2; }
  void check_values(CurveAdaptive& curve, unsigned int source_index) {
    require(typeid(curve) == typeid(*sources[source_index]),
            "cloning preserves the actual dynamic curve type");
    require(curve.GetId() == 70 + source_index && curve.GetNumBerPoints() == 3 && destroyed == 0,
            "clone/source values and borrowed samples remain alive");
    for (unsigned int j = 0; j < 3; ++j) {
      unsigned int index = source_index * 3 + (source_index == 0 ? j : 2 - j);
      auto* point = points[index].get();
      require(curve.GetPoint(j) == point && point->GetId() == 100 + index &&
                  point->GetX() == (index % 3) * 0.5 && point->GetY() == 0 && point->GetZ() == 0,
              "ordered borrowed sample identities and values are preserved");
    }
    if (kind != 0) {
      auto& parametric = static_cast<CurveAdaptiveParametric&>(curve);
      require(parametric.parameters_ ==
                  (source_index == 0 ? std::list<double>{0, 0.5, 1} : std::list<double>{1, 0.5, 0}),
              "forward/reversed parameter pairing survives publication");
      for (double t : {0.0, 0.5, 1.0}) {
        auto p = parametric.FindPointByParameter(t);
        auto d = parametric.CalculateGradientByParameter(t);
        require(std::abs(p.GetX() - t) < 1e-12 && p.GetY() == 0 && p.GetZ() == 0 &&
                    std::abs(d.GetX() - 1) < 1e-12 && d.GetY() == 0 && d.GetZ() == 0,
                "actual copied curve agrees with independent line position/derivative");
      }
    }
  }
  unsigned int check_graph(bool complete, bool trace) {
    unsigned int committed = 0, next_clone = 2;
    bool unchanged_seen = false;
    for (unsigned int s = 0; s < sources.size(); ++s) {
      auto& source = *sources[s];
      check_values(source, s);
      const bool done = source.GetNumBerPatches() == 1;
      if (done) {
        require(!unchanged_seen && source.GetPatch(0) == incidents[0],
                "commits form an ordered prefix");
        ++committed;
      } else {
        unchanged_seen = true;
        const unsigned int expected = incident_count + (variant == 1 ? 2 : 0);
        require(source.GetNumBerPatches() == expected,
                "failing source retains every original incidence");
        for (unsigned int p = 0; p < expected; ++p) {
          auto* expected_patch = variant == 1 && (p == 0 || p + 1 == expected)
                                     ? nullptr
                                     : incidents[p - (variant == 1 ? 1 : 0)];
          require(source.GetPatch(p) == expected_patch,
                  "failed source retains incidence order and null entries");
        }
      }
      for (unsigned int p = 0; p < incident_count; ++p) {
        auto* patch = dynamic_cast<PatchBezier*>(incidents[p]);
        if (!patch)
          continue;
        auto* expected = &source;
        if (done && p > 0) {
          expected = geometry.GetCurve(next_clone++);
          require(expected != nullptr && expected != &source && expected->GetNumBerPatches() == 1 &&
                      expected->GetPatch(0) == patch,
                  "each published clone has its sole target incidence");
          check_values(*expected, s);
        }
        for (unsigned int e = s; e < 4; e += 2)
          require(patch->GetCurve(e) == expected,
                  "failure preserves coherent curve-to-patch back references");
        for (unsigned int e = 0; e < 4; ++e)
          require(patch->IsCurveReversed(e) == (e % 2 == 1),
                  "publication preserves incidence orientation");
        auto position = patch->Parameterize(0.25, 0.75);
        require(std::abs(position.GetX() - 0.25) < 1e-12 &&
                    std::abs(position.GetY() - 0.75) < 1e-12 && position.GetZ() == 0,
                "publication preserves independently checked patch control-net geometry");
      }
    }
    require(geometry.GetNumberCurves() == 2 + committed * clone_count() &&
                geometry.GetNumberPatches() == incident_count,
            "failed curve publishes no partial clone suffix");
    require(!complete || committed == 2, "successful operation commits all shared curves");
    if (trace)
      std::printf("sync_graph=kind:%d variant:%d committed:%u clones:%u orientation:1 values:1\n",
                  kind, variant, committed, geometry.GetNumberCurves() - 2);
    return committed;
  }
};
void normal(int kind, int variant) {
  int destroyed = 0;
  {
    Fixture fixture(kind, variant, destroyed);
    apmesh::generation::DisableSharedCurveSynchronization(&fixture.geometry);
    fixture.check_graph(true, true);
    apmesh::generation::DisableSharedCurveSynchronization(&fixture.geometry);
    fixture.check_graph(true, false);
  }
  require(destroyed == 6, "external owners destroy all samples exactly once");
}
void helper(int kind, bool null_patch) {
  int destroyed = 0;
  {
    Fixture fixture(kind, 0, destroyed);
    auto* source = fixture.sources[0];
    source->ClearPatches();
    auto copy =
        apmesh::generation::CloneCurveForPatch(source, null_patch ? nullptr : fixture.incidents[1]);
    require(copy && copy.get() != source && copy->GetNumBerPatches() == (null_patch ? 0U : 1U),
            "helper returns an exclusive pending owner");
    if (!null_patch)
      require(copy->GetPatch(0) == fixture.incidents[1], "helper borrows the requested patch");
    fixture.check_values(*copy, 0);
    fixture.check_values(*source, 0);
    require(source->GetNumBerPatches() == 0, "helper preserves source incidence containers");
    copy.reset();
    fixture.check_values(*source, 0);
  }
  require(destroyed == 6, "helper does not own borrowed samples");
  std::printf("sync_helper=kind:%d null:%d values:1 lifetime:1\n", kind, null_patch);
}
void guards() {
  apmesh::generation::DisableSharedCurveSynchronization(nullptr);
  require(!apmesh::generation::CloneCurveForPatch(nullptr, nullptr), "null source remains null");
  Geometry geometry;
  geometry.InsertCurve(static_cast<CurveAdaptive*>(nullptr));
  auto curve = std::make_unique<CurveAdaptive>();
  auto* original = curve.get();
  Patch patch;
  curve->InsertPatch(nullptr);
  curve->InsertPatch(&patch);
  geometry.InsertCurve(std::move(curve));
  apmesh::generation::DisableSharedCurveSynchronization(&geometry);
  require(geometry.GetNumberCurves() == 2 && geometry.GetCurve(1) == original &&
              original->GetNumBerPatches() == 2 && original->GetPatch(0) == nullptr &&
              original->GetPatch(1) == &patch,
          "filtered singleton and null curve preserve the original no-op behavior");
  std::puts("sync_guards=null-source:1 null-geometry:1 filtered-singleton:1");
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
template <class Action> void inject(int ordinal, Action action) {
  bool caught = false;
  {
    AllocationScope hook(ordinal);
    try {
      action();
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  require(caught && denied == 1, "each measured denial throws exactly once");
}
void failures(int kind, int variant, bool direct) {
  int total = 0, destroyed = 0;
  {
    Fixture fixture(kind, variant, destroyed);
    if (direct)
      fixture.sources[0]->ClearPatches();
    {
      AllocationScope hook(-1);
      if (direct) {
        auto copy =
            apmesh::generation::CloneCurveForPatch(fixture.sources[0], fixture.incidents[1]);
      } else
        apmesh::generation::DisableSharedCurveSynchronization(&fixture.geometry);
      total = attempts;
    }
    if (!direct)
      fixture.check_graph(true, false);
  }
  require(total > 0 && destroyed == 6, "failure sweep requires positive successful allocations");
  std::printf("sync_measured=kind:%d variant:%d direct:%d allocations:%d\n", kind, variant, direct,
              total);
  unsigned int committed_failures = 0;
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    destroyed = 0;
    {
      Fixture fixture(kind, variant, destroyed);
      std::printf("sync_inject=ordinal:%d\n", ordinal);
      if (direct) {
        fixture.sources[0]->ClearPatches();
        inject(ordinal, [&] {
          auto copy =
              apmesh::generation::CloneCurveForPatch(fixture.sources[0], fixture.incidents[1]);
        });
        fixture.check_values(*fixture.sources[0], 0);
        require(fixture.sources[0]->GetNumBerPatches() == 0,
                "failed helper preserves source incidences");
        auto retry =
            apmesh::generation::CloneCurveForPatch(fixture.sources[0], fixture.incidents[1]);
        require(retry && retry->GetNumBerPatches() == 1,
                "helper retry completes with target incidence");
        fixture.check_values(*retry, 0);
      } else {
        inject(ordinal,
               [&] { apmesh::generation::DisableSharedCurveSynchronization(&fixture.geometry); });
        if (fixture.check_graph(false, false) > 0)
          ++committed_failures;
        apmesh::generation::DisableSharedCurveSynchronization(&fixture.geometry);
        fixture.check_graph(true, false);
      }
    }
    require(destroyed == 6, "failed graph/helper and retry preserve external sample ownership");
  }
  if (!direct)
    require(committed_failures > 0,
            "multi-curve sweep must observe a committed prefix before later failure");
  std::printf("sync_failure_sites=kind:%d variant:%d direct:%d denied:%d/%d prefix:%u retry:1\n",
              kind, variant, direct, total, total, committed_failures);
}
#endif
bool scenario(const char* mode, const char* prefix, int& kind, int& variant) {
  const auto n = std::strlen(prefix);
  if (std::strlen(mode) != n + 3 || std::strncmp(mode, prefix, n) != 0 || mode[n] < '0' ||
      mode[n] > '3' || mode[n + 1] != '-' || mode[n + 2] < '0' || mode[n + 2] > '3')
    return false;
  kind = mode[n] - '0';
  variant = mode[n + 2] - '0';
  return true;
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
  bool passed = true;
  try {
    require(argc == 2, "one scenario required");
    const char* mode = argv[1];
    int kind = -1, variant = -1;
    if (std::strcmp(mode, "contracts") == 0) {
      for (int k = 0; k < 4; ++k) {
        for (int v = 0; v < 4; ++v)
          normal(k, v);
        for (int v = 0; v < 2; ++v)
          helper(k, v);
      }
      guards();
    } else if (scenario(mode, "normal-", kind, variant))
      normal(kind, variant);
    else if (scenario(mode, "helper-", kind, variant) && variant < 2)
      helper(kind, variant);
    else if (std::strcmp(mode, "guards") == 0)
      guards();
    else if (std::strcmp(mode, "use-after-free") == 0) {
      auto* p = new PointAdaptive(1, 2, 3);
      delete p;
      std::printf("expired=%g\n", p->GetX());
    } else if (std::strcmp(mode, "leak") == 0)
      std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
    else {
#if defined(_MSC_VER) && defined(_DEBUG)
      if (scenario(mode, "failure-", kind, variant))
        failures(kind, variant, false);
      else if (scenario(mode, "helper-failure-", kind, variant) && variant == 0)
        failures(kind, 0, true);
      else if (std::strcmp(mode, "allocation-hook-control") == 0) {
        inject(0, [] { auto p = std::make_unique<PointAdaptive>(); });
        std::puts("allocation_hook_control=detected");
      } else
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
