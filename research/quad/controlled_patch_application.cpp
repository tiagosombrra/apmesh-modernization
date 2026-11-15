#include "controlled_patch_application.h"
#include "application/runtime_config.h"
#include "physical_quadrilateral_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "data/triangle_adaptive.h"
#include <functional>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <locale>
#include <set>
#include <sstream>
#include <tuple>
#include "owned_aft_front.h"
#include "interior_template_dispatch.h"
#include "front_interface_audit.h"
#include "typed_mixed_curvature.h"
#include "typed_mixed_quality.h"
#include "mixed_surface_residual.h"

#include "crab_mesh/aft/boundary.h"
#include "crab_mesh/aft/quadtree.h"
#include "crab_mesh/aft/quadtree_cell.h"
#include "data/curve/curve_adaptive_parametric.h"
#include "data/geometry.h"
#include "data/patch/patch_bezier.h"
#include "input_output/models_3d.h"
#include "input_output/patch_reader.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <iterator>
#include <map>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace apmesh::quad {
namespace {
using apmesh::quad::InteriorTemplateDispatcher;
using apmesh::quad::InteriorTemplateMode;
using apmesh::quad::OwnedQuadAftFront;
using apmesh::quad::SnapshotLegacyFront;
using apmesh::quad::UvVertex;
using Par2DJMesh::AFT::Boundary;
using Par2DJMesh::AFT::Quadtree;
using Par2DJMesh::AFT::QuadtreeCell;
using Par2DJMesh::Basics::Face;
using Par2DJMesh::Basics::Vertex;
using Xyz = std::array<double, 3>;

void Require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}
Xyz Values(const PointAdaptive& value) { return {value.GetX(), value.GetY(), value.GetZ()}; }
Xyz Values(const VectorAdaptive& value) { return {value.GetX(), value.GetY(), value.GetZ()}; }
Xyz Difference(const Xyz& a, const Xyz& b) { return {a[0] - b[0], a[1] - b[1], a[2] - b[2]}; }
Xyz Cross(const Xyz& a, const Xyz& b) {
  return {a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]};
}
double Dot(const Xyz& a, const Xyz& b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
double Norm(const Xyz& a) { return std::sqrt(Dot(a, a)); }
bool Finite(const Xyz& a) {
  return std::isfinite(a[0]) && std::isfinite(a[1]) && std::isfinite(a[2]);
}

std::unique_ptr<Quadtree> MakeSourceTree(bool refined) {
  auto tree = std::make_unique<Quadtree>();
  auto boundary = std::make_unique<Boundary>();
  // Each chart sample is one of the oriented four original Bezier sides.
  // This is a fixed 16-segment sampling policy, NOT Adapter::AdaptCurve.
  for (int side = 0; side < 4; ++side) {
    for (int step = 0; step < 4; ++step) {
      const double t = 0.25 * static_cast<double>(step);
      const UvVertex uv = side == 0   ? UvVertex{t, 0.0}
                          : side == 1 ? UvVertex{1.0, t}
                          : side == 2 ? UvVertex{1.0 - t, 1.0}
                                      : UvVertex{0.0, 1.0 - t};
      boundary->addVertex(uv.u, uv.v, nullptr);
    }
  }
  Require(boundary->close(nullptr), "R2b2 source UV boundary could not close");
  tree->setBoundary(boundary.release());
  auto low = std::make_unique<Vertex>(0.0, 0.0);
  auto high = std::make_unique<Vertex>(1.0, 1.0);
  auto root = std::make_unique<QuadtreeCell>(tree->getCellId(), tree.get(), low.get(), high.get());
  tree->setRoot(root.get());
  root.release();
  low.release();
  high.release();
  tree->getRoot()->subdivideToLevel(2);
  if (refined) {
    bool found = false;
    for (auto* cell : tree->getLeaves()) {
      if (cell->getMin()->getX() == 0.25 && cell->getMin()->getY() == 0.25) {
        cell->subdivideToLevel(3);
        found = true;
        break;
      }
    }
    Require(found, "R2b2 did not locate the native refined cell");
  }
  return tree;
}

UvVertex PointRule(const apmesh::quad::LeafPolygonOrigin&, const std::vector<UvVertex>& polygon) {
  UvVertex center{0.0, 0.0};
  for (const auto& vertex : polygon) {
    center.u += vertex.u;
    center.v += vertex.v;
  }
  center.u /= static_cast<double>(polygon.size());
  center.v /= static_cast<double>(polygon.size());
  return center;
}

Xyz Evaluate(PatchBezier& patch, UvVertex uv) {
  Require(std::isfinite(uv.u) && std::isfinite(uv.v) && uv.u >= 0.0 && uv.u <= 1.0 && uv.v >= 0.0 &&
              uv.v <= 1.0,
          "R2b2 source patch UV is out of the real Bezier chart");
  const Xyz xyz = Values(patch.Parameterize(uv.u, uv.v));
  const Xyz qu = Values(patch.Qu(uv.u, uv.v));
  const Xyz qv = Values(patch.Qv(uv.u, uv.v));
  Require(Finite(xyz) && Finite(qu) && Finite(qv) && Norm(Cross(qu, qv)) > 1e-12,
          "R2b2 actual Bezier XYZ or differential Jacobian is degenerate");
  return xyz;
}

void ValidateSourceCurves(PatchBezier& patch) {
  // Oriented patch controls and the source CurveAdaptiveParametric instances
  // must map the same geometric sites along all four original patch sides.
  for (unsigned side = 0; side < 4; ++side) {
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(patch.GetCurve(side));
    Require(curve != nullptr, "R2b2 physical source curve is not parametric");
    for (unsigned n = 0; n <= 4; ++n) {
      const double t = static_cast<double>(n) / 4.0;
      const UvVertex uv = side == 0   ? UvVertex{t, 0.0}
                          : side == 1 ? UvVertex{1.0, t}
                          : side == 2 ? UvVertex{t, 1.0}
                                      : UvVertex{0.0, t};
      const double curve_t = patch.IsCurveReversed(side) ? 1.0 - t : t;
      const Xyz on_patch = Evaluate(patch, uv);
      const Xyz on_curve = Values(curve->FindPointByParameter(curve_t));
      const double scale = std::max(1.0, Norm(on_patch));
      Require(Finite(on_curve) && Norm(Difference(on_patch, on_curve)) <= 2e-7 * scale,
              "R2b2 source Bezier physical curve/patch boundary mismatch");
    }
  }
}

struct FaceUv {
  std::array<UvVertex, 3> triangle;
};

void CheckFacet(PatchBezier& patch, const FaceUv& face, double& smallest_alignment) {
  const UvVertex middle{(face.triangle[0].u + face.triangle[1].u + face.triangle[2].u) / 3.0,
                        (face.triangle[0].v + face.triangle[1].v + face.triangle[2].v) / 3.0};
  const Xyz a = Evaluate(patch, face.triangle[0]);
  const Xyz b = Evaluate(patch, face.triangle[1]);
  const Xyz c = Evaluate(patch, face.triangle[2]);
  const Xyz du = Values(patch.Qu(middle.u, middle.v));
  const Xyz dv = Values(patch.Qv(middle.u, middle.v));
  const Xyz reference = Cross(du, dv);
  const Xyz facet = Cross(Difference(b, a), Difference(c, a));
  const double denom = Norm(reference) * Norm(facet);
  Require(std::isfinite(denom) && denom > 1e-14,
          "R2b2 physical mapped face has near-zero projected area");
  const double alignment = Dot(reference, facet) / denom;
  Require(std::isfinite(alignment) && alignment > 0.0,
          "R2b2 mapped Bezier TRI/QUAD facet is inverted");
  smallest_alignment = std::min(smallest_alignment, alignment);
}

struct Candidate {
  std::unique_ptr<SubMesh> mesh = std::make_unique<SubMesh>();
  std::vector<UvVertex> uv;
  std::vector<std::vector<std::size_t>> faces;
  std::vector<LeafPolygonOrigin> quad_origins;
  std::size_t quads = 0;
  double min_alignment = 1.0;
  double min_quality = 1.0;
};

struct PublicationFailure : std::runtime_error {
  using std::runtime_error::runtime_error;
};

using ResearchSourceTreeFactory = std::function<std::unique_ptr<Quadtree>()>;

Candidate Generate(PatchBezier& patch, bool fail_before_commit,
                   const ResearchSourceTreeFactory& source_tree_factory = {}) {
  ValidateSourceCurves(patch);
  auto original = source_tree_factory ? source_tree_factory() : MakeSourceTree(true);
  Require(original->makeTemplateBasedMesh() == Par2DJMesh::AFT::QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
          "Original interior TRI reference failed");
  const auto front = SnapshotLegacyFront(*original);
  auto tree = source_tree_factory ? source_tree_factory() : MakeSourceTree(true);
  InteriorTemplateDispatcher dispatch(*tree);
  const auto selected = dispatch.Select(InteriorTemplateMode::ExperimentalQuad, PointRule);
  auto* raw = tree.get();
  auto aft = std::make_unique<OwnedQuadAftFront>(raw->getBoundary(), raw);
  tree.release();
  const auto seeded = aft->Seed(selected, front);
  for (auto* edge : aft->getBoundary()->getEdges())
    aft->getQuadtree()->findCell(edge);
  const auto report = aft->AttemptExteriorTriangulation(selected);
  Require(report.front_drained && report.triangles_positive && report.seam_orientation_complete &&
              report.seam_vertices_unchanged && report.uv_area_balanced &&
              report.spatial_overlap_tested && report.no_spatial_overlap &&
              report.exterior_triangles > 0,
          "Original AFT failed complete nonoverlapping UV coverage");
  Candidate result;
  std::map<std::pair<double, double>, std::size_t> uv_ids;
  const auto add_node = [&](UvVertex uv) {
    const auto xyz = Evaluate(patch, uv);
    const auto id = result.uv.size();
    Require(uv_ids.emplace(std::make_pair(uv.u, uv.v), id).second,
            "Unpaired coincident UV nodes in controlled chart");
    auto node = std::make_unique<NodeAdaptive>(xyz[0], xyz[1], xyz[2]);
    node->SetId(static_cast<unsigned long>(id + 1));
    result.mesh->AddNoh(std::move(node));
    result.uv.push_back(uv);
    return id;
  };
  for (const auto& uv : selected.uv_quads.vertices)
    add_node(uv);
  for (const auto& quad : selected.uv_quads.quads)
    result.faces.emplace_back(quad.vertices.begin(), quad.vertices.end());
  result.quads = result.faces.size();
  result.quad_origins = selected.quad_face_origins;
  Require(result.quad_origins.size() == result.quads,
          "Mixed residual leaf provenance differs from the real native tree");
  std::map<Vertex*, std::size_t> aft_ids;
  // Only the already-audited seam may bridge source pointer identities to QUAD IDs.
  for (auto* v : aft->OwnedSeamVertices())
    aft_ids.emplace(v, uv_ids.at({v->getX(), v->getY()}));
  Require(aft_ids.size() == seeded.distinct_quad_front_vertices,
          "Incomplete canonical QUAD/AFT seam");
  for (auto* face : aft->Triangles()) {
    std::vector<std::size_t> ids;
    for (auto* v : {face->getV1(), face->getV2(), face->getV3()}) {
      auto it = aft_ids.find(v);
      if (it == aft_ids.end())
        it = aft_ids.emplace(v, add_node({v->getX(), v->getY()})).first;
      ids.push_back(it->second);
    }
    result.faces.push_back(std::move(ids));
  }
  struct Incidence {
    unsigned count = 0;
    std::size_t a = 0, b = 0, face = 0;
  };
  std::map<std::pair<std::size_t, std::size_t>, Incidence> edges;
  std::vector<std::vector<std::size_t>> adjacency(result.faces.size());
  unsigned boundary_edges = 0;
  for (std::size_t i = 0; i < result.faces.size(); ++i) {
    const auto& ids = result.faces[i];
    for (std::size_t k = 0; k < ids.size(); ++k) {
      const auto a = ids[k], b = ids[(k + 1) % ids.size()];
      auto& edge = edges[std::minmax(a, b)];
      Require(edge.count < 2 && a != b, "Nonmanifold or collapsed mixed edge");
      if (edge.count == 1) {
        Require(edge.a == b && edge.b == a, "Mixed edge winding mismatch");
        adjacency[i].push_back(edge.face);
        adjacency[edge.face].push_back(i);
      } else {
        edge.a = a;
        edge.b = b;
        edge.face = i;
      }
      ++edge.count;
    }
    const auto audit_facet = [&](unsigned a, unsigned b, unsigned c) {
      CheckFacet(patch, {{result.uv[ids[a]], result.uv[ids[b]], result.uv[ids[c]]}},
                 result.min_alignment);
      const auto x = Evaluate(patch, result.uv[ids[a]]), y = Evaluate(patch, result.uv[ids[b]]),
                 z = Evaluate(patch, result.uv[ids[c]]);
      const auto ab = Difference(y, x), ac = Difference(z, x), bc = Difference(z, y);
      const double quality =
          2 * std::sqrt(3.0) * Norm(Cross(ab, ac)) / (Dot(ab, ab) + Dot(ac, ac) + Dot(bc, bc));
      Require(std::isfinite(quality) && quality > 0, "Invalid physical facet quality");
      result.min_quality = std::min(result.min_quality, quality);
    };
    audit_facet(0, 1, 2);
    auto* a = result.mesh->GetNoh(static_cast<unsigned>(ids[0]));
    auto* b = result.mesh->GetNoh(static_cast<unsigned>(ids[1]));
    auto* c = result.mesh->GetNoh(static_cast<unsigned>(ids[2]));
    if (ids.size() == 4) {
      audit_facet(0, 2, 3);
      auto* d = result.mesh->GetNoh(static_cast<unsigned>(ids[3]));
      research::QuadrilateralAdaptive::Parameters uv{{{result.uv[ids[0]].u, result.uv[ids[0]].v},
                                                      {result.uv[ids[1]].u, result.uv[ids[1]].v},
                                                      {result.uv[ids[2]].u, result.uv[ids[2]].v},
                                                      {result.uv[ids[3]].u, result.uv[ids[3]].v}}};
      double u = 0, v = 0;
      for (auto id : ids) {
        u += result.uv[id].u / 4;
        v += result.uv[id].v / 4;
      }
      const auto normal = patch.Qu(u, v) * patch.Qv(u, v);
      auto quad = std::make_unique<research::QuadrilateralAdaptive>(
          research::QuadrilateralAdaptive::Nodes{a, b, c, d}, uv, normal);
      quad->SetId(static_cast<unsigned long>(i + 1));
      result.mesh->AddElement(std::move(quad));
    } else {
      auto tri = std::make_unique<TriangleAdaptive>(a, b, c);
      tri->SetId(static_cast<unsigned long>(i + 1));
      tri->SetParametersN1({result.uv[ids[0]].u, result.uv[ids[0]].v});
      tri->SetParametersN2({result.uv[ids[1]].u, result.uv[ids[1]].v});
      tri->SetParametersN3({result.uv[ids[2]].u, result.uv[ids[2]].v});
      result.mesh->AddElement(std::move(tri));
    }
  }
  for (const auto& entry : edges)
    if (entry.second.count == 1) {
      const auto& a = result.uv[entry.second.a];
      const auto& b = result.uv[entry.second.b];
      Require((a.u == b.u && (a.u == 0 || a.u == 1)) || (a.v == b.v && (a.v == 0 || a.v == 1)),
              "Gap or unexpected interior boundary");
      ++boundary_edges;
    }
  Require(boundary_edges == 16 && result.uv.size() + result.faces.size() == edges.size() + 1,
          "Original boundary or Euler disk contract changed");
  std::set<std::size_t> seen{0};
  std::vector<std::size_t> work{0};
  while (!work.empty()) {
    const auto i = work.back();
    work.pop_back();
    for (auto j : adjacency[i])
      if (seen.insert(j).second)
        work.push_back(j);
  }
  Require(seen.size() == result.faces.size(), "Disconnected physical chart");
  for (unsigned i = 0; i < result.mesh->GetNumberElements(); ++i)
    Require(result.mesh->GetElement(i)->GetId() == i + 1, "Physical element identity differs");
  if (fail_before_commit)
    throw PublicationFailure("Injected failure before physical publication");
  return result;
}

// Capture exactly the live non-owning element links, including their order.
std::vector<std::vector<ElementAdaptive*>> CaptureNodeObservers(SubMesh& mesh) {
  std::vector<std::vector<ElementAdaptive*>> snapshots;
  snapshots.reserve(mesh.GetNumberNos());
  for (unsigned i = 0; i < mesh.GetNumberNos(); ++i) {
    const auto& observers = mesh.GetNoh(i)->GetElements();
    snapshots.emplace_back(observers.begin(), observers.end());
  }
  return snapshots;
}

// Verify that a physical history node observes only its own actual elements.
void CheckTypedIncidence(SubMesh& mesh, const Candidate& layout) {
  Require(mesh.GetNumberNos() == layout.uv.size() &&
              mesh.GetNumberElements() == layout.faces.size(),
          "Typed history size differs from the accepted QUAD/TRI layout");
  std::vector<std::set<ElementAdaptive*>> expected(mesh.GetNumberNos());
  for (unsigned i = 0; i < mesh.GetNumberElements(); ++i) {
    auto* element = mesh.GetElement(i);
    Require(element != nullptr, "Missing physical history element");
    const auto& face = layout.faces[i];
    Require(face.size() == 3 || face.size() == 4, "Unexpected mixed element arity");
    const bool is_quad = dynamic_cast<research::QuadrilateralAdaptive*>(element) != nullptr;
    const bool is_tri = dynamic_cast<TriangleAdaptive*>(element) != nullptr;
    Require((face.size() == 4 && is_quad && !is_tri) ||
                (face.size() == 3 && is_tri && !is_quad),
            "History element type does not match its physical topology");
    for (const auto index : face) {
      Require(index < expected.size() && expected[index].insert(element).second,
              "Duplicate or invalid typed history incidence");
    }
  }
  for (unsigned i = 0; i < mesh.GetNumberNos(); ++i) {
    auto* node = mesh.GetNoh(i);
    Require(node != nullptr && node->GetId() == static_cast<unsigned long>(i + 1),
            "Typed history node identity changed");
    const auto& actual = node->GetElements();
    Require(actual.size() == expected[i].size() &&
                std::set<ElementAdaptive*>(actual.begin(), actual.end()) == expected[i],
            "Typed history contains a stale, foreign or duplicated observer");
  }
}

// Rebuild a true owned mixed-element graph; never copy borrowed observer lists.
std::unique_ptr<SubMesh> CloneTypedHistory(const SubMesh& original,
                                           const Candidate& layout, PatchBezier& patch,
                                           int fail_before_element) {
  Require(original.GetNumberNos() == layout.uv.size() &&
              original.GetNumberElements() == layout.faces.size(),
          "Typed history source/layout count mismatch");
  auto clone = std::make_unique<SubMesh>();
  for (unsigned i = 0; i < original.GetNumberNos(); ++i) {
    const auto* node = original.GetNoh(i);
    Require(node != nullptr, "Typed history source has a missing node");
    auto copied = std::make_unique<NodeAdaptive>(node->GetX(), node->GetY(), node->GetZ());
    copied->SetId(node->GetId());
    copied->SetGa(node->GetGa());
    copied->SetGd(node->GetGd());
    copied->SetHa(node->GetHa());
    copied->SetHd(node->GetHd());
    clone->AddNoh(std::move(copied));
  }
  for (unsigned i = 0; i < original.GetNumberElements(); ++i) {
    if (fail_before_element == static_cast<int>(i))
      throw PublicationFailure("Injected partial typed history clone failure");
    const auto& face = layout.faces[i];
    auto* source_element = original.GetElement(i);
    Require(source_element != nullptr, "Typed history source has a missing element");
    auto* a = clone->GetNoh(static_cast<unsigned>(face.at(0)));
    auto* b = clone->GetNoh(static_cast<unsigned>(face.at(1)));
    auto* c = clone->GetNoh(static_cast<unsigned>(face.at(2)));
    if (face.size() == 4) {
      const auto* source_quad = dynamic_cast<const research::QuadrilateralAdaptive*>(source_element);
      Require(source_quad != nullptr, "A QUAD was lost during typed history cloning");
      research::QuadrilateralAdaptive::Parameters parameters{};
      double u = 0.0, v = 0.0;
      for (unsigned corner = 0; corner < 4; ++corner) {
        const auto uv = layout.uv.at(face[corner]);
        parameters[corner] = {uv.u, uv.v};
        Require(source_quad->GetParameters()[corner] == parameters[corner],
                "QUAD source UV metadata differs from layout");
        u += uv.u / 4.0;
        v += uv.v / 4.0;
      }
      auto* d = clone->GetNoh(static_cast<unsigned>(face[3]));
      const auto normal = patch.Qu(u, v) * patch.Qv(u, v);
      auto copied = std::make_unique<research::QuadrilateralAdaptive>(
          research::QuadrilateralAdaptive::Nodes{a, b, c, d}, parameters, normal);
      copied->SetId(static_cast<unsigned long>(i + 1));
      clone->AddElement(std::move(copied));
    } else {
      Require(face.size() == 3, "Unsupported history element arity");
      const auto* source_tri = dynamic_cast<const TriangleAdaptive*>(source_element);
      Require(source_tri != nullptr, "An AFT triangle was lost during typed history cloning");
      auto matches = [](const std::tuple<double, double>& values, UvVertex uv) {
        return std::get<0>(values) == uv.u && std::get<1>(values) == uv.v;
      };
      Require(matches(source_tri->GetParametersN1(), layout.uv.at(face[0])) &&
                  matches(source_tri->GetParametersN2(), layout.uv.at(face[1])) &&
                  matches(source_tri->GetParametersN3(), layout.uv.at(face[2])),
              "AFT triangle source UV metadata differs from layout");
      auto copied = std::make_unique<TriangleAdaptive>(a, b, c);
      copied->SetId(static_cast<unsigned long>(i + 1));
      copied->SetParametersN1({layout.uv[face[0]].u, layout.uv[face[0]].v});
      copied->SetParametersN2({layout.uv[face[1]].u, layout.uv[face[1]].v});
      copied->SetParametersN3({layout.uv[face[2]].u, layout.uv[face[2]].v});
      clone->AddElement(std::move(copied));
    }
    const auto* replica = clone->GetElement(i);
    Require(replica != source_element &&
                std::abs(replica->GetArea() - source_element->GetArea()) <=
                    1e-12 * std::max(1.0, std::abs(source_element->GetArea())),
            "History copy changed physical element area or reused its identity");
  }
  return clone;
}

void ProbeTypedHistory(SubMesh& accepted, const Candidate& layout, PatchBezier& patch) {
  // The probe runs before OBJ publication and before the candidate is committed.
  SubMesh* previous_patch_owner = patch.GetSubMesh();
  CheckTypedIncidence(accepted, layout);
  const auto original_observers = CaptureNodeObservers(accepted);
  const auto* first_original_node = accepted.GetNoh(0);
  const auto* first_original_element = accepted.GetElement(0);
  {
    auto clone = CloneTypedHistory(accepted, layout, patch, -1);
    CheckTypedIncidence(*clone, layout);
    Require(clone->GetNoh(0) != first_original_node &&
                clone->GetElement(0) != first_original_element,
            "Typed history clone aliases a previously accepted owner");

    // Restore the original observer even if a later verification throws.
    struct RestoreOriginalPatch final {
      PatchBezier& patch;
      SubMesh* previous;
      ~RestoreOriginalPatch() { patch.SetSubMesh(previous); }
    } restore{patch, previous_patch_owner};
    clone->SetPatch(&patch);
    patch.SetSubMesh(clone.get());
    Require(patch.GetSubMesh() == clone.get(),
            "Typed clone could not be staged as the current Patch submesh");
    bool rejected = false;
    try {
      auto failed = CloneTypedHistory(*clone, layout, patch, 7);
      (void)failed;
    } catch (const PublicationFailure&) {
      rejected = true;
    }
    Require(rejected && patch.GetSubMesh() == clone.get(),
            "Rejected partial history clone replaced the accepted candidate");
    CheckTypedIncidence(*clone, layout);
    CheckTypedIncidence(accepted, layout);
    Require(CaptureNodeObservers(accepted) == original_observers,
            "Transient history clone mutated previously accepted node observers");
  }
  Require(patch.GetSubMesh() == previous_patch_owner &&
              accepted.GetNoh(0) == first_original_node &&
              accepted.GetElement(0) == first_original_element &&
              CaptureNodeObservers(accepted) == original_observers,
          "Typed history clone teardown damaged previously accepted state");
  std::cout << "QUAD_TYPED_HISTORY_CLONE accepted_clone=1 partial_failure_rollback=1"
               " source_observers_preserved=1 adaptive_epochs=0\n";
}

// Observe the physical mixed graph without changing its accepted QUAD/TRI faces.
void ProbeMixedCurvature(SubMesh& mesh, const Candidate& layout) {
  std::vector<research::MixedPoint3> physical;
  physical.reserve(mesh.GetNumberNos());
  for (unsigned i = 0; i < mesh.GetNumberNos(); ++i) {
    const auto* node = mesh.GetNoh(i);
    Require(node != nullptr, "Missing node for typed mixed curvature");
    physical.push_back({node->GetX(), node->GetY(), node->GetZ()});
  }
  const auto observed = research::AuditMixedCurvature(physical, layout.faces);
  Require(observed.vertices.size() == layout.uv.size() &&
              observed.quadrilaterals == layout.quads &&
              observed.triangles == layout.faces.size() - layout.quads &&
              observed.boundary_edges == 16 && observed.boundary_vertices == 16 &&
              observed.interior_vertices + observed.boundary_vertices == layout.uv.size() &&
              observed.interior_vertices > 0 && observed.min_barycentric_area > 0,
          "Mixed TRI/QUAD curvature metrics differ from validated physical chart");

  // Each malformed metric witness is rejected independently of the live mesh.
  unsigned rejected = 0;
  const auto must_reject = [&](const std::vector<research::MixedPoint3>& points,
                               const std::vector<research::MixedFace>& faces) {
    try {
      (void)research::AuditMixedCurvature(points, faces);
    } catch (const std::invalid_argument&) {
      ++rejected;
    }
  };
  must_reject({{0, 0, 0}, {1, 0, 0}, {0, 1, 0}}, {{0, 1, 1}});
  must_reject({{0, 0, 0}, {1, 0, 0}, {0, 1, 0}, {-1, 0, 0}, {0, -1, 0}},
              {{0, 1, 2}, {0, 3, 4}});
  must_reject({{0, 0, 0}, {1, 0, 0}, {0, 1, 0}, {1, 1, 0}},
              {{0, 1, 2}, {0, 1, 3}});
  must_reject({{0, 0, 0}, {1, 0, 0}, {2, 0, 0}}, {{0, 1, 2}});
  must_reject({{0, 0, 0}, {1, 0, 0}, {0, 1, std::numeric_limits<double>::quiet_NaN()}},
              {{0, 1, 2}});
  Require(rejected == 5, "Malformed typed mixed curvature input was accepted");

  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << std::setprecision(17)
         << "QUAD_TYPED_CURVATURE quad=" << observed.quadrilaterals
         << " tri=" << observed.triangles
         << " boundary_edges=" << observed.boundary_edges
         << " boundary_vertices=" << observed.boundary_vertices
         << " interior_vertices=" << observed.interior_vertices
         << " angle_defect_total=" << observed.total_angle_defect
         << " min_barycentric_area=" << observed.min_barycentric_area
         << " negative_cases=" << rejected
         << " policy=triangulated_barycentric_probe adaptive_epochs=0\n";
  std::cout << output.str();
}

// Observe true physical four-corner quality without changing QUAD ownership.
void ProbePhysicalQuadQuality(SubMesh& mesh, const Candidate& layout, PatchBezier& patch) {
  double min_scaled = 1.0;
  double min_warp_cosine = 1.0;
  double max_edge_ratio = 1.0;
  unsigned count = 0;
  for (std::size_t i = 0; i < layout.quads; ++i) {
    const auto& face = layout.faces.at(i);
    Require(face.size() == 4 &&
                dynamic_cast<research::QuadrilateralAdaptive*>(mesh.GetElement(static_cast<unsigned>(i))) != nullptr,
            "Unexpected physical element in typed QUAD quality gate");
    research::PhysicalQuadCorners points{};
    research::PhysicalQuadCorners normals{};
    for (unsigned corner = 0; corner < 4; ++corner) {
      const auto id = face[corner];
      const auto* node = mesh.GetNoh(static_cast<unsigned>(id));
      Require(node != nullptr, "Missing physical QUAD quality node");
      points[corner] = {node->GetX(), node->GetY(), node->GetZ()};
      const auto uv = layout.uv.at(id);
      normals[corner] = Cross(Values(patch.Qu(uv.u, uv.v)), Values(patch.Qv(uv.u, uv.v)));
    }
    const auto metric = research::ObservePhysicalQuadQuality(points, normals);
    min_scaled = std::min(min_scaled, metric.min_scaled_jacobian);
    min_warp_cosine = std::min(min_warp_cosine, metric.diagonal_normal_cosine);
    max_edge_ratio = std::max(max_edge_ratio, metric.edge_ratio);
    ++count;
  }
  Require(count == 42 && min_scaled > 0.0 && min_warp_cosine > 0.0 &&
              std::isfinite(max_edge_ratio),
          "Invalid controlled typed QUAD physical quality");

  // Independent malformed physical-only witnesses do not mutate the live mesh.
  const research::PhysicalQuadCorners square{{{0, 0, 0}, {1, 0, 0}, {1, 1, 0}, {0, 1, 0}}};
  const research::PhysicalQuadCorners forward{{{0, 0, 1}, {0, 0, 1}, {0, 0, 1}, {0, 0, 1}}};
  const auto flat = research::ObservePhysicalQuadQuality(square, forward);
  Require(std::abs(flat.min_scaled_jacobian - 1.0) < 1e-12 &&
              std::abs(flat.diagonal_normal_cosine - 1.0) < 1e-12 &&
              std::abs(flat.edge_ratio - 1.0) < 1e-12,
          "Analytic square QUAD physical quality witness failed");
  unsigned rejected = 0;
  const auto must_reject = [&](const research::PhysicalQuadCorners& points,
                               const research::PhysicalQuadCorners& normals) {
    try {
      (void)research::ObservePhysicalQuadQuality(points, normals);
    } catch (const std::invalid_argument&) {
      ++rejected;
    }
  };
  must_reject({{{0, 0, 0}, {0, 1, 0}, {1, 1, 0}, {1, 0, 0}}}, forward);
  must_reject({{{0, 0, 0}, {1, 0, 0}, {1, 0, 0}, {0, 1, 0}}}, forward);
  must_reject(square, {{{0, 0, -1}, {0, 0, -1}, {0, 0, -1}, {0, 0, -1}}});
  auto nonfinite = square;
  nonfinite[0][0] = std::numeric_limits<double>::quiet_NaN();
  must_reject(nonfinite, forward);
  Require(rejected == 4, "Malformed typed QUAD physical quality input was admitted");
  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << std::setprecision(17)
         << "QUAD_TYPED_QUALITY quads=" << count
         << " min_scaled_jacobian=" << min_scaled
         << " min_warpage_cosine=" << min_warp_cosine
         << " max_edge_ratio=" << max_edge_ratio
         << " negative_cases=" << rejected
         << " policy=corner_normal_metric_probe adaptive_epochs=0\n";
  std::cout << output.str();
}

// Read the accepted physical candidate and choose a real native source leaf by error.
research::MixedSurfaceResidual ProbeMixedSurfaceResidual(const Candidate& candidate, PatchBezier& patch) {
  std::vector<research::ResidualUv> parametric;
  std::vector<research::ResidualPoint3> physical;
  parametric.reserve(candidate.uv.size());
  physical.reserve(candidate.uv.size());
  for (std::size_t i = 0; i < candidate.uv.size(); ++i) {
    parametric.push_back({candidate.uv[i].u, candidate.uv[i].v});
    const auto* n = candidate.mesh->GetNoh(static_cast<unsigned>(i));
    Require(n != nullptr, "Mixed residual references a missing accepted physical node");
    physical.push_back({n->GetX(), n->GetY(), n->GetZ()});
  }
  const auto source = [&patch](const research::ResidualUv& uv) -> research::ResidualPoint3 {
    return Evaluate(patch, UvVertex{uv[0], uv[1]});
  };
  const auto metrics = research::MeasureMixedSurfaceResidual(
      parametric, physical, candidate.faces, source);
  Require(metrics.quadrilaterals == candidate.quads &&
              metrics.triangles == candidate.faces.size() - candidate.quads &&
              metrics.samples == 5 * metrics.quadrilaterals + 4 * metrics.triangles &&
              metrics.worst_quad_face < candidate.quad_origins.size() &&
              metrics.maximum >= metrics.quad_maximum &&
              metrics.maximum >= metrics.triangle_maximum &&
              metrics.worst_triangle_face >= candidate.quads &&
              metrics.worst_triangle_face < candidate.faces.size(),
          "Mixed physical error/source-leaf witness is invalid");
  const auto& leaf = candidate.quad_origins[metrics.worst_quad_face];
  Require(leaf.cell_id >= 0 && leaf.relative_depth >= 2 &&
              metrics.worst_quad_sample_uv[0] > 0.0 &&
              metrics.worst_quad_sample_uv[0] < 1.0 &&
              metrics.worst_quad_sample_uv[1] > 0.0 &&
              metrics.worst_quad_sample_uv[1] < 1.0,
          "Mixed residual selected an invalid real native quadtree source leaf");
  std::ostringstream line;
  line.imbue(std::locale::classic());
  line << std::setprecision(17)
       << "QUAD_SOURCE_RESIDUAL samples=" << metrics.samples
       << " quads=" << metrics.quadrilaterals
       << " triangles=" << metrics.triangles
       << " maximum=" << metrics.maximum
       << " rms=" << metrics.rms
       << " quad_maximum=" << metrics.quad_maximum
       << " triangle_maximum=" << metrics.triangle_maximum
       << " worst_quad_face=" << metrics.worst_quad_face
       << " worst_triangle_face=" << metrics.worst_triangle_face
       << " dominant_region="
       << (metrics.triangle_maximum > metrics.quad_maximum ? "tri_aft" : "quad_interior")
       << " tri_sample_u=" << metrics.worst_triangle_sample_uv[0]
       << " tri_sample_v=" << metrics.worst_triangle_sample_uv[1]
       << " real_leaf_ordinal=" << leaf.leaf_ordinal
       << " real_cell_id=" << leaf.cell_id
       << " source_depth=" << leaf.relative_depth
       << " select_u=" << metrics.worst_quad_sample_uv[0]
       << " select_v=" << metrics.worst_quad_sample_uv[1]
       << " policy=physical_bilinear_quad_tri_barycentric_v1"
       << " real_tree_edits=0 adaptive_epochs=0\n";
  std::cout << line.str();
  return metrics;
}

// Mutate only fresh native Quadtree proposals; preserve the first physical candidate.
struct NativeRefinementTrial {
  long chosen_cell_id = -1;
  unsigned initial_leaf_depth = 0;
  std::size_t leaves = 0;
  std::size_t quads = 0;
  long double interior_uv_area = 0.0L;
  bool emitted_disk = false;
  std::string rejection = "none";
};

NativeRefinementTrial TrialRealTreeRefinement(const research::ResidualUv& selected_uv) {
  Require(std::isfinite(selected_uv[0]) && std::isfinite(selected_uv[1]) &&
              selected_uv[0] > 0.0 && selected_uv[0] < 1.0 &&
              selected_uv[1] > 0.0 && selected_uv[1] < 1.0,
          "Native QUAD tree refinement selection requires strict interior UV");
  auto tree = MakeSourceTree(true);
  NativeRefinementTrial trial;
  QuadtreeCell* target = nullptr;
  for (auto* leaf : tree->getLeaves()) {
    auto* minimum = leaf->getMin();
    auto* maximum = leaf->getMax();
    if (selected_uv[0] > minimum->getX() && selected_uv[0] < maximum->getX() &&
        selected_uv[1] > minimum->getY() && selected_uv[1] < maximum->getY()) {
      Require(target == nullptr, "Ambiguous native source cell chosen for refinement");
      target = leaf;
    }
  }
  Require(target != nullptr && !target->subdivided() && target->getLevel() < 8,
          "No eligible original native source quadtree leaf contains the error site");
  trial.chosen_cell_id = target->getId();
  trial.initial_leaf_depth = static_cast<unsigned>(target->getLevel());
  const auto leaves_before = tree->GetLeafCount();
  target->subdivideToLevel(target->getLevel() + 1);
  tree->refineAccordingToNeighbors();
  trial.leaves = tree->GetLeafCount();
  Require(trial.leaves > leaves_before,
          "Native source tree trial did not actually refine a source leaf");
  try {
    const auto captured = CaptureLeafPolygons(*tree);
    trial.interior_uv_area = captured.interior_area;
    const auto emitted = EmitLeafQuads(*tree, PointRule);
    trial.quads = emitted.quads.size();
    trial.emitted_disk = true;
  } catch (const std::invalid_argument& error) {
    // A disconnected island or broken 2:1 interface is a rejected native trial.
    trial.rejection = error.what();
  }
  return trial;
}

// A bounded three-leaf source refinement band reconnects a corner AFT island
// toward the interior QUAD region, without claiming any new physical mesh.
struct ConnectedBandTrial {
  std::array<long, 3> refined_cell_ids{{-1, -1, -1}};
  std::size_t baseline_leaves = 0;
  std::size_t leaves = 0;
  std::size_t quads = 0;
  long double uv_area = 0.0L;
  bool admitted_uv_disk = false;
  std::string rejection = "none";
};

ConnectedBandTrial TrialConnectedAftBand(
    const research::ResidualUv& selected_uv,
    std::unique_ptr<Quadtree>* retained_native_tree = nullptr) {
  Require(std::isfinite(selected_uv[0]) && std::isfinite(selected_uv[1]) &&
              selected_uv[0] > 0.0 && selected_uv[0] < 1.0 &&
              selected_uv[1] > 0.0 && selected_uv[1] < 1.0,
          "Connected AFT band needs a real interior source residual sample");
  auto tree = MakeSourceTree(true);
  ConnectedBandTrial result;
  result.baseline_leaves = tree->GetLeafCount();
  const auto find_leaf = [&tree](double u, double v) -> QuadtreeCell* {
    QuadtreeCell* chosen = nullptr;
    for (auto* cell : tree->getLeaves()) {
      auto* low = cell->getMin();
      auto* high = cell->getMax();
      if (u > low->getX() && u < high->getX() &&
          v > low->getY() && v < high->getY()) {
        Require(chosen == nullptr, "Ambiguous source leaf in connected band");
        chosen = cell;
      }
    }
    Require(chosen != nullptr, "Connected band source site lacks a native leaf");
    return chosen;
  };

  auto* corner = find_leaf(selected_uv[0], selected_uv[1]);
  const double u0 = corner->getMin()->getX();
  const double v0 = corner->getMin()->getY();
  const double du = corner->getMax()->getX() - u0;
  const double dv = corner->getMax()->getY() - v0;
  const double center_u = u0 + 0.5 * du;
  const double center_v = v0 + 0.5 * dv;
  // Only the current lower-left AFT-dominated corner geometry is qualified.
  Require(corner->getLevel() == 2 && center_u < 0.5 && center_v < 0.5 &&
              std::isfinite(du) && std::isfinite(dv) && du > 0.0 && dv > 0.0,
          "Connected AFT band requires the pinned corner source chart");
  auto* east = find_leaf(center_u + du, center_v);
  auto* north = find_leaf(center_u, center_v + dv);
  const std::array<QuadtreeCell*, 3> selected{{corner, east, north}};
  std::set<QuadtreeCell*> unique(selected.begin(), selected.end());
  Require(unique.size() == 3 &&
              east->getLevel() == corner->getLevel() &&
              north->getLevel() == corner->getLevel(),
          "Connected band did not select three distinct native source leaves");
  for (std::size_t i = 0; i < selected.size(); ++i) {
    auto* leaf = selected[i];
    result.refined_cell_ids[i] = leaf->getId();
    Require(!leaf->subdivided(), "Connected band attempted repeat native leaf edit");
    leaf->subdivideToLevel(leaf->getLevel() + 1);
  }
  tree->refineAccordingToNeighbors();
  result.leaves = tree->GetLeafCount();
  Require(result.leaves >= result.baseline_leaves + 9,
          "Connected band did not perform three actual native subdivisions");
  try {
    const auto region = CaptureLeafPolygons(*tree);
    result.uv_area = region.interior_area;
    auto emitted = EmitLeafQuads(*tree, PointRule);
    result.quads = emitted.quads.size();
    result.admitted_uv_disk = true;
  } catch (const std::invalid_argument& failure) {
    // Retain the genuine native topological failure as a rejected proposal.
    result.rejection = failure.what();
  }
  if (result.admitted_uv_disk && retained_native_tree)
    *retained_native_tree = std::move(tree);
  return result;
}

void ProbeConnectedAftBand(const Candidate& unchanged,
                           const research::MixedSurfaceResidual& residual) {
  Require(unchanged.mesh && unchanged.quads > 0 &&
              residual.worst_triangle_face >= unchanged.quads &&
              residual.worst_triangle_face < unchanged.faces.size(),
          "Connected band has no previous real physical AFT source error");
  const auto observers = CaptureNodeObservers(*unchanged.mesh);
  const auto* original_node = unchanged.mesh->GetNoh(0);
  const auto* original_element = unchanged.mesh->GetElement(0);
  const auto band = TrialConnectedAftBand(residual.worst_triangle_sample_uv);
  Require(band.refined_cell_ids[0] == 6 && band.refined_cell_ids[1] > 0 &&
              band.refined_cell_ids[2] > 0 &&
              unchanged.mesh->GetNoh(0) == original_node &&
              unchanged.mesh->GetElement(0) == original_element &&
              CaptureNodeObservers(*unchanged.mesh) == observers,
          "Connected native band lost physical source selection or prior owner identity");
  std::ostringstream out;
  out.imbue(std::locale::classic());
  out << std::setprecision(17)
      << "QUAD_CONNECTED_BAND_TRIAL"
      << " source=real_candidate_worst_aft_triangle"
      << " source_cell_id=" << band.refined_cell_ids[0]
      << " bridge_east_cell_id=" << band.refined_cell_ids[1]
      << " bridge_north_cell_id=" << band.refined_cell_ids[2]
      << " baseline_leaves=" << band.baseline_leaves
      << " refined_leaves=" << band.leaves
      << " native_leaf_edits=3"
      << " admitted_uv_disk=" << int(band.admitted_uv_disk)
      << " quad_uv_area=" << band.uv_area
      << " emitted_quads=" << band.quads
      << " prior_physical_owner_preserved=1"
      << " actual_aft_retriangulations=0"
      << " adaptive_epochs=0\n";
  std::cout << out.str();
  if (!band.admitted_uv_disk)
    std::cout << "QUAD_CONNECTED_BAND_REJECTION reason=" << band.rejection << '\n';
}

void ProbeNativeTreeAlternatives(const Candidate& unchanged,
                                 const research::MixedSurfaceResidual& residual) {
  Require(unchanged.mesh != nullptr && unchanged.quads > 0 &&
              residual.worst_quad_face < unchanged.quads &&
              residual.worst_triangle_face >= unchanged.quads &&
              residual.worst_triangle_face < unchanged.faces.size(),
          "Native tree trials lack a real physical candidate/error-face identity");
  const auto previous_observers = CaptureNodeObservers(*unchanged.mesh);
  const auto* node = unchanged.mesh->GetNoh(0);
  const auto* element = unchanged.mesh->GetElement(0);
  const auto baseline_tree = MakeSourceTree(true);
  const auto baseline = CaptureLeafPolygons(*baseline_tree);
  Require(baseline.source_leaves == 19 && baseline.interior_area == 0.25L,
          "Unexpected original fixed16 native QUAD region before refinement");
  const auto quad_trial = TrialRealTreeRefinement(residual.worst_quad_sample_uv);
  const auto aft_trial = TrialRealTreeRefinement(residual.worst_triangle_sample_uv);
  Require(quad_trial.chosen_cell_id != aft_trial.chosen_cell_id &&
              quad_trial.initial_leaf_depth == 2 && aft_trial.initial_leaf_depth == 2 &&
              quad_trial.leaves > baseline.source_leaves &&
              aft_trial.leaves > baseline.source_leaves,
          "Mixed source errors did not select two distinct real native level-2 leaves");
  Require(unchanged.mesh->GetNoh(0) == node &&
              unchanged.mesh->GetElement(0) == element &&
              CaptureNodeObservers(*unchanged.mesh) == previous_observers,
          "Transient native tree trials damaged the original accepted physical candidate");
  Require(quad_trial.interior_uv_area >= baseline.interior_area || !quad_trial.emitted_disk,
          "Interior QUAD trial unexpectedly lost admitted source region");
  Require(aft_trial.interior_uv_area >= baseline.interior_area || !aft_trial.emitted_disk,
          "Boundary AFT trial unexpectedly lost admitted source region");

  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << std::setprecision(17)
         << "QUAD_NATIVE_TREE_TRIALS"
         << " source=generated_real_mixed_physical_candidate"
         << " baseline_leaves=" << baseline.source_leaves
         << " baseline_quad_uv_area=" << baseline.interior_area
         << " quad_cell_id=" << quad_trial.chosen_cell_id
         << " quad_leaves=" << quad_trial.leaves
         << " quad_emitted_disk=" << int(quad_trial.emitted_disk)
         << " quad_uv_area=" << quad_trial.interior_uv_area
         << " quad_faces=" << quad_trial.quads
         << " aft_cell_id=" << aft_trial.chosen_cell_id
         << " aft_leaves=" << aft_trial.leaves
         << " aft_emitted_disk=" << int(aft_trial.emitted_disk)
         << " aft_uv_area=" << aft_trial.interior_uv_area
         << " aft_quad_faces=" << aft_trial.quads
         << " source_candidate_preserved=1"
         << " native_trial_refinements=2"
         << " actual_adaptive_epochs=0\n";
  std::cout << output.str();
  // Preserve rejected-candidate reasons without admitting a partial quadtree.
  if (!quad_trial.emitted_disk)
    std::cout << "QUAD_NATIVE_TRIAL_REJECTION region=quad reason=" << quad_trial.rejection << '\n';
  if (!aft_trial.emitted_disk)
    std::cout << "QUAD_NATIVE_TRIAL_REJECTION region=aft reason=" << aft_trial.rejection << '\n';
}

void Export(const Candidate& result, const std::filesystem::path& path) {
  Require(!std::filesystem::exists(path), "Controlled output already exists");
  auto staging = path;
  staging += ".pending";
  Require(std::filesystem::create_directory(staging), "Pending output already exists");
  const auto temporary = staging / "mesh.obj";
  try {
    std::ofstream out(temporary, std::ios::binary);
    out.imbue(std::locale::classic());
    Require(bool(out), "Cannot create controlled output");
    out << std::setprecision(17)
        << "# controlled curved Bezier; experimental fixed16/vertex_mean; not adaptive\n";
    for (unsigned i = 0; i < result.mesh->GetNumberNos(); ++i) {
      const auto* n = result.mesh->GetNoh(i);
      out << "v " << n->GetX() << ' ' << n->GetY() << ' ' << n->GetZ() << '\n';
    }
    for (const auto& uv : result.uv)
      out << "vt " << uv.u << ' ' << uv.v << '\n';
    for (std::size_t i = 0; i < result.faces.size(); ++i) {
      if (i == 0)
        out << "g QUAD\n";
      if (i == result.quads)
        out << "g TRI_AFT\n";
      out << "f";
      for (auto id : result.faces[i])
        out << ' ' << id + 1 << '/' << id + 1;
      out << '\n';
    }
    out.close();
    Require(bool(out), "Controlled output write failed");
    // Same-directory link publishes without replacing any concurrently created output.
    std::filesystem::create_hard_link(temporary, path);
  } catch (...) {
    std::error_code ec;
    std::filesystem::remove(temporary, ec);
    std::filesystem::remove(staging, ec);
    throw;
  }
  std::error_code ec;
  std::filesystem::remove(temporary, ec);
  std::filesystem::remove(staging, ec);
}
// Test the *next* source-error-selected boundary band on actual native trees.
// The previously refined first band is rebuilt before every candidate trial.
// This does not publish a second physical SubMesh or accept an adaptive epoch.
struct SecondNativeBandTrial {
  std::size_t baseline_leaves = 0;
  std::size_t leaves = 0;
  std::size_t quads = 0;
  long double uv_area = 0.0L;
  long selected_cell_id = -1;
  long west_cell_id = -1;
  long north_cell_id = -1;
  bool admitted_uv_disk = false;
  std::string rejection = "none";
};

SecondNativeBandTrial TrialSecondNativeBand(const research::ResidualUv& first_source,
                                            const research::ResidualUv& second_source,
                                            unsigned variant,
                                            std::unique_ptr<Quadtree>* retained_native_tree = nullptr) {
  Require(variant < 4 && std::isfinite(second_source[0]) &&
              std::isfinite(second_source[1]) &&
              second_source[0] > 0.75 && second_source[0] < 1.0 &&
              second_source[1] > 0.0 && second_source[1] < 0.25,
          "Second connected AFT band needs the measured lower-right source chart");
  std::unique_ptr<Quadtree> tree;
  const auto first = TrialConnectedAftBand(first_source, &tree);
  Require(first.admitted_uv_disk && tree && first.leaves == 28 &&
              first.quads == 62 && first.uv_area == 0.328125L,
          "Second native trial did not reproduce the first physical source band");
  SecondNativeBandTrial result;
  result.baseline_leaves = tree->GetLeafCount();
  const auto find_leaf = [&tree](double u, double v) -> QuadtreeCell* {
    QuadtreeCell* chosen = nullptr;
    for (auto* cell : tree->getLeaves()) {
      auto* low = cell->getMin();
      auto* high = cell->getMax();
      if (u > low->getX() && u < high->getX() &&
          v > low->getY() && v < high->getY()) {
        Require(chosen == nullptr, "Ambiguous second-band native source leaf");
        chosen = cell;
      }
    }
    Require(chosen != nullptr, "Second AFT source site lacks a native leaf");
    return chosen;
  };
  auto* corner = find_leaf(second_source[0], second_source[1]);
  Require(corner->getLevel() == 2 &&
              corner->getMin()->getX() == 0.75 &&
              corner->getMin()->getY() == 0.0,
          "Second AFT source leaf was not the original lower-right level-2 cell");
  const double du = corner->getMax()->getX() - corner->getMin()->getX();
  const double dv = corner->getMax()->getY() - corner->getMin()->getY();
  Require(du == 0.25 && dv == 0.25,
          "Second AFT source cell changed its original dyadic extent");
  const double u = corner->getMin()->getX() + 0.5 * du;
  const double v = corner->getMin()->getY() + 0.5 * dv;
  auto* west = find_leaf(u - du, v);
  auto* north = find_leaf(u, v + dv);
  Require(west != corner && north != corner && west != north &&
              west->getLevel() == 2 && north->getLevel() == 2,
          "Second native AFT bridge cells are not distinct original leaves");
  result.selected_cell_id = corner->getId();
  result.west_cell_id = west->getId();
  result.north_cell_id = north->getId();
  std::vector<QuadtreeCell*> chosen{corner};
  if (variant & 1u)
    chosen.push_back(west);
  if (variant & 2u)
    chosen.push_back(north);
  for (auto* leaf : chosen) {
    Require(!leaf->subdivided() && leaf->getLevel() == 2,
            "Second native AFT trial attempted an invalid repeat source edit");
    leaf->subdivideToLevel(3);
  }
  tree->refineAccordingToNeighbors();
  result.leaves = tree->GetLeafCount();
  Require(result.leaves >= result.baseline_leaves + 3 * chosen.size(),
          "Second AFT native trial lost required source leaf edits");
  try {
    const auto region = CaptureLeafPolygons(*tree);
    result.uv_area = region.interior_area;
    const auto emitted = EmitLeafQuads(*tree, PointRule);
    result.quads = emitted.quads.size();
    result.admitted_uv_disk = true;
    if (retained_native_tree)
      *retained_native_tree = std::move(tree);
  } catch (const std::invalid_argument& failure) {
    // A disconnected island is reported as a rejected native proposal.
    result.rejection = failure.what();
  }
  return result;
}

void ProbeSecondNativeAftVariants(const Candidate& previous_physical,
                                  const research::MixedSurfaceResidual& first_source,
                                  const research::MixedSurfaceResidual& second_source) {
  Require(previous_physical.mesh && previous_physical.quads == 62 &&
              second_source.worst_triangle_face >= previous_physical.quads &&
              second_source.worst_triangle_face < previous_physical.faces.size(),
          "Second native refinement lacks the actual preceding physical AFT error");
  const auto previous_observers = CaptureNodeObservers(*previous_physical.mesh);
  const auto* previous_node = previous_physical.mesh->GetNoh(0);
  const auto* previous_element = previous_physical.mesh->GetElement(0);
  static const std::array<const char*, 4> names{{"corner", "west", "north", "both"}};
  for (unsigned variant = 0; variant < names.size(); ++variant) {
    const auto trial = TrialSecondNativeBand(first_source.worst_triangle_sample_uv,
                                             second_source.worst_triangle_sample_uv,
                                             variant);
    Require(previous_physical.mesh->GetNoh(0) == previous_node &&
                previous_physical.mesh->GetElement(0) == previous_element &&
                CaptureNodeObservers(*previous_physical.mesh) == previous_observers,
            "Second temporary native refinement modified the previous physical owner");
    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << std::setprecision(17)
        << "QUAD_SECOND_NATIVE_BAND"
        << " variant=" << names[variant]
        << " source=staged_previous_physical_worst_aft"
        << " selected_native_id=" << trial.selected_cell_id
        << " west_native_id=" << trial.west_cell_id
        << " north_native_id=" << trial.north_cell_id
        << " baseline_leaves=" << trial.baseline_leaves
        << " refined_leaves=" << trial.leaves
        << " native_leaf_edits=" << (1u + ((variant & 1u) != 0u) + ((variant & 2u) != 0u))
        << " admitted_uv_disk=" << int(trial.admitted_uv_disk)
        << " quad_uv_area=" << trial.uv_area
        << " emitted_quads=" << trial.quads
        << " previous_physical_owner_preserved=1"
        << " actual_second_aft_retriangulations=0"
        << " adaptive_epochs=0\n";
    std::cout << out.str();
    if (!trial.admitted_uv_disk)
      std::cout << "QUAD_SECOND_NATIVE_BAND_REJECTION variant=" << names[variant]
                << " reason=" << trial.rejection << '\n';
  }
}

// Reconstruct each new native disk with the ORIGINAL AFT exterior pipeline.
// A failure remains a rejected proposal: no prior typed owner is replaced.
// The original source's fixed16 boundary is retained, so no true mixed epoch.
void ProbeSecondPhysicalAftVariants(const Candidate& previous_physical,
                                    PatchBezier& patch,
                                    const research::MixedSurfaceResidual& first_source,
                                    const research::MixedSurfaceResidual& second_source,
                                    const std::filesystem::path& output_prefix) {
  Require(previous_physical.mesh && previous_physical.quads == 62 &&
              second_source.worst_triangle_face >= previous_physical.quads &&
              second_source.worst_triangle_face < previous_physical.faces.size(),
          "Second physical AFT trials require the preceding real mixed source residual");
  const auto previous_observers = CaptureNodeObservers(*previous_physical.mesh);
  auto* previous_node = previous_physical.mesh->GetNoh(0);
  auto* previous_element = previous_physical.mesh->GetElement(0);
  auto* previous_patch_owner = patch.GetSubMesh();
  static const std::array<const char*, 4> names{{"corner", "west", "north", "both"}};
  for (unsigned variant = 0; variant < names.size(); ++variant) {
    const auto native = TrialSecondNativeBand(first_source.worst_triangle_sample_uv,
                                               second_source.worst_triangle_sample_uv,
                                               variant);
    const auto candidate_path = std::filesystem::path(
        output_prefix.string() + "." + names[variant] + ".second-band-candidate.obj");
    bool staged = false;
    std::string reason = native.rejection;
    std::size_t physical_nodes = 0;
    std::size_t physical_quads = 0;
    std::size_t physical_triangles = 0;
    double min_facet_quality = 0.0;
    double max_source_error = 0.0;
    if (native.admitted_uv_disk) {
      try {
        const auto factory = [&first_source, &second_source, variant, &native]()
            -> std::unique_ptr<Quadtree> {
          std::unique_ptr<Quadtree> ready;
          const auto repeat = TrialSecondNativeBand(
              first_source.worst_triangle_sample_uv,
              second_source.worst_triangle_sample_uv, variant, &ready);
          Require(ready && repeat.admitted_uv_disk &&
                      repeat.quads == native.quads &&
                      repeat.leaves == native.leaves &&
                      repeat.uv_area == native.uv_area,
                  "Original native AFT and QUAD template trees differ for second band");
          return ready;
        };
        // Generate invokes the same native tree factory separately for the
        // original TRI reference front and typed QUAD/interior AFT pipeline.
        auto candidate = Generate(patch, false, factory);
        CheckTypedIncidence(*candidate.mesh, candidate);
        Require(candidate.quads == native.quads &&
                    candidate.faces.size() > candidate.quads &&
                    candidate.mesh->GetNumberNos() == candidate.uv.size(),
                "Native second physical band lost actual typed QUAD/AFT elements");
        std::vector<research::ResidualUv> uv;
        std::vector<research::ResidualPoint3> xyz;
        uv.reserve(candidate.uv.size());
        xyz.reserve(candidate.uv.size());
        for (std::size_t i = 0; i < candidate.uv.size(); ++i) {
          uv.push_back({candidate.uv[i].u, candidate.uv[i].v});
          const auto* node = candidate.mesh->GetNoh(static_cast<unsigned>(i));
          Require(node != nullptr, "Second AFT physical candidate contains a null node");
          xyz.push_back({node->GetX(), node->GetY(), node->GetZ()});
        }
        const auto source = [&patch](const research::ResidualUv& site)
            -> research::ResidualPoint3 {
          return Evaluate(patch, {site[0], site[1]});
        };
        const auto errors = research::MeasureMixedSurfaceResidual(
            uv, xyz, candidate.faces, source);
        Require(errors.quadrilaterals == candidate.quads &&
                    errors.triangles == candidate.faces.size() - candidate.quads &&
                    errors.triangles > 0 &&
                    std::isfinite(errors.maximum) &&
                    std::isfinite(candidate.min_quality) &&
                    candidate.min_quality > 0.0,
                "Second AFT physical proposal failed typed Bezier quality/source checks");
        physical_nodes = candidate.mesh->GetNumberNos();
        physical_quads = candidate.quads;
        physical_triangles = errors.triangles;
        min_facet_quality = candidate.min_quality;
        max_source_error = errors.maximum;
        Require(!std::filesystem::exists(candidate_path),
                "Second unaccepted AFT physical output already exists");
        // Preserve both previously generated physical owners: artifact only.
        Export(candidate, candidate_path);
        staged = true;
      } catch (const std::exception& failure) {
        reason = failure.what();
      }
    }
    Require(patch.GetSubMesh() == previous_patch_owner &&
                previous_physical.mesh->GetNoh(0) == previous_node &&
                previous_physical.mesh->GetElement(0) == previous_element &&
                CaptureNodeObservers(*previous_physical.mesh) == previous_observers,
            "Second AFT physical proposal mutated earlier typed owner/observers");
    Require(staged == std::filesystem::exists(candidate_path),
            "Second physical AFT output presence differs from recorded status");
    std::ostringstream out;
    out.imbue(std::locale::classic());
    out << std::setprecision(17)
        << "QUAD_SECOND_PHYSICAL_AFT_CANDIDATE"
        << " variant=" << names[variant]
        << " status=" << (staged ? "staged_unaccepted" : "rejected")
        << " source=previous_staged_physical_worst_aft"
        << " native_leaves=" << native.leaves
        << " native_quad_uv_area=" << native.uv_area
        << " native_emitted_quads=" << native.quads
        << " physical_nodes=" << physical_nodes
        << " physical_quads=" << physical_quads
        << " physical_triangles=" << physical_triangles
        << " min_facet_quality=" << min_facet_quality
        << " max_source_error=" << max_source_error
        << " original_aft_pipeline_requested=" << int(native.admitted_uv_disk)
        << " exported_candidate=" << int(staged)
        << " previous_physical_owner_preserved=1"
        << " adaptive_epochs=0\n";
    std::cout << out.str();
    if (!staged)
      std::cout << "QUAD_SECOND_PHYSICAL_AFT_REJECTION variant=" << names[variant]
                << " reason=" << reason << '\n';
  }
}

// A completely separate, non-accepted physical candidate rebuilt from the
// exact source-error-selected connected native tree and original AFT pipeline.
void ProbePhysicalConnectedBand(const Candidate& previous, PatchBezier& patch,
                                const research::MixedSurfaceResidual& source_residual,
                                const std::filesystem::path& output_prefix) {
  Require(previous.mesh && previous.quads > 0 &&
              source_residual.worst_triangle_face >= previous.quads &&
              source_residual.worst_triangle_face < previous.faces.size(),
          "Physical connected band requires a genuine preceding mixed candidate");
  const auto previous_observers = CaptureNodeObservers(*previous.mesh);
  auto* previous_node = previous.mesh->GetNoh(0);
  auto* previous_element = previous.mesh->GetElement(0);
  auto* previous_patch_owner = patch.GetSubMesh();
  const auto sample = source_residual.worst_triangle_sample_uv;
  const auto candidate_path = std::filesystem::path(output_prefix.string() + ".band-candidate.obj");
  const auto factory = [sample]() -> std::unique_ptr<Quadtree> {
    std::unique_ptr<Quadtree> ready;
    const auto band = TrialConnectedAftBand(sample, &ready);
    Require(band.admitted_uv_disk && ready && band.refined_cell_ids[0] == 6 &&
                band.refined_cell_ids[1] == 7 && band.refined_cell_ids[2] == 9 &&
                band.leaves == 28 && band.quads == 62 &&
                band.uv_area == 0.328125L,
            "Physical connected band lacks an independently admissible original native tree");
    return ready;
  };
  bool staged = false;
  std::string reason = "none";
  std::size_t physical_quads = 0;
  std::size_t physical_triangles = 0;
  std::size_t physical_nodes = 0;
  double maximum_error = 0.0;
  double maximum_triangle_error = 0.0;
  double maximum_quad_error = 0.0;
  double minimum_facet_quality = 0.0;
  try {
    // The original AFT gets its own real *band-refined* legacy front.
    // The new QUAD selector consumes a second identical but independent tree.
    auto candidate = Generate(patch, false, factory);
    CheckTypedIncidence(*candidate.mesh, candidate);
    Require(candidate.quads == 62 &&
                candidate.faces.size() > candidate.quads &&
                candidate.mesh->GetNumberNos() == candidate.uv.size(),
            "Band-refined physical proposal lacks both typed QUAD and original AFT TRI");
    std::vector<research::ResidualUv> uv;
    std::vector<research::ResidualPoint3> xyz;
    uv.reserve(candidate.uv.size());
    xyz.reserve(candidate.uv.size());
    for (std::size_t i = 0; i < candidate.uv.size(); ++i) {
      uv.push_back({candidate.uv[i].u, candidate.uv[i].v});
      const auto* node = candidate.mesh->GetNoh(static_cast<unsigned>(i));
      Require(node != nullptr, "Physical band has a null typed node");
      xyz.push_back({node->GetX(), node->GetY(), node->GetZ()});
    }
    const auto source = [&patch](const research::ResidualUv& uv_site)
        -> research::ResidualPoint3 {
      return Evaluate(patch, {uv_site[0], uv_site[1]});
    };
    const auto errors = research::MeasureMixedSurfaceResidual(
        uv, xyz, candidate.faces, source);
    Require(errors.quadrilaterals == candidate.quads &&
                errors.triangles == candidate.faces.size() - candidate.quads &&
                errors.triangles > 0 && std::isfinite(errors.maximum) &&
                std::isfinite(candidate.min_quality) && candidate.min_quality > 0.0,
            "Band candidate failed original Bezier source or facet quality admission");
    ProbeSecondNativeAftVariants(candidate, source_residual, errors);
    ProbeSecondPhysicalAftVariants(candidate, patch, source_residual, errors, output_prefix);
    physical_quads = candidate.quads;
    physical_triangles = errors.triangles;
    physical_nodes = candidate.mesh->GetNumberNos();
    maximum_error = errors.maximum;
    maximum_quad_error = errors.quad_maximum;
    maximum_triangle_error = errors.triangle_maximum;
    minimum_facet_quality = candidate.min_quality;
    Require(!std::filesystem::exists(candidate_path),
            "Nonaccepted physical band candidate output already exists");
    // Candidate-only artifact; no Patch/SubMesh owner adoption and no epoch commit.
    Export(candidate, candidate_path);
    staged = true;
  } catch (const std::exception& error) {
    reason = error.what();
  }
  Require(patch.GetSubMesh() == previous_patch_owner &&
              previous.mesh->GetNoh(0) == previous_node &&
              previous.mesh->GetElement(0) == previous_element &&
              CaptureNodeObservers(*previous.mesh) == previous_observers,
          "Rejected or staged physical band damaged the existing mixed owner");
  Require(staged == std::filesystem::exists(candidate_path),
          "Physical candidate publication status disagrees with actual file");
  std::ostringstream output;
  output.imbue(std::locale::classic());
  output << std::setprecision(17)
         << "QUAD_BAND_PHYSICAL_CANDIDATE"
         << " status=" << (staged ? "staged_unaccepted" : "rejected")
         << " source=original_native_connected_band"
         << " previous_physical_owner_preserved=1"
         << " original_aft_pipeline_requested=1"
         << " physical_quads=" << physical_quads
         << " physical_triangles=" << physical_triangles
         << " physical_nodes=" << physical_nodes
         << " max_source_error=" << maximum_error
         << " max_quad_error=" << maximum_quad_error
         << " max_aft_error=" << maximum_triangle_error
         << " min_facet_quality=" << minimum_facet_quality
         << " exported_candidate=" << int(staged)
         << " adaptive_epochs=0\n";
  std::cout << output.str();
  if (!staged)
    std::cout << "QUAD_BAND_PHYSICAL_REJECTION reason=" << reason << '\n';
}

// A complete physical owner snapshot also records the ORDERED node observers.
struct OwnerRehearsalWitness {
  SubMesh* owner = nullptr;
  std::vector<NodeAdaptive*> nodes;
  std::vector<ElementAdaptive*> elements;
  std::vector<unsigned long> node_ids;
  std::vector<Xyz> physical_xyz;
  std::vector<std::array<double, 4>> node_curvatures;
  std::vector<unsigned long> element_ids;
  std::vector<double> element_areas;
  std::vector<std::vector<ElementAdaptive*>> ordered_observers;
};

OwnerRehearsalWitness SnapshotOwnerRehearsal(SubMesh& mesh) {
  OwnerRehearsalWitness result;
  result.owner = &mesh;
  result.ordered_observers = CaptureNodeObservers(mesh);
  for (unsigned i = 0; i < mesh.GetNumberNos(); ++i) {
    auto* node = mesh.GetNoh(i);
    Require(node != nullptr, "Accepted owner has a missing physical node");
    result.nodes.push_back(node);
    result.node_ids.push_back(node->GetId());
    result.physical_xyz.push_back({node->GetX(), node->GetY(), node->GetZ()});
    result.node_curvatures.push_back(
        {node->GetGa(), node->GetGd(), node->GetHa(), node->GetHd()});
  }
  for (unsigned i = 0; i < mesh.GetNumberElements(); ++i) {
    auto* element = mesh.GetElement(i);
    Require(element != nullptr, "Accepted owner has a missing typed element");
    result.elements.push_back(element);
    result.element_ids.push_back(element->GetId());
    result.element_areas.push_back(element->GetArea());
  }
  return result;
}

void RequireOwnerRehearsalUnchanged(PatchBezier& patch,
                                   const OwnerRehearsalWitness& original) {
  Require(original.owner != nullptr && patch.GetSubMesh() == original.owner &&
              original.owner->GetPatch() == &patch &&
              original.nodes.size() == original.owner->GetNumberNos() &&
              original.elements.size() == original.owner->GetNumberElements() &&
              CaptureNodeObservers(*original.owner) == original.ordered_observers,
          "Owner rehearsal lost the previously accepted physical graph");
  for (std::size_t i = 0; i < original.nodes.size(); ++i) {
    const auto* node = original.owner->GetNoh(static_cast<unsigned>(i));
    Require(node == original.nodes[i] &&
                node->GetId() == original.node_ids[i] &&
                Xyz{node->GetX(), node->GetY(), node->GetZ()} == original.physical_xyz[i] &&
                (std::array<double, 4>{node->GetGa(), node->GetGd(),
                                       node->GetHa(), node->GetHd()}) ==
                    original.node_curvatures[i],
            "Failed physical transaction changed accepted node identity, XYZ or curvature");
  }
  for (std::size_t i = 0; i < original.elements.size(); ++i) {
    const auto* element = original.owner->GetElement(static_cast<unsigned>(i));
    Require(element == original.elements[i] &&
                element->GetId() == original.element_ids[i] &&
                element->GetArea() == original.element_areas[i],
            "Failed physical transaction changed accepted element identity or area");
  }
}

std::string ReadRehearsalOutput(const std::filesystem::path& file) {
  std::ifstream stream(file, std::ios::binary);
  Require(bool(stream), "Previously accepted physical OBJ was not readable");
  return {std::istreambuf_iterator<char>(stream), std::istreambuf_iterator<char>()};
}

// Test only: real native AFT successor of an already-published physical P1
// graph. Swaps are reversible rehearsals, not scientifically admitted epochs.
// No second artifact is published; all exceptions precede the noexcept swap.
void ProbePhysicalOwnerTransactionRehearsal(
    PatchBezier& patch, SubMesh& accepted, const Candidate& original,
    const research::MixedSurfaceResidual& first_source,
    const std::filesystem::path& output_prefix) {
  Require(accepted.GetNumberNos() == 69 && original.quads == 42 &&
              original.faces.size() == 78 && patch.GetSubMesh() == &accepted,
          "Owner transaction rehearsal requires the real previously published P1 graph");
  CheckTypedIncidence(accepted, original);
  const auto witness = SnapshotOwnerRehearsal(accepted);
  const auto previous_file = std::filesystem::path(output_prefix.string() + ".obj");
  const auto original_bytes = ReadRehearsalOutput(previous_file);

  // Recompute the source error from the ACTUAL published previous owner,
  // not merely from a separate proposal measured before publication.
  std::vector<research::ResidualUv> accepted_uv;
  std::vector<research::ResidualPoint3> accepted_xyz;
  accepted_uv.reserve(original.uv.size());
  accepted_xyz.reserve(original.uv.size());
  for (std::size_t i = 0; i < original.uv.size(); ++i) {
    accepted_uv.push_back({original.uv[i].u, original.uv[i].v});
    const auto* node = accepted.GetNoh(static_cast<unsigned>(i));
    Require(node != nullptr, "Accepted prior owner has a missing source-error node");
    accepted_xyz.push_back({node->GetX(), node->GetY(), node->GetZ()});
  }
  const auto source = [&patch](const research::ResidualUv& site)
      -> research::ResidualPoint3 { return Evaluate(patch, {site[0], site[1]}); };
  const auto actual_prior_source = research::MeasureMixedSurfaceResidual(
      accepted_uv, accepted_xyz, original.faces, source);
  Require(actual_prior_source.worst_triangle_face == first_source.worst_triangle_face &&
              actual_prior_source.worst_triangle_sample_uv ==
                  first_source.worst_triangle_sample_uv &&
              std::abs(actual_prior_source.maximum - first_source.maximum) <= 1e-14,
          "Actual published P1 owner source error diverges from original native AFT");
  const auto source_site = actual_prior_source.worst_triangle_sample_uv;
  const auto factory = [source_site]() -> std::unique_ptr<Quadtree> {
    std::unique_ptr<Quadtree> tree;
    const auto trial = TrialConnectedAftBand(source_site, &tree);
    Require(trial.admitted_uv_disk && tree && trial.leaves == 28 &&
                trial.quads == 62 && trial.uv_area == 0.328125L,
            "Owner rehearsal successor differs from the real native error-selected band");
    return tree;
  };
  unsigned injected_failures = 0;
  for (unsigned stage = 0; stage < 5; ++stage) {
    try {
      if (stage == 0)
        throw PublicationFailure("Injected owner trial failure before native reconstruction");
      auto layout = Generate(patch, stage == 1, factory);
      CheckTypedIncidence(*layout.mesh, layout);
      Require(layout.quads == 62 && layout.mesh->GetNumberNos() == 93 &&
                  layout.faces.size() == 106,
              "Owner transaction trial successor is not the genuine typed physical band");
      auto trial = CloneTypedHistory(*layout.mesh, layout, patch, stage == 2 ? 7 : -1);
      CheckTypedIncidence(*trial, layout);
      if (stage == 3) {
        // A back observer may be prepared without adopting the forward owner.
        trial->SetPatch(&patch);
        throw PublicationFailure("Injected failure after back-observer staging");
      }
      if (stage == 4)
        throw PublicationFailure("Injected failure immediately before noexcept owner swap");
      throw std::runtime_error("Physical owner failure injection did not fire");
    } catch (const PublicationFailure&) {
      ++injected_failures;
    }
    RequireOwnerRehearsalUnchanged(patch, witness);
    Require(ReadRehearsalOutput(previous_file) == original_bytes,
            "Failed physical transaction altered accepted OBJ output bytes");
  }
  Require(injected_failures == 5,
          "Accepted physical owner rehearsal did not reject every injected failure");

  auto physical = Generate(patch, false, factory);
  Require(physical.quads == 62 && physical.mesh->GetNumberNos() == 93 &&
              physical.faces.size() == 106,
          "Owner rehearsal success is not the actual next native AFT physical band");
  auto staged = CloneTypedHistory(*physical.mesh, physical, patch, -1);
  CheckTypedIncidence(*staged, physical);
  Require(staged->GetNoh(0) != witness.nodes.front() &&
              staged->GetElement(0) != witness.elements.front(),
          "Replacement typed physical history aliases the accepted owner");

  // No filesystem mutation or unknown-throwing work occurs after this point.
  // This real patch swap is deliberately REVERSED before the function returns.
  {
    struct RestorePrevious final {
      PatchBezier& patch;
      SubMesh* prior;
      ~RestorePrevious() noexcept { patch.SetSubMesh(prior); }
    } restore{patch, &accepted};
    staged->SetPatch(&patch);
    patch.SetSubMesh(staged.get());
    Require(patch.GetSubMesh() == staged.get() &&
                staged->GetPatch() == &patch,
            "Noexcept owner rehearsal could not temporarily adopt the real typed successor");
    CheckTypedIncidence(*staged, physical);
    patch.SetSubMesh(&accepted);
    staged->SetPatch(nullptr);
  }
  RequireOwnerRehearsalUnchanged(patch, witness);
  Require(ReadRehearsalOutput(previous_file) == original_bytes,
          "Temporary owner swap modified the original published physical OBJ");
  CheckTypedIncidence(*staged, physical);
  std::cout << "QUAD_OWNER_TRANSACTION_REHEARSAL"
            << " source=published_previous_P1_real_AFT"
            << " prior_nodes=69 prior_quads=42 prior_triangles=36"
            << " next_nodes=93 next_quads=62 next_triangles=44"
            << " injected_failures=" << injected_failures
            << " temporary_noexcept_swaps=1"
            << " reverted_to_previous_owner=1"
            << " ordered_node_observers_preserved=1"
            << " node_curvature_and_element_area_preserved=1"
            << " previous_obj_bytes_unchanged=1"
            << " measured_after_actual_prior_owner_publication=1"
            << " accepted_adaptive_epochs=0\n";
}

} // namespace

