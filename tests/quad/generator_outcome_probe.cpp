#include "application/runtime_config.h"
#include "generator/generator_adaptive.h"
#include "timer/timer.h"
#include "adapter_capture.h"
#include "source_tree_replay.h"
#include "interior_template_dispatch.h"
#include "front_interface_audit.h"
#include "owned_aft_front.h"
#include "dynamic_physical_audit.h"
#include "shared_curve_audit.h"
#include "shared_curve_sector_audit.h"

#include "data/geometry.h"
#include "input_output/patch_reader.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace {
using Key = std::tuple<std::uint64_t, std::uint64_t, int>;
using AttemptKey = std::tuple<std::uint64_t, std::uint64_t, int, int, int, int, int>;

AttemptKey Identity(const apmesh::quad::PatchAttemptIdentity& attempt) {
  return {attempt.outer.session, attempt.outer.epoch, attempt.outer.global_retry,
          attempt.patch_index, attempt.adaptive_step,
          attempt.retry_index, attempt.local_attempt};
}

void Require(bool valid, const char* message) {
  if (!valid) {
    throw std::runtime_error(message);
  }
}


// A bounded research diagnostic that executes the ORIGINAL exterior AFT on
// an independently owned clone of the ORIGINAL adapted model Quadtree.
// The result is explicitly classified; a rejected candidate is not a pass
// for physical QUAD admission, even if the regression CTest itself passes.
struct DynamicSourceAftWitness {
  bool attempted = false;
  bool admitted = false;
  std::size_t source_sites = 0;
  std::size_t source_leaves = 0;
  std::size_t quad_faces = 0;
  std::size_t exterior_triangles = 0;
  int source_patch_index = -1;
  apmesh::quad::AdapterBoundaryCapture original_boundary;
  std::vector<apmesh::quad::PhysicalQuadUv> accepted_quad_uv;
  std::vector<apmesh::quad::PhysicalTriangleUv> accepted_tri_uv;
  std::string rejection;
};

