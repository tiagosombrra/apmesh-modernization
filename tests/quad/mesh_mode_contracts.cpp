#include "input_output/input_validation.h"

#include <iostream>
#include <stdexcept>

namespace {
struct Case {
  const char* key;
  const char* value;
  bool accepted;
};

bool Accepts(const Case& test) {
  try {
    apmesh::io::ValidateConfigValue(test.key, test.value);
    return true;
  } catch (const std::runtime_error&) {
    return false;
  }
}
} // namespace

int main() {
  const Case tests[] = {
      {"MESH_ELEMENT_KIND", "tri", true},
      {"MESH_ELEMENT_KIND", "quad_uv", true},
      {"MESH_ELEMENT_KIND", "quad", false},
      {"MESH_ELEMENT_KIND", "TRI", false},
      {"MESH_ELEMENT_KIND", "quad_uv_experimental", false},
      {"MESH_ELEMENT_KIND", "", false},
      {"MESH_ELEMENT_KIND", "tri trailing", false},
      {"USE_TEMPLATE", "y", true},
      {"USE_TEMPLATE", "n", true},
      {"USE_TEMPLATE", "quad_uv", false},
      {"UNDECLARED_MESH_KIND", "tri", false},
  };
  for (const auto& test : tests) {
    if (Accepts(test) != test.accepted) {
      std::cerr << "Unexpected validation for " << test.key << '=' << test.value << '\n';
      return 1;
    }
  }
  std::cout << "validated_mesh_mode_cases=" << sizeof(tests) / sizeof(tests[0]) << '\n';
  return 0;
}
