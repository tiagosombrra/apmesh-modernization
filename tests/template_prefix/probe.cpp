#include "prefix_hooks.h"
#include "crab_mesh/aft/advancing_front.h"
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <exception>
#include <memory>
#include <set>
#include <string>
#include <utility>
#include <vector>
#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

double TOLERANCE_AFT = 0.0001, TOLERANCE = 0.0001, DELTA = 0.0001, EPSYLON = 0.0000001;
std::string USE_TEMPLATE = "y";
int AFT_LOCAL_POSTPROCESS_PASSES = 0;
double AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD = 0, AFT_LOCAL_POSTPROCESS_BLEND = 0.5;
double QUADTREE_FACE_QUALITY_THRESHOLD = 0, QUADTREE_LOW_QUALITY_H_FACTOR = 1;
double TEMPLATE_POOR_SCORE_THRESHOLD = 0;

namespace prefix_test {
struct Leaf {
  long id, level;
  std::array<double, 4> box;
  std::array<std::vector<long>, 4> neighbors;
};
std::vector<Leaf> leaves;
std::set<QuadtreeCell*> live;
int presorts = 0, sort_reads = 0, preflights = 0, cardinal_links = 0, interior_leaves = 0,
    primary_reads = 0, chained_reads = 0, refusal_tag = -1;
bool armed = false;

void Require(bool condition, const char* reason, int tag = -1) {
  if (!condition)
    throw Refused{reason, tag};
}

void Gather(QuadtreeCell* cell, std::vector<QuadtreeCell*>& result) {
  if (!cell)
    throw Refused{"null_cell", -1};
  if (cell->subdivided()) {
    for (int i = 0; i < 4; ++i)
      Gather(cell->getChild(i), result);
  } else {
    result.push_back(cell);
  }
}

void Inspect(Quadtree* tree, bool ordered = true) {
  Require(tree && tree->getRoot(), "missing_root");
  Require(tree->getMin()->getX() == 0 && tree->getMin()->getY() == 0 &&
              tree->getMax()->getX() == 1 && tree->getMax()->getY() == 1,
          "root_domain");
  std::vector<QuadtreeCell*> cells;
  Gather(tree->getRoot(), cells);
  live = std::set<QuadtreeCell*>(cells.begin(), cells.end());
  Require(live.size() == cells.size(), "duplicate_leaf");
  auto native_leaves = tree->getLeaves();
  Require(native_leaves.size() == live.size() &&
              std::set<QuadtreeCell*>(native_leaves.begin(), native_leaves.end()) == live,
          "leaf_inventory");
  leaves.clear();
  cardinal_links = interior_leaves = 0;
  for (auto* cell : cells) {
    Leaf row{cell->getId(),
             cell->getLevel(),
             {cell->getMin()->getX(), cell->getMin()->getY(), cell->getMax()->getX(),
              cell->getMax()->getY()},
             {}};
    bool interior = true;
    for (int direction = 0; direction < 4; ++direction) {
      auto neighbors = cell->getNeighbors(direction);
      const auto& b = row.box;
      const bool exterior = direction == 0   ? b[1] == 0
                            : direction == 1 ? b[2] == 1
                            : direction == 2 ? b[3] == 1
                                             : b[0] == 0;
      Require(neighbors.empty() == exterior, "cardinal_boundary");
      Require(neighbors.size() <= 2, "cardinal_count");
      interior = interior && !exterior;
      double previous = 0;
      double covered = 0;
      bool first = true;
      for (auto* other : neighbors) {
        Require(live.count(other) == 1, "foreign_neighbor");
        const std::array<double, 4> q{other->getMin()->getX(), other->getMin()->getY(),
                                      other->getMax()->getX(), other->getMax()->getY()};
        const bool horizontal = direction == 0 || direction == 2;
        const double overlap = horizontal ? std::min(b[2], q[2]) - std::max(b[0], q[0])
                                          : std::min(b[3], q[3]) - std::max(b[1], q[1]);
        const bool touching = direction == 0   ? b[1] == q[3]
                              : direction == 1 ? b[2] == q[0]
                              : direction == 2 ? b[3] == q[1]
                                               : b[0] == q[2];
        Require(touching && overlap > 0, "neighbor_overlap");
        covered += overlap;
        Require(std::abs(static_cast<long>(cell->getLevel()) -
                         static_cast<long>(other->getLevel())) <= 1,
                "neighbor_level");
        auto reciprocal = other->getNeighbors((direction + 2) % 4);
        Require(std::count(reciprocal.begin(), reciprocal.end(), cell) == 1, "reciprocity");
        const double coordinate = horizontal ? q[0] : q[1];
        if (!first && ordered)
          Require(direction < 2 ? previous < coordinate : previous > coordinate, "neighbor_order");
        previous = coordinate;
        first = false;
        row.neighbors[direction].push_back(other->getId());
        ++cardinal_links;
      }
      Require(covered == (exterior ? 0 : (direction % 2 == 0 ? b[2] - b[0] : b[3] - b[1])),
              "neighbor_coverage");
    }
    interior_leaves += interior;
    leaves.push_back(std::move(row));
  }
}

void BeforeSort(Quadtree* tree) {
  ++presorts;
  Require(presorts == 1, "duplicate_presort");
  Inspect(tree, false);
  armed = true;
}

void BeforeTemplates(Quadtree* tree) {
  ++preflights;
  Require(preflights == 1, "duplicate_preflight");
  Inspect(tree);
  armed = true;
}

QuadtreeCell* Neighbor(const QuadtreeCellList& cells, bool last, int tag, bool chained) {
  Require(!cells.empty(), "empty_neighbor_read", tag);
  auto* result = last ? cells.back() : cells.front();
  Require(result != nullptr, "null_neighbor_read", tag);
  if (armed) {
    Require(live.count(result) == 1, "foreign_neighbor_read", tag);
    if (!preflights)
      ++sort_reads;
    else if (chained)
      ++chained_reads;
    else
      ++primary_reads;
  }
  return result;
}
} // namespace prefix_test

