#ifndef APMESH_RESEARCH_MESH_STUDIO_NATIVE_LINEAGE_CAPTURE_H
#define APMESH_RESEARCH_MESH_STUDIO_NATIVE_LINEAGE_CAPTURE_H

#include <cstdint>
#include <string>

class Geometry;
class MeshAdaptive;

namespace apmesh::mesh_studio {

// Only the opt-in serial research engine calls this after AcceptedMeshScope::Commit.
// Failures in optional observation must not affect TRI acceptance or scientific output.
void WriteAcceptedEpochIfEnabled(
    const Geometry& source, MeshAdaptive& accepted_mesh, int adaptive_step,
    int retry_index, std::uint64_t session, std::uint64_t outer_epoch,
    int global_retry, const std::string& output_prefix) noexcept;

} // namespace apmesh::mesh_studio

#endif // APMESH_RESEARCH_MESH_STUDIO_NATIVE_LINEAGE_CAPTURE_H
