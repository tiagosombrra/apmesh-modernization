#ifndef DATA_MODEL_H
#define DATA_MODEL_H

#include <memory>
#include <vector>

#include "../data/mesh/mesh_adaptive.h"
#include "geometry.h"

class Model {
public:
  Model();
  explicit Model(Geometry* geometry);
  ~Model();

  Model(const Model&) = delete;
  Model& operator=(const Model&) = delete;
  // Transfer owners and the geometry borrow; the source becomes empty/null.
  // Assignment retires prior meshes in reverse order; self-move is unchanged.
  Model(Model&& other) noexcept;
  Model& operator=(Model&& other) noexcept;

  // Geometry is borrowed and must outlive every mesh that refers to it.
  void SetGeometry(Geometry* geometry);
  Geometry* GetGeometry();
  // Consume exclusive ownership on entry, including allocation failure.
  // Preserve existing entries on failure; null appends an empty slot.
  // Duplicate or foreign-owned arguments are invalid.
  void InsertMeshAdaptive(std::unique_ptr<MeshAdaptive> mesh_adaptive);
  void InsertMeshAdaptive(MeshAdaptive* mesh_adaptive);
  unsigned int GetNumberMeshes() const;
  MeshAdaptive* GetMeshAdaptive(const unsigned int position);

protected:
  Geometry* geometry_;
  std::vector<std::unique_ptr<MeshAdaptive>> meshes_;
};

#endif // DATA_MODEL_H
