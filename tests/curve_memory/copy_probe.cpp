#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <list>
#include <memory>
#include <new>
#include <vector>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/curve/curve_adaptive_parametric_hermite.h"

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
double position(double t) { return 0.3 * t + 0.6 * t * t + 0.1 * t * t * t; }
std::array<double, 3> coordinates(const PointAdaptive& p) { return {p.GetX(), p.GetY(), p.GetZ()}; }
std::array<double, 3> coordinates(const VectorAdaptive& v) {
  return {v.GetX(), v.GetY(), v.GetZ()};
}
bool same_point(const PointAdaptive& a, const PointAdaptive& b) {
  return a.GetId() == b.GetId() && coordinates(a) == coordinates(b);
}
template <class T> std::vector<const T*> nodes(const std::list<T>& values) {
  std::vector<const T*> result;
  for (const auto& value : values)
    result.push_back(std::addressof(value));
  return result;
}
class CountedPoint : public PointAdaptive {
public:
  CountedPoint(double t, unsigned long id, int& destroyed)
      : PointAdaptive(position(t), 0, 0, id), destroyed_(destroyed) {}
  ~CountedPoint() override { ++destroyed_; }

private:
  int& destroyed_;
};
class CountedPatch : public Patch {
public:
  CountedPatch(unsigned int id, int& destroyed) : destroyed_(destroyed) { SetId(id); }
  ~CountedPatch() override { ++destroyed_; }

private:
  int& destroyed_;
};

struct Fixture {
  int kind, variant;
  int& destroyed;
  int& patches_destroyed;
  const std::array<double, 5> sample_parameters{0, 0.125, 0.5, 0.875, 1};
  std::array<std::unique_ptr<CountedPoint>, 5> samples;
  std::array<std::unique_ptr<CountedPatch>, 2> patches;
  std::unique_ptr<CurveAdaptiveParametric> source;
  std::list<PointAdaptive*> original_points;
  std::list<double> original_parameters;
  std::vector<PointAdaptive* const*> point_nodes;
  std::vector<const double*> parameter_nodes;
  PointAdaptive point0, point1, point2, point3;
  VectorAdaptive vector0, vector1;
  Matrix4x1 gx, gy, gz;
  Matrix4x4 basis;
  Matrix1x4 scratch;
  double length;

