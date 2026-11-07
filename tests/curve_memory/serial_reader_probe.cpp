#include "input_output/patch_reader.h"

#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <type_traits>
#include <vector>
#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif
#if defined(_WIN32)
#include <windows.h>
#endif

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};
std::string INPUT_MODEL;
int RANK_MPI = 0;

namespace {
void Require(bool ok, const char* message) {
  if (!ok) {
    std::fprintf(stderr, "Serial reader contract failed: %s\n", message);
    std::exit(1);
  }
}
template <class T> PatchBezier* Observer(T& owner) {
  if constexpr (std::is_pointer_v<T>)
    return owner;
  else
    return owner.get();
}
template <class T> void DestroyOriginal(T& owner) {
  if constexpr (std::is_pointer_v<T>)
    delete owner;
}
std::uint64_t Bits(double value) {
  std::uint64_t bits;
  std::memcpy(&bits, &value, sizeof(bits));
  return bits;
}
bool LookupContracts() {
  using PublicLookup = PointAdaptive (PatchReader::*)(std::vector<PointAdaptive>, unsigned long);
  static_assert(std::is_same_v<decltype(&PatchReader::GetPointVectorControlPoints), PublicLookup>);
  PatchReader reader;
  std::vector<PointAdaptive> points{{1.25, -0.0, 3.5, 7}, {8, 9, 10, 7}, {-3, 4, 5, 9}};
  auto first = reader.GetPointVectorControlPoints(points, 7);
  Require(first.GetId() == 7 && Bits(first.GetX()) == Bits(1.25) &&
              Bits(first.GetY()) == Bits(-0.0) && Bits(first.GetZ()) == Bits(3.5),
          "lookup must retain the first duplicate ID and exact scalar bits");
  first.SetX(42);
  auto last = reader.GetPointVectorControlPoints(points, 9);
  Require(last.GetId() == 9 && Bits(last.GetX()) == Bits(-3.0) && Bits(last.GetY()) == Bits(4.0) &&
              Bits(last.GetZ()) == Bits(5.0),
          "lookup lost its later matching control");
  for (const auto& missing :
       {reader.GetPointVectorControlPoints(points, 99), reader.GetPointVectorControlPoints({}, 7)})
    Require(missing.GetId() == static_cast<unsigned long>(-1) &&
                Bits(missing.GetX()) == Bits(0.0) && Bits(missing.GetY()) == Bits(0.0) &&
                Bits(missing.GetZ()) == Bits(0.0),
            "missing and empty lookups must retain the original default point");
  Require(points.size() == 3 && points[0].GetId() == 7 && points[1].GetId() == 7 &&
              points[2].GetId() == 9 && Bits(points[0].GetX()) == Bits(1.25) &&
              Bits(points[0].GetY()) == Bits(-0.0) && Bits(points[1].GetX()) == Bits(8.0),
          "lookup result must not alias or mutate the source vector");
  std::puts(
      "control_lookup duplicate=1 later=1 missing=1 empty=1 independent=1 public_value_api=1");
  return true;
}
std::array<PointAdaptive, 16> Controls(PatchBezier* p) {
  return {p->GetPt00(), p->GetPt10(), p->GetPt20(), p->GetPt30(), p->GetPt01(), p->GetPt11(),
          p->GetPt21(), p->GetPt31(), p->GetPt02(), p->GetPt12(), p->GetPt22(), p->GetPt32(),
          p->GetPt03(), p->GetPt13(), p->GetPt23(), p->GetPt33()};
}
bool Live(Geometry& geometry) {
  for (unsigned int i = 0; i < geometry.GetNumberPatches(); ++i) {
    auto* p = static_cast<PatchBezier*>(geometry.GetPatch(i));
    if (p == nullptr || p->GetNumBerCurves() != 4)
      return false;
    for (unsigned int s = 0; s < 4; ++s) {
      bool found = false;
      for (unsigned int c = 0; c < geometry.GetNumberCurves(); ++c)
        found |= geometry.GetCurve(c) == p->GetCurve(s);
      if (!found)
        return false;
      found = false;
      for (unsigned int j = 0; j < p->GetCurve(s)->GetNumBerPatches(); ++j)
        found |= p->GetCurve(s)->GetPatch(j) == p;
      if (!found)
        return false;
    }
  }
  for (unsigned int c = 0; c < geometry.GetNumberCurves(); ++c) {
    auto* curve = geometry.GetCurve(c);
    if (curve == nullptr)
      return false;
    for (unsigned int j = 0; j < curve->GetNumBerPatches(); ++j) {
      bool found = false;
      for (unsigned int p = 0; p < geometry.GetNumberPatches(); ++p)
        found |= curve->GetPatch(j) == geometry.GetPatch(p);
      if (!found)
        return false;
    }
  }
  return true;
}
struct Prefix {
  std::vector<Patch*> patches;
  std::vector<CurveAdaptive*> curves;
  std::vector<std::vector<Patch*>> incidence;
  explicit Prefix(Geometry& geometry) {
    for (unsigned int i = 0; i < geometry.GetNumberPatches(); ++i)
      patches.push_back(geometry.GetPatch(i));
    for (unsigned int i = 0; i < geometry.GetNumberCurves(); ++i) {
      auto* curve = geometry.GetCurve(i);
      curves.push_back(curve);
      incidence.emplace_back();
      for (unsigned int j = 0; j < curve->GetNumBerPatches(); ++j)
        incidence.back().push_back(curve->GetPatch(j));
    }
  }
  bool Matches(Geometry& geometry) const {
    if (geometry.GetNumberPatches() < patches.size() || geometry.GetNumberCurves() < curves.size())
      return false;
    for (unsigned int i = 0; i < patches.size(); ++i)
      if (geometry.GetPatch(i) != patches[i])
        return false;
    for (unsigned int i = 0; i < curves.size(); ++i) {
      if (geometry.GetCurve(i) != curves[i] || curves[i]->GetNumBerPatches() < incidence[i].size())
        return false;
      for (unsigned int j = 0; j < incidence[i].size(); ++j)
        if (curves[i]->GetPatch(j) != incidence[i][j])
          return false;
    }
    return Live(geometry);
  }
};
void Trace(Geometry& geometry) {
  std::printf("serial_geometry=patches:%u curves:%u\n", geometry.GetNumberPatches(),
              geometry.GetNumberCurves());
  for (unsigned int i = 0; i < geometry.GetNumberPatches(); ++i) {
    auto* patch = static_cast<PatchBezier*>(geometry.GetPatch(i));
    auto points = Controls(patch);
    for (unsigned int j = 0; j < points.size(); ++j)
      std::printf("serial_control=patch:%u slot:%u id:%lu x:%016llx y:%016llx z:%016llx\n", i, j,
                  points[j].GetId(), static_cast<unsigned long long>(Bits(points[j].GetX())),
                  static_cast<unsigned long long>(Bits(points[j].GetY())),
                  static_cast<unsigned long long>(Bits(points[j].GetZ())));
    for (unsigned int s = 0; s < 4; ++s) {
      unsigned int c = 0;
      while (c < geometry.GetNumberCurves() && geometry.GetCurve(c) != patch->GetCurve(s))
        ++c;
      std::printf("serial_incidence=patch:%u slot:%u curve:%u reversed:%d\n", i, s, c,
                  patch->IsCurveReversed(s));
    }
    for (double u : {0.0, 0.25, 0.5, 1.0})
      for (double v : {0.0, 0.25, 0.5, 1.0}) {
        auto p = patch->Parameterize(u, v);
        auto qu = patch->Qu(u, v);
        auto qv = patch->Qv(u, v);
        for (double x : {p.GetX(), p.GetY(), p.GetZ(), qu.GetX(), qu.GetY(), qu.GetZ(), qv.GetX(),
                         qv.GetY(), qv.GetZ()})
          std::printf("serial_value=patch:%u u:%g v:%g bits:%016llx\n", i, u, v,
                      static_cast<unsigned long long>(Bits(x)));
      }
  }
}
bool Read(const char* path, bool repeat) {
  PatchReader reader;
  auto first = reader.LoaderBezierPatchFile(path);
  if (first.empty())
    return false;
  bool independent = true;
  if (repeat) {
    auto second = reader.LoaderBezierPatchFile(path);
    independent = second.size() == first.size();
    for (auto& a : first)
      for (auto& b : second)
        independent &= Observer(a) != Observer(b);
    std::printf("serial_reuse=first:%zu second:%zu independent:%d\n", first.size(), second.size(),
                independent);
    for (auto& owner : second)
      DestroyOriginal(owner);
  } else
    for (auto& owner : first)
      DestroyOriginal(owner);
  return independent;
}
bool Build(Geometry& geometry, const char* path, bool trace) {
  PatchReader reader;
  auto count = geometry.GetNumberPatches();
  Prefix prefix(geometry);
  reader.ReaderFilePatches(&geometry, path);
  if (trace)
    Trace(geometry);
  return geometry.GetNumberPatches() > count && prefix.Matches(geometry);
}
#if defined(_MSC_VER) && defined(_DEBUG)
int attempts = 0, denied = 0, fail_after = -1;
int __cdecl Hook(int kind, void*, std::size_t, int block, long, const unsigned char*, int) {
  if (kind == _HOOK_ALLOC && block == _NORMAL_BLOCK) {
    ++attempts;
    if (fail_after-- == 0) {
      ++denied;
      return FALSE;
    }
  }
  return TRUE;
}
struct AllocationScope {
  _CRT_ALLOC_HOOK prior;
  explicit AllocationScope(int ordinal) : prior(_CrtSetAllocHook(Hook)) {
    attempts = denied = 0;
    fail_after = ordinal;
  }
  ~AllocationScope() { _CrtSetAllocHook(prior); }
};
bool Trial(int operation, bool seed, const char* path, int ordinal) {
  Geometry geometry;
  if (seed)
    Require(Build(geometry, path, false), "seeded live graph");
  Prefix prefix(geometry);
  bool complete = false;
  int caught = 0;
  {
    AllocationScope hook(ordinal);
    try {
      if (operation == 0)
        complete = Read(path, false);
      else {
        auto count = geometry.GetNumberPatches();
        PatchReader reader;
        reader.ReaderFilePatches(&geometry, path);
        complete = geometry.GetNumberPatches() > count;
      }
    } catch (const std::bad_alloc&) {
      caught = 1;
    } catch (const std::ios_base::failure&) {
      caught = 2;
    } catch (const std::runtime_error&) {
      caught = 3;
    }
  }
  bool live = prefix.Matches(geometry);
  std::printf("serial_trial=ordinal:%d attempts:%d denied:%d caught:%d complete:%d live:%d\n",
              ordinal, attempts, denied, caught, complete, live);
  return live && (ordinal < 0 ? complete && caught == 0 : denied == 1 && caught != 0);
}
bool Failures(int operation, bool seed, const char* path, int first) {
  Require(Trial(operation, seed, path, -1), "complete calibration");
  int total = attempts;
  std::printf("serial_measured=allocations:%d\n", total);
  Require(total > 0 && first >= 0 && first < total, "positive allocation interval");
  int end = total - first < 32 ? total : first + 32;
  for (int ordinal = first; ordinal < end; ++ordinal) {
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    bool ok = Trial(operation, seed, path, ordinal);
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    std::printf("serial_denied=ordinal:%d blocks:%zu bytes:%zu\n", ordinal,
                delta.lCounts[_NORMAL_BLOCK], delta.lSizes[_NORMAL_BLOCK]);
    if (!ok || delta.lCounts[_NORMAL_BLOCK] != 0 || delta.lSizes[_NORMAL_BLOCK] != 0)
      return false;
  }
  std::printf("serial_range=first:%d end:%d total:%d\n", first, end, total);
  return true;
}
#endif
} // namespace

