#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <memory>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "crab_mesh/aft/advancing_front.h"

#if defined(min) || defined(max)
#error Windows headers must not export min/max macros into the UV interfaces.
#endif

double TOLERANCE_AFT = 1e-8;
double TOLERANCE = 1e-8;
double DELTA = 1e-8;
double EPSYLON = 1e-8;
std::string USE_TEMPLATE = "y";
int AFT_LOCAL_POSTPROCESS_PASSES = 0;
double AFT_LOCAL_POSTPROCESS_QUALITY_THRESHOLD = 0.0;
double AFT_LOCAL_POSTPROCESS_BLEND = 0.5;
double QUADTREE_FACE_QUALITY_THRESHOLD = 0.0;
double QUADTREE_LOW_QUALITY_H_FACTOR = 1.0;
double TEMPLATE_POOR_SCORE_THRESHOLD = 0.0;

namespace {
void require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Contract failed: %s\n", message);
    std::exit(1);
  }
}

void square(Boundary& boundary) {
  for (int side = 0; side < 4; ++side) {
    for (int step = 0; step < 4; ++step) {
      const double t = step / 4.0;
      const double x = side == 0 ? t : (side == 1 ? 1.0 : (side == 2 ? 1.0 - t : 0.0));
      const double y = side == 1 ? t : (side == 2 ? 1.0 : (side == 3 ? 1.0 - t : 0.0));
      boundary.addVertex(x, y, nullptr);
    }
  }
  require(boundary.close(nullptr), "square boundary closes");
  // A null-curve fixture supplies the normalized size normally set by curve integration.
  for (auto* edge : boundary.getEdges())
    edge->setLen(edge->length());
}

struct InjectedFailure {};

class FailedFront : public AdvancingFront {
public:
  explicit FailedFront(int failure) : AdvancingFront(0.85, 1e-8, 0), failure_(failure) {}
  MethodStatus makeGeometryBasedMesh() override {
    require(!getQuadtree()->getMesh().empty(), "failure injected after actual template generation");
    std::printf("templates_before_failure=%zu\n", getQuadtree()->getMesh().size());
    if (failure_ == 1)
      throw InjectedFailure{};
    return failure_ == 2 ? ADVF_GEOMETRY_EDGE_REJECTED_TWICE : ADVF_EMPTY;
  }
  MethodStatus makeTopologyBasedMesh() override {
    require(failure_ == 2, "topology fallback only in selected control");
    return ADVF_TOPOLOGY_EDGE_REJECTED_TWICE;
  }

private:
  int failure_;
};

void failed(int failure) {
  bool caught = false;
  try {
    FailedFront front(failure);
    square(*front.getBoundary());
    require(!front.execute({}), "injected failure returns false");
  } catch (const InjectedFailure&) {
    caught = true;
  }
  require(caught == (failure == 1), "exception unwind reaches caller");
}

void normal(bool check_transfer) {
  AdvancingFront front(0.85, 1e-8, 0);
  square(*front.getBoundary());
  require(front.execute({}), "real UV generation succeeds");
  require(!front.getMesh().empty() && !front.getInnerVertices().empty(),
          "nonempty generated output");
  require(front.GetRunStats().quadtree_template_count > 0, "positive template coverage");
  std::printf("generated_faces=%zu templates=%llu\n", front.getMesh().size(),
              front.GetRunStats().quadtree_template_count);
  const auto& counts = front.getQuadtree()->GetTemplateStats().template_count;
  std::printf("template_type_counts=%llu,%llu,%llu,%llu,%llu,%llu\n", counts[0], counts[1],
              counts[2], counts[3], counts[4], counts[5]);
  if (check_transfer) {
    require(front.getQuadtree()->getMesh().empty() && front.getQuadtree()->getEdges().empty() &&
                front.getQuadtree()->getVertices().empty(),
            "template owners transfer to front once");
  }
}

class CountedVertex : public Vertex {
public:
  CountedVertex(double x, double y, int& destroyed) : Vertex(x, y), destroyed_(destroyed) {}
  ~CountedVertex() override { ++destroyed_; }

private:
  int& destroyed_;
};

