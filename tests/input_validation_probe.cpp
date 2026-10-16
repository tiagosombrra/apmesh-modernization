#include "input_output/input_validation.h"

#include <iostream>

int main(int argc, char** argv) {
  try {
    if (argc != 4) {
      throw std::runtime_error("Expected the three shipped model paths");
    }
    for (int index = 1; index < argc; ++index) {
      apmesh::io::ValidateBezierPatchInput(argv[index]);
    }
    apmesh::io::ValidateConfigValue("NUM_THREADS", "1");
    apmesh::io::ValidateConfigValue("NUM_PROCESSES", "1");
    apmesh::io::ValidateConfigValue("EPSYLON", "1e-7");
    apmesh::io::ValidateConfigValue("PATCH_QUADTREE_DEPTH_STEP1", "-1");
    apmesh::io::ValidateConfigValue("BUILD_DIR", "directory with spaces");
    apmesh::io::ValidateConfigValue("EXECUTABLE", "bin/ap_mesh.exe");
    std::cout << "Validated three shipped models and six valid configuration controls\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "Input validation control failed: " << error.what() << '\n';
    return 1;
  }
}
