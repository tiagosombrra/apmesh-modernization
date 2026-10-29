#include "crab_mesh/aft/advancing_front.h"
#include "shortcut_hooks.h"
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

namespace shortcut_test {
struct Allocation {
  void* pointer;
  std::size_t size;
  bool live;
};
std::array<Allocation, 16> allocations{};
std::array<int, 6> destroyed{};
std::array<long, 3> endpoint_ids{};
std::array<double, 2> midpoint{};
Face* pending = nullptr;
Vertex* pending_mid = nullptr;
bool enabled = false, active = false, face_freed = false, mid_freed = false;
bool cleanup_active = false;
int cleanup_calls = 0, cleanup_allocations = 0;
int target_window = 1, seen = 0, entered = 0, attempts = 0, denied = 0, target = 0;
int records = 0, phase = -1, constructed = 0, adopted = 0;
long before_id = -1, face_id = -1;
std::size_t before_mesh = 0;
double area = 0;
void Begin(std::size_t prefix, long last_id) noexcept {
  if (!enabled)
    return;
  ++seen;
  if (seen != target_window)
    return;
  ++entered;
  active = true;
  phase = 0;
  before_mesh = prefix;
  before_id = last_id;
}
void Built(Face* face) noexcept {
  if (!active)
    return;
  ++constructed;
  phase = 1;
  pending = face;
  pending_mid = face->getMid();
  face_id = face->getId();
  endpoint_ids = {face->getV1()->getId(), face->getV2()->getId(), face->getV3()->getId()};
  midpoint = {face->getMid()->getX(), face->getMid()->getY()};
  area = face->orientedSurface();
}
void Adopted(std::size_t) noexcept {
  if (!active)
    return;
  ++adopted;
  phase = 2;
  active = false;
}
void BeginCleanup() noexcept {
  if (enabled) {
    cleanup_active = true;
    ++cleanup_calls;
  }
}
void EndCleanup() noexcept { cleanup_active = false; }
bool Allow() noexcept {
  if (cleanup_active)
    ++cleanup_allocations;
  if (active && ++attempts == target) {
    ++denied;
    return false;
  }
  return true;
}
void Free(void* pointer) noexcept {
  if (enabled && pointer) {
    if (pointer == pending)
      face_freed = true;
    if (pointer == pending_mid)
      mid_freed = true;
  }
  for (int i = 0; i < records; ++i)
    if (allocations[i].pointer == pointer && allocations[i].live)
      allocations[i].live = false;
}
} // namespace shortcut_test
#if defined(_MSC_VER) && defined(_DEBUG)
int __cdecl Hook(int kind, void* pointer, std::size_t, int block, long, const unsigned char*, int) {
  if (kind == _HOOK_FREE)
    shortcut_test::Free(pointer);
  return kind != _HOOK_ALLOC || block != _NORMAL_BLOCK || shortcut_test::Allow();
}
#else
void* operator new(std::size_t bytes) {
  using namespace shortcut_test;
  if (!Allow())
    throw std::bad_alloc();
  void* pointer = std::malloc(bytes ? bytes : 1);
  if (!pointer)
    throw std::bad_alloc();
  if (active) {
    if (records == static_cast<int>(allocations.size()))
      std::abort();
    allocations[records++] = {pointer, bytes, true};
  }
  return pointer;
}
void* operator new[](std::size_t bytes) { return ::operator new(bytes); }
void operator delete(void* pointer) noexcept {
  shortcut_test::Free(pointer);
  std::free(pointer);
}
void operator delete[](void* pointer) noexcept { ::operator delete(pointer); }
void operator delete(void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
void operator delete[](void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
#endif

namespace {
void Require(bool value) {
  if (!value)
    std::abort();
}
class CountedVertex : public Vertex {
public:
  CountedVertex(double x, double y, int index) : Vertex(x, y, 101 + index), index_(index) {}
  ~CountedVertex() override { ++shortcut_test::destroyed[index_]; }

private:
  int index_;
};
struct PendingEdgeDelete {
  void operator()(Edge* edge) const noexcept {
    edge->DetachVertices();
    delete edge;
  }
};
struct State {
  std::size_t mesh = 0, front = 0, rejected = 0, owner_vertices = 0, owner_edges = 0;
  int live_vertices = 0, adjacency = 0, geometry_faces = 0, free_edges = 0;
  long last_face = -1, last_edge = -1;
};
class Fixture : public AdvancingFront {
public:
  std::array<Vertex*, 6> points{};
  std::array<Edge*, 6> sides{};
  void Triangle(int index, bool front_based) {
    const double x = 3.0 * index;
    for (int n = 0; n < 3; ++n) {
      auto vertex = std::make_unique<CountedVertex>(x + (n == 0   ? 0
                                                         : n == 1 ? 1
                                                                  : 0.5),
                                                    n == 2 ? 1 : 0, 3 * index + n);
      points[3 * index + n] = vertex.get();
      innerVertices.push_back(vertex.get());
      vertex.release();
      vertices.push_back(points[3 * index + n]);
    }
    for (int n = 0; n < 3; ++n) {
      Vertex* a = points[3 * index + n];
      Vertex* b = points[3 * index + (n + 1) % 3];
      std::unique_ptr<Edge, PendingEdgeDelete> edge(new Edge(a, b, 201 + 3 * index + n));
      sides[3 * index + n] = edge.get();
      innerEdges.push_back(edge.get());
      edge.release();
      edges.push_back(sides[3 * index + n]);
      a->addAdjacentEdge(sides[3 * index + n]);
      b->addAdjacentEdge(sides[3 * index + n]);
      if (front_based || n != 0)
        front.push_back(sides[3 * index + n]);
      else
        rejected.push_back(sides[3 * index + n]);
    }
  }
  void SelectTarget(int index, int rotation, int count) {
    front.clear();
    for (int n = 0; n < count; ++n)
      front.push_back(sides[3 * index + (rotation + n) % 3]);
  }
  State Snapshot(int prefix, int rotation, int count) {
    State state;
    state.mesh = mesh.size();
    state.front = front.size();
    state.rejected = rejected.size();
    state.owner_vertices = innerVertices.size();
    state.owner_edges = innerEdges.size();
    state.last_face = lastFaceId;
    state.last_edge = lastEdgeId;
    Require(state.front == static_cast<std::size_t>(count));
    int position = 0;
    for (auto* side : front) {
      Require(side == sides[3 * prefix + (rotation + position) % 3]);
      ++position;
    }
    for (int i = 0; i < 3 * (prefix + 1); ++i) {
      if (shortcut_test::destroyed[i]) {
        std::fprintf(stderr, "borrowed_endpoint_destroyed=%d phase=%d denied=%d\n", i,
                     shortcut_test::phase, shortcut_test::denied);
        std::exit(4);
      }
      const int component = i / 3, n = i % 3;
      Require(points[i]->getId() == 101 + i);
      Require(points[i]->getX() == 3.0 * component + (n == 0 ? 0 : n == 1 ? 1 : 0.5));
      Require(points[i]->getY() == (n == 2 ? 1 : 0));
      ++state.live_vertices;
      const auto adjacent = points[i]->getAdjacentEdges();
      Require(adjacent.size() == 2 && adjacent.count(sides[3 * component + n]) == 1 &&
              adjacent.count(sides[3 * component + (n + 2) % 3]) == 1);
      ++state.adjacency;
      state.free_edges += sides[i]->isFree();
    }
    int index = 0;
    for (auto* face : mesh) {
      const int offset = (prefix == 1 && index == 0) ? 0 : rotation;
      Require(face->getId() == index + 1);
      Require(face->getV1() == points[3 * index + offset] &&
              face->getV2() == points[3 * index + (offset + 1) % 3] &&
              face->getV3() == points[3 * index + (offset + 2) % 3]);
      Require(face->getMid()->getX() == 3.0 * index + 0.5 && face->getMid()->getY() == 1.0 / 3 &&
              face->orientedSurface() == 0.5 && face->h == 0);
      ++state.geometry_faces;
      ++index;
    }
    return state;
  }
};
State Operation(bool sorted, int rotation, int prefix, int count, bool& threw, bool& done,
                int& returned) {
  Fixture fixture;
  const bool enabled_before_preparation = shortcut_test::enabled;
  shortcut_test::enabled = false;
  fixture.setBoundarySorted(sorted);
  fixture.Triangle(0, true);
  if (prefix) {
    Require(fixture.makeGeometryBasedMesh() == ADVF_GEOMETRY_MESH_DONE);
    fixture.Triangle(1, true);
  }
  fixture.SelectTarget(prefix, rotation, count);
  shortcut_test::enabled = enabled_before_preparation;
  try {
    returned = fixture.makeGeometryBasedMesh();
    done = returned == ADVF_GEOMETRY_MESH_DONE;
  } catch (const std::bad_alloc&) {
    shortcut_test::active = false;
    threw = true;
  }
  Require(fixture.isBoundarySorted() == sorted);
  return fixture.Snapshot(prefix, rotation, count);
}
} // namespace
int main(int argc, char* argv[]) {
  if (argc != 5)
    return 3;
  const bool sorted = std::atoi(argv[1]) != 0;
  const int rotation = std::atoi(argv[2]), prefix = std::atoi(argv[3]);
  const char* mode = argv[4];
  if (rotation < 0 || rotation > 2 || prefix < 0 || prefix > 1)
    return 3;
  if (std::strcmp(mode, "uaf-control") == 0)
    return shortcut_test::ExpiredAccess();
  int count = 3, target = std::atoi(mode);
  if (std::strncmp(mode, "guard-", 6) == 0) {
    count = std::atoi(mode + 6);
    if (prefix || count < 0 || count > 2)
      return 3;
  }
  bool threw = false, done = false;
  int returned = -1;
  Operation(sorted, rotation, prefix, count, threw, done, returned);
  shortcut_test::destroyed.fill(0);
  threw = done = false;
  returned = -1;
  shortcut_test::target = target;
  shortcut_test::enabled = true;
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemState before{}, after{}, difference{};
  const auto previous = _CrtSetAllocHook(Hook);
  _CrtMemCheckpoint(&before);
#endif
  State state;
  if (std::strcmp(mode, "leak-control") == 0 || std::strcmp(mode, "denial-control") == 0) {
    shortcut_test::target = std::strcmp(mode, "denial-control") == 0 ? 1 : 0;
    try {
      shortcut_test::Begin(0, 0);
      shortcut_test::RetainedStorageControl();
      shortcut_test::active = false;
    } catch (const std::bad_alloc&) {
      shortcut_test::active = false;
      threw = true;
    }
  } else
    state = Operation(sorted, rotation, prefix, count, threw, done, returned);
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
  for (int i = 0; i < shortcut_test::records; ++i)
    if (shortcut_test::allocations[i].live) {
      ++live;
      bytes += shortcut_test::allocations[i].size;
    }
  const char* profile = "native-allocation-observer";
#endif
  using namespace shortcut_test;
  std::printf(
      "{\"sorted\":%d,\"rotation\":%d,\"prefix\":%d,\"front_count\":%d,\"mode\":\"%s\","
      "\"profile\":\"%s\",\"threw\":%d,\"done\":%d,\"returned\":%d,"
      "\"seen\":%d,\"entered\":%d,\"attempts\":%d,\"denied\":%d,\"phase\":%d,"
      "\"constructed\":%d,\"adopted\":%d,\"before_id\":%ld,\"face_id\":%ld,\"before_mesh\":%zu,"
      "\"endpoint_ids\":[%ld,%ld,%ld],\"midpoint\":[%.17g,%.17g],\"area\":%.17g,"
      "\"face_freed\":%d,\"mid_freed\":%d,\"mesh\":%zu,\"front\":%zu,\"rejected\":%zu,"
      "\"owner_vertices\":%zu,\"owner_edges\":%zu,\"live_vertices\":%d,\"adjacency\":%d,"
      "\"geometry_faces\":%d,\"free_edges\":%d,\"last_face\":%ld,\"last_edge\":%ld,"
      "\"destroyed\":[%d,%d,%d,%d,%d,%d],\"retained_blocks\":%ld,\"retained_bytes\":%zu,"
      "\"cleanup_calls\":%d,\"cleanup_allocations\":%d}\n",
      sorted, rotation, prefix, count, mode, profile, threw, done, returned, seen, entered,
      attempts, denied, phase, constructed, adopted, before_id, face_id, before_mesh,
      endpoint_ids[0], endpoint_ids[1], endpoint_ids[2], midpoint[0], midpoint[1], area, face_freed,
      mid_freed, state.mesh, state.front, state.rejected, state.owner_vertices, state.owner_edges,
      state.live_vertices, state.adjacency, state.geometry_faces, state.free_edges, state.last_face,
      state.last_edge, destroyed[0], destroyed[1], destroyed[2], destroyed[3], destroyed[4],
      destroyed[5], live, bytes, cleanup_calls, cleanup_allocations);
  return live ? 1 : 0;
}
