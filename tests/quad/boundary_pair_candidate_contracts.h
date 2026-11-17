#ifndef APMESH_TEST_QUAD_BOUNDARY_PAIR_CANDIDATE_CONTRACTS_H
#define APMESH_TEST_QUAD_BOUNDARY_PAIR_CANDIDATE_CONTRACTS_H

#include "boundary_pair_candidates.h"

#include <iostream>
#include <stdexcept>

namespace quad_test {
inline void BoundaryPairCandidateContracts() {
  using Triangle = std::array<std::size_t, 3>;
  const auto require = [](bool value) {
    if (!value)
      throw std::runtime_error("Boundary pair candidate contract failed");
  };
  const std::vector<Triangle> square{{0, 1, 2}, {0, 2, 3}};
  const auto original = square;
  const auto pairs = apmesh::quad::CollectBoundaryPairCandidates(4, square);
  require(square == original && pairs.size() == 1);
  require(pairs[0].first_triangle == 0 && pairs[0].second_triangle == 1 &&
          pairs[0].shared_edge == std::array<std::size_t, 2>{0, 2} &&
          pairs[0].boundary_cycle == std::array<std::size_t, 4>{0, 1, 2, 3});
  require(apmesh::quad::CollectBoundaryPairCandidates(0, {}).empty());
  require(apmesh::quad::CollectBoundaryPairCandidates(5, {{0, 1, 2}, {0, 3, 4}}).empty());
  // All three possibilities are retained; this inventory does not pick winners.
  require(
      apmesh::quad::CollectBoundaryPairCandidates(4, {{0, 1, 3}, {1, 2, 3}, {2, 0, 3}}).size() ==
      3);
  const std::vector<std::vector<Triangle>> invalid{{{0, 1, 5}},
                                                   {{0, 0, 1}},
                                                   {{0, 1, 2}, {0, 1, 3}},
                                                   {{0, 1, 2}, {1, 0, 3}, {0, 1, 4}},
                                                   {{0, 1, 2}, {2, 1, 0}}};
  unsigned rejected = 0;
  for (const auto& input : invalid) {
    try {
      (void)apmesh::quad::CollectBoundaryPairCandidates(5, input);
    } catch (const std::invalid_argument&) {
      ++rejected;
    }
  }
  require(rejected == invalid.size());
  std::cout << "BOUNDARY_PAIR_CANDIDATES topology_cases=4 rejected=5 selected=0\n";
}
} // namespace quad_test
#endif
