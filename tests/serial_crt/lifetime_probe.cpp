#include <array>
#include <cstdio>
#include <cstring>
#include <memory>
#include <new>
#include <crtdbg.h>
#include "application/run_application.h"
#include <Windows.h>

#if !defined(_MSC_VER) || !defined(_DEBUG) || _ITERATOR_DEBUG_LEVEL != 2
#error The executable-lifetime CRT observer requires MSVC checked Debug
#endif

#if defined(AP_MESH_CRT_REUSE_ENTRY)
extern "C" int SerialCrtReuseRun(int argc, char** argv);
#endif

namespace {
_CrtMemState before{};
HANDLE output_handle = INVALID_HANDLE_VALUE;
int app_exit = 0;
int late_mode = 0;
long attempts = 0;
long denied = 0;
bool caught = false;
bool active = false;
void* deliberate_retention = nullptr;
_CRT_ALLOC_HOOK preceding_hook = nullptr;

struct Line {
  char text[512]{};
  unsigned length = 0;
  void Add(const char* value) {
    while (*value && length + 1 < sizeof(text))
      text[length++] = *value++;
  }
  void Number(long long value) {
    auto magnitude = static_cast<unsigned long long>(value);
    if (value < 0) {
      Add("-");
      magnitude = 0 - magnitude;
    }
    char digits[32];
    unsigned count = 0;
    do {
      digits[count++] = static_cast<char>('0' + magnitude % 10);
      magnitude /= 10;
    } while (magnitude);
    while (count && length + 1 < sizeof(text))
      text[length++] = digits[--count];
  }
  void Flush() {
    Add("\n");
    DWORD written = 0;
    if (!WriteFile(output_handle, text, length, &written, nullptr) || written != length)
      TerminateProcess(GetCurrentProcess(), 74);
  }
};

long long Difference(size_t after, size_t original) {
  return static_cast<long long>(after) - static_cast<long long>(original);
}

void ObserveAllocation(const unsigned char* storage, const char* phase) {
  long request = 0;
  const bool observed = _CrtIsMemoryBlock(storage, 64, &request, nullptr, nullptr) != 0;
  Line line;
  line.Add("LIFETIME_ALLOCATION phase=");
  line.Add(phase);
  line.Add(" observed=");
  line.Number(observed);
  line.Add(" request=");
  line.Number(request);
  line.Add(" bytes=64");
  line.Flush();
}

int DenialHook(int operation, void* storage, size_t size, int kind, long request,
               const unsigned char* file, int line) {
  if (operation == _HOOK_ALLOC &&
      (_BLOCK_TYPE(kind) == _NORMAL_BLOCK || _BLOCK_TYPE(kind) == _CLIENT_BLOCK)) {
    ++attempts;
    if (attempts == 2) {
      ++denied;
      return FALSE;
    }
  }
  return preceding_hook ? preceding_hook(operation, storage, size, kind, request, file, line)
                        : TRUE;
}

struct HookScope {
  HookScope() { preceding_hook = _CrtSetAllocHook(DenialHook); }
  ~HookScope() { _CrtSetAllocHook(preceding_hook); }
};

struct GlobalOwner {
  std::unique_ptr<unsigned char[]> storage;
  ~GlobalOwner() {
    if (late_mode == 1) {
      auto temporary = std::make_unique<unsigned char[]>(64);
      ObserveAllocation(temporary.get(), "shutdown");
      temporary[0] = 73;
    } else if (late_mode == 2) {
      deliberate_retention = new unsigned char[64];
      ObserveAllocation(static_cast<unsigned char*>(deliberate_retention), "shutdown");
    }
    Line line;
    line.Add("LIFETIME_OWNER destroyed=1 late_mode=");
    line.Number(late_mode);
    line.Flush();
  }
};
GlobalOwner global_owner;
} // namespace

