#include <algorithm>
#include <array>
#include <iostream>
#include <set>
#include <stdexcept>

#include "crab_mesh/aft/smoothing_adjacency.h"

namespace {
using Par2DJMesh::AFT::orderedSmoothingAdjacency;

struct EdgeSample {
  long id;
  double neighbor_x;
  long getId() const { return id; }
};
using EdgeList = std::list<EdgeSample*>;

double sumNeighbors(const EdgeList& edges) {
  double sum = 0.0;
  for (EdgeSample* edge : edges)
    sum += edge->neighbor_x;
  return sum;
}

void require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}

void CheckFaceAdjacency() {
  struct FaceSample {
    int* a;
    int* b;
    int* c;
    double value;
    int* getV1() const { return a; }
    int* getV2() const { return b; }
    int* getV3() const { return c; }
  };
  using Faces = std::list<FaceSample*>;
  using Index = Par2DJMesh::AFT::SmoothingFaceAdjacency<int*, Faces>;
  std::array<int, 4> vertices{};
  FaceSample a{&vertices[0], &vertices[1], &vertices[2], 1e16};
  FaceSample b{&vertices[0], &vertices[0], &vertices[1], -1e16};
  FaceSample c{&vertices[0], &vertices[2], &vertices[2], 1.0};
  FaceSample d{nullptr, nullptr, nullptr, 2.0};
  Faces faces{&a, &b, &c, &d, &c};
  const Index index(faces);
  auto compare = [&](int* vertex) {
    Faces scanned;
    for (auto* face : faces)
      if (face->getV1() == vertex || face->getV2() == vertex || face->getV3() == vertex)
        scanned.push_back(face);
    require(index.Find(vertex) == scanned, "Face incidence order or multiplicity changed");
    double expected = 0.0, actual = 0.0;
    for (auto* face : scanned)
      expected += face->value;
    for (auto* face : index.Find(vertex))
      actual += face->value;
    require(actual == expected, "Face reduction order changed");
  };
  for (auto& vertex : vertices)
    compare(&vertex);
  compare(nullptr);
  require(index.Find(&vertices[0]).size() == 4, "Repeated endpoints duplicated incidence");
  require(index.Find(&vertices[3]).empty(), "Missing vertex acquired an incidence");
  c.value = 3.0;
  compare(&vertices[0]);
  require(Index(Faces{}).Find(&vertices[0]).empty(), "Empty mesh acquired incidence");
  faces.reverse();
  const Index rebuilt(faces);
  require(rebuilt.Find(&vertices[0]).front() == &c, "New scope retained previous order");
  std::cout << "Face incidence order, duplicates, repeated endpoints and live values passed\n";
}
} // namespace

int main() {
  try {
    CheckFaceAdjacency();
    std::array<EdgeSample, 3> fixture{};
    std::set<EdgeSample*> adjacency;
    require(orderedSmoothingAdjacency(adjacency).empty(), "Empty adjacency");
    const std::array<double, 3> values = {1e16, -1e16, 1.0};
    std::array<int, 3> allocation_order = {0, 1, 2};
    bool observed_pointer_order_drift = false;
    do {
      for (int slot = 0; slot < 3; ++slot) {
        EdgeSample& edge = fixture[slot];
        const int logical_index = allocation_order[slot];
        // Reuse fixed addresses while permuting the logical allocation order.
        edge.id = logical_index + 1;
        edge.neighbor_x = values[logical_index];
        adjacency.insert(&edge);
      }
      const EdgeList pointer_order(adjacency.begin(), adjacency.end());
      observed_pointer_order_drift |= sumNeighbors(pointer_order) != 1.0;
      const EdgeList ordered = orderedSmoothingAdjacency(adjacency);
      require(ordered.size() == 3, "Adjacency membership changed");
      long expected_id = 1;
      for (EdgeSample* edge : ordered) {
        require(edge->getId() == expected_id++, "Incorrect logical edge order");
      }
      require(sumNeighbors(ordered) == 1.0, "Allocation-dependent cancellation");
    } while (std::next_permutation(allocation_order.begin(), allocation_order.end()));
    require(observed_pointer_order_drift, "Negative control did not expose drift");

    fixture[1].id = fixture[0].id;
    bool duplicate_rejected = false;
    try {
      orderedSmoothingAdjacency(adjacency);
    } catch (const std::logic_error&) {
      duplicate_rejected = true;
    }
    require(duplicate_rejected, "Ambiguous edge IDs were accepted");
    adjacency.erase(&fixture[1]);
    adjacency.erase(&fixture[2]);
    require(orderedSmoothingAdjacency(adjacency).size() == 1, "Singleton adjacency changed");
    std::cout << "Six allocation permutations, cancellation control and ID invariant passed\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