namespace {
struct PrefixReached {};
struct Summary {
  int boundary_vertices = 0, boundary_edges = 0, template_vertices = 0, template_edges = 0,
      template_faces = 0, front_edges = 0, vertex_views = 0, edge_views = 0, geometry_entries = 0;
  long vertex_id = 0, edge_id = 0, face_id = 0;
  double template_area = 0, normalized_sum = 0, midpoint_error = 0;
};
Summary summary;

PointAdaptive Physical(int side, double t) {
  return PointAdaptive(side == 1   ? 2
                       : side == 3 ? 0
                                   : 2 * t,
                       side == 0   ? 0
                       : side == 2 ? 3
                                   : 3 * t,
                       0);
}

std::unique_ptr<CurveAdaptiveParametricBezier> MakeCurve(int side, bool reversed) {
  const auto parameter = [reversed](double t) { return reversed ? 1 - t : t; };
  return std::make_unique<CurveAdaptiveParametricBezier>(
      Physical(side, parameter(0)), Physical(side, parameter(1.0 / 3)),
      Physical(side, parameter(2.0 / 3)), Physical(side, parameter(1)));
}

std::unique_ptr<Face> OldFace(std::array<std::array<double, 2>, 3> xy, long id) {
  auto a = std::make_unique<Vertex>(xy[0][0], xy[0][1]);
  auto b = std::make_unique<Vertex>(xy[1][0], xy[1][1]);
  auto c = std::make_unique<Vertex>(xy[2][0], xy[2][1]);
  auto face = std::make_unique<Face>(a.get(), b.get(), c.get(), id);
  a.release();
  b.release();
  c.release();
  face->h = 0.25; // Explicit analytic prefix input; no adaptive-policy result is claimed.
  return face;
}

class Fixture : public AdvancingFront {
  struct TemplateOwners {
    VertexList vertices;
    EdgeList edges;
    FaceList faces;
  };
  bool complete_;
  std::unique_ptr<TemplateOwners> template_owners_;

public:
  explicit Fixture(bool complete = false)
      : AdvancingFront(1.0, TOLERANCE_AFT, 7, 0.5), complete_(complete) {
    quadtree->setMaxLevelCap(-1);
  }

