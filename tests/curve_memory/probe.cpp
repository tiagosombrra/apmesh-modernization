#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <list>
#include <memory>
#include <new>
#include <utility>
#include <vector>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/curve/curve_adaptive_parametric.h"

double TOLERANCE = 1e-8;
double DELTA = 1e-8;
double EPSYLON = 1e-8;

namespace {
void require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Contract failed: %s\n", message);
    std::exit(1);
  }
}

class CountedPoint : public PointAdaptive {
public:
  CountedPoint(int id, int& destroyed) : PointAdaptive(id / 8.0, 0, 0, id), destroyed_(destroyed) {}
  ~CountedPoint() override { ++destroyed_; }

private:
  int& destroyed_;
};

class CountedPatch : public Patch {
public:
  explicit CountedPatch(int& destroyed) : destroyed_(destroyed) { SetId(91); }
  ~CountedPatch() override { ++destroyed_; }

private:
  int& destroyed_;
};

template <class T> std::vector<const T*> nodes(const std::list<T>& values) {
  std::vector<const T*> result;
  for (const auto& value : values)
    result.push_back(std::addressof(value));
  return result;
}

struct Fixture {
  int& destroyed;
  int& patches_destroyed;
  std::array<std::unique_ptr<CountedPoint>, 8> points;
  CountedPatch patch;
  CurveAdaptiveParametric curve;
  std::list<PointAdaptive*> incoming_points;
  std::list<double> incoming_parameters;
  std::list<PointAdaptive*> original_points;
  std::list<double> original_parameters;
  std::vector<PointAdaptive* const*> point_nodes;
  std::vector<const double*> parameter_nodes;

  Fixture(int variant, int& destroyed_points, int& destroyed_patches)
      : destroyed(destroyed_points), patches_destroyed(destroyed_patches),
        patch(destroyed_patches) {
    for (int index = 0; index < 8; ++index)
      points[index] = std::make_unique<CountedPoint>(index, destroyed);
    curve.SetId(73);
    curve.InsertPatch(&patch);
    Matrix4x1 coefficients;
    coefficients << 0.1, 0.6, 0.3, 0.0;
    curve.SetMatGeoGx(coefficients);
    curve.CalculateLengthCurve();
    const int old_size =
        variant == 0 || variant == 6 ? 2 : (variant == 1 ? 0 : (variant == 2 ? 5 : 3));
    const int new_size =
        variant <= 1 || variant == 6 ? 5 : (variant == 2 ? 2 : (variant == 4 ? 0 : 3));
    for (int index = 0; index < old_size; ++index) {
      curve.InsertPoint(points[index].get());
      curve.parameters_.push_back(index / 8.0);
    }
    const std::array<int, 5> ids{7, 6, -1, 7, 5};
    const std::array<double, 5> values{0.875, 0.125, 0.875, 0.5, 0.25};
    for (int index = 0; index < new_size; ++index) {
      incoming_points.push_back(ids[index] < 0 ? nullptr : points[ids[index]].get());
      incoming_parameters.push_back(values[index]);
    }
    if (variant == 5) {
      incoming_points = curve.GetPoints();
      incoming_parameters = curve.parameters_;
    }
    original_points = curve.GetPoints();
    original_parameters = curve.parameters_;
    point_nodes = nodes(curve.GetPoints());
    parameter_nodes = nodes(curve.parameters_);
  }

  void replace(bool parameters, int variant) {
    if (parameters) {
      if (variant == 5)
        curve.UpdateParameters(curve.parameters_);
      else if (variant == 6)
        curve.UpdateParameters(std::move(incoming_parameters));
      else
        curve.UpdateParameters(incoming_parameters);
    } else {
      if (variant == 5)
        curve.SetPoints(curve.GetPoints());
      else if (variant == 6)
        curve.SetPoints(std::move(incoming_points));
      else
        curve.SetPoints(incoming_points);
    }
  }

