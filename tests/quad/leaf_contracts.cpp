#include "quadtree_quad.h"
#include "tree_fixture.h"

#include <algorithm>
#include <array>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>

namespace {
using namespace apmesh::quad;

void Check(bool condition, const char* message) {
  if (!condition) {
    throw std::runtime_error(message);
  }
}

void Reject(const std::function<void()>& operation, const std::string& reason) {
  try {
    operation();
  } catch (const std::invalid_argument& error) {
    Check(std::string(error.what()).find(reason) != std::string::npos, error.what());
    return;
  }
  throw std::runtime_error("Malformed quadtree was accepted");
}

UvVertex TestPoint(const LeafPolygonOrigin&, const std::vector<UvVertex>& polygon) {
  // Explicit injected test points. This is not the application's centroid policy.
  UvVertex point{0, 0};
  for (const auto& vertex : polygon) {
    point.u += vertex.u;
    point.v += vertex.v;
  }
  point.u /= static_cast<double>(polygon.size());
  point.v /= static_cast<double>(polygon.size());
  return point;
}

std::string State(Par2DJMesh::AFT::Quadtree& tree) {
  std::ostringstream out;
  out << std::hexfloat << tree.getRoot();
  for (auto* leaf : tree.getLeaves()) {
    out << ' ' << leaf << ':' << leaf->getId() << ':' << leaf->getLevel() << ':' << leaf->getMin()
        << ':' << leaf->getMax() << ':' << leaf->getMin()->getX() << ':' << leaf->getMin()->getY()
        << ':' << leaf->getMax()->getX() << ':' << leaf->getMax()->getY();
    for (int side = 0; side < 4; ++side) {
      out << '[';
      for (auto* neighbor : leaf->getNeighbors(side)) {
        out << neighbor << ',';
      }
      out << ']';
    }
  }
  for (auto* vertex : tree.GetTemplateVertices()) {
    out << 'v' << vertex << ':' << vertex->getId() << ':' << vertex->getX() << ':'
        << vertex->getY();
  }
  for (auto* edge : tree.GetTemplateEdges()) {
    out << 'e' << edge << ':' << edge->getId() << ':' << edge->getV1() << ':' << edge->getV2();
  }
  for (auto* edge : tree.GetFrontEdges()) {
    out << 'b' << edge;
  }
  for (auto* face : tree.GetTemplateFaces()) {
    out << 'f' << face << ':' << face->getId() << ':' << face->getV1() << ':' << face->getV2()
        << ':' << face->getV3();
  }
  const auto& stats = tree.GetTemplateStats();
  out << ':' << stats.total_templates << ':' << stats.low_score_templates << ':'
      << stats.overall_score_sum << ':' << stats.overall_score_min << ':'
      << stats.low_quality_subdivide_hits;
  for (std::size_t i = 0; i < 6; ++i) {
    out << ':' << stats.template_count[i] << ':' << stats.template_score_sum[i] << ':'
        << stats.template_score_min[i];
  }
  return out.str();
}

long double InteriorArea(Par2DJMesh::AFT::Quadtree& tree) {
  long double area = 0;
  for (auto* leaf : tree.getLeaves()) {
    if (!leaf->inBoundary()) {
      area += (static_cast<long double>(leaf->getMax()->getX()) - leaf->getMin()->getX()) *
              (static_cast<long double>(leaf->getMax()->getY()) - leaf->getMin()->getY());
    }
  }
  return area;
}

} // namespace

