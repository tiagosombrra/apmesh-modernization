#ifndef APMESH_ESTIMATE_TRIANGLE_COUNT_ESTIMATE_H
#define APMESH_ESTIMATE_TRIANGLE_COUNT_ESTIMATE_H

class PatchBezier;

namespace apmesh::estimation {
// Count a temporary physical mesh without retaining it or its new curve samples.
// The patch and its four live curves outlive this serial call. Existing samples
// are borrowed; only samples published into initially empty curves are owned.
// Restore the prior SubMesh observer on success and failure. Evaluator scratch
// is not rolled back; no concurrent observation or arbitrary curve mutation.
long CountEstimateTriangles(PatchBezier* patch, int degree);
} // namespace apmesh::estimation

#endif // APMESH_ESTIMATE_TRIANGLE_COUNT_ESTIMATE_H
