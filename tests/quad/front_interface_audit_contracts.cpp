#include "front_interface_audit.h"
#include "experimental_point_rule.h"
#include "tree_fixture.h"

#include <algorithm>
#include <cmath>
#include <functional>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using apmesh::quad::CompareLegacyAndQuadFront;
using apmesh::quad::ExperimentalPointRule;
using apmesh::quad::FrontInterfaceAudit;
using apmesh::quad::InteriorTemplateDispatcher;
using apmesh::quad::InteriorTemplateMode;
using apmesh::quad::InteriorTemplateSelection;
using apmesh::quad::SnapshotLegacyFront;
using apmesh::quad::UvFrontSegment;
using apmesh::quad::UvVertex;

void Check(bool ok, const char* why) {
  if (!ok) {
    throw std::runtime_error(why);
  }
}

UvVertex Mean(const apmesh::quad::LeafPolygonOrigin&,
              const std::vector<UvVertex>& polygon) {
  UvVertex candidate{0, 0};
  for (const auto& point : polygon) {
    candidate.u += point.u;
    candidate.v += point.v;
  }
  candidate.u /= static_cast<double>(polygon.size());
  candidate.v /= static_cast<double>(polygon.size());
  return candidate;
}

UvVertex Centroid(const apmesh::quad::LeafPolygonOrigin&,
                  const std::vector<UvVertex>& polygon) {
  return apmesh::quad::ExperimentalInteriorPoint(
      polygon, ExperimentalPointRule::PolygonAreaCentroid);
}

struct Witness {
  std::vector<UvFrontSegment> legacy;
  InteriorTemplateSelection quad;
};

// Both trees use the same actual native C++ hierarchy and refinement. The
// legacy template call belongs only to an independent comparison fixture.
Witness MakeWitness(bool refined, bool use_centroid = false) {
  quad_test::TreeFixture legacy;
  quad_test::TreeFixture quad;
  if (refined) {
    legacy.CentralLeaf()->subdivideToLevel(3);
    quad.CentralLeaf()->subdivideToLevel(3);
  }

  InteriorTemplateDispatcher choice(quad.tree);
  auto selected = choice.Select(InteriorTemplateMode::ExperimentalQuad,
                                use_centroid ? Centroid : Mean);
  Check(!selected.uv_quads.quads.empty() && selected.legacy_tri_faces == 0 &&
            !selected.live_aft_interface_published &&
            !selected.physical_elements_published &&
            quad.tree.GetTemplateFaces().empty() && quad.tree.GetFrontEdges().empty(),
        "The QUAD source modified or used original TRI template ownership");

  legacy.tree.makeTemplateBasedMesh();
  Check(!legacy.tree.GetTemplateFaces().empty(),
        "Independent original Quadtree TRI reference has no templates");
  auto borrowed_snapshot = SnapshotLegacyFront(legacy.tree);
  Check(!borrowed_snapshot.empty(), "Real Quadtree legacy front was not populated");
  return {std::move(borrowed_snapshot), std::move(selected)};
}

FrontInterfaceAudit Audit(const Witness& w) {
  return CompareLegacyAndQuadFront(w.legacy, w.quad.uv_quads,
                                   w.quad.quad_region_boundary);
}

void CheckAudit(const Witness& w, std::size_t expected_quad_edges) {
  const auto result = Audit(w);
  Check(result.complete_coverage && result.opposite_winding &&
            result.quad_segments == expected_quad_edges &&
            result.legacy_segments == w.legacy.size() &&
            result.legacy_segments > 0 &&
            result.quad_segments > result.legacy_segments &&
            result.original_split_segments > 0 &&
            result.new_split_points ==
                result.quad_segments - result.legacy_segments &&
            result.max_parts_per_legacy_segment >= 2 &&
            result.legacy_total_length == result.quad_total_length &&
            std::abs(result.legacy_total_length - 2.0L) < 1.0e-15L,
        "Real Quadtree has unqualified QUAD split coverage or winding");
}

template <typename Fn>
void Reject(Fn&& operation) {
  try {
    operation();
  } catch (const std::invalid_argument&) {
    return;
  }
  throw std::runtime_error("Malformed QUAD-to-AFT front geometry was admitted");
}

}  // namespace

