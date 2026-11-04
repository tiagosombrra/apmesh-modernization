#include "data/patch/patch.h"

#include "data/mesh/sub_mesh.h"

Patch::Patch() = default;

Patch::Patch(Patch* patch) : id_(patch ? patch->GetId() : 0) {}

Patch::~Patch() {
  while (sub_mesh_observers_ != nullptr) {
    SubMesh* observer = sub_mesh_observers_;
    sub_mesh_observers_ = observer->next_patch_observer_;
    observer->patch_ = nullptr;
    observer->previous_patch_observer_ = nullptr;
    observer->next_patch_observer_ = nullptr;
  }
}

Patch::Patch(Patch&& other) noexcept : id_(other.id_), sub_mesh_(other.sub_mesh_) {}
Patch& Patch::operator=(Patch&& other) noexcept {
  if (this != &other) {
    id_ = other.id_;
    sub_mesh_ = other.sub_mesh_;
  }
  return *this;
}

unsigned int Patch::GetId() const noexcept { return id_; }

void Patch::SetId(unsigned int id) noexcept { id_ = id; }

SubMesh* Patch::GetSubMesh() const noexcept { return sub_mesh_; }

void Patch::SetSubMesh(SubMesh* sub_mesh) noexcept { sub_mesh_ = sub_mesh; }
