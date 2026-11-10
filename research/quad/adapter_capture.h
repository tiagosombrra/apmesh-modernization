#ifndef APMESH_RESEARCH_QUAD_ADAPTER_CAPTURE_H
#define APMESH_RESEARCH_QUAD_ADAPTER_CAPTURE_H

#include "quadtree_quad.h"
#include "crab_mesh/aft/advancing_front.h"

#include <functional>
#include <stdexcept>
#include <utility>

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

struct CaptureHooks {
  CaptureProvider provider;
  CaptureSink sink;
};

inline void ValidateCaptureHooks(const CaptureHooks& hooks) {
  if (static_cast<bool>(hooks.provider) != static_cast<bool>(hooks.sink)) {
    throw std::invalid_argument("Both UV capture provider and sink must be supplied");
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
