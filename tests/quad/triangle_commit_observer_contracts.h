#ifndef APMESH_TEST_TRIANGLE_COMMIT_OBSERVER_CONTRACTS_H
#define APMESH_TEST_TRIANGLE_COMMIT_OBSERVER_CONTRACTS_H

#include "crab_mesh/aft/advancing_front.h"
#include <iostream>
#include <memory>
#include <stdexcept>

namespace quad_test {
inline void TriangleCommitObserverContracts() {
  using AdvancingFront = Par2DJMesh::AFT::AdvancingFront;
  using Edge = Par2DJMesh::Basics::Edge;
  using Vertex = Par2DJMesh::Basics::Vertex;
  struct EdgeDelete {
    void operator()(Edge* edge) const noexcept {
      edge->DetachVertices();
      delete edge;
    }
  };
  class ShortcutOwner final : public AdvancingFront {
  public:
    ShortcutOwner(Edge* a, Edge* b, Edge* c) : AdvancingFront(nullptr, nullptr) {
      front = {a, b, c};
    }
  };
  unsigned observed = 0, rejected = 0;
  for (unsigned mode = 0; mode < 4; ++mode) {
    auto a = std::make_unique<Vertex>(0, 0);
    auto b = std::make_unique<Vertex>(1, 0);
    auto c = std::make_unique<Vertex>(0, 1);
    std::unique_ptr<Edge, EdgeDelete> ab(new Edge(a.get(), b.get()));
    std::unique_ptr<Edge, EdgeDelete> bc(new Edge(b.get(), c.get()));
    std::unique_ptr<Edge, EdgeDelete> ca(new Edge(c.get(), a.get()));
    ShortcutOwner owner(ab.get(), bc.get(), ca.get());
    if (mode != 0)
      owner.SetTriangleCommitObserver([&](const std::array<Vertex*, 3>& endpoints) {
        if (owner.getMesh().size() != 1 ||
            endpoints != std::array<Vertex*, 3>{a.get(), b.get(), c.get()})
          throw std::logic_error("Triangle observer ran before ownership or changed endpoints");
        ++observed;
        if (mode == 2)
          throw std::runtime_error("Injected triangle observer abort");
      });
    if (mode == 3)
      owner.SetTriangleCommitObserver({});
    try {
      if (owner.makeGeometryBasedMesh() != Par2DJMesh::AFT::ADVF_GEOMETRY_MESH_DONE)
        throw std::logic_error("Triangle shortcut changed its status");
    } catch (const std::runtime_error&) {
      if (mode != 2 || owner.getMesh().size() != 1)
        throw;
      ++rejected;
    }
    if (owner.getMesh().size() != 1)
      throw std::logic_error("Triangle commit lost its face owner");
  }
  if (observed != 2 || rejected != 1)
    throw std::logic_error("Missing shortcut/cleared/throwing triangle observer coverage");
  std::cout << "TRIANGLE_COMMIT_OBSERVER cases=4 injected_aborts=1\n";
}
} // namespace quad_test
#endif
