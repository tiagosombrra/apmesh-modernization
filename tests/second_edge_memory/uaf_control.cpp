#include "second_edge_hooks.h"
namespace second_edge_test {
// Deliberately invalid: the instrument and analyzer must detect this control.
int ExpiredAccess() {
  auto* vertex = new Par2DJMesh::Basics::Vertex(0.25, 0.75);
  delete vertex;
  volatile double expired = vertex->getX();
  return expired == 0 ? 0 : 1;
}
} // namespace second_edge_test

namespace second_edge_test {
long ReadEdgeId(Par2DJMesh::Basics::Edge* edge) { return edge->getId(); }
} // namespace second_edge_test
