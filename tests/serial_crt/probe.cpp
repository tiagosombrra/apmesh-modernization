#include <array>
#include <cstdio>
#include <cstring>
#include <memory>
#include <new>
#include <crtdbg.h>
#include <Windows.h>
#include "application/run_application.h"

#if !defined(_MSC_VER) || !defined(_DEBUG) || _ITERATOR_DEBUG_LEVEL != 2
#error The complete-entry CRT observer requires MSVC Debug with checked iterators
#endif

namespace {
long allocation_attempts = 0;
long denied_allocations = 0;
bool deny_next = false;
_CRT_ALLOC_HOOK previous_hook = nullptr;
void* retained_control = nullptr;

int AllocationHook(int operation, void* storage, size_t size, int kind, long request,
                   const unsigned char* file, int line) {
  const int block_kind = _BLOCK_TYPE(kind);
  if ((operation == _HOOK_ALLOC || operation == _HOOK_REALLOC) &&
      (block_kind == _NORMAL_BLOCK || block_kind == _CLIENT_BLOCK)) {
    ++allocation_attempts;
    if (deny_next) {
      deny_next = false;
      ++denied_allocations;
      return FALSE;
    }
  }
  return previous_hook ? previous_hook(operation, storage, size, kind, request, file, line) : TRUE;
}

long long Difference(size_t after, size_t before) {
  return static_cast<long long>(after) - static_cast<long long>(before);
}
} // namespace

int main(int argc, char** argv) {
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
  std::setvbuf(stdout, nullptr, _IONBF, 0);
  std::setvbuf(stderr, nullptr, _IONBF, 0);
  for (int report : std::array{_CRT_WARN, _CRT_ERROR, _CRT_ASSERT}) {
    _CrtSetReportMode(report, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(report, _CRTDBG_FILE_STDERR);
  }
  if (argc < 2) {
    std::fputs("One control or the production --config invocation is required\n", stderr);
    return 64;
  }
  const bool replacement = argc == 2 && std::strcmp(argv[1], "replacement-control") == 0;
  auto baseline = replacement ? std::make_unique<unsigned char[]>(64) : nullptr;
  // Keep the checkpoint's newest block alive until the newer-object dump completes.
  auto checkpoint_anchor = std::make_unique<unsigned char[]>(1);
  _CrtMemState before{}, after{};
  _CrtMemCheckpoint(&before);
  previous_hook = _CrtSetAllocHook(AllocationHook);
  int result = 0;
  bool caught_denial = false;
  if (argc == 3 && std::strcmp(argv[1], "--config") == 0) {
    // The actual entry returns after Execute-local Geometry and outer Generator teardown.
    result = apmesh::application::RunApplication(argc, argv);
  } else if (argc == 2 && std::strcmp(argv[1], "release-control") == 0) {
    auto* storage = new unsigned char[64];
    storage[0] = 73;
    delete[] storage;
  } else if (argc == 2 && (std::strcmp(argv[1], "leak-control") == 0 || replacement)) {
    // Equal-sized baseline retirement challenges net-difference-only leak detection.
    baseline.reset();
    retained_control = new unsigned char[64];
    std::printf("retained_control=%p\n", retained_control);
  } else if (argc == 2 && std::strcmp(argv[1], "hook-control") == 0) {
    deny_next = true;
    try {
      auto* storage = new unsigned char[64];
      delete[] storage;
    } catch (const std::bad_alloc&) {
      caught_denial = true;
    }
    if (!caught_denial || denied_allocations != 1 || allocation_attempts != 1)
      result = 3;
  } else {
    std::fputs("Unknown CRT observer invocation\n", stderr);
    result = 64;
  }
  _CrtSetAllocHook(previous_hook);
  _CrtMemCheckpoint(&after);
  const bool heap_valid = _CrtCheckMemory() != 0;
  const auto normal_blocks =
      Difference(after.lCounts[_NORMAL_BLOCK], before.lCounts[_NORMAL_BLOCK]);
  const auto normal_bytes = Difference(after.lSizes[_NORMAL_BLOCK], before.lSizes[_NORMAL_BLOCK]);
  const auto client_blocks =
      Difference(after.lCounts[_CLIENT_BLOCK], before.lCounts[_CLIENT_BLOCK]);
  const auto client_bytes = Difference(after.lSizes[_CLIENT_BLOCK], before.lSizes[_CLIENT_BLOCK]);
  std::printf("SERIAL_CRT app_exit=%d heap_valid=%d iterator_level=%d allocations=%ld denied=%ld "
              "caught=%d normal_blocks_delta=%lld normal_bytes_delta=%lld "
              "client_blocks_delta=%lld client_bytes_delta=%lld\n",
              result, heap_valid, _ITERATOR_DEBUG_LEVEL, allocation_attempts, denied_allocations,
              caught_denial, normal_blocks, normal_bytes, client_blocks, client_bytes);
  // Always dump newer live blocks: a zero net difference can hide replacement retention.
  std::fputs("SERIAL_CRT_DUMP_BEGIN\n", stderr);
  _CrtMemDumpAllObjectsSince(&before);
  std::fputs("SERIAL_CRT_DUMP_END\n", stderr);
  checkpoint_anchor.reset();
  if (!heap_valid || normal_blocks != 0 || normal_bytes != 0 || client_blocks != 0 ||
      client_bytes != 0)
    return result == 0 ? 2 : result;
  return result;
}
