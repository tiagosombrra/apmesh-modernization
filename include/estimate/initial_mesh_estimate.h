#ifndef APMESH_ESTIMATE_INITIAL_MESH_ESTIMATE_H
#define APMESH_ESTIMATE_INITIAL_MESH_ESTIMATE_H

#include <memory>

class PatchCoons;
class SubMesh;

namespace apmesh::estimation {
// The result exclusively owns the physical mesh. Curve samples remain under
// the caller's collective curve-sample lifetime, independently of copied nodes.
// Only success publishes the patch observer. The caller must retire/rebind it
// before destroying the result. Failure is terminal: published sample prefixes
// and consumed IDs are not rolled back; inner resources are reclaimed.
// Nonpositive degrees throw invalid_argument before touching the patch.
std::unique_ptr<SubMesh> BuildInitialEstimateSubMesh(PatchCoons* patch, int degree);
} // namespace apmesh::estimation

#endif // APMESH_ESTIMATE_INITIAL_MESH_ESTIMATE_H
