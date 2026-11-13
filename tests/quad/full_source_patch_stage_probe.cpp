#include "disjoint_owner_stage.h"
#include "owned_aft_front.h"
#include "interior_template_dispatch.h"
#include "front_interface_audit.h"

#include "crab_mesh/aft/boundary.h"
#include "crab_mesh/aft/quadtree.h"
#include "crab_mesh/aft/quadtree_cell.h"
#include "data/curve/curve_adaptive_parametric.h"
#include "data/geometry.h"
#include "data/patch/patch_bezier.h"
#include "input_output/patch_reader.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace {
using apmesh::quad::InteriorTemplateDispatcher;
using apmesh::quad::InteriorTemplateMode;
using apmesh::quad::OwnedQuadAftFront;
using apmesh::quad::SnapshotLegacyFront;
using apmesh::quad::UvVertex;
using apmesh::quad::research::DisjointOwnerStage;
using apmesh::quad::research::QuadrilateralAdaptive;
using Par2DJMesh::AFT::Boundary;
using Par2DJMesh::AFT::Quadtree;
using Par2DJMesh::AFT::QuadtreeCell;
using Par2DJMesh::Basics::Face;
using Par2DJMesh::Basics::Vertex;

void Require(bool condition, const char* message) {
  if (!condition) throw std::runtime_error(message);
}

std::unique_ptr<Quadtree> MakeSourceTree(bool refined) {
  auto tree = std::make_unique<Quadtree>();
  auto boundary = std::make_unique<Boundary>();
  // Retain the already-audited R2b2 fixed UV chart sampling, not AdaptCurve.
  for (int side = 0; side < 4; ++side) {
    for (int step = 0; step < 4; ++step) {
      const double t = 0.25 * static_cast<double>(step);
      const UvVertex uv = side == 0 ? UvVertex{t, 0.0}
          : side == 1 ? UvVertex{1.0, t}
          : side == 2 ? UvVertex{1.0 - t, 1.0}
                      : UvVertex{0.0, 1.0 - t};
      boundary->addVertex(uv.u, uv.v, nullptr);
    }
  }
  Require(boundary->close(nullptr), "Native boundary failed to close");
  tree->setBoundary(boundary.release());
  auto low = std::make_unique<Vertex>(0.0, 0.0);
  auto high = std::make_unique<Vertex>(1.0, 1.0);
  auto root = std::make_unique<QuadtreeCell>(
      tree->getCellId(), tree.get(), low.get(), high.get());
  tree->setRoot(root.get());
  root.release();
  low.release();
  high.release();
  tree->getRoot()->subdivideToLevel(2);
  if (refined) {
    bool found = false;
    for (auto* leaf : tree->getLeaves()) {
      if (leaf->getMin()->getX() == 0.25 &&
          leaf->getMin()->getY() == 0.25) {
        leaf->subdivideToLevel(3);
        found = true;
        break;
      }
    }
    Require(found, "Refined original chart leaf was not found");
  }
  return tree;
}

UvVertex PointRule(const apmesh::quad::LeafPolygonOrigin&,
                   const std::vector<UvVertex>& polygon) {
  UvVertex center{0.0, 0.0};
  for (const auto& uv : polygon) {
    center.u += uv.u;
    center.v += uv.v;
  }
  center.u /= static_cast<double>(polygon.size());
  center.v /= static_cast<double>(polygon.size());
  return center;
}

