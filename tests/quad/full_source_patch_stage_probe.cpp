#include "disjoint_owner_stage.h"
#include "owned_aft_front.h"
#include "interior_template_dispatch.h"
#include "front_interface_audit.h"

#include "crab_mesh/aft/boundary.h"
#include "crab_mesh/aft/quadtree.h"
#include "crab_mesh/aft/quadtree_cell.h"
#include "data/curve/curve_adaptive_parametric.h"
#include "data/geometry.h"
#include "adapter/adapter.h"
#include "crab_mesh/performer/ranged_id_manager.h"
#include "generator/curve_publication.h"
#include "generator/curve_sample_lifetime.h"
#include "generator/curve_sample_graph.h"
#include "generator/initial_mesh.h"
#include "data/patch/patch_bezier.h"
#include "input_output/patch_reader.h"
#include "shared_curve_audit.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

// The original serial curve sorter uses this process-local comparator scratch.
extern std::vector<CurveAdaptiveParametric*> ptr_aux;

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

// Read-only snapshots from actual staged SubMesh boundary nodes. The original
// source Curve pointer groups geometric incidences, not approved physical sheets.
struct BoundarySite {
  const NodeAdaptive* node = nullptr;
  Xyz physical{};
  Xyz source{};
};

struct SourceCurveIncidence {
  const CurveAdaptiveParametric* curve = nullptr;
  unsigned patch = 0;
  unsigned side = 0;
  std::array<BoundarySite, 5> sites{};
};

struct SourceSeamReport {
  std::size_t source_incidences = 0;
  std::size_t source_site_checks = 0;
  std::size_t shared_curve_groups = 0;
  std::size_t shared_incidence_pairs = 0;
  std::size_t pairwise_source_site_checks = 0;
  std::size_t max_source_valence = 0;
};

bool NearSource(const Xyz& a, const Xyz& b) {
  return Finite(a) && Finite(b) &&
         Norm(Subtract(a, b)) <= 2e-7 *
             std::max({1.0, Norm(a), Norm(b)});
}

// Neither source positions nor patch node observers are changed. This only
// checks fixed-quarter source-knot coincidence and distinct physical owners.
SourceSeamReport AuditReadOnlySourceSeams(
    const std::vector<SourceCurveIncidence>& incidences,
    unsigned expected_max_valence) {
  Require(!incidences.empty(), "No source chart boundary incidences");
  std::set<std::pair<unsigned, unsigned>> sides;
  std::map<const CurveAdaptiveParametric*,
           std::vector<const SourceCurveIncidence*>> grouped;
  SourceSeamReport report;
  report.source_incidences = incidences.size();
  for (const auto& incidence : incidences) {
    Require(incidence.curve != nullptr && incidence.side < 4U &&
                sides.insert({incidence.patch, incidence.side}).second,
            "Malformed, duplicated or missing source chart incidence");
    for (unsigned t = 0; t < 5U; ++t) {
      const auto& site = incidence.sites[t];
      Require(site.node != nullptr &&
                  NearSource(site.physical, site.source),
              "Physical AFT boundary node disagrees with source curve knot");
      ++report.source_site_checks;
    }
    grouped[incidence.curve].push_back(&incidence);
  }
  for (const auto& group : grouped) {
    const auto& owners = group.second;
    report.max_source_valence =
        std::max(report.max_source_valence, owners.size());
    if (owners.size() < 2U) continue;
    ++report.shared_curve_groups;
    for (std::size_t i = 0; i < owners.size(); ++i) {
      for (std::size_t j = i + 1; j < owners.size(); ++j) {
        Require(owners[i]->patch != owners[j]->patch,
                "Duplicate patch owner on one original shared curve");
        ++report.shared_incidence_pairs;
        for (unsigned t = 0; t < 5U; ++t) {
          const auto& left = owners[i]->sites[t];
          const auto& right = owners[j]->sites[t];
          Require(left.node != right.node &&
                      NearSource(left.physical, right.physical) &&
                      NearSource(left.source, right.source),
                  "Original shared curve nodes mismatch or share physical ownership");
          ++report.pairwise_source_site_checks;
        }
      }
    }
  }
  Require(report.shared_curve_groups > 0U &&
              report.pairwise_source_site_checks > 0U &&
              report.max_source_valence == expected_max_valence,
          "Original high-valence source curve incidence is not represented");
  return report;
}

void CheckSourceSeamNegativeControls(
    const std::vector<SourceCurveIncidence>& incidences,
    unsigned expected_max_valence) {
  const auto rejected = [&](std::vector<SourceCurveIncidence> changed,
                            const char* reason) {
    bool failed = false;
    try {
      static_cast<void>(
          AuditReadOnlySourceSeams(changed, expected_max_valence));
    } catch (const std::runtime_error&) {
      failed = true;
    }
    Require(failed, reason);
  };
  auto distorted = incidences;
  distorted.front().sites[2].physical[0] += 1.0;
  rejected(std::move(distorted),
           "Injected physical boundary distortion escaped source audit");

  auto missing = incidences;
  missing.front().sites[0].node = nullptr;
  rejected(std::move(missing),
           "Missing source-owned boundary node escaped source audit");

  auto wrong_curve = incidences;
  wrong_curve.front().curve = nullptr;
  rejected(std::move(wrong_curve),
           "Missing original curve provenance escaped source audit");

  // All real source-patch node pointers must remain disjoint even if their
  // sampled XYZ positions coincide exactly.
  auto aliased = incidences;
  bool found_shared = false;
  for (std::size_t i = 0; i < aliased.size() && !found_shared; ++i) {
    for (std::size_t j = i + 1; j < aliased.size(); ++j) {
      if (aliased[i].curve == aliased[j].curve &&
          aliased[i].patch != aliased[j].patch) {
        aliased[j].sites[0].node = aliased[i].sites[0].node;
        found_shared = true;
        break;
      }
    }
  }
  Require(found_shared, "No shared original curve for alias rejection");
  rejected(std::move(aliased),
           "Unauthorized original physical node alias escaped source audit");
}

