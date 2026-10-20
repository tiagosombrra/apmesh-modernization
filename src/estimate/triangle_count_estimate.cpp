#include "estimate/triangle_count_estimate.h"

#include <memory>

#include "data/mesh/sub_mesh.h"
#include "data/patch/patch_bezier.h"
#include "estimate/initial_mesh_estimate.h"
#include "estimate/estimate_mesh_scope.h"

namespace apmesh::estimation {
long CountEstimateTriangles(PatchBezier* patch, int degree) {
  std::unique_ptr<SubMesh> mesh;
  // Restore the patch and retire fresh samples before releasing the physical
  // mesh; its nodes are independent copies, not owners of curve sample objects.
  detail::EstimateMeshScope scope(*patch);
  mesh = BuildInitialEstimateSubMesh(patch, degree);
  return mesh->GetNumberElements();
}
} // namespace apmesh::estimation