  Fixture(int curve_kind, int sequence, int& destroyed_points, int& destroyed_patches)
      : kind(curve_kind), variant(sequence), destroyed(destroyed_points),
        patches_destroyed(destroyed_patches) {
    for (int i = 0; i < 5; ++i)
      samples[i] = std::make_unique<CountedPoint>(sample_parameters[i], 100 + i, destroyed);
    patches[0] = std::make_unique<CountedPatch>(91, patches_destroyed);
    patches[1] = std::make_unique<CountedPatch>(92, patches_destroyed);
    const PointAdaptive first(0, 0, 0, 10), last(1, 0, 0, 13);
    if (kind == 0) {
      source = std::make_unique<CurveAdaptiveParametric>(first, last);
      Matrix4x1 coefficients;
      coefficients << 0.1, 0.6, 0.3, 0;
      source->SetMatGeoGx(coefficients);
      source->CalculateLengthCurve();
    } else if (kind == 1)
      source = std::make_unique<CurveAdaptiveParametricBezier>(first, PointAdaptive(0.1, 0, 0, 11),
                                                               PointAdaptive(0.4, 0, 0, 12), last);
    else
      source = std::make_unique<CurveAdaptiveParametricHermite>(
          first, last, VectorAdaptive(0.3, 0, 0), VectorAdaptive(1.8, 0, 0));
    source->SetId(73);
    for (const auto& patch : patches)
      source->InsertPatch(patch.get());
    if (variant != 0) {
      for (int i = 0; i < 5; ++i) {
        const int sample = variant == 2 ? 4 - i : i;
        source->InsertPoint(samples[sample].get());
        source->parameters_.push_back(sample_parameters[sample]);
      }
    }
    original_points = source->GetPoints();
    original_parameters = source->parameters_;
    point_nodes = nodes(source->GetPoints());
    parameter_nodes = nodes(source->parameters_);
    point0 = source->GetPoint0();
    point1 = source->GetPoint1();
    gx = source->GetMatGeoGx();
    gy = source->GetMatGeoGy();
    gz = source->GetMatGeoGz();
    basis = source->GetMatBase();
    scratch = source->GetMatParameters();
    length = source->GetLength();
    require(std::abs(length - 1) < 1e-12, "initialized analytic source has unit physical length");
    if (kind == 1) {
      point2 = static_cast<CurveAdaptiveParametricBezier*>(source.get())->GetPoint2();
      point3 = static_cast<CurveAdaptiveParametricBezier*>(source.get())->GetPoint3();
    } else if (kind == 2) {
      vector0 = static_cast<CurveAdaptiveParametricHermite*>(source.get())->GetVector0();
      vector1 = static_cast<CurveAdaptiveParametricHermite*>(source.get())->GetVector1();
    }
  }
  std::unique_ptr<CurveAdaptiveParametric> copy() {
    if (kind == 1)
      return std::make_unique<CurveAdaptiveParametricBezier>(
          static_cast<CurveAdaptiveParametricBezier*>(source.get()));
    if (kind == 2)
      return std::make_unique<CurveAdaptiveParametricHermite>(
          static_cast<CurveAdaptiveParametricHermite*>(source.get()));
    return std::make_unique<CurveAdaptiveParametric>(source.get());
  }
  void check_objects() {
    require(destroyed == 0 && patches_destroyed == 0,
            "curve copies never destroy borrowed samples or patches");
    for (int i = 0; i < 5; ++i)
      require(samples[i]->GetId() == static_cast<unsigned long>(100 + i) &&
                  coordinates(*samples[i]) ==
                      std::array<double, 3>{position(sample_parameters[i]), 0, 0},
              "caller sample ID and geometry survive copy and destruction");
    for (int i = 0; i < 2; ++i)
      require(patches[i]->GetId() == static_cast<unsigned int>(91 + i) &&
                  patches[i]->GetSubMesh() == nullptr,
              "borrowed patch state is unchanged");
  }
  void check_fields(CurveAdaptiveParametric& curve) {
    require(curve.GetId() == 73 && curve.GetLength() == length &&
                same_point(curve.GetPoint0(), point0) && same_point(curve.GetPoint1(), point1) &&
                curve.GetMatGeoGx() == gx && curve.GetMatGeoGy() == gy &&
                curve.GetMatGeoGz() == gz && curve.GetMatBase() == basis &&
                curve.GetMatParameters() == scratch,
            "copy preserves initialized scalar, endpoint, coefficient, basis and scratch state");
    require(curve.GetPoints() == original_points && curve.GetNumBerPatches() == 2 &&
                curve.GetPatch(0) == patches[0].get() && curve.GetPatch(1) == patches[1].get(),
            "copy preserves ordered borrowed sample and patch identities");
    if (kind == 1) {
      auto& bezier = static_cast<CurveAdaptiveParametricBezier&>(curve);
      require(same_point(bezier.GetPoint2(), point2) && same_point(bezier.GetPoint3(), point3),
              "Bezier copy preserves its additional control values and IDs");
    } else if (kind == 2) {
      auto& hermite = static_cast<CurveAdaptiveParametricHermite&>(curve);
      require(coordinates(hermite.GetVector0()) == coordinates(vector0) &&
                  coordinates(hermite.GetVector1()) == coordinates(vector1),
              "Hermite copy preserves its tangent vectors");
    }
    check_objects();
  }
  void check_source() {
    require(source != nullptr, "source lifetime is active for source-stability checks");
    check_fields(*source);
    require(source->parameters_ == original_parameters &&
                nodes(source->GetPoints()) == point_nodes &&
                nodes(source->parameters_) == parameter_nodes,
            "copy failure or mutation preserves source sequence values and element nodes");
  }
  void check_copy(CurveAdaptiveParametric& curve, bool trace, bool source_alive = true) {
    check_fields(curve);
    if (source_alive)
      for (const auto* copied : nodes(curve.GetPoints()))
        for (const auto* original : point_nodes)
          require(copied != original, "sample containers have independent list nodes");
    for (int i = 0; i < 5; ++i) {
      const double t = sample_parameters[i];
      const auto point = curve.FindPointByParameter(t);
      const auto gradient = curve.CalculateGradientByParameter(t);
      require(std::abs(point.GetX() - position(t)) < 1e-12 && point.GetY() == 0 &&
                  point.GetZ() == 0 &&
                  std::abs(gradient.GetX() - (0.3 + 1.2 * t + 0.3 * t * t)) < 1e-12 &&
                  gradient.GetY() == 0 && gradient.GetZ() == 0,
              "copied evaluator agrees with independent cubic position and derivative");
      if (trace)
        std::printf("copy_geometry=kind:%d variant:%d sample:%d x:%a gradient:%a\n", kind, variant,
                    i, point.GetX(), gradient.GetX());
    }
    const double arc = curve.CalculateParametricLength(0.125, 0.875);
    const double reverse_arc = curve.CalculateParametricLength(0.875, 0.125);
    require(std::abs(arc - (position(0.875) - position(0.125))) < 1e-12 &&
                std::abs(reverse_arc + arc) < 1e-12,
            "copied evaluator preserves independently checked signed arc integrals");
    if (trace)
      std::printf("copy_arc=kind:%d variant:%d value:%a reverse:%a\n", kind, variant, arc,
                  reverse_arc);
    require(curve.parameters_ == original_parameters &&
                curve.parameters_.size() == curve.GetNumBerPoints(),
            "copied parameter sequence preserves sampled-point pairing and order");
    if (source_alive)
      for (const auto* copied : nodes(curve.parameters_))
        for (const auto* original : parameter_nodes)
          require(copied != original, "copied parameter values have independent list nodes");
    auto parameter = curve.parameters_.begin();
    for (const auto* point : curve.GetPoints()) {
      require(parameter != curve.parameters_.end() &&
                  std::abs(curve.FindPointByParameter(*parameter).GetX() - point->GetX()) < 1e-12,
              "actual copied point/parameter traversal preserves physical sample correspondence");
      ++parameter;
    }
    if (trace)
      std::printf("copy_values=kind:%d variant:%d parameters:%zu pairs:%u independent:1\n", kind,
                  variant, curve.parameters_.size(), curve.GetNumBerPoints());
    check_objects();
  }
};