struct ChartCounts {
  std::size_t nodes = 0;
  std::size_t quads = 0;
  std::size_t tris = 0;
  std::array<SourceCurveIncidence, 4> source_sides{};
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
  // Extract only sites that actually exist in the typed physical AFT output.
  // A source sample that is not represented by a candidate node is a failure,
  // not permission to manufacture a missing physical seam node.
  for (unsigned side = 0; side < 4U; ++side) {
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(patch.GetCurve(side));
    Require(curve != nullptr, "Original source boundary curve is unavailable");
    auto& incidence = counts.source_sides[side];
    incidence.curve = curve;
    incidence.patch = patch_id;
    incidence.side = side;
    for (unsigned k = 0; k < 5U; ++k) {
      const double source_t = static_cast<double>(k) / 4.0;
      const double local_t =
          patch.IsCurveReversed(side) ? 1.0 - source_t : source_t;
      const UvVertex uv = side == 0U ? UvVertex{local_t, 0.0}
          : side == 1U ? UvVertex{1.0, local_t}
          : side == 2U ? UvVertex{local_t, 1.0}
                       : UvVertex{0.0, local_t};
      const auto it = local_nodes.find({uv.u, uv.v});
      Require(it != local_nodes.end() && it->second != nullptr,
              "Native typed QUAD/AFT physical boundary is missing a source knot");
      const auto* node = it->second;
      incidence.sites[k] = {
          node, {node->GetX(), node->GetY(), node->GetZ()},
          Values(curve->FindPointByParameter(source_t))};
    }
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

// Source-only original two-pass Adapter experiment on one genuine high-valence
// curve per original model. It is independent of the detached QUAD/AFT charts.
struct NativeAdaptedSite {
  double parameter = 0.0;
  unsigned long source_node_id = 0UL;
  Xyz physical{};
};

using NativeAdaptedSites = std::vector<NativeAdaptedSite>;

NativeAdaptedSites SnapshotNativeAdaptedSource(
    CurveAdaptiveParametric& source) {
  const std::vector<double> t(source.parameters_.begin(),
                              source.parameters_.end());
  const auto& points = source.GetPoints();
  Require(t.size() == points.size() && t.size() > 2U,
          "Real two-pass Adapter did not produce a refined physical curve");
  NativeAdaptedSites sites;
  sites.reserve(t.size());
  auto point = points.begin();
  std::set<unsigned long> node_ids;
  for (std::size_t i = 0; i < t.size(); ++i, ++point) {
    auto* physical = dynamic_cast<NodeAdaptive*>(*point);
    Require(physical && physical->GetId() > 0UL &&
                node_ids.insert(physical->GetId()).second &&
                std::isfinite(t[i]) && t[i] >= 0.0 && t[i] <= 1.0 &&
                (i == 0U || t[i] > t[i - 1U]),
            "Real two-pass Adapter output has invalid ordered samples or IDs");
    sites.push_back({t[i], physical->GetId(), Values(*physical)});
  }
  Require(t.front() == 0.0 && t.back() == 1.0,
          "Real original adapted curve dropped source endpoints");
  return sites;
}

struct NativeAdaptedReport {
  std::size_t intervals = 0;
  std::size_t source_sites = 0;
  std::size_t incidences = 0;
  std::size_t full_incidence_site_checks = 0;
  std::size_t full_incidence_interval_checks = 0;
  std::size_t geometric_incidence_pairs = 0;
  std::size_t pairwise_interval_matches = 0;
};

NativeAdaptedReport AuditNativeAdapterSourceIntervals(
    Geometry& original, CurveAdaptiveParametric& source,
    const NativeAdaptedSites& samples, unsigned expected_valence) {
  Require(samples.size() > 2U && expected_valence > 2U,
          "Original source Adapter interval audit requires adaptive samples");
  NativeAdaptedReport result;
  result.source_sites = samples.size();
  result.intervals = samples.size() - 1U;
  const auto observed = SnapshotNativeAdaptedSource(source);
  Require(observed.size() == samples.size(),
          "Original adapted source curve changed during a read-only audit");
  for (std::size_t i = 0; i < samples.size(); ++i) {
    Require(samples[i].source_node_id == observed[i].source_node_id &&
                samples[i].parameter == observed[i].parameter &&
                NearSource(samples[i].physical, observed[i].physical) &&
                NearSource(samples[i].physical,
                           Values(source.FindPointByParameter(samples[i].parameter))),
            "Original source Adapter sample was forged or mutated");
  }
  std::vector<unsigned> incident_patches;
  for (unsigned p = 0; p < original.GetNumberPatches(); ++p) {
    auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(p));
    Require(patch != nullptr, "Original source patch type changed");
    for (unsigned side = 0; side < patch->GetNumBerCurves(); ++side) {
      if (patch->GetCurve(side) != &source) continue;
      Require(std::find(incident_patches.begin(), incident_patches.end(), p) ==
                  incident_patches.end(),
              "High-valence source curve occurs twice in one patch");
      incident_patches.push_back(p);
      ++result.incidences;
      for (std::size_t i = 0; i < samples.size(); ++i) {
        const double local = patch->IsCurveReversed(side)
            ? 1.0 - samples[i].parameter : samples[i].parameter;
        const UvVertex uv = side == 0U ? UvVertex{local, 0.0}
            : side == 1U ? UvVertex{1.0, local}
            : side == 2U ? UvVertex{local, 1.0}
                         : UvVertex{0.0, local};
        Require(NearSource(samples[i].physical,
                           Values(patch->Parameterize(uv.u, uv.v))),
                "Original adapted source parameter did not match patch XYZ");
        ++result.full_incidence_site_checks;
      }
      for (std::size_t i = 1; i < samples.size(); ++i) {
        Require(samples[i].parameter > samples[i - 1U].parameter &&
                    samples[i].source_node_id != samples[i - 1U].source_node_id,
                "Original dynamically adapted source interval collapsed");
        ++result.full_incidence_interval_checks;
      }
    }
  }
  Require(result.incidences == expected_valence &&
              result.incidences == source.GetNumBerPatches() &&
              result.full_incidence_site_checks ==
                  samples.size() * expected_valence &&
              result.full_incidence_interval_checks ==
                  result.intervals * expected_valence,
          "Original source high-valence adaptation coverage incomplete");
  result.geometric_incidence_pairs =
      result.incidences * (result.incidences - 1U) / 2U;
  result.pairwise_interval_matches =
      result.geometric_incidence_pairs * result.intervals;
  // A shared source CurveAdaptiveParametric owns one parameter partition;
  // these are geometric pairwise interval equalities, not physical joins.
  return result;
}

unsigned RejectAlteredAdapterSnapshots(
    Geometry& original, CurveAdaptiveParametric& source,
    const NativeAdaptedSites& valid, unsigned valence) {
  unsigned rejected = 0;
  const auto must_reject = [&](NativeAdaptedSites samples) {
    bool failed = false;
    try {
      static_cast<void>(AuditNativeAdapterSourceIntervals(
          original, source, samples, valence));
    } catch (const std::runtime_error&) {
      failed = true;
    }
    Require(failed, "Invalid original Adapter source partition was admitted");
    ++rejected;
  };
  auto distorted = valid;
  distorted[1].physical[0] += 1.0;
  must_reject(std::move(distorted));
  auto dropped = valid;
  dropped.erase(dropped.begin() + 1);
  must_reject(std::move(dropped));
  auto reordered = valid;
  std::swap(reordered[0], reordered[1]);
  must_reject(std::move(reordered));
  auto alias = valid;
  alias[1].source_node_id = alias[0].source_node_id;
  must_reject(std::move(alias));
  auto wrong_param = valid;
  wrong_param[1].parameter =
      (wrong_param[0].parameter + wrong_param[1].parameter) / 2.0;
  must_reject(std::move(wrong_param));
  return rejected;
}

// Research-only original source-directed native AFT Boundary, not a QUAD
// mesh, source curve owner, or cross-chart physical node sharing contract.
struct DetachedSourceBoundary {
  std::unique_ptr<Boundary> boundary;
  std::vector<std::unique_ptr<NodeAdaptive>> physical_copies;
  apmesh::quad::AdapterBoundaryCapture capture;
  std::size_t adapted_side = 0;
};

DetachedSourceBoundary BuildDetachedSourceBoundaryImpl(
    PatchBezier& patch, unsigned patch_id, CurveAdaptiveParametric* adapted,
    bool all_sides, bool corrupt_first_copy = false) {
  DetachedSourceBoundary result;
  result.boundary = std::make_unique<Boundary>();
  std::map<Vertex*, NodeAdaptive*> copied_nodes;
  std::size_t adapted_sides = 0;
  CurveAdaptiveParametric* last_curve = nullptr;
  bool last_reversed = false;
  for (unsigned side = 0; side < 4U; ++side) {
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(patch.GetCurve(side));
    Require(curve != nullptr, "Native detached contour has a missing source curve");
    const std::vector<double> parameters(curve->parameters_.begin(),
                                         curve->parameters_.end());
    Require(parameters.size() == curve->GetNumBerPoints() &&
                parameters.size() >= 2U && parameters.front() == 0.0 &&
                parameters.back() == 1.0,
            "Native detached contour has incomplete actual source parameters");
    const bool reversed = patch.IsCurveReversed(side);
    if (all_sides) {
      Require(parameters.size() > 2U,
              "R2c7 source curve was not actually adapted on all four sides");
    } else if (curve == adapted) {
      Require(parameters.size() > 2U,
              "Original high-valence source curve did not adapt");
      result.adapted_side = side;
      ++adapted_sides;
    } else {
      Require(parameters.size() == 2U,
              "Untouched source side was silently adapted or replaced");
    }
    for (std::size_t i = 0; i < parameters.size(); ++i) {
      Require(std::isfinite(parameters[i]) &&
                  (i == 0U || parameters[i] > parameters[i - 1U]),
              "Original source contour parameters are not strictly ordered");
    }
    for (std::size_t offset = 0; offset + 1U < parameters.size(); ++offset) {
      // Use the original serial Adapter's CCW traversal and curve reversal.
      const std::size_t index =
          reversed ? (side < 2U ? parameters.size() - 1U - offset : offset)
                   : (side < 2U ? offset : parameters.size() - 1U - offset);
      const double source_parameter = parameters[index];
      const double local_parameter =
          reversed ? 1.0 - source_parameter : source_parameter;
      const UvVertex uv = side == 0U ? UvVertex{local_parameter, 0.0}
          : side == 1U ? UvVertex{1.0, local_parameter}
          : side == 2U ? UvVertex{local_parameter, 1.0}
                       : UvVertex{0.0, local_parameter};

      auto* source_node = dynamic_cast<NodeAdaptive*>(
          curve->GetPoint(static_cast<unsigned>(index)));
      Require(source_node && source_node->GetId() > 0UL &&
                  NearSource(Values(*source_node),
                             Values(curve->FindPointByParameter(source_parameter))) &&
                  NearSource(Values(*source_node),
                             Values(patch.Parameterize(uv.u, uv.v))),
              "Real adapted source sample does not lie on its original patch");

      auto copy = std::make_unique<NodeAdaptive>(
          source_node->GetX(), source_node->GetY(), source_node->GetZ());
      copy->SetId(source_node->GetId());
      if (corrupt_first_copy && result.physical_copies.empty())
        copy->SetId(copy->GetId() + 1UL);
      Require(copy->GetNumberElements() == 0U,
              "Detached physical sample copied external TRI adjacency");
      NodeAdaptive* owned = copy.get();
      auto* vertex = result.boundary->addVertex(
          uv.u, uv.v, curve, reversed);
      Require(vertex != nullptr && vertex->getId() > 0 &&
                  copied_nodes.emplace(vertex, owned).second,
              "Failed to construct disjoint native AFT source contour vertex");
      result.physical_copies.push_back(std::move(copy));
    }
    last_curve = curve;
    last_reversed = reversed;
  }
  Require((all_sides ? adapted_sides == 0U : adapted_sides == 1U) &&
              last_curve != nullptr &&
              result.boundary->close(last_curve, last_reversed),
          "Native detached high-valence source boundary failed to close");
  result.capture = apmesh::quad::SnapshotOriginalAdapterBoundary(
      patch, *result.boundary, copied_nodes,
      {static_cast<int>(patch_id), 1, 0, 0, {2U, 1U, 0}});
  std::size_t expected_edges = 0;
  for (unsigned side = 0; side < 4U; ++side) {
    auto* curve = static_cast<CurveAdaptiveParametric*>(patch.GetCurve(side));
    const auto intervals = curve->GetNumBerPoints() - 1U;
    Require(result.capture.side_counts[side] == intervals,
            "Detached AFT contour has an incorrect source side count");
    expected_edges += intervals;
  }
  Require(result.capture.vertices.size() ==
              result.physical_copies.size() &&
              result.capture.vertices.size() == expected_edges &&
              result.capture.directed_edges.size() == expected_edges &&
              (!all_sides &&
               result.capture.side_counts[result.adapted_side] !=
                   adapted->GetNumBerPoints() - 1U) == false,
          "Detached AFT contour omitted or duplicated source intervals");

  double twice_area = 0.0;
  std::size_t inspected = 0;
  auto vertices = result.boundary->getBoundary();
  auto edges = result.boundary->getEdges();
  auto v = vertices.begin();
  auto e = edges.begin();
  std::set<const NodeAdaptive*> separate_copy_owners;
  for (std::size_t i = 0; i < result.capture.vertices.size();
       ++i, ++v, ++e) {
    Require(v != vertices.end() && e != edges.end() &&
                *v != nullptr && *e != nullptr,
            "Detached contour has missing owned vertices or edges");
    auto* edge = *e;
    const auto& site = result.capture.vertices[i];
    const auto& next =
        result.capture.vertices[(i + 1U) % result.capture.vertices.size()];
    Require(edge->getV1() == *v &&
                edge->getV2() != nullptr &&
                edge->getV1()->getId() == site.aft_vertex_id &&
                edge->getV2()->getId() == next.aft_vertex_id &&
                edge->getMid() != nullptr &&
                std::isfinite(edge->getLen()) && edge->getLen() > 0.0 &&
                separate_copy_owners.insert(
                    result.physical_copies[i].get()).second,
            "Original native contour lost directed edge, curved metric or owner");
    twice_area += site.uv.u * next.uv.v - next.uv.u * site.uv.v;
    ++inspected;
  }
  Require(inspected == result.capture.vertices.size() &&
              v == vertices.end() && e == edges.end() &&
              std::isfinite(twice_area) && twice_area > 0.0 &&
              patch.GetSubMesh() != nullptr,
          "Detached actual source contour invalidated original TRI Patch");
  return result;
}

DetachedSourceBoundary BuildDetachedAdaptedSourceBoundary(
    PatchBezier& patch, unsigned patch_id, CurveAdaptiveParametric& adapted) {
  return BuildDetachedSourceBoundaryImpl(
      patch, patch_id, &adapted, false);
}

struct DetachedSourceBoundaryStats {
  std::size_t patch_boundaries = 0;
  std::size_t total_boundary_vertices = 0;
  std::size_t adapted_side_edges = 0;
  std::size_t all_native_directed_edges = 0;
  std::size_t per_patch_source_sites = 0;
  std::size_t matched_canonical_source_sites = 0;
  std::size_t matched_incidence_pairs = 0;
  std::size_t pairwise_source_sites = 0;
  std::size_t pairwise_source_intervals = 0;
  std::size_t rejected_negative_snapshots = 0;
};

DetachedSourceBoundaryStats AuditDetachedSourceBoundaries(
    Geometry& original, CurveAdaptiveParametric& source,
    const std::vector<DetachedSourceBoundary>& boundaries,
    unsigned expected_valence) {
  Require(boundaries.size() == expected_valence,
          "Missing native detached original high-valence source patch");
  DetachedSourceBoundaryStats stats;
  stats.patch_boundaries = boundaries.size();
  std::vector<apmesh::quad::SharedCurveSide> source_sides;
  source_sides.reserve(boundaries.size());
  std::set<const NodeAdaptive*> physical_owners;
  for (unsigned i = 0; i < boundaries.size(); ++i) {
    const auto& candidate = boundaries[i];
    auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(i));
    Require(patch && candidate.boundary && patch->GetSubMesh() &&
                patch->GetCurve(static_cast<unsigned>(candidate.adapted_side)) == &source,
            "Detached native contour lost original source Patch identity");
    stats.total_boundary_vertices += candidate.capture.vertices.size();
    stats.all_native_directed_edges += candidate.capture.directed_edges.size();
    stats.adapted_side_edges +=
        candidate.capture.side_counts[candidate.adapted_side];
    for (const auto& copy : candidate.physical_copies)
      Require(copy && physical_owners.insert(copy.get()).second,
              "Two separate original AFT boundaries share a physical node owner");
    auto side = apmesh::quad::SnapshotSharedCurveSide(
        candidate.capture, static_cast<unsigned>(candidate.adapted_side));
    Require(side.curve_id == source.GetId() &&
                side.ordered_by_original_parameter.size() ==
                    source.GetNumBerPoints(),
            "Native detached adapted contour dropped source incidence samples");
    const std::vector<double> canonical_parameters(
        source.parameters_.begin(), source.parameters_.end());
    for (std::size_t j = 0; j < side.ordered_by_original_parameter.size(); ++j) {
      const auto& sample = side.ordered_by_original_parameter[j];
      Require(sample.t == canonical_parameters[j] &&
                  NearSource(sample.xyz,
                             Values(source.FindPointByParameter(sample.t))) &&
                  sample.node_id ==
                      source.GetPoint(static_cast<unsigned>(j))->GetId(),
              "Native detached original AFT side lost adapted source provenance");
      ++stats.matched_canonical_source_sites;
    }
    source_sides.push_back(std::move(side));
    ++stats.per_patch_source_sites;
  }
  Require(physical_owners.size() == stats.total_boundary_vertices,
          "Detached source boundaries have missing physical node owners");
  for (unsigned i = 0; i < source_sides.size(); ++i) {
    for (unsigned j = i + 1U; j < source_sides.size(); ++j) {
      const auto cmp = apmesh::quad::CompareSharedCurveSides(
          source_sides[i], source_sides[j], false, true);
      Require(cmp.matched &&
                  cmp.compared_sites == source.GetNumBerPoints(),
              "Different detached AFT patches disagree on a shared source curve");
      ++stats.matched_incidence_pairs;
      stats.pairwise_source_sites += cmp.compared_sites;
      stats.pairwise_source_intervals += cmp.compared_sites - 1U;
    }
  }
  Require(stats.per_patch_source_sites == expected_valence &&
              stats.matched_incidence_pairs ==
                  expected_valence * (expected_valence - 1U) / 2U &&
              stats.total_boundary_vertices ==
                  expected_valence * (source.GetNumBerPoints() + 2U) &&
              stats.adapted_side_edges ==
                  expected_valence * (source.GetNumBerPoints() - 1U),
          "Original detached dynamic AFT contour coverage was incomplete");
  return stats;
}

