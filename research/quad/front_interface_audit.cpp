#include "front_interface_audit.h"

#include "crab_mesh/aft/edge.h"
#include "crab_mesh/aft/quadtree.h"
#include "crab_mesh/aft/vertex.h"

#include <algorithm>
#include <cmath>
#include <map>
#include <stdexcept>
#include <utility>
#include <vector>

namespace apmesh::quad {
namespace {

void Require(bool condition, const char* why) {
  if (!condition) {
    throw std::invalid_argument(why);
  }
}

using EdgeId = std::pair<VertexId, VertexId>;
using LineId = std::pair<int, double>;

struct FaceEdgeUse {
  std::size_t count = 0;
  std::array<VertexId, 2> directed{};
};

EdgeId Canonical(VertexId a, VertexId b) {
  return std::minmax(a, b);
}

std::vector<UvFrontSegment> QuadBoundaryGeometry(
    const UvMesh& mesh,
    const std::vector<std::array<VertexId, 2>>& directed_boundary) {
  Require(!mesh.vertices.empty() && !mesh.quads.empty(),
          "QUAD front needs a nonempty physical source UV mesh");

  std::map<EdgeId, FaceEdgeUse> face_edges;
  for (const auto& quad : mesh.quads) {
    for (std::size_t i = 0; i < quad.vertices.size(); ++i) {
      const auto a = quad.vertices[i];
      const auto b = quad.vertices[(i + 1) % quad.vertices.size()];
      Require(a < mesh.vertices.size() && b < mesh.vertices.size() && a != b,
              "QUAD face references an invalid UV vertex");
      auto& use = face_edges[Canonical(a, b)];
      Require(use.count < 2, "QUAD face edge has more than two owners");
      if (use.count == 1) {
        Require(use.directed[0] == b && use.directed[1] == a,
                "QUAD internal edge faces have inconsistent winding");
      }
      if (++use.count == 1) {
        use.directed = {a, b};
      }
    }
  }

  std::size_t expected_boundary_edges = 0;
  for (const auto& item : face_edges) {
    if (item.second.count == 1) {
      ++expected_boundary_edges;
    }
  }
  Require(expected_boundary_edges > 0 &&
              directed_boundary.size() == expected_boundary_edges,
          "QUAD boundary cardinality does not match one-owner face edges");

  std::map<EdgeId, bool> supplied;
  std::vector<UvFrontSegment> result;
  result.reserve(directed_boundary.size());
  for (const auto& edge : directed_boundary) {
    const auto a = edge[0];
    const auto b = edge[1];
    Require(a < mesh.vertices.size() && b < mesh.vertices.size() && a != b,
            "QUAD front references an invalid UV vertex");
    const auto key = Canonical(a, b);
    const auto use = face_edges.find(key);
    Require(use != face_edges.end() && use->second.count == 1,
            "QUAD front is not a one-owner face edge");
    Require(use->second.directed == edge,
            "QUAD boundary orientation differs from source face winding");
    Require(supplied.emplace(key, true).second,
            "QUAD boundary contains a duplicate one-owner edge");
    result.push_back({mesh.vertices[a], mesh.vertices[b]});
  }
  Require(supplied.size() == expected_boundary_edges,
          "QUAD boundary omits a one-owner face edge");
  return result;
}

struct OrientedInterval {
  double low = 0;
  double high = 0;
  int direction = 0;
};

using LineGroups = std::map<LineId, std::vector<OrientedInterval>>;

LineId AddSegment(LineGroups& groups, const UvFrontSegment& edge) {
  const auto& a = edge.first;
  const auto& b = edge.second;
  Require(std::isfinite(a.u) && std::isfinite(a.v) &&
              std::isfinite(b.u) && std::isfinite(b.v),
          "Nonfinite front endpoint");
  Require(a.u != b.u || a.v != b.v, "Degenerate zero-length front segment");
  const bool horizontal = a.v == b.v;
  const bool vertical = a.u == b.u;
  Require(horizontal != vertical, "Non-axis-aligned front segment");
  const double first = horizontal ? a.u : a.v;
  const double last = horizontal ? b.u : b.v;
  const double constant = horizontal ? a.v : a.u;
  const LineId line = {horizontal ? 0 : 1, constant == 0.0 ? 0.0 : constant};
  groups[line].push_back(
      {std::min(first, last), std::max(first, last), last > first ? 1 : -1});
  return line;
}

LineGroups Group(const std::vector<UvFrontSegment>& source) {
  Require(!source.empty(), "Front must contain at least one segment");
  LineGroups grouped;
  for (const auto& edge : source) {
    AddSegment(grouped, edge);
  }

  for (auto& [line, segments] : grouped) {
    (void)line;
    std::sort(segments.begin(), segments.end(),
              [](const OrientedInterval& a, const OrientedInterval& b) {
                if (a.low != b.low) {
                  return a.low < b.low;
                }
                return a.high < b.high;
              });
    for (std::size_t i = 1; i < segments.size(); ++i) {
      Require(segments[i - 1].high <= segments[i].low,
              "Front has overlapping or duplicate collinear segments");
    }
  }
  return grouped;
}

}  // namespace

std::vector<UvFrontSegment> SnapshotLegacyFront(
    const Par2DJMesh::AFT::Quadtree& legacy_tree) {
  Require(!legacy_tree.GetTemplateFaces().empty(),
          "Legacy tree has no published TRI templates");
  const auto& front = legacy_tree.GetFrontEdges();
  Require(!front.empty(), "Legacy Quadtree has no published AFT front");

  std::vector<UvFrontSegment> result;
  result.reserve(front.size());
  for (const auto* edge : front) {
    Require(edge != nullptr, "Legacy front has a null edge");
    Require(edge->getV1() != nullptr && edge->getV2() != nullptr,
            "Legacy front has a missing endpoint");
    Require(edge->getCell() != nullptr && edge->isInBoundary(),
            "Legacy front has no owned cell or boundary status");
    result.push_back(
        {{edge->getV1()->getX(), edge->getV1()->getY()},
         {edge->getV2()->getX(), edge->getV2()->getY()}});
  }
  return result;
}

FrontInterfaceAudit CompareLegacyAndQuadFront(
    const std::vector<UvFrontSegment>& legacy_front, const UvMesh& quad_mesh,
    const std::vector<std::array<VertexId, 2>>& quad_region_boundary) {
  const auto quad_front = QuadBoundaryGeometry(quad_mesh, quad_region_boundary);
  const auto legacy_lines = Group(legacy_front);
  const auto quad_lines = Group(quad_front);

  Require(legacy_lines.size() == quad_lines.size(),
          "Legacy and QUAD fronts have different supporting source lines");

  FrontInterfaceAudit report;
  report.legacy_segments = legacy_front.size();
  report.quad_segments = quad_front.size();

  for (const auto& [line, source] : legacy_lines) {
    const auto selected = quad_lines.find(line);
    Require(selected != quad_lines.end(),
            "QUAD front is missing a legacy supporting source line");
    const auto& split = selected->second;
    std::size_t pos = 0;

    for (const auto& legacy : source) {
      double cursor = legacy.low;
      std::size_t pieces = 0;
      report.legacy_total_length +=
          static_cast<long double>(legacy.high) - legacy.low;
      while (pos < split.size() && split[pos].low < legacy.high) {
        const auto& candidate = split[pos++];
        Require(candidate.low == cursor,
                "QUAD front has a gap or overlap in legacy edge coverage");
        Require(candidate.high <= legacy.high,
                "QUAD front spans more than one original legacy edge");
        Require(candidate.direction == -legacy.direction,
                "QUAD and legacy AFT fronts must have opposite winding");
        report.quad_total_length +=
            static_cast<long double>(candidate.high) - candidate.low;
        cursor = candidate.high;
        ++pieces;
      }
      Require(pieces > 0 && cursor == legacy.high,
              "QUAD front does not fully cover a legacy boundary edge");
      if (pieces == 1) {
        ++report.original_unsplit_segments;
      } else {
        ++report.original_split_segments;
        report.new_split_points += pieces - 1;
      }
      report.max_parts_per_legacy_segment =
          std::max(report.max_parts_per_legacy_segment, pieces);
    }
    Require(pos == split.size(),
            "QUAD front contains unowned segments beyond the legacy front");
  }

  Require(report.quad_total_length == report.legacy_total_length,
          "QUAD front total length differs from original legacy boundary");
  Require(report.original_unsplit_segments + report.original_split_segments ==
              report.legacy_segments &&
              report.quad_segments ==
                  report.legacy_segments + report.new_split_points,
          "QUAD interface segment accounting is inconsistent");
  report.opposite_winding = true;
  report.complete_coverage = true;
  return report;
}

}  // namespace apmesh::quad