  void BoundaryInput(int divisions, int mask,
                     std::array<std::unique_ptr<CurveAdaptiveParametricBezier>, 4>& curves,
                     bool missing_curve) {
    using prefix_test::Require;
    for (int side = 0; side < 4; ++side) {
      Require(std::abs(curves[side]->GetLength() - (side % 2 == 0 ? 2 : 3)) < 1e-12,
              "analytic_curve_length");
      const bool reverse = (mask & (1 << side)) != 0;
      for (double local : {0.0, 0.25, 0.5, 0.75, 1.0}) {
        const auto expected = Physical(side, local);
        const auto actual = curves[side]->FindPointByParameter(reverse ? 1 - local : local);
        Require(std::abs(actual.GetX() - expected.GetX()) < 1e-12 &&
                    std::abs(actual.GetY() - expected.GetY()) < 1e-12 &&
                    std::abs(actual.GetZ() - expected.GetZ()) < 1e-12,
                "analytic_curve_position");
      }
      for (int k = 0; k < divisions; ++k) {
        const double t =
            side < 2 ? static_cast<double>(k) / divisions : 1 - static_cast<double>(k) / divisions;
        const double u = side == 1 ? 1 : side == 3 ? 0 : t;
        const double v = side == 0 ? 0 : side == 2 ? 1 : t;
        auto* curve = missing_curve && side == 0 ? nullptr : curves[side].get();
        boundary->addVertex(u, v, curve, reverse);
      }
    }
    Require(boundary->close(curves[3].get(), (mask & 8) != 0), "boundary_close");
    summary.boundary_vertices = static_cast<int>(boundary->getBoundary().size());
    summary.boundary_edges = static_cast<int>(boundary->getEdges().size());
    Require(summary.boundary_vertices == 4 * divisions && summary.boundary_edges == 4 * divisions,
            "boundary_inventory");
    double area = 0;
    for (auto* edge : boundary->getEdges()) {
      Require(std::isfinite(edge->getLen()) && std::abs(edge->getLen() - 1.0 / divisions) < 1e-12,
              "normalized_boundary_size");
      const double expected_x = (edge->getV1()->getX() + edge->getV2()->getX()) / 2;
      const double expected_y = (edge->getV1()->getY() + edge->getV2()->getY()) / 2;
      summary.midpoint_error =
          std::max(summary.midpoint_error, std::max(std::abs(edge->getMid()->getX() - expected_x),
                                                    std::abs(edge->getMid()->getY() - expected_y)));
      area += edge->getV1()->getX() * edge->getV2()->getY() -
              edge->getV2()->getX() * edge->getV1()->getY();
      summary.normalized_sum += edge->getLen();
    }
    Require(std::abs(area - 2) < 1e-12 && summary.midpoint_error <= 2 * TOLERANCE,
            "boundary_geometry");
  }

  MethodStatus makeGeometryBasedMesh() override {
    using prefix_test::Require;
    ++summary.geometry_entries;
    // Default mode cuts at this prefix. Complete mode resumes the native caller below.
    prefix_test::Inspect(quadtree);
    const auto bv = boundary->getBoundary();
    const auto be = boundary->getEdges();
    const auto qv = quadtree->getVertices();
    const auto qe = quadtree->getEdges();
    const auto qf = quadtree->getMesh();
    summary.template_vertices = static_cast<int>(qv.size());
    summary.template_edges = static_cast<int>(qe.size());
    summary.template_faces = static_cast<int>(qf.size());
    summary.front_edges = static_cast<int>(front.size());
    summary.vertex_views = static_cast<int>(vertices.size());
    summary.edge_views = static_cast<int>(edges.size());
    summary.vertex_id = lastVertexId;
    summary.edge_id = lastEdgeId;
    summary.face_id = lastFaceId;
    Require(innerVertices.empty() && innerEdges.empty() && mesh.empty(), "premature_transfer");
    std::set<Vertex*> owners(bv.begin(), bv.end());
    owners.insert(qv.begin(), qv.end());
    Require(owners.size() == bv.size() + qv.size(), "duplicate_vertex_owner");
    std::set<long> vertex_ids;
    for (auto* vertex : owners) {
      Require(vertex_ids.insert(vertex->getId()).second && vertex->getId() <= lastVertexId,
              "vertex_id_inventory");
    }
    std::set<Edge*> edge_owners(be.begin(), be.end());
    edge_owners.insert(qe.begin(), qe.end());
    Require(edge_owners.size() == be.size() + qe.size(), "duplicate_edge_owner");
    std::set<long> edge_ids;
    for (auto* edge : edge_owners) {
      Require(edge_ids.insert(edge->getId()).second && edge->getId() <= lastEdgeId,
              "edge_id_inventory");
      Require(owners.count(edge->getV1()) && owners.count(edge->getV2()), "edge_endpoint_owner");
    }
    for (auto* vertex : vertices)
      Require(owners.count(vertex), "vertex_observer");
    for (auto* edge : edges)
      Require(edge_owners.count(edge), "edge_observer");
    for (auto* edge : front)
      Require(edge_owners.count(edge), "front_observer");
    for (auto* vertex : owners)
      for (auto* edge : vertex->getAdjacentEdges())
        Require(edge_owners.count(edge) && (edge->getV1() == vertex || edge->getV2() == vertex),
                "adjacency_observer");
    for (auto* face : qf) {
      Require(owners.count(face->getV1()) && owners.count(face->getV2()) &&
                  owners.count(face->getV3()),
              "face_endpoint_owner");
      Require(face->orientedSurface() > 0 && face->getId() <= lastFaceId, "template_face");
      summary.template_area += face->orientedSurface();
    }
    if (complete_) {
      template_owners_ = std::make_unique<TemplateOwners>();
      template_owners_->vertices = qv;
      template_owners_->edges = qe;
      template_owners_->faces = qf;
      return AdvancingFront::makeGeometryBasedMesh();
    }
    throw PrefixReached{};
  }

