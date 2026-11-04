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

void CheckFindUvStatistics(const std::filesystem::path& output) {
  using apmesh::diagnostics::FindUvStatistics;
  using apmesh::diagnostics::FindUvStatisticsScope;
  struct Restore {
    unsigned int imax = I_MAX;
    unsigned long long calls = FINDUV_TOTAL_CALLS.load(), exits = FINDUV_IMAX_EXITS.load();
    std::string mode = ADAPTIVE_MODE, name = NAME_MODEL, write = WRITE_MESH;
    int steps = STEPS;
    std::streambuf* stream = std::cout.rdbuf();
    ~Restore() {
      I_MAX = imax;
      FINDUV_TOTAL_CALLS.store(calls);
      FINDUV_IMAX_EXITS.store(exits);
      ADAPTIVE_MODE = mode;
      NAME_MODEL = name;
      WRITE_MESH = write;
      STEPS = steps;
      std::cout.rdbuf(stream);
    }
  };
  std::ostringstream transcript;
  Restore restore;
  std::cout.rdbuf(transcript.rdbuf());
  const auto require = [](bool condition) {
    if (!condition)
      throw std::runtime_error("FindUV execution statistics contract failed");
  };
  const auto equal = [](FindUvStatistics a, FindUvStatistics b) {
    return a.calls == b.calls && a.imax_exits == b.imax_exits;
  };
  const auto fixture =
      std::filesystem::path(__FILE__).parent_path() / "curve_memory/data/charge_input.bp";
  Geometry geometry;
  PatchReader reader;
  reader.ReaderFilePatches(&geometry, fixture.string().c_str());
  auto& bezier = *static_cast<PatchBezier*>(geometry.GetPatch(0));
  const PointAdaptive p00(0, 0, 0), p10(1, 0, 0), p01(0, 1, 0), p11(1, 1, 0);
  const VectorAdaptive u(1, 0, 0), v(0, 1, 0), twist(0, 0, 0);
  CurveAdaptiveParametricHermite c0(p00, p10, u, u), c1(p10, p11, v, v), c2(p01, p11, u, u),
      c3(p00, p01, v, v);
  PatchHermite hermite(&c0, &c1, &c2, &c3, twist, twist, twist, twist);
  const auto invoke = [](PatchCoons& patch, bool limited) {
    I_MAX = limited ? 1U : 100000U;
    const auto uv = patch.FindUV(patch.Parameterize(limited ? 0.2 : 0.5, limited ? 0.7 : 0.5));
    std::array<unsigned long long, 2> bits{};
    const std::array<double, 2> values{std::get<0>(uv), std::get<1>(uv)};
    static_assert(sizeof(bits) == sizeof(values));
    std::memcpy(bits.data(), values.data(), sizeof(bits));
    return bits;
  };
  const auto b0 = invoke(bezier, false), b1 = invoke(bezier, true), h0 = invoke(hermite, false),
             h1 = invoke(hermite, true);
  transcript.str("");
  FINDUV_TOTAL_CALLS.store(1000);
  FINDUV_IMAX_EXITS.store(1999);
  FindUvStatistics outer, inner;
  {
    FindUvStatisticsScope outer_scope(outer);
    require(invoke(bezier, true) == b1);
    try {
      FindUvStatisticsScope inner_scope(inner);
      require(invoke(hermite, true) == h1 && invoke(bezier, false) == b0);
      throw 7;
    } catch (int value) {
      require(value == 7);
    }
    require(invoke(hermite, false) == h0);
  }
  require(equal(outer, {2, 1}) && equal(inner, {2, 1}));
  require(invoke(bezier, false) == b0 && equal(outer, {2, 1}) && equal(inner, {2, 1}));
  require(FINDUV_TOTAL_CALLS.load() == 1005 && FINDUV_IMAX_EXITS.load() == 2001);
  require(transcript.str().find("[FindUV Bezier] I_MAX") != std::string::npos &&
          transcript.str().find("[FindUV Hermite] I_MAX") == std::string::npos);

  I_MAX = restore.imax;
  ADAPTIVE_MODE = "legacy";
  STEPS = 0;
  WRITE_MESH = "h";
  NAME_MODEL = (output / "finduv-first").generic_string();
  Timer timer;
  GeneratorAdaptive first, second;
  require(equal(first.GetFindUvStatistics(), {}) && equal(second.GetFindUvStatistics(), {}));
  auto before_calls = FINDUV_TOTAL_CALLS.load(), before_exits = FINDUV_IMAX_EXITS.load();
  require(first.Execute(apmesh::application::GenerationRequest{1, 1, fixture.generic_string()},
                        &timer) == 0);
  const auto first_result = first.GetFindUvStatistics();
  require(first_result.calls > 0 &&
          first_result.calls == FINDUV_TOTAL_CALLS.load() - before_calls &&
          first_result.imax_exits == FINDUV_IMAX_EXITS.load() - before_exits);
  FINDUV_TOTAL_CALLS.fetch_add(31);
  FINDUV_IMAX_EXITS.fetch_add(7);
  NAME_MODEL = (output / "finduv-second").generic_string();
  char program[] = "finduv", processes[] = "1", threads[] = "1";
  std::string input = fixture.generic_string();
  char* arguments[] = {program, processes, threads, input.data(), nullptr};
  before_calls = FINDUV_TOTAL_CALLS.load();
  before_exits = FINDUV_IMAX_EXITS.load();
  require(second.Execute(arguments, &timer) == 0);
  const auto second_result = second.GetFindUvStatistics();
  require(second_result.calls > 0 &&
          second_result.calls == FINDUV_TOTAL_CALLS.load() - before_calls &&
          second_result.imax_exits == FINDUV_IMAX_EXITS.load() - before_exits &&
          equal(first.GetFindUvStatistics(), first_result));
  const auto missing = (output / "finduv-absent.bp").generic_string();
  require(!std::filesystem::exists(missing));
  FindUvStatistics preceding;
  {
    FindUvStatisticsScope preceding_scope(preceding);
    bool caught = false;
    try {
      first.Execute(apmesh::application::GenerationRequest{1, 1, missing}, &timer);
    } catch (const std::runtime_error& error) {
      caught = error.what() == "Cannot open model input: " + missing;
    }
    require(caught && equal(first.GetFindUvStatistics(), {}));
    require(invoke(bezier, false) == b0 && equal(preceding, {1, 0}));
  }
  require(equal(second.GetFindUvStatistics(), second_result));
  std::cout.rdbuf(restore.stream);
  std::cout << "finduv_statistics patches=2 nested=2 unwind=2 "
               "executions=2 reset=1 legacy=1 scalar_bits=10\n";
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

void CheckSerialFlowContexts(const std::filesystem::path& output) {
  using apmesh::application::SerialFlowConfig;
  GeneratorAdaptive legacy;
  GeneratorAdaptive identity_only({"unused", "unused", "", ""});
  const auto saved = legacy.BuildSerialFlowRuntime();
  const auto apply = [](const SerialFlowConfig& config) {
    ENABLE_SHARED_CURVE_SYNC = config.shared_curve_sync;
    ENABLE_HYBRID_RECONSTRUCTION = config.hybrid_reconstruction;
    WRITE_RUNTIME_SUMMARY = config.write_runtime_summary;
    WRITE_ADAPTATION_DEBUG = config.write_adaptation_debug;
    USE_TEMPLATE = config.template_mode;
  };
  const auto equal = [](const SerialFlowConfig& a, const SerialFlowConfig& b) {
    return a.shared_curve_sync == b.shared_curve_sync &&
           a.hybrid_reconstruction == b.hybrid_reconstruction &&
           a.write_runtime_summary == b.write_runtime_summary &&
           a.write_adaptation_debug == b.write_adaptation_debug &&
           a.template_mode == b.template_mode;
  };
  const auto observe_sync = [](GeneratorAdaptive& generator, Geometry& geometry) {
    Models3d models;
    models.ModelDoisPatchesPlanosCurva(&geometry);
    unsigned before_shared = 0;
    for (unsigned i = 0; i < geometry.GetNumberCurves(); ++i)
      before_shared += geometry.GetCurve(i)->GetNumBerPatches() > 1U;
    if (before_shared == 0)
      throw std::runtime_error("Serial flow fixture has no shared native curve");
    DomainCandidateFixture::ConfigureSynchronization(generator, geometry);
    unsigned after_shared = 0;
    for (unsigned i = 0; i < geometry.GetNumberCurves(); ++i)
      after_shared += geometry.GetCurve(i)->GetNumBerPatches() > 1U;
    return std::array<unsigned, 2>{{geometry.GetNumberCurves(), after_shared}};
  };
  const auto report_has_prefix = [](const std::string& path, const std::string& prefix) {
    std::ifstream file(path);
    std::string line;
    while (std::getline(file, line))
      if (line.rfind(prefix, 0) == 0)
        return true;
    return false;
  };
  const std::array<SerialFlowConfig, 4> cases{{{1, 1, 1, 1, "y"},
                                               {0, 0, 0, 0, "n"},
                                               {0, 1, 9, 0, ""},
                                               {1, 9, 0, 9, std::string(192, 'x')}}};
  unsigned index = 0;
  for (const auto& value : cases) {
    apply(value);
    Geometry reference_geometry;
    const auto expected_sync = observe_sync(legacy, reference_geometry);
    const auto foreign = SerialFlowConfig{
        value.shared_curve_sync == 0 ? 1 : 0, value.hybrid_reconstruction == 0 ? 1 : 0,
        value.write_runtime_summary == 0 ? 1 : 0, value.write_adaptation_debug == 0 ? 1 : 0,
        value.template_mode == "y" ? "n" : "y"};
    const std::string prefix =
        (output / ("serial_flow_" + std::to_string(index++))).generic_string();
    std::unique_ptr<GeneratorAdaptive> owned;
    {
      auto captured =
          apmesh::application::MakeGenerationContext(apmesh::application::RuntimeConfig{});
      if (!equal(value, *captured.serial_flow))
        throw std::runtime_error("Serial flow factory changed already-applied controls");
      apmesh::application::GenerationContext source{"unused", prefix, "", ""};
      source.serial_flow = captured.serial_flow;
      owned = std::make_unique<GeneratorAdaptive>(source);
      source.serial_flow = captured.serial_flow = foreign;
    }
    apply(foreign);
    Geometry owned_geometry, foreign_geometry;
    const auto actual_sync = observe_sync(*owned, owned_geometry);
    const auto foreign_sync = observe_sync(legacy, foreign_geometry);
    if (!equal(value, owned->BuildSerialFlowRuntime()) ||
        !equal(foreign, legacy.BuildSerialFlowRuntime()) ||
        !equal(foreign, identity_only.BuildSerialFlowRuntime()) ||
        DomainCandidateFixture::AdapterDebugMode(*owned) != value.write_adaptation_debug ||
        actual_sync != expected_sync || actual_sync == foreign_sync ||
        (value.shared_curve_sync == 0 ? actual_sync[1] != 0 : actual_sync[1] == 0))
      throw std::runtime_error(
          "Serial flow ownership, debug binding or native synchronization failed");
    Par2DJMesh::AFT::AdvancingFront front, unconfigured;
    DomainCandidateFixture::ConfigureAft(*owned, front);
    if (front.TemplateMode() != value.template_mode ||
        unconfigured.TemplateMode() != foreign.template_mode ||
        ((front.TemplateMode() == std::string("y")) != (value.template_mode == std::string("y"))))
      throw std::runtime_error("Template mode capture or exact literal gate changed");
    Timer timer(1, 1, 12);
    owned->WriteRuntimeSummary(&timer);
    owned->WriteAcceptanceLog(2, 0.25, GeneratorAdaptive::MeshQualityStats{}, 0.1, 1.5, true);
    owned->WriteCompatibilitySummary(&owned_geometry);
    const std::string runtime = prefix + "_runtime_summary.csv";
    const std::string debug = prefix + "_passo_2_acceptance_accepted.log";
    const std::string metadata = prefix + "," + std::to_string(value.shared_curve_sync) + "," +
                                 std::to_string(value.hybrid_reconstruction) + ",";
    if (std::filesystem::exists(runtime) != (value.write_runtime_summary != 0) ||
        std::filesystem::exists(debug) != (value.write_adaptation_debug != 0) ||
        !report_has_prefix(prefix + "_compatibility_summary.csv", metadata) ||
        (value.write_runtime_summary != 0 && !report_has_prefix(runtime, metadata)) ||
        !equal(value, *owned->GetGenerationContext()->serial_flow) ||
        !equal(foreign, legacy.BuildSerialFlowRuntime()))
      throw std::runtime_error("Serial flow diagnostic gates/metadata or immutable state changed");
    owned.reset();
    USE_TEMPLATE = value.template_mode == "y" ? "n" : "y";
    if (front.TemplateMode() != value.template_mode || unconfigured.TemplateMode() != USE_TEMPLATE)
      throw std::runtime_error(
          "Front template mode expired with its generator or legacy stopped following globals");
  }
  apply(saved);
  std::cout << "serial_flow_context cases=4 sync=4 diagnostics=4 templates=4 retired=4 legacy=2\n";
}

class AftContextProbe : public Par2DJMesh::AFT::AdvancingFront {
  using Vertex = Par2DJMesh::Basics::Vertex;
  using Face = Par2DJMesh::Basics::Face;
  std::array<Vertex, 4> corners_{
      {Vertex(0.0, 0.0), Vertex(1.0, 0.0), Vertex(1.0, 1.0), Vertex(0.0, 1.0)}};
  std::unique_ptr<Vertex> center_ = std::make_unique<Vertex>(0.05, 0.25);

public:
  explicit AftContextProbe(const std::array<double, 3>& inputs)
      : AdvancingFront(inputs[0], TOLERANCE_AFT, inputs[1], inputs[2]) {
    struct DetachDelete {
      void operator()(Face* face) const noexcept {
        face->DetachVertices();
        delete face;
      }
    };
    for (unsigned i = 0; i < 4; ++i) {
      std::unique_ptr<Face, DetachDelete> face(
          new Face(&corners_[i], &corners_[(i + 1) % 4], center_.get(), i + 1));
      mesh.push_back(face.get());
      face.release();
    }
    innerVertices.push_back(center_.get());
  }
  ~AftContextProbe() override {
    for (auto* face : mesh) {
      face->DetachVertices();
      delete face;
    }
    mesh.clear();
    innerVertices.clear();
  }
  double SmoothingFactor() const { return phi; }
  std::array<double, 4> Observe() {
    center_->setPosition(0.05, 0.25);
    ResetRunStats();
    bool changed = false;
    if (!poorRegionShapeSmoothing(changed))
      throw std::runtime_error("Native AFT poor-region smoothing failed");
    const auto& stats = GetRunStats();
    if (changed != (stats.postprocess_vertices_moved > 0))
      throw std::runtime_error("Native AFT moved-vertex oracle disagrees");
    return {{center_->getX(), center_->getY(),
             static_cast<double>(stats.postprocess_vertices_considered),
             static_cast<double>(stats.postprocess_vertices_moved)}};
  }
};

void CheckAftContexts() {
  using apmesh::application::AftConfig;
  const std::array<double AftConfig::*, 5> doubles{
      {&AftConfig::ratio, &AftConfig::smoothing_iterations, &AftConfig::smoothing_factor,
       &AftConfig::postprocess_quality_threshold, &AftConfig::postprocess_blend}};
  GeneratorAdaptive legacy;
  GeneratorAdaptive identity_only({"unused", "unused", "", ""});
  const auto saved = legacy.BuildAftRuntime();
  const auto apply = [](const AftConfig& config) {
    RATIO_AFT = config.ratio;
    SMOOTHING_LAPLACIAN_NUMBER = config.smoothing_iterations;
    SMOOTHING_LAPLACIAN_FACTOR = config.smoothing_factor;
    AFT_LOCAL_POSTPROCESS_PASSES = config.postprocess_passes;
    AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD = config.postprocess_quality_threshold;
    AFT_LOCAL_POSTPROCESS_BLEND = config.postprocess_blend;
  };
  const auto equal = [&](const AftConfig& a, const AftConfig& b) {
    for (auto field : doubles)
      if (std::memcmp(&(a.*field), &(b.*field), sizeof(double)) != 0)
        return false;
    return a.postprocess_passes == b.postprocess_passes;
  };
  const auto same = [](const std::array<double, 4>& a, const std::array<double, 4>& b) {
    return std::memcmp(a.data(), b.data(), a.size() * sizeof(double)) == 0;
  };
  const auto make_front = [](const GeneratorAdaptive& generator) {
    auto front =
        std::make_unique<AftContextProbe>(DomainCandidateFixture::AftConstructorInputs(generator));
    DomainCandidateFixture::ConfigureAft(generator, *front);
    return front;
  };
  const auto check_front = [](AftContextProbe& front, const AftConfig& config) {
    const double factor = front.getQuadtree()->getFactor();
    const double phi = front.SmoothingFactor();
    const double threshold = front.PostprocessQualityThreshold();
    const double blend = front.PostprocessBlend();
    if (std::memcmp(&factor, &config.ratio, sizeof(double)) != 0 ||
        std::memcmp(&phi, &config.smoothing_factor, sizeof(double)) != 0 ||
        front.getNumImproves() != static_cast<unsigned int>(config.smoothing_iterations) ||
        front.PostprocessPasses() != config.postprocess_passes ||
        std::memcmp(&threshold, &config.postprocess_quality_threshold, sizeof(double)) != 0 ||
        std::memcmp(&blend, &config.postprocess_blend, sizeof(double)) != 0)
      throw std::runtime_error("AFT constructor conversion or postprocess binding changed");
  };
  std::array<AftConfig, 3> cases{};
  cases[1] = {0.85, 6.75, 0.4, 1, 0.8, 0.25};
  cases[2] = {1.1, 2.25, 0.6, 3, 0.6, 0.5};
  const AftConfig foreign{1.3, 5.0, 0.2, 0, 0.0, 0.0};
  unsigned raw_negative_differences = 0;
  for (const auto& value : cases) {
    apply(value);
    const auto expected = legacy.BuildAftRuntime();
    auto reference = make_front(legacy);
    const auto expected_post = reference->Observe();
    std::unique_ptr<GeneratorAdaptive> owned;
    {
      auto captured =
          apmesh::application::MakeGenerationContext(apmesh::application::RuntimeConfig{});
      if (!equal(expected, *captured.aft))
        throw std::runtime_error("AFT factory changed already-applied process values");
      apmesh::application::GenerationContext source{"unused", "unused", "", ""};
      source.aft = captured.aft;
      owned = std::make_unique<GeneratorAdaptive>(source);
      source.aft = captured.aft = foreign;
    }
    apply(foreign);
    auto front = make_front(*owned);
    check_front(*front, value);
    if (!equal(expected, owned->BuildAftRuntime()) || !equal(foreign, legacy.BuildAftRuntime()) ||
        !equal(foreign, identity_only.BuildAftRuntime()) || !same(expected_post, front->Observe()))
      throw std::runtime_error("AFT ownership or raw native smoothing differential failed");
    auto foreign_front = make_front(legacy);
    raw_negative_differences += !same(expected_post, foreign_front->Observe());
    DomainCandidateFixture::StableAft(*owned);
    if (!equal(value, *owned->GetGenerationContext()->aft) ||
        !equal(foreign, legacy.BuildAftRuntime()))
      throw std::runtime_error("Owned AFT update changed raw settings or process state");
    auto stable_front = make_front(*owned);
    apply(value);
    DomainCandidateFixture::StableAft(legacy);
    const auto stable = legacy.BuildAftRuntime();
    auto stable_reference = make_front(legacy);
    const auto stable_post = stable_reference->Observe();
    if (!equal(stable, owned->BuildAftRuntime()) || !same(stable_post, stable_front->Observe()) ||
        stable_post[3] <= 0.0)
      throw std::runtime_error(
          "AFT stable values, native differential or positive movement failed");
    check_front(*stable_front, stable);
    apply(foreign);
    owned.reset();
    check_front(*stable_front, stable);
    if (!same(stable_post, stable_front->Observe()))
      throw std::runtime_error("AFT value-owned settings expired with the generator");
    apply(value);
    DomainCandidateFixture::StableAft(identity_only);
    if (!equal(stable, legacy.BuildAftRuntime()))
      throw std::runtime_error("Legacy AFT update stopped writing process state");
  }
  apply(saved);
  if (raw_negative_differences != 2)
    throw std::runtime_error("AFT foreign-global control did not expose both active cases");
  std::cout << "aft_context cases=3 scalar_bits=15 post_bits=36 retired=3 legacy=2\n";
}

void CheckAcceptanceContexts(const std::filesystem::path& output) {
  using apmesh::application::AcceptanceConfig;
  const std::array<double AcceptanceConfig::*, 22> doubles{
      {&AcceptanceConfig::error_weight,
       &AcceptanceConfig::quality_min_weight,
       &AcceptanceConfig::poor_ratio_weight,
       &AcceptanceConfig::growth_weight,
       &AcceptanceConfig::step1_growth_weight,
       &AcceptanceConfig::stepn_growth_weight,
       &AcceptanceConfig::step1_max_growth_soft,
       &AcceptanceConfig::stepn_max_growth_soft,
       &AcceptanceConfig::step1_min_error_drop_abs,
       &AcceptanceConfig::step1_min_error_drop_pct,
       &AcceptanceConfig::min_score,
       &AcceptanceConfig::max_error_increase_pct,
       &AcceptanceConfig::poor_ratio_target,
       &AcceptanceConfig::small_gains_min_error_drop_abs,
       &AcceptanceConfig::small_gains_min_error_drop_per_element,
       &AcceptanceConfig::small_gains_growth_weight,
       &AcceptanceConfig::min_efficiency,
       &AcceptanceConfig::max_element_growth_soft,
       &AcceptanceConfig::quality_drop_tolerance,
       &AcceptanceConfig::target_growth_tolerance,
       &AcceptanceConfig::error_drop_min,
       &AcceptanceConfig::budget_miss_penalty}};
  const std::array<int AcceptanceConfig::*, 4> integers{
      {&AcceptanceConfig::mode, &AcceptanceConfig::growth_penalty_mode,
       &AcceptanceConfig::small_gains_mode, &AcceptanceConfig::efficiency_mode}};
  GeneratorAdaptive legacy;
  GeneratorAdaptive identity_only({"unused", "unused", "", ""});
  const auto saved = legacy.BuildAcceptanceRuntime();
  const int saved_debug = WRITE_ADAPTATION_DEBUG;
  WRITE_ADAPTATION_DEBUG = 1;
  const auto apply = [](const AcceptanceConfig& config) {
    ACCEPTANCE_MODE = config.mode;
    ACCEPTANCE_WEIGHT_ERROR = config.error_weight;
    ACCEPTANCE_WEIGHT_QUALITY_MIN = config.quality_min_weight;
    ACCEPTANCE_WEIGHT_POOR_RATIO = config.poor_ratio_weight;
    ACCEPTANCE_WEIGHT_GROWTH = config.growth_weight;
    ACCEPTANCE_STEP1_GROWTH_WEIGHT = config.step1_growth_weight;
    ACCEPTANCE_STEPN_GROWTH_WEIGHT = config.stepn_growth_weight;
    ACCEPTANCE_STEP1_MAX_GROWTH_SOFT = config.step1_max_growth_soft;
    ACCEPTANCE_STEPN_MAX_GROWTH_SOFT = config.stepn_max_growth_soft;
    ACCEPTANCE_GROWTH_PENALTY_MODE = config.growth_penalty_mode;
    ACCEPTANCE_STEP1_MIN_ERROR_DROP_ABS = config.step1_min_error_drop_abs;
    ACCEPTANCE_STEP1_MIN_ERROR_DROP_PCT = config.step1_min_error_drop_pct;
    ACCEPTANCE_MIN_SCORE = config.min_score;
    ACCEPTANCE_MAX_ERROR_INCREASE_PCT = config.max_error_increase_pct;
    ACCEPTANCE_POOR_RATIO_TARGET = config.poor_ratio_target;
    STEP2_ACCEPT_SMALL_GAINS_MODE = config.small_gains_mode;
    STEP2_MIN_ERROR_DROP_ABS = config.small_gains_min_error_drop_abs;
    STEP2_MIN_ERROR_DROP_PER_ELEMENT = config.small_gains_min_error_drop_per_element;
    STEP2_ACCEPTANCE_GROWTH_WEIGHT = config.small_gains_growth_weight;
    STEP_ACCEPT_EFFICIENCY_MODE = config.efficiency_mode;
    STEP_ACCEPT_MIN_EFFICIENCY = config.min_efficiency;
    STEP_ACCEPT_MAX_ELEMENT_GROWTH_SOFT = config.max_element_growth_soft;
    STEP_ACCEPT_QUALITY_DROP_TOLERANCE = config.quality_drop_tolerance;
    STEP_ACCEPT_TARGET_GROWTH_TOLERANCE = config.target_growth_tolerance;
    STEP_ACCEPT_ERROR_DROP_MIN = config.error_drop_min;
    STEP_ACCEPT_BUDGET_MISS_PENALTY = config.budget_miss_penalty;
  };
  const auto equal = [&](const AcceptanceConfig& a, const AcceptanceConfig& b) {
    for (auto field : doubles)
      if (std::memcmp(&(a.*field), &(b.*field), sizeof(double)) != 0)
        return false;
    for (auto field : integers)
      if (a.*field != b.*field)
        return false;
    return true;
  };
  const auto penalties = [](const GeneratorAdaptive& generator) {
    std::array<double, 10> result{};
    unsigned index = 0;
    for (int step : {1, 2})
      for (double growth : {0.8, 1.0, 1.5, 3.0, 8.0})
        result[index++] = DomainCandidateFixture::AcceptanceGrowthPenalty(generator, growth, step);
    return result;
  };
  const auto same = [](const std::array<double, 10>& a, const std::array<double, 10>& b) {
    return std::memcmp(a.data(), b.data(), a.size() * sizeof(double)) == 0;
  };
  std::array<AcceptanceConfig, 3> cases{};
  cases[1].mode = cases[1].growth_penalty_mode = cases[1].small_gains_mode = 1;
  cases[1].step1_growth_weight = 0.5;
  cases[1].stepn_growth_weight = 0.25;
  cases[1].step1_max_growth_soft = 2.0;
  cases[1].stepn_max_growth_soft = 3.0;
  cases[1].min_score = 0.07;
  cases[1].min_efficiency = 0.002;
  cases[2].mode = cases[2].growth_penalty_mode = 2;
  cases[2].step1_growth_weight = 0.07;
  cases[2].stepn_growth_weight = 0.33;
  cases[2].growth_weight = -0.0;
  cases[2].efficiency_mode = 0;
  cases[2].small_gains_min_error_drop_abs = 0.003;
  cases[2].target_growth_tolerance = 0.15;
  AcceptanceConfig foreign;
  for (std::size_t i = 0; i < doubles.size(); ++i)
    foreign.*doubles[i] = 0.5 + static_cast<double>(i) * 0.01;
  for (auto field : integers)
    foreign.*field = 9;
  foreign.growth_penalty_mode = 1;
  foreign.step1_max_growth_soft = foreign.stepn_max_growth_soft = 1.0;
  unsigned case_index = 0;
  for (const auto& value : cases) {
    apply(value);
    const auto expected = legacy.BuildAcceptanceRuntime();
    const auto expected_penalties = penalties(legacy);
    const std::string prefix =
        (output / ("acceptance_context_" + std::to_string(case_index++))).generic_string();
    std::unique_ptr<GeneratorAdaptive> owned;
    {
      auto captured =
          apmesh::application::MakeGenerationContext(apmesh::application::RuntimeConfig{});
      if (!equal(expected, *captured.acceptance))
        throw std::runtime_error("Acceptance factory changed raw process values");
      apmesh::application::GenerationContext source{"unused", prefix, "", ""};
      source.acceptance = captured.acceptance;
      owned = std::make_unique<GeneratorAdaptive>(source);
      source.acceptance = captured.acceptance = foreign;
    }
    apply(foreign);
    if (!equal(foreign, legacy.BuildAcceptanceRuntime()) ||
        !equal(foreign, identity_only.BuildAcceptanceRuntime()) ||
        !equal(expected, owned->BuildAcceptanceRuntime()) ||
        !same(expected_penalties, penalties(*owned)) || same(expected_penalties, penalties(legacy)))
      throw std::runtime_error("Acceptance ownership or native growth differential failed");
    for (bool accepted : {false, true}) {
      owned->WriteAcceptanceLog(2, 0.25, GeneratorAdaptive::MeshQualityStats{}, 0.1, 1.5, accepted);
      const std::string filename =
          prefix + "_passo_2_acceptance_" + (accepted ? "accepted" : "rejected") + ".log";
      std::ifstream file(filename);
      std::string line;
      bool found = false;
      while (std::getline(file, line))
        found = found || line == "acceptance_mode=" + std::to_string(value.mode);
      if (!found)
        throw std::runtime_error("Acceptance report used foreign process mode");
    }
    if (!equal(value, *owned->GetGenerationContext()->acceptance) ||
        !equal(foreign, legacy.BuildAcceptanceRuntime()))
      throw std::runtime_error("Acceptance evaluation changed raw context or process state");
  }
  apply(saved);
  WRITE_ADAPTATION_DEBUG = saved_debug;
  std::cout << "acceptance_context cases=3 scalar_bits=66 growth_bits=30 logs=6 legacy=2\n";
}

void CheckPatchConsistencyContexts() {
  using apmesh::application::PatchConsistencyConfig;
  const std::array<double PatchConsistencyConfig::*, 11> doubles{
      {&PatchConsistencyConfig::area_tolerance, &PatchConsistencyConfig::error_tolerance,
       &PatchConsistencyConfig::curvature_tolerance, &PatchConsistencyConfig::quality_tolerance,
       &PatchConsistencyConfig::max_budget_ratio_step2,
       &PatchConsistencyConfig::max_budget_ratio_stepn, &PatchConsistencyConfig::min_group_share,
       &PatchConsistencyConfig::h_clamp_ratio, &PatchConsistencyConfig::step2_weight,
       &PatchConsistencyConfig::acceptance_penalty_weight,
       &PatchConsistencyConfig::acceptance_max_group_dispersion_step2}};
  const std::array<int PatchConsistencyConfig::*, 7> integers{
      {&PatchConsistencyConfig::mode, &PatchConsistencyConfig::neighbor_only,
       &PatchConsistencyConfig::depth_clamp, &PatchConsistencyConfig::group_min_patches,
       &PatchConsistencyConfig::group_neighbor_protection,
       &PatchConsistencyConfig::disable_group_coarsen_if_unbalanced,
       &PatchConsistencyConfig::acceptance_mode}};
  GeneratorAdaptive legacy;
  GeneratorAdaptive identity_only({"unused", "unused", "", ""});
  const auto saved = legacy.BuildPatchConsistencyRuntime();
  const auto apply = [](const PatchConsistencyConfig& config) {
    PATCH_CONSISTENCY_MODE = config.mode;
    PATCH_CONSISTENCY_AREA_TOL = config.area_tolerance;
    PATCH_CONSISTENCY_ERROR_TOL = config.error_tolerance;
    PATCH_CONSISTENCY_CURVATURE_TOL = config.curvature_tolerance;
    PATCH_CONSISTENCY_QUALITY_TOL = config.quality_tolerance;
    PATCH_CONSISTENCY_NEIGHBOR_ONLY = config.neighbor_only;
    PATCH_CONSISTENCY_MAX_BUDGET_RATIO_STEP2 = config.max_budget_ratio_step2;
    PATCH_CONSISTENCY_MAX_BUDGET_RATIO_STEPN = config.max_budget_ratio_stepn;
    PATCH_CONSISTENCY_MIN_GROUP_SHARE = config.min_group_share;
    PATCH_CONSISTENCY_H_CLAMP_RATIO = config.h_clamp_ratio;
    PATCH_CONSISTENCY_DEPTH_CLAMP = config.depth_clamp;
    STEP2_CONSISTENCY_WEIGHT = config.step2_weight;
    STEP2_GROUP_MIN_PATCHES = config.group_min_patches;
    STEP2_GROUP_NEIGHBOR_PROTECTION = config.group_neighbor_protection;
    STEP2_DISABLE_GROUP_COARSEN_IF_UNBALANCED = config.disable_group_coarsen_if_unbalanced;
    STEP_ACCEPT_CONSISTENCY_MODE = config.acceptance_mode;
    STEP_ACCEPT_CONSISTENCY_PENALTY_WEIGHT = config.acceptance_penalty_weight;
    STEP_ACCEPT_MAX_GROUP_DISPERSION_STEP2 = config.acceptance_max_group_dispersion_step2;
  };
  const auto equal = [&](const PatchConsistencyConfig& a, const PatchConsistencyConfig& b) {
    for (auto field : doubles)
      if (std::memcmp(&(a.*field), &(b.*field), sizeof(double)) != 0)
        return false;
    for (auto field : integers)
      if (a.*field != b.*field)
        return false;
    return true;
  };
  Geometry geometry;
  Models3d models;
  models.ModelDoisPatchesPlanosCurva(&geometry);
  if (geometry.GetNumberPatches() != 2)
    throw std::runtime_error("Consistency control requires the existing two-patch model");
  const auto observe = [&](GeneratorAdaptive& generator, bool stable) {
    std::array<double, 24> result{};
    for (int step : {2, 3}) {
      const auto values =
          DomainCandidateFixture::ConsistencyOutputs(generator, geometry, step, stable);
      std::copy(values.begin(), values.end(), result.begin() + (step - 2) * 12);
    }
    return result;
  };
  const auto same = [](const std::array<double, 24>& a, const std::array<double, 24>& b) {
    return std::memcmp(a.data(), b.data(), a.size() * sizeof(double)) == 0;
  };
  std::array<PatchConsistencyConfig, 3> cases{};
  for (auto& config : cases)
    config.area_tolerance = 1.0;
  cases[1].mode = 1;
  cases[1].max_budget_ratio_step2 = 1.2;
  cases[1].max_budget_ratio_stepn = 1.4;
  cases[1].min_group_share = 0.1;
  cases[1].h_clamp_ratio = 1.1;
  cases[1].acceptance_penalty_weight = 0.73;
  cases[2].mode = 1;
  cases[2].group_min_patches = 3;
  cases[2].depth_clamp = 0;
  cases[2].acceptance_max_group_dispersion_step2 = 0.25;
  PatchConsistencyConfig foreign;
  foreign.mode = 1;
  foreign.area_tolerance = 1.0;
  foreign.max_budget_ratio_step2 = 2.5;
  foreign.max_budget_ratio_stepn = 3.0;
  foreign.min_group_share = 0.1;
  foreign.h_clamp_ratio = 2.0;
  foreign.depth_clamp = 0;
  foreign.acceptance_mode = 9;
  foreign.step2_weight = 0.91;
  foreign.disable_group_coarsen_if_unbalanced = 0;
  for (const auto& value : cases) {
    apply(value);
    const auto expected = legacy.BuildPatchConsistencyRuntime();
    const auto expected_outputs = observe(legacy, false);
    std::unique_ptr<GeneratorAdaptive> owned;
    {
      auto captured =
          apmesh::application::MakeGenerationContext(apmesh::application::RuntimeConfig{});
      if (!equal(expected, *captured.patch_consistency))
        throw std::runtime_error("Consistency factory capture changed raw process settings");
      apmesh::application::GenerationContext source{"unused", "unused", "", ""};
      source.patch_consistency = captured.patch_consistency;
      owned = std::make_unique<GeneratorAdaptive>(source);
      source.patch_consistency = captured.patch_consistency = foreign;
    }
    apply(foreign);
    const auto foreign_outputs = observe(legacy, false);
    if (!equal(foreign, legacy.BuildPatchConsistencyRuntime()) ||
        !equal(foreign, identity_only.BuildPatchConsistencyRuntime()) ||
        !equal(expected, owned->BuildPatchConsistencyRuntime()) ||
        !same(expected_outputs, observe(*owned, false)) ||
        same(expected_outputs, foreign_outputs) || foreign_outputs[6] < 0.0 ||
        foreign_outputs[6] != foreign_outputs[7] || foreign_outputs[11] != 1.0)
      throw std::runtime_error(
          "Consistency ownership, positive grouping or native differential failed");
    auto intermediate = value;
    intermediate.mode = 1;
    DomainCandidateFixture::EnablePatchConsistency(*owned);
    if (!equal(intermediate, owned->BuildPatchConsistencyRuntime()))
      throw std::runtime_error("First consistency update changed its position or other settings");
    DomainCandidateFixture::EnableConsistencyAcceptance(*owned);
    if (!equal(value, *owned->GetGenerationContext()->patch_consistency) ||
        !equal(foreign, legacy.BuildPatchConsistencyRuntime()))
      throw std::runtime_error("Owned consistency updates changed raw settings or globals");
    apply(value);
    DomainCandidateFixture::EnablePatchConsistency(legacy);
    DomainCandidateFixture::EnableConsistencyAcceptance(legacy);
    const auto stable = legacy.BuildPatchConsistencyRuntime();
    if (!equal(stable, owned->BuildPatchConsistencyRuntime()) ||
        !same(observe(legacy, true), observe(*owned, true)))
      throw std::runtime_error("Stable consistency updates changed effective values or grouping");
    apply(value);
    DomainCandidateFixture::EnablePatchConsistency(identity_only);
    DomainCandidateFixture::EnableConsistencyAcceptance(identity_only);
    if (!equal(stable, legacy.BuildPatchConsistencyRuntime()))
      throw std::runtime_error("Legacy consistency updates stopped writing process state");
  }
  apply(saved);
  std::cout << "patch_consistency_context cases=3 scalar_bits=33 outputs=144 "
               "stable_writes=2 legacy=2\n";
}

void CheckPatchGenerationContexts() {
  using apmesh::application::PatchGenerationConfig;
  const std::array<double PatchGenerationConfig::*, 28> doubles{
      {&PatchGenerationConfig::refinement_strength,
       &PatchGenerationConfig::coarsening_strength,
       &PatchGenerationConfig::error_exponent,
       &PatchGenerationConfig::quality_weight,
       &PatchGenerationConfig::quality_target,
       &PatchGenerationConfig::quality_min_target,
       &PatchGenerationConfig::top_error_fraction,
       &PatchGenerationConfig::efficiency_weight,
       &PatchGenerationConfig::efficiency_target,
       &PatchGenerationConfig::history_blend,
       &PatchGenerationConfig::step2_refinement_scale,
       &PatchGenerationConfig::inefficient_cap,
       &PatchGenerationConfig::refinement_attenuation,
       &PatchGenerationConfig::top_error_fraction_scale,
       &PatchGenerationConfig::factor_range_shrink,
       &PatchGenerationConfig::noneligible_factor_min,
       &PatchGenerationConfig::smoothing_neighbor_weight,
       &PatchGenerationConfig::eligible_refinement_damp,
       &PatchGenerationConfig::eligible_refinement_damp_on_retry,
       &PatchGenerationConfig::eligible_elements_threshold,
       &PatchGenerationConfig::eligible_h_scale,
       &PatchGenerationConfig::micro_relaxation_scale,
       &PatchGenerationConfig::micro_max_delta_scale,
       &PatchGenerationConfig::micro_patch_refinement_scale,
       &PatchGenerationConfig::micro_factor_range_scale,
       &PatchGenerationConfig::budget_pressure_start,
       &PatchGenerationConfig::micro_h_scale,
       &PatchGenerationConfig::constrained_h_scale}};
  const std::array<int PatchGenerationConfig::*, 9> integers{
      {&PatchGenerationConfig::adaptation_mode, &PatchGenerationConfig::stepwise_mode,
       &PatchGenerationConfig::hard_spatial_filter_mode,
       &PatchGenerationConfig::top_patch_count_min, &PatchGenerationConfig::top_patch_count_max,
       &PatchGenerationConfig::noneligible_force_coarsen,
       &PatchGenerationConfig::micro_refinement_mode, &PatchGenerationConfig::control_mode,
       &PatchGenerationConfig::top_rank_only_mode}};
  GeneratorAdaptive legacy;
  GeneratorAdaptive identity_only({"unused", "unused", "", ""});
  const auto saved = legacy.BuildPatchGenerationRuntime();
  const auto apply = [](const PatchGenerationConfig& config) {
    PATCH_ADAPTATION_MODE = config.adaptation_mode;
    PATCH_REFINEMENT_STRENGTH = config.refinement_strength;
    PATCH_COARSENING_STRENGTH = config.coarsening_strength;
    PATCH_ERROR_EXPONENT = config.error_exponent;
    PATCH_QUALITY_WEIGHT = config.quality_weight;
    PATCH_QUALITY_TARGET = config.quality_target;
    PATCH_QUALITY_MIN_TARGET = config.quality_min_target;
    PATCH_TOP_ERROR_FRACTION = config.top_error_fraction;
    PATCH_EFFICIENCY_WEIGHT = config.efficiency_weight;
    PATCH_EFFICIENCY_TARGET = config.efficiency_target;
    PATCH_HISTORY_BLEND = config.history_blend;
    PATCH_STEP2_REFINEMENT_SCALE = config.step2_refinement_scale;
    PATCH_INEFFICIENT_CAP = config.inefficient_cap;
    PATCH_STEPWISE_MODE = config.stepwise_mode;
    STEP2_REFINEMENT_ATTENUATION = config.refinement_attenuation;
    STEP2_TOP_ERROR_FRACTION_SCALE = config.top_error_fraction_scale;
    STEP2_FACTOR_RANGE_SHRINK = config.factor_range_shrink;
    STEP2_HARD_SPATIAL_FILTER_MODE = config.hard_spatial_filter_mode;
    STEP2_TOP_PATCH_COUNT_MIN = config.top_patch_count_min;
    STEP2_TOP_PATCH_COUNT_MAX = config.top_patch_count_max;
    STEP2_NONELIGIBLE_FACTOR_MIN = config.noneligible_factor_min;
    STEP2_NONELIGIBLE_FORCE_COARSEN = config.noneligible_force_coarsen;
    STEP2_SMOOTHING_NEIGHBOR_WEIGHT = config.smoothing_neighbor_weight;
    STEP2_ELIGIBLE_REFINEMENT_DAMP = config.eligible_refinement_damp;
    STEP2_ELIGIBLE_REFINEMENT_DAMP_ON_RETRY = config.eligible_refinement_damp_on_retry;
    STEP2_ELIGIBLE_ELEMENTS_THRESHOLD = config.eligible_elements_threshold;
    STEP2_ELIGIBLE_H_SCALE = config.eligible_h_scale;
    STEP2_MICRO_REFINEMENT_MODE = config.micro_refinement_mode;
    STEP2_MICRO_RELAXATION_SCALE = config.micro_relaxation_scale;
    STEP2_MICRO_MAX_DELTA_SCALE = config.micro_max_delta_scale;
    STEP2_MICRO_PATCH_REFINEMENT_SCALE = config.micro_patch_refinement_scale;
    STEP2_MICRO_FACTOR_RANGE_SCALE = config.micro_factor_range_scale;
    PATCH_GENERATION_CONTROL_MODE = config.control_mode;
    PATCH_GENERATION_BUDGET_PRESSURE_START = config.budget_pressure_start;
    PATCH_GENERATION_MICRO_H_SCALE = config.micro_h_scale;
    PATCH_GENERATION_CONSTRAINED_H_SCALE = config.constrained_h_scale;
    PATCH_GENERATION_TOP_RANK_ONLY_MODE = config.top_rank_only_mode;
  };
  const auto equal = [&](const PatchGenerationConfig& a, const PatchGenerationConfig& b) {
    for (auto field : doubles)
      if (std::memcmp(&(a.*field), &(b.*field), sizeof(double)) != 0)
        return false;
    for (auto field : integers)
      if (a.*field != b.*field)
        return false;
    return true;
  };
  Geometry geometry;
  Models3d models;
  models.ModelDoisPatchesPlanosCurva(&geometry);
  if (geometry.GetNumberPatches() != 2)
    throw std::runtime_error("Patch control fixture requires two existing native patches");
  const auto observe = [&](GeneratorAdaptive& generator, bool stable) {
    std::vector<double> result;
    for (int step : {1, 2}) {
      auto factors = DomainCandidateFixture::PatchFactors(generator, geometry, step, stable);
      result.insert(result.end(), factors.begin(), factors.end());
    }
    auto smooth = DomainCandidateFixture::SmoothPatchFactors(generator, geometry);
    result.insert(result.end(), smooth.begin(), smooth.end());
    return result;
  };
  const auto same = [](const std::vector<double>& a, const std::vector<double>& b) {
    return a.size() == 6 && b.size() == 6 &&
           std::memcmp(a.data(), b.data(), a.size() * sizeof(double)) == 0;
  };
  std::array<PatchGenerationConfig, 3> cases{};
  cases[1].adaptation_mode = 1;
  cases[1].refinement_strength = 0.31;
  cases[1].coarsening_strength = 0.07;
  cases[1].hard_spatial_filter_mode = 1;
  cases[1].top_patch_count_min = cases[1].top_patch_count_max = 1;
  cases[1].noneligible_factor_min = 1.04;
  cases[1].smoothing_neighbor_weight = 0.25;
  cases[1].micro_refinement_mode = 1;
  cases[1].eligible_refinement_damp = 0.37;
  cases[2].refinement_strength = 0.42;
  cases[2].coarsening_strength = 0.18;
  cases[2].quality_weight = 0.65;
  cases[2].top_error_fraction = 0.5;
  cases[2].stepwise_mode = 1;
  cases[2].noneligible_force_coarsen = 0;
  PatchGenerationConfig foreign;
  for (std::size_t i = 0; i < doubles.size(); ++i)
    foreign.*doubles[i] = 0.5 + static_cast<double>(i) * 0.01;
  for (auto field : integers)
    foreign.*field = 0;
  foreign.adaptation_mode = 1;
  foreign.top_patch_count_min = 1;
  foreign.top_patch_count_max = 2;
  unsigned differentiated = 0;
  for (const auto& value : cases) {
    apply(value);
    const auto expected = legacy.BuildPatchGenerationRuntime();
    const auto expected_outputs = observe(legacy, false);
    std::unique_ptr<GeneratorAdaptive> owned;
    {
      apmesh::application::RuntimeConfig config;
      config.patch_refinement_strength = value.refinement_strength;
      config.patch_coarsening_strength = value.coarsening_strength;
      config.step2_eligible_refinement_damp = value.eligible_refinement_damp;
      auto captured = apmesh::application::MakeGenerationContext(config);
      if (!equal(expected, *captured.patch_generation))
        throw std::runtime_error("Patch generation factory capture changed raw values");
      apmesh::application::GenerationContext source{"unused", "unused", "", ""};
      source.patch_generation = captured.patch_generation;
      owned = std::make_unique<GeneratorAdaptive>(source);
      source.patch_generation = foreign;
      captured.patch_generation = foreign;
      config.patch_refinement_strength = 9.0;
    }
    apply(foreign);
    if (!equal(foreign, legacy.BuildPatchGenerationRuntime()) ||
        !equal(foreign, identity_only.BuildPatchGenerationRuntime()) ||
        !equal(expected, owned->BuildPatchGenerationRuntime()) ||
        !same(expected_outputs, observe(*owned, false)))
      throw std::runtime_error("Patch generation ownership or native factor differential failed");
    differentiated += !same(expected_outputs, observe(legacy, false));
    DomainCandidateFixture::EnablePatchGeneration(*owned);
    if (!equal(value, *owned->GetGenerationContext()->patch_generation) ||
        !equal(foreign, legacy.BuildPatchGenerationRuntime()))
      throw std::runtime_error("Patch overrides changed raw settings or process globals");
    DomainCandidateFixture::EnablePatchRefinementModes(*owned);
    if (!equal(value, *owned->GetGenerationContext()->patch_generation) ||
        !equal(foreign, legacy.BuildPatchGenerationRuntime()))
      throw std::runtime_error("Patch overrides changed raw settings or process globals");
    DomainCandidateFixture::ApplyStablePatchRefinement(*owned);
    if (!equal(value, *owned->GetGenerationContext()->patch_generation) ||
        !equal(foreign, legacy.BuildPatchGenerationRuntime()))
      throw std::runtime_error("Patch overrides changed raw settings or process globals");
    apply(value);
    DomainCandidateFixture::EnablePatchGeneration(legacy);
    DomainCandidateFixture::EnablePatchRefinementModes(legacy);
    DomainCandidateFixture::ApplyStablePatchRefinement(legacy);
    const auto stable = legacy.BuildPatchGenerationRuntime();
    if (!equal(stable, owned->BuildPatchGenerationRuntime()) ||
        !same(observe(legacy, true), observe(*owned, true)))
      throw std::runtime_error("Patch stable overrides changed effective values or native factors");
    apply(value);
    DomainCandidateFixture::EnablePatchGeneration(identity_only);
    DomainCandidateFixture::EnablePatchRefinementModes(identity_only);
    DomainCandidateFixture::ApplyStablePatchRefinement(identity_only);
    if (!equal(stable, legacy.BuildPatchGenerationRuntime()))
      throw std::runtime_error("Legacy patch overrides stopped updating process state");
  }
  apply(saved);
  if (differentiated != 3)
    throw std::runtime_error("Foreign patch controls did not exercise the native factor oracle");
  std::cout << "patch_generation_context cases=3 scalar_bits=84 factor_bits=36 stable_writes=13 "
               "legacy=2\n";
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
  CheckFindUvStatistics(output);
  CheckGenerationRequests(output);
  CheckAdaptivePolicyContexts();
#if defined(AP_MESH_DOMAIN_FAILURE_WRAP)
  CheckStopRetryContexts();
  CheckAdaptationContexts();
  CheckElementBudgetContexts();
  CheckCurveControlsContexts();
  CheckQuadtreeControlsContexts();
  CheckPatchGenerationContexts();
  CheckPatchConsistencyContexts();
  CheckAcceptanceContexts(output);
  CheckAftContexts();
  CheckSerialFlowContexts(output);
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
