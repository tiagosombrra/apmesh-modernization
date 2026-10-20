#ifndef APMESH_ESTIMATE_ESTIMATE_MESH_SCOPE_H
#define APMESH_ESTIMATE_ESTIMATE_MESH_SCOPE_H

#include <array>

class CurveAdaptive;
class PatchBezier;
class SubMesh;

namespace apmesh::estimation::detail {
// Borrow fixed patch topology and initially populated sample lists. The actual
// estimate factory publishes fresh samples only into initially empty lists;
// this scope owns those samples and restores the preceding mesh observer.
// Keep the physical mesh owner alive until after this scope is destroyed.
class EstimateMeshScope {
public:
  explicit EstimateMeshScope(PatchBezier& patch) noexcept;
  ~EstimateMeshScope() noexcept;

  EstimateMeshScope(const EstimateMeshScope&) = delete;
  EstimateMeshScope& operator=(const EstimateMeshScope&) = delete;
  EstimateMeshScope(EstimateMeshScope&&) = delete;
  EstimateMeshScope& operator=(EstimateMeshScope&&) = delete;

private:
  PatchBezier& patch_;
  SubMesh* previous_mesh_;
  std::array<CurveAdaptive*, 4> curves_{};
  std::array<bool, 4> owns_samples_{};
};
} // namespace apmesh::estimation::detail

#endif // APMESH_ESTIMATE_ESTIMATE_MESH_SCOPE_H
