// Compile this test against the REAL APMesh header in a complete repository checkout.
// It executes the original ValidateBezierPatchInput, NOT the Geometry loader/mesher.
#include "input_output/input_validation.h"
#include <exception>
#include <iostream>

int main(int argc, char** argv) {
  if (argc != 2) return 2;
  try {
    apmesh::io::ValidateBezierPatchInput(argv[1]);
    std::cout << "apmesh-original-bp-header-validation-pass\n";
    return 0;
  } catch (const std::exception& e) {
    std::cerr << "Native header validation failed: " << e.what() << "\n";
    return 2;
  }
}
