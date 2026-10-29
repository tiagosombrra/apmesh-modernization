#include "crab_mesh/aft/advancing_front.h"
#include "marker_hooks.h"
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

namespace marker_test {
struct Allocation {
  void* pointer;
  std::size_t size;
  bool live;
};
std::array<Allocation, 64> allocations{};
std::array<int, 6> destroyed{};
Edge* marker = nullptr;
Vertex* marker_mid = nullptr;
bool enabled = false, active = false, capture = false;
bool marker_freed = false, mid_freed = false, cleanup_active = false;
int cleanup_calls = 0, cleanup_allocations = 0;
int target_window = 1, selection_seen = 0, face_seen = 0;
int attempts = 0, denied = 0, target = 0, records = 0;
int requested_stage = 0, phase = -1, constructed = 0, published = 0, retiring = 0;
void BeginMarker() noexcept {
  if (!enabled)
    return;
  capture = true;
  active = requested_stage == 0;
  phase = 0;
}
void Constructed(Edge* edge) noexcept {
  if (!enabled)
    return;
  marker = edge;
  marker_mid = edge->getMid();
  if (edge->getV1() || edge->getV2() || !marker_mid)
    std::abort();
  ++constructed;
}
void Published() noexcept {
  if (!enabled)
    return;
  ++published;
  if (marker_freed) {
    std::fprintf(stderr, "marker_destroyed_before_consumption\n");
    std::exit(5);
  }
  capture = active = false;
}
void Retiring(Edge* edge) noexcept {
  if (!enabled)
    return;
  if (edge != marker)
    std::abort();
  ++retiring;
}
void BeginSelection() noexcept {
  if (!enabled)
    return;
  ++selection_seen;
  active = requested_stage == 1 && selection_seen == target_window;
  phase = 1;
}
void BeginFace() noexcept {
  if (!enabled)
    return;
  ++face_seen;
  active = requested_stage == 2 && face_seen == target_window;
  phase = 2;
}
void EndWindow() noexcept { active = false; }
void BeginCleanup() noexcept {
  if (enabled) {
    ++cleanup_calls;
    cleanup_active = true;
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
    if (pointer == marker)
      marker_freed = true;
    if (pointer == marker_mid)
      mid_freed = true;
  }
  for (int i = 0; i < records; ++i)
    if (allocations[i].pointer == pointer && allocations[i].live)
      allocations[i].live = false;
}
} // namespace marker_test
#if defined(_MSC_VER) && defined(_DEBUG)
int __cdecl Hook(int kind, void* pointer, std::size_t, int block, long, const unsigned char*, int) {
  if (kind == _HOOK_FREE)
    marker_test::Free(pointer);
  return kind != _HOOK_ALLOC || block != _NORMAL_BLOCK || marker_test::Allow();
}
#else
void* operator new(std::size_t bytes) {
  using namespace marker_test;
  if (!Allow())
    throw std::bad_alloc();
  void* pointer = std::malloc(bytes ? bytes : 1);
  if (!pointer)
    throw std::bad_alloc();
  if (capture) {
    if (records == static_cast<int>(allocations.size()))
      std::abort();
    allocations[records++] = {pointer, bytes, true};
  }
  return pointer;
}
void* operator new[](std::size_t bytes) { return ::operator new(bytes); }
void operator delete(void* pointer) noexcept {
  marker_test::Free(pointer);
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
  ~CountedVertex() override { ++marker_test::destroyed[index_]; }

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
  int marker_front = 0, marker_owned = 0, marker_rejected = 0;
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
  void PrepareGeometry() {
    auto minimum = std::make_unique<Vertex>(0, 0);
    auto maximum = std::make_unique<Vertex>(4, 4);
    auto root = std::make_unique<QuadtreeCell>(quadtree->getCellId(), quadtree, minimum.get(),
                                               maximum.get());
    quadtree->setRoot(root.get());
    for (auto* side : sides)
      if (side)
        side->setCell(root.get());
    root.release();
    minimum.release();
    maximum.release();
  }
  bool Run(bool front_based, bool geometry) {
    return makeMesh(front_based, geometry) ==
           (geometry ? ADVF_GEOMETRY_MESH_DONE : ADVF_TOPOLOGY_MESH_DONE);
  }
  State Snapshot(int triangles) {
    State state;
    state.mesh = mesh.size();
    state.front = front.size();
    state.rejected = rejected.size();
    state.owner_vertices = innerVertices.size();
    state.owner_edges = innerEdges.size();
    state.last_face = lastFaceId;
    state.last_edge = lastEdgeId;
    for (auto* edge : front)
      state.marker_front += edge == marker_test::marker;
    for (auto* edge : innerEdges)
      state.marker_owned += edge == marker_test::marker;
    for (auto* edge : rejected)
      state.marker_rejected += edge == marker_test::marker;
    if (marker_test::marker_freed &&
        (state.marker_front || state.marker_rejected || state.marker_owned)) {
      std::fprintf(stderr, "expired_marker_observer front=%d rejected=%d owned=%d\n",
                   state.marker_front, state.marker_rejected, state.marker_owned);
      std::exit(4);
    }
    for (int i = 0; i < triangles * 3; ++i) {
      const int component = i / 3, n = i % 3;
      if (marker_test::destroyed[i] != 0) {
        std::fprintf(stderr, "borrowed_endpoint_destroyed=%d phase=%d denied=%d\n", i,
                     marker_test::phase, marker_test::denied);
        std::exit(4);
      }
      Require(points[i]->getId() == 101 + i);
      Require(points[i]->getX() == 3.0 * component + (n == 0   ? 0
                                                      : n == 1 ? 1
                                                               : 0.5) &&
              points[i]->getY() == (n == 2 ? 1 : 0));
      ++state.live_vertices;
      const auto adjacent = points[i]->getAdjacentEdges();
      Require(adjacent.size() == 2 && adjacent.count(sides[3 * component + n]) == 1 &&
              adjacent.count(sides[3 * component + (n + 2) % 3]) == 1);
      ++state.adjacency;
      state.free_edges += sides[i]->isFree();
    }
    int index = 0;
    for (auto* face : mesh) {
      Require(face->getId() == index + 1 && face->getV1() == points[3 * index] &&
              face->getV2() == points[3 * index + 1] && face->getV3() == points[3 * index + 2]);
      Require(face->getMid()->getX() == 3.0 * index + 0.5 && face->getMid()->getY() == 1.0 / 3 &&
              face->orientedSurface() == 0.5 && face->h == 0);
      ++state.geometry_faces;
      ++index;
    }
    return state;
  }
};
State Operation(bool front_based, bool geometry, int prefix, bool& threw, bool& done) {
  Fixture fixture;
  for (int i = 0; i <= prefix; ++i)
    fixture.Triangle(i, front_based);
  if (geometry)
    fixture.PrepareGeometry();
  try {
    done = fixture.Run(front_based, geometry);
  } catch (const std::bad_alloc&) {
    marker_test::active = marker_test::capture = false;
    threw = true;
  }
  return fixture.Snapshot(prefix + 1);
}
} // namespace

