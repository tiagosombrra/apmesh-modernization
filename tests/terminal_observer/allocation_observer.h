#ifndef APMESH_TESTS_TERMINAL_ALLOCATION_OBSERVER_H
#define APMESH_TESTS_TERMINAL_ALLOCATION_OBSERVER_H

#include <stdexcept>

// Supply the unchanged typed fixture's bounded allocation-observer interface.
namespace domain_candidate_test {
struct State {
  bool active = false;
  int remaining = -1, attempts = 0, denied = 0;
  bool deny_unwinding = false;
  int unwind_attempts = 0;
  int native_control_calls = 0, native_control_uncaught = -1;
};
extern State state;
inline void Require(bool condition, const char* message) {
  if (!condition)
    throw std::runtime_error(message);
}
} // namespace domain_candidate_test

void* TerminalControlAllocate();
void TerminalControlRelease(void* pointer);
int TerminalControlRead(void* pointer);
class SubMesh;
SubMesh* TerminalControlAllocateSubMesh();

#if defined(AP_MESH_TERMINAL_ALLOCATOR_WRAP)
void TerminalControlAllocatorForms();
void TerminalControlLeak();
#endif

#endif
