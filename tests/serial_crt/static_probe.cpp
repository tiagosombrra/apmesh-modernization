#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <new>
#include <crtdbg.h>
#include "application/run_application.h"
#include "application/runtime_config.h"
#include "input_output/input_validation.h"
#include <Windows.h>

#if !defined(_MSC_VER) || !defined(_DEBUG) || _ITERATOR_DEBUG_LEVEL != 2
#error The static-teardown observer requires MSVC checked Debug
#endif

namespace {
constexpr long capacity = 32768;
constexpr unsigned frames_per_request = 32;
struct Record {
  size_t bytes;
  void* frames[frames_per_request];
  unsigned short frame_count;
  bool live;
  bool watched;
};
Record records[capacity]{};
HANDLE output_handle = INVALID_HANDLE_VALUE;
int phase = 0;
long observer_errors = 0;
long denied = 0;
long reallocations = 0;
bool deny_next = false;
bool capturing = false;
bool in_hook = false;
_CRT_ALLOC_HOOK preceding_hook = nullptr;

// Teardown logging uses the process handle directly, after C++ stream owners retire.
struct Line {
  char text[1024]{};
  size_t length = 0;
  void Add(const char* value) {
    while (*value && length + 1 < sizeof(text))
      text[length++] = *value++;
  }
  void Number(unsigned long long value, unsigned base = 10) {
    char digits[32];
    unsigned count = 0;
    do {
      digits[count++] = "0123456789abcdef"[value % base];
      value /= base;
    } while (value);
    while (count && length + 1 < sizeof(text))
      text[length++] = digits[--count];
  }
  void Flush() {
    Add("\n");
    DWORD written = 0;
    if (output_handle == INVALID_HANDLE_VALUE ||
        !WriteFile(output_handle, text, static_cast<DWORD>(length), &written, nullptr) ||
        written != length)
      ++observer_errors;
  }
};

void State(const char* name) {
  unsigned blocks = 0;
  size_t bytes = 0;
  for (const auto& record : records)
    if (record.watched && record.live) {
      ++blocks;
      bytes += record.bytes;
    }
  Line line;
  line.Add("CRT_STATE name=");
  line.Add(name);
  line.Add(" phase=");
  line.Number(phase);
  line.Add(" blocks=");
  line.Number(blocks);
  line.Add(" bytes=");
  line.Number(bytes);
  line.Add(" errors=");
  line.Number(observer_errors);
  line.Add(" reallocations=");
  line.Number(reallocations);
  line.Flush();
}

void Frames(long request, void* const* frames, unsigned count, const char* kind) {
  for (unsigned i = 0; i < count; ++i) {
    HMODULE module = nullptr;
    char path[MAX_PATH]{};
    if (!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
                                GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                            reinterpret_cast<const char*>(frames[i]), &module) ||
        GetModuleFileNameA(module, path, MAX_PATH) == 0) {
      ++observer_errors;
      continue;
    }
    Line line;
    line.Add("CRT_FRAME kind=");
    line.Add(kind);
    line.Add(" request=");
    line.Number(request);
    line.Add(" rva=0x");
    line.Number(reinterpret_cast<uintptr_t>(frames[i]) - reinterpret_cast<uintptr_t>(module), 16);
    line.Add(" module=");
    line.Add(path);
    line.Flush();
  }
}

int Hook(int operation, void* storage, size_t bytes, int kind, long request,
         const unsigned char* file, int line) {
  if (in_hook) {
    ++observer_errors;
    return TRUE;
  }
  in_hook = true;
  const int accepted =
      preceding_hook ? preceding_hook(operation, storage, bytes, kind, request, file, line) : TRUE;
  if (!accepted) {
    ++observer_errors;
    in_hook = false;
    return accepted;
  }
  const int block_kind = _BLOCK_TYPE(kind);
  if (block_kind == _NORMAL_BLOCK || block_kind == _CLIENT_BLOCK) {
    if (operation == _HOOK_REALLOC) {
      // Ambiguous realloc outcomes cannot silently qualify this finite observer.
      ++reallocations;
    } else if (operation == _HOOK_ALLOC && capturing) {
      if (deny_next) {
        deny_next = false;
        ++denied;
        in_hook = false;
        return FALSE;
      }
      if (request <= 0 || request >= capacity) {
        ++observer_errors;
      } else {
        auto& record = records[request];
        if (record.live)
          ++observer_errors;
        record.bytes = bytes;
        record.frame_count = CaptureStackBackTrace(1, frames_per_request, record.frames, nullptr);
        record.live = true;
        if (!record.frame_count)
          ++observer_errors;
      }
    } else if (operation == _HOOK_FREE && storage) {
      const auto actual_size = _msize_dbg(storage, block_kind);
      long released_request = 0;
      if (actual_size > (std::numeric_limits<unsigned>::max)() ||
          !_CrtIsMemoryBlock(storage, static_cast<unsigned>(actual_size), &released_request,
                             nullptr, nullptr)) {
        ++observer_errors;
      } else if (released_request > 0 && released_request < capacity) {
        auto& record = records[released_request];
        if (record.watched) {
          Line event;
          event.Add("CRT_FREE request=");
          event.Number(released_request);
          event.Add(" phase=");
          event.Number(phase);
          event.Add(" bytes=");
          event.Number(record.bytes);
          event.Flush();
          void* frames[frames_per_request];
          const auto count = CaptureStackBackTrace(1, frames_per_request, frames, nullptr);
          Frames(released_request, frames, count, "release");
        }
        record.live = false;
      }
    }
  }
  in_hook = false;
  return TRUE;
}

