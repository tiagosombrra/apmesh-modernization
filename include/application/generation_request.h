#ifndef APMESH_APPLICATION_GENERATION_REQUEST_H
#define APMESH_APPLICATION_GENERATION_REQUEST_H

#include <optional>
#include <string>

namespace apmesh::application {
// Synchronous execution input; numerical policies still come from the runtime.
struct GenerationRequest {
  int num_processes = 1;
  int num_threads = 1;
  // Used by the serial reader when the generator has no owned context.
  // A missing path selects the historical built-in model; an empty path is a file input.
  std::optional<std::string> input_model;
};
} // namespace apmesh::application

#endif
