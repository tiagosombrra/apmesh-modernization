#ifndef APMESH_TESTS_CANDIDATE_SNAPSHOT_FIXTURE_H
#define APMESH_TESTS_CANDIDATE_SNAPSHOT_FIXTURE_H

namespace domain_candidate_test {
SubMesh* GenerateSnapshotCandidate(int step, int index, int retry) {
  const auto n = static_cast<std::size_t>(state.calls++);
  Require(step == 4 && index == 0 && n < state.face_counts.size() && retry == state.retries[n],
          "snapshot generation sequence changed");
  auto mesh = MakeMesh(state.face_counts[n], true);
  state.meshes[n] = mesh.get();
  if (state.alias)
    state.first = state.snapshot_stats[n];
  return mesh.release();
}
const Adapter::DomainStructuralStats* SnapshotStats() {
  const auto n = static_cast<std::size_t>(state.calls - 1);
  Require(n < state.snapshot_stats.size(), "snapshot stats context missing");
  if (state.calls == state.null_stat_call)
    return nullptr;
  if (state.calls == state.copy_deny_call)
    state.remaining = 0;
  return state.alias ? &state.first : &state.snapshot_stats[n];
}
Adapter::DomainStructuralStats Snapshot(unsigned faces, unsigned stamp) {
  Adapter::DomainStructuralStats s;
  s.generated_faces = faces;
  s.transition_floor = 0.01 * stamp;
  s.good_ratio_ge_0_60 = 0.25 + 0.01 * stamp;
  auto region = [stamp](unsigned offset) {
    const double v = 0.001 * (stamp + offset);
    return Adapter::RegionQualityStats{stamp + offset, v,        v + 0.01, v + 0.02, v + 0.03,
                                       v + 0.04,       v + 0.05, v + 0.06, v + 0.07};
  };
  s.boundary_region = region(10);
  s.transition_region = region(20);
  s.interior_region = region(30);
  s.transition_region.good_ratio_ge_0_60 = 1;
  s.generation_status = "ready";
  return s;
}
} // namespace domain_candidate_test

