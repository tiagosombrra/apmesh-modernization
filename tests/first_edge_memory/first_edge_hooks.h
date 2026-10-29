#pragma once
#include "crab_mesh/aft/edge.h"
#include <cstddef>
namespace first_edge_test {
void Begin(long last_id, std::size_t owners, bool owned) noexcept;
void Built(Par2DJMesh::Basics::Edge* edge) noexcept;
void Step(int phase) noexcept;
void End() noexcept;
void BeginCleanup() noexcept;
void EndCleanup() noexcept;
void RetainedStorageControl();
int ExpiredAccess();
long ReadEdgeId(Par2DJMesh::Basics::Edge* edge);
} // namespace first_edge_test
