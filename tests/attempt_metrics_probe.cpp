// Reuse the runtime definitions, as in curve_orientation_probe.cpp.
#define main apmesh_uninvoked_cli_main
#include "../src/main.cpp"
#undef main

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

int main(int argc, char* argv[]) {
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
