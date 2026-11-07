#include "allocation_observer.h"

#include <cstdlib>
#include <exception>
#include <new>

#include "data/mesh/sub_mesh.h"

namespace domain_candidate_test {
State state;
}

namespace {
void ObserveAllocation() {
  auto& state = domain_candidate_test::state;
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
}
} // namespace

#if defined(AP_MESH_TERMINAL_ALLOCATOR_WRAP)
// GNU link wrapping observes calls before the sanitizer's own allocation functions.
// The CMake option restricts these Itanium ABI symbols to qualified Linux x86_64.
void operator delete(void* value, std::size_t size) noexcept;
void operator delete[](void* value, std::size_t size) noexcept;

extern "C" {
void* __real__Znwm(std::size_t size);
void __real__ZdlPv(void* value);
void __real__ZdaPv(void* value);
void __real__ZdlPvm(void* value, std::size_t size);
void __real__ZdaPvm(void* value, std::size_t size);

void* __wrap__Znwm(std::size_t size) {
  ObserveAllocation();
  return __real__Znwm(size == 0 ? 1 : size);
}
void* __wrap__Znam(std::size_t size) { return __wrap__Znwm(size); }
void __wrap__ZdlPv(void* value) noexcept { __real__ZdlPv(value); }
void __wrap__ZdaPv(void* value) noexcept { __real__ZdaPv(value); }
void __wrap__ZdlPvm(void* value, std::size_t size) noexcept { __real__ZdlPvm(value, size); }
void __wrap__ZdaPvm(void* value, std::size_t size) noexcept { __real__ZdaPvm(value, size); }
}
#else
void* operator new(std::size_t size) {
  ObserveAllocation();
  if (void* value = std::malloc(size == 0 ? 1 : size))
    return value;
  throw std::bad_alloc();
}
void* operator new[](std::size_t size) { return ::operator new(size); }
void operator delete(void* value) noexcept { std::free(value); }
void operator delete[](void* value) noexcept { std::free(value); }
void operator delete(void* value, std::size_t) noexcept { std::free(value); }
void operator delete[](void* value, std::size_t) noexcept { std::free(value); }
#endif

#if defined(AP_MESH_TERMINAL_ALLOCATOR_WRAP)
void TerminalControlAllocatorForms() {
  auto& state = domain_candidate_test::state;
  const auto previous = state;
  state = domain_candidate_test::State{};
  state.active = true;
  state.remaining = 100;
  void* volatile zero_size = ::operator new(0);
  ::operator delete(zero_size);
  void* array = ::operator new[](17);
  *static_cast<volatile unsigned char*>(array) = 73;
  ::operator delete[](array);
  void* scalar = ::operator new(17);
  *static_cast<volatile unsigned char*>(scalar) = 73;
  ::operator delete(scalar, std::size_t{17});
  array = ::operator new[](17);
  *static_cast<volatile unsigned char*>(array) = 73;
  ::operator delete[](array, std::size_t{17});
  const bool forwarded = state.attempts == 4 && state.denied == 0;
  state = domain_candidate_test::State{};
  state.active = true;
  state.remaining = 0;
  int caught = 0;
  try {
    scalar = ::operator new(17);
    ::operator delete(scalar);
  } catch (const std::bad_alloc&) {
    ++caught;
  }
  state.remaining = 0;
  try {
    array = ::operator new[](17);
    ::operator delete[](array);
  } catch (const std::bad_alloc&) {
    ++caught;
  }
  const bool denied = caught == 2 && state.attempts == 2 && state.denied == 2;
  state = previous;
  domain_candidate_test::Require(forwarded && denied,
                                 "Wrapped allocation forms lost forwarding or denial");
}

#endif

void* TerminalControlAllocate() { return new int(73); }
void TerminalControlRelease(void* pointer) { delete static_cast<int*>(pointer); }
int TerminalControlRead(void* pointer) { return *static_cast<volatile int*>(pointer); }

SubMesh* TerminalControlAllocateSubMesh() {
  ++domain_candidate_test::state.native_control_calls;
  domain_candidate_test::state.native_control_uncaught = std::uncaught_exceptions();
  // An explicit allocation-function call is observable even if a new-expression could be elided.
  void* storage = ::operator new(sizeof(SubMesh));
  try {
    return ::new (storage) SubMesh();
  } catch (...) {
    ::operator delete(storage);
    throw;
  }
}
