#include <algorithm>
#include "adapter/domain_generation_error.h"
#include <atomic>
#include <cctype>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
#include "data/curve/curve_adaptive_parametric_bezier.h"
#include "data/curve/curve_adaptive_parametric_hermite.h"
#include "data/definitions.h"
#include "data/model.h"
#include "data/patch/patch_bezier.h"
#include "data/patch/patch_hermite.h"
#include "data/vector_adaptive.h"
#include "data/vertex_adaptive.h"
#include "generator/generator_adaptive.h"
#include "input_output/models_3d.h"
#include "input_output/input_validation.h"
#include "input_output/patch_reader.h"
#include "timer/timer.h"
#include "application/runtime_config.h"
#include "application/run_application.h"

using apmesh::application::ApplyRuntimeConfig;
using apmesh::application::LoadRuntimeConfig;

#include <array>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <memory>
#include <sstream>
#include <stdexcept>

#if defined(_WIN32)
#include <windows.h>
#endif

namespace {
std::unique_ptr<MeshAdaptive> MakeMesh(unsigned count) {
  auto mesh = std::make_unique<MeshAdaptive>();
  auto sub = std::make_unique<SubMesh>();
  for (unsigned index = 0; index < count; ++index) {
    const double x = 2.0 * index;
    std::array<NodeAdaptive*, 3> nodes{};
    for (unsigned corner = 0; corner < 3; ++corner) {
      auto node = std::make_unique<NodeAdaptive>(x + (corner == 1), corner == 2, 0.0);
      node->SetId(3 * index + corner);
      nodes[corner] = node.get();
      sub->AddNoh(std::move(node));
    }
    auto triangle = std::make_unique<TriangleAdaptive>(nodes[0], nodes[1], nodes[2]);
    triangle->SetParametersN1({0.0, 0.0});
    triangle->SetParametersN2({1.0, 0.0});
    triangle->SetParametersN3({0.0, 1.0});
    sub->AddElement(std::move(triangle));
  }
  mesh->InsertSubMeshAdaptive(sub.release());
  return mesh;
}

struct Attempt {
  unsigned elements;
  GeneratorAdaptive::MeshAttemptMetrics metrics;
};

void CheckGenerationContexts(const std::filesystem::path& output) {
  const std::string saved_name = NAME_MODEL, saved_process = NUMBER_PROCESS,
                    saved_mode = WRITE_MESH;
  const std::string first_prefix = (output / "context-first" / "owned").generic_string();
  const std::string second_prefix = (output / "context-second" / "owned").generic_string();
  std::unique_ptr<GeneratorAdaptive> first;
  {
    apmesh::application::GenerationContext source{"first.bp", first_prefix, "h", "a"};
    first = std::make_unique<GeneratorAdaptive>(source);
    source = {"changed.bp", "changed-output", "m", "changed-process"};
  }
  GeneratorAdaptive second({"second.bp", second_prefix, "q", "b"});
  NAME_MODEL = (output / "foreign").generic_string();
  NUMBER_PROCESS = "foreign";
  WRITE_MESH = "m";
  const auto* context = first->GetGenerationContext();
  if (context == nullptr || context->input_model != "first.bp" ||
      context->output_prefix != first_prefix || context->write_mode != "h" ||
      context->process_suffix != "a" ||
      second.GetGenerationContext()->output_prefix != second_prefix)
    throw std::runtime_error("Generation identity did not retain independent owned values");

  auto mesh = MakeMesh(1);
  const GeneratorAdaptive::MeshAttemptMetrics metric{1, 1, 1, 1, 0, 1, 0, 0, 0, 0, .5, .1};
  first->WriteQualityMesh(mesh.get(), 0, metric);
  second.WriteQualityMesh(mesh.get(), 0, metric);
  first->WriteQualityMesh(mesh.get(), 1, metric);
  const auto rows = [](const std::string& path) {
    std::ifstream file(path);
    std::string line;
    unsigned count = 0;
    while (std::getline(file, line))
      ++count;
    return count;
  };
  if (rows(first_prefix + "_n.process_a_metrics_rank_-1.csv") != 3 ||
      rows(second_prefix + "_n.process_b_metrics_rank_-1.csv") != 2 ||
      std::filesystem::exists(NAME_MODEL + "_n.process_foreign_metrics_rank_-1.csv"))
    throw std::runtime_error("Interleaved generation outputs used another identity");
  GeneratorAdaptive legacy;
  if (legacy.GetGenerationContext() != nullptr)
    throw std::runtime_error("Legacy generator unexpectedly captured process state");
  NAME_MODEL = saved_name;
  NUMBER_PROCESS = saved_process;
  WRITE_MESH = saved_mode;
  std::cout << "generation_context owned=2 source_retired=1 interleaved_writes=3 legacy=1\n";
}

void CheckGenerationRequests(const std::filesystem::path& output) {
  using apmesh::application::GenerationRequest;
  const std::string path = (output / "missing-request.bp").generic_string();
  const std::string owned_path = (output / "missing-context.bp").generic_string();
  if (std::filesystem::exists(path) || std::filesystem::exists(owned_path) ||
      GenerationRequest{}.input_model.has_value())
    throw std::runtime_error("Generation request control precondition failed");
  GenerationRequest request;
  {
    std::string source = path;
    request = {2, 3, source};
    source.clear();
  }
  GeneratorAdaptive legacy;
  GeneratorAdaptive owned({owned_path, "unused", "", ""});
  const auto rejected = [](auto&& execute, const std::string& expected, bool bridge) {
    std::ostringstream transcript;
    struct RestoreBuffer {
      std::streambuf* previous;
      ~RestoreBuffer() { std::cout.rdbuf(previous); }
    } restore{std::cout.rdbuf(transcript.rdbuf())};
    bool caught = false;
    try {
      execute();
    } catch (const std::runtime_error& error) {
      caught = error.what() == "Cannot open model input: " + expected;
    }
    const bool printed = transcript.str().find("argv[]:") != std::string::npos;
    if (!caught || printed != bridge ||
        (bridge && transcript.str().find("argv[]:extra\n") == std::string::npos))
      throw std::runtime_error("Typed generation request or legacy bridge changed input routing");
  };
  Timer timer;
  rejected([&] { legacy.Execute(request, &timer); }, path, false);
  rejected([&] { owned.Execute(request, &timer); }, owned_path, false);
  request.input_model = "";
  rejected([&] { legacy.Execute(request, &timer); }, "", false);
  char program[] = "legacy", processes[] = "2", threads[] = "3", extra[] = "extra";
  std::string mutable_path = path;
  char* arguments[] = {program, processes, threads, mutable_path.data(), extra, nullptr};
  rejected([&] { legacy.Execute(arguments, &timer); }, path, true);
  rejected([&] { owned.Execute(arguments, &timer); }, owned_path, true);
  std::cout << "generation_request typed=3 legacy=2 context_precedence=2 empty_path=1\n";
}

void CheckAdaptivePolicyContexts() {
  using apmesh::application::AdaptivePolicyConfig;
  using apmesh::application::RuntimeConfig;
  const AdaptivePolicyConfig saved{
      ADAPTIVE_MODE,      ADAPTIVE_MAX_STEPS,        STEPS,
      ADAPTIVE_INTENSITY, ADAPTIVE_QUALITY_PRIORITY, ADAPTIVE_TARGET_GROWTH};
  const auto apply = [](const AdaptivePolicyConfig& config) {
    ADAPTIVE_MODE = config.mode;
    ADAPTIVE_MAX_STEPS = config.adaptive_max_steps;
    STEPS = config.legacy_max_steps;
    ADAPTIVE_INTENSITY = config.intensity;
    ADAPTIVE_QUALITY_PRIORITY = config.quality_priority;
    ADAPTIVE_TARGET_GROWTH = config.target_growth;
  };
  const auto equal = [](const GeneratorAdaptive::AdaptivePolicyRuntime& a,
                        const GeneratorAdaptive::AdaptivePolicyRuntime& b) {
    const std::array<double, 7> first{{a.intensity, a.quality_priority, a.step1_target_growth,
                                       a.stepn_target_growth, a.step2_accept_quality_min,
                                       a.step2_accept_max_error_increase_abs,
                                       a.equivalent_patch_min_ratio}};
    const std::array<double, 7> second{{b.intensity, b.quality_priority, b.step1_target_growth,
                                        b.stepn_target_growth, b.step2_accept_quality_min,
                                        b.step2_accept_max_error_increase_abs,
                                        b.equivalent_patch_min_ratio}};
    return a.mode == b.mode && a.stable_mode == b.stable_mode && a.debug_mode == b.debug_mode &&
           a.max_steps == b.max_steps &&
           std::memcmp(first.data(), second.data(), first.size() * sizeof(double)) == 0;
  };
  GeneratorAdaptive legacy;
  GeneratorAdaptive identity_only({"unused", "unused", "", ""});
  const std::array<AdaptivePolicyConfig, 4> cases{{
      {"", 7, 11, -0.5, 1.5, 0.5},
      {"legacy", 4, 9, 0.35, 0.25, 2.2},
      {"adaptive_stable", 7, 13, 1.5, -0.5, 0.8},
      {"research_debug", 9, 17, 0.55, 0.8, 1.9},
  }};
  for (const auto& value : cases) {
    apply(value);
    const auto expected = legacy.BuildAdaptivePolicyRuntime();
    std::unique_ptr<GeneratorAdaptive> owned;
    {
      RuntimeConfig config;
      config.adaptive_mode = value.mode;
      config.adaptive_max_iterations = value.adaptive_max_steps;
      config.adaptive_intensity = value.intensity;
      config.adaptive_quality_priority = value.quality_priority;
      config.adaptive_target_growth = value.target_growth;
      auto source = apmesh::application::MakeGenerationContext(config);
      config.adaptive_mode = "changed";
      config.adaptive_intensity = 0.99;
      owned = std::make_unique<GeneratorAdaptive>(source);
      source.adaptive_policy.reset();
    }
    apply({"legacy", 31, 99, 0.0, 0.0, 9.0});
    const auto foreign = legacy.BuildAdaptivePolicyRuntime();
    if (equal(expected, foreign) || !equal(expected, owned->BuildAdaptivePolicyRuntime()) ||
        !equal(foreign, identity_only.BuildAdaptivePolicyRuntime()))
      throw std::runtime_error("Adaptive policy ownership or legacy differential control failed");
    if (expected.mode != (value.mode.empty() ? "legacy" : value.mode) ||
        expected.max_steps !=
            (value.mode == "adaptive_stable" ? value.adaptive_max_steps : value.legacy_max_steps) ||
        expected.stable_mode != (value.mode == "adaptive_stable") ||
        expected.debug_mode != (value.mode == "research_debug"))
      throw std::runtime_error("Adaptive mode or step-limit selection changed");
  }
  apply(saved);
  std::cout << "adaptive_policy_context cases=4 scalar_bits=28 conflicting_globals=4 legacy=2\n";
}

void CheckDomainInputs(const std::string& mode) {
  GeneratorAdaptive generator;
  Geometry geometry;
  auto mesh = MakeMesh(2);
  Geometry* geometry_argument = mode == "null-mesh" ? &geometry : nullptr;
  MeshAdaptive* mesh_argument = mode == "null-geometry" ? mesh.get() : nullptr;
  bool rejected = false;
  try {
    generator.AdaptDomain(geometry_argument, mesh_argument);
  } catch (const std::invalid_argument& error) {
    rejected = std::string(error.what()) == "Domain adaptation requires a geometry and mesh";
  }
  if (!rejected || mesh->GetNumberSubMeshesAdaptive() != 1 ||
      mesh->GetSubMeshAdaptiveByPosition(0)->GetNumberElements() != 2 ||
      geometry.GetNumberPatches() != 0)
    throw std::runtime_error("Null domain inputs were not rejected before mesh mutation");
}

void WriteCurvatureControl(const std::filesystem::path& output, bool curved) {
  Geometry geometry;
  Models3d models;
  if (curved)
    models.ModelBaseQuadrada(&geometry);
  else
    models.ModelBordaCurva(&geometry);
  Model model(&geometry);
  Timer timer;
  GeneratorAdaptive generator;
  ADAPTIVE_MODE = "legacy";
  STEPS = 0;
  WRITE_MESH.clear();
  NAME_MODEL = (output / "diagnostic").generic_string();
  generator.Generator(model, &timer);
  generator.SaveErrorMesh(generator.mesh_.get());
  const SubMesh* sub = generator.mesh_->GetSubMeshAdaptiveByPosition(0);
  std::ofstream fixture(output / "fixture.json");
  fixture << std::setprecision(17) << "{\"nodes\":[";
  for (unsigned i = 0; i < sub->GetNumberNos(); ++i) {
    const NodeAdaptive* node = sub->GetNoh(i);
    const auto parameters = static_cast<PatchHermite*>(sub->GetPatch())->FindUV(*node);
    if (i)
      fixture << ',';
    fixture << '[' << node->GetId() << ',' << node->GetX() << ',' << node->GetY() << ','
            << node->GetZ() << ',' << node->GetGa() << ',' << node->GetGd() << ','
            << std::get<0>(parameters) << ',' << std::get<1>(parameters) << ']';
  }
  fixture << "],\"faces\":[";
  for (unsigned i = 0; i < sub->GetNumberElements(); ++i) {
    const ElementAdaptive* triangle = sub->GetElement(i);
    if (i)
      fixture << ',';
    fixture << '[' << triangle->GetNoh(1).GetId() << ',' << triangle->GetNoh(2).GetId() << ','
            << triangle->GetNoh(3).GetId() << ']';
  }
  fixture << "]}\n";
}
} // namespace

