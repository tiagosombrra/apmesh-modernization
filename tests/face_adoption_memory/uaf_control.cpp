#include "face_adoption_hooks.h"
namespace face_adoption_test {
// Deliberately invalid: the instrument and analyzer must detect this control.
int ExpiredAccess() {
  auto* vertex = new Par2DJMesh::Basics::Vertex(0.25, 0.75);
  delete vertex;
  volatile double expired = vertex->getX();
  return expired == 0 ? 0 : 1;
}
} // namespace face_adoption_test