DynamicSourceAftWitness ProbeNativeAftOnAdaptedSource(
    Par2DJMesh::AFT::Quadtree& source,
    const apmesh::quad::AdapterBoundaryCapture& contour) {
  using apmesh::quad::InteriorTemplateMode;
  using apmesh::quad::InteriorTemplateDispatcher;
  using apmesh::quad::OwnedQuadAftFront;
  auto legacy = apmesh::quad::ReplayNativeSourceTree(source, contour);
  auto candidate = apmesh::quad::ReplayNativeSourceTree(source, contour);
  DynamicSourceAftWitness result;
  result.attempted = true;
  result.source_sites = contour.vertices.size();
  result.source_leaves = source.GetLeafCount();
  result.source_patch_index = contour.attempt.patch_index;
  result.original_boundary = contour;

  try {
    Require(legacy.owned_tree != nullptr && candidate.owned_tree != nullptr,
            "R2b2 real source has no research-owned Quadtree");
    Require(legacy.owned_tree->makeTemplateBasedMesh() ==
                Par2DJMesh::AFT::QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
            "R2b2 original TRI template reference could not initialize");
    const auto original_front =
        apmesh::quad::SnapshotLegacyFront(*legacy.owned_tree);
    InteriorTemplateDispatcher selector(*candidate.owned_tree);
    const auto select = selector.Select(
        InteriorTemplateMode::ExperimentalQuad,
        [](const apmesh::quad::LeafPolygonOrigin&,
           const std::vector<apmesh::quad::UvVertex>& polygon) {
          apmesh::quad::UvVertex center{};
          for (const auto& site : polygon) {
            center.u += site.u;
            center.v += site.v;
          }
          center.u /= static_cast<double>(polygon.size());
          center.v /= static_cast<double>(polygon.size());
          return center;
        });
    result.quad_faces = select.uv_quads.quads.size();
    auto* tree = candidate.owned_tree.get();
    auto aft = std::make_unique<OwnedQuadAftFront>(tree->getBoundary(), tree);
    candidate.owned_tree.release();
    const auto seeded = aft->Seed(select, original_front);
    Require(seeded.patch_boundary_edges == contour.vertices.size() &&
                seeded.quad_interface_edges > 0 &&
                !seeded.physical_quads_published,
            "R2b2 real adapted AFT seed lost original physical curve perimeter");
    const auto geometry = aft->AttemptExteriorTriangulation(select);
    result.exterior_triangles = geometry.exterior_triangles;
    Require(geometry.exterior_triangles > 0 &&
                geometry.front_drained &&
                geometry.triangles_positive &&
                geometry.seam_orientation_complete &&
                geometry.seam_vertices_unchanged &&
                geometry.uv_area_balanced &&
                geometry.spatial_overlap_tested &&
                geometry.no_spatial_overlap,
            "R2b2 real adapted exterior AFT did not meet all strict UV gates");
    // Freeze every actual AFT TRI and selected QUAD vertex by value while its
    // research-owned native objects are live. Physical evaluation happens
    // ONLY after original TRI GeneratorAdaptive::Execute has completed.
    for (const auto& quad : select.uv_quads.quads) {
      const auto& uv = select.uv_quads.vertices;
      result.accepted_quad_uv.push_back(
          {uv[quad.vertices[0]], uv[quad.vertices[1]],
           uv[quad.vertices[2]], uv[quad.vertices[3]]});
    }
    for (auto* face : aft->Triangles()) {
      Require(face != nullptr && face->getV1() != nullptr &&
                  face->getV2() != nullptr && face->getV3() != nullptr,
              "R2b2 original AFT emitted incomplete TRI face");
      result.accepted_tri_uv.push_back(apmesh::quad::PhysicalTriangleUv{
          apmesh::quad::UvVertex{face->getV1()->getX(), face->getV1()->getY()},
          apmesh::quad::UvVertex{face->getV2()->getX(), face->getV2()->getY()},
          apmesh::quad::UvVertex{face->getV3()->getX(), face->getV3()->getY()}});
    }
    Require(result.accepted_quad_uv.size() == result.quad_faces &&
                result.accepted_tri_uv.size() == result.exterior_triangles,
            "R2b2 actual AFT UV physical witness lost selected face identity");
    result.admitted = true;
  } catch (const std::exception& error) {
    // This is a measured scientific rejection, not a passing hybrid mesh.
    // Every candidate owner is discarded on this path, including partial AFT.
    result.rejection = error.what();
    result.accepted_quad_uv.clear();
    result.accepted_tri_uv.clear();
  }

  Require(source.GetTemplateFaces().empty() &&
              source.GetTemplateEdges().empty() &&
              source.GetFrontEdges().empty(),
          "R2b2 candidate AFT mutated its original in-flight TRI source");
  return result;
}

Key OuterKey(const apmesh::quad::OuterAttemptIdentity& outer) {
  return {outer.session, outer.epoch, outer.global_retry};
}

