#ifndef APMESH_TESTS_DOMAIN_CANDIDATE_FIXTURE_H
#define APMESH_TESTS_DOMAIN_CANDIDATE_FIXTURE_H

#include <cstdio>
#include <new>

namespace domain_candidate_test {
enum class Mode { Normal, Before, During, After, Adoption };
struct Record {
  void* address = nullptr;
  unsigned kind = 0;
  bool freed = false;
};
struct State {
  bool active = false, select = false, alias = false, suppress = false;
  int branch = 0, calls = 0, insertions = 0, selected = -1;
  int remaining = -1, attempts = 0, denied = 0, suppressed = 0;
  bool deny_unwinding = false;
  int unwind_attempts = 0;
  bool snapshots = false;
  int copy_deny_call = 0;
  int null_stat_call = 0;
  std::vector<Adapter::DomainStructuralStats> snapshot_stats;
  std::vector<unsigned> face_counts;
  std::vector<int> retries;
  Mode mode = Mode::Normal;
  std::array<Record, 128> records{};
  unsigned size = 0;
  std::array<SubMesh*, 4> meshes{};
  Adapter::DomainStructuralStats first, second;
} state;
void Require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}
void Track(void* address, unsigned kind) {
  Require(state.size < state.records.size(), "candidate observer capacity exceeded");
  state.records[state.size++] = {address, kind, false};
}
bool Release(void* address) {
  if (!state.active || address == nullptr)
    return true;
  for (unsigned i = state.size; i > 0; --i) {
    auto& record = state.records[i - 1];
    if (record.address != address || record.freed)
      continue;
    if (state.suppress && record.kind == 0 && state.suppressed == 0) {
      ++state.suppressed;
      return false;
    }
    record.freed = true;
    break;
  }
  return true;
}
std::unique_ptr<SubMesh> MakeMesh(unsigned count, bool observe) {
  auto mesh = std::make_unique<SubMesh>();
  if (observe)
    Track(mesh.get(), 0);
  for (unsigned i = 0; i < count; ++i) {
    std::array<NodeAdaptive*, 3> nodes{};
    for (unsigned k = 0; k < 3; ++k) {
      auto node = std::make_unique<NodeAdaptive>(2.0 * i + (k == 1), k == 2, 0.0);
      node->SetId(3 * i + k);
      nodes[k] = node.get();
      if (observe)
        Track(node.get(), 1);
      mesh->AddNoh(std::move(node));
    }
    auto triangle = std::make_unique<TriangleAdaptive>(nodes[0], nodes[1], nodes[2]);
    triangle->SetParametersN1({0, 0});
    triangle->SetParametersN2({1, 0});
    triangle->SetParametersN3({0, 1});
    if (observe)
      Track(triangle.get(), 2);
    mesh->AddElement(std::move(triangle));
  }
  return mesh;
}
struct Failure {};
SubMesh* GenerateSnapshotCandidate(int step, int index, int retry);
const Adapter::DomainStructuralStats* SnapshotStats();
} // namespace domain_candidate_test

extern "C" SubMesh* RealCandidateAdapt(
    Adapter*, PatchCoons*, Performer::IdManager*, double, double, int, int, int,
    int) asm("__real__ZN7Adapter11AdaptDomainEP10PatchCoonsPN9Performer9IdManagerEddiiii");
extern "C" SubMesh* WrappedCandidateAdapt(
    Adapter*, PatchCoons*, Performer::IdManager*, double, double, int, int, int,
    int) asm("__wrap__ZN7Adapter11AdaptDomainEP10PatchCoonsPN9Performer9IdManagerEddiiii");
