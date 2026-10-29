#pragma once
#include "crab_mesh/aft/edge.h"
#include <cstddef>
namespace second_edge_test {
void Begin(long last_id, std::size_t owners, Par2DJMesh::Basics::Edge* first, bool owned) noexcept;
void Built(Par2DJMesh::Basics::Edge* edge) noexcept;
void Step(int phase) noexcept;
void End() noexcept;
void BeginCleanup() noexcept;
void EndCleanup() noexcept;
void RetainedStorageControl();
int ExpiredAccess();
long ReadEdgeId(Par2DJMesh::Basics::Edge* edge);
} // namespace second_edge_test