unsigned RejectDetachedSourceBoundaryMutations(
    const std::vector<DetachedSourceBoundary>& boundaries) {
  Require(boundaries.size() > 1U,
          "Source boundary rejection needs a shared curve pair");
  const auto& first = boundaries[0];
  const auto& second = boundaries[1];
  const unsigned side_a = static_cast<unsigned>(first.adapted_side);
  const unsigned side_b = static_cast<unsigned>(second.adapted_side);
  const auto original_left = apmesh::quad::SnapshotSharedCurveSide(
      first.capture, side_a);
  const auto original_right = apmesh::quad::SnapshotSharedCurveSide(
      second.capture, side_b);
  Require(apmesh::quad::CompareSharedCurveSides(
              original_left, original_right, false, true).matched,
          "Genuine detached source boundaries are not initially equivalent");
  unsigned rejected = 0;
  const auto must_reject = [&](apmesh::quad::AdapterBoundaryCapture altered) {
    bool failed = false;
    try {
      const auto right = apmesh::quad::SnapshotSharedCurveSide(altered, side_b);
      const auto compared = apmesh::quad::CompareSharedCurveSides(
          original_left, right, false, true);
      failed = !compared.matched;
    } catch (const std::invalid_argument&) {
      failed = true;
    }
    Require(failed, "Corrupted detached original source boundary was accepted");
    ++rejected;
  };
  const auto find_site = [&]() {
    for (std::size_t i = 0; i < second.capture.vertices.size(); ++i)
      if (second.capture.vertices[i].side == side_b)
        return i;
    throw std::runtime_error("Detached source boundary has no shared side");
  };
  const std::size_t selected = find_site();
  auto displaced = second.capture;
  displaced.vertices[selected].physical_xyz[0] += 1.0;
  must_reject(std::move(displaced));
  auto parameter_changed = second.capture;
  parameter_changed.vertices[selected].original_parameter += 0.03125;
  must_reject(std::move(parameter_changed));
  auto id_changed = second.capture;
  id_changed.vertices[selected].physical_node_id += 98765UL;
  must_reject(std::move(id_changed));
  auto source_changed = second.capture;
  source_changed.vertices[selected].curve_id += 999UL;
  must_reject(std::move(source_changed));
  auto inversion_changed = second.capture;
  inversion_changed.vertices[selected].curve_reversed =
      !inversion_changed.vertices[selected].curve_reversed;
  must_reject(std::move(inversion_changed));
  auto omitted = second.capture;
  omitted.vertices.erase(omitted.vertices.begin() +
                         static_cast<std::ptrdiff_t>(selected));
  must_reject(std::move(omitted));
  auto endpoint_changed = second.capture;
  endpoint_changed.original_curve_endpoints[side_b].node_id = 0UL;
  must_reject(std::move(endpoint_changed));
  return rejected;
}

// A dedicated research Quadtree owns one actual source-driven native AFT
// boundary, never the accepted TRI Patch observer or another patch's contour.
// Its leaves are an independently qualified *test* hierarchy, not the original
// GeneratorAdaptive::AdaptDomain accepted epoch or production QUAD tree.
std::unique_ptr<Quadtree> MakeDynamicSourceTree(
    DetachedSourceBoundary& source) {
  Require(source.boundary != nullptr &&
              source.capture.vertices.size() == 9U,
          "Dynamic original native Quadtree requires nine directed sources");
  auto tree = std::make_unique<Quadtree>();
  tree->setBoundary(source.boundary.release());
  auto low = std::make_unique<Vertex>(0.0, 0.0);
  auto high = std::make_unique<Vertex>(1.0, 1.0);
  auto root = std::make_unique<QuadtreeCell>(
      tree->getCellId(), tree.get(), low.get(), high.get());
  tree->setRoot(root.get());
  root.release();
  low.release();
  high.release();
  tree->getRoot()->subdivideToLevel(2);
  Require(tree->GetLeafCount() == 16U,
          "Dynamic original source root did not produce the full test tree");
  return tree;
}

double DynamicUvQuality(const std::array<UvVertex, 3>& uv) {
  const auto squared = [](const UvVertex& a, const UvVertex& b) {
    return (a.u - b.u) * (a.u - b.u) +
           (a.v - b.v) * (a.v - b.v);
  };
  const double sum = squared(uv[0], uv[1]) +
                     squared(uv[1], uv[2]) +
                     squared(uv[2], uv[0]);
  const double twice = (uv[1].u - uv[0].u) * (uv[2].v - uv[0].v) -
                       (uv[1].v - uv[0].v) * (uv[2].u - uv[0].u);
  Require(std::isfinite(twice) && twice > 1e-12 &&
              std::isfinite(sum) && sum > 0.0,
          "Dynamic source-driven UV element collapsed or inverted");
  const double quality = 2.0 * std::sqrt(3.0) * twice / sum;
  Require(std::isfinite(quality) && quality > 1e-10,
          "Dynamic source-driven UV triangle has invalid shape quality");
  return quality;
}

double DynamicPhysicalAlignment(PatchBezier& patch,
                                const std::array<UvVertex, 3>& uv) {
  CheckFaceOrientation(patch, uv);
  const UvVertex middle{
      (uv[0].u + uv[1].u + uv[2].u) / 3.0,
      (uv[0].v + uv[1].v + uv[2].v) / 3.0};
  const Xyz source = Cross(Values(patch.Qu(middle.u, middle.v)),
                           Values(patch.Qv(middle.u, middle.v)));
  const Xyz a = Values(patch.Parameterize(uv[0].u, uv[0].v));
  const Xyz b = Values(patch.Parameterize(uv[1].u, uv[1].v));
  const Xyz c = Values(patch.Parameterize(uv[2].u, uv[2].v));
  const Xyz facet = Cross(Subtract(b, a), Subtract(c, a));
  const double denominator = Norm(source) * Norm(facet);
  Require(std::isfinite(denominator) && denominator > 1e-14,
          "Dynamic physical original facet has no differential orientation");
  const double cosine = Dot(source, facet) / denominator;
  Require(std::isfinite(cosine) && cosine > 0.0 &&
              cosine <= 1.0 + 1e-10,
          "Dynamic original QUAD/AFT facet does not follow Bézier normal");
  return cosine;
}

struct DynamicNativeChartCounts {
  std::size_t physical_nodes = 0;
  std::size_t quads = 0;
  std::size_t tris = 0;
  std::size_t original_boundary_sites = 0;
  std::size_t original_adapted_sites = 0;
  std::size_t source_quadtree_leaves = 0;
  std::size_t quad_seam_edges = 0;
  std::size_t original_source_boundary_edges = 0;
  double min_uv_triangle_quality = 1.0;
  double min_physical_alignment = 1.0;
};

