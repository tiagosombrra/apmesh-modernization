#ifndef APMESH_RESEARCH_QUAD_ADAPTER_CAPTURE_H
#define APMESH_RESEARCH_QUAD_ADAPTER_CAPTURE_H

#include "quadtree_quad.h"
#include "crab_mesh/aft/advancing_front.h"

#include <functional>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace apmesh::quad {

// An identity for a candidate attempt, not a published/accepted TRI mesh.
struct PatchAttemptIdentity {
  int patch_index = -1;
  int adaptive_step = -1;
  int retry_index = 0;
  int local_attempt = 0;
};

enum class CaptureDisposition { PendingTriDecision };

// All returned geometry and provenance are values, never legacy owner pointers.
struct AttemptUvCapture {
  PatchAttemptIdentity attempt;
  LeafPolygonMesh polygons;
  CaptureDisposition disposition = CaptureDisposition::PendingTriDecision;
};

using CaptureProvider = std::function<LeafPolygonMesh(Par2DJMesh::AFT::Quadtree&)>;
using CaptureSink = std::function<void(AttemptUvCapture)>;

// A local TRI attempt may be selected for Adapter return but later be rejected
// by the global generator. These events never certify an accepted mesh.
enum class LocalSelectionKind { SelectedForAdapterReturn, Superseded, GenerationFailed };

struct LocalAttemptRecord {
  PatchAttemptIdentity attempt;
  bool generation_succeeded = false;
  std::string generation_status;
};

struct LocalSelectionEvent {
  PatchAttemptIdentity attempt;
  LocalSelectionKind kind = LocalSelectionKind::GenerationFailed;
  std::string generation_status;
};

using LocalSelectionSink = std::function<void(LocalSelectionEvent)>;

struct CaptureHooks {
  CaptureProvider provider;
  CaptureSink sink;
  LocalSelectionSink local_selection_sink;
};

// Validate the entire stream before publishing any final decision.
inline void PublishLocalSelections(const std::vector<LocalAttemptRecord>& attempts,
                                   int selected_local_attempt,
                                   const LocalSelectionSink& sink) {
  if (!sink) {
    return;
  }
  std::set<int> seen;
  bool chosen_found = false;
  for (const auto& record : attempts) {
    if (!seen.insert(record.attempt.local_attempt).second) {
      throw std::invalid_argument("Duplicate local attempt in capture decision stream");
    }
    if (record.attempt.local_attempt == selected_local_attempt) {
      if (!record.generation_succeeded) {
        throw std::invalid_argument("Cannot select a failed TRI generation attempt");
      }
      chosen_found = true;
    }
  }
  if (selected_local_attempt >= 0 && !chosen_found) {
    throw std::invalid_argument("Selected local attempt was not generated");
  }
  if (selected_local_attempt < 0) {
    for (const auto& record : attempts) {
      if (record.generation_succeeded) {
        throw std::invalid_argument("Unselected stream contains a successful TRI attempt");
      }
    }
  }
  for (const auto& record : attempts) {
    const LocalSelectionKind kind =
        !record.generation_succeeded
            ? LocalSelectionKind::GenerationFailed
            : (record.attempt.local_attempt == selected_local_attempt
                   ? LocalSelectionKind::SelectedForAdapterReturn
                   : LocalSelectionKind::Superseded);
    sink(LocalSelectionEvent{record.attempt, kind, record.generation_status});
  }
}

inline void ValidateCaptureHooks(const CaptureHooks& hooks) {
  if (static_cast<bool>(hooks.provider) != static_cast<bool>(hooks.sink)) {
    throw std::invalid_argument("Both UV capture provider and sink must be supplied");
  }
  if (hooks.local_selection_sink && !hooks.provider) {
    throw std::invalid_argument("Local TRI decisions require matching UV capture hooks");
  }
}

inline void BindRefinedCapture(Par2DJMesh::AFT::AdvancingFront& front,
                              const CaptureHooks& hooks, PatchAttemptIdentity attempt) {
  ValidateCaptureHooks(hooks);
  if (!hooks.provider) {
    return;
  }
  // Copy callbacks into the front's lifetime; the tree must never escape this call.
  front.SetRefinedQuadtreeObserver(
      [provider = hooks.provider, sink = hooks.sink, attempt](Par2DJMesh::AFT::Quadtree& tree) {
        LeafPolygonMesh snapshot = provider(tree);
        sink(AttemptUvCapture{attempt, std::move(snapshot),
                              CaptureDisposition::PendingTriDecision});
      });
}

} // namespace apmesh::quad
#endif // APMESH_RESEARCH_QUAD_ADAPTER_CAPTURE_H
