#ifndef APMESH_QUAD_CONTROLLED_PATCH_APPLICATION_H
#define APMESH_QUAD_CONTROLLED_PATCH_APPLICATION_H
namespace apmesh::application {
struct RuntimeConfig;
}
namespace apmesh::quad {
int RunControlledPatch(const application::RuntimeConfig& config);
int RunRealBoundaryPatch(const application::RuntimeConfig& config);
} // namespace apmesh::quad
#endif
