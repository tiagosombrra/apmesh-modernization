#pragma once
#include "crab_mesh/aft/vertex.h"

namespace front_angle_test {
void Begin(bool geometry) noexcept;
void Constructed(Par2DJMesh::Basics::Vertex* vertex, int index) noexcept;
void Observe(Par2DJMesh::Basics::Vertex* first, Par2DJMesh::Basics::Vertex* second,
             Par2DJMesh::Basics::Vertex* selected, double angle) noexcept;
void End() noexcept;
int ExpiredAccess();
} // namespace front_angle_test