#if defined(AP_MESH_DOMAIN_FAILURE_WRAP)
#include "domain_candidate_fixture.h"
#include "candidate_snapshot_fixture.h"
#include "accepted_root_fixture.h"
#include "domain_observer_fixture.h"
#include "typed_domain_failure_fixture.h"
namespace {
bool inject_domain_failure = false;
}
extern "C" bool RealDomainExecute(AdvancingFront*, const FaceList&) asm(
    "__real__ZN10Par2DJMesh3AFT14AdvancingFront7executeERKNSt7__"
    "cxx114listIPNS_6Basics4FaceESaIS6_EEE");
extern "C" bool WrappedDomainExecute(AdvancingFront*, const FaceList&) asm(
    "__wrap__ZN10Par2DJMesh3AFT14AdvancingFront7executeERKNSt7__cxx114listIPNS_6Basics4FaceESaIS6_"
    "EEE");
extern "C" bool WrappedDomainExecute(AdvancingFront* front, const FaceList& previous) {
  const auto context = front->GetRunStats();
  domain_observer_test::BeforeExecute(context.adaptive_step, context.patch_index);
  if (typed_domain_test::BeforeExecute(context.adaptive_step, context.patch_index))
    return false;
  if (inject_domain_failure && context.adaptive_step == 2 && context.patch_index == 0) {
    std::cerr << "Domain failure control: step=2 patch=0\n";
    return false;
  }
  return RealDomainExecute(front, previous);
}

