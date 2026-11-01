#ifndef APMESH_APPLICATION_GENERATION_CONTEXT_H
#define APMESH_APPLICATION_GENERATION_CONTEXT_H

#include <string>

namespace apmesh::application {
// Value-owned identity/output options. Numerical policies remain in the legacy runtime.
struct GenerationContext {
  std::string input_model;
  std::string output_prefix;
  std::string write_mode;
  std::string process_suffix;
};
} // namespace apmesh::application

#endif