void AfterLazyStatics() {
  phase = 3;
  State("after_lazy_statics");
}

struct ControlOwner {
  unsigned char* storage = nullptr;
  ~ControlOwner() {
    delete[] storage;
    if (phase) {
      Line line;
      line.Add("CRT_CONTROL_OWNER destroyed=1");
      line.Flush();
    }
  }
};
ControlOwner control_owner;
void* deliberate_retention = nullptr;

void PathOwner(const char* name, const std::string& owner) {
  if (!_CrtIsValidHeapPointer(owner.data())) {
    ++observer_errors;
    return;
  }
  const auto bytes = _msize_dbg(const_cast<char*>(owner.data()), _NORMAL_BLOCK);
  long request = 0;
  if (bytes > (std::numeric_limits<unsigned>::max)() ||
      !_CrtIsMemoryBlock(owner.data(), static_cast<unsigned>(bytes), &request, nullptr, nullptr)) {
    ++observer_errors;
    return;
  }
  Line line;
  line.Add("CRT_OWNER name=");
  line.Add(name);
  line.Add(" request=");
  line.Number(request);
  line.Add(" bytes=");
  line.Number(bytes);
  line.Flush();
}
} // namespace

extern "C" void SerialCrtAfterExecutableStatics() {
  if (phase) {
    phase = 4;
    State("after_executable_statics");
  }
}

int main(int argc, char** argv) {
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
  output_handle = GetStdHandle(STD_ERROR_HANDLE);
  std::setvbuf(stdout, nullptr, _IONBF, 0);
  std::setvbuf(stderr, nullptr, _IONBF, 0);
  for (int kind : std::array{_CRT_WARN, _CRT_ERROR, _CRT_ASSERT}) {
    _CrtSetReportMode(kind, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(kind, _CRTDBG_FILE_STDERR);
  }
  if (argc < 2 || std::atexit(AfterLazyStatics) != 0)
    return 64;
  auto* anchor = new unsigned char[1];
  _CrtMemState before{};
  _CrtMemCheckpoint(&before);
  preceding_hook = _CrtSetAllocHook(Hook);
  capturing = true;
  phase = 1;
  int result = 0;
  if (argc == 3 && std::strcmp(argv[1], "--config") == 0) {
    result = apmesh::application::RunApplication(argc, argv);
    PathOwner("INPUT_MODEL", INPUT_MODEL);
    PathOwner("NAME_MODEL", NAME_MODEL);
  } else if (argc == 2 && std::strcmp(argv[1], "keys-control") == 0) {
    apmesh::io::ValidateConfigValue("NUM_THREADS", "1");
  } else if (argc == 2 && std::strcmp(argv[1], "static-release-control") == 0) {
    control_owner.storage = new unsigned char[64];
  } else if (argc == 2 && std::strcmp(argv[1], "static-leak-control") == 0) {
    deliberate_retention = new unsigned char[64];
  } else if (argc == 2 && std::strcmp(argv[1], "release-control") == 0) {
    auto* storage = new unsigned char[64];
    delete[] storage;
  } else if (argc == 2 && std::strcmp(argv[1], "hook-control") == 0) {
    deny_next = true;
    bool caught = false;
    try {
      auto* storage = new unsigned char[64];
      delete[] storage;
    } catch (const std::bad_alloc&) {
      caught = true;
    }
    if (!caught || denied != 1)
      result = 3;
  } else {
    result = 64;
  }
  capturing = false;
  for (long request = 1; request < capacity; ++request) {
    auto& record = records[request];
    if (!record.live)
      continue;
    record.watched = true;
    Line line;
    line.Add("CRT_WATCH request=");
    line.Number(request);
    line.Add(" bytes=");
    line.Number(record.bytes);
    line.Flush();
    Frames(request, record.frames, record.frame_count, "allocation");
  }
  std::fputs("STATIC_CRT_DUMP_BEGIN\n", stderr);
  _CrtMemDumpAllObjectsSince(&before);
  std::fputs("STATIC_CRT_DUMP_END\n", stderr);
  State("entry_return");
  std::printf("STATIC_CRT app_exit=%d heap_valid=%d iterator_level=%d denied=%ld errors=%ld\n",
              result, _CrtCheckMemory() != 0, _ITERATOR_DEBUG_LEVEL, denied, observer_errors);
  delete[] anchor;
  phase = 2;
  // Keep the hook active through executable and dependent runtime static teardown.
  return observer_errors || reallocations ? 3 : result;
}