void CheckStopRetryContexts() {
  using apmesh::application::StopRetryConfig;
  GeneratorAdaptive legacy;
  GeneratorAdaptive identity_only({"unused", "unused", "", ""});
  const auto saved = legacy.BuildStopRetryRuntime();
  const auto apply = [](const StopRetryConfig& config) {
    EPSYLON = config.global_error_target;
    MIN_IMPROVEMENT = config.minimum_improvement;
    PATIENCE = config.patience;
    TOL_LOCAL = config.local_error_target;
    ADAPTIVE_RETRY_COUNT = config.retry_count;
    ADAPTIVE_RETRY_SHRINK = config.retry_shrink;
    MAX_RETRY_ELEMENT_GROWTH_FACTOR = config.growth_factor_limit;
    MAX_RETRY_ELEMENT_GROWTH_ABS = config.growth_absolute_limit;
    ERROR_FLOOR = config.error_floor;
    MIN_ERROR_DROP_ABS = config.minimum_error_drop;
    MIN_ERROR_DROP_PER_ELEMENT = config.minimum_error_drop_per_element;
  };
  const auto equal = [](const StopRetryConfig& a, const StopRetryConfig& b) {
    const std::array<double, 9> first{{a.global_error_target, a.minimum_improvement,
                                       a.local_error_target, a.retry_shrink, a.growth_factor_limit,
                                       a.growth_absolute_limit, a.error_floor, a.minimum_error_drop,
                                       a.minimum_error_drop_per_element}};
    const std::array<double, 9> second{{b.global_error_target, b.minimum_improvement,
                                        b.local_error_target, b.retry_shrink, b.growth_factor_limit,
                                        b.growth_absolute_limit, b.error_floor,
                                        b.minimum_error_drop, b.minimum_error_drop_per_element}};
    return a.patience == b.patience && a.retry_count == b.retry_count &&
           std::memcmp(first.data(), second.data(), first.size() * sizeof(double)) == 0;
  };
  const std::array<StopRetryConfig, 3> cases{{
      {},
      {0.125, 0.25, 5, 0.0625, 2, 0.75, 3.0, 20.0, 0.01, 0.02, 0.03},
      {-0.125, 0.0, 1, 0.0, -2, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0},
  }};
  for (const auto& value : cases) {
    apply(value);
    auto expected = legacy.BuildStopRetryRuntime();
    std::unique_ptr<GeneratorAdaptive> owned;
    {
      apmesh::application::RuntimeConfig config;
      config.epsylon = value.global_error_target;
      config.min_improvement = value.minimum_improvement;
      config.patience = value.patience;
      config.tol_local = value.local_error_target;
      config.adaptive_retry_count = value.retry_count;
      config.adaptive_retry_shrink = value.retry_shrink;
      auto source = apmesh::application::MakeGenerationContext(config);
      config.epsylon = 99.0;
      owned = std::make_unique<GeneratorAdaptive>(source);
      source.stop_retry.reset();
    }
    apply({0.5, 0.75, 9, 0.25, 13, 0.5, 7.0, 40.0, 0.1, 0.2, 0.3});
    const auto foreign = legacy.BuildStopRetryRuntime();
    if (equal(expected, foreign) || !equal(expected, owned->BuildStopRetryRuntime()) ||
        !equal(foreign, identity_only.BuildStopRetryRuntime()))
      throw std::runtime_error("Stopping/retry ownership or legacy differential control failed");
    DomainCandidateFixture::PromoteRetry(*owned);
    expected.retry_count = std::max(1, value.retry_count);
    if (!equal(expected, owned->BuildStopRetryRuntime()) || ADAPTIVE_RETRY_COUNT != 13 ||
        owned->GetGenerationContext()->stop_retry->retry_count != value.retry_count)
      throw std::runtime_error("Owned retry promotion changed raw configuration or global state");
    for (GeneratorAdaptive* generator : {&legacy, &identity_only}) {
      apply(value);
      DomainCandidateFixture::PromoteRetry(*generator);
      if (!equal(expected, generator->BuildStopRetryRuntime()) ||
          ADAPTIVE_RETRY_COUNT != expected.retry_count)
        throw std::runtime_error("Legacy retry promotion stopped updating process state");
    }
  }
  apply(saved);
  std::cout << "stop_retry_context cases=3 scalar_bits=27 promotion=3 legacy=2\n";
}