  void check_observers() {
    require(destroyed == 0 && patches_destroyed == 0,
            "setters and copies never delete borrowed objects");
    for (int index = 0; index < 8; ++index)
      require(points[index]->GetId() == static_cast<unsigned long>(index) &&
                  points[index]->GetX() == index / 8.0 && points[index]->GetY() == 0 &&
                  points[index]->GetZ() == 0,
              "caller point identity and geometry are unchanged");
    require(curve.GetId() == 73 && curve.GetNumBerPatches() == 1 && curve.GetPatch(0) == &patch &&
                patch.GetId() == 91 && patch.GetSubMesh() == nullptr,
            "curve and borrowed patch state are unchanged");
    Matrix4x1 expected;
    expected << 0.1, 0.6, 0.3, 0.0;
    require(curve.GetMatGeoGx() == expected && curve.GetMatGeoGy().isZero() &&
                curve.GetMatGeoGz().isZero() && std::abs(curve.GetLength() - 1.0) < 1e-12,
            "collection mutation preserves polynomial coefficients and total length");
  }

  void check_unchanged() {
    require(curve.GetPoints() == original_points && curve.parameters_ == original_parameters,
            "failed collection replacement preserves ordered live values");
    require(nodes(curve.GetPoints()) == point_nodes && nodes(curve.parameters_) == parameter_nodes,
            "failed collection replacement preserves live list nodes");
    check_observers();
  }

  void check_success(bool parameters, int variant, const std::list<PointAdaptive*>& expected_points,
                     const std::list<double>& expected_parameters) {
    require(curve.GetPoints() == (parameters ? original_points : expected_points) &&
                curve.parameters_ == (parameters ? expected_parameters : original_parameters),
            "replacement preserves exact pointer/value order and the other collection");
    if (variant != 6)
      require(incoming_points == expected_points && incoming_parameters == expected_parameters,
              "lvalue caller input lists remain unchanged after success");
    require(parameters ? nodes(curve.GetPoints()) == point_nodes
                       : nodes(curve.parameters_) == parameter_nodes,
            "the other collection retains its live list nodes");
    check_observers();
    std::printf("collection_success=kind:%s variant:%d values:",
                parameters ? "parameters" : "points", variant);
    if (parameters) {
      for (double value : curve.parameters_)
        std::printf("%a,", value);
    } else {
      for (const auto* point : curve.GetPoints())
        std::printf("%ld,", point ? static_cast<long>(point->GetId()) : -1L);
    }
    std::puts("");
  }
};

std::unique_ptr<CurveAdaptive> make_copy(Fixture& fixture, bool parametric) {
  if (parametric)
    return std::make_unique<CurveAdaptiveParametric>(&fixture.curve);
  return std::make_unique<CurveAdaptive>(&fixture.curve);
}

void copy_contract(Fixture& fixture, bool parametric) {
  auto copy = make_copy(fixture, parametric);
  require(copy->GetId() == 73 && copy->GetPoints() == fixture.original_points &&
              copy->GetPatch(0) == &fixture.patch && copy->GetNumBerPatches() == 1 &&
              copy->GetLength() == fixture.curve.GetLength(),
          "pointer-taking copy constructor preserves scalar and borrowed collection values");
  if (parametric)
    require(static_cast<CurveAdaptiveParametric*>(copy.get())->GetMatGeoGx() ==
                fixture.curve.GetMatGeoGx(),
            "parametric copy preserves initialized coefficients");
  copy.reset();
  fixture.check_unchanged();
}

void contracts() {
  for (int kind = 0; kind < 2; ++kind) {
    for (int variant = 0; variant < 7; ++variant) {
      int destroyed = 0, patches_destroyed = 0;
      {
        Fixture fixture(variant, destroyed, patches_destroyed);
        const auto expected_points = fixture.incoming_points;
        const auto expected_parameters = fixture.incoming_parameters;
        fixture.replace(kind != 0, variant);
        fixture.check_success(kind != 0, variant, expected_points, expected_parameters);
      }
      require(destroyed == 8 && patches_destroyed == 1,
              "caller owners destroy borrowed objects once");
    }
    int destroyed = 0, patches_destroyed = 0;
    {
      Fixture fixture(0, destroyed, patches_destroyed);
      copy_contract(fixture, kind != 0);
      std::printf("collection_copy=kind:%d borrowed:1\n", kind);
    }
    require(destroyed == 8 && patches_destroyed == 1, "copied observers do not acquire ownership");
  }
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

template <class Action> int measure(Action action) {
  AllocationScope hook(-1);
  action();
  return attempts;
}
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
  require(caught && denied == 1, "every calibrated allocation denial propagates exactly once");
}