std::unique_ptr<AdvancingFront> partial(int& destroyed) {
  auto front = std::make_unique<AdvancingFront>();
  front->getBoundary()->addVertex(0, 0, nullptr);
  front->getBoundary()->addVertex(1, 0, nullptr);
  auto* a = new CountedVertex(0.2, 0.2, destroyed);
  auto* b = new CountedVertex(0.8, 0.2, destroyed);
  auto* c = new CountedVertex(0.2, 0.8, destroyed);
  front->addVertices({a, b, c});
  auto* edge = new Edge(a, b);
  a->addAdjacentEdge(edge);
  b->addAdjacentEdge(edge);
  front->addEdges({edge});
  front->addMesh({new Face(a, b, c)});
  return front;
}

void pending_tree() {
  auto boundary = std::make_unique<Boundary>();
  square(*boundary);
  Quadtree tree(boundary.release());
  require(tree.execute({}), "standalone quadtree builds");
  require(tree.makeTemplateBasedMesh() == QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
          "standalone templates build");
  require(!tree.getMesh().empty(), "standalone output awaiting transfer");
}

class TransferFront : public AdvancingFront {
public:
  using AdvancingFront::fillMesh;
};

void prepare_transfer(TransferFront& front) {
  square(*front.getBoundary());
  require(front.getQuadtree()->execute({}), "transfer source quadtree builds");
  require(front.getQuadtree()->makeTemplateBasedMesh() == QUAD_MAKE_TEMPLATE_BASED_MESH_DONE,
          "transfer source templates build");
  require(!front.getQuadtree()->getMesh().empty(), "positive transfer source coverage");
}

void transfer_order() {
  TransferFront front;
  prepare_transfer(front);
  auto expected_vertices = front.getQuadtree()->getVertices();
  auto expected_edges = front.getQuadtree()->getEdges();
  auto expected_faces = front.getQuadtree()->getMesh();
  auto* a = new Vertex(0.2, 0.2);
  auto* b = new Vertex(0.8, 0.2);
  auto* c = new Vertex(0.2, 0.8);
  auto* edge = new Edge(a, b);
  auto* face = new Face(a, b, c);
  front.addVertices({a, b, c});
  front.addEdges({edge});
  front.addMesh({face});
  expected_vertices.insert(expected_vertices.begin(), {a, b, c});
  expected_edges.push_front(edge);
  expected_faces.push_front(face);
  front.fillMesh();
  require(front.getInnerVertices() == expected_vertices &&
              front.getInnerEdges() == expected_edges && front.getMesh() == expected_faces,
          "owner handoff preserves every address and append order");
  require(front.getQuadtree()->getVertices().empty() && front.getQuadtree()->getEdges().empty() &&
              front.getQuadtree()->getMesh().empty(),
          "source owners consumed");
  front.fillMesh();
  require(front.getInnerVertices() == expected_vertices &&
              front.getInnerEdges() == expected_edges && front.getMesh() == expected_faces,
          "repeated empty handoff does not duplicate owners");
}

void midpoint_alias() {
  int destroyed = 0;
  {
    AdvancingFront front;
    auto* a = new CountedVertex(0, 0, destroyed);
    auto* b = new CountedVertex(1, 0, destroyed);
    auto* c = new CountedVertex(0, 1, destroyed);
    front.addVertices({a, b, c});
    front.addMesh({new Face(a, b, c, a, 1)});
  }
  require(destroyed == 3, "borrowed midpoint alias is not destroyed by face detachment");
}

void face_alias_cache() {
  int destroyed = 0;
  auto a = std::make_unique<CountedVertex>(0, 0, destroyed);
  auto b = std::make_unique<CountedVertex>(3, 0, destroyed);
  auto c = std::make_unique<CountedVertex>(0, 3, destroyed);
  {
    Face face(a.get(), b.get(), c.get(), a.get(), 17);
    face.setVertices(a.get(), b.get(), c.get());
    require(destroyed == 0 && face.getMid() != a.get(),
            "cache replacement preserves the borrowed endpoint alias");
    require(face.getMid()->getX() == 1 && face.getMid()->getY() == 1,
            "replacement midpoint retains the centroid formula");
    face.DetachVertices();
  }
  require(destroyed == 0, "endpoints remain caller-owned after explicit detachment");
}