extern "C" void* SerialCrtLifetimeBegin() {
  output_handle = GetStdHandle(STD_ERROR_HANDLE);
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
  std::setvbuf(stdout, nullptr, _IONBF, 0);
  std::setvbuf(stderr, nullptr, _IONBF, 0);
  for (int kind : std::array{_CRT_WARN, _CRT_ERROR, _CRT_ASSERT}) {
    _CrtSetReportMode(kind, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(kind, _CRTDBG_FILE_STDERR);
  }
  // The early lifetime owner keeps the newest checkpoint block alive through the dump.
  auto* anchor = new unsigned char[1];
  _CrtMemCheckpoint(&before);
  active = true;
  return anchor;
}

extern "C" void SerialCrtLifetimeEnd(void* anchor) {
  _CrtMemState after{};
  _CrtMemCheckpoint(&after);
  const bool heap_valid = _CrtCheckMemory() != 0;
  Line begin;
  begin.Add("LIFETIME_DUMP_BEGIN");
  begin.Flush();
  _CrtMemDumpAllObjectsSince(&before);
  Line end;
  end.Add("LIFETIME_DUMP_END");
  end.Flush();
  Line result;
  result.Add("LIFETIME_FINAL active=");
  result.Number(active);
  result.Add(" heap_valid=");
  result.Number(heap_valid);
  result.Add(" normal_blocks_delta=");
  result.Number(Difference(after.lCounts[_NORMAL_BLOCK], before.lCounts[_NORMAL_BLOCK]));
  result.Add(" normal_bytes_delta=");
  result.Number(Difference(after.lSizes[_NORMAL_BLOCK], before.lSizes[_NORMAL_BLOCK]));
  result.Add(" client_blocks_delta=");
  result.Number(Difference(after.lCounts[_CLIENT_BLOCK], before.lCounts[_CLIENT_BLOCK]));
  result.Add(" client_bytes_delta=");
  result.Number(Difference(after.lSizes[_CLIENT_BLOCK], before.lSizes[_CLIENT_BLOCK]));
  result.Flush();
  delete[] static_cast<unsigned char*>(anchor);
}

int main(int argc, char** argv) {
  if (argc == 3 && std::strcmp(argv[1], "--lifetime-control") == 0) {
    if (std::strcmp(argv[2], "release") == 0) {
      auto storage = std::make_unique<unsigned char[]>(64);
      ObserveAllocation(storage.get(), "main");
      storage[0] = 73;
    } else if (std::strcmp(argv[2], "global-release") == 0) {
      global_owner.storage = std::make_unique<unsigned char[]>(64);
      ObserveAllocation(global_owner.storage.get(), "main");
    } else if (std::strcmp(argv[2], "late-release") == 0) {
      late_mode = 1;
    } else if (std::strcmp(argv[2], "late-retention") == 0) {
      late_mode = 2;
    } else if (std::strcmp(argv[2], "retention") == 0) {
      deliberate_retention = new unsigned char[64];
      ObserveAllocation(static_cast<unsigned char*>(deliberate_retention), "main");
    } else if (std::strcmp(argv[2], "denial") == 0) {
      try {
        HookScope hook;
        auto first = std::make_unique<unsigned char[]>(64);
        ObserveAllocation(first.get(), "main");
        auto second = std::make_unique<unsigned char[]>(64);
      } catch (const std::bad_alloc&) {
        caught = true;
      }
      if (attempts != 2 || denied != 1 || !caught)
        app_exit = 3;
    } else {
      app_exit = 64;
    }
  } else {
#if defined(AP_MESH_CRT_REUSE_ENTRY)
    app_exit = SerialCrtReuseRun(argc, argv);
#else
    app_exit = apmesh::application::RunApplication(argc, argv);
#endif
  }
  std::printf("LIFETIME_MAIN app_exit=%d iterator_level=%d attempts=%ld denied=%ld caught=%d\n",
              app_exit, _ITERATOR_DEBUG_LEVEL, attempts, denied, caught);
  return app_exit;
}
