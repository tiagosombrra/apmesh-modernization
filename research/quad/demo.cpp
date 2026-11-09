#include "uv_mesh.h"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

int main(int argc, char** argv) {
  try {
    if (argc != 2) {
      std::cerr << "Usage: quad_uv_demo OUTPUT.obj\n";
      return 2;
    }
    const std::string path = argv[1];
    if (std::filesystem::exists(path)) {
      throw std::invalid_argument("Output already exists");
    }
    const apmesh::quad::PolygonMesh input{{{0, 0}, {1, 0}, {2, 0}, {2, 1}, {1, 1}, {0, 1}},
                                          {{0, 1, 4, 5}, {1, 2, 3, 4}},
                                          {{0.5, 0.5}, {1.5, 0.5}}};
    const auto mesh = apmesh::quad::Subdivide(input);
    const auto summary = apmesh::quad::Validate(mesh, 2);
    std::ofstream output(path);
    apmesh::quad::WriteObj(output, mesh);
    output.close();
    if (!output) {
      throw std::runtime_error("Failed to close QUAD OBJ");
    }
    std::cout << "vertices=" << mesh.vertices.size() << " quads=" << mesh.quads.size()
              << " area=" << summary.area << " boundary_edges=" << summary.boundary_edges
              << " interior_edges=" << summary.interior_edges << '\n';
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