void CheckAdaptationContexts() {
  using apmesh::application::AdaptationConfig;
  GeneratorAdaptive legacy;
  GeneratorAdaptive identity_only({"unused", "unused", "", ""});
  const auto saved = legacy.BuildAdaptationRuntime();
  const auto apply = [](const AdaptationConfig& config) {
    ADAPTATION_RELAXATION = config.relaxation;
    ADAPTATION_MAX_DELTA = config.max_delta;
    PATCH_FACTOR_MIN = config.factor_min;
    PATCH_FACTOR_MAX = config.factor_max;
  };
  const auto bits = [](const AdaptationConfig& config) {
    return std::array<double, 4>{
        {config.relaxation, config.max_delta, config.factor_min, config.factor_max}};
  };
  const auto equal = [&](const AdaptationConfig& a, const AdaptationConfig& b) {
    const auto first = bits(a), second = bits(b);
    return std::memcmp(first.data(), second.data(), first.size() * sizeof(double)) == 0;
  };
  const auto same_factors = [](const std::vector<double>& a, const std::vector<double>& b) {
    return a.size() == b.size() && std::memcmp(a.data(), b.data(), a.size() * sizeof(double)) == 0;
  };
  const std::vector<double> targets{0.4, 0.95, 1.4};
  const std::array<AdaptationConfig, 3> cases{
      {{}, {0.20, 0.03, 0.87, 1.04}, {0.65, 0.25, 0.70, 1.30}}};
  for (const auto& value : cases) {
    apply(value);
    const auto expected = legacy.BuildAdaptationRuntime();
    const auto expected_factors = DomainCandidateFixture::RateLimit(legacy, targets);
    std::unique_ptr<GeneratorAdaptive> owned;
    {
      apmesh::application::RuntimeConfig config;
      config.adaptation_relaxation = value.relaxation;
      config.adaptation_max_delta = value.max_delta;
      config.patch_factor_min = value.factor_min;
      config.patch_factor_max = value.factor_max;
      auto source = apmesh::application::MakeGenerationContext(config);
      config.adaptation_relaxation = 99.0;
      owned = std::make_unique<GeneratorAdaptive>(source);
      source.adaptation.reset();
    }
    apply({1.0, 0.8, 0.10, 2.0});
    const auto foreign = legacy.BuildAdaptationRuntime();
    if (equal(expected, foreign) || !equal(expected, owned->BuildAdaptationRuntime()) ||
        !equal(foreign, identity_only.BuildAdaptationRuntime()) ||
        same_factors(expected_factors, DomainCandidateFixture::RateLimit(legacy, targets)) ||
        !same_factors(expected_factors, DomainCandidateFixture::RateLimit(*owned, targets)))
      throw std::runtime_error("Adaptation ownership or rate-limit differential control failed");
    DomainCandidateFixture::StableAdaptation(*owned);
    if (!equal(foreign, legacy.BuildAdaptationRuntime()) ||
        !equal(value, *owned->GetGenerationContext()->adaptation))
      throw std::runtime_error("Owned stable adaptation changed raw configuration or globals");
    DomainCandidateFixture::StableAdaptation(legacy);
    const auto stable = legacy.BuildAdaptationRuntime();
    if (!equal(stable, owned->BuildAdaptationRuntime()) ||
        !same_factors(DomainCandidateFixture::RateLimit(legacy, targets),
                      DomainCandidateFixture::RateLimit(*owned, targets)))
      throw std::runtime_error("Owned stable adaptation changed effective values or factors");
    apply(foreign);
    DomainCandidateFixture::StableAdaptation(identity_only);
    if (!equal(stable, legacy.BuildAdaptationRuntime()))
      throw std::runtime_error("Identity-only stable adaptation stopped updating process state");
  }
  apply(saved);
  std::cout << "adaptation_context cases=3 scalar_bits=12 rate_limit_bits=18 stable=3 legacy=2\n";
}

