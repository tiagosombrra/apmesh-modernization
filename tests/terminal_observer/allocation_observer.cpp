#include "allocation_observer.h"

#include <cstdlib>
#include <exception>
#include <new>

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

void* TerminalControlAllocate() { return new int(73); }
void TerminalControlRelease(void* pointer) { delete static_cast<int*>(pointer); }
int TerminalControlRead(void* pointer) { return *static_cast<volatile int*>(pointer); }
