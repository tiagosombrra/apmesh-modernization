#include "data/mesh/sub_mesh.h"
#include "data/patch/patch_bezier.h"
#include "data/patch/patch_hermite.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <type_traits>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

double TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
unsigned int I_MAX = 100;
std::atomic<unsigned long long> FINDUV_TOTAL_CALLS{0}, FINDUV_IMAX_EXITS{0};

namespace {
void Require(bool value, const char* message) {
  if (!value) {
    std::fprintf(stderr, "Detached patch-copy contract failed: %s\n", message);
    std::exit(2);
  }
}
class InspectableBezier : public PatchBezier {
public:
  explicit InspectableBezier(PatchBezier* source) : PatchBezier(source) {}
  void CorruptBasis() { mat_base_(0, 0) = 0; }
};
class InspectableHermite : public PatchHermite {
public:
  explicit InspectableHermite(PatchHermite* source) : PatchHermite(source) {}
  bool FlagsTrue() const {
    return signal_curve1_ && signal_curve2_ && signal_curve3_ && signal_curve4_;
  }
  void CorruptDirection() { signal_curve1_ = false; }
};
#ifndef AP_MESH_PATCH_COPY_ORIGINAL
void Ready(PatchBezier& patch) {
  const auto basis = patch.GetB();
  const double expected[4][4] = {{-1, 3, -3, 1}, {3, -6, 3, 0}, {-3, 3, 0, 0}, {1, 0, 0, 0}};
  for (int row = 0; row < 4; ++row)
    for (int col = 0; col < 4; ++col)
      Require(basis(row, col) == expected[row][col], "initialized Bezier basis");
  Require(patch.GetArea() == 0 && patch.GetKaMedio() == 0 && patch.GetSegmentMedio() == 0 &&
              patch.GetAreaTriangle() == 0 && patch.GetNumberTriangle() == 0 &&
              patch.GetIdProcess() == 0 && patch.GetIdPatchBezier() == 0,
          "zero detached metadata");
}
#if defined(_MSC_VER) && defined(_DEBUG)
int allocation_attempts = 0;
int AllocationHook(int kind, void*, size_t, int block_type, long, const unsigned char*, int) {
  if (kind == _HOOK_ALLOC && block_type == _NORMAL_BLOCK) {
    ++allocation_attempts;
    return FALSE;
  }
  return TRUE;
}
class NoAlloc {
public:
  NoAlloc() {
    allocation_attempts = 0;
    previous_ = _CrtSetAllocHook(AllocationHook);
  }
  ~NoAlloc() { _CrtSetAllocHook(previous_); }
  NoAlloc(const NoAlloc&) = delete;
  NoAlloc& operator=(const NoAlloc&) = delete;

private:
  _CRT_ALLOC_HOOK previous_;
};
#endif
#endif
std::uint64_t Bits(double value) {
  std::uint64_t result;
  std::memcpy(&result, &value, sizeof(result));
  return result;
}
template <class A, class B> bool SameXYZ(const A& a, const B& b) {
  return Bits(a.GetX()) == Bits(b.GetX()) && Bits(a.GetY()) == Bits(b.GetY()) &&
         Bits(a.GetZ()) == Bits(b.GetZ());
}
template <class M> bool SameMatrix(const M& a, const M& b) {
  for (int row = 0; row < a.rows(); ++row)
    for (int col = 0; col < a.cols(); ++col)
      if (Bits(a(row, col)) != Bits(b(row, col)))
        return false;
  return true;
}
bool Detached(PatchCoons& copy) {
  return copy.GetNumBerCurves() == 0 && !copy.GetCurve(0) && !copy.GetCurve(4) &&
         !copy.GetSubMesh();
}
template <class P> void Evaluate(P& source, P& copy, int shape) {
  unsigned int vectors = 0;
  for (double u : {0.0, 0.25, 0.5, 0.75, 1.0})
    for (double v : {0.0, 0.25, 0.5, 0.75, 1.0}) {
      auto a = source.Parameterize(u, v), b = copy.Parameterize(u, v);
      Require(SameXYZ(a, b), "bitwise copied parameterization");
      Require(std::abs(b.GetX() - u) < 1e-12 && std::abs(b.GetY() - v) < 1e-12 &&
                  std::abs(b.GetZ() - shape * 0.25 * u * v) < 1e-12,
              "independent analytic planar/bilinear surface");
      auto emit = [&](const auto& point) {
        std::printf("xyz=%016llx,%016llx,%016llx\n",
                    static_cast<unsigned long long>(Bits(point.GetX())),
                    static_cast<unsigned long long>(Bits(point.GetY())),
                    static_cast<unsigned long long>(Bits(point.GetZ())));
        ++vectors;
      };
      emit(b);
      using Derivative = VectorAdaptive (P::*)(double, double);
      for (Derivative method :
           {static_cast<Derivative>(&P::Qu), static_cast<Derivative>(&P::Qv),
            static_cast<Derivative>(&P::Quu), static_cast<Derivative>(&P::Quv),
            static_cast<Derivative>(&P::Qvu), static_cast<Derivative>(&P::Qvv)}) {
        auto da = (source.*method)(u, v), db = (copy.*method)(u, v);
        Require(SameXYZ(da, db), "bitwise copied first/second partials");
        emit(db);
      }
    }
  Require(vectors == 175, "nonempty surface/derivative inventory");
  std::printf("evaluated_vectors=%u\n", vectors);
}
template <class C>
void Incidence(const std::array<std::unique_ptr<C>, 4>& curves, Patch* parent, Patch* source) {
  for (const auto& curve : curves) {
    Require(curve->GetNumBerPatches() == 4, "source incidence count unchanged");
    Require(curve->GetPatch(0) == parent && !curve->GetPatch(1) && curve->GetPatch(2) == parent &&
                curve->GetPatch(3) == source,
            "preexisting observer identities and order");
  }
}
void Base() {
  Patch source;
  SubMesh mesh;
  source.SetId(731);
  source.SetSubMesh(&mesh);
  Patch copy(&source), empty(static_cast<Patch*>(nullptr));
  Require(copy.GetId() == 731 && !copy.GetSubMesh(), "base copies ID only");
  Require(empty.GetId() == 0 && !empty.GetSubMesh(), "base null source");
  Require(source.GetSubMesh() == &mesh, "source borrow remains");
  std::puts("base_id_only=1 null_source=1 submesh_detached=1");
}
void Bezier(int shape, unsigned int mask, const char* challenge = nullptr, int noalloc = -1) {
  Patch parent;
  SubMesh mesh;
  std::array<PointAdaptive, 16> points;
  for (unsigned int i = 0; i < points.size(); ++i) {
    const double u = (i / 4) / 3.0, v = (i % 4) / 3.0;
    points[i] = PointAdaptive(u, v, shape * 0.25 * u * v, 100 + i);
  }
  std::array<std::unique_ptr<CurveAdaptiveParametricBezier>, 4> curves;
  const std::array<std::array<unsigned int, 4>, 4> controls{
      {{0, 4, 8, 12}, {12, 13, 14, 15}, {3, 7, 11, 15}, {0, 1, 2, 3}}};
  for (unsigned int i = 0; i < 4; ++i) {
    auto c = controls[i];
    if ((mask & (1u << i)) != 0)
      std::reverse(c.begin(), c.end());
    curves[i] = std::make_unique<CurveAdaptiveParametricBezier>(points[c[0]], points[c[1]],
                                                                points[c[2]], points[c[3]]);
    curves[i]->InsertPatch(&parent);
    curves[i]->InsertPatch(nullptr);
    curves[i]->InsertPatch(&parent);
  }
  auto source = std::make_unique<PatchBezier>(
      curves[0].get(), curves[1].get(), curves[2].get(), curves[3].get(), points[5], points[9],
      points[6], points[10], (mask & 1) == 0, (mask & 2) == 0, (mask & 4) == 0, (mask & 8) == 0);
  source->SetId(713);
  source->SetSubMesh(&mesh);
  source->Parameterize(0.25, 0.75);
  // One fixture leaves source load metadata uninitialized; the other seeds it.
  // Neither the probe nor production copy reads source load metadata.
  if (shape != 0) {
    source->SetArea(9);
    source->SetKaMedio(8);
    source->SetSegmentMedio(7);
    source->SetAreaTriangle(6);
    source->SetNumberTriangle(5);
    source->SetIdProcess(4);
    source->SetIdPatchBezier(3);
  }
#ifndef AP_MESH_PATCH_COPY_ORIGINAL
#if defined(_MSC_VER) && defined(_DEBUG)
  if (noalloc >= 0) {
    {
      NoAlloc guard;
      InspectableBezier copy(source.get());
      Ready(copy);
      Require(Detached(copy), "nonallocating detached topology");
      if ((noalloc % 2) != 0) {
        InspectableBezier second(&copy);
        Ready(second);
      }
    }
    Require(allocation_attempts == 0, "copy and retirement must not allocate");
    std::printf("patch_copy_noalloc=%d,attempts:0\n", noalloc);
    return;
  }
#endif
#endif
  auto copy = std::make_unique<InspectableBezier>(source.get());
  Require(Detached(*copy) && copy->GetId() == 713, "Bezier ID and detached topology");
  Require(SameMatrix(source->GetGx(), copy->GetGx()) &&
              SameMatrix(source->GetGy(), copy->GetGy()) &&
              SameMatrix(source->GetGz(), copy->GetGz()) &&
              SameMatrix(source->GetU(), copy->GetU()) && SameMatrix(source->GetV(), copy->GetV()),
          "Bezier initialized geometric and scratch matrices");
  using Control = PointAdaptive (PatchBezier::*)() const;
  const std::array<Control, 16> getters{
      &PatchBezier::GetPt00, &PatchBezier::GetPt01, &PatchBezier::GetPt02, &PatchBezier::GetPt03,
      &PatchBezier::GetPt10, &PatchBezier::GetPt11, &PatchBezier::GetPt12, &PatchBezier::GetPt13,
      &PatchBezier::GetPt20, &PatchBezier::GetPt21, &PatchBezier::GetPt22, &PatchBezier::GetPt23,
      &PatchBezier::GetPt30, &PatchBezier::GetPt31, &PatchBezier::GetPt32, &PatchBezier::GetPt33};
  for (auto get : getters) {
    auto a = (source.get()->*get)(), b = (copy.get()->*get)();
    Require(SameXYZ(a, b) && a.GetId() == b.GetId(), "all sixteen control values and IDs");
  }
  for (unsigned int i = 0; i < 4; ++i)
    Require(copy->IsCurveReversed(i) == ((mask & (1u << i)) != 0), "copied Bezier direction flags");
  Require(!copy->IsCurveReversed(4), "invalid direction slot");
  Incidence(curves, &parent, source.get());
#ifndef AP_MESH_PATCH_COPY_ORIGINAL
  if (challenge && std::strcmp(challenge, "basis-control") == 0)
    copy->CorruptBasis();
  if (challenge && std::strcmp(challenge, "metadata-control") == 0)
    copy->SetArea(9);
  if (challenge && std::strcmp(challenge, "topology-control") == 0)
    copy->InsertCurve(curves[0].get());
  Ready(*copy);
  Require(Detached(*copy), "detached topology");
  InspectableBezier repeated(copy.get());
  Ready(repeated);
  Require(Detached(repeated) && repeated.GetId() == copy->GetId(), "repeated detached copy");
#endif
  Evaluate<PatchBezier>(*source, *copy, shape);
  const auto scratch = copy->GetU();
  source->Parameterize(0.125, 0.875);
  Require(SameMatrix(copy->GetU(), scratch), "independent scratch storage");
  source.reset();
  for (const auto& curve : curves)
    Require(curve->GetNumBerPatches() == 3 && curve->GetPatch(0) == &parent &&
                !curve->GetPatch(1) && curve->GetPatch(2) == &parent,
            "source retirement leaves the original prefix");
  Require(std::abs(copy->Parameterize(0.5, 0.5).GetZ() - shape * 0.0625) < 1e-12,
          "detached numeric payload outlives source");
  copy.reset();
  for (const auto& curve : curves)
    Require(curve->GetNumBerPatches() == 3, "detached retirement does not mutate incidence");
  std::printf("bezier shape=%d mask=%u controls=16 curves=0 submesh=0 incidence_unchanged=1\n",
              shape, mask);
}
void Hermite(int shape, bool challenge = false, int noalloc = -1) {
  Patch parent;
  SubMesh mesh;
  const double z = shape * 0.25;
  PointAdaptive p00(0, 0, 0), p10(1, 0, 0), p01(0, 1, 0), p11(1, 1, z);
  VectorAdaptive u0(1, 0, 0), u1(1, 0, z), v0(0, 1, 0), v1(0, 1, z), twist(0, 0, z);
  std::array<std::unique_ptr<CurveAdaptiveParametricHermite>, 4> curves{
      std::make_unique<CurveAdaptiveParametricHermite>(p00, p10, u0, u0),
      std::make_unique<CurveAdaptiveParametricHermite>(p10, p11, v1, v1),
      std::make_unique<CurveAdaptiveParametricHermite>(p01, p11, u1, u1),
      std::make_unique<CurveAdaptiveParametricHermite>(p00, p01, v0, v0)};
  for (const auto& curve : curves) {
    curve->InsertPatch(&parent);
    curve->InsertPatch(nullptr);
    curve->InsertPatch(&parent);
  }
  auto source = std::make_unique<PatchHermite>(curves[0].get(), curves[1].get(), curves[2].get(),
                                               curves[3].get(), twist, twist, twist, twist, false,
                                               true, false, true);
  source->SetId(719);
  source->SetSubMesh(&mesh);
  source->Parameterize(0.25, 0.75);
#ifndef AP_MESH_PATCH_COPY_ORIGINAL
#if defined(_MSC_VER) && defined(_DEBUG)
  if (noalloc >= 0) {
    {
      NoAlloc guard;
      InspectableHermite copy(source.get());
      Require(copy.FlagsTrue() && Detached(copy), "nonallocating initialized Hermite copy");
      if ((noalloc % 2) != 0) {
        InspectableHermite second(&copy);
        Require(second.FlagsTrue(), "repeated directions");
      }
    }
    Require(allocation_attempts == 0, "copy and retirement must not allocate");
    for (const auto& curve : curves)
      curve->RemovePatchObservers(source.get());
    std::printf("patch_copy_noalloc=%d,attempts:0\n", noalloc);
    return;
  }
#endif
#endif
  auto copy = std::make_unique<InspectableHermite>(source.get());
#ifndef AP_MESH_PATCH_COPY_ORIGINAL
  if (challenge)
    copy->CorruptDirection();
  Require(copy->FlagsTrue(), "initialized Hermite directions");
  for (unsigned int i = 0; i < 5; ++i)
    Require(!copy->IsCurveReversed(i), "unchanged Coons orientation fallback");
  InspectableHermite repeated(copy.get());
  Require(repeated.FlagsTrue() && Detached(repeated) && repeated.GetId() == copy->GetId(),
          "repeated Hermite copy");
#endif
  Require(Detached(*copy) && copy->GetId() == 719, "Hermite ID and detached topology");
  Require(SameMatrix(source->GetH(), copy->GetH()) && SameMatrix(source->GetGx(), copy->GetGx()) &&
              SameMatrix(source->GetGy(), copy->GetGy()) &&
              SameMatrix(source->GetGz(), copy->GetGz()) &&
              SameMatrix(source->GetU(), copy->GetU()) && SameMatrix(source->GetV(), copy->GetV()),
          "Hermite initialized basis, geometry and scratch matrices");
  using Control = PointAdaptive (PatchHermite::*)() const;
  for (Control get : {&PatchHermite::GetPt00, &PatchHermite::GetPt01, &PatchHermite::GetPt10,
                      &PatchHermite::GetPt11}) {
    auto a = (source.get()->*get)(), b = (copy.get()->*get)();
    Require(SameXYZ(a, b) && a.GetId() == b.GetId(), "Hermite corner values and IDs");
  }
  using Tangent = VectorAdaptive (PatchHermite::*)() const;
  for (Tangent get : {&PatchHermite::GetQu00, &PatchHermite::GetQu01, &PatchHermite::GetQu10,
                      &PatchHermite::GetQu11, &PatchHermite::GetQv00, &PatchHermite::GetQv01,
                      &PatchHermite::GetQv10, &PatchHermite::GetQv11, &PatchHermite::GetTw00,
                      &PatchHermite::GetTw01, &PatchHermite::GetTw10, &PatchHermite::GetTw11})
    Require(SameXYZ((source.get()->*get)(), (copy.get()->*get)()), "Hermite tangent/twist values");
  Incidence(curves, &parent, source.get());
  Evaluate<PatchHermite>(*source, *copy, shape);
  copy.reset();
  Incidence(curves, &parent, source.get());
  // Hermite observer retirement is a separate obligation; prepare a valid teardown.
  for (const auto& curve : curves)
    curve->RemovePatchObservers(source.get());
  source.reset();
  std::printf(
      "hermite shape=%d curves=0 submesh=0 incidence_unchanged=1 explicit_source_cleanup=1\n",
      shape);
}
} // namespace