void normal(int kind, int variant) {
  int destroyed = 0, patches_destroyed = 0;
  {
    Fixture fixture(kind, variant, destroyed, patches_destroyed);
    auto copy = fixture.copy();
    fixture.check_copy(*copy, true);
    if (!copy->parameters_.empty())
      copy->parameters_.front() = 0.75;
    copy->GetPoints().clear();
    copy->ClearPatches();
    fixture.check_source();
    copy.reset();
    fixture.check_source();
    auto survivor = fixture.copy();
    fixture.source.reset();
    fixture.check_copy(*survivor, false, false);
    survivor.reset();
    fixture.check_objects();
    std::printf("copy_lifetimes=kind:%d variant:%d copy-first:1 source-first:1\n", kind, variant);
  }
  require(destroyed == 5 && patches_destroyed == 2,
          "external owners destroy each borrowed object exactly once");
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
  require(caught && denied == 1, "each calibrated allocation denial propagates exactly once");
}
void failures(int kind, int variant) {
  int total = 0, destroyed = 0, patches_destroyed = 0;
  {
    Fixture fixture(kind, variant, destroyed, patches_destroyed);
    {
      AllocationScope hook(-1);
      fixture.copy();
      total = attempts;
    }
    require(total > 0, "constructor denial sweep requires positive measured allocations");
    std::printf("copy_measured=kind:%d variant:%d allocations:%d\n", kind, variant, total);
    auto calibration = fixture.copy();
    fixture.check_copy(*calibration, false);
    calibration.reset();
    fixture.check_source();
  }
  require(destroyed == 5 && patches_destroyed == 2, "calibration preserves caller ownership");
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    destroyed = patches_destroyed = 0;
    {
      Fixture fixture(kind, variant, destroyed, patches_destroyed);
      std::printf("copy_inject=kind:%d variant:%d ordinal:%d\n", kind, variant, ordinal);
      inject(ordinal, [&] { fixture.copy(); });
      fixture.check_source();
      auto retry = fixture.copy();
      fixture.check_copy(*retry, false);
      retry.reset();
      fixture.check_source();
    }
    require(destroyed == 5 && patches_destroyed == 2,
            "failed construction preserves external ownership");
  }
  std::printf("copy_failure_sites=kind:%d variant:%d denied:%d/%d unchanged=1 retry=1\n", kind,
              variant, total, total);
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
  const char* mode = argv[1];
  if (std::strcmp(mode, "contracts") == 0) {
    for (int kind = 0; kind < 3; ++kind)
      for (int variant = 0; variant < 3; ++variant)
        normal(kind, variant);
  } else if (std::strncmp(mode, "copy-", 5) == 0 && std::strlen(mode) == 8 && mode[5] >= '0' &&
             mode[5] <= '2' && mode[6] == '-' && mode[7] >= '0' && mode[7] <= '2')
    normal(mode[5] - '0', mode[7] - '0');
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
    } else if (std::strncmp(mode, "failure-", 8) == 0 && std::strlen(mode) == 11 &&
               mode[8] >= '0' && mode[8] <= '2' && mode[9] == '-' && mode[10] >= '0' &&
               mode[10] <= '2')
      failures(mode[8] - '0', mode[10] - '0');
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
