#include "interior_template_dispatch.h"
#include "experimental_point_rule.h"
#include "tree_fixture.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <functional>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using apmesh::quad::ExperimentalPointRule;
using apmesh::quad::InteriorTemplateDispatcher;
using apmesh::quad::InteriorTemplateMode;
using apmesh::quad::InteriorTemplateSelection;
using apmesh::quad::UvVertex;
using apmesh::quad::VertexId;

void Check(bool condition, const char* reason) {
  if (!condition) throw std::runtime_error(reason);
}

UvVertex SyntheticMean(const apmesh::quad::LeafPolygonOrigin&,
                       const std::vector<UvVertex>& polygon) {
  UvVertex result{0, 0};
  for (const auto& p : polygon) {
    result.u += p.u;
    result.v += p.v;
  }
  result.u /= static_cast<double>(polygon.size());
  result.v /= static_cast<double>(polygon.size());
  return result;
}

UvVertex SyntheticCentroid(const apmesh::quad::LeafPolygonOrigin&,
                           const std::vector<UvVertex>& polygon) {
  return apmesh::quad::ExperimentalInteriorPoint(
      polygon, ExperimentalPointRule::PolygonAreaCentroid);
}

template <typename Fn>
void ExpectReject(Fn&& op, const std::string& fragment) {
  try {
    op();
  } catch (const std::invalid_argument& e) {
    Check(std::string(e.what()).find(fragment) != std::string::npos,
          "Different rejection reason from contract");
    return;
  }
  throw std::runtime_error("Unsafe QUAD template dispatch was accepted");
}

std::vector<const void*> Leaves(const quad_test::TreeFixture& fixture) {
  // Test source-cell identities without reordering or borrowing ownership.
  auto& nonconst = const_cast<quad_test::TreeFixture&>(fixture);
  std::vector<const void*> result;
  for (const auto* cell : nonconst.tree.getLeaves()) result.push_back(cell);
  return result;
}

void CheckResearchResult(const InteriorTemplateSelection& result,
                         std::size_t expected_quads,
                         std::size_t expected_front) {
  Check(result.mode == InteriorTemplateMode::ExperimentalQuad &&
            result.legacy_tri_faces == 0 &&
            !result.live_aft_interface_published &&
            !result.physical_elements_published,
        "Research-only QUAD mode mislabeled physical/live publication");
  Check(result.uv_quads.quads.size() == expected_quads &&
            result.quad_region_boundary.size() == expected_front &&
            result.excluded_boundary_leaves == 12 &&
            result.source_leaves > 0 &&
            std::abs(result.quad_region_area - 0.25L) <= 1e-12L,
        "Actual refined Quadtree QUAD counts or physical bounds changed");
  apmesh::quad::Validate(result.uv_quads, result.quad_region_area);
  std::map<std::pair<VertexId, VertexId>, unsigned> owner_count;
  for (const auto& quad : result.uv_quads.quads) {
    for (std::size_t i = 0; i < 4; ++i) {
      const VertexId a = quad.vertices[i];
      const VertexId b = quad.vertices[(i + 1) % 4];
      ++owner_count[std::minmax(a, b)];
    }
  }
  for (const auto& edge : result.quad_region_boundary) {
    Check(edge[0] < result.uv_quads.vertices.size() &&
              edge[1] < result.uv_quads.vertices.size() &&
              edge[0] != edge[1] &&
              owner_count[std::minmax(edge[0], edge[1])] == 1,
          "QUAD front is not a uniquely incident oriented UV segment");
  }
  const auto external = std::count_if(
      owner_count.begin(), owner_count.end(),
      [](const auto& edge) { return edge.second == 1; });
  Check(static_cast<std::size_t>(external) == expected_front,
        "QUAD front does not cover all exterior edges exactly once");
}

}  // namespace

