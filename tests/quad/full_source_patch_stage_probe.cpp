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
#include "generator/initial_mesh.h"
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
  for (unsigned patch = 0; patch < original.GetNumberPatches(); ++patch) {
    Require(original.GetPatch(patch)->GetSubMesh() ==
                original_coarse_meshes[patch].get(),
            "Source Adapter curve audit modified original accepted TRI observer");
  }
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
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "R2c2 full original AFT detached staging failed: "
              << error.what() << '\n';
    return 1;
  }
}
