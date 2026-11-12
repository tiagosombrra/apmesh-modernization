#include "application/runtime_config.h"
#include "generator/generator_adaptive.h"
#include "timer/timer.h"
#include "adapter_capture.h"
#include "source_tree_replay.h"

#include <cstdint>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
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
              corrupt_source_replay_rejected,
          "Real Eistute/Book adapted source tree replay was not independently qualified");
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
            << " boundary_captures=" << original_boundary_callbacks
            << " boundary_source_samples=" << original_boundary_samples
            << " interior_curve_samples=" << original_interior_curve_samples
            << " identical_refined_boundary=" << source_tree_boundary_matches
            << " repeated_logical_attempt_keys=" << repeated_boundary_keys
            << " original_source_trees_replayed=" << replayed_actual_source_trees
            << " original_adapted_boundary_sites=" << replayed_adapted_boundary_sites
            << " original_source_leaves_replayed=" << replayed_actual_source_leaves
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
