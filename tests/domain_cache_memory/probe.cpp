#include "adapter/domain_uv_cache.h"
#include "crab_mesh/aft/advancing_front.h"
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <type_traits>

#if defined(_WIN32)
#include <windows.h>
#endif
#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

double TOLERANCE_AFT = 1e-8, TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
std::string USE_TEMPLATE = "y";
int AFT_LOCAL_POSTPROCESS_PASSES = 0;
double AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD = 0, AFT_LOCAL_POSTPROCESS_BLEND = 0.5;
double QUADTREE_FACE_QUALITY_THRESHOLD = 0, QUADTREE_LOW_QUALITY_H_FACTOR = 1;
double TEMPLATE_POOR_SCORE_THRESHOLD = 0;

namespace injection {
bool enabled = false;
int attempts = 0, denied = 0, remaining = -1;
bool Allow() {
  if (!enabled)
    return true;
  ++attempts;
  if (remaining-- == 0) {
    ++denied;
    return false;
  }
  return true;
}
} // namespace injection
#if !defined(_MSC_VER) || !defined(_DEBUG)
void* operator new(std::size_t size) {
  if (!injection::Allow())
    throw std::bad_alloc();
  if (void* value = std::malloc(size == 0 ? 1 : size))
    return value;
  throw std::bad_alloc();
}
void* operator new[](std::size_t size) { return ::operator new(size); }
void operator delete(void* value) noexcept { std::free(value); }
void operator delete[](void* value) noexcept { std::free(value); }
void operator delete(void* value, std::size_t) noexcept { std::free(value); }
void operator delete[](void* value, std::size_t) noexcept { std::free(value); }
#endif

