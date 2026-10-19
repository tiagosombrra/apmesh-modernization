#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <new>
#include <stdexcept>
#include <utility>

#if defined(_MSC_VER) && defined(_DEBUG)
#include <crtdbg.h>
#endif

#include "data/mesh/sub_mesh.h"
#include "data/node_adaptive.h"
#include "data/triangle_adaptive.h"

double TOLERANCE = 1e-8, EPSYLON = 1e-8;

namespace {
void Require(bool value, const char* message) {
  if (!value) {
    std::fprintf(stderr, "Triangle lifetime contract failed: %s\n", message);
    std::exit(1);
  }
}

class VisibleTriangle : public TriangleAdaptive {
public:
  using TriangleAdaptive::TriangleAdaptive;
  NodeAdaptive* Vertex(unsigned int index) const {
    return index == 0 ? n1_ : (index == 1 ? n2_ : n3_);
  }
};

class ThrowingTriangle final : public TriangleAdaptive {
public:
  ThrowingTriangle(NodeAdaptive* a, NodeAdaptive* b, NodeAdaptive* c) : TriangleAdaptive(a, b, c) {
    throw 17;
  }
};

struct Entry {
  ElementAdaptive* value = nullptr;
  const void* identity = nullptr;
};
struct Snapshot {
  std::array<std::array<Entry, 8>, 4> entries{};
  std::array<unsigned int, 4> sizes{};
  explicit Snapshot(const std::array<NodeAdaptive*, 4>& nodes) {
    for (unsigned int n = 0; n < 4; ++n)
      for (const auto& entry : nodes[n]->GetElements()) {
        Require(sizes[n] < 8, "bounded observer fixture");
        entries[n][sizes[n]++] = {entry, &entry};
      }
  }
  bool Matches(const std::array<NodeAdaptive*, 4>& nodes) const {
    for (unsigned int n = 0; n < 4; ++n) {
      if (nodes[n]->GetNumberElements() != sizes[n])
        return false;
      unsigned int i = 0;
      for (const auto& entry : nodes[n]->GetElements()) {
        if (entry != entries[n][i].value || &entry != entries[n][i].identity)
          return false;
        ++i;
      }
    }
    return true;
  }
};

struct Fixture {
  NodeAdaptive a{0, 0, 0}, b{1, 0, 0}, c{0, 1, 0}, d{1, 0, 0};
  std::array<NodeAdaptive*, 4> nodes{&a, &b, &c, &d};
  std::array<std::unique_ptr<TriangleAdaptive>, 2> parents;
  std::array<unsigned int, 3> vertices{0, 1, 2};
  std::unique_ptr<VisibleTriangle> pending;
  Snapshot before;
  int variant;
  explicit Fixture(int mode) : before(nodes), variant(mode) {
    Require(mode >= 0 && mode < 10, "bounded lifetime variant");
    for (unsigned int n = 0; n < 4; ++n) {
      nodes[n]->SetId(40 + n);
      nodes[n]->SetGa(10 + n);
      nodes[n]->SetGd(20 + n);
      nodes[n]->SetHa(30 + n);
      nodes[n]->SetHd(50 + n);
    }
    parents[0] = std::make_unique<TriangleAdaptive>(&a, &b, &c);
    for (auto* node : nodes)
      node->InsertElement(nullptr);
    parents[1] = std::make_unique<TriangleAdaptive>(&c, &b, &a);
    for (auto* node : nodes)
      node->InsertElement(nullptr);
    before = Snapshot(nodes);
    if (mode == 1)
      vertices = {0, 0, 2};
    if (mode == 2)
      vertices = {0, 1, 1};
    if (mode == 3)
      vertices = {0, 0, 0};
    if (mode == 4)
      vertices = {0, 1, 0};
    if (mode == 5)
      vertices = {2, 1, 0};
    if (mode == 6 || mode == 7)
      return;
    pending = std::make_unique<VisibleTriangle>(nodes[vertices[0]], nodes[vertices[1]],
                                                nodes[vertices[2]]);
    if (mode == 8) {
      pending->ReplaceNode(&b, &d);
      vertices[1] = 3;
    }
    if (mode == 9) {
      pending->ReplaceNode(&a, &b);
      vertices[0] = 1;
    }
    Require(pending->GetArea() == (mode >= 1 && mode <= 4 ? 0.0 : 0.5),
            "independent cached analytic area before deletion");
  }
  bool State() const {
    if (!before.Matches(nodes))
      return false;
    for (unsigned int n = 0; n < 4; ++n)
      if (nodes[n]->GetId() != 40 + n || nodes[n]->GetX() != (n == 1 || n == 3 ? 1 : 0) ||
          nodes[n]->GetY() != (n == 2 ? 1 : 0) || nodes[n]->GetZ() != 0 ||
          nodes[n]->GetGa() != 10 + n || nodes[n]->GetGd() != 20 + n ||
          nodes[n]->GetHa() != 30 + n || nodes[n]->GetHd() != 50 + n)
        return false;
    return true;
  }
  void Consume() const {
    for (auto* node : nodes)
      for (auto* element : node->GetElements())
        if (element)
          Require(element->GetArea() == 0.5, "live original parent traversal after cleanup");
  }
  bool Destroy() {
    if (variant == 6) {
      auto empty = std::make_unique<TriangleAdaptive>();
      empty.reset();
    } else if (variant == 7) {
      bool caught = false;
      try {
        ThrowingTriangle failed(&a, &b, &c);
      } catch (int value) {
        caught = value == 17;
      }
      Require(caught, "derived failure after a completed base construction");
    } else {
      // Delete through the owning base pointer to cover virtual destruction.
      std::unique_ptr<ElementAdaptive> owner(std::move(pending));
      owner.reset();
    }
    const bool restored = State();
    if (restored)
      Consume();
    std::printf("lifetime_destroy=variant:%d restored:%d\n", variant, restored);
    return restored;
  }
  void Fresh() {
    // A bounded component construction after exact cleanup, not a CLI retry.
    {
      VisibleTriangle fresh(&a, &b, &c);
      Require(fresh.GetArea() == 0.5, "fresh analytic construction after cleanup");
    }
    Require(State(), "fresh destruction restores the same original list nodes");
    Consume();
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
#endif

struct Adoption {
  SubMesh mesh;
  std::array<NodeAdaptive*, 4> nodes{};
  std::unique_ptr<TriangleAdaptive> argument;
  std::unique_ptr<Snapshot> before;
  int variant;
  explicit Adoption(int mode) : variant(mode) {
    Require(mode >= 0 && mode < 4, "bounded raw/owning empty/populated adoption");
    for (int n = 0; n < 4; ++n) {
      mesh.AddNoh(std::make_unique<NodeAdaptive>(n == 1 ? 1.0 : 0.0, n == 2 ? 1.0 : 0.0, 0));
      nodes[n] = mesh.GetNoh(n);
    }
    if (mode % 2) {
      mesh.AddElement(std::make_unique<TriangleAdaptive>(nodes[0], nodes[1], nodes[2]));
      for (auto* node : nodes)
        node->InsertElement(nullptr);
    }
    before = std::make_unique<Snapshot>(nodes);
    argument = std::make_unique<TriangleAdaptive>(nodes[0], nodes[1], nodes[2]);
  }
  void Insert() {
    if (variant < 2)
      mesh.SetElement(argument.release());
    else
      mesh.AddElement(std::move(argument));
  }
  bool Restored() {
    if (mesh.GetNumberElements() != static_cast<unsigned int>(variant % 2) || argument ||
        !before->Matches(nodes))
      return false;
    for (auto* node : nodes)
      for (auto* element : node->GetElements())
        if (element && element->GetArea() != 0.5)
          return false;
    return true;
  }
};

#if defined(_MSC_VER) && defined(_DEBUG)
bool AdoptionFailure(int variant) {
  int total;
  {
    Adoption fixture(variant);
    {
      AllocationScope hook(-1);
      fixture.Insert();
      total = attempts;
    }
  }
  Require(total > 0, "positive actual vector-growth calibration");
  std::printf("lifetime_adoption_measured=variant:%d allocations:%d\n", variant, total);
  bool passed = true;
  for (int ordinal = 0; ordinal < total; ++ordinal) {
    Adoption fixture(variant);
    _CrtMemState before{}, after{}, delta{};
    _CrtMemCheckpoint(&before);
    bool caught = false;
    {
      AllocationScope hook(ordinal);
      try {
        fixture.Insert();
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    _CrtMemCheckpoint(&after);
    _CrtMemDifference(&delta, &before, &after);
    const bool restored = fixture.Restored();
    bool fresh = false;
    if (restored) {
      auto replacement =
          std::make_unique<TriangleAdaptive>(fixture.nodes[0], fixture.nodes[1], fixture.nodes[2]);
      fixture.mesh.AddElement(std::move(replacement));
      fresh = fixture.mesh.GetNumberElements() == static_cast<unsigned int>(variant % 2 + 1);
    }
    // The consumed argument and three registration nodes must have been freed.
    const bool released = before.lCounts[_NORMAL_BLOCK] == after.lCounts[_NORMAL_BLOCK] + 4 &&
                          before.lSizes[_NORMAL_BLOCK] > after.lSizes[_NORMAL_BLOCK];
    const bool clean =
        caught && denied == 1 && attempts == ordinal + 1 && restored && released && fresh;
    std::printf("lifetime_adoption_denied=variant:%d ordinal:%d attempts:%d restored:%d "
                "released:%d fresh:%d\n",
                variant, ordinal, attempts, restored, released, fresh);
    passed = passed && clean;
  }
  std::printf("lifetime_adoption_sites=variant:%d denied:%d/%d restored:%d\n", variant, total,
              total, passed);
  return passed;
}
#endif

int Variant(const char* mode, unsigned int prefix, int limit) {
  Require(std::strlen(mode) == prefix + 1 && mode[prefix] >= '0' && mode[prefix] < '0' + limit,
          "bounded single-digit mode");
  return mode[prefix] - '0';
}
bool Run(const char* mode) {
  if (std::strcmp(mode, "contracts") == 0) {
    bool passed = true;
    for (int variant = 0; variant < 10; ++variant) {
      Fixture fixture(variant);
      const bool restored = fixture.Destroy();
      if (restored && variant != 6)
        fixture.Fresh();
      passed = restored && passed;
    }
    return passed;
  }
  if (std::strncmp(mode, "normal-", 7) == 0) {
    Fixture fixture(Variant(mode, 7, 10));
    const bool restored = fixture.Destroy();
    if (restored && fixture.variant != 6)
      fixture.Fresh();
    return restored;
  }
  if (std::strcmp(mode, "consume-after-delete") == 0) {
    Fixture fixture(0);
    fixture.pending.reset();
    volatile double total = 0;
    for (auto* node : fixture.nodes)
      for (auto* element : node->GetElements())
        if (element)
          total = total + element->GetArea();
    std::printf("lifetime_consumed=area:%.1f restored:%d\n", total, fixture.State());
    return fixture.State();
  }
  if (std::strcmp(mode, "use-after-free") == 0) {
    auto* node = new NodeAdaptive(1, 2, 3);
    delete node;
    std::printf("expired-x=%g\n", node->GetX());
  } else if (std::strcmp(mode, "leak") == 0) {
    std::printf("deliberate-leak=%p\n", static_cast<void*>(new NodeAdaptive(1, 2, 3)));
#if defined(_MSC_VER) && defined(_DEBUG)
  } else if (std::strncmp(mode, "noalloc-", 8) == 0) {
    const int variant = Variant(mode, 8, 10);
    Fixture fixture(variant);
    bool restored;
    {
      AllocationScope hook(0);
      // Empty/default and derived-failure modes construct under the hook and
      // therefore are excluded from the destruction-only no-allocation modes.
      Require(variant != 6 && variant != 7, "destruction-only mode");
      restored = fixture.Destroy();
    }
    std::printf("lifetime_allocation=attempts:%d denied:%d\n", attempts, denied);
    if (restored)
      fixture.Fresh();
    return restored && attempts == 0 && denied == 0;
  } else if (std::strncmp(mode, "adoption-", 9) == 0)
    return AdoptionFailure(Variant(mode, 9, 4));
  else if (std::strcmp(mode, "allocation-hook-control") == 0) {
    bool caught = false;
    {
      AllocationScope hook(0);
      try {
        auto node = std::make_unique<NodeAdaptive>();
      } catch (const std::bad_alloc&) {
        caught = true;
      }
    }
    Require(caught && attempts == 1 && denied == 1, "actual CRT denial control");
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