int RunControlledPatch(const application::RuntimeConfig& config) {
  Geometry geometry;
  Models3d models;
  if (config.input_model == "builtin:curva_bezier")
    models.ModelCurvaBezier(&geometry);
  else {
    PatchReader reader;
    reader.ReaderFilePatches(&geometry, config.input_model);
  }
  Require(geometry.GetNumberPatches() == 1, "Controlled QUAD accepts exactly one source patch");
  auto* patch = dynamic_cast<PatchBezier*>(geometry.GetPatch(0));
  Require(patch != nullptr, "Controlled source must be Bezier");
  auto candidate = Generate(*patch, false);
  ProbeTypedHistory(*candidate.mesh, candidate, *patch);
  ProbeMixedCurvature(*candidate.mesh, candidate);
  ProbePhysicalQuadQuality(*candidate.mesh, candidate, *patch);
  const auto mixed_residual = ProbeMixedSurfaceResidual(candidate, *patch);
  ProbeNativeTreeAlternatives(candidate, mixed_residual);
  ProbeConnectedAftBand(candidate, mixed_residual);
  ProbePhysicalConnectedBand(candidate, *patch, mixed_residual, config.output_prefix);
  Export(candidate, config.output_prefix + ".obj");
  candidate.mesh->SetPatch(patch);
  patch->SetSubMesh(candidate.mesh.get());
  std::unique_ptr<SubMesh> accepted;
  accepted.swap(candidate.mesh);
  std::cout << "QUAD_CONTROLLED_PATCH quads=" << candidate.quads
            << " triangles=" << candidate.faces.size() - candidate.quads
            << " nodes=" << accepted->GetNumberNos()
            << " boundary=16 UV_disk=1 overlap=0 min_alignment=" << candidate.min_alignment
            << " min_facet_quality=" << candidate.min_quality << " ids_unique=1 published=1\n";
  ProbePhysicalOwnerTransactionRehearsal(*patch, *accepted, candidate,
                                        mixed_residual, config.output_prefix);
  if (config.quad_verify_rollback) {
    auto* old = accepted.get();
    auto* node = old->GetNoh(0);
    auto* element = old->GetElement(0);
    std::vector<std::vector<ElementAdaptive*>> observers;
    for (unsigned i = 0; i < old->GetNumberNos(); ++i) {
      const auto& values = old->GetNoh(i)->GetElements();
      observers.emplace_back(values.begin(), values.end());
    }
    try {
      auto rejected = Generate(*patch, true);
      (void)rejected;
    } catch (const PublicationFailure& error) {
      Require(accepted.get() == old && patch->GetSubMesh() == old && old->GetNoh(0) == node &&
                  old->GetElement(0) == element,
              "Rollback damaged the accepted physical owner");
      for (unsigned i = 0; i < old->GetNumberNos(); ++i) {
        const auto& values = old->GetNoh(i)->GetElements();
        Require(std::vector<ElementAdaptive*>(values.begin(), values.end()) == observers[i],
                "Rollback changed accepted node observers");
      }
      std::cout << "QUAD_ROLLBACK preserved=1 previous_nonempty=1 reason=" << error.what() << '\n';
      return 1;
    }
    throw std::runtime_error("Expected publication failure did not occur");
  }
  return 0;
}
} // namespace apmesh::quad