namespace {
using Cache = apmesh::adaptation::DomainUvCache;
using Face = Cache::Face;
using Vertex = Cache::Vertex;
using UV = Cache::Parameters;
static_assert(!std::is_copy_constructible_v<Cache> && !std::is_move_constructible_v<Cache>);
void Require(bool value, const char* message) {
  if (!value) {
    std::fprintf(stderr, "Domain UV cache contract failed: %s\n", message);
    std::exit(2);
  }
}
#if defined(_MSC_VER) && defined(_DEBUG)
int __cdecl Hook(int kind, void*, std::size_t, int block, long, const unsigned char*, int) {
  return kind != _HOOK_ALLOC || block != _NORMAL_BLOCK || injection::Allow();
}
#endif
class AllocationScope {
public:
  explicit AllocationScope(int ordinal) {
    injection::attempts = injection::denied = 0;
    injection::remaining = ordinal;
    injection::enabled = true;
#if defined(_MSC_VER) && defined(_DEBUG)
    previous_ = _CrtSetAllocHook(Hook);
#endif
  }
  ~AllocationScope() {
    injection::enabled = false;
#if defined(_MSC_VER) && defined(_DEBUG)
    _CrtSetAllocHook(previous_);
#endif
  }

private:
#if defined(_MSC_VER) && defined(_DEBUG)
  _CRT_ALLOC_HOOK previous_;
#endif
};
struct Failure {};
std::array<UV, 3> Points(int shape) {
  if (shape == 0)
    return {{{0, 0}, {0.25, 0}, {0, 0.25}}};
  if (shape == 1)
    return {{{0.25, 0.25}, {0.75, 0.25}, {0.5, 0.25 + std::sqrt(3.0) / 4}}};
  return {{{0, 0}, {1.0 / 128, 0}, {1.0 / 256, 0.0256}}};
}
std::unique_ptr<Face> Make(int shape, long id) {
  const auto p = Points(shape);
  return Cache::MakeFace(p[0], p[1], p[2], id);
}
void Fill(Cache& cache, int shape, int count) {
  for (int i = 0; i < count; ++i) {
    auto face = Make(shape, 100 + i);
    face->h = 0.25;
    cache.Append(std::move(face));
  }
}
void ValidateFaces(const FaceList& faces, int shape, int count, bool emit) {
  Require(faces.size() == static_cast<std::size_t>(count), "complete ordered cache");
  const auto p = Points(shape);
  int index = 0;
  for (auto* face : faces) {
    Require(face->getId() == 100 + index && face->h == 0.25,
            "face identity and mutable size survive");
    std::array<Vertex*, 3> vertices{face->getV1(), face->getV2(), face->getV3()};
    Require(vertices[0] != vertices[1] && vertices[1] != vertices[2] && vertices[0] != vertices[2],
            "distinct owned endpoint identities");
    for (unsigned k = 0; k < 3; ++k)
      Require(vertices[k]->getX() == std::get<0>(p[k]) && vertices[k]->getY() == std::get<1>(p[k]),
              "ordered exact copied UV");
    Require(face->getMid() != vertices[0] && face->getMid() != vertices[1] &&
                face->getMid() != vertices[2],
            "distinct owned midpoint");
    if (emit)
      std::printf("live shape=%d face=%d id=%ld uv=%.17g,%.17g;%.17g,%.17g;%.17g,%.17g "
                  "mid=%.17g,%.17g h=%.17g q=%.17g\n",
                  shape, index, face->getId(), vertices[0]->getX(), vertices[0]->getY(),
                  vertices[1]->getX(), vertices[1]->getY(), vertices[2]->getX(),
                  vertices[2]->getY(), face->getMid()->getX(), face->getMid()->getY(), face->h,
                  face->quality());
    ++index;
  }
}
void Validate(Cache& cache, int shape, int count, bool emit) {
  ValidateFaces(cache.BorrowFaces(), shape, count, emit);
}
void OriginalLive() {
  for (int shape = 0; shape < 3; ++shape)
    for (int count : {1, 3, 8}) {
      FaceList faces;
      for (int i = 0; i < count; ++i) {
        const auto p = Points(shape);
        auto* a = new Vertex(std::get<0>(p[0]), std::get<1>(p[0]));
        auto* b = new Vertex(std::get<0>(p[1]), std::get<1>(p[1]));
        auto* c = new Vertex(std::get<0>(p[2]), std::get<1>(p[2]));
        auto* face = new Face(a, b, c, 100 + i);
        face->h = 0.25;
        faces.push_back(face);
      }
      ValidateFaces(faces, shape, count, true);
      while (!faces.empty()) {
        auto* face = faces.front();
        faces.pop_front();
        delete face;
      }
    }
}
void Operation(int shape, int count, bool fail) {
  Cache cache;
  Fill(cache, shape, count);
  struct Borrower {
    Cache& cache;
    int count;
    ~Borrower() noexcept {
      Require(cache.BorrowFaces().size() == static_cast<std::size_t>(count),
              "borrower survives until cache teardown");
      for (auto* face : cache.BorrowFaces())
        Require(std::isfinite(face->getMid()->getX()) && face->getV1() != nullptr,
                "borrower reads live native cache objects while unwinding");
    }
  };
  if (fail) {
    Borrower observer{cache, count};
    Require(&observer.cache == &cache && observer.count == count,
            "throwing borrower attached to the complete live cache");
    throw Failure{};
  }
  cache.Clear();
  cache.Clear();
}
void Sweep(int shape, int count, bool fail) {
  int total = 0;
  {
    AllocationScope scope(-1);
    try {
      Operation(shape, count, fail);
    } catch (const Failure&) {
    }
    total = injection::attempts;
  }
  Require(total > 0, "positive allocation calibration");
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    bool caught = false;
    {
      AllocationScope scope(ordinal);
      try {
        Operation(shape, count, fail);
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    Require(caught && injection::denied == 1 && injection::attempts == ordinal + 1,
            "every denial propagates without cleanup allocation");
  }
  std::printf("sweep shape=%d count=%d throw=%d allocations=%d denials=%d complete=1\n", shape,
              count, fail, total, total);
}
void AppendDenied(int shape) {
  Cache cache;
  Fill(cache, shape, 2);
  auto* first = cache.BorrowFaces().front();
  auto* tail = cache.BorrowFaces().back();
  auto face = Make(shape, 999);
  bool caught = false;
  {
    AllocationScope scope(0);
    try {
      cache.Append(std::move(face));
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  Require(caught && injection::attempts == 1 && injection::denied == 1 && !face,
          "list append denial destroys pending owner");
  Require(cache.BorrowFaces().front() == first && cache.BorrowFaces().back() == tail,
          "prior prefix identity preserved");
  Validate(cache, shape, 2, false);
  std::printf("append_denied shape=%d prefix=2 unchanged=1\n", shape);
}
void NoAlloc(int shape, int count) {
  auto cache = std::make_unique<Cache>();
  Fill(*cache, shape, count);
  {
    AllocationScope scope(0);
    cache->Clear();
    Require(cache->BorrowFaces().empty(), "clear empties the owner view");
    cache->Clear();
    cache.reset();
  }
  Require(injection::attempts == 0, "clear and destruction do not allocate");
  std::printf("nonalloc shape=%d faces=%d attempts=0\n", shape, count);
}
void Square(Boundary& boundary) {
  for (int side = 0; side < 4; ++side)
    for (int step = 0; step < 4; ++step) {
      const double t = step / 4.0;
      const double x = side == 0 ? t : side == 1 ? 1 : side == 2 ? 1 - t : 0;
      const double y = side == 1 ? t : side == 2 ? 1 : side == 3 ? 1 - t : 0;
      boundary.addVertex(x, y, nullptr);
    }
  Require(boundary.close(nullptr), "analytic square closes");
  for (auto* edge : boundary.getEdges())
    edge->setLen(edge->length());
}
class Consumer : public AdvancingFront {
  int mode_;

public:
  explicit Consumer(int mode) : AdvancingFront(0.85, 1e-8, 0), mode_(mode) {}
  MethodStatus makeGeometryBasedMesh() override {
    Require(!getQuadtree()->getMesh().empty(),
            "actual templates precede injected consumer outcome");
    if (mode_ == 1)
      throw Failure{};
    if (mode_ == 2)
      return ADVF_EMPTY;
    return AdvancingFront::makeGeometryBasedMesh();
  }
};
void Consume(int mode) {
  Cache cache;
  cache.Append(Cache::MakeFace({0, 0}, {1, 0}, {1, 1}, 100));
  cache.Append(Cache::MakeFace({0, 0}, {1, 1}, {0, 1}, 101));
  for (auto* face : cache.BorrowFaces())
    face->h = 0.25;
  bool caught = false;
  bool success = false;
  try {
    Consumer front(mode);
    Square(*front.getBoundary());
    success = front.execute(cache.BorrowFaces());
  } catch (const Failure&) {
    caught = true;
  }
  Require(caught == (mode == 1) && success == (mode == 0),
          "actual AFT success/false/exception paths");
  Require(cache.BorrowFaces().size() == 2, "cache membership survives real AFT unwinding");
  long id = 100;
  for (auto* face : cache.BorrowFaces())
    Require(face->getId() == id++ && face->h == 0.25 && face->orientedSurface() == 0.5,
            "square cache remains valid after actual AFT teardown");
  std::printf("consumer mode=%d cached_faces=2 alive_after_front=1\n", mode);
}
void HookControl() {
  bool caught = false;
  {
    AllocationScope scope(0);
    try {
      auto value = std::make_unique<Vertex>();
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  Require(caught && injection::denied == 1 && injection::attempts == 1,
          "independent real denial hook");
  std::puts("allocation_hook_control=detected");
}
void OriginalThrow(int count) {
  try {
    FaceList faces;
    for (int i = 0; i < count; ++i) {
      const auto p = Points(0);
      auto* a = new Vertex(std::get<0>(p[0]), std::get<1>(p[0]));
      auto* b = new Vertex(std::get<0>(p[1]), std::get<1>(p[1]));
      auto* c = new Vertex(std::get<0>(p[2]), std::get<1>(p[2]));
      auto* face = new Face(a, b, c, 100 + i);
      faces.push_back(face);
    }
    throw Failure{};
  } catch (const Failure&) {
  }
  std::puts("original_cached_throw=observed");
}
void OriginalPartial() {
  int first = 0;
  {
    AllocationScope scope(-1);
    auto value = std::make_unique<Vertex>(0, 0);
    first = injection::attempts;
  }
  Require(first > 0, "first original vertex has real allocations");
  bool caught = false;
  {
    AllocationScope scope(first);
    try {
      auto* a = new Vertex(0, 0);
      auto* b = new Vertex(1, 0);
      delete b;
      delete a;
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  Require(caught && injection::denied == 1 && injection::attempts == first + 1,
          "original second-vertex allocation denial exercised");
  std::puts("original_partial_denial=observed");
}
void Contracts(bool emit) {
  for (int shape = 0; shape < 3; ++shape) {
    for (int count : {1, 3, 8}) {
      if (emit) {
        Cache cache;
        Fill(cache, shape, count);
        Validate(cache, shape, count, true);
      } else {
        Sweep(shape, count, false);
        Sweep(shape, count, true);
        NoAlloc(shape, count);
      }
    }
    if (!emit)
      AppendDenied(shape);
  }
  if (!emit)
    for (int mode = 0; mode < 3; ++mode)
      Consume(mode);
}
} // namespace

int main(int argc, char** argv) {
  Require(argc == 2, "one scenario required");
  std::setvbuf(stdout, nullptr, _IONBF, 0);
#if defined(_WIN32)
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
#endif
#if defined(_MSC_VER) && defined(_DEBUG)
  for (int kind : {_CRT_WARN, _CRT_ERROR, _CRT_ASSERT}) {
    _CrtSetReportMode(kind, _CRTDBG_MODE_FILE);
    _CrtSetReportFile(kind, _CRTDBG_FILE_STDERR);
  }
#endif
  {
    Cache warm;
    Fill(warm, 0, 1);
    Validate(warm, 0, 1, true);
    HookControl();
    Consume(0);
  }
  std::puts("warmup_complete");
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  if (std::strcmp(argv[1], "contracts") == 0)
    Contracts(false);
  else if (std::strcmp(argv[1], "live") == 0)
    Contracts(true);
  else if (std::strcmp(argv[1], "original-live") == 0)
    OriginalLive();
  else if (std::strcmp(argv[1], "hook") == 0)
    HookControl();
  else if (std::strcmp(argv[1], "original-throw") == 0)
    OriginalThrow(3);
  else if (std::strcmp(argv[1], "original-partial") == 0)
    OriginalPartial();
  else if (std::strcmp(argv[1], "leak") == 0)
    Make(0, 1).release();
  else if (std::strcmp(argv[1], "uaf") == 0) {
    Cache cache;
    Fill(cache, 0, 1);
    auto* face = cache.BorrowFaces().front();
    cache.Clear();
    std::printf("expired-x=%g\n", face->getV1()->getX());
  } else
    Require(false, "known scenario");
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  const auto blocks = delta.lCounts[_NORMAL_BLOCK];
  const auto bytes = delta.lSizes[_NORMAL_BLOCK];
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", blocks, bytes);
  if (blocks != 0 || bytes != 0)
    return 1;
#endif
  std::puts("PASS");
  return 0;
}