void CheckElementBudgetContexts() {
  using apmesh::application::ElementBudgetConfig;
  const std::array<double ElementBudgetConfig::*, 24> doubles{
      {&ElementBudgetConfig::absolute_limit,
       &ElementBudgetConfig::growth_factor,
       &ElementBudgetConfig::soft_ratio,
       &ElementBudgetConfig::retry_topk_shrink,
       &ElementBudgetConfig::retry_h_scale,
       &ElementBudgetConfig::retry_factor_range_scale,
       &ElementBudgetConfig::pressure_start,
       &ElementBudgetConfig::pressure_h_scale,
       &ElementBudgetConfig::pressure_factor_shrink,
       &ElementBudgetConfig::patch_local_base,
       &ElementBudgetConfig::patch_local_rank_scale,
       &ElementBudgetConfig::patch_local_efficiency_scale,
       &ElementBudgetConfig::patch_local_h_scale,
       &ElementBudgetConfig::patch_local_hard_cap,
       &ElementBudgetConfig::step2_growth,
       &ElementBudgetConfig::step3plus_growth,
       &ElementBudgetConfig::target_h_scale,
       &ElementBudgetConfig::step1_growth,
       &ElementBudgetConfig::target_min,
       &ElementBudgetConfig::target_max,
       &ElementBudgetConfig::patch_error_weight,
       &ElementBudgetConfig::patch_efficiency_weight,
       &ElementBudgetConfig::patch_quality_weight,
       &ElementBudgetConfig::patch_min_share}};
  const std::array<int ElementBudgetConfig::*, 8> integers{
      {&ElementBudgetConfig::step_mode, &ElementBudgetConfig::pressure_mode,
       &ElementBudgetConfig::patch_local_mode, &ElementBudgetConfig::target_growth_mode,
       &ElementBudgetConfig::budget_driven, &ElementBudgetConfig::target_mode,
       &ElementBudgetConfig::patch_allocation_mode, &ElementBudgetConfig::patch_topk_only_mode}};
  GeneratorAdaptive legacy;
  GeneratorAdaptive identity_only({"unused", "unused", "", ""});
  const auto saved = legacy.BuildElementBudgetRuntime();
  const auto apply = [](const ElementBudgetConfig& config) {
    STEP_ELEMENT_BUDGET_MODE = config.step_mode;
    STEP_ELEMENT_BUDGET_ABS = config.absolute_limit;
    STEP_ELEMENT_BUDGET_GROWTH_FACTOR = config.growth_factor;
    STEP_ELEMENT_BUDGET_SOFT_RATIO = config.soft_ratio;
    STEP_ELEMENT_BUDGET_RETRY_SHRINK_TOPK = config.retry_topk_shrink;
    STEP_ELEMENT_BUDGET_RETRY_H_SCALE = config.retry_h_scale;
    STEP_ELEMENT_BUDGET_RETRY_FACTOR_RANGE_SCALE = config.retry_factor_range_scale;
    STEP_ELEMENT_BUDGET_PRESSURE_MODE = config.pressure_mode;
    STEP_ELEMENT_BUDGET_PRESSURE_START = config.pressure_start;
    STEP_ELEMENT_BUDGET_PRESSURE_H_SCALE = config.pressure_h_scale;
    STEP_ELEMENT_BUDGET_PRESSURE_FACTOR_SHRINK = config.pressure_factor_shrink;
    PATCH_LOCAL_ELEMENT_BUDGET_MODE = config.patch_local_mode;
    PATCH_LOCAL_ELEMENT_BUDGET_BASE = config.patch_local_base;
    PATCH_LOCAL_ELEMENT_BUDGET_SCALE_BY_RANK = config.patch_local_rank_scale;
    PATCH_LOCAL_ELEMENT_BUDGET_SCALE_BY_EFFICIENCY = config.patch_local_efficiency_scale;
    PATCH_LOCAL_BUDGET_H_SCALE = config.patch_local_h_scale;
    PATCH_LOCAL_BUDGET_HARD_CAP = config.patch_local_hard_cap;
    STEP_TARGET_ELEMENT_GROWTH_MODE = config.target_growth_mode;
    STEP2_TARGET_ELEMENT_GROWTH = config.step2_growth;
    STEP3PLUS_TARGET_ELEMENT_GROWTH = config.step3plus_growth;
    STEP_TARGET_GROWTH_H_SCALE = config.target_h_scale;
    BUDGET_DRIVEN_ADAPTATION = config.budget_driven;
    STEP_ELEMENT_TARGET_MODE = config.target_mode;
    STEP1_TARGET_ELEMENT_GROWTH = config.step1_growth;
    STEP_ELEMENT_TARGET_MIN = config.target_min;
    STEP_ELEMENT_TARGET_MAX = config.target_max;
    PATCH_BUDGET_ALLOCATION_MODE = config.patch_allocation_mode;
    PATCH_BUDGET_ERROR_WEIGHT = config.patch_error_weight;
    PATCH_BUDGET_EFFICIENCY_WEIGHT = config.patch_efficiency_weight;
    PATCH_BUDGET_QUALITY_WEIGHT = config.patch_quality_weight;
    PATCH_BUDGET_MIN_SHARE = config.patch_min_share;
    PATCH_BUDGET_TOPK_ONLY_MODE = config.patch_topk_only_mode;
  };
  const auto equal = [&](const ElementBudgetConfig& a, const ElementBudgetConfig& b) {
    for (auto field : doubles)
      if (std::memcmp(&(a.*field), &(b.*field), sizeof(double)) != 0)
        return false;
    for (auto field : integers)
      if (a.*field != b.*field)
        return false;
    return true;
  };
  const auto targets = [](const GeneratorAdaptive& generator) {
    return std::array<double, 3>{{DomainCandidateFixture::ClampElementTarget(generator, 0.0),
                                  DomainCandidateFixture::ClampElementTarget(generator, 100.0),
                                  DomainCandidateFixture::ClampElementTarget(generator, 10000.0)}};
  };
  const auto same_targets = [](const std::array<double, 3>& a, const std::array<double, 3>& b) {
    return std::memcmp(a.data(), b.data(), a.size() * sizeof(double)) == 0;
  };
  std::array<ElementBudgetConfig, 3> cases{};
  ElementBudgetConfig foreign;
  for (std::size_t i = 0; i < doubles.size(); ++i) {
    cases[1].*doubles[i] = static_cast<double>(i + 1) * 0.125;
    cases[2].*doubles[i] = static_cast<double>(i + 1) * 0.25;
    foreign.*doubles[i] = 100.0 + static_cast<double>(i);
  }
  for (std::size_t i = 0; i < integers.size(); ++i) {
    cases[1].*integers[i] = static_cast<int>(i % 2);
    cases[2].*integers[i] = static_cast<int>(i % 3);
    foreign.*integers[i] = 9;
  }
  foreign.target_min = 250.0;
  foreign.target_max = 900.0;
  for (const auto& value : cases) {
    apply(value);
    const auto expected = legacy.BuildElementBudgetRuntime();
    const auto expected_targets = targets(legacy);
    std::unique_ptr<GeneratorAdaptive> owned;
    {
      auto source =
          apmesh::application::MakeGenerationContext(apmesh::application::RuntimeConfig{});
      owned = std::make_unique<GeneratorAdaptive>(source);
      source.element_budget.reset();
    }
    apply(foreign);
    if (equal(expected, legacy.BuildElementBudgetRuntime()) ||
        !equal(expected, owned->BuildElementBudgetRuntime()) ||
        !equal(foreign, identity_only.BuildElementBudgetRuntime()) ||
        same_targets(expected_targets, targets(legacy)) ||
        !same_targets(expected_targets, targets(*owned)))
      throw std::runtime_error("Element budget ownership or target-clamp differential failed");
    DomainCandidateFixture::StableElementBudget(*owned);
    if (!equal(foreign, legacy.BuildElementBudgetRuntime()) ||
        !equal(value, *owned->GetGenerationContext()->element_budget))
      throw std::runtime_error(
          "Owned element budget overrides changed raw configuration or globals");
    apply(value);
    DomainCandidateFixture::StableElementBudget(legacy);
    const auto stable = legacy.BuildElementBudgetRuntime();
    if (!equal(stable, owned->BuildElementBudgetRuntime()) ||
        !same_targets(targets(legacy), targets(*owned)))
      throw std::runtime_error(
          "Owned element budget overrides changed effective values or targets");
    apply(value);
    DomainCandidateFixture::StableElementBudget(identity_only);
    if (!equal(stable, legacy.BuildElementBudgetRuntime()))
      throw std::runtime_error("Legacy element budget overrides stopped updating process state");
  }
  apply(saved);
  std::cout << "element_budget_context cases=3 scalar_bits=72 target_bits=18 stable=3 legacy=2\n";
}

