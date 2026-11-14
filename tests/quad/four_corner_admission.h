#ifndef APMESH_QUAD_TEST_FOUR_CORNER_ADMISSION_H
#define APMESH_QUAD_TEST_FOUR_CORNER_ADMISSION_H

#include "physical_quadrilateral_adaptive.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <vector>

namespace apmesh::quad::test {

inline void TestFourCornerAdmission() {
  using research::QuadrilateralAdaptive;
  using Parameters = QuadrilateralAdaptive::Parameters;
  const Parameters square{{{0, 0}, {1, 0}, {1, 1}, {0, 1}}};
  std::array<NodeAdaptive, 4> owned{NodeAdaptive(0, 0, 0), NodeAdaptive(1, 0, 0),
                                    NodeAdaptive(1, 1, 0), NodeAdaptive(0, 1, 0)};
  const QuadrilateralAdaptive::Nodes nodes{&owned[0], &owned[1], &owned[2], &owned[3]};
  const VectorAdaptive normal(0, 0, 1);
  QuadrilateralAdaptive first(nodes, square, normal);
  QuadrilateralAdaptive second(nodes, square, normal);
  std::array<std::vector<ElementAdaptive*>, 4> values;
  std::array<std::vector<const void*>, 4> slots;
  for (std::size_t i = 0; i < owned.size(); ++i) {
    for (const auto& observer : owned[i].GetElements()) {
      values[i].push_back(observer);
      slots[i].push_back(&observer);
    }
  }
  unsigned accepted = 0;
  unsigned rejected = 0;
  const auto require = [](bool condition, const char* message) {
    if (!condition)
      throw std::runtime_error(message);
  };
  const auto check = [&](const Parameters& uv, bool expected, const char* message) {
    bool constructed = false;
    try {
      QuadrilateralAdaptive candidate(nodes, uv, normal);
      constructed = true;
      require(candidate.GetArea() == 1.0, "UV admission changed the physical square area");
      for (const auto& node : owned) {
        require(node.GetElements().size() == 3 && node.GetElements().back() == &candidate,
                "Accepted UV input did not append its own observer");
      }
    } catch (const std::invalid_argument&) {
      constructed = false;
    }
    for (std::size_t i = 0; i < owned.size(); ++i) {
      require(owned[i].GetElements().size() == values[i].size(),
              "UV admission changed existing observer count");
      std::size_t j = 0;
      for (const auto& observer : owned[i].GetElements()) {
        require(observer == values[i][j] && &observer == slots[i][j],
                "UV admission changed observer value, order or list slot");
        ++j;
      }
    }
    require(constructed == expected, message);
    if (constructed)
      ++accepted;
    else
      ++rejected;
  };
  const auto transforms = [&](Parameters shape, bool expected, const char* message) {
    for (unsigned reflected = 0; reflected < 2; ++reflected) {
      auto variant = shape;
      if (reflected) {
        for (auto& point : variant)
          point[0] = 1.0 - point[0];
        std::reverse(variant.begin(), variant.end());
      }
      for (unsigned rotation = 0; rotation < 4; ++rotation) {
        check(variant, expected, message);
        std::rotate(variant.begin(), variant.begin() + 1, variant.end());
      }
    }
  };

  // Physical nodes remain a valid square so these witnesses isolate UV admission.
  transforms(Parameters{{{0, 0}, {1, 0}, {0.25, 0.25}, {0, 1}}}, false,
             "Concave UV quad was accepted");
  transforms(Parameters{{{0, 0}, {1, 0}, {0.5, 0.5}, {0, 1}}}, false,
             "Collinear UV corner was accepted");
  transforms(Parameters{{{0, 0}, {1, 0}, {1, 0}, {0, 1}}}, false,
             "Repeated UV position was accepted");
  transforms(Parameters{{{0, 0}, {1, 1}, {1, 0}, {0, 1}}}, false, "Crossing UV quad was accepted");
  transforms(square, true, "Valid square UV input was refused");
  transforms(Parameters{{{0.125, 0.125}, {0.875, 0.125}, {0.75, 0.875}, {0.25, 0.75}}}, true,
             "Valid skew convex UV input was refused");
  auto clockwise = square;
  std::reverse(clockwise.begin(), clockwise.end());
  for (unsigned rotation = 0; rotation < 4; ++rotation) {
    check(clockwise, false, "Clockwise UV input was accepted");
    std::rotate(clockwise.begin(), clockwise.begin() + 1, clockwise.end());
  }
  // Exact dyadic offsets place the small corner determinant below/above 1e-14.
  for (int exponent : {-48, -46}) {
    const double point = 0.5 + std::ldexp(1.0, exponent);
    Parameters near_collinear{{{0, 0}, {1, 0}, {point, point}, {0, 1}}};
    for (unsigned rotation = 0; rotation < 4; ++rotation) {
      check(near_collinear, exponent == -46,
            "UV corner threshold acceptance differs from its contract");
      std::rotate(near_collinear.begin(), near_collinear.begin() + 1, near_collinear.end());
    }
  }
  require(accepted == 20 && rejected == 40, "Incomplete four-corner admission inventory");
  std::cout << "quad_four_corner_admission=ok accepted=20 rejected=40 "
               "observer_values_order_slots=preserved\n";
}

} // namespace apmesh::quad::test

#endif
