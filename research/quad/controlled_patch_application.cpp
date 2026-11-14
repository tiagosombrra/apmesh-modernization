#include "controlled_patch_application.h"
#include "application/runtime_config.h"
#include "physical_quadrilateral_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "data/triangle_adaptive.h"
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

Candidate Generate(PatchBezier& patch, bool fail_before_commit) {
  ValidateSourceCurves(patch);
  auto original = MakeSourceTree(true);
  Require(original->makeTemplateBasedMesh() == Par2DJMesh::AFT::QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
          "Original interior TRI reference failed");
  const auto front = SnapshotLegacyFront(*original);
  auto tree = MakeSourceTree(true);
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
void ProbeMixedSurfaceResidual(const Candidate& candidate, PatchBezier& patch) {
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
  ProbeMixedSurfaceResidual(candidate, *patch);
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