  void PrintCompleteResult(bool success) {
    using prefix_test::Require;
    Require(complete_ && template_owners_, "missing_complete_prefix");
    for (auto* vertex : template_owners_->vertices)
      Require(std::count(innerVertices.begin(), innerVertices.end(), vertex) == 1 &&
                  std::count(vertices.begin(), vertices.end(), vertex) == 1,
              "template_vertex_transfer");
    for (auto* edge : template_owners_->edges)
      Require(std::count(innerEdges.begin(), innerEdges.end(), edge) == 1 &&
                  std::count(edges.begin(), edges.end(), edge) == 1,
              "template_edge_transfer");
    for (auto* face : template_owners_->faces)
      Require(std::count(mesh.begin(), mesh.end(), face) == 1, "template_face_transfer");
    const auto& stats = GetRunStats();
    std::printf("{\"complete_result\":{\"success\":%d,\"tree_owners\":[%zu,%zu,%zu],"
                "\"transferred\":[%zu,%zu,%zu],\"inner\":[%zu,%zu,%zu],\"queues\":[%zu,%zu],"
                "\"quality\":[%.17g,%.17g,%.17g,%.17g],\"vertices\":[",
                success, quadtree->getVertices().size(), quadtree->getEdges().size(),
                quadtree->getMesh().size(), template_owners_->vertices.size(),
                template_owners_->edges.size(), template_owners_->faces.size(),
                innerVertices.size(), innerEdges.size(), mesh.size(), front.size(), rejected.size(),
                stats.quality_post_aft_min, stats.quality_post_aft_mean,
                stats.quality_post_smoothing_min, stats.quality_post_smoothing_mean);
    bool first = true;
    for (auto* vertex : vertices) {
      std::printf("%s[%ld,%.17g,%.17g]", first ? "" : ",", vertex->getId(), vertex->getX(),
                  vertex->getY());
      first = false;
    }
    std::printf("],\"edges\":[");
    first = true;
    for (auto* edge : edges) {
      std::printf("%s[%ld,%ld,%ld]", first ? "" : ",", edge->getId(), edge->getV1()->getId(),
                  edge->getV2()->getId());
      first = false;
    }
    std::printf("],\"faces\":[");
    first = true;
    for (auto* face : mesh) {
      std::printf("%s[%ld,%ld,%ld,%ld,%.17g]", first ? "" : ",", face->getId(),
                  face->getV1()->getId(), face->getV2()->getId(), face->getV3()->getId(),
                  face->orientedSurface());
      first = false;
    }
    std::printf("]}}\n");
  }
};

void PrintLeaves() {
  std::printf("[\n");
  bool first = true;
  for (const auto& row : prefix_test::leaves) {
    std::printf("%s{\"id\":%ld,\"level\":%ld,\"box\":[%.17g,%.17g,%.17g,%.17g],\"neighbors\":[",
                first ? "" : ",", row.id, row.level, row.box[0], row.box[1], row.box[2],
                row.box[3]);
    first = false;
    for (int d = 0; d < 4; ++d) {
      std::printf("%s[", d ? "," : "");
      bool initial = true;
      for (auto id : row.neighbors[d]) {
        std::printf("%s%ld", initial ? "" : ",", id);
        initial = false;
      }
      std::printf("]");
    }
    std::printf("]}");
  }
  std::printf("]");
}
} // namespace

