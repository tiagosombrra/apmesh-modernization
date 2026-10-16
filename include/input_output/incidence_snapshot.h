#ifndef AP_MESH_INCIDENCE_SNAPSHOT_H
#define AP_MESH_INCIDENCE_SNAPSHOT_H

#include <string>

class MeshAdaptive;

namespace apmesh {
namespace io {

// Observe each patch before rollback or later adaptation mutates its geometry.
// The snapshot preserves local UV corners and full-precision physical nodes.
void WriteIncidenceSnapshot(const MeshAdaptive& mesh, const std::string& path, int step);

} // namespace io
} // namespace apmesh

#endif
