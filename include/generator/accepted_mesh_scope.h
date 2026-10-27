#ifndef APMESH_GENERATOR_ACCEPTED_MESH_SCOPE_H
#define APMESH_GENERATOR_ACCEPTED_MESH_SCOPE_H

#include "generator/domain_observer_cleanup.h"

#include <exception>
#include <memory>

namespace apmesh::generation {

// Keep an unarchived accepted mesh alive while the active owner builds trials.
// Archived accepted meshes remain owned by the existing report history.
class AcceptedMeshScope {
public:
  AcceptedMeshScope(Geometry& geometry, std::unique_ptr<MeshAdaptive>& active,
                    const MeshAdaptive* accepted) noexcept
      : geometry_(geometry), active_(active), exceptions_(std::uncaught_exceptions()) {
    if (active.get() == accepted)
      accepted_ = std::move(active);
  }

  AcceptedMeshScope(const AcceptedMeshScope&) = delete;
  AcceptedMeshScope& operator=(const AcceptedMeshScope&) = delete;

  ~AcceptedMeshScope() noexcept {
    if (!accepted_)
      return;
    if (std::uncaught_exceptions() > exceptions_) {
      const std::vector<std::pair<int, std::unique_ptr<MeshAdaptive>>> no_archive;
      DetachOwnedDomainObservers(geometry_, active_.get(), no_archive);
      DetachOwnedDomainObservers(geometry_, accepted_.get(), no_archive);
    }
    active_ = std::move(accepted_);
  }

  // Called only after the existing acceptance decision selects the active mesh.
  MeshAdaptive* Commit() noexcept {
    accepted_.reset();
    return active_.get();
  }

private:
  Geometry& geometry_;
  std::unique_ptr<MeshAdaptive>& active_;
  int exceptions_;
  std::unique_ptr<MeshAdaptive> accepted_;
};

} // namespace apmesh::generation

#endif // APMESH_GENERATOR_ACCEPTED_MESH_SCOPE_H
