#ifndef APMESH_QUAD_RESEARCH_TYPED_MIXED_CURVATURE_H
#define APMESH_QUAD_RESEARCH_TYPED_MIXED_CURVATURE_H

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <map>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>

namespace apmesh::quad::research {

// Read-only, polygon-aware topology and barycentric angle-defect diagnostic.
// A QUAD remains a four-node element; its 0-2 diagonal is only a metric witness.
using MixedPoint3 = std::array<double, 3>;
using MixedFace = std::vector<std::size_t>;

struct MixedVertexDiagnostic {
  bool boundary = false;
  std::size_t incident_faces = 0;
  double incident_angle_sum = 0.0;
  double barycentric_area = 0.0;
  double angle_defect = 0.0;
  double angle_defect_density = 0.0;
};

struct MixedCurvatureDiagnostic {
  std::vector<MixedVertexDiagnostic> vertices;
  std::size_t triangles = 0;
  std::size_t quadrilaterals = 0;
  std::size_t boundary_edges = 0;
  std::size_t interior_vertices = 0;
  std::size_t boundary_vertices = 0;
  double total_angle_defect = 0.0;
  double min_barycentric_area = 0.0;
};

inline MixedCurvatureDiagnostic AuditMixedCurvature(
    const std::vector<MixedPoint3>& positions,
    const std::vector<MixedFace>& faces) {
  auto require = [](bool ok, const char* why) {
    if (!ok)
      throw std::invalid_argument(why);
  };
  require(!positions.empty() && !faces.empty(), "Empty mixed curvature source");
  for (const auto& p : positions)
    for (const double coord : p)
      require(std::isfinite(coord), "Nonfinite mixed curvature coordinate");

  using Edge = std::pair<std::size_t, std::size_t>;
  struct HalfEdge {
    std::size_t from = 0, to = 0;
  };
  constexpr double pi = 3.141592653589793238462643383279502884;
  std::map<Edge, std::vector<HalfEdge>> edge_incidence;
  std::vector<std::map<std::size_t, std::set<std::size_t>>> vertex_links(positions.size());
  MixedCurvatureDiagnostic result;
  result.vertices.resize(positions.size());

  auto subtract = [](const MixedPoint3& a, const MixedPoint3& b) {
    return MixedPoint3{a[0] - b[0], a[1] - b[1], a[2] - b[2]};
  };
  auto dot = [](const MixedPoint3& a, const MixedPoint3& b) {
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
  };
  auto cross = [](const MixedPoint3& a, const MixedPoint3& b) {
    return MixedPoint3{a[1]*b[2] - a[2]*b[1],
                       a[2]*b[0] - a[0]*b[2],
                       a[0]*b[1] - a[1]*b[0]};
  };
  auto norm = [&](const MixedPoint3& a) {
    return std::sqrt(dot(a, a));
  };
  auto triangle_metric = [&](std::size_t a, std::size_t b, std::size_t c) {
    const auto ab = subtract(positions.at(b), positions.at(a));
    const auto ac = subtract(positions.at(c), positions.at(a));
    const auto ba = subtract(positions.at(a), positions.at(b));
    const auto bc = subtract(positions.at(c), positions.at(b));
    const auto ca = subtract(positions.at(a), positions.at(c));
    const auto cb = subtract(positions.at(b), positions.at(c));
    const double area = 0.5 * norm(cross(ab, ac));
    require(std::isfinite(area) && area > 1e-14,
            "Collapsed physical mixed diagnostic subtriangle");
    const std::array<double, 3> lengths{norm(ab), norm(ac), norm(bc)};
    for (double length : lengths)
      require(std::isfinite(length) && length > 1e-14,
              "Invalid mixed diagnostic edge length");
    auto angle = [&](const MixedPoint3& v, const MixedPoint3& w,
                     double len_v, double len_w) {
      const double cosine = dot(v, w) / (len_v * len_w);
      require(std::isfinite(cosine), "Nonfinite mixed angle cosine");
      return std::acos(std::clamp(cosine, -1.0, 1.0));
    };
    result.vertices[a].incident_angle_sum += angle(ab, ac, lengths[0], lengths[1]);
    result.vertices[b].incident_angle_sum += angle(ba, bc, lengths[0], lengths[2]);
    result.vertices[c].incident_angle_sum += angle(ca, cb, lengths[1], lengths[2]);
    for (const auto id : {a, b, c})
      result.vertices[id].barycentric_area += area / 3.0;
  };

  for (const auto& face : faces) {
    require(face.size() == 3 || face.size() == 4,
            "Mixed metric requires exactly TRI or QUAD arity");
    std::set<std::size_t> distinct;
    for (const auto v : face) {
      require(v < positions.size() && distinct.insert(v).second,
              "Invalid or repeated mixed face vertex");
      ++result.vertices[v].incident_faces;
    }
    for (std::size_t k = 0; k < face.size(); ++k) {
      const std::size_t vertex = face[k];
      const std::size_t before = face[(k + face.size() - 1) % face.size()];
      const std::size_t after = face[(k + 1) % face.size()];
      auto& link = vertex_links[vertex];
      require(link[before].insert(after).second && link[after].insert(before).second,
              "Repeated mixed vertex-link sector");
      auto& uses = edge_incidence[std::minmax(vertex, after)];
      require(uses.size() < 2, "Nonmanifold mixed edge incidence");
      if (!uses.empty())
        require(uses.front().from == after && uses.front().to == vertex,
                "Mismatched mixed halfedge winding");
      uses.push_back({vertex, after});
    }
    triangle_metric(face[0], face[1], face[2]);
    if (face.size() == 4) {
      triangle_metric(face[0], face[2], face[3]);
      ++result.quadrilaterals;
    } else {
      ++result.triangles;
    }
  }

  for (const auto& entry : edge_incidence) {
    if (entry.second.size() != 1)
      continue;
    ++result.boundary_edges;
    result.vertices[entry.first.first].boundary = true;
    result.vertices[entry.first.second].boundary = true;
  }

  for (std::size_t v = 0; v < positions.size(); ++v) {
    auto& node = result.vertices[v];
    const auto& link = vertex_links[v];
    require(node.incident_faces > 0 && !link.empty(),
            "Unused mixed diagnostic vertex");
    std::size_t endpoints = 0;
    for (const auto& item : link) {
      require(item.second.size() >= 1 && item.second.size() <= 2,
              "Mixed vertex sector is not a 2-manifold fan");
      if (item.second.size() == 1)
        ++endpoints;
    }
    require(node.boundary ? endpoints == 2 : endpoints == 0,
            "Mixed vertex link violates boundary/interior fan topology");
    std::set<std::size_t> visited;
    std::vector<std::size_t> pending{link.begin()->first};
    while (!pending.empty()) {
      const auto current = pending.back();
      pending.pop_back();
      if (!visited.insert(current).second)
        continue;
      for (const auto neighbor : link.at(current))
        if (!visited.count(neighbor))
          pending.push_back(neighbor);
    }
    require(visited.size() == link.size(), "Disconnected mixed vertex link");
    require(std::isfinite(node.barycentric_area) && node.barycentric_area > 1e-14 &&
                std::isfinite(node.incident_angle_sum),
            "Invalid mixed vertex dual area or corner angles");
    node.angle_defect = (node.boundary ? pi : 2.0*pi) - node.incident_angle_sum;
    node.angle_defect_density = node.angle_defect / node.barycentric_area;
    require(std::isfinite(node.angle_defect) && std::isfinite(node.angle_defect_density),
            "Nonfinite mixed curvature diagnostic");
    result.total_angle_defect += node.angle_defect;
    if (v == 0)
      result.min_barycentric_area = node.barycentric_area;
    result.min_barycentric_area = std::min(result.min_barycentric_area, node.barycentric_area);
    if (node.boundary)
      ++result.boundary_vertices;
    else
      ++result.interior_vertices;
  }
  // Gauss-Bonnet for a connected oriented triangle-metric disk: total deficit 2*pi.
  // This is a metric witness, not a general curvature law for warped QUAD patches.
  require(std::abs(result.total_angle_defect - 2.0*pi) <= 1e-7,
          "Mixed patch angle-defect Gauss-Bonnet witness failed");
  return result;
}

} // namespace apmesh::quad::research
#endif // APMESH_QUAD_RESEARCH_TYPED_MIXED_CURVATURE_H
