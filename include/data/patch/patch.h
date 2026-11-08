#ifndef DATA_PATCH_PATCH_H
#define DATA_PATCH_PATCH_H

class SubMesh;

class Patch {
public:
  Patch();
  explicit Patch(Patch* patch);
  virtual ~Patch(); // In .cpp

  Patch(const Patch&) = delete;
  Patch& operator=(const Patch&) = delete;

  Patch(Patch&&) noexcept;
  Patch& operator=(Patch&&) noexcept;

  unsigned int GetId() const noexcept;
  void SetId(unsigned int id) noexcept;

  SubMesh* GetSubMesh() const noexcept;
  // Register a null or live borrowed SubMesh without allocation. Registration
  // is independent of SubMesh::SetPatch; mesh retirement clears this observer.
  void SetSubMesh(SubMesh* sub_mesh) noexcept;

protected:
  unsigned int id_ = 0;
  SubMesh* sub_mesh_ = nullptr; // non-owning (MeshAdaptive owns it)

private:
  friend class SubMesh;
  // All live SubMesh back observers, including archived meshes. Object moves
  // preserve registrations by address rather than copying or transferring them.
  SubMesh* sub_mesh_observers_ = nullptr;

  // Forward observers are separate from the mesh-to-patch registrations above.
  Patch* previous_sub_mesh_observer_ = nullptr;
  Patch* next_sub_mesh_observer_ = nullptr;
  void DetachSubMeshObserver(Patch*& first) noexcept {
    if (previous_sub_mesh_observer_ != nullptr)
      previous_sub_mesh_observer_->next_sub_mesh_observer_ = next_sub_mesh_observer_;
    else
      first = next_sub_mesh_observer_;
    if (next_sub_mesh_observer_ != nullptr)
      next_sub_mesh_observer_->previous_sub_mesh_observer_ = previous_sub_mesh_observer_;
    sub_mesh_ = nullptr;
    previous_sub_mesh_observer_ = nullptr;
    next_sub_mesh_observer_ = nullptr;
  }
};

#endif // DATA_PATCH_PATCH_H
