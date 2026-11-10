#include "adapter/adapter.h"
#include "crab_mesh/performer/ranged_id_manager.h"
#include "data/geometry.h"
#include "data/mesh/sub_mesh.h"
#include "data/patch/patch_coons.h"
#include "generator/curve_sample_lifetime.h"
#include "generator/initial_mesh.h"
#include "input_output/models_3d.h"
#include "quadtree_quad.h"

#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {
using apmesh::quad::AttemptUvCapture;
using apmesh::quad::CaptureHooks;
using apmesh::quad::LocalSelectionEvent;
using apmesh::quad::LocalSelectionKind;
using Par2DJMesh::AFT::Quadtree;

struct IntentionalCaptureAbort final {};
void Require(bool condition, const char* message) {
  if (!condition) {
    throw std::runtime_error(message);
  }
}

struct CaseResult {
  unsigned snapshots = 0;
  unsigned local_decisions = 0;
  unsigned source_leaves = 0;
  unsigned polygon_count = 0;
  unsigned output_triangles = 0;
};

// The real production-owned single-patch geometry and the real coarse TRI
// initializer are used. No synthetic Quadtree or mocked Adapter is involved.
CaseResult RunPatch(bool abort_during_capture) {
  std::cerr << "m3_live_stage=begin abort=" << abort_during_capture << std::endl;
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
  Require(patch->GetSubMesh() == previous.get() && previous->GetNumberElements() == 4,
          "Fixture failed to publish original TRI coarse mesh");

  Adapter adapter;
  std::vector<AttemptUvCapture> snapshots;
  std::vector<LocalSelectionEvent> decisions;
  CaptureHooks hooks;
  hooks.provider = [](Quadtree& tree) { return apmesh::quad::CaptureLeafPolygons(tree); };
  hooks.sink = [&](AttemptUvCapture snapshot) {
    Require(snapshot.attempt.patch_index == 0 &&
                snapshot.attempt.adaptive_step == 1 &&
                snapshot.attempt.retry_index == 0 &&
                snapshot.attempt.local_attempt == 0,
            "Real Adapter lost patch/step/retry/attempt provenance");
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
  adapter.SetResearchUvCapture(std::move(hooks));
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
  Require(interrupted == abort_during_capture,
          "Actual Adapter did not preserve the intentional observer exception");
  Require(patch->GetSubMesh() == previous.get(),
          "Actual capture mutated the accepted coarse patch observer");

  CaseResult result;
  result.snapshots = static_cast<unsigned>(snapshots.size());
  result.local_decisions = static_cast<unsigned>(decisions.size());
  Require(result.snapshots == 1, "Expected exactly one real UV capture");
  result.source_leaves = snapshots.front().polygons.source_leaves;
  result.polygon_count = static_cast<unsigned>(
      snapshots.front().polygons.input.polygons.size());

  if (abort_during_capture) {
    Require(!generated && decisions.empty(),
            "Aborted capture published a local selection or mesh");
  } else {
    Require(generated && generated->GetNumberElements() > 0,
            "Real Adapter did not return generated TRI elements");
    Require(decisions.size() == 1 &&
                decisions.front().kind == LocalSelectionKind::SelectedForAdapterReturn &&
                decisions.front().attempt.local_attempt == 0 &&
                decisions.front().attempt.patch_index == 0 &&
                decisions.front().attempt.adaptive_step == 1,
            "Real Adapter did not publish the correct local TRI selection");
    result.output_triangles = generated->GetNumberElements();
  }
  // The original patch binding is preserved independently of the output.
  // Unbind before both mesh owners and the geometry are destroyed.
  patch->SetSubMesh(nullptr);
  std::cerr << "m3_live_stage=before_fixture_destruct" << std::endl;
  return result;
}

} // namespace

int main() {
  try {
    const auto normal = RunPatch(false);
    const auto failed = RunPatch(true);
    Require(normal.source_leaves > 0 && failed.source_leaves > 0,
            "No refined real Quadtree was observed");
    Require(normal.polygon_count > 0 && failed.polygon_count > 0,
            "No actual UV polygon graph was transferred");
    Require(normal.local_decisions == 1 && failed.local_decisions == 0,
            "Failure and success published indistinguishable local decisions");
    std::cout << "real_adapter_capture_cases=2 normal_triangles="
              << normal.output_triangles << " snapshots="
              << (normal.snapshots + failed.snapshots)
              << " selected=" << normal.local_decisions
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