int DomainCandidateFixture::RunSnapshots() {
  using namespace domain_candidate_test;
  unsigned cases = 0;
  try {
    // Exercise actual caller decisions with distinct and reused Adapter cache slots.
    for (bool alias : {false, true}) {
      for (int scenario = 0; scenario < 20; ++scenario) {
        Geometry geometry;
        Models3d models;
        models.ModelBaseQuadrada(&geometry);
        auto accepted = MakeMesh(3, false);
        auto* patch = static_cast<PatchCoons*>(geometry.GetPatch(0));
        patch->SetSubMesh(accepted.get());
        GeneratorAdaptive generator;
        generator.step_ = ADAPTIVE_CURRENT_STEP = 4;
        ADAPTIVE_CURRENT_RETRY = 0;
        generator.current_policy_.stable_mode = true;
        generator.stable_consecutive_reject_count_ = 1;
        generator.last_submesh_error_ = {1};
        generator.last_candidate_elements_current_ = {
            scenario < 2 || (scenario >= 8 && scenario < 12) || scenario >= 16 ? 8ULL : 0ULL};
        generator.current_adaptation_relaxation_ = generator.current_adaptation_max_delta_ = 1;
        generator.id_managers_.resize(1);
        state = domain_candidate_test::State{};
        state.snapshots = state.active = true;
        state.alias = alias;
        state.face_counts = {3, scenario % 2 == 0 ? 4U : 2U};
        state.retries = {0, scenario < 2 ? 2 : scenario < 4 ? 3 : 1};
        state.snapshot_stats = {Snapshot(state.face_counts[0], 1),
                                Snapshot(state.face_counts[1], 2)};
        int expected = scenario % 2 == 0 ? 1 : 0;
        if (scenario >= 2 && scenario < 4)
          state.snapshot_stats[0].generation_status = "degenerate_needs_retry";
        if (scenario == 3)
          state.snapshot_stats[1].generation_status = "degenerate_needs_retry";
        if (scenario >= 4 && scenario < 8) {
          state.snapshot_stats[0].transition_underresolved = 1;
          state.snapshot_stats[1].transition_underresolved = scenario % 2 == 0 ? 0 : 1;
          if (scenario >= 6) {
            state.snapshot_stats[0].transition_underresolved =
                state.snapshot_stats[1].transition_underresolved = 0;
            state.snapshot_stats[0].curve_interior_coupling = 0.5;
            state.snapshot_stats[0].interior_transition_imbalance = 0.125;
            const double boundary = 0.125 - 1.0e-9;
            state.snapshot_stats[1].interior_transition_imbalance =
                scenario == 6 ? std::nextafter(boundary, 0.0) : boundary;
          }
        }
        if (scenario == 8 || scenario == 9) {
          state.face_counts = {3, 4, 5, 6};
          state.retries = {0, 2, 3, 1};
          state.snapshot_stats.clear();
          for (unsigned i = 0; i < 4; ++i)
            state.snapshot_stats.push_back(Snapshot(state.face_counts[i], i + 1));
          state.snapshot_stats[0].generation_status = state.snapshot_stats[1].generation_status =
              "degenerate_needs_retry";
          state.snapshot_stats[2].transition_underresolved = 1;
          state.snapshot_stats[3].transition_underresolved = scenario == 8 ? 0 : 1;
          expected = scenario == 8 ? 3 : 2;
        }
        if (scenario == 10 || scenario == 11) {
          state.face_counts = {3, 2};
          state.retries = {0, 2};
          state.snapshot_stats = {Snapshot(3, 1), Snapshot(2, 2)};
          for (auto& s : state.snapshot_stats)
            s.generation_status.assign(257, 's');
          state.copy_deny_call = scenario == 10 ? 1 : 2;
          state.deny_unwinding = true;
          expected = -1;
        }
        if (scenario >= 12 && scenario < 16) {
          state.face_counts = {3, 4};
          state.retries = {0, 1};
          state.snapshot_stats = {Snapshot(3, 1), Snapshot(4, 2)};
          state.snapshot_stats[0].curve_domain_balance = 0.7;
          state.snapshot_stats[0].interior_transition_imbalance = 0.01;
          state.snapshot_stats[1].curve_domain_balance = 0.7 + (scenario < 14    ? 0.005
                                                                : scenario == 14 ? 2.0e-6
                                                                                 : 0.5e-6);
          state.snapshot_stats[1].interior_transition_imbalance = scenario == 13 ? 0.041 : 0.03;
          expected = scenario % 2 == 0 ? 1 : 0;
        }
        if (scenario >= 16) {
          state.retries = {0, 2};
          state.null_stat_call = scenario < 18 ? 1 : 2;
        }
        const bool missing = expected >= 0 && state.null_stat_call == expected + 1;
        const auto expected_stats = expected >= 0
                                        ? state.snapshot_stats[static_cast<std::size_t>(expected)]
                                        : Adapter::DomainStructuralStats{};
        bool caught = false;
        {
          MeshAdaptive destination;
          try {
            generator.AdaptDomain(&geometry, &destination);
          } catch (const std::bad_alloc&) {
            caught = true;
          }
          state.remaining = -1;
          Require(caught == (expected < 0), "snapshot copy failure contract changed");
          Require(state.calls == (scenario == 10 ? 1 : static_cast<int>(state.face_counts.size())),
                  "snapshot attempt count changed");
          if (expected >= 0) {
            Require(state.selected == expected && state.insertions == 1,
                    "snapshot selection lost candidate identity");
            const auto& actual = generator.current_patch_adaptation_.at(0);
            if (missing) {
              Require(actual.transition_floor == 0 &&
                          actual.generation_status_structural == "unknown",
                      "missing selected snapshot exported another candidate's statistics");
            } else {
              Require(
                  actual.transition_floor == expected_stats.transition_floor &&
                      actual.transition_underresolved == expected_stats.transition_underresolved &&
                      actual.interior_transition_imbalance ==
                          expected_stats.interior_transition_imbalance &&
                      actual.curve_domain_balance == expected_stats.curve_domain_balance &&
                      actual.curve_interior_coupling == expected_stats.curve_interior_coupling &&
                      actual.good_ratio_ge_0_60 == expected_stats.good_ratio_ge_0_60 &&
                      actual.generated_faces_structural == expected_stats.generated_faces &&
                      actual.generation_status_structural == expected_stats.generation_status,
                  "selected scalar statistics describe another candidate");
              Require(
                  actual.boundary_element_count == expected_stats.boundary_region.element_count &&
                      actual.boundary_quality_min == expected_stats.boundary_region.quality_min &&
                      actual.boundary_quality_mean == expected_stats.boundary_region.quality_mean &&
                      actual.boundary_good_ratio_ge_0_60 ==
                          expected_stats.boundary_region.good_ratio_ge_0_60 &&
                      actual.transition_band_elements ==
                          expected_stats.transition_region.element_count &&
                      actual.transition_band_quality_min ==
                          expected_stats.transition_region.quality_min &&
                      actual.transition_band_quality_mean ==
                          expected_stats.transition_region.quality_mean &&
                      actual.transition_band_q_ge_0_60 ==
                          expected_stats.transition_region.good_ratio_ge_0_60 &&
                      actual.interior_core_elements ==
                          expected_stats.interior_region.element_count &&
                      actual.interior_core_quality_min ==
                          expected_stats.interior_region.quality_min &&
                      actual.interior_core_quality_mean ==
                          expected_stats.interior_region.quality_mean &&
                      actual.interior_core_q_ge_0_60 ==
                          expected_stats.interior_region.good_ratio_ge_0_60,
                  "selected region statistics describe another candidate");
              Require(actual.generated_faces_structural == actual.actual_patch_elements,
                      "selected statistics and owned mesh face counts differ");
            }
          } else {
            Require(state.insertions == 0 && patch->GetSubMesh() == accepted.get() &&
                        destination.GetNumberSubMeshesAdaptive() == 0 && state.denied == 1 &&
                        state.unwind_attempts == 0,
                    "snapshot copy failure leaked, allocated during unwinding or published a "
                    "candidate");
          }
          patch->SetSubMesh(accepted.get());
        }
        Require(state.size > 0 &&
                    std::none_of(state.records.begin(), state.records.begin() + state.size,
                                 [](const Record& r) { return !r.freed; }),
                "snapshot candidate retained native storage");
        state.active = false;
        std::printf(
            "snapshot scenario=%d alias=%d calls=%d selected=%d retained=0 denied=%d unwind=0\n",
            scenario, alias, state.calls, expected, state.denied);
        ++cases;
      }
    }
    std::printf("snapshot_contracts=%u complete=1\n", cases);
    return 0;
  } catch (const std::exception& error) {
    state.active = false;
    std::fprintf(stderr, "Snapshot contract failure: %s\n", error.what());
    return 1;
  }
}
#endif // APMESH_TESTS_CANDIDATE_SNAPSHOT_FIXTURE_H
