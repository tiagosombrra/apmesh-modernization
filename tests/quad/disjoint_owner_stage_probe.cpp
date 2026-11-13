#include "disjoint_owner_stage.h"
#include "data/geometry.h"
#include "data/patch/patch_bezier.h"
#include "input_output/patch_reader.h"

#include <array>
#include <iostream>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>

namespace {
using apmesh::quad::research::DisjointOwnerStage;
using apmesh::quad::research::QuadrilateralAdaptive;

void Require(bool condition, const char* reason) {
  if (!condition)
    throw std::runtime_error(reason);
}

std::unique_ptr<SubMesh> SyntheticChart(unsigned chart_id, unsigned generation) {
  auto chart = std::make_unique<SubMesh>();
  const double base = static_cast<double>(chart_id) * 8.0 +
                      static_cast<double>(generation) * 0.001;
  const std::array<std::array<double, 3>, 7> xyz{{
      {{base, 0, 0}}, {{base + 1, 0, 0}},
      {{base + 1, 1, 0}}, {{base, 1, 0}},
      {{base + 2, 0, 0}}, {{base + 3, 0, 0}},
      {{base + 2, 1, 0}},
  }};
  std::array<NodeAdaptive*, 7> nodes{};
  for (unsigned i = 0; i < xyz.size(); ++i) {
    auto node = std::make_unique<NodeAdaptive>(
        xyz[i][0], xyz[i][1], xyz[i][2]);
    node->SetId(static_cast<unsigned long>(
        chart_id * 1000U + generation * 10U + i + 1U));
    nodes[i] = node.get();
    chart->AddNoh(std::move(node));
  }
  const QuadrilateralAdaptive::Nodes quad_nodes{
      nodes[0], nodes[1], nodes[2], nodes[3]};
  const QuadrilateralAdaptive::Parameters uv{{
      {{0.0, 0.0}}, {{1.0, 0.0}},
      {{1.0, 1.0}}, {{0.0, 1.0}},
  }};
  chart->AddElement(std::make_unique<QuadrilateralAdaptive>(
      quad_nodes, uv, VectorAdaptive(0, 0, 1)));
  chart->AddElement(std::make_unique<TriangleAdaptive>(
      nodes[4], nodes[5], nodes[6]));
  DisjointOwnerStage::CheckChart(*chart);
  return chart;
}

void CheckModel(const std::unique_ptr<MeshAdaptive>& model,
                unsigned expected_charts) {
  Require(model != nullptr &&
              model->GetNumberSubMeshesAdaptive() == expected_charts,
          "Disconnected owner model slot count changed");
  std::set<const NodeAdaptive*> all_nodes;
  std::set<const ElementAdaptive*> all_elements;
  for (unsigned patch = 0; patch < expected_charts; ++patch) {
    const SubMesh* chart = model->GetSubMeshAdaptiveByPosition(patch);
    Require(chart != nullptr && chart->GetPatch() == nullptr &&
                chart->GetNumberNos() == 7 &&
                chart->GetNumberElements() == 2,
            "Detached patch chart was not owned at its unique index");
    DisjointOwnerStage::CheckChart(*chart);
    for (unsigned slot = 0; slot < 7; ++slot)
      Require(all_nodes.insert(chart->GetNoh(slot)).second,
              "Candidate shares a live node across disconnected charts");
    for (unsigned slot = 0; slot < 2; ++slot)
      Require(all_elements.insert(chart->GetElement(slot)).second,
              "Candidate shares an element across disconnected charts");
  }
  Require(all_nodes.size() == expected_charts * 7U &&
              all_elements.size() == expected_charts * 2U,
          "Unexpected detached patch chart owner inventory");
}

std::unique_ptr<SubMesh> SourcePatchChart(PatchBezier& patch,
                                          unsigned chart_id,
                                          unsigned generation) {
  // These are two small, detached UV test elements on the REAL original
  // surface, not the original native Quadtree/AFT-generated full mesh.
  const std::array<std::array<double, 2>, 7> uv{{
      {{0.1, 0.1}}, {{0.4, 0.1}}, {{0.4, 0.4}}, {{0.1, 0.4}},
      {{0.6, 0.6}}, {{0.9, 0.6}}, {{0.6, 0.9}},
  }};
  auto chart = std::make_unique<SubMesh>();
  std::array<NodeAdaptive*, 7> nodes{};
  for (unsigned i = 0; i < uv.size(); ++i) {
    const auto p = patch.Parameterize(uv[i][0], uv[i][1]);
    auto node = std::make_unique<NodeAdaptive>(
        p.GetX(), p.GetY(), p.GetZ());
    node->SetId(static_cast<unsigned long>(
        chart_id * 1000U + generation * 10U + i + 1U));
    nodes[i] = node.get();
    chart->AddNoh(std::move(node));
  }
  const QuadrilateralAdaptive::Nodes quad_nodes{
      nodes[0], nodes[1], nodes[2], nodes[3]};
  const QuadrilateralAdaptive::Parameters quad_uv{{
      {{0.1, 0.1}}, {{0.4, 0.1}},
      {{0.4, 0.4}}, {{0.1, 0.4}},
  }};
  const VectorAdaptive normal = patch.Qu(0.25, 0.25) * patch.Qv(0.25, 0.25);
  chart->AddElement(std::make_unique<QuadrilateralAdaptive>(
      quad_nodes, quad_uv, normal));
  chart->AddElement(std::make_unique<TriangleAdaptive>(
      nodes[4], nodes[5], nodes[6]));
  DisjointOwnerStage::CheckChart(*chart);
  return chart;
}

void TestOriginalSourceDisjointCharts(const std::string& source_path,
                                      unsigned expected) {
  Geometry original;
  PatchReader reader;
  Require(reader.ReaderFilePatches(&original, source_path) == &original &&
              original.GetNumberPatches() == expected,
          "Original PatchReader model source cardinality mismatch");
  std::unique_ptr<MeshAdaptive> active = std::make_unique<MeshAdaptive>();
  active->InsertSubMeshAdaptive(SyntheticChart(0, 1).release());
  MeshAdaptive* const baseline = active.get();
  SubMesh* const baseline_chart = active->GetSubMeshAdaptiveByPosition(0);
  unsigned rejected = 0;
  for (unsigned fault = 0; fault <= expected; ++fault) {
    DisjointOwnerStage stage(expected);
    for (unsigned patch_id = 0; patch_id < expected; ++patch_id) {
      auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(patch_id));
      Require(patch != nullptr, "Missing real source Bezier patch");
      stage.Add(SourcePatchChart(*patch, patch_id, fault + 2U));
    }
    bool failed = false;
    try {
      stage.Replace(active, static_cast<int>(fault));
    } catch (const std::runtime_error&) {
      failed = true;
    }
    Require(failed && active.get() == baseline &&
                active->GetSubMeshAdaptiveByPosition(0) == baseline_chart,
            "Real-source detached stage damaged the previous mesh owner");
    ++rejected;
  }
  DisjointOwnerStage stage(expected);
  for (unsigned patch_id = 0; patch_id < expected; ++patch_id) {
    auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(patch_id));
    Require(patch != nullptr, "Missing real source patch for final stage");
    stage.Add(SourcePatchChart(*patch, patch_id, 80));
  }
  stage.Replace(active);
  CheckModel(active, expected);
  for (unsigned patch_id = 0; patch_id < expected; ++patch_id) {
    auto* patch = dynamic_cast<PatchBezier*>(original.GetPatch(patch_id));
    Require(patch != nullptr && patch->GetSubMesh() == nullptr,
            "Detached original source patch gained an unauthorized mesh observer");
  }
  std::cout << "R2C2_REAL_SOURCE_DISJOINT"
            << " patches=" << expected
            << " original_PatchReader=1"
            << " source_patch_examples=" << expected
            << " original_bezier_xyz=1"
            << " sample_elements_per_patch=2"
            << " fault_cases_rejected=" << rejected
            << " source_native_AFT_mesh=0"
            << " cross_patch_shared_nodes=0"
            << " patch_observers_touched=0"
            << " actual_global_mesh_published=0"
            << " scientific_sheet_approval=0\\n";
}

