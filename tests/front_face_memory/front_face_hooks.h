#pragma once
#include "crab_mesh/aft/face.h"
namespace front_face_test {
void Begin() noexcept;
void Stage(int stage) noexcept;
void Observe(Par2DJMesh::Basics::Face& face) noexcept;
void Cache(Par2DJMesh::Basics::Face& face, int index) noexcept;
void End() noexcept;
int ExpiredAccess();
} // namespace front_face_test