void CheckCurveControlsContexts() {
  using apmesh::application::CurveControlsConfig;
  const std::array<double CurveControlsConfig::*, 11> doubles{
      {&CurveControlsConfig::adaptation_blend, &CurveControlsConfig::factor_sensitivity,
       &CurveControlsConfig::step2_sensitivity_scale, &CurveControlsConfig::efficiency_weight,
       &CurveControlsConfig::point_growth_step1, &CurveControlsConfig::point_growth_stepn,
       &CurveControlsConfig::point_budget_blend,
       &CurveControlsConfig::consistency_max_point_ratio_step2,
       &CurveControlsConfig::consistency_group_blend, &CurveControlsConfig::discretization_factor,
       &CurveControlsConfig::internal_discretization_factor}};
  const std::array<int CurveControlsConfig::*, 6> integers{
      {&CurveControlsConfig::adaptation_policy, &CurveControlsConfig::point_budget_mode,
       &CurveControlsConfig::point_min, &CurveControlsConfig::point_max,
       &CurveControlsConfig::consistency_mode, &CurveControlsConfig::consistency_priority_bonus}};
  GeneratorAdaptive legacy;
  GeneratorAdaptive identity_only({"unused", "unused", "", ""});
  const auto saved = legacy.BuildCurveControlsRuntime();
  const auto apply = [](const CurveControlsConfig& config) {
    CURVE_ADAPTATION_POLICY = config.adaptation_policy;
    CURVE_ADAPTATION_BLEND = config.adaptation_blend;
    CURVE_FACTOR_SENSITIVITY = config.factor_sensitivity;
    STEP2_CURVE_SENSITIVITY_SCALE = config.step2_sensitivity_scale;
    CURVE_EFFICIENCY_WEIGHT = config.efficiency_weight;
    CURVE_POINT_BUDGET_MODE = config.point_budget_mode;
    CURVE_POINT_GROWTH_STEP1 = config.point_growth_step1;
    CURVE_POINT_GROWTH_STEPN = config.point_growth_stepn;
    CURVE_POINT_BUDGET_BLEND = config.point_budget_blend;
    CURVE_POINT_MIN = config.point_min;
    CURVE_POINT_MAX = config.point_max;
    CURVE_CONSISTENCY_MODE = config.consistency_mode;
    CURVE_CONSISTENCY_MAX_POINT_RATIO_STEP2 = config.consistency_max_point_ratio_step2;
    CURVE_CONSISTENCY_PRIORITY_BONUS = config.consistency_priority_bonus;
    CURVE_CONSISTENCY_GROUP_BLEND = config.consistency_group_blend;
    DISCRETIZATION_CURVE_FACTOR = config.discretization_factor;
    DISCRETIZATION_CURVE_FACTOR_INTERNAL = config.internal_discretization_factor;
  };
  const auto equal = [&](const CurveControlsConfig& a, const CurveControlsConfig& b) {
    for (auto field : doubles)
      if (std::memcmp(&(a.*field), &(b.*field), sizeof(double)) != 0)
        return false;
    for (auto field : integers)
      if (a.*field != b.*field)
        return false;
    return true;
  };
  const auto points = [](const GeneratorAdaptive& generator) {
    return std::array<int, 3>{{DomainCandidateFixture::ClampCurvePoints(generator, -3),
                               DomainCandidateFixture::ClampCurvePoints(generator, 8),
                               DomainCandidateFixture::ClampCurvePoints(generator, 300)}};
  };
  const auto pair_equal = [](const std::array<double, 2>& a, const CurveControlsConfig& value) {
    const std::array<double, 2> expected{
        {value.discretization_factor, value.internal_discretization_factor}};
    return std::memcmp(a.data(), expected.data(), a.size() * sizeof(double)) == 0;
  };
  std::array<CurveControlsConfig, 3> cases{};
  CurveControlsConfig foreign;
  for (std::size_t i = 0; i < doubles.size(); ++i) {
    cases[1].*doubles[i] = 0.5 + static_cast<double>(i) * 0.125;
    cases[2].*doubles[i] = 1.0 + static_cast<double>(i) * 0.25;
    foreign.*doubles[i] = 10.0 + static_cast<double>(i);
  }
  cases[1].adaptation_policy = 3;
  cases[1].point_min = 3;
  cases[1].point_max = 33;
  cases[2].adaptation_policy = 2;
  cases[2].point_min = 9;
  cases[2].point_max = 4;
  cases[2].consistency_mode = 2;
  foreign.adaptation_policy = 9;
  foreign.point_budget_mode = foreign.consistency_mode = 9;
  foreign.point_min = 20;
  foreign.point_max = 27;
  for (const auto& value : cases) {
    apply(value);
    const auto expected = legacy.BuildCurveControlsRuntime();
    const auto expected_points = points(legacy);
    std::unique_ptr<GeneratorAdaptive> owned;
    {
      apmesh::application::RuntimeConfig config;
      config.curve_adaptation_policy = value.adaptation_policy;
      config.curve_adaptation_blend = value.adaptation_blend;
      config.curve_factor_sensitivity = value.factor_sensitivity;
      config.curve_point_budget_mode = value.point_budget_mode;
      config.curve_point_growth_step1 = value.point_growth_step1;
      config.curve_point_growth_stepn = value.point_growth_stepn;
      config.curve_point_budget_blend = value.point_budget_blend;
      config.curve_point_min = value.point_min;
      config.curve_point_max = value.point_max;
      auto source = apmesh::application::MakeGenerationContext(config);
      config.curve_adaptation_blend = 99.0;
      owned = std::make_unique<GeneratorAdaptive>(source);
      source.curves.reset();
    }
    apply(foreign);
    if (equal(expected, legacy.BuildCurveControlsRuntime()) ||
        !equal(expected, owned->BuildCurveControlsRuntime()) ||
        !equal(foreign, identity_only.BuildCurveControlsRuntime()) ||
        expected_points == points(legacy) || expected_points != points(*owned) ||
        !pair_equal(DomainCandidateFixture::CurveDiscretization(*owned), value) ||
        !pair_equal(DomainCandidateFixture::CurveDiscretization(legacy), foreign))
      throw std::runtime_error(
          "Curve controls ownership, point clamp or Adapter factor pair changed");
    DomainCandidateFixture::CurvePointBudget(*owned);
    auto intermediate = value;
    intermediate.point_budget_mode = 1;
    if (!equal(intermediate, owned->BuildCurveControlsRuntime()))
      throw std::runtime_error("Curve point-budget update changed other controls");
    DomainCandidateFixture::CurveConsistency(*owned);
    if (!equal(foreign, legacy.BuildCurveControlsRuntime()) ||
        !equal(value, *owned->GetGenerationContext()->curves))
      throw std::runtime_error("Owned curve mode updates changed raw configuration or globals");
    apply(value);
    DomainCandidateFixture::CurvePointBudget(legacy);
    DomainCandidateFixture::CurveConsistency(legacy);
    const auto stable = legacy.BuildCurveControlsRuntime();
    if (!equal(stable, owned->BuildCurveControlsRuntime()) || points(legacy) != points(*owned) ||
        !pair_equal(DomainCandidateFixture::CurveDiscretization(*owned), value))
      throw std::runtime_error("Curve mode updates lost prior effective settings or point targets");
    apply(value);
    DomainCandidateFixture::CurvePointBudget(identity_only);
    DomainCandidateFixture::CurveConsistency(identity_only);
    if (!equal(stable, legacy.BuildCurveControlsRuntime()))
      throw std::runtime_error("Legacy curve mode updates stopped changing process state");
  }
  apply(saved);
  std::cout << "curve_controls_context cases=3 scalar_bits=33 point_targets=18 adapter_bits=12 "
               "stable=3 legacy=2\n";
}