void TestStage(unsigned patches) {
  std::unique_ptr<MeshAdaptive> active = std::make_unique<MeshAdaptive>();
  active->InsertSubMeshAdaptive(SyntheticChart(0, 1).release());
  MeshAdaptive* const baseline = active.get();
  SubMesh* const baseline_chart = active->GetSubMeshAdaptiveByPosition(0);
  NodeAdaptive* const baseline_node = baseline_chart->GetNoh(0);
  ElementAdaptive* const baseline_element = baseline_chart->GetElement(0);
  unsigned rejected = 0;
  for (unsigned fault = 0; fault <= patches; ++fault) {
    DisjointOwnerStage staged(patches);
    for (unsigned i = 0; i < patches; ++i)
      staged.Add(SyntheticChart(i, fault + 2));
    bool thrown = false;
    try {
      staged.Replace(active, static_cast<int>(fault));
    } catch (const std::runtime_error&) {
      thrown = true;
    }
    Require(thrown && active.get() == baseline &&
                active->GetSubMeshAdaptiveByPosition(0) == baseline_chart &&
                baseline_chart->GetNoh(0) == baseline_node &&
                baseline_chart->GetElement(0) == baseline_element,
            "Injected stage failure changed prior accepted model or nodes");
    CheckModel(active, 1);
    ++rejected;
  }

  // A candidate with a missing chart must fail without moving the active root.
  {
    DisjointOwnerStage incomplete(patches);
    for (unsigned i = 0; i + 1 < patches; ++i)
      incomplete.Add(SyntheticChart(i, 77));
    bool thrown = false;
    try {
      incomplete.Replace(active);
    } catch (const std::invalid_argument&) {
      thrown = true;
    }
    Require(thrown && active.get() == baseline &&
                active->GetSubMeshAdaptiveByPosition(0) == baseline_chart,
            "Incomplete staged candidate changed the active mesh");
    ++rejected;
  }
  {
    DisjointOwnerStage staged(patches);
    for (unsigned i = 0; i < patches; ++i)
      staged.Add(SyntheticChart(i, 90));
    staged.Replace(active);
    Require(active.get() != baseline,
            "Fully validated candidate did not atomically replace owner root");
    CheckModel(active, patches);
  }
  // A second complete detached stage exercises repeated bounded ownership
  // retirement. No actual patch geometry or advisor policy is involved.
  auto* const previous = active.get();
  {
    DisjointOwnerStage staged(patches);
    for (unsigned i = 0; i < patches; ++i)
      staged.Add(SyntheticChart(i, 91));
    staged.Replace(active);
    Require(active.get() != previous,
            "Repeated detached model replacement did not retire prior root");
    CheckModel(active, patches);
  }
  std::cout << "R2C2_DISJOINT_STAGE"
            << " patches=" << patches
            << " staged_charts=" << patches
            << " isolated_nodes=" << patches * 7U
            << " isolated_elements=" << patches * 2U
            << " fault_cases_rejected=" << rejected
            << " repeated_atomic_replacements=2"
            << " cross_patch_shared_nodes=0"
            << " patch_observers_touched=0"
            << " actual_source_geometry=0"
            << " physical_SubMesh_published=0"
            << " scientific_sheet_approval=0\n";
}
}  // namespace

int main(int argc, char** argv) {
  try {
    Require(argc == 3, "Expected original Eistute and Book .bp model paths");
    TestStage(4);
    TestStage(28);
    TestOriginalSourceDisjointCharts(argv[1], 4);
    TestOriginalSourceDisjointCharts(argv[2], 28);
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "R2c2 detached owner stage failure: "
              << error.what() << '\n';
    return 1;
  }
}
