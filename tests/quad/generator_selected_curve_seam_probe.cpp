// R2.7.34: isolated original source curve pointer equality and native TRI seam research.
// No raw C++ pointer address escapes this research process.
// R2.7.33: research-only Linux ELF interception of original Adapter return.
// Original ap_mesh_engine, numerical decisions and the R2.7.30 probe stay unchanged.
#include "application/runtime_config.h"
#include "generator/generator_adaptive.h"
#include "timer/timer.h"
#include "adapter_capture.h"

#include "adapter/adapter.h"
#include "data/curve/curve_adaptive.h"
#include "data/patch/patch_coons.h"
#include "data/point_adaptive.h"
#include "data/triangle_adaptive.h"
#include <array>
#include <cmath>
#include <algorithm>
#include <cstdlib>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <optional>
#include <sstream>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace {
using Key = std::tuple<std::uint64_t, std::uint64_t, int>;

// This thread-local state is only visible in the separately linked serial
// research process. The original engine has no dependency on these objects.
thread_local std::optional<apmesh::quad::PatchAttemptIdentity> pending_selected;
thread_local std::size_t selections_since_return = 0;
thread_local std::size_t actual_adapter_returns = 0;
thread_local std::vector<const CurveAdaptive*> original_source_curve_objects;

// The returned ordinal names a source C++ object for this single process only.
// Never serialize, hash or reveal any original C++ address as an identity.
std::size_t OriginalCurveObjectOrdinal(const CurveAdaptive* curve) {
  if (!curve) throw std::runtime_error("R2734 original source curve object missing");
  const auto found = std::find(original_source_curve_objects.begin(),
                               original_source_curve_objects.end(), curve);
  if (found != original_source_curve_objects.end()) {
    return static_cast<std::size_t>(found - original_source_curve_objects.begin());
  }
  if (original_source_curve_objects.size() >= 100) {
    throw std::runtime_error("R2734 original source curve object count exceeded");
  }
  original_source_curve_objects.push_back(curve);
  return original_source_curve_objects.size() - 1;
}
constexpr std::size_t kMaxNativeSelectedFaces = 120000;
constexpr std::size_t kMaxNativeSelectedNodes = 240000;

