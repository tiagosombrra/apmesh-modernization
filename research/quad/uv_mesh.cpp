#include "uv_mesh.h"

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <limits>
#include <locale>
#include <map>
#include <ostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <utility>

namespace apmesh::quad {
namespace {

using Edge = std::pair<VertexId, VertexId>;
using Polygons = std::vector<std::vector<VertexId>>;

Edge Canonical(VertexId a, VertexId b) { return std::minmax(a, b); }

long double Cross(const UvVertex& a, const UvVertex& b, const UvVertex& c) {
  return (static_cast<long double>(b.u) - a.u) * (static_cast<long double>(c.v) - a.v) -
         (static_cast<long double>(b.v) - a.v) * (static_cast<long double>(c.u) - a.u);
}

void Require(bool condition, const char* message) {
  if (!condition) {
    throw std::invalid_argument(message);
  }
}

long double AreaTolerance(const std::vector<UvVertex>& vertices, long double relative) {
  Require(std::isfinite(relative) && relative > 0 && relative < 1,
          "Relative tolerance must be finite and between zero and one");
  Require(!vertices.empty(), "Mesh has no vertices");
  double min_u = vertices.front().u;
  double max_u = min_u;
  double min_v = vertices.front().v;
  double max_v = min_v;
  std::set<std::pair<double, double>> coordinates;
  for (const auto& vertex : vertices) {
    Require(std::isfinite(vertex.u) && std::isfinite(vertex.v), "Non-finite UV coordinate");
    Require(coordinates.emplace(vertex.u, vertex.v).second,
            "Coincident coordinates have different vertex IDs");
    min_u = std::min(min_u, vertex.u);
    max_u = std::max(max_u, vertex.u);
    min_v = std::min(min_v, vertex.v);
    max_v = std::max(max_v, vertex.v);
  }
  const long double extent =
      std::max(static_cast<long double>(max_u) - min_u, static_cast<long double>(max_v) - min_v);
  Require(extent > 0 && std::isfinite(extent * extent), "Invalid UV coordinate extent");
  const long double tolerance = relative * extent * extent;
  Require(tolerance > 0 && std::isfinite(tolerance), "Invalid geometric tolerance");
  return tolerance;
}

bool Inside(const UvVertex& point, const std::vector<VertexId>& polygon,
            const std::vector<UvVertex>& vertices, long double tolerance) {
  for (std::size_t i = 0; i < polygon.size(); ++i) {
    if (Cross(vertices[polygon[i]], vertices[polygon[(i + 1) % polygon.size()]], point) <=
        tolerance) {
      return false;
    }
  }
  return true;
}

TopologySummary Inspect(const std::vector<UvVertex>& vertices, const Polygons& polygons,
                        long double relative) {
  const long double tolerance = AreaTolerance(vertices, relative);
  Require(!polygons.empty(), "Mesh has no faces");
  std::map<Edge, std::vector<Edge>> edges;
  std::vector<bool> used(vertices.size(), false);
  long double area = 0;
  for (const auto& polygon : polygons) {
    Require(polygon.size() >= 3, "Polygon has fewer than three vertices");
    std::set<VertexId> unique;
    for (VertexId id : polygon) {
      Require(id < vertices.size(), "Vertex ID is out of range");
      Require(unique.insert(id).second, "Face repeats a vertex ID");
      used[id] = true;
    }
    // Every other vertex must lie strictly left of every directed edge.
    // Unlike local turn tests, this also rejects self-intersecting stars.
    for (std::size_t i = 0; i < polygon.size(); ++i) {
      const auto a = polygon[i];
      const auto b = polygon[(i + 1) % polygon.size()];
      for (VertexId id : polygon) {
        if (id != a && id != b) {
          Require(Cross(vertices[a], vertices[b], vertices[id]) > tolerance,
                  "Face is inverted, degenerate or not strictly convex");
        }
      }
      edges[Canonical(a, b)].emplace_back(a, b);
    }
    const auto& origin = vertices[polygon.front()];
    for (std::size_t i = 1; i + 1 < polygon.size(); ++i) {
      area += Cross(origin, vertices[polygon[i]], vertices[polygon[i + 1]]) / 2;
    }
  }
  Require(std::all_of(used.begin(), used.end(), [](bool value) { return value; }),
          "Mesh contains an unused vertex");
  Require(std::isfinite(area) && area > tolerance, "Invalid mesh area");

  std::size_t boundary = 0;
  std::vector<std::size_t> boundary_degree(vertices.size(), 0);
  std::vector<std::vector<VertexId>> adjacency(vertices.size());
  for (const auto& [key, incidence] : edges) {
    Require(incidence.size() <= 2, "Edge has more than two incident faces");
    if (incidence.size() == 2) {
      Require(incidence[0].first == incidence[1].second &&
                  incidence[0].second == incidence[1].first,
              "Shared edge orientations disagree");
    } else {
      ++boundary;
      ++boundary_degree[key.first];
      ++boundary_degree[key.second];
    }
    adjacency[key.first].push_back(key.second);
    adjacency[key.second].push_back(key.first);
    const auto& a = vertices[key.first];
    const auto& b = vertices[key.second];
    for (VertexId id = 0; id < vertices.size(); ++id) {
      if (id == key.first || id == key.second) {
        continue;
      }
      const auto& p = vertices[id];
      const long double dot =
          (static_cast<long double>(p.u) - a.u) * (static_cast<long double>(p.u) - b.u) +
          (static_cast<long double>(p.v) - a.v) * (static_cast<long double>(p.v) - b.v);
      Require(!(std::abs(Cross(a, b, p)) <= tolerance && dot < -tolerance),
              "Vertex lies inside an unsplit edge (hanging node)");
    }
  }
  for (std::size_t degree : boundary_degree) {
    Require(degree == 0 || degree == 2, "Boundary vertex is not manifold");
  }
  for (auto first = edges.begin(); first != edges.end(); ++first) {
    auto second = first;
    for (++second; second != edges.end(); ++second) {
      const auto [a, b] = first->first;
      const auto [c, d] = second->first;
      if (a == c || a == d || b == c || b == d) {
        continue;
      }
      const long double abc = Cross(vertices[a], vertices[b], vertices[c]);
      const long double abd = Cross(vertices[a], vertices[b], vertices[d]);
      const long double cda = Cross(vertices[c], vertices[d], vertices[a]);
      const long double cdb = Cross(vertices[c], vertices[d], vertices[b]);
      const bool crosses_ab =
          (abc > tolerance && abd < -tolerance) || (abd > tolerance && abc < -tolerance);
      const bool crosses_cd =
          (cda > tolerance && cdb < -tolerance) || (cdb > tolerance && cda < -tolerance);
      Require(!(crosses_ab && crosses_cd), "Mesh edges cross");
    }
  }
  for (std::size_t i = 0; i < polygons.size(); ++i) {
    for (std::size_t j = i + 1; j < polygons.size(); ++j) {
      for (VertexId id : polygons[i]) {
        Require(!Inside(vertices[id], polygons[j], vertices, tolerance), "Faces overlap");
      }
      for (VertexId id : polygons[j]) {
        Require(!Inside(vertices[id], polygons[i], vertices, tolerance), "Faces overlap");
      }
    }
  }
  std::vector<bool> visited(vertices.size(), false);
  std::vector<VertexId> pending{0};
  visited[0] = true;
  while (!pending.empty()) {
    const auto id = pending.back();
    pending.pop_back();
    for (auto next : adjacency[id]) {
      if (!visited[next]) {
        visited[next] = true;
        pending.push_back(next);
      }
    }
  }
  Require(std::all_of(visited.begin(), visited.end(), [](bool value) { return value; }),
          "Mesh is disconnected");
  Require(vertices.size() + polygons.size() == edges.size() + 1,
          "Mesh is not a single topological disk");
  return {boundary, edges.size() - boundary, area};
}

Polygons Faces(const UvMesh& mesh) {
  Polygons result;
  result.reserve(mesh.quads.size());
  for (const auto& quad : mesh.quads) {
    result.emplace_back(quad.vertices.begin(), quad.vertices.end());
  }
  return result;
}

} // namespace

TopologySummary Validate(const UvMesh& mesh, long double expected_area,
                         long double relative_tolerance) {
  Require(std::isfinite(expected_area) && expected_area > 0, "Invalid expected domain area");
  const auto summary = Inspect(mesh.vertices, Faces(mesh), relative_tolerance);
  Require(std::abs(summary.area - expected_area) <=
              AreaTolerance(mesh.vertices, relative_tolerance),
          "Mesh area differs from expected domain area");
  return summary;
}

UvMesh Subdivide(const PolygonMesh& input, long double relative_tolerance) {
  const auto source = Inspect(input.vertices, input.polygons, relative_tolerance);
  Require(input.interior_points.size() == input.polygons.size(),
          "Exactly one interior point is required per polygon");
  const auto tolerance = AreaTolerance(input.vertices, relative_tolerance);
  for (std::size_t i = 0; i < input.polygons.size(); ++i) {
    const auto& point = input.interior_points[i];
    Require(std::isfinite(point.u) && std::isfinite(point.v), "Non-finite interior point");
    Require(Inside(point, input.polygons[i], input.vertices, tolerance),
            "Supplied point is not strictly inside its polygon");
  }
  UvMesh result{input.vertices, {}};
  std::map<Edge, VertexId> midpoints;
  for (std::size_t i = 0; i < input.polygons.size(); ++i) {
    const auto& polygon = input.polygons[i];
    std::vector<VertexId> side_points;
    side_points.reserve(polygon.size());
    for (std::size_t j = 0; j < polygon.size(); ++j) {
      const auto a = polygon[j];
      const auto b = polygon[(j + 1) % polygon.size()];
      const auto key = Canonical(a, b);
      const auto found = midpoints.find(key);
      if (found != midpoints.end()) {
        side_points.push_back(found->second);
      } else {
        const auto id = result.vertices.size();
        const auto& start = input.vertices[a];
        const auto& end = input.vertices[b];
        result.vertices.push_back({0.5 * start.u + 0.5 * end.u, 0.5 * start.v + 0.5 * end.v});
        midpoints.emplace(key, id);
        side_points.push_back(id);
      }
    }
    const auto center = result.vertices.size();
    result.vertices.push_back(input.interior_points[i]);
    for (std::size_t j = 0; j < polygon.size(); ++j) {
      result.quads.push_back({{polygon[j], side_points[j], center,
                               side_points[(j + polygon.size() - 1) % polygon.size()]}});
    }
  }
  Validate(result, source.area, relative_tolerance);
  return result;
}

void WriteObj(std::ostream& output, const UvMesh& mesh) {
  Inspect(mesh.vertices, Faces(mesh), 1.0e-12L);
  std::ostringstream encoded;
  encoded.imbue(std::locale::classic());
  encoded << std::setprecision(std::numeric_limits<double>::max_digits10);
  for (const auto& vertex : mesh.vertices) {
    encoded << "v " << vertex.u << ' ' << vertex.v << " 0\n";
  }
  for (const auto& quad : mesh.quads) {
    encoded << 'f';
    for (auto id : quad.vertices) {
      encoded << ' ' << id + 1;
    }
    encoded << '\n';
  }
  if (!encoded) {
    throw std::runtime_error("Failed to encode QUAD OBJ");
  }
  const auto text = encoded.str();
  if (text.size() > static_cast<std::size_t>(std::numeric_limits<std::streamsize>::max())) {
    throw std::length_error("QUAD OBJ exceeds stream size limit");
  }
  output.write(text.data(), static_cast<std::streamsize>(text.size()));
  if (!output) {
    throw std::runtime_error("Failed to write QUAD OBJ");
  }
}

} // namespace apmesh::quad
