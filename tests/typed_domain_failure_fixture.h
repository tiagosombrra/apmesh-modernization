#ifndef APMESH_TESTS_TYPED_DOMAIN_FAILURE_FIXTURE_H
#define APMESH_TESTS_TYPED_DOMAIN_FAILURE_FIXTURE_H

#include "adapter/domain_generation_error.h"
#include "domain_candidate_fixture.h"

namespace typed_domain_test {
using Error = apmesh::adaptation::DomainGenerationError;
bool inject = false, captured = false;
int target = 0, calls = 0;
Geometry* geometry = nullptr;
std::array<SubMesh*, 128> initial{};
unsigned changed = 0, published = 0;

bool BeforeExecute(int step, int patch) {
  using namespace domain_candidate_test;
  if (!inject || step != 2)
    return false;
  if (geometry != nullptr && patch == 0 && !captured) {
    Require(geometry->GetNumberPatches() <= initial.size(), "typed fixture patch capacity");
    for (unsigned i = 0; i < geometry->GetNumberPatches(); ++i)
      initial[i] = geometry->GetPatch(i)->GetSubMesh();
    captured = true;
  }
  if (patch != target)
    return false;
  if (geometry != nullptr && calls == 0)
    for (unsigned i = 0; i < geometry->GetNumberPatches(); ++i) {
      auto* value = geometry->GetPatch(i)->GetSubMesh();
      published += value != nullptr;
      changed += value != initial[i];
    }
  ++calls;
  std::fprintf(stderr, "Typed domain control: step=2 patch=%d\n", target);
  return true;
}

void Prepare(int patch, Geometry* external = nullptr) {
  inject = true;
  captured = false;
  target = patch;
  calls = 0;
  geometry = external;
  changed = published = 0;
  initial.fill(nullptr);
  domain_candidate_test::state = domain_candidate_test::State{};
  domain_candidate_test::state.deny_unwinding = true;
}

int RunTypes() {
  using namespace domain_candidate_test;
  try {
    unsigned index = 0;
    for (const auto& context :
         std::array<std::array<int, 3>, 3>{{{-1, -1, 0}, {2, 0, 0}, {4, 1, 3}}})
      for (unsigned length : {0U, 17U, 257U}) {
        state = domain_candidate_test::State{};
        std::string status(length, 'x');
        if (length == 17)
          status = "generation_failed";
        const std::string expected = status;
        bool identity = false, payload = false;
        state.active = state.deny_unwinding = true;
        state.remaining = 0;
        try {
          throw Error(context[0], context[1], context[2], std::move(status));
        } catch (const Error& error) {
          status.clear();
          payload = error.Step() == context[0] && error.PatchIndex() == context[1] &&
                    error.RetryIndex() == context[2] && error.Status() == expected &&
                    std::strcmp(error.what(), "domain generation failed") == 0;
          const auto* address = &error;
          try {
            throw;
          } catch (const Error& same) {
            identity = &same == address;
          }
        }
        state.active = state.deny_unwinding = false;
        Require(payload && identity && state.attempts == 0 && state.unwind_attempts == 0 &&
                    state.denied == 0,
                "typed payload move, lifetime or nonallocating propagation failed");
        std::printf("typed_error case=%u status_bytes=%u payload=1 identity=1 allocations=0\n",
                    index++, length);
      }
    struct Signal {};
    struct AllocationProbe {
      bool& detected;
      ~AllocationProbe() noexcept {
        try {
          auto value = std::make_unique<SubMesh>();
        } catch (const std::bad_alloc&) {
          detected = true;
        }
      }
    };
    state = domain_candidate_test::State{};
    state.deny_unwinding = true;
    bool detected = false, caught = false;
    try {
      AllocationProbe probe{detected};
      Require(&probe.detected == &detected, "unwind allocation probe is not attached");
      throw Signal{};
    } catch (const Signal&) {
      caught = true;
    }
    state.deny_unwinding = false;
    Require(detected && caught && state.unwind_attempts == 1 && state.denied == 1,
            "native allocation during unwinding was not denied");
    std::puts("typed_unwind_hook attempts=1 denied=1");
    std::puts("typed_error_contracts=9 complete=1");
    return 0;
  } catch (const std::exception& error) {
    state.active = state.deny_unwinding = false;
    std::fprintf(stderr, "Typed domain failure: %s\n", error.what());
    return 1;
  }
}

int RunLibrary(const char* path, int patch) {
  using namespace domain_candidate_test;
  try {
    const auto config = LoadRuntimeConfig(path);
    ApplyRuntimeConfig(config);
    Timer timer(config.num_processes, config.num_threads, 12);
    Geometry external;
    Model model;
    PatchReader reader;
    model.SetGeometry(reader.ReaderFilePatches(&external, config.input_model));
    auto generator = std::make_unique<GeneratorAdaptive>();
    Prepare(patch, &external);
    bool payload = false;
    try {
      generator->Generator(model, &timer);
    } catch (const Error& error) {
      payload = error.Step() == 2 && error.PatchIndex() == patch && error.RetryIndex() == 0 &&
                error.Status() == "generation_failed" &&
                std::strcmp(error.what(), "domain generation failed") == 0;
    }
    unsigned detached = 0, remaining = 0, samples = 0;
    for (unsigned i = 0; i < external.GetNumberPatches(); ++i)
      detached += external.GetPatch(i)->GetSubMesh() == nullptr;
    for (unsigned i = 0; i < external.GetNumberCurves(); ++i)
      samples += static_cast<unsigned>(external.GetCurve(i)->GetPoints().size());
    state.deny_unwinding = false;
    state.active = true;
    state.remaining = 0;
    generator.reset();
    state.active = false;
    inject = false;
    for (unsigned i = 0; i < external.GetNumberPatches(); ++i)
      remaining += external.GetPatch(i)->GetSubMesh() != nullptr;
    std::printf("typed_library patches=%u target=%d calls=%d changed_before=%u detached=%u "
                "nonnull_after_owner=%u samples=%u allocations=%d unwind_allocations=%d denied=%d "
                "payload=%d\n",
                external.GetNumberPatches(), patch, calls, changed, detached, remaining, samples,
                state.attempts, state.unwind_attempts, state.denied, payload);
    Require(payload && captured && published == external.GetNumberPatches() &&
                detached == published && remaining == 0 && samples == 0 && state.attempts == 0 &&
                state.unwind_attempts == 0 && state.denied == 0,
            "typed library failure lost context, cleanup or nonallocating unwinding");
    return 0;
  } catch (const std::exception& error) {
    state.active = state.deny_unwinding = false;
    inject = false;
    std::fprintf(stderr, "Typed domain failure: %s\n", error.what());
    return 1;
  }
}
} // namespace typed_domain_test

#endif // APMESH_TESTS_TYPED_DOMAIN_FAILURE_FIXTURE_H
