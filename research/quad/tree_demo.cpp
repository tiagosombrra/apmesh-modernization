#include "quadtree_quad.h"
#include "tree_fixture.h"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>

int main(int argc, char** argv) {
  try {
    if (argc != 2) {
      std::cerr << "Usage: quad_tree_demo OUTPUT.obj\n";
      return 2;
    }
    if (std::filesystem::exists(argv[1])) {
      throw std::invalid_argument("Output already exists");
    }
    quad_test::TreeFixture fixture;
    fixture.CentralLeaf()->subdivideToLevel(3);
    // Explicit synthetic-demo point rule; no application centroid policy is set.
    const auto mesh =
        apmesh::quad::EmitLeafQuads(fixture.tree, [](const auto&, const auto& polygon) {
          apmesh::quad::UvVertex point{0, 0};
          for (const auto& vertex : polygon) {
            point.u += vertex.u;
            point.v += vertex.v;
          }
          point.u /= static_cast<double>(polygon.size());
          point.v /= static_cast<double>(polygon.size());
          return point;
        });
    const auto summary = apmesh::quad::Validate(mesh, 0.25L);
    std::ofstream output(argv[1], std::ios::binary);
    apmesh::quad::WriteObj(output, mesh);
    output.close();
    if (!output) {
      throw std::runtime_error("Failed to close tree QUAD OBJ");
    }
    std::cout << "source_leaves=" << fixture.tree.GetLeafCount() << " quads=" << mesh.quads.size()
              << " vertices=" << mesh.vertices.size() << " area=" << summary.area << '\n';
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