void primitive_contracts() {
  Vertex a(0, 0), b(3, 4), c(0, 3), d(6, 0);
  Edge edge(&a, &b, 19);
  edge.setLen(0.25);
  require(edge.length() == 5 && edge.getMid()->getX() == 1.5 && edge.getMid()->getY() == 2,
          "edge construction geometry");
  edge.setVertices(&a, &d);
  require(edge.getV1() == &a && edge.getV2() == &d && edge.length() == 6 &&
              edge.getMid()->getX() == 3 && edge.getMid()->getY() == 0 && edge.getLen() == 0.25 &&
              edge.getId() == 19,
          "edge replacement geometry, scalar state and identity");
  edge.setVertices(nullptr, nullptr);
  require(edge.length() == 0 && edge.getMid()->getX() == 0 && edge.getMid()->getY() == 0,
          "null endpoint replacement retains default cache geometry");
  Face face(&a, &b, &c, 23);
  face.h = 0.5;
  face.setVertices(&a, &d, &c);
  require(face.getMid()->getX() == 2 && face.getMid()->getY() == 1 && face.surface() == 9 &&
              face.h == 0.5 && face.getId() == 23,
          "face replacement geometry, scalar state and identity");
  face.DetachVertices();
  face_alias_cache();
}

#if defined(_MSC_VER) && defined(_DEBUG)
int denied_allocations = 0;
int allocation_attempts = 0;
int fail_after = -1;
bool forbid_allocations = true;
int allocation_hook(int kind, void*, std::size_t, int, long, const unsigned char*, int) {
  if (kind == _HOOK_ALLOC || kind == _HOOK_REALLOC) {
    ++allocation_attempts;
    if (forbid_allocations || fail_after-- == 0) {
      ++denied_allocations;
      return FALSE;
    }
  }
  return TRUE;
}

void allocation_free_teardown() {
  int destroyed = 0;
  auto front = partial(destroyed);
  std::set_terminate([] {
    std::fprintf(stderr, "teardown allocation caused termination\n");
    std::_Exit(73);
  });
  const auto previous = _CrtSetAllocHook(allocation_hook);
  front.reset();
  _CrtSetAllocHook(previous);
  require(destroyed == 3 && denied_allocations == 0, "teardown performs no allocation");
  std::puts("teardown_allocation_attempts=0");
}

void allocation_hook_control() {
  bool caught = false;
  const auto previous = _CrtSetAllocHook(allocation_hook);
  try {
    auto unexpected = std::make_unique<Vertex>(1, 2);
  } catch (const std::bad_alloc&) {
    caught = true;
  }
  _CrtSetAllocHook(previous);
  require(caught && denied_allocations > 0, "deliberate allocation denial is observed");
  std::puts("allocation_hook_control=detected");
}

void transfer_allocation_failure() {
  forbid_allocations = false;
  allocation_attempts = 0;
  {
    TransferFront front;
    prepare_transfer(front);
    const auto previous = _CrtSetAllocHook(allocation_hook);
    front.fillMesh();
    _CrtSetAllocHook(previous);
  }
  const int total = allocation_attempts;
  require(total > 2, "positive measured allocation coverage in observer preparation");
  for (const int index : {0, total / 2, total - 1}) {
    TransferFront front;
    prepare_transfer(front);
    const auto original_vertices = front.getQuadtree()->getVertices();
    const auto original_edges = front.getQuadtree()->getEdges();
    const auto original_faces = front.getQuadtree()->getMesh();
    allocation_attempts = denied_allocations = 0;
    fail_after = index;
    bool caught = false;
    const auto previous = _CrtSetAllocHook(allocation_hook);
    try {
      front.fillMesh();
    } catch (const std::bad_alloc&) {
      caught = true;
    }
    _CrtSetAllocHook(previous);
    require(caught && denied_allocations == 1,
            "injected transfer allocation failure reaches caller");
    require(front.getInnerVertices().empty() && front.getInnerEdges().empty() &&
                front.getMesh().empty(),
            "failed observer preparation transfers no owners");
    require(front.getQuadtree()->getVertices() == original_vertices &&
                front.getQuadtree()->getEdges() == original_edges &&
                front.getQuadtree()->getMesh() == original_faces,
            "source owners remain complete after allocation failure");
  }
  std::printf("transfer_allocation_failures=3 measured_allocations=%d\n", total);
}

