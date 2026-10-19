#include "estimate/triangle_count_estimate.h"
#include "estimate/initial_mesh_estimate.h"
#include "data/mesh/sub_mesh.h"
#include "data/patch/patch_bezier.h"

class OriginalTriangleCounter {
public:
  SubMesh* InitialMeshEstimate(PatchCoons* patch, int degree) {
    return apmesh::estimation::BuildInitialEstimateSubMesh(patch, degree).release();
  }
  long CalculateNumbersTriangle(PatchBezier* patch, int degree);
};
long OriginalTriangleCounter::CalculateNumbersTriangle(PatchBezier* patch,
                                                     int degree) {
  SubMesh* sub = InitialMeshEstimate(patch, degree);

  return sub->GetNumberElements();
}


namespace apmesh::estimation {
long CountEstimateTriangles(PatchBezier* patch, int degree) {
  OriginalTriangleCounter counter;
  return counter.CalculateNumbersTriangle(patch, degree);
}
} // namespace apmesh::estimation
