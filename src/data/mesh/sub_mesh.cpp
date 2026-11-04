#include "data/mesh/sub_mesh.h"

#include "data/node_adaptive.h"
#include "data/element_adaptive.h"
#include "data/patch/patch.h"
#include <memory>

SubMesh::SubMesh() = default;
SubMesh::~SubMesh() { DetachPatchObserver(true); }

SubMesh::SubMesh(SubMesh&& other) noexcept
    : nos_(std::move(other.nos_)), elements_(std::move(other.elements_)) {
  AttachPatchObserver(other.patch_);
}
SubMesh& SubMesh::operator=(SubMesh&& other) noexcept {
  if (this != &other) {
    // Elements borrow nodes, so retire them before replacing their node owners.
    elements_.clear();
    nos_ = std::move(other.nos_);
    elements_ = std::move(other.elements_);
    // Preserve existing foreign forward links and the moved-from back observer.
    DetachPatchObserver(false);
    AttachPatchObserver(other.patch_);
  }
  return *this;
}

Patch* SubMesh::GetPatch() const noexcept { return patch_; }

void SubMesh::SetPatch(Patch* patch) noexcept {
  if (patch_ != patch) {
    DetachPatchObserver(true);
    AttachPatchObserver(patch);
  }
}

void SubMesh::DetachPatchObserver(bool retire_forward) noexcept {
  if (patch_ != nullptr) {
    if (previous_patch_observer_ != nullptr)
      previous_patch_observer_->next_patch_observer_ = next_patch_observer_;
    else
      patch_->sub_mesh_observers_ = next_patch_observer_;
    if (next_patch_observer_ != nullptr)
      next_patch_observer_->previous_patch_observer_ = previous_patch_observer_;
    if (retire_forward && patch_->sub_mesh_ == this)
      patch_->sub_mesh_ = nullptr;
  }
  patch_ = nullptr;
  previous_patch_observer_ = nullptr;
  next_patch_observer_ = nullptr;
}

void SubMesh::AttachPatchObserver(Patch* patch) noexcept {
  patch_ = patch;
  if (patch_ != nullptr) {
    next_patch_observer_ = patch_->sub_mesh_observers_;
    if (next_patch_observer_ != nullptr)
      next_patch_observer_->previous_patch_observer_ = this;
    patch_->sub_mesh_observers_ = this;
  }
}

NodeAdaptive* SubMesh::GetNoh(unsigned int position) noexcept {
  return (position < nos_.size()) ? nos_[position].get() : nullptr;
}

const NodeAdaptive* SubMesh::GetNoh(unsigned int position) const noexcept {
  return (position < nos_.size()) ? nos_[position].get() : nullptr;
}

ElementAdaptive* SubMesh::GetElement(unsigned int position) noexcept {
  return (position < elements_.size()) ? elements_[position].get() : nullptr;
}

const ElementAdaptive* SubMesh::GetElement(unsigned int position) const noexcept {
  return (position < elements_.size()) ? elements_[position].get() : nullptr;
}

void SubMesh::AddNoh(std::unique_ptr<NodeAdaptive> noh) { nos_.push_back(std::move(noh)); }

void SubMesh::AddElement(std::unique_ptr<ElementAdaptive> element) {
  elements_.push_back(std::move(element));
}

void SubMesh::SetNoh(NodeAdaptive* noh) {
  if (!noh)
    return;
  auto copy = std::make_unique<NodeAdaptive>(*noh);
  // A new mesh node must not retain observers into the source mesh.
  copy->ClearElements();
  copy->SetId(noh->GetId());
  nos_.push_back(std::move(copy));
}

void SubMesh::SetElement(ElementAdaptive* element) {
  AddElement(std::unique_ptr<ElementAdaptive>(element));
}

unsigned int SubMesh::GetNumberNos() const noexcept {
  return static_cast<unsigned int>(nos_.size());
}

unsigned int SubMesh::GetNumberElements() const noexcept {
  return static_cast<unsigned int>(elements_.size());
}
