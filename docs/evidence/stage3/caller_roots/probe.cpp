#include "input_output/patch_reader.h"
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <string>
#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif
#include <windows.h>

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};
std::string INPUT_MODEL;
int RANK_MPI = 0;

int main(int argc, char** argv) {
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
  if (argc != 3)
    return 2;
  std::puts("reader_root_audit=begin");
#if defined(_MSC_VER) && defined(_DEBUG)
  for (int report : {_CRT_WARN, _CRT_ERROR, _CRT_ASSERT}) {
    _CrtSetReportMode(report, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(report, _CRTDBG_FILE_STDERR);
  }
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  if (std::strcmp(argv[1], "clean") == 0) {
    auto patch = std::make_unique<PatchBezier>();
    std::printf("clean_patch_curves=%u\n", patch->GetNumBerCurves());
  } else if (std::strcmp(argv[1], "leak-control") == 0) {
    std::printf("deliberate_leak=%p\n", static_cast<void*>(new PatchBezier()));
  } else if (std::strcmp(argv[1], "direct") == 0) {
    PatchReader reader;
    auto result = reader.LoaderBezierPatchFile(argv[2]);
    std::printf("returned_patches=%zu\n", result.size());
    for (auto* patch : result)
      delete patch;
  } else if (std::strcmp(argv[1], "geometry") == 0) {
    Geometry geometry;
    PatchReader reader;
    reader.ReaderFilePatches(&geometry, argv[2]);
    std::printf("geometry_patches=%u curves=%u\n", geometry.GetNumberPatches(),
                geometry.GetNumberCurves());
  } else if (std::strcmp(argv[1], "unique-loader") == 0) {
    PatchReader reader;
    auto result = reader.LoaderBPFile(argv[2]);
    std::printf("unique_returned_patches=%zu\n", result.size());
  } else if (std::strcmp(argv[1], "repeat") == 0) {
    PatchReader reader;
    auto first = reader.LoaderBezierPatchFile(argv[2]);
    auto second = reader.LoaderBezierPatchFile(argv[2]);
    std::printf("first=%zu second=%zu same_first=%d\n", first.size(), second.size(),
                first.front() == second.front());
    for (auto* patch : second)
      delete patch;
  } else
    return 2;
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  return delta.lCounts[_NORMAL_BLOCK] == 0 && delta.lSizes[_NORMAL_BLOCK] == 0 ? 0 : 1;
#else
  return 0;
#endif
}
