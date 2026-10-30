#include "crab_mesh/aft/advancing_front.h"
#include "ideal_hooks.h"
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
namespace ideal_test {
struct Allocation {
  void* p;
  std::size_t bytes;
  bool live;
};
std::array<Allocation, 256> allocations{};
std::array<int, 8> destroyed{};
bool enabled = false, armed = false, active = false, freed = false, cleanup = false;
int attempts = 0, target = 0, denied = 0, phase = 0, records = 0, entered = 0,
    cleanup_allocations = 0, cleanup_calls = 0;
unsigned long long events = 0;
Vertex* ideal = nullptr;
double ideal_x = 0, ideal_y = 0;
void Begin() noexcept {
  if (enabled && armed) {
    active = true;
    ++entered;
    phase = 10;
    events |= 1ULL;
  }
}
void Built(Vertex* v) noexcept {
  if (active) {
    ideal = v;
    ideal_x = v->getX();
    ideal_y = v->getY();
    phase = 20;
    events |= 2ULL;
  }
}
void Step(int n) noexcept {
  if (active) {
    phase = n;
    events |= 1ULL << (n - 20);
  }
}
void End() noexcept {
  if (active) {
    phase = 90;
    active = false;
  }
}
void BeginCleanup() noexcept {
  if (enabled && armed) {
    ++cleanup_calls;
    cleanup = true;
  }
}
void EndCleanup() noexcept { cleanup = false; }
bool Allow() noexcept {
  if (cleanup) {
    ++cleanup_allocations;
    return false;
  }
  if (active && ++attempts == target) {
    ++denied;
    return false;
  }
  return true;
}
void Free(void* p) noexcept {
  if (enabled && p && p == ideal)
    freed = true;
  for (int n = 0; n < records; ++n)
    if (allocations[n].p == p && allocations[n].live)
      allocations[n].live = false;
}
} // namespace ideal_test
#if defined(_MSC_VER) && defined(_DEBUG)
int __cdecl Hook(int kind, void* p, std::size_t, int block, long, const unsigned char*, int) {
  if (kind == _HOOK_FREE)
    ideal_test::Free(p);
  return kind != _HOOK_ALLOC || block != _NORMAL_BLOCK || ideal_test::Allow();
}
#else
void* operator new(std::size_t bytes) {
  using namespace ideal_test;
  if (!Allow())
    throw std::bad_alloc();
  void* p = std::malloc(bytes ? bytes : 1);
  if (!p)
    throw std::bad_alloc();
  if (active) {
    if (records == static_cast<int>(allocations.size()))
      std::abort();
    allocations[records++] = {p, bytes, true};
  }
  return p;
}
void* operator new[](std::size_t n) { return ::operator new(n); }
void operator delete(void* p) noexcept {
  ideal_test::Free(p);
  std::free(p);
}
void operator delete[](void* p) noexcept { ::operator delete(p); }
void operator delete(void* p, std::size_t) noexcept { ::operator delete(p); }
void operator delete[](void* p, std::size_t) noexcept { ::operator delete(p); }
#endif
namespace {
void Require(bool b) {
  if (!b) {
    std::fprintf(stderr, "fixture_contract_failed\n");
    std::abort();
  }
}
class CountedVertex : public Vertex {
  int index_;

public:
  CountedVertex(double x, double y, int i) : Vertex(x, y, 101 + i), index_(i) {}
  ~CountedVertex() override { ++ideal_test::destroyed[index_]; }
};
struct EdgeDelete {
  void operator()(Edge* e) const noexcept {
    e->DetachVertices();
    delete e;
  }
};
struct State {
  int owners = 0, views = 0, observers = 0, mesh = 0, edge_owners = 0, borrowed = 0;
  int ideal_owner = 0, ideal_view = 0, ideal_front = 0, best_kind = 0;
  long id = 0, best_id = -1;
  double best_x = 0, best_y = 0, area = 0;
  std::array<int, 8> adjacency{};
  std::array<double, 7> face{};
};
class Fixture : public AdvancingFront {
public:
  std::array<Vertex*, 8> points{};
  Edge* base = nullptr;
  QuadtreeCell* cell = nullptr;
  void Geometry() {
    auto low = std::make_unique<Vertex>(0, 0), high = std::make_unique<Vertex>(8, 8);
    auto root =
        std::make_unique<QuadtreeCell>(quadtree->getCellId(), quadtree, low.get(), high.get());
    quadtree->setRoot(root.release());
    low.release();
    high.release();
    quadtree->getRoot()->subdivideToLevel(2);
    cell = quadtree->getRoot()->getChild(QUAD_BOTTOM_LEFT)->getChild(QUAD_BOTTOM_LEFT);
    Require(cell->height() == 2.0);
  }
  Vertex* Point(double x, double y, int i) {
    auto v = std::make_unique<CountedVertex>(x, y, i);
    points[i] = v.get();
    innerVertices.push_back(v.get());
    v.release();
    vertices.push_back(points[i]);
    return points[i];
  }
  Edge* Side(Vertex* a, Vertex* b, int id) {
    std::unique_ptr<Edge, EdgeDelete> e(new Edge(a, b, id));
    auto p = e.get();
    innerEdges.push_back(p);
    e.release();
    edges.push_back(p);
    front.push_back(p);
    a->addAdjacentEdge(p);
    b->addAdjacentEdge(p);
    p->setCell(cell);
    return p;
  }
  void Prefix() {
    auto a = Point(5, 5, 4), b = Point(6, 5, 5), c = Point(5.5, 6, 6);
    Side(a, b, 301);
    Side(b, c, 302);
    Side(c, a, 303);
    Require(makeMesh(true, false) == ADVF_TOPOLOGY_MESH_DONE && mesh.size() == 1);
  }
  void Prepare(int mode, int reverse, int prefix) {
    Geometry();
    if (prefix)
      Prefix();
    frontVertices.clear();
    auto a = Point(0, 0, 0), b = Point(2, 0, 1);
    Vertex* c = nullptr;
    Vertex* d = nullptr;
    if (mode == 1 || mode == 6) {
      c = Point(2, 1.5, 2);
      d = Point(0, 1, 3);
    } else if (mode == 2) {
      c = Point(1, 0.1, 2);
      d = Point(0, 4, 3);
    } else if (mode == 3) {
      c = Point(2, 0.5, 2);
      d = Point(0, 0.5, 3);
    } else if (mode == 4) {
      c = Point(2, 2, 2);
      d = Point(0, 2, 3);
    } else {
      c = Point(2, 4, 2);
      d = Point(0, 4, 3);
    }
    base = Side(a, b, 201);
    Side(b, c, 202);
    Side(c, d, 203);
    Side(d, a, 204);
    frontVertices.push_back(a);
    frontVertices.push_back(b);
    if (mode != 3 && mode != 4 && mode != 5) {
      frontVertices.push_back(reverse ? d : c);
      frontVertices.push_back(reverse ? c : d);
    }
  }
  bool Select(Vertex*& best, int mode) { return findBestVertex(base, best, mode < 5); }
  State Snapshot(Vertex* best) {
    using namespace ideal_test;
    State s;
    s.owners = static_cast<int>(innerVertices.size());
    s.views = static_cast<int>(vertices.size());
    s.observers = static_cast<int>(frontVertices.size());
    s.mesh = static_cast<int>(mesh.size());
    s.edge_owners = static_cast<int>(innerEdges.size());
    s.id = lastVertexId;
    for (int i = 0; i < 8; ++i)
      if (points[i]) {
        if (destroyed[i]) {
          std::fprintf(stderr, "borrowed_vertex_destroyed=%d\n", i);
          std::exit(4);
        }
        Require(points[i]->getId() == 101 + i);
        ++s.borrowed;
        s.adjacency[i] = static_cast<int>(points[i]->getAdjacentEdges().size());
        if (points[i] == best)
          s.best_kind = 2;
      }
    for (auto p : innerVertices) {
      s.ideal_owner += ideal && p == ideal;
      if (p == best && !s.best_kind)
        s.best_kind = 1;
    }
    for (auto p : vertices)
      s.ideal_view += ideal && p == ideal;
    for (auto p : frontVertices)
      s.ideal_front += ideal && p == ideal;
    if (best && !s.best_kind) {
      if (best == ideal)
        s.best_kind = freed ? 3 : 1;
      else
        s.best_kind = 4;
    }
    if (s.best_kind == 1 || s.best_kind == 2) {
      s.best_id = best->getId();
      s.best_x = best->getX();
      s.best_y = best->getY();
    }
    for (auto f : mesh) {
      s.area += f->orientedSurface();
      s.face = {static_cast<double>(f->getId()),
                static_cast<double>(f->getV1()->getId()),
                static_cast<double>(f->getV2()->getId()),
                static_cast<double>(f->getV3()->getId()),
                f->getMid()->getX(),
                f->getMid()->getY(),
                f->orientedSurface()};
    }
    return s;
  }
  void Cleanup(int action, Vertex* best) {
    using namespace ideal_test;
    bool owned = false;
    for (auto p : innerVertices)
      owned |= p == ideal;
    if (action == 3 && ideal && freed) {
      for (auto p : frontVertices)
        if (p == ideal) {
          volatile double expired = ReadVertexX(p);
          (void)expired;
        }
      return;
    }
    if (action == 2 && freed && best) {
      delete best;
      return;
    }
    if (!action || !ideal || freed || owned)
      return;
    ++cleanup_calls;
    cleanup = true;
    if (action != 3) {
      frontVertices.remove(ideal);
      vertices.remove(ideal);
    }
    delete ideal;
    cleanup = false;
    if (action == 3) {
      for (auto p : frontVertices)
        if (p == ideal) {
          volatile double expired = ReadVertexX(p);
          (void)expired;
        }
    }
  }
};
State Operation(int mode, int reverse, int prefix, int action, bool& threw, int& result) {
  Fixture f;
  f.Prepare(mode, reverse, prefix);
  Vertex* best = nullptr;
  ideal_test::armed = true;
  try {
    result = f.Select(best, mode);
    ideal_test::active = false;
  } catch (const std::bad_alloc&) {
    ideal_test::active = false;
    threw = true;
  }
  ideal_test::armed = false;
  f.Cleanup(action, best);
  return f.Snapshot(best);
}
} // namespace
int main(int argc, char** argv) {
  if (argc != 6)
    return 3;
  using namespace ideal_test;
  int mode = std::atoi(argv[1]), reverse = std::atoi(argv[2]), prefix = std::atoi(argv[3]),
      action = std::atoi(argv[5]);
  target = std::atoi(argv[4]);
  if (std::strcmp(argv[4], "uaf-control") == 0)
    return ExpiredAccess();
  bool threw = false;
  int result = -1;
  Operation(mode, reverse, prefix, 0, threw, result);
  destroyed.fill(0);
  threw = false;
  result = -1;
  enabled = true;
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemState before{}, after{}, difference{};
  auto previous = _CrtSetAllocHook(Hook);
  _CrtMemCheckpoint(&before);
#endif
  State s;
  if (std::strcmp(argv[4], "leak-control") == 0 || std::strcmp(argv[4], "denial-control") == 0) {
    target = std::strcmp(argv[4], "denial-control") == 0 ? 1 : 0;
    active = true;
    try {
      RetainedStorageControl();
      active = false;
    } catch (const std::bad_alloc&) {
      active = false;
      threw = true;
    }
  } else
    s = Operation(mode, reverse, prefix, action, threw, result);
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
      bytes += allocations[i].bytes;
    }