extern "C" SubMesh* WrappedCandidateAdapt(Adapter* adapter, PatchCoons* patch,
                                          Performer::IdManager* manager, double factor, double h,
                                          int depth, int step, int index, int retry) {
  using namespace domain_candidate_test;
  if (!state.active)
    return RealCandidateAdapt(adapter, patch, manager, factor, h, depth, step, index, retry);
  if (state.snapshots)
    return GenerateSnapshotCandidate(step, index, retry);
  ++state.calls;
  Require(state.calls <= 2 && step == 4 && index == 0, "unexpected caller generation context");
  const int expected_retry = state.branch == 0 ? 2 : state.branch == 1 ? 3 : 1;
  Require(retry == (state.calls == 1 ? 0 : expected_retry), "caller retry selection changed");
  if (state.calls == 2 && state.mode == Mode::Before)
    throw Failure{};
  if (state.calls == 2 && state.mode == Mode::During)
    state.remaining = 1;
  auto mesh = MakeMesh(state.calls == 1 ? 3 : state.select ? 4 : 2, true);
  state.meshes[static_cast<unsigned>(state.calls - 1)] = mesh.get();
  if (state.alias && state.calls == 2)
    state.first = state.second;
  return mesh.release();
}
extern "C" const Adapter::DomainStructuralStats*
RealCandidateStats(const Adapter*, int) asm("__real__ZNK7Adapter23GetPatchStructuralStatsEi");
extern "C" const Adapter::DomainStructuralStats*
WrappedCandidateStats(const Adapter*, int) asm("__wrap__ZNK7Adapter23GetPatchStructuralStatsEi");
extern "C" const Adapter::DomainStructuralStats* WrappedCandidateStats(const Adapter* adapter,
                                                                       int patch) {
  using namespace domain_candidate_test;
  if (!state.active)
    return RealCandidateStats(adapter, patch);
  if (state.snapshots)
    return SnapshotStats();
  if (state.calls == 2 && state.mode == Mode::After)
    throw Failure{};
  if (state.branch == 0)
    return nullptr;
  return state.alias || state.calls == 1 ? &state.first : &state.second;
}
extern "C" void RealCandidateInsert(MeshAdaptive*, SubMesh*, int) asm(
    "__real__ZN12MeshAdaptive31InsertSubMeshAdaptiveByPositionEP7SubMeshi");
extern "C" void WrappedCandidateInsert(MeshAdaptive*, SubMesh*, int) asm(
    "__wrap__ZN12MeshAdaptive31InsertSubMeshAdaptiveByPositionEP7SubMeshi");
extern "C" void WrappedCandidateInsert(MeshAdaptive* parent, SubMesh* mesh, int position) {
  using namespace domain_candidate_test;
  if (state.active) {
    ++state.insertions;
    Require(position == 0, "candidate insertion position changed");
    state.selected = mesh == state.meshes[0] ? 0 : mesh == state.meshes[1] ? 1 : -1;
    if (state.snapshots) {
      // Reclaimed earlier candidates may share an address with a later generation.
      state.selected = -1;
      for (int i = 0; i < state.calls; ++i)
        if (state.meshes[static_cast<std::size_t>(i)] == mesh)
          state.selected = i;
    }
    Require(state.selected >= 0, "candidate insertion lost exclusive identity");
    if (state.mode == Mode::Adoption)
      state.remaining = 0;
  }
  RealCandidateInsert(parent, mesh, position);
}
extern "C" void* RealCandidateNew(std::size_t) asm("__real__Znwy");
extern "C" void* WrappedCandidateNew(std::size_t) asm("__wrap__Znwy");
extern "C" void* WrappedCandidateNew(std::size_t size) {
  using namespace domain_candidate_test;
  if (state.deny_unwinding && std::uncaught_exceptions() > 0) {
    ++state.unwind_attempts;
    ++state.denied;
    throw std::bad_alloc();
  }
  if (state.active && state.remaining >= 0) {
    ++state.attempts;
    if (state.remaining-- == 0) {
      ++state.denied;
      throw std::bad_alloc();
    }
  }
  return RealCandidateNew(size);
}
extern "C" void RealCandidateDelete(void*) asm("__real__ZdlPv");
extern "C" void WrappedCandidateDelete(void*) asm("__wrap__ZdlPv");
extern "C" void WrappedCandidateDelete(void* value) {
  if (domain_candidate_test::Release(value))
    RealCandidateDelete(value);
}
extern "C" void RealCandidateSizedDelete(void*, std::size_t) asm("__real__ZdlPvy");
extern "C" void WrappedCandidateSizedDelete(void*, std::size_t) asm("__wrap__ZdlPvy");
extern "C" void WrappedCandidateSizedDelete(void* value, std::size_t size) {
  if (domain_candidate_test::Release(value))
    RealCandidateSizedDelete(value, size);
}

