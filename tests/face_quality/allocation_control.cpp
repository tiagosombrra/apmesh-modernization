#include <cstddef>

#if defined(_MSC_VER)
__declspec(noinline)
#elif defined(__GNUC__)
__attribute__((noinline))
#endif
unsigned char* AllocateQualityControl() {
  return new unsigned char[64];
}
