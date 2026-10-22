#include "../../include/data/model.h"

#include <utility>

Model::Model() : geometry_(nullptr) {}

Model::Model(Geometry* geometry) : geometry_(geometry) {}

Model::~Model() {
  // Retire meshes in the original reverse insertion order.
  while (!meshes_.empty())
    meshes_.pop_back();
}

Model::Model(Model&& other) noexcept : geometry_(std::exchange(other.geometry_, nullptr)) {
  meshes_.swap(other.meshes_);
}

Model& Model::operator=(Model&& other) noexcept {
  if (this == &other)
    return *this;
  Model incoming(std::move(other));
  std::swap(geometry_, incoming.geometry_);
  meshes_.swap(incoming.meshes_);
  return *this;
}

void Model::SetGeometry(Geometry* geometry) { this->geometry_ = geometry; }

Geometry* Model::GetGeometry() { return this->geometry_; }

void Model::InsertMeshAdaptive(MeshAdaptive* mesh_adaptive) {
  InsertMeshAdaptive(std::unique_ptr<MeshAdaptive>(mesh_adaptive));
}

void Model::InsertMeshAdaptive(std::unique_ptr<MeshAdaptive> mesh_adaptive) {
  meshes_.push_back(std::move(mesh_adaptive));
}

unsigned int Model::GetNumberMeshes() const { return static_cast<unsigned int>(meshes_.size()); }

MeshAdaptive* Model::GetMeshAdaptive(const unsigned int position) {
  return (position < this->meshes_.size()) ? this->meshes_[position].get() : nullptr;
}
