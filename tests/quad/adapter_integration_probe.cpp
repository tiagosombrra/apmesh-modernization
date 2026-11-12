#include "adapter/adapter.h"
#include "application/generation_context.h"
#include "crab_mesh/performer/ranged_id_manager.h"
#include "data/curve/curve_adaptive_parametric.h"
#include "data/geometry.h"
#include "data/mesh/sub_mesh.h"
#include "data/patch/patch_coons.h"
#include "generator/curve_sample_lifetime.h"
#include "generator/initial_mesh.h"
#include "input_output/models_3d.h"
#include "quadtree_quad.h"

#include <iostream>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// The production generator initializes this legacy curve-sort scratch space.
extern std::vector<CurveAdaptiveParametric*> ptr_aux;

namespace {
using apmesh::quad::AdapterBoundaryCapture;
using apmesh::quad::AttemptUvCapture;
using apmesh::quad::CaptureHooks;
using apmesh::quad::LocalSelectionEvent;
using apmesh::quad::LocalSelectionKind;
using Par2DJMesh::AFT::Quadtree;

struct IntentionalCaptureAbort final {};

// Reproduce the sort-scratch setup performed by GeneratorAdaptive, without
// retaining pointers after this fixture's curves have been destroyed.
struct ScopedLegacyCurveSorting {
  std::vector<CurveAdaptiveParametric*> previous;
  ScopedLegacyCurveSorting() : previous(std::move(ptr_aux)) {
    ptr_aux.resize(1, nullptr);
  }
  ~ScopedLegacyCurveSorting() { ptr_aux = std::move(previous); }
  ScopedLegacyCurveSorting(const ScopedLegacyCurveSorting&) = delete;
  ScopedLegacyCurveSorting& operator=(const ScopedLegacyCurveSorting&) = delete;
};

void Require(bool condition, const char* message) {
  if (!condition) {
    throw std::runtime_error(message);
  }
}

struct CaseResult {
  unsigned snapshots = 0;
  unsigned boundary_snapshots = 0;
  unsigned local_decisions = 0;
  unsigned source_leaves = 0;
  unsigned polygon_count = 0;
  unsigned output_triangles = 0;
  unsigned selected_decisions = 0;
  unsigned superseded_or_failed = 0;
  apmesh::quad::OuterAttemptIdentity outer{};
};

// The real production-owned single-patch geometry and the real coarse TRI
// initializer are used. No synthetic Quadtree or mocked Adapter is involved.
CaseResult RunPatch(bool abort_during_capture,
                    apmesh::quad::OuterAttemptIdentity outer = {},
                    bool abort_during_boundary = false) {
  std::cerr << "m3_live_stage=begin abort=" << abort_during_capture << std::endl;
  ScopedLegacyCurveSorting sort_scratch;
  Geometry geometry;
  Models3d model;
  model.ModelBaseQuadrada(&geometry);
  std::cerr << "m3_live_stage=geometry_created" << std::endl;
  Require(geometry.GetNumberPatches() == 1, "Expected one native square patch");
  auto* patch = dynamic_cast<PatchCoons*>(geometry.GetPatch(0));
  Require(patch != nullptr, "Model patch is not a Coons patch");

  Performer::RangedIdManager id_manager(0, 0, 100000, 100000, 2);
  id_manager.setId(100);
  id_manager.setId(1, 200);
  apmesh::generation::CurveSampleLifetime sample_lifetime(geometry);
  auto previous = apmesh::generation::BuildInitialSubMesh(patch, &id_manager);
  std::cerr << "m3_live_stage=coarse_tri_built" << std::endl;
  for (unsigned i = 0; i < patch->GetNumBerCurves(); ++i) {
    auto* curve = dynamic_cast<CurveAdaptiveParametric*>(patch->GetCurve(i));
    Require(curve != nullptr && curve->GetNumBerPoints() == 2,
            "Fixture did not prepare two curve samples");
    // The production curve-adaptation stage has already produced these values.
    curve->UpdateParameters({0.0, 1.0});
  }
  std::cerr << "m3_live_stage=curve_parameters_ready" << std::endl;
  Require(patch->GetSubMesh() == previous.get() && previous->GetNumberElements() == 4,
          "Fixture failed to publish original TRI coarse mesh");

  // A smaller AFT ratio creates genuine interior cells in this bounded real
  // patch; the former default ratio refined only boundary-adjacent leaves.
  // This is a test-only override, never a production or scientific default.
  apmesh::application::AftConfig fixture_aft;
  fixture_aft.ratio = 0.15;
  Adapter adapter(nullptr, nullptr, &fixture_aft);
  std::vector<AttemptUvCapture> snapshots;
  std::vector<AdapterBoundaryCapture> boundaries;
  std::vector<LocalSelectionEvent> decisions;
  CaptureHooks hooks;
  hooks.provider = [](Quadtree& tree) {
    std::cerr << "m3_live_stage=provider_enter" << std::endl;
    auto data = apmesh::quad::CaptureLeafPolygons(tree);
    std::cerr << "m3_live_stage=provider_return" << std::endl;
    return data;
  };
  hooks.sink = [&](AttemptUvCapture snapshot) {
    std::cerr << "m3_live_stage=sink_enter" << std::endl;
    Require(snapshot.attempt.patch_index == 0 &&
                snapshot.attempt.adaptive_step == 1 &&
                snapshot.attempt.retry_index == 0 &&
                snapshot.attempt.local_attempt >= 0,
            "Real Adapter lost patch/step/retry/attempt provenance");
    Require(apmesh::quad::SameOuterAttempt(snapshot.attempt.outer, outer),
            "Real Adapter UV snapshot has wrong global retry epoch");
    Require(!snapshot.polygons.input.polygons.empty() &&
                !snapshot.polygons.input.vertices.empty() &&
                snapshot.polygons.input.interior_points.empty(),
            "Real Adapter UV capture was empty or invented an interior point");
    snapshots.push_back(std::move(snapshot));
    std::cerr << "m3_live_stage=uv_snapshot_received" << std::endl;
    if (abort_during_capture) {
      throw IntentionalCaptureAbort{};
    }
  };
  hooks.local_selection_sink = [&](LocalSelectionEvent outcome) {
    decisions.push_back(std::move(outcome));
  };
  hooks.boundary_sink = [&](AdapterBoundaryCapture source) {
    Require(source.attempt.patch_index == 0 &&
                source.attempt.adaptive_step == 1 &&
                source.attempt.retry_index == 0 &&
                apmesh::quad::SameOuterAttempt(source.attempt.outer, outer),
            "Real Adapter boundary snapshot lost the original attempt identity");
    Require(source.vertices.size() == 4 && source.directed_edges.size() == 4 &&
                !source.accepted_mesh_published,
            "One-site-per-side square contour was not captured before TRI generation");
    for (unsigned side = 0; side < 4; ++side) {
      const auto& sample = source.vertices[side];
      Require(source.side_counts[side] == 1 && sample.side == side &&
                  sample.source_index == (side >= 2 ? 1U : 0U) &&
                  sample.physical_node_id > 0,
              "Native curve side/parameter/physical node IDs were reordered");
    }
    boundaries.push_back(std::move(source));
    if (abort_during_boundary) throw IntentionalCaptureAbort{};
  };
  adapter.SetResearchUvCapture(std::move(hooks));
  adapter.SetResearchOuterAttempt(outer);
  std::cerr << "m3_live_stage=hooks_registered" << std::endl;
  bool interrupted = false;
  std::unique_ptr<SubMesh> generated;
  try {
    std::cerr << "m3_live_stage=before_real_adapter" << std::endl;
    generated.reset(adapter.AdaptDomain(patch, &id_manager,
                                        1.0, 0.20, 3, 1, 0, 0));
  } catch (const IntentionalCaptureAbort&) {
    interrupted = true;
    std::cerr << "m3_live_stage=expected_abort_observed" << std::endl;
  }
  std::cerr << "m3_live_stage=after_real_adapter" << std::endl;
  Require(interrupted == (abort_during_capture || abort_during_boundary),
          "Actual Adapter did not preserve the intentional observer exception");
  Require(patch->GetSubMesh() == previous.get(),
          "Actual capture mutated the accepted coarse patch observer");

  CaseResult result;
  result.snapshots = static_cast<unsigned>(snapshots.size());
  result.boundary_snapshots = static_cast<unsigned>(boundaries.size());
  result.local_decisions = static_cast<unsigned>(decisions.size());
  result.outer = outer;
  Require(result.snapshots >= (abort_during_capture ? 1U :
                                     (abort_during_boundary ? 0U : 2U)),
          "Expected real UV capture for both the initial and retry attempts");
  Require(result.boundary_snapshots >= 1U &&
              result.boundary_snapshots >= result.snapshots,
          "Real Adapter did not capture the source boundary before refinement");
  std::set<int> captured_attempts;
  for (const auto& observed : snapshots) {
    Require(captured_attempts.insert(observed.attempt.local_attempt).second,
            "Real Adapter called UV capture more than once for the same attempt");
    Require(observed.disposition == apmesh::quad::CaptureDisposition::PendingTriDecision,
            "UV observation was incorrectly marked accepted");
  }
  result.source_leaves = snapshots.front().polygons.source_leaves;
  result.polygon_count = static_cast<unsigned>(
      snapshots.front().polygons.input.polygons.size());

  if (abort_during_capture || abort_during_boundary) {
    Require(!generated && decisions.empty() &&
                (!abort_during_boundary || snapshots.empty()),
            "Aborted capture published a local selection or mesh");
  } else {
    Require(generated && generated->GetNumberElements() > 0,
            "Real Adapter did not return generated TRI elements");
    Require(decisions.size() == snapshots.size(),
            "Real Adapter did not record one local outcome per captured attempt");
    std::set<int> decided_attempts;
    for (const auto& event : decisions) {
      Require(apmesh::quad::SameOuterAttempt(event.attempt.outer, outer),
              "Real Adapter decision lost global retry epoch");
      Require(event.attempt.patch_index == 0 && event.attempt.adaptive_step == 1 &&
                  event.attempt.retry_index == 0,
              "Real local decision lost patch, step or retry provenance");
      Require(captured_attempts.count(event.attempt.local_attempt) == 1 &&
                  decided_attempts.insert(event.attempt.local_attempt).second,
              "Local decision did not correlate with a unique UV observation");
      if (event.kind == LocalSelectionKind::SelectedForAdapterReturn) {
        ++result.selected_decisions;
      } else if (event.kind == LocalSelectionKind::Superseded ||
                 event.kind == LocalSelectionKind::GenerationFailed) {
        ++result.superseded_or_failed;
      }
    }
    Require(result.selected_decisions == 1 && result.superseded_or_failed >= 1,
            "Real fallback did not yield one selected and one nonselected attempt");
    result.output_triangles = generated->GetNumberElements();
  }
  // The original patch binding is preserved independently of the output.
  // Unbind before both mesh owners and the geometry are destroyed.
  patch->SetSubMesh(nullptr);
  std::cerr << "m3_live_stage=before_fixture_destruct" << std::endl;
  return result;
}

} // namespace