int main(int argc, char** argv) {
  Require(argc >= 3, "scenario and fixture are required");
  std::setvbuf(stdout, nullptr, _IONBF, 0);
#if defined(_WIN32)
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
#endif
#if defined(_MSC_VER) && defined(_DEBUG)
  for (int report : {_CRT_WARN, _CRT_ERROR, _CRT_ASSERT}) {
    _CrtSetReportMode(report, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(report, _CRTDBG_FILE_STDERR);
  }
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  bool passed = true;
  int operation = -1, seed = -1, first = -1;
  if (std::strcmp(argv[1], "contracts") == 0) {
    passed = LookupContracts() && Read(argv[2], false) && Read(argv[2], true);
    Geometry geometry;
    passed &= Build(geometry, argv[2], false);
    passed &= Build(geometry, argv[2], false);
  } else if (std::strcmp(argv[1], "read") == 0)
    passed = Read(argv[2], false);
  else if (std::strcmp(argv[1], "reuse") == 0)
    passed = Read(argv[2], true);
  else if (std::sscanf(argv[1], "normal-%d-%d", &operation, &seed) == 2 ||
           std::sscanf(argv[1], "trace-%d-%d", &operation, &seed) == 2) {
    Geometry geometry;
    if (seed)
      passed = Build(geometry, argv[2], false);
    passed &= operation == 0 ? Read(argv[2], false)
                             : Build(geometry, argv[2], std::strncmp(argv[1], "trace", 5) == 0);
  } else if (std::strncmp(argv[1], "reject", 6) == 0) {
    Geometry geometry;
    if (std::strcmp(argv[1], "reject-seeded") == 0)
      passed = Build(geometry, argv[2], false);
    Require(argc == 4, "rejected fixture required");
    Prefix prefix(geometry);
    bool caught = false;
    PatchReader reader;
    try {
      reader.ReaderFilePatches(&geometry, argv[3]);
    } catch (const std::runtime_error&) {
      caught = true;
    }
    passed &= caught && prefix.Matches(geometry);
    std::printf("serial_rejected=caught:%d live:%d\n", caught, prefix.Matches(geometry));
  } else if (std::strcmp(argv[1], "prefix-negative-control") == 0) {
    Geometry geometry;
    Require(Build(geometry, argv[2], false), "control live graph");
    PatchBezier foreign;
    auto* curve = geometry.GetCurve(0);
    curve->InsertPatch(&foreign);
    passed = !Live(geometry);
    curve->RemovePatchObservers(&foreign);
    passed &= Live(geometry);
    std::puts("serial_prefix_control=rejected");
  } else if (std::strcmp(argv[1], "leak") == 0)
    std::printf("deliberate_leak=%p\n", static_cast<void*>(new PatchBezier()));
  else if (std::strcmp(argv[1], "use-after-free") == 0) {
    auto* point = new PointAdaptive(1, 2, 3);
    delete point;
    std::printf("expired=%g\n", point->GetX());
  } else {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::sscanf(argv[1], "calibrate-%d-%d", &operation, &seed) == 2) {
      passed = Trial(operation, seed != 0, argv[2], -1);
      std::printf("serial_measured=allocations:%d\n", attempts);
    } else if (std::sscanf(argv[1], "failure-%d-%d-%d", &operation, &seed, &first) == 3)
      passed = Failures(operation, seed != 0, argv[2], first);
    else {
      Require(std::strcmp(argv[1], "allocation-hook-control") == 0, "known CRT mode");
      bool caught = false;
      {
        AllocationScope hook(0);
        try {
          auto p = std::make_unique<PointAdaptive>();
        } catch (const std::bad_alloc&) {
          caught = true;
        }
      }
      passed = caught && denied == 1;
      std::puts("allocation_hook_control=detected");
    }
#else
    Require(false, "unknown scenario or unavailable CRT hook");
#endif
  }
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  passed &= delta.lCounts[_NORMAL_BLOCK] == 0 && delta.lSizes[_NORMAL_BLOCK] == 0;
#endif
  std::puts(passed ? "PASS" : "FAIL");
  return passed ? 0 : 1;
}
