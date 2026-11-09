#include "quadtree_quad.h"

#include "crab_mesh/aft/quadtree.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <map>
#include <set>
#include <stdexcept>
#include <utility>

namespace apmesh::quad {
namespace {

using Cell = Par2DJMesh::AFT::QuadtreeCell;
using Grid = std::uint64_t;
using Key = std::pair<Grid, Grid>;
constexpr unsigned max_depth = 30;

void Require(bool condition, const char* message) {
  if (!condition) {
    throw std::invalid_argument(message);
  }
}

struct Box {
  Cell* cell;
  unsigned depth;
  Grid x;
  Grid y;
  UvVertex minimum;
  UvVertex maximum;
};

struct Snapshot {
  std::map<Cell*, Box> boxes;
  std::map<Cell*, std::array<std::vector<Cell*>, 4>> neighbors;
  Grid resolution;
};

Snapshot ReadTree(Par2DJMesh::AFT::Quadtree& tree) {
  auto* root = tree.getRoot();
  Require(root && root->getMin() && root->getMax(), "Quadtree root/bounds are missing");
  const long root_level = root->getLevel();
  Require(root_level >= 0, "Quadtree root level is invalid");
  std::vector<Box> pending{{root,
                            0,
                            0,
                            0,
                            {root->getMin()->getX(), root->getMin()->getY()},
                            {root->getMax()->getX(), root->getMax()->getY()}}};
  Snapshot result;
  std::set<Cell*> visited;
  unsigned deepest = 0;
  while (!pending.empty()) {
    const auto box = pending.back();
    pending.pop_back();
    Require(box.cell && visited.insert(box.cell).second, "Quadtree has a repeated/cyclic cell");
    Require(box.depth <= max_depth, "Quadtree exceeds the supported relative depth");
    Require(box.cell->getLevel() >= root_level &&
                static_cast<unsigned long>(box.cell->getLevel() - root_level) == box.depth,
            "Quadtree level disagrees with hierarchy");
    auto* minimum = box.cell->getMin();
    auto* maximum = box.cell->getMax();
    Require(minimum && maximum, "Quadtree cell bounds are missing");
    Require(std::isfinite(minimum->getX()) && std::isfinite(minimum->getY()) &&
                std::isfinite(maximum->getX()) && std::isfinite(maximum->getY()) &&
                minimum->getX() < maximum->getX() && minimum->getY() < maximum->getY(),
            "Quadtree cell bounds are invalid");
    Require(minimum->getX() == box.minimum.u && minimum->getY() == box.minimum.v &&
                maximum->getX() == box.maximum.u && maximum->getY() == box.maximum.v,
            "Quadtree cell bounds disagree with dyadic hierarchy");
    std::array<Cell*, 4> children{};
    std::size_t count = 0;
    for (std::size_t i = 0; i < children.size(); ++i) {
      children[i] = box.cell->getChild(static_cast<int>(i));
      count += children[i] ? 1 : 0;
    }
    Require(count == 0 || count == 4, "Quadtree has an incomplete child set");
    if (count == 0) {
      result.boxes.emplace(box.cell, box);
      deepest = std::max(deepest, box.depth);
      continue;
    }
    Require(box.depth < max_depth, "Quadtree exceeds the supported relative depth");
    // Match the existing tree's midpoint arithmetic while only reading it.
    const UvVertex middle{(box.minimum.u + box.maximum.u) / 2.0,
                          (box.minimum.v + box.maximum.v) / 2.0};
    Require(std::isfinite(middle.u) && std::isfinite(middle.v) && middle.u > box.minimum.u &&
                middle.u < box.maximum.u && middle.v > box.minimum.v && middle.v < box.maximum.v,
            "Quadtree midpoint is not representable");
    const unsigned next = box.depth + 1;
    const Grid x = box.x * 2;
    const Grid y = box.y * 2;
    pending.push_back({children[0], next, x, y, box.minimum, middle});
    pending.push_back(
        {children[1], next, x + 1, y, {middle.u, box.minimum.v}, {box.maximum.u, middle.v}});
    pending.push_back({children[2], next, x + 1, y + 1, middle, box.maximum});
    pending.push_back(
        {children[3], next, x, y + 1, {box.minimum.u, middle.v}, {middle.u, box.maximum.v}});
  }
  result.resolution = Grid{1} << (deepest + 1);
  for (auto& [cell, box] : result.boxes) {
    const Grid scale = result.resolution >> box.depth;
    box.x *= scale;
    box.y *= scale;
    std::array<std::vector<Cell*>, 4> neighbors;
    for (int side = 0; side < 4; ++side) {
      const auto source = cell->getNeighbors(side);
      neighbors[static_cast<std::size_t>(side)].assign(source.begin(), source.end());
    }
    result.neighbors.emplace(cell, std::move(neighbors));
  }
  return result;
}

void CheckNeighbors(const Snapshot& tree) {
  // Reject malformed local lists before cross-cell checks. Otherwise pointer-map
  // iteration order can report reciprocity before a duplicate on another cell.
  for (const auto& [cell, sides] : tree.neighbors) {
    for (const auto& neighbors : sides) {
      Require(neighbors.size() <= 2, "Quadtree is not balanced 2:1");
      std::set<Cell*> unique;
      for (auto* neighbor : neighbors) {
        Require(neighbor && neighbor != cell && unique.insert(neighbor).second &&
                    tree.boxes.count(neighbor) != 0,
                "Quadtree has an invalid/duplicate neighbor");
      }
    }
  }
  for (const auto& [cell, box] : tree.boxes) {
    const Grid span = tree.resolution >> box.depth;
    const auto& sides = tree.neighbors.at(cell);
    for (std::size_t side = 0; side < sides.size(); ++side) {
      const auto& neighbors = sides[side];
      std::vector<std::pair<Grid, Grid>> intervals;
      for (auto* neighbor : neighbors) {
        const auto& other = tree.boxes.at(neighbor);
        Require((box.depth <= other.depth + 1) && (other.depth <= box.depth + 1),
                "Quadtree is not balanced 2:1");
        const auto& reverse = tree.neighbors.at(neighbor)[(side + 2) % 4];
        Require(std::count(reverse.begin(), reverse.end(), cell) == 1,
                "Quadtree neighbor relation is not reciprocal");
        const Grid other_span = tree.resolution >> other.depth;
        if (side == 0) {
          Require(other.y + other_span == box.y, "Bottom neighbor geometry disagrees");
        } else if (side == 1) {
          Require(box.x + span == other.x, "Right neighbor geometry disagrees");
        } else if (side == 2) {
          Require(box.y + span == other.y, "Top neighbor geometry disagrees");
        } else {
          Require(other.x + other_span == box.x, "Left neighbor geometry disagrees");
        }
        const Grid start = side % 2 == 0 ? other.x : other.y;
        intervals.emplace_back(start, start + other_span);
      }
      if (intervals.empty()) {
        continue;
      }
      const Grid start = side % 2 == 0 ? box.x : box.y;
      if (intervals.size() == 1) {
        Require(intervals[0].first <= start && intervals[0].second >= start + span,
                "Single neighbor does not cover the cell side");
      } else {
        std::sort(intervals.begin(), intervals.end());
        Require(intervals[0].first == start && intervals[0].second == start + span / 2 &&
                    intervals[1].first == start + span / 2 && intervals[1].second == start + span,
                "Finer neighbors do not cover two exact half sides");
      }
    }
  }
}

unsigned RotateMask(unsigned mask, unsigned turns) {
  for (unsigned i = 0; i < turns; ++i) {
    mask = ((mask << 1U) | (mask >> 3U)) & 15U;
  }
  return mask;
}

std::pair<LeafPattern, unsigned> Classify(unsigned mask) {
  // Source type numbers differ from the left-to-right order in Figure 7.
  constexpr std::array<unsigned, 6> canonical{0U, 8U, 10U, 12U, 13U, 15U};
  for (std::size_t type = 0; type < canonical.size(); ++type) {
    for (unsigned turns = 0; turns < 4; ++turns) {
      if (RotateMask(canonical[type], turns) == mask) {
        return {static_cast<LeafPattern>(type + 1), turns};
      }
    }
  }
  throw std::invalid_argument("Unknown quadtree leaf split signature");
}

const std::vector<std::vector<std::size_t>>& Cycles(LeafPattern pattern) {
  // A B C D S E N W O; ordered CCW graph transcription from Figure 7.
  static const std::array<std::vector<std::vector<std::size_t>>, 6> cycles{
      std::vector<std::vector<std::size_t>>{{0, 1, 2, 3}},
      {{0, 1, 8, 7}, {1, 2, 8}, {7, 8, 2, 3}},
      {{0, 1, 5, 7}, {7, 5, 2, 3}},
      {{0, 1, 8, 7}, {7, 8, 6, 3}, {8, 1, 2, 6}},
      {{0, 4, 7}, {7, 4, 6, 3}, {4, 1, 2, 6}},
      {{0, 4, 8, 7}, {4, 1, 5, 8}, {8, 5, 2, 6}, {7, 8, 6, 3}}};
  return cycles.at(static_cast<std::size_t>(pattern) - 1);
}

} // namespace

LeafPolygonMesh CaptureLeafPolygons(Par2DJMesh::AFT::Quadtree& tree) {
  auto snapshot = ReadTree(tree);
  const auto leaves = tree.getLeaves();
  Require(leaves.size() == snapshot.boxes.size(), "Quadtree leaf list is stale");
  std::set<Cell*> seen;
  for (auto* leaf : leaves) {
    Require(leaf && snapshot.boxes.count(leaf) != 0 && seen.insert(leaf).second,
            "Quadtree leaf list has an invalid/repeated entry");
  }
  CheckNeighbors(snapshot);
  LeafPolygonMesh result;
  result.source_leaves = leaves.size();
  std::map<Key, VertexId> ids;
  constexpr std::array<std::pair<Grid, Grid>, 9> canonical{
      std::pair<Grid, Grid>{0, 0}, {2, 0}, {2, 2}, {0, 2}, {1, 0}, {2, 1}, {1, 2}, {0, 1}, {1, 1}};
  std::size_t ordinal = 0;
  for (auto* leaf : leaves) {
    const auto leaf_ordinal = ordinal++;
    const auto& box = snapshot.boxes.at(leaf);
    const auto& neighbors = snapshot.neighbors.at(leaf);
    if (std::any_of(neighbors.begin(), neighbors.end(),
                    [](const auto& side) { return side.empty(); })) {
      ++result.excluded_boundary_leaves;
      continue;
    }
    unsigned mask = 0;
    for (unsigned side = 0; side < 4; ++side) {
      if (neighbors[side].size() == 2) {
        mask |= 1U << side;
      }
    }
    const auto [pattern, turns] = Classify(mask);
    const Grid span = snapshot.resolution >> box.depth;
    const std::array<double, 3> x{box.minimum.u, (box.minimum.u + box.maximum.u) / 2.0,
                                  box.maximum.u};
    const std::array<double, 3> y{box.minimum.v, (box.minimum.v + box.maximum.v) / 2.0,
                                  box.maximum.v};
    std::size_t polygon_ordinal = 0;
    for (const auto& cycle : Cycles(pattern)) {
      std::vector<VertexId> polygon;
      for (auto index : cycle) {
        auto [u, v] = canonical[index];
        for (unsigned i = 0; i < turns; ++i) {
          const Grid next = 2 - v;
          v = u;
          u = next;
        }
        const Key key{box.x + span * u / 2, box.y + span * v / 2};
        const UvVertex point{x[static_cast<std::size_t>(u)], y[static_cast<std::size_t>(v)]};
        const auto found = ids.find(key);
        if (found == ids.end()) {
          const auto id = result.input.vertices.size();
          result.input.vertices.push_back(point);
          ids.emplace(key, id);
          polygon.push_back(id);
        } else {
          const auto& previous = result.input.vertices[found->second];
          Require(previous.u == point.u && previous.v == point.v,
                  "Shared dyadic vertex coordinates disagree");
          polygon.push_back(found->second);
        }
      }
      result.input.polygons.push_back(std::move(polygon));
      result.origins.push_back(
          {leaf->getId(), leaf_ordinal, box.depth, pattern, polygon_ordinal++});
    }
    result.interior_area += (static_cast<long double>(box.maximum.u) - box.minimum.u) *
                            (static_cast<long double>(box.maximum.v) - box.minimum.v);
  }
  Require(!result.input.polygons.empty(), "Quadtree has no included interior leaves");
  return result;
}

UvMesh EmitLeafQuads(Par2DJMesh::AFT::Quadtree& tree, const PolygonPointSelector& selector,
                     long double relative_tolerance) {
  Require(static_cast<bool>(selector), "A polygon point selector is required");
  auto captured = CaptureLeafPolygons(tree);
  for (std::size_t i = 0; i < captured.input.polygons.size(); ++i) {
    std::vector<UvVertex> points;
    for (auto id : captured.input.polygons[i]) {
      points.push_back(captured.input.vertices[id]);
    }
    captured.input.interior_points.push_back(selector(captured.origins[i], points));
  }
  auto result = Subdivide(captured.input, relative_tolerance);
  Validate(result, captured.interior_area, relative_tolerance);
  return result;
}

} // namespace apmesh::quad