int main() {
  std::size_t outcomes = 0;
  try {
    const auto run = [&outcomes](const std::string& name, const std::function<void()>& operation) {
      operation();
      ++outcomes;
      std::cout << "PASS " << name << '\n';
    };
    run("real-uniform-tree", [] {
      quad_test::TreeFixture fixture;
      const auto before = State(fixture.tree);
      const auto captured = CaptureLeafPolygons(fixture.tree);
      Check(captured.source_leaves == 16 && captured.excluded_boundary_leaves == 12,
            "Uniform tree source/exclusion count");
      Check(captured.input.polygons.size() == 4 && captured.interior_area == 0.25L,
            "Uniform tree polygon coverage");
      const auto mesh = EmitLeafQuads(fixture.tree, TestPoint);
      Check(mesh.quads.size() == 16, "Uniform tree did not emit 16 quads");
      Validate(mesh, 0.25L);
      Check(State(fixture.tree) == before, "Bridge changed source tree");
    });
    run("real-adaptive-tree", [] {
      quad_test::TreeFixture fixture;
      fixture.CentralLeaf()->subdivideToLevel(3);
      const auto before = State(fixture.tree);
      const auto captured = CaptureLeafPolygons(fixture.tree);
      Check(captured.source_leaves == 19 && captured.excluded_boundary_leaves == 12,
            "Adaptive leaf count");
      const auto mesh = EmitLeafQuads(fixture.tree, TestPoint);
      Check(mesh.quads.size() == 42, "Adaptive 2:1 tree did not emit 42 quads");
      Validate(mesh, 0.25L);
      Check(State(fixture.tree) == before, "Adaptive bridge changed source tree");
    });
    const std::array<LeafPattern, 16> expected{
        LeafPattern::T1, LeafPattern::T2, LeafPattern::T2, LeafPattern::T4,
        LeafPattern::T2, LeafPattern::T3, LeafPattern::T4, LeafPattern::T5,
        LeafPattern::T2, LeafPattern::T4, LeafPattern::T3, LeafPattern::T5,
        LeafPattern::T4, LeafPattern::T5, LeafPattern::T5, LeafPattern::T6};
    const std::array<std::size_t, 6> quad_counts{4, 11, 8, 12, 11, 16};
    for (unsigned mask = 0; mask < 16; ++mask) {
      run("real-neighbor-mask-" + std::to_string(mask), [=] {
        quad_test::TreeFixture fixture;
        auto* center = fixture.CentralLeaf();
        std::array<Par2DJMesh::AFT::QuadtreeCell*, 4> neighbors{};
        for (int side = 0; side < 4; ++side) {
          neighbors[static_cast<std::size_t>(side)] = center->getNeighbors(side).front();
        }
        for (unsigned side = 0; side < 4; ++side) {
          if ((mask & (1U << side)) != 0) {
            neighbors[side]->subdivideToLevel(3);
          }
        }
        const auto before = State(fixture.tree);
        const auto captured = CaptureLeafPolygons(fixture.tree);
        std::size_t target_quads = 0;
        for (std::size_t i = 0; i < captured.origins.size(); ++i) {
          if (captured.origins[i].cell_id == center->getId()) {
            Check(captured.origins[i].pattern == expected[mask], "Wrong source T1-T6 class");
            target_quads += captured.input.polygons[i].size();
          }
          if (i > 0) {
            Check(captured.origins[i - 1].leaf_ordinal <= captured.origins[i].leaf_ordinal,
                  "Leaf publication order changed");
          }
        }
        Check(target_quads == quad_counts[static_cast<std::size_t>(expected[mask]) - 1],
              "Target cell polygon connectivity/count");
        const auto mesh = EmitLeafQuads(fixture.tree, TestPoint);
        Validate(mesh, InteriorArea(fixture.tree));
        Check(State(fixture.tree) == before, "Mask emission changed tree/order/identity");
      });
    }
    run("legacy-tri-owners-and-trace-preserved", [] {
      quad_test::TreeFixture fixture;
      fixture.CentralLeaf()->subdivideToLevel(3);
      fixture.tree.makeTemplateBasedMesh();
      Check(!fixture.tree.GetTemplateFaces().empty(), "No actual TRI preservation comparisons");
      const auto before = State(fixture.tree);
      EmitLeafQuads(fixture.tree, TestPoint);
      Check(State(fixture.tree) == before, "Bridge changed existing TRI owners/geometry/stats");
    });
    run("neighbor-order-independent-without-sorting-source", [] {
      quad_test::TreeFixture fixture;
      fixture.CentralLeaf()->subdivideToLevel(3);
      std::ostringstream expected_obj;
      WriteObj(expected_obj, EmitLeafQuads(fixture.tree, TestPoint));
      for (auto* leaf : fixture.tree.getLeaves()) {
        for (int side = 0; side < 4; ++side) {
          auto neighbors = leaf->getNeighbors(side);
          neighbors.reverse();
          leaf->setNeighbors(side, neighbors);
        }
      }
      const auto before = State(fixture.tree);
      std::ostringstream actual_obj;
      WriteObj(actual_obj, EmitLeafQuads(fixture.tree, TestPoint));
      Check(expected_obj.str() == actual_obj.str(), "Neighbor list order changed QUAD output");
      Check(State(fixture.tree) == before, "Bridge sorted source neighbors");
    });
    run("reject-empty-root", [] {
      Par2DJMesh::AFT::Quadtree tree;
      Reject([&] { CaptureLeafPolygons(tree); }, "root");
    });
    run("reject-empty-interior", [] {
      quad_test::TreeFixture fixture(1);
      Reject([&] { CaptureLeafPolygons(fixture.tree); }, "no included");
    });
    run("reject-empty-selector", [] {
      quad_test::TreeFixture fixture;
      Reject([&] { EmitLeafQuads(fixture.tree, {}); }, "selector");
    });
    run("reject-unbalanced-tree-without-refining-it", [] {
      quad_test::TreeFixture fixture;
      fixture.CentralLeaf()->subdivideToLevel(4);
      const auto before = State(fixture.tree);
      Reject([&] { CaptureLeafPolygons(fixture.tree); }, "balanced 2:1");
      Check(State(fixture.tree) == before, "Bridge repaired source balance implicitly");
    });
    run("reject-duplicate-neighbor", [] {
      quad_test::TreeFixture fixture;
      auto* leaf = fixture.CentralLeaf();
      auto neighbors = leaf->getNeighbors(0);
      neighbors.push_back(neighbors.front());
      leaf->setNeighbors(0, neighbors);
      const auto before = State(fixture.tree);
      Reject([&] { CaptureLeafPolygons(fixture.tree); }, "duplicate neighbor");
      Check(State(fixture.tree) == before, "Bridge mutated invalid neighbors");
    });
    run("reject-one-way-neighbor", [] {
      quad_test::TreeFixture fixture;
      auto* leaf = fixture.CentralLeaf();
      leaf->setNeighbors(0, {});
      Reject([&] { CaptureLeafPolygons(fixture.tree); }, "reciprocal");
    });
    run("reject-foreign-neighbor", [] {
      quad_test::TreeFixture fixture;
      Par2DJMesh::AFT::QuadtreeCell foreign(1000, nullptr, fixture.tree.getMin(),
                                            fixture.tree.getMax());
      fixture.CentralLeaf()->setNeighbors(0, {&foreign});
      Reject([&] { CaptureLeafPolygons(fixture.tree); }, "neighbor");
    });
    run("reject-inconsistent-level", [] {
      quad_test::TreeFixture fixture;
      fixture.CentralLeaf()->setLevel(9);
      Reject([&] { CaptureLeafPolygons(fixture.tree); }, "level");
    });
    run("selector-exception-preserves-source", [] {
      quad_test::TreeFixture fixture;
      const auto before = State(fixture.tree);
      bool observed = false;
      try {
        EmitLeafQuads(fixture.tree, [](const auto&, const auto&) -> UvVertex {
          throw std::runtime_error("point selection failed");
        });
      } catch (const std::runtime_error& error) {
        observed = std::string(error.what()) == "point selection failed";
      }
      Check(observed && State(fixture.tree) == before, "Selector failure changed source");
    });
    run("reject-invalid-selected-point", [] {
      quad_test::TreeFixture fixture;
      const auto before = State(fixture.tree);
      Reject(
          [&] {
            EmitLeafQuads(fixture.tree, [](const auto&, const auto&) {
              return UvVertex{std::numeric_limits<double>::quiet_NaN(), 0};
            });
          },
          "Non-finite");
      Check(State(fixture.tree) == before, "Invalid point changed source");
    });
    std::cout << "quad_leaf_contract_outcomes=" << outcomes << " failed=0\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "FAIL after " << outcomes << " outcomes: " << error.what() << '\n';
    return 1;
  }
}
