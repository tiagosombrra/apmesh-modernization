#include "application/runtime_config.h"
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/node_adaptive.h"
#include "generator/generator_adaptive.h"
#include "input_output/patch_reader.h"
#include "boundary_pair_candidate_contracts.h"
#include "live_boundary_pair_contracts.h"
#include "triangle_commit_observer_contracts.h"
#include "real_boundary_source.h"
#include "crab_mesh/aft/quadtree.h"
#include "crab_mesh/aft/quadtree_cell.h"
#include <algorithm>
#include <iomanip>
#include <iostream>
#include <optional>
#include <string_view>
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

void CheckCertifiedRefinement(PatchBezier& patch, const apmesh::quad::RealBoundarySource& source) {
  using namespace apmesh::quad;
  unsigned long last_id = 0;
  for (const auto& site : source.sites)
    last_id = std::max(last_id, site.source_id);
  std::vector<bool> requested(source.sites.size(), false);
  Require(CertifyBoundaryRefinement(patch, source, source, requested, last_id).empty(),
          "Unchanged boundary has a certified split");
  requested[0] = true;
  const auto refined = SplitFeedbackIntervals(patch, source, requested, last_id);
  const auto splits = CertifyBoundaryRefinement(patch, source, refined, requested, last_id);
  Require(splits.size() == 1 && splits.front().parent_interval == 0 &&
              splits.front().inserted_site == 1,
          "Native boundary refinement lost the requested parent interval");
  const auto* previous_owner = patch.GetSubMesh();
  const auto reject = [&](const auto& candidate, const auto& expected, unsigned long last) {
    try {
      (void)CertifyBoundaryRefinement(patch, source, candidate, expected, last);
    } catch (const std::runtime_error&) {
      Require(patch.GetSubMesh() == previous_owner, "Refinement proof changed the existing owner");
      return;
    }
    throw std::runtime_error("Invalid boundary refinement was certified");
  };
  reject(source, requested, last_id);
  reject(refined, requested, refined.sites[1].source_id);
  auto wrong_interval = requested;
  wrong_interval[0] = false;
  wrong_interval[1] = true;
  reject(refined, wrong_interval, last_id);
  auto moved = refined;
  moved.sites[0].xyz[2] += 1;
  reject(moved, requested, last_id);
}

void ReportCornerWitness(PatchBezier& patch, unsigned patch_index) {
  const auto endpoint = [&](unsigned side, bool local_end) {
    auto* curve = patch.GetCurve(side);
    if (curve->GetNumBerPoints() == 0)
      return static_cast<NodeAdaptive*>(nullptr);
    const bool source_end = local_end != patch.IsCurveReversed(side);
    const unsigned point = source_end ? curve->GetNumBerPoints() - 1 : 0;
    return dynamic_cast<NodeAdaptive*>(curve->GetPoint(point));
  };
  const std::array<const NodeAdaptive*, 4> first{endpoint(0, false), endpoint(0, true),
                                                 endpoint(1, true), endpoint(2, false)};
  const std::array<const NodeAdaptive*, 4> second{endpoint(3, false), endpoint(1, false),
                                                  endpoint(2, true), endpoint(3, true)};
  std::cerr << std::setprecision(17);
  for (unsigned corner = 0; corner < first.size(); ++corner) {
    const auto* a = first[corner];
    const auto* b = second[corner];
    if (!a || !b)
      continue;
    std::cerr << "SHARED_NATIVE_CORNER patch=" << patch_index << " corner=" << corner
              << " ids=" << a->GetId() << ',' << b->GetId()
              << " xyz_delta=" << a->GetX() - b->GetX() << ',' << a->GetY() - b->GetY() << ','
              << a->GetZ() - b->GetZ() << '\n';
  }
}

bool SameSample(const apmesh::quad::OriginalCurveSample& a,
                const apmesh::quad::OriginalCurveSample& b) {
  return a.parameter == b.parameter && a.xyz == b.xyz && a.source_id == b.source_id;
}

bool SameCurve(const std::vector<apmesh::quad::OriginalCurveSample>& a,
               const std::vector<apmesh::quad::OriginalCurveSample>& b) {
  return std::equal(a.begin(), a.end(), b.begin(), b.end(), SameSample);
}

