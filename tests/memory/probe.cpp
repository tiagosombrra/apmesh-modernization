#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <utility>
#include <vector>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"

double EPSYLON = 1e-8;
double TOLERANCE = 1e-8;

namespace {
void require(bool condition, const char* message) {
  if (!condition) {
    std::fprintf(stderr, "Contract failed: %s\n", message);
    std::exit(1);
  }
}

class CountedNode : public NodeAdaptive {
public:
  explicit CountedNode(int& destroyed) : destroyed_(destroyed) {}
  ~CountedNode() override { ++destroyed_; }

private:
  int& destroyed_;
};

struct NodeState {
  unsigned long id;
  std::array<double, 7> values;
  std::vector<ElementAdaptive*> entries;
  std::vector<const void*> slots;
};

NodeState Observe(const NodeAdaptive& node) {
  NodeState state{node.GetId(),
                  {node.GetX(), node.GetY(), node.GetZ(), node.GetGa(), node.GetGd(), node.GetHa(),
                   node.GetHd()},
                  {},
                  {}};
  for (const auto& entry : node.GetElements()) {
    state.entries.push_back(entry);
    state.slots.push_back(std::addressof(entry));
  }
  return state;
}

bool SameValues(const NodeState& first, const NodeState& second) {
  return first.id == second.id &&
         std::memcmp(first.values.data(), second.values.data(), sizeof(first.values)) == 0;
}

bool SameState(const NodeState& first, const NodeState& second) {
  return SameValues(first, second) && first.entries == second.entries &&
         first.slots == second.slots;
}

struct CopyFixture {
  NodeAdaptive source{1, 2, 3, 42}, b{2, 2, 3}, c{1, 3, 3}, d{0, 2, 3};
  TriangleAdaptive first{&source, &b, &c}, second{&source, &c, &d};
  NodeAdaptive target{9, 8, 7, 77};
  explicit CopyFixture(bool populated, bool empty_source = false) {
    source.SetGa(-0.0);
    source.SetGd(5);
    source.SetHa(6);
    source.SetHd(7);
    target.SetGa(14);
    target.SetGd(15);
    target.SetHa(16);
    target.SetHd(17);
    source.InsertElement(nullptr);
    source.InsertElement(&first);
    if (empty_source)
      source.ClearElements();
    if (populated) {
      target.InsertElement(nullptr);
      target.InsertElement(&second);
    }
  }
  void Assign(bool observers_only) {
    if (observers_only)
      target.setElements(source.GetElements());
    else
      target = source;
  }
};

void copy_contracts() {
  for (bool populated : {false, true}) {
    for (bool observers_only : {false, true}) {
      CopyFixture fixture(populated);
      const auto source = Observe(fixture.source), target = Observe(fixture.target);
      fixture.Assign(observers_only);
      const auto copied = Observe(fixture.target);
      require(SameValues(copied, observers_only ? target : source) &&
                  copied.entries == source.entries,
              "copy preserves exact scalar bits, pointer order, duplicates and null observers");
      require(SameState(Observe(fixture.source), source), "copy preserves source and list nodes");
      NodeAdaptive independent(fixture.source);
      const auto ordinary = Observe(independent);
      require(SameValues(ordinary, source) && ordinary.entries == source.entries &&
                  ordinary.slots.front() != source.slots.front(),
              "ordinary construction keeps an independent container of live borrowed elements");
      const auto before_self = Observe(fixture.target);
      auto* alias = &fixture.target;
      fixture.target = *alias;
      fixture.target.setElements(fixture.target.GetElements());
      require(SameState(Observe(fixture.target), before_self),
              "self copies retain every list node");
      require(fixture.first.GetArea() == 0.5 && fixture.second.GetArea() == 0.5,
              "copy does not change actual source triangle caches");
    }
  }
  std::puts("node_copy_contracts=4 scalar_bits=1 pointer_order=1 source_nodes=1 self=1");
}

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

private:
  _CRT_ALLOC_HOOK previous_;
};

