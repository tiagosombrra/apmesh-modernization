#ifndef APMESH_RESEARCH_QUAD_UV_MESH_H
#define APMESH_RESEARCH_QUAD_UV_MESH_H

#include <array>
#include <cstddef>
#include <iosfwd>
#include <vector>

namespace apmesh::quad {

using VertexId = std::size_t;

struct UvVertex {
  double u;
  double v;
};

struct UvQuad {
  std::array<VertexId, 4> vertices;
};

struct UvMesh {
  std::vector<UvVertex> vertices;
  std::vector<UvQuad> quads;
};

struct PolygonMesh {
  std::vector<UvVertex> vertices;
  std::vector<std::vector<VertexId>> polygons;
  // One caller-selected point per polygon. No centroid policy is implied.
  std::vector<UvVertex> interior_points;
};

struct TopologySummary {
  std::size_t boundary_edges;
  std::size_t interior_edges;
  long double area;
};

// Research-only planar disk contract: finite coordinates, convex CCW faces,
// unique coordinate/ID correspondence, conforming edges and one connected disk.
// The tolerance is relative to the squared bounding-box extent. Throws
// invalid_argument on invalid geometry/topology; allocation failures propagate.
TopologySummary Validate(const UvMesh& mesh, long double expected_area,
                         long double relative_tolerance = 1.0e-12L);

// Split each polygon into one quad per original corner using canonical edge
// midpoints and the supplied interior point. Input IDs/order remain unchanged;
// new midpoint IDs follow first edge encounter, then the polygon's point ID.
// A complete local result is validated before return. Input is never mutated.
UvMesh Subdivide(const PolygonMesh& input, long double relative_tolerance = 1.0e-12L);

// OBJ uses UV as XY, Z=0 and four indices per face. No TRI writer is reused.
void WriteObj(std::ostream& output, const UvMesh& mesh);

} // namespace apmesh::quad

#endif