class AllocationScope {
public:
  explicit AllocationScope(int ordinal) {
    allocation_attempts = denied_allocations = 0;
    forbid_allocations = false;
    fail_after = ordinal;
    previous_ = _CrtSetAllocHook(allocation_hook);
  }
  ~AllocationScope() { _CrtSetAllocHook(previous_); }
  AllocationScope(const AllocationScope&) = delete;
  AllocationScope& operator=(const AllocationScope&) = delete;

private:
  _CRT_ALLOC_HOOK previous_;
};

template <class Action> int measure_allocations(Action action) {
  AllocationScope hook(-1);
  action();
  return allocation_attempts;
}

template <class Action> bool inject_allocation_failure(int ordinal, Action action) {
  bool caught = false;
  {
    AllocationScope hook(ordinal);
    try {
      action();
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  return caught && denied_allocations == 1;
}

template <class Action> void construction_failures(const char* name, Action action) {
  const int total = measure_allocations(action);
  require(total > 0, "construction control has positive measured allocation coverage");
  for (int ordinal = 0; ordinal < total; ++ordinal)
    require(inject_allocation_failure(ordinal, action),
            "every construction failure reaches caller");
  std::printf("allocation_failure_sites=%s:%d/%d\n", name, total, total);
}

void edge_construction_failures() {
  int destroyed = 0;
  auto a = std::make_unique<CountedVertex>(0, 0, destroyed);
  auto b = std::make_unique<CountedVertex>(3, 4, destroyed);
  construction_failures("edge", [&] {
    Edge edge(a.get(), b.get());
    edge.DetachVertices();
  });
  require(destroyed == 0, "failed edge construction never adopts caller endpoints");
}

void face_construction_failures() {
  int destroyed = 0;
  auto a = std::make_unique<CountedVertex>(0, 0, destroyed);
  auto b = std::make_unique<CountedVertex>(3, 0, destroyed);
  auto c = std::make_unique<CountedVertex>(0, 3, destroyed);
  construction_failures("face", [&] {
    Face face(a.get(), b.get(), c.get(), 1);
    face.DetachVertices();
  });
  construction_failures("face-explicit", [&] {
    Face face(a.get(), b.get(), c.get(), a.get(), 1);
    face.DetachVertices();
  });
  require(destroyed == 0, "failed face construction never adopts caller endpoints/midpoint");
}

void cache_replacement_failures(bool is_edge) {
  Vertex a(0, 0), b(3, 4), c(0, 3), d(6, 0);
  int total = 0;
  if (is_edge) {
    Edge edge(&a, &b);
    total = measure_allocations([&] { edge.setVertices(&c, &d); });
    edge.DetachVertices();
  } else {
    Face face(&a, &b, &c);
    total = measure_allocations([&] { face.setVertices(&b, &c, &d); });
    face.DetachVertices();
  }
  require(total > 0, "cache control has positive measured allocation coverage");
  bool unchanged = true;
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    if (is_edge) {
      Edge edge(&a, &b, 19);
      edge.setLen(0.25);
      auto* midpoint = edge.getMid();
      const bool caught = inject_allocation_failure(ordinal, [&] { edge.setVertices(&c, &d); });
      unchanged = unchanged && caught && edge.getV1() == &a && edge.getV2() == &b &&
                  edge.getMid() == midpoint && edge.length() == 5 && edge.getLen() == 0.25 &&
                  midpoint->getX() == 1.5 && midpoint->getY() == 2 && edge.getId() == 19;
      edge.DetachVertices();
    } else {
      Face face(&a, &b, &c, 23);
      face.h = 0.5;
      auto* midpoint = face.getMid();
      const bool caught = inject_allocation_failure(ordinal, [&] { face.setVertices(&b, &c, &d); });
      unchanged = unchanged && caught && face.getV1() == &a && face.getV2() == &b &&
                  face.getV3() == &c && face.getMid() == midpoint && midpoint->getX() == 1 &&
                  midpoint->getY() == 7.0 / 3.0 && face.h == 0.5 && face.getId() == 23;
      face.DetachVertices();
    }
  }
  std::printf("allocation_failure_sites=%s-cache:%d/%d unchanged=%d\n", is_edge ? "edge" : "face",
              total, total, unchanged ? 1 : 0);
  require(unchanged,
          "failed replacement preserves endpoints, cache identity/geometry and scalar state");
}
#endif

void scenario(const char* mode) {
  if (std::strcmp(mode, "normal") == 0)
    normal(false);
  else if (std::strcmp(mode, "transfer-contract") == 0)
    normal(true);
  else if (std::strcmp(mode, "failure") == 0)
    failed(0);
  else if (std::strcmp(mode, "exception") == 0)
    failed(1);
  else if (std::strcmp(mode, "topology-failure") == 0)
    failed(2);
  else if (std::strcmp(mode, "pending-tree") == 0)
    pending_tree();
  else if (std::strcmp(mode, "transfer-order") == 0)
    transfer_order();
  else if (std::strcmp(mode, "midpoint-alias") == 0)
    midpoint_alias();
  else if (std::strcmp(mode, "face-alias-cache") == 0)
    face_alias_cache();
  else if (std::strcmp(mode, "primitive-contracts") == 0)
    primitive_contracts();
  else if (std::strcmp(mode, "partial") == 0) {
    int destroyed = 0;
    partial(destroyed).reset();
    require(destroyed == 3, "shared endpoints destroyed exactly once by front");
  } else if (std::strcmp(mode, "teardown-allocation") == 0) {
#if defined(_MSC_VER) && defined(_DEBUG)
    allocation_free_teardown();
#else
    require(false, "Debug CRT allocation hook required");
#endif
  } else if (std::strcmp(mode, "allocation-hook-control") == 0 ||
             std::strcmp(mode, "transfer-allocation-failure") == 0) {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::strcmp(mode, "allocation-hook-control") == 0)
      allocation_hook_control();
    else
      transfer_allocation_failure();
#else
    require(false, "Debug CRT allocation hook required");
#endif
  } else if (std::strcmp(mode, "edge-construction-failure") == 0 ||
             std::strcmp(mode, "face-construction-failure") == 0 ||
             std::strcmp(mode, "front-construction-failure") == 0 ||
             std::strcmp(mode, "edge-cache-failure") == 0 ||
             std::strcmp(mode, "face-cache-failure") == 0) {
#if defined(_MSC_VER) && defined(_DEBUG)
    if (std::strcmp(mode, "edge-construction-failure") == 0)
      edge_construction_failures();
    else if (std::strcmp(mode, "face-construction-failure") == 0)
      face_construction_failures();
    else if (std::strcmp(mode, "front-construction-failure") == 0)
      construction_failures("front", [] { AdvancingFront front; });
    else
      cache_replacement_failures(std::strcmp(mode, "edge-cache-failure") == 0);
#else
    require(false, "Debug CRT allocation hook required");
#endif
  } else if (std::strcmp(mode, "use-after-free") == 0) {
    auto* vertex = new Vertex(1, 2);
    delete vertex;
    std::printf("expired-x=%g\n", vertex->getX());
  } else if (std::strcmp(mode, "shared-delete") == 0) {
    auto* shared = new Vertex(0, 0);
    auto* first = new Edge(shared, new Vertex(1, 0));
    auto* second = new Edge(shared, new Vertex(0, 1));
    delete first;
    delete second;
  } else if (std::strcmp(mode, "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new Vertex(1, 2)));
  } else
    require(false, "unknown scenario");
}
} // namespace

int main(int argc, char** argv) {
  require(argc == 2, "one scenario required");
  std::setvbuf(stdout, nullptr, _IONBF, 0);
#if defined(_WIN32)
  SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
#endif
  std::puts("UV lifetime diagnostic");
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_WARN, _CRTDBG_FILE_STDERR);
  _CrtSetReportMode(_CRT_ERROR, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_ERROR, _CRTDBG_FILE_STDERR);
  _CrtSetReportMode(_CRT_ASSERT, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_ASSERT, _CRTDBG_FILE_STDERR);
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  if (std::strcmp(argv[1], "contracts") == 0) {
    for (int repetition = 0; repetition < 10; ++repetition) {
      for (const auto* mode :
           {"normal", "partial", "failure", "exception", "topology-failure", "pending-tree"})
        scenario(mode);
    }
    scenario("transfer-contract");
    scenario("transfer-order");
    scenario("midpoint-alias");
  } else
    scenario(argv[1]);
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  if (delta.lCounts[_NORMAL_BLOCK] != 0) {
    _CrtMemDumpAllObjectsSince(&before);
    return 1;
  }
#endif
  std::puts("PASS");
}
