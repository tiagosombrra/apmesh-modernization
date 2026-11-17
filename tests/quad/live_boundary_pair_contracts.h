#ifndef APMESH_TEST_LIVE_BOUNDARY_PAIR_CONTRACTS_H
#define APMESH_TEST_LIVE_BOUNDARY_PAIR_CONTRACTS_H

#include "live_boundary_pairing.h"
#include <iostream>
#include <limits>

namespace quad_test {
inline void LiveBoundaryPairContracts() {
  using namespace apmesh::quad;
  const auto require = [](bool value, const char* message) {
    if (!value)
      throw std::runtime_error(message);
  };
  const std::array<UvVertex, 4> square{{{0, 0}, {1, 0}, {1, 1}, {0, 1}}};
  const auto make = [](const std::array<UvVertex, 4>& uv, const research::PhysicalQuadCorners& xyz,
                       double normal = 1.0) {
    LiveBoundaryPairing result;
    for (std::size_t i = 0; i < 4; ++i)
      result.AddSite({uv[i], xyz[i], {0, 0, normal}});
    result.ObserveTriangle({0, 1, 2});
    result.ObserveTriangle({0, 2, 3});
    return result;
  };
  const research::PhysicalQuadCorners xyz{{{0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0}}};
  const auto good = make(square, xyz);
  require(good.Selected().size() == 1 && good.Events()[0].score == 1.0 && good.Consumed()[0] &&
              good.Consumed()[1],
          "Square pair was not selected exactly once");
  const research::PhysicalQuadCorners shear{{{0, 0, 0}, {1, 0, 0}, {3, 1, 0}, {2, 1, 0}}};
  const auto bad_shape = make(square, shear);
  require(bad_shape.Selected().empty() && bad_shape.Events()[0].status == "rejected_shape",
          "Square UV hid an unacceptable physical angle");
  const auto inverse_chart = make({{{0, 0}, {1, 0}, {3, 1}, {2, 1}}}, xyz);
  require(inverse_chart.Selected().size() == 1 && inverse_chart.Events()[0].score == 1.0,
          "A distorted UV chart overrode valid physical shape");
  const auto concave = make({{{0, 0}, {1, 0}, {0.2, 0.2}, {0, 1}}}, xyz);
  require(concave.Events()[0].status == "rejected_uv", "Concave union was accepted");
  const auto reversed = make(square, xyz, -1.0);
  require(reversed.Events()[0].status == "rejected_physical", "Reversed physical normal passed");
  auto nonfinite = xyz;
  nonfinite[1][0] = std::numeric_limits<double>::infinity();
  require(make(square, nonfinite).Events()[0].status == "rejected_physical",
          "Nonfinite physical pair passed");
  LiveBoundaryPairing alternatives;
  for (const auto p : std::array<UvVertex, 5>{{{0, 0}, {1, 0}, {0, 1}, {1, -1}, {1, 1}}})
    alternatives.AddSite({p, {p.u, p.v, 0}, {0, 0, 1}});
  alternatives.ObserveTriangle({1, 0, 3});
  alternatives.ObserveTriangle({2, 1, 4});
  require(alternatives.Selected().empty(), "Nonadjacent alternatives paired prematurely");
  alternatives.ObserveTriangle({0, 1, 2});
  require(alternatives.Selected().size() == 1 && alternatives.Selected()[0].first_triangle == 1 &&
              alternatives.Events().back().score == 1.0,
          "Live alternatives did not choose the physically best available pair");
  LivePairEvent first{{0, 2, {0, 1}, {0, 1, 2, 3}}, 0, "eligible", 1.0, 1.0, true};
  auto second = first;
  second.edge_ratio = 2.0;
  require(PreferLivePair(first, second), "Exact angular tie ignored edge ratio");
  second = first;
  second.front_order = 1;
  require(PreferLivePair(first, second), "Exact physical tie ignored frontier order");
  second = first;
  second.candidate.first_triangle = 1;
  require(PreferLivePair(first, second), "Exact frontier tie ignored source identity");
  unsigned negatives = 0;
  for (const auto triangle :
       std::array<std::array<std::size_t, 3>, 3>{{{0, 1, 9}, {0, 0, 1}, {0, 1, 2}}}) {
    auto instance = good;
    try {
      instance.ObserveTriangle(triangle);
    } catch (const std::invalid_argument&) {
      ++negatives;
    }
  }
  require(negatives == 3, "Foreign/repeated/nonmanifold live triangle passed");
  std::cout << "LIVE_PAIR_CONTRACTS geometry_cases=7 exact_ties=3 invalid_topologies=3\n";
}
} // namespace quad_test
#endif
