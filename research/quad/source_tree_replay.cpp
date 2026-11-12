#include "source_tree_replay.h"

#include "crab_mesh/aft/boundary.h"
#include "crab_mesh/aft/edge.h"
#include "crab_mesh/aft/quadtree_cell.h"
#include "crab_mesh/aft/vertex.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <map>
#include <memory>
#include <stdexcept>
#include <tuple>
#include <utility>
#include <vector>

namespace apmesh::quad {
namespace {
using Par2DJMesh::AFT::Quadtree;
using Par2DJMesh::AFT::QuadtreeCell;
using Par2DJMesh::AFT::Boundary;
using Par2DJMesh::Basics::Vertex;
using Box = std::tuple<long, double, double, double, double>;
using NeighborSides = std::array<std::vector<Box>, 4>;

void Require(bool ok, const char* message) {
  if (!ok) throw std::invalid_argument(message);
}

Box SnapshotBox(QuadtreeCell* cell) {
  Require(cell && cell->getMin() && cell->getMax(),
          "R2b2 source replay has an incomplete cell box");
  const double x0 = cell->getMin()->getX();
  const double y0 = cell->getMin()->getY();
  const double x1 = cell->getMax()->getX();
  const double y1 = cell->getMax()->getY();
  Require(std::isfinite(x0) && std::isfinite(y0) &&
              std::isfinite(x1) && std::isfinite(y1) &&
              x0 < x1 && y0 < y1,
          "R2b2 source replay has a nonfinite/degenerate cell");
  return {cell->getLevel(), x0, y0, x1, y1};
}

void MirrorHierarchy(QuadtreeCell* from, QuadtreeCell* to,
                     std::size_t& max_depth, long root_level) {
  Require(SnapshotBox(from) == SnapshotBox(to),
          "R2b2 source replay changed a native dyadic cell");
  Require(from->getLevel() - root_level >= 0 &&
              from->getLevel() - root_level <= 30,
          "R2b2 source exceeds supported exact clone depth");
  max_depth = std::max(max_depth,
      static_cast<std::size_t>(from->getLevel() - root_level));
  if (!from->subdivided()) {
    Require(!to->subdivided(),
            "R2b2 source replay subdivided an original source leaf");
    return;
  }
  Require(!to->subdivided(),
          "R2b2 source replay had unexpected pre-refined children");
  // Subdivide only THIS node to the next level, never all source leaves.
  to->subdivideToLevel(static_cast<unsigned long>(to->getLevel() + 1));
  Require(to->subdivided(), "R2b2 native source clone did not subdivide");
  for (int quadrant = 0; quadrant < 4; ++quadrant) {
    auto* from_child = from->getChild(quadrant);
    auto* to_child = to->getChild(quadrant);
    Require(from_child && to_child,
            "R2b2 source has a missing quadrant during clone");
    MirrorHierarchy(from_child, to_child, max_depth, root_level);
  }
}

std::map<Box, NeighborSides> LeafMap(Quadtree& tree) {
  std::map<Box, NeighborSides> result;
  for (auto* cell : tree.getLeaves()) {
    const Box key = SnapshotBox(cell);
    NeighborSides sides;
    for (int side = 0; side < 4; ++side) {
      const auto neighbors = cell->getNeighbors(side);
      for (auto* neighbor : neighbors) {
        Require(neighbor != nullptr, "R2b2 source has a null neighbor");
        sides[static_cast<std::size_t>(side)].push_back(SnapshotBox(neighbor));
      }
      auto& current = sides[static_cast<std::size_t>(side)];
      Require(current.size() <= 2U,
              "R2b2 source is not a balanced 2:1 native tree");
      std::sort(current.begin(), current.end());
    }
    Require(result.emplace(key, std::move(sides)).second,
            "R2b2 source has duplicate leaf geometry");
  }
  Require(!result.empty(), "R2b2 source has no native leaves");
  return result;
}

void ValidateSourceContour(const AdapterBoundaryCapture& source,
                           Quadtree& original) {
  Require(!source.accepted_mesh_published &&
              source.vertices.size() >= 4U &&
              source.vertices.size() == source.directed_edges.size(),
          "R2b2 source replay requires one provisional closed Adapter contour");
  auto* boundary = original.getBoundary();
  Require(boundary != nullptr, "R2b2 original source boundary is absent");
  const auto live_vertices = boundary->getBoundary();
  const auto live_edges = boundary->getEdges();
  Require(live_vertices.size() == source.vertices.size() &&
              live_edges.size() == source.vertices.size(),
          "R2b2 captured source chart differs from real native Boundary");

  std::size_t side_total = 0;
  for (const auto count : source.side_counts) {
    Require(count > 0U, "R2b2 missing original Adapter curve side");
    side_total += count;
  }
  Require(side_total == source.vertices.size(),
          "R2b2 source side count no longer matches original contour");

  auto v = live_vertices.begin();
  auto e = live_edges.begin();
  double signed_twice_area = 0.0;
  for (std::size_t i = 0; i < source.vertices.size(); ++i, ++v, ++e) {
    const auto& point = source.vertices[i];
    const auto& next = source.vertices[(i + 1U) % source.vertices.size()];
    const auto& segment = source.directed_edges[i];
    Require(point.side < 4U && point.aft_vertex_id > 0 &&
                point.physical_node_id > 0 && point.original_parameter >= 0.0 &&
                point.original_parameter <= 1.0 &&
                std::isfinite(point.uv.u) && std::isfinite(point.uv.v) &&
                std::isfinite(point.chart_parameter) &&
                std::isfinite(point.physical_xyz[0]) &&
                std::isfinite(point.physical_xyz[1]) &&
                std::isfinite(point.physical_xyz[2]) &&
                *v != nullptr && *e != nullptr,
            "R2b2 original source Adapter site has invalid provenance");
    Require((*v)->getId() == point.aft_vertex_id &&
                (*v)->getX() == point.uv.u && (*v)->getY() == point.uv.v,
            "R2b2 source vertex diverged from its real native AFT owner");
    Require((*e)->getV1() == *v &&
                (*e)->getV2() != nullptr &&
                segment == std::array<double, 4>{
                    point.uv.u, point.uv.v, next.uv.u, next.uv.v},
            "R2b2 original directed curve boundary diverged from its capture");
    signed_twice_area += point.uv.u * next.uv.v - next.uv.u * point.uv.v;
  }
  Require(std::isfinite(signed_twice_area) && signed_twice_area > 0.0,
          "R2b2 original Adapter chart has invalid winding");
}

}  // namespace

NativeSourceTreeReplay ReplayNativeSourceTree(
    Quadtree& original, const AdapterBoundaryCapture& source) {
  Require(original.getRoot() != nullptr,
          "R2b2 cannot clone an uninitialized original native Quadtree");
  ValidateSourceContour(source, original);
  auto target = std::make_unique<Quadtree>();
  auto boundary = std::make_unique<Boundary>();
  for (const auto& point : source.vertices) {
    auto* v = boundary->addVertex(point.uv.u, point.uv.v, nullptr);
    Require(v && v->getId() == point.aft_vertex_id,
            "R2b2 replay assigned a different original boundary site ID");
  }
  Require(boundary->close(nullptr),
          "R2b2 cannot close reconstructed native curve boundary");
  target->setBoundary(boundary.release());

  const auto source_root = SnapshotBox(original.getRoot());
  auto low = std::make_unique<Vertex>(
      std::get<1>(source_root), std::get<2>(source_root));
  auto high = std::make_unique<Vertex>(
      std::get<3>(source_root), std::get<4>(source_root));
  auto root = std::make_unique<QuadtreeCell>(
      target->getCellId(), target.get(), low.get(), high.get(),
      nullptr, std::get<0>(source_root));
  target->setRoot(root.get());
  root.release();
  low.release();
  high.release();

  NativeSourceTreeReplay report;
  report.original_leaves = original.GetLeafCount();
  report.source_boundary_segments = source.directed_edges.size();
  report.max_source_depth = 0;
  MirrorHierarchy(original.getRoot(), target->getRoot(),
                  report.max_source_depth, std::get<0>(source_root));

  const auto expected = LeafMap(original);
  const auto actual = LeafMap(*target);
  Require(expected == actual,
          "R2b2 independent native clone lost leaf bounds, depth or neighbors");
  report.replayed_leaves = target->GetLeafCount();
  report.matched_leaf_neighbors = actual.size();
  report.replayed_source_vertices = target->getBoundary()->getBoundary().size();
  Require(report.original_leaves == report.replayed_leaves &&
              report.source_boundary_segments == report.replayed_source_vertices,
          "R2b2 replay changed source leaf or boundary cardinality");

  for (auto* edge : target->getBoundary()->getEdges()) {
    target->findCell(edge);
    Require(edge->getCell() != nullptr,
            "R2b2 copied source curve edge lacks a live native cell");
  }

  report.owned_tree = std::move(target);
  return report;
}

}  // namespace apmesh::quad