int main(int argc, char** argv) {
  try {
    if (argc == 2 && std::string(argv[1]) == "--boundary-abort") {
      // Keep this fault injection in an independent process. The historic
      // three-scenario program is still exercised unchanged in one process.
      const auto aborted = RunPatch(false, {901, 20, 3}, true);
      Require(aborted.boundary_snapshots == 1 &&
                  aborted.snapshots == 0 &&
                  aborted.local_decisions == 0,
              "Pre-refinement Adapter boundary abort published provisional output");
      std::cout << "real_adapter_boundary_abort=ok snapshots=1"
                   " refined_tree_callbacks=0 selected=0"
                   " accepted_submesh_unchanged=1\n";
      return 0;
    }
    Require(argc == 1, "Usage: quad_adapter_integration_probe [--boundary-abort]");
    const auto normal = RunPatch(false, {901, 17, 0});
    const auto repeated = RunPatch(false, {901, 18, 1});
    const auto failed = RunPatch(true, {901, 19, 2});
    Require(normal.local_decisions == repeated.local_decisions &&
                normal.selected_decisions == repeated.selected_decisions &&
                !apmesh::quad::SameOuterAttempt(normal.outer, repeated.outer),
            "Two identical patch/retry paths collided across global epochs");
    Require(normal.source_leaves > 0 && failed.source_leaves > 0,
            "No refined real Quadtree was observed");
    Require(normal.polygon_count > 0 && failed.polygon_count > 0,
            "No actual UV polygon graph was transferred");
    Require(normal.local_decisions >= 2 && normal.selected_decisions == 1 &&
                normal.superseded_or_failed >= 1 && failed.local_decisions == 0,
            "Real retry/local selection and abort decisions were not separated");
    std::cout << "real_adapter_capture_cases=3 normal_triangles="
              << normal.output_triangles << " snapshots="
              << (normal.snapshots + failed.snapshots)
              << " boundary_snapshots="
              << normal.boundary_snapshots + repeated.boundary_snapshots +
                     failed.boundary_snapshots
              << " local_attempts=" << normal.local_decisions
              << " selected=" << normal.selected_decisions
              << " superseded_or_failed=" << normal.superseded_or_failed
              << " aborted_decisions=" << failed.local_decisions << '\n';
    return 0;
  } catch (const std::exception& e) {
    std::cerr << "Real Adapter QUAD capture contract failed: " << e.what() << '\n';
    return 1;
  } catch (...) {
    std::cerr << "Real Adapter QUAD capture contract failed: unexpected exception\n";
    return 1;
  }
}