int main() {
  std::size_t checks = 0;
  try {
    const auto run = [&checks](const char* label, const std::function<void()>& task) {
      task();
      ++checks;
      std::cout << "PASS " << label << '\n';
    };
    run("uniform-native-tree-split-front-exact", [] {
      const auto witness = MakeWitness(false);
      Check(witness.quad.uv_quads.quads.size() == 16,
            "Uniform native tree QUAD count changed from R1");
      CheckAudit(witness, 16);
      const auto result = Audit(witness);
      std::cout << "  uniform_source_edges=" << result.legacy_segments
                << " quad_parts=" << result.quad_segments
                << " original_split=" << result.original_split_segments << '\n';
    });
    run("refined-native-tree-t1-t6-front-exact", [] {
      const auto witness = MakeWitness(true);
      Check(witness.quad.uv_quads.quads.size() == 42,
            "Refined native tree QUAD count changed from R1");
      CheckAudit(witness, 20);
      const auto result = Audit(witness);
      std::cout << "  refined_source_edges=" << result.legacy_segments
                << " quad_parts=" << result.quad_segments
                << " original_split=" << result.original_split_segments << '\n';
    });
    run("refined-area-centroid-rule-unchanged-front", [] {
      CheckAudit(MakeWitness(true, true), 20);
    });
    run("value-snapshot-survives-source-destruction", [] {
      // MakeWitness destroys both real tree owners before this comparison.
      auto detached = MakeWitness(false);
      const auto before = detached.legacy;
      CheckAudit(detached, 16);
      Check(before.size() == detached.legacy.size(),
            "Owned segment capture lost entries when original tree was released");
    });
    run("independent-front-order-does-not-change-comparison", [] {
      auto detached = MakeWitness(true);
      std::reverse(detached.legacy.begin(), detached.legacy.end());
      std::reverse(detached.quad.quad_region_boundary.begin(),
                   detached.quad.quad_region_boundary.end());
      CheckAudit(detached, 20);
    });
    run("unpublished-legacy-tree-rejected", [] {
      quad_test::TreeFixture fresh;
      Reject([&] { SnapshotLegacyFront(fresh.tree); });
    });
    run("duplicate-legacy-edge-rejected", [] {
      auto witness = MakeWitness(false);
      witness.legacy.push_back(witness.legacy.front());
      Reject([&] { Audit(witness); });
    });
    run("missing-legacy-edge-rejected", [] {
      auto witness = MakeWitness(false);
      witness.legacy.pop_back();
      Reject([&] { Audit(witness); });
    });
    run("reversed-legacy-winding-rejected", [] {
      auto witness = MakeWitness(false);
      std::swap(witness.legacy[0].first, witness.legacy[0].second);
      Reject([&] { Audit(witness); });
    });
    run("nonaxis-legacy-edge-rejected", [] {
      auto witness = MakeWitness(false);
      auto& edge = witness.legacy.front();
      if (edge.first.v == edge.second.v) {
        edge.first.v += 0.01;
      } else {
        edge.first.u += 0.01;
      }
      Reject([&] { Audit(witness); });
    });
    run("nonfinite-legacy-edge-rejected", [] {
      auto witness = MakeWitness(false);
      witness.legacy.front().first.u = std::numeric_limits<double>::quiet_NaN();
      Reject([&] { Audit(witness); });
    });
    run("zero-length-legacy-edge-rejected", [] {
      auto witness = MakeWitness(false);
      witness.legacy.front().second = witness.legacy.front().first;
      Reject([&] { Audit(witness); });
    });
    run("missing-quad-halfedge-rejected", [] {
      auto witness = MakeWitness(true);
      witness.quad.quad_region_boundary.pop_back();
      Reject([&] { Audit(witness); });
    });
    run("duplicate-quad-halfedge-rejected", [] {
      auto witness = MakeWitness(true);
      witness.quad.quad_region_boundary.back() =
          witness.quad.quad_region_boundary.front();
      Reject([&] { Audit(witness); });
    });
    run("reversed-quad-winding-rejected", [] {
      auto witness = MakeWitness(false);
      std::swap(witness.quad.quad_region_boundary.front()[0],
                witness.quad.quad_region_boundary.front()[1]);
      Reject([&] { Audit(witness); });
    });
    run("foreign-quad-vertex-id-rejected", [] {
      auto witness = MakeWitness(false);
      witness.quad.quad_region_boundary.front()[0] =
          witness.quad.uv_quads.vertices.size();
      Reject([&] { Audit(witness); });
    });
    run("moved-quad-midpoint-rejected", [] {
      auto witness = MakeWitness(false);
      const auto id = witness.quad.quad_region_boundary.front()[0];
      witness.quad.uv_quads.vertices.at(id).u += 0.007;
      Reject([&] { Audit(witness); });
    });
    run("legacy-edge-partial-gap-rejected", [] {
      auto witness = MakeWitness(false);
      auto& first = witness.legacy.front();
      first.second.u = 0.5 * (first.first.u + first.second.u);
      first.second.v = 0.5 * (first.first.v + first.second.v);
      Reject([&] { Audit(witness); });
    });
    run("legacy-front-extra-offline-edge-rejected", [] {
      auto witness = MakeWitness(false);
      witness.legacy.push_back({{0.01, 0.01}, {0.02, 0.01}});
      Reject([&] { Audit(witness); });
    });
    run("invalid-quad-face-incidence-rejected", [] {
      auto witness = MakeWitness(false);
      witness.quad.uv_quads.quads.push_back(witness.quad.uv_quads.quads.front());
      Reject([&] { Audit(witness); });
    });

    Check(checks == 20, "R2a positive and negative contract coverage was incomplete");
    std::cout << "r2a_front_geometry_audit=ok outcomes=" << checks
              << " native_cpp_quadtree=1 legacy_front_published_reference=1"
              << " quad_source_template_provenance=1 oriented_split_coverage=1"
              << " aft_active_edges_published=0 physical_quad_published=0"
              << " application_quad_mode_enabled=0 historical_1993_policy_approved=0\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "FAIL R2a source front audit: " << error.what() << '\n';
    return 1;
  }
}