void CheckQuadtreeControlsContexts() {
  using apmesh::application::QuadtreeControlsConfig;
  const std::array<double QuadtreeControlsConfig::*, 9> doubles{
      {&QuadtreeControlsConfig::saturation_elements_threshold,
       &QuadtreeControlsConfig::saturation_efficiency_threshold,
       &QuadtreeControlsConfig::saturation_h_scale,
       &QuadtreeControlsConfig::hard_saturation_factor_min, &QuadtreeControlsConfig::min_h_scale,
       &QuadtreeControlsConfig::neighbor_relax, &QuadtreeControlsConfig::face_quality_threshold,
       &QuadtreeControlsConfig::low_quality_h_factor,
       &QuadtreeControlsConfig::template_poor_score_threshold}};
  const std::array<int QuadtreeControlsConfig::*, 10> integers{
      {&QuadtreeControlsConfig::saturation_mode, &QuadtreeControlsConfig::hard_saturation_mode,
       &QuadtreeControlsConfig::hard_saturation_steps,
       &QuadtreeControlsConfig::skip_low_quality_on_saturated,
       &QuadtreeControlsConfig::postprocess_damp_on_saturated, &QuadtreeControlsConfig::cap_mode,
       &QuadtreeControlsConfig::depth_step1, &QuadtreeControlsConfig::depth_stepn,
       &QuadtreeControlsConfig::template_limit_mode,
       &QuadtreeControlsConfig::resolve_negative_depth}};
  GeneratorAdaptive legacy;
  GeneratorAdaptive identity_only({"unused", "unused", "", ""});
  const auto saved = legacy.BuildQuadtreeRuntime();
  const auto apply = [](const QuadtreeControlsConfig& config) {
    QUADTREE_SATURATION_MODE = config.saturation_mode;
    QUADTREE_SATURATION_ELEMENTS_THRESHOLD = config.saturation_elements_threshold;
    QUADTREE_SATURATION_EFFICIENCY_THRESHOLD = config.saturation_efficiency_threshold;
    QUADTREE_SATURATION_H_SCALE = config.saturation_h_scale;
    QUADTREE_HARD_SATURATION_MODE = config.hard_saturation_mode;
    QUADTREE_HARD_SATURATION_STEPS = config.hard_saturation_steps;
    QUADTREE_HARD_SATURATION_FACTOR_MIN = config.hard_saturation_factor_min;
    QUADTREE_SKIP_LOW_QUALITY_SUBDIVIDE_ON_SATURATED = config.skip_low_quality_on_saturated;
    QUADTREE_POSTPROCESS_DAMP_ON_SATURATED = config.postprocess_damp_on_saturated;
    PATCH_QUADTREE_CAP_MODE = config.cap_mode;
    PATCH_QUADTREE_DEPTH_STEP1 = config.depth_step1;
    PATCH_QUADTREE_DEPTH_STEPN = config.depth_stepn;
    PATCH_QUADTREE_MIN_H_SCALE = config.min_h_scale;
    PATCH_QUADTREE_NEIGHBOR_RELAX = config.neighbor_relax;
    PATCH_QUADTREE_TEMPLATE_LIMIT_MODE = config.template_limit_mode;
    ADAPTER_RESOLVE_NEGATIVE_QUADTREE_DEPTH = config.resolve_negative_depth;
    QUADTREE_FACE_QUALITY_THRESHOLD = config.face_quality_threshold;
    QUADTREE_LOW_QUALITY_H_FACTOR = config.low_quality_h_factor;
    TEMPLATE_POOR_SCORE_THRESHOLD = config.template_poor_score_threshold;
  };
  const auto equal = [&](const QuadtreeControlsConfig& a, const QuadtreeControlsConfig& b) {
    for (auto field : doubles)
      if (std::memcmp(&(a.*field), &(b.*field), sizeof(double)) != 0)
        return false;
    for (auto field : integers)
      if (a.*field != b.*field)
        return false;
    return true;
  };
  const auto depths = [](const GeneratorAdaptive& generator) {
    return std::array<int, 7>{{DomainCandidateFixture::EstimateTreeDepth(generator, -1.0, 0),
                               DomainCandidateFixture::EstimateTreeDepth(generator, 0.1, 1),
                               DomainCandidateFixture::EstimateTreeDepth(generator, 0.7, 2),
                               DomainCandidateFixture::ResolveTreeDepth(generator, 99, 1),
                               DomainCandidateFixture::ResolveTreeDepth(generator, -1, 1),
                               DomainCandidateFixture::ResolveTreeDepth(generator, -1, 2),
                               DomainCandidateFixture::ResolveTreeDepth(generator, 0, 2)}};
  };
  const auto observe = [](Par2DJMesh::AFT::Quadtree& tree) {
    using Par2DJMesh::Basics::Vertex;
    using Par2DJMesh::Basics::Face;
    Vertex minimum(0.0, 0.0), maximum(1.0, 1.0);
    Vertex a(0.0, 0.0), b(1.0, 0.0), c(0.01, 0.001);
    Face face(&a, &b, &c, 1);
    struct Detach {
      Face& face;
      ~Detach() { face.DetachVertices(); }
    } detach{face};
    Par2DJMesh::AFT::QuadtreeCell cell(1, &tree, &minimum, &maximum);
    face.h = 1.4;
    tree.ResetTemplateStats();
    const bool subdivide = cell.shouldSubdivide(&face);
    tree.RecordTemplateChoice(1, 0.3);
    return std::array<unsigned long long, 3>{{subdivide ? 1ULL : 0ULL,
                                              tree.GetTemplateStats().low_quality_subdivide_hits,
                                              tree.GetTemplateStats().low_score_templates}};
  };
  std::array<QuadtreeControlsConfig, 3> cases{};
  cases[1].cap_mode = 1;
  cases[1].depth_step1 = 3;
  cases[1].depth_stepn = 7;
  cases[1].min_h_scale = 0.75;
  cases[1].face_quality_threshold = 0.4;
  cases[1].low_quality_h_factor = 0.5;
  cases[1].template_poor_score_threshold = 0.45;
  cases[2].cap_mode = 1;
  cases[2].depth_step1 = 40;
  cases[2].depth_stepn = -2;
  cases[2].resolve_negative_depth = 0;
  cases[2].saturation_mode = cases[2].hard_saturation_mode = 1;
  cases[2].saturation_h_scale = 1.3;
  cases[2].face_quality_threshold = 0.1;
  cases[2].low_quality_h_factor = 0.8;
  cases[2].template_poor_score_threshold = 0.2;
  for (const auto& value : cases) {
    apply(value);
    const auto expected = legacy.BuildQuadtreeRuntime();
    const auto expected_depths = depths(legacy);
    Par2DJMesh::AFT::Quadtree reference;
    const auto expected_stats = observe(reference);
    std::unique_ptr<GeneratorAdaptive> owned;
    {
      apmesh::application::RuntimeConfig config;
      config.patch_quadtree_depth_step1 = value.depth_step1;
      config.patch_quadtree_depth_stepn = value.depth_stepn;
      config.patch_quadtree_min_h_scale = value.min_h_scale;
      config.adapter_resolve_negative_quadtree_depth = value.resolve_negative_depth;
      config.quadtree_face_quality_threshold = value.face_quality_threshold;
      config.quadtree_low_quality_h_factor = value.low_quality_h_factor;
      auto source = apmesh::application::MakeGenerationContext(config);
      config.patch_quadtree_depth_step1 = 22;
      owned = std::make_unique<GeneratorAdaptive>(source);
      source.quadtree.reset();
    }
    auto foreign = value;
    foreign.cap_mode = 1 - value.cap_mode;
    foreign.depth_step1 = 1;
    foreign.depth_stepn = 2;
    foreign.face_quality_threshold = value.face_quality_threshold > 0.0 ? 0.0 : 1.0;
    foreign.low_quality_h_factor = value.low_quality_h_factor < 1.0 ? 1.0 : 0.25;
    foreign.template_poor_score_threshold = value.template_poor_score_threshold > 0.0 ? 0.0 : 0.8;
    apply(foreign);
    Par2DJMesh::AFT::Quadtree captured, foreign_tree;
    DomainCandidateFixture::ConfigureTree(*owned, captured);
    if (!equal(expected, owned->BuildQuadtreeRuntime()) ||
        !equal(foreign, identity_only.BuildQuadtreeRuntime()) ||
        expected_depths != depths(*owned) || expected_stats != observe(captured) ||
        expected_stats == observe(foreign_tree))
      throw std::runtime_error("Quadtree ownership, depth or native quality controls changed");
    DomainCandidateFixture::QuadtreeCap(*owned);
    auto intermediate = value;
    intermediate.cap_mode = 1;
    if (!equal(intermediate, owned->BuildQuadtreeRuntime()))
      throw std::runtime_error("Quadtree cap update changed other controls");
    DomainCandidateFixture::QuadtreeQuality(*owned);
    if (!equal(foreign, legacy.BuildQuadtreeRuntime()) ||
        !equal(value, *owned->GetGenerationContext()->quadtree))
      throw std::runtime_error("Owned quadtree updates changed raw configuration or globals");
    apply(value);
    DomainCandidateFixture::QuadtreeCap(legacy);
    DomainCandidateFixture::QuadtreeQuality(legacy);
    const auto stable = legacy.BuildQuadtreeRuntime();
    Par2DJMesh::AFT::Quadtree stable_reference;
    const auto stable_stats = observe(stable_reference);
    DomainCandidateFixture::ConfigureTree(*owned, captured);
    if (!equal(stable, owned->BuildQuadtreeRuntime()) || depths(legacy) != depths(*owned) ||
        stable_stats != observe(captured))
      throw std::runtime_error("Adapter lost effective quadtree state or quality snapshot");
    apply(value);
    DomainCandidateFixture::QuadtreeCap(identity_only);
    DomainCandidateFixture::QuadtreeQuality(identity_only);
    if (!equal(stable, legacy.BuildQuadtreeRuntime()))
      throw std::runtime_error("Legacy quadtree adjustments stopped changing global state");
    owned.reset();
    apply(foreign);
    if (stable_stats != observe(captured))
      throw std::runtime_error("Quadtree quality controls did not outlive the generator");
  }
  apply(saved);
  std::cout << "quadtree_context cases=3 scalar_bits=27 depths=42 quality=9 "
               "retired=3 legacy=2\n";
}
#endif