std::unique_ptr<SubMesh> BuildDynamicAdaptedAftChart(
    PatchBezier& patch, unsigned patch_id,
    DetachedSourceBoundary&& source,
    DetachedSourceBoundary&& reference,
    DynamicNativeChartCounts& counts) {
  SubMesh* const original_tri = patch.GetSubMesh();
  Require(original_tri != nullptr && source.boundary &&
              reference.boundary &&
              source.capture.vertices.size() == 9U &&
              reference.capture.vertices.size() == 9U,
          "Original dynamic patch lacks a real native source boundary pair");
  auto legacy = MakeDynamicSourceTree(reference);
  Require(legacy->makeTemplateBasedMesh() ==
              Par2DJMesh::AFT::QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
          "Original dynamic native reference TRI template failed");
  const auto original_front = SnapshotLegacyFront(*legacy);
  auto tree = MakeDynamicSourceTree(source);
  InteriorTemplateDispatcher selector(*tree);
  auto selected = selector.Select(InteriorTemplateMode::ExperimentalQuad,
                                  PointRule);
  Require(!selected.uv_quads.quads.empty() &&
              !selected.quad_region_boundary.empty(),
          "Dynamic original source Quadtree selected no interior QUADs");
  counts.source_quadtree_leaves = selected.source_leaves;
  auto* owner = tree.get();
  auto aft = std::make_unique<OwnedQuadAftFront>(
      owner->getBoundary(), owner);
  tree.release();
  const auto seeded = aft->Seed(selected, original_front);
  Require(seeded.patch_boundary_edges == source.capture.vertices.size() &&
              seeded.quad_interface_edges ==
                  selected.quad_region_boundary.size() &&
              seeded.attached_exterior_cells > 0U,
          "Dynamic native source QUAD/AFT interface lost source cell coverage");
  counts.quad_seam_edges = seeded.quad_interface_edges;
  counts.original_source_boundary_edges = seeded.patch_boundary_edges;
  for (auto* edge : aft->getBoundary()->getEdges()) {
    aft->getQuadtree()->findCell(edge);
    Require(edge && edge->getCell() != nullptr,
            "Dynamic adapted AFT edge lacks a live original source tree cell");
  }
  const auto exterior = aft->AttemptExteriorTriangulation(selected);
  Require(exterior.exterior_triangles > 0U &&
              exterior.front_drained && exterior.triangles_positive &&
              exterior.seam_orientation_complete &&
              exterior.seam_vertices_unchanged &&
              exterior.uv_area_balanced &&
              exterior.spatial_overlap_tested &&
              exterior.no_spatial_overlap &&
              exterior.unresolved_front_edges == 0U &&
              exterior.unresolved_rejected_edges == 0U &&
              exterior.seam_edges_with_one_tri == seeded.quad_interface_edges,
          "Dynamic native source QUAD/AFT front did not close cleanly");

  auto chart = std::make_unique<SubMesh>();
  std::map<std::pair<double, double>, NodeAdaptive*> local_nodes;
  const auto node_at = [&](UvVertex uv) {
    const auto key = std::make_pair(uv.u, uv.v);
    const auto existing = local_nodes.find(key);
    if (existing != local_nodes.end()) return existing->second;
    const Xyz xyz = Evaluate(patch, uv);
    auto point = std::make_unique<NodeAdaptive>(xyz[0], xyz[1], xyz[2]);
    point->SetId(static_cast<unsigned long>(
        1000000U * (patch_id + 1U) + local_nodes.size() + 1U));
    NodeAdaptive* observed = point.get();
    chart->AddNoh(std::move(point));
    local_nodes.emplace(key, observed);
    return observed;
  };
  for (const auto& quad : selected.uv_quads.quads) {
    QuadrilateralAdaptive::Parameters uv{};
    QuadrilateralAdaptive::Nodes nodes{};
    UvVertex center{};
    for (unsigned n = 0; n < 4U; ++n) {
      const UvVertex vertex =
          selected.uv_quads.vertices.at(quad.vertices[n]);
      uv[n] = {vertex.u, vertex.v};
      nodes[n] = node_at(vertex);
      center.u += vertex.u;
      center.v += vertex.v;
    }
    center.u *= 0.25;
    center.v *= 0.25;
    const std::array<UvVertex, 3> left{
        {selected.uv_quads.vertices.at(quad.vertices[0]),
         selected.uv_quads.vertices.at(quad.vertices[1]),
         selected.uv_quads.vertices.at(quad.vertices[2])}};
    const std::array<UvVertex, 3> right{
        {selected.uv_quads.vertices.at(quad.vertices[0]),
         selected.uv_quads.vertices.at(quad.vertices[2]),
         selected.uv_quads.vertices.at(quad.vertices[3])}};
    for (const auto& face : {left, right}) {
      counts.min_uv_triangle_quality =
          std::min(counts.min_uv_triangle_quality, DynamicUvQuality(face));
      counts.min_physical_alignment =
          std::min(counts.min_physical_alignment,
                   DynamicPhysicalAlignment(patch, face));
    }
    const VectorAdaptive reference_normal =
        patch.Qu(center.u, center.v) * patch.Qv(center.u, center.v);
    chart->AddElement(std::make_unique<QuadrilateralAdaptive>(
        nodes, uv, reference_normal));
    ++counts.quads;
  }
  for (Face* face : aft->Triangles()) {
    Require(face != nullptr, "Native dynamic AFT emitted a null TRI face");
    const std::array<UvVertex, 3> uv{{
        {face->getV1()->getX(), face->getV1()->getY()},
        {face->getV2()->getX(), face->getV2()->getY()},
        {face->getV3()->getX(), face->getV3()->getY()}}};
    counts.min_uv_triangle_quality =
        std::min(counts.min_uv_triangle_quality, DynamicUvQuality(uv));
    counts.min_physical_alignment =
        std::min(counts.min_physical_alignment,
                 DynamicPhysicalAlignment(patch, uv));
    auto triangle = std::make_unique<TriangleAdaptive>(
        node_at(uv[0]), node_at(uv[1]), node_at(uv[2]));
    triangle->SetParametersN1({uv[0].u, uv[0].v});
    triangle->SetParametersN2({uv[1].u, uv[1].v});
    triangle->SetParametersN3({uv[2].u, uv[2].v});
    chart->AddElement(std::move(triangle));
    ++counts.tris;
  }
  for (std::size_t i = 0; i < source.capture.vertices.size(); ++i) {
    const auto& observed = source.capture.vertices[i];
    const auto original = local_nodes.find({observed.uv.u, observed.uv.v});
    Require(original != local_nodes.end() && original->second != nullptr &&
                NearSource(Values(*original->second),
                           source.capture.vertices[i].physical_xyz) &&
                NearSource(Values(*original->second),
                           Values(*source.physical_copies[i])) &&
                original->second != source.physical_copies[i].get(),
            "Native dynamic QUAD/AFT physical mesh dropped or aliased a real adapted boundary knot");
    ++counts.original_boundary_sites;
    if (observed.side == source.adapted_side)
      ++counts.original_adapted_sites;
  }
  counts.physical_nodes = chart->GetNumberNos();
  Require(counts.quads == selected.uv_quads.quads.size() &&
              counts.tris == aft->Triangles().size() &&
              counts.quads > 0U && counts.tris > 0U &&
              counts.original_boundary_sites == 9U &&
              counts.original_adapted_sites == 6U &&
              counts.min_uv_triangle_quality > 0.0 &&
              counts.min_physical_alignment > 0.0 &&
              chart->GetNumberElements() == counts.quads + counts.tris &&
              patch.GetSubMesh() == original_tri,
          "Dynamic physical AFT mixed chart failed source owner or geometry gate");
  DisjointOwnerStage::CheckChart(*chart);
  return chart;
}

// Capture only immutable, owned physical values and ordered element kinds.
// This compares actual old/new full QUAD/AFT candidate generations without
// dereferencing any pointers after the old MeshAdaptive owner is retired.
struct DynamicPhysicalFingerprint {
  std::vector<std::tuple<unsigned long, double, double, double>> nodes;
  std::vector<unsigned> element_types;
  bool operator==(const DynamicPhysicalFingerprint& other) const {
    return nodes == other.nodes && element_types == other.element_types;
  }
};

DynamicPhysicalFingerprint FingerprintDynamicChart(const SubMesh& chart) {
  DisjointOwnerStage::CheckChart(chart);
  DynamicPhysicalFingerprint result;
  result.nodes.reserve(chart.GetNumberNos());
  result.element_types.reserve(chart.GetNumberElements());
  for (unsigned i = 0; i < chart.GetNumberNos(); ++i) {
    const auto* node = chart.GetNoh(i);
    Require(node && Finite(Values(*node)),
            "Dynamic source physical fingerprint contains an invalid node");
    result.nodes.emplace_back(
        node->GetId(), node->GetX(), node->GetY(), node->GetZ());
  }
  for (unsigned i = 0; i < chart.GetNumberElements(); ++i) {
    const auto* element = chart.GetElement(i);
    const unsigned kind =
        dynamic_cast<const QuadrilateralAdaptive*>(element) ? 4U :
        dynamic_cast<const TriangleAdaptive*>(element) ? 3U : 0U;
    Require(kind != 0U,
            "Dynamic source physical fingerprint contains an untyped element");
    result.element_types.push_back(kind);
  }
  return result;
}

std::vector<DynamicPhysicalFingerprint> SnapshotDynamicPhysicalModel(
    MeshAdaptive& active, unsigned original_patches) {
  Require(active.GetNumberSubMeshesAdaptive() == original_patches,
          "Dynamic physical model owner has incomplete chart publication");
  std::vector<DynamicPhysicalFingerprint> result;
  result.reserve(original_patches);
  for (unsigned i = 0; i < original_patches; ++i) {
    const auto* chart = active.GetSubMeshAdaptiveByPosition(i);
    Require(chart && chart->GetPatch() == nullptr,
            "Dynamic physical model chart was rebound to an original Patch");
    result.push_back(FingerprintDynamicChart(*chart));
  }
  return result;
}

struct DynamicNativeModelTotals {
  std::size_t charts = 0;
  std::size_t physical_nodes = 0;
  std::size_t quads = 0;
  std::size_t tris = 0;
  std::size_t source_knot_checks = 0;
  std::size_t adapted_knot_checks = 0;
  std::size_t source_tree_leaves = 0;
  std::size_t quad_seam_edges = 0;
  std::size_t native_boundary_edges = 0;
  double min_uv_triangle_quality = 1.0;
  double min_physical_alignment = 1.0;
  std::size_t rejected_physical_stage_faults = 0;
  std::size_t rejected_incomplete_physical_stages = 0;
  std::size_t repeated_atomic_physical_publications = 0;
  std::size_t repeated_deterministic_chart_checks = 0;
  std::size_t preserved_original_source_node_observers = 0;
};

