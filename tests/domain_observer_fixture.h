#ifndef APMESH_TESTS_DOMAIN_OBSERVER_FIXTURE_H
#define APMESH_TESTS_DOMAIN_OBSERVER_FIXTURE_H

#include "domain_candidate_fixture.h"
#include "generator/domain_observer_cleanup.h"

namespace domain_observer_test {
struct Failure : std::exception {
  const char* what() const noexcept override { return "Controlled domain observer exception"; }
};
bool inject = false;
int target = 0;
Geometry* external_geometry = nullptr;
std::array<SubMesh*, 128> initial_links{};
bool captured = false, thrown = false;
unsigned live_before = 0, changed_before = 0;
const Failure* expected_exception = nullptr;

void BeforeExecute(int step, int patch) {
  using namespace domain_candidate_test;
  if (!inject || step != 2)
    return;
  const unsigned count = external_geometry->GetNumberPatches();
  Require(count > 0 && count <= initial_links.size(), "observer fixture geometry coverage");
  if (patch == 0 && !captured) {
    for (unsigned i = 0; i < count; ++i)
      initial_links[i] = external_geometry->GetPatch(i)->GetSubMesh();
    captured = true;
  }
  if (patch != target)
    return;
  for (unsigned i = 0; i < count; ++i) {
    auto* link = external_geometry->GetPatch(i)->GetSubMesh();
    live_before += link != nullptr;
    changed_before += link != initial_links[i];
  }
  try {
    throw Failure{};
  } catch (const Failure& error) {
    thrown = true;
    expected_exception = &error;
    state.attempts = state.denied = 0;
    state.active = true;
    state.remaining = 0;
    throw;
  }
}

void HelperCase(int layout, bool reverse, bool rethrow) {
  using namespace domain_candidate_test;
  state = domain_candidate_test::State{};
  unsigned owners = 0;
  bool identity = !rethrow;
  {
    Geometry geometry;
    std::unique_ptr<MeshAdaptive> active;
    GeneratorAdaptive::MeshVector retained;
    std::vector<SubMesh*> owned;
    const auto make_owner = [&owned]() {
      auto mesh = std::make_unique<MeshAdaptive>();
      for (unsigned count : {1U, 2U}) {
        auto sub = MakeMesh(count, true);
        owned.push_back(sub.get());
        mesh->InsertSubMeshAdaptiveByPosition(sub.release(), count == 1 ? 0 : 2);
      }
      return mesh;
    };
    if (layout != 1)
      active = make_owner();
    retained.emplace_back(-1, nullptr);
    if (layout != 0) {
      retained.emplace_back(1, make_owner());
      retained.emplace_back(2, make_owner());
    }
    owners = static_cast<unsigned>(owned.size());
    auto foreign_a = MakeMesh(1, true);
    auto foreign_b = MakeMesh(2, true);
    std::vector<SubMesh*> links{foreign_a.get(), nullptr};
    for (auto* sub : owned) {
      links.push_back(sub);
      links.push_back(sub);
    }
    links.push_back(foreign_b.get());
    links.push_back(nullptr);
    if (reverse)
      std::reverse(links.begin(), links.end());
    for (auto* link : links) {
      auto patch = std::make_unique<Patch>();
      patch->SetSubMesh(link);
      geometry.InsertPatch(std::move(patch));
    }
    geometry.InsertPatch(std::unique_ptr<Patch>{});
    state.active = true;
    if (rethrow) {
      const Failure* expected = nullptr;
      try {
        try {
          throw Failure{};
        } catch (const Failure& error) {
          expected = &error;
          state.remaining = 0;
          apmesh::generation::DetachOwnedDomainObservers(geometry, active.get(), retained);
          apmesh::generation::DetachOwnedDomainObservers(geometry, active.get(), retained);
          throw;
        }
      } catch (const Failure& error) {
        identity = &error == expected;
      }
    } else {
      state.remaining = 0;
      apmesh::generation::DetachOwnedDomainObservers(geometry, active.get(), retained);
      apmesh::generation::DetachOwnedDomainObservers(geometry, active.get(), retained);
    }
    Require(state.attempts == 0 && state.denied == 0 && state.remaining == 0 && identity,
            "observer cleanup allocated or replaced the exception");
    Require(std::none_of(state.records.begin(), state.records.begin() + state.size,
                         [](const Record& record) { return record.freed; }),
            "observer cleanup retired an owner");
    for (unsigned i = 0; i < links.size(); ++i) {
      const bool ours = std::find(owned.begin(), owned.end(), links[i]) != owned.end();
      Require(geometry.GetPatch(i)->GetSubMesh() == (ours ? nullptr : links[i]),
              "observer cleanup lost a null/foreign prefix or an owned alias");
    }
    Require(geometry.GetPatch(static_cast<unsigned>(links.size())) == nullptr,
            "observer cleanup changed the null patch slot");
    for (unsigned i = 0; i < owned.size(); ++i) {
      const unsigned count = i % 2 + 1;
      Require(owned[i]->GetNumberElements() == count && owned[i]->GetNumberNos() == 3 * count &&
                  owned[i]->GetNoh(0)->GetId() == 0,
              "observer cleanup mutated a live native owner");
    }
    Require(foreign_a->GetNumberElements() == 1 && foreign_b->GetNumberElements() == 2,
            "observer cleanup mutated foreign native objects");
  }
  state.active = false;
  Require(std::all_of(state.records.begin(), state.records.begin() + state.size,
                      [](const Record& record) { return record.freed; }),
          "native owner teardown retained observed storage");
  std::printf("domain_observers layout=%d reverse=%d rethrow=%d owners=%u owned_links=%u "
              "foreign_links=2 null_links=2 null_patches=1 attempts=0 identity=1\n",
              layout, reverse, rethrow, owners, 2 * owners);
}

int RunHelpers() {
  using namespace domain_candidate_test;
  try {
    for (int layout = 0; layout < 3; ++layout)
      for (bool reverse : {false, true})
        for (bool rethrow : {false, true})
          HelperCase(layout, reverse, rethrow);
    state = domain_candidate_test::State{};
    state.active = true;
    state.remaining = 0;
    bool caught = false;
    try {
      auto control = std::make_unique<SubMesh>();
    } catch (const std::bad_alloc&) {
      caught = true;
    }
    state.active = false;
    Require(caught && state.denied == 1 && state.attempts == 1,
            "observer allocation hook did not deny a native allocation");
    std::puts("domain_observer_hook attempts=1 denied=1");
    std::puts("domain_observer_contracts=12 complete=1");
    return 0;
  } catch (const std::exception& error) {
    state.active = false;
    std::fprintf(stderr, "Domain observer failure: %s\n", error.what());
    return 1;
  }
}

int RunFailure(const char* path, int patch_index) {
  using namespace domain_candidate_test;
  try {
    const auto config = LoadRuntimeConfig(path);
    ApplyRuntimeConfig(config);
    Timer timer(config.num_processes, config.num_threads, 12);
    Geometry geometry;
    Model model;
    PatchReader reader;
    model.SetGeometry(reader.ReaderFilePatches(&geometry, config.input_model));
    auto generator = std::make_unique<GeneratorAdaptive>();
    external_geometry = &geometry;
    initial_links.fill(nullptr);
    captured = thrown = false;
    live_before = changed_before = 0;
    expected_exception = nullptr;
    target = patch_index;
    inject = true;
    state = domain_candidate_test::State{};
    bool identity = false;
    try {
      generator->Generator(model, &timer);
    } catch (const Failure& error) {
      identity = &error == expected_exception;
    }
    expected_exception = nullptr;
    unsigned null_after = 0, nonnull_after_owner = 0, samples_after = 0;
    for (unsigned i = 0; i < geometry.GetNumberPatches(); ++i)
      null_after += geometry.GetPatch(i)->GetSubMesh() == nullptr;
    for (unsigned i = 0; i < geometry.GetNumberCurves(); ++i)
      samples_after += static_cast<unsigned>(geometry.GetCurve(i)->GetPoints().size());
    generator.reset();
    for (unsigned i = 0; i < geometry.GetNumberPatches(); ++i)
      nonnull_after_owner += geometry.GetPatch(i)->GetSubMesh() != nullptr;
    state.active = false;
    inject = false;
    std::printf(
        "domain_failure patches=%u target=%d live_before=%u changed_before=%u "
        "null_after=%u nonnull_after_owner=%u samples_after=%u attempts=%d denied=%d identity=%d\n",
        geometry.GetNumberPatches(), target, live_before, changed_before, null_after,
        nonnull_after_owner, samples_after, state.attempts, state.denied, identity);
    Require(thrown && captured && live_before == geometry.GetNumberPatches(),
            "domain exception coverage is missing");
    Require(null_after == live_before && nonnull_after_owner == 0,
            "owned patch observers remain after domain exception");
    Require(identity && state.attempts == 0 && state.denied == 0 && samples_after == 0,
            "domain propagation changed exception identity, allocated or retained samples");
    return 0;
  } catch (const std::exception& error) {
    state.active = false;
    inject = false;
    std::fprintf(stderr, "Domain observer failure: %s\n", error.what());
    return 1;
  }
}
} // namespace domain_observer_test

#endif // APMESH_TESTS_DOMAIN_OBSERVER_FIXTURE_H
