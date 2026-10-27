#ifndef APMESH_TESTS_ACCEPTED_ROOT_FIXTURE_H
#define APMESH_TESTS_ACCEPTED_ROOT_FIXTURE_H

#include "generator/accepted_mesh_scope.h"

namespace accepted_root_test {
using domain_candidate_test::Require;
using domain_candidate_test::state;
struct Failure {};

std::unique_ptr<MeshAdaptive> MakeOwner(unsigned first) {
  auto owner = std::make_unique<MeshAdaptive>();
  for (unsigned i = 0; i < 2; ++i)
    owner->InsertSubMeshAdaptive(domain_candidate_test::MakeMesh(first + i, true).release());
  return owner;
}
void Bind(Geometry& geometry, MeshAdaptive* mesh, bool reverse) {
  for (unsigned i = 0; i < 2; ++i)
    geometry.GetPatch(reverse ? 1 - i : i)->SetSubMesh(mesh->GetSubMeshAdaptiveByPosition(i));
}
bool LiveChild(const SubMesh* child) {
  for (unsigned i = state.size; i > 0; --i)
    if (state.records[i - 1].address == child)
      return !state.records[i - 1].freed;
  return false;
}
void CheckReleased() {
  Require(state.size > 0 &&
              std::all_of(state.records.begin(), state.records.begin() + state.size,
                          [](const domain_candidate_test::Record& r) { return r.freed; }),
          "accepted root retained observed native storage");
}
void Case(bool archived, int action, bool reverse, bool suppress) {
  state = domain_candidate_test::State{};
  state.active = true;
  state.suppress = suppress;
  {
    Geometry geometry;
    for (unsigned i = 0; i < 4; ++i)
      geometry.InsertPatch(std::make_unique<Patch>());
    auto foreign = domain_candidate_test::MakeMesh(1, false);
    geometry.GetPatch(2)->SetSubMesh(foreign.get());
    auto active = MakeOwner(1);
    auto* accepted = active.get();
    const auto* accepted_child = accepted->GetSubMeshAdaptiveByPosition(0);
    GeneratorAdaptive::MeshVector archive;
    archive.reserve(2);
    if (archived)
      archive.emplace_back(0, std::move(active));
    MeshAdaptive* selected = nullptr;
    bool caught = false, allocation = false;
    try {
      Bind(geometry, accepted, reverse);
      apmesh::generation::AcceptedMeshScope scope(geometry, active, accepted);
      Require(!active && LiveChild(accepted_child) && accepted_child->GetNumberElements() == 1,
              "scope did not retain the accepted root before construction");
      if (action == 2) {
        state.remaining = 0;
        state.deny_unwinding = true;
        throw Failure{};
      }
      if (action == 3) {
        state.remaining = 3;
        state.deny_unwinding = true;
      }
      active = MakeOwner(3);
      Bind(geometry, active.get(), reverse);
      if (action == 4) {
        state.remaining = 0;
        state.deny_unwinding = true;
        throw Failure{};
      }
      state.remaining = 0;
      if (action == 1) {
        auto* expected = active.get();
        selected = scope.Commit();
        Require(selected == expected, "commit did not select the active candidate");
      } else {
        Bind(geometry, accepted, reverse);
      }
      if (archived)
        archive.emplace_back(1, std::move(active));
    } catch (const Failure&) {
      caught = true;
    } catch (const std::bad_alloc&) {
      caught = allocation = true;
    }
    state.remaining = -1;
    Require(caught == (action >= 2) && allocation == (action == 3) &&
                state.denied == (action == 3 ? 1 : 0) && state.unwind_attempts == 0,
            "accepted root failure or nonallocation contract changed");
    if (!archived) {
      Require(active.get() == (action == 1 ? selected : accepted),
              "scope lost the selected or restored active owner");
      if (caught)
        Require(geometry.GetPatch(0)->GetSubMesh() == nullptr &&
                    geometry.GetPatch(1)->GetSubMesh() == nullptr,
                "unwinding left owned observers attached");
    }
    Require(geometry.GetPatch(2)->GetSubMesh() == foreign.get() &&
                geometry.GetPatch(3)->GetSubMesh() == nullptr,
            "scope changed foreign or null observations");
    for (unsigned i = 0; i < 2; ++i)
      geometry.GetPatch(i)->SetSubMesh(nullptr);
  }
  state.active = false;
  CheckReleased();
  std::printf("accepted_root archived=%d action=%d reverse=%d denied=%d unwind=0 retained=0\n",
              archived, action, reverse, state.denied);
}
void Sequence(bool archived) {
  state = domain_candidate_test::State{};
  state.active = true;
  {
    Geometry geometry;
    for (unsigned i = 0; i < 2; ++i)
      geometry.InsertPatch(std::make_unique<Patch>());
    auto active = MakeOwner(1);
    auto* accepted = active.get();
    Bind(geometry, accepted, false);
    GeneratorAdaptive::MeshVector archive;
    archive.reserve(5);
    if (archived)
      archive.emplace_back(0, std::move(active));
    unsigned commits = 0;
    for (unsigned step = 1; step <= 4; ++step) {
      auto* prior = accepted;
      {
        apmesh::generation::AcceptedMeshScope scope(geometry, active, accepted);
        for (unsigned retry = 0; retry < 2; ++retry) {
          Bind(geometry, accepted, false);
          Require(geometry.GetPatch(0)->GetSubMesh() == accepted->GetSubMeshAdaptiveByPosition(0),
                  "retry seed lost accepted identity");
          active = MakeOwner(1);
          Bind(geometry, active.get(), false);
        }
        if (step == 1 || step == 4) {
          accepted = scope.Commit();
          ++commits;
        } else {
          Bind(geometry, accepted, false);
        }
        if (archived)
          archive.emplace_back(static_cast<int>(step), std::move(active));
      }
      Require((step == 1 || step == 4) ? accepted != prior : accepted == prior,
              "accept/reject sequence changed the wrong root");
      Require((archived || active.get() == accepted) &&
                  geometry.GetPatch(0)->GetSubMesh() == accepted->GetSubMeshAdaptiveByPosition(0),
              "rejected history replaced the accepted root");
    }
    Require(commits == 2 && archive.size() == (archived ? 5U : 0U),
            "accepted sequence lost rejected report entries");
    Bind(geometry, accepted, false);
    for (unsigned i = 0; i < 2; ++i)
      geometry.GetPatch(i)->SetSubMesh(nullptr);
  }
  state.active = false;
  CheckReleased();
  std::printf("accepted_sequence archived=%d steps=4 retries=8 commits=2 retained=0\n", archived);
}
int Run(bool release_control) {
  try {
    for (bool archived : {false, true})
      for (int action = 0; action < 5; ++action)
        for (bool reverse : {false, true})
          Case(archived, action, reverse, release_control);
    for (bool archived : {false, true})
      Sequence(archived);
    std::puts("accepted_root_contracts=22 complete=1");
    return 0;
  } catch (const std::exception& error) {
    state.active = false;
    state.remaining = -1;
    if (release_control)
      std::fprintf(stderr, "accepted_root_release_suppressed=%d\n", state.suppressed);
    std::fprintf(stderr, "Accepted root contract failure: %s\n", error.what());
    return 1;
  }
}
} // namespace accepted_root_test
#endif // APMESH_TESTS_ACCEPTED_ROOT_FIXTURE_H
