#pragma once
#include "crab_mesh/aft/edge.h"
namespace marker_test {
void BeginMarker() noexcept;
void Constructed(Par2DJMesh::Basics::Edge* edge) noexcept;
void Published() noexcept;
void Retiring(Par2DJMesh::Basics::Edge* edge) noexcept;
void BeginSelection() noexcept;
void BeginFace() noexcept;
void EndWindow() noexcept;
void BeginCleanup() noexcept;
void EndCleanup() noexcept;
int ExpiredAccess();
} // namespace marker_test
