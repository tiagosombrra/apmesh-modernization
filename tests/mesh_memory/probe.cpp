#include <climits>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <utility>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/mesh/mesh_adaptive.h"
#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"

double TOLERANCE = 1e-8, EPSYLON = 1e-8;

namespace {
void Require(bool value, const char* message) {
  if (!value) {
    std::fprintf(stderr, "Mesh adoption contract failed: %s\n", message);
    std::exit(1);
  }
}

struct Destruction {
  int nodes = 0, triangles = 0;
  bool ordered = true;
  bool Complete() const { return nodes == 3 && triangles == 1 && ordered; }
};

class CountedNode final : public NodeAdaptive {
public:
  CountedNode(Destruction& count, double x, double y) : NodeAdaptive(x, y, 0), count_(count) {}
  ~CountedNode() override { ++count_.nodes; }

private:
  Destruction& count_;
};

class CountedTriangle final : public TriangleAdaptive {
public:
  CountedTriangle(Destruction& count, NodeAdaptive* a, NodeAdaptive* b, NodeAdaptive* c)
      : TriangleAdaptive(a, b, c), count_(count) {}
  ~CountedTriangle() override {
    count_.ordered = count_.ordered && count_.nodes == 0;
    ++count_.triangles;
  }

private:
  Destruction& count_;
};

std::unique_ptr<SubMesh> Graph(Destruction& count) {
  auto graph = std::make_unique<SubMesh>();
  graph->AddNoh(std::make_unique<CountedNode>(count, 0, 0));
  graph->AddNoh(std::make_unique<CountedNode>(count, 1, 0));
  graph->AddNoh(std::make_unique<CountedNode>(count, 0, 1));
  graph->AddElement(std::make_unique<CountedTriangle>(count, graph->GetNoh(0), graph->GetNoh(1),
                                                      graph->GetNoh(2)));
  return graph;
}

void Validate(SubMesh* graph) {
  Require(graph && graph->GetNumberNos() == 3 && graph->GetNumberElements() == 1,
          "complete physical graph survives adoption");
  auto* triangle = graph->GetElement(0);
  Require(triangle->GetArea() == 0.5, "independent analytic triangle area");
  for (unsigned int i = 0; i < 3; ++i)
    Require(graph->GetNoh(i)->GetNumberElements() == 1 &&
                graph->GetNoh(i)->GetElement(0) == triangle,
            "node adjacency keeps actual element identity");
}

// Stack-only subclass exposes capacity to force growth without assuming a vendor policy.
class FixtureMesh final : public MeshAdaptive {
public:
  int Capacity() const { return static_cast<int>(sub_meshes_.capacity()); }
};

struct Fixture {
  Destruction previous_count, argument_count;
  FixtureMesh mesh;
  std::unique_ptr<SubMesh> argument;
  SubMesh* previous = nullptr;
  SubMesh* identity = nullptr;
  int variant, size, position;
  explicit Fixture(int mode) : variant(mode) {
    if (mode != 0 && mode != 2) {
      mesh.ResizeSubMeshAdaptiveByPosition(3);
      mesh.ResizeSubMeshAdaptiveByPosition(mesh.Capacity());
      auto graph = Graph(previous_count);
      previous = graph.get();
      mesh.InsertSubMeshAdaptiveByPosition(graph.release(), 0);
    }
    size = static_cast<int>(mesh.GetNumberSubMeshesAdaptive());
    position = mode == 2 ? 4 : size + 3;
    if (mode == 4)
      position = 0;
    if (mode == 5)
      position = 1;
    if (mode == 6)
      position = -1;
    if (mode == 7)
      position = INT_MIN;
    if (mode == 10)
      position = 0;
    if (mode < 8)
      argument = Graph(argument_count);
    identity = argument.get();
  }
  bool HasPrevious() const { return previous != nullptr; }
  bool Appends() const { return variant == 0 || variant == 1 || variant == 8; }
  void Insert() {
    auto* raw = argument.release();
    if (Appends())
      mesh.InsertSubMeshAdaptive(raw);
    else
      mesh.InsertSubMeshAdaptiveByPosition(raw, position);
  }
  bool ArgumentDestroyed() const { return identity == nullptr || argument_count.Complete(); }
  void Unchanged() {
    Require(static_cast<int>(mesh.GetNumberSubMeshesAdaptive()) == size,
            "failed insertion preserves container size");
    if (HasPrevious()) {
      Require(mesh.GetSubMeshAdaptiveByPosition(0) == previous && previous_count.nodes == 0 &&
                  previous_count.triangles == 0,
              "previous owner and graph survive failure");
      Validate(previous);
    }
    for (int i = 1; i < size; ++i)
      Require(mesh.GetSubMeshAdaptiveByPosition(i) == nullptr, "existing empty slots preserved");
  }
  bool Normal(bool trace) {
    Insert();
    if (position < 0 && !Appends()) {
      Unchanged();
      // The consumed argument must be released even though no slot is published.
      if (!ArgumentDestroyed())
        return false;
    } else {
      int index = Appends() ? size : position;
      int expected_size = Appends() ? size + 1 : (position >= size ? position + 1 : size);
      Require(static_cast<int>(mesh.GetNumberSubMeshesAdaptive()) == expected_size,
              "ordered append, sparse growth or replacement size");
      Require(mesh.GetSubMeshAdaptiveByPosition(index) == identity,
              "adoption preserves object identity, including null slots");
      if (identity)
        Validate(identity);
      for (int i = 0; i < expected_size; ++i) {
        if (i == index)
          continue;
        Require(mesh.GetSubMeshAdaptiveByPosition(i) == (i == 0 ? previous : nullptr),
                "all other populated and empty slots preserved");
      }
      if (variant == 4 || variant == 10)
        Require(previous_count.Complete(), "replacement destroys old graph once");
      if (HasPrevious() && variant != 4 && variant != 10)
        Validate(previous);
      if (trace)
        std::printf("mesh_observed=variant:%d size:%d index:%d graph:%d area:%.1f\n", variant,
                    expected_size, index, identity != nullptr, identity ? 0.5 : 0.0);
    }
    // Actual move construction/assignment, replacement and removal must keep one owner.
    MeshAdaptive moved(std::move(mesh));
    Destruction retired;
    MeshAdaptive destination;
    destination.InsertSubMeshAdaptive(Graph(retired).release());
    destination = std::move(moved);
    Require(retired.Complete(), "move assignment destroys destination graph");
    if (position >= 0) {
      Require(destination.GetSubMeshAdaptiveByPosition(Appends() ? size : position) == identity,
              "moves preserve the adopted graph address");
      if (identity)
        Validate(identity);
    }
    while (destination.GetNumberSubMeshesAdaptive())
      destination.RemoveSubMeshAdaptive();
    destination.RemoveSubMeshAdaptive();
    destination.ResizeSubMeshAdaptiveByPosition(-1);
    return ArgumentDestroyed() && (!HasPrevious() || previous_count.Complete());
  }
};

#if defined(_MSC_VER) && defined(_DEBUG)
int attempts = 0, denied = 0, fail_after = -1;
int AllocationHook(int kind, void*, std::size_t, int, long, const unsigned char*, int) {
  if (kind == _HOOK_ALLOC || kind == _HOOK_REALLOC) {
    ++attempts;
    if (fail_after-- == 0) {
      ++denied;
      return 0;
    }
  }
  return 1;
}
class AllocationScope {
public:
  explicit AllocationScope(int ordinal) {
    attempts = denied = 0;
    fail_after = ordinal;
    previous_ = _CrtSetAllocHook(AllocationHook);
  }
  ~AllocationScope() { _CrtSetAllocHook(previous_); }
  AllocationScope(const AllocationScope&) = delete;
  AllocationScope& operator=(const AllocationScope&) = delete;

private:
  _CRT_ALLOC_HOOK previous_;
};

bool Failures(int variant) {
  int total;
  {
    Fixture fixture(variant);
    {
      AllocationScope hook(-1);
      fixture.Insert();
      total = attempts;
    }
  }
  Require(total > 0, "positive actual vector-growth allocation calibration");
  std::printf("mesh_measured=variant:%d allocations:%d\n", variant, total);
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    bool caught = false, released = false;
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    {
      Fixture fixture(variant);
      {
        AllocationScope hook(ordinal);
        try {
          fixture.Insert();
        } catch (const std::bad_alloc&) {
          caught = true;
        }
      }
      Require(caught && denied == 1 && attempts == ordinal + 1,
              "one denial propagates without an unwind allocation");
      fixture.Unchanged();
      released = fixture.ArgumentDestroyed();
    }
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    const auto blocks = delta.lCounts[_NORMAL_BLOCK];
    std::printf(
        "mesh_denied=variant:%d ordinal:%d attempts:%d released:%d retained:%zu bytes:%zu\n",
        variant, ordinal, attempts, released, blocks, delta.lSizes[_NORMAL_BLOCK]);
    if (!released || blocks != 0 || delta.lSizes[_NORMAL_BLOCK] != 0)
      return false;
  }
  std::printf("mesh_failure_sites=variant:%d denied:%d/%d\n", variant, total, total);
  return true;
}

