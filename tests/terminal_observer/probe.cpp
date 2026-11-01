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
#include <cstdio>
#include <cstring>
#include <memory>

#include "allocation_observer.h"
#include "execute_observer.h"
#include "typed_domain_failure_fixture.h"

namespace terminal_observer {
unsigned forwarded = 0;
bool Execute(AdvancingFront& front, const FaceList& previous) {
  const auto& context = front.GetRunStats();
  if (typed_domain_test::BeforeExecute(context.adaptive_step, context.patch_index))
    return false;
  ++forwarded;
  return front.execute(previous);
}
} // namespace terminal_observer

int main(int argc, char* argv[]) {
  using domain_candidate_test::Require;
  if (argc == 2 && std::strcmp(argv[1], "--observer-contracts") == 0) {
    typed_domain_test::Prepare(1);
    Require(!typed_domain_test::BeforeExecute(1, 1) && !typed_domain_test::BeforeExecute(2, 0) &&
                typed_domain_test::calls == 0,
            "Observer intercepted an unselected context");
    AdvancingFront front;
    front.SetAdaptiveContext(2, 1);
    Require(!terminal_observer::Execute(front, FaceList{}) && typed_domain_test::calls == 1 &&
                terminal_observer::forwarded == 0,
            "Observer did not intercept the live AFT selected context");
    typed_domain_test::inject = false;
    Require(!typed_domain_test::BeforeExecute(2, 1) && typed_domain_test::calls == 1,
            "Disabled observer still intercepted a context");
    domain_candidate_test::state = domain_candidate_test::State{};
    {
      std::unique_ptr<SubMesh> mesh(TerminalControlAllocateSubMesh());
      Require(mesh->GetNumberNos() == 0 && mesh->GetNumberElements() == 0 &&
                  domain_candidate_test::state.native_control_calls == 1 &&
                  domain_candidate_test::state.native_control_uncaught == 0,
              "Independent native SubMesh allocation was not live outside unwinding");
    }
    std::puts("terminal_native_submesh allocation=1 release=1 uncaught=0");
    domain_candidate_test::state = domain_candidate_test::State{};
    domain_candidate_test::state.active = true;
    domain_candidate_test::state.remaining = 0;
    bool denied = false;
    try {
      void* value = TerminalControlAllocate();
      TerminalControlRelease(value);
    } catch (const std::bad_alloc&) {
      denied = true;
    }
    domain_candidate_test::state.active = false;
    Require(denied && domain_candidate_test::state.attempts == 1 &&
                domain_candidate_test::state.denied == 1,
            "Actual independent allocation was not denied");
    std::puts("terminal_observer selected=1 excluded=2 disabled=1 live_aft=1 hook_denied=1");
    return 0;
  }
  if (argc == 2 && (std::strcmp(argv[1], "--instrument-release") == 0 ||
                    std::strcmp(argv[1], "--instrument-uaf") == 0)) {
    void* value = TerminalControlAllocate();
    Require(TerminalControlRead(value) == 73, "Instrument allocation was not live");
    TerminalControlRelease(value);
    if (std::strcmp(argv[1], "--instrument-uaf") == 0)
      return TerminalControlRead(value);
    std::puts("terminal_instrument release=1");
    return 0;
  }
  if (argc == 2 && std::strcmp(argv[1], "--typed-domain-contracts") == 0) {
    const int code = typed_domain_test::RunTypes();
    const auto& state = domain_candidate_test::state;
    std::printf("terminal_unwind_allocation calls=%d uncaught=%d attempts=%d denied=%d\n",
                state.native_control_calls, state.native_control_uncaught, state.unwind_attempts,
                state.denied);
    return code;
  }
  if (argc == 4 && std::strcmp(argv[1], "--typed-domain-library-config") == 0)
    return typed_domain_test::RunLibrary(argv[2], std::stoi(argv[3]));
  if (argc == 4 && std::strcmp(argv[1], "--typed-domain-cli-config") == 0) {
    typed_domain_test::Prepare(std::stoi(argv[3]));
    char config_flag[] = "--config";
    char* forwarded[] = {argv[0], config_flag, argv[2]};
    const int code = apmesh::application::RunApplication(3, forwarded);
    std::fprintf(stderr, "Typed CLI unwind allocations=%d\n",
                 domain_candidate_test::state.unwind_attempts);
    return code;
  }
  std::fprintf(stderr, "Error: unknown terminal observer invocation\n");
  return 2;
}