int main(int argc, char* argv[]) {
#if defined(AP_MESH_DOMAIN_FAILURE_WRAP)
  if (argc == 2 && std::string(argv[1]) == "--accepted-root-contracts")
    return accepted_root_test::Run(false);
  if (argc == 2 && std::string(argv[1]) == "--accepted-root-release-control")
    return accepted_root_test::Run(true);
  if (argc == 2 && std::string(argv[1]) == "--candidate-snapshot-contracts")
    return DomainCandidateFixture::RunSnapshots();
  if (argc == 2 && std::string(argv[1]) == "--typed-domain-contracts")
    return typed_domain_test::RunTypes();
  if (argc == 4 && std::string(argv[1]) == "--typed-domain-library-config")
    return typed_domain_test::RunLibrary(argv[2], std::stoi(argv[3]));
  if (argc == 4 && std::string(argv[1]) == "--typed-domain-cli-config") {
    typed_domain_test::Prepare(std::stoi(argv[3]));
    char config_flag[] = "--config";
    char* forwarded[] = {argv[0], config_flag, argv[2]};
    const int code = apmesh::application::RunApplication(3, forwarded);
    std::fprintf(stderr, "Typed CLI unwind allocations=%d\n",
                 domain_candidate_test::state.unwind_attempts);
    return code;
  }
  if (argc == 2 && std::string(argv[1]) == "--domain-observer-contracts")
    return domain_observer_test::RunHelpers();
  if (argc == 4 && std::string(argv[1]) == "--domain-observer-config")
    return domain_observer_test::RunFailure(argv[2], std::stoi(argv[3]));
  if (argc == 2 && std::string(argv[1]) == "--domain-candidate-contracts")
    return DomainCandidateFixture::Run(false);
  if (argc == 2 && std::string(argv[1]) == "--domain-candidate-release-control")
    return DomainCandidateFixture::Run(true);
  if (argc == 3 && std::string(argv[1]) == "--domain-failure-config") {
    inject_domain_failure = true;
    char config_flag[] = "--config";
    char* forwarded[] = {argv[0], config_flag, argv[2]};
    return apmesh::application::RunApplication(3, forwarded);
  }
#endif
  if (argc == 3) {
#if defined(_WIN32)
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);
#endif
    const std::string mode(argv[1]);
    const std::filesystem::path output = std::filesystem::absolute(argv[2]);
    if (!std::filesystem::create_directories(output))
      throw std::runtime_error("Output directory already exists");
    std::filesystem::current_path(output);
    if (mode == "null-geometry" || mode == "null-mesh" || mode == "null-both")
      CheckDomainInputs(mode);
    else if (mode == "curved" || mode == "planar")
      WriteCurvatureControl(output, mode == "curved");
    else
      throw std::runtime_error("Unknown generator diagnostic control");
    return 0;
  }
  if (argc != 2)
    throw std::runtime_error("Expected a fresh output directory");
  const std::filesystem::path output(argv[1]);
  if (!std::filesystem::create_directories(output))
    throw std::runtime_error("Output directory already exists");
  CheckGenerationContexts(output);
  CheckGenerationRequests(output);
  CheckAdaptivePolicyContexts();
#if defined(AP_MESH_DOMAIN_FAILURE_WRAP)
  CheckStopRetryContexts();
  CheckAdaptationContexts();
  CheckElementBudgetContexts();
  CheckCurveControlsContexts();
  CheckQuadtreeControlsContexts();
#endif
  NAME_MODEL = (output / "attempt").generic_string();
  NUMBER_PROCESS.clear();
  GeneratorAdaptive generator;
  // Accepted steps are 0, 1 and 4. Steps 2, 3 and 5 are rejected candidates.
  // The last case represents rejection before curvature evaluation.
  const std::array<Attempt, 6> attempts{{
      {2, {10, 10, 10, 2, 0, 1, 0, 6, 0, 0, .8, .2}},
      {4, {8, 10, 10, 2, 1, 2, .25, 9, 3, 0, .6, .15}},
      {6, {12, 8, 10, 4, -2, 1.5, -.5, 15, 3, 1, .3, .075}},
      {8, {9, 8, 10, 4, -.25, 2, -.125, 21, 3, 2, .15, .0375}},
      {5, {4, 8, 10, 4, 4, 1.25, .75, 12, 3, 1, .4, .1}},
      {7, {6, 4, 10, 5, -1, 1.4, -.25, 0, 0, 3, .1, .025}},
  }};
  for (unsigned step = 0; step < attempts.size(); ++step) {
    auto mesh = MakeMesh(attempts[step].elements);
    generator.WriteQualityMesh(mesh.get(), static_cast<int>(step), attempts[step].metrics);
  }
  NAME_MODEL = (output / "zero").generic_string();
  auto mesh = MakeMesh(1);
  const GeneratorAdaptive::MeshAttemptMetrics zero{0, 0, 0, 1, 0, 1, 0, 0, 0, 0, .5, .1};
  generator.WriteQualityMesh(mesh.get(), 0, zero);
  generator.WriteQualityMesh(mesh.get(), 1, zero);
  return 0;
}