int main(int argc, char* argv[]) {
  if (argc != 4)
    return 3;
  if (std::strcmp(argv[3], "uaf-control") == 0)
    return marker_test::ExpiredAccess();
  const int stage = std::atoi(argv[1]), prefix = std::atoi(argv[2]);
  const char* mode = argv[3];
  if (stage < 0 || stage > 2 || prefix < 0 || prefix > 1)
    return 3;
  bool threw = false, done = false;
  Operation(true, true, prefix, threw, done);
  marker_test::destroyed.fill(0);
  threw = done = false;
  marker_test::target_window = prefix + 1;
  marker_test::target = std::atoi(mode);
  marker_test::requested_stage = stage;
  marker_test::enabled = true;
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemState before{}, after{}, difference{};
  const auto previous = _CrtSetAllocHook(Hook);
  _CrtMemCheckpoint(&before);
#endif
  State state;
  if (std::strcmp(mode, "leak-control") == 0 || std::strcmp(mode, "denial-control") == 0) {
    marker_test::active = marker_test::capture = true;
    marker_test::target = std::strcmp(mode, "denial-control") == 0 ? 1 : 0;
    try {
      (void)new Vertex(0.25, 0.75);
      marker_test::active = marker_test::capture = false;
    } catch (const std::bad_alloc&) {
      marker_test::active = marker_test::capture = false;
      threw = true;
    }
  } else
    state = Operation(true, true, prefix, threw, done);
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
  for (int i = 0; i < marker_test::records; ++i)
    if (marker_test::allocations[i].live) {
      ++live;
      bytes += marker_test::allocations[i].size;
    }
  const char* profile = "native-allocation-observer";
#endif
  using namespace marker_test;
  std::printf(
      "{\"stage\":%d,\"prefix\":%d,\"mode\":\"%s\",\"profile\":\"%s\","
      "\"threw\":%d,\"done\":%d,\"attempts\":%d,\"denied\":%d,\"constructed\":%d,"
      "\"published\":%d,\"retiring\":%d,\"marker_freed\":%d,\"mid_freed\":%d,"
      "\"selection_seen\":%d,\"face_seen\":%d,\"marker_front\":%d,\"marker_owned\":%d,"
      "\"marker_rejected\":%d,\"cleanup_calls\":%d,\"cleanup_allocations\":%d,"
      "\"mesh\":%zu,\"front\":%zu,\"rejected\":%zu,\"owner_vertices\":%zu,\"owner_edges\":%zu,"
      "\"live_vertices\":%d,\"adjacency\":%d,\"geometry_faces\":%d,\"free_edges\":%d,"
      "\"last_face\":%ld,\"last_edge\":%ld,\"destroyed\":[%d,%d,%d,%d,%d,%d],"
      "\"retained_blocks\":%ld,\"retained_bytes\":%zu}\n",
      stage, prefix, mode, profile, threw, done, attempts, denied, constructed, published, retiring,
      marker_freed, mid_freed, selection_seen, face_seen, state.marker_front, state.marker_owned,
      state.marker_rejected, cleanup_calls, cleanup_allocations, state.mesh, state.front,
      state.rejected, state.owner_vertices, state.owner_edges, state.live_vertices, state.adjacency,
      state.geometry_faces, state.free_edges, state.last_face, state.last_edge, destroyed[0],
      destroyed[1], destroyed[2], destroyed[3], destroyed[4], destroyed[5], live, bytes);
  return live ? 1 : 0;
}
