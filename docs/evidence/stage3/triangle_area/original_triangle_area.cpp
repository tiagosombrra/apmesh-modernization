#include "estimate/charge_estimate_process.h"
#include "estimate/initial_mesh_estimate.h"

double ChargeEstimateProcess::CalculateAreaTriangleMedio(PatchBezier* patch,
                                                         Timer* timer,
                                                         int degree) {
  MeshAdaptive* mesh = new MeshAdaptive;
  SubMesh* sub_mesh = InitialMeshEstimate(patch, degree);
  mesh->InsertSubMeshAdaptive(sub_mesh);
  // delete sub;

  while (CalculateErroEstimative(mesh, timer, degree) && degree < 5) {
    ++degree;
    //        cout<<"grau: "<<grau<<endl;
    //        cout<<"sub: "<<sub<<endl;
    SubMesh* sub1 = InitialMeshEstimate(patch, degree);
    mesh->RemoveSubMeshAdaptive();
    mesh->InsertSubMeshAdaptive(sub1);
    // delete sub1;
  }

  // cout<<"menor_grau: "<<menor_grau<<endl;

  SubMesh* sub2 = InitialMeshEstimate(patch, minor_degree_);
  mesh->RemoveSubMeshAdaptive();
  mesh->InsertSubMeshAdaptive(sub2);

  static_cast<PatchBezier*>(patch)->SetAreaTriangle(
      mesh->GetSubMeshAdaptiveByPosition(0)->GetElement(0)->GetArea());
  // delete malha;
  return patch->GetAreaTriangle();
}

SubMesh* ChargeEstimateProcess::InitialMeshEstimate(PatchCoons* patch, int degree) {
  return apmesh::estimation::BuildInitialEstimateSubMesh(patch, degree).release();
}
