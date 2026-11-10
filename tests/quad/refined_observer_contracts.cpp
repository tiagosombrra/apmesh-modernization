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


void AssertLocalSelectionStream() {
  using apmesh::quad::LocalAttemptRecord;
  using apmesh::quad::LocalSelectionEvent;
  using apmesh::quad::LocalSelectionKind;
  std::vector<LocalAttemptRecord> records{
      {{4, 2, 1, 0}, true, "degenerate_needs_retry"},
      {{4, 2, 1, 1}, false, "generation_failed"},
      {{4, 2, 1, 2}, true, "ok"},
  };
  std::vector<LocalSelectionEvent> results;
  apmesh::quad::PublishLocalSelections(
      records, 2, [&](LocalSelectionEvent value) { results.push_back(std::move(value)); });
  Require(results.size() == 3, "Decision stream lost attempted candidates");
  Require(results[0].kind == LocalSelectionKind::Superseded &&
              results[1].kind == LocalSelectionKind::GenerationFailed &&
              results[2].kind == LocalSelectionKind::SelectedForAdapterReturn,
          "Local attempt disposition was incorrectly classified");
  Require(results[2].attempt.patch_index == 4 &&
              results[2].attempt.adaptive_step == 2 &&
              results[2].attempt.retry_index == 1 &&
              results[2].attempt.local_attempt == 2 &&
              results[2].generation_status == "ok",
          "Decision stream lost attempt metadata");
  // A locally selected attempt is not a globally accepted TRI mesh.
  Require(results[2].kind == LocalSelectionKind::SelectedForAdapterReturn,
          "Selection was promoted to global acceptance");

  bool rejected = false;
  records.push_back(records[2]);
  const auto previous = results.size();
  try {
    apmesh::quad::PublishLocalSelections(
        records, 2, [&](LocalSelectionEvent value) { results.push_back(std::move(value)); });
  } catch (const std::invalid_argument&) {
    rejected = true;
  }
  Require(rejected && results.size() == previous, "Duplicate stream emitted partial decisions");
  records.pop_back();

  rejected = false;
  try {
    apmesh::quad::PublishLocalSelections(
        records, 1, [&](LocalSelectionEvent value) { results.push_back(std::move(value)); });
  } catch (const std::invalid_argument&) {
    rejected = true;
  }
  Require(rejected && results.size() == previous, "Failed TRI attempt was marked selected");

  rejected = false;
  try {
    apmesh::quad::PublishLocalSelections(
        records, 8, [&](LocalSelectionEvent value) { results.push_back(std::move(value)); });
  } catch (const std::invalid_argument&) {
    rejected = true;
  }
  Require(rejected && results.size() == previous, "Missing local attempt was fabricated");

  rejected = false;
  try {
    apmesh::quad::PublishLocalSelections(
        records, -1, [&](LocalSelectionEvent value) { results.push_back(std::move(value)); });
  } catch (const std::invalid_argument&) {
    rejected = true;
  }
  Require(rejected && results.size() == previous, "Success was suppressed without selection");

  std::vector<LocalAttemptRecord> all_failed{
      {{4, 2, 1, 0}, false, "generation_failed"},
      {{4, 2, 1, 1}, false, "generation_failed"}};
  std::vector<LocalSelectionEvent> failed;
  apmesh::quad::PublishLocalSelections(
      all_failed, -1, [&](LocalSelectionEvent value) { failed.push_back(std::move(value)); });
  Require(failed.size() == 2 &&
              failed[0].kind == LocalSelectionKind::GenerationFailed &&
              failed[1].kind == LocalSelectionKind::GenerationFailed,
          "Unsuccessful patch received an invented accepted result");
}

void AssertDecisionHookRequiresCapture() {
  apmesh::quad::CaptureHooks hooks;
  hooks.local_selection_sink = [](apmesh::quad::LocalSelectionEvent) {};
  bool rejected = false;
  try {
    apmesh::quad::ValidateCaptureHooks(hooks);
  } catch (const std::invalid_argument&) {
    rejected = true;
  }
  Require(rejected, "Decision-only hook was allowed without matching UV capture");
}


void AssertOuterEpochAndLegacyCompatibility() {
  using apmesh::quad::LocalAttemptRecord;
  using apmesh::quad::LocalSelectionEvent;
  using apmesh::quad::OuterAttemptIdentity;
  using apmesh::quad::PatchAttemptIdentity;
  const PatchAttemptIdentity legacy{6, 4, 1, 0};
  Require(apmesh::quad::SameOuterAttempt(legacy.outer, {}),
          "Legacy four-field attempt acquired an unrequested global correlation");
  const OuterAttemptIdentity outer1{712, 31, 0};
  const OuterAttemptIdentity outer2{712, 32, 1};
  PatchAttemptIdentity a{6, 4, 1, 0};
  PatchAttemptIdentity b{6, 4, 1, 0};
  a.outer = outer1;
  b.outer = outer2;
  Require(!apmesh::quad::SamePatchScope(a, b),
          "Distinct global epochs collided despite identical patch coordinates");
  Require(apmesh::quad::SamePatchScope(a, a), "A stable global join key changed");

  // Use distinct local IDs so the mixed-epoch validation, rather than only
  // duplicate-ID validation, is the reason this entire stream is rejected.
  b.local_attempt = 1;
  std::vector<LocalSelectionEvent> results;
  std::vector<LocalAttemptRecord> mixed{{a, true, "ok"}, {b, true, "ok"}};
  bool rejected = false;
  try {
    apmesh::quad::PublishLocalSelections(
        mixed, 0, [&](LocalSelectionEvent e) { results.push_back(std::move(e)); });
  } catch (const std::invalid_argument&) {
    rejected = true;
  }
  Require(rejected && results.empty(), "Mixed outer epochs emitted partial decisions");

  for (const OuterAttemptIdentity malformed :
       {OuterAttemptIdentity{0, 1, 0}, OuterAttemptIdentity{712, 0, 0},
        OuterAttemptIdentity{712, 1, -1}}) {
    rejected = false;
    try {
      apmesh::quad::ValidateOuterAttempt(malformed);
    } catch (const std::invalid_argument&) {
      rejected = true;
    }
    Require(rejected, "Incomplete global namespace or retry was accepted");
  }
  apmesh::quad::ValidateOuterAttempt({});
  apmesh::quad::ValidateOuterAttempt(outer1);
}

} // namespace

int main() {
  try {
    AssertObservationBeforeTriangles();
    AssertCallbackDisabledByDefault();
    AssertValueOwnedAttemptCapture();
    AssertCaptureHookFailureAtomicity();
    AssertAttemptIsolation();
    AssertLocalSelectionStream();
    AssertDecisionHookRequiresCapture();
    AssertOuterEpochAndLegacyCompatibility();
    std::cout << "refined_observer_contract_cases=8 failed=0\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "Refined observer contract failed: " << error.what() << '\n';
    return 1;
  }
}
