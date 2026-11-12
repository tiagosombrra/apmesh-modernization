#include "owned_aft_front.h"
#include "experimental_point_rule.h"
#include "tree_fixture.h"

#include <array>
#include <cmath>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using apmesh::quad::ExperimentalPointRule;
using apmesh::quad::InteriorTemplateDispatcher;
using apmesh::quad::InteriorTemplateMode;
using apmesh::quad::InteriorTemplateSelection;
using apmesh::quad::OwnedAftFrontReport;
using apmesh::quad::OwnedQuadAftFront;
using apmesh::quad::SnapshotLegacyFront;
using apmesh::quad::UvFrontSegment;
using apmesh::quad::UvVertex;
using Par2DJMesh::AFT::Boundary;
using Par2DJMesh::AFT::Quadtree;
using Par2DJMesh::AFT::QuadtreeCell;
using Par2DJMesh::Basics::Edge;
using Par2DJMesh::Basics::Vertex;

void Check(bool condition, const char* why) {
  if (!condition) throw std::runtime_error(why);
}

UvVertex Mean(const apmesh::quad::LeafPolygonOrigin&,
              const std::vector<UvVertex>& polygon) {
  UvVertex point{0, 0};
  for (auto p : polygon) {
    point.u += p.u;
    point.v += p.v;
  }
  point.u /= static_cast<double>(polygon.size());
  point.v /= static_cast<double>(polygon.size());
  return point;
}

UvVertex Centroid(const apmesh::quad::LeafPolygonOrigin&,
                  const std::vector<UvVertex>& polygon) {
  return apmesh::quad::ExperimentalInteriorPoint(
      polygon, ExperimentalPointRule::PolygonAreaCentroid);
}

template <typename F>
void Reject(F&& op) {
  try {
    op();
  } catch (const std::invalid_argument&) {
    return;
  }
  throw std::runtime_error("R2b admitted an invalid or repeated owned front");
}

std::unique_ptr<Quadtree> NewTree(bool refined, bool eight_boundary_points = false) {
  auto tree = std::make_unique<Quadtree>();
  auto boundary = std::make_unique<Boundary>();
  if (eight_boundary_points) {
    // The research boundary is a nonuniform polygon in UV, not a Bezier patch.
    const std::array<UvVertex, 8> corners{{
        {0, 0}, {0.5, 0}, {1, 0}, {1, 0.5},
        {1, 1}, {0.5, 0.96}, {0, 1}, {0, 0.5},
    }};
    for (const auto& p : corners) boundary->addVertex(p.u, p.v, nullptr);
  } else {
    boundary->addVertex(0, 0, nullptr);
    boundary->addVertex(1, 0, nullptr);
    boundary->addVertex(1, 1, nullptr);
    boundary->addVertex(0, 1, nullptr);
  }
  Check(boundary->close(nullptr), "AFT fixture boundary did not close");
  tree->setBoundary(boundary.release());

  auto min = std::make_unique<Vertex>(0, 0);
  auto max = std::make_unique<Vertex>(1, 1);
  auto root = std::make_unique<QuadtreeCell>(
      tree->getCellId(), tree.get(), min.get(), max.get());
  tree->setRoot(root.get());
  root.release();
  min.release();
  max.release();
  tree->getRoot()->subdivideToLevel(2);

  if (refined) {
    bool found = false;
    for (auto* leaf : tree->getLeaves()) {
      if (leaf->getMin()->getX() == 0.25 &&
          leaf->getMin()->getY() == 0.25) {
        leaf->subdivideToLevel(3);
        found = true;
        break;
      }
    }
    Check(found, "R2b native tree lacks intended refined source leaf");
  }
  return tree;
}

struct Scenario {
  std::unique_ptr<OwnedQuadAftFront> aft;
  InteriorTemplateSelection selected;
  std::vector<UvFrontSegment> original;
};