int main() {
  std::size_t outcomes = 0;
  try {
    const auto run = [&outcomes](const char* name, const std::function<void()>& op) {
      op();
      ++outcomes;
      std::cout << "PASS " << name << '\n';
    };
    run("uniform-real-tree-quad-instead-of-tri", [] {
      quad_test::TreeFixture fixture;
      const auto before = Leaves(fixture);
      InteriorTemplateDispatcher selection(fixture.tree);
      auto result = selection.Select(InteriorTemplateMode::ExperimentalQuad, SyntheticMean);
      CheckResearchResult(result, 16, 16);
      Check(before == Leaves(fixture) &&
                fixture.tree.GetTemplateFaces().empty() &&
                fixture.tree.GetTemplateEdges().empty() &&
                fixture.tree.GetFrontEdges().empty(),
            "QUAD selection mutated source or also published legacy TRI");
      Check(selection.HasSelected(), "Successful research mode did not commit its choice");
    });
    run("refined-real-tree-quad-instead-of-tri", [] {
      quad_test::TreeFixture fixture;
      fixture.CentralLeaf()->subdivideToLevel(3);
      const auto before = Leaves(fixture);
      InteriorTemplateDispatcher selection(fixture.tree);
      const auto result = selection.Select(InteriorTemplateMode::ExperimentalQuad, SyntheticMean);
      CheckResearchResult(result, 42, 20);
      Check(before == Leaves(fixture) && fixture.tree.GetTemplateFaces().empty(),
            "Refined tree source or production TRI publication changed");
    });
    run("refined-centroid-independent-alternative", [] {
      quad_test::TreeFixture fixture;
      fixture.CentralLeaf()->subdivideToLevel(3);
      InteriorTemplateDispatcher selection(fixture.tree);
      auto result = selection.Select(InteriorTemplateMode::ExperimentalQuad, SyntheticCentroid);
      CheckResearchResult(result, 42, 20);
      Check(fixture.tree.GetTemplateFaces().empty(),
            "Experimental centroid published legacy TRI");
    });
    run("legacy-tri-selection-preserves-production-template-path", [] {
      quad_test::TreeFixture expected;
      quad_test::TreeFixture observed;
      expected.CentralLeaf()->subdivideToLevel(3);
      observed.CentralLeaf()->subdivideToLevel(3);
      expected.tree.makeTemplateBasedMesh();
      InteriorTemplateDispatcher selection(observed.tree);
      const auto result = selection.Select(InteriorTemplateMode::LegacyTri);
      Check(result.legacy_tri_faces > 0 &&
                result.legacy_tri_faces == expected.tree.GetTemplateFaces().size() &&
                observed.tree.GetTemplateEdges().size() == expected.tree.GetTemplateEdges().size() &&
                observed.tree.GetFrontEdges().size() == expected.tree.GetFrontEdges().size() &&
                observed.tree.GetTemplateVertices().size() == expected.tree.GetTemplateVertices().size() &&
                result.uv_quads.quads.empty() &&
                result.quad_region_boundary.empty(),
            "Dispatched TRI is not the same original Quadtree publication");
    });
    run("reject-double-selection-of-same-attempt", [] {
      quad_test::TreeFixture fixture;
      InteriorTemplateDispatcher choice(fixture.tree);
      choice.Select(InteriorTemplateMode::ExperimentalQuad, SyntheticMean);
      ExpectReject([&] { choice.Select(InteriorTemplateMode::LegacyTri); },
                   "already committed");
      Check(fixture.tree.GetTemplateFaces().empty(), "TRI published after research QUAD choice");
    });
    run("reject-quad-after-legacy-published-templates", [] {
      quad_test::TreeFixture fixture;
      fixture.tree.makeTemplateBasedMesh();
      const auto faces = fixture.tree.GetTemplateFaces().size();
      InteriorTemplateDispatcher choice(fixture.tree);
      ExpectReject([&] { choice.Select(InteriorTemplateMode::ExperimentalQuad, SyntheticMean); },
                   "already published");
      Check(fixture.tree.GetTemplateFaces().size() == faces,
            "Failed overlapping QUAD attempt destroyed TRI owners");
    });
    run("reject-quad-without-explicit-point-rule", [] {
      quad_test::TreeFixture fixture;
      InteriorTemplateDispatcher choice(fixture.tree);
      ExpectReject([&] { choice.Select(InteriorTemplateMode::ExperimentalQuad); },
                   "explicit interior-point");
      Check(!choice.HasSelected() && fixture.tree.GetTemplateFaces().empty(),
            "Missing point policy changed production source");
    });
    run("reject-point-rule-on-legacy-tri", [] {
      quad_test::TreeFixture fixture;
      InteriorTemplateDispatcher choice(fixture.tree);
      ExpectReject([&] { choice.Select(InteriorTemplateMode::LegacyTri, SyntheticMean); },
                   "must not receive");
      Check(!choice.HasSelected() && fixture.tree.GetTemplateFaces().empty(),
            "TRI policy changed despite invalid point selector");
    });
    run("reject-unsupported-mesh-element-kind", [] {
      quad_test::TreeFixture fixture;
      InteriorTemplateDispatcher choice(fixture.tree);
      ExpectReject([&] {
        choice.Select(static_cast<InteriorTemplateMode>(127), SyntheticMean);
      }, "Unsupported");
      Check(!choice.HasSelected(), "Invalid dispatcher enum was published");
    });
    run("reject-outside-polygon-then-retry", [] {
      quad_test::TreeFixture fixture;
      InteriorTemplateDispatcher choice(fixture.tree);
      const auto before = Leaves(fixture);
      ExpectReject([&] {
        choice.Select(InteriorTemplateMode::ExperimentalQuad,
                      [](const auto&, const auto&) { return UvVertex{9.0, 9.0}; });
      }, "strictly inside");
      Check(!choice.HasSelected() && fixture.tree.GetTemplateFaces().empty() &&
                Leaves(fixture) == before, "Invalid QUAD point modified the source tree");
      const auto accepted = choice.Select(InteriorTemplateMode::ExperimentalQuad, SyntheticMean);
      CheckResearchResult(accepted, 16, 16);
    });
    run("selector-callback-throw-then-retry", [] {
      quad_test::TreeFixture fixture;
      InteriorTemplateDispatcher choice(fixture.tree);
      bool caught = false;
      try {
        choice.Select(InteriorTemplateMode::ExperimentalQuad, [](const auto&, const auto&) -> UvVertex {
          throw std::runtime_error("intentional callback failure");
        });
      } catch (const std::runtime_error& e) {
        caught = std::string(e.what()) == "intentional callback failure";
      }
      Check(caught && !choice.HasSelected() && fixture.tree.GetTemplateFaces().empty(),
            "Throwing callback destroyed the tree or committed a broken selection");
      const auto accepted = choice.Select(InteriorTemplateMode::ExperimentalQuad, SyntheticMean);
      CheckResearchResult(accepted, 16, 16);
    });
    run("reject-second-mode-after-tri-success", [] {
      quad_test::TreeFixture fixture;
      InteriorTemplateDispatcher choice(fixture.tree);
      choice.Select(InteriorTemplateMode::LegacyTri);
      const auto faces = fixture.tree.GetTemplateFaces().size();
      ExpectReject([&] { choice.Select(InteriorTemplateMode::ExperimentalQuad, SyntheticMean); },
                   "already committed");
      Check(faces > 0 && faces == fixture.tree.GetTemplateFaces().size(),
            "Completed TRI template ownership changed on second selection");
    });
    Check(outcomes == 12, "Not all positive and adversarial dispatch contracts ran");
    std::cout << "r1_live_quadtree_template_dispatch=ok outcomes=" << outcomes
              << " quad_faces_uniform=16 quad_faces_refined=42"
              << " legacy_tri_unmodified=1 overlap_prevented_per_attempt=1"
              << " aft_interface_published=0 physical_quad_published=0"
              << " application_quad_mode_enabled=0"
              << " centroid_1993_approval=0\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "FAIL r1_template_dispatch: " << error.what() << '\n';
    return 1;
  }
}
