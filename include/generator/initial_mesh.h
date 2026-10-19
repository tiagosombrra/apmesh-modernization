#ifndef APMESH_GENERATOR_INITIAL_MESH_H
#define APMESH_GENERATOR_INITIAL_MESH_H

#include <memory>

class PatchCoons;
class SubMesh;
namespace Performer {
class IdManager;
}

namespace apmesh::generation {
// Build the existing five-node/four-triangle serial coarse mesh. The caller
// owns the returned mesh. Samples transfer to collective curve ownership after
// their first successful insertion; CurveSampleLifetime must surround the call.
// Failure destroys unpublished resources and preserves the prior patch/mesh
// observer. Published curve prefixes and consumed IDs are not rolled back.
std::unique_ptr<SubMesh> BuildInitialSubMesh(PatchCoons* patch, Performer::IdManager* id_manager);
} // namespace apmesh::generation

#endif // APMESH_GENERATOR_INITIAL_MESH_H
