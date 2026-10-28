#pragma once
#include "crab_mesh/aft/face.h"
#include <cstddef>
namespace face_adoption_test {
void Begin(std::size_t prefix, long last_id) noexcept;
void Built(Par2DJMesh::Basics::Face* face) noexcept;
void Adopted(std::size_t count) noexcept;
int ExpiredAccess();
} // namespace face_adoption_test
