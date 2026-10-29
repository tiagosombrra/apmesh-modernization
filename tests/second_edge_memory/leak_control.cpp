#include "second_edge_hooks.h"
namespace second_edge_test {
// Deliberately invalid: retained storage must be detected independently.
void RetainedStorageControl() {
  auto* retained = new Par2DJMesh::Basics::Vertex(0.25, 0.75);
  (void)retained;
}
} // namespace second_edge_test