DynamicNativeModelTotals StageDynamicOriginalPhysicalCharts(
    Geometry& original, CurveAdaptiveParametric& adapted,
    std::vector<DetachedSourceBoundary>& source_boundaries,
    unsigned original_patches) {
  Require(source_boundaries.size() == original_patches,
          "Dynamic original physical model has missing source chart owners");
  std::vector<SubMesh*> original_tri;
  original_tri.reserve(original_patches);
  std::unique_ptr<MeshAdaptive> disconnected = std::make_unique<MeshAdaptive>();
  DisjointOwnerStage staged(original_patches);
  DynamicNativeModelTotals report;
  for (unsigned patch_id = 0; patch_id < original_patches; ++patch_id) {
    auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(patch_id));
    Require(patch != nullptr && patch->GetSubMesh() != nullptr,
            "Dynamic physical chart requires its original accepted TRI observer");
    original_tri.push_back(patch->GetSubMesh());
    auto reference =
        BuildDetachedAdaptedSourceBoundary(*patch, patch_id, adapted);
    DynamicNativeChartCounts counts;
    auto physical = BuildDynamicAdaptedAftChart(
        *patch, patch_id, std::move(source_boundaries[patch_id]),
        std::move(reference), counts);
    DisjointOwnerStage::CheckChart(*physical);
    staged.Add(std::move(physical));
    ++report.charts;
    report.physical_nodes += counts.physical_nodes;
    report.quads += counts.quads;
    report.tris += counts.tris;
    report.source_knot_checks += counts.original_boundary_sites;
    report.adapted_knot_checks += counts.original_adapted_sites;
    report.source_tree_leaves += counts.source_quadtree_leaves;
    report.quad_seam_edges += counts.quad_seam_edges;
    report.native_boundary_edges += counts.original_source_boundary_edges;
    report.min_uv_triangle_quality =
        std::min(report.min_uv_triangle_quality,
                 counts.min_uv_triangle_quality);
    report.min_physical_alignment =
        std::min(report.min_physical_alignment,
                 counts.min_physical_alignment);
  }
  staged.Replace(disconnected);
  Require(disconnected != nullptr &&
              disconnected->GetNumberSubMeshesAdaptive() == original_patches &&
              report.charts == original_patches &&
              report.source_knot_checks == 9U * original_patches &&
              report.adapted_knot_checks == 6U * original_patches &&
              report.native_boundary_edges == 9U * original_patches &&
              report.quads > 0U && report.tris > 0U &&
              report.physical_nodes > report.source_knot_checks &&
              report.min_uv_triangle_quality > 0.0 &&
              report.min_physical_alignment > 0.0,
          "Actual source dynamic physical QUAD/AFT model inventory incomplete");
  std::set<const NodeAdaptive*> unique_nodes;
  for (unsigned p = 0; p < original_patches; ++p) {
    auto* chart = disconnected->GetSubMeshAdaptiveByPosition(p);
    Require(chart != nullptr && chart->GetPatch() == nullptr &&
                original.GetPatch(p)->GetSubMesh() == original_tri[p],
            "Staged dynamic physical source chart mutated an original observer");
    DisjointOwnerStage::CheckChart(*chart);
    for (unsigned n = 0; n < chart->GetNumberNos(); ++n)
      Require(unique_nodes.insert(chart->GetNoh(n)).second,
              "Native dynamic AFT physical node is shared across patch owners");
  }
  Require(unique_nodes.size() == report.physical_nodes,
          "Staged native dynamic physical chart node inventory mismatched");

  // Start from a REAL fully admitted source-driven QUAD/AFT model. Fail the
  // replacement of a new equally real model at three distinct adoption points,
  // then verify the complete original owner graph remains byte-for-byte stable
  // as values and pointer-for-pointer live as observers.
  MeshAdaptive* const accepted_owner = disconnected.get();
  const auto accepted_values =
      SnapshotDynamicPhysicalModel(*accepted_owner, original_patches);
  std::vector<SubMesh*> accepted_charts;
  std::vector<NodeAdaptive*> accepted_nodes;
  std::vector<ElementAdaptive*> accepted_elements;
  accepted_charts.reserve(original_patches);
  accepted_nodes.reserve(original_patches);
  accepted_elements.reserve(original_patches);
  for (unsigned p = 0; p < original_patches; ++p) {
    auto* chart = accepted_owner->GetSubMeshAdaptiveByPosition(p);
    accepted_charts.push_back(chart);
    accepted_nodes.push_back(chart->GetNoh(0));
    accepted_elements.push_back(chart->GetElement(0));
  }
  const NativeAdaptedSites source_values =
      SnapshotNativeAdaptedSource(adapted);
  const std::vector<PointAdaptive*> source_observers(
      adapted.GetPoints().begin(), adapted.GetPoints().end());
  const auto verify_original_observers = [&] {
    Require(disconnected.get() != nullptr &&
                disconnected->GetNumberSubMeshesAdaptive() == original_patches,
            "Dynamic stage lost its accepted MeshAdaptive owner");
    for (unsigned p = 0; p < original_patches; ++p)
      Require(original.GetPatch(p)->GetSubMesh() == original_tri[p],
              "Dynamic stage rebound the original accepted TRI Patch");
    const auto current = SnapshotNativeAdaptedSource(adapted);
    Require(current.size() == source_values.size() &&
                adapted.GetPoints().size() == source_observers.size(),
            "Dynamic stage mutated the actual original Adapter source graph");
    for (std::size_t i = 0; i < source_values.size(); ++i)
      Require(current[i].parameter == source_values[i].parameter &&
                  current[i].source_node_id == source_values[i].source_node_id &&
                  current[i].physical == source_values[i].physical &&
                  adapted.GetPoint(static_cast<unsigned>(i)) ==
                      source_observers[i],
              "Dynamic stage changed an original adapted source NodeAdaptive observer");
  };
  const auto prepare_full_dynamic_stage = [&](DisjointOwnerStage& next,
                                               unsigned count) {
    Require(count <= original_patches,
            "Dynamic stage requested more patches than source geometry owns");
    for (unsigned p = 0; p < count; ++p) {
      auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(p));
      Require(patch && patch->GetSubMesh() == original_tri[p],
              "Dynamic stage has an invalid original source TRI observer");
      auto native = BuildDetachedAdaptedSourceBoundary(*patch, p, adapted);
      auto reference = BuildDetachedAdaptedSourceBoundary(*patch, p, adapted);
      DynamicNativeChartCounts counts;
      auto physical = BuildDynamicAdaptedAftChart(
          *patch, p, std::move(native), std::move(reference), counts);
      Require(counts.quads > 0U && counts.tris > 0U &&
                  counts.original_adapted_sites == 6U &&
                  counts.original_boundary_sites == 9U,
              "Dynamic stage test would accept an incomplete real source patch");
      Require(FingerprintDynamicChart(*physical) == accepted_values[p],
              "Identical original Adapter source graph produced different physical elements");
      ++report.repeated_deterministic_chart_checks;
      next.Add(std::move(physical));
    }
  };
  const auto verify_failed_stage = [&] {
    Require(disconnected.get() == accepted_owner &&
                SnapshotDynamicPhysicalModel(*disconnected, original_patches)
                    == accepted_values,
            "Rejected dynamic stage changed accepted physical QUAD/AFT values");
    for (unsigned p = 0; p < original_patches; ++p) {
      auto* live = disconnected->GetSubMeshAdaptiveByPosition(p);
      Require(live == accepted_charts[p] &&
                  live->GetNoh(0) == accepted_nodes[p] &&
                  live->GetElement(0) == accepted_elements[p],
              "Rejected dynamic stage changed an accepted physical element owner");
    }
    verify_original_observers();
  };
  const std::array<unsigned, 3> fault_positions{
      {0U, original_patches / 2U, original_patches}};
  for (const auto fault : fault_positions) {
    DisjointOwnerStage candidate(original_patches);
    prepare_full_dynamic_stage(candidate, original_patches);
    bool rejected = false;
    try {
      candidate.Replace(disconnected, static_cast<int>(fault));
    } catch (const std::runtime_error&) {
      rejected = true;
    }
    Require(rejected, "Injected dynamic physical owner rollback was admitted");
    verify_failed_stage();
    ++report.rejected_physical_stage_faults;
  }
  {
    // A fully real but incomplete collection must not replace prior work.
    DisjointOwnerStage incomplete(original_patches);
    prepare_full_dynamic_stage(incomplete, original_patches - 1U);
    bool rejected = false;
    try {
      incomplete.Replace(disconnected);
    } catch (const std::invalid_argument&) {
      rejected = true;
    }
    Require(rejected, "Incomplete dynamic source physical stage was admitted");
    verify_failed_stage();
    ++report.rejected_incomplete_physical_stages;
  }
  {
    // The second complete publication consumes a fresh real source-conformant
    // QUAD/AFT graph. Do not dereference any retired graph after replacement.
    DisjointOwnerStage next(original_patches);
    prepare_full_dynamic_stage(next, original_patches);
    next.Replace(disconnected);
    Require(disconnected.get() != accepted_owner &&
                SnapshotDynamicPhysicalModel(*disconnected, original_patches)
                    == accepted_values,
            "Repeated real dynamic QUAD/AFT stage changed its physical output");
    verify_original_observers();
    ++report.repeated_atomic_physical_publications;
  }
  Require(report.rejected_physical_stage_faults == 3U &&
              report.rejected_incomplete_physical_stages == 1U &&
              report.repeated_atomic_physical_publications == 1U &&
              report.repeated_deterministic_chart_checks ==
                  5U * original_patches - 1U,
          "Dynamic original physical stage fault/repeat controls incomplete");
  report.preserved_original_source_node_observers = source_observers.size();
  return report;
}