void RunSharedSource(const apmesh::application::RuntimeConfig& config) {
  using namespace apmesh::quad;
  apmesh::application::ApplyRuntimeConfig(config);
  Geometry geometry;
  PatchReader reader;
  reader.ReaderFilePatches(&geometry, config.input_model);
  Require(geometry.GetNumberPatches() == 2, "Expected two original Bezier patches");
  std::array<PatchBezier*, 2> patches{};
  for (unsigned i = 0; i < patches.size(); ++i) {
    patches[i] = dynamic_cast<PatchBezier*>(geometry.GetPatch(i));
    Require(patches[i] != nullptr, "Expected an original Bezier patch");
  }
  std::array<unsigned, 2> sides{};
  unsigned shared = 0;
  for (unsigned a = 0; a < 4; ++a)
    for (unsigned b = 0; b < 4; ++b)
      if (patches[0]->GetCurve(a) == patches[1]->GetCurve(b)) {
        sides = {a, b};
        ++shared;
      }
  Require(shared == 1, "Expected exactly one original shared curve");

  struct Capture {
    RealBoundarySource source;
    PatchAttemptIdentity attempt{};
    unsigned domain = 0;
    bool local = false;
    bool selected_domain = false;
  };
  std::vector<Capture> captures;
  std::optional<RealBoundarySource> pending;
  unsigned active_patch = 2;
  unsigned active_domain = 0;
  CaptureHooks hooks;
  hooks.domain_begin_sink = [&](int, OuterAttemptIdentity, unsigned patch, unsigned domain) {
    Require(patch < patches.size(), "Unknown native patch");
    active_patch = patch;
    active_domain = domain;
  };
  hooks.provider = [&](Par2DJMesh::AFT::Quadtree& tree) {
    Require(active_patch < patches.size() && !pending, "Missing native domain scope");
    try {
      pending = CaptureRealBoundary(*patches[active_patch], tree);
    } catch (const std::runtime_error&) {
      ReportCornerWitness(*patches[active_patch], active_patch);
      throw;
    }
    LeafPolygonMesh witness;
    witness.source_leaves = pending->source_leaves;
    return witness;
  };
  hooks.sink = [&](AttemptUvCapture value) {
    Require(pending && value.attempt.patch_index == static_cast<int>(active_patch),
            "Native contour belongs to a different patch");
    captures.push_back({std::move(*pending), value.attempt, active_domain});
    pending.reset();
  };
  hooks.local_selection_sink = [&](LocalSelectionEvent value) {
    for (auto& capture : captures)
      if (capture.domain == active_domain && SamePatchScope(capture.attempt, value.attempt) &&
          capture.attempt.local_attempt == value.attempt.local_attempt)
        capture.local = value.kind == LocalSelectionKind::SelectedForAdapterReturn;
  };
  hooks.domain_selection_sink = [&](int step, OuterAttemptIdentity outer, unsigned patch,
                                    unsigned domain) {
    for (auto& capture : captures)
      if (capture.attempt.patch_index == static_cast<int>(patch) &&
          capture.attempt.adaptive_step == step && SameOuterAttempt(capture.attempt.outer, outer))
        capture.selected_domain = capture.domain == domain;
  };
  Model model(&geometry);
  GeneratorAdaptive generator(apmesh::application::MakeGenerationContext(config, NUMBER_PROCESS));
  Timer timer(config.num_processes, config.num_threads, 12);
  timer.InitTimerParallel(0, 0, 10);
  generator.SetResearchUvCapture(std::move(hooks), 25112026);
  generator.Generator(model, &timer);
  const auto* outcomes = generator.GetResearchGlobalOutcomeLog();
  Require(outcomes && !outcomes->truncated(), "Incomplete original decision log");

  std::array<const RealBoundarySource*, 2> source{};
  int step = -1;
  for (std::size_t i = 0; i < outcomes->size(); ++i) {
    const auto& outcome = outcomes->data()[i];
    if (outcome.kind != GlobalOutcomeKind::AcceptedStepCommitted)
      continue;
    for (const auto& capture : captures)
      if (capture.local && capture.selected_domain &&
          capture.attempt.adaptive_step == outcome.adaptive_step &&
          SameOuterAttempt(capture.attempt.outer, outcome.outer)) {
        auto& selected = source.at(capture.attempt.patch_index);
        Require(selected == nullptr, "Multiple captures for selected native patch");
        selected = &capture.source;
      }
    if (source[0] && source[1]) {
      step = outcome.adaptive_step;
      break;
    }
    source = {};
  }
  Require(step >= 0, "No accepted original TRI step with both patch sources");
  const auto& original = source[0]->original_curves[sides[0]];
  Require(SameCurve(original, source[1]->original_curves[sides[1]]),
          "Accepted TRI source partitions disagree");
  std::cout << "SHARED_SOURCE_WITNESS step=" << step << " sides=" << sides[0] << ',' << sides[1]
            << " shared_sites=" << original.size() << " native_leaves=" << source[0]->source_leaves
            << ',' << source[1]->source_leaves << '\n';
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
    CheckCertifiedRefinement(*patch, source);
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
    if (argc == 3 && std::string_view(argv[1]) == "--shared-source") {
      RunSharedSource(apmesh::application::LoadRuntimeConfig(argv[2]));
      return 0;
    }
    quad_test::BoundaryPairCandidateContracts();
    quad_test::TriangleCommitObserverContracts();
    quad_test::LiveBoundaryPairContracts();
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
    std::cout << "CERTIFIED_BOUNDARY_REFINEMENT confirmed=" << captures << " unchanged=" << captures
              << " negative_controls=" << 4 * captures << '\n';
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "Real-boundary source contracts failed: " << error.what() << '\n';
    return 1;
  }
}