bool NoAllocation(int variant) {
  Fixture fixture(variant);
  {
    AllocationScope hook(0);
    fixture.Insert();
  }
  Require(attempts == 0 && denied == 0,
          "replacement/presized/negative insertion does not allocate");
  bool released = fixture.position >= 0 || fixture.ArgumentDestroyed();
  if (fixture.position < 0)
    fixture.Unchanged();
  else {
    Require(fixture.mesh.GetSubMeshAdaptiveByPosition(fixture.position) == fixture.identity,
            "nonallocating adoption keeps identity");
    if (fixture.identity)
      Validate(fixture.identity);
    if (variant == 10)
      Require(fixture.previous_count.Complete(), "null replacement destroys old graph");
  }
  std::printf("mesh_noalloc=variant:%d attempts:%d released:%d\n", variant, attempts, released);
  return released;
}
#endif

bool Run(const char* mode) {
  if (std::strcmp(mode, "contracts") == 0) {
    for (int variant = 0; variant < 11; ++variant) {
      Fixture fixture(variant);
      if (!fixture.Normal(true))
        return false;
    }
  } else if (std::strncmp(mode, "normal-", 7) == 0) {
    Fixture fixture(std::atoi(mode + 7));
    return fixture.Normal(true);
  } else if (std::strcmp(mode, "use-after-free") == 0) {
    auto* node = new NodeAdaptive(1, 2, 3);
    delete node;
    std::printf("expired-x=%g\n", node->GetX());
  } else if (std::strcmp(mode, "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new NodeAdaptive(1, 2, 3)));
#if defined(_MSC_VER) && defined(_DEBUG)
  } else if (std::strncmp(mode, "failure-", 8) == 0) {
    return Failures(std::atoi(mode + 8));
  } else if (std::strncmp(mode, "noalloc-", 8) == 0) {
    return NoAllocation(std::atoi(mode + 8));
  } else if (std::strcmp(mode, "allocation-hook-control") == 0) {
    bool caught = false;
    {
      AllocationScope hook(0);
      try {
        auto data = std::make_unique<NodeAdaptive>();
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    Require(caught && denied == 1 && attempts == 1, "actual allocation hook is active");
    std::puts("allocation_hook_control=detected");
#endif
  } else
    Require(false, "unknown mode");
  return true;
}
} // namespace

int main(int argc, char** argv) {
  Require(argc == 2, "one mode required");
  std::setvbuf(stdout, nullptr, _IONBF, 0);
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_WARN, _CRTDBG_FILE_STDERR);
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  bool passed = Run(argv[1]);
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", delta.lCounts[_NORMAL_BLOCK],
              delta.lSizes[_NORMAL_BLOCK]);
  passed = passed && delta.lCounts[_NORMAL_BLOCK] == 0 && delta.lSizes[_NORMAL_BLOCK] == 0;
#endif
  std::puts(passed ? "PASS" : "FAIL");
  return passed ? 0 : 1;
}
