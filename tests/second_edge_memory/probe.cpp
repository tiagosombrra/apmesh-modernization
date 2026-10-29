#include "crab_mesh/aft/advancing_front.h"
#include "second_edge_hooks.h"
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

namespace second_edge_test {
struct Allocation {
  void* pointer;
  std::size_t size;
  bool live;
};
std::array<Allocation, 96> allocations{};
std::array<int, 12> destroyed{};
bool enabled = false, active = false, freed = false, mid_freed = false, owned = false,
     cleanup_active = false;
int cleanup_calls = 0, cleanup_allocations = 0;
Edge* pending = nullptr;
Vertex* midpoint = nullptr;
int attempts = 0, target = 0, denied = 0, records = 0, entered = 0, phase = -1;
long before_id = -1, edge_id = -1;
std::size_t before_owners = 0;
Edge* first_pointer = nullptr;
Vertex* first_mid = nullptr;
bool first_freed = false, first_mid_freed = false;
void Begin(long id, std::size_t owners, Edge* first, bool has_owner) noexcept {
  if (!enabled || entered)
    return;
  ++entered;
  active = true;
  phase = 0;
  before_id = id;
  before_owners = owners;
  first_pointer = first;
  first_mid = first->getMid();
  owned = has_owner;
}
void Built(Edge* edge) noexcept {
  if (!active)
    return;
  pending = edge;
  midpoint = edge->getMid();
  edge_id = edge->getId();
  phase = 1;
}
void Step(int next) noexcept {
  if (active)
    phase = next;
}
void End() noexcept {
  if (active) {
    phase = 7;
    active = false;
  }
}
void BeginCleanup() noexcept {
  if (enabled) {
    cleanup_active = true;
    ++cleanup_calls;
  }
}
void EndCleanup() noexcept { cleanup_active = false; }
bool Allow() noexcept {
  if (cleanup_active) {
    ++cleanup_allocations;
    return false;
  }
  if (active && ++attempts == target) {
    ++denied;
    return false;
  }
  return true;
}
void Free(void* pointer) noexcept {
  if (enabled && pointer) {
    if (pointer == first_pointer)
      first_freed = true;
    if (pointer == first_mid)
      first_mid_freed = true;
  }
  if (enabled && pointer) {
    if (pointer == pending)
      freed = true;
    if (pointer == midpoint)
      mid_freed = true;
  }
  for (int i = 0; i < records; ++i)
    if (allocations[i].pointer == pointer && allocations[i].live)
      allocations[i].live = false;
}
} // namespace second_edge_test
#if defined(_MSC_VER) && defined(_DEBUG)
int __cdecl Hook(int kind, void* pointer, std::size_t, int block, long, const unsigned char*, int) {
  if (kind == _HOOK_FREE)
    second_edge_test::Free(pointer);
  return kind != _HOOK_ALLOC || block != _NORMAL_BLOCK || second_edge_test::Allow();
}
#else
void* operator new(std::size_t bytes) {
  using namespace second_edge_test;
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
  second_edge_test::Free(pointer);
  std::free(pointer);
}
void operator delete[](void* pointer) noexcept { ::operator delete(pointer); }
void operator delete(void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
void operator delete[](void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
#endif

namespace {
void Require(bool value) {
  if (!value) {
    std::fprintf(stderr, "fixture_contract_failed\n");
    std::abort();
  }
}
class CountedVertex : public Vertex {
  int index_;

public:
  CountedVertex(double x, double y, int index) : Vertex(x, y, 101 + index), index_(index) {}
  ~CountedVertex() override { ++second_edge_test::destroyed[index_]; }
};
struct EdgeDelete {
  void operator()(Edge* edge) const noexcept {
    edge->DetachVertices();
    delete edge;
  }
};
struct State {
  std::size_t mesh = 0, owners = 0, views = 0, front = 0, rejected = 0, cell = 0;
  int borrowed = 0, owner_pending = 0, view_pending = 0, queue_pending = 0, cell_pending = 0,
      free_edges = 0;
  int first_owned = 0, first_view = 0, first_adjacency = 0, first_cell = 0, first_free = -1;
  long last_edge = 0, last_face = 0, first_id = -1;
  std::array<int, 12> adjacency{};
  std::array<double, 4> first_geometry{};
  std::array<double, 7> pending_geometry{};
  std::array<std::array<double, 7>, 4> faces{};
};
class Fixture : public AdvancingFront {
public:
  std::array<Vertex*, 12> points{};
  std::array<Edge*, 12> sides{};
  void Polygon(bool prefix, bool first_new, bool front_based) {
    const int count = prefix ? 3 : first_new ? 5 : 4, offset = prefix ? 0 : 6;
    const std::array<std::array<double, 2>, 5> triangle{{{0, 0}, {1, 0}, {0.5, 1}, {0, 0}, {0, 0}}};
    const std::array<std::array<double, 2>, 5> quad{{{3, 0}, {4, 0}, {4, 2}, {3, 1}, {0, 0}}};
    const std::array<std::array<double, 2>, 5> pentagon{{{3, 0}, {5, 0}, {6, 2}, {4, 1}, {2, 2}}};
    const auto& coordinates = prefix ? triangle : first_new ? pentagon : quad;
    for (int n = 0; n < count; ++n) {
      int i = offset + n;
      auto p = std::make_unique<CountedVertex>(coordinates[n][0], coordinates[n][1], i);
      points[i] = p.get();
      innerVertices.push_back(p.get());
      p.release();
      vertices.push_back(points[i]);
    }
    for (int n = 0; n < count; ++n) {
      auto* a = points[offset + n];
      auto* b = points[offset + (n + 1) % count];
      std::unique_ptr<Edge, EdgeDelete> e(new Edge(a, b, 201 + offset + n));
      sides[offset + n] = e.get();
      innerEdges.push_back(e.get());
      e.release();
      edges.push_back(sides[offset + n]);
      a->addAdjacentEdge(sides[offset + n]);
      b->addAdjacentEdge(sides[offset + n]);
      if (front_based || n != 0)
        front.push_back(sides[offset + n]);
      else
        rejected.push_back(sides[offset + n]);
    }
  }
  void Geometry() {
    auto low = std::make_unique<Vertex>(-1, -1), high = std::make_unique<Vertex>(8, 8);
    auto root =
        std::make_unique<QuadtreeCell>(quadtree->getCellId(), quadtree, low.get(), high.get());
    quadtree->setRoot(root.get());
    root.release();
    low.release();
    high.release();
  }
  int Run(bool front_based, bool geometry) {
    for (auto* side : sides)
      if (side)
        side->setCell(quadtree->getRoot());
    return makeMesh(front_based, geometry);
  }
  void Prefix() {
    Polygon(true, false, true);
    Require(Run(true, false) == ADVF_TOPOLOGY_MESH_DONE && mesh.size() == 1);
  }
  State Snapshot(bool consume_stale) {
    using namespace second_edge_test;
    State s;
    s.mesh = mesh.size();
    s.owners = innerEdges.size();
    s.views = edges.size();
    s.front = front.size();
    s.rejected = rejected.size();
    s.last_edge = lastEdgeId;
    s.last_face = lastFaceId;
    for (int i = 0; i < 12; ++i) {
      if (!points[i])
        continue;
      if (destroyed[i]) {
        std::fprintf(stderr, "borrowed_endpoint_destroyed=%d phase=%d denied=%d\n", i, phase,
                     denied);
        std::exit(4);
      }
      Require(points[i]->getId() == 101 + i);
      ++s.borrowed;
      const auto adjacent = points[i]->getAdjacentEdges();
      s.adjacency[i] = static_cast<int>(adjacent.size());
      if (consume_stale && freed && adjacent.count(pending)) {
        volatile long expired = ReadEdgeId(pending);
        (void)expired;
      }
    }
    auto* first = findEdge(points[6], points[9]);
    Require(first != nullptr);
    if (entered)
      Require(first == first_pointer);
    s.first_id = first->getId();
    s.first_free = first->isFree();
    s.first_geometry = {static_cast<double>(first->getV1()->getId()),
                        static_cast<double>(first->getV2()->getId()), first->getMid()->getX(),
                        first->getMid()->getY()};
    s.first_adjacency = static_cast<int>(first->getV1()->getAdjacentEdges().count(first) +
                                         first->getV2()->getAdjacentEdges().count(first));
    for (auto* edge : innerEdges) {
      s.owner_pending += edge == pending;
      s.first_owned += edge == first;
      s.free_edges += edge->isFree();
    }
    for (auto* edge : edges) {
      s.view_pending += edge == pending;
      s.first_view += edge == first;
    }
    for (auto* edge : front)
      s.queue_pending += edge == pending;
    for (auto* edge : rejected)
      s.queue_pending += edge == pending;
    const auto cells = quadtree->getRoot()->getEdges();
    s.cell = cells.size();
    for (auto* edge : cells) {
      s.cell_pending += edge == pending;
      s.first_cell += edge == first;
    }
    int n = 0;
    for (auto* face : mesh) {
      Require(n < 4);
      s.faces[n++] = {static_cast<double>(face->getId()),
                      static_cast<double>(face->getV1()->getId()),
                      static_cast<double>(face->getV2()->getId()),
                      static_cast<double>(face->getV3()->getId()),
                      face->getMid()->getX(),
                      face->getMid()->getY(),
                      face->orientedSurface()};
    }
    if (pending && !freed)
      s.pending_geometry = {static_cast<double>(pending->getId()),
                            static_cast<double>(pending->getV1()->getId()),
                            static_cast<double>(pending->getV2()->getId()),
                            pending->getMid()->getX(),
                            pending->getMid()->getY(),
                            pending->getV1()->getX(),
                            pending->getV2()->getX()};
    return s;
  }
};
State Operation(bool front_based, bool geometry, int sorted, int prefix, int first_new, int action,
                bool& threw, int& status) {
  Fixture f;
  f.Geometry();
  f.setBoundarySorted(sorted != 0);
  if (prefix)
    f.Prefix();
  f.Polygon(false, first_new != 0, front_based);
  try {
    status = f.Run(front_based, geometry);
  } catch (const std::bad_alloc&) {
    second_edge_test::active = false;
    threw = true;
  }
  using namespace second_edge_test;
  return f.Snapshot(action == 3);
}
} // namespace
int main(int argc, char** argv) {
  if (argc != 8)
    return 3;
  using namespace second_edge_test;
  const int front_based = std::atoi(argv[1]), geometry = std::atoi(argv[2]),
            sorted = std::atoi(argv[3]), prefix = std::atoi(argv[4]),
            first_new = std::atoi(argv[5]), action = std::atoi(argv[7]);
  target = std::atoi(argv[6]);
  if (std::strcmp(argv[6], "uaf-control") == 0)
    return ExpiredAccess();
  bool threw = false;
  int status = -1;
  Operation(front_based, geometry, sorted, prefix, first_new, 0, threw, status);
  destroyed.fill(0);
  threw = false;
  status = -1;
  enabled = true;
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemState before{}, after{}, difference{};
  auto previous = _CrtSetAllocHook(Hook);
  _CrtMemCheckpoint(&before);
#endif
  State s;
  if (std::strcmp(argv[6], "leak-control") == 0 || std::strcmp(argv[6], "denial-control") == 0) {
    target = std::strcmp(argv[6], "denial-control") == 0 ? 1 : 0;
    active = true;
    try {
      RetainedStorageControl();
      active = false;
    } catch (const std::bad_alloc&) {
      active = false;
      threw = true;
    }
  } else
    s = Operation(front_based, geometry, sorted, prefix, first_new, action, threw, status);
  long live = 0;
  std::size_t bytes = 0;
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtSetAllocHook(previous);
  _CrtMemDifference(&difference, &before, &after);
  live = difference.lCounts[_NORMAL_BLOCK];
  bytes = difference.lSizes[_NORMAL_BLOCK];
#else
  for (int i = 0; i < records; ++i)
    if (allocations[i].live) {
      ++live;
      bytes += allocations[i].size;
    }
#endif
  std::printf("{\"context\":[%d,%d,%d,%d,%d],\"target\":%d,\"action\":%d,\"owned\":%d,\"entered\":%"
              "d,\"phase\":%d,\"attempts\":%d,\"denied\":%d,\"threw\":%d,\"status\":%d,\"before_"
              "id\":%ld,\"edge_id\":%ld,\"before_owners\":%zu,\"freed\":%d,\"mid_freed\":%d,"
              "\"first_freed\":%d,\"first_mid_freed\":%d,\"cleanup_calls\":%d,\"cleanup_"
              "allocations\":%d,\"retained_blocks\":%ld,\"retained_bytes\":%zu",
              front_based, geometry, sorted, prefix, first_new, target, action, owned, entered,
              phase, attempts, denied, threw, status, before_id, edge_id, before_owners, freed,
              mid_freed, first_freed, first_mid_freed, cleanup_calls, cleanup_allocations, live,
              bytes);
  std::printf(
      ",\"mesh\":%zu,\"owners\":%zu,\"views\":%zu,\"front\":%zu,\"rejected\":%zu,\"cell\":%zu,"
      "\"borrowed\":%d,\"owner_pending\":%d,\"view_pending\":%d,\"queue_pending\":%d,\"cell_"
      "pending\":%d,\"free_edges\":%d,\"last_edge\":%ld,\"last_face\":%ld,\"first_id\":%ld,\"first_"
      "owned\":%d,\"first_view\":%d,\"first_adjacency\":%d,\"first_cell\":%d,\"first_free\":%d",
      s.mesh, s.owners, s.views, s.front, s.rejected, s.cell, s.borrowed, s.owner_pending,
      s.view_pending, s.queue_pending, s.cell_pending, s.free_edges, s.last_edge, s.last_face,
      s.first_id, s.first_owned, s.first_view, s.first_adjacency, s.first_cell, s.first_free);
  std::printf(",\"destroyed\":[");
  for (int i = 0; i < 12; ++i)
    std::printf("%s%d", i ? "," : "", destroyed[i]);
  std::printf("],\"adjacency\":[");
  for (int i = 0; i < 12; ++i)
    std::printf("%s%d", i ? "," : "", s.adjacency[i]);
  std::printf("],\"first_geometry\":[");
  for (int i = 0; i < 4; ++i)
    std::printf("%s%.17g", i ? "," : "", s.first_geometry[i]);
  std::printf("],\"pending_geometry\":[");
  for (int i = 0; i < 7; ++i)
    std::printf("%s%.17g", i ? "," : "", s.pending_geometry[i]);
  std::printf("],\"faces\":[");
  for (int i = 0; i < 4; ++i) {
    std::printf("%s[", i ? "," : "");
    for (int j = 0; j < 7; ++j)
      std::printf("%s%.17g", j ? "," : "", s.faces[i][j]);
    std::printf("]");
  }
  std::printf("]}\n");
  return live ? 1 : 0;
}