void failures(bool parameters, int variant, bool constructor) {
  const char* kind = constructor ? (parameters ? "parametric-copy" : "base-copy")
                                 : (parameters ? "parameters" : "points");
  int total = 0;
  int destroyed = 0, patches_destroyed = 0;
  {
    Fixture fixture(variant, destroyed, patches_destroyed);
    total = measure([&] {
      if (constructor)
        make_copy(fixture, parameters);
      else
        fixture.replace(parameters, variant);
    });
  }
  require(destroyed == 8 && patches_destroyed == 1, "calibrated caller teardown occurs once");
  require(total > 0, "failure sweep requires positive measured allocations");
  std::printf("collection_measured=kind:%s variant:%d allocations:%d\n", kind, variant, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    destroyed = patches_destroyed = 0;
    {
      Fixture fixture(variant, destroyed, patches_destroyed);
      const auto expected_points = fixture.incoming_points;
      const auto expected_parameters = fixture.incoming_parameters;
      std::printf("collection_inject=kind:%s variant:%d ordinal:%d\n", kind, variant, ordinal);
      inject(ordinal, [&] {
        if (constructor)
          make_copy(fixture, parameters);
        else
          fixture.replace(parameters, variant);
      });
      fixture.check_unchanged();
      require(fixture.incoming_points == expected_points &&
                  fixture.incoming_parameters == expected_parameters,
              "failure preserves caller input lists");
      if (constructor)
        copy_contract(fixture, parameters);
      else {
        fixture.replace(parameters, variant);
        fixture.check_success(parameters, variant, expected_points, expected_parameters);
      }
    }
    require(destroyed == 8 && patches_destroyed == 1,
            "failed copy/setter preserves caller ownership");
  }
  std::printf("collection_failure_sites=kind:%s variant:%d denied:%d/%d unchanged=1 retry=1\n",
              kind, variant, total, total);
}
#endif
} // namespace

int main(int argc, char** argv) {
  require(argc == 2, "one scenario required");
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
  if (std::strcmp(argv[1], "contracts") == 0)
    contracts();
  else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* expired = new PointAdaptive(1, 2, 3);
    delete expired;
    std::printf("expired-x=%g\n", expired->GetX());
  } else if (std::strcmp(argv[1], "leak") == 0)
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::strcmp(argv[1], "allocation-hook-control") == 0) {
      inject(0, [] { auto point = std::make_unique<PointAdaptive>(); });
      std::puts("allocation_hook_control=detected");
    } else if (std::strncmp(argv[1], "points-failure-", 15) == 0 && std::strlen(argv[1]) == 16 &&
               argv[1][15] >= '0' && argv[1][15] <= '5')
      failures(false, argv[1][15] - '0', false);
    else if (std::strncmp(argv[1], "parameters-failure-", 19) == 0 && std::strlen(argv[1]) == 20 &&
             argv[1][19] >= '0' && argv[1][19] <= '5')
      failures(true, argv[1][19] - '0', false);
    else if (std::strcmp(argv[1], "base-copy-failure") == 0 ||
             std::strcmp(argv[1], "parametric-copy-failure") == 0)
      failures(std::strcmp(argv[1], "parametric-copy-failure") == 0, 0, true);
    else
      require(false, "unknown scenario");
#else
    require(false, "Debug CRT allocation hook required");
#endif
  }
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  if (delta.lCounts[_NORMAL_BLOCK] != 0) {
    _CrtMemDumpAllObjectsSince(&before);
    return 1;
  }
#endif
  std::puts("PASS");
}
