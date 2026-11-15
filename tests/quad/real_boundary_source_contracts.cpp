#include "application/runtime_config.h"
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "generator/generator_adaptive.h"
#include "real_boundary_source.h"
#include "crab_mesh/aft/quadtree.h"
#include "crab_mesh/aft/quadtree_cell.h"
#include <algorithm>
#include <iostream>
#include <stdexcept>

namespace {
void Require(bool value, const char* message) {
  if (!value)
    throw std::runtime_error(message);
}

void MakeReversedSource(Geometry& geometry) {
  Geometry original;
  Models3d models;
  models.ModelCurvaBezier(&original);
  auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(0));
  Require(patch != nullptr, "Missing original curved fixture");
  std::array<CurveAdaptive*, 4> curves{};
  for (unsigned side = 0; side < 4; ++side) {
    auto* curve = dynamic_cast<CurveAdaptiveParametricBezier*>(patch->GetCurve(side));
    Require(curve != nullptr, "Missing original Bezier curve");
    auto copy =
        side == 0
            ? std::make_unique<CurveAdaptiveParametricBezier>(
                  curve->GetPoint3(), curve->GetPoint2(), curve->GetPoint1(), curve->GetPoint0())
            : std::make_unique<CurveAdaptiveParametricBezier>(
                  curve->GetPoint0(), curve->GetPoint1(), curve->GetPoint2(), curve->GetPoint3());
    curves[side] = copy.get();
    geometry.InsertCurve(std::move(copy));
  }
  geometry.InsertPatch(std::make_unique<PatchBezier>(
      curves[0], curves[1], curves[2], curves[3], patch->GetPt11(), patch->GetPt21(),
      patch->GetPt12(), patch->GetPt22(), false, true, true, true));
  auto* reversed = dynamic_cast<PatchBezier*>(geometry.GetPatch(0));
  Require(reversed && reversed->IsCurveReversed(0), "Reversed fixture lost source traversal");
  for (const double u : {0.0, 0.17, 0.61, 1.0})
    for (const double v : {0.0, 0.29, 0.83, 1.0}) {
      const auto a = patch->Parameterize(u, v);
      const auto b = reversed->Parameterize(u, v);
      Require(a.GetX() == b.GetX() && a.GetY() == b.GetY() && a.GetZ() == b.GetZ(),
              "Valid reversed-curve fixture changed the original surface");
    }
}

unsigned CheckNegatives(PatchBezier& patch, const apmesh::quad::RealBoundarySource& source) {
  using namespace apmesh::quad;
  unsigned rejected = 0;
  auto* previous = patch.GetSubMesh();
  for (unsigned fault = 0; fault < 9; ++fault) {
    auto broken = source;
    switch (fault) {
    case 0:
      broken.sites.erase(broken.sites.begin());
      break;
    case 1:
      broken.sites.push_back(broken.sites.front());
      break;
    case 2:
      broken.sites.front().source_id += 1000000;
      break;
    case 3:
      broken.sites.front().xyz[2] += 1;
      break;
    case 4:
      broken.sites.front().parameter += 0.125;
      break;
    case 5:
      std::reverse(broken.sites.begin(), broken.sites.end());
      break;
    case 6:
      broken.reversed_curves[0] = !broken.reversed_curves[0];
      break;
    case 7:
      broken.sites.front().normalized_length *= 2;
      break;
    case 8:
      broken.cells.front().children[0] = 0;
      break;
    }
    bool refused = false;
    try {
      auto tree = ReplayRealSourceTree(patch, broken);
      (void)tree;
    } catch (const std::runtime_error&) {
      refused = true;
    }
    Require(refused && patch.GetSubMesh() == previous,
            "Broken source boundary/tree passed or replaced the original owner");
    ++rejected;
  }
  return rejected;
}

void Run(const apmesh::application::RuntimeConfig& base, bool reverse, unsigned& captures,
         unsigned& negatives) {
  auto config = base;
  config.output_prefix += reverse ? "-reversed-reference" : "-native-reference";
  apmesh::application::ApplyRuntimeConfig(config);
  Geometry geometry;
  if (reverse)
    MakeReversedSource(geometry);
  else {
    Models3d models;
    models.ModelCurvaBezier(&geometry);
  }
  auto* patch = dynamic_cast<PatchBezier*>(geometry.GetPatch(0));
  Model model(&geometry);
  GeneratorAdaptive generator(apmesh::application::MakeGenerationContext(config, NUMBER_PROCESS));
  Timer timer(config.num_processes, config.num_threads, 12);
  timer.InitTimerParallel(0, 0, 10);
  apmesh::quad::CaptureHooks hooks;
  hooks.provider = [&](Par2DJMesh::AFT::Quadtree& original) {
    const auto source = apmesh::quad::CaptureRealBoundary(*patch, original);
    Require(!reverse || source.reversed_sides > 0, "Original generator lost reversed source side");
    auto replayed = apmesh::quad::ReplayRealSourceTree(*patch, source);
    Require(replayed->GetLeafCount() == original.GetLeafCount(), "Native tree replay differs");
    const auto original_leaves = original.getLeaves();
    const auto replayed_leaves = replayed->getLeaves();
    auto actual = replayed_leaves.begin();
    for (auto* expected : original_leaves) {
      Require(expected->getId() == (*actual)->getId(), "Original leaf identity/order changed");
      ++actual;
    }
    negatives += CheckNegatives(*patch, source);
    ++captures;
    apmesh::quad::LeafPolygonMesh result;
    result.source_leaves = source.source_leaves;
    return result;
  };
  hooks.sink = [](apmesh::quad::AttemptUvCapture) {};
  generator.SetResearchUvCapture(std::move(hooks), reverse ? 15112028 : 15112027);
  generator.Generator(model, &timer);
}
} // namespace

int main(int argc, char** argv) {
  try {
    Require(argc == 2, "Expected original-curve runtime configuration");
    const auto config = apmesh::application::LoadRuntimeConfig(argv[1]);
    unsigned captures = 0, negatives = 0;
    Run(config, false, captures, negatives);
    const unsigned before_reversed = captures;
    Run(config, true, captures, negatives);
    Require(before_reversed > 0 && captures > before_reversed && negatives == 9 * captures,
            "Missing real original-source or valid reversed-source coverage");
    std::cout << "REAL_BOUNDARY_SOURCE_CONTRACTS captures=" << captures
              << " reversed_captures=" << captures - before_reversed
              << " negative_controls=" << negatives << '\n';
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "Real-boundary source contracts failed: " << error.what() << '\n';
    return 1;
  }
}
