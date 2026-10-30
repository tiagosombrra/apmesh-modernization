#pragma once
#include "crab_mesh/aft/quadtree.h"

namespace prefix_test {
struct Refused {
  const char* reason;
  int tag;
};
void BeforeSort(Quadtree* tree);
void BeforeTemplates(Quadtree* tree);
QuadtreeCell* Neighbor(const QuadtreeCellList& cells, bool last, int tag, bool chained);
} // namespace prefix_test
