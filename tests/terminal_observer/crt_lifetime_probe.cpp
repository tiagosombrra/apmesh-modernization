// Preserve the existing terminal caller and lifetime-calibration bodies under test-only names.
#define main TerminalObserverEntry
#include "probe.cpp"
#undef main

#define main SerialCrtCalibrationEntry
#include "../serial_crt/lifetime_probe.cpp"
#undef main

int main(int argc, char** argv) {
  if (argc == 3 && std::strcmp(argv[1], "--lifetime-control") == 0)
    return SerialCrtCalibrationEntry(argc, argv);
  app_exit = TerminalObserverEntry(argc, argv);
  std::printf("LIFETIME_MAIN app_exit=%d iterator_level=%d attempts=%ld denied=%ld caught=%d\n",
              app_exit, _ITERATOR_DEBUG_LEVEL, attempts, denied, caught);
  return app_exit;
}
