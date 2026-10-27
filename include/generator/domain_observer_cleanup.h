#ifndef APMESH_GENERATOR_DOMAIN_OBSERVER_CLEANUP_H
#define APMESH_GENERATOR_DOMAIN_OBSERVER_CLEANUP_H

#include "data/geometry.h"
#include "data/mesh/mesh_adaptive.h"

#include <memory>
#include <utility>
#include <vector>

namespace apmesh::generation {

// Owners and Geometry remain live throughout this error-only operation.
// Compare observer identities without dereferencing a foreign SubMesh.
inline void DetachOwnedDomainObservers(
    Geometry& geometry, const MeshAdaptive* active,
    const std::vector<std::pair<int, std::unique_ptr<MeshAdaptive>>>& retained) noexcept {
  const auto is_owned = [active, &retained](const SubMesh* observer) noexcept {
    if (observer == nullptr)
      return false;
    const auto contains = [observer](const MeshAdaptive* mesh) noexcept {
      if (mesh == nullptr)
        return false;
      for (unsigned int i = 0; i < mesh->GetNumberSubMeshesAdaptive(); ++i)
        if (mesh->GetSubMeshAdaptiveByPosition(i) == observer)
          return true;
      return false;
    };
    if (contains(active))
      return true;
    for (const auto& entry : retained)
      if (contains(entry.second.get()))
        return true;
    return false;
  };
  for (unsigned int i = 0; i < geometry.GetNumberPatches(); ++i)
    if (auto* patch = geometry.GetPatch(i); patch != nullptr && is_owned(patch->GetSubMesh()))
      patch->SetSubMesh(nullptr);
}

} // namespace apmesh::generation

#endif // APMESH_GENERATOR_DOMAIN_OBSERVER_CLEANUP_H
