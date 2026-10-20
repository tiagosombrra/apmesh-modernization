#include "estimate/charge_estimate_process.h"

#include <array>
#include <memory>
#include <utility>

extern std::string INPUT_MODEL;

namespace {
// The constructor appends observers before it can finish. Restore only that
// suffix if construction, evaluation or consuming Geometry adoption fails.
// Curves remain live and their pre-existing observer prefix is borrowed.
class PatchObserverScope {
public:
  explicit PatchObserverScope(std::array<CurveAdaptive*, 4> curves) noexcept : curves_(curves) {
    for (std::size_t index = 0; index < curves_.size(); ++index)
      counts_[index] = curves_[index]->GetNumBerPatches();
  }
  ~PatchObserverScope() {
    if (active_)
      for (std::size_t index = 0; index < curves_.size(); ++index)
        curves_[index]->TruncatePatchObservers(counts_[index]);
  }
  PatchObserverScope(const PatchObserverScope&) = delete;
  PatchObserverScope& operator=(const PatchObserverScope&) = delete;
  void Commit() noexcept { active_ = false; }

private:
  std::array<CurveAdaptive*, 4> curves_;
  std::array<unsigned int, 4> counts_{};
  bool active_ = true;
};
} // namespace

static bool SortByNt(const PatchBezier* lhs, const PatchBezier* rhs) {
  return lhs->GetKaMedio() > rhs->GetKaMedio();
}