using Xyz = std::array<double, 3>;
Xyz Values(const PointAdaptive& p) {
  return {p.GetX(), p.GetY(), p.GetZ()};
}
Xyz Values(const VectorAdaptive& p) {
  return {p.GetX(), p.GetY(), p.GetZ()};
}
Xyz Subtract(const Xyz& a, const Xyz& b) {
  return {a[0] - b[0], a[1] - b[1], a[2] - b[2]};
}
Xyz Cross(const Xyz& a, const Xyz& b) {
  return {a[1] * b[2] - a[2] * b[1],
          a[2] * b[0] - a[0] * b[2],
          a[0] * b[1] - a[1] * b[0]};
}
double Dot(const Xyz& a, const Xyz& b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}
double Norm(const Xyz& a) { return std::sqrt(Dot(a, a)); }
bool Finite(const Xyz& a) {
  return std::isfinite(a[0]) && std::isfinite(a[1]) &&
         std::isfinite(a[2]);
}
Xyz Evaluate(PatchBezier& patch, UvVertex uv) {
  Require(std::isfinite(uv.u) && std::isfinite(uv.v) &&
              uv.u >= 0.0 && uv.u <= 1.0 &&
              uv.v >= 0.0 && uv.v <= 1.0,
          "Real source chart UV escaped its parameter domain");
  const Xyz xyz = Values(patch.Parameterize(uv.u, uv.v));
  const Xyz qu = Values(patch.Qu(uv.u, uv.v));
  const Xyz qv = Values(patch.Qv(uv.u, uv.v));
  Require(Finite(xyz) && Finite(qu) && Finite(qv) &&
              Norm(Cross(qu, qv)) > 1e-12,
          "Real source chart has an invalid differential Jacobian");
  return xyz;
}

void CheckFaceOrientation(PatchBezier& patch,
                          const std::array<UvVertex, 3>& uv) {
  const UvVertex middle{
      (uv[0].u + uv[1].u + uv[2].u) / 3.0,
      (uv[0].v + uv[1].v + uv[2].v) / 3.0};
  const Xyz a = Evaluate(patch, uv[0]);
  const Xyz b = Evaluate(patch, uv[1]);
  const Xyz c = Evaluate(patch, uv[2]);
  const Xyz source = Cross(Values(patch.Qu(middle.u, middle.v)),
                           Values(patch.Qv(middle.u, middle.v)));
  const Xyz facet = Cross(Subtract(b, a), Subtract(c, a));
  const double denominator = Norm(source) * Norm(facet);
  Require(std::isfinite(denominator) && denominator > 1e-14 &&
              Dot(source, facet) / denominator > 0.0,
          "Native QUAD/AFT physical facet is collapsed or inverted");
}

void CheckOriginalSourceBoundary(PatchBezier& patch) {
  // This checks each original patch against its own source Curve objects.
  // It does not certify interpatch subdivisions or approved sheet pairing.
  for (unsigned side = 0; side < 4; ++side) {
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(patch.GetCurve(side));
    Require(curve != nullptr, "Missing original parametric source curve");
    for (unsigned step = 0; step <= 4; ++step) {
      const double t = static_cast<double>(step) / 4.0;
      const UvVertex uv = side == 0 ? UvVertex{t, 0.0}
          : side == 1 ? UvVertex{1.0, t}
          : side == 2 ? UvVertex{t, 1.0}
                      : UvVertex{0.0, t};
      const double source_t = patch.IsCurveReversed(side) ? 1.0 - t : t;
      const Xyz from_patch = Evaluate(patch, uv);
      const Xyz from_curve = Values(curve->FindPointByParameter(source_t));
      Require(Finite(from_curve) &&
                  Norm(Subtract(from_patch, from_curve)) <=
                      2e-7 * std::max(1.0, Norm(from_patch)),
              "Original source curve and patch boundary do not agree");
    }
  }
}

struct ChartCounts {
  std::size_t nodes = 0;
  std::size_t quads = 0;
  std::size_t tris = 0;
};

