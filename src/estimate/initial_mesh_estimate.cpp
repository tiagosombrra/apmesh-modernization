#include "estimate/initial_mesh_estimate.h"

#include <cstdint>
#include <limits>
#include <stdexcept>
#include <utility>

#include "data/curve/curve_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/patch/patch_coons.h"
#include "data/triangle_adaptive.h"

namespace apmesh::estimation {
std::unique_ptr<SubMesh> BuildInitialEstimateSubMesh(PatchCoons* patch, int degree) {
  static_assert(std::numeric_limits<int>::digits <= 31 &&
                std::numeric_limits<double>::digits >= 53);
  if (degree <= 0)
    throw std::invalid_argument("Estimator degree must be positive");
  // For positive 32-bit degrees each increment below 1 advances by more
  // than half of 1/degree. This integer ceiling cannot truncate the legacy
  // floating sequence; retain its endpoint test and repeated additions.
  const auto iteration_limit = 2 * (static_cast<std::uint64_t>(degree) + 1);
  int idv = 1;
  int ide = 1;
  int jump = degree;
  int length = degree + 1;
  int total_1 = 0;
  int total_2 = 0;

  CurveAdaptive* c1 = patch->GetCurve(0);
  CurveAdaptive* c2 = patch->GetCurve(1);
  CurveAdaptive* c3 = patch->GetCurve(2);
  CurveAdaptive* c4 = patch->GetCurve(3);

  if (c1->GetNumBerPoints())
    c1 = nullptr;
  if (c2->GetNumBerPoints())
    c2 = nullptr;
  if (c3->GetNumBerPoints())
    c3 = nullptr;
  if (c4->GetNumBerPoints())
    c4 = nullptr;

  auto sub = std::make_unique<SubMesh>();

  double v = 0.0;
  for (std::uint64_t row = 0; row < iteration_limit && v <= 1.0; ++row, v += 1.0 / degree) {
    double u = 0.0;
    for (std::uint64_t column = 0; column < iteration_limit && u <= 1.0;
         ++column, u += 1.0 / degree) {
      auto pending = std::make_unique<NodeAdaptive>(patch->Parameterize(u, v));
      auto* p = pending.get();
      p->SetId(idv++);

      if (v == 0 and c1) {
        c1->InsertPoint(p);
        pending.release();
      } else if (v == 1 and c3) {
        c3->InsertPoint(p);
        pending.release();
      }

      if (u == 0 and c4) {
        c4->InsertPoint(p);
        pending.release();
      } else if (u == 1 and c2) {
        c2->InsertPoint(p);
        pending.release();
      }
      // First publication transfers this sample to the collective curve owner.
      // Physical mesh nodes are copies; unpublished samples stay local.

      sub->SetNoh(static_cast<NodeAdaptive*>(p));
      total_1++;
    }
  }

  v = 1.0 / (2.0 * degree);
  for (std::uint64_t row = 0; row < iteration_limit && v <= 1.0 - (1.0 / (2.0 * degree));
       ++row, v += 1.0 / degree) {
    double u = 1.0 / (2.0 * degree);
    for (std::uint64_t column = 0; column < iteration_limit && u <= 1.0 - (1.0 / (2.0 * degree));
         ++column, u += 1.0 / degree) {

      auto pending = std::make_unique<NodeAdaptive>(patch->Parameterize(u, v));
      auto* p = pending.get();
      sub->SetNoh(static_cast<NodeAdaptive*>(p));
      p->SetId(idv++);
    }
  }

  total_2 = total_1;

  for (int i = 0; i < (total_2 - length - 1); ++i) {
    if (i == jump) {
      jump = jump + length;
      ++i;
      total_1 = total_1 - 1;
    }

    auto e1 = std::make_unique<TriangleAdaptive>(sub->GetNoh(i), sub->GetNoh(i + 1),
                                                 sub->GetNoh(i + total_1));
    e1->SetParametersN1(patch->FindUV(*(sub->GetNoh(i))));
    e1->SetParametersN2(patch->FindUV(*(sub->GetNoh(i + 1))));
    e1->SetParametersN3(patch->FindUV(*(sub->GetNoh(i + total_1))));
    e1->SetId(ide++);
    sub->AddElement(std::move(e1));

    auto e2 = std::make_unique<TriangleAdaptive>(sub->GetNoh(i + 1), sub->GetNoh(i + length + 1),
                                                 sub->GetNoh(i + total_1));
    e2->SetParametersN1(patch->FindUV(*(sub->GetNoh(i + 1))));
    e2->SetParametersN2(patch->FindUV(*(sub->GetNoh(i + length + 1))));
    e2->SetParametersN3(patch->FindUV(*(sub->GetNoh(i + total_1))));
    e2->SetId(ide++);
    sub->AddElement(std::move(e2));

    auto e3 = std::make_unique<TriangleAdaptive>(sub->GetNoh(i + length + 1),
                                                 sub->GetNoh(i + length), sub->GetNoh(i + total_1));
    e3->SetParametersN1(patch->FindUV(*(sub->GetNoh(i + length + 1))));
    e3->SetParametersN2(patch->FindUV(*(sub->GetNoh(i + length))));
    e3->SetParametersN3(patch->FindUV(*(sub->GetNoh(i + total_1))));
    e3->SetId(ide++);
    sub->AddElement(std::move(e3));

    auto e4 = std::make_unique<TriangleAdaptive>(sub->GetNoh(i + length), sub->GetNoh(i),
                                                 sub->GetNoh(i + total_1));
    e4->SetParametersN1(patch->FindUV(*(sub->GetNoh(i + length))));
    e4->SetParametersN2(patch->FindUV(*(sub->GetNoh(i))));
    e4->SetParametersN3(patch->FindUV(*(sub->GetNoh(i + total_1))));
    e4->SetId(ide++);
    sub->AddElement(std::move(e4));
  }

  patch->SetSubMesh(sub.get());
  sub->SetPatch(patch);

  return sub;
}
} // namespace apmesh::estimation
