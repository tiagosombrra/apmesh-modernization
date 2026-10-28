#include "crab_mesh/aft/advancing_front.h"
#include "front_angle_hooks.h"
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

namespace front_angle_test {
struct Allocation {
  void* pointer = nullptr;
  std::size_t size = 0;
  bool live = false;
};
std::array<Allocation, 32> records{};
std::array<Vertex*, 2> objects{};
std::array<int, 2> release_order{};
std::array<double, 5> values{};
bool enabled = false, active = false, geometry_phase = false;
int attempts = 0, denied = 0, target = 0, entered = 0, finished = 0;
int record_count = 0, constructed = 0, released = 0;
long observed_id = -1;
void Begin(bool geometry) noexcept {
  if (enabled) {
    ++entered;
    active = true;
    geometry_phase = geometry;
  }
}
void Constructed(Vertex* vertex, int index) noexcept {
  if (enabled) {
    objects[index - 1] = vertex;
    ++constructed;
  }
}
void Observe(Vertex* first, Vertex* second, Vertex* selected, double angle) noexcept {
  if (enabled) {
    values = {first->getX(), first->getY(), second->getX(), second->getY(), angle};
    observed_id = selected->getId();
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
  if (!enabled || !pointer)
    return;
  for (int i = 0; i < 2; ++i)
    if (objects[i] == pointer) {
      if (released == 2)
        std::abort();
      release_order[released++] = i + 1;
      objects[i] = nullptr;
    }
  for (int i = 0; i < record_count; ++i)
    if (records[i].pointer == pointer && records[i].live)
      records[i].live = false;
}
} // namespace front_angle_test

#if defined(_MSC_VER) && defined(_DEBUG)
int __cdecl Hook(int kind, void* pointer, std::size_t, int block, long, const unsigned char*, int) {
  if (kind == _HOOK_FREE)
    front_angle_test::RecordFree(pointer);
  return kind != _HOOK_ALLOC || block != _NORMAL_BLOCK || front_angle_test::Allow();
}
#else
void* operator new(std::size_t bytes) {
  using namespace front_angle_test;
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
void* operator new[](std::size_t bytes) { return ::operator new(bytes); }
void operator delete(void* pointer) noexcept {
  front_angle_test::RecordFree(pointer);
  std::free(pointer);
}
void operator delete[](void* pointer) noexcept { ::operator delete(pointer); }
void operator delete(void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
void operator delete[](void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
#endif

namespace {
class FrontFixture : public AdvancingFront {
public:
  bool Select(Edge* edge, Vertex* first, Vertex* second, Vertex*& selected, bool geometry) {
    frontVertices.push_back(first);
    if (second)
      frontVertices.push_back(second);
    try {
      const bool found = findBestVertex(edge, selected, geometry);
      frontVertices.clear();
      return found;
    } catch (...) {
      frontVertices.clear();
      throw;
    }
  }
};
bool Operation(int layout, long& selected_id) {
  FrontFixture front;
  auto first = std::make_unique<Vertex>(0, 0, 101);
  auto second = std::make_unique<Vertex>(1, 0, 102);
  auto edge = std::make_unique<Edge>(first.get(), second.get(), 201);
  first.release();
  second.release();
  if (layout == 4) {
    auto* tree = front.getQuadtree();
    auto minimum = std::make_unique<Vertex>(0, 0);
    auto maximum = std::make_unique<Vertex>(1, 1);
    auto root =
        std::make_unique<QuadtreeCell>(tree->getCellId(), tree, minimum.get(), maximum.get());
    tree->setRoot(root.get());
    edge->setCell(root.get());
    root.release();
    minimum.release();
    maximum.release();
  }
  auto a = std::make_unique<Vertex>(layout == 0 || layout == 4 ? 0.5 : 0.25,
                                    layout == 0   ? 1.0
                                    : layout == 3 ? 0.7
                                                  : 0.75,
                                    301);
  auto b = std::make_unique<Vertex>(layout == 3 ? 0.8 : 0.75, layout == 3 ? 0.9 : 0.75, 302);
  Vertex* selected = nullptr;
  const bool found = front.Select(edge.get(), layout == 2 || layout == 3 ? b.get() : a.get(),
                                  layout == 0 || layout == 4 ? nullptr
                                  : layout == 1              ? b.get()
                                                             : a.get(),
                                  selected, layout == 4);
  if (selected)
    selected_id = selected->getId();
  return found;
}
} // namespace

int main(int argc, char* argv[]) {
  if (argc != 3)
    return 2;
  const int layout = std::atoi(argv[1]);
  const char* mode = argv[2];
  if (layout < 0 || layout > 4)
    return 2;
  if (std::strcmp(mode, "uaf-control") == 0)
    return front_angle_test::ExpiredAccess();
  long selected_id = -1;
  Operation(layout, selected_id);
  selected_id = -1;
  front_angle_test::target = std::atoi(mode);
  front_angle_test::enabled = true;
  bool threw = false, found = false;
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemState before{}, after{}, difference{};
  const auto previous = _CrtSetAllocHook(Hook);
  _CrtMemCheckpoint(&before);
#endif
  try {
    if (std::strcmp(mode, "leak-control") == 0 || std::strcmp(mode, "denial-control") == 0) {
      front_angle_test::target = std::strcmp(mode, "denial-control") == 0 ? 1 : 0;
      front_angle_test::Begin(false);
      (void)new Vertex(0.25, 0.75, 900);
      front_angle_test::End();
    } else {
      found = Operation(layout, selected_id);
    }
  } catch (const std::bad_alloc&) {
    front_angle_test::active = false;
    threw = true;
  }
  long live = 0;
  std::size_t bytes = 0;
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtSetAllocHook(previous);
  _CrtMemDifference(&difference, &before, &after);
  live = difference.lCounts[_NORMAL_BLOCK];
  bytes = difference.lSizes[_NORMAL_BLOCK];
  const char* profile = "msvc-debug-crt";
#else
  for (int i = 0; i < front_angle_test::record_count; ++i)
    if (front_angle_test::records[i].live) {
      ++live;
      bytes += front_angle_test::records[i].size;
    }
  const char* profile = "native-allocation-observer";
#endif
  using namespace front_angle_test;
  std::printf(
      "{\"layout\":%d,\"mode\":\"%s\",\"profile\":\"%s\",\"geometry\":%d,"
      "\"entered\":%d,\"finished\":%d,\"attempts\":%d,\"denied\":%d,\"threw\":%d,"
      "\"found\":%d,\"selected_id\":%ld,\"observed_id\":%ld,\"constructed\":%d,"
      "\"released\":%d,\"release_order\":[%d,%d],\"values\":[%.17g,%.17g,%.17g,%.17g,%.17g],"
      "\"retained_blocks\":%ld,\"retained_bytes\":%zu}\n",
      layout, mode, profile, geometry_phase, entered, finished, attempts, denied, threw, found,
      selected_id, observed_id, constructed, released, release_order[0], release_order[1],
      values[0], values[1], values[2], values[3], values[4], live, bytes);
  return live ? 1 : 0;
}
