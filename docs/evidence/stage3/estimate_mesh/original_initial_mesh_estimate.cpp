#include "estimate/initial_mesh_estimate.h"

#include "data/curve/curve_adaptive.h"
#include "data/mesh/mesh_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/patch/patch_coons.h"
#include "data/triangle_adaptive.h"

namespace apmesh::estimation {
std::unique_ptr<SubMesh> BuildInitialEstimateSubMesh(PatchCoons* patch, int degree) {
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

  for (double v = 0.0; v <= 1.0; v += 1.0 / degree) {
    for (double u = 0.0; u <= 1.0; u += 1.0 / degree) {
      PointAdaptive* p = new NodeAdaptive(patch->Parameterize(u, v));
      p->SetId(idv++);

      // cout << "u = " << u << " v = " << v << endl;
      if (v == 0 and c1)  // p está na curva 1
        c1->InsertPoint(p);
      else if (v == 1 and c3)  // p está na curva 3
        c3->InsertPoint(p);

      if (u == 0 and c4)  // p está na curva 4
        c4->InsertPoint(p);
      else if (u == 1 and c2)  // p está na curva 2
        c2->InsertPoint(p);

      sub->SetNoh(static_cast<NodeAdaptive*>(p));
      total_1++;
    }
  }

  for (double v = 1.0 / (2.0 * degree); v <= 1.0 - (1.0 / (2.0 * degree));
       v += 1.0 / degree) {
    for (double u = 1.0 / (2.0 * degree); u <= 1.0 - (1.0 / (2.0 * degree));
         u += 1.0 / degree) {
      //   cout << "u = " << u << " v = " << v << endl;
      PointAdaptive* p = new NodeAdaptive(patch->Parameterize(u, v));
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

    ElementAdaptive* e1 = new TriangleAdaptive(
        sub->GetNoh(i), sub->GetNoh(i + 1), sub->GetNoh(i + total_1));
    ((TriangleAdaptive*)e1)->SetParametersN1(patch->FindUV(*(sub->GetNoh(i))));
    ((TriangleAdaptive*)e1)
        ->SetParametersN2(patch->FindUV(*(sub->GetNoh(i + 1))));
    ((TriangleAdaptive*)e1)
        ->SetParametersN3(patch->FindUV(*(sub->GetNoh(i + total_1))));
    e1->SetId(ide++);
    sub->SetElement(e1);

    ElementAdaptive* e2 =
        new TriangleAdaptive(sub->GetNoh(i + 1), sub->GetNoh(i + length + 1),
                             sub->GetNoh(i + total_1));
    ((TriangleAdaptive*)e2)
        ->SetParametersN1(patch->FindUV(*(sub->GetNoh(i + 1))));
    ((TriangleAdaptive*)e2)
        ->SetParametersN2(patch->FindUV(*(sub->GetNoh(i + length + 1))));
    ((TriangleAdaptive*)e2)
        ->SetParametersN3(patch->FindUV(*(sub->GetNoh(i + total_1))));
    e2->SetId(ide++);
    sub->SetElement(e2);

    ElementAdaptive* e3 =
        new TriangleAdaptive(sub->GetNoh(i + length + 1),
                             sub->GetNoh(i + length), sub->GetNoh(i + total_1));
    ((TriangleAdaptive*)e3)
        ->SetParametersN1(patch->FindUV(*(sub->GetNoh(i + length + 1))));
    ((TriangleAdaptive*)e3)
        ->SetParametersN2(patch->FindUV(*(sub->GetNoh(i + length))));
    ((TriangleAdaptive*)e3)
        ->SetParametersN3(patch->FindUV(*(sub->GetNoh(i + total_1))));
    e3->SetId(ide++);
    sub->SetElement(e3);

    ElementAdaptive* e4 = new TriangleAdaptive(
        sub->GetNoh(i + length), sub->GetNoh(i), sub->GetNoh(i + total_1));
    ((TriangleAdaptive*)e4)
        ->SetParametersN1(patch->FindUV(*(sub->GetNoh(i + length))));
    ((TriangleAdaptive*)e4)->SetParametersN2(patch->FindUV(*(sub->GetNoh(i))));
    ((TriangleAdaptive*)e4)
        ->SetParametersN3(patch->FindUV(*(sub->GetNoh(i + total_1))));
    e4->SetId(ide++);
    sub->SetElement(e4);
    // cout<<"i "<<i<<endl;
  }

  // 5. define a submalha do patch
  patch->SetSubMesh(sub);
  sub->SetPatch(patch);

  MeshAdaptive* mesh = new MeshAdaptive;
  mesh->InsertSubMeshAdaptive(sub);

  return std::unique_ptr<SubMesh>(sub);
}
} // namespace apmesh::estimation