void RunNativeOriginalSharedCurveAdaptation(const std::string& model,
                                            unsigned expected_valence) {
  Geometry original;
  PatchReader reader;
  Require(reader.ReaderFilePatches(&original, model) == &original &&
              original.GetNumberPatches() == expected_valence,
          "Original model for native Adapter curve sample audit unavailable");
  Performer::RangedIdManager id_manager(0, 0, 100000, 100000, 2);
  id_manager.setId(100);
  id_manager.setId(1, 200);
  apmesh::generation::CurveSampleLifetime lifetime(original);
  std::vector<std::unique_ptr<SubMesh>> original_coarse_meshes;
  original_coarse_meshes.reserve(original.GetNumberPatches());
  for (unsigned patch = 0; patch < original.GetNumberPatches(); ++patch) {
    auto* source = dynamic_cast<PatchCoons*>(original.GetPatch(patch));
    Require(source != nullptr, "Original source model lacks a Coons patch");
    original_coarse_meshes.push_back(
        apmesh::generation::BuildInitialSubMesh(source, &id_manager));
  }

  // Retire initial samples replaced by the two original Adapter passes.
  // Any still referenced by other original curves remain under their existing
  // collective CurveSampleLifetime owner. Destruction precedes that owner.
  struct RetireOrphanedSamples {
    Geometry& geometry;
    std::set<PointAdaptive*> initial;
    ~RetireOrphanedSamples() noexcept {
      std::set<PointAdaptive*> current;
      for (unsigned c = 0; c < geometry.GetNumberCurves(); ++c)
        for (auto* point : geometry.GetCurve(c)->GetPoints())
          current.insert(point);
      for (auto* point : initial)
        if (!current.count(point)) delete point;
    }
  } retire{original, {}};
  for (unsigned c = 0; c < original.GetNumberCurves(); ++c) {
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(
        original.GetCurve(c));
    Require(curve != nullptr && curve->GetNumBerPoints() == 2U,
            "Native coarse original model has uninitialized curve endpoints");
    curve->UpdateParameters({0.0, 1.0});
    for (auto* point : curve->GetPoints()) retire.initial.insert(point);
  }

  CurveAdaptiveParametric* target = nullptr;
  for (unsigned c = 0; c < original.GetNumberCurves(); ++c) {
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(
        original.GetCurve(c));
    if (curve && curve->GetNumBerPatches() == expected_valence) {
      Require(target == nullptr,
              "More than one expected high-valence original source curve");
      target = curve;
    }
  }
  Require(target != nullptr, "Missing original valence-4/28 source curve");
  // Production's serial sorter expects its shared comparator slot to exist.
  // Preserve and restore any previous process-scoped fixture scratch.
  struct ScopedOriginalSortScratch {
    std::vector<CurveAdaptiveParametric*> previous;
    ScopedOriginalSortScratch() : previous(std::move(ptr_aux)) {
      ptr_aux.resize(1U, nullptr);
    }
    ~ScopedOriginalSortScratch() { ptr_aux = std::move(previous); }
  } sort_scratch;
  target->CalculateLengthCurve();
  Require(std::isfinite(target->GetLength()) && target->GetLength() > 0.0,
          "Original high-valence curve has invalid parametric length");
  Adapter adapter;
  std::map<PointAdaptive*, PointAdaptive*> point_cache;
  apmesh::generation::RefineCurveSamples(
      target, point_cache,
      [&] {
        return adapter.AdaptCurveByCurve(target, point_cache, &id_manager, 1.0);
      },
      [&] {
        return adapter.AdaptCurveBySurface(target, point_cache, &id_manager, 1.0);
      },
      false, 0, &id_manager);
  const NativeAdaptedSites sampled = SnapshotNativeAdaptedSource(*target);
  const auto report = AuditNativeAdapterSourceIntervals(
      original, *target, sampled, expected_valence);
  const unsigned rejected = RejectAlteredAdapterSnapshots(
      original, *target, sampled, expected_valence);
  Require(rejected == 5U, "Original Adapter source negative controls incomplete");
  // The native Boundary owners are distinct from the original coarse TRI
  // owners and from each other. Only original source curve nodes are borrowed
  // while the observed source geometry is live.
  for (unsigned c = 0; c < original.GetNumberCurves(); ++c) {
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(
        original.GetCurve(c));
    Require(curve != nullptr, "Missing original contour source curve");
    if (curve != target) curve->CalculateLengthCurve();
    Require(std::isfinite(curve->GetLength()) && curve->GetLength() > 0.0,
            "Native source AFT edge lacks original parametric length");
  }
  std::vector<DetachedSourceBoundary> native_boundaries;
  native_boundaries.reserve(expected_valence);
  for (unsigned patch = 0; patch < original.GetNumberPatches(); ++patch) {
    auto* source_patch = dynamic_cast<PatchBezier*>(original.GetPatch(patch));
    Require(source_patch != nullptr,
            "Missing original Bezier patch for detached native AFT contour");
    native_boundaries.push_back(BuildDetachedAdaptedSourceBoundary(
        *source_patch, patch, *target));
  }
  const auto boundary_report = AuditDetachedSourceBoundaries(
      original, *target, native_boundaries, expected_valence);
  const unsigned boundary_rejected =
      RejectDetachedSourceBoundaryMutations(native_boundaries);
  Require(boundary_rejected == 7U &&
              boundary_report.adapted_side_edges ==
                  report.full_incidence_interval_checks &&
              boundary_report.pairwise_source_intervals ==
                  report.pairwise_interval_matches,
          "Original native detached contour lost adapted curve interval coverage");
  std::cout << "R2C3_NATIVE_ADAPTED_AFT_BOUNDARIES"
            << " original_patches=" << expected_valence
            << " original_high_valence_curves=1"
            << " detached_boundary_owners=" << boundary_report.patch_boundaries
            << " native_owned_vertices=" << boundary_report.total_boundary_vertices
            << " native_directed_edges=" << boundary_report.all_native_directed_edges
            << " adapted_source_edges=" << boundary_report.adapted_side_edges
            << " canonical_source_site_checks="
            << boundary_report.matched_canonical_source_sites
            << " shared_incidence_pairs=" << boundary_report.matched_incidence_pairs
            << " cross_patch_source_site_pairs="
            << boundary_report.pairwise_source_sites
            << " cross_patch_source_interval_pairs="
            << boundary_report.pairwise_source_intervals
            << " rejected_negative_snapshots=" << boundary_rejected
            << " actual_source_Adapter_partition=1"
            << " untouched_source_sides_coarse=1"
            << " native_Boundary_closed=1"
            << " native_curved_edge_metrics=1"
            << " physical_node_copy_owners_disjoint=1"
            << " native_AFT_triangulation_executed=0"
            << " quadtree_quad_templates_executed=0"
            << " globally_welded=0"
            << " patch_observers_rebound=0"
            << " advisor_sheet_approved=0\n";
  for (unsigned patch = 0; patch < original.GetNumberPatches(); ++patch) {
    Require(original.GetPatch(patch)->GetSubMesh() ==
                original_coarse_meshes[patch].get(),
            "Source Adapter curve audit modified original accepted TRI observer");
  }
  const auto physical = StageDynamicOriginalPhysicalCharts(
      original, *target, native_boundaries, expected_valence);
  std::cout << "R2C3_ADAPTED_SOURCE_PHYSICAL_QUAD_AFT"
            << " original_patches=" << expected_valence
            << " disconnected_physical_charts=" << physical.charts
            << " physical_nodes=" << physical.physical_nodes
            << " typed_QUAD=" << physical.quads
            << " typed_TRI=" << physical.tris
            << " source_boundary_knot_checks=" << physical.source_knot_checks
            << " dynamic_curve_knot_checks=" << physical.adapted_knot_checks
            << " research_source_tree_leaves=" << physical.source_tree_leaves
            << " original_AFT_boundary_edges=" << physical.native_boundary_edges
            << " quad_aft_seam_edges=" << physical.quad_seam_edges
            << " minimum_uv_triangle_quality="
            << physical.min_uv_triangle_quality
            << " minimum_physical_normal_alignment="
            << physical.min_physical_alignment
            << " all_fronts_drained=1"
            << " quad_tri_area_balance=1"
            << " positive_nonoverlapping_uv_faces=1"
            << " real_original_six_interval_curve_used=1"
            << " original_other_three_sides_coarse=1"
            << " original_tri_patch_observers_preserved=1"
            << " all_chart_physical_nodes_disjoint=1"
            << " global_physical_mesh_welded=0"
            << " scientific_sheet_owner_approved=0"
            << " production_quad_enabled=0\n";
  std::cout << "R2C4_DYNAMIC_PHYSICAL_STAGE_ROLLBACK"
            << " original_patches=" << expected_valence
            << " genuine_physical_charts_per_complete_stage="
            << physical.charts
            << " rejected_injected_owner_faults="
            << physical.rejected_physical_stage_faults
            << " rejected_incomplete_stages="
            << physical.rejected_incomplete_physical_stages
            << " repeated_atomic_publications="
            << physical.repeated_atomic_physical_publications
            << " deterministic_real_chart_comparisons="
            << physical.repeated_deterministic_chart_checks
            << " preserved_adapted_source_node_observers="
            << physical.preserved_original_source_node_observers
            << " original_TRI_Patch_observers_preserved=1"
            << " previous_accepted_QUAD_TRI_owner_preserved_on_fault=1"
            << " previous_accepted_QUAD_TRI_nodes_preserved_on_fault=1"
            << " previous_accepted_QUAD_TRI_elements_preserved_on_fault=1"
            << " original_Adapter_source_graph_unchanged=1"
            << " original_Adapter_reexecuted=0"
            << " global_welding=0"
            << " patch_observer_transaction=0"
            << " advisor_sheet_approved=0\n";
  std::cout << "R2C3_NATIVE_ADAPTER_SOURCE_INTERVALS"
            << " original_patches=" << expected_valence
            << " original_shared_source_curves=1"
            << " source_sites=" << report.source_sites
            << " source_intervals=" << report.intervals
            << " original_source_incidences=" << report.incidences
            << " complete_incidence_sites=" << report.full_incidence_site_checks
            << " complete_incidence_intervals="
            << report.full_incidence_interval_checks
            << " pairwise_incidence_comparisons="
            << report.geometric_incidence_pairs
            << " pairwise_interval_matches="
            << report.pairwise_interval_matches
            << " rejected_negative_controls=" << rejected
            << " adaptation=AdapterByCurve+AdapterBySurface"
            << " original_submesh_observers_preserved=1"
            << " topology_sheet_approval=0"
            << " physical_cross_patch_welding=0"
            << " global_mesh_publication=0\n";
}

// R2c-6: a separate, original, complete-model serial two-pass source curve
// sweep. This uses the production graph transaction, but does NOT claim the
// generator's budget/target policy or complete accepted AdaptDomain epoch.
struct AllCurveIncidenceSnapshot {
  unsigned patch_id = 0;
  unsigned side = 0;
  unsigned long curve_id = 0UL;
  bool reversed = false;
  std::vector<NativeAdaptedSite> canonical_source_sites;
};

std::vector<NativeAdaptedSite> SnapshotAnyOriginalSourceCurve(
    CurveAdaptiveParametric& curve) {
  const std::vector<double> parameters(
      curve.parameters_.begin(), curve.parameters_.end());
  const auto& nodes = curve.GetPoints();
  Require(parameters.size() == nodes.size() && parameters.size() >= 2U &&
              parameters.front() == 0.0 && parameters.back() == 1.0,
          "Whole-model original two-pass Adapter curve has missing endpoints");
  std::vector<NativeAdaptedSite> result;
  result.reserve(parameters.size());
  std::set<unsigned long> ids;
  auto node = nodes.begin();
  for (unsigned i = 0; i < parameters.size(); ++i, ++node) {
    auto* original = dynamic_cast<NodeAdaptive*>(*node);
    Require(original != nullptr && original->GetId() != 0UL &&
                ids.insert(original->GetId()).second &&
                std::isfinite(parameters[i]) &&
                (i == 0U || parameters[i] > parameters[i - 1U]),
            "Whole-model original curve has invalid real samples or parameter order");
    const Xyz observed = Values(*original);
    Require(NearSource(observed,
                       Values(curve.FindPointByParameter(parameters[i]))),
            "Whole-model original Adapter generated an off-curve physical sample");
    result.push_back({parameters[i], original->GetId(), observed});
  }
  return result;
}

void ValidateWholeModelSourceIncidence(
    PatchBezier& patch, CurveAdaptiveParametric& source,
    const AllCurveIncidenceSnapshot& side) {
  Require(side.side < 4U && side.curve_id == source.GetId() &&
              side.reversed == patch.IsCurveReversed(side.side) &&
              patch.GetCurve(side.side) == &source,
          "Whole-model source incidence has foreign curve or orientation metadata");
  const auto canonical = SnapshotAnyOriginalSourceCurve(source);
  Require(side.canonical_source_sites.size() == canonical.size(),
          "Whole-model source incidence omitted an actual Adapter site");
  for (unsigned i = 0; i < canonical.size(); ++i) {
    const auto& recorded = side.canonical_source_sites[i];
    const auto& original = canonical[i];
    Require(recorded.parameter == original.parameter &&
                recorded.source_node_id == original.source_node_id &&
                NearSource(recorded.physical, original.physical),
            "Whole-model source incidence changed a canonical source sample");
    const double local = side.reversed
        ? 1.0 - recorded.parameter : recorded.parameter;
    const UvVertex uv = side.side == 0U ? UvVertex{local, 0.0}
        : side.side == 1U ? UvVertex{1.0, local}
        : side.side == 2U ? UvVertex{local, 1.0}
                          : UvVertex{0.0, local};
    Require(NearSource(recorded.physical,
                       Values(patch.Parameterize(uv.u, uv.v))),
            "Whole-model original patch boundary disagrees with adapted source");
  }
}

bool SameCanonicalWholeModelSide(
    const AllCurveIncidenceSnapshot& a,
    const AllCurveIncidenceSnapshot& b) {
  if (a.patch_id == b.patch_id || a.curve_id != b.curve_id ||
      a.canonical_source_sites.size() != b.canonical_source_sites.size())
    return false;
  for (unsigned i = 0; i < a.canonical_source_sites.size(); ++i) {
    const auto& left = a.canonical_source_sites[i];
    const auto& right = b.canonical_source_sites[i];
    if (left.parameter != right.parameter ||
        left.source_node_id != right.source_node_id ||
        !NearSource(left.physical, right.physical))
      return false;
  }
  // Shared source identity does not imply opposite winding at valence > 2.
  return true;
}

unsigned RejectWholeModelSourceSnapshotCorruptions(
    PatchBezier& original_patch, CurveAdaptiveParametric& original_curve,
    const AllCurveIncidenceSnapshot& valid) {
  unsigned rejected = 0;
  const auto must_reject = [&](AllCurveIncidenceSnapshot altered) {
    bool failed = false;
    try {
      ValidateWholeModelSourceIncidence(
          original_patch, original_curve, altered);
    } catch (const std::runtime_error&) {
      failed = true;
    }
    Require(failed,
            "Invalid whole-model original source incidence escaped the oracle");
    ++rejected;
  };
  auto distorted = valid;
  distorted.canonical_source_sites.front().physical[0] += 1.0;
  must_reject(std::move(distorted));
  auto wrong_parameter = valid;
  wrong_parameter.canonical_source_sites.front().parameter += 0.1;
  must_reject(std::move(wrong_parameter));
  auto wrong_node = valid;
  wrong_node.canonical_source_sites.front().source_node_id += 99999UL;
  must_reject(std::move(wrong_node));
  auto wrong_curve = valid;
  wrong_curve.curve_id += 99999UL;
  must_reject(std::move(wrong_curve));
  auto wrong_orientation = valid;
  wrong_orientation.reversed = !wrong_orientation.reversed;
  must_reject(std::move(wrong_orientation));
  auto omitted = valid;
  omitted.canonical_source_sites.pop_back();
  must_reject(std::move(omitted));
  return rejected;
}

// R2c-7 is a detached all-four-side native AFT contour gate. Physical owners
// stay separate; shared original curve identity never authorizes sheet welding.
struct AllSidesAftBoundaryReport {
  std::size_t contours = 0;
  std::size_t side_incidences = 0;
  std::size_t directed_edges = 0;
  std::size_t physical_copy_owners = 0;
  std::size_t shared_source_pairs = 0;
  std::size_t compared_shared_sites = 0;
  std::size_t rejected_owner_faults = 0;
  std::size_t rejected_snapshot_faults = 0;
};