std::unique_ptr<SubMesh> BuildOriginalAftChart(
    PatchBezier& patch, unsigned patch_id, bool refined, ChartCounts& counts) {
  Require(patch.GetSubMesh() == nullptr,
          "Original patch already owns a physical SubMesh observer");
  CheckOriginalSourceBoundary(patch);
  auto original = MakeSourceTree(refined);
  Require(original->makeTemplateBasedMesh() ==
              Par2DJMesh::AFT::QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
          "Original reference TRI template extraction failed");
  const auto original_front = SnapshotLegacyFront(*original);
  auto tree = MakeSourceTree(refined);
  InteriorTemplateDispatcher selector(*tree);
  auto selected = selector.Select(InteriorTemplateMode::ExperimentalQuad,
                                  PointRule);
  auto* tree_owner = tree.get();
  auto aft = std::make_unique<OwnedQuadAftFront>(
      tree_owner->getBoundary(), tree_owner);
  tree.release();
  const auto seeded = aft->Seed(selected, original_front);
  Require(seeded.patch_boundary_edges == 16U &&
              seeded.quad_interface_edges == (refined ? 20U : 16U),
          "Native source chart QUAD front incidence changed");
  for (auto* edge : aft->getBoundary()->getEdges()) {
    aft->getQuadtree()->findCell(edge);
    Require(edge->getCell() != nullptr,
            "Original AFT chart boundary lacks a source cell");
  }
  const auto exterior = aft->AttemptExteriorTriangulation(selected);
  Require(exterior.exterior_triangles > 0 &&
              exterior.front_drained && exterior.triangles_positive &&
              exterior.seam_orientation_complete &&
              exterior.seam_vertices_unchanged &&
              exterior.uv_area_balanced && exterior.spatial_overlap_tested &&
              exterior.no_spatial_overlap &&
              exterior.seam_edges_with_one_tri == seeded.quad_interface_edges,
          "Original AFT chart was not locally admissible");

  auto chart = std::make_unique<SubMesh>();
  std::map<std::pair<double, double>, NodeAdaptive*> local_nodes;
  const auto node_at = [&](UvVertex uv) -> NodeAdaptive* {
    const auto key = std::make_pair(uv.u, uv.v);
    const auto existing = local_nodes.find(key);
    if (existing != local_nodes.end()) return existing->second;
    const Xyz xyz = Evaluate(patch, uv);
    auto node = std::make_unique<NodeAdaptive>(xyz[0], xyz[1], xyz[2]);
    node->SetId(static_cast<unsigned long>(
        100000U * (patch_id + 1U) + local_nodes.size() + 1U));
    NodeAdaptive* observed = node.get();
    chart->AddNoh(std::move(node));
    local_nodes.emplace(key, observed);
    return observed;
  };

  for (const auto& quad : selected.uv_quads.quads) {
    QuadrilateralAdaptive::Parameters uv{};
    QuadrilateralAdaptive::Nodes nodes{};
    UvVertex middle{0.0, 0.0};
    for (unsigned corner = 0; corner < 4; ++corner) {
      const auto& p = selected.uv_quads.vertices[quad.vertices[corner]];
      uv[corner] = {p.u, p.v};
      nodes[corner] = node_at(p);
      middle.u += p.u;
      middle.v += p.v;
    }
    middle.u /= 4.0;
    middle.v /= 4.0;
    CheckFaceOrientation(patch, {{selected.uv_quads.vertices[quad.vertices[0]],
                                  selected.uv_quads.vertices[quad.vertices[1]],
                                  selected.uv_quads.vertices[quad.vertices[2]]}});
    CheckFaceOrientation(patch, {{selected.uv_quads.vertices[quad.vertices[0]],
                                  selected.uv_quads.vertices[quad.vertices[2]],
                                  selected.uv_quads.vertices[quad.vertices[3]]}});
    const VectorAdaptive reference =
        patch.Qu(middle.u, middle.v) * patch.Qv(middle.u, middle.v);
    chart->AddElement(std::make_unique<QuadrilateralAdaptive>(
        nodes, uv, reference));
    ++counts.quads;
  }
  for (Face* face : aft->Triangles()) {
    const std::array<UvVertex, 3> uv{{
        {face->getV1()->getX(), face->getV1()->getY()},
        {face->getV2()->getX(), face->getV2()->getY()},
        {face->getV3()->getX(), face->getV3()->getY()},
    }};
    CheckFaceOrientation(patch, uv);
    auto triangle = std::make_unique<TriangleAdaptive>(
        node_at(uv[0]), node_at(uv[1]), node_at(uv[2]));
    triangle->SetParametersN1({uv[0].u, uv[0].v});
    triangle->SetParametersN2({uv[1].u, uv[1].v});
    triangle->SetParametersN3({uv[2].u, uv[2].v});
    chart->AddElement(std::move(triangle));
    ++counts.tris;
  }
  counts.nodes = chart->GetNumberNos();
  Require(counts.quads == selected.uv_quads.quads.size() &&
              counts.tris == aft->Triangles().size() &&
              counts.quads > 1U && counts.tris > 1U &&
              counts.nodes > 7U &&
              chart->GetNumberElements() == counts.quads + counts.tris,
          "Incomplete original AFT physical QUAD/TRI chart inventory");
  DisjointOwnerStage::CheckChart(*chart);
  Require(patch.GetSubMesh() == nullptr,
          "Research chart creation changed original Patch forward observer");
  return chart;
}