Scenario Make(bool refined = false, bool centroid = false,
              bool nonuniform_boundary = false) {
  // The separate independent legacy tree publishes original TRI template
  // owners; its front is immediately copied as pure UV value geometry.
  auto originalTree = NewTree(refined, nonuniform_boundary);
  Check(originalTree->makeTemplateBasedMesh() ==
            Par2DJMesh::AFT::QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
        "Independent legacy TRI source fixture failed");
  auto snapshot = SnapshotLegacyFront(*originalTree);
  auto source = NewTree(refined, nonuniform_boundary);
  InteriorTemplateDispatcher choice(*source);
  auto selected = choice.Select(InteriorTemplateMode::ExperimentalQuad,
                                centroid ? Centroid : Mean);
  Check(source->GetTemplateFaces().empty() && source->GetFrontEdges().empty(),
        "R2b research source has legacy TRI template publication");
  auto* raw = source.get();
  auto aft = std::make_unique<OwnedQuadAftFront>(raw->getBoundary(), raw);
  source.release();
  return {std::move(aft), std::move(selected), std::move(snapshot)};
}

void CheckSeed(Scenario& scenario, std::size_t expected_segments,
               std::size_t expected_patch_edges) {
  const auto report = scenario.aft->Seed(scenario.selected, scenario.original);
  Check(report.patch_boundary_edges == expected_patch_edges &&
            report.quad_interface_edges == expected_segments &&
            report.distinct_quad_front_vertices == expected_segments &&
            report.attached_exterior_cells > 0 &&
            report.total_active_front_edges == expected_patch_edges + expected_segments &&
            !report.physical_quads_published &&
            !report.exterior_triangles_qualified &&
            scenario.aft->IsSeeded() &&
            scenario.aft->ActiveFront().size() == report.total_active_front_edges &&
            scenario.aft->OwnedSeamEdges().size() == expected_segments &&
            scenario.aft->OwnedSeamVertices().size() == expected_segments &&
            scenario.aft->Triangles().empty() &&
            scenario.aft->getQuadtree()->GetTemplateFaces().empty(),
        "R2b active AFT frontier was not seeded without TRI interior duplication");

  // Every active interface is a genuine AFT edge with a live exterior cell.
  std::set<const Vertex*> canonical;
  std::size_t inspected = 0;
  for (auto* edge : scenario.aft->OwnedSeamEdges()) {
    Check(edge && edge->getV1() && edge->getV2() && edge->getCell() &&
              edge->getCell()->inBoundary() && edge->isFree() &&
              edge->isInBoundary() && edge->getMid(),
          "R2b owned AFT front edge is not usable by makeIdealVertex");
    canonical.insert(edge->getV1());
    canonical.insert(edge->getV2());
    Check(scenario.aft->belongsToAdvFront(edge),
          "R2b AFT does not recognize owned QUAD interface edge");
    ++inspected;
  }
  Check(inspected == expected_segments && canonical.size() == expected_segments,
        "R2b failed to share endpoint IDs at exact QUAD split midpoints");

  std::multiset<std::array<double, 4>> actual;
  for (auto* edge : scenario.aft->OwnedSeamEdges()) {
    actual.insert({edge->getV1()->getX(), edge->getV1()->getY(),
                   edge->getV2()->getX(), edge->getV2()->getY()});
  }
  for (const auto& face_edge : scenario.selected.quad_region_boundary) {
    const auto& a = scenario.selected.uv_quads.vertices.at(face_edge[0]);
    const auto& b = scenario.selected.uv_quads.vertices.at(face_edge[1]);
    const auto desired = std::array<double, 4>{b.u, b.v, a.u, a.v};
    auto it = actual.find(desired);
    Check(it != actual.end(), "AFT interface failed exact reversal of QUAD CCW winding");
    actual.erase(it);
  }
  Check(actual.empty(), "R2b introduced an unknown active AFT seam segment");
}