AllSidesAftBoundaryReport AuditWholeModelAllSidesAftBoundaries(
    Geometry& original, const apmesh::quad::SharedCurveTopology& topology,
    const std::vector<SubMesh*>& accepted_tri, unsigned expected_patches) {
  AllSidesAftBoundaryReport report;
  std::vector<DetachedSourceBoundary> physical;
  physical.reserve(expected_patches);
  std::set<const NodeAdaptive*> independent_owners;
  std::map<const CurveAdaptiveParametric*,
           std::vector<apmesh::quad::SharedCurveSide>> incidences;

  for (unsigned p = 0; p < expected_patches; ++p) {
    auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(p));
    Require(patch && patch->GetSubMesh() == accepted_tri.at(p),
            "R2c7 lost the original accepted TRI patch observer");
    physical.push_back(BuildDetachedSourceBoundaryImpl(
        *patch, p, nullptr, true));
    const auto& candidate = physical.back();
    Require(candidate.boundary &&
                candidate.capture.vertices.size() ==
                    candidate.physical_copies.size(),
            "R2c7 original native AFT owner count mismatch");
    ++report.contours;
    report.directed_edges += candidate.capture.directed_edges.size();
    report.physical_copy_owners += candidate.physical_copies.size();
    for (const auto& copy : candidate.physical_copies)
      Require(copy && independent_owners.insert(copy.get()).second,
              "R2c7 shared a physical copy across separate original patches");
    for (unsigned side = 0; side < 4U; ++side) {
      auto* curve = dynamic_cast<CurveAdaptiveParametric*>(
          patch->GetCurve(side));
      Require(curve && curve->GetNumBerPoints() > 2U &&
                  candidate.capture.side_counts[side] ==
                      curve->GetNumBerPoints() - 1U,
              "R2c7 lost one of four genuinely adapted original patch sides");
      auto observed = apmesh::quad::SnapshotSharedCurveSide(
          candidate.capture, side);
      const auto canonical = SnapshotAnyOriginalSourceCurve(*curve);
      Require(observed.curve_id == curve->GetId() &&
                  observed.ordered_by_original_parameter.size() ==
                      canonical.size(),
              "R2c7 original curve source-site count is incomplete");
      for (unsigned i = 0; i < canonical.size(); ++i) {
        const auto& actual = observed.ordered_by_original_parameter[i];
        const auto& source = canonical[i];
        Require(actual.t == source.parameter &&
                    actual.node_id == source.source_node_id &&
                    NearSource(actual.xyz, source.physical),
                "R2c7 all-side original source node/parameter/XYZ mismatch");
      }
      incidences[curve].push_back(std::move(observed));
      ++report.side_incidences;
    }
    Require(patch->GetSubMesh() == accepted_tri.at(p),
            "R2c7 all-sides contour unexpectedly replaced production TRI");
  }
  Require(report.contours == expected_patches &&
              report.side_incidences == 4U * expected_patches &&
              report.directed_edges == report.physical_copy_owners &&
              independent_owners.size() == report.physical_copy_owners &&
              incidences.size() == topology.curves,
          "R2c7 complete original AFT boundary graph is not covered");
  for (const auto& entry : incidences) {
    const auto& sides = entry.second;
    for (std::size_t i = 0; i < sides.size(); ++i)
      for (std::size_t j = i + 1U; j < sides.size(); ++j) {
        const auto comparison = apmesh::quad::CompareSharedCurveSides(
            sides[i], sides[j], false, true);
        Require(comparison.matched,
                "R2c7 original source partitions diverge across AFT boundaries");
        ++report.shared_source_pairs;
        report.compared_shared_sites += comparison.compared_sites;
      }
  }
  // A real, originally adapted node is corrupted before native capture.
  // The source sample/ID/UV checks must reject it without changing TRI.
  auto* first = dynamic_cast<PatchBezier*>(original.GetPatch(0));
  Require(first != nullptr, "R2c7 source patch vanished before fault trial");
  bool rejected_invalid_copy = false;
  try {
    static_cast<void>(BuildDetachedSourceBoundaryImpl(
        *first, 0U, nullptr, true, true));
  } catch (const std::exception&) {
    rejected_invalid_copy = true;
  }
  Require(rejected_invalid_copy &&
              first->GetSubMesh() == accepted_tri.at(0),
          "R2c7 injected wrong node owner escaped native boundary preflight");
  ++report.rejected_owner_faults;

  // Adversarial value-only shared-seam controls never modify physical owners.
  bool shared_checked = false;
  for (const auto& entry : incidences) {
    if (entry.second.size() < 2U) continue;
    const auto& left = entry.second[0];
    const auto& right = entry.second[1];
    auto broken_node = right;
    ++broken_node.ordered_by_original_parameter[0].node_id;
    Require(!apmesh::quad::CompareSharedCurveSides(
                left, broken_node, false, true).matched,
            "R2c7 shared source node identity fault escaped");
    ++report.rejected_snapshot_faults;
    auto broken_xyz = right;
    broken_xyz.ordered_by_original_parameter[0].xyz[0] += 1.0;
    Require(!apmesh::quad::CompareSharedCurveSides(
                left, broken_xyz, false, true).matched,
            "R2c7 shared source XYZ deformation escaped");
    ++report.rejected_snapshot_faults;
    shared_checked = true;
    break;
  }
  Require(shared_checked && report.rejected_owner_faults == 1U &&
              report.rejected_snapshot_faults == 2U,
          "R2c7 all-sides native source controls are incomplete");
  return report;
}

struct WholeModelSourceEpochReport {
  std::size_t original_patches = 0;
  std::size_t original_curves = 0;
  std::size_t original_curve_incidences = 0;
  std::size_t shared_original_curves = 0;
  std::size_t nonmanifold_original_curves = 0;
  std::size_t refined_original_curves = 0;
  std::size_t unchanged_two_endpoint_curves = 0;
  std::size_t adapted_source_points = 0;
  std::size_t adapted_source_intervals = 0;
  std::size_t complete_incidence_sites = 0;
  std::size_t complete_incidence_intervals = 0;
  std::size_t shared_source_incidence_pairs = 0;
  std::size_t shared_source_site_pair_comparisons = 0;
  std::size_t shared_source_interval_pair_comparisons = 0;
  std::size_t shared_opposite_source_traversal_pairs = 0;
  std::size_t shared_same_source_traversal_pairs = 0;
  std::size_t maximum_original_curve_valence = 0;
  std::size_t corrupted_source_snapshots_rejected = 0;
  std::size_t initial_tri_observers_preserved = 0;
  std::size_t curves_with_curve_and_surface_pass = 0;
};