void RunSource(const std::string& source, unsigned expected, bool refined) {
  Geometry original;
  PatchReader reader;
  Require(reader.ReaderFilePatches(&original, source) == &original &&
              original.GetNumberPatches() == expected,
          "Original source model does not match chart cardinality");
  std::unique_ptr<MeshAdaptive> active = std::make_unique<MeshAdaptive>();
  MeshAdaptive* const prior = active.get();
  const std::array<unsigned, 3> faults{{0U, expected / 2U, expected}};
  unsigned rejected = 0;
  for (const unsigned fault : faults) {
    DisjointOwnerStage staged(expected);
    for (unsigned i = 0; i < expected; ++i) {
      auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(i));
      Require(patch != nullptr, "Original input contains a non-Bezier patch");
      ChartCounts ignored;
      staged.Add(BuildOriginalAftChart(*patch, i, refined, ignored));
    }
    bool threw = false;
    try {
      staged.Replace(active, static_cast<int>(fault));
    } catch (const std::runtime_error&) {
      threw = true;
    }
    Require(threw && active.get() == prior &&
                active->GetNumberSubMeshesAdaptive() == 0U,
            "Fault changed an existing detached physical owner");
    ++rejected;
  }

  DisjointOwnerStage staged(expected);
  ChartCounts total;
  for (unsigned i = 0; i < expected; ++i) {
    auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(i));
    Require(patch != nullptr, "Missing original source Bezier chart");
    ChartCounts count;
    staged.Add(BuildOriginalAftChart(*patch, i, refined, count));
    total.nodes += count.nodes;
    total.quads += count.quads;
    total.tris += count.tris;
  }
  staged.Replace(active);
  Require(active.get() != prior &&
              active->GetNumberSubMeshesAdaptive() == expected,
          "Complete native QUAD/AFT owner stage was not replaced");
  std::set<const NodeAdaptive*> unique_nodes;
  for (unsigned i = 0; i < expected; ++i) {
    const SubMesh* chart = active->GetSubMeshAdaptiveByPosition(i);
    Require(chart != nullptr, "Missing staged native source chart");
    DisjointOwnerStage::CheckChart(*chart);
    for (unsigned j = 0; j < chart->GetNumberNos(); ++j)
      Require(unique_nodes.insert(chart->GetNoh(j)).second,
              "Native AFT chart shares another patch's physical node");
    auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(i));
    Require(patch != nullptr && patch->GetSubMesh() == nullptr &&
                chart->GetPatch() == nullptr,
            "Source Patch/SubMesh observer relation was modified");
  }
  Require(unique_nodes.size() == total.nodes,
          "Native chart physical node inventory is inconsistent");
  std::cout << "R2C2_FULL_SOURCE_AFT"
            << " original_patches=" << expected
            << " physical_nodes=" << total.nodes
            << " typed_QUAD=" << total.quads
            << " typed_TRI=" << total.tris
            << " rejected_injected_stages=" << rejected
            << " per_patch_source_boundary_audited=1"
            << " native_AFT_exterior=1"
            << " native_Quadtree_templates=1"
            << " distinct_patch_node_owners=1"
            << " patch_observers_touched=0"
            << " interpatch_seam_conformity_proved=0"
            << " shared_node_welding=0"
            << " global_physical_mesh_published=0"
            << " advisor_sheet_approved=0\n";
}
}  // namespace

int main(int argc, char** argv) {
  try {
    Require(argc == 3, "Expected original Eistute and Book .bp sources");
    RunSource(argv[1], 4U, false);
    RunSource(argv[2], 28U, true);
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "R2c2 full original AFT detached staging failed: "
              << error.what() << '\n';
    return 1;
  }
}
