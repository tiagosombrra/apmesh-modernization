#include "adapter_capture.h"
#include "quadtree_quad.h"

#include "crab_mesh/aft/advancing_front.h"

#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>
#include <utility>

namespace {
using Par2DJMesh::AFT::AdvancingFront;
using Par2DJMesh::AFT::Quadtree;

void Require(bool valid, const char* message) {
  if (!valid) {
    throw std::runtime_error(message);
  }
}

struct StopAtObservation final {};

std::unique_ptr<AdvancingFront> SquareFront() {
  auto front = std::make_unique<AdvancingFront>();
  // Bound test-only edge refinement; unrestricted null-curve edges are unsafe.
  front->getQuadtree()->setMaxLevelCap(3);
  auto* boundary = front->getQuadtree()->getBoundary();
  boundary->addVertex(0, 0, nullptr);
  boundary->addVertex(1, 0, nullptr);
  boundary->addVertex(1, 1, nullptr);
  boundary->addVertex(0, 1, nullptr);
  Require(boundary->close(nullptr), "Test boundary did not close");
  front->SetTemplateMode("y");
  return front;
}

void AssertObservationBeforeTriangles() {
  auto front = SquareFront();
  std::size_t invocations = 0;
  std::size_t captured_leaves = 0;
  std::size_t captured_polygons = 0;
  front->SetRefinedQuadtreeObserver([&](Quadtree& tree) {
    ++invocations;
    Require(tree.getRoot() != nullptr, "Observer ran before quadtree root allocation");
    Require(tree.GetTemplateFaces().empty(), "Observer ran after TRI template publication");
    Require(tree.GetTemplateVertices().empty(), "Observer ran after TRI vertex publication");
    const auto captured = apmesh::quad::CaptureLeafPolygons(tree);
    Require(captured.source_leaves == tree.GetLeafCount(), "Observed leaf count is inconsistent");
    Require(!captured.input.polygons.empty(), "Observed tree had no interior polygons");
    Require(captured.input.interior_points.empty(), "Read-only capture selected numeric points");
    captured_leaves = captured.source_leaves;
    captured_polygons = captured.input.polygons.size();
    // Stop before the TRI pipeline; do not assume any scientific point rule.
    throw StopAtObservation{};
  });

  bool stopped = false;
  try {
    front->execute({});
  } catch (const StopAtObservation&) {
    stopped = true;
  }
  Require(stopped && invocations == 1, "Observer was not invoked once at the live checkpoint");
  Require(captured_leaves > 0 && captured_polygons > 0, "No real quadtree data was captured");
  Require(front->getQuadtree()->GetTemplateFaces().empty(),
          "Observer failure published TRI templates");
  Require(front->getQuadtree()->GetTemplateVertices().empty(),
          "Observer failure published TRI-owned vertices");
  std::cout << "refined_observer_captured_leaves=" << captured_leaves
            << " polygons=" << captured_polygons << '\n';
}

void AssertCallbackDisabledByDefault() {
  auto front = SquareFront();
  // An empty callback must not change the original TRI generator execution.
  front->SetRefinedQuadtreeObserver({});
  const bool successful = front->execute({});
  Require(successful, "Disabled observation broke the original TRI execution");
  Require(!front->getMesh().empty(), "Original TRI generation produced no faces");
}

void AssertValueOwnedAttemptCapture() {
  using apmesh::quad::AttemptUvCapture;
  using apmesh::quad::CaptureDisposition;
  using apmesh::quad::CaptureHooks;
  using apmesh::quad::PatchAttemptIdentity;
  std::optional<AttemptUvCapture> saved;
  unsigned calls = 0;
  const PatchAttemptIdentity identity{7, 3, 2, 5};
  {
    auto front = SquareFront();
    CaptureHooks hooks;
    hooks.provider = [&](Quadtree& tree) {
      ++calls;
      return apmesh::quad::CaptureLeafPolygons(tree);
    };
    hooks.sink = [&](AttemptUvCapture result) {
      saved.emplace(std::move(result));
      throw StopAtObservation{};
    };
    apmesh::quad::BindRefinedCapture(*front, hooks, identity);
    bool stopped = false;
    try {
      front->execute({});
    } catch (const StopAtObservation&) {
      stopped = true;
    }
    Require(stopped && calls == 1, "Value capture was not invoked exactly once");
    Require(front->getQuadtree()->GetTemplateFaces().empty(),
            "Capture published TRI templates");
  }
  // The source is already destroyed: the snapshot must remain valid.
  Require(saved.has_value(), "Lost snapshot after source destruction");
  Require(saved->attempt.patch_index == 7 && saved->attempt.adaptive_step == 3 &&
              saved->attempt.retry_index == 2 && saved->attempt.local_attempt == 5,
          "Patch/step/retry/attempt provenance changed");
  Require(saved->disposition == CaptureDisposition::PendingTriDecision,
          "Provisional capture was incorrectly accepted");
  Require(!saved->polygons.input.vertices.empty() &&
              !saved->polygons.input.polygons.empty() &&
              saved->polygons.origins.size() == saved->polygons.input.polygons.size(),
          "Snapshot lost value-owned UV vertices, polygons or source origins");
  Require(saved->polygons.input.interior_points.empty(),
          "Snapshot invented an interior-point policy");
}

void AssertCaptureHookFailureAtomicity() {
  using apmesh::quad::AttemptUvCapture;
  using apmesh::quad::CaptureHooks;
  auto front = SquareFront();
  CaptureHooks partial;
  partial.provider = [](Quadtree& tree) { return apmesh::quad::CaptureLeafPolygons(tree); };
  bool refused = false;
  try {
    apmesh::quad::BindRefinedCapture(*front, partial, {1, 2, 3, 4});
  } catch (const std::invalid_argument&) {
    refused = true;
  }
  Require(refused, "Incomplete capture hook pair was accepted");

  unsigned sink_calls = 0;
  CaptureHooks failing;
  failing.provider = [](Quadtree&) -> apmesh::quad::LeafPolygonMesh {
    throw std::runtime_error("capture producer rejected source");
  };
  failing.sink = [&](AttemptUvCapture) { ++sink_calls; };
  apmesh::quad::BindRefinedCapture(*front, failing, {1, 2, 3, 4});
  bool caught = false;
  try {
    front->execute({});
  } catch (const std::runtime_error& error) {
    caught = std::string(error.what()) == "capture producer rejected source";
  }
  Require(caught && sink_calls == 0, "Failed capture leaked a partial event");
  Require(front->getQuadtree()->GetTemplateFaces().empty(),
          "Failed capture published TRI templates");

  auto unchanged = SquareFront();
  apmesh::quad::BindRefinedCapture(*unchanged, {}, {0, 0, 0, 0});
  Require(unchanged->execute({}) && !unchanged->getMesh().empty(),
          "Disabled capture hooks changed the historical TRI execution");
}

void AssertAttemptIsolation() {
  using apmesh::quad::AttemptUvCapture;
  using apmesh::quad::CaptureHooks;
  std::vector<AttemptUvCapture> saved;
  for (int attempt = 0; attempt != 2; ++attempt) {
    auto front = SquareFront();
    CaptureHooks hooks;
    hooks.provider = [](Quadtree& tree) { return apmesh::quad::CaptureLeafPolygons(tree); };
    hooks.sink = [&](AttemptUvCapture result) {
      saved.push_back(std::move(result));
      throw StopAtObservation{};
    };
    apmesh::quad::BindRefinedCapture(*front, hooks, {2, 8, 1, attempt});
    bool stopped = false;
    try {
      front->execute({});
    } catch (const StopAtObservation&) {
      stopped = true;
    }
    Require(stopped, "Observer did not stop the independent attempt");
  }
  Require(saved.size() == 2 && saved[0].attempt.local_attempt == 0 &&
              saved[1].attempt.local_attempt == 1 &&
              saved[0].attempt.retry_index == saved[1].attempt.retry_index,
          "Independent attempts shared incorrect provenance");
}

} // namespace

int main() {
  try {
    AssertObservationBeforeTriangles();
    AssertCallbackDisabledByDefault();
    AssertValueOwnedAttemptCapture();
    AssertCaptureHookFailureAtomicity();
    AssertAttemptIsolation();
    std::cout << "refined_observer_contract_cases=5 failed=0\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "Refined observer contract failed: " << error.what() << '\n';
    return 1;
  }
}
