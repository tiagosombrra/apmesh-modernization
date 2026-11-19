// Read-only original-generator pre-AFT Quadtree observability.
// This source is distinct from the frozen R2.7.30 local TRI selection probe.
#include "application/runtime_config.h"
#include "generator/generator_adaptive.h"
#include "timer/timer.h"
#include "adapter_capture.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <limits>
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
  std::size_t selection_event_order = 0;
  apmesh::quad::CaptureHooks hooks;
  hooks.provider = [&](Par2DJMesh::AFT::Quadtree& tree) {
    // The M3-6c contract is global chronology, not a scientific polygon rule.
    Require(tree.getRoot() != nullptr, "Global fixture observed an uninitialized tree");
    // The observer reads provisional pre-AFT UV source cells by value only.
    // Unsupported source trees are reported, never coerced into TRI geometry.
    try {
      if (tree.GetLeafCount() > 25000) {
        throw std::runtime_error("pre-AFT UV source-tree bound exceeded");
      }
      return apmesh::quad::CaptureLeafPolygons(tree);
    } catch (const std::exception&) {
      apmesh::quad::LeafPolygonMesh unsupported;
      unsupported.source_leaves = tree.GetLeafCount();
      return unsupported;
    }
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
    const auto& mesh = capture.polygons;
    const bool supported = !mesh.input.polygons.empty() &&
        mesh.origins.size() == mesh.input.polygons.size() &&
        !mesh.input.vertices.empty() && mesh.source_leaves > 0;
    std::array<std::size_t, 6> patterns{};
    double min_u = 0.0, min_v = 0.0, max_u = 0.0, max_v = 0.0;
    if (supported) {
      min_u = max_u = mesh.input.vertices.front().u;
      min_v = max_v = mesh.input.vertices.front().v;
      for (const auto& v : mesh.input.vertices) {
        Require(std::isfinite(v.u) && std::isfinite(v.v),
                "Observed pre-AFT UV source contains nonfinite coordinate");
        min_u = std::min(min_u, v.u);
        min_v = std::min(min_v, v.v);
        max_u = std::max(max_u, v.u);
        max_v = std::max(max_v, v.v);
      }
      for (const auto& origin : mesh.origins) {
        const auto pattern = static_cast<unsigned>(origin.pattern);
        Require(pattern >= 1U && pattern <= 6U,
                "Observed original source leaf has invalid T1-T6 pattern");
        ++patterns[pattern - 1];
      }
      Require(std::isfinite(static_cast<double>(mesh.interior_area)) &&
                  mesh.interior_area > 0.0L,
              "Observed original pre-AFT UV area is invalid");
    }
    // A successful source tree yields summary only, not selected local TRI.
    // The original selection stream is paired with captures by strict ordinal.
    const auto& a = capture.attempt;
    std::cout << std::setprecision(17)
              << "R2732_UV_CAPTURE=ordinal=" << captured_calls
              << ",outer_epoch=" << a.outer.epoch
              << ",outer_retry=" << a.outer.global_retry
              << ",step=" << a.adaptive_step
              << ",retry=" << a.retry_index
              << ",patch=" << a.patch_index
              << ",local=" << a.local_attempt
              << ",status=" << (supported ? "qualified" : "unsupported")
              << ",leaves=" << mesh.source_leaves
              << ",excluded=" << mesh.excluded_boundary_leaves
              << ",vertices=" << mesh.input.vertices.size()
              << ",polygons=" << mesh.input.polygons.size()
              << ",area=" << static_cast<double>(mesh.interior_area)
              << ",u_min=" << min_u << ",v_min=" << min_v
              << ",u_max=" << max_u << ",v_max=" << max_v;
    for (const auto count : patterns) {
      std::cout << ",pattern=" << count;
    }
    std::cout << '\n';
  };
  hooks.local_selection_sink = [&](apmesh::quad::LocalSelectionEvent event) {
    Require(event.attempt.outer.session == session && event.attempt.outer.epoch > 0,
            "Local Adapter decision lost outer generator epoch");
    Require(++selection_event_order <= 8192,
            "Research local-selection observer exceeded maximum bounded events");
    Require(event.attempt.adaptive_step > 0 && event.attempt.patch_index >= 0 &&
                event.attempt.local_attempt >= 0,
            "Research local-selection observer received an invalid patch attempt");
    const char* kind = "generation_failed";
    if (event.kind == apmesh::quad::LocalSelectionKind::SelectedForAdapterReturn) {
      kind = "selected";
      locally_selected.push_back(event.attempt.outer);
    } else if (event.kind == apmesh::quad::LocalSelectionKind::Superseded) {
      kind = "superseded";
    }
    // The original Adapter emits these events only after choosing its local return.
    // An Adapter-local selection is never an accepted global TRI epoch.
    std::cout << "R2730_LOCAL_SELECTION=ordinal=" << selection_event_order
              << ",session=" << event.attempt.outer.session
              << ",outer_epoch=" << event.attempt.outer.epoch
              << ",outer_retry=" << event.attempt.outer.global_retry
              << ",step=" << event.attempt.adaptive_step
              << ",retry=" << event.attempt.retry_index
              << ",patch=" << event.attempt.patch_index
              << ",local=" << event.attempt.local_attempt
              << ",kind=" << kind
              << ",status=" << event.generation_status << '\n';
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
    std::cerr << "Usage: quad_generator_local_selection_probe CONFIG_PATH\n";
    return 2;
  }
  try {
    return Run(argv[1]);
  } catch (const std::exception& error) {
    std::cerr << "M3-6c real generator outcome failure: " << error.what() << '\n';
    return 1;
  }
}
