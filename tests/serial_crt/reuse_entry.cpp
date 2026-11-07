#define main SerialCrtReuseEntry
#include "../attempt_metrics_probe.cpp"
#undef main

// Keep the original entry's C++ declaration and call in the same translation unit.
extern "C" int SerialCrtReuseRun(int argc, char** argv) { return SerialCrtReuseEntry(argc, argv); }
