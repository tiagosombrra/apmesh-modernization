extern "C" void* SerialCrtLifetimeBegin();
extern "C" void SerialCrtLifetimeEnd(void* anchor);

namespace {
struct ExecutableLifetime {
  void* anchor;
  ExecutableLifetime() : anchor(SerialCrtLifetimeBegin()) {}
  ~ExecutableLifetime() { SerialCrtLifetimeEnd(anchor); }
};
} // namespace

// Enclose user-priority initialization and teardown; native late-allocation controls verify it.
#pragma init_seg(lib)
namespace {
ExecutableLifetime executable_lifetime;
}