int Run(const std::string& config_path) {
  const auto config = apmesh::application::LoadRuntimeConfig(config_path);
  Require(config.mesh_element_kind == "tri", "Real generator fixture cannot produce QUAD");
  apmesh::application::ApplyRuntimeConfig(config);

  Timer timer(config.num_processes, config.num_threads, 12);
  const apmesh::application::GenerationRequest request{
      config.num_processes, config.num_threads, config.input_model};
  GeneratorAdaptive generator(apmesh::application::MakeGenerationContext(config, NUMBER_PROCESS));

  constexpr std::uint64_t session = 6306001;
  std::vector<apmesh::quad::OuterAttemptIdentity> uv_attempts;
  std::vector<apmesh::quad::OuterAttemptIdentity> locally_selected;
  std::size_t source_leaves = 0;
  std::size_t captured_calls = 0;
  std::size_t original_boundary_callbacks = 0;
  std::size_t original_boundary_samples = 0;
  std::size_t original_interior_curve_samples = 0;
  std::size_t source_tree_boundary_matches = 0;
  std::size_t replayed_actual_source_trees = 0;
  std::size_t replayed_adapted_boundary_sites = 0;
  std::size_t replayed_actual_source_leaves = 0;
  bool corrupt_source_replay_rejected = false;
  DynamicSourceAftWitness real_source_aft;
  bool source_aft_observed = false;
  // The original generator can revisit a logical patch/retry identity.
  // Chronological callback order, not a uniqueness assumption, joins the
  // actual source boundary to its one refined Quadtree observation.
  std::vector<apmesh::quad::AdapterBoundaryCapture> boundaries;
  std::map<AttemptKey, std::size_t> occurrences;
  std::size_t repeated_boundary_keys = 0;
  apmesh::quad::CaptureHooks hooks;
  hooks.provider = [&](Par2DJMesh::AFT::Quadtree& tree) {
    // The M3-6c contract is global chronology, not a scientific polygon rule.
    Require(tree.getRoot() != nullptr, "Global fixture observed an uninitialized tree");
    Require(!boundaries.empty() &&
                boundaries.size() > source_tree_boundary_matches,
            "Original Adapter did not publish a new boundary before refinement");
    const auto& source_boundary = boundaries.back();
    const auto actual = tree.getBoundary()->getBoundary();
    const auto edges = tree.getBoundary()->getEdges();
    Require(actual.size() == source_boundary.vertices.size() &&
                edges.size() == source_boundary.directed_edges.size(),
            "Real refined Quadtree changed original Adapter boundary count");
    std::size_t offset = 0;
    for (auto* vertex : actual) {
      const auto& source = source_boundary.vertices[offset++];
      Require(vertex->getId() == source.aft_vertex_id &&
                  vertex->getX() == source.uv.u && vertex->getY() == source.uv.v,
              "Real refined Quadtree changed source UV/vertex identity");
    }
    ++source_tree_boundary_matches;
    if (replayed_actual_source_trees == 0 &&
        source_boundary.vertices.size() > 4U) {
      // Build a separate native Quadtree from a REAL adapted Eistute/Book
      // source attempt, never the research fixed 16-site chart.
      const auto replay = apmesh::quad::ReplayNativeSourceTree(tree, source_boundary);
      Require(replay.owned_tree &&
                  replay.original_leaves == replay.replayed_leaves &&
                  replay.replayed_source_vertices == source_boundary.vertices.size() &&
                  replay.matched_leaf_neighbors == tree.GetLeafCount(),
              "Native replay did not preserve the real adapted model Quadtree");
      auto corrupted = source_boundary;
      corrupted.directed_edges.front()[0] += 1.0 / 256.0;
      try {
        static_cast<void>(apmesh::quad::ReplayNativeSourceTree(tree, corrupted));
      } catch (const std::invalid_argument&) {
        corrupt_source_replay_rejected = true;
      }
      Require(corrupt_source_replay_rejected,
              "Native source replay did not reject a modified real curved boundary");
      Require(tree.GetFrontEdges().empty() &&
                  tree.GetTemplateFaces().empty(),
              "Native QUAD source replay published into the original TRI Quadtree");
      real_source_aft = ProbeNativeAftOnAdaptedSource(tree, source_boundary);
      source_aft_observed = real_source_aft.attempted;
      replayed_adapted_boundary_sites += source_boundary.vertices.size();
      replayed_actual_source_leaves += replay.replayed_leaves;
      ++replayed_actual_source_trees;
    }
    apmesh::quad::LeafPolygonMesh snapshot;
    snapshot.source_leaves = tree.GetLeafCount();
    return snapshot;
  };
  hooks.sink = [&](apmesh::quad::AttemptUvCapture capture) {
    Require(capture.disposition == apmesh::quad::CaptureDisposition::PendingTriDecision,
            "UV capture was promoted to accepted geometry");
    Require(capture.attempt.outer.session == session &&
                capture.attempt.outer.epoch > 0,
            "UV capture lost its outer generator namespace");
    Require(!boundaries.empty() &&
                Identity(capture.attempt) == Identity(boundaries.back().attempt) &&
                source_tree_boundary_matches == captured_calls + 1,
            "Refined Quadtree did not join the current source boundary callback");
    source_leaves += capture.polygons.source_leaves;
    ++captured_calls;
    uv_attempts.push_back(capture.attempt.outer);
  };
  hooks.boundary_sink = [&](apmesh::quad::AdapterBoundaryCapture capture) {
    Require(capture.attempt.outer.session == session &&
                capture.attempt.outer.epoch > 0 &&
                !capture.accepted_mesh_published &&
                capture.vertices.size() == capture.directed_edges.size(),
            "Original Adapter boundary has invalid provenance or publication state");
    std::size_t sum = 0;
    for (const auto count : capture.side_counts) {
      Require(count > 0, "Original Adapter dropped a source curve side");
      sum += count;
    }
    Require(sum == capture.vertices.size() && sum >= 4,
            "Adapter boundary lost physical curve samples");
    std::size_t previous_side = 0;
    double previous_local = 0;
    bool first = true;
    for (const auto& point : capture.vertices) {
      Require(point.physical_node_id > 0 &&
                  point.aft_vertex_id > 0 &&
                  point.side < 4U &&
                  point.chart_parameter >= 0.0 &&
                  point.chart_parameter <= 1.0,
              "Adapter source curve identity, UV or node was invalid");
      if (!first && point.side == previous_side)
        Require(point.side < 2U ? point.chart_parameter > previous_local
                                 : point.chart_parameter < previous_local,
                "Adapter boundary lost the original oriented sample order");
      if (point.original_parameter > 1e-8 &&
          point.original_parameter < 1.0 - 1e-8)
        ++original_interior_curve_samples;
      previous_side = point.side;
      previous_local = point.chart_parameter;
      first = false;
    }
    const auto key = Identity(capture.attempt);
    if (++occurrences[key] > 1U)
      ++repeated_boundary_keys;
    boundaries.push_back(std::move(capture));
    original_boundary_samples += sum;
    ++original_boundary_callbacks;
  };
  hooks.local_selection_sink = [&](apmesh::quad::LocalSelectionEvent event) {
    Require(event.attempt.outer.session == session && event.attempt.outer.epoch > 0,
            "Local Adapter decision lost outer generator epoch");
    if (event.kind == apmesh::quad::LocalSelectionKind::SelectedForAdapterReturn) {
      locally_selected.push_back(event.attempt.outer);
    }
  };
  generator.SetResearchUvCapture(std::move(hooks), session);
  Require(generator.GetResearchGlobalOutcomeLog() != nullptr,
          "Research-only global log was not installed");

  const int status = generator.Execute(request, &timer);
  Require(status == 0, "Original TRI generator did not complete successfully");
  const auto* log = generator.GetResearchGlobalOutcomeLog();
  Require(log != nullptr && log->size() > 0,
          "Real GeneratorAdaptive did not publish global outcomes");
  Require(!log->truncated(), "Global outcome trace exceeded its bounded capacity");

  std::size_t accepted = 0;
  std::size_t restored = 0;
  std::size_t budget = 0;
  std::size_t growth = 0;
  std::uint64_t last_epoch = 0;
  std::set<Key> global_epochs;
  for (std::size_t i = 0; i < log->size(); ++i) {
    const auto& event = log->data()[i];
    Require(event.outer.session == session && event.outer.epoch > 0 &&
                event.outer.epoch >= last_epoch && event.outer.global_retry >= 0,
            "Global outcome stream lost monotonic outer epoch");
    Require(event.adaptive_step > 0, "Global event lacks an adaptive step");
    last_epoch = event.outer.epoch;
    global_epochs.insert(OuterKey(event.outer));
    switch (event.kind) {
      case apmesh::quad::GlobalOutcomeKind::AcceptedStepCommitted:
        ++accepted;
        break;
      case apmesh::quad::GlobalOutcomeKind::RejectedStepRestored:
        ++restored;
        break;
      case apmesh::quad::GlobalOutcomeKind::ElementBudgetRejectedCandidate:
        ++budget;
        break;
      case apmesh::quad::GlobalOutcomeKind::GrowthRejectedCandidate:
        ++growth;
        break;
    }
  }

  Require(accepted > 0, "Real generator never committed an accepted TRI step");
  Require(restored > 0, "Real generator never restored a rejected TRI step");
  Require(captured_calls > 0 && source_leaves > 0,
          "Hook-enabled real GeneratorAdaptive never observed a refined Quadtree");
  Require(original_boundary_callbacks >= captured_calls &&
              source_tree_boundary_matches == captured_calls &&
              original_boundary_samples >= 4U * captured_calls &&
              original_interior_curve_samples > 0,
          "Real Generator source AdaptCurve samples were not retained through Quadtree");
  Require(replayed_actual_source_trees == 1 &&
              replayed_adapted_boundary_sites > 4U &&
              replayed_actual_source_leaves > 0 &&
              corrupt_source_replay_rejected && source_aft_observed &&
              real_source_aft.source_sites == replayed_adapted_boundary_sites &&
              real_source_aft.source_leaves == replayed_actual_source_leaves,
          "Real Eistute/Book adapted source tree/AFT diagnostic was not attempted");
  Require(!locally_selected.empty(),
          "Real generator did not emit any local Adapter selections");
  std::set<Key> uv_keys;
  for (const auto& outer : uv_attempts) {
    uv_keys.insert(OuterKey(outer));
  }
  std::size_t joined_local_global = 0;
  for (const auto& outer : locally_selected) {
    const auto key = OuterKey(outer);
    Require(uv_keys.count(key) > 0,
            "Locally selected Adapter event lacks matching UV capture namespace");
    if (global_epochs.count(key) > 0) {
      ++joined_local_global;
    }
  }
  Require(joined_local_global > 0,
          "No selected Adapter attempt was correlated to a real global outcome epoch");

  // Compare an independent BP model to the actual original Adapter source
  // curve XYZ sites and ALL accepted TRI/QUAD UV faces only after original TRI
  // generation/acceptance and restoration traces are complete. ReaderFilePatches
  // is a separate owner; no source or physical SubMesh is replaced.
  bool dynamic_physical_attempted = false;
  bool dynamic_physical_admitted = false;
  bool negative_source_xyz_rejected = false;
  bool negative_inverted_facet_rejected = false;
  bool negative_invalid_uv_rejected = false;
  apmesh::quad::DynamicPhysicalAudit dynamic_physical;
  std::string dynamic_physical_rejection = "not_attempted";
  if (real_source_aft.admitted) {
    dynamic_physical_attempted = true;
    try {
      Geometry independent_geometry;
      PatchReader independent_reader;
      Require(independent_reader.ReaderFilePatches(
                  &independent_geometry, config.input_model) == &independent_geometry,
              "R2b2 dynamic source physical PatchReader failed");
      Require(real_source_aft.source_patch_index >= 0 &&
                  static_cast<unsigned>(real_source_aft.source_patch_index) <
                      independent_geometry.GetNumberPatches(),
              "R2b2 original Adapter patch index diverged from physical model");
      auto* native = dynamic_cast<PatchBezier*>(independent_geometry.GetPatch(
          static_cast<unsigned>(real_source_aft.source_patch_index)));
      Require(native != nullptr, "R2b2 actual source geometry is not PatchBezier");
      const auto* accepted_before = native->GetSubMesh();
      const auto& source = real_source_aft.original_boundary;
      const auto& quads = real_source_aft.accepted_quad_uv;
      const auto& triangles = real_source_aft.accepted_tri_uv;
      dynamic_physical = apmesh::quad::AuditActualAdapterPhysicalFaces(
          *native, source, quads, triangles);

      auto tampered_source = source;
      tampered_source.vertices.front().physical_xyz[0] +=
          0.125 * std::max(1.0,
              apmesh::quad::PhysicalNorm(
                  tampered_source.vertices.front().physical_xyz));
      try {
        static_cast<void>(apmesh::quad::AuditActualAdapterPhysicalFaces(
            *native, tampered_source, quads, triangles));
      } catch (const std::invalid_argument&) {
        negative_source_xyz_rejected = true;
      }
      auto inverted_faces = triangles;
      std::swap(inverted_faces.front()[0], inverted_faces.front()[1]);
      try {
        static_cast<void>(apmesh::quad::AuditActualAdapterPhysicalFaces(
            *native, source, quads, inverted_faces));
      } catch (const std::invalid_argument&) {
        negative_inverted_facet_rejected = true;
      }
      auto invalid_uv_faces = quads;
      invalid_uv_faces.front()[0].u = -0.125;
      try {
        static_cast<void>(apmesh::quad::AuditActualAdapterPhysicalFaces(
            *native, source, invalid_uv_faces, triangles));
      } catch (const std::invalid_argument&) {
        negative_invalid_uv_rejected = true;
      }
      Require(negative_source_xyz_rejected &&
                  negative_inverted_facet_rejected &&
                  negative_invalid_uv_rejected &&
                  native->GetSubMesh() == accepted_before,
              "R2b2 physical negative controls or immutable ownership failed");
      dynamic_physical_admitted = true;
      dynamic_physical_rejection = "none";
    } catch (const std::exception& error) {
      // A physical rejection MUST be visible even if UV AFT was admitted.
      dynamic_physical_rejection = error.what();
    }
  }

  Require(!real_source_aft.admitted || dynamic_physical_attempted,
          "R2b2 accepted UV AFT was not presented for physical admission");


  // Audit the entire actual source model curve-incidence graph from a fresh
  // independently owned PatchReader geometry, then compare ONLY source
  // Adapter captures belonging to one coherent global epoch+retry. The test
  // returns measured rejections, never a fabricated model-wide hybrid mesh.
  Geometry shared_geometry;
  PatchReader shared_reader;
  Require(shared_reader.ReaderFilePatches(
              &shared_geometry, config.input_model) == &shared_geometry,
          "R2b2 shared curve PatchReader failed");
  const auto shared_graph =
      apmesh::quad::BuildSharedCurveTopology(shared_geometry);
  Require(shared_graph.patches == (
              config.input_model.find("book") != std::string::npos ? 28U : 4U),
          "R2b2 external original model patch cardinality changed");
  const auto shared = apmesh::quad::AuditCoherentAdapterSharedCurves(
      shared_graph, boundaries);
  Require(shared.model_curves == shared_geometry.GetNumberCurves() &&
              shared.model_shared_curves > 0U &&
              shared.coherent_epoch_patches > 1U &&
              shared.coherent_epoch_shared_curves_compared > 0U &&
              shared.coherent_epoch_shared_curves_matched +
                  shared.coherent_epoch_shared_curves_rejected ==
                  shared.coherent_epoch_shared_curves_compared &&
              shared.coherent_epoch_shared_curves_geometry_matched +
                  shared.coherent_epoch_shared_curves_geometry_rejected ==
                  shared.coherent_epoch_shared_curves_compared &&
              shared.coherent_epoch_shared_curves_source_ids_matched +
                  shared.coherent_epoch_shared_curves_source_ids_rejected ==
                  shared.coherent_epoch_shared_curves_compared,
          "R2b2 no real same-epoch shared curve interfaces were audited");

  // Check high-valence source sheets as separate geometric radial sectors
  // in XYZ. A cyclic angular ordering is NOT an accepted sheet pairing.
  const auto sectors = apmesh::quad::AuditOriginalHighValenceSectors(
      shared_geometry, shared_graph, boundaries, shared);
  Require(sectors.high_valence_curves_sampled ==
              shared_graph.nonmanifold_curves &&
              sectors.incidences_evaluated ==
                  (shared_graph.patches == 4U ? 4U : 28U) &&
              !sectors.sectors.empty() &&
              !sectors.automatic_sheet_pairing_enabled,
          "R2b2 real central curve sector incidence was not observed");

  // A duplicate radial direction must be classified as an ambiguous sector;
  // a zero physical tangent cannot support any angular sheet ordering.
  auto duplicate_sectors = sectors.sectors.front();
  duplicate_sectors.push_back(duplicate_sectors.front());
  std::sort(duplicate_sectors.begin(), duplicate_sectors.end(),
            [](const apmesh::quad::SharedCurveRadialSector& a,
               const apmesh::quad::SharedCurveRadialSector& b) {
              return a.angle_radians < b.angle_radians;
            });
  bool zero_tangent_rejected = false;
  try {
    static_cast<void>(apmesh::quad::NormalizedPhysical(
        {0.0, 0.0, 0.0}, "R2b2 deliberately invalid curve tangent"));
  } catch (const std::invalid_argument&) {
    zero_tangent_rejected = true;
  }
  const bool sector_negative_controls =
      apmesh::quad::CircularMinimumAngle(duplicate_sectors) == 0.0 &&
      zero_tangent_rejected;
  Require(sector_negative_controls,
          "R2b2 radial source duplicate/tangent negative cases did not reject");

  std::ostringstream sector_order;
  for (const auto& curve : sectors.sectors) {
    for (const auto& sheet : curve) {
      if (sector_order.tellp() > 0) sector_order << ",";
      sector_order << sheet.patch << ":" << sheet.side;
    }
  }
  std::cout << "R2B2_SHARED_SHEET_SECTORS"
            << " patches=" << shared.model_patches
            << " high_valence_curves=" << sectors.high_valence_curves_sampled
            << " curve_incidences=" << sectors.incidences_evaluated
            << " angular_adjacent_pairs=" << sectors.angular_adjacent_pairs
            << " radial_coincident_pairs=" << sectors.radial_coincident_pairs
            << " minimum_cyclic_angle="
            << sectors.minimum_cyclic_angle_radians
            << " max_patch_curve_xyz_error=" << sectors.maximum_curve_xyz_error
            << " source_geometry_admitted=" << sectors.source_geometry_admitted
            << " automatic_sheet_pairing_enabled="
            << sectors.automatic_sheet_pairing_enabled
            << " negative_controls=" << sector_negative_controls
            << " reason=" << sectors.rejection
            << " radial_order=" << sector_order.str() << "\n";

  // Construct four adversarial counterparts from an ACTUAL original Adapter
  // sampled curve, without inventing a new curve or a synthetic UV geometry.
  const auto original_side =
      apmesh::quad::SnapshotSharedCurveSide(boundaries.front(), 0U);
  auto counterparty = original_side;
  counterparty.patch = (original_side.patch + 1U) % shared_graph.patches;
  counterparty.traversal *= -1;
  Require(apmesh::quad::CompareSharedCurveSides(
              original_side, counterparty).matched,
          "R2b2 original source curve self-pair calibration failed");
  auto bad_xyz = counterparty;
  bad_xyz.ordered_by_original_parameter.front().xyz[0] += 0.5 *
      std::max(1.0, apmesh::quad::PhysicalNorm(
          bad_xyz.ordered_by_original_parameter.front().xyz));
  auto bad_node = counterparty;
  ++bad_node.ordered_by_original_parameter.front().node_id;
  auto bad_sampling = counterparty;
  bad_sampling.ordered_by_original_parameter.pop_back();
  auto bad_orientation = counterparty;
  bad_orientation.traversal *= -1;
  const bool shared_negative_controls =
      !apmesh::quad::CompareSharedCurveSides(original_side, bad_xyz).matched &&
      !apmesh::quad::CompareSharedCurveSides(original_side, bad_node).matched &&
      !apmesh::quad::CompareSharedCurveSides(original_side, bad_sampling).matched &&
      !apmesh::quad::CompareSharedCurveSides(original_side, bad_orientation).matched;
  Require(shared_negative_controls &&
              apmesh::quad::CompareSharedCurveSides(
                  original_side, bad_orientation, false).matched &&
              apmesh::quad::CompareSharedCurveSides(
                  original_side, bad_node, false, false).matched,
          "R2b2 real source geometry and multi-sheet orientation controls failed");
  std::ostringstream shared_rejections;
  for (const auto& entry : shared.rejection_reasons) {
    if (shared_rejections.tellp() > 0)
      shared_rejections << ",";
    shared_rejections << entry.first << ":" << entry.second;
  }
  std::cout << "R2B2_SHARED_CURVE_MODEL"
            << " patches=" << shared.model_patches
            << " curves=" << shared.model_curves
            << " shared_curves=" << shared.model_shared_curves
            << " exterior_curves=" << shared.model_exterior_curves
            << " nonmanifold_curves=" << shared.model_nonmanifold_curves
            << " coherent_epoch=" << shared.epoch
            << " coherent_retry=" << shared.retry
            << " coherent_epoch_patches=" << shared.coherent_epoch_patches
            << " shared_compared=" << shared.coherent_epoch_shared_curves_compared
            << " shared_matched=" << shared.coherent_epoch_shared_curves_matched
            << " shared_rejected=" << shared.coherent_epoch_shared_curves_rejected
            << " shared_unobserved=" << shared.coherent_epoch_shared_curves_unobserved
            << " shared_geometry_matched="
            << shared.coherent_epoch_shared_curves_geometry_matched
            << " shared_geometry_rejected="
            << shared.coherent_epoch_shared_curves_geometry_rejected
            << " shared_source_ids_matched="
            << shared.coherent_epoch_shared_curves_source_ids_matched
            << " shared_source_ids_rejected="
            << shared.coherent_epoch_shared_curves_source_ids_rejected
            << " shared_node_id_mismatch_pairs="
            << shared.shared_node_id_mismatch_pairs
            << " shared_node_id_mismatch_sites="
            << shared.shared_node_id_mismatch_sites
            << " shared_node_id_mismatch_endpoints="
            << shared.shared_node_id_mismatch_endpoints
            << " shared_node_id_mismatch_interiors="
            << shared.shared_node_id_mismatch_interiors
            << " sheet_policy_pending=" << shared.coherent_epoch_sheet_policy_pending
            << " same_orientation_pairs=" << shared.shared_same_orientation_pairs
            << " opposite_orientation_pairs=" << shared.shared_opposite_orientation_pairs
            << " shared_node_pairs=" << shared.shared_site_pairs_compared
            << " max_shared_xyz_error=" << shared.maximum_xyz_error
            << " repeated_source_attempts=" << shared.repeated_patch_attempts
            << " negative_controls=" << shared_negative_controls
            << " rejection_reasons="
            << (shared_rejections.str().empty() ? "none" : shared_rejections.str())
            << " physical_SubMesh_published=0"
            << " global_mixed_model_admitted=0\n";

  // Outer global commit/restore decisions are not equivalent to physical QUAD.
  std::cout << "real_generator_outcomes=1 accepted_tri=" << accepted
            << " restored_tri=" << restored
            << " budget_evaluations=" << budget
            << " growth_evaluations=" << growth
            << " uv_captures=" << captured_calls
            << " boundary_captures=" << original_boundary_callbacks
            << " boundary_source_samples=" << original_boundary_samples
            << " interior_curve_samples=" << original_interior_curve_samples
            << " identical_refined_boundary=" << source_tree_boundary_matches
            << " repeated_logical_attempt_keys=" << repeated_boundary_keys
            << " original_source_trees_replayed=" << replayed_actual_source_trees
            << " original_adapted_boundary_sites=" << replayed_adapted_boundary_sites
            << " original_source_leaves_replayed=" << replayed_actual_source_leaves
            << " dynamic_source_aft_attempted=" << source_aft_observed
            << " dynamic_source_aft_admitted=" << real_source_aft.admitted
            << " dynamic_source_aft_quad_faces=" << real_source_aft.quad_faces
            << " dynamic_source_aft_exterior_triangles="
            << real_source_aft.exterior_triangles
            << " dynamic_source_aft_rejection="
            << (real_source_aft.rejection.empty() ? "none" :
                real_source_aft.rejection)
            << " dynamic_physical_attempted=" << dynamic_physical_attempted
            << " dynamic_physical_admitted=" << dynamic_physical_admitted
            << " dynamic_physical_source_nodes="
            << dynamic_physical.source_sites_compared
            << " dynamic_physical_facets=" << dynamic_physical.mapped_facets
            << " dynamic_physical_min_alignment="
            << dynamic_physical.minimum_orientation_alignment
            << " dynamic_physical_max_source_error="
            << dynamic_physical.max_source_xyz_error
            << " dynamic_physical_negative_controls="
            << (negative_source_xyz_rejected &&
                negative_inverted_facet_rejected && negative_invalid_uv_rejected)
            << " dynamic_physical_rejection=" << dynamic_physical_rejection
            << " negative_replay_corruption_rejected="
            << corrupt_source_replay_rejected
            << " local_selected=" << locally_selected.size()
            << " global_epochs=" << global_epochs.size()
            << " truncated=" << log->truncated() << '\n';
  return 0;
}

} // namespace

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "Usage: quad_generator_outcome_probe CONFIG_PATH\n";
    return 2;
  }
  try {
    return Run(argv[1]);
  } catch (const std::exception& error) {
    std::cerr << "M3-6c real generator outcome failure: " << error.what() << '\n';
    return 1;
  }
}