#endif
  std::printf(
      "{\"context\":[%d,%d,%d],\"target\":%d,\"action\":%d,\"attempts\":%d,\"denied\":%d,\"threw\":"
      "%d,\"result\":%d,\"entered\":%d,\"phase\":%d,\"events\":%llu,\"constructed\":%d,\"freed\":%"
      "d,\"ideal_xy\":[%.17g,%.17g],\"cleanup_calls\":%d,\"cleanup_allocations\":%d,\"retained_"
      "blocks\":%ld,\"retained_bytes\":%zu,\"vertex_size\":%zu",
      mode, reverse, prefix, target, action, attempts, denied, threw, result, entered, phase,
      events, ideal != nullptr, freed, ideal_x, ideal_y, cleanup_calls, cleanup_allocations, live,
      bytes, sizeof(Vertex));
  std::printf(
      ",\"owners\":%d,\"views\":%d,\"observers\":%d,\"mesh\":%d,\"edge_owners\":%d,\"borrowed\":%d,"
      "\"ideal_owner\":%d,\"ideal_view\":%d,\"ideal_front\":%d,\"best_kind\":%d,\"best_id\":%ld,"
      "\"best_xy\":[%.17g,%.17g],\"last_vertex_id\":%ld,\"area\":%.17g,\"adjacency\":[",
      s.owners, s.views, s.observers, s.mesh, s.edge_owners, s.borrowed, s.ideal_owner,
      s.ideal_view, s.ideal_front, s.best_kind, s.best_id, s.best_x, s.best_y, s.id, s.area);
  for (int i = 0; i < 8; ++i)
    std::printf("%s%d", i ? "," : "", s.adjacency[i]);
  std::printf("],\"face\":[");
  for (int i = 0; i < 7; ++i)
    std::printf("%s%.17g", i ? "," : "", s.face[i]);
  std::printf("],\"destroyed\":[");
  for (int i = 0; i < 8; ++i)
    std::printf("%s%d", i ? "," : "", destroyed[i]);
  std::printf("]}\n");
  return live ? 1 : 0;
}
