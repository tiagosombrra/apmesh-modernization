#include "quadtree_quad.h"

#include "crab_mesh/aft/advancing_front.h"

#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
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

} // namespace

int main() {
  try {
    AssertObservationBeforeTriangles();
    AssertCallbackDisabledByDefault();
    std::cout << "refined_observer_contract_cases=2 failed=0\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "Refined observer contract failed: " << error.what() << '\n';
    return 1;
  }
}
