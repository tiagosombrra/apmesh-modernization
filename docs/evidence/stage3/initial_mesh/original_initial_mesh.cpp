#include "generator/initial_mesh.h"
#include "data/patch/patch_coons.h"
#include "data/curve/curve_adaptive.h"
#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "crab_mesh/performer/id_manager.h"
#include <array>
#include <tuple>
using std::make_tuple;
namespace {
class GeneratorAdaptive {public: static SubMesh* InitialMesh(PatchCoons*,Performer::IdManager*);};
SubMesh* GeneratorAdaptive::InitialMesh(PatchCoons* patch,
                                        Performer::IdManager* idManager) {
  CurveAdaptive* c1 = patch->GetCurve(0);
  CurveAdaptive* c2 = patch->GetCurve(1);
  CurveAdaptive* c3 = patch->GetCurve(2);
  CurveAdaptive* c4 = patch->GetCurve(3);

  // 1. verifica quais curvas ainda não foram discretizadas
  if (c1->GetNumBerPoints())
    c1 = nullptr;  // c1 já foi trabalhada no patch vizinho
  if (c2->GetNumBerPoints())
    c2 = nullptr;  // c2 já foi trabalhada no patch vizinho
  if (c3->GetNumBerPoints())
    c3 = nullptr;  // c3 já foi trabalhada no patch vizinho
  if (c4->GetNumBerPoints())
    c4 = nullptr;  // c4 já foi trabalhada no patch vizinho

  SubMesh* sub = new SubMesh;

  //========================= Malha Grosseira
  //====================================
  // 2. divide cada patch em 9 regiões e gera os nós dos extremos de cada região
  for (double v = 0.0; v <= 1.0; v += 1) {
    for (double u = 0.0; u <= 1.0; u += 1) {
      //			cout << "u = " << u << " v = " << v << endl;
      PointAdaptive* p = new NodeAdaptive(patch->Parameterize(u, v));
      p->SetId(idManager->next(0));
      bool inserted = false;

      //			cout << "ponto " << p->id << " " <<  p->x << " "
      //<< p->y << " " << p->z << endl; 			cout << "===="
      //<< endl;

      if (v == 0 && c1)  // p está na curva 1 (c1 = nullptr)
        c1->InsertPoint(p), inserted = true;
      else if (v == 1 && c3)  // p está na curva 3
        c3->InsertPoint(p), inserted = true;

      if (u == 0 && c4)  // p está na curva 4
        c4->InsertPoint(p), inserted = true;
      else if (u == 1 && c2)  // p está na curva 2
        c2->InsertPoint(p), inserted = true;

      sub->SetNoh(static_cast<NodeAdaptive*>(p));
      if (!inserted) delete p;
    }
  }

  const std::array<CurveAdaptive*, 4> initialized_curves = {c1, c2, c3, c4};
  for (unsigned int slot = 0; slot < initialized_curves.size(); ++slot) {
    if (initialized_curves[slot] != nullptr && patch->IsCurveReversed(slot)) {
      initialized_curves[slot]->GetPoints().reverse();
    }
  }

  // Coarse initial mesh: 4 triangles per patch with a central node.
  PointAdaptive* center = new NodeAdaptive(patch->Parameterize(0.5, 0.5));
  center->SetId(idManager->next(0));
  sub->SetNoh(static_cast<NodeAdaptive*>(center));

  ElementAdaptive* e1 =
      new TriangleAdaptive(sub->GetNoh(0), sub->GetNoh(1), sub->GetNoh(4));
  ((TriangleAdaptive*)e1)->SetParametersN1(make_tuple(0, 0));
  ((TriangleAdaptive*)e1)->SetParametersN2(make_tuple(1, 0));
  ((TriangleAdaptive*)e1)->SetParametersN3(make_tuple(0.5, 0.5));
  e1->SetId(idManager->next(1));
  sub->SetElement(e1);

  ElementAdaptive* e2 =
      new TriangleAdaptive(sub->GetNoh(1), sub->GetNoh(3), sub->GetNoh(4));
  ((TriangleAdaptive*)e2)->SetParametersN1(make_tuple(1, 0));
  ((TriangleAdaptive*)e2)->SetParametersN2(make_tuple(1, 1));
  ((TriangleAdaptive*)e2)->SetParametersN3(make_tuple(0.5, 0.5));
  e2->SetId(idManager->next(1));
  sub->SetElement(e2);

  ElementAdaptive* e3 =
      new TriangleAdaptive(sub->GetNoh(3), sub->GetNoh(2), sub->GetNoh(4));
  ((TriangleAdaptive*)e3)->SetParametersN1(make_tuple(1, 1));
  ((TriangleAdaptive*)e3)->SetParametersN2(make_tuple(0, 1));
  ((TriangleAdaptive*)e3)->SetParametersN3(make_tuple(0.5, 0.5));
  e3->SetId(idManager->next(1));
  sub->SetElement(e3);

  ElementAdaptive* e4 =
      new TriangleAdaptive(sub->GetNoh(2), sub->GetNoh(0), sub->GetNoh(4));
  ((TriangleAdaptive*)e4)->SetParametersN1(make_tuple(0, 1));
  ((TriangleAdaptive*)e4)->SetParametersN2(make_tuple(0, 0));
  ((TriangleAdaptive*)e4)->SetParametersN3(make_tuple(0.5, 0.5));
  e4->SetId(idManager->next(1));
  sub->SetElement(e4);
  //==============================================================================*/

  // 5. define a submalha do patch
  patch->SetSubMesh(sub);
  sub->SetPatch(patch);

  return sub;
}

}
namespace apmesh::generation {
std::unique_ptr<SubMesh> BuildInitialSubMesh(PatchCoons* patch, Performer::IdManager* manager) {return std::unique_ptr<SubMesh>(GeneratorAdaptive::InitialMesh(patch,manager));}
}
