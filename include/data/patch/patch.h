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
  // Borrowed forward link only; registration belongs to SubMesh::SetPatch.
  // Foreign/copied forward links remain the caller's lifetime responsibility.
  void SetSubMesh(SubMesh* sub_mesh) noexcept;

protected:
  unsigned int id_ = 0;
  SubMesh* sub_mesh_ = nullptr; // non-owning (MeshAdaptive owns it)

private:
  friend class SubMesh;
  // All live SubMesh back observers, including archived meshes. Object moves
  // preserve registrations by address rather than copying or transferring them.
  SubMesh* sub_mesh_observers_ = nullptr;
};

#endif // DATA_PATCH_PATCH_H
