#include "crab_mesh/aft/advancing_front.h"
#include "first_edge_hooks.h"
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

namespace first_edge_test {
struct Allocation {
  void* pointer;
  std::size_t size;
  bool live;
};
std::array<Allocation, 96> allocations{};
std::array<int, 8> destroyed{};
bool enabled = false, active = false, freed = false, mid_freed = false, owned = false,
     cleanup_active = false;
int cleanup_calls = 0, cleanup_allocations = 0;
Edge* pending = nullptr;
Vertex* midpoint = nullptr;
int attempts = 0, target = 0, denied = 0, records = 0, entered = 0, phase = -1;
long before_id = -1, edge_id = -1;
std::size_t before_owners = 0;
void Begin(long id, std::size_t owners, bool has_owner) noexcept {
  if (!enabled || entered)
    return;
  ++entered;
  active = true;
  phase = 0;
  before_id = id;
  before_owners = owners;
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
    if (pointer == pending)
      freed = true;
    if (pointer == midpoint)
      mid_freed = true;
  }
  for (int i = 0; i < records; ++i)
    if (allocations[i].pointer == pointer && allocations[i].live)
      allocations[i].live = false;
}
} // namespace first_edge_test
#if defined(_MSC_VER) && defined(_DEBUG)
int __cdecl Hook(int kind, void* pointer, std::size_t, int block, long, const unsigned char*, int) {
  if (kind == _HOOK_FREE)
    first_edge_test::Free(pointer);
  return kind != _HOOK_ALLOC || block != _NORMAL_BLOCK || first_edge_test::Allow();
}
#else
void* operator new(std::size_t bytes) {
  using namespace first_edge_test;
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
  first_edge_test::Free(pointer);
  std::free(pointer);
}
void operator delete[](void* pointer) noexcept { ::operator delete(pointer); }
void operator delete(void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
void operator delete[](void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
#endif

namespace {
void RequireAt(bool x, int line) {
  if (!x) {
    std::fprintf(stderr, "fixture_assertion_line=%d\n", line);
    std::abort();
  }
}
#define Require(x) RequireAt((x), __LINE__)
class CountedVertex : public Vertex {
  int index_;

public:
  CountedVertex(double x, double y, int index) : Vertex(x, y, 101 + index), index_(index) {}
  ~CountedVertex() override { ++first_edge_test::destroyed[index_]; }
};
struct EdgeDelete {
  void operator()(Edge* e) const noexcept {
    e->DetachVertices();
    delete e;
  }
};
struct State {
  std::size_t mesh = 0, owners = 0, views = 0, front = 0, rejected = 0, cell = 0;
  int borrowed = 0, adjacent_a = 0, adjacent_c = 0, owner_pending = 0, view_pending = 0,
      queue_pending = 0, cell_pending = 0, faces = 0, free_edges = 0, pending_adjacent = 0;
  long last_edge = 0, last_face = 0, face_order = 0;
};
class Fixture : public AdvancingFront {
public:
  std::array<Vertex*, 8> points{};
  std::array<Edge*, 8> sides{};
  void Triangle(int index, bool missing, bool front_based) {
    double x = 3.0 * index;
    int count = missing ? 4 : 3;
    int offset = 4 * index;
    for (int n = 0; n < count; ++n) {
      int k = offset + n;
      double px = missing ? (n == 1 || n == 2 ? 1 : 0) : (n == 0 ? 0 : n == 1 ? 1 : 0.5);
      auto p = std::make_unique<CountedVertex>(x + px,
                                               missing ? (n == 2   ? 1
                                                          : n == 3 ? 2
                                                                   : 0)
                                                       : (n == 2 ? 1 : 0),
                                               k);
      points[k] = p.get();
      innerVertices.push_back(p.get());
      p.release();
      vertices.push_back(points[k]);
    }
    for (int n = 0; n < count; ++n) {
      Vertex* a = points[offset + n];
      Vertex* b = points[offset + (n + 1) % count];
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
  void PrepareGeometry() {
    auto minimum = std::make_unique<Vertex>(-0.5, -0.5),
         maximum = std::make_unique<Vertex>(7.5, 7.5);
    auto root = std::make_unique<QuadtreeCell>(quadtree->getCellId(), quadtree, minimum.get(),
                                               maximum.get());
    quadtree->setRoot(root.get());
    root.release();
    minimum.release();
    maximum.release();
  }
  int Run(bool front_based, bool geometry) {
    for (auto* e : sides)
      if (e)
        e->setCell(quadtree->getRoot());
    return makeMesh(front_based, geometry);
  }
  void PreparePrefix() {
    Triangle(0, false, true);
    Require(Run(true, false) == ADVF_TOPOLOGY_MESH_DONE && mesh.size() == 1);
  }
  State Snapshot(int prefix, bool consume_stale) {
    using namespace first_edge_test;
    State s;
    s.mesh = mesh.size();
    s.owners = innerEdges.size();
    s.views = edges.size();
    s.front = front.size();
    s.rejected = rejected.size();
    s.last_edge = lastEdgeId;
    s.last_face = lastFaceId;
    for (int i = 0; i < 8; ++i) {
      if (!points[i])
        continue;
      if (destroyed[i]) {
        std::fprintf(stderr, "borrowed_endpoint_destroyed=%d phase=%d denied=%d\n", i, phase,
                     denied);
        std::exit(4);
      }
      auto* p = points[i];
      Require(p->getId() == 101 + i);
      double x = i < 4 ? (i == 0 ? 0 : i == 1 ? 1 : 0.5) : (i == 5 || i == 6 ? 4 : 3);
      Require(p->getX() == x && p->getY() == (i == 7 ? 2 : i == 2 || i == 6 ? 1 : 0));
      ++s.borrowed;
      auto adjacent = p->getAdjacentEdges();
      if (pending) {
        s.pending_adjacent += static_cast<int>(adjacent.count(pending));
        if (freed && adjacent.count(pending) && consume_stale) {
          volatile long expired = ReadEdgeId(pending);
          (void)expired;
        }
      }
      if (i == 4)
        s.adjacent_a = static_cast<int>(adjacent.size());
      if (i == 6)
        s.adjacent_c = static_cast<int>(adjacent.size());
      if (i < 4 || i == 5 || i == 7)
        Require(adjacent.size() == 2);
    }
    for (auto* e : innerEdges) {
      s.owner_pending += e == pending;
      s.free_edges += e->isFree();
    }
    for (auto* e : edges)
      s.view_pending += e == pending;
    for (auto* e : front)
      s.queue_pending += e == pending;
    for (auto* e : rejected)
      s.queue_pending += e == pending;
    auto cell_edges = quadtree->getRoot()->getEdges();
    s.cell = cell_edges.size();
    for (auto* e : cell_edges)
      s.cell_pending += e == pending;
    int index = 0;
    for (auto* face : mesh) {
      Require(face->getId() == index + 1);
      if (prefix && index == 0) {
        Require(face->getV1() == points[0] && face->getV2() == points[1] &&
                face->getV3() == points[2]);
        Require(face->getMid()->getX() == 0.5 && face->getMid()->getY() == 1.0 / 3);
      } else {
        int n = index - prefix;
        if (n == 0)
          Require(face->getV1() == points[4] && face->getV2() == points[5] &&
                  face->getV3() == points[6]);
        else {
          Require(n == 1);
          auto a = face->getV1();
          auto b = face->getV2();
          auto c = face->getV3();
          Require((a == points[4] && b == points[6] && c == points[7]) ||
                  (a == points[6] && b == points[7] && c == points[4]) ||
                  (a == points[7] && b == points[4] && c == points[6]));
        }
        Require(face->getMid()->getX() == (n == 0 ? 11.0 / 3 : 10.0 / 3) &&
                face->getMid()->getY() == (n == 0 ? 1.0 / 3 : 1.0));
      }
      Require(face->orientedSurface() ==
              ((prefix && index == 0) || index - prefix == 0 ? 0.5 : 1.0));
      s.face_order = s.face_order * 1000 + (face->getV1()->getId() - 100) * 100 +
                     (face->getV2()->getId() - 100) * 10 + face->getV3()->getId() - 100;
      ++s.faces;
      ++index;
    }
    if (pending && !freed) {
      Require(pending->getV1() == points[4] && pending->getV2() == points[6]);
      Require(pending->getMid()->getX() == 3.5 && pending->getMid()->getY() == 0.5);
    }
    return s;
  }
};
State Operation(bool front_based, bool geometry, int sorted, int prefix, int action, bool& threw,
                int& status) {
  Fixture f;
  f.PrepareGeometry();
  f.setBoundarySorted(sorted != 0);
  if (prefix)
    f.PreparePrefix();
  f.Triangle(1, true, front_based);
  try {
    status = f.Run(front_based, geometry);
  } catch (const std::bad_alloc&) {
    first_edge_test::active = false;
    threw = true;
  }
  using namespace first_edge_test;
  State state = f.Snapshot(prefix, action == 1);
  return state;
}
} // namespace
int main(int argc, char** argv) {
  if (argc != 7)
    return 3;
  using namespace first_edge_test;
  bool front_based = std::atoi(argv[1]) != 0, geometry = std::atoi(argv[2]) != 0;
  int sorted = std::atoi(argv[3]), prefix = std::atoi(argv[4]), action = std::atoi(argv[6]);
  target = std::atoi(argv[5]);
  if (std::strcmp(argv[5], "uaf-control") == 0)
    return ExpiredAccess();
  bool threw = false;
  int status = -1;
  Operation(front_based, geometry, sorted, prefix, 0, threw, status);
  destroyed.fill(0);
  threw = false;
  status = -1;
  enabled = true;
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemState before{}, after{}, difference{};
  auto previous = _CrtSetAllocHook(Hook);
  _CrtMemCheckpoint(&before);
#endif
  State state;
  if (std::strcmp(argv[5], "leak-control") == 0 || std::strcmp(argv[5], "denial-control") == 0) {
    target = std::strcmp(argv[5], "denial-control") == 0 ? 1 : 0;
    active = true;
    try {
      RetainedStorageControl();
      active = false;
    } catch (const std::bad_alloc&) {
      active = false;
      threw = true;
    }
  } else
    state = Operation(front_based, geometry, sorted, prefix, action, threw, status);
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
  std::printf(
      "{\"context\":[%d,%d,%d,%d],\"target\":%d,\"owned\":%d,\"cleanup_calls\":%d,\"cleanup_"
      "allocations\":%d,\"pending_adjacent\":%d,\"threw\":%d,\"status\":%d,\"entered\":%d,"
      "\"phase\":%d,\"attempts\":%d,\"denied\":%d,\"before_id\":%ld,\"edge_id\":%ld,\"before_"
      "owners\":%zu,\"freed\":%d,\"mid_freed\":%d,\"mesh\":%zu,\"owners\":%zu,\"views\":%zu,"
      "\"front\":%zu,\"rejected\":%zu,\"cell\":%zu,\"borrowed\":%d,\"adjacent_a\":%d,\"adjacent_"
      "c\":%d,\"owner_pending\":%d,\"view_pending\":%d,\"queue_pending\":%d,\"cell_pending\":%d,"
      "\"faces\":%d,\"free_edges\":%d,\"last_edge\":%ld,\"last_face\":%ld,\"face_order\":%ld,"
      "\"destroyed\":[%d,%d,%d,%d,%d,%d,%d,%d],\"retained_blocks\":%ld,\"retained_bytes\":%zu}\n",
      front_based, geometry, sorted, prefix, target, owned, cleanup_calls, cleanup_allocations,
      state.pending_adjacent, threw, status, entered, phase, attempts, denied, before_id, edge_id,
      before_owners, freed, mid_freed, state.mesh, state.owners, state.views, state.front,
      state.rejected, state.cell, state.borrowed, state.adjacent_a, state.adjacent_c,
      state.owner_pending, state.view_pending, state.queue_pending, state.cell_pending, state.faces,
      state.free_edges, state.last_edge, state.last_face, state.face_order, destroyed[0],
      destroyed[1], destroyed[2], destroyed[3], destroyed[4], destroyed[5], destroyed[6],
      destroyed[7], live, bytes);
  return live ? 1 : 0;
}
