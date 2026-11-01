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
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <memory>
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
