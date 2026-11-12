#ifndef APMESH_RESEARCH_QUAD_ADAPTER_CAPTURE_H
#define APMESH_RESEARCH_QUAD_ADAPTER_CAPTURE_H

#include "quadtree_quad.h"
#include "crab_mesh/aft/advancing_front.h"
#include "data/patch/patch_coons.h"
#include "data/node_adaptive.h"

#include <array>
#include <cmath>
#include <cstdint>
#include <functional>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace apmesh::quad {

// A research caller defines a unique nonzero session namespace. The epoch
// monotonically identifies one outer generator retry within that namespace.
// All-zero scope is the legacy direct-Adapter fixture path, never a global join.
struct OuterAttemptIdentity {
  std::uint64_t session = 0;
  std::uint64_t epoch = 0;
  int global_retry = -1;
};

inline bool SameOuterAttempt(const OuterAttemptIdentity& a,
                             const OuterAttemptIdentity& b) noexcept {
  return a.session == b.session && a.epoch == b.epoch &&
         a.global_retry == b.global_retry;
}

inline void ValidateOuterAttempt(const OuterAttemptIdentity& context) {
  if (SameOuterAttempt(context, {})) {
    return;
  }
  if (context.session == 0 || context.epoch == 0 || context.global_retry < 0) {
    throw std::invalid_argument("Incomplete outer generator attempt namespace or epoch");
  }
}

// An identity for a candidate attempt, not a published/accepted TRI mesh.
struct PatchAttemptIdentity {
  int patch_index = -1;
  int adaptive_step = -1;
  int retry_index = 0;
  int local_attempt = 0;
  OuterAttemptIdentity outer{};
};

inline bool SamePatchScope(const PatchAttemptIdentity& a,
                           const PatchAttemptIdentity& b) noexcept {
  return a.patch_index == b.patch_index && a.adaptive_step == b.adaptive_step &&
         a.retry_index == b.retry_index && SameOuterAttempt(a.outer, b.outer);
}

// A value-only snapshot of the ACTUAL original serial Adapter boundary.
// The source curve, physical sample and AFT vertex IDs never escape as pointers.
// This is observational engineering, not an acceptance or scientific point rule.
struct AdapterBoundaryPoint {
  UvVertex uv{};
  std::array<double, 3> physical_xyz{};
  long aft_vertex_id = 0;
  unsigned side = 0;
  unsigned source_index = 0;
  unsigned long curve_id = 0;
  unsigned long physical_node_id = 0;
  bool curve_reversed = false;
  double original_parameter = 0.0;
  double chart_parameter = 0.0;
};

struct AdapterBoundaryEdgeMetric {
  UvVertex source_midpoint{};
  double source_normalized_length = -1.0;
};

// This endpoint belongs to the ORIGINAL source curve object. The actual AFT
// Boundary omits the last site of each side and aliases the first site of the
// next side for topological closure; that borrowed corner may carry the NEXT
// curve's patch-local node ID despite having exactly identical physical XYZ.
struct AdapterOriginalCurveEndpoint {
  double parameter = 0.0;
  unsigned long node_id = 0;
  unsigned source_index = 0;
  std::array<double, 3> xyz{};
};

struct AdapterBoundaryCapture {
  PatchAttemptIdentity attempt{};
  std::vector<AdapterBoundaryPoint> vertices;
  std::vector<std::array<double, 4>> directed_edges;
  std::vector<AdapterBoundaryEdgeMetric> original_edge_metrics;
  std::array<std::size_t, 4> side_counts{};
  std::array<AdapterOriginalCurveEndpoint, 4> original_curve_endpoints{};
  bool accepted_mesh_published = false;
};