int main(int argc, char** argv) {
  std::setvbuf(stdout, nullptr, _IONBF, 0);
  Require(argc >= 2, "mode is required");
  static_assert(!std::is_copy_constructible_v<PatchBezier> &&
                !std::is_move_constructible_v<PatchBezier>);
  static_assert(!std::is_copy_constructible_v<PatchHermite> &&
                !std::is_move_constructible_v<PatchHermite>);
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  const char* mode = argv[1];
  if (std::strcmp(mode, "contracts") == 0) {
    Base();
    for (int shape = 0; shape < 2; ++shape)
      for (unsigned int mask = 0; mask < 16; ++mask)
        Bezier(shape, mask);
    Hermite(0);
    Hermite(1);
  } else if (std::strcmp(mode, "base") == 0)
    Base();
  else if (std::strcmp(mode, "bezier") == 0) {
    Require(argc == 4, "Bezier shape/mask required");
    Bezier(std::atoi(argv[2]), static_cast<unsigned int>(std::atoi(argv[3])));
  } else if (std::strcmp(mode, "hermite") == 0) {
    Require(argc == 3, "Hermite shape required");
    Hermite(std::atoi(argv[2]));
  }
#ifndef AP_MESH_PATCH_COPY_ORIGINAL
  else if (std::strcmp(mode, "basis-control") == 0 || std::strcmp(mode, "metadata-control") == 0 ||
           std::strcmp(mode, "topology-control") == 0)
    Bezier(1, 5, mode);
  else if (std::strcmp(mode, "direction-control") == 0)
    Hermite(1, true);
#if defined(_MSC_VER) && defined(_DEBUG)
  else if (std::strncmp(mode, "noalloc-", 8) == 0) {
    const int n = std::atoi(mode + 8);
    Require(n >= 0 && n < 12, "noallocation variant");
    const unsigned int masks[4] = {0, 5, 10, 15};
    if (n < 8)
      Bezier(n / 4, masks[n % 4], nullptr, n);
    else
      Hermite((n - 8) / 2, false, n);
  } else if (std::strcmp(mode, "hook-control") == 0) {
    bool denied = false;
    {
      NoAlloc guard;
      try {
        auto* p = new PointAdaptive(1, 2, 3);
        delete p;
      } catch (const std::bad_alloc&) {
        denied = true;
      }
    }
    Require(denied && allocation_attempts == 1, "working independent denial hook");
    std::puts("patch_copy_hook=detected");
  }
#endif
#endif
  else if (std::strcmp(mode, "leak-control") == 0)
    std::printf("deliberate_point_leak=%p\n", static_cast<void*>(new PointAdaptive(1, 2, 3)));
  else if (std::strcmp(mode, "uaf-control") == 0) {
    auto* patch = new Patch;
    delete patch;
    std::printf("expired_id=%u\n", patch->GetId());
  } else
    Require(false, "unknown mode");
  std::puts("PASS");
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