// Return geometry-owned patch observers in descending mean-curvature order.
std::list<PatchBezier*> ChargeEstimateProcess::ChargeEstimate(Geometry* geometry, Timer* timer) {
  std::list<PatchBezier*> list_patch_bezier_order;

  PatchReader patch_reader;
  timer->EndTimerParallel(0, 0, 10); // Full
  timer->InitTimerParallel(0, 0, 5); // File reading

  auto control_patches = patch_reader.LoaderBPFile(INPUT_MODEL);

  timer->EndTimerParallel(0, 0, 5); // File reading
  TIME_READ_FILE = timer->timer_parallel_[0][0][5];

  timer->InitTimerParallel(0, 0, 5); // Full

  timer->InitTimerParallel(0, 0, 1); // Process-zero charge estimation

  CurveAdaptive* patch_c1;
  CurveAdaptive* patch_c2;
  CurveAdaptive* patch_c3;
  CurveAdaptive* patch_c4;

  double area_minor = 1000;
  double area_major = 0;
  double kam_minor = 1000;
  double kam_major = 0;

  [[maybe_unused]] double elementos = 0;

  for (const auto& input_patch : control_patches) {
    VertexAdaptive control00(input_patch->GetPt00().GetX(), input_patch->GetPt00().GetY(),
                             input_patch->GetPt00().GetZ());
    auto* p00 = &control00;
    VertexAdaptive control10(input_patch->GetPt10().GetX(), input_patch->GetPt10().GetY(),
                             input_patch->GetPt10().GetZ());
    auto* p10 = &control10;
    VertexAdaptive control20(input_patch->GetPt20().GetX(), input_patch->GetPt20().GetY(),
                             input_patch->GetPt20().GetZ());
    auto* p20 = &control20;
    VertexAdaptive control30(input_patch->GetPt30().GetX(), input_patch->GetPt30().GetY(),
                             input_patch->GetPt30().GetZ());
    auto* p30 = &control30;

    VertexAdaptive control01(input_patch->GetPt01().GetX(), input_patch->GetPt01().GetY(),
                             input_patch->GetPt01().GetZ());
    auto* p01 = &control01;
    VertexAdaptive control11(input_patch->GetPt11().GetX(), input_patch->GetPt11().GetY(),
                             input_patch->GetPt11().GetZ());
    auto* p11 = &control11;
    VertexAdaptive control21(input_patch->GetPt21().GetX(), input_patch->GetPt21().GetY(),
                             input_patch->GetPt21().GetZ());
    auto* p21 = &control21;
    VertexAdaptive control31(input_patch->GetPt31().GetX(), input_patch->GetPt31().GetY(),
                             input_patch->GetPt31().GetZ());
    auto* p31 = &control31;

    VertexAdaptive control02(input_patch->GetPt02().GetX(), input_patch->GetPt02().GetY(),
                             input_patch->GetPt02().GetZ());
    auto* p02 = &control02;
    VertexAdaptive control12(input_patch->GetPt12().GetX(), input_patch->GetPt12().GetY(),
                             input_patch->GetPt12().GetZ());
    auto* p12 = &control12;
    VertexAdaptive control22(input_patch->GetPt22().GetX(), input_patch->GetPt22().GetY(),
                             input_patch->GetPt22().GetZ());
    auto* p22 = &control22;
    VertexAdaptive control32(input_patch->GetPt32().GetX(), input_patch->GetPt32().GetY(),
                             input_patch->GetPt32().GetZ());
    auto* p32 = &control32;

    VertexAdaptive control03(input_patch->GetPt03().GetX(), input_patch->GetPt03().GetY(),
                             input_patch->GetPt03().GetZ());
    auto* p03 = &control03;
    VertexAdaptive control13(input_patch->GetPt13().GetX(), input_patch->GetPt13().GetY(),
                             input_patch->GetPt13().GetZ());
    auto* p13 = &control13;
    VertexAdaptive control23(input_patch->GetPt23().GetX(), input_patch->GetPt23().GetY(),
                             input_patch->GetPt23().GetZ());
    auto* p23 = &control23;
    VertexAdaptive control33(input_patch->GetPt33().GetX(), input_patch->GetPt33().GetY(),
                             input_patch->GetPt33().GetZ());
    auto* p33 = &control33;

    if (geometry->VerifyCurveGeometry(p00, p10, p20, p30) == nullptr) {
      patch_c1 = new CurveAdaptiveParametricBezier(*p00, *p10, *p20, *p30);
      geometry->InsertCurve(patch_c1);
    } else {
      patch_c1 = geometry->VerifyCurveGeometry(p00, p10, p20, p30);
    }

    if (geometry->VerifyCurveGeometry(p30, p31, p32, p33) == nullptr) {
      patch_c2 = new CurveAdaptiveParametricBezier(*p30, *p31, *p32, *p33);
      geometry->InsertCurve(patch_c2);
    } else {
      patch_c2 = geometry->VerifyCurveGeometry(p30, p31, p32, p33);
    }

    if (geometry->VerifyCurveGeometry(p03, p13, p23, p33) == nullptr) {
      patch_c3 = new CurveAdaptiveParametricBezier(*p03, *p13, *p23, *p33);
      geometry->InsertCurve(patch_c3);
    } else {
      patch_c3 = geometry->VerifyCurveGeometry(p03, p13, p23, p33);
    }

    if (geometry->VerifyCurveGeometry(p00, p01, p02, p03) == nullptr) {
      patch_c4 = new CurveAdaptiveParametricBezier(*p00, *p01, *p02, *p03);
      geometry->InsertCurve(patch_c4);
    } else {
      patch_c4 = geometry->VerifyCurveGeometry(p00, p01, p02, p03);
    }

    PatchObserverScope observer_scope({patch_c1, patch_c2, patch_c3, patch_c4});
    auto pending_patch = std::make_unique<PatchBezier>(patch_c1, patch_c2, patch_c3, patch_c4, *p11,
                                                       *p21, *p12, *p22);
    auto* patch = pending_patch.get();

    patch->SetArea(CalculateAreaPatch(patch, 4));

    if (patch->GetArea() < area_minor) {
      area_minor = patch->GetArea();
    } else if (patch->GetArea() > area_major) {
      area_major = patch->GetArea();
    }

    patch->SetKaMedio(CalculateKaMedioPatch(patch, 25));

    if (patch->GetKaMedio() < kam_minor) {
      kam_minor = patch->GetKaMedio();
    } else if (patch->GetKaMedio() > kam_major) {
      kam_major = patch->GetKaMedio();
    }

    patch->SetAreaTriangle(CalculateAreaTriangleMedioRad(patch));
    TRIANGLE_MEDIO = patch->GetAreaTriangle();

    patch->SetNumberTriangle(patch->GetArea() / patch->GetAreaTriangle());

    elementos += patch->GetNumberTriangle();

    geometry->InsertPatch(std::move(pending_patch));
    observer_scope.Commit();

    list_patch_bezier_order.push_back(patch);

    curvatures_.push_back(patch->GetKaMedio());
  }

  if (WRITE_MESH == std::string("m")) {
    write_obj_file_.WriteCurvaturePatches(curvatures_, kam_major);
  }

  if (list_patch_bezier_order.size() > 1) {
    list_patch_bezier_order.sort(SortByNt);
  }

  timer->EndTimerParallel(0, 0, 1); // Process-zero charge estimation

  return list_patch_bezier_order;
}
