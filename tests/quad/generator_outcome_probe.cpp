#include "application/runtime_config.h"
#include "generator/generator_adaptive.h"
#include "timer/timer.h"
#include "adapter_capture.h"

#include <cstdint>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace {
using Key = std::tuple<std::uint64_t, std::uint64_t, int>;

void Require(bool valid, const char* message) {
  if (!valid) {
    throw std::runtime_error(message);
  }
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
  apmesh::quad::CaptureHooks hooks;
  hooks.provider = [&](Par2DJMesh::AFT::Quadtree& tree) {
    // The M3-6c contract is global chronology, not a scientific polygon rule.
    Require(tree.getRoot() != nullptr, "Global fixture observed an uninitialized tree");
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
    source_leaves += capture.polygons.source_leaves;
    ++captured_calls;
    uv_attempts.push_back(capture.attempt.outer);
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
  Require(!locally_selected.empty(),
          "Real generator did not emit any local Adapter selections");
  std::set<Key> uv_keys;
  for (const auto& outer : uv_attempts) {
    uv_keys.insert(OuterKey(outer));
  }
  for (const auto& outer : locally_selected) {
    Require(uv_keys.count(OuterKey(outer)) > 0,
            "Locally selected Adapter event lacks matching UV capture namespace");
  }

  // Outer global commit/restore decisions are not equivalent to physical QUAD.
  std::cout << "real_generator_outcomes=1 accepted_tri=" << accepted
            << " restored_tri=" << restored
            << " budget_evaluations=" << budget
            << " growth_evaluations=" << growth
            << " uv_captures=" << captured_calls
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
