#include "crab_mesh/aft/advancing_front.h"
#include "front_face_hooks.h"
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

double TOLERANCE_AFT = 1e-8, TOLERANCE = 1e-8, DELTA = 1e-8, EPSYLON = 1e-8;
std::string USE_TEMPLATE = "y";
int AFT_LOCAL_POSTPROCESS_PASSES = 0;
double AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD = 0, AFT_LOCAL_POSTPROCESS_BLEND = 0.5;
double QUADTREE_FACE_QUALITY_THRESHOLD = 0, QUADTREE_LOW_QUALITY_H_FACTOR = 1;
double TEMPLATE_POOR_SCORE_THRESHOLD = 0;

namespace front_face_test {
struct Allocation {
  void* pointer;
  std::size_t size;
  bool live;
};
std::array<Allocation, 32> records{};
std::array<int, 5> destroyed{}, destroyed_before_owner_cleanup{};
std::array<long, 3> attached_ids{};
std::array<double, 2> midpoint{};
std::array<Vertex*, 3> cache_objects{};
std::array<int, 3> cache_release_order{-1, -1, -1};
int cache_releases = 0, live_fields_checked = 0, adjacency_checked = 0;
int consumer_reads = 0, quarantined_handles = 0;

bool enabled = false, active = false;
int attempts = 0, denied = 0, target = 0, entered = 0, finished = 0;
int phase = -1, record_count = 0, attached = 0, result = -1;
bool threw = false;
void Cache(Face& face, int index) noexcept {
  if (enabled)
    cache_objects[index] = face.getMid();
}
void Begin() noexcept {
  if (enabled) {
    ++entered;
    active = true;
    phase = 0;
  }
}
void Stage(int value) noexcept {
  if (enabled)
    phase = value;
}
void Observe(Face& face) noexcept {
  if (enabled) {
    ++attached;
    attached_ids = {face.getV1()->getId(), face.getV2()->getId(), face.getV3()->getId()};
    midpoint = {face.getMid()->getX(), face.getMid()->getY()};
  }
}
void End() noexcept {
  if (enabled) {
    ++finished;
    active = false;
  }
}
bool Allow() noexcept {
  if (active && ++attempts == target) {
    ++denied;
    return false;
  }
  return true;
}
void RecordFree(void* pointer) noexcept {
  if (enabled && pointer) {
    for (int i = 0; i < 3; ++i)
      if (cache_objects[i] == pointer) {
        if (cache_releases == 3)
          std::abort();
        cache_release_order[cache_releases++] = i;
        cache_objects[i] = nullptr;
      }
  }
  for (int i = 0; i < record_count; ++i)
    if (records[i].pointer == pointer && records[i].live)
      records[i].live = false;
}
} // namespace front_face_test
#if defined(_MSC_VER) && defined(_DEBUG)
int __cdecl Hook(int kind, void* pointer, std::size_t, int block, long, const unsigned char*, int) {
  if (kind == _HOOK_FREE)
    front_face_test::RecordFree(pointer);
  return kind != _HOOK_ALLOC || block != _NORMAL_BLOCK || front_face_test::Allow();
}
#else
void* operator new(std::size_t bytes) {
  using namespace front_face_test;
  if (!Allow())
    throw std::bad_alloc();
  void* pointer = std::malloc(bytes ? bytes : 1);
  if (!pointer)
    throw std::bad_alloc();
  if (active) {
    if (record_count == static_cast<int>(records.size()))
      std::abort();
    records[record_count++] = {pointer, bytes, true};
  }
  return pointer;
}
void* operator new[](std::size_t size) { return ::operator new(size); }
void operator delete(void* pointer) noexcept {
  front_face_test::RecordFree(pointer);
  std::free(pointer);
}
void operator delete[](void* pointer) noexcept { ::operator delete(pointer); }
void operator delete(void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
void operator delete[](void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
#endif

namespace {
class CountedVertex : public Vertex {
public:
  CountedVertex(double x, double y, int index) : Vertex(x, y, 101 + index), index_(index) {}
  ~CountedVertex() override { ++front_face_test::destroyed[index_]; }

private:
  int index_;
};
class BorrowedEdge : public Edge {
public:
  using Edge::Edge;
  ~BorrowedEdge() override { DetachVertices(); }
};
class FrontFixture : public AdvancingFront {
public:
  bool Inspect(Edge* edge, Vertex* candidate, const std::array<Vertex*, 5>& points, int layout,
               Edge* crossing) {
    for (auto* point : points)
      frontVertices.push_back(point);
    if (crossing)
      edges.push_back(crossing);
    try {
      const bool result = interceptionTest(edge, candidate, layout != 4, layout == 2);
      frontVertices.clear();
      edges.clear();
      return result;
    } catch (...) {
      frontVertices.clear();
      edges.clear();
      throw;
    }
  }
};
void Operation(int layout, bool consume) {
  FrontFixture front;
  std::array<std::unique_ptr<CountedVertex>, 5> owners;
  owners[0] = std::make_unique<CountedVertex>(0, 0, 0);
  owners[1] = std::make_unique<CountedVertex>(1, 0, 1);
  owners[2] = std::make_unique<CountedVertex>(0.5, 1, 2);
  owners[3] = std::make_unique<CountedVertex>(layout == 0 ? 2 : 0.5,
                                              layout == 0   ? 2
                                              : layout == 1 ? 0.25
                                              : layout == 2 ? 0
                                                            : 1,
                                              3);
  owners[4] = std::make_unique<CountedVertex>(2, 2, 4);
  BorrowedEdge edge(owners[0].get(), owners[1].get(), 201);
  BorrowedEdge side1(owners[1].get(), owners[2].get(), 203);
  BorrowedEdge side2(owners[2].get(), owners[0].get(), 204);
  owners[0]->addAdjacentEdge(&edge);
  owners[0]->addAdjacentEdge(&side2);
  owners[1]->addAdjacentEdge(&edge);
  owners[1]->addAdjacentEdge(&side1);
  owners[2]->addAdjacentEdge(&side1);
  owners[2]->addAdjacentEdge(&side2);
  std::array<double, 5> original_x{}, original_y{};
  for (int i = 0; i < 5; ++i) {
    original_x[i] = owners[i]->getX();
    original_y[i] = owners[i]->getY();
  }
  auto x = std::make_unique<Vertex>(-0.1, 0.5);
  auto y = std::make_unique<Vertex>(0.6, 0.5);
  auto crossing = std::make_unique<Edge>(x.get(), y.get(), 202);
  x.release();
  y.release();
  std::array<Vertex*, 5> views{};
  for (int i = 0; i < 5; ++i)
    views[i] = owners[i].get();
  try {
    const bool found = front.Inspect(&edge, owners[2].get(), views, layout,
                                     layout == 5 ? crossing.get() : nullptr);
    if (front_face_test::enabled)
      front_face_test::result = found;
  } catch (const std::bad_alloc&) {
    front_face_test::active = false;
    front_face_test::threw = true;
  }
  if (front_face_test::enabled)
    front_face_test::destroyed_before_owner_cleanup = front_face_test::destroyed;
  if (consume) {
    std::printf("consume_borrower phase=%d denied=%d destroyed=%d,%d,%d\n", front_face_test::phase,
                front_face_test::denied, front_face_test::destroyed[0],
                front_face_test::destroyed[1], front_face_test::destroyed[2]);
    std::fflush(stdout);
    for (int i = 0; i < 3; ++i) {
      volatile double value = owners[i]->getX() + owners[i]->getY();
      (void)value;
      ++front_face_test::consumer_reads;
    }
  }
  for (int i = 0; i < 5; ++i)
    if (!front_face_test::destroyed[i]) {
      if (owners[i]->getId() != 101 + i || owners[i]->getX() != original_x[i] ||
          owners[i]->getY() != original_y[i])
        std::abort();
      if (front_face_test::enabled)
        ++front_face_test::live_fields_checked;
      if (i < 3) {
        const auto adjacent = owners[i]->getAdjacentEdges();
        const std::array<Edge*, 2> expected = i == 0   ? std::array<Edge*, 2>{&edge, &side2}
                                              : i == 1 ? std::array<Edge*, 2>{&edge, &side1}
                                                       : std::array<Edge*, 2>{&side1, &side2};
        if (adjacent.size() != 2 || adjacent.count(expected[0]) != 1 ||
            adjacent.count(expected[1]) != 1)
          std::abort();
        if (front_face_test::enabled)
          ++front_face_test::adjacency_checked;
      }
    }
  // Diagnostic-only quarantine: release handles whose native objects were already
  // destroyed by Face. This preserves the failed borrower contract without a
  // second invalid deletion. The separate consume case performs actual access.
  for (int i = 0; i < 5; ++i)
    if (front_face_test::destroyed[i]) {
      owners[i].release();
      ++front_face_test::quarantined_handles;
    }
}
} // namespace

int main(int argc, char* argv[]) {
  if (argc < 3)
    return 3;
  if (std::strcmp(argv[2], "uaf-control") == 0)
    return front_face_test::ExpiredAccess();
  const int layout = std::atoi(argv[1]);
  const char* mode = argv[2];
  if (layout < 0 || layout > 5)
    return 3;
  Operation(layout, false);
  front_face_test::destroyed.fill(0);
  front_face_test::threw = false;
  front_face_test::consumer_reads = 0;
  front_face_test::enabled = true;
  front_face_test::target = std::atoi(mode);
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemState before{}, after{}, difference{};
  const auto previous = _CrtSetAllocHook(Hook);
  _CrtMemCheckpoint(&before);
#endif
  if (std::strcmp(mode, "denial-control") == 0 || std::strcmp(mode, "leak-control") == 0) {
    front_face_test::target = std::strcmp(mode, "denial-control") == 0 ? 1 : 0;
    try {
      front_face_test::Begin();
      (void)new Vertex(0.25, 0.75);
      front_face_test::End();
    } catch (const std::bad_alloc&) {
      front_face_test::active = false;
      front_face_test::threw = true;
    }
  } else {
    Operation(layout, argc == 4 && std::strcmp(argv[3], "consume") == 0);
  }
  long retained_blocks = 0;
  std::size_t retained_bytes = 0;
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtSetAllocHook(previous);
  _CrtMemDifference(&difference, &before, &after);
  retained_blocks = difference.lCounts[_NORMAL_BLOCK];
  retained_bytes = difference.lSizes[_NORMAL_BLOCK];
  const char* profile = "msvc-debug-crt";
#else
  for (int i = 0; i < front_face_test::record_count; ++i)
    if (front_face_test::records[i].live) {
      ++retained_blocks;
      retained_bytes += front_face_test::records[i].size;
    }
  const char* profile = "native-allocation-observer";
#endif
  using namespace front_face_test;
  const bool damaged = destroyed_before_owner_cleanup[0] || destroyed_before_owner_cleanup[1] ||
                       destroyed_before_owner_cleanup[2];
  std::printf("{\"cache_releases\":%d,\"cache_release_order\":[%d,%d,%d],\"live_fields_checked\":%"
              "d,\"adjacency_checked\":%d,\"consumer_reads\":%d,\"quarantined_handles\":%d,",
              cache_releases, cache_release_order[0], cache_release_order[1],
              cache_release_order[2], live_fields_checked, adjacency_checked, consumer_reads,
              quarantined_handles);
  std::printf("\"layout\":%d,\"mode\":\"%s\",\"profile\":\"%s\",\"attempts\":%d,\"denied\":%d,"
              "\"threw\":%d,"
              "\"entered\":%d,\"finished\":%d,\"phase\":%d,\"result\":%d,\"attached\":%d,"
              "\"attached_ids\":[%ld,%ld,%ld],\"midpoint\":[%.17g,%.17g],"
              "\"destroyed_before_owner_cleanup\":[%d,%d,%d,%d,%d],\"destroyed_after_cleanup\":[%d,"
              "%d,%d,%d,%d],"
              "\"retained_blocks\":%ld,\"retained_bytes\":%zu}\n",
              layout, mode, profile, attempts, denied, threw, entered, finished, phase, result,
              attached, attached_ids[0], attached_ids[1], attached_ids[2], midpoint[0], midpoint[1],
              destroyed_before_owner_cleanup[0], destroyed_before_owner_cleanup[1],
              destroyed_before_owner_cleanup[2], destroyed_before_owner_cleanup[3],
              destroyed_before_owner_cleanup[4], destroyed[0], destroyed[1], destroyed[2],
              destroyed[3], destroyed[4], retained_blocks, retained_bytes);
  return damaged ? 1 : retained_blocks ? 2 : 0;
}