int main(int argc, char** argv) {
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_WARN, _CRTDBG_FILE_STDERR);
  _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_ERROR, _CRTDBG_FILE_STDERR);
  _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_ASSERT, _CRTDBG_FILE_STDERR);
#endif
  const bool complete = argc == 6 && std::string(argv[5]) == "--complete";
  if (argc != 5 && !complete)
    return 3;
  const int divisions = std::atoi(argv[1]), mask = std::atoi(argv[2]),
            old_mode = std::atoi(argv[3]), control = std::atoi(argv[4]);
  if ((divisions != 2 && divisions != 4) || (mask != 0 && mask != 15) ||
      (old_mode != 0 && old_mode != 1) || (control != 0 && control != 1))
    return 3;
  if (complete && (control != 0 || (divisions == 2 && old_mode == 0)))
    return 3;
  const char* status = "unexpected_return";
  const char* reason = "none";
  bool teardown = false, curves_live = false;
  try {
    std::array<std::unique_ptr<CurveAdaptiveParametricBezier>, 4> curves;
    for (int side = 0; side < 4; ++side)
      curves[side] = MakeCurve(side, (mask & (1 << side)) != 0);
    {
      std::vector<std::unique_ptr<Face>> old;
      if (old_mode) {
        old.push_back(OldFace({{{0, 0}, {1, 0}, {1, 1}}}, 1));
        old.push_back(OldFace({{{0, 0}, {1, 1}, {0, 1}}}, 2));
      }
      FaceList input;
      for (auto& face : old)
        input.push_back(face.get());
      Fixture fixture(complete);
      try {
        fixture.BoundaryInput(divisions, mask, curves, control == 1);
        const bool success = fixture.execute(input);
        if (complete) {
          fixture.PrintCompleteResult(success);
          status = success ? "prefix_completed" : "execution_rejected";
        }
      } catch (const PrefixReached&) {
        status = "prefix_completed";
      } catch (const prefix_test::Refused& failure) {
        status = "prefix_refused";
        reason = failure.reason;
        prefix_test::refusal_tag = failure.tag;
      }
    }
    teardown = true;
    curves_live = true;
    for (int side = 0; side < 4; ++side)
      curves_live =
          curves_live && std::abs(curves[side]->GetLength() - (side % 2 == 0 ? 2 : 3)) < 1e-12;
  } catch (const std::exception& error) {
    std::fprintf(stderr, "fixture_exception: %s\n", error.what());
    return 2;
  }
#if defined(_ITERATOR_DEBUG_LEVEL)
  constexpr int iterator_level = _ITERATOR_DEBUG_LEVEL;
#else
  constexpr int iterator_level = -1;
#endif
  std::printf(
      "{\"context\":[%d,%d,%d,%d],\"status\":\"%s\",\"reason\":\"%s\",\"refusal_tag\":%d,"
      "\"configuration\":[1,0.0001,-1,1],\"old_faces\":%d,\"old_h\":%.17g,\"preflights\":%d,"
      "\"reads\":[%d,%d],\"geometry_entries\":%d,\"teardown\":%d,\"curves_live\":%d,\"iterator_"
      "level\":%d,\"boundary\":[%d,%d,%.17g,%.17g],\"templates\":[%d,%d,%d,%.17g],\"views\":[%d,%d,"
      "%d],\"ids\":[%ld,%ld,%ld],\"cardinal_links\":%d,\"interior_leaves\":%d,\"leaves\":",
      divisions, mask, old_mode, control, status, reason, prefix_test::refusal_tag, old_mode * 2,
      old_mode ? 0.25 : 0, prefix_test::preflights, prefix_test::primary_reads,
      prefix_test::chained_reads, summary.geometry_entries, teardown, curves_live, iterator_level,
      summary.boundary_vertices, summary.boundary_edges, summary.normalized_sum,
      summary.midpoint_error, summary.template_vertices, summary.template_edges,
      summary.template_faces, summary.template_area, summary.vertex_views, summary.edge_views,
      summary.front_edges, summary.vertex_id, summary.edge_id, summary.face_id,
      prefix_test::cardinal_links, prefix_test::interior_leaves);
  PrintLeaves();
  std::printf(",\"presorts\":%d,\"sort_reads\":%d}\n", prefix_test::presorts,
              prefix_test::sort_reads);
  return status == std::string("prefix_completed") || status == std::string("prefix_refused") ? 0
                                                                                              : 1;
}
