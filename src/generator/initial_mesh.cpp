#include "generator/initial_mesh.h"

#include <array>
#include <initializer_list>
#include <tuple>
#include <utility>

#include "crab_mesh/performer/id_manager.h"
#include "data/curve/curve_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/patch/patch_coons.h"
#include "data/triangle_adaptive.h"

namespace apmesh::generation {
std::unique_ptr<SubMesh> BuildInitialSubMesh(PatchCoons* patch, Performer::IdManager* id_manager) {
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

  auto sub_mesh = std::make_unique<SubMesh>();
  for (const double v : {0.0, 1.0}) {
    for (const double u : {0.0, 1.0}) {
      auto pending = std::make_unique<NodeAdaptive>(patch->Parameterize(u, v));
      auto* point = pending.get();
      point->SetId(id_manager->next(0));
      if (v == 0 && c1) {
        c1->InsertPoint(point);
        pending.release();
      } else if (v == 1 && c3) {
        c3->InsertPoint(point);
        pending.release();
      }
      if (u == 0 && c4) {
        c4->InsertPoint(point);
        pending.release();
      } else if (u == 1 && c2) {
        c2->InsertPoint(point);
        pending.release();
      }
      // First successful publication transfers the sample to the collective
      // curve owner. Otherwise it stays local and is deleted after the copy.
      sub_mesh->SetNoh(point);
    }
  }

  const std::array<CurveAdaptive*, 4> initialized_curves = {c1, c2, c3, c4};
  for (unsigned int slot = 0; slot < initialized_curves.size(); ++slot) {
    if (initialized_curves[slot] != nullptr && patch->IsCurveReversed(slot)) {
      initialized_curves[slot]->GetPoints().reverse();
    }
  }

  {
    auto center = std::make_unique<NodeAdaptive>(patch->Parameterize(0.5, 0.5));
    center->SetId(id_manager->next(0));
    sub_mesh->SetNoh(center.get());
  }

  auto e1 = std::make_unique<TriangleAdaptive>(sub_mesh->GetNoh(0), sub_mesh->GetNoh(1),
                                               sub_mesh->GetNoh(4));
  e1->SetParametersN1(std::make_tuple(0, 0));
  e1->SetParametersN2(std::make_tuple(1, 0));
  e1->SetParametersN3(std::make_tuple(0.5, 0.5));
  e1->SetId(id_manager->next(1));
  sub_mesh->AddElement(std::move(e1));

  auto e2 = std::make_unique<TriangleAdaptive>(sub_mesh->GetNoh(1), sub_mesh->GetNoh(3),
                                               sub_mesh->GetNoh(4));
  e2->SetParametersN1(std::make_tuple(1, 0));
  e2->SetParametersN2(std::make_tuple(1, 1));
  e2->SetParametersN3(std::make_tuple(0.5, 0.5));
  e2->SetId(id_manager->next(1));
  sub_mesh->AddElement(std::move(e2));

  auto e3 = std::make_unique<TriangleAdaptive>(sub_mesh->GetNoh(3), sub_mesh->GetNoh(2),
                                               sub_mesh->GetNoh(4));
  e3->SetParametersN1(std::make_tuple(1, 1));
  e3->SetParametersN2(std::make_tuple(0, 1));
  e3->SetParametersN3(std::make_tuple(0.5, 0.5));
  e3->SetId(id_manager->next(1));
  sub_mesh->AddElement(std::move(e3));

  auto e4 = std::make_unique<TriangleAdaptive>(sub_mesh->GetNoh(2), sub_mesh->GetNoh(0),
                                               sub_mesh->GetNoh(4));
  e4->SetParametersN1(std::make_tuple(0, 1));
  e4->SetParametersN2(std::make_tuple(0, 0));
  e4->SetParametersN3(std::make_tuple(0.5, 0.5));
  e4->SetId(id_manager->next(1));
  sub_mesh->AddElement(std::move(e4));

  patch->SetSubMesh(sub_mesh.get());
  sub_mesh->SetPatch(patch);
  return sub_mesh;
}
} // namespace apmesh::generation
