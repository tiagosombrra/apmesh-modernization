#include "ideal_hooks.h"
namespace ideal_test {
// Deliberately invalid: the instrument and analyzer must detect this control.
int ExpiredAccess() {
  auto* vertex = new Par2DJMesh::Basics::Vertex(0.25, 0.75);
  delete vertex;
  volatile double expired = vertex->getX();
  return expired == 0 ? 0 : 1;
}
} // namespace ideal_test

namespace ideal_test {
double ReadVertexX(Par2DJMesh::Basics::Vertex* vertex) { return vertex->getX(); }
} // namespace ideal_test