// Call only after Boundary::close succeeds and the Adapter has copied all
// source curve nodes into the provisional SubMesh. This does NOT refine a tree.
inline AdapterBoundaryCapture SnapshotOriginalAdapterBoundary(
    PatchCoons& patch, Par2DJMesh::AFT::Boundary& boundary,
    const std::map<Par2DJMesh::Basics::Vertex*, NodeAdaptive*>& borrowed_nodes,
    PatchAttemptIdentity attempt) {
  if (patch.GetNumBerCurves() != 4U)
    throw std::invalid_argument("Adapter research boundary needs four source curves");
  AdapterBoundaryCapture result;
  result.attempt = attempt;
  const auto actual_list = boundary.getBoundary();
  const std::vector<Par2DJMesh::Basics::Vertex*> actual(
      actual_list.begin(), actual_list.end());
  const auto edge_list = boundary.getEdges();
  if (actual.size() != edge_list.size() || actual.size() < 4U)
    throw std::invalid_argument("Adapter research boundary is not a closed edge cycle");

  std::size_t cursor = 0;
  for (unsigned side = 0; side < 4U; ++side) {
    auto* curve = static_cast<CurveAdaptiveParametric*>(patch.GetCurve(side));
    if (curve == nullptr)
      throw std::invalid_argument("Adapter research source has null curve");
    const std::vector<double> parameters(
        curve->parameters_.begin(), curve->parameters_.end());
    const auto count = parameters.size();
    if (count < 2U || count != curve->GetNumBerPoints())
      throw std::invalid_argument("Adapter source curve point/parameter mismatch");
    const bool reversed = patch.IsCurveReversed(side);
    result.side_counts[side] = count - 1U;
    const std::size_t terminal_index = reversed
        ? (side < 2U ? 0U : count - 1U)
        : (side < 2U ? count - 1U : 0U);
    const auto* terminal = curve->GetPoint(
        static_cast<unsigned>(terminal_index));
    if (terminal == nullptr || terminal->GetId() == 0UL ||
        !std::isfinite(parameters[terminal_index])) {
      throw std::invalid_argument("Original source curve endpoint has invalid provenance");
    }
    const std::array<double, 3> terminal_xyz{
        terminal->GetX(), terminal->GetY(), terminal->GetZ()};
    if (!std::isfinite(terminal_xyz[0]) ||
        !std::isfinite(terminal_xyz[1]) ||
        !std::isfinite(terminal_xyz[2])) {
      throw std::invalid_argument("Original source curve endpoint XYZ is invalid");
    }
    result.original_curve_endpoints[side] = {
        parameters[terminal_index], terminal->GetId(),
        static_cast<unsigned>(terminal_index), terminal_xyz};

    for (std::size_t offset = 0; offset + 1U < count; ++offset) {
      if (cursor >= actual.size())
        throw std::invalid_argument("Adapter boundary dropped source curve samples");
      const std::size_t index = reversed
          ? (side < 2U ? count - 1U - offset : offset)
          : (side < 2U ? offset : count - 1U - offset);
      const double source_t = parameters[index];
      const double local_t = reversed ? 1.0 - source_t : source_t;
      const UvVertex uv = side == 0 ? UvVertex{local_t, 0.0}
          : side == 1 ? UvVertex{1.0, local_t}
          : side == 2 ? UvVertex{local_t, 1.0}
                      : UvVertex{0.0, local_t};
      auto* vertex = actual[cursor++];
      const auto it = borrowed_nodes.find(vertex);
      auto* original = curve->GetPoint(static_cast<unsigned>(index));
      if (it == borrowed_nodes.end() || it->second == nullptr ||
          vertex == nullptr || original == nullptr ||
          !std::isfinite(source_t) || !std::isfinite(local_t) ||
          source_t < 0.0 || source_t > 1.0 ||
          local_t < 0.0 || local_t > 1.0 ||
          vertex->getX() != uv.u || vertex->getY() != uv.v ||
          it->second->GetId() != original->GetId())
        throw std::invalid_argument("Adapter boundary source sample identity/UV mismatch");
      const std::array<double, 3> xyz{
          it->second->GetX(), it->second->GetY(), it->second->GetZ()};
      const std::array<double, 3> source_xyz{
          original->GetX(), original->GetY(), original->GetZ()};
      for (unsigned axis = 0; axis < 3U; ++axis)
        if (!std::isfinite(xyz[axis]) || xyz[axis] != source_xyz[axis])
          throw std::invalid_argument("Adapter boundary source physical node was changed");
      result.vertices.push_back({uv, xyz, vertex->getId(), side,
                                 static_cast<unsigned>(index), curve->GetId(),
                                 original->GetId(), reversed, source_t, local_t});
    }
  }
  if (cursor != actual.size())
    throw std::invalid_argument("Adapter boundary contains unowned extra curve samples");
  std::size_t edge_index = 0;
  for (auto* edge : edge_list) {
    if (edge == nullptr || edge->getV1() != actual[edge_index] ||
        edge->getV2() != actual[(edge_index + 1U) % actual.size()])
      throw std::invalid_argument("Adapter boundary broke directed edge sequence");
    const auto& a = result.vertices[edge_index];
    const auto& b = result.vertices[(edge_index + 1U) % result.vertices.size()];
    result.directed_edges.push_back({a.uv.u, a.uv.v, b.uv.u, b.uv.v});
    auto* midpoint = edge->getMid();
    const double h = edge->getLen();
    if (midpoint == nullptr || !std::isfinite(midpoint->getX()) ||
        !std::isfinite(midpoint->getY()) || !std::isfinite(h)) {
      throw std::invalid_argument("Adapter edge midpoint/arc length is nonfinite or absent");
    }
    result.original_edge_metrics.push_back(
        {{midpoint->getX(), midpoint->getY()}, h});
    ++edge_index;
  }
  double twice_area = 0.0;
  for (const auto& segment : result.directed_edges)
    twice_area += segment[0] * segment[3] - segment[2] * segment[1];
  if (!std::isfinite(twice_area) || twice_area <= 0.0)
    throw std::invalid_argument("Adapter boundary has invalid directed UV area");
  return result;
}

enum class CaptureDisposition { PendingTriDecision };

// All returned geometry and provenance are values, never legacy owner pointers.
struct AttemptUvCapture {
  PatchAttemptIdentity attempt;
  LeafPolygonMesh polygons;
  CaptureDisposition disposition = CaptureDisposition::PendingTriDecision;
};

using CaptureProvider = std::function<LeafPolygonMesh(Par2DJMesh::AFT::Quadtree&)>;
using CaptureSink = std::function<void(AttemptUvCapture)>;
using AdapterBoundarySink = std::function<void(AdapterBoundaryCapture)>;

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
  AdapterBoundarySink boundary_sink;
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
    ValidateOuterAttempt(record.attempt.outer);
    if (!attempts.empty() && !SamePatchScope(record.attempt, attempts.front().attempt)) {
      throw std::invalid_argument("Cross-epoch or cross-patch local selection stream");
    }
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
  if (hooks.boundary_sink && !hooks.provider) {
    throw std::invalid_argument("Adapter boundary observer requires matching UV hooks");
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
