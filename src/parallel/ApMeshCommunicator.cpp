#include "../../include/parallel/ApMeshCommunicator.h"

ApMeshCommunicator::ApMeshCommunicator(bool sharedParallelismEnabled)
    : Parallel::TMCommunicator::TMCommunicator(sharedParallelismEnabled) {}

ApMeshCommunicator::~ApMeshCommunicator() {}

bool ApMeshCommunicator::isMaster() const {
  return (this->rank() == this->root());
}

Parallel::Transferable *ApMeshCommunicator::unpack([
    [maybe_unused]] Parallel::Package &p) const {
  return NULL;
}
