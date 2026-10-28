#include "front_angle_hooks.h"

namespace front_angle_test {
// Deliberately invalid: both ASan and static analysis must detect this control.
int ExpiredAccess() {
  auto* vertex = new Par2DJMesh::Basics::Vertex(0.25, 0.75);
  delete vertex;
  volatile double expired = vertex->getX();
  return expired == 0 ? 0 : 1;
}
} // namespace front_angle_test