bool copy_failures(int variant) {
  const bool populated = (variant & 2) != 0, observers_only = variant % 2 != 0;
  int total = 0;
  {
    CopyFixture fixture(populated, variant >= 4);
    AllocationScope hook(-1);
    fixture.Assign(observers_only);
    total = attempts;
  }
  require(total > 0, "positive measured node copy allocation coverage");
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    CopyFixture fixture(populated, variant >= 4);
    const auto source = Observe(fixture.source), target = Observe(fixture.target);
    bool caught = false;
    {
      AllocationScope hook(ordinal);
      try {
        fixture.Assign(observers_only);
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    require(caught && denied == 1, "each measured denial propagates bad_alloc exactly once");
    const bool unchanged = SameState(Observe(fixture.target), target);
    std::printf("node_copy_denial=variant:%d ordinal:%d unchanged:%d\n", variant, ordinal,
                unchanged);
    if (!unchanged)
      return false;
    require(SameState(Observe(fixture.source), source), "denied copy leaves source unchanged");
    fixture.Assign(observers_only);
    const auto copied = Observe(fixture.target);
    require(SameValues(copied, observers_only ? target : source) &&
                copied.entries == source.entries,
            "helper-local retry copies the complete value and observation sequence");
  }
  std::printf("node_copy_failure_sites=variant:%d denied:%d/%d unchanged=1 retry=1\n", variant,
              total, total);
  return true;
}

bool clone_failures() {
  int total = 0;
  {
    CopyFixture fixture(true);
    SubMesh mesh;
    AllocationScope hook(-1);
    mesh.SetNoh(&fixture.source);
    total = attempts;
  }
  require(total > 0, "physical clone allocation coverage is measured");
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    CopyFixture fixture(true);
    const auto source = Observe(fixture.source);
    SubMesh mesh;
    bool caught = false;
    {
      AllocationScope hook(ordinal);
      try {
        mesh.SetNoh(&fixture.source);
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    require(caught && denied == 1 && mesh.GetNumberNos() == 0,
            "failed physical clone publishes no owner and propagates denial");
    require(SameState(Observe(fixture.source), source), "physical clone preserves source");
    mesh.SetNoh(&fixture.source);
    const auto copied = Observe(*mesh.GetNoh(0));
    require(SameValues(copied, source) && copied.entries.empty(),
            "physical clone has identical scalar bits and no foreign observations");
  }
  std::printf("node_clone_failure_sites=denied:%d/%d source_observers:4 scalar_bits:1\n", total,
              total);
  return true;
}

void self_noalloc() {
  CopyFixture fixture(true);
  const auto before = Observe(fixture.source);
  {
    AllocationScope hook(0);
    auto* alias = &fixture.source;
    fixture.source = *alias;
    fixture.source.setElements(fixture.source.GetElements());
  }
  require(attempts == 0 && denied == 0 && SameState(Observe(fixture.source), before),
          "self assignment and aliased observer replacement allocate nothing");
  std::puts("node_copy_self=allocations:0 list_nodes:preserved");
}

bool construction_failures(bool empty_source) {
  CopyFixture fixture(false, empty_source);
  const auto source = Observe(fixture.source);
  int total = 0;
  {
    AllocationScope hook(-1);
    auto copy = std::make_unique<NodeAdaptive>(fixture.source);
    total = attempts;
  }
  require(total > 0, "ordinary node construction has measured allocations");
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    bool caught = false;
    {
      AllocationScope hook(ordinal);
      try {
        auto copy = std::make_unique<NodeAdaptive>(fixture.source);
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    require(caught && denied == 1 && SameState(Observe(fixture.source), source),
            "ordinary copy construction denial preserves its live source");
  }
  std::printf("node_construct_failure_sites=empty:%d denied:%d/%d source_nodes:preserved\n",
              empty_source, total, total);
  return true;
}

void allocation_hook_control() {
  bool caught = false;
  {
    AllocationScope hook(0);
    try {
      auto node = std::make_unique<NodeAdaptive>();
    } catch (const std::bad_alloc&) {
      caught = true;
    }
  }
  require(caught && attempts == 1 && denied == 1, "actual node allocation hook control");
  std::puts("node_allocation_hook=detected");
}
#endif

void contracts() {
  for (int iteration = 0; iteration < 200; ++iteration) {
    SubMesh first;
    SubMesh second;
    {
      NodeAdaptive source(1.0, 2.0, 3.0, 42);
      source.SetGa(4.0);
      source.SetGd(5.0);
      source.SetHa(6.0);
      source.SetHd(7.0);
      NodeAdaptive b(2.0, 2.0, 3.0);
      NodeAdaptive c(1.0, 3.0, 3.0);
      TriangleAdaptive original(&source, &b, &c);
      first.SetNoh(&source);
      second.SetNoh(&source);
      first.SetNoh(nullptr);
      require(first.GetNumberNos() == 1, "null copy is ignored");
      auto* copy = first.GetNoh(0);
      require(copy != &source && copy != second.GetNoh(0), "independent identity");
      require(copy->GetId() == 42 && copy->GetX() == 1.0 && copy->GetY() == 2.0 &&
                  copy->GetZ() == 3.0,
              "ID and physical position preserved");
      require(copy->GetGa() == 4.0 && copy->GetGd() == 5.0 && copy->GetHa() == 6.0 &&
                  copy->GetHd() == 7.0,
              "curvature state preserved");
      require(source.GetNumberElements() == 1 && source.GetElement(0) == &original,
              "source adjacency untouched");
      require(copy->GetNumberElements() == 0 && second.GetNoh(0)->GetNumberElements() == 0,
              "copied node starts without foreign element observers");
      source.SetX(99.0);
      require(copy->GetX() == 1.0, "independent scalar storage");
    }
    require(first.GetNoh(0)->GetNumberElements() == 0, "source destruction is safe");
    first.AddNoh(std::make_unique<NodeAdaptive>(2.0, 2.0, 3.0));
    first.AddNoh(std::make_unique<NodeAdaptive>(1.0, 3.0, 3.0));
    auto local =
        std::make_unique<TriangleAdaptive>(first.GetNoh(0), first.GetNoh(1), first.GetNoh(2));
    auto* element = local.get();
    first.AddElement(std::move(local));
    require(first.GetNoh(0)->GetNumberElements() == 1 && first.GetNoh(0)->GetElement(0) == element,
            "local triangle rebuilds adjacency");
    require(element->GetArea() == 0.5, "local geometry preserved");
    SubMesh moved(std::move(first));
    require(moved.GetElement(0) == element && moved.GetNoh(0)->GetElement(0) == element,
            "move preserves owned addresses");
    second = std::move(moved);
    require(second.GetNumberNos() == 3 && second.GetElement(0) == element,
            "replacement transfers owned nodes and elements");
  }
  int destroyed = 0;
  {
    SubMesh owner;
    auto node = std::make_unique<CountedNode>(destroyed);
    auto* identity = node.get();
    owner.AddNoh(std::move(node));
    require(!node && owner.GetNoh(0) == identity, "unique adoption preserves identity");
  }
  require(destroyed == 1, "adopted node destroyed exactly once");
}

// Deliberately broken controls must run in separate processes.
void broken(const char* mode) {
  if (std::strcmp(mode, "expired-copy") == 0) {
    SubMesh destination;
    NodeAdaptive a(0, 0, 0), b(1, 0, 0), c(0, 1, 0);
    auto source = std::make_unique<TriangleAdaptive>(&a, &b, &c);
    destination.SetNoh(&a);
    source.reset();
    auto* copy = destination.GetNoh(0);
    if (copy->GetNumberElements() != 0) {
      std::printf("expired-area=%g\n", copy->GetElement(0)->GetArea());
    }
  } else if (std::strcmp(mode, "leak") == 0) {
    auto* leaked = new NodeAdaptive(1, 2, 3);
    std::printf("deliberate-leak=%p\n", static_cast<void*>(leaked));
  } else if (std::strcmp(mode, "use-after-free") == 0) {
    auto* node = new NodeAdaptive(1, 2, 3);
    delete node;
    std::printf("expired-x=%g\n", node->GetX());
  } else if (std::strcmp(mode, "double-free") == 0) {
    auto* data = static_cast<int*>(std::malloc(64));
    std::free(data);
    std::free(data);
  } else {
    require(false, "unknown mode");
  }
}
} // namespace

int main(int argc, char** argv) {
  require(argc == 2, "one mode required");
  std::puts("Node lifetime diagnostic");
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtSetReportMode(_CRT_WARN, _CRTDBG_MODE_FILE);
  _CrtSetReportFile(_CRT_WARN, _CRTDBG_FILE_STDERR);
  _CrtMemState before{}, after{}, delta{};
  _CrtMemCheckpoint(&before);
#endif
  bool passed = true;
  if (std::strcmp(argv[1], "contracts") == 0) {
    contracts();
    copy_contracts();
  } else if (std::strcmp(argv[1], "copy-contracts") == 0) {
    copy_contracts();
#if defined(_MSC_VER) && defined(_DEBUG)
  } else if (std::strncmp(argv[1], "copy-failure-", 13) == 0 && std::strlen(argv[1]) == 14 &&
             argv[1][13] >= '0' && argv[1][13] <= '7') {
    passed = copy_failures(argv[1][13] - '0');
  } else if (std::strcmp(argv[1], "clone-failure") == 0) {
    passed = clone_failures();
  } else if (std::strcmp(argv[1], "copy-self-noalloc") == 0) {
    self_noalloc();
  } else if (std::strcmp(argv[1], "construct-failure-0") == 0 ||
             std::strcmp(argv[1], "construct-failure-1") == 0) {
    passed = construction_failures(argv[1][18] == '1');
  } else if (std::strcmp(argv[1], "allocation-hook-control") == 0) {
    allocation_hook_control();
#endif
  } else {
    broken(argv[1]);
  }
#if defined(_MSC_VER) && defined(_DEBUG)
  _CrtMemCheckpoint(&after);
  _CrtMemDifference(&delta, &before, &after);
  const auto blocks = delta.lCounts[_NORMAL_BLOCK];
  std::printf("CRT retained_blocks=%zu retained_bytes=%zu\n", blocks, delta.lSizes[_NORMAL_BLOCK]);
  if (blocks != 0) {
    _CrtMemDumpAllObjectsSince(&before);
    return 1;
  }
#endif
  std::puts(passed ? "PASS" : "FAIL");
  return passed ? 0 : 1;
}