WholeModelSourceEpochReport RunWholeOriginalModelTwoPassCurveSweep(
    const std::string& source_path, unsigned expected_patches) {
  Geometry original;
  PatchReader reader;
  Require(reader.ReaderFilePatches(&original, source_path) == &original &&
              original.GetNumberPatches() == expected_patches &&
              original.GetNumberCurves() > 0U,
          "Original full-model source curve sweep input was invalid");
  const auto topology = apmesh::quad::BuildSharedCurveTopology(original);
  Require(topology.patches == expected_patches &&
              topology.curves == original.GetNumberCurves(),
          "Original whole-model curve topology was modified");
  Performer::RangedIdManager id_manager(0, 0, 100000, 100000, 2);
  id_manager.setId(100);
  id_manager.setId(1, 200);
  apmesh::generation::CurveSampleLifetime lifetime(original);
  std::vector<std::unique_ptr<SubMesh>> coarse;
  coarse.reserve(expected_patches);
  for (unsigned p = 0; p < expected_patches; ++p) {
    auto* patch = dynamic_cast<PatchCoons*>(original.GetPatch(p));
    Require(patch != nullptr,
            "Whole-model original curve sweep contains foreign Patch type");
    coarse.push_back(
        apmesh::generation::BuildInitialSubMesh(patch, &id_manager));
  }
  std::vector<SubMesh*> accepted_coarse_tri;
  accepted_coarse_tri.reserve(expected_patches);
  for (unsigned p = 0; p < expected_patches; ++p) {
    auto* patch = original.GetPatch(p);
    Require(patch->GetSubMesh() == coarse[p].get(),
            "Whole-model initial original coarse TRI observer was not accepted");
    accepted_coarse_tri.push_back(patch->GetSubMesh());
  }

  for (unsigned c = 0; c < original.GetNumberCurves(); ++c) {
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(
        original.GetCurve(c));
    Require(curve && curve->GetNumBerPoints() == 2U &&
                curve->GetNumBerPatches() == topology.incidence[c].size(),
            "Whole-model source curve was not initialized exactly once");
    curve->UpdateParameters({0.0, 1.0});
    curve->CalculateLengthCurve();
    Require(std::isfinite(curve->GetLength()) && curve->GetLength() > 0.0,
            "Original whole-model source curve length is invalid");
  }

  // The original serial sorter requires a process-local comparator scratch.
  // Its prior contents are restored after this independent source fixture.
  struct ScopedCurveComparatorScratch {
    std::vector<CurveAdaptiveParametric*> saved;
    ScopedCurveComparatorScratch() : saved(std::move(ptr_aux)) {
      ptr_aux.resize(1U, nullptr);
    }
    ~ScopedCurveComparatorScratch() { ptr_aux = std::move(saved); }
  } sort_scratch;

  Adapter original_adapter;
  WholeModelSourceEpochReport report;
  report.original_patches = expected_patches;
  report.original_curves = original.GetNumberCurves();
  report.original_curve_incidences = 4U * expected_patches;
  report.shared_original_curves = topology.shared_curves;
  report.nonmanifold_original_curves = topology.nonmanifold_curves;
  const std::vector<CurveAdaptiveParametric*> original_curve_pointers = [&] {
    std::vector<CurveAdaptiveParametric*> pointers;
    pointers.reserve(original.GetNumberCurves());
    for (unsigned c = 0; c < original.GetNumberCurves(); ++c)
      pointers.push_back(static_cast<CurveAdaptiveParametric*>(
          original.GetCurve(c)));
    return pointers;
  }();
  // Exactly one serial outer transaction owns the full list/parameter graph
  // while the actual original two-pass Adapter primitives visit every curve.
  {
    apmesh::generation::CurveSampleGraphTransaction all_curves(&original);
    auto& cache = all_curves.Cache();
    for (auto* curve : original_curve_pointers) {
      apmesh::generation::RefineCurveSamples(
          curve, cache,
          [&] {
            return original_adapter.AdaptCurveByCurve(
                curve, cache, &id_manager, 1.0);
          },
          [&] {
            return original_adapter.AdaptCurveBySurface(
                curve, cache, &id_manager, 1.0);
          },
          false, 0, &id_manager);
      ++report.curves_with_curve_and_surface_pass;
    }
    all_curves.Commit();
  }
  Require(report.curves_with_curve_and_surface_pass ==
              report.original_curves,
          "Original full-model sweep skipped a source curve adaptation pass");

  std::vector<std::vector<AllCurveIncidenceSnapshot>> incidences(
      original.GetNumberCurves());
  for (unsigned c = 0; c < original.GetNumberCurves(); ++c) {
    auto* curve = original_curve_pointers[c];
    Require(curve == original.GetCurve(c),
            "Original whole-model curve pointer changed across adaptation");
    const auto sites = SnapshotAnyOriginalSourceCurve(*curve);
    report.adapted_source_points += sites.size();
    report.adapted_source_intervals += sites.size() - 1U;
    if (sites.size() > 2U) ++report.refined_original_curves;
    else ++report.unchanged_two_endpoint_curves;
    const auto& group = topology.incidence[c];
    report.maximum_original_curve_valence =
        std::max(report.maximum_original_curve_valence, group.size());
    for (const auto& incidence : group) {
      auto* patch = dynamic_cast<PatchBezier*>(
          original.GetPatch(static_cast<unsigned>(incidence.patch)));
      Require(patch && patch->GetSubMesh() ==
                  accepted_coarse_tri[incidence.patch],
              "Original source all-curve sweep rebound the accepted TRI Patch");
      AllCurveIncidenceSnapshot side{
          static_cast<unsigned>(incidence.patch), incidence.side,
          curve->GetId(), patch->IsCurveReversed(incidence.side), sites};
      ValidateWholeModelSourceIncidence(*patch, *curve, side);
      report.complete_incidence_sites += side.canonical_source_sites.size();
      report.complete_incidence_intervals +=
          side.canonical_source_sites.size() - 1U;
      incidences[c].push_back(std::move(side));
    }
    Require(incidences[c].size() == group.size(),
            "Original full-model source curve incidence coverage incomplete");
  }
  Require(report.maximum_original_curve_valence == expected_patches &&
              report.complete_incidence_intervals >= 4U * expected_patches &&
              report.adapted_source_points ==
                  report.adapted_source_intervals + report.original_curves,
          "Whole-model source curve sweep has incomplete interval coverage");

  bool negative_pair_tested = false;
  for (unsigned c = 0; c < incidences.size(); ++c) {
    auto& group = incidences[c];
    for (unsigned i = 0; i < group.size(); ++i)
      for (unsigned j = i + 1U; j < group.size(); ++j) {
        Require(SameCanonicalWholeModelSide(group[i], group[j]),
                "Original all-curve shared incidence has divergent source samples");
        ++report.shared_source_incidence_pairs;
        report.shared_source_site_pair_comparisons +=
            group[i].canonical_source_sites.size();
        report.shared_source_interval_pair_comparisons +=
            group[i].canonical_source_sites.size() - 1U;
        const int direction_a = (group[i].side < 2U ? 1 : -1) *
                                (group[i].reversed ? -1 : 1);
        const int direction_b = (group[j].side < 2U ? 1 : -1) *
                                (group[j].reversed ? -1 : 1);
        if (direction_a == -direction_b)
          ++report.shared_opposite_source_traversal_pairs;
        else
          ++report.shared_same_source_traversal_pairs;
        if (!negative_pair_tested) {
          auto broken = group[j];
          broken.canonical_source_sites[0].source_node_id += 55555UL;
          Require(!SameCanonicalWholeModelSide(group[i], broken),
                  "Original whole-model pairwise source identity fault escaped");
          ++report.corrupted_source_snapshots_rejected;
          negative_pair_tested = true;
        }
      }
  }
  Require(negative_pair_tested &&
              report.shared_source_incidence_pairs > 0 &&
              report.shared_source_interval_pair_comparisons > 0,
          "Original all-curve high-valence shared source pairs were not audited");

  const auto& radial = incidences.at(
      [&] {
        for (unsigned i = 0; i < incidences.size(); ++i)
          if (incidences[i].size() == expected_patches) return i;
        throw std::runtime_error(
            "Original whole-model high-valence curve owner not found");
      }());
  Require(!radial.empty(), "Missing original high-valence source incidence");
  auto* radial_patch = dynamic_cast<PatchBezier*>(
      original.GetPatch(radial.front().patch_id));
  Require(radial_patch != nullptr,
          "Missing original high-valence incidence source patch");
  const auto* radial_curve = dynamic_cast<CurveAdaptiveParametric*>(
      radial_patch->GetCurve(radial.front().side));
  Require(radial_curve != nullptr,
          "Missing original high-valence incidence source curve");
  report.corrupted_source_snapshots_rejected +=
      RejectWholeModelSourceSnapshotCorruptions(
          *radial_patch, *const_cast<CurveAdaptiveParametric*>(radial_curve),
          radial.front());
  Require(report.corrupted_source_snapshots_rejected == 7U,
          "Whole-model original source negative snapshot cases incomplete");

  for (unsigned p = 0; p < expected_patches; ++p) {
    auto* patch = original.GetPatch(p);
    Require(patch->GetSubMesh() == accepted_coarse_tri[p],
            "Whole-model all-curve source sweep mutated original TRI observer");
    ++report.initial_tri_observers_preserved;
  }
  const auto all_sides = AuditWholeModelAllSidesAftBoundaries(
      original, topology, accepted_coarse_tri, expected_patches);
  Require(all_sides.directed_edges == report.complete_incidence_intervals &&
              all_sides.shared_source_pairs ==
                  report.shared_source_incidence_pairs &&
              all_sides.compared_shared_sites ==
                  report.shared_source_site_pair_comparisons,
          "R2c7 all-sides AFT native source coverage diverged from R2c6");
  std::cout << "R2C7_ALL_SIDES_AFT_BOUNDARIES"
            << " original_patches=" << all_sides.contours
            << " all_original_adapted_patch_sides=" << all_sides.side_incidences
            << " native_aft_directed_edges=" << all_sides.directed_edges
            << " separate_physical_copy_owners=" << all_sides.physical_copy_owners
            << " shared_curve_incidence_pairs=" << all_sides.shared_source_pairs
            << " shared_source_site_comparisons=" << all_sides.compared_shared_sites
            << " rejected_invalid_owner_trials=" << all_sides.rejected_owner_faults
            << " rejected_shared_snapshot_trials=" << all_sides.rejected_snapshot_faults
            << " native_boundary_closed_ccw=1"
            << " all_four_original_sides_adapted=1"
            << " disconnected_patch_owners=1"
            << " accepted_TRI_Patch_observers_preserved=1"
            << " original_GeneratorAdaptive_Domain_epoch=0"
            << " complete_physical_QUAD_AFT_mesh=0"
            << " cross_patch_node_welding=0"
            << " advisor_sheet_approval=0
";
  std::cout << "R2C6_WHOLE_ORIGINAL_MODEL_SOURCE_CURVES"
            << " original_patches=" << report.original_patches
            << " original_curves=" << report.original_curves
            << " all_original_curves_two_pass=" << report.curves_with_curve_and_surface_pass
            << " original_curve_incidences=" << report.original_curve_incidences
            << " original_shared_curves=" << report.shared_original_curves
            << " original_nonmanifold_curves=" << report.nonmanifold_original_curves
            << " refined_original_curves=" << report.refined_original_curves
            << " unchanged_two_endpoint_curves="
            << report.unchanged_two_endpoint_curves
            << " adapted_source_points=" << report.adapted_source_points
            << " adapted_source_intervals=" << report.adapted_source_intervals
            << " complete_incidence_sites=" << report.complete_incidence_sites
            << " complete_incidence_intervals=" << report.complete_incidence_intervals
            << " shared_source_incidence_pairs="
            << report.shared_source_incidence_pairs
            << " shared_source_site_pair_comparisons="
            << report.shared_source_site_pair_comparisons
            << " shared_source_interval_pair_comparisons="
            << report.shared_source_interval_pair_comparisons
            << " opposite_oriented_incidence_pairs="
            << report.shared_opposite_source_traversal_pairs
            << " same_oriented_incidence_pairs="
            << report.shared_same_source_traversal_pairs
            << " maximum_source_valence=" << report.maximum_original_curve_valence
            << " rejected_source_snapshot_controls="
            << report.corrupted_source_snapshots_rejected
            << " preserved_original_TRI_Patch_observers="
            << report.initial_tri_observers_preserved
            << " single_original_curve_graph_transaction=1"
            << " full_generator_policy_targets_computed=0"
            << " accepted_GeneratorAdaptive_Domain_epoch=0"
            << " independent_physical_seam_nodes_proved=0"
            << " nonmanifold_sheet_owner_approved=0"
            << " global_mesh_published=0\n";
  return report;
}

void RunSource(const std::string& source, unsigned expected, bool refined) {
  Geometry original;
  PatchReader reader;
  Require(reader.ReaderFilePatches(&original, source) == &original &&
              original.GetNumberPatches() == expected,
          "Original source model does not match chart cardinality");
  std::unique_ptr<MeshAdaptive> active = std::make_unique<MeshAdaptive>();
  auto* initial_patch = dynamic_cast<PatchBezier*>(original.GetPatch(0));
  Require(initial_patch != nullptr, "Missing initial original Bezier chart");
  ChartCounts initial_counts;
  active->InsertSubMeshAdaptive(
      BuildOriginalAftChart(*initial_patch, 0U, refined, initial_counts).release());
  MeshAdaptive* const prior = active.get();
  SubMesh* const prior_chart = active->GetSubMeshAdaptiveByPosition(0);
  NodeAdaptive* const prior_node = prior_chart->GetNoh(0);
  ElementAdaptive* const prior_element = prior_chart->GetElement(0);
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
                active->GetNumberSubMeshesAdaptive() == 1U &&
                active->GetSubMeshAdaptiveByPosition(0) == prior_chart &&
                prior_chart->GetNoh(0) == prior_node &&
                prior_chart->GetElement(0) == prior_element,
            "Fault changed the already-accepted original physical chart");
    ++rejected;
  }

  DisjointOwnerStage staged(expected);
  ChartCounts total;
  std::vector<SourceCurveIncidence> source_incidences;
  source_incidences.reserve(expected * 4U);
  for (unsigned i = 0; i < expected; ++i) {
    auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(i));
    Require(patch != nullptr, "Missing original source Bezier chart");
    ChartCounts count;
    staged.Add(BuildOriginalAftChart(*patch, i, refined, count));
    total.nodes += count.nodes;
    total.quads += count.quads;
    total.tris += count.tris;
    source_incidences.insert(source_incidences.end(),
                             count.source_sides.begin(),
                             count.source_sides.end());
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
  const auto seams =
      AuditReadOnlySourceSeams(source_incidences, expected);
  CheckSourceSeamNegativeControls(source_incidences, expected);
  std::cout << "R2C2_SOURCE_CURVE_SITES"
            << " original_patches=" << expected
            << " source_incidences=" << seams.source_incidences
            << " source_site_checks=" << seams.source_site_checks
            << " shared_curve_groups=" << seams.shared_curve_groups
            << " shared_incidence_pairs=" << seams.shared_incidence_pairs
            << " shared_curve_site_pair_checks="
            << seams.pairwise_source_site_checks
            << " max_source_valence=" << seams.max_source_valence
            << " rejected_negative_controls=4"
            << " physical_boundary_samples=real_SubMesh_nodes"
            << " original_curve_order=1"
            << " source_sheet_continuity_approved=0"
            << " global_seam_conformity_proved=0"
            << " patch_observers_touched=0\n";
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
    RunNativeOriginalSharedCurveAdaptation(argv[1], 4U);
    RunNativeOriginalSharedCurveAdaptation(argv[2], 28U);
    RunWholeOriginalModelTwoPassCurveSweep(argv[1], 4U);
    RunWholeOriginalModelTwoPassCurveSweep(argv[2], 28U);
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "R2c2 full original AFT detached staging failed: "
              << error.what() << '\n';
    return 1;
  }
}
