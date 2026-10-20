#include "estimate/charge_estimate_process.h"

#include "estimate/estimate_mesh_scope.h"
#include "estimate/initial_mesh_estimate.h"

double ChargeEstimateProcess::CalculateAreaTriangleMedio(PatchBezier* patch, Timer* timer,
                                                         int degree) {
  MeshAdaptive mesh;
  apmesh::estimation::detail::EstimateMeshScope scope(*patch);
  auto initial = apmesh::estimation::BuildInitialEstimateSubMesh(patch, degree);
  mesh.InsertSubMeshAdaptive(initial.release());

  while (CalculateErroEstimative(&mesh, timer, degree) && degree < 5) {
    ++degree;
    auto next = apmesh::estimation::BuildInitialEstimateSubMesh(patch, degree);
    mesh.RemoveSubMeshAdaptive();
    mesh.InsertSubMeshAdaptive(next.release());
  }

  auto selected = apmesh::estimation::BuildInitialEstimateSubMesh(patch, minor_degree_);
  mesh.RemoveSubMeshAdaptive();
  mesh.InsertSubMeshAdaptive(selected.release());

  patch->SetAreaTriangle(mesh.GetSubMeshAdaptiveByPosition(0)->GetElement(0)->GetArea());
  return patch->GetAreaTriangle();
}