void WriteSelectedTri(SubMesh& sub, PatchCoons& patch,
                      const apmesh::quad::PatchAttemptIdentity& selected,
                      std::size_t return_ordinal) {
  const char* dir = std::getenv("APMESH_R2733_SELECTED_TRI_DIR");
  if (dir == nullptr || dir[0] == '\0') {
    throw std::runtime_error("R2733 selected TRI output directory not configured");
  }
  const std::size_t faces = sub.GetNumberElements();
  const std::size_t nodes = sub.GetNumberNos();
  if (faces == 0 || faces > kMaxNativeSelectedFaces ||
      nodes == 0 || nodes > kMaxNativeSelectedNodes ||
      patch.GetNumBerCurves() != 4) {
    throw std::runtime_error("R2733 native selected TRI face/node/source-curve bound");
  }
  const std::filesystem::path root(dir);
  if (!std::filesystem::is_directory(root)) {
    throw std::runtime_error("R2733 original source-bound output directory missing");
  }
  const std::string name = "adapter_return_" +
      std::to_string(return_ordinal) + ".ndjson";
  const auto target = root / name;
  const auto pending = root / (name + ".pending");
  if (std::filesystem::exists(target) || std::filesystem::exists(pending)) {
    throw std::runtime_error("R2733 refused to overwrite research TRI evidence");
  }

  std::ofstream file(pending, std::ios::out | std::ios::binary);
  if (!file) {
    throw std::runtime_error("R2733 cannot create source-owned TRI evidence");
  }
  file << std::setprecision(17);
  file << "{\"type\":\"source_selected_adapter_return\",\"return_index\":"
       << return_ordinal << ",\"step\":" << selected.adaptive_step
       << ",\"retry\":" << selected.retry_index
       << ",\"patch\":" << selected.patch_index
       << ",\"local\":" << selected.local_attempt
       << ",\"outer_epoch\":" << selected.outer.epoch
       << ",\"outer_retry\":" << selected.outer.global_retry
       << ",\"session\":" << selected.outer.session
       << ",\"native_source_patch_id\":" << patch.GetId()
       << ",\"face_count\":" << faces << ",\"node_count\":" << nodes
       << ",\"source_curves\":[";
  for (unsigned int edge = 0; edge < patch.GetNumBerCurves(); ++edge) {
    const auto* curve = patch.GetCurve(edge);
    if (!curve || curve->GetNumBerPoints() < 2) {
      throw std::runtime_error("R2733 missing original source curve");
    }
    const std::size_t object_group = OriginalCurveObjectOrdinal(curve);
    // GetPoint lacks a const overload in the original code; we only read it.
    const PointAdaptive* first = curve->GetPoint(0);
    const PointAdaptive* last =
        curve->GetPoint(curve->GetNumBerPoints() - 1);
    if (first == nullptr || last == nullptr ||
        !std::isfinite(first->GetX()) || !std::isfinite(first->GetY()) ||
        !std::isfinite(first->GetZ()) || !std::isfinite(last->GetX()) ||
        !std::isfinite(last->GetY()) || !std::isfinite(last->GetZ())) {
      throw std::runtime_error("R2734 original source curve endpoints are invalid");
    }
    if (edge != 0) file << ',';
    file << "{\"edge_slot\":" << edge
         << ",\"native_curve_id\":" << curve->GetId()
         << ",\"reversed\":" << (patch.IsCurveReversed(edge) ? "true" : "false")
         << ",\"source_curve_points\":" << curve->GetNumBerPoints()
         << ",\"source_object_group\":" << object_group
         << ",\"source_endpoint_xyz\":[["
         << first->GetX() << ',' << first->GetY() << ',' << first->GetZ()
         << "],[" << last->GetX() << ',' << last->GetY() << ',' << last->GetZ()
         << "]]}";
  }
  file << "],\"provisional_post_aft_selected_local_not_global_commit\":true}\n";

  for (std::size_t element_slot = 0; element_slot < faces; ++element_slot) {
    auto* base = sub.GetElement(static_cast<unsigned int>(element_slot));
    // Legacy GetId() is non-const; this observer still calls accessors only.
    auto* tri = dynamic_cast<TriangleAdaptive*>(base);
    if (!tri) throw std::runtime_error("R2733 non-TRI native selected element");
    const std::array<std::tuple<double, double>, 3> uv{{
        tri->GetParametersN1(), tri->GetParametersN2(),
        tri->GetParametersN3()}};
    file << "{\"type\":\"face\",\"element_slot\":" << element_slot
         << ",\"native_element_id\":" << tri->GetId()
         << ",\"vertices\":[";
    for (unsigned int corner = 0; corner < 3; ++corner) {
      const PointAdaptive p = tri->GetVertexPoint(corner + 1);
      const double u = std::get<0>(uv[corner]);
      const double v = std::get<1>(uv[corner]);
      if (!std::isfinite(p.GetX()) || !std::isfinite(p.GetY()) ||
          !std::isfinite(p.GetZ()) || !std::isfinite(u) || !std::isfinite(v)) {
        throw std::runtime_error("R2733 nonfinite real native selected TRI corner");
      }
      if (corner != 0) file << ',';
      file << "{\"native_node_id\":" << p.GetId()
           << ",\"xyz\":[" << p.GetX() << ',' << p.GetY() << ',' << p.GetZ()
           << "],\"uv\":[" << u << ',' << v << "]}";
    }
    file << "]}\n";
  }
  file << "{\"type\":\"complete\",\"face_records\":" << faces
       << ",\"not_global_accepted_step\":true}\n";
  file.flush();
  if (!file.good()) throw std::runtime_error("R2733 short TRI source write");
  file.close();
  if (!file.good()) throw std::runtime_error("R2733 incomplete TRI source close");
  std::filesystem::rename(pending, target);
  std::cout << "R2733_TRI_RETURN=return_index=" << return_ordinal
            << ",outer_epoch=" << selected.outer.epoch
            << ",outer_retry=" << selected.outer.global_retry
            << ",step=" << selected.adaptive_step
            << ",retry=" << selected.retry_index
            << ",patch=" << selected.patch_index
            << ",local=" << selected.local_attempt
            << ",faces=" << faces << ",nodes=" << nodes
            << ",file=" << name << '\n';
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
  std::size_t selection_event_order = 0;
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
    Require(++selection_event_order <= 8192,
            "Research local-selection observer exceeded maximum bounded events");
    Require(event.attempt.adaptive_step > 0 && event.attempt.patch_index >= 0 &&
                event.attempt.local_attempt >= 0,
            "Research local-selection observer received an invalid patch attempt");
    const char* kind = "generation_failed";
    if (event.kind == apmesh::quad::LocalSelectionKind::SelectedForAdapterReturn) {
      kind = "selected";
      locally_selected.push_back(event.attempt.outer);
      pending_selected = event.attempt;
      ++selections_since_return;
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

// Linux ELF --wrap redirects only undefined original engine references to
// Adapter::AdaptDomain. This observer calls the original symbol once, then
// forwards its exact returned pointer unchanged to GeneratorAdaptive.
extern "C" SubMesh*
__real__ZN7Adapter11AdaptDomainEP10PatchCoonsPN9Performer9IdManagerEddiiii(
    Adapter*, PatchCoons*, Performer::IdManager*, double, double,
    int, int, int, int);

extern "C" SubMesh*
__wrap__ZN7Adapter11AdaptDomainEP10PatchCoonsPN9Performer9IdManagerEddiiii(
    Adapter* adapter, PatchCoons* patch, Performer::IdManager* manager,
    double factor, double target_h, int depth, int step, int patch_index,
    int local_retry) {
  SubMesh* returned =
      __real__ZN7Adapter11AdaptDomainEP10PatchCoonsPN9Performer9IdManagerEddiiii(
          adapter, patch, manager, factor, target_h, depth, step,
          patch_index, local_retry);
  ++actual_adapter_returns;
  try {
    if (selections_since_return != 1 || !pending_selected ||
        pending_selected->adaptive_step != step ||
        pending_selected->patch_index != patch_index ||
        pending_selected->retry_index != local_retry ||
        !returned || !patch) {
      throw std::runtime_error("R2733 selected native Adapter return scope mismatch");
    }
    if (step == 4) {
      WriteSelectedTri(*returned, *patch, *pending_selected, actual_adapter_returns);
    } else {
      std::cout << "R2733_TRI_RETURN=return_index=" << actual_adapter_returns
                << ",outer_epoch=" << pending_selected->outer.epoch
                << ",outer_retry=" << pending_selected->outer.global_retry
                << ",step=" << step << ",retry=" << local_retry
                << ",patch=" << patch_index
                << ",local=" << pending_selected->local_attempt
                << ",faces=" << returned->GetNumberElements()
                << ",nodes=" << returned->GetNumberNos()
                << ",file=none\n";
    }
  } catch (const std::exception& error) {
    // Observation errors must not change or free the original TRI result.
    std::cerr << "R2733_TRI_OBSERVER_ERROR=" << error.what() << '\n';
  }
  pending_selected.reset();
  selections_since_return = 0;
  return returned;
}
