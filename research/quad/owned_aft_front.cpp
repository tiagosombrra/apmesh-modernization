#include "owned_aft_front.h"

#include "crab_mesh/aft/quadtree_cell.h"

#include <algorithm>
#include <cmath>
#include <iterator>
#include <list>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <utility>
#include <vector>

namespace apmesh::quad {
namespace {

using Par2DJMesh::AFT::QUAD_B;
using Par2DJMesh::AFT::QUAD_L;
using Par2DJMesh::AFT::QUAD_R;
using Par2DJMesh::AFT::QUAD_T;
using Par2DJMesh::AFT::QuadtreeCell;
using Par2DJMesh::Basics::Edge;
using Par2DJMesh::Basics::Vertex;
using EdgeKey = std::pair<VertexId, VertexId>;

void Require(bool accepted, const char* reason) {
  if (!accepted) {
    throw std::invalid_argument(reason);
  }
}

EdgeKey Key(VertexId first, VertexId second) { return std::minmax(first, second); }

// Edge::~Edge deletes its endpoints. The owner lists must delete edges before
// vertices; uncommitted RAII edges must always detach borrowed endpoints.
struct PendingEdgeDelete {
  void operator()(Edge* edge) const noexcept {
    if (edge != nullptr) {
      edge->DetachVertices();
      delete edge;
    }
  }
};
using PendingEdge = std::unique_ptr<Edge, PendingEdgeDelete>;

struct FaceIncidence {
  std::size_t count = 0;
  std::size_t origin = 0;
  std::array<VertexId, 2> direction{};
};

struct PlannedEdge {
  VertexId first = 0;
  VertexId second = 0;
  QuadtreeCell* exterior = nullptr;
};

std::vector<PlannedEdge> ValidateAndPlan(Par2DJMesh::AFT::Quadtree& tree,
                                         const InteriorTemplateSelection& selected) {
  Require(selected.mode == InteriorTemplateMode::ExperimentalQuad &&
              selected.legacy_tri_faces == 0 && !selected.live_aft_interface_published &&
              !selected.physical_elements_published,
          "R2b requires a research-only, unpublished QUAD template selection");
  Require(tree.GetTemplateFaces().empty() && tree.GetTemplateEdges().empty() &&
              tree.GetTemplateVertices().empty() && tree.GetFrontEdges().empty(),
          "R2b cannot seed QUAD over already-published TRI template owners");

  const auto leaves = tree.getLeaves();
  Require(selected.source_leaves == leaves.size() &&
              selected.uv_quads.quads.size() == selected.quad_face_origins.size(),
          "QUAD face provenance does not match this source Quadtree");

  std::map<EdgeKey, FaceIncidence> owners;
  for (std::size_t i = 0; i < selected.uv_quads.quads.size(); ++i) {
    const auto& quad = selected.uv_quads.quads[i];
    for (std::size_t n = 0; n < quad.vertices.size(); ++n) {
      const auto a = quad.vertices[n];
      const auto b = quad.vertices[(n + 1) % quad.vertices.size()];
      Require(a < selected.uv_quads.vertices.size() && b < selected.uv_quads.vertices.size() &&
                  a != b,
              "R2b has invalid QUAD face vertex incidence");
      auto& incidence = owners[Key(a, b)];
      Require(incidence.count < 2, "R2b cannot handle nonmanifold QUAD edge");
      if (incidence.count == 1) {
        Require(incidence.direction[0] == b && incidence.direction[1] == a,
                "R2b has inconsistent shared QUAD edge winding");
      }
      if (incidence.count++ == 0) {
        incidence.origin = i;
        incidence.direction = {a, b};
      }
    }
  }

  std::size_t boundaryCount = 0;
  for (const auto& [edge, incidence] : owners) {
    (void)edge;
    if (incidence.count == 1) {
      ++boundaryCount;
    }
  }
  Require(!selected.quad_region_boundary.empty() &&
              boundaryCount == selected.quad_region_boundary.size(),
          "R2b needs each and every one-owner QUAD interface edge");

  std::set<EdgeKey> unique;
  std::vector<PlannedEdge> planned;
  planned.reserve(selected.quad_region_boundary.size());
  for (const auto& directed : selected.quad_region_boundary) {
    const auto a = directed[0];
    const auto b = directed[1];
    Require(a < selected.uv_quads.vertices.size() && b < selected.uv_quads.vertices.size() &&
                a != b,
            "R2b QUAD interface references an invalid UV vertex");
    const auto edge = Key(a, b);
    const auto face = owners.find(edge);
    Require(face != owners.end() && face->second.count == 1 && face->second.direction == directed &&
                unique.insert(edge).second,
            "R2b QUAD interface has duplicate, omitted or reversed face edges");
    const auto& origin = selected.quad_face_origins.at(face->second.origin);
    Require(origin.leaf_ordinal < leaves.size(), "R2b QUAD origin references a foreign leaf");
    auto* source = *std::next(leaves.begin(), static_cast<std::ptrdiff_t>(origin.leaf_ordinal));
    Require(source != nullptr && source->getId() == origin.cell_id &&
                static_cast<unsigned>(source->getLevel()) == origin.relative_depth &&
                !source->inBoundary(),
            "R2b QUAD source leaf identity/depth is stale");

    const auto& p = selected.uv_quads.vertices[a];
    const auto& q = selected.uv_quads.vertices[b];
    Require(std::isfinite(p.u) && std::isfinite(p.v) && std::isfinite(q.u) && std::isfinite(q.v),
            "R2b interface has nonfinite UV vertices");

    const double cx = 0.5 * (p.u + q.u);
    const double cy = 0.5 * (p.v + q.v);
    auto* low = source->getMin();
    auto* high = source->getMax();
    Require(low != nullptr && high != nullptr, "R2b source cell has no box");
    const bool horizontal = p.v == q.v;
    const bool vertical = p.u == q.u;
    Require(horizontal != vertical, "R2b interface is not an axis-aligned cell edge");
    int side = -1;
    if (horizontal && p.v == low->getY()) {
      side = QUAD_B;
    } else if (vertical && p.u == high->getX()) {
      side = QUAD_R;
    } else if (horizontal && p.v == high->getY()) {
      side = QUAD_T;
    } else if (vertical && p.u == low->getX()) {
      side = QUAD_L;
    }
    Require(side != -1 && cx >= low->getX() && cx <= high->getX() && cy >= low->getY() &&
                cy <= high->getY(),
            "R2b interface does not lie on its source Quadtree leaf boundary");

    // AFT's ideal point height must use the exterior, currently unmeshed cell,
    // rather than the already filled QUAD source cell.
    QuadtreeCell* exterior = nullptr;
    for (auto* neighbor : source->getNeighbors(side)) {
      if (neighbor == nullptr || !neighbor->inBoundary()) {
        continue;
      }
      auto* nmin = neighbor->getMin();
      auto* nmax = neighbor->getMax();
      Require(nmin && nmax, "R2b exterior Quadtree cell has no bounds");
      if (cx >= nmin->getX() && cx <= nmax->getX() && cy >= nmin->getY() && cy <= nmax->getY()) {
        Require(exterior == nullptr, "R2b interface has ambiguous exterior cell ownership");
        exterior = neighbor;
      }
    }
    Require(exterior != nullptr && exterior != source,
            "R2b QUAD front does not have a valid exterior cell observer");
    // Reverse the face CCW direction only at the exterior AFT boundary.
    planned.push_back({b, a, exterior});
  }
  Require(unique.size() == boundaryCount,
          "R2b QUAD interface has incomplete one-owner face coverage");
  return planned;
}

} // namespace

OwnedQuadAftFront::OwnedQuadAftFront(Par2DJMesh::AFT::Boundary* boundary,
                                     Par2DJMesh::AFT::Quadtree* tree)
    : AdvancingFront(boundary, tree, 1.0e-8, 0U) {}

OwnedAftFrontReport OwnedQuadAftFront::Seed(const InteriorTemplateSelection& selected,
                                            const std::vector<UvFrontSegment>& original_tri_front) {
  Require(!seeded_ && front.empty() && vertices.empty() && innerVertices.empty() &&
              innerEdges.empty() && edges.empty() && mesh.empty() && seam_edges_.empty() &&
              seam_vertices_.empty(),
          "R2b front was already initialized or has prior accepted content");
  Require(quadtree != nullptr && boundary != nullptr && quadtree->getBoundary() == boundary,
          "R2b requires an AFT-owned Quadtree and its original boundary");
  const auto verified = CompareLegacyAndQuadFront(original_tri_front, selected.uv_quads,
                                                  selected.quad_region_boundary);
  Require(verified.complete_coverage && verified.opposite_winding,
          "R2b input failed the independent R2a coverage and orientation gate");
  const auto planned = ValidateAndPlan(*quadtree, selected);

  // Build complete RAII graph and all duplicate observer-list nodes BEFORE
  // committing any new AFT-owned objects. No production tree is mutated here.
  std::map<VertexId, std::unique_ptr<Vertex>> pending_vertices;
  for (const auto& plan : planned) {
    for (VertexId id : {plan.first, plan.second}) {
      if (pending_vertices.count(id) != 0) {
        continue;
      }
      const auto& uv = selected.uv_quads.vertices.at(id);
      pending_vertices.emplace(id, std::make_unique<Vertex>(uv.u, uv.v));
    }
  }

  std::vector<PendingEdge> pending_edges;
  pending_edges.reserve(planned.size());
  std::list<Vertex*> owned_vertices;
  std::list<Vertex*> vertex_observers;
  std::list<Edge*> owned_edges;
  std::list<Edge*> edge_observers;
  std::list<Edge*> active_edges;
  // Stage the research seam identity separately from AFT's growing owner lists.
  // Both vectors are complete before the first AFT publication.
  std::vector<Vertex*> staged_seam_vertices;
  std::vector<Edge*> staged_seam_edges;
  staged_seam_vertices.reserve(pending_vertices.size());
  staged_seam_edges.reserve(planned.size());

  for (auto& [id, value] : pending_vertices) {
    (void)id;
    owned_vertices.push_back(value.get());
    vertex_observers.push_back(value.get());
    staged_seam_vertices.push_back(value.get());
  }
  for (const auto& plan : planned) {
    auto* first = pending_vertices.at(plan.first).get();
    auto* second = pending_vertices.at(plan.second).get();
    PendingEdge edge(new Edge(first, second));
    edge->setCell(plan.exterior);
    edge->setInBoundary(true);
    edge->setFree(true);
    // Match the original AFT adjacency contract before exposing the front.
    first->addAdjacentEdge(edge.get());
    second->addAdjacentEdge(edge.get());
    owned_edges.push_back(edge.get());
    edge_observers.push_back(edge.get());
    active_edges.push_back(edge.get());
    staged_seam_edges.push_back(edge.get());
    pending_edges.push_back(std::move(edge));
  }

  // Original makeInitialFront adds the untouched patch boundary only: no TRI
  // templates were published into this Quadtree by the QUAD selector.
  makeInitialFront();
  Require(front.size() == boundary->getEdges().size() && quadtree->GetFrontEdges().empty(),
          "R2b failed to create an uncontaminated original AFT boundary");

  lastVertexId = std::max(lastVertexId, boundary->getLastVertexId());
  lastEdgeId = std::max(lastEdgeId, boundary->getLastEdgeId());
  for (auto& [id, value] : pending_vertices) {
    (void)id;
    value->setId(++lastVertexId);
  }
  for (auto& value : pending_edges) {
    value->setId(++lastEdgeId);
  }

  OwnedAftFrontReport report;
  report.patch_boundary_edges = front.size();
  report.quad_interface_edges = planned.size();
  report.distinct_quad_front_vertices = pending_vertices.size();
  std::set<QuadtreeCell*> exterior_cells;
  for (const auto& plan : planned) {
    exterior_cells.insert(plan.exterior);
  }
  report.attached_exterior_cells = exterior_cells.size();
  report.total_active_front_edges = report.patch_boundary_edges + report.quad_interface_edges;

  // All five std::list::splice operations are nonallocating with the same
  // default allocator. The AFT destructor owns and cleans edges before nodes.
  front.splice(front.end(), active_edges);
  vertices.splice(vertices.end(), vertex_observers);
  edges.splice(edges.end(), edge_observers);
  innerVertices.splice(innerVertices.end(), owned_vertices);
  innerEdges.splice(innerEdges.end(), owned_edges);
  seam_edges_.swap(staged_seam_edges);
  seam_vertices_.swap(staged_seam_vertices);
  for (auto& edge : pending_edges) {
    edge.release();
  }
  for (auto& [id, vertex] : pending_vertices) {
    (void)id;
    vertex.release();
  }
  seeded_ = true;
  return report;
}

void OwnedQuadAftFront::SetResearchAbortAfterTriangles(std::size_t n) {
  Require(seeded_ && !exterior_attempted_ && n > 0 && mesh.empty(),
          "R2b2 fault hook requires a new seeded AFT before TRI emission");
  research_abort_after_triangles_ = n;
  research_abort_enabled_ = true;
}

bool OwnedQuadAftFront::findBestVertex(Edge* edge, Vertex*& best, bool geometry_phase) {
  if (research_abort_enabled_ && mesh.size() >= research_abort_after_triangles_) {
    throw std::runtime_error("R2b2 injected research-only failure after partial exterior TRI");
  }
  return AdvancingFront::findBestVertex(edge, best, geometry_phase);
}

namespace {

double SignedTwiceArea(const std::vector<UvVertex>& points) {
  double twice = 0.0;
  for (std::size_t i = 0; i < points.size(); ++i) {
    const auto& a = points[i];
    const auto& b = points[(i + 1) % points.size()];
    twice += a.u * b.v - b.u * a.v;
  }
  return twice;
}

double TriangleTwiceArea(Par2DJMesh::Basics::Face* face) {
  auto* a = face->getV1();
  auto* b = face->getV2();
  auto* c = face->getV3();
  return (b->getX() - a->getX()) * (c->getY() - a->getY()) -
         (b->getY() - a->getY()) * (c->getX() - a->getX());
}

} // namespace

namespace {
using UvPolygon = std::vector<UvVertex>;
long double CrossUv(const UvVertex& a, const UvVertex& b, const UvVertex& c) {
  return (static_cast<long double>(b.u) - a.u) * (static_cast<long double>(c.v) - a.v) -
         (static_cast<long double>(b.v) - a.v) * (static_cast<long double>(c.u) - a.u);
}
void CheckConvex(const UvPolygon& p) {
  Require(p.size() >= 3 && SignedTwiceArea(p) > 0.0,
          "R2b2 overlap audit requires positive-area CCW polygon");
  for (std::size_t i = 0; i < p.size(); ++i) {
    const auto& a = p[i];
    const auto& b = p[(i + 1) % p.size()];
    const auto& c = p[(i + 2) % p.size()];
    Require(std::isfinite(a.u) && std::isfinite(a.v) && CrossUv(a, b, c) >= 0.0L,
            "R2b2 overlap audit requires finite convex faces");
  }
}
double IntersectionArea(UvPolygon subject, const UvPolygon& clip) {
  for (std::size_t i = 0; i < clip.size() && !subject.empty(); ++i) {
    const auto& a = clip[i];
    const auto& b = clip[(i + 1) % clip.size()];
    UvPolygon next;
    next.reserve(subject.size() * 2);
    auto previous = subject.back();
    auto prev_distance = CrossUv(a, b, previous);
    for (const auto& current : subject) {
      const auto cur_distance = CrossUv(a, b, current);
      const bool prev_in = prev_distance >= 0.0L;
      const bool cur_in = cur_distance >= 0.0L;
      if (prev_in != cur_in) {
        const long double t = prev_distance / (prev_distance - cur_distance);
        next.push_back({static_cast<double>(previous.u + t * (current.u - previous.u)),
                        static_cast<double>(previous.v + t * (current.v - previous.v))});
      }
      if (cur_in)
        next.push_back(current);
      previous = current;
      prev_distance = cur_distance;
    }
    subject.swap(next);
  }
  if (subject.size() < 3)
    return 0.0;
  return std::max(0.0, 0.5 * SignedTwiceArea(subject));
}
} // namespace

UvOverlapReport AuditUvOverlap(const UvMesh& quads,
                               const std::vector<std::array<UvVertex, 3>>& triangles) {
  std::vector<UvPolygon> quad_faces;
  quad_faces.reserve(quads.quads.size());
  for (const auto& q : quads.quads) {
    UvPolygon face;
    for (auto id : q.vertices) {
      Require(id < quads.vertices.size(), "R2b2 QUAD overlap index out of range");
      face.push_back(quads.vertices[id]);
    }
    CheckConvex(face);
    quad_faces.push_back(std::move(face));
  }
  std::vector<UvPolygon> tri_faces;
  tri_faces.reserve(triangles.size());
  for (const auto& t : triangles) {
    UvPolygon face(t.begin(), t.end());
    CheckConvex(face);
    tri_faces.push_back(std::move(face));
  }
  UvOverlapReport result;
  // The research fixture uses dyadic UV inputs. Intersections smaller than
  // 1e-11 square UV units are treated as numeric boundary contact.
  constexpr double positive_overlap_epsilon = 1.0e-11;
  for (const auto& t : tri_faces) {
    for (const auto& q : quad_faces) {
      const double overlap = IntersectionArea(t, q);
      if (overlap > positive_overlap_epsilon) {
        ++result.tri_quad_pairs;
        result.overlap_area += overlap;
      }
    }
  }
  for (std::size_t i = 0; i < tri_faces.size(); ++i) {
    for (std::size_t j = i + 1; j < tri_faces.size(); ++j) {
      const double overlap = IntersectionArea(tri_faces[i], tri_faces[j]);
      if (overlap > positive_overlap_epsilon) {
        ++result.tri_tri_pairs;
        result.overlap_area += overlap;
      }
    }
  }
  result.no_overlap = result.tri_quad_pairs == 0 && result.tri_tri_pairs == 0;
  return result;
}

ExteriorAftReport
OwnedQuadAftFront::AttemptExteriorTriangulation(const InteriorTemplateSelection& selected) {
  Require(seeded_ && !exterior_attempted_ && mesh.empty(),
          "R2b2 requires an unused, successfully seeded AFT instance");
  Require(selected.mode == InteriorTemplateMode::ExperimentalQuad &&
              selected.quad_region_boundary.size() == seam_edges_.size() &&
              quadtree->GetTemplateFaces().empty(),
          "R2b2 source changed or contains overlapping legacy TRI templates");

  // Normal execution associates cells during Quadtree::generate. The synthetic
  // test fixture explicitly registers these cells before calling this method.
  for (auto* e : boundary->getEdges()) {
    Require(e != nullptr && e->getCell() != nullptr && e->getV1() != nullptr &&
                e->getV2() != nullptr,
            "R2b2 requires source-boundary edges with live cell observers");
  }
  std::map<Vertex*, std::pair<double, double>> saved_uv;
  for (auto* v : seam_vertices_) {
    Require(v != nullptr, "R2b2 has a null owned seam vertex");
    saved_uv.emplace(v, std::make_pair(v->getX(), v->getY()));
  }
  std::vector<UvVertex> polygon;
  for (auto* v : boundary->getBoundary()) {
    Require(v != nullptr, "R2b2 has a null patch boundary vertex");
    polygon.push_back({v->getX(), v->getY()});
  }
  Require(polygon.size() >= 3, "R2b2 needs a real closed UV patch boundary");

  ExteriorAftReport report;
  report.boundary_uv_area = 0.5 * SignedTwiceArea(polygon);
  Require(report.boundary_uv_area > 0.0,
          "R2b2 requires a positively oriented source patch contour");
  for (const auto& face : selected.uv_quads.quads) {
    std::vector<UvVertex> points;
    for (auto id : face.vertices) {
      Require(id < selected.uv_quads.vertices.size(),
              "R2b2 QUAD source face has a foreign UV vertex");
      points.push_back(selected.uv_quads.vertices[id]);
    }
    Require(points.size() == 4, "R2b2 requires four-node interior QUAD faces");
    const double area = 0.5 * SignedTwiceArea(points);
    Require(std::isfinite(area) && area > 0.0, "R2b2 QUAD interior face has invalid signed area");
    report.quad_uv_area += area;
  }

  // After this point the original AFT can mutate partial faces/fronts.
  // A rejected/unfinished attempt must be discarded with its AFT owner; it
  // must never be presented as an accepted mesh or reused on the same owner.
  exterior_attempted_ = true;
  const auto geometric = makeGeometryBasedMesh();
  report.geometry_done = (geometric == Par2DJMesh::AFT::ADVF_GEOMETRY_MESH_DONE);
  if (geometric == Par2DJMesh::AFT::ADVF_GEOMETRY_EDGE_REJECTED_TWICE) {
    report.topology_attempted = true;
    report.topology_done = (makeTopologyBasedMesh() == Par2DJMesh::AFT::ADVF_TOPOLOGY_MESH_DONE);
  }
  report.exterior_triangles = mesh.size();
  report.unresolved_front_edges = front.size();
  report.unresolved_rejected_edges = rejected.size();
  report.front_drained = front.empty() && rejected.empty();

  report.triangles_positive = !mesh.empty();
  for (auto* face : mesh) {
    const double twice = TriangleTwiceArea(face);
    if (!std::isfinite(twice) || twice <= 1.0e-12) {
      report.triangles_positive = false;
    }
    report.triangle_uv_area += 0.5 * twice;
  }
  for (auto* edge : seam_edges_) {
    std::size_t count = 0;
    for (auto* face : mesh) {
      const std::array<std::pair<Vertex*, Vertex*>, 3> oriented{{{face->getV1(), face->getV2()},
                                                                 {face->getV2(), face->getV3()},
                                                                 {face->getV3(), face->getV1()}}};
      for (const auto& side : oriented) {
        if (side.first == edge->getV1() && side.second == edge->getV2()) {
          ++count;
        }
      }
    }
    if (count == 1)
      ++report.seam_edges_with_one_tri;
  }
  report.seam_orientation_complete = report.seam_edges_with_one_tri == seam_edges_.size();
  report.seam_vertices_unchanged = true;
  for (const auto& [v, position] : saved_uv) {
    if (v->getX() != position.first || v->getY() != position.second) {
      report.seam_vertices_unchanged = false;
    }
  }
  report.uv_area_balanced =
      std::fabs(report.quad_uv_area + report.triangle_uv_area - report.boundary_uv_area) <=
      1.0e-8 * std::max(1.0, report.boundary_uv_area);

  // Independent pairwise positive-area clipping audit, separate from area sum.
  std::vector<std::array<UvVertex, 3>> triangles_uv;
  triangles_uv.reserve(mesh.size());
  for (auto* f : mesh) {
    auto* a = f->getV1();
    auto* b = f->getV2();
    auto* c = f->getV3();
    triangles_uv.push_back(
        {{{a->getX(), a->getY()}, {b->getX(), b->getY()}, {c->getX(), c->getY()}}});
  }
  const auto overlap = AuditUvOverlap(selected.uv_quads, triangles_uv);
  report.spatial_overlap_tested = true;
  report.no_spatial_overlap = overlap.no_overlap;
  report.overlapping_tri_quad_pairs = overlap.tri_quad_pairs;
  report.overlapping_tri_tri_pairs = overlap.tri_tri_pairs;
  report.cumulative_overlap_area = overlap.overlap_area;
  // No physical Bézier XYZ or mixed-element SubMesh is published here.
  report.qualified = false;
  return report;
}

} // namespace apmesh::quad
