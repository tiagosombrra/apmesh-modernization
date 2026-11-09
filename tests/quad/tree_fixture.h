#ifndef APMESH_TEST_QUAD_TREE_FIXTURE_H
#define APMESH_TEST_QUAD_TREE_FIXTURE_H

#include "crab_mesh/aft/quadtree.h"

#include <memory>
#include <stdexcept>

namespace quad_test {

struct TreeFixture {
  // A real closed boundary makes the existing TRI template entry admissible.
  // Quadtree owns the boundary, root endpoints and complete cell graph.
  Par2DJMesh::AFT::Quadtree tree;

  explicit TreeFixture(unsigned depth = 2) {
    auto boundary = std::make_unique<Par2DJMesh::AFT::Boundary>();
    boundary->addVertex(0, 0, nullptr);
    boundary->addVertex(1, 0, nullptr);
    boundary->addVertex(1, 1, nullptr);
    boundary->addVertex(0, 1, nullptr);
    if (!boundary->close(nullptr)) {
      throw std::runtime_error("Fixture boundary did not close");
    }
    tree.setBoundary(boundary.release());
    auto minimum = std::make_unique<Par2DJMesh::Basics::Vertex>(0, 0);
    auto maximum = std::make_unique<Par2DJMesh::Basics::Vertex>(1, 1);
    auto root = std::make_unique<Par2DJMesh::AFT::QuadtreeCell>(tree.getCellId(), &tree,
                                                                minimum.get(), maximum.get());
    tree.setRoot(root.get());
    root.release();
    minimum.release();
    maximum.release();
    tree.getRoot()->subdivideToLevel(depth);
  }

  Par2DJMesh::AFT::QuadtreeCell* CentralLeaf() {
    for (auto* leaf : tree.getLeaves()) {
      if (leaf->getMin()->getX() == 0.25 && leaf->getMin()->getY() == 0.25) {
        return leaf;
      }
    }
    throw std::runtime_error("Central fixture leaf not found");
  }
};

} // namespace quad_test

#endif
