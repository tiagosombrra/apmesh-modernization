#include <cstddef>
#include <cstdio>
#include <new>
#include <string>

bool deny = false;
unsigned denied = 0;
extern "C" void* __real__Znwm(std::size_t);
extern "C" void* __wrap__Znwm(std::size_t size) {
  if (deny) {
    ++denied;
    throw std::bad_alloc();
  }
  return __real__Znwm(size);
}
int main() {
  const std::string source(257, 's');
  bool caught = false;
  deny = true;
  try {
    const std::string copy = source;
    std::printf("copied=%zu\n", copy.size());
  } catch (const std::bad_alloc&) {
    caught = true;
  }
  deny = false;
  std::printf("caught=%u denied=%u\n", unsigned(caught), denied);
  return caught && denied == 1 ? 0 : 1;
}
