#pragma once
#include "crab_mesh/aft/vertex.h"
namespace ideal_test {
void Begin() noexcept;
void Built(Par2DJMesh::Basics::Vertex*) noexcept;
void Step(int) noexcept;
void End() noexcept;
void BeginCleanup() noexcept;
void EndCleanup() noexcept;
void RetainedStorageControl();
int ExpiredAccess();
double ReadVertexX(Par2DJMesh::Basics::Vertex*);
} // namespace ideal_test