void CheckUnmodified(Scenario& scenario) {
  Check(!scenario.aft->IsSeeded() && scenario.aft->ActiveFront().empty() &&
            scenario.aft->OwnedSeamEdges().empty() &&
            scenario.aft->OwnedSeamVertices().empty() &&
            scenario.aft->Triangles().empty() &&
            scenario.aft->getQuadtree()->GetTemplateFaces().empty(),
        "R2b rejected preflight nevertheless mutated AFT or TRI template owners");
}

}  // namespace

int main() {
  unsigned accepted = 0;
  try {
    const auto run = [&accepted](const char* name, const std::function<void()>& test) {
      test();
      ++accepted;
      std::cout << "PASS " << name << '\n';
    };
    run("native-uniform-quad-front-ownership", [] {
      auto s = Make();
      CheckSeed(s, 16, 4);
    });
    run("native-refined-source-and-exterior-cell-ownership", [] {
      auto s = Make(true);
      CheckSeed(s, 20, 4);
    });
    run("experimental-centroid-independent-seam", [] {
      auto s = Make(true, true);
      CheckSeed(s, 20, 4);
    });
    run("nonuniform-eight-edge-patch-uv-boundary-preserved", [] {
      auto s = Make(false, false, true);
      CheckSeed(s, 16, 8);
    });
    run("invalid-quad-direction-does-not-publish", [] {
      auto s = Make();
      std::swap(s.selected.quad_region_boundary[0][0],
                s.selected.quad_region_boundary[0][1]);
      Reject([&] { s.aft->Seed(s.selected, s.original); });
      CheckUnmodified(s);
    });
    run("missing-quad-halfedge-fails-closed", [] {
      auto s = Make(true);
      s.selected.quad_region_boundary.pop_back();
      Reject([&] { s.aft->Seed(s.selected, s.original); });
      CheckUnmodified(s);
    });
    run("foreign-quad-origin-fails-closed", [] {
      auto s = Make();
      for (auto& origin : s.selected.quad_face_origins) {
        origin.cell_id = -12345;
      }
      Reject([&] { s.aft->Seed(s.selected, s.original); });
      CheckUnmodified(s);
    });
    run("stale-leaf-ordinal-fails-closed", [] {
      auto s = Make();
      for (auto& origin : s.selected.quad_face_origins) {
        origin.leaf_ordinal = s.selected.source_leaves;
      }
      Reject([&] { s.aft->Seed(s.selected, s.original); });
      CheckUnmodified(s);
    });
    run("source-leaf-count-mismatch-fails-closed", [] {
      auto s = Make();
      ++s.selected.source_leaves;
      Reject([&] { s.aft->Seed(s.selected, s.original); });
      CheckUnmodified(s);
    });
    run("mismatched-original-front-fails-closed", [] {
      auto s = Make();
      std::swap(s.original[0].first, s.original[0].second);
      Reject([&] { s.aft->Seed(s.selected, s.original); });
      CheckUnmodified(s);
    });
    run("quad-still-has-original-tri-owners-fails-closed", [] {
      auto s = Make();
      s.selected.legacy_tri_faces = 1;
      Reject([&] { s.aft->Seed(s.selected, s.original); });
      CheckUnmodified(s);
    });
    run("two-attempt-reuse-prohibited", [] {
      auto s = Make();
      CheckSeed(s, 16, 4);
      const auto count = s.aft->OwnedSeamEdges().size();
      Reject([&] { s.aft->Seed(s.selected, s.original); });
      Check(s.aft->IsSeeded() && s.aft->OwnedSeamEdges().size() == count,
            "Rejected duplicate attempt destroyed accepted owned AFT front");
    });
    run("repair-invalid-source-then-retry", [] {
      auto s = Make();
      const auto saved = s.selected.quad_face_origins;
      s.selected.quad_face_origins.front().cell_id = -1;
      Reject([&] { s.aft->Seed(s.selected, s.original); });
      CheckUnmodified(s);
      s.selected.quad_face_origins = saved;
      CheckSeed(s, 16, 4);
    });
    run("r2b2-reject-unseeded-exterior-attempt", [] {
      auto s = Make();
      Reject([&] { s.aft->AttemptExteriorTriangulation(s.selected); });
      CheckUnmodified(s);
    });
    run("r2b2-reject-unbound-patch-cells", [] {
      auto s = Make();
      CheckSeed(s, 16, 4);
      Reject([&] { s.aft->AttemptExteriorTriangulation(s.selected); });
      Check(s.aft->Triangles().empty(), "Failed AFT preflight emitted triangles");
    });
    run("r2b2-run-native-original-geometry-topology", [] {
      auto s = Make();
      CheckSeed(s, 16, 4);
      // The original production tree registers boundary cells in generate().
      // This research fixture manually constructs the same already-refined tree.
      for (auto* edge : s.aft->getBoundary()->getEdges())
        s.aft->getQuadtree()->findCell(edge);
      for (auto* edge : s.aft->getBoundary()->getEdges())
        Check(edge->getCell() != nullptr,
              "Native source patch boundary has no valid cell observer");
      const auto report = s.aft->AttemptExteriorTriangulation(s.selected);
      Check(report.exterior_triangles == s.aft->Triangles().size() &&
                s.aft->OwnedSeamEdges().size() == 16 &&
                s.aft->OwnedSeamVertices().size() == 16 &&
                report.seam_edges_with_one_tri == 16 &&
                report.boundary_uv_area > report.quad_uv_area &&
                report.seam_vertices_unchanged &&
                report.spatial_overlap_tested && !report.qualified,
            "R2b2 misrepresented its measured exterior AFT attempt");
      std::cout << "R2B2_DIAGNOSTIC exterior_triangles="
                << report.exterior_triangles
                << " geometry_done=" << report.geometry_done
                << " topology_attempted=" << report.topology_attempted
                << " topology_done=" << report.topology_done
                << " unresolved_front=" << report.unresolved_front_edges
                << " rejected=" << report.unresolved_rejected_edges
                << " seam_owned=" << report.seam_edges_with_one_tri
                << " seam_expected=" << s.aft->OwnedSeamEdges().size()
                << " area_boundary=" << report.boundary_uv_area
                << " area_quad=" << report.quad_uv_area
                << " area_tri=" << report.triangle_uv_area
                << " area_balanced=" << report.uv_area_balanced << '\n';
      Reject([&] { s.aft->AttemptExteriorTriangulation(s.selected); });
      // This is an executable scientific gate: partial or overlapping area
      // cannot be promoted merely because AFT returned some faces.
      const bool complete = report.exterior_triangles > 0 &&
          report.triangles_positive && report.front_drained &&
          report.seam_orientation_complete && report.uv_area_balanced &&
          report.spatial_overlap_tested && report.no_spatial_overlap;
      if (!complete) {
        throw std::runtime_error(
            "R2b2 exterior AFT not closed: tri=" +
            std::to_string(report.exterior_triangles) +
            " front=" + std::to_string(report.unresolved_front_edges) +
            " rejected=" + std::to_string(report.unresolved_rejected_edges) +
            " seam=" + std::to_string(report.seam_edges_with_one_tri) +
            " triangle_positive=" + std::to_string(report.triangles_positive) +
            " area_balanced=" + std::to_string(report.uv_area_balanced) +
            " overlap_area=" + std::to_string(report.cumulative_overlap_area) +
            " patch=" + std::to_string(report.boundary_uv_area) +
            " quad=" + std::to_string(report.quad_uv_area) +
            " tri_area=" + std::to_string(report.triangle_uv_area));
      }
    });
    run("r2b2-uv-overlap-shared-edge-is-not-overlap", [] {
      apmesh::quad::UvMesh quads;
      const std::vector<std::array<UvVertex, 3>> triangles{
          {{{0, 0}, {1, 0}, {0, 1}}},
          {{{1, 0}, {1, 1}, {0, 1}}}};
      const auto result = apmesh::quad::AuditUvOverlap(quads, triangles);
      Check(result.no_overlap && result.overlap_area == 0.0,
            "Shared TRI edge was incorrectly counted as spatial overlap");
    });
    run("r2b2-uv-overlap-triangle-triangle-detected", [] {
      apmesh::quad::UvMesh quads;
      const std::vector<std::array<UvVertex, 3>> triangles{
          {{{0, 0}, {1, 0}, {0, 1}}},
          {{{0.1, 0.1}, {0.9, 0.1}, {0.1, 0.9}}}};
      const auto result = apmesh::quad::AuditUvOverlap(quads, triangles);
      Check(!result.no_overlap && result.tri_tri_pairs == 1 &&
                result.overlap_area > 0.0,
            "Positive-area TRI/TRI overlap was missed");
    });
    run("r2b2-uv-overlap-triangle-quad-detected", [] {
      apmesh::quad::UvMesh quads;
      quads.vertices = {{0, 0}, {0.5, 0}, {0.5, 0.5}, {0, 0.5}};
      quads.quads.push_back({{0, 1, 2, 3}});
      const std::vector<std::array<UvVertex, 3>> triangles{
          {{{0.2, 0.2}, {0.6, 0.2}, {0.2, 0.6}}}};
      const auto result = apmesh::quad::AuditUvOverlap(quads, triangles);
      Check(!result.no_overlap && result.tri_quad_pairs == 1 &&
                result.overlap_area > 0.0,
            "Positive-area TRI/QUAD overlap was missed");
    });
    run("r2b2-refined-20-split-interface-complete", [] {
      auto s = Make(true);
      CheckSeed(s, 20, 4);
      for (auto* edge : s.aft->getBoundary()->getEdges())
        s.aft->getQuadtree()->findCell(edge);
      const auto result = s.aft->AttemptExteriorTriangulation(s.selected);
      std::cout << "R2B2_REFINED exterior_triangles=" << result.exterior_triangles
                << " seam=" << result.seam_edges_with_one_tri
                << " expected=20"
                << " area_tri=" << result.triangle_uv_area
                << " overlap_area=" << result.cumulative_overlap_area << '\n';
      Check(result.exterior_triangles > 0 && result.front_drained &&
                result.triangles_positive && result.seam_orientation_complete &&
                result.seam_edges_with_one_tri == 20 &&
                result.seam_vertices_unchanged && result.uv_area_balanced &&
                result.spatial_overlap_tested && result.no_spatial_overlap,
            "Refined QUAD interface did not complete with correct TRI exterior");
    });
    run("r2b2-nonuniform-eight-point-contour-complete", [] {
      auto s = Make(false, false, true);
      CheckSeed(s, 16, 8);
      for (auto* edge : s.aft->getBoundary()->getEdges())
        s.aft->getQuadtree()->findCell(edge);
      const auto result = s.aft->AttemptExteriorTriangulation(s.selected);
      std::cout << "R2B2_NONUNIFORM exterior_triangles=" << result.exterior_triangles
                << " seam=" << result.seam_edges_with_one_tri
                << " expected=16"
                << " area_patch=" << result.boundary_uv_area
                << " area_tri=" << result.triangle_uv_area
                << " overlap_area=" << result.cumulative_overlap_area << '\n';
      Check(result.exterior_triangles > 0 && result.front_drained &&
                result.triangles_positive && result.seam_orientation_complete &&
                result.seam_edges_with_one_tri == 16 &&
                result.seam_vertices_unchanged && result.uv_area_balanced &&
                result.spatial_overlap_tested && result.no_spatial_overlap,
            "Nonuniform source patch boundary did not complete with TRI exterior");
    });
    Check(accepted == 21, "R2b/R2b2 native diagnostic controls were skipped");
    std::cout << "r2b_owned_aft_front=ok outcomes=" << accepted
              << " native_quadtree_and_boundary=1"
              << " aft_active_real_edges=1"
              << " exterior_cell_observers=1"
              << " no_legacy_tri_interior=1"
              << " physical_quad_published=0 exterior_triangles_qualified=0"
              << " real_bezier_patch_validated=0 cli_quad_enabled=0\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "FAIL r2b: " << error.what() << '\n';
    return 1;
  }
}