// Seed bounded fixture state without changing production policy or exposing it publicly.
class DomainCandidateFixture {
  static void Case(int branch, bool select, domain_candidate_test::Mode mode, bool alias,
                   bool suppress) {
    using namespace domain_candidate_test;
    Geometry geometry;
    Models3d models;
    models.ModelBaseQuadrada(&geometry);
    Require(geometry.GetNumberPatches() == 1, "fixture requires one native patch");
    auto accepted = MakeMesh(3, false);
    auto* patch = static_cast<PatchCoons*>(geometry.GetPatch(0));
    patch->SetSubMesh(accepted.get());
    GeneratorAdaptive generator;
    generator.step_ = ADAPTIVE_CURRENT_STEP = 4;
    ADAPTIVE_CURRENT_RETRY = 0;
    generator.current_policy_.stable_mode = true;
    generator.stable_consecutive_reject_count_ = 1;
    generator.last_submesh_error_ = {1};
    generator.last_candidate_elements_current_ = {branch == 0 ? 8ULL : 0ULL};
    generator.current_adaptation_relaxation_ = generator.current_adaptation_max_delta_ = 1;
    generator.id_managers_.resize(1);
    state = domain_candidate_test::State{};
    state.branch = branch;
    state.select = select;
    state.alias = alias;
    state.mode = mode;
    state.suppress = suppress;
    state.first.generated_faces = state.second.generated_faces = 3;
    state.first.transition_region.good_ratio_ge_0_60 =
        state.second.transition_region.good_ratio_ge_0_60 = 1;
    state.first.generation_status = state.second.generation_status =
        branch == 1 ? "degenerate_needs_retry" : "ready";
    if (branch == 2) {
      state.first.transition_underresolved = 1;
      state.second.transition_underresolved = select ? 0 : 1;
    }
    bool caught = false;
    state.active = true;
    {
      MeshAdaptive destination;
      try {
        generator.AdaptDomain(&geometry, &destination);
      } catch (const Failure&) {
        caught = true;
      } catch (const std::bad_alloc&) {
        caught = true;
      }
      Require(state.calls == 2 && caught == (mode != Mode::Normal),
              "caller branch or expected exception missing");
      Require(state.insertions == (mode == Mode::Normal || mode == Mode::Adoption ? 1 : 0),
              "caller insertion count changed");
      if (mode == Mode::Normal) {
        Require(state.selected == (select ? 1 : 0), "caller selected identity changed");
        Require(patch->GetSubMesh() == destination.GetSubMeshAdaptiveByPosition(0),
                "successful insertion did not publish the selected mesh");
      } else {
        Require(patch->GetSubMesh() == accepted.get(), "failure published a pending candidate");
        Require(destination.GetNumberSubMeshesAdaptive() == 0,
                "failed insertion changed the existing empty destination");
      }
      patch->SetSubMesh(accepted.get());
    }
    const auto live = std::count_if(state.records.begin(), state.records.begin() + state.size,
                                    [](const Record& record) { return !record.freed; });
    Require(state.size > 0 && live == 0, "candidate release observer detected retained storage");
    Require(state.denied == (mode == Mode::During || mode == Mode::Adoption ? 1 : 0),
            "actual allocation denial count changed");
    state.active = false;
    std::printf("candidate branch=%d select=%d mode=%d alias=%d calls=2 retained=0 denied=%d\n",
                branch, select, static_cast<int>(mode), alias, state.denied);
  }

public:
  static void EnablePatchGeneration(GeneratorAdaptive& generator) {
    generator.EnablePatchGeneration();
  }
  static void EnablePatchRefinementModes(GeneratorAdaptive& generator) {
    generator.EnablePatchRefinementModes();
  }
  static void ApplyStablePatchRefinement(GeneratorAdaptive& generator) {
    generator.ApplyStablePatchRefinement();
  }
  static std::vector<double> PatchFactors(GeneratorAdaptive& generator, const Geometry& geometry,
                                          int step, bool stable) {
    generator.step_ = step;
    generator.current_policy_ = generator.BuildAdaptivePolicyRuntime();
    generator.current_policy_.stable_mode = stable;
    generator.last_submesh_error_ = {0.7, 0.2};
    generator.patch_history_.clear();
    generator.current_budget_retry_count_ = step == 2 ? 1U : 0U;
    generator.previous_patch_factors_.clear();
    generator.current_adaptation_relaxation_ = 1.0;
    generator.current_adaptation_max_delta_ = 0.2;
    return generator.ComputePatchAdaptationFactors(&geometry);
  }
  static std::vector<double> SmoothPatchFactors(GeneratorAdaptive& generator,
                                                const Geometry& geometry) {
    generator.step_ = 2;
    generator.current_patch_eligible_mask_ = {1, 0};
    generator.current_patch_adaptation_.clear();
    return generator.SmoothPatchAdaptationFactors(&geometry, {0.84, 1.05});
  }
  static void QuadtreeCap(GeneratorAdaptive& generator) { generator.EnableQuadtreeCap(); }
  static void QuadtreeQuality(GeneratorAdaptive& generator) {
    generator.ApplyStableQuadtreeQuality();
  }
  static int EstimateTreeDepth(const GeneratorAdaptive& generator, double h, int step) {
    return generator.EstimateOwnedQuadtreeDepth(h, step);
  }
  static int ResolveTreeDepth(const GeneratorAdaptive& generator, int depth, int step) {
    return generator.adapter_.ResolveQuadtreeDepth(depth, step);
  }
  static void ConfigureTree(const GeneratorAdaptive& generator, Par2DJMesh::AFT::Quadtree& tree) {
    generator.adapter_.ConfigureQuadtree(&tree);
  }
  static void CurvePointBudget(GeneratorAdaptive& generator) { generator.EnableCurvePointBudget(); }
  static void CurveConsistency(GeneratorAdaptive& generator) { generator.EnableCurveConsistency(); }
  static int ClampCurvePoints(const GeneratorAdaptive& generator, int value) {
    return generator.ClampCurveTarget(value);
  }
  static std::array<double, 2> CurveDiscretization(const GeneratorAdaptive& generator) {
    return {{generator.adapter_.CurveDiscretizationFactor(),
             generator.adapter_.InternalCurveDiscretizationFactor()}};
  }
  static void StableElementBudget(GeneratorAdaptive& generator) {
    generator.ApplyStableElementBudgetSettings();
  }
  static double ClampElementTarget(const GeneratorAdaptive& generator, double target) {
    return generator.ClampBudgetTargetElements(target);
  }
  static void PromoteRetry(GeneratorAdaptive& generator) { generator.PromoteAdaptiveRetry(); }
  static void StableAdaptation(GeneratorAdaptive& generator) {
    generator.ApplyStableAdaptationSettings();
  }
  static std::vector<double> RateLimit(GeneratorAdaptive& generator,
                                       const std::vector<double>& targets) {
    const auto settings = generator.BuildAdaptationRuntime();
    generator.current_adaptation_relaxation_ = settings.relaxation;
    generator.current_adaptation_max_delta_ = settings.max_delta;
    generator.previous_patch_factors_.clear();
    return generator.ApplyAdaptationRateLimit(targets);
  }
  static int RunSnapshots();
  static int Run(bool release_control) {
    try {
      for (int branch = 0; branch < 3; ++branch)
        for (bool select : {false, true})
          for (int mode = 0; mode < 5; ++mode)
            Case(branch, select, static_cast<domain_candidate_test::Mode>(mode), false,
                 release_control);
      Case(2, false, domain_candidate_test::Mode::Normal, true, false);
      Case(2, true, domain_candidate_test::Mode::Normal, true, false);
      std::puts("candidate_contracts=32 complete=1");
      return 0;
    } catch (const std::exception& error) {
      domain_candidate_test::state.active = false;
      if (release_control)
        std::fprintf(stderr, "candidate_release_control_suppressed=%d\n",
                     domain_candidate_test::state.suppressed);
      std::fprintf(stderr, "Candidate contract failure: %s\n", error.what());
      return 1;
    }
  }
};

#endif // APMESH_TESTS_DOMAIN_CANDIDATE_FIXTURE_H
